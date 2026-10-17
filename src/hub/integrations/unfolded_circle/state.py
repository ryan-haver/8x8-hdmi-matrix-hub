"""Pure state projection and diff tracker for Unfolded Circle entities (UC-04, UC-07, UC-08, BE-24)."""

from __future__ import annotations

from typing import Any

from .entities import (
    build_entities,
    extract_input_names,
    extract_output_names,
    extract_presets,
)


def _valid_input_port(value: Any, port_count: int = 8) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= port_count


def _parse_power_state(raw: Any) -> str | None:
    if isinstance(raw, bool):
        return "ON" if raw else "OFF"
    if isinstance(raw, int):
        if raw == 1:
            return "ON"
        if raw == 0:
            return "OFF"
        return None
    if isinstance(raw, str):
        norm = raw.strip().lower()
        if norm in ("1", "on", "true"):
            return "ON"
        if norm in ("0", "off", "false", "standby"):
            return "OFF"
    return None


def _parse_port_target(target: str, port: int | None = None) -> tuple[str, int]:
    """Normalize `(port_type, port)` or an entity_id into `(kind, port_num)`."""
    if port is not None:
        return target.lower(), int(port)
    if target == "switch.matrix_power":
        return ("matrix", 0)
    if target.startswith("media_player.output_"):
        return ("output", int(target.rsplit("_", 1)[1]))
    if target.startswith("remote.output_") and target.endswith("_cec"):
        num = target.removeprefix("remote.output_").removesuffix("_cec")
        return ("output", int(num))
    if target.startswith("remote.input_") and target.endswith("_cec"):
        num = target.removeprefix("remote.input_").removesuffix("_cec")
        return ("input", int(num))
    raise ValueError(f"Cannot resolve power target from {target!r}")


class EntityStateProjector:
    """Pure state projector and attribute diff tracker for UC entities.

    Responsibilities:
    - Media players and CEC remotes start in ``"UNKNOWN"`` power state (`BE-24`),
      and a toggle from ``"UNKNOWN"`` resolves to ``"ON"`` (`UC-10`, `DI-13`).
    - When ``connected=False``, projects device state ``"ERROR"`` / ``"DISCONNECTED"``
      and marks all entities ``"UNAVAILABLE"`` without fabricating ``"Input 0"`` (`UC-04`).
    - Diffs attributes against last-pushed state and returns ONLY changed entity
      attributes (`UC-07`), except on initial subscribe/wake resync.
    - Live renames (``names`` event) update entity names and ``source_list`` /
      ``options`` in place without clearing ``configured_entities`` (`UC-08`).
    """

    def __init__(
        self,
        *,
        port_count: int = 8,
        include_select: bool = True,
        include_legacy_sensors: bool = False,
    ) -> None:
        self.port_count = port_count
        self.include_select = include_select
        self.include_legacy_sensors = include_legacy_sensors

        self.connected: bool = True
        self.device_state: str = "CONNECTED"
        self.standby: bool = False

        self.input_names: dict[int, str] = {n: f"Input {n}" for n in range(1, port_count + 1)}
        self.output_names: dict[int, str] = {n: f"Output {n}" for n in range(1, port_count + 1)}
        self.routed_inputs: dict[int, int] = {}

        # Tracked CEC / matrix power states: ("input"|"output"|"matrix", port) -> "UNKNOWN"|"ON"|"OFF"
        self._power_states: dict[tuple[str, int], str] = {}

        # Ground-truth attributes per entity_id (when connected)
        self.truth: dict[str, dict[str, Any]] = {}
        # Last attributes pushed to the Remote per entity_id
        self.last_pushed: dict[str, dict[str, Any]] = {}
        # Entity display names in place (entity_id -> {"en": ...})
        self.entity_names: dict[str, dict[str, str]] = {}
        # Subscribed / configured entities registry (in-place updated on rename, never cleared: UC-08)
        self.configured_entities: dict[str, dict[str, Any]] = {}
        self.available_entities: dict[str, dict[str, Any]] = {}
        # Pending attribute keys accumulated while in standby (UC-06)
        self._pending_standby: dict[str, set[str]] = {}

        self._seed_defaults()

    def _seed_defaults(self) -> None:
        """Initialize all entities with safe default states (`UNKNOWN` power, no fabricated values)."""
        initial_entities = build_entities(
            {"port_count": self.port_count},
            include_select=self.include_select,
            include_legacy_sensors=self.include_legacy_sensors,
        )
        for desc in initial_entities:
            eid = desc["entity_id"]
            self.truth[eid] = dict(desc["attributes"])
            self.entity_names[eid] = dict(desc["name"])
            self.available_entities[eid] = dict(desc)
            self.configured_entities[eid] = dict(desc)

        for n in range(1, self.port_count + 1):
            self._power_states[("input", n)] = "UNKNOWN"
            self._power_states[("output", n)] = "UNKNOWN"
        self._power_states[("matrix", 0)] = "UNKNOWN"

    # ------------------------------------------------------------------
    # Power state & toggle resolution (BE-24, UC-10, DI-13)
    # ------------------------------------------------------------------

    def get_power_state(self, target: str, port: int | None = None) -> str:
        """Return the tracked power state (`"UNKNOWN"`, `"ON"`, or `"OFF"`)."""
        key = _parse_port_target(target, port)
        return self._power_states.get(key, "UNKNOWN")

    def resolve_toggle(self, target: str, port: int | None = None) -> str:
        """Resolve a toggle command from current tracked power state.

        From ``"UNKNOWN"`` or ``"OFF"``, resolves to ``"ON"`` (`BE-24`, `UC-10`).
        From ``"ON"``, resolves to ``"OFF"``.
        """
        current = self.get_power_state(target, port)
        return "OFF" if current == "ON" else "ON"

    def record_power(self, target: str, port: int | None = None, on: bool | str = True) -> dict[str, dict[str, Any]]:
        """Record a power command outcome and return the resulting attribute diff."""
        kind, port_num = _parse_port_target(target, port)
        new_state = on if isinstance(on, str) else ("ON" if on else "OFF")
        self._power_states[(kind, port_num)] = new_state

        affected: list[str] = []
        if kind == "matrix":
            affected.append("switch.matrix_power")
        elif kind == "input":
            affected.append(f"remote.input_{port_num}_cec")
        elif kind == "output":
            affected.append(f"remote.output_{port_num}_cec")
            affected.append(f"media_player.output_{port_num}")

        for eid in affected:
            self.truth.setdefault(eid, {})["state"] = new_state

        return self._compute_diff(affected)

    # ------------------------------------------------------------------
    # Projection & diffing (UC-04, UC-07)
    # ------------------------------------------------------------------

    def projected_attributes(self, entity_id: str) -> dict[str, Any]:
        """Return the current projected attributes for `entity_id`."""
        attrs = dict(self.truth.get(entity_id, {}))
        if not self.connected:
            attrs["state"] = "UNAVAILABLE"
        return attrs

    def _compute_diff(
        self,
        entity_ids: list[str] | None = None,
        *,
        force: bool = False,
    ) -> dict[str, dict[str, Any]]:
        target_ids = entity_ids if entity_ids is not None else list(self.truth.keys())
        diff: dict[str, dict[str, Any]] = {}

        for eid in target_ids:
            if eid not in self.truth:
                continue
            proj = self.projected_attributes(eid)
            if eid in self.available_entities:
                self.available_entities[eid]["attributes"] = dict(proj)
            if eid in self.configured_entities:
                self.configured_entities[eid]["attributes"] = dict(proj)

            prev = self.last_pushed.get(eid)
            if force or prev is None:
                changed = dict(proj)
            else:
                changed = {k: v for k, v in proj.items() if prev.get(k) != v}

            if not changed:
                continue

            if self.standby and not force:
                self._pending_standby.setdefault(eid, set()).update(changed.keys())
            else:
                self.last_pushed.setdefault(eid, {}).update(changed)
                diff[eid] = changed

        return diff

    @staticmethod
    def _resolve_device_state(connected: bool, raw_state: str | None) -> str:
        if raw_state:
            upper = raw_state.strip().upper()
            if upper in ("CONNECTED", "DEGRADED"):
                return "CONNECTED"
            if upper == "CONNECTING":
                return "CONNECTING"
            if upper in ("BACKOFF", "ERROR", "RECONNECTING"):
                return "ERROR"
            if upper == "DISCONNECTED":
                return "DISCONNECTED"
        return "CONNECTED" if connected else "ERROR"

    # ------------------------------------------------------------------
    # Snapshot & event ingestion (UC-04, UC-07, UC-08)
    # ------------------------------------------------------------------

    def project_snapshot(
        self,
        snapshot: dict[str, Any],
        *,
        force: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """Project a full hub snapshot and return changed (or full if `force=True`) entity attributes."""
        raw_conn_state = snapshot.get("connection_state") or snapshot.get("device_state")
        if "connected" in snapshot:
            connected = bool(snapshot["connected"])
        elif isinstance(raw_conn_state, str):
            connected = raw_conn_state.strip().upper() in ("CONNECTED", "DEGRADED")
        else:
            connected = True

        self.connected = connected
        self.device_state = self._resolve_device_state(connected, raw_conn_state)

        # If disconnected, mark all entities UNAVAILABLE without fabricating values (UC-04)
        if not connected:
            return self._compute_diff(force=force)

        self._apply_names_internal(
            extract_input_names(snapshot, count=self.port_count),
            extract_output_names(snapshot, count=self.port_count),
            allow_generic_overwrite=False,
        )

        # Matrix power switch (UC-09)
        power_val = snapshot.get("power")
        if power_val is None and isinstance(snapshot.get("system"), dict):
            power_val = snapshot["system"].get("power")
        parsed_power = _parse_power_state(power_val)
        if parsed_power is not None:
            self._power_states[("matrix", 0)] = parsed_power
            self.truth["switch.matrix_power"]["state"] = parsed_power

        # Matrix remote and preset buttons are available when connected
        self.truth["remote.orei_matrix"]["state"] = "ON"
        for preset in extract_presets(snapshot, count=self.port_count):
            n = preset["number"]
            eid = f"button.preset_{n}"
            self.truth.setdefault(eid, {})["state"] = "AVAILABLE"
            self.entity_names[eid] = {"en": preset["name"]}
            if eid in self.configured_entities:
                self.configured_entities[eid]["name"] = {"en": preset["name"]}
            if eid in self.available_entities:
                self.available_entities[eid]["name"] = {"en": preset["name"]}

        # Routing & display state
        self._apply_routing_from_snapshot(snapshot)
        self._apply_signals_from_snapshot(snapshot)
        self._apply_displays_from_snapshot(snapshot)

        return self._compute_diff(force=force)

    def _apply_routing_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        routing_map: dict[int, Any] = {}
        raw_routing = snapshot.get("routing")
        if isinstance(raw_routing, list):
            for idx, val in enumerate(raw_routing, start=1):
                routing_map[idx] = val
        elif isinstance(raw_routing, dict):
            for k, val in raw_routing.items():
                try:
                    routing_map[int(k)] = val
                except (TypeError, ValueError):
                    continue

        raw_outputs = snapshot.get("outputs")
        if isinstance(raw_outputs, list):
            for idx, out in enumerate(raw_outputs, start=1):
                if isinstance(out, dict):
                    port = int(out.get("port") or out.get("output") or out.get("number") or idx)
                    src = out.get("source", out.get("current_input", out.get("input")))
                    if src is not None:
                        routing_map[port] = src
        elif isinstance(raw_outputs, dict):
            for k, out in raw_outputs.items():
                try:
                    port = int(k)
                except (TypeError, ValueError):
                    continue
                if isinstance(out, dict):
                    src = out.get("source", out.get("current_input", out.get("input")))
                    if src is not None:
                        routing_map[port] = src

        for out_num, in_num in routing_map.items():
            if 1 <= out_num <= self.port_count:
                self._set_output_route(out_num, in_num)

    def _set_output_route(self, output_num: int, input_num: Any) -> None:
        """Update routing for `output_num` ONLY if `input_num` is valid (1..8); never fabricate 'Input 0' (UC-04)."""
        if not _valid_input_port(input_num, self.port_count):
            return
        self.routed_inputs[output_num] = int(input_num)
        source_name = self.input_names.get(int(input_num), f"Input {input_num}")
        mp_id = f"media_player.output_{output_num}"
        if mp_id in self.truth:
            self.truth[mp_id]["source"] = source_name
        sel_id = f"select.output_{output_num}_source"
        if sel_id in self.truth:
            self.truth[sel_id]["current_option"] = source_name
            self.truth[sel_id]["state"] = "ON"
        leg_id = f"sensor.output_{output_num}_source"
        if leg_id in self.truth:
            self.truth[leg_id]["value"] = source_name
            self.truth[leg_id]["state"] = "ON"

    def _apply_signals_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        signals: dict[int, bool] = {}
        raw_signals = snapshot.get("signals") or snapshot.get("signal")
        if isinstance(raw_signals, list):
            for idx, val in enumerate(raw_signals, start=1):
                if val is not None:
                    signals[idx] = bool(val)
        elif isinstance(raw_signals, dict):
            for k, val in raw_signals.items():
                try:
                    idx = int(k)
                except (TypeError, ValueError):
                    continue
                if val is not None:
                    signals[idx] = bool(val)

        raw_inputs = snapshot.get("inputs")
        if isinstance(raw_inputs, list):
            for idx, item in enumerate(raw_inputs, start=1):
                if isinstance(item, dict) and "signal" in item and item["signal"] is not None:
                    port = int(item.get("port") or item.get("input") or item.get("number") or idx)
                    signals[port] = bool(item["signal"])

        for in_num, has_signal in signals.items():
            if 1 <= in_num <= self.port_count:
                self._set_input_signal(in_num, has_signal)

    def _set_input_signal(self, input_num: int, has_signal: bool | None) -> None:
        if has_signal is None:
            return
        sig_id = f"sensor.input_{input_num}_signal"
        if sig_id in self.truth:
            self.truth[sig_id]["state"] = "ON"
            self.truth[sig_id]["value"] = bool(has_signal)

    def _apply_displays_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        displays: dict[int, bool] = {}
        raw_displays = snapshot.get("displays") or snapshot.get("connections")
        if isinstance(raw_displays, list):
            for idx, val in enumerate(raw_displays, start=1):
                if val is not None:
                    displays[idx] = bool(val)
        elif isinstance(raw_displays, dict):
            for k, val in raw_displays.items():
                try:
                    idx = int(k)
                except (TypeError, ValueError):
                    continue
                if val is not None:
                    displays[idx] = bool(val)

        raw_outputs = snapshot.get("outputs")
        if isinstance(raw_outputs, list):
            for idx, item in enumerate(raw_outputs, start=1):
                if isinstance(item, dict):
                    port = int(item.get("port") or item.get("output") or item.get("number") or idx)
                    conn = item.get("connected", item.get("display"))
                    if conn is not None:
                        displays[port] = bool(conn)

        for out_num, is_connected in displays.items():
            if 1 <= out_num <= self.port_count:
                self._set_output_display(out_num, is_connected)

    def _set_output_display(self, output_num: int, is_connected: bool | None) -> None:
        if is_connected is None:
            return
        disp_id = f"sensor.output_{output_num}_display"
        if disp_id in self.truth:
            self.truth[disp_id]["state"] = "ON"
            self.truth[disp_id]["value"] = bool(is_connected)
        leg_id = f"sensor.output_{output_num}_connected"
        if leg_id in self.truth:
            self.truth[leg_id]["state"] = "ON"
            self.truth[leg_id]["value"] = "Connected" if is_connected else "Disconnected"

    def _apply_names_internal(
        self,
        new_inputs: dict[int, str] | None,
        new_outputs: dict[int, str] | None,
        *,
        allow_generic_overwrite: bool = False,
    ) -> None:
        """Update port names, source_list, options, and entity names in place without clearing configured_entities (UC-08)."""
        if new_inputs:
            generic_inputs = {n: f"Input {n}" for n in range(1, self.port_count + 1)}
            has_custom = any(self.input_names.get(n) != generic_inputs[n] for n in generic_inputs)
            if allow_generic_overwrite or new_inputs != generic_inputs or not has_custom:
                for k, v in new_inputs.items():
                    port = int(k)
                    if 1 <= port <= self.port_count and isinstance(v, str) and v.strip():
                        self.input_names[port] = v.strip()

        if new_outputs:
            generic_outputs = {n: f"Output {n}" for n in range(1, self.port_count + 1)}
            has_custom_out = any(self.output_names.get(n) != generic_outputs[n] for n in generic_outputs)
            if allow_generic_overwrite or new_outputs != generic_outputs or not has_custom_out:
                for k, v in new_outputs.items():
                    port = int(k)
                    if 1 <= port <= self.port_count and isinstance(v, str) and v.strip():
                        self.output_names[port] = v.strip()

        source_list = [self.input_names[i] for i in range(1, self.port_count + 1)]

        for n in range(1, self.port_count + 1):
            in_name = self.input_names[n]
            self._rename_entity_in_place(f"remote.input_{n}_cec", f"{in_name} CEC")
            self._rename_entity_in_place(f"sensor.input_{n}_signal", f"{in_name} Signal")
            if self.include_legacy_sensors:
                self._rename_entity_in_place(f"sensor.input_{n}_cable", f"{in_name} Cable")

            out_name = self.output_names[n]
            mp_id = f"media_player.output_{n}"
            self._rename_entity_in_place(mp_id, out_name)
            self.truth[mp_id]["source_list"] = list(source_list)

            if self.include_select:
                sel_id = f"select.output_{n}_source"
                self._rename_entity_in_place(sel_id, f"{out_name} Source")
                self.truth[sel_id]["options"] = list(source_list)

            self._rename_entity_in_place(f"remote.output_{n}_cec", f"{out_name} TV")
            self._rename_entity_in_place(f"sensor.output_{n}_display", f"{out_name} Display")

            if self.include_legacy_sensors:
                self._rename_entity_in_place(f"sensor.output_{n}_connected", f"{out_name} Connected")
                self._rename_entity_in_place(f"sensor.output_{n}_cable", f"{out_name} Cable")
                self._rename_entity_in_place(f"sensor.output_{n}_source", f"{out_name} Source")

            # Keep currently routed input label in sync after input rename
            routed = self.routed_inputs.get(n)
            if routed is not None and _valid_input_port(routed, self.port_count):
                new_src_label = self.input_names[routed]
                self.truth[mp_id]["source"] = new_src_label
                if self.include_select:
                    self.truth[f"select.output_{n}_source"]["current_option"] = new_src_label
                if self.include_legacy_sensors:
                    self.truth[f"sensor.output_{n}_source"]["value"] = new_src_label

    def _rename_entity_in_place(self, entity_id: str, new_display_name: str) -> None:
        name_dict = {"en": new_display_name}
        self.entity_names[entity_id] = name_dict
        if entity_id in self.configured_entities:
            self.configured_entities[entity_id]["name"] = dict(name_dict)
        if entity_id in self.available_entities:
            self.available_entities[entity_id]["name"] = dict(name_dict)

    def apply_event(
        self,
        event: str | dict[str, Any],
        data: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Apply an incremental hub event and return ONLY changed entity attributes (`UC-07`)."""
        if isinstance(event, dict):
            ev_type = str(event.get("type") or event.get("event") or "")
            payload = event.get("data") if isinstance(event.get("data"), dict) else event
        else:
            ev_type = str(event)
            payload = data or {}

        ev_norm = ev_type.strip().lower()

        if ev_norm in ("hub_connection", "connection", "connection_state"):
            raw_state = payload.get("connection_state") or payload.get("state")
            if "connected" in payload:
                connected = bool(payload["connected"])
            elif isinstance(raw_state, str):
                connected = raw_state.strip().upper() in ("CONNECTED", "DEGRADED")
            else:
                connected = False
            self.connected = connected
            self.device_state = self._resolve_device_state(connected, raw_state)
            return self._compute_diff()

        if ev_norm in ("routing", "routing_change", "switch"):
            if "routing" in payload:
                self._apply_routing_from_snapshot(payload)
            else:
                out_num = payload.get("output")
                in_num = payload.get("input", payload.get("source"))
                if out_num is None and in_num is not None:
                    for n in range(1, self.port_count + 1):
                        self._set_output_route(n, in_num)
                elif out_num is not None:
                    self._set_output_route(int(out_num), in_num)
            return self._compute_diff()

        if ev_norm in ("signal", "signal_change"):
            port = payload.get("port", payload.get("input"))
            present = payload.get("present", payload.get("signal"))
            if port is not None and present is not None:
                self._set_input_signal(int(port), bool(present))
            elif "signals" in payload or "inputs" in payload:
                self._apply_signals_from_snapshot(payload)
            return self._compute_diff()

        if ev_norm in ("display", "cable", "connection_change", "cable_change"):
            port_type = str(payload.get("port_type") or "output").lower()
            port = payload.get("port", payload.get("output"))
            connected_val = payload.get("connected", payload.get("display", payload.get("present")))
            if port_type == "output" and port is not None and connected_val is not None:
                self._set_output_display(int(port), bool(connected_val))
            elif "displays" in payload or "outputs" in payload:
                self._apply_displays_from_snapshot(payload)
            return self._compute_diff()

        if ev_norm in ("power", "power_change"):
            parsed = _parse_power_state(payload.get("power", payload.get("state")))
            if parsed is not None:
                self._power_states[("matrix", 0)] = parsed
                self.truth["switch.matrix_power"]["state"] = parsed
            return self._compute_diff(["switch.matrix_power"])

        if ev_norm in ("names", "names_change", "rename"):
            in_updates: dict[int, str] = {}
            out_updates: dict[int, str] = {}
            raw_in = payload.get("inputs") or payload.get("input_names") or payload.get("input_name")
            if isinstance(raw_in, dict):
                for k, v in raw_in.items():
                    if isinstance(v, str) and v.strip():
                        in_updates[int(k)] = v.strip()
            raw_out = payload.get("outputs") or payload.get("output_names") or payload.get("output_name")
            if isinstance(raw_out, dict):
                for k, v in raw_out.items():
                    if isinstance(v, str) and v.strip():
                        out_updates[int(k)] = v.strip()
            if payload.get("port_type") == "input" and payload.get("port") and payload.get("name"):
                in_updates[int(payload["port"])] = str(payload["name"]).strip()
            elif payload.get("port_type") == "output" and payload.get("port") and payload.get("name"):
                out_updates[int(payload["port"])] = str(payload["name"]).strip()

            self._apply_names_internal(
                in_updates or None,
                out_updates or None,
                allow_generic_overwrite=bool(payload.get("explicit", False)),
            )
            return self._compute_diff()

        if ev_norm in ("presets", "presets_change"):
            for preset in extract_presets(payload, count=self.port_count):
                n = preset["number"]
                self._rename_entity_in_place(f"button.preset_{n}", preset["name"])
            return self._compute_diff()

        return {}

    # ------------------------------------------------------------------
    # Standby & resync (UC-06, UC-07)
    # ------------------------------------------------------------------

    def enter_standby(self) -> None:
        """Pause pushes while the Remote is in standby (`UC-06`)."""
        self.standby = True

    def exit_standby(self) -> dict[str, dict[str, Any]]:
        """Resume pushes and flush all changes accumulated during standby (`UC-06`)."""
        self.standby = False
        pending, self._pending_standby = self._pending_standby, {}
        if not pending:
            return self._compute_diff()
        flushed: dict[str, dict[str, Any]] = {}
        for eid, keys in pending.items():
            proj = self.projected_attributes(eid)
            changed = {k: proj[k] for k in keys if k in proj}
            if changed:
                self.last_pushed.setdefault(eid, {}).update(changed)
                flushed[eid] = changed
        return flushed

    def resync(self, entity_ids: list[str] | None = None) -> dict[str, dict[str, Any]]:
        """Force full attribute projection for newly subscribed entities or wake resync."""
        return self._compute_diff(entity_ids, force=True)
