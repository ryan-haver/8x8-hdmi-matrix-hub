"""
Persistent Storage Path Resolution.

Centralizes resolution of the persistent data directory for ALL user-addressable
state (device settings, themes, UI preferences, driver state, scenes, profiles,
CEC macros). This is the single source of truth that:

1. Honors user-configured volume paths in Docker deployments
2. Respects the UC-standard ``UC_CONFIG_HOME`` env var for backward compat
3. Provides a dedicated ``MATRIX_DATA_DIR`` override for explicit control
4. Falls back to the project-local ``data/`` dir for local development
5. Migrates legacy files from the old hardcoded ``data/`` location transparently

Path Resolution Priority
========================

When resolving the data directory, the following priority applies:

1. ``MATRIX_DATA_DIR`` env var (explicit, recommended for Docker)
2. ``UC_CONFIG_HOME`` env var (UC-standard, used by ``config/`` directory)
   - The data dir becomes ``$UC_CONFIG_HOME/data`` so that the existing
     ``$UC_CONFIG_HOME`` continues to govern the ``config/`` subdirectory
3. ``<project_root>/data`` (local development default)

When deploying via Docker, mount your chosen host path to ``/data`` in the
container and set ``UC_CONFIG_HOME=/data`` (or use ``MATRIX_DATA_DIR=/data``
directly). All persistent files will then live under that mount.

Backward Compatibility
======================

Runtime preparation imports config catalogs from the installation's resolved
data directory, with backups. Importing a different old volume requires an
explicit source; a fresh installation never inherits another checkout's catalogs.
Non-catalog preferences retain their project-local legacy copy behavior.
"""

import logging
import os
import threading
from pathlib import Path

_LOG = logging.getLogger("persistence")

# Cache the resolved data directory to avoid recomputing on every access.
# Tests can call ``reset_data_dir_cache()`` to force re-resolution.
_data_dir_cache: Path | None = None

# Lock protecting concurrent access to _data_dir_cache and _legacy_migrations.
# Uses threading.Lock (not asyncio.Lock) because get_data_dir() and
# migrate_legacy_file() are called from both sync and async contexts.
_persistence_lock = threading.Lock()

# Track which legacy files have been migrated (in-memory only; migrations
# are also persisted by the file appearing at the new path).
_legacy_migrations: set[str] = set()


def get_project_root() -> Path:
    """Return the project root directory (parent of ``src/``)."""
    return Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """
    Resolve and return the canonical persistent data directory.

    Resolution order (highest priority first):

    1. ``MATRIX_DATA_DIR`` env var (explicit, recommended for Docker)
    2. ``UC_CONFIG_HOME`` env var → ``$UC_CONFIG_HOME/data``
    3. ``<project_root>/data`` (local development default)

    The result is cached for the process lifetime. Call
    :func:`reset_data_dir_cache` to force re-resolution (useful in tests).

    Thread-safe: uses ``threading.Lock`` to prevent concurrent first-call
    resolution from initializing the cache twice.

    :returns: Resolved absolute path to the data directory.
    """
    global _data_dir_cache

    # Fast path: lock-free check for the common already-resolved case.
    if _data_dir_cache is not None:
        return _data_dir_cache

    with _persistence_lock:
        # Double-check after acquiring the lock.
        if _data_dir_cache is not None:
            return _data_dir_cache

        # Priority 1: Explicit MATRIX_DATA_DIR override.
        # This is the recommended variable for Docker deployments where the
        # operator wants full control over the host path.
        explicit = os.environ.get("MATRIX_DATA_DIR")
        if explicit:
            _data_dir_cache = Path(explicit).resolve()
            return _data_dir_cache

        # Priority 2: UC_CONFIG_HOME (UC-standard backward-compat).
        # We append ``/data`` so the existing UC_CONFIG_HOME continues to
        # control the ``config/`` subdirectory without mixing the two layouts.
        uc_home = os.environ.get("UC_CONFIG_HOME")
        if uc_home:
            _data_dir_cache = (Path(uc_home) / "data").resolve()
            return _data_dir_cache

        # Priority 3: Local development default.
        _data_dir_cache = (get_project_root() / "data").resolve()
        return _data_dir_cache


def get_config_dir() -> Path:
    """
    Resolve and return the configuration directory (scenes/profiles/macros).

    Resolution order:

    1. ``UC_CONFIG_HOME`` env var (UC-standard)
    2. ``$HOME`` env var (when running outside Docker)
    3. ``./config`` relative to CWD (legacy local-dev fallback)

    :returns: Resolved absolute path to the config directory.
    """
    uc_home = os.environ.get("UC_CONFIG_HOME")
    if uc_home:
        return Path(uc_home).resolve()

    home = os.environ.get("HOME")
    if home:
        return Path(home).resolve() / "config"

    return Path("./config").resolve()


def ensure_data_dir(data_dir: Path | None = None) -> Path:
    """
    Ensure the data directory exists, creating it if necessary.

    :param data_dir: Directory to ensure (defaults to :func:`get_data_dir`).
    :returns: Resolved data directory path (same as input).
    """
    if data_dir is None:
        data_dir = get_data_dir()

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_legacy_data_paths() -> list[Path]:
    """
    Return the list of legacy data directory paths to check for migration.

    Currently the only legacy location is the project-root ``data/`` directory
    that was hardcoded in older versions of the codebase.

    :returns: Ordered list of legacy paths (highest priority first).
    """
    return [get_project_root() / "data"]


def migrate_legacy_file(target_file: Path, filename: str, *, legacy_dirs: tuple[Path, ...] | None = None) -> bool:
    """
    Copy a legacy file to the new data directory if it exists in a legacy
    location but not at the target path.

    This enables transparent upgrades: users who have existing
    ``data/themes.json``, ``data/ui_preferences.json``, etc. will see their
    settings preserved at the new location on first access.

    Managed catalogs import only from explicitly supplied ``legacy_dirs``.
    An explicit destination does not authorize reading another installation's
    project-local data. Runtime preparation supplies its own old data volume;
    direct callers may supply a deliberate old-volume source. Non-catalog
    preferences retain their existing legacy-location lookup and recovery.

    Migration is atomic, corruption-aware and never destructive (PER-03):
    - If the target exists and is valid JSON, skip migration (idempotent).
    - If a non-catalog target cannot be *read* (permissions, sharing
      violation, I/O error), leave it untouched and skip migration — an
      unreadable file is not a corrupt one.
    - Unsafe existing managed targets fail closed, with their bytes untouched.
    - If a non-catalog target is corrupt (not valid JSON/UTF-8), it is only
      replaced once a readable, valid legacy file is in hand; the corrupt
      content is first copied to ``<name>.corrupt``; backup failure prevents replacement.
    - The target is never deleted. Writes go through ``atomic_write_json`` so
      a crash mid-migration cannot leave a partial file.

    :param target_file: Where the file should live (new location).
    :param filename: Name of the file to migrate.
    :param legacy_dirs: Explicit old-volume sources; required for managed catalogs.
    :returns: True if a legacy file was migrated, False otherwise.
    """
    import json as _json

    from hub.persistence.migrations import (
        _WRITE_FAILURES,
        DEFAULT_REGISTRY,
        MigrationError,
        block_path,
        validate_payload,
        write_backup,
    )

    target_file = Path(target_file).resolve()
    managed = DEFAULT_REGISTRY.has(filename) or filename == "scenes.json"
    if managed and target_file in _WRITE_FAILURES:
        raise MigrationError(f"{target_file}: {_WRITE_FAILURES[target_file]}")
    target_corrupt = False
    if target_file.exists():
        try:
            with open(target_file, encoding="utf-8") as _f:
                current = _json.load(_f)
            if managed:
                if filename == "scenes.json":
                    from hub.persistence.startup import scene_shape

                    scene_shape(current)
                else:
                    validate_payload(filename, current)
            return False  # Valid target already exists
        except ValueError as exc:
            if managed:
                block_path(target_file, "unsafe existing migration target")
                raise MigrationError(f"{target_file}: unsafe existing migration target") from exc
            target_corrupt = True
            _LOG.warning("Migration target %s is corrupt; will replace it only from a valid legacy file", target_file)
        except OSError as exc:
            if managed:
                block_path(target_file, "unreadable existing migration target")
                raise MigrationError(f"{target_file}: unreadable existing migration target") from exc
            _LOG.warning("Cannot read migration target %s (%s); leaving it untouched", target_file, exc)
            return False

    sources = legacy_dirs if legacy_dirs is not None else (() if managed else tuple(get_legacy_data_paths()))
    for legacy_dir in sources:
        legacy_file = legacy_dir / filename
        if legacy_file.exists() and legacy_file.resolve() != target_file.resolve():
            try:
                # Validate legacy file before touching the target
                with open(legacy_file, encoding="utf-8") as _f:
                    _legacy_data = _json.load(_f)
            except (ValueError, OSError) as exc:
                _LOG.warning("Could not migrate legacy file %s: %s", legacy_file, exc)
                if managed:
                    raise MigrationError(f"{legacy_file}: unreadable legacy source") from exc
                return False
            if managed:
                if filename == "scenes.json":
                    from hub.persistence.startup import scene_shape

                    scene_shape(_legacy_data)
                else:
                    validate_payload(filename, _legacy_data)
                if write_backup(legacy_file, DEFAULT_REGISTRY.detect_version(_legacy_data)) is None:
                    raise MigrationError(f"{legacy_file}: backup failed before legacy-location import")
                if DEFAULT_REGISTRY.has(filename):
                    _legacy_data = DEFAULT_REGISTRY.apply(filename, _legacy_data)[0]
            try:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                if target_corrupt:
                    _preserve_corrupt_file(target_file)
                # Use atomic write for migration target — prevents partial writes
                from _file_io import atomic_write_json

                atomic_write_json(target_file, _legacy_data)
            except OSError as exc:
                _LOG.warning("Could not write migrated file %s: %s", target_file, exc)
                if managed:
                    raise MigrationError(f"{target_file}: legacy-location import failed") from exc
                return False
            with _persistence_lock:
                _legacy_migrations.add(str(target_file.resolve()))
            _LOG.info("Migrated legacy file %s -> %s", legacy_file, target_file)
            return True

    return False


def _preserve_corrupt_file(path: Path) -> None:
    """Preserve corrupt original bytes, refusing a conflicting existing backup."""
    import shutil

    backup = path.with_name(f"{path.name}.corrupt")
    if backup.exists():
        if backup.read_bytes() != path.read_bytes():
            raise OSError(f"Corrupt backup already contains different bytes: {backup}")
        return
    shutil.copy2(path, backup)
    _LOG.warning("Saved corrupt %s as %s", path, backup)


def reset_data_dir_cache() -> None:
    """
    Reset the cached data directory. Intended for tests that need to switch
    between multiple resolutions within a single process.
    """
    global _data_dir_cache
    with _persistence_lock:
        _data_dir_cache = None
        _legacy_migrations.clear()


def describe_storage_layout() -> dict[str, str]:
    """
    Return a human-readable description of the current storage layout.

    Useful for the ``GET /api/system/info`` endpoint and for debugging.

    :returns: Dictionary of storage paths and resolved values.
    """
    data_dir = get_data_dir()
    config_dir = get_config_dir()
    return {
        "data_dir": str(data_dir),
        "config_dir": str(config_dir),
        "matrix_data_dir_env": os.environ.get("MATRIX_DATA_DIR", ""),
        "uc_config_home_env": os.environ.get("UC_CONFIG_HOME", ""),
    }
