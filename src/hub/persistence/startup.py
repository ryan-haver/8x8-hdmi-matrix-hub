"""Prepare resolved storage before readers, default seeding or PIN rehashing.

Standalone readers use the same file preparation helpers. Failure state is keyed
by absolute path, never by basename or the last volume prepared in this process.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from _file_io import atomic_read_json, atomic_write_json

from . import migrations as migration
from .migrations import (
    DEFAULT_REGISTRY,
    SCHEMA_VERSION_KEY,
    MigrationError,
    MigrationResult,
)

SCENES_V2_FILENAME = "scenes_v2.json"
SCENES_LEGACY_FILENAME = "scenes.json"
SHORTCUTS_SHIPPED_FILENAME = "system_shortcuts.json"
SHORTCUTS_ALIAS_FILENAME = "shortcuts.json"
_CONFIG_FILENAMES = ("profiles.json", "cec_macros.json")
_DATA_FILENAMES = (
    "scenes_v2.json",
    "system_shortcuts.json",
    "dashboard_layout.json",
    "device_settings.json",
    "flic_buttons.json",
)
_IMPORT_KEY = "_runtime_imports"


@dataclass(frozen=True)
class PersistencePaths:
    config_dir: Path
    data_dir: Path
    expected_config_files: dict[str, Path] = field(default_factory=dict)
    expected_data_files: dict[str, Path] = field(default_factory=dict)

    def canonical(self, filename: str) -> Path:
        return {**self.expected_config_files, **self.expected_data_files}[filename]


@dataclass(frozen=True)
class PreparedPersistence:
    paths: PersistencePaths
    results: tuple[MigrationResult, ...]
    blocked_writes: dict[str, str] = field(default_factory=dict)
    raised_during: tuple[str, ...] = ()

    def is_write_blocked(self, filename: str) -> bool:
        return is_write_blocked(self.paths.canonical(filename))

    def block_reason(self, filename: str) -> str | None:
        return block_reason(self.paths.canonical(filename))


_PREPARED: PreparedPersistence | None = None


def _read(path: Path) -> Any:
    try:
        return atomic_read_json(path)
    except (ValueError, OSError) as exc:
        raise MigrationError(f"{path}: unreadable stored data") from exc


def scene_shape(payload: Any) -> str:
    """Distinguish real legacy output-state scenes from unified step scenes."""
    if isinstance(payload, dict) and SCHEMA_VERSION_KEY in payload:
        version = payload[SCHEMA_VERSION_KEY]
        if (
            isinstance(version, bool)
            or not isinstance(version, int)
            or not 0 <= version <= DEFAULT_REGISTRY.current_version
        ):
            raise MigrationError("scenes.json: unsupported schema_version")
    records = payload.get("scenes") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise MigrationError("scenes.json: ambiguous scene container")
    if not records:
        return "empty"
    shapes = set()
    for record in records:
        if not isinstance(record, dict):
            raise MigrationError("scenes.json: invalid scene record")
        unified = any(k in record for k in ("steps", "actions", "items"))
        legacy = "outputs" in record
        if unified == legacy:
            raise MigrationError("scenes.json: ambiguous scene shape")
        shapes.add("unified" if unified else "legacy")
    if len(shapes) != 1:
        raise MigrationError("scenes.json: mixed scene shapes")
    shape = shapes.pop()
    migration.validate_payload(
        "scenes_v2.json" if shape == "unified" else "profiles.json",
        {"scenes" if shape == "unified" else "profiles": records},
    )
    return shape


def _normalise(filename: str, payload: Any) -> dict:
    migration.validate_payload(filename, payload)
    return DEFAULT_REGISTRY.apply(filename, payload)[0]


def _contains(target: Any, source: Any) -> bool:
    if isinstance(source, dict):
        return isinstance(target, dict) and all(
            k in target and _contains(target[k], v)
            for k, v in source.items()
            if k not in (SCHEMA_VERSION_KEY, _IMPORT_KEY)
        )
    if isinstance(source, list):
        if not isinstance(target, list):
            return False
        if all(isinstance(r, dict) and "id" in r for r in source):
            by_id = {r.get("id"): r for r in target if isinstance(r, dict)}
            return all(r["id"] in by_id and _contains(by_id[r["id"]], r) for r in source)
        return target == source
    return target == source


def _import_catalog(source: Path, target: Path, payload: Any) -> None:
    """Preserve source bytes and record provenance for edits and PIN rehashes."""
    normalized = _normalise(target.name, payload)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists():
        current = _normalise(target.name, _read(target))
        imports = current.get(_IMPORT_KEY, {})
        if not isinstance(imports, dict):
            raise MigrationError(f"{target}: invalid import provenance metadata")
        if imports.get(source.name) == digest:
            return
        # Shortcut dual files must agree; scenes may contain additional canonical records.
        equivalent = _contains(current, normalized)
        if target.name == SHORTCUTS_SHIPPED_FILENAME:
            equivalent = equivalent and _contains(normalized, current)
        if not equivalent:
            raise MigrationError(f"conflicting {source} and {target}: source content is not represented")
        # Equivalent independent files need provenance too, so subsequent edits
        # and PIN rehashes do not turn an accepted import into a restart conflict.
        normalized = current
        if migration.write_backup(target, DEFAULT_REGISTRY.detect_version(_read(target))) is None:
            raise MigrationError(f"{target}: backup failed before recording import")
    version = DEFAULT_REGISTRY.detect_version(payload)
    if migration.write_backup(source, version) is None:
        raise MigrationError(f"{source}: backup failed before import")
    imports = normalized.setdefault(_IMPORT_KEY, {})
    if not isinstance(imports, dict):
        raise MigrationError(f"{target}: invalid import provenance metadata")
    imports[source.name] = digest
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(target, normalized)
    except (OSError, TimeoutError) as exc:
        raise MigrationError(f"{target}: atomic import failed") from exc


def prepare_scene_files(data_dir: Path) -> None:
    target = Path(data_dir) / SCENES_V2_FILENAME
    legacy = Path(data_dir) / SCENES_LEGACY_FILENAME
    try:
        migration.assert_writable(target)
        if target.exists():
            _normalise(target.name, _read(target))
        if legacy.exists():
            payload = _read(legacy)
            shape = scene_shape(payload)
            if shape in ("unified", "empty"):
                _import_catalog(legacy, target, payload if isinstance(payload, dict) else {"scenes": payload})
            elif target.exists():
                raise MigrationError(f"conflicting {legacy} and {target}: incompatible record shapes")
    except (MigrationError, OSError) as exc:
        migration.block_path(target, str(exc))
        migration.block_path(legacy, str(exc))
        raise MigrationError(str(exc)) from exc


def prepare_shortcut_files(data_dir: Path) -> None:
    target = Path(data_dir) / SHORTCUTS_SHIPPED_FILENAME
    alias = Path(data_dir) / SHORTCUTS_ALIAS_FILENAME
    try:
        migration.assert_writable(target)
        if target.exists():
            _normalise(target.name, _read(target))
        if alias.exists():
            _import_catalog(alias, target, _read(alias))
    except (MigrationError, OSError) as exc:
        migration.block_path(target, str(exc))
        migration.block_path(alias, str(exc))
        raise MigrationError(str(exc)) from exc


def prepare_profile_file(config_dir: Path) -> None:
    target = Path(config_dir) / "profiles.json"
    source = Path(config_dir) / "scenes.json"
    migration.assert_writable(target)
    if target.exists() or not source.exists():
        return
    try:
        payload = _read(source)
        shape = scene_shape(payload)
        if shape == "legacy":
            envelope = dict(payload) if isinstance(payload, dict) else {"scenes": payload}
            envelope["profiles"] = envelope.pop("scenes")
            _import_catalog(source, target, envelope)
    except (MigrationError, OSError) as exc:
        migration.block_path(target, str(exc))
        raise MigrationError(str(exc)) from exc


def prepare_runtime_storage(*, config_dir: Path, data_dir: Path) -> PreparedPersistence:
    global _PREPARED
    from persistence import migrate_legacy_file

    config_dir, data_dir = Path(config_dir).resolve(), Path(data_dir).resolve()
    paths = PersistencePaths(
        config_dir, data_dir, {n: config_dir / n for n in _CONFIG_FILENAMES}, {n: data_dir / n for n in _DATA_FILENAMES}
    )
    targets = list(dict.fromkeys([*paths.expected_config_files.values(), *paths.expected_data_files.values()]))
    extras = list(dict.fromkeys([config_dir / "scenes.json", data_dir / "scenes.json", data_dir / "shortcuts.json"]))
    results = []
    # Explicit preparation is the recovery boundary; unrelated paths retain
    # their failures. Validation below re-blocks any still-unsafe file.
    for path in targets + extras:
        migration._WRITE_FAILURES.pop(path, None)
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        for path in targets + extras:
            migrate_legacy_file(path, path.name)
        # Preflight the complete inventory before any conversion or default writer.
        for path in targets + extras:
            if path.exists():
                if path.name == "scenes.json":
                    scene_shape(_read(path))
                else:
                    _normalise(path.name, _read(path))
        prepare_profile_file(config_dir)
        prepare_scene_files(data_dir)
        prepare_shortcut_files(data_dir)
        for path in targets:
            result = migration.migrate_data_file(path)
            results.append(result)
            if result.status in ("unreadable", "unsupported"):
                raise MigrationError(f"{path}: {result.status} stored data")
        for path in extras:
            if path.exists() and path not in targets:
                version = DEFAULT_REGISTRY.detect_version(_read(path))
                results.append(MigrationResult(path=path, status="preserved", from_version=version, to_version=version))
    except (MigrationError, OSError, TimeoutError) as exc:
        # Fail closed for this resolved installation; no manager may seed a
        # missing target after a failed alias/import operation.
        for path in targets + extras:
            migration.block_path(path, str(exc))
        _PREPARED = PreparedPersistence(paths, tuple(results), {str(p): str(exc) for p in targets + extras})
        raise MigrationError(str(exc)) from exc
    _PREPARED = PreparedPersistence(paths, tuple(results))
    return _PREPARED


def prepared_persistence() -> PreparedPersistence | None:
    return _PREPARED


def _actual_path(path: Path | str) -> Path:
    path = Path(path)
    if path.parent == Path(".") and _PREPARED:
        try:
            return _PREPARED.paths.canonical(path.name)
        except KeyError:
            pass
    return path.resolve()


def is_write_blocked(path: Path | str) -> bool:
    try:
        migration.assert_writable(_actual_path(path))
        return False
    except MigrationError:
        return True


def block_reason(path: Path | str) -> str | None:
    try:
        migration.assert_writable(_actual_path(path))
        return None
    except MigrationError as exc:
        return str(exc)


def reset_preparation() -> None:
    global _PREPARED
    _PREPARED = None
    migration._WRITE_FAILURES.clear()
