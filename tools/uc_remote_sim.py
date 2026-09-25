"""Scripted Remote 3: an Unfolded Circle Integration-API client (UC-21 test harness).

The Remote (the "core") is the WebSocket *client* of an integration driver. This
module plays that role so tests and the validation runner can drive the hub's
UC integration exactly as a Remote 3 does, and observe what the driver sends
back. Message kinds, names and fields follow the pinned official specification
(``python tools/uc_reference.py``; see ``docs/vendor/UNFOLDED_CIRCLE.md``):

* ``core-api/integration-api/UCR-integration-asyncapi.yaml`` (message schemas)
* ``core-api/doc/integration-driver/websocket.md`` (authentication)
* ``core-api/doc/integration-driver/driver-setup.md`` (setup flow)
* ``core-api/doc/entities/entity_*.md`` (command ids and parameters)

Envelopes::

    request   {"kind": "req",   "id": <int, increasing>, "msg": "...", "msg_data": {...}}
    response  {"kind": "resp",  "req_id": <id>, "code": <HTTP status>, "msg": "...", "msg_data": {...}}
    event     {"kind": "event", "msg": "...", "cat": "DEVICE|ENTITY|REMOTE", "msg_data": {...}}

Authentication (websocket.md): the driver either answers the connection with an
``authentication`` response (``req_id`` 0, no token needed), or sends an
``auth_required`` event, after which the client sends an ``auth`` request with
its token. Header authentication sends the token as ``auth-token`` while
connecting. All three are supported here.

Everything received is recorded (``messages``, ``events``) with a monotonic
timestamp, so a test can assert what was pushed after a mark. A connection
closed by the driver is recorded with its WebSocket close code (``close_code``;
RFC 6455: 1000 normal, 1011 internal error).

Command-line use against a running driver::

    python -m tools.uc_remote_sim ws://127.0.0.1:9095 info
    python -m tools.uc_remote_sim ws://127.0.0.1:9095 entities
    python -m tools.uc_remote_sim ws://127.0.0.1:9095 states remote.orei_matrix button.preset_1
    python -m tools.uc_remote_sim ws://127.0.0.1:9095 setup host=192.168.1.50 port=443
    python -m tools.uc_remote_sim ws://127.0.0.1:9095 cmd remote.output_1_cec send_cmd command=POWER_ON
    python -m tools.uc_remote_sim ws://127.0.0.1:9095 listen --seconds 30
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import sys
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

import aiohttp

#: Integration-API version this client speaks (the pinned spec's ``info.version``).
SPEC_VERSION = "0.16.0-beta"

#: Remote entity commands (entity_remote.md). Everything else is a simple command sent with ``send_cmd``.
REMOTE_COMMANDS = ("on", "off", "toggle", "send_cmd", "send_cmd_sequence")

#: WebSocket close codes worth naming in messages (RFC 6455 §7.4.1).
CLOSE_CODES = {1000: "normal closure", 1001: "going away", 1006: "abnormal closure (no close frame)",
               1011: "internal error"}


class RemoteSimError(Exception):
    """Protocol error seen by the scripted Remote."""


class ConnectionClosedError(RemoteSimError):
    """The driver closed the connection (``code`` is the WebSocket close code, ``None`` if unknown)."""

    def __init__(self, code: int | None, reason: str = "") -> None:
        self.code = code
        self.reason = reason
        name = CLOSE_CODES.get(code or 0, "")
        super().__init__(f"connection closed by the driver: code {code}" + (f" ({name})" if name else "")
                         + (f", reason {reason!r}" if reason else ""))


@dataclass
class Received:
    """One message from the driver."""

    t: float  # time.monotonic() when received
    data: dict[str, Any]

    @property
    def kind(self) -> str:
        return str(self.data.get("kind", ""))

    @property
    def msg(self) -> str:
        return str(self.data.get("msg", ""))

    @property
    def msg_data(self) -> Any:
        return self.data.get("msg_data")


@dataclass
class SetupOutcome:
    """Result of a setup step: the request acknowledgement plus the ``driver_setup_change`` events."""

    response: dict[str, Any]
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def final(self) -> dict[str, Any] | None:
        """The last ``driver_setup_change`` payload (``STOP`` or a ``WAIT_USER_ACTION`` page)."""
        return self.events[-1] if self.events else None

    @property
    def state(self) -> str | None:
        """``OK`` / ``ERROR`` (setup finished), ``WAIT_USER_ACTION`` (next page), ``None`` (nothing arrived)."""
        return self.final.get("state") if self.final else None

    @property
    def error(self) -> str | None:
        return self.final.get("error") if self.final else None


def entity_type_of(entity_id: str) -> str:
    """Entity type from an entity id of the form ``<type>.<name>`` (this driver's convention)."""
    return entity_id.split(".", 1)[0]


class UcRemoteSim:
    """A scripted Remote 3 connected to one integration driver.

    Use as ``async with UcRemoteSim(url) as remote:`` or call :meth:`connect` /
    :meth:`close`. Requests return the driver's response dict; they raise
    :class:`ConnectionClosedError` when the driver drops the connection before
    answering, and :class:`TimeoutError` when it never answers.
    """

    def __init__(self, url: str, *, token: str | None = None, header_auth: bool = False,
                 request_timeout: float = 10.0, heartbeat: float | None = None) -> None:
        self.url = url
        self.token = token
        self.header_auth = header_auth
        self.request_timeout = request_timeout
        self.heartbeat = heartbeat
        self.messages: list[Received] = []
        self.authentication: dict[str, Any] | None = None
        self.close_code: int | None = None
        self.close_reason: str = ""
        self._session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._reader: asyncio.Task[None] | None = None
        self._next_id = 1
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._auth: asyncio.Future[dict[str, Any]] | None = None
        self._closed = asyncio.Event()
        self._new_message = asyncio.Event()
        self._entity_types: dict[str, str] = {}
        #: Everything sent, for evidence (``(t, message)``).
        self.sent: list[tuple[float, dict[str, Any]]] = []

    # ------------------------------------------------------------------ lifecycle

    async def __aenter__(self) -> UcRemoteSim:
        await self.connect()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def connect(self, timeout: float = 10.0) -> dict[str, Any]:
        """Open the WebSocket and authenticate; returns the driver's ``authentication`` response."""
        headers = {"auth-token": self.token} if (self.token and self.header_auth) else None
        self._session = aiohttp.ClientSession()
        loop = asyncio.get_running_loop()
        self._auth = loop.create_future()
        try:
            self._ws = await self._session.ws_connect(
                self.url, headers=headers, heartbeat=self.heartbeat, autoping=True,
                timeout=aiohttp.ClientWSTimeout(ws_close=5.0), max_msg_size=16 * 1024 * 1024,
            )
        except BaseException:
            await self._session.close()
            self._session = None
            raise
        self._reader = asyncio.create_task(self._read_loop(), name="uc-remote-sim-reader")
        try:
            self.authentication = await asyncio.wait_for(asyncio.shield(self._auth), timeout)
            if self.authentication.get("code") != 200:
                raise RemoteSimError(f"authentication failed: {self.authentication}")
        except BaseException:
            await self.close()
            raise
        return self.authentication

    async def close(self) -> None:
        """Close the connection (normal closure) and release resources."""
        if self._ws is not None and not self._ws.closed:
            with contextlib.suppress(Exception):
                await self._ws.close()
        if self._reader is not None:
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await asyncio.wait_for(self._reader, 5)
            self._reader = None
        if self._session is not None:
            await self._session.close()
            self._session = None

    @property
    def closed(self) -> bool:
        return self._closed.is_set()

    async def wait_closed(self, timeout: float = 5.0) -> int | None:
        """Wait until the driver closes the connection; returns the close code."""
        await asyncio.wait_for(self._closed.wait(), timeout)
        return self.close_code

    # ------------------------------------------------------------------ transport

    async def _read_loop(self) -> None:
        assert self._ws is not None
        ws = self._ws
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                    except ValueError:
                        data = {"kind": "invalid", "raw": str(msg.data)[:2000]}
                    self._dispatch(Received(time.monotonic(), data))
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    self._dispatch(Received(time.monotonic(), {"kind": "binary", "size": len(msg.data)}))
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self.close_reason = f"transport error: {ws.exception()!r}"
                    break
        except (aiohttp.ClientError, ConnectionError) as exc:
            self.close_reason = self.close_reason or f"{type(exc).__name__}: {exc}"
        finally:
            self.close_code = ws.close_code if ws.close_code is not None else self.close_code
            if not self.close_reason and ws.close_code is not None:
                # aiohttp keeps the peer's close reason in the CLOSE message only; the code is what matters.
                self.close_reason = CLOSE_CODES.get(ws.close_code, "")
            err = ConnectionClosedError(self.close_code, self.close_reason)
            for fut in self._pending.values():
                if not fut.done():
                    fut.set_exception(err)
            self._pending.clear()
            if self._auth is not None and not self._auth.done():
                self._auth.set_exception(err)
            self._closed.set()
            self._new_message.set()

    def _dispatch(self, rec: Received) -> None:
        self.messages.append(rec)
        data = rec.data
        if rec.kind == "resp":
            req_id = data.get("req_id")
            if rec.msg == "authentication" and self._auth is not None and not self._auth.done():
                # Unsolicited (req_id 0, no token needed) or the answer to our `auth` request.
                self._auth.set_result(data)
            fut = self._pending.pop(req_id, None) if isinstance(req_id, int) else None
            if fut is not None and not fut.done():
                fut.set_result(data)
        elif rec.kind == "event" and rec.msg == "auth_required":
            # Message-based authentication (websocket.md): answer with the token.
            asyncio.get_running_loop().create_task(self._send_auth())
        self._new_message.set()

    async def _send_auth(self) -> None:
        """Answer ``auth_required``; the ``authentication`` response resolves the handshake in :meth:`_dispatch`."""
        try:
            await self.request("auth", {"token": self.token or ""})
        except (RemoteSimError, TimeoutError) as exc:
            if self._auth is not None and not self._auth.done():
                self._auth.set_exception(exc)

    async def _send(self, message: dict[str, Any]) -> None:
        if self._ws is None or self._ws.closed or self.closed:
            raise ConnectionClosedError(self.close_code, self.close_reason)
        self.sent.append((time.monotonic(), message))
        try:
            await self._ws.send_str(json.dumps(message))
        except (ConnectionError, aiohttp.ClientError, RuntimeError) as exc:
            raise ConnectionClosedError(self.close_code, f"send failed: {exc}") from exc

    async def request(self, msg: str, msg_data: dict[str, Any] | None = None,
                      timeout: float | None = None) -> dict[str, Any]:
        """Send a ``req`` message and wait for the ``resp`` with the same id."""
        req_id = self._next_id
        self._next_id += 1
        fut: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._pending[req_id] = fut
        message: dict[str, Any] = {"kind": "req", "id": req_id, "msg": msg}
        if msg_data is not None:
            message["msg_data"] = msg_data
        try:
            await self._send(message)
            return await asyncio.wait_for(fut, timeout or self.request_timeout)
        finally:
            self._pending.pop(req_id, None)

    async def send_event(self, msg: str, msg_data: dict[str, Any] | None = None, cat: str = "DEVICE") -> None:
        """Send an ``event`` message (connect, disconnect, standby, abort_driver_setup)."""
        message: dict[str, Any] = {"kind": "event", "msg": msg, "cat": cat}
        if msg_data is not None:
            message["msg_data"] = msg_data
        await self._send(message)

    # ------------------------------------------------------------------ observation

    @property
    def events(self) -> list[Received]:
        return [m for m in self.messages if m.kind == "event"]

    def mark(self) -> float:
        """A point in time; pass it to :meth:`events_since` / :meth:`wait_event`."""
        return time.monotonic()

    def events_since(self, since: float, msg: str | None = None) -> list[Received]:
        return [m for m in self.messages if m.kind == "event" and m.t >= since and (msg is None or m.msg == msg)]

    def entity_changes(self, since: float = 0.0, entity_id: str | None = None) -> list[dict[str, Any]]:
        """``entity_change`` payloads received since ``since`` (optionally for one entity)."""
        return [m.msg_data for m in self.events_since(since, "entity_change")
                if entity_id is None or (m.msg_data or {}).get("entity_id") == entity_id]

    def device_states(self, since: float = 0.0) -> list[str]:
        """``device_state`` event states received since ``since``."""
        return [str((m.msg_data or {}).get("state")) for m in self.events_since(since, "device_state")]

    async def wait_event(self, msg: str, predicate: Callable[[Any], bool] | None = None, *,
                         since: float = 0.0, timeout: float = 5.0) -> Received:
        """Wait for an event named ``msg`` (whose ``msg_data`` satisfies ``predicate``) received after ``since``."""
        deadline = time.monotonic() + timeout
        while True:
            for m in self.events_since(since, msg):
                if predicate is None or predicate(m.msg_data):
                    return m
            if self.closed:
                raise ConnectionClosedError(self.close_code, self.close_reason)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"no '{msg}' event within {timeout:.1f}s")
            self._new_message.clear()
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._new_message.wait(), remaining)

    # ------------------------------------------------------------------ Remote events (driver lifecycle)

    async def send_connect(self) -> None:
        """The Remote asks the driver to connect its devices (``connect``, cat DEVICE)."""
        await self.send_event("connect", cat="DEVICE")

    async def send_disconnect(self) -> None:
        await self.send_event("disconnect", cat="DEVICE")

    async def enter_standby(self) -> None:
        await self.send_event("enter_standby", cat="REMOTE")

    async def exit_standby(self) -> None:
        await self.send_event("exit_standby", cat="REMOTE")

    async def abort_driver_setup(self, error: str = "USER_CANCELLED") -> None:
        await self.send_event("abort_driver_setup", {"error": error}, cat="DEVICE")

    # ------------------------------------------------------------------ requests

    async def get_driver_version(self) -> dict[str, Any]:
        return await self.request("get_driver_version")

    async def get_driver_metadata(self) -> dict[str, Any]:
        return await self.request("get_driver_metadata")

    async def get_device_state(self) -> dict[str, Any]:
        return await self.request("get_device_state")

    async def get_available_entities(self) -> list[dict[str, Any]]:
        resp = await self.request("get_available_entities")
        entities = list((resp.get("msg_data") or {}).get("available_entities") or [])
        self._entity_types.update({e["entity_id"]: e["entity_type"] for e in entities if "entity_id" in e})
        return entities

    async def subscribe_events(self, entity_ids: Iterable[str]) -> dict[str, Any]:
        return await self.request("subscribe_events", {"entity_ids": list(entity_ids)})

    async def unsubscribe_events(self, entity_ids: Iterable[str]) -> dict[str, Any]:
        return await self.request("unsubscribe_events", {"entity_ids": list(entity_ids)})

    async def get_entity_states(self) -> list[dict[str, Any]]:
        resp = await self.request("get_entity_states")
        return list(resp.get("msg_data") or [])

    async def entity_state(self, entity_id: str) -> dict[str, Any] | None:
        """Attributes of one configured entity (from ``get_entity_states``)."""
        for e in await self.get_entity_states():
            if e.get("entity_id") == entity_id:
                return dict(e.get("attributes") or {})
        return None

    async def entity_command(self, entity_id: str, cmd_id: str, params: dict[str, Any] | None = None, *,
                             entity_type: str | None = None, timeout: float | None = None) -> dict[str, Any]:
        """``entity_command``; returns the response (``code`` is the status the driver acknowledged)."""
        data: dict[str, Any] = {
            "entity_type": entity_type or self._entity_types.get(entity_id) or entity_type_of(entity_id),
            "entity_id": entity_id,
            "cmd_id": cmd_id,
        }
        if params is not None:
            data["params"] = params
        return await self.request("entity_command", data, timeout=timeout)

    # --- remote entity (entity_remote.md)

    async def remote_on(self, entity_id: str) -> dict[str, Any]:
        return await self.entity_command(entity_id, "on")

    async def remote_off(self, entity_id: str) -> dict[str, Any]:
        return await self.entity_command(entity_id, "off")

    async def remote_toggle(self, entity_id: str) -> dict[str, Any]:
        return await self.entity_command(entity_id, "toggle")

    async def remote_send_cmd(self, entity_id: str, command: str, *, repeat: int | None = None,
                              delay: int | None = None, hold: int | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"command": command}
        params.update({k: v for k, v in (("repeat", repeat), ("delay", delay), ("hold", hold)) if v is not None})
        return await self.entity_command(entity_id, "send_cmd", params)

    async def remote_send_cmd_sequence(self, entity_id: str, sequence: list[str], *, repeat: int | None = None,
                                       delay: int | None = None, hold: int | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"sequence": list(sequence)}
        params.update({k: v for k, v in (("repeat", repeat), ("delay", delay), ("hold", hold)) if v is not None})
        return await self.entity_command(entity_id, "send_cmd_sequence", params)

    # --- media player (entity_media_player.md), button (entity_button.md), switch (entity_switch.md)

    async def select_source(self, entity_id: str, source: str) -> dict[str, Any]:
        return await self.entity_command(entity_id, "select_source", {"source": source})

    async def button_push(self, entity_id: str) -> dict[str, Any]:
        return await self.entity_command(entity_id, "push")

    async def switch(self, entity_id: str, cmd_id: str) -> dict[str, Any]:
        if cmd_id not in ("on", "off", "toggle"):
            raise ValueError(f"switch command must be on/off/toggle, not {cmd_id!r}")
        return await self.entity_command(entity_id, cmd_id)

    # ------------------------------------------------------------------ setup (driver-setup.md)

    async def _setup_events(self, since: float, timeout: float) -> list[dict[str, Any]]:
        """``driver_setup_change`` payloads until the setup stops or waits for the user."""
        out: list[dict[str, Any]] = []
        seen = 0
        deadline = time.monotonic() + timeout
        while True:
            changes = [m.msg_data or {} for m in self.events_since(since, "driver_setup_change")]
            out = changes
            if changes[seen:]:
                seen = len(changes)
                last = changes[-1]
                if last.get("event_type") == "STOP" or last.get("state") == "WAIT_USER_ACTION":
                    return out
            remaining = deadline - time.monotonic()
            if remaining <= 0 or self.closed:
                return out
            self._new_message.clear()
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._new_message.wait(), min(remaining, 0.5))

    async def setup_driver(self, setup_data: dict[str, Any], *, reconfigure: bool = False,
                           language: str | None = None, timeout: float = 30.0) -> SetupOutcome:
        """Start the setup flow (``setup_driver``) and collect ``driver_setup_change`` events."""
        since = self.mark()
        data: dict[str, Any] = {"setup_data": setup_data}
        if reconfigure:
            data["reconfigure"] = True
        if language:
            data["language"] = language
        resp = await self.request("setup_driver", data, timeout=timeout)
        return SetupOutcome(resp, await self._setup_events(since, timeout))

    async def set_driver_user_data(self, *, input_values: dict[str, Any] | None = None,
                                   confirm: bool | None = None, timeout: float = 30.0) -> SetupOutcome:
        """Answer a ``WAIT_USER_ACTION`` page with input values or a confirmation."""
        if (input_values is None) == (confirm is None):
            raise ValueError("pass exactly one of input_values / confirm")
        since = self.mark()
        data = {"input_values": input_values} if input_values is not None else {"confirm": confirm}
        resp = await self.request("set_driver_user_data", data, timeout=timeout)
        return SetupOutcome(resp, await self._setup_events(since, timeout))

    # ------------------------------------------------------------------ the Remote's usual start-up

    async def attach(self, entity_ids: Iterable[str] | None = None, *, connect: bool = True,
                     device_state_timeout: float = 15.0) -> list[dict[str, Any]]:
        """What a Remote does after (re)connecting: ``connect``, list entities, subscribe.

        Subscribes ``entity_ids`` (default: every available entity) and returns
        the available entities. With ``connect`` it first sends the ``connect``
        event and waits for the driver's ``device_state`` event.
        """
        if connect:
            since = self.mark()
            await self.send_connect()
            await self.wait_event("device_state", since=since, timeout=device_state_timeout)
        entities = await self.get_available_entities()
        ids = list(entity_ids) if entity_ids is not None else [e["entity_id"] for e in entities]
        await self.subscribe_events(ids)
        return entities


# ---------------------------------------------------------------------- CLI


def _kv(items: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in items:
        key, _, value = item.partition("=")
        try:
            out[key] = json.loads(value)
        except ValueError:
            out[key] = value
    return out


async def _cli(args: argparse.Namespace) -> int:
    async with UcRemoteSim(args.url, token=args.token, header_auth=args.header_auth) as remote:
        print(json.dumps({"authentication": remote.authentication}))
        if args.action == "info":
            print(json.dumps(await remote.get_driver_version(), indent=2))
            print(json.dumps(await remote.get_driver_metadata(), indent=2))
            print(json.dumps(await remote.get_device_state(), indent=2))
        elif args.action == "entities":
            for e in await remote.get_available_entities():
                print(f"{e['entity_id']:32} {e['entity_type']:13} {e.get('features')} {e.get('name')}")
        elif args.action == "states":
            await remote.get_available_entities()
            if args.rest:
                await remote.subscribe_events(args.rest)
            print(json.dumps(await remote.get_entity_states(), indent=2))
        elif args.action == "setup":
            outcome = await remote.setup_driver(_kv(args.rest), reconfigure=args.reconfigure)
            print(json.dumps({"response": outcome.response, "events": outcome.events}, indent=2))
        elif args.action == "cmd":
            if len(args.rest) < 2:
                print("cmd needs: <entity_id> <cmd_id> [key=value ...]", file=sys.stderr)
                return 2
            entity_id, cmd_id, *params = args.rest
            await remote.get_available_entities()
            await remote.subscribe_events([entity_id])
            try:
                resp = await remote.entity_command(entity_id, cmd_id, _kv(params) or None)
                print(json.dumps(resp, indent=2))
            except ConnectionClosedError as exc:
                print(str(exc), file=sys.stderr)
                return 1
        elif args.action == "listen":
            await remote.attach()
            await asyncio.sleep(args.seconds)
            for m in remote.events:
                print(json.dumps(m.data))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.uc_remote_sim", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", help="driver WebSocket URL, e.g. ws://127.0.0.1:9095")
    p.add_argument("action", choices=("info", "entities", "states", "setup", "cmd", "listen"))
    p.add_argument("rest", nargs="*", help="action arguments (entity ids, key=value pairs)")
    p.add_argument("--token", help="auth token (message auth, or header auth with --header-auth)")
    p.add_argument("--header-auth", action="store_true", help="send the token as the auth-token header")
    p.add_argument("--reconfigure", action="store_true", help="setup: reconfigure an existing setup")
    p.add_argument("--seconds", type=float, default=10.0, help="listen: how long")
    return asyncio.run(_cli(p.parse_args(argv)))


if __name__ == "__main__":
    sys.exit(main())
