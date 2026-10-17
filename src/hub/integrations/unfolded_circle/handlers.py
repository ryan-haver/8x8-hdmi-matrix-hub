"""Command dispatcher for the Unfolded Circle Remote 3 integration (UC-01, UC-08, UC-10, UC-12, DI-9)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .entities import CEC_COMMAND_ALIASES
from .state import EntityStateProjector

_LOG = logging.getLogger("uc.handlers")

STATUS_OK = 200
STATUS_BAD_REQUEST = 400
STATUS_NOT_FOUND = 404
STATUS_SERVER_ERROR = 500
STATUS_NOT_IMPLEMENTED = 501
STATUS_SERVICE_UNAVAILABLE = 503

MAX_CMD_REPEAT = 20
MAX_CMD_DELAY_MS = 5000
DEFAULT_CMD_DELAY_MS = 0


def _bounded_non_negative_int(params: dict[str, Any], key: str, default: int, maximum: int) -> int:
    raw = params.get(key)
    if raw is None:
        return default
    if isinstance(raw, bool):
        raise ValueError(f"{key} must be an integer")
    val = int(raw)
    if val < 0:
        raise ValueError(f"{key} must not be negative")
    return min(val, maximum)


def parse_command_timing(params: dict[str, Any] | None) -> tuple[int, int, int]:
    """Parse `(repeat, delay_ms, hold_ms)` from UC remote command parameters."""
    params = params or {}
    repeat = max(1, _bounded_non_negative_int(params, "repeat", 1, MAX_CMD_REPEAT))
    delay = _bounded_non_negative_int(params, "delay", DEFAULT_CMD_DELAY_MS, MAX_CMD_DELAY_MS)
    hold = _bounded_non_negative_int(params, "hold", 0, MAX_CMD_DELAY_MS)
    return repeat, delay, hold


def extract_command_sequence(cmd_id: str, params: dict[str, Any] | None) -> list[str] | None:
    """Extract simple command strings for `send_cmd` or `send_cmd_sequence`."""
    params = params or {}
    if cmd_id == "send_cmd":
        cmd = params.get("command")
        if isinstance(cmd, str) and cmd.strip():
            return [cmd.strip()]
        return None
    if cmd_id == "send_cmd_sequence":
        seq = params.get("sequence")
        if isinstance(seq, str):
            seq = [part.strip() for part in seq.split(",") if part.strip()]
        if not isinstance(seq, list) or not seq:
            return None
        cleaned = [item.strip() for item in seq if isinstance(item, str) and item.strip()]
        if len(cleaned) != len(seq):
            return None
        return cleaned
    return None


class UCCommandDispatcher:
    """Routes Unfolded Circle entity commands to ``hub_client`` with exception isolation (`UC-01`)."""

    def __init__(
        self,
        hub_client: Any,
        projector: EntityStateProjector | None = None,
        *,
        port_count: int = 8,
    ) -> None:
        self.hub_client = hub_client
        self.projector = projector if projector is not None else EntityStateProjector(port_count=port_count)
        self.port_count = port_count
        self._blocked_profiles: set[str] = set()
        self._blocked_scenes: set[str] = set()

    def update_pin_blocks(self, snapshot: dict[str, Any] | None) -> None:
        """Record PIN-protected profiles/scenes that are not allowed on the Remote (§4.2)."""
        self._blocked_profiles.clear()
        self._blocked_scenes.clear()
        if not snapshot:
            return
        for key, target_set in (("profiles", self._blocked_profiles), ("scenes", self._blocked_scenes)):
            raw = snapshot.get(key)
            items = raw.values() if isinstance(raw, dict) else (raw if isinstance(raw, list) else [])
            for item in items:
                if not isinstance(item, dict):
                    continue
                item_id = str(item.get("id") or "").strip()
                if not item_id:
                    continue
                has_pin = bool(
                    item.get("has_pin")
                    or item.get("pin_protected")
                    or item.get("passcode_required")
                    or item.get("pin")
                    or item.get("passcode")
                )
                allow_remote = bool(item.get("allow_remote") or item.get("remote_allowed"))
                if has_pin and not allow_remote:
                    target_set.add(item_id)

    def _is_available(self) -> bool:
        if self.hub_client is None:
            return False
        if getattr(self.hub_client, "connected", True) is False:
            return False
        if not self.projector.connected:
            return False
        return True

    async def __call__(
        self,
        entity: Any,
        cmd_id: str,
        params: dict[str, Any] | None = None,
        websocket: Any = None,
    ) -> int:
        entity_id = (
            entity
            if isinstance(entity, str)
            else (entity.get("entity_id") if isinstance(entity, dict) else getattr(entity, "id", ""))
        )
        return await self.dispatch(str(entity_id), cmd_id, params)

    async def handle(
        self,
        entity_id: str | Any,
        cmd_id: str,
        params: dict[str, Any] | None = None,
    ) -> int:
        """Alias for :meth:`dispatch`."""
        return await self.dispatch(entity_id, cmd_id, params)

    async def dispatch(
        self,
        entity_id: str | Any,
        cmd_id: str,
        params: dict[str, Any] | None = None,
    ) -> int:
        """Dispatch a command for ``entity_id`` and return an HTTP-like UC status code (`200`, `400`, `501`, `503`, `500`)."""
        if not isinstance(entity_id, str):
            entity_id = (
                entity_id.get("entity_id", "")
                if isinstance(entity_id, dict)
                else getattr(entity_id, "id", "")
            )
        try:
            if not self._is_available():
                return STATUS_SERVICE_UNAVAILABLE

            if entity_id == "remote.orei_matrix":
                return await self._handle_matrix_remote(cmd_id, params)

            if entity_id == "switch.matrix_power":
                return await self._handle_matrix_power(cmd_id)

            if entity_id.startswith("button.preset_"):
                return await self._handle_preset_button(entity_id, cmd_id)

            if entity_id.startswith("media_player.output_"):
                return await self._handle_media_player(entity_id, cmd_id, params)

            if entity_id.startswith("select.output_") and entity_id.endswith("_source"):
                return await self._handle_select_source(entity_id, cmd_id, params)

            if entity_id.startswith("remote.input_") and entity_id.endswith("_cec"):
                port_str = entity_id.removeprefix("remote.input_").removesuffix("_cec")
                return await self._handle_cec_remote("input", int(port_str), cmd_id, params)

            if entity_id.startswith("remote.output_") and entity_id.endswith("_cec"):
                port_str = entity_id.removeprefix("remote.output_").removesuffix("_cec")
                return await self._handle_cec_remote("output", int(port_str), cmd_id, params)

            return STATUS_BAD_REQUEST
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOG.exception("Unhandled exception executing %s on %s", cmd_id, entity_id)
            return STATUS_SERVER_ERROR

    # ------------------------------------------------------------------
    # Per-entity-type handlers
    # ------------------------------------------------------------------

    async def _handle_preset_button(self, entity_id: str, cmd_id: str) -> int:
        if cmd_id != "push":
            return STATUS_NOT_IMPLEMENTED
        try:
            preset_num = int(entity_id.removeprefix("button.preset_"))
        except ValueError:
            return STATUS_BAD_REQUEST
        if not (1 <= preset_num <= self.port_count):
            return STATUS_BAD_REQUEST
        ok = await self._call_recall_preset(preset_num)
        return STATUS_OK if ok else STATUS_SERVER_ERROR

    async def _handle_matrix_power(self, cmd_id: str) -> int:
        norm = cmd_id.strip().lower()
        if norm not in ("on", "off", "toggle"):
            return STATUS_NOT_IMPLEMENTED
        if norm == "toggle":
            turn_on = self.projector.resolve_toggle("switch.matrix_power") == "ON"
        else:
            turn_on = norm == "on"
        ok = await self._call_power(turn_on)
        if ok:
            self.projector.record_power("switch.matrix_power", on=turn_on)
            return STATUS_OK
        return STATUS_SERVER_ERROR

    def _resolve_input_from_name(self, source_name: Any) -> int | None:
        if not isinstance(source_name, str) or not source_name.strip():
            return None
        target = source_name.strip()
        for num, name in self.projector.input_names.items():
            if name == target:
                return num
        if target.lower().startswith("input "):
            try:
                num = int(target.split(" ", 1)[1])
                if 1 <= num <= self.port_count:
                    return num
            except ValueError:
                return None
        return None

    async def _handle_media_player(
        self,
        entity_id: str,
        cmd_id: str,
        params: dict[str, Any] | None,
    ) -> int:
        try:
            output_num = int(entity_id.removeprefix("media_player.output_"))
        except ValueError:
            return STATUS_BAD_REQUEST
        if not (1 <= output_num <= self.port_count):
            return STATUS_BAD_REQUEST

        norm = cmd_id.strip().lower()
        params = params or {}

        if norm == "select_source":
            input_num = self._resolve_input_from_name(params.get("source"))
            if input_num is None:
                return STATUS_BAD_REQUEST
            ok = await self._call_switch(input_num, output_num)
            if ok:
                self.projector.apply_event("routing", {"output": output_num, "input": input_num})
                return STATUS_OK
            return STATUS_SERVER_ERROR

        if norm in ("on", "off", "toggle"):
            if norm == "toggle":
                turn_on = self.projector.resolve_toggle("output", output_num) == "ON"
            else:
                turn_on = norm == "on"
            cec_cmd = "POWER_ON" if turn_on else "POWER_OFF"
            ok = await self._call_send_cec("output", output_num, cec_cmd)
            if ok:
                self.projector.record_power("output", output_num, on=turn_on)
                return STATUS_OK
            return STATUS_SERVER_ERROR

        if norm == "volume_up":
            ok = await self._call_send_cec("output", output_num, "VOLUME_UP")
            return STATUS_OK if ok else STATUS_SERVER_ERROR

        if norm == "volume_down":
            ok = await self._call_send_cec("output", output_num, "VOLUME_DOWN")
            return STATUS_OK if ok else STATUS_SERVER_ERROR

        if norm in ("mute_toggle", "mute"):
            ok = await self._call_send_cec("output", output_num, "MUTE")
            return STATUS_OK if ok else STATUS_SERVER_ERROR

        return STATUS_NOT_IMPLEMENTED

    async def _handle_select_source(
        self,
        entity_id: str,
        cmd_id: str,
        params: dict[str, Any] | None,
    ) -> int:
        try:
            output_num = int(entity_id.removeprefix("select.output_").removesuffix("_source"))
        except ValueError:
            return STATUS_BAD_REQUEST
        if not (1 <= output_num <= self.port_count):
            return STATUS_BAD_REQUEST

        norm = cmd_id.strip().lower()
        params = params or {}

        if norm == "select_option":
            option = params.get("option", params.get("source"))
            input_num = self._resolve_input_from_name(option)
            if input_num is None:
                return STATUS_BAD_REQUEST
        elif norm == "select_first":
            input_num = 1
        elif norm == "select_last":
            input_num = self.port_count
        elif norm in ("select_next", "select_previous"):
            current = self.projector.routed_inputs.get(output_num, 1)
            cycle = bool(params.get("cycle", True))
            step = 1 if norm == "select_next" else -1
            nxt = current + step
            if cycle:
                input_num = ((nxt - 1) % self.port_count) + 1
            else:
                input_num = max(1, min(self.port_count, nxt))
        else:
            return STATUS_NOT_IMPLEMENTED

        ok = await self._call_switch(input_num, output_num)
        if ok:
            self.projector.apply_event("routing", {"output": output_num, "input": input_num})
            return STATUS_OK
        return STATUS_SERVER_ERROR

    async def _handle_cec_remote(
        self,
        port_type: str,
        port_num: int,
        cmd_id: str,
        params: dict[str, Any] | None,
    ) -> int:
        if not (1 <= port_num <= self.port_count):
            return STATUS_BAD_REQUEST

        norm = cmd_id.strip().lower()
        if norm in ("on", "off", "toggle"):
            if norm == "toggle":
                turn_on = self.projector.resolve_toggle(port_type, port_num) == "ON"
            else:
                turn_on = norm == "on"
            commands = ["POWER_ON" if turn_on else "POWER_OFF"]
            repeat, delay, hold = 1, 0, 0
        elif norm in ("send_cmd", "send_cmd_sequence"):
            raw_commands = extract_command_sequence(norm, params)
            if raw_commands is None:
                return STATUS_BAD_REQUEST
            try:
                repeat, delay, hold = parse_command_timing(params)
            except (TypeError, ValueError):
                return STATUS_BAD_REQUEST
            commands = []
            for raw_cmd in raw_commands:
                mapped = CEC_COMMAND_ALIASES.get(raw_cmd.strip().upper())
                if mapped is None:
                    return STATUS_BAD_REQUEST
                commands.append(mapped)
        else:
            return STATUS_NOT_IMPLEMENTED

        first = True
        for cec_cmd in commands:
            for _ in range(repeat):
                if not first and delay > 0:
                    await asyncio.sleep(delay / 1000.0)
                first = False
                ok = await self._call_send_cec(port_type, port_num, cec_cmd)
                if not ok:
                    return STATUS_SERVER_ERROR
                if cec_cmd in ("POWER_ON", "POWER_OFF"):
                    self.projector.record_power(port_type, port_num, on=(cec_cmd == "POWER_ON"))
                if hold > 0:
                    await asyncio.sleep(hold / 1000.0)

        return STATUS_OK

    def _parse_matrix_command(self, raw_cmd: str) -> tuple[str, Any] | None:
        token = raw_cmd.strip()
        upper = token.upper()

        if upper.startswith("PRESET_"):
            try:
                num = int(token.split("_", 1)[1])
            except ValueError:
                return None
            return ("preset", num) if 1 <= num <= self.port_count else None

        if upper.startswith("ROUTE_ALL_IN_"):
            try:
                num = int(token.rsplit("_", 1)[1])
            except ValueError:
                return None
            return ("route_all", num) if 1 <= num <= self.port_count else None

        if upper.startswith("PROFILE_"):
            item_id = token[len("PROFILE_") :].strip()
            if not item_id or item_id in self._blocked_profiles:
                return None
            return ("profile", item_id)

        if upper.startswith("SCENE_"):
            item_id = token[len("SCENE_") :].strip()
            if not item_id or item_id in self._blocked_scenes:
                return None
            return ("scene", item_id)

        if upper.startswith("SHORTCUT_"):
            item_id = token[len("SHORTCUT_") :].strip()
            return ("shortcut", item_id) if item_id else None

        if upper.startswith("MACRO_"):
            item_id = token[len("MACRO_") :].strip()
            return ("macro", item_id) if item_id else None

        return None

    async def _handle_matrix_remote(
        self,
        cmd_id: str,
        params: dict[str, Any] | None,
    ) -> int:
        norm = cmd_id.strip().lower()
        if norm not in ("send_cmd", "send_cmd_sequence"):
            return STATUS_NOT_IMPLEMENTED

        raw_commands = extract_command_sequence(norm, params)
        if raw_commands is None:
            return STATUS_BAD_REQUEST

        parsed_actions: list[tuple[str, Any]] = []
        for raw_cmd in raw_commands:
            parsed = self._parse_matrix_command(raw_cmd)
            if parsed is None:
                return STATUS_BAD_REQUEST
            parsed_actions.append(parsed)

        for kind, target in parsed_actions:
            if kind == "preset":
                ok = await self._call_recall_preset(int(target))
            elif kind == "route_all":
                ok = await self._call_switch(int(target), None)
                if ok:
                    self.projector.apply_event("routing", {"input": int(target), "output": None})
            else:
                ok = await self._call_run_action(kind, str(target))
            if not ok:
                return STATUS_SERVER_ERROR

        return STATUS_OK

    # ------------------------------------------------------------------
    # HubClient call adapters
    # ------------------------------------------------------------------

    async def _call_switch(self, input_num: int, output_num: int | None) -> bool:
        if hasattr(self.hub_client, "switch"):
            res = self.hub_client.switch(input_num, output_num)
            return bool(await res if asyncio.iscoroutine(res) else res)
        if output_num is None and hasattr(self.hub_client, "switch_all"):
            res = self.hub_client.switch_all(input_num)
            return bool(await res if asyncio.iscoroutine(res) else res)
        if output_num is not None and hasattr(self.hub_client, "switch_input"):
            res = self.hub_client.switch_input(input_num, output_num)
            return bool(await res if asyncio.iscoroutine(res) else res)
        raise AttributeError("hub_client has no switch method")

    async def _call_recall_preset(self, preset_num: int) -> bool:
        if hasattr(self.hub_client, "recall_preset"):
            res = self.hub_client.recall_preset(preset_num)
            return bool(await res if asyncio.iscoroutine(res) else res)
        if hasattr(self.hub_client, "run_action"):
            res = self.hub_client.run_action("preset", preset_num)
            return bool(await res if asyncio.iscoroutine(res) else res)
        raise AttributeError("hub_client has no recall_preset method")

    async def _call_power(self, on: bool) -> bool:
        if hasattr(self.hub_client, "power"):
            res = self.hub_client.power(on)
            return bool(await res if asyncio.iscoroutine(res) else res)
        method_name = "power_on" if on else "power_off"
        if hasattr(self.hub_client, method_name):
            res = getattr(self.hub_client, method_name)()
            return bool(await res if asyncio.iscoroutine(res) else res)
        raise AttributeError("hub_client has no power method")

    async def _call_send_cec(self, port_type: str, port_num: int, command: str) -> bool:
        if hasattr(self.hub_client, "send_cec"):
            res = self.hub_client.send_cec(port_type, port_num, command)
            return bool(await res if asyncio.iscoroutine(res) else res)
        method_name = f"send_cec_{port_type}"
        if hasattr(self.hub_client, method_name):
            res = getattr(self.hub_client, method_name)(port_num, command)
            return bool(await res if asyncio.iscoroutine(res) else res)
        raise AttributeError("hub_client has no send_cec method")

    async def _call_run_action(self, kind: str, action_id: str) -> bool:
        if hasattr(self.hub_client, "run_action"):
            res = self.hub_client.run_action(kind, action_id)
            return bool(await res if asyncio.iscoroutine(res) else res)
        raise AttributeError("hub_client has no run_action method")
