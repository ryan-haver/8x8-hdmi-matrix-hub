"""Single entity factory for the Unfolded Circle Remote 3 integration (BE-22, DI-9, UC-10, UC-12, UC-13)."""

from __future__ import annotations

from typing import Any

# Standard UC command names (UC-12)
STANDARD_CEC_COMMANDS: tuple[str, ...] = (
    "CURSOR_UP",
    "CURSOR_DOWN",
    "CURSOR_LEFT",
    "CURSOR_RIGHT",
    "CURSOR_ENTER",
    "BACK",
    "HOME",
    "MENU",
    "PLAY_PAUSE",
    "VOLUME_UP",
    "VOLUME_DOWN",
    "MUTE_TOGGLE",
)

# Legacy CEC command names kept as aliases so existing activities/macros never break (UC-12, §4.3)
LEGACY_INPUT_CEC_COMMANDS: tuple[str, ...] = (
    "POWER_ON",
    "POWER_OFF",
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "SELECT",
    "MENU",
    "BACK",
    "PLAY",
    "PAUSE",
    "STOP",
    "PREVIOUS",
    "NEXT",
    "REWIND",
    "FAST_FORWARD",
    "VOLUME_UP",
    "VOLUME_DOWN",
    "MUTE",
)

LEGACY_OUTPUT_CEC_COMMANDS: tuple[str, ...] = (
    "POWER_ON",
    "POWER_OFF",
    "MUTE",
    "VOLUME_DOWN",
    "VOLUME_UP",
    "ACTIVE",
)

INPUT_CEC_SIMPLE_COMMANDS: list[str] = list(
    dict.fromkeys((*STANDARD_CEC_COMMANDS, *LEGACY_INPUT_CEC_COMMANDS))
)

OUTPUT_CEC_SIMPLE_COMMANDS: list[str] = list(
    dict.fromkeys((*LEGACY_OUTPUT_CEC_COMMANDS, *STANDARD_CEC_COMMANDS))
)

# Canonical mapping from UC standard / legacy CEC command names to hub CEC command keys
CEC_COMMAND_ALIASES: dict[str, str] = {
    "CURSOR_UP": "UP",
    "CURSOR_DOWN": "DOWN",
    "CURSOR_LEFT": "LEFT",
    "CURSOR_RIGHT": "RIGHT",
    "CURSOR_ENTER": "SELECT",
    "DPAD_UP": "UP",
    "DPAD_DOWN": "DOWN",
    "DPAD_LEFT": "LEFT",
    "DPAD_RIGHT": "RIGHT",
    "DPAD_MIDDLE": "SELECT",
    "BACK": "BACK",
    "HOME": "MENU",
    "MENU": "MENU",
    "PLAY_PAUSE": "PLAY",
    "PLAY": "PLAY",
    "PAUSE": "PAUSE",
    "STOP": "STOP",
    "PREVIOUS": "PREVIOUS",
    "NEXT": "NEXT",
    "REWIND": "REWIND",
    "FAST_FORWARD": "FAST_FORWARD",
    "VOLUME_UP": "VOLUME_UP",
    "VOLUME_DOWN": "VOLUME_DOWN",
    "MUTE_TOGGLE": "MUTE",
    "MUTE": "MUTE",
    "POWER_ON": "POWER_ON",
    "POWER_OFF": "POWER_OFF",
    "UP": "UP",
    "DOWN": "DOWN",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "SELECT": "SELECT",
    "ACTIVE": "ACTIVE",
}

SURVIVING_GOLDEN_ENTITY_IDS: frozenset[str] = frozenset(
    {
        "remote.orei_matrix",
        "switch.matrix_power",
        *(f"button.preset_{n}" for n in range(1, 9)),
        *(f"remote.input_{n}_cec" for n in range(1, 9)),
        *(f"remote.output_{n}_cec" for n in range(1, 9)),
        *(f"media_player.output_{n}" for n in range(1, 9)),
    }
)


def extract_input_names(snapshot: dict[str, Any] | None, count: int = 8) -> dict[int, str]:
    """Extract 1-indexed input names from a hub snapshot."""
    names = {i: f"Input {i}" for i in range(1, count + 1)}
    if not snapshot:
        return names

    raw_map = snapshot.get("input_names")
    if isinstance(raw_map, dict):
        for k, v in raw_map.items():
            try:
                idx = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= count and isinstance(v, str) and v.strip():
                names[idx] = v.strip()

    raw_inputs = snapshot.get("inputs")
    if isinstance(raw_inputs, dict):
        for k, v in raw_inputs.items():
            try:
                idx = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= count:
                if isinstance(v, str) and v.strip():
                    names[idx] = v.strip()
                elif isinstance(v, dict) and isinstance(v.get("name"), str) and v["name"].strip():
                    names[idx] = v["name"].strip()
    elif isinstance(raw_inputs, list):
        for pos, item in enumerate(raw_inputs, start=1):
            if isinstance(item, str) and item.strip() and pos <= count:
                names[pos] = item.strip()
            elif isinstance(item, dict):
                idx = int(item.get("port") or item.get("input") or item.get("number") or pos)
                label = item.get("name")
                if 1 <= idx <= count and isinstance(label, str) and label.strip():
                    names[idx] = label.strip()

    return names


def extract_output_names(snapshot: dict[str, Any] | None, count: int = 8) -> dict[int, str]:
    """Extract 1-indexed output names from a hub snapshot."""
    names = {i: f"Output {i}" for i in range(1, count + 1)}
    if not snapshot:
        return names

    raw_map = snapshot.get("output_names")
    if isinstance(raw_map, dict):
        for k, v in raw_map.items():
            try:
                idx = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= count and isinstance(v, str) and v.strip():
                names[idx] = v.strip()

    raw_outputs = snapshot.get("outputs")
    if isinstance(raw_outputs, dict):
        for k, v in raw_outputs.items():
            try:
                idx = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= count:
                if isinstance(v, str) and v.strip():
                    names[idx] = v.strip()
                elif isinstance(v, dict) and isinstance(v.get("name"), str) and v["name"].strip():
                    names[idx] = v["name"].strip()
    elif isinstance(raw_outputs, list):
        for pos, item in enumerate(raw_outputs, start=1):
            if isinstance(item, str) and item.strip() and pos <= count:
                names[pos] = item.strip()
            elif isinstance(item, dict):
                idx = int(item.get("port") or item.get("output") or item.get("number") or pos)
                label = item.get("name")
                if 1 <= idx <= count and isinstance(label, str) and label.strip():
                    names[idx] = label.strip()

    return names


def extract_presets(snapshot: dict[str, Any] | None, count: int = 8) -> list[dict[str, Any]]:
    """Extract preset metadata (number, name, favorite, visible) from a hub snapshot."""
    presets: dict[int, dict[str, Any]] = {
        n: {"number": n, "name": f"Preset {n}", "favorite": False, "visible": True}
        for n in range(1, count + 1)
    }
    if not snapshot:
        return [presets[n] for n in range(1, count + 1)]

    fav_list = snapshot.get("favorite_presets") or snapshot.get("favourites") or []
    fav_set = {int(x) for x in fav_list if isinstance(x, (int, str)) and str(x).isdigit()}
    for n in fav_set:
        if n in presets:
            presets[n]["favorite"] = True

    raw_presets = snapshot.get("presets")
    if isinstance(raw_presets, dict):
        for k, v in raw_presets.items():
            try:
                num = int(k)
            except (TypeError, ValueError):
                continue
            if num not in presets:
                continue
            if isinstance(v, str) and v.strip():
                presets[num]["name"] = v.strip()
            elif isinstance(v, dict):
                if isinstance(v.get("name"), str) and v["name"].strip():
                    presets[num]["name"] = v["name"].strip()
                if "favorite" in v or "favourite" in v:
                    presets[num]["favorite"] = bool(v.get("favorite", v.get("favourite")))
                if "visible" in v or "hidden" in v:
                    presets[num]["visible"] = bool(v.get("visible", not v.get("hidden", False)))
    elif isinstance(raw_presets, list):
        for pos, item in enumerate(raw_presets, start=1):
            if isinstance(item, str) and item.strip() and pos in presets:
                presets[pos]["name"] = item.strip()
            elif isinstance(item, dict):
                num = int(item.get("number") or item.get("preset") or item.get("id") or pos)
                if num not in presets:
                    continue
                if isinstance(item.get("name"), str) and item["name"].strip():
                    presets[num]["name"] = item["name"].strip()
                if "favorite" in item or "favourite" in item:
                    presets[num]["favorite"] = bool(item.get("favorite", item.get("favourite")))
                if "visible" in item or "hidden" in item:
                    presets[num]["visible"] = bool(item.get("visible", not item.get("hidden", False)))

    return [presets[n] for n in range(1, count + 1)]


def _is_pin_blocked(item: dict[str, Any]) -> bool:
    """Return True if a profile/scene is PIN-protected and not explicitly allowed on the Remote (§4.2)."""
    has_pin = bool(
        item.get("has_pin")
        or item.get("pin_protected")
        or item.get("passcode_required")
        or item.get("pin")
        or item.get("passcode")
    )
    if not has_pin:
        return False
    return not bool(item.get("allow_remote") or item.get("remote_allowed"))


def _extract_action_items(
    snapshot: dict[str, Any] | None,
    key: str,
    id_fields: tuple[str, ...] = ("id", "key"),
    *,
    check_pin: bool = False,
) -> list[dict[str, str]]:
    """Extract ordered (id, name) action descriptors from snapshot."""
    if not snapshot:
        return []
    raw = snapshot.get(key)
    items: list[dict[str, str]] = []
    if isinstance(raw, dict):
        for item_id, val in raw.items():
            if isinstance(val, dict):
                if check_pin and _is_pin_blocked(val):
                    continue
                if val.get("visible") is False or val.get("hidden") is True:
                    continue
                label = str(val.get("name") or val.get("label") or item_id)
            else:
                label = str(val or item_id)
            items.append({"id": str(item_id), "name": label})
    elif isinstance(raw, list):
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            if check_pin and _is_pin_blocked(entry):
                continue
            if entry.get("visible") is False or entry.get("hidden") is True:
                continue
            item_id = None
            for f in id_fields:
                if entry.get(f) is not None and str(entry.get(f)).strip():
                    item_id = str(entry[f]).strip()
                    break
            if not item_id:
                continue
            label = str(entry.get("name") or entry.get("label") or item_id)
            items.append({"id": item_id, "name": label})
    return items


def _build_cec_button_mapping(*, is_output: bool = False) -> list[dict[str, Any]]:
    """Build standard UC physical button mapping for CEC remotes (UC-12)."""
    mappings: list[dict[str, Any]] = [
        {"button": "POWER", "short_press": {"cmd_id": "toggle"}},
        {"button": "VOLUME_UP", "short_press": {"cmd_id": "VOLUME_UP"}},
        {"button": "VOLUME_DOWN", "short_press": {"cmd_id": "VOLUME_DOWN"}},
        {"button": "MUTE", "short_press": {"cmd_id": "MUTE_TOGGLE"}},
    ]
    if not is_output:
        mappings.extend(
            [
                {"button": "DPAD_UP", "short_press": {"cmd_id": "CURSOR_UP"}},
                {"button": "DPAD_DOWN", "short_press": {"cmd_id": "CURSOR_DOWN"}},
                {"button": "DPAD_LEFT", "short_press": {"cmd_id": "CURSOR_LEFT"}},
                {"button": "DPAD_RIGHT", "short_press": {"cmd_id": "CURSOR_RIGHT"}},
                {"button": "DPAD_MIDDLE", "short_press": {"cmd_id": "CURSOR_ENTER"}},
                {"button": "BACK", "short_press": {"cmd_id": "BACK"}},
                {"button": "HOME", "short_press": {"cmd_id": "HOME"}},
                {"button": "MENU", "short_press": {"cmd_id": "MENU"}},
                {"button": "PLAY", "short_press": {"cmd_id": "PLAY_PAUSE"}},
                {"button": "PREV", "short_press": {"cmd_id": "PREVIOUS"}},
                {"button": "NEXT", "short_press": {"cmd_id": "NEXT"}},
            ]
        )
    return mappings


def _ui_item(
    label: str,
    cmd_id: str,
    x: int,
    y: int,
    width: int = 2,
    height: int = 1,
    *,
    icon: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "type": "icon" if icon else "text",
        "text": label,
        "command": {"cmd_id": cmd_id},
        "location": {"x": x, "y": y},
        "size": {"width": width, "height": height},
    }
    if icon:
        item["icon"] = icon
    return item


def _grid_page(page_id: str, name: str, entries: list[tuple[str, str, str | None]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for idx, (label, cmd_id, icon) in enumerate(entries):
        x = (idx % 2) * 2
        y = idx // 2
        items.append(_ui_item(label, cmd_id, x, y, 2, 1, icon=icon))
    rows = max(6, (len(entries) + 1) // 2)
    return {
        "page_id": page_id,
        "name": name,
        "grid": {"width": 4, "height": rows},
        "items": items,
    }


def _build_input_cec_pages(port: int) -> list[dict[str, Any]]:
    nav_page = {
        "page_id": f"input_{port}_nav",
        "name": "Navigation",
        "grid": {"width": 4, "height": 6},
        "items": [
            _ui_item("Power On", "POWER_ON", 0, 0, 2, 1, icon="uc:power-on"),
            _ui_item("Power Off", "POWER_OFF", 2, 0, 2, 1, icon="uc:power-off"),
            _ui_item("Up", "CURSOR_UP", 1, 1, 2, 1, icon="uc:up-arrow"),
            _ui_item("Left", "CURSOR_LEFT", 0, 2, 1, 1, icon="uc:left-arrow"),
            _ui_item("OK", "CURSOR_ENTER", 1, 2, 2, 1, icon="uc:check"),
            _ui_item("Right", "CURSOR_RIGHT", 3, 2, 1, 1, icon="uc:right-arrow"),
            _ui_item("Down", "CURSOR_DOWN", 1, 3, 2, 1, icon="uc:down-arrow"),
            _ui_item("Menu", "MENU", 0, 4, 2, 1, icon="uc:menu"),
            _ui_item("Back", "BACK", 2, 4, 2, 1, icon="uc:back"),
            _ui_item("Home", "HOME", 1, 5, 2, 1, icon="uc:home"),
        ],
    }
    playback_page = {
        "page_id": f"input_{port}_playback",
        "name": "Playback",
        "grid": {"width": 4, "height": 6},
        "items": [
            _ui_item("Previous", "PREVIOUS", 0, 0, 1, 1, icon="uc:prev"),
            _ui_item("Rewind", "REWIND", 1, 0, 1, 1, icon="uc:bw"),
            _ui_item("Fast Forward", "FAST_FORWARD", 2, 0, 1, 1, icon="uc:fw"),
            _ui_item("Next", "NEXT", 3, 0, 1, 1, icon="uc:next"),
            _ui_item("Play/Pause", "PLAY_PAUSE", 0, 1, 2, 1, icon="uc:play-pause"),
            _ui_item("Stop", "STOP", 2, 1, 2, 1, icon="uc:stop"),
            _ui_item("Vol -", "VOLUME_DOWN", 0, 2, 1, 1, icon="uc:vol-down"),
            _ui_item("Mute", "MUTE_TOGGLE", 1, 2, 2, 1, icon="uc:mute"),
            _ui_item("Vol +", "VOLUME_UP", 3, 2, 1, 1, icon="uc:vol-up"),
        ],
    }
    return [nav_page, playback_page]


def _build_output_cec_pages(port: int) -> list[dict[str, Any]]:
    control_page = {
        "page_id": f"output_{port}_control",
        "name": "TV Control",
        "grid": {"width": 4, "height": 3},
        "items": [
            _ui_item("Power On", "POWER_ON", 0, 0, 2, 1, icon="uc:power-on"),
            _ui_item("Power Off", "POWER_OFF", 2, 0, 2, 1, icon="uc:power-off"),
            _ui_item("Active Input", "ACTIVE", 1, 1, 2, 1, icon="uc:input"),
            _ui_item("Vol -", "VOLUME_DOWN", 0, 2, 1, 1, icon="uc:vol-down"),
            _ui_item("Mute", "MUTE_TOGGLE", 1, 2, 2, 1, icon="uc:mute"),
            _ui_item("Vol +", "VOLUME_UP", 3, 2, 1, 1, icon="uc:vol-up"),
        ],
    }
    return [control_page]


def _build_matrix_remote(
    snapshot: dict[str, Any] | None,
    input_names: dict[int, str],
    presets: list[dict[str, Any]],
    port_count: int = 8,
) -> dict[str, Any]:
    """Build the `remote.orei_matrix` activity anchor entity (DI-9)."""
    profiles = _extract_action_items(snapshot, "profiles", ("id",), check_pin=True)
    scenes = _extract_action_items(snapshot, "scenes", ("id",), check_pin=True)
    shortcuts = _extract_action_items(snapshot, "shortcuts", ("key", "id"), check_pin=False)
    macros = _extract_action_items(snapshot, "macros", ("id",), check_pin=False)

    simple_commands: list[str] = [f"PRESET_{n}" for n in range(1, port_count + 1)]
    simple_commands.extend(f"ROUTE_ALL_IN_{n}" for n in range(1, port_count + 1))
    simple_commands.extend(f"PROFILE_{p['id']}" for p in profiles)
    simple_commands.extend(f"SCENE_{s['id']}" for s in scenes)
    simple_commands.extend(f"SHORTCUT_{sc['id']}" for sc in shortcuts)
    simple_commands.extend(f"MACRO_{m['id']}" for m in macros)

    pages: list[dict[str, Any]] = []

    fav_presets = [p for p in presets if p.get("favorite") and p.get("visible", True)]
    if fav_presets:
        pages.append(
            _grid_page(
                "orei_matrix_favourites",
                "Favourites",
                [(p["name"], f"PRESET_{p['number']}", "uc:star") for p in fav_presets],
            )
        )

    visible_presets = [p for p in presets if p.get("visible", True)]
    pages.append(
        _grid_page(
            "orei_matrix_main",
            "Presets",
            [(p["name"], f"PRESET_{p['number']}", "uc:grid") for p in visible_presets],
        )
    )

    pages.append(
        _grid_page(
            "orei_matrix_routing",
            "Route All",
            [
                (f"All -> {input_names[n]}", f"ROUTE_ALL_IN_{n}", "uc:input")
                for n in range(1, port_count + 1)
            ],
        )
    )

    if profiles:
        pages.append(
            _grid_page(
                "orei_matrix_profiles",
                "Profiles",
                [(p["name"], f"PROFILE_{p['id']}", "uc:bookmark") for p in profiles],
            )
        )

    if scenes:
        pages.append(
            _grid_page(
                "orei_matrix_scenes",
                "Scenes",
                [(s["name"], f"SCENE_{s['id']}", "uc:magic") for s in scenes],
            )
        )

    if shortcuts:
        pages.append(
            _grid_page(
                "orei_matrix_shortcuts",
                "Shortcuts",
                [(sc["name"], f"SHORTCUT_{sc['id']}", "uc:bolt") for sc in shortcuts],
            )
        )

    if macros:
        pages.append(
            _grid_page(
                "orei_matrix_macros",
                "Macros",
                [(m["name"], f"MACRO_{m['id']}", "uc:list") for m in macros],
            )
        )

    return {
        "entity_id": "remote.orei_matrix",
        "entity_type": "remote",
        "name": {"en": "OREI Matrix"},
        "icon": "uc:integration",
        "features": ["send_cmd"],
        "attributes": {"state": "ON"},
        "simple_commands": simple_commands,
        "button_mapping": [],
        "ui_pages": pages,
        "options": {
            "simple_commands": simple_commands,
            "button_mapping": [],
            "user_interface": {"pages": pages},
        },
    }


def build_entities(
    snapshot: dict[str, Any] | None = None,
    *,
    include_select: bool = True,
    include_legacy_sensors: bool = False,
) -> list[dict[str, Any]]:
    """Build the complete Unfolded Circle entity descriptor list from a hub snapshot.

    Preserves all surviving golden entity IDs (`remote.orei_matrix`,
    `button.preset_1..8`, `remote.input_1..8_cec`, `remote.output_1..8_cec`,
    `switch.matrix_power`, `media_player.output_1..8`), plus
    `select.output_1..8_source` (when ``include_select=True``) and binary
    sensors `sensor.output_1..8_display` and `sensor.input_1..8_signal` (`UC-13`).
    """
    snapshot = snapshot or {}
    port_count = int(snapshot.get("port_count") or 8)
    input_names = extract_input_names(snapshot, count=port_count)
    output_names = extract_output_names(snapshot, count=port_count)
    presets = extract_presets(snapshot, count=port_count)
    source_list = [input_names[i] for i in range(1, port_count + 1)]

    entities: list[dict[str, Any]] = []

    # 1. Activity anchor remote: remote.orei_matrix
    entities.append(_build_matrix_remote(snapshot, input_names, presets, port_count=port_count))

    # 2. Preset buttons: button.preset_1..8
    for preset in presets:
        n = preset["number"]
        entities.append(
            {
                "entity_id": f"button.preset_{n}",
                "entity_type": "button",
                "name": {"en": preset["name"]},
                "icon": "uc:star" if preset.get("favorite") else "uc:grid",
                "features": ["press"],
                "attributes": {"state": "AVAILABLE"},
                "visible": bool(preset.get("visible", True)),
                "favorite": bool(preset.get("favorite", False)),
            }
        )

    # 3. Source CEC remotes: remote.input_1..8_cec
    input_button_mapping = _build_cec_button_mapping(is_output=False)
    for n in range(1, port_count + 1):
        in_name = input_names[n]
        pages = _build_input_cec_pages(n)
        cmds = list(INPUT_CEC_SIMPLE_COMMANDS)
        entities.append(
            {
                "entity_id": f"remote.input_{n}_cec",
                "entity_type": "remote",
                "name": {"en": f"{in_name} CEC"},
                "icon": "uc:remote",
                "features": ["send_cmd", "on_off", "toggle"],
                "attributes": {"state": "UNKNOWN"},
                "simple_commands": cmds,
                "button_mapping": list(input_button_mapping),
                "ui_pages": pages,
                "options": {
                    "simple_commands": cmds,
                    "button_mapping": list(input_button_mapping),
                    "user_interface": {"pages": pages},
                },
            }
        )

    # 4. Binary input signal sensors: sensor.input_1..8_signal (UC-13)
    for n in range(1, port_count + 1):
        in_name = input_names[n]
        entities.append(
            {
                "entity_id": f"sensor.input_{n}_signal",
                "entity_type": "sensor",
                "name": {"en": f"{in_name} Signal"},
                "icon": "uc:signal",
                "features": [],
                "device_class": "binary",
                "attributes": {"state": "UNKNOWN", "value": None},
                "options": {},
            }
        )
        if include_legacy_sensors:
            entities.append(
                {
                    "entity_id": f"sensor.input_{n}_cable",
                    "entity_type": "sensor",
                    "name": {"en": f"{in_name} Cable"},
                    "icon": "uc:cable",
                    "features": [],
                    "device_class": "custom",
                    "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                    "options": {"custom_unit": ""},
                }
            )

    # 5. Matrix power switch: switch.matrix_power
    entities.append(
        {
            "entity_id": "switch.matrix_power",
            "entity_type": "switch",
            "name": {"en": "Matrix Power"},
            "icon": "uc:power-on",
            "features": ["on_off", "toggle"],
            "attributes": {"state": "UNKNOWN"},
        }
    )

    # 6. Per-output entities: media_player, select (optional), output CEC remote, binary display sensor
    output_button_mapping = _build_cec_button_mapping(is_output=True)
    for n in range(1, port_count + 1):
        out_name = output_names[n]
        entities.append(
            {
                "entity_id": f"media_player.output_{n}",
                "entity_type": "media_player",
                "name": {"en": out_name},
                "icon": "uc:tv",
                "features": [
                    "on_off",
                    "toggle",
                    "select_source",
                    "volume_up_down",
                    "mute_toggle",
                ],
                "device_class": "tv",
                "attributes": {
                    "state": "UNKNOWN",
                    "source_list": list(source_list),
                    "source": "",
                },
            }
        )

        if include_select:
            entities.append(
                {
                    "entity_id": f"select.output_{n}_source",
                    "entity_type": "select",
                    "name": {"en": f"{out_name} Source"},
                    "icon": "uc:input",
                    "features": [],
                    "attributes": {
                        "state": "ON",
                        "options": list(source_list),
                        "current_option": "",
                    },
                }
            )

        out_pages = _build_output_cec_pages(n)
        out_cmds = list(OUTPUT_CEC_SIMPLE_COMMANDS)
        entities.append(
            {
                "entity_id": f"remote.output_{n}_cec",
                "entity_type": "remote",
                "name": {"en": f"{out_name} TV"},
                "icon": "uc:tv",
                "features": ["send_cmd", "on_off", "toggle"],
                "attributes": {"state": "UNKNOWN"},
                "simple_commands": out_cmds,
                "button_mapping": list(output_button_mapping),
                "ui_pages": out_pages,
                "options": {
                    "simple_commands": out_cmds,
                    "button_mapping": list(output_button_mapping),
                    "user_interface": {"pages": out_pages},
                },
            }
        )

        entities.append(
            {
                "entity_id": f"sensor.output_{n}_display",
                "entity_type": "sensor",
                "name": {"en": f"{out_name} Display"},
                "icon": "uc:tv",
                "features": [],
                "device_class": "binary",
                "attributes": {"state": "UNKNOWN", "value": None},
                "options": {},
            }
        )

        if include_legacy_sensors:
            entities.extend(
                [
                    {
                        "entity_id": f"sensor.output_{n}_connected",
                        "entity_type": "sensor",
                        "name": {"en": f"{out_name} Connected"},
                        "icon": "uc:tv",
                        "features": [],
                        "device_class": "custom",
                        "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                        "options": {"custom_unit": ""},
                    },
                    {
                        "entity_id": f"sensor.output_{n}_cable",
                        "entity_type": "sensor",
                        "name": {"en": f"{out_name} Cable"},
                        "icon": "uc:cable",
                        "features": [],
                        "device_class": "custom",
                        "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                        "options": {"custom_unit": ""},
                    },
                    {
                        "entity_id": f"sensor.output_{n}_source",
                        "entity_type": "sensor",
                        "name": {"en": f"{out_name} Source"},
                        "icon": "uc:input",
                        "features": [],
                        "device_class": "custom",
                        "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                        "options": {"custom_unit": ""},
                    },
                ]
            )

    return entities
