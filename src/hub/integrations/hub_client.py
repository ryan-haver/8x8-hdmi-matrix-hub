"""Transport-independent asynchronous hub contract and event projection.

All I/O methods are async; subscribe is synchronous and returns an idempotent
unsubscribe function. Subscribers receive an initial snapshot projection, then
changes. Snapshot dictionaries use one-based integer port numbers. Unknown
signals/cables/displays are absent, rather than reported as false.
"""

import asyncio
import inspect
import logging
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

_LOG = logging.getLogger(__name__)


@dataclass
class HubSnapshot:
    connected: bool = False
    power: bool = False
    routing: dict[int, int] = field(default_factory=dict)
    input_names: dict[int, str] = field(default_factory=dict)
    output_names: dict[int, str] = field(default_factory=dict)
    preset_names: dict[int, str] = field(default_factory=dict)
    input_signals: dict[int, bool] = field(default_factory=dict)
    input_cables: dict[int, bool] = field(default_factory=dict)
    output_displays: dict[int, bool] = field(default_factory=dict)
    favorite_presets: list[int] = field(default_factory=list)
    profiles: list[dict[str, Any]] = field(default_factory=list)
    scenes: list[dict[str, Any]] = field(default_factory=list)
    shortcuts: list[dict[str, Any]] = field(default_factory=list)
    macros: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class HubEvent:
    kind: str
    data: dict[str, Any]


@runtime_checkable
class HubClient(Protocol):
    async def snapshot(self) -> HubSnapshot: ...
    async def switch(self, input_num: int, output_num: int | None = None) -> bool: ...
    async def cycle_input(self, direction: str, output_num: int = 1) -> bool: ...
    async def recall_preset(self, preset: int) -> bool: ...
    async def save_preset(self, preset: int) -> bool: ...
    async def power(self, on: bool) -> bool: ...
    async def send_cec(self, target_kind: str, port: int, command: str) -> bool: ...
    async def run_action(self, kind: str, action_id: str, *, passcode: str | None = None) -> dict[str, Any]: ...
    def subscribe(self, callback: Callable[[HubEvent], Any]) -> Callable[[], None]: ...
    async def close(self) -> None: ...


def port_map(value: Any) -> dict[int, Any]:
    if isinstance(value, dict):
        return {int(key): item for key, item in value.items() if str(key).isdigit()}
    if isinstance(value, list):
        return dict(enumerate(value, 1))
    return {}


def apply_status(snapshot: HubSnapshot, data: dict[str, Any], *, legacy_routing: bool = False) -> None:
    """Accept REST status/full and both current and legacy WS snapshots."""
    if "connected" in data:
        snapshot.connected = data["connected"] is True
    if "power" in data:
        snapshot.power = data["power"] in (True, 1, "on")
    routing = data.get("routing", data.get("outputs"))
    if routing is None and legacy_routing:
        routing = data.get("allconnect")
    routes = port_map(routing)
    if routes and all(isinstance(value, int) and not isinstance(value, bool) for value in routes.values()):
        snapshot.routing = routes
    for name in ("input_names", "output_names", "preset_names"):
        if name in data:
            setattr(snapshot, name, port_map(data[name]))
    if "favorite_presets" in data:
        snapshot.favorite_presets = [int(value) for value in data["favorite_presets"]]
    for key, field_name in (("inputs_inactive", "input_signals"), ("outputs_connected", "output_displays")):
        if key in data:
            setattr(
                snapshot,
                field_name,
                {port: bool(value) for port, value in port_map(data[key]).items() if value is not None},
            )
    for row in data.get("inputs", []):
        if not isinstance(row, dict):
            continue
        port = int(row.get("number", row.get("port", row.get("input", 0))))
        if port < 1:
            continue
        if "name" in row:
            snapshot.input_names[port] = row["name"]
        signal = row.get("signalActive", row.get("has_signal"))
        if signal is not None:
            snapshot.input_signals[port] = bool(signal)
        cable = row.get("cableConnected", row.get("sourceDetected"))
        if cable is not None:
            snapshot.input_cables[port] = bool(cable)
    for row in data.get("outputs_detail", []):
        port = int(row["number"])
        if "name" in row:
            snapshot.output_names[port] = row["name"]
        if row.get("connected") is not None:
            snapshot.output_displays[port] = bool(row["connected"])


def project(snapshot: HubSnapshot) -> list[HubEvent]:
    """Stable event payloads, shared by both transports."""
    return [
        HubEvent("hub_connection", {"connected": snapshot.connected}),
        HubEvent("power", {"on": snapshot.power}),
        HubEvent("routing", {"routing": snapshot.routing}),
        HubEvent("signal", {"input_signals": snapshot.input_signals}),
        HubEvent("cable", {"input_cables": snapshot.input_cables}),
        HubEvent("display", {"output_displays": snapshot.output_displays}),
        HubEvent("names", {"input_names": snapshot.input_names, "output_names": snapshot.output_names}),
        HubEvent("presets", {"preset_names": snapshot.preset_names, "favorite_presets": snapshot.favorite_presets}),
    ]


class EventPublisher:
    """Isolate subscriber errors and own every asynchronous callback task."""

    def __init__(self) -> None:
        self._snapshot = HubSnapshot()
        self._callbacks: dict[object, Callable[[HubEvent], Any]] = {}
        self._tasks: set[asyncio.Task[Any]] = set()
        self._closed = False

    def _schedule(self, awaitable: Any) -> None:
        task = asyncio.create_task(awaitable)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _emit(self, event: HubEvent) -> None:
        for callback in list(self._callbacks.values()):
            await self._deliver(callback, event)

    async def _deliver(self, callback: Callable[[HubEvent], Any], event: HubEvent) -> None:
        try:
            result = callback(deepcopy(event))
            if inspect.isawaitable(result):
                await result
        except Exception:
            _LOG.exception("Hub subscriber failed")

    async def _publish_snapshot(self, snapshot: HubSnapshot) -> None:
        before = project(self._snapshot)
        after = project(snapshot)
        self._snapshot = deepcopy(snapshot)
        for old, new in zip(before, after, strict=True):
            if old != new:
                await self._emit(new)

    async def _start_events(self) -> None:
        """Start a transport's event source after the initial projection."""

    def subscribe(self, callback: Callable[[HubEvent], Any]) -> Callable[[], None]:
        if self._closed:
            raise RuntimeError("Hub client is closed")
        token = object()
        self._callbacks[token] = callback

        async def initial() -> None:
            try:
                snapshot = await self.snapshot()  # type: ignore[attr-defined]
                for event in project(snapshot):
                    if token not in self._callbacks:
                        break
                    await self._deliver(callback, event)
                if token in self._callbacks:
                    await self._start_events()
            except Exception:
                _LOG.exception("Initial hub snapshot failed")

        self._schedule(initial())

        def unsubscribe() -> None:
            self._callbacks.pop(token, None)

        return unsubscribe

    async def _close_events(self) -> None:
        self._closed = True
        self._callbacks.clear()
        tasks = list(self._tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()
