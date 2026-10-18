"""Versioned persistence for every JSON file the hub keeps on disk (PER-04, API-12).

Why
===
Each persisted file used to grow its own ad-hoc "read whatever shape is there"
loader. A file written by an older release then silently lost data, and there
was no way to tell a current file from a legacy one. This module makes the
schema version an explicit, per-file contract:

* every managed file carries a top-level ``schema_version`` integer,
* a file below :data:`CURRENT_SCHEMA_VERSION` is migrated by an ordered chain of
  pure functions (one per version step),
* the pre-migration bytes are copied to ``<name>.v<old>.bak`` **before** any
  function runs, so a bad migration can always be undone by hand, and
* the migrated payload is written through the project's atomic JSON writer
  (PER-01/PER-02), so a crash mid-migration leaves the backup and either the
  old or the new file — never a half-written one.

What is *not* done
==================
Migrations never delete unknown top-level keys. A file written by a newer
release, or by a fork with extra keys, keeps them; the point of a migration is
to add what is missing, not to decide what the operator is allowed to keep.

``flic_buttons.json`` and ``shortcuts.json`` are flat maps (their keys are
Bluetooth addresses / shortcut keys, not schema fields). Their v1 migration
therefore stamps ``schema_version`` alongside the record keys. That key can
never collide with a real record key; the readers that consume these two files
are expected to skip it (Phase 4 wiring).

The file names
==============
:data:`LEGACY_FILENAMES` maps a retired file name to the canonical one. The
runtime ships with ``system_shortcuts.json`` as the canonical shortcuts
file; the registry alias ``shortcuts.json`` may also be present in older
installations and is migrated in place instead of being silently ignored
or destructively renamed.
"""

from __future__ import annotations

import logging
import re
import shutil
import sys
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# The runtime puts ``src/`` on sys.path (run.py, rest_api/utils.py do the same)
# so that top-level modules can import each other; ``hub.persistence`` is a
# package inside that same directory.
_SRC_DIR = Path(__file__).resolve().parents[2]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from _file_io import atomic_read_json, atomic_write_json  # noqa: E402

_LOG = logging.getLogger("hub.persistence")

#: The key every managed file carries at its top level.
SCHEMA_VERSION_KEY = "schema_version"

#: The schema version this release writes (PER-04).
CURRENT_SCHEMA_VERSION = 2

#: Retired file name -> canonical name, for files that were renamed in flight.
#: ``shortcuts.json`` is the legacy name; the runtime uses ``system_shortcuts.json``
#: as the canonical shortcuts file. Importing the alias via the runtime
#: barrier is non-destructive.
LEGACY_FILENAMES: dict[str, str] = {
    "shortcuts.json": "system_shortcuts.json",
}

#: The persisted JSON files the hub owns and migrates.
MANAGED_FILENAMES: tuple[str, ...] = (
    "scenes_v2.json",
    "profiles.json",
    "cec_macros.json",
    "system_shortcuts.json",
    "dashboard_layout.json",
    "device_settings.json",
    "flic_buttons.json",
)

#: A migration rewrites one payload from ``to_version - 1`` to ``to_version``.
MigrationFunction = Callable[[Any], Any]


class MigrationError(ValueError):
    """A payload has a shape no migration can turn into the current one."""


class SchemaVersionError(MigrationError):
    """A file was written by a newer release than this one understands."""


def is_button_key(key: str) -> bool:
    """Whether a flat-map key identifies a button rather than extension metadata."""
    return bool(re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", key))


def is_shortcut_key(key: str) -> bool:
    key = _normalize_shortcut_key(key)
    return key.startswith("user.") or key in {
        "route_all_to_output",
        "route_one_to_one",
        "power_off_all",
        "mute_all_audio",
        "unmute_all_audio",
        "beep_on",
        "beep_off",
        "panel_lock_on",
        "panel_lock_off",
        "system_reboot",
        "lcd_timeout_off",
        "lcd_timeout_10s",
        "lcd_timeout_30s",
        "lcd_timeout_60s",
        "lcd_timeout_always_on",
        *(f"preset_recall_{n}" for n in range(1, 9)),
    }


def flat_map_records(filename: str, payload: Mapping) -> dict[str, dict]:
    """Reader seam for R5: schema/extension metadata never count as records.

    Call after ``load_versioned_json`` and save surviving records with
    ``save_versioned_json``; the latter preserves opaque metadata and unknown
    fields without resurrecting deleted records. Public callers still project
    the known button fields rather than returning this private storage view.
    """
    predicate = is_button_key if filename == "flic_buttons.json" else is_shortcut_key
    return {key: dict(value) for key, value in payload.items() if predicate(key) and isinstance(value, Mapping)}


def validate_payload(filename: str, payload: Any) -> None:
    """Reject shapes that readers would otherwise silently discard or default.

    Legacy optional fields can be absent; a present known container must have
    the supported shape. Extension keys are opaque, including scalar flat-map
    metadata. Validation never hashes PINs or changes the payload.
    """
    filename = LEGACY_FILENAMES.get(filename, filename)
    if filename == "scenes.json":
        from .startup import scene_shape

        if scene_shape(payload) not in ("legacy", "empty"):
            raise MigrationError("scenes.json: legacy writer cannot overwrite unified scenes")
        return
    if isinstance(payload, Mapping) and SCHEMA_VERSION_KEY in payload:
        version = payload[SCHEMA_VERSION_KEY]
        if isinstance(version, bool) or not isinstance(version, int) or version < 0:
            raise MigrationError(f"{filename}: invalid schema_version")
        if version > CURRENT_SCHEMA_VERSION:
            raise SchemaVersionError(f"{filename}: schema_version {version} is newer than {CURRENT_SCHEMA_VERSION}")
    collections = {
        "profiles.json": "profiles",
        "scenes_v2.json": "scenes",
        "cec_macros.json": "macros",
        "dashboard_layout.json": "cards",
    }
    collection = collections.get(filename)
    if collection:
        if collection == "cards" and isinstance(payload, Mapping) and "version" in payload:
            _validate_integer(filename, "version", payload["version"])
        records = payload.get(collection) if isinstance(payload, Mapping) else payload
        if not isinstance(records, list) or any(not isinstance(r, Mapping) for r in records):
            raise MigrationError(f"{filename}: {collection} must be a list of objects")
        identities = set()
        for record in records:
            if collection == "cards" and not isinstance(record.get("type"), str):
                raise MigrationError(f"{filename}: invalid card type")
            identity = (record.get("type"), record.get("id")) if collection == "cards" else record.get("id")
            if not isinstance(record.get("id"), str) or not record["id"] or identity in identities:
                raise MigrationError(f"{filename}: missing or duplicate record identity")
            identities.add(identity)
            for key in ("name", "icon", "passcode_hash"):
                if key in record and record[key] is not None and not isinstance(record[key], str):
                    raise MigrationError(f"{filename}: invalid {key}")
            for key in ("pinned", "favorite", "dashboard_visible", "password_protected", "continue_on_error"):
                if key in record and not isinstance(record[key], bool):
                    raise MigrationError(f"{filename}: {key} must be a boolean")
            for key in ("dashboard_order", "pin_order", "order"):
                if key in record:
                    _validate_integer(filename, key, record[key])
            if filename == "scenes_v2.json" and "outputs" in record:
                raise MigrationError(f"{filename}: legacy output-state scene in unified catalog")
            if collection == "cards" and record.get("type") not in {
                "profile",
                "preset",
                "system_shortcut",
                "macro",
                "scene",
                "aggregate_widget",
            }:
                raise MigrationError(f"{filename}: unsupported card type")
            for key in ("outputs", "cec_config", "overrides", "params"):
                if key in record and not isinstance(record[key], Mapping):
                    raise MigrationError(f"{filename}: {key} must be an object")
            for key in ("steps", "actions", "items", "macros", "execution_log", "execution_history"):
                if key in record and not isinstance(record[key], list):
                    raise MigrationError(f"{filename}: {key} must be a list")
            if "outputs" in record:
                for port, setting in record["outputs"].items():
                    if not str(port).isdigit() or not isinstance(setting, Mapping):
                        raise MigrationError(f"{filename}: invalid output settings")
                    if "input" in setting and (
                        isinstance(setting["input"], bool)
                        or not isinstance(setting["input"], int)
                        or not 1 <= setting["input"] <= 8
                    ):
                        raise MigrationError(f"{filename}: invalid output input")
            for key in ("nav_targets", "playback_targets", "volume_targets", "power_on_targets", "power_off_targets"):
                config = record.get("cec_config", {})
                if key in config and not isinstance(config[key], list):
                    raise MigrationError(f"{filename}: invalid CEC targets")
            for profile_outputs in record.get("overrides", {}).values():
                if not isinstance(profile_outputs, Mapping) or any(
                    not str(port).isdigit() or not isinstance(settings, Mapping)
                    for port, settings in profile_outputs.items()
                ):
                    raise MigrationError(f"{filename}: invalid scene overrides")
                for settings in profile_outputs.values():
                    if any(key in _OVERRIDE_FIELDS and not isinstance(value, bool) for key, value in settings.items()):
                        raise MigrationError(f"{filename}: known override flags must be boolean")
            for key in ("steps", "actions", "items"):
                for step in record.get(key, []):
                    if not isinstance(step, Mapping):
                        raise MigrationError(f"{filename}: invalid step")
                    if "targets" in step and not isinstance(step["targets"], list):
                        raise MigrationError(f"{filename}: targets must be a list")
                    if "params" in step and not isinstance(step["params"], Mapping):
                        raise MigrationError(f"{filename}: step params must be an object")
                    if "delay_ms" in step:
                        _validate_integer(filename, "delay_ms", step["delay_ms"])
            for key in ("execution_history", "execution_log"):
                if any(not isinstance(item, Mapping) for item in record.get(key, [])):
                    raise MigrationError(f"{filename}: invalid {key} record")
                if key == "execution_history":
                    for item in record.get(key, []):
                        for field_name in ("steps_completed", "total_steps"):
                            if field_name in item:
                                _validate_integer(filename, field_name, item[field_name])
        return
    if filename == "device_settings.json":
        if not isinstance(payload, Mapping):
            raise MigrationError(f"{filename}: expected an object")
        for key in ("inputs", "outputs", "presets"):
            if key not in payload:
                continue
            values = payload[key]
            if isinstance(values, Mapping):
                values = values.values()
            elif not isinstance(values, list):
                raise MigrationError(f"{filename}: {key} must be a port map or legacy list")
            elif payload.get(SCHEMA_VERSION_KEY) == CURRENT_SCHEMA_VERSION:
                raise MigrationError(f"{filename}: current {key} must be a port map")
            else:
                ports = set()
                for item in values:
                    port = item.get("port", item.get("number")) if isinstance(item, Mapping) else None
                    _validate_integer(filename, "legacy port identity", port)
                    if not 1 <= int(port) <= 8 or int(port) in ports:
                        raise MigrationError(f"{filename}: invalid or duplicate port identity")
                    ports.add(int(port))
            if any(not isinstance(item, Mapping) for item in values):
                raise MigrationError(f"{filename}: invalid {key} record")
        for key in ("favorite_presets", "dashboard_presets"):
            if key in payload and not isinstance(payload[key], list):
                raise MigrationError(f"{filename}: {key} must be a list")
        return
    if filename in ("flic_buttons.json", "system_shortcuts.json"):
        if isinstance(payload, list):
            if any(not isinstance(item, Mapping) for item in payload):
                raise MigrationError(f"{filename}: invalid legacy record list")
            identities = set()
            for item in payload:
                identity = (
                    item.get("bdaddr") or item.get("address")
                    if filename == "flic_buttons.json"
                    else item.get("key") or item.get("id")
                )
                if not isinstance(identity, str) or not identity:
                    raise MigrationError(f"{filename}: legacy record has no identity")
                identity = _normalize_shortcut_key(identity) if filename == "system_shortcuts.json" else identity
                if identity in identities or (filename == "flic_buttons.json" and not is_button_key(identity)):
                    raise MigrationError(f"{filename}: invalid or duplicate legacy identity")
                identities.add(identity)
                if "order" in item:
                    _validate_integer(filename, "order", item["order"])
            return
        if not isinstance(payload, Mapping):
            raise MigrationError(f"{filename}: expected an object or legacy list")
        for key, value in payload.items():
            if filename == "flic_buttons.json" and is_button_key(key):
                if not isinstance(value, (Mapping, str)):
                    raise MigrationError(f"{filename}: invalid button record")
                if isinstance(value, str) and payload.get(SCHEMA_VERSION_KEY) == CURRENT_SCHEMA_VERSION:
                    raise MigrationError(f"{filename}: current button must be an object")
                if isinstance(value, Mapping) and value.get("bdaddr", key) != key:
                    raise MigrationError(f"{filename}: conflicting button address")
            elif filename == "system_shortcuts.json" and is_shortcut_key(key):
                if not isinstance(value, Mapping):
                    raise MigrationError(f"{filename}: invalid shortcut record")
                if "params" in value and not isinstance(value["params"], Mapping):
                    raise MigrationError(f"{filename}: invalid shortcut params")
                if "order" in value:
                    _validate_integer(filename, "shortcut order", value["order"])


def _validate_integer(filename: str, key: str, value: Any) -> None:
    try:
        if isinstance(value, bool) or not isinstance(value, (int, str)):
            raise ValueError
        int(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise MigrationError(f"{filename}: invalid {key}") from exc


# Storage ownership is explicit: absent known fields stay deleted. Only unknown
# fields of surviving identities are copied; removed records are never restored.
_PROFILE_FIELDS = set(
    "id name icon outputs cec_config macros power_on_macro power_off_macro pinned pin_order favorite dashboard_visible dashboard_order password_protected passcode_hash execution_log".split()
)
_SCENE_FIELDS = set(
    "id name icon steps overrides favorite dashboard_visible dashboard_order password_protected passcode_hash last_executed execution_history".split()
)
_MACRO_FIELDS = set(
    "id name icon description steps continue_on_error favorite dashboard_visible dashboard_order created_at updated_at".split()
)
_SHORTCUT_FIELDS = set(
    "key id name label icon enabled order category favorite dashboard_visible builtin params type".split()
)
_OUTPUT_FIELDS = set("input enabled scaler scaler_mode hdcp_mode hdr_mode audio_mute arc".split())
_CEC_FIELDS = set(
    "nav_targets playback_targets volume_targets power_on_targets power_off_targets auto_resolved".split()
)
_OVERRIDE_FIELDS = {"input", "enabled", "hdcp", "hdr", "scaler", "arc", "audio_mute"}


def _with_extensions(old: Any, new: Mapping, owned: set[str]) -> dict:
    result = {k: v for k, v in old.items() if k not in owned} if isinstance(old, Mapping) else {}
    result.update(new)
    return result


def _storage_record(old: Any, new: Mapping, owned: set[str]) -> dict:
    result = _with_extensions(old, new, owned)
    old = old if isinstance(old, Mapping) else {}
    if "overrides" in new:
        # Retain opaque nested metadata when the last known flag is cleared.
        # Absent known flags must never be restored from the old raw object.
        previous, updated = old.get("overrides", {}), new["overrides"]
        overrides = {}
        for profile_id in previous.keys() | updated.keys():
            outputs = {}
            before, after = previous.get(profile_id, {}), updated.get(profile_id, {})
            for port in before.keys() | after.keys():
                settings = _with_extensions(before.get(port, {}), after.get(port, {}), _OVERRIDE_FIELDS)
                if settings:
                    outputs[port] = settings
            if outputs:
                overrides[profile_id] = outputs
        result["overrides"] = overrides
    if "outputs" in new:
        result["outputs"] = {
            k: _with_extensions(old.get("outputs", {}).get(k, {}), v, _OUTPUT_FIELDS) for k, v in new["outputs"].items()
        }
    if "cec_config" in new:
        result["cec_config"] = _with_extensions(old.get("cec_config", {}), new["cec_config"], _CEC_FIELDS)
    if "steps" in new:
        # Match the unchanged command/reference identity, never the old index:
        # deleting/reordering a step must not move private fields to another step.
        remaining = list(old.get("steps", []))
        steps = []
        for step in new["steps"]:
            keys = ("command", "targets") if "command" in step else ("type", "id")
            previous = next((s for s in remaining if all(s.get(k) == step.get(k) for k in keys)), {})
            if previous:
                remaining.remove(previous)
            steps.append(_with_extensions(previous, step, set("command targets delay_ms type id params".split())))
        result["steps"] = steps
    if "execution_history" in new:
        previous = {r.get("timestamp"): r for r in old.get("execution_history", [])}
        fields = {"timestamp", "status", "steps_completed", "total_steps", "error"}
        result["execution_history"] = [
            _with_extensions(previous.get(r.get("timestamp"), {}), r, fields) for r in new["execution_history"]
        ]
    return result


def storage_payload(filename: str, old: Any, new: Mapping) -> dict:
    """Private lossless serialization, separate from public model projections."""
    filename = LEGACY_FILENAMES.get(filename, filename)
    catalogs = {
        "profiles.json": ("profiles", _PROFILE_FIELDS),
        "scenes.json": ("scenes", {"id", "name", "outputs", "cec_config"}),
        "scenes_v2.json": ("scenes", _SCENE_FIELDS),
        "cec_macros.json": ("macros", _MACRO_FIELDS),
        "dashboard_layout.json": ("cards", {"type", "id", "order"}),
    }
    old = old if isinstance(old, Mapping) else {}
    if filename in catalogs:
        collection, fields = catalogs[filename]
        result = _with_extensions(old, new, {collection, "schema_version"})
        identify = (lambda r: (r.get("type"), r.get("id"))) if collection == "cards" else (lambda r: r.get("id"))
        records = {identify(r): r for r in old.get(collection, [])}
        result[collection] = [_storage_record(records.get(identify(r), {}), r, fields) for r in new[collection]]
        return result
    if filename in ("system_shortcuts.json", "flic_buttons.json"):
        predicate = is_button_key if filename == "flic_buttons.json" else is_shortcut_key
        fields = {"bdaddr", "name", "serial"} if filename == "flic_buttons.json" else _SHORTCUT_FIELDS
        result = {k: v for k, v in old.items() if not predicate(k)}
        result.update(
            {
                k: _with_extensions(old.get(k, {}), v, fields) if predicate(k) and isinstance(v, Mapping) else v
                for k, v in new.items()
            }
        )
        return result
    return dict(new)


# ---------------------------------------------------------------------------
# Small, forgiving readers for legacy payloads
# ---------------------------------------------------------------------------


def _text(value: Any) -> str:
    """Return a stripped string, or ``""`` for anything that is not a string."""
    return value.strip() if isinstance(value, str) else ""


def _flag(item: Mapping[str, Any], key: str, default: bool) -> bool:
    value = item.get(key, None)
    return value if isinstance(value, bool) else default


def _index(item: Mapping[str, Any], key: str, default: int) -> int:
    value = item.get(key, None)
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


def _records(value: Any) -> list[dict[str, Any]]:
    """Return the mapping entries of ``value`` as dicts; anything else is dropped."""
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _as_envelope(payload: Any, collection_key: str) -> dict[str, Any]:
    """Accept both the ``{"scenes": [...]}`` and the bare-list legacy shape.

    The bare list is what v0 wrote for every collection file, so it is always
    wrapped rather than rejected. A payload that is neither a mapping nor a list
    is not recoverable.
    """
    if isinstance(payload, Mapping):
        return dict(payload)
    if isinstance(payload, list):
        return {collection_key: _records(payload)}
    raise MigrationError(f"expected an object or a list, got {type(payload).__name__}")


def _ensure_list_collection(payload: Any, collection_key: str) -> Any:
    """v1 -> v2: the file is an envelope whose ``collection_key`` holds records."""
    data = _as_envelope(payload, collection_key)
    data[collection_key] = _records(data.get(collection_key))
    return data


def _ensure_map_collection(payload: Any) -> Any:
    """v1 -> v2: the file is a flat ``{record key: record}`` map, as v0 wrote it."""
    if not isinstance(payload, Mapping):
        raise MigrationError(f"expected an object, got {type(payload).__name__}")
    return dict(payload)


# ---------------------------------------------------------------------------
# v0 -> v1 migrations: the shapes older releases actually wrote
# ---------------------------------------------------------------------------


def _migrate_flic_buttons_v1(payload: Any) -> Any:
    """``flic_buttons.json``: a bare list of buttons becomes a map keyed by bdaddr."""
    metadata = {}
    entries: list[tuple[dict[str, Any], str]] = []
    if isinstance(payload, list):
        entries = [(item, _text(item.get("bdaddr") or item.get("address"))) for item in _records(payload)]
    elif isinstance(payload, Mapping):
        for key, item in payload.items():
            key_text = _text(key)
            if key_text == SCHEMA_VERSION_KEY:
                continue
            if isinstance(item, Mapping) and (is_button_key(key_text) or item.get("bdaddr")):
                entries.append((dict(item), _text(item.get("bdaddr")) or key_text))
            elif isinstance(item, Mapping):
                metadata[key_text] = dict(item)
            else:
                # Only an address identifies the old shorthand button format.
                if is_button_key(key_text):
                    entries.append(({"name": item}, key_text))
                else:
                    metadata[key_text] = item
    else:
        raise MigrationError(f"expected an object or a list, got {type(payload).__name__}")

    buttons: dict[str, Any] = dict(metadata)
    for item, bdaddr in entries:
        if not bdaddr:
            continue
        record = dict(item)
        record["bdaddr"] = bdaddr
        record.setdefault("name", bdaddr)
        record.setdefault("serial", "")
        buttons[bdaddr] = record
    return buttons


def _migrate_scenes_v1(payload: Any) -> Any:
    """``scenes_v2.json``: bare list -> ``{"scenes": [...]}`` with sane per-scene defaults."""
    data = _as_envelope(payload, "scenes")
    scenes = []
    for scene in _records(data.get("scenes")):
        # Older files spelled the step list ``actions`` or ``items``; the reader
        # only ever looks at ``steps``, so the legacy key is left in place and
        # the normalised copy is added beside it.
        steps = scene.get("steps")
        if not isinstance(steps, list):
            for legacy_key in ("actions", "items"):
                candidate = scene.get(legacy_key)
                if isinstance(candidate, list):
                    steps = candidate
                    break
        scene["steps"] = _records(steps)
        if not isinstance(scene.get("overrides"), Mapping):
            scene["overrides"] = {}
        scene["favorite"] = _flag(scene, "favorite", False)
        scene["dashboard_visible"] = _flag(scene, "dashboard_visible", False)
        scene["dashboard_order"] = _index(scene, "dashboard_order", 0)
        scene["password_protected"] = _flag(scene, "password_protected", False)
        scene.setdefault("passcode_hash", "")
        scene.setdefault("execution_history", [])
        scenes.append(scene)
    data["scenes"] = scenes
    return data


def _migrate_profiles_v1(payload: Any) -> Any:
    """``profiles.json``: bare list -> ``{"profiles": [...]}`` with v2 field defaults."""
    data = _as_envelope(payload, "profiles")
    profiles = []
    for profile in _records(data.get("profiles")):
        outputs = profile.get("outputs")
        normalized: dict[str, Any] = {}
        if isinstance(outputs, Mapping):
            for port, setting in outputs.items():
                if isinstance(setting, Mapping):
                    normalized[str(port)] = dict(setting)
        profile["outputs"] = normalized
        profile.setdefault("icon", "\U0001f4fa")
        profile.setdefault("macros", [])
        profile["pinned"] = _flag(profile, "pinned", True)
        profile["pin_order"] = _index(profile, "pin_order", 0)
        profile["favorite"] = _flag(profile, "favorite", False)
        profile["dashboard_visible"] = _flag(profile, "dashboard_visible", False)
        profile["dashboard_order"] = _index(profile, "dashboard_order", 0)
        profile["password_protected"] = _flag(profile, "password_protected", False)
        profile.setdefault("passcode_hash", "")
        profile.setdefault("execution_log", [])
        profiles.append(profile)
    data["profiles"] = profiles
    data.setdefault("version", 2)
    return data


def _migrate_macros_v1(payload: Any) -> Any:
    """``cec_macros.json``: bare list -> ``{"macros": [...]}`` with per-step defaults."""
    data = _as_envelope(payload, "macros")
    macros = []
    for macro in _records(data.get("macros")):
        steps = []
        for step in _records(macro.get("steps")):
            step.setdefault("command", "")
            step.setdefault("targets", [])
            step["delay_ms"] = _index(step, "delay_ms", 0)
            steps.append(step)
        macro["steps"] = steps
        macro["continue_on_error"] = _flag(macro, "continue_on_error", False)
        macro["favorite"] = _flag(macro, "favorite", False)
        macro["dashboard_visible"] = _flag(macro, "dashboard_visible", False)
        macro["dashboard_order"] = _index(macro, "dashboard_order", 0)
        macros.append(macro)
    data["macros"] = macros
    data.setdefault("version", 1)
    return data


def _normalize_shortcut_key(key: str) -> str:
    """Map the shortcut keys older releases used onto the current ones."""
    if key.startswith("builtin."):
        key = key[len("builtin.") :]
    if key == "all_to_out_1":
        return "route_all_to_output"
    if key == "one_to_one":
        return "route_one_to_one"
    return key


def _migrate_shortcuts_v1(payload: Any) -> Any:
    """``shortcuts.json``: bare list -> the flat ``{key: prefs}`` map the reader uses."""
    metadata = {}
    if isinstance(payload, list):
        items = _records(payload)
    elif isinstance(payload, Mapping):
        items = []
        for key, value in payload.items():
            key_text = _text(key)
            if key_text == SCHEMA_VERSION_KEY:
                continue
            if not is_shortcut_key(key_text):
                metadata[key_text] = value
                continue
            if not isinstance(value, Mapping):
                raise MigrationError(f"invalid shortcut record: {key_text}")
            items.append(dict(value) if isinstance(value, Mapping) else {"label": value})
            items[-1].setdefault("key", key_text)
            items[-1].setdefault("id", key_text)
    else:
        raise MigrationError(f"expected an object or a list, got {type(payload).__name__}")

    shortcuts: dict[str, Any] = dict(metadata)
    for item in items:
        raw_key = _text(item.get("key")) or _text(item.get("id"))
        if not raw_key:
            continue
        key = _normalize_shortcut_key(raw_key)
        record = dict(item)
        record["key"] = key
        record["id"] = _text(item.get("id")) or key
        record["label"] = _text(item.get("label")) or _text(item.get("name")) or key
        record.setdefault("name", record["label"])
        record["enabled"] = _flag(record, "enabled", True)
        record["order"] = _index(record, "order", 0)
        record["favorite"] = _flag(record, "favorite", False)
        record["dashboard_visible"] = _flag(record, "dashboard_visible", False)
        if not isinstance(record.get("params"), Mapping):
            record["params"] = {}
        shortcuts[key] = record
    return shortcuts


def _migrate_dashboard_layout_v1(payload: Any) -> Any:
    """``dashboard_layout.json``: bare list -> ``{"cards": [...]}`` with int ordering."""
    data = _as_envelope(payload, "cards")
    cards = []
    for card in _records(data.get("cards")):
        card["type"] = _text(card.get("type"))
        card["id"] = _text(card.get("id"))
        card["order"] = _index(card, "order", 0)
        cards.append(card)
    data["cards"] = cards
    return data


def _port_key(item: Mapping[str, Any], fallback: str) -> str:
    """The port a legacy list entry describes, as a string key.

    Only an explicit ``port``/``number`` is trusted; falling back to the entry's
    position would silently renumber a list that simply forgot its keys.
    """
    raw = item.get("port", item.get("number"))
    if isinstance(raw, bool):
        return fallback
    if isinstance(raw, int):
        return str(raw)
    if isinstance(raw, float):
        return str(int(raw))
    text = _text(raw)
    return text or fallback


def _index_keyed(value: Any) -> dict[str, Any]:
    """Turn a legacy list of port settings into ``{"1": {...}, ...}``."""
    if isinstance(value, Mapping):
        return {str(key): dict(item) for key, item in value.items() if isinstance(item, Mapping)}
    settings: dict[str, Any] = {}
    for position, item in enumerate(_records(value), start=1):
        record = dict(item)
        # The port the entry described is now the key it is stored under.
        record.pop("port", None)
        record.pop("number", None)
        settings[_port_key(item, str(position))] = record
    return settings


def _migrate_device_settings_v1(payload: Any) -> Any:
    """``device_settings.json``: port lists become port-keyed maps; keys always present."""
    data = _as_envelope(payload, "inputs")
    for key in ("inputs", "outputs", "presets"):
        data[key] = _index_keyed(data.get(key))
    data.setdefault("version", 2)
    return data


def _migrate_device_settings_v2(payload: Any) -> Any:
    """v1 -> v2: the three port maps exist. Every other top-level key is left alone."""
    if not isinstance(payload, Mapping):
        raise MigrationError(f"expected an object, got {type(payload).__name__}")
    data = dict(payload)
    for key in ("inputs", "outputs", "presets"):
        if isinstance(data.get(key), list):
            data[key] = _index_keyed(data[key])
        elif not isinstance(data.get(key), Mapping):
            data[key] = {}
    return data


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DataFileSpec:
    """One managed file and the ordered migrations that bring it up to date."""

    filename: str
    description: str
    migrations: tuple[tuple[int, MigrationFunction], ...]
    collection_key: str | None = None
    map_collection: bool = False

    @property
    def versions(self) -> tuple[int, ...]:
        """The schema versions this file can be read as, oldest first."""
        return tuple(version for version, _ in self.migrations)


class MigrationRegistry:
    """Ordered migration chains, keyed by data file name."""

    def __init__(self, current_version: int = CURRENT_SCHEMA_VERSION) -> None:
        self._current_version = current_version
        self._specs: dict[str, DataFileSpec] = {}
        self._aliases: dict[str, str] = {}

    # -- registration -----------------------------------------------------

    def register(
        self,
        filename: str,
        *,
        description: str,
        migrations: Iterable[tuple[int, MigrationFunction]],
        collection_key: str | None = None,
        map_collection: bool = False,
        aliases: Iterable[str] = (),
    ) -> DataFileSpec:
        """Register ``filename``; ``migrations`` are ``(to_version, function)`` pairs."""
        chain = tuple(sorted(migrations, key=lambda item: item[0]))
        seen: set[int] = set()
        for version, _ in chain:
            if version in seen:
                raise ValueError(f"{filename}: two migrations target version {version}")
            seen.add(version)
            if not 1 <= version <= self._current_version:
                raise ValueError(f"{filename}: migration version {version} is outside 1..{self._current_version}")
        for version in range(1, self._current_version + 1):
            if version not in seen:
                raise ValueError(f"{filename}: no migration to version {version}")
        spec = DataFileSpec(
            filename=filename,
            description=description,
            migrations=chain,
            collection_key=collection_key,
            map_collection=map_collection,
        )
        self._specs[filename] = spec
        for alias in aliases:
            self._aliases[alias] = filename
        return spec

    def alias(self, legacy_filename: str, filename: str) -> None:
        """Map a retired file name onto the canonical one."""
        if filename not in self._specs:
            raise KeyError(f"{filename} is not registered")
        self._aliases[legacy_filename] = filename

    # -- lookups ----------------------------------------------------------

    @property
    def current_version(self) -> int:
        return self._current_version

    def filenames(self) -> tuple[str, ...]:
        return tuple(self._specs)

    def aliases(self) -> dict[str, str]:
        return dict(self._aliases)

    def has(self, filename: str) -> bool:
        return self.resolve(filename) in self._specs

    def resolve(self, filename: str) -> str:
        """Return the canonical name for ``filename`` (itself, unless aliased)."""
        return self._aliases.get(filename, filename)

    def spec(self, filename: str) -> DataFileSpec:
        canonical = self.resolve(filename)
        try:
            return self._specs[canonical]
        except KeyError:
            raise KeyError(f"{filename} is not a managed data file") from None

    def known_filenames(self) -> tuple[str, ...]:
        """Canonical names first, then the retired names, in registration order."""
        return self.filenames() + tuple(alias for alias in self._aliases if alias not in self._specs)

    # -- version handling -------------------------------------------------

    @staticmethod
    def detect_version(payload: Any) -> int:
        """The schema version of a payload; ``0`` when it carries none.

        Only :data:`SCHEMA_VERSION_KEY` is authoritative. The unrelated ``version``
        key some files have carried since v0 (a *file format* marker) is left
        alone and is not read as a schema version.
        """
        if not isinstance(payload, Mapping):
            return 0
        raw = payload.get(SCHEMA_VERSION_KEY)
        if isinstance(raw, bool) or not isinstance(raw, int):
            return 0
        return raw if raw > 0 else 0

    def migration_path(self, filename: str, from_version: int) -> tuple[tuple[int, MigrationFunction], ...]:
        """The migrations to run, oldest first."""
        spec = self.spec(filename)
        return tuple(item for item in spec.migrations if item[0] > from_version)

    def apply(self, filename: str, payload: Any) -> tuple[Any, list[int]]:
        """Run the chain in memory and stamp the current version.

        :returns: ``(migrated payload, versions applied)``.
        :raises SchemaVersionError: the file is newer than this release.
        :raises MigrationError: the payload has a shape no migration accepts.
        """
        spec = self.spec(filename)
        validate_payload(filename, payload)
        version = self.detect_version(payload)
        if version > self._current_version:
            raise SchemaVersionError(
                f"{filename} was written by a newer release (schema_version {version} > {self._current_version})"
            )

        migrated = payload
        applied: list[int] = []
        for target, function in spec.migrations:
            if target <= version:
                continue
            migrated = function(migrated)
            applied.append(target)

        if not isinstance(migrated, Mapping):
            raise MigrationError(f"{filename}: migration produced {type(migrated).__name__}, not an object")
        stamped = {SCHEMA_VERSION_KEY: self._current_version}
        for key, value in migrated.items():
            if key != SCHEMA_VERSION_KEY:
                stamped[str(key)] = value
        return stamped, applied


def build_default_registry() -> MigrationRegistry:
    """The registry for every file in :data:`MANAGED_FILENAMES`."""
    registry = MigrationRegistry()
    registry.register(
        "scenes_v2.json",
        description="Unified scenes (Phase 8)",
        collection_key="scenes",
        migrations=[
            (1, _migrate_scenes_v1),
            (2, lambda payload: _ensure_list_collection(payload, "scenes")),
        ],
    )
    registry.register(
        "profiles.json",
        description="Profiles (scene + macro assignments)",
        collection_key="profiles",
        migrations=[
            (1, _migrate_profiles_v1),
            (2, lambda payload: _ensure_list_collection(payload, "profiles")),
        ],
    )
    registry.register(
        "cec_macros.json",
        description="CEC macros",
        collection_key="macros",
        migrations=[
            (1, _migrate_macros_v1),
            (2, lambda payload: _ensure_list_collection(payload, "macros")),
        ],
    )
    registry.register(
        "system_shortcuts.json",
        description="System shortcut preferences",
        map_collection=True,
        migrations=[
            (1, _migrate_shortcuts_v1),
            (2, _ensure_map_collection),
        ],
        aliases=LEGACY_FILENAMES,
    )
    registry.register(
        "dashboard_layout.json",
        description="Dashboard card order",
        collection_key="cards",
        migrations=[
            (1, _migrate_dashboard_layout_v1),
            (2, lambda payload: _ensure_list_collection(payload, "cards")),
        ],
    )
    registry.register(
        "device_settings.json",
        description="Port names, icons and preset names",
        migrations=[
            (1, _migrate_device_settings_v1),
            (2, _migrate_device_settings_v2),
        ],
    )
    registry.register(
        "flic_buttons.json",
        description="Registered Flic buttons, keyed by Bluetooth address",
        map_collection=True,
        migrations=[
            (1, _migrate_flic_buttons_v1),
            (2, _migrate_flic_buttons_v1),
        ],
    )
    return registry


#: The registry the module-level helpers use.
DEFAULT_REGISTRY = build_default_registry()

# Absolute paths prevent one failed volume from poisoning a different volume.
_WRITE_FAILURES: dict[Path, str] = {}


def block_path(path: Path | str, reason: str) -> None:
    _WRITE_FAILURES[Path(path).resolve()] = reason


def assert_writable(path: Path | str) -> None:
    path = Path(path).resolve()
    if path in _WRITE_FAILURES:
        raise MigrationError(f"{path}: {_WRITE_FAILURES[path]}")
    if path.exists() and (DEFAULT_REGISTRY.has(path.name) or path.name == "scenes.json"):
        try:
            validate_payload(path.name, atomic_read_json(path))
        except (ValueError, OSError) as exc:
            raise MigrationError(f"{path}: refusing unsafe write: {exc}") from exc


# ---------------------------------------------------------------------------
# Migration on disk
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MigrationResult:
    """What happened to one file. ``status`` is one of:

    ``migrated``     the file was below the current version and is now at it
    ``current``      the file already carried the current version
    ``missing``      there is no such file (nothing to do, not an error)
    ``unsupported``  the file was written by a newer release; left untouched
    ``unreadable``   the file is not valid JSON; left untouched
    ``preserved``    an import source was validated and kept byte-for-byte
    """

    path: Path
    status: str
    from_version: int = 0
    to_version: int = CURRENT_SCHEMA_VERSION
    applied: tuple[int, ...] = ()
    backup: Path | None = None

    @property
    def migrated(self) -> bool:
        return self.status == "migrated"


def backup_path_for(path: Path | str, from_version: int) -> Path:
    """Where the pre-migration copy of ``path`` goes (``<name>.v<old>.bak``)."""
    path = Path(path)
    return path.with_name(f"{path.name}.v{from_version}.bak")


def write_backup(path: Path, from_version: int) -> Path | None:
    """Copy ``path`` next to itself before it is rewritten.

    An existing backup is never overwritten: the oldest one holds the bytes the
    operator actually started from, which is the only copy worth keeping.

    :returns: the backup path, or ``None`` when it could not be written.
    """
    target = backup_path_for(path, from_version)
    if target.exists():
        try:
            if target.read_bytes() == path.read_bytes():
                return target
        except OSError:
            pass
        _LOG.error("Backup %s already contains different bytes; refusing to overwrite it", target)
        return None
    try:
        shutil.copy2(path, target)
    except OSError as exc:
        _LOG.warning("Could not back up %s before migrating it: %s", path, exc)
        return None
    _LOG.info("Backed up %s to %s before migrating it", path.name, target.name)
    return target


def migrate_data_file(
    path: Path | str,
    *,
    registry: MigrationRegistry | None = None,
    backup: bool = True,
) -> MigrationResult:
    """Bring one data file up to :data:`CURRENT_SCHEMA_VERSION`, in place.

    Order of operations, and the reason for it: the pre-migration copy is taken
    first, the migration functions only ever see the in-memory payload, and the
    result is written once, atomically. A crash at any point leaves either the
    untouched original or a file whose backup already exists.
    """
    registry = registry or DEFAULT_REGISTRY
    path = Path(path)
    spec = registry.spec(path.name)

    if not path.exists():
        return MigrationResult(path=path, status="missing")

    try:
        payload = atomic_read_json(path)
    except (ValueError, OSError) as exc:
        _LOG.warning("Leaving %s untouched: it could not be read (%s)", path.name, exc)
        return MigrationResult(path=path, status="unreadable")

    version = registry.detect_version(payload)
    if version > registry.current_version:
        _LOG.warning(
            "Leaving %s untouched: schema_version %d is newer than the supported %d",
            path.name,
            version,
            registry.current_version,
        )
        return MigrationResult(
            path=path,
            status="unsupported",
            from_version=version,
            to_version=registry.current_version,
        )
    if version == registry.current_version:
        validate_payload(path.name, payload)
        return MigrationResult(path=path, status="current", from_version=version, to_version=version)

    try:
        migrated, applied = registry.apply(path.name, payload)
    except MigrationError as exc:
        _LOG.warning("Leaving %s untouched: %s", path.name, exc)
        return MigrationResult(path=path, status="unreadable", from_version=version)

    backup_file = write_backup(path, version) if backup else None
    if backup and backup_file is None:
        block_path(path, "backup failed before migration")
        raise MigrationError(f"{path}: backup failed before migration")
    try:
        atomic_write_json(path, migrated)
    except (OSError, TimeoutError) as exc:
        block_path(path, "atomic migration replacement failed")
        _LOG.error("Could not write the migrated %s: %s (the backup is intact)", path.name, exc)
        raise MigrationError(f"{path}: atomic migration replacement failed") from exc

    _LOG.info(
        "Migrated %s from schema_version %d to %d%s",
        spec.filename,
        version,
        registry.current_version,
        f" (backup {backup_file.name})" if backup_file else "",
    )
    return MigrationResult(
        path=path,
        status="migrated",
        from_version=version,
        to_version=registry.current_version,
        applied=tuple(applied),
        backup=backup_file,
    )


def migrate_all_data_files(
    directory: Path | str,
    *,
    registry: MigrationRegistry | None = None,
    backup: bool = True,
    filenames: Iterable[str] | None = None,
) -> dict[str, MigrationResult]:
    """Migrate every managed file that exists in ``directory``.

    Retired file names are included, so an installation still carrying
    ``system_shortcuts.json`` is upgraded in place. A directory that does not
    exist yields an empty result rather than an error: the hub creates its data
    directory long before anything is written to it.
    """
    registry = registry or DEFAULT_REGISTRY
    directory = Path(directory)
    wanted = tuple(filenames) if filenames is not None else registry.known_filenames()

    results: dict[str, MigrationResult] = {}
    if not directory.is_dir():
        return results
    for name in wanted:
        if name in results or not registry.has(name):
            continue
        result = migrate_data_file(directory / name, registry=registry, backup=backup)
        if result.status != "missing":
            results[name] = result
    return results


def load_versioned_json(
    path: Path | str,
    *,
    default: Any = None,
    registry: MigrationRegistry | None = None,
    migrate: bool = True,
    backup: bool = True,
) -> Any:
    """Read a data file, migrating it on the way through when it is behind.

    :param default: returned only when the file does not exist.
    :param migrate: set False to read the file exactly as it is on disk.
    """
    registry = registry or DEFAULT_REGISTRY
    path = Path(path)
    assert_writable(path)
    if migrate and registry is DEFAULT_REGISTRY:
        # Generic readers share the constructor import boundary: checking only
        # the target's existence can turn an alias into a default-seeding path.
        from .startup import prepare_profile_file, prepare_scene_files, prepare_shortcut_files

        if path.name == "profiles.json":
            prepare_profile_file(path.parent)
        elif path.name == "scenes_v2.json":
            prepare_scene_files(path.parent)
        elif path.name == "system_shortcuts.json":
            prepare_shortcut_files(path.parent)
    if not path.exists():
        return default

    try:
        payload = atomic_read_json(path)
    except (ValueError, OSError) as exc:
        block_path(path, "unreadable input")
        raise MigrationError(f"{path}: could not read stored data") from exc

    if not migrate or not registry.has(path.name):
        if registry.has(path.name) or path.name == "scenes.json":
            validate_payload(path.name, payload)
        return payload

    result = migrate_data_file(path, registry=registry, backup=backup)
    if result.status in ("unreadable", "unsupported"):
        block_path(path, result.status)
        raise MigrationError(f"{path}: {result.status} stored data")
    if not result.migrated:
        return payload
    # Re-read: the caller wants the current shape, which may carry fields the
    # pre-migration payload did not have.
    return atomic_read_json(path, default=payload)


def save_versioned_json(
    path: Path | str,
    payload: Any,
    *,
    registry: MigrationRegistry | None = None,
    indent: int = 2,
) -> bool:
    """Write a data file with the current ``schema_version`` stamped on it.

    Validate the existing file and import boundary before merging private
    extensions into surviving records. Missing known fields and records stay
    deleted. Public projections remain independent of this disk encoder.

    :returns: False when ``payload`` is not a JSON object (nothing is written).
    """
    registry = registry or DEFAULT_REGISTRY
    path = Path(path)
    assert_writable(path)
    if not isinstance(payload, Mapping):
        _LOG.warning("Refusing to write %s: expected an object, got %s", path.name, type(payload).__name__)
        return False

    if registry.has(path.name) or path.name == "scenes.json":
        validate_payload(path.name, payload)
    old = load_versioned_json(path, registry=registry, default={})
    if registry.has(path.name) or path.name == "scenes.json":
        payload = storage_payload(path.name, old, payload)
    stamped: dict[str, Any] = {SCHEMA_VERSION_KEY: registry.current_version}
    for key, value in payload.items():
        if key != SCHEMA_VERSION_KEY:
            stamped[str(key)] = value

    atomic_write_json(path, stamped, indent=indent)
    return True


__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "DEFAULT_REGISTRY",
    "LEGACY_FILENAMES",
    "MANAGED_FILENAMES",
    "SCHEMA_VERSION_KEY",
    "DataFileSpec",
    "MigrationError",
    "MigrationRegistry",
    "MigrationResult",
    "SchemaVersionError",
    "backup_path_for",
    "build_default_registry",
    "load_versioned_json",
    "migrate_all_data_files",
    "migrate_data_file",
    "save_versioned_json",
    "write_backup",
]
