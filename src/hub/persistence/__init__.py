"""Persistent state for the hub: versioned files, migrations and backups (PER-04).

The public surface is deliberately small — a caller loads, mutates and saves one
data file by name, and the schema version travels with the file:

    >>> from hub.persistence import load_versioned_json, save_versioned_json
    >>> save_versioned_json(data_dir / "profiles.json", {"profiles": []})
    True
    >>> load_versioned_json(data_dir / "profiles.json")["schema_version"]
    2

See :mod:`hub.persistence.migrations` for the file inventory, the migration
functions and the backup-before-migrate contract.
"""

from __future__ import annotations

from .migrations import (
    CURRENT_SCHEMA_VERSION,
    DEFAULT_REGISTRY,
    LEGACY_FILENAMES,
    MANAGED_FILENAMES,
    SCHEMA_VERSION_KEY,
    DataFileSpec,
    MigrationError,
    MigrationRegistry,
    MigrationResult,
    SchemaVersionError,
    backup_path_for,
    build_default_registry,
    load_versioned_json,
    migrate_all_data_files,
    migrate_data_file,
    save_versioned_json,
    write_backup,
)
from .startup import (
    PersistencePaths,
    PreparedPersistence,
    block_reason,
    is_write_blocked,
    prepare_runtime_storage,
    prepared_persistence,
    reset_preparation,
)

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
    "PersistencePaths",
    "PreparedPersistence",
    "SchemaVersionError",
    "backup_path_for",
    "block_reason",
    "build_default_registry",
    "is_write_blocked",
    "load_versioned_json",
    "migrate_all_data_files",
    "migrate_data_file",
    "prepared_persistence",
    "prepare_runtime_storage",
    "reset_preparation",
    "save_versioned_json",
    "write_backup",
]
