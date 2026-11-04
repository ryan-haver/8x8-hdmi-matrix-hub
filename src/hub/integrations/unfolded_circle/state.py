"""Pure state projection and diff tracker for Unfolded Circle entities (UC-04, UC-07, UC-08, BE-24)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .entities import (
    build_compatible_entities,
    build_entities,
    extract_favorite_preset_numbers,
    extract_input_names,
    extract_output_names,
    extract_presets,
    normalize_snapshot,
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
    - Does NOT populate ``configured_entities`` merely because entities are available;
      only explicitly subscribed entities belong in ``configured_entities``.
    """

    def __init__(
        self,
        *,
        port_count: int = 8,
        include_select: bool = True,
        include_legacy_sensors: bool = False,
        compatible: bool = False,
    ) -> None:
        self.port_count = port_count
        self.compatible = compatible
        if compatible:
            self.include_select = False
            self.include_legacy_sensors = True
        else:
            self.include_select = include_select
            self.include_legacy_sensors = include_legacy_sensors

        self.connected: bool = True
        self.device_state: str = "CONNECTED"
        self.standby: bool = False

        self.input_names: dict[int, str] = {n: f"Input {n}" for n in range(1, port_count + 1)}
        self.output_names: dict[int, str] = {n: f"Output {n}" for n in range(1, port_count + 1)}
        self.preset_names: dict[int, str] = {n: f"Preset {n}" for n in range(1, port_count + 1)}
        self.favorite_presets: list[int] = []
        self.catalog: dict[str, list[dict[str, Any]]] = {
            "profiles": [],
            "scenes": [],
            "macros": [],
            "shortcuts": [],
        }
        self.routed_inputs: dict[int, int] = {}

        # Tracked CEC / matrix power states: ("input"|"output"|"matrix", port) -> "UNKNOWN"|"ON"|"OFF"
        self._power_states: dict[tuple[str, int], str] = {}

        # Ground-truth attributes per entity_id (when connected)
        self.truth: dict[str, dict[str, Any]] = {}
        # Last attributes pushed to the Remote per entity_id
        self.last_pushed: dict[str, dict[str, Any]] = {}
        # Entity display names in place (entity_id -> {"en": ...})
        self.entity_names: dict[str, dict[str, str]] = {}
        # Subscribed / configured entities registry (ONLY subscribed entities; updated in place on rename: UC-08)
        self.configured_entities: dict[str, dict[str, Any]] = {}
        self.available_entities: dict[str, dict[str, Any]] = {}
        # Pending attribute keys accumulated while in standby (UC-06)
        self._pending_standby: dict[str, set[str]] = {}

        self._seed_defaults()

    def _build_descriptor_list(self, snapshot: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        snap = dict(snapshot or {})
        snap.setdefault("port_count", self.port_count)
        snap.setdefault("input_names", dict(self.input_names))
        snap.setdefault("output_names", dict(self.output_names))
        snap.setdefault("preset_names", dict(self.preset_names))
        snap.setdefault("favorite_presets", list(self.favorite_presets))
        for k, v in self.catalog.items():
            snap.setdefault(k, list(v))
        if self.compatible:
            return build_compatible_entities(snap)
        return build_entities(
            snap,
            include_select=self.include_select,
            include_legacy_sensors=self.include_legacy_sensors,
        )

    def _seed_defaults(self) -> None:
        """Initialize available entities with safe default states (`UNKNOWN` power, no fabricated values)."""
        initial_entities = self._build_descriptor_list()
        for desc in initial_entities:
            eid = desc["entity_id"]
            self.truth[eid] = dict(desc["attributes"])
            self.entity_names[eid] = dict(desc["name"])
            self.available_entities[eid] = dict(desc)

        for n in range(1, self.port_count + 1):
            self._power_states[("input", n)] = "UNKNOWN"
            self._power_states[("output", n)] = "UNKNOWN"
        self._power_states[("matrix", 0)] = "UNKNOWN"

    # ------------------------------------------------------------------
    # Subscription management (available vs configured entities)
    # ------------------------------------------------------------------

    def subscribe_entities(self, entity_ids: Iterable[str]) -> dict[str, dict[str, Any]]:
        """Subscribe `entity_ids` into `configured_entities` and return their full projected attributes."""
        subscribed: list[str] = []
        for eid in entity_ids:
            if eid in self.available_entities:
                desc = dict(self.available_entities[eid])
                desc["name"] = dict(self.entity_names.get(eid, desc.get("name", {"en": eid})))
                desc["attributes"] = self.projected_attributes(eid)
                self.configured_entities[eid] = desc
                subscribed.append(eid)
        return self.resync(subscribed)

    def unsubscribe_entities(self, entity_ids: Iterable[str]) -> None:
        """Remove `entity_ids` from `configured_entities`."""
        for eid in entity_ids:
            self.configured_entities.pop(eid, None)
            self.last_pushed.pop(eid, None)
            self._pending_standby.pop(eid, None)

    def _refresh_descriptors_in_place(self, snapshot: Mapping[str, Any] | None = None) -> None:
        """Rebuild descriptors in place (preserving `configured_entities` membership and projected attributes)."""
        descriptors = self._build_descriptor_list(snapshot)
        for desc in descriptors:
            eid = desc["entity_id"]
            self.entity_names[eid] = dict(desc["name"])
            if eid not in self.truth:
                self.truth[eid] = dict(desc["attributes"])
            proj = self.projected_attributes(eid)
            updated_desc = dict(desc)
            updated_desc["attributes"] = dict(proj)
            self.available_entities[eid] = updated_desc
            if eid in self.configured_entities:
                cfg_desc = dict(desc)
                cfg_desc["attributes"] = dict(proj)
                self.configured_entities[eid] = cfg_desc

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
        snapshot: Any,
        *,
        force: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """Project a full hub snapshot (`HubSnapshot` or `dict`) and return changed attributes."""
        snap = normalize_snapshot(snapshot)
        raw_conn_state = snap.get("connection_state") or snap.get("device_state")
        if "connected" in snap:
            connected = bool(snap["connected"])
        elif isinstance(raw_conn_state, str):
            connected = raw_conn_state.strip().upper() in ("CONNECTED", "DEGRADED")
        else:
            connected = True

        self.connected = connected
        self.device_state = self._resolve_device_state(connected, raw_conn_state)

        # Always capture non-empty port/preset/catalog metadata from snapshot so restored
        # entities carry saved names even before the matrix finishes connecting.
        if snap.get("input_names") or snap.get("output_names") or snap.get("inputs") or snap.get("outputs"):
            self._apply_names_internal(
                extract_input_names(snap, count=self.port_count),
                extract_output_names(snap, count=self.port_count),
                allow_generic_overwrite=False,
            )

        self._apply_presets_from_snapshot(snap)
        self._apply_catalog_from_snapshot(snap)
        self._refresh_descriptors_in_place(snap)

        # If disconnected, mark all entities UNAVAILABLE without fabricating values (UC-04)
        if not connected:
            return self._compute_diff(force=force)

        # Matrix power switch (UC-09)
        power_val = snap.get("power")
        if power_val is None and isinstance(snap.get("system"), Mapping):
            power_val = snap["system"].get("power")
        parsed_power = _parse_power_state(power_val)
        if parsed_power is not None:
            self._power_states[("matrix", 0)] = parsed_power
            self.truth["switch.matrix_power"]["state"] = parsed_power

        # Matrix remote and preset buttons are available when connected
        self.truth["remote.orei_matrix"]["state"] = "ON"
        for n in range(1, self.port_count + 1):
            eid = f"button.preset_{n}"
            self.truth.setdefault(eid, {})["state"] = "AVAILABLE"

        # Routing, signal, display, and cable state
        self._apply_routing_from_snapshot(snap)
        self._apply_signals_from_snapshot(snap)
        self._apply_displays_from_snapshot(snap)
        self._apply_cables_from_snapshot(snap)

        return self._compute_diff(force=force)

    def _apply_presets_from_snapshot(self, snap: Mapping[str, Any]) -> bool:
        if not any(k in snap for k in ("presets", "preset_names", "favorite_presets", "favourites")):
            return False
        presets = extract_presets(snap, count=self.port_count)
        favs = extract_favorite_preset_numbers(snap, count=self.port_count)
        new_names = {p["number"]: p["name"] for p in presets}
        changed = (new_names != self.preset_names) or (favs != self.favorite_presets)
        self.preset_names = new_names
        self.favorite_presets = favs
        for p in presets:
            n = p["number"]
            self._rename_entity_in_place(f"button.preset_{n}", p["name"])
        return changed

    def _apply_catalog_from_snapshot(self, snap: Mapping[str, Any]) -> bool:
        changed = False
        for key in ("profiles", "scenes", "macros", "shortcuts"):
            if key in snap and isinstance(snap[key], list):
                new_list = [dict(item) if isinstance(item, Mapping) else item for item in snap[key]]
                if new_list != self.catalog.get(key):
                    self.catalog[key] = new_list
                    changed = True
        return changed

    def _apply_routing_from_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        routing_map: dict[int, Any] = {}
        raw_routing = snapshot.get("routing")
        if isinstance(raw_routing, list):
            for idx, val in enumerate(raw_routing, start=1):
                routing_map[idx] = val
        elif isinstance(raw_routing, Mapping):
            for k, val in raw_routing.items():
                try:
                    routing_map[int(k)] = val
                except (TypeError, ValueError):
                    continue

        raw_outputs = snapshot.get("outputs")
        if isinstance(raw_outputs, list):
            for idx, out in enumerate(raw_outputs, start=1):
                if isinstance(out, Mapping):
                    port = int(out.get("port") or out.get("output") or out.get("number") or idx)
                    src = out.get("source", out.get("current_input", out.get("input")))
                    if src is not None:
                        routing_map[port] = src
        elif isinstance(raw_outputs, Mapping):
            for k, out in raw_outputs.items():
                try:
                    port = int(k)
                except (TypeError, ValueError):
                    continue
                if isinstance(out, Mapping):
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

    def _apply_signals_from_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        signals: dict[int, bool] = {}
        raw_signals = (
            snapshot.get("input_signals")
            if "input_signals" in snapshot
            else (snapshot.get("signals") or snapshot.get("signal"))
        )
        if isinstance(raw_signals, list):
            for idx, val in enumerate(raw_signals, start=1):
                if val is not None:
                    signals[idx] = bool(val)
        elif isinstance(raw_signals, Mapping):
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
                if isinstance(item, Mapping) and "signal" in item and item["signal"] is not None:
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
            if self.include_legacy_sensors:
                self.truth[sig_id]["value"] = "Active" if has_signal else "No Signal"
            else:
                self.truth[sig_id]["value"] = bool(has_signal)

    def _apply_displays_from_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        displays: dict[int, bool] = {}
        raw_displays = (
            snapshot.get("output_displays")
            if "output_displays" in snapshot
            else (snapshot.get("displays") or snapshot.get("connections"))
        )
        if isinstance(raw_displays, list):
            for idx, val in enumerate(raw_displays, start=1):
                if val is not None:
                    displays[idx] = bool(val)
        elif isinstance(raw_displays, Mapping):
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
                if isinstance(item, Mapping):
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

    def _apply_cables_from_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        raw_in_cables = snapshot.get("input_cables")
        if isinstance(raw_in_cables, Mapping):
            for k, val in raw_in_cables.items():
                try:
                    idx = int(k)
                except (TypeError, ValueError):
                    continue
                if 1 <= idx <= self.port_count and val is not None:
                    self._set_cable_status("input", idx, bool(val))
        elif isinstance(raw_in_cables, list):
            for idx, val in enumerate(raw_in_cables, start=1):
                if 1 <= idx <= self.port_count and val is not None:
                    self._set_cable_status("input", idx, bool(val))

        raw_out_cables = snapshot.get("output_cables")
        if isinstance(raw_out_cables, Mapping):
            for k, val in raw_out_cables.items():
                try:
                    idx = int(k)
                except (TypeError, ValueError):
                    continue
                if 1 <= idx <= self.port_count and val is not None:
                    self._set_cable_status("output", idx, bool(val))
        elif isinstance(raw_out_cables, list):
            for idx, val in enumerate(raw_out_cables, start=1):
                if 1 <= idx <= self.port_count and val is not None:
                    self._set_cable_status("output", idx, bool(val))

        raw_cables = snapshot.get("cables")
        if isinstance(raw_cables, Mapping):
            for side_key, side_name in (("inputs", "input"), ("outputs", "output")):
                side_map = raw_cables.get(side_key)
                if isinstance(side_map, Mapping):
                    for k, val in side_map.items():
                        try:
                            idx = int(k)
                        except (TypeError, ValueError):
                            continue
                        if 1 <= idx <= self.port_count and val is not None:
                            self._set_cable_status(side_name, idx, bool(val))

    def _set_cable_status(self, port_type: str, port_num: int, is_connected: bool | None) -> None:
        if is_connected is None:
            return
        cable_id = f"sensor.{port_type}_{port_num}_cable"
        if cable_id in self.truth:
            self.truth[cable_id]["state"] = "ON"
            self.truth[cable_id]["value"] = "Connected" if is_connected else "Disconnected"

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

            if self.include_select and f"select.output_{n}_source" in self.truth:
                sel_id = f"select.output_{n}_source"
                self._rename_entity_in_place(sel_id, f"{out_name} Source")
                self.truth[sel_id]["options"] = list(source_list)

            self._rename_entity_in_place(f"remote.output_{n}_cec", f"{out_name} TV")
            if f"sensor.output_{n}_display" in self.truth:
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
                if self.include_select and f"select.output_{n}_source" in self.truth:
                    self.truth[f"select.output_{n}_source"]["current_option"] = new_src_label
                if self.include_legacy_sensors and f"sensor.output_{n}_source" in self.truth:
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
        event: Any,
        data: Mapping[str, Any] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Apply an incremental hub event (`HubEvent`, `str`, or `dict`) and return ONLY changed entity attributes (`UC-07`)."""
        if hasattr(event, "kind") and hasattr(event, "data"):
            ev_type = str(event.kind)
            payload: dict[str, Any] = dict(event.data) if isinstance(event.data, Mapping) else {}
        elif isinstance(event, Mapping):
            ev_type = str(event.get("kind") or event.get("type") or event.get("event") or "")
            raw_data = event.get("data")
            payload = dict(raw_data) if isinstance(raw_data, Mapping) else dict(event)
        else:
            ev_type = str(event)
            payload = dict(data) if isinstance(data, Mapping) else {}

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
            elif any(k in payload for k in ("input_signals", "signals", "inputs")):
                self._apply_signals_from_snapshot(payload)
            return self._compute_diff()

        if ev_norm in ("cable", "cable_change"):
            port_type = str(payload.get("type") or payload.get("port_type") or "input").lower()
            if port_type.endswith("s"):
                port_type = port_type[:-1]
            port = payload.get("port", payload.get("input", payload.get("output")))
            connected_val = payload.get("connected", payload.get("present"))
            if port_type in ("input", "output") and port is not None and connected_val is not None:
                self._set_cable_status(port_type, int(port), bool(connected_val))
            elif any(k in payload for k in ("input_cables", "output_cables", "cables")):
                self._apply_cables_from_snapshot(payload)
            return self._compute_diff()

        if ev_norm in ("display", "connection_change"):
            port = payload.get("port", payload.get("output"))
            connected_val = payload.get("connected", payload.get("display", payload.get("present")))
            if port is not None and connected_val is not None:
                self._set_output_display(int(port), bool(connected_val))
            elif any(k in payload for k in ("output_displays", "displays", "connections", "outputs")):
                self._apply_displays_from_snapshot(payload)
            return self._compute_diff()

        if ev_norm in ("power", "power_change"):
            raw_pwr = payload["on"] if "on" in payload else payload.get("power", payload.get("state"))
            parsed = _parse_power_state(raw_pwr)
            if parsed is not None:
                self._power_states[("matrix", 0)] = parsed
                self.truth["switch.matrix_power"]["state"] = parsed
            return self._compute_diff(["switch.matrix_power"])

        if ev_norm in ("names", "names_change", "rename"):
            in_updates: dict[int, str] = {}
            out_updates: dict[int, str] = {}
            raw_in = payload.get("inputs") or payload.get("input_names") or payload.get("input_name")
            if isinstance(raw_in, Mapping):
                for k, v in raw_in.items():
                    if isinstance(v, str) and v.strip():
                        in_updates[int(k)] = v.strip()
            raw_out = payload.get("outputs") or payload.get("output_names") or payload.get("output_name")
            if isinstance(raw_out, Mapping):
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
            self._refresh_descriptors_in_place()
            return self._compute_diff()

        if ev_norm in ("presets", "presets_change"):
            self._apply_presets_from_snapshot(payload)
            self._refresh_descriptors_in_place()
            return self._compute_diff()

        if ev_norm in ("catalog", "catalog_change"):
            self._apply_catalog_from_snapshot(payload)
            self._refresh_descriptors_in_place()
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
