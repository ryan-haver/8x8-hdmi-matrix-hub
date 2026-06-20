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

Upgrading from a version that hardcoded ``<project_root>/data/`` is safe:
on first access, if the resolved new path is empty but the legacy path
contains files, the relevant legacy file is copied to the new location.
"""

import logging
import os
import shutil
from pathlib import Path

_LOG = logging.getLogger("persistence")

# Cache the resolved data directory to avoid recomputing on every access.
# Tests can call ``reset_data_dir_cache()`` to force re-resolution.
_data_dir_cache: Path | None = None

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

    :returns: Resolved absolute path to the data directory.
    """
    global _data_dir_cache

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


def migrate_legacy_file(target_file: Path, filename: str) -> bool:
    """
    Copy a legacy file to the new data directory if it exists in a legacy
    location but not at the target path.

    This enables transparent upgrades: users who have existing
    ``data/themes.json``, ``data/ui_preferences.json``, etc. will see their
    settings preserved at the new location on first access.

    :param target_file: Where the file should live (new location).
    :param filename: Name of the file to migrate.
    :returns: True if a legacy file was migrated, False otherwise.
    """
    if target_file.exists():
        return False

    if filename in _legacy_migrations:
        # Already migrated in this process.
        return False

    for legacy_dir in get_legacy_data_paths():
        legacy_file = legacy_dir / filename
        if legacy_file.exists() and legacy_file.resolve() != target_file.resolve():
            try:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(legacy_file, target_file)
                _legacy_migrations.add(filename)
                _LOG.info(
                    "Migrated legacy file %s -> %s", legacy_file, target_file
                )
                return True
            except OSError as exc:
                _LOG.warning(
                    "Could not migrate legacy file %s: %s", legacy_file, exc
                )
                return False

    return False


def reset_data_dir_cache() -> None:
    """
    Reset the cached data directory. Intended for tests that need to switch
    between multiple resolutions within a single process.
    """
    global _data_dir_cache
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