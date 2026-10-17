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
:data:`LEGACY_FILENAMES` maps a retired file name to the canonical one, so an
installation that still has ``system_shortcuts.json`` (the name the runtime has
always used) is migrated in place instead of being silently ignored.
"""

from __future__ import annotations

import logging
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
LEGACY_FILENAMES: dict[str, str] = {
    "system_shortcuts.json": "shortcuts.json",
}

#: The persisted JSON files the hub owns and migrates.
MANAGED_FILENAMES: tuple[str, ...] = (
    "scenes_v2.json",
    "profiles.json",
    "cec_macros.json",
    "shortcuts.json",
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
    return {
        str(key): dict(item)
        for key, item in payload.items()
        if str(key) != SCHEMA_VERSION_KEY and isinstance(item, Mapping)
    }


# ---------------------------------------------------------------------------
# v0 -> v1 migrations: the shapes older releases actually wrote
# ---------------------------------------------------------------------------


def _migrate_flic_buttons_v1(payload: Any) -> Any:
    """``flic_buttons.json``: a bare list of buttons becomes a map keyed by bdaddr."""
    entries: list[tuple[dict[str, Any], str]] = []
    if isinstance(payload, list):
        entries = [(item, _text(item.get("bdaddr") or item.get("address"))) for item in _records(payload)]
    elif isinstance(payload, Mapping):
        for key, item in payload.items():
            key_text = _text(key)
            if key_text == SCHEMA_VERSION_KEY:
                continue
            if isinstance(item, Mapping):
                entries.append((dict(item), _text(item.get("bdaddr")) or key_text))
            else:
                # ``{"80:e4:...": "Couch Button"}``: the value was the button name.
                entries.append(({"name": item}, key_text))
    else:
        raise MigrationError(f"expected an object or a list, got {type(payload).__name__}")

    buttons: dict[str, Any] = {}
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
    if isinstance(payload, list):
        items = _records(payload)
    elif isinstance(payload, Mapping):
        items = []
        for key, value in payload.items():
            key_text = _text(key)
            if key_text == SCHEMA_VERSION_KEY:
                continue
            items.append(dict(value) if isinstance(value, Mapping) else {"label": value})
            items[-1].setdefault("key", key_text)
            items[-1].setdefault("id", key_text)
    else:
        raise MigrationError(f"expected an object or a list, got {type(payload).__name__}")

    shortcuts: dict[str, Any] = {}
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
        if not isinstance(data.get(key), Mapping):
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
        "shortcuts.json",
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
            (2, _ensure_map_collection),
        ],
    )
    return registry


#: The registry the module-level helpers use.
DEFAULT_REGISTRY = build_default_registry()


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
        _LOG.info("Keeping the existing migration backup %s", target)
        return target
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
        return MigrationResult(path=path, status="current", from_version=version, to_version=version)

    try:
        migrated, applied = registry.apply(path.name, payload)
    except MigrationError as exc:
        _LOG.warning("Leaving %s untouched: %s", path.name, exc)
        return MigrationResult(path=path, status="unreadable", from_version=version)

    backup_file = write_backup(path, version) if backup else None
    try:
        atomic_write_json(path, migrated)
    except (OSError, TimeoutError) as exc:
        _LOG.error("Could not write the migrated %s: %s (the backup is intact)", path.name, exc)
        return MigrationResult(
            path=path,
            status="unreadable",
            from_version=version,
            applied=tuple(applied),
            backup=backup_file,
        )

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
            results[registry.resolve(name)] = result
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

    :param default: returned when the file does not exist or cannot be parsed.
    :param migrate: set False to read the file exactly as it is on disk.
    """
    registry = registry or DEFAULT_REGISTRY
    path = Path(path)
    if not path.exists():
        return default

    try:
        payload = atomic_read_json(path)
    except (ValueError, OSError) as exc:
        _LOG.warning("Could not read %s: %s", path.name, exc)
        return default

    if not migrate or not registry.has(path.name):
        return payload

    result = migrate_data_file(path, registry=registry, backup=backup)
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

    Unlike :func:`load_versioned_json` this never migrates: the caller owns the
    payload, so the file is written as given (plus the version) and atomically.

    :returns: False when ``payload`` is not a JSON object (nothing is written).
    """
    registry = registry or DEFAULT_REGISTRY
    path = Path(path)
    if not isinstance(payload, Mapping):
        _LOG.warning("Refusing to write %s: expected an object, got %s", path.name, type(payload).__name__)
        return False

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
