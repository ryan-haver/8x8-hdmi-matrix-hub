"""Single entity factory and ucapi entity converter for the Unfolded Circle Remote 3 integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, is_dataclass
from typing import Any

import ucapi
from ucapi import Button, MediaPlayer, Sensor, StatusCodes, Switch
from ucapi.media_player import DeviceClasses as MediaPlayerDeviceClasses
from ucapi.media_player import Features as MediaPlayerFeatures
from ucapi.remote import Features as RemoteFeatures
from ucapi.remote import Remote
from ucapi.select import Select
from ucapi.sensor import DeviceClasses as SensorDeviceClasses
from ucapi.switch import Features as SwitchFeatures

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

OUTPUT_CEC_COMMAND_SET: frozenset[str] = frozenset(LEGACY_OUTPUT_CEC_COMMANDS)

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

APPROVED_GOLDEN_ENTITY_IDS: frozenset[str] = frozenset(
    {
        *SURVIVING_GOLDEN_ENTITY_IDS,
        *(f"sensor.input_{n}_signal" for n in range(1, 9)),
        *(f"sensor.input_{n}_cable" for n in range(1, 9)),
        *(f"sensor.output_{n}_connected" for n in range(1, 9)),
        *(f"sensor.output_{n}_cable" for n in range(1, 9)),
        *(f"sensor.output_{n}_source" for n in range(1, 9)),
    }
)


def normalize_snapshot(snapshot: Any) -> dict[str, Any]:
    """Normalize a :class:`HubSnapshot` dataclass or mapping into a plain dictionary."""
    if snapshot is None:
        return {}
    if isinstance(snapshot, Mapping):
        return dict(snapshot)
    if is_dataclass(snapshot):
        return asdict(snapshot)
    result: dict[str, Any] = {}
    for attr in (
        "connected",
        "connection_state",
        "device_state",
        "power",
        "routing",
        "input_names",
        "output_names",
        "preset_names",
        "presets",
        "input_signals",
        "input_cables",
        "output_displays",
        "output_cables",
        "favorite_presets",
        "profiles",
        "scenes",
        "shortcuts",
        "macros",
        "port_count",
    ):
        if hasattr(snapshot, attr):
            val = getattr(snapshot, attr)
            if val is not None:
                result[attr] = val
    return result


def extract_input_names(snapshot: Any = None, count: int = 8) -> dict[int, str]:
    """Extract 1-indexed input names from a hub snapshot."""
    snap = normalize_snapshot(snapshot)
    names = {i: f"Input {i}" for i in range(1, count + 1)}
    if not snap:
        return names

    raw_map = snap.get("input_names")
    if isinstance(raw_map, Mapping):
        for k, v in raw_map.items():
            try:
                idx = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= count and isinstance(v, str) and v.strip():
                names[idx] = v.strip()

    raw_inputs = snap.get("inputs")
    if isinstance(raw_inputs, Mapping):
        for k, v in raw_inputs.items():
            try:
                idx = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= count:
                if isinstance(v, str) and v.strip():
                    names[idx] = v.strip()
                elif isinstance(v, Mapping) and isinstance(v.get("name"), str) and v["name"].strip():
                    names[idx] = v["name"].strip()
    elif isinstance(raw_inputs, list):
        for pos, item in enumerate(raw_inputs, start=1):
            if isinstance(item, str) and item.strip() and pos <= count:
                names[pos] = item.strip()
            elif isinstance(item, Mapping):
                idx = int(item.get("port") or item.get("input") or item.get("number") or pos)
                label = item.get("name")
                if 1 <= idx <= count and isinstance(label, str) and label.strip():
                    names[idx] = label.strip()

    return names


def extract_output_names(snapshot: Any = None, count: int = 8) -> dict[int, str]:
    """Extract 1-indexed output names from a hub snapshot."""
    snap = normalize_snapshot(snapshot)
    names = {i: f"Output {i}" for i in range(1, count + 1)}
    if not snap:
        return names

    raw_map = snap.get("output_names")
    if isinstance(raw_map, Mapping):
        for k, v in raw_map.items():
            try:
                idx = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= count and isinstance(v, str) and v.strip():
                names[idx] = v.strip()

    raw_outputs = snap.get("outputs")
    if isinstance(raw_outputs, Mapping):
        for k, v in raw_outputs.items():
            try:
                idx = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= count:
                if isinstance(v, str) and v.strip():
                    names[idx] = v.strip()
                elif isinstance(v, Mapping) and isinstance(v.get("name"), str) and v["name"].strip():
                    names[idx] = v["name"].strip()
    elif isinstance(raw_outputs, list):
        for pos, item in enumerate(raw_outputs, start=1):
            if isinstance(item, str) and item.strip() and pos <= count:
                names[pos] = item.strip()
            elif isinstance(item, Mapping):
                idx = int(item.get("port") or item.get("output") or item.get("number") or pos)
                label = item.get("name")
                if 1 <= idx <= count and isinstance(label, str) and label.strip():
                    names[idx] = label.strip()

    return names


def extract_favorite_preset_numbers(snapshot: Any = None, count: int = 8) -> list[int]:
    """Extract ordered 1-indexed favorite preset numbers from a hub snapshot."""
    snap = normalize_snapshot(snapshot)
    if not snap:
        return []

    fav_list = snap.get("favorite_presets") or snap.get("favourites")
    ordered: list[int] = []
    if isinstance(fav_list, (list, tuple)):
        for x in fav_list:
            try:
                num = int(x)
            except (TypeError, ValueError):
                continue
            if 1 <= num <= count and num not in ordered:
                ordered.append(num)

    raw_presets = snap.get("presets")
    if isinstance(raw_presets, list):
        for pos, item in enumerate(raw_presets, start=1):
            if isinstance(item, Mapping):
                num = int(item.get("number") or item.get("preset") or item.get("id") or pos)
                if 1 <= num <= count and bool(item.get("favorite", item.get("favourite"))):
                    if item.get("visible", not item.get("hidden", False)):
                        if num not in ordered:
                            ordered.append(num)
    elif isinstance(raw_presets, Mapping):
        for k, v in raw_presets.items():
            try:
                num = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= num <= count and isinstance(v, Mapping):
                if bool(v.get("favorite", v.get("favourite"))) and v.get(
                    "visible", not v.get("hidden", False)
                ):
                    if num not in ordered:
                        ordered.append(num)

    return ordered


def extract_presets(snapshot: Any = None, count: int = 8) -> list[dict[str, Any]]:
    """Extract preset metadata (number, name, favorite, visible) from a hub snapshot."""
    snap = normalize_snapshot(snapshot)
    presets: dict[int, dict[str, Any]] = {
        n: {"number": n, "name": f"Preset {n}", "favorite": False, "visible": True}
        for n in range(1, count + 1)
    }
    if not snap:
        return [presets[n] for n in range(1, count + 1)]

    fav_list = snap.get("favorite_presets") or snap.get("favourites") or []
    fav_set: set[int] = set()
    if isinstance(fav_list, (list, tuple, set)):
        for x in fav_list:
            try:
                fav_set.add(int(x))
            except (TypeError, ValueError):
                continue
    for n in fav_set:
        if n in presets:
            presets[n]["favorite"] = True

    raw_preset_names = snap.get("preset_names")
    if isinstance(raw_preset_names, Mapping):
        for k, v in raw_preset_names.items():
            try:
                num = int(k)
            except (TypeError, ValueError):
                continue
            if num in presets and isinstance(v, str) and v.strip():
                presets[num]["name"] = v.strip()
    elif isinstance(raw_preset_names, list):
        for pos, v in enumerate(raw_preset_names, start=1):
            if pos in presets and isinstance(v, str) and v.strip():
                presets[pos]["name"] = v.strip()

    raw_presets = snap.get("presets")
    if isinstance(raw_presets, Mapping):
        for k, v in raw_presets.items():
            try:
                num = int(k)
            except (TypeError, ValueError):
                continue
            if num not in presets:
                continue
            if isinstance(v, str) and v.strip():
                presets[num]["name"] = v.strip()
            elif isinstance(v, Mapping):
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
            elif isinstance(item, Mapping):
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


def is_item_pin_blocked(item: Mapping[str, Any]) -> bool:
    """Return True if a profile/scene is PIN/password-protected and not explicitly allowed on Remote."""
    has_pin = bool(
        item.get("password_protected")
        or item.get("requires_pin")
        or item.get("pin_required")
        or item.get("has_pin")
        or item.get("pin_protected")
        or item.get("passcode_required")
        or item.get("pin")
        or item.get("passcode")
        or item.get("pin_hash")
    )
    if not has_pin:
        return False
    return not bool(item.get("allow_remote") or item.get("remote_allowed"))


_is_pin_blocked = is_item_pin_blocked


def _extract_action_items(
    snapshot: Mapping[str, Any] | None,
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
    if isinstance(raw, Mapping):
        for item_id, val in raw.items():
            if isinstance(val, Mapping):
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
            if not isinstance(entry, Mapping):
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


def _build_input_cec_pages(port: int, *, compatible: bool = False) -> list[dict[str, Any]]:
    if compatible:
        nav_page = {
            "page_id": f"input_{port}_nav",
            "name": "Navigation",
            "grid": {"width": 4, "height": 6},
            "items": [
                _ui_item("Power On", "POWER_ON", 0, 0, 2, 1),
                _ui_item("Power Off", "POWER_OFF", 2, 0, 2, 1),
                _ui_item("▲", "UP", 1, 1, 2, 1),
                _ui_item("◀", "LEFT", 0, 2, 1, 1),
                _ui_item("OK", "SELECT", 1, 2, 2, 1),
                _ui_item("▶", "RIGHT", 3, 2, 1, 1),
                _ui_item("▼", "DOWN", 1, 3, 2, 1),
                _ui_item("Menu", "MENU", 0, 4, 2, 1),
                _ui_item("Back", "BACK", 2, 4, 2, 1),
            ],
        }
        playback_page = {
            "page_id": f"input_{port}_playback",
            "name": "Playback",
            "grid": {"width": 4, "height": 6},
            "items": [
                _ui_item("⏮", "PREVIOUS", 0, 0, 1, 1),
                _ui_item("⏪", "REWIND", 1, 0, 1, 1),
                _ui_item("⏩", "FAST_FORWARD", 2, 0, 1, 1),
                _ui_item("⏭", "NEXT", 3, 0, 1, 1),
                _ui_item("▶ Play", "PLAY", 0, 1, 2, 1),
                _ui_item("⏸ Pause", "PAUSE", 2, 1, 2, 1),
                _ui_item("⏹ Stop", "STOP", 1, 2, 2, 1),
                _ui_item("🔉 Vol-", "VOLUME_DOWN", 0, 3, 1, 1),
                _ui_item("🔇 Mute", "MUTE", 1, 3, 2, 1),
                _ui_item("🔊 Vol+", "VOLUME_UP", 3, 3, 1, 1),
            ],
        }
        return [nav_page, playback_page]

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


def _build_output_cec_pages(port: int, *, compatible: bool = False) -> list[dict[str, Any]]:
    if compatible:
        control_page = {
            "page_id": f"output_{port}_control",
            "name": "TV Control",
            "grid": {"width": 4, "height": 3},
            "items": [
                _ui_item("📺 Power On", "POWER_ON", 0, 0, 2, 1),
                _ui_item("⏻ Power Off", "POWER_OFF", 2, 0, 2, 1),
                _ui_item("Input", "ACTIVE", 1, 1, 2, 1),
                _ui_item("🔉", "VOLUME_DOWN", 0, 2, 1, 1),
                _ui_item("🔇 Mute", "MUTE", 1, 2, 2, 1),
                _ui_item("🔊", "VOLUME_UP", 3, 2, 1, 1),
            ],
        }
        return [control_page]

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
    snapshot: Mapping[str, Any] | None,
    input_names: dict[int, str],
    presets: list[dict[str, Any]],
    port_count: int = 8,
    *,
    compatible: bool = False,
) -> dict[str, Any]:
    """Build the `remote.orei_matrix` activity anchor entity."""
    preset_by_num = {p["number"]: p for p in presets}
    fav_numbers = extract_favorite_preset_numbers(snapshot, count=port_count)

    if compatible:
        simple_commands = [f"PRESET_{n}" for n in range(1, port_count + 1)]
        pages: list[dict[str, Any]] = []
        if fav_numbers:
            pages.append(
                _grid_page(
                    "orei_matrix_favourites",
                    "Favourites",
                    [
                        (preset_by_num[n]["name"], f"PRESET_{n}", None)
                        for n in fav_numbers
                        if n in preset_by_num
                    ],
                )
            )
        pages.append(
            _grid_page(
                "orei_matrix_main",
                "Presets",
                [
                    (preset_by_num[n]["name"], f"PRESET_{n}", None)
                    for n in range(1, port_count + 1)
                ],
            )
        )
        return {
            "entity_id": "remote.orei_matrix",
            "entity_type": "remote",
            "name": {"en": "OREI Matrix"},
            "features": ["send_cmd"],
            "attributes": {"state": "ON"},
            "simple_commands": simple_commands,
            "button_mapping": [],
            "ui_pages": pages,
            "options": {
                "simple_commands": simple_commands,
                "user_interface": {"pages": pages},
            },
        }

    profiles = _extract_action_items(snapshot, "profiles", ("id",), check_pin=True)
    scenes = _extract_action_items(snapshot, "scenes", ("id",), check_pin=True)
    shortcuts = _extract_action_items(snapshot, "shortcuts", ("key", "id"), check_pin=False)
    macros = _extract_action_items(snapshot, "macros", ("id",), check_pin=False)

    simple_commands = [f"PRESET_{n}" for n in range(1, port_count + 1)]
    simple_commands.extend(f"ROUTE_ALL_IN_{n}" for n in range(1, port_count + 1))
    simple_commands.extend(f"PROFILE_{p['id']}" for p in profiles)
    simple_commands.extend(f"SCENE_{s['id']}" for s in scenes)
    simple_commands.extend(f"SHORTCUT_{sc['id']}" for sc in shortcuts)
    simple_commands.extend(f"MACRO_{m['id']}" for m in macros)

    pages = []
    fav_presets = [
        preset_by_num[n]
        for n in fav_numbers
        if n in preset_by_num and preset_by_num[n].get("visible", True)
    ]
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


def build_compatible_entities(snapshot: Any = None) -> list[dict[str, Any]]:
    """Build the 74 approved golden entity descriptors for the active UC bridge.

    Matches `tests/uc/golden/entities.json` and `src/driver.py` entity IDs,
    device classes, features, and target-specific CEC simple_commands.
    """
    snap = normalize_snapshot(snapshot)
    port_count = int(snap.get("port_count") or 8)
    input_names = extract_input_names(snap, count=port_count)
    output_names = extract_output_names(snap, count=port_count)
    presets = extract_presets(snap, count=port_count)
    source_list = [input_names[i] for i in range(1, port_count + 1)]

    entities: list[dict[str, Any]] = []

    # 1. remote.orei_matrix
    entities.append(
        _build_matrix_remote(snap, input_names, presets, port_count=port_count, compatible=True)
    )

    # 2. button.preset_1..8
    for preset in presets:
        n = preset["number"]
        entities.append(
            {
                "entity_id": f"button.preset_{n}",
                "entity_type": "button",
                "name": {"en": preset["name"]},
                "features": ["press"],
                "attributes": {"state": "AVAILABLE"},
                "visible": bool(preset.get("visible", True)),
                "favorite": bool(preset.get("favorite", False)),
            }
        )

    # 3. remote.input_1..8_cec
    for n in range(1, port_count + 1):
        in_name = input_names[n]
        pages = _build_input_cec_pages(n, compatible=True)
        cmds = list(LEGACY_INPUT_CEC_COMMANDS)
        entities.append(
            {
                "entity_id": f"remote.input_{n}_cec",
                "entity_type": "remote",
                "name": {"en": f"{in_name} CEC"},
                "features": ["send_cmd", "on_off", "toggle"],
                "attributes": {"state": "UNKNOWN"},
                "simple_commands": cmds,
                "button_mapping": [],
                "ui_pages": pages,
                "options": {
                    "simple_commands": cmds,
                    "user_interface": {"pages": pages},
                },
            }
        )

    # 4. sensor.input_1..8_signal
    for n in range(1, port_count + 1):
        in_name = input_names[n]
        entities.append(
            {
                "entity_id": f"sensor.input_{n}_signal",
                "entity_type": "sensor",
                "name": {"en": f"{in_name} Signal"},
                "features": [],
                "device_class": "custom",
                "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                "options": {"custom_unit": ""},
            }
        )

    # 5. sensor.input_1..8_cable
    for n in range(1, port_count + 1):
        in_name = input_names[n]
        entities.append(
            {
                "entity_id": f"sensor.input_{n}_cable",
                "entity_type": "sensor",
                "name": {"en": f"{in_name} Cable"},
                "features": [],
                "device_class": "custom",
                "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                "options": {"custom_unit": ""},
            }
        )

    # 6. switch.matrix_power
    entities.append(
        {
            "entity_id": "switch.matrix_power",
            "entity_type": "switch",
            "name": {"en": "Matrix Power"},
            "features": ["on_off", "toggle"],
            "attributes": {"state": "UNKNOWN"},
        }
    )

    # 7. Per-output entities: media_player, output CEC remote, and 3 custom sensors
    for n in range(1, port_count + 1):
        out_name = output_names[n]
        entities.append(
            {
                "entity_id": f"media_player.output_{n}",
                "entity_type": "media_player",
                "name": {"en": out_name},
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

        out_pages = _build_output_cec_pages(n, compatible=True)
        out_cmds = list(LEGACY_OUTPUT_CEC_COMMANDS)
        entities.append(
            {
                "entity_id": f"remote.output_{n}_cec",
                "entity_type": "remote",
                "name": {"en": f"{out_name} TV"},
                "features": ["send_cmd", "on_off", "toggle"],
                "attributes": {"state": "UNKNOWN"},
                "simple_commands": out_cmds,
                "button_mapping": [],
                "ui_pages": out_pages,
                "options": {
                    "simple_commands": out_cmds,
                    "user_interface": {"pages": out_pages},
                },
            }
        )

        entities.extend(
            [
                {
                    "entity_id": f"sensor.output_{n}_connected",
                    "entity_type": "sensor",
                    "name": {"en": f"{out_name} Connected"},
                    "features": [],
                    "device_class": "custom",
                    "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                    "options": {"custom_unit": ""},
                },
                {
                    "entity_id": f"sensor.output_{n}_cable",
                    "entity_type": "sensor",
                    "name": {"en": f"{out_name} Cable"},
                    "features": [],
                    "device_class": "custom",
                    "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                    "options": {"custom_unit": ""},
                },
                {
                    "entity_id": f"sensor.output_{n}_source",
                    "entity_type": "sensor",
                    "name": {"en": f"{out_name} Source"},
                    "features": [],
                    "device_class": "custom",
                    "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                    "options": {"custom_unit": ""},
                },
            ]
        )

    return entities


def build_entities(
    snapshot: Any = None,
    *,
    include_select: bool = True,
    include_legacy_sensors: bool = False,
) -> list[dict[str, Any]]:
    """Build the Unfolded Circle entity descriptor list from a hub snapshot.

    Preserves all surviving golden entity IDs (`remote.orei_matrix`,
    `button.preset_1..8`, `remote.input_1..8_cec`, `remote.output_1..8_cec`,
    `switch.matrix_power`, `media_player.output_1..8`), plus
    `select.output_1..8_source` (when ``include_select=True``) and sensors.
    When ``include_select=False`` and ``include_legacy_sensors=True``, emits
    the 74 approved golden entity IDs without duplicate display sensors.
    """
    snap = normalize_snapshot(snapshot)
    port_count = int(snap.get("port_count") or 8)
    input_names = extract_input_names(snap, count=port_count)
    output_names = extract_output_names(snap, count=port_count)
    presets = extract_presets(snap, count=port_count)
    source_list = [input_names[i] for i in range(1, port_count + 1)]

    entities: list[dict[str, Any]] = []

    # 1. Activity anchor remote: remote.orei_matrix
    entities.append(_build_matrix_remote(snap, input_names, presets, port_count=port_count))

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

    # 4. Input signal & cable sensors
    for n in range(1, port_count + 1):
        in_name = input_names[n]
        if include_legacy_sensors:
            entities.append(
                {
                    "entity_id": f"sensor.input_{n}_signal",
                    "entity_type": "sensor",
                    "name": {"en": f"{in_name} Signal"},
                    "icon": "uc:signal",
                    "features": [],
                    "device_class": "custom",
                    "attributes": {"state": "UNKNOWN", "value": "Unknown"},
                    "options": {"custom_unit": ""},
                }
            )
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
        else:
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

    # 6. Per-output entities: media_player, select (optional), output CEC remote, sensors
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
        else:
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

    return entities


def to_ucapi_entity(
    desc: Mapping[str, Any],
    cmd_handler: Callable[..., Awaitable[StatusCodes]] | None = None,
) -> ucapi.Entity:
    """Convert an entity descriptor dictionary into an actual `ucapi.Entity` instance."""
    entity_id = str(desc["entity_id"])
    entity_type = str(desc["entity_type"])
    name = desc.get("name") or entity_id
    attrs = dict(desc.get("attributes") or {})
    icon = desc.get("icon")

    if entity_type == "button":
        btn = Button(
            entity_id,
            name,
            icon=icon,
            cmd_handler=cmd_handler,
        )
        if attrs:
            btn.attributes.update(attrs)
        return btn

    if entity_type == "remote":
        features = [RemoteFeatures(f) for f in (desc.get("features") or [])]
        opts = desc.get("options") or {}
        simple_commands = desc.get("simple_commands") or opts.get("simple_commands")
        button_mapping = desc.get("button_mapping")
        if button_mapping is None and "button_mapping" in opts:
            button_mapping = opts["button_mapping"]
        ui_pages = desc.get("ui_pages")
        if ui_pages is None and isinstance(opts.get("user_interface"), Mapping):
            ui_pages = opts["user_interface"].get("pages")
        return Remote(
            entity_id,
            name,
            features,
            attrs,
            simple_commands=list(simple_commands) if simple_commands else None,
            button_mapping=list(button_mapping) if button_mapping else None,
            ui_pages=list(ui_pages) if ui_pages else None,
            icon=icon,
            cmd_handler=cmd_handler,
        )

    if entity_type == "media_player":
        features = [MediaPlayerFeatures(f) for f in (desc.get("features") or [])]
        dev_cls = desc.get("device_class")
        mp_cls = MediaPlayerDeviceClasses(dev_cls) if dev_cls else MediaPlayerDeviceClasses.TV
        return MediaPlayer(
            entity_id,
            name,
            features,
            attrs,
            device_class=mp_cls,
            options=dict(desc.get("options") or {}) or None,
            icon=icon,
            cmd_handler=cmd_handler,
        )

    if entity_type == "switch":
        features = [SwitchFeatures(f) for f in (desc.get("features") or [])]
        return Switch(
            entity_id,
            name,
            features,
            attrs,
            options=dict(desc.get("options") or {}) or None,
            icon=icon,
            cmd_handler=cmd_handler,
        )

    if entity_type == "sensor":
        dev_cls = desc.get("device_class")
        sensor_cls = SensorDeviceClasses(dev_cls) if dev_cls else SensorDeviceClasses.CUSTOM
        opts = desc.get("options")
        return Sensor(
            entity_id,
            name,
            [],
            attrs,
            device_class=sensor_cls,
            options=dict(opts) if opts is not None else None,
            icon=icon,
        )

    if entity_type == "select":
        return Select(
            entity_id,
            name,
            attrs,
            icon=icon,
            cmd_handler=cmd_handler,
        )

    raise ValueError(f"Unsupported UC entity_type: {entity_type!r}")


def build_ucapi_entities(
    snapshot: Any = None,
    cmd_handler: Callable[..., Awaitable[StatusCodes]] | None = None,
    *,
    compatible: bool = True,
    include_select: bool = False,
    include_legacy_sensors: bool = True,
) -> list[ucapi.Entity]:
    """Build actual `ucapi.Entity` instances from a snapshot."""
    if compatible and not include_select and include_legacy_sensors:
        descriptors = build_compatible_entities(snapshot)
    else:
        descriptors = build_entities(
            snapshot,
            include_select=include_select,
            include_legacy_sensors=include_legacy_sensors,
        )
    return [to_ucapi_entity(desc, cmd_handler=cmd_handler) for desc in descriptors]
