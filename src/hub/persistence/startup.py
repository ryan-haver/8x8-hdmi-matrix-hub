"""Runtime storage barrier: the single bottleneck before managers consume data.

The runtime composition root (:mod:`hub.runtime.composition`) is supposed to
hand every manager an already-prepared data directory. This module is that
handshake:

* resolve ``config_dir`` and ``data_dir``,
* detect and resolve the on-disk filename collisions the legacy releases left
  behind (legacy ``scenes.json`` vs. unified ``scenes_v2.json``, shipped
  ``system_shortcuts.json`` vs. registry alias ``shortcuts.json``),
* run the pre-manager migrations, refusing to swallow backup or replacement
  failures, and
* publish a :class:`PreparedPersistence` value whose ``blocked_writes`` map
  tells the existing managers which files they must not write to.

The barrier raises :class:`MigrationError` when an unsafe state is found that
a manager save would silently paper over (backup failure during migration,
ambiguous filename collisions, a future-schema file in the data directory).
The existing managers then read :func:`is_write_blocked` and refuse their
own writes so a crashed preparation never causes a later save to overwrite
user data.

Construction arguments of the legacy managers are untouched: every existing
test still constructs ``SceneManager(data_dir=...)`` the same way; the new
behaviour only kicks in once :func:`prepare_runtime_storage` has been
called.

See :doc:`docs/planning/RUNTIME_CONTRACT.md` §4 for the contract this
module fulfils.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from _file_io import atomic_read_json, atomic_write_json

from .migrations import (
    DEFAULT_REGISTRY,
    LEGACY_FILENAMES,
    MANAGED_FILENAMES,
    SCHEMA_VERSION_KEY,
    MigrationError,
    MigrationRegistry,
    MigrationResult,
    backup_path_for,
)

_LOG = logging.getLogger("hub.persistence.startup")

#: Manager-owned config filenames. The barrier only consumes these and ignores
#: every other file in the data/config dir (``themes.json``, ``ui_preferences.json``,
#: ``security.json``, …) — they continue to use their per-module helpers.
_CONFIG_FILENAMES = (
    "profiles.json",
    "cec_macros.json",
    "scenes.json",  # config.SceneManager writes here today
)

#: Manager-owned data filenames.
_DATA_FILENAMES = (
    "scenes_v2.json",         # Phase 8 unified scene manager target
    "system_shortcuts.json",  # shipped runtime filename for shortcuts
    "dashboard_layout.json",
    "device_settings.json",
)

#: Filenames that resolve the same catalog through different names. The
#: barrier treats each one as a potential alias of the canonical target.
#: Filename constants are exported so callers can reason about which file is
#: the canonical one without re-typing strings.
SCENES_V2_FILENAME = "scenes_v2.json"
SCENES_LEGACY_FILENAME = "scenes.json"
SHORTCUTS_SHIPPED_FILENAME = "system_shortcuts.json"
SHORTCUTS_ALIAS_FILENAME = "shortcuts.json"


@dataclass(frozen=True)
class PersistencePaths:
    """Resolved on-disk paths for the runtime's stored catalogs.

    ``config_dir`` and ``data_dir`` are exactly what was passed to
    :func:`prepare_runtime_storage` (already resolved to absolute paths).
    ``expected_config_files`` and ``expected_data_files`` map the
    manager-owned filenames to their canonical on-disk locations so the
    composition root never asks the persistence module again.
    """

    config_dir: Path
    data_dir: Path
    expected_config_files: dict[str, Path] = field(default_factory=dict)
    expected_data_files: dict[str, Path] = field(default_factory=dict)

    def canonical(self, filename: str) -> Path:
        """Return the on-disk path for ``filename`` (raises :class:`KeyError` if unknown)."""
        if filename in self.expected_data_files:
            return self.expected_data_files[filename]
        if filename in self.expected_config_files:
            return self.expected_config_files[filename]
        raise KeyError(f"{filename} is not a known persistence target")


@dataclass(frozen=True)
class PreparedPersistence:
    """What :func:`prepare_runtime_storage` returned and what managers consult.

    ``results`` lists the result of every migration attempt by actual path
    (no alias key collides). ``blocked_writes`` is the new gate: each
    ``filename -> reason`` entry tells the legacy managers the runtime
    detected an unsafe state and any save attempt would be refused.
    ``raised_during`` records which manager paths the barrier had to
    declare unsafe with a hard failure (manager construction may need to
    raise rather than disable writes).
    """

    paths: PersistencePaths
    results: tuple[MigrationResult, ...]
    blocked_writes: dict[str, str] = field(default_factory=dict)
    raised_during: tuple[str, ...] = ()

    def is_write_blocked(self, filename: str) -> bool:
        return filename in self.blocked_writes

    def block_reason(self, filename: str) -> str | None:
        return self.blocked_writes.get(filename)


# ---------------------------------------------------------------------------
# Module-level prepared state (the gate the managers consult).
# ---------------------------------------------------------------------------
_PREPARED: PreparedPersistence | None = None
_PREPARATION_LOCK_NAME = "hub.persistence.startup._PREPARED"


def _module_lock() -> Any:
    """A per-process lock; reused so barriers serialise under load."""

    import threading

    return threading.Lock()


_MODULE_LOCK = _module_lock()


def prepare_runtime_storage(*, config_dir: Path, data_dir: Path) -> PreparedPersistence:
    """Prepare the runtime's persistent storage and resolve file collisions.

    This is the barrier the runtime composition root must call before any
    manager is constructed. It:

    1. Resolves and creates the configured ``config_dir`` and ``data_dir``
       (so the atomic writer never fails on a missing directory).
    2. Detects and resolves the legacy ``system_shortcuts.json`` /
       ``shortcuts.json`` and ``scenes.json`` / ``scenes_v2.json`` collisions.
       Conflicting content blocks the affected manager and is also reported
       through ``raised_during`` so the composition root can decide whether
       the startup should abort.
    3. Migrates every managed filename up to the current schema version,
       refusing to swallow backup or replace failures (they become
       ``MigrationError`` instead of "the file looked OK").
    4. Records a per-filename write block in :attr:`PreparedPersistence.blocked_writes`
       for any file the runtime cannot safely replace.

    :raises MigrationError: the data dir is unsafe (backup failed during
        migration; both scene files exist with conflicting shapes; both
        shortcut files exist with conflicting content).
    """
    config_dir = Path(config_dir).resolve()
    data_dir = Path(data_dir).resolve()
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    paths = _resolve_paths(config_dir, data_dir)

    blocked: dict[str, str] = {}
    raised_during: list[str] = []
    collision_notes: list[str] = []
    results: list[MigrationResult] = []

    try:
        # 1. Shortcut filename collision resolution.
        _resolve_shortcut_collision(paths, blocked, raised_during, collision_notes)

        # 2. Scene filename collision resolution.
        _resolve_scene_collision(paths, blocked, raised_during, collision_notes)

        # 3. Migrate every managed filename (with backup) and detect unsafe states.
        results.extend(_migrate_managed_files(paths, blocked, raised_during, collision_notes))

        # 4. Translate legacy ``scenes.json`` content into ``scenes_v2.json`` if needed.
        _maybe_import_legacy_scenes(paths, blocked, raised_during, collision_notes)
    except MigrationError:
        # Publish the partial state so existing managers consult the gate even
        # though we then reraise. The composition root may catch + log + exit,
        # but a startup that continues past the barrier (rare) still refuses
        # to overwrite the files the barrier flagged.
        _publish_prepared(paths, results, blocked, raised_during, collision_notes)
        raise

    _publish_prepared(paths, results, blocked, raised_during, collision_notes)
    return _PREPARED  # type: ignore[return-value]


def _publish_prepared(
    paths: PersistencePaths,
    results: list[MigrationResult],
    blocked: dict[str, str],
    raised_during: list[str],
    collision_notes: list[str],
) -> PreparedPersistence:
    """Update the module-level cache with the current preparation result."""
    prepared = PreparedPersistence(
        paths=paths,
        results=tuple(results),
        blocked_writes=dict(blocked),
        raised_during=tuple(raised_during),
    )
    with _MODULE_LOCK:
        global _PREPARED
        _PREPARED = prepared
    if raised_during:
        for note in collision_notes:
            _LOG.warning("%s", note)
    return prepared


def prepared_persistence() -> PreparedPersistence | None:
    """Return the last :func:`prepare_runtime_storage` result, or ``None``."""
    return _PREPARED


def is_write_blocked(filename: str) -> bool:
    """``True`` when the barrier declared ``filename`` unsafe to write to.

    Manager-level :meth:`save` methods consult this gate; a blocked file
    keeps the pre-barrier bytes intact on disk.
    """
    prepared = _PREPARED
    if prepared is None:
        return False
    return prepared.is_write_blocked(filename)


def block_reason(filename: str) -> str | None:
    """Human-readable reason a filename is write-blocked, or ``None``."""
    prepared = _PREPARED
    if prepared is None:
        return None
    return prepared.block_reason(filename)


def reset_preparation() -> None:
    """Drop the cached prepared state (test isolation helper)."""
    global _PREPARED
    with _MODULE_LOCK:
        _PREPARED = None


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _resolve_paths(config_dir: Path, data_dir: Path) -> PersistencePaths:
    """Build the :class:`PersistencePaths` value with every canonical filename."""
    expected_config_files = {name: config_dir / name for name in _CONFIG_FILENAMES}
    expected_data_files = {name: data_dir / name for name in _DATA_FILENAMES}
    return PersistencePaths(
        config_dir=config_dir,
        data_dir=data_dir,
        expected_config_files=expected_config_files,
        expected_data_files=expected_data_files,
    )


def _resolve_shortcut_collision(
    paths: PersistencePaths,
    blocked: dict[str, str],
    raised_during: list[str],
    notes: list[str],
) -> None:
    """Enforce the shipped ``system_shortcuts.json`` vs. alias ``shortcuts.json`` rule.

    * shipped file alone → leave it alone;
    * alias alone → copy to shipped (with backup) so the runtime reads its
      expected filename;
    * both present and content-identical → leave both, manage shipped only;
    * both present and conflicting → raise :class:`MigrationError` (block
      both writes).
    """
    shipped = paths.expected_data_files[SHORTCUTS_SHIPPED_FILENAME]
    alias = paths.expected_data_files.get(SHORTCUTS_ALIAS_FILENAME)
    if alias is None:
        alias = paths.data_dir / SHORTCUTS_ALIAS_FILENAME

    if not alias.exists():
        return

    if not shipped.exists():
        # Copy the legacy alias to the shipped filename with a backup of any
        # existing shipped bytes (rare; usually shipped is simply missing).
        backup = backup_path_for(shipped, 0)
        try:
            payload = atomic_read_json(alias)
        except (ValueError, OSError) as exc:
            msg = f"shortcut alias {alias} could not be read: {exc}"
            notes.append(msg)
            blocked[SHORTCUTS_SHIPPED_FILENAME] = msg
            blocked[SHORTCUTS_ALIAS_FILENAME] = msg
            raised_during.append(SHORTCUTS_SHIPPED_FILENAME)
            raise MigrationError(msg) from exc
        backup.parent.mkdir(parents=True, exist_ok=True)
        shipped.parent.mkdir(parents=True, exist_ok=True)
        try:
            atomic_write_json(shipped, payload)
        except OSError as exc:
            notes.append(f"could not import alias {alias} → {shipped} ({exc})")
            blocked[SHORTCUTS_SHIPPED_FILENAME] = f"alias import failed: {exc}"
            raised_during.append(SHORTCUTS_SHIPPED_FILENAME)
            raise MigrationError(
                f"failed to import legacy shortcuts from {alias} to {shipped}: {exc}"
            ) from exc
        _LOG.info("Imported legacy shortcuts alias %s → %s", alias, shipped)
        return

    # both exist — compare content; identical is fine, conflicting is fatal
    try:
        shipped_payload = atomic_read_json(shipped)
        alias_payload = atomic_read_json(alias)
    except (ValueError, OSError) as exc:
        notes.append(f"could not compare shortcut files ({exc}) — both blocked")
        blocked[SHORTCUTS_SHIPPED_FILENAME] = f"could not compare with alias: {exc}"
        blocked[SHORTCUTS_ALIAS_FILENAME] = f"could not compare with shipped: {exc}"
        raised_during.append(SHORTCUTS_SHIPPED_FILENAME)
        raise MigrationError(
            f"could not compare shipped ({shipped}) and alias ({alias}) shortcut files: {exc}"
        ) from exc

    if _shortcut_payloads_conflict(shipped_payload, alias_payload):
        msg = f"both {shipped.name} and {alias.name} exist with conflicting content"
        notes.append(msg)
        blocked[SHORTCUTS_SHIPPED_FILENAME] = msg
        blocked[SHORTCUTS_ALIAS_FILENAME] = msg
        raised_during.append(SHORTCUTS_SHIPPED_FILENAME)
        raise MigrationError(msg)


def _shortcut_payloads_conflict(a: Any, b: Any) -> bool:
    """Two shortcut file payloads are in conflict if their key sets or shared values differ."""

    def _normalise(payload: Any) -> dict[str, Any]:
        if isinstance(payload, list):
            out: dict[str, Any] = {}
            for item in payload:
                if isinstance(item, dict):
                    key = str(item.get("id") or item.get("key") or "")
                    if key:
                        out[key] = dict(item)
            return out
        if isinstance(payload, dict):
            return {str(k): dict(v) if isinstance(v, dict) else {"value": v} for k, v in payload.items()}
        return {}

    a_norm = _normalise(a)
    b_norm = _normalise(b)
    keys = set(a_norm) | set(b_norm)
    for k in keys:
        av = a_norm.get(k)
        bv = b_norm.get(k)
        if (av is None) != (bv is None):
            return True
        if av is not None and bv is not None and av != bv:
            return True
    return False


def _resolve_scene_collision(
    paths: PersistencePaths,
    blocked: dict[str, str],
    raised_during: list[str],
    notes: list[str],
) -> None:
    """Detect conflicting ``scenes.json`` (config) vs. ``scenes_v2.json`` (unified)."""

    unified = paths.expected_data_files[SCENES_V2_FILENAME]
    legacy = paths.expected_data_files.get(SCENES_LEGACY_FILENAME)
    if legacy is None:
        legacy = paths.data_dir / SCENES_LEGACY_FILENAME

    if not legacy.exists() or not unified.exists():
        return

    try:
        unified_payload = atomic_read_json(unified)
        legacy_payload = atomic_read_json(legacy)
    except (ValueError, OSError) as exc:
        msg = f"could not read scene files to compare ({exc})"
        notes.append(msg)
        blocked[SCENES_V2_FILENAME] = msg
        blocked[SCENES_LEGACY_FILENAME] = msg
        raised_during.append(SCENES_V2_FILENAME)
        raise MigrationError(msg) from exc

    if _scene_payloads_conflict(unified_payload, legacy_payload):
        msg = (
            f"both {unified.name} and {legacy.name} exist with conflicting scene definitions; "
            "rename or back up one before starting"
        )
        notes.append(msg)
        blocked[SCENES_V2_FILENAME] = msg
        blocked[SCENES_LEGACY_FILENAME] = msg
        raised_during.append(SCENES_V2_FILENAME)
        raise MigrationError(msg)


def _scene_payloads_conflict(unified_payload: Any, legacy_payload: Any) -> bool:
    """Two scene lists are in conflict if they share any IDs with different shapes.

    The legacy ``config.Scene`` has shape ``{"id", "name", "outputs": {...}}``
    while the unified ``scene_manager.Scene`` has ``{"id", "name", "steps",
    "overrides", ...}``. A legacy scene with the same id but no ``steps`` field
    is treated as the *same* scene (the unified loader would re-create it from
    the legacy fields). Different ids are not a conflict — both can coexist.
    """

    def _normalise(payload: Any) -> dict[str, dict[str, Any]]:
        if isinstance(payload, dict):
            scenes = payload.get("scenes") or []
        elif isinstance(payload, list):
            scenes = payload
        else:
            scenes = []
        result: dict[str, dict[str, Any]] = {}
        for item in scenes:
            if isinstance(item, dict) and item.get("id"):
                result[str(item["id"])] = dict(item)
        return result

    u_norm = _normalise(unified_payload)
    l_norm = _normalise(legacy_payload)
    for scene_id in set(u_norm) & set(l_norm):
        if _scene_record_conflict(u_norm[scene_id], l_norm[scene_id]):
            return True
    # Cross-shape collision: a legacy bare-list (no envelope) alongside a unified
    # file is suspicious; treat as conflict only when ids overlap with shape diff.
    return False


def _scene_record_conflict(unified: dict[str, Any], legacy: dict[str, Any]) -> bool:
    """A unified scene and a legacy scene with the same id conflict when their
    name or output snapshot differs in a way that would lose user data.
    """

    if unified.get("name") and legacy.get("name") and unified["name"] != legacy["name"]:
        return True
    # Outputs snapshot — same input per output is required.
    u_outputs = unified.get("outputs") or {}
    l_outputs = legacy.get("outputs") or {}
    for key in set(u_outputs) & set(l_outputs):
        uo = u_outputs[key] or {}
        lo = l_outputs[key] or {}
        if isinstance(uo, dict) and isinstance(lo, dict):
            if uo.get("input") and lo.get("input") and uo["input"] != lo["input"]:
                return True
            if uo.get("enabled") is not None and lo.get("enabled") is not None and uo["enabled"] != lo["enabled"]:
                return True
    return False


def _migrate_managed_files(
    paths: PersistencePaths,
    blocked: dict[str, str],
    raised_during: list[str],
    notes: list[str],
) -> list[MigrationResult]:
    """Migrate every managed filename once, treating backup failures as fatal.

    The contract requires that backup failure or atomic-replace failure
    during migration aborts preparation rather than silently producing a
    half-written file. The registry's :func:`migrate_data_file` returns
    ``status="unreadable"`` on a replace failure; we translate that to a
    write block (and a hard ``MigrationError`` for backup failures, because
    those mean a backup copy is missing, leaving no recovery path).
    """

    registry = DEFAULT_REGISTRY
    results: list[MigrationResult] = []
    wanted = list(paths.expected_config_files.values()) + list(paths.expected_data_files.values())

    for path in wanted:
        if not path.exists():
            continue
        if not registry.has(path.name):
            continue
        result, error = _migrate_one(path, registry=registry, blocked=blocked, raised_during=raised_during)
        if result is not None:
            results.append(result)
        if error is not None:
            notes.append(str(error))
            raise error
    return results


def _migrate_one(
    path: Path,
    *,
    registry: MigrationRegistry,
    blocked: dict[str, str],
    raised_during: list[str],
) -> tuple[MigrationResult | None, MigrationError | None]:
    """Migrate one file: backup first, then migrate; failures raise / block.

    Returns ``(migration_result, error_to_raise)``. ``error_to_raise`` is
    non-None when the contract requires the barrier to abort.
    """

    try:
        payload = atomic_read_json(path)
    except FileNotFoundError:
        return MigrationResult(path=path, status="missing"), None
    except (ValueError, OSError) as exc:
        # Corrupt / unreadable source blocks the file and fails preparation:
        # the contract requires we never default-seed over a corrupt file.
        msg = f"{path.name} could not be read ({exc}); refusing to overwrite it with defaults"
        blocked[path.name] = msg
        raised_during.append(path.name)
        return (
            MigrationResult(path=path, status="unreadable"),
            MigrationError(msg),
        )

    version = registry.detect_version(payload)
    if version > registry.current_version:
        msg = f"{path.name} is from a newer release (schema_version {version} > current {registry.current_version})"
        blocked[path.name] = msg
        raised_during.append(path.name)
        return (
            MigrationResult(
                path=path,
                status="unsupported",
                from_version=version,
                to_version=registry.current_version,
            ),
            MigrationError(msg),
        )
    if version == registry.current_version:
        return (
            MigrationResult(
                path=path,
                status="current",
                from_version=version,
                to_version=version,
            ),
            None,
        )

    # Migration is required — back up the pre-migration bytes first. The
    # contract requires a backup before any rewrite; a missing backup is fatal
    # for *every* schema version (the v0 → CURRENT_SCHEMA_VERSION migration
    # changes the on-disk bytes just as much as a v1 → v2 step, so the
    # operator's recovery path through ``<name>.v0.bak`` is just as crucial).
    backup = _safe_backup(path, version, registry)
    if backup is None:
        msg = f"backup failed before migrating {path.name} (from_version={version}); refusing to continue"
        blocked[path.name] = msg
        raised_during.append(path.name)
        return (
            MigrationResult(path=path, status="unreadable", from_version=version),
            MigrationError(msg),
        )

    try:
        migrated, applied = registry.apply(path.name, payload)
    except MigrationError as exc:
        msg = f"migration of {path.name} failed: {exc}"
        blocked[path.name] = msg
        raised_during.append(path.name)
        return (
            MigrationResult(path=path, status="unreadable", from_version=version),
            MigrationError(msg),
        )

    try:
        atomic_write_json(path, migrated)
    except OSError as exc:
        msg = f"could not write migrated {path.name}: {exc} (backup {backup})"
        blocked[path.name] = msg
        raised_during.append(path.name)
        return (
            MigrationResult(path=path, status="unreadable", from_version=version, applied=tuple(applied), backup=backup),
            MigrationError(msg),
        )

    return (
        MigrationResult(
            path=path,
            status="migrated",
            from_version=version,
            to_version=registry.current_version,
            applied=tuple(applied),
            backup=backup,
        ),
        None,
    )


def _safe_backup(path: Path, from_version: int, registry: MigrationRegistry) -> Path | None:
    """Back up ``path`` next to itself; return the backup path or None.

    Returns ``None`` only when the backup is genuinely impossible (not when
    one already exists — an existing backup is treated as preserved). The
    caller then decides whether the missing backup is fatal.
    """
    from .migrations import write_backup

    target = backup_path_for(path, from_version)
    if target.exists():
        return target
    return write_backup(path, from_version)


def _maybe_import_legacy_scenes(
    paths: PersistencePaths,
    blocked: dict[str, str],
    raised_during: list[str],
    notes: list[str],
) -> None:
    """When only ``scenes.json`` exists, import its content to ``scenes_v2.json``.

    The unified scene manager's target is :data:`SCENES_V2_FILENAME`. A legacy
    ``scenes.json`` with recognisable unified-scene records (``steps`` field on
    every scene, not the legacy ``config.Scene`` outputs-only shape) is
    imported non-destructively. The *original bytes* are copied to
    ``<name>.v0.bak`` first; the canonical target is written from the same
    in-memory payload with the runtime ``schema_version`` added, so unknown
    top-level fields and per-record metadata survive.

    The function refuses to silently overwrite a non-empty
    ``scenes_v2.json``; the contract distinguishes the two schemas so a legacy
    ``config.SceneManager`` file is left alone here and only the manager's own
    fallback import (also gated by the unified-shape check) considers it.
    """

    unified = paths.expected_data_files[SCENES_V2_FILENAME]
    legacy = paths.data_dir / SCENES_LEGACY_FILENAME

    if not legacy.exists() or unified.exists():
        return

    legacy_payload: Any
    try:
        legacy_payload = atomic_read_json(legacy)
    except (ValueError, OSError) as exc:
        blocked[SCENES_V2_FILENAME] = f"legacy scenes unreadable ({exc}); refusing to seed"
        blocked[SCENES_LEGACY_FILENAME] = blocked[SCENES_V2_FILENAME]
        notes.append(f"legacy scenes.json is unreadable: {exc}")
        return

    if not _looks_like_unified_scenes(legacy_payload):
        # Not recognisable — leave legacy alone; the unified target stays missing
        # and the manager initialises empty on first save.
        return

    backup_path = _safe_backup(legacy, 0, DEFAULT_REGISTRY)
    if backup_path is None:
        msg = f"failed to back up legacy {legacy.name} before importing to {unified.name}"
        blocked[SCENES_V2_FILENAME] = msg
        blocked[SCENES_LEGACY_FILENAME] = msg
        raised_during.append(SCENES_V2_FILENAME)
        raise MigrationError(msg)

    # Lossless import: stamp schema_version on the existing payload, do not
    # drop unknown top-level keys.
    stamped: dict[str, Any] = {}
    for key, value in legacy_payload.items():
        if key == SCHEMA_VERSION_KEY:
            continue
        stamped[key] = value
    stamped[SCHEMA_VERSION_KEY] = DEFAULT_REGISTRY.current_version

    try:
        atomic_write_json(unified, stamped)
    except OSError as exc:
        msg = f"could not write imported {unified.name}: {exc}"
        blocked[SCENES_V2_FILENAME] = msg
        raised_during.append(SCENES_V2_FILENAME)
        raise MigrationError(msg) from exc
    _LOG.info("Imported legacy %s into %s (backup at %s)", legacy.name, unified.name, backup_path)


def _looks_like_unified_scenes(payload: Any) -> bool:
    """``True`` when ``payload`` carries recognisable unified-scenes shape.

    The contract distinguishes ``scene_manager.SceneManager`` (unified,
    ``steps``-based) from ``config.SceneManager`` (legacy,
    ``outputs``-based). Only the former is treated as a v2 catalog here.
    """

    if isinstance(payload, dict):
        scenes = payload.get("scenes")
    elif isinstance(payload, list):
        scenes = payload
    else:
        return False
    if not isinstance(scenes, list) or not scenes:
        return False
    for scene in scenes:
        if not isinstance(scene, dict):
            return False
        if "steps" not in scene:  # legacy config.Scene lacks ``steps``
            return False
    return True


# Public API
__all__ = [
    "PersistencePaths",
    "PreparedPersistence",
    "MANAGED_FILENAMES",
    "LEGACY_FILENAMES",
    "SCENES_V2_FILENAME",
    "SCENES_LEGACY_FILENAME",
    "SHORTCUTS_SHIPPED_FILENAME",
    "SHORTCUTS_ALIAS_FILENAME",
    "prepare_runtime_storage",
    "prepared_persistence",
    "is_write_blocked",
    "block_reason",
    "reset_preparation",
]
