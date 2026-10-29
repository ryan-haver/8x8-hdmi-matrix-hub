"""In-process client for a state provider, or OreiMatrix plus hub callbacks.

The provider may implement HubClient itself. For OreiMatrix, inject hub-owned
``snapshot_provider``, ``action_runner`` and ``event_subscribe`` callbacks to
include catalogs and settings and to follow front-panel changes. This client
never starts a poller and never disconnects the shared matrix on close.
"""

import asyncio
import inspect
import logging
from collections.abc import Awaitable, Callable
from copy import deepcopy
from typing import Any

from .hub_client import EventPublisher, HubClient, HubEvent, HubSnapshot, apply_status, port_map, project

_LOG = logging.getLogger(__name__)


class HubClientLocal(EventPublisher, HubClient):
    def __init__(
        self,
        provider: Any,
        *,
        snapshot_provider: Callable[[], HubSnapshot | Awaitable[HubSnapshot]] | None = None,
        action_runner: Callable[..., Awaitable[dict[str, Any]]] | None = None,
        event_subscribe: Callable[[Callable[[HubEvent], Any]], Callable[[], None]] | None = None,
    ) -> None:
        super().__init__()
        self.provider = provider
        self._snapshot_provider = snapshot_provider or getattr(provider, "snapshot", None)
        self._action_runner = action_runner or getattr(provider, "run_action", None)
        self._shared_action_runner = action_runner is not None
        self._unsubscribe: Callable[[], None] | None = None
        self._event_subscribe = event_subscribe or getattr(provider, "subscribe", None)
        self._cycle_lock = asyncio.Lock()
        self._refresh_lock = asyncio.Lock()
        self._projection_version = 0

    async def snapshot(self) -> HubSnapshot:
        if self._closed:
            raise RuntimeError("Hub client is closed")
        if self._snapshot_provider is not None:
            state = self._snapshot_provider()
            if inspect.isawaitable(state):
                state = await state
            return deepcopy(state)
        state = deepcopy(self._snapshot)
        state.connected = self.provider.connected is True
        if state.connected:
            apply_status(state, await self.provider.get_full_status())
            apply_status(state, await self.provider.get_status())
            cables = await self.provider.get_all_cable_status()
            state.input_cables = {
                port: bool(value) for port, value in port_map(cables.get("inputs", {})).items() if value is not None
            }
        return state

    async def _refresh(self) -> None:
        async with self._refresh_lock:
            previous = deepcopy(self._snapshot)
            state = await self.snapshot()
            self._snapshot = previous
            self._projection_version += 1
            await self._publish_snapshot(state)

    def _changed(self, event: HubEvent) -> None:
        if not self._closed:
            # Output cable detection has no field in HubSnapshot, but integrations
            # still receive the port notification from the hub's event bus.
            if event.kind == "catalog" or (event.kind == "cable" and event.data.get("type") == "output"):
                self._schedule(self._emit(event))
            self._schedule(self._refresh())

    def subscribe(self, callback: Callable[[HubEvent], Any]) -> Callable[[], None]:
        if self._closed:
            raise RuntimeError("Hub client is closed")
        token = object()
        pending = []
        initializing = True

        async def ordered(event):
            if initializing:
                pending.append(deepcopy(event))
            else:
                await self._deliver(callback, event)

        self._callbacks[token] = ordered
        if self._unsubscribe is None and self._event_subscribe is not None:
            self._unsubscribe = self._event_subscribe(self._changed)

        async def initial():
            nonlocal initializing
            version = self._projection_version
            try:
                state = await self.snapshot()
            except Exception:
                initializing = False
                _LOG.exception("Initial hub snapshot failed")
                while pending and token in self._callbacks:
                    await self._deliver(callback, pending.pop(0))
                return
            if version == self._projection_version:
                self._snapshot = deepcopy(state)
            events = project(state) + [HubEvent("catalog", {
                "profiles": state.profiles, "scenes": state.scenes,
                "macros": state.macros, "shortcuts": state.shortcuts,
            })]
            for event in events:
                if token not in self._callbacks:
                    return
                await self._deliver(callback, event)
            # New deliveries append while callbacks yield; drain them before
            # opening live delivery so an initial snapshot cannot overtake a write.
            while pending and token in self._callbacks:
                await self._deliver(callback, pending.pop(0))
            initializing = False

        self._schedule(initial())

        def unsubscribe():
            self._callbacks.pop(token, None)

        return unsubscribe

    async def _command(self, method: str, *args: Any, **kwargs: Any) -> bool:
        if self._closed:
            raise RuntimeError("Hub client is closed")
        if not (await self.snapshot()).connected:
            return False
        success = bool(await getattr(self.provider, method)(*args, **kwargs))
        if success:
            await self._refresh()
        return success

    async def switch(self, input_num: int, output_num: int | None = None) -> bool:
        if not 1 <= input_num <= 8 or (output_num is not None and not 1 <= output_num <= 8):
            return False
        if hasattr(self.provider, "switch"):
            return await self._command("switch", input_num, output_num)
        if output_num is None:
            return await self._command("switch_input_to_all", input_num)
        return await self._command("switch_input", input_num, output_num)

    async def cycle_input(self, direction: str, output_num: int = 1, *, cycle: bool = True) -> bool:
        if direction not in {"next", "previous"}:
            raise ValueError("direction must be next or previous")
        async with self._cycle_lock:
            if hasattr(self.provider, "cycle_input"):
                # Preserve old provider calls byte-for-byte for the default.
                kwargs = {} if cycle else {"cycle": False}
                return await self._command("cycle_input", direction, output_num, **kwargs)
            state = await self.snapshot()
            current = state.routing.get(output_num)
            if not state.connected or current is None:
                return False
            target = current + (1 if direction == "next" else -1)
            target = (target - 1) % 8 + 1 if cycle else min(8, max(1, target))
            return await self.switch(target, output_num)

    async def recall_preset(self, preset: int) -> bool:
        if self._shared_action_runner:
            if not 1 <= preset <= 8:
                return False
            return bool((await self.run_action("preset", str(preset))).get("success"))
        return await self._command("recall_preset", preset) if 1 <= preset <= 8 else False

    async def save_preset(self, preset: int) -> bool:
        return await self._command("save_preset", preset) if 1 <= preset <= 8 else False

    async def power(self, on: bool) -> bool:
        if hasattr(self.provider, "power"):
            return await self._command("power", on)
        return await self._command("power_on" if on else "power_off")

    async def send_cec(self, target_kind: str, port: int, command: str) -> bool:
        if target_kind not in {"input", "output"}:
            raise ValueError("target_kind must be input or output")
        if not 1 <= port <= 8:
            return False
        if self._snapshot_provider is not None and hasattr(self.provider, "snapshot"):
            return await self._command("send_cec", target_kind, port, command)
        return await self._command("send_cec", command, port, is_output=target_kind == "output")

    async def run_action(self, kind: str, action_id: str, *, passcode: str | None = None) -> dict[str, Any]:
        if kind not in {"profile", "scene", "shortcut", "macro", "preset"}:
            raise ValueError(f"Unknown action kind: {kind}")
        if self._closed:
            raise RuntimeError("Hub client is closed")
        if self._action_runner is None:
            return {"success": False, "data": None, "error": "Action runner is not configured"}
        result = await self._action_runner(kind, action_id, passcode=passcode)
        await self._refresh()
        return result

    async def close(self) -> None:
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None
        await self._close_events()
