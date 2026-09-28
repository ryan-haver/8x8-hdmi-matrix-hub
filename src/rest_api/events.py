"""The hub's live event stream: the server side of the /ws contract (docs/api/WEBSOCKET.md).

One :class:`EventStream` per hub process owns

* the WebSocket clients: each gets its own outbound queue and writer task, so
  :meth:`EventStream.publish` never waits for a client and a stalled client is
  dropped after ``SEND_TIMEOUT`` without holding up a command (API-09);
* the matrix view: what the hub last read from the matrix (link state, routing,
  power, names, input signal, display presence, audio mute, cables). A status
  poller refreshes it every ``STATUS_POLL_INTERVAL`` seconds, and at once when
  the matrix reports a change: an accepted write (``Events.STATE_CHANGED``, from
  any caller: REST, the Remote, scenes, shortcuts), a Telnet push (cable
  plugged) or a link change. Each difference is published once, whatever made
  the change (UC-17): the hub, another controller or the front panel.

The poller runs with the REST app (``install_event_stream``), in every mode,
whether or not a Remote or any WebSocket client is connected.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any

from aiohttp import web

_LOG = logging.getLogger("rest_api.events")

#: Version of the message contract (docs/api/WEBSOCKET.md). Sent in ``connected``.
PROTOCOL_VERSION = 1
#: Default seconds between two status polls (``STATUS_POLL_INTERVAL``).
DEFAULT_POLL_INTERVAL = 5.0
MIN_POLL_INTERVAL = 0.2
#: A client that has not taken a message for this long is disconnected (API-09).
SEND_TIMEOUT = 5.0
#: Messages waiting for one client; a client that falls this far behind is disconnected.
QUEUE_LIMIT = 256
#: After an accepted write, wait this long for more writes (route to all, preset save) before reading.
SETTLE_SECONDS = 0.15
#: ... but never longer than this in total.
SETTLE_MAX_SECONDS = 1.0

PORTS = range(1, 9)


def poll_interval_from_env() -> float:
    """``STATUS_POLL_INTERVAL`` in seconds (default 5, minimum 0.2)."""
    raw = os.environ.get("STATUS_POLL_INTERVAL", "").strip()
    if not raw:
        return DEFAULT_POLL_INTERVAL
    try:
        value = float(raw)
    except ValueError:
        _LOG.warning("STATUS_POLL_INTERVAL=%r is not a number; using %.0f s", raw, DEFAULT_POLL_INTERVAL)
        return DEFAULT_POLL_INTERVAL
    return max(MIN_POLL_INTERVAL, value)


def message(event: str, data: dict[str, Any]) -> str:
    """One contract message: ``{"event": <name>, "data": {...}}``."""
    return json.dumps({"event": event, "data": data})


def link_summary(device: Any) -> dict[str, Any]:
    """The matrix link as the contract reports it (``connected``, ``state``, ``host``)."""
    if device is None:
        return {"configured": False, "connected": False, "state": "not_configured", "host": None}
    connected = getattr(device, "connected", False) is True
    state = getattr(device, "connection_state", None)
    state_value = getattr(state, "value", None)
    if not isinstance(state_value, str):
        state_value = "connected" if connected else "disconnected"
    host = getattr(device, "host", None)
    return {
        "configured": True,
        "connected": connected,
        "state": state_value,
        "host": host if isinstance(host, str) else None,
    }


async def _close(ws: web.WebSocketResponse) -> None:
    with contextlib.suppress(Exception):
        await asyncio.wait_for(ws.close(), timeout=1)


def _per_port(values: Any) -> list[Any]:
    return list(values[:8]) if isinstance(values, list) else []


def _is_port(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 8


@dataclass
class MatrixView:
    """What the hub last read from the matrix. A missing key means "not known yet"."""

    routing: dict[int, int] = field(default_factory=dict)
    power: str | None = None
    input_names: dict[int, str] = field(default_factory=dict)
    output_names: dict[int, str] = field(default_factory=dict)
    signal: dict[int, bool] = field(default_factory=dict)
    display: dict[int, bool] = field(default_factory=dict)
    muted: dict[int, bool] = field(default_factory=dict)
    cables: dict[str, dict[int, bool]] = field(default_factory=lambda: {"input": {}, "output": {}})
    #: The last complete reads, for the ``status`` snapshot.
    raw_status: dict[str, Any] | None = None
    raw_outputs: dict[str, Any] | None = None
    raw_inputs: dict[str, Any] | None = None
    raw_cables: dict[str, Any] | None = None


@dataclass
class _Client:
    ws: web.WebSocketResponse
    queue: asyncio.Queue[str | None]
    task: asyncio.Task[None] | None = None
    #: Whether this client has had a ``status`` snapshot (sent as soon as the hub has one).
    has_snapshot: bool = False


class EventStream:
    """The /ws clients and the hub-owned matrix poller (see the module docstring)."""

    def __init__(self, poll_interval: float | None = None) -> None:
        self.poll_interval = poll_interval if poll_interval is not None else poll_interval_from_env()
        self._clients: dict[web.WebSocketResponse, _Client] = {}
        self.view = MatrixView()
        self._link: dict[str, Any] | None = None
        self._device: Any = None
        self._unlisten: list[Callable[[], None]] = []
        self._wake: asyncio.Event | None = None
        self._settle = False
        self._force_cables = False
        self._poll_task: asyncio.Task[None] | None = None
        self._poll_lock: asyncio.Lock | None = None

    # ------------------------------------------------------------------ clients

    @property
    def client_count(self) -> int:
        return len(self._clients)

    def add_client(self, ws: web.WebSocketResponse) -> None:
        """Register a prepared WebSocket: ``connected`` first, then a ``status`` snapshot once there is one."""
        client = _Client(ws=ws, queue=asyncio.Queue(maxsize=QUEUE_LIMIT))
        self._clients[ws] = client
        client.task = asyncio.get_running_loop().create_task(self._writer(client), name="ws_client_writer")
        from .utils import get_matrix_device

        self._send(client, message("connected", {
            "message": "Connected to the HDMI matrix hub",
            "client_count": len(self._clients),
            "protocol": PROTOCOL_VERSION,
            "matrix": link_summary(get_matrix_device()),
        }))
        self._send_snapshot(client)
        if client.has_snapshot is False:
            self.request_poll()  # the hub has not read the matrix yet: do it now, the snapshot follows

    async def remove_client(self, ws: web.WebSocketResponse) -> None:
        client = self._clients.pop(ws, None)
        if client is None or client.task is None:
            return
        client.task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await client.task

    def send(self, ws: web.WebSocketResponse, event: str, data: dict[str, Any]) -> None:
        """A reply to one client (``pong``, ``error``, ``status`` for ``get_status``)."""
        client = self._clients.get(ws)
        if client is not None:
            self._send(client, message(event, data))
            if event == "status":
                client.has_snapshot = True

    def publish(self, event: str, data: dict[str, Any]) -> None:
        """Queue ``event`` for every client and return at once (API-09)."""
        text = message(event, data)
        for client in list(self._clients.values()):
            self._send(client, text)

    def _send(self, client: _Client, text: str) -> None:
        try:
            client.queue.put_nowait(text)
        except asyncio.QueueFull:
            _LOG.warning("WebSocket client is %d messages behind; disconnecting it", QUEUE_LIMIT)
            self._drop(client)

    def _drop(self, client: _Client) -> None:
        self._clients.pop(client.ws, None)
        if client.task is not None:
            client.task.cancel()
        asyncio.get_running_loop().create_task(_close(client.ws))

    async def _writer(self, client: _Client) -> None:
        while True:
            text = await client.queue.get()
            if text is None or client.ws.closed:
                break
            try:
                await asyncio.wait_for(client.ws.send_str(text), timeout=SEND_TIMEOUT)
            except TimeoutError:
                _LOG.warning("WebSocket client did not take a message within %.0f s; disconnecting it", SEND_TIMEOUT)
                break
            except Exception as exc:  # noqa: BLE001 - a broken client only affects itself
                _LOG.debug("WebSocket send failed: %s", exc)
                break
        self._clients.pop(client.ws, None)
        await _close(client.ws)

    # ------------------------------------------------------------------ snapshot

    def status_snapshot(self) -> dict[str, Any] | None:
        """The ``status`` payload from the last complete read, or ``None`` before the first one."""
        view = self.view
        if view.raw_status is None or not view.routing:
            return None
        from .core import _format_inputs, _format_outputs, _format_status
        from .utils import get_input_names, get_output_names

        device = self._device
        formatted = _format_status(view.raw_status, device, get_input_names(), get_output_names())
        formatted["connected"] = getattr(device, "connected", False) is True
        formatted["state"] = link_summary(device)["state"]
        # Port details carry the same names as the top level (BE-31: the hub's name cache alone is
        # empty in the core-only hub, and the details used to reset every name to "Output N").
        formatted["inputs"] = _format_inputs(view.raw_inputs, view.raw_cables, formatted["input_names"])
        formatted["outputs_detail"] = _format_outputs(view.raw_outputs, view.raw_cables, formatted["output_names"])
        return formatted

    def _send_snapshot(self, client: _Client) -> None:
        snapshot = self.status_snapshot()
        if snapshot is not None:
            self._send(client, message("status", snapshot))
            client.has_snapshot = True

    # ------------------------------------------------------------------ poller

    def start(self) -> None:
        loop = asyncio.get_running_loop()
        self._wake = asyncio.Event()
        if self._poll_task is None or self._poll_task.done():
            self._poll_task = loop.create_task(self._poll_loop(), name="hub_status_poller")

    async def stop(self) -> None:
        task, self._poll_task = self._poll_task, None
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        self._follow(None)
        for client in list(self._clients.values()):
            await self.remove_client(client.ws)

    def request_poll(self, *, settle: bool = False, force_cables: bool = False) -> None:
        """Read the matrix now instead of at the next interval."""
        self._settle = self._settle or settle
        self._force_cables = self._force_cables or force_cables
        if self._wake is not None:
            self._wake.set()

    async def _poll_loop(self) -> None:
        assert self._wake is not None
        _LOG.info("Hub status poller started (every %.1f s)", self.poll_interval)
        while True:
            try:
                with contextlib.suppress(TimeoutError):
                    await asyncio.wait_for(self._wake.wait(), self.poll_interval)
                if self._wake.is_set() and self._settle:
                    await self._wait_for_quiet()
                self._wake.clear()
                force_cables, self._force_cables, self._settle = self._force_cables, False, False
                await self.poll_once(force_cables=force_cables)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - one failed poll must not stop the stream
                _LOG.warning("Status poll failed: %s", exc, exc_info=True)

    async def _wait_for_quiet(self) -> None:
        """Let a burst of writes finish (route to all, preset save) so it is read once, at its end."""
        assert self._wake is not None
        loop = asyncio.get_running_loop()
        deadline = loop.time() + SETTLE_MAX_SECONDS
        while loop.time() < deadline:
            self._wake.clear()
            try:
                await asyncio.wait_for(self._wake.wait(), SETTLE_SECONDS)
            except TimeoutError:
                return

    async def poll_once(self, *, force_cables: bool = False) -> None:
        """Read the matrix and publish what changed since the last read."""
        if self._poll_lock is None:
            self._poll_lock = asyncio.Lock()
        async with self._poll_lock:
            from .utils import get_matrix_device

            device = get_matrix_device()
            self._follow(device)
            self._check_link(device)
            if device is None or getattr(device, "connected", False) is not True:
                return
            raw_status = await device.get_status()
            raw_outputs = await device.get_output_status()
            raw_inputs = await device.get_input_status()
            raw_cables = None
            if getattr(device, "telnet_connected", False) is True:
                raw_cables = await device.get_all_cable_status(force_refresh=force_cables)
            self._check_link(device)
            if getattr(device, "connected", False) is not True:
                return  # the link went down during the read: keep the last known values
            self._apply(raw_status, raw_outputs, raw_inputs, raw_cables)

    # ------------------------------------------------------------------ device and link

    def _follow(self, device: Any) -> None:
        """Listen to the current matrix; a different matrix starts a new view (no diffs across devices)."""
        if device is self._device:
            return
        for unlisten in self._unlisten:
            with contextlib.suppress(Exception):
                unlisten()
        self._unlisten = []
        self._device = device
        self.view = MatrixView()
        self._link = None
        events = getattr(device, "events", None)
        if device is None or events is None or not callable(getattr(events, "on", None)):
            return
        try:
            from orei_matrix import Events
        except ImportError:  # pragma: no cover - src/ is always importable in the hub
            return

        def on_link(*_args: Any) -> None:
            self.request_poll()

        def on_change(change: Any = None, *_args: Any) -> None:
            self.request_poll(settle=True, force_cables=isinstance(change, dict) and "push" in change)

        remove = getattr(events, "remove_listener", None)

        def unlistener(event: Any, callback: Callable[..., None]) -> Callable[[], None]:
            return lambda: remove(event, callback) if callable(remove) else None

        for event, callback in ((Events.CONNECTED, on_link), (Events.DISCONNECTED, on_link),
                                (Events.STATE_CHANGED, on_change)):
            events.on(event, callback)
            self._unlisten.append(unlistener(event, callback))

    def _check_link(self, device: Any) -> None:
        link = link_summary(device)
        previous = self._link
        self._link = link
        if previous is None:
            return
        if link["connected"] != previous["connected"] or (link["connected"] and link["state"] != previous["state"]):
            self.publish("matrix_connection", {"connected": link["connected"], "state": link["state"],
                                               "host": link["host"]})

    # ------------------------------------------------------------------ diffing

    def _known(self) -> int:
        """How many values the hub knows (to notice a first reading, e.g. cables once Telnet is up)."""
        v = self.view
        return (len(v.routing) + len(v.input_names) + len(v.output_names) + len(v.signal) + len(v.display)
                + len(v.muted) + len(v.cables["input"]) + len(v.cables["output"]) + (v.power is not None))

    def _apply(self, raw_status: Any, raw_outputs: Any, raw_inputs: Any, raw_cables: Any) -> None:
        view = self.view
        had_snapshot = view.raw_status is not None and bool(view.routing)
        known_before = self._known()
        if isinstance(raw_status, dict) and _per_port(raw_status.get("routing")):
            self._apply_status(raw_status)
            view.raw_status = raw_status
        if isinstance(raw_outputs, dict):
            self._apply_outputs(raw_outputs)
            view.raw_outputs = raw_outputs
        if isinstance(raw_inputs, dict):
            self._apply_inputs(raw_inputs)
            view.raw_inputs = raw_inputs
        if isinstance(raw_cables, dict):
            self._apply_cables(raw_cables)
            view.raw_cables = raw_cables
        # A first reading of something (e.g. cables once Telnet came up after the first read) is not a
        # change event; every client gets a fresh snapshot instead. Clients that connected before the
        # first complete read get their first one now.
        if had_snapshot and self._known() > known_before:
            waiting = list(self._clients.values())
        else:
            waiting = [c for c in self._clients.values() if not c.has_snapshot]
        if waiting:
            snapshot = self.status_snapshot()
            if snapshot is not None:
                text = message("status", snapshot)
                for client in waiting:
                    self._send(client, text)
                    client.has_snapshot = True

    def _apply_status(self, raw: dict[str, Any]) -> None:
        from .core import _format_status
        from .utils import get_input_names, get_output_names

        view = self.view
        formatted = _format_status(raw, self._device, get_input_names(), get_output_names())
        input_names = {int(k): str(v) for k, v in formatted["input_names"].items()}
        output_names = {int(k): str(v) for k, v in formatted["output_names"].items()}
        for port in PORTS:
            old = view.input_names.get(port)
            if old is not None and old != input_names[port]:
                self.publish("input_name_change", {"input": port, "name": input_names[port]})
            old = view.output_names.get(port)
            if old is not None and old != output_names[port]:
                self.publish("output_name_change", {"output": port, "name": output_names[port]})
        view.input_names, view.output_names = input_names, output_names

        for output, source in enumerate(_per_port(raw.get("routing")), start=1):
            if not _is_port(source):
                continue  # 0 / garbage = unknown: keep the last known source
            previous = view.routing.get(output)
            view.routing[output] = source
            if previous is not None and previous != source:
                self.publish("routing_change", {
                    "output": output,
                    "input": source,
                    "input_name": input_names.get(source, f"Input {source}"),
                    "previous_input": previous,
                })

        power = raw.get("power")
        if power in ("on", "off"):
            if view.power is not None and view.power != power:
                self.publish("power_change", {"power": power})
            view.power = power

    def _apply_outputs(self, raw: dict[str, Any]) -> None:
        view = self.view
        for output, value in enumerate(_per_port(raw.get("allconnect")), start=1):
            if value not in (0, 1):
                continue
            connected = value == 1
            previous = view.display.get(output)
            view.display[output] = connected
            if previous is not None and previous != connected:
                self.publish("connection_change", {
                    "output": output,
                    "connected": connected,
                    "output_name": view.output_names.get(output, f"Output {output}"),
                })
        for output, value in enumerate(_per_port(raw.get("allaudiomute")), start=1):
            if value not in (0, 1):
                continue
            muted = value == 1
            previous = view.muted.get(output)
            view.muted[output] = muted
            if previous is not None and previous != muted:
                self.publish("audio_mute", {"output": output, "muted": muted})

    def _apply_inputs(self, raw: dict[str, Any]) -> None:
        view = self.view
        # get input status "inactive": 1 = signal present, 0 = none (the device's naming)
        for input_num, value in enumerate(_per_port(raw.get("inactive")), start=1):
            if value not in (0, 1):
                continue
            has_signal = value == 1
            previous = view.signal.get(input_num)
            view.signal[input_num] = has_signal
            if previous is not None and previous != has_signal:
                self.publish("signal_change", {
                    "input": input_num,
                    "has_signal": has_signal,
                    "input_name": view.input_names.get(input_num, f"Input {input_num}"),
                })

    def _apply_cables(self, raw: dict[str, Any]) -> None:
        view = self.view
        for side, kind in (("inputs", "input"), ("outputs", "output")):
            ports = raw.get(side)
            if not isinstance(ports, dict):
                continue
            names = view.input_names if kind == "input" else view.output_names
            for port in PORTS:
                value = ports.get(port)
                if not isinstance(value, bool):
                    continue  # None = unknown (the Telnet dump did not list the port)
                previous = view.cables[kind].get(port)
                view.cables[kind][port] = value
                if previous is not None and previous != value:
                    self.publish("cable_change", {
                        "type": kind,
                        "port": port,
                        "connected": value,
                        "name": names.get(port, f"{kind.capitalize()} {port}"),
                    })


# ---------------------------------------------------------------------- the hub's one stream

_stream: EventStream | None = None


def get_event_stream() -> EventStream:
    """The hub's event stream (created on first use)."""
    global _stream
    if _stream is None:
        _stream = EventStream()
    return _stream


def reset_event_stream() -> None:
    """Forget the stream (tests; a new app gets a new one)."""
    global _stream
    _stream = None


def install_event_stream(app: web.Application) -> None:
    """Run the hub's event stream (and its poller) for the app's lifetime."""

    async def _ctx(app: web.Application) -> AsyncIterator[None]:
        global _stream
        stream = EventStream()
        _stream = stream
        stream.start()
        yield
        await stream.stop()
        if _stream is stream:
            _stream = None

    app.cleanup_ctx.append(_ctx)
