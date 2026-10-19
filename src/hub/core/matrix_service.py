"""The one owner of matrix connection and state (WP-C3, UC-17).

:class:`MatrixService` wraps a matrix client (:class:`orei_matrix.OreiMatrix`
or anything matching :class:`MatrixClient`), keeps the last known snapshot
and publishes each change on the :class:`~hub.core.EventBus`:

======================  ===============================================
topic                   published when
======================  ===============================================
``"hub_connection"``    the link to the matrix comes up or goes down
``"routing"``           an output's source changes (switch or refresh)
``"power"``             the matrix power state changes
``"names"``             any effective name changes (by the NameStore)
``"presets"``           a preset is recalled or saved
``"signal"``            an input's signal detection changes
``"cable"``             a cable is plugged or unplugged
``"display"``           an output's display/enable/ARC/mute state changes
======================  ===============================================

Port loops and checks go through the :class:`~hub.core.MatrixModel`, never a
hard-coded 8 (BE-26). The service has no default host: it uses the client's.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
import uuid
from collections.abc import Awaitable
from copy import deepcopy
from typing import Any, Protocol, TypeVar

from .event_bus import (
    TOPIC_CABLE,
    TOPIC_DISPLAY,
    TOPIC_HUB_CONNECTION,
    TOPIC_POWER,
    TOPIC_PRESETS,
    TOPIC_ROUTING,
    TOPIC_SIGNAL,
    EventBus,
)
from .models import BK808_MODEL, MatrixModel
from .name_store import NameStore

_LOG = logging.getLogger(__name__)

_T = TypeVar("_T")

MAX_NAME_LENGTH = 32
"""Longest name the matrix stores (its web interface allows 32 characters)."""

_INPUT_PREFIX = re.compile(r"^IN\d+-(.*)$", re.IGNORECASE)

_PORT_KINDS: dict[str, str] = {"input": "inputs", "inputs": "inputs", "output": "outputs", "outputs": "outputs"}

# get output status array -> display field
_DISPLAY_FIELDS: tuple[tuple[str, str], ...] = (
    ("allconnect", "connected"),
    ("allout", "enabled"),
    ("allarc", "arc"),
    ("allaudiomute", "audio_mute"),
)


class MatrixClient(Protocol):
    """What :class:`MatrixService` needs from a matrix client (OreiMatrix's API)."""

    host: str
    port: int

    @property
    def connected(self) -> bool: ...

    async def connect(self) -> bool: ...

    async def disconnect(self) -> Any: ...

    async def get_video_status(self) -> dict[str, Any] | None: ...

    async def get_input_status(self, force_refresh: bool = False) -> dict[str, Any] | None: ...

    async def get_output_status(self, force_refresh: bool = False) -> dict[str, Any] | None: ...

    async def get_all_cable_status(self, force_refresh: bool = False) -> dict[str, dict[int, bool | None]]: ...

    async def switch_input(self, input_num: int, output_num: int, /) -> bool: ...

    async def switch_input_to_all(self, input_num: int, /) -> bool: ...

    async def recall_preset(self, preset: int, /) -> bool: ...

    async def save_preset(self, preset_num: int, /) -> bool: ...

    async def power_on(self) -> bool: ...

    async def power_off(self) -> bool: ...

    async def set_input_name(self, input_num: int, name: str, /) -> bool: ...

    async def set_output_name(self, output_num: int, name: str, /) -> bool: ...

    async def set_preset_name(self, preset_num: int, name: str, /) -> bool: ...


def _flag(value: object) -> bool | None:
    """Device 1/0 flag as a bool; anything else is unknown."""
    if type(value) is int and value in (0, 1):
        return value == 1
    if isinstance(value, bool):
        return value
    return None


def _strip_input_prefix(name: object) -> object:
    # Older firmware reports "IN01-NES"; MCU V1.10.01 sends "NES" (see OreiMatrix.get_all_input_names).
    if isinstance(name, str):
        match = _INPUT_PREFIX.match(name)
        if match:
            return match.group(1)
    return name


class MatrixService:
    """Connection, last known state and every write to one matrix."""

    def __init__(
        self,
        client: MatrixClient,
        model: MatrixModel = BK808_MODEL,
        names: NameStore | None = None,
        bus: EventBus | None = None,
    ) -> None:
        if names is not None:
            if names.model != model:
                raise ValueError(f"NameStore is for {names.model.model_id}, service for {model.model_id}")
            if bus is not None and names.bus is not None and names.bus is not bus:
                raise ValueError("NameStore publishes on a different EventBus")
            bus = bus or names.bus
        self._client = client
        self._client_generation = 0
        self._raw: dict[str, Any] = {}
        self._model = model
        self._bus = bus if bus is not None else EventBus()
        self._names = names if names is not None else NameStore(model, self._bus)
        if self._names.bus is None:
            raise ValueError("NameStore needs the service's EventBus to announce renames")

        self._connected = False
        self._last_error: str | None = None
        self._last_refresh: float | None = None
        self._routing: dict[int, int | None] = dict.fromkeys(model.output_range())
        self._power: bool | None = None
        self._signal: dict[int, bool | None] = dict.fromkeys(model.input_range())
        self._cables: dict[str, dict[int, bool | None]] = {
            "inputs": dict.fromkeys(model.input_range()),
            "outputs": dict.fromkeys(model.output_range()),
        }
        self._display: dict[int, dict[str, bool | None]] = {
            o: dict.fromkeys(field for _, field in self._display_fields()) for o in model.output_range()
        }
        # Bumped by every accepted write: a refresh that started before the
        # write must not put the old routing/power/names back.
        self._write_generation = 0
        self._refresh_lock = asyncio.Lock()

    # -- read-only state --------------------------------------------------

    @property
    def client(self) -> MatrixClient:
        return self._client

    @property
    def model(self) -> MatrixModel:
        return self._model

    @property
    def bus(self) -> EventBus:
        return self._bus

    @property
    def names(self) -> NameStore:
        return self._names

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def host(self) -> str | None:
        return self._client.host or None

    @property
    def port(self) -> int:
        return int(self._client.port)

    @property
    def last_error(self) -> str | None:
        return self._last_error

    @property
    def routing(self) -> dict[int, int | None]:
        """Output -> input routed to it (None = unknown)."""
        return dict(self._routing)

    @property
    def inputs(self) -> dict[int, str]:
        return self._names.snapshot()["inputs"]

    @property
    def outputs(self) -> dict[int, str]:
        return self._names.snapshot()["outputs"]

    @property
    def presets(self) -> dict[int, str]:
        return self._names.snapshot()["presets"]

    @property
    def power(self) -> bool | None:
        return self._power

    @property
    def signal(self) -> dict[int, bool | None]:
        """Input -> signal detected (None = unknown)."""
        return dict(self._signal)

    @property
    def cables(self) -> dict[str, dict[int, bool | None]]:
        return {side: dict(ports) for side, ports in self._cables.items()}

    @property
    def display(self) -> dict[int, dict[str, bool | None]]:
        return {o: dict(fields) for o, fields in self._display.items()}

    def snapshot(self) -> dict[str, Any]:
        """Everything the hub knows about the matrix, as plain copies."""
        names = self._names.snapshot()
        return {
            "connected": self._connected,
            "host": self.host,
            "port": self.port,
            "last_error": self._last_error,
            "last_refresh": self._last_refresh,
            "model": {
                "model_id": self._model.model_id,
                "name": self._model.name,
                "input_count": self._model.input_count,
                "output_count": self._model.output_count,
                "preset_count": self._model.preset_count,
            },
            "routing": self.routing,
            "power": self._power,
            "inputs": names["inputs"],
            "outputs": names["outputs"],
            "presets": names["presets"],
            "signal": self.signal,
            "cables": self.cables,
            "display": self.display,
        }

    # -- connection -------------------------------------------------------

    def replace_client(self, client: MatrixClient, *, names: NameStore | None = None) -> None:
        """Reset state at a transaction boundary; old reads cannot commit afterward."""
        self._client_generation += 1
        self._client = client
        self._raw = {}
        self._routing = dict.fromkeys(self._model.output_range())
        self._power = None
        self._signal = dict.fromkeys(self._model.input_range())
        self._cables = {"inputs": dict.fromkeys(self._model.input_range()),
                        "outputs": dict.fromkeys(self._model.output_range())}
        self._display = {o: dict.fromkeys(f for _, f in self._display_fields()) for o in self._model.output_range()}
        self._last_refresh = None
        self._last_error = None
        self._names = names if names is not None else NameStore(self._model, self._bus)
        self._set_connected(False)

    def raw_snapshot(self) -> dict[str, Any]:
        """Lossless protocol fields plus current command-confirmed state for REST."""
        raw = deepcopy(self._raw)
        if "video" in raw:
            raw["video"].update(allsource=[self._routing[o] for o in self._model.output_range()],
                                 power=int(self._power) if self._power is not None else None,
                                 allinputname=list(self.inputs.values()), alloutputname=list(self.outputs.values()),
                                 allname=list(self.presets.values()))
        if "status" in raw:
            raw["status"].update(
                routing=[self._routing[o] for o in self._model.output_range()],
                power="on" if self._power else "off", connected=self.connected,
                host=self.host, port=self.port,
                input_names=list(self.inputs.values()), output_names=list(self.outputs.values()),
                preset_names=list(self.presets.values()),
            )
        return raw

    def _set_connected(self, connected: bool, error: str | None = None) -> None:
        if error is not None:
            self._last_error = error
        elif connected:
            self._last_error = None
        if connected == self._connected:
            return
        self._connected = connected
        _LOG.info("Matrix %s %s", self.host, "connected" if connected else "disconnected")
        self._bus.publish(
            TOPIC_HUB_CONNECTION,
            {"connected": connected, "host": self.host, "port": self.port, "error": self._last_error},
        )

    def _sync_connection(self) -> None:
        """Take the client's view of the link (it notices drops on any request)."""
        try:
            connected = bool(self._client.connected)
        except Exception:
            _LOG.exception("Reading the matrix client's connection state failed")
            return
        self._set_connected(connected)

    async def _safe(self, what: str, call: Awaitable[_T]) -> _T | None:
        generation = self._client_generation
        client = self._client
        try:
            return await call
        except Exception as exc:
            message = str(exc)
            for field in ("password", "user", "_user"):
                secret = getattr(client, field, None)
                if isinstance(secret, str) and secret:
                    message = message.replace(secret, "[redacted]")
            reference = uuid.uuid4().hex[:8]
            _LOG.error("[%s] Matrix %s failed: %s", reference, what, message)
            if generation == self._client_generation:
                self._last_error = f"Internal server error (ref: {reference})"
            return None

    async def connect(self) -> bool:
        """Connect to the matrix and, once connected, read the full snapshot."""
        if not self.host:
            self._set_connected(False, "no matrix host configured")
            return False
        ok = bool(await self._safe("connect", self._client.connect()))
        self._set_connected(ok, None if ok else (self._last_error or "connect failed"))
        if ok:
            await self.refresh_snapshot()
        return ok

    async def disconnect(self) -> None:
        await self._safe("disconnect", self._client.disconnect())
        self._set_connected(False)

    # -- snapshot ---------------------------------------------------------

    def _display_fields(self) -> list[tuple[str, str]]:
        return [(key, f) for key, f in _DISPLAY_FIELDS if f != "arc" or self._model.supports_arc]

    def invalidate_preset_cache(self) -> None:
        """Expire slot readback for an explicit status refresh, when supported.

        Older structural clients have no slot cache. Keep them compatible while
        the sole protocol client owns its own cache lifecycle.
        """
        invalidate = getattr(self._client, "invalidate_preset_cache", None)
        if callable(invalidate):
            invalidate()

    def invalidate_cec_cache(self) -> None:
        """Expire CEC enable decisions on explicit status synchronization.

        The protocol client refreshes flags lazily before the next CEC command.
        Structural clients without a CEC cache need no invalidation.
        """
        invalidate = getattr(self._client, "clear_cec_cache", None)
        if callable(invalidate):
            invalidate()

    async def refresh_snapshot(self) -> bool:
        """Read the matrix and publish what changed. False if the main status read failed.

        ``get video status`` (routing, power, names) must succeed; the signal,
        cable and display reads are best effort and leave their part as it was.
        """
        async with self._refresh_lock:
            previous_raw = deepcopy(self._raw)
            client = self._client
            client_generation = self._client_generation
            generation = self._write_generation
            video = await self._safe("status read", client.get_video_status())
            if client_generation != self._client_generation:
                return False
            if not isinstance(video, dict):
                self._sync_connection()
                return False
            if generation == self._write_generation:  # no write landed meanwhile
                self._apply_video_status(video)
                self._raw["video"] = deepcopy(video)
                self._raw["status"] = {"routing": deepcopy(video.get("allsource", [])),
                                       "power": "on" if video.get("power") == 1 else "off"}

            input_status = await self._safe("input status read", client.get_input_status(force_refresh=True))
            if client_generation != self._client_generation:
                return False
            if isinstance(input_status, dict):
                self._raw["inputs"] = deepcopy(input_status)
                self._apply_signal(input_status)

            cables = await self._safe("cable status read", client.get_all_cable_status(force_refresh=True))
            if client_generation != self._client_generation:
                return False
            if isinstance(cables, dict):
                self._raw["cables"] = deepcopy(cables)
                self._apply_cables(cables)

            output_status = await self._safe("output status read", client.get_output_status(force_refresh=True))
            if client_generation != self._client_generation:
                return False
            if isinstance(output_status, dict):
                self._raw["outputs"] = deepcopy(output_status)
                self._apply_display(output_status)

            self._last_refresh = time.time()
            self._sync_connection()
            if self._raw != previous_raw:
                self._bus.publish("snapshot", {})
            return True

    def _apply_video_status(self, video: dict[str, Any]) -> None:
        allsource = video.get("allsource")
        if isinstance(allsource, list):
            routing: dict[int, int | None] = {}
            for output in self._model.output_range():
                src = allsource[output - 1] if output - 1 < len(allsource) else None
                routing[output] = src if type(src) is int and src in self._model.input_range() else None
            self._update_routing(routing, "refresh")

        power = _flag(video.get("power"))
        if power is not None:
            self._update_power(power, "refresh")

        def names(key: str) -> list[object] | None:
            value = video.get(key)
            return list(value) if isinstance(value, list) else None

        inputs = names("allinputname")
        self._names.apply_device_names(
            inputs=[_strip_input_prefix(n) for n in inputs] if inputs is not None else None,
            outputs=names("alloutputname"),
            presets=names("allname"),
        )

    def _apply_signal(self, input_status: dict[str, Any]) -> None:
        # "inactive" is misnamed by the device: 1 = signal present (driver.py, cec_resolver.py).
        inactive = input_status.get("inactive")
        if not isinstance(inactive, list):
            return
        signal = {i: _flag(inactive[i - 1]) if i - 1 < len(inactive) else None for i in self._model.input_range()}
        changed = {i: v for i, v in signal.items() if self._signal.get(i) != v}
        if changed:
            self._signal = signal
            self._bus.publish(TOPIC_SIGNAL, {"signal": dict(signal), "changed": changed})

    def _apply_cables(self, cables: dict[str, Any]) -> None:
        new: dict[str, dict[int, bool | None]] = {}
        for side, ports in (("inputs", self._model.input_range()), ("outputs", self._model.output_range())):
            reported = cables.get(side)
            reported = reported if isinstance(reported, dict) else {}
            new[side] = {p: _flag(reported.get(p)) for p in ports}
        changed = {side: {p: v for p, v in new[side].items() if self._cables[side].get(p) != v} for side in new}
        changed = {side: ports for side, ports in changed.items() if ports}
        if changed:
            self._cables = new
            self._bus.publish(TOPIC_CABLE, {"cables": self.cables, "changed": changed})

    def _apply_display(self, output_status: dict[str, Any]) -> None:
        new = {o: dict(fields) for o, fields in self._display.items()}
        for key, field in self._display_fields():
            values = output_status.get(key)
            if not isinstance(values, list):
                continue  # not reported: keep what we knew
            for o in self._model.output_range():
                new[o][field] = _flag(values[o - 1]) if o - 1 < len(values) else None
        changed = {o: fields for o, fields in new.items() if fields != self._display[o]}
        if changed:
            self._display = new
            self._bus.publish(TOPIC_DISPLAY, {"display": self.display, "changed": changed})

    def _update_routing(self, routing: dict[int, int | None], source: str) -> None:
        changed = {o: i for o, i in routing.items() if self._routing.get(o) != i}
        if not changed:
            return
        self._routing.update(routing)
        self._bus.publish(TOPIC_ROUTING, {"routing": self.routing, "changed": changed, "source": source})

    def _update_power(self, power: bool, source: str) -> None:
        if power == self._power:
            return
        self._power = power
        self._bus.publish(TOPIC_POWER, {"power": power, "source": source})

    # -- writes -----------------------------------------------------------

    async def _write(self, what: str, call: Awaitable[bool], *, propagate_errors: bool = False) -> bool:
        try:
            if propagate_errors:
                try:
                    ok = bool(await call)
                except Exception:
                    # The caller logs the exception with its public correlation
                    # reference. Health and connection events retain no details.
                    self._last_error = f"{what} failed"
                    raise
            else:
                ok = bool(await self._safe(what, call))
        finally:
            self._sync_connection()
        if ok:
            self._write_generation += 1
        return ok

    async def switch(self, input_num: int, output_num: int | None = None) -> bool:
        """Route ``input_num`` to ``output_num``, or to every output if None."""
        self._model.validate_input(input_num)
        if output_num is None:
            ok = await self._write(f"switch input {input_num} to all", self._client.switch_input_to_all(input_num))
            targets = list(self._model.output_range())
        else:
            self._model.validate_output(output_num)
            ok = await self._write(
                f"switch input {input_num} to output {output_num}",
                self._client.switch_input(input_num, output_num),
            )
            targets = [output_num]
        if ok:
            self._update_routing(dict.fromkeys(targets, input_num), "switch")
        return ok

    async def recall_preset(self, preset: int, *, propagate_errors: bool = False) -> bool:
        """Recall and refresh; optionally propagate client errors to the action runner."""
        self._model.validate_preset(preset)
        if not await self._write(
            f"recall preset {preset}", self._client.recall_preset(preset), propagate_errors=propagate_errors
        ):
            return False
        self._bus.publish(
            TOPIC_PRESETS, {"action": "recall", "preset": preset, "name": self._names.preset_name(preset)}
        )
        await self.refresh_snapshot()
        return True

    async def save_preset(self, preset: int) -> bool:
        """Save the current routing as ``preset``."""
        self._model.validate_preset(preset)
        if not await self._write(f"save preset {preset}", self._client.save_preset(preset)):
            return False
        self._bus.publish(
            TOPIC_PRESETS,
            {
                "action": "save",
                "preset": preset,
                "name": self._names.preset_name(preset),
                "routing": self.routing,
            },
        )
        return True

    async def set_power(self, on: bool) -> bool:
        """Turn the matrix on or off."""
        call = self._client.power_on() if on else self._client.power_off()
        if not await self._write(f"power {'on' if on else 'off'}", call):
            return False
        self._update_power(bool(on), "command")
        return True

    @staticmethod
    def _clean_name(name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        return name.strip()[:MAX_NAME_LENGTH]

    async def rename_port(self, kind: str, port: int, name: str) -> bool:
        """Rename an input or output on the matrix (``kind`` "input"/"output").

        On success the NameStore records the device name (dropping any
        override), which publishes one ``"names"`` event.
        """
        store_kind = _PORT_KINDS.get(kind)
        if store_kind is None:
            raise ValueError(f"kind must be 'input' or 'output', got {kind!r}")
        name = self._clean_name(name)
        if store_kind == "inputs":
            self._model.validate_input(port)
            call = self._client.set_input_name(port, name)
        else:
            self._model.validate_output(port)
            call = self._client.set_output_name(port, name)
        if not await self._write(f"rename {kind} {port}", call):
            return False
        self._names.set_device_name(store_kind, port, name)
        return True

    async def rename_preset(self, preset: int, name: str) -> bool:
        """Rename a preset on the matrix; publishes a ``"names"`` event on success."""
        self._model.validate_preset(preset)
        name = self._clean_name(name)
        if not await self._write(f"rename preset {preset}", self._client.set_preset_name(preset, name)):
            return False
        self._names.set_device_name("presets", preset, name)
        return True
