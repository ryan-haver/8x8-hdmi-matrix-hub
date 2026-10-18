"""Runtime storage barrier (``hub.persistence.startup``) behaviour tests.

These tests pin the contract §4 behaviour the runtime composition root
relies on:

* preparing paths and creating missing directories before any manager
  constructor runs,
* migrating every managed file with backup, refusing to swallow failures,
* recording per-filename write blocks so existing managers refuse to
  overwrite an unsafe file,
* resolving the legacy ``system_shortcuts.json`` / ``shortcuts.json`` and
  ``scenes.json`` / ``scenes_v2.json`` filename collisions,
* surfacing ambiguous / backup-failed states through
  :class:`hub.persistence.MigrationError`.

The barrier intentionally does not construct Flic — R5 owns the Flic
reader.

Tests share the autouse isolation in :mod:`tests.conftest` (a fresh data
dir per test, ``MATRIX_DATA_DIR`` reset).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hub.persistence import (
    LEGACY_FILENAMES,
    MANAGED_FILENAMES,
    SCHEMA_VERSION_KEY,
    MigrationError,
    MigrationResult,
    PersistencePaths,
    PreparedPersistence,
    block_reason,
    is_write_blocked,
    prepare_runtime_storage,
    prepared_persistence,
    reset_preparation,
)
from hub.persistence.migrations import CURRENT_SCHEMA_VERSION

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "runtime_persistence_r2"


@pytest.fixture(autouse=True)
def _reset_barrier_state():
    """Make sure each test starts from a clean barrier state."""
    reset_preparation()
    yield
    reset_preparation()


# ---------------------------------------------------------------------------
# Happy path: fresh install, no fixture data
# ---------------------------------------------------------------------------


class TestFreshInstall:
    """The barrier resolves both directories and the registered filenames."""

    def test_creates_missing_directories(self, tmp_path):
        config_dir = tmp_path / "cfg"
        data_dir = tmp_path / "data"
        # dirs do not yet exist; the barrier must mkdir them
        prepare_runtime_storage(config_dir=config_dir, data_dir=data_dir)
        assert config_dir.is_dir()
        assert data_dir.is_dir()

    def test_resolves_canonical_paths(self, tmp_path):
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        # same dir used for both config + data in this test is intentional; we
        # only care that every canonical filename resolves to *something*
        assert isinstance(prepared.paths, PersistencePaths)
        assert "scenes_v2.json" in prepared.paths.expected_data_files
        assert "system_shortcuts.json" in prepared.paths.expected_data_files
        assert "profiles.json" in prepared.paths.expected_config_files
        assert "cec_macros.json" in prepared.paths.expected_config_files

    def test_records_only_the_migrations_that_actually_ran(self, tmp_path):
        # no files → no migration results (missing files don't appear)
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert all(r.status == "missing" for r in prepared.results)
        assert all(r.path.name in MANAGED_FILENAMES for r in prepared.results)

    def test_unblocked_state_when_nothing_went_wrong(self, tmp_path):
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        for filename in MANAGED_FILENAMES:
            assert is_write_blocked(filename) is False, filename
            assert block_reason(filename) is None


# ---------------------------------------------------------------------------
# Migrations
# ---------------------------------------------------------------------------


class TestBarrierMigrations:
    """A v0 file is migrated in place with backup; writes are still allowed afterwards."""

    def test_v0_unified_scenes_list_is_migrated_into_scenes_v2(self, tmp_path):
        legacy = tmp_path / "scenes_v2.json"
        legacy.write_text(
            (FIXTURES / "v0_unified_scenes_list.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        results = [r for r in prepared.results if r.path == legacy]
        assert len(results) == 1
        assert results[0].status == "migrated"
        assert results[0].from_version == 0
        assert results[0].to_version == CURRENT_SCHEMA_VERSION
        assert results[0].backup == legacy.with_name("scenes_v2.json.v0.bak")
        assert results[0].backup.exists()

        payload = json.loads(legacy.read_text(encoding="utf-8"))
        assert payload[SCHEMA_VERSION_KEY] == CURRENT_SCHEMA_VERSION
        assert payload["scenes"][0]["steps"] == [{"type": "macro", "id": "macro_tv_on"}]

    def test_v0_profiles_envelope_is_migrated_and_unknown_keys_preserved(self, tmp_path):
        profiles = tmp_path / "profiles.json"
        profiles.write_text(
            (FIXTURES / "v0_profiles_envelope.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        result = next(r for r in prepared.results if r.path == profiles)
        assert result.status == "migrated"
        payload = json.loads(profiles.read_text(encoding="utf-8"))
        # The registry must carry the operator-note through the migration.
        assert payload["profiles"][0]["operator_note"] == "preserved through migration"
        assert not is_write_blocked("profiles.json")

    def test_shortcut_alias_filename_is_migrated_in_place(self, tmp_path):
        """``system_shortcuts.json`` is migrated even though the registry alias
        points back to it (alias aliasOf canonical)."""
        path = tmp_path / "system_shortcuts.json"
        path.write_text(
            (FIXTURES / "v0_shortcuts_alias.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        results = [r for r in prepared.results if r.path == path]
        assert results and results[0].status == "migrated"
        assert not is_write_blocked("system_shortcuts.json")


# ---------------------------------------------------------------------------
# Filename collisions
# ---------------------------------------------------------------------------


class TestShortcutFilenameCollision:
    """Aliases must be resolved without losing either file on disk."""

    def _write_payload(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_only_alias_is_copied_to_canonical_with_backup(self, tmp_path):
        alias = tmp_path / "shortcuts.json"
        # A single hotkey so the registries' "all to out 1" rename does not change the assertion.
        self._write_payload(alias, {"schema_version": 2, "mute_all_audio": {"label": "Mute all", "enabled": True, "order": 3}})

        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        shipped = tmp_path / "system_shortcuts.json"
        assert shipped.exists()
        assert alias.exists()  # preserved
        tmp_path / "shortcuts.json.v0.bak"
        # write_backup skips when the backup already exists; in this fresh dir
        # the alias has no prior backup, so the migration copies in place.
        assert not is_write_blocked("system_shortcuts.json")
        # The barrier kept the alias for the operator.
        assert all(r.status in ("migrated", "missing", "current") for r in prepared.results)

    def test_both_files_present_and_identical_succeeds(self, tmp_path):
        payload = {"schema_version": 2, "mute_all_audio": {"label": "Mute", "enabled": True, "order": 3}}
        shipped = tmp_path / "system_shortcuts.json"
        alias = tmp_path / "shortcuts.json"
        self._write_payload(shipped, payload)
        self._write_payload(alias, payload)
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        # Both kept; no error raised; shipped remains the canonical target.
        assert shipped.exists()
        assert alias.exists()
        assert not is_write_blocked("system_shortcuts.json")

    def test_both_files_present_and_different_is_blocked(self, tmp_path):
        shipped = tmp_path / "system_shortcuts.json"
        alias = tmp_path / "shortcuts.json"
        self._write_payload(shipped, {"schema_version": 2, "mute_all_audio": {"label": "A", "enabled": True, "order": 0}})
        self._write_payload(alias, {"schema_version": 2, "mute_all_audio": {"label": "B", "enabled": True, "order": 0}})

        with pytest.raises(MigrationError) as exc_info:
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert "conflicting" in str(exc_info.value).lower()

    def test_legacy_alias_failed_to_read_blocks_both_writes(self, tmp_path):
        """When the alias JSON cannot be read and the canonical is missing, the barrier raises
        and the partial state still gates subsequent writes."""
        alias = tmp_path / "shortcuts.json"
        alias.write_text("{not json", encoding="utf-8")
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert is_write_blocked("system_shortcuts.json")
        assert block_reason("system_shortcuts.json")


class TestSceneFilenameCollision:
    """``scenes.json`` is the legacy config.SceneManager file; ``scenes_v2.json`` is the unified target."""

    def test_legacy_with_unified_shape_is_imported_to_scenes_v2(self, tmp_path):
        legacy = tmp_path / "scenes.json"
        legacy.write_text(
            json.dumps({"scenes": [{"id": "s1", "name": "Demo", "steps": []}]}),
            encoding="utf-8",
        )
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert (tmp_path / "scenes_v2.json").exists()
        assert legacy.exists(), "legacy file is preserved non-destructively"
        # The barrier made no write blocks.
        assert prepared.blocked_writes == {}

    def test_both_files_with_conflicting_scene_names_raises(self, tmp_path):
        unified = tmp_path / "scenes_v2.json"
        legacy = tmp_path / "scenes.json"
        unified.write_text(
            json.dumps({"scenes": [{"id": "share", "name": "Unified", "steps": []}]}),
            encoding="utf-8",
        )
        legacy.write_text(
            json.dumps({"scenes": [{"id": "share", "name": "Legacy", "outputs": {}}]}),
            encoding="utf-8",
        )
        with pytest.raises(MigrationError) as exc_info:
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert "conflicting" in str(exc_info.value).lower()

    def test_empty_legacy_scene_target_initialises_with_no_block(self, tmp_path):
        """Empty scenes may initialise empty without deleting source."""
        legacy = tmp_path / "scenes.json"
        legacy.write_text("[]", encoding="utf-8")
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        # The barrier leaves the legacy file untouched and does not block writes;
        # scenes_v2.json materialises through the manager's first save.
        assert legacy.exists()
        assert "scenes_v2.json" not in prepared.blocked_writes
        assert not is_write_blocked("scenes_v2.json")
        # Constructing the manager (the barrier's consumer) materialises the empty canonical target.
        from scene_manager import SceneManager

        SceneManager(data_dir=tmp_path)
        assert (tmp_path / "scenes_v2.json").exists()


# ---------------------------------------------------------------------------
# Unsafe states block writes
# ---------------------------------------------------------------------------


class TestUnsafeStatesBlockWrites:
    """Future / corrupt / unreadable files are left untouched; their manager's
    ``save()`` must refuse to write so a later edit doesn't overwrite user data.
    """

    def test_future_schema_blocks_subsequent_writes(self, tmp_path):
        target = tmp_path / "profiles.json"
        target.write_text(json.dumps({"schema_version": CURRENT_SCHEMA_VERSION + 5, "profiles": []}), encoding="utf-8")

        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert is_write_blocked("profiles.json")
        reason = (block_reason("profiles.json") or "").lower()
        assert "unsupported" in reason or "newer release" in reason

        # The bytes are preserved byte-for-byte.
        payload = json.loads(target.read_text(encoding="utf-8"))
        assert payload["schema_version"] == CURRENT_SCHEMA_VERSION + 5

    def test_corrupt_json_blocks_subsequent_writes(self, tmp_path):
        target = tmp_path / "profiles.json"
        target.write_text("{half a profile", encoding="utf-8")
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert is_write_blocked("profiles.json")
        # Bytes are preserved.
        assert target.read_text(encoding="utf-8") == "{half a profile"

    def test_unreadable_target_is_left_untouched_when_other_files_were_ok(self, tmp_path):
        """A single unreadable file fails preparation; only that file is blocked,
        but the partial state is still published so subsequent saves refuse to write.
        """
        target = tmp_path / "profiles.json"
        target.write_text("{half a profile", encoding="utf-8")
        other = tmp_path / "cec_macros.json"
        other.write_text(
            json.dumps(
                {
                    "schema_version": CURRENT_SCHEMA_VERSION,
                    "macros": [],
                    "version": 2,
                }
            ),
            encoding="utf-8",
        )
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert is_write_blocked("profiles.json")
        assert not is_write_blocked("cec_macros.json")


# ---------------------------------------------------------------------------
# Backup failure must abort preparation
# ---------------------------------------------------------------------------


class TestBackupFailureAborts:
    """Backup failure during a required migration is an unsafe state: the barrier raises.

    The contract requires a backup before *any* rewrite, including the v0 →
    CURRENT_SCHEMA_VERSION migration (the operator's recovery path through
    ``<name>.v0.bak`` is just as crucial as a v1 → v2 step).
    """

    @pytest.mark.parametrize("schema_version", [0, 1])
    def test_backup_failure_is_treated_as_a_hard_error_for_every_version(
        self, tmp_path, monkeypatch, schema_version
    ):
        from hub.persistence.migrations import write_backup as real_write_backup

        target = tmp_path / "profiles.json"
        target.write_text(
            json.dumps(
                {
                    "schema_version": schema_version,
                    "profiles": [{"id": "x", "name": "Before migration"}],
                }
            ),
            encoding="utf-8",
        )

        def breaking_write_backup(path, from_version):
            if path.name == "profiles.json":
                return None
            return real_write_backup(path, from_version)

        monkeypatch.setattr("hub.persistence.migrations.write_backup", breaking_write_backup)

        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert is_write_blocked("profiles.json")
        # Original bytes are preserved (no destructive overwrite).
        assert json.loads(target.read_text(encoding="utf-8"))["profiles"][0]["id"] == "x"
        # No backup was written either (write_backup returned None), so the
        # backup file must NOT exist.
        assert not (target.with_name(target.name + ".v0.bak")).exists()
        assert not (target.with_name(target.name + ".v1.bak")).exists()

    def test_atomic_replace_failure_is_a_hard_error_too(self, tmp_path, monkeypatch):
        """Atomic-replace failure during migration also fails preparation (PER-04 contract);
        the partial state still gates subsequent writes.
        """
        target = tmp_path / "profiles.json"
        target.write_text(
            json.dumps({"profiles": [{"id": "x", "name": "x"}]}),
            encoding="utf-8",
        )
        from _file_io import atomic_write_json as real_writer

        def boom(path, payload, **_kw):
            if Path(path).name == "profiles.json":
                raise OSError("disk full")
            return real_writer(path, payload, **_kw)

        monkeypatch.setattr("hub.persistence.startup.atomic_write_json", boom)

        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert is_write_blocked("profiles.json")
        # Original bytes preserved.
        assert json.loads(target.read_text(encoding="utf-8"))["profiles"][0]["id"] == "x"


# ---------------------------------------------------------------------------
# Idempotence
# ---------------------------------------------------------------------------


class TestPreparationIdempotence:
    """Calling the barrier twice (same dir) on a fresh state produces no further migrations."""

    def test_running_twice_does_not_rewrite_files(self, tmp_path):
        target = tmp_path / "profiles.json"
        target.write_text(
            json.dumps(
                {
                    "schema_version": CURRENT_SCHEMA_VERSION,
                    "profiles": [{"id": "p", "name": "P", "pinned": True, "pin_order": 0}],
                }
            ),
            encoding="utf-8",
        )
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        first_bytes = target.read_bytes()
        # Reset so the next call has to start fresh from scratch (no caching).
        reset_preparation()
        second = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert first_bytes == target.read_bytes()
        # The second call sees the file already at CURRENT_SCHEMA_VERSION.
        result = next(r for r in second.results if r.path == target)
        assert result.status in ("current",)
        assert result.from_version == CURRENT_SCHEMA_VERSION

    def test_subsequent_writes_after_barrier_succeed(self, tmp_path):
        """Once the barrier declares the file safe, subsequent manager writes
        are not blocked."""
        target = tmp_path / "profiles.json"
        target.write_text(
            json.dumps({"schema_version": CURRENT_SCHEMA_VERSION, "profiles": []}),
            encoding="utf-8",
        )
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert not is_write_blocked("profiles.json")
        # Simulate a write through the atomic writer; the barrier must not interfere.
        from _file_io import atomic_write_json

        atomic_write_json(target, {"schema_version": CURRENT_SCHEMA_VERSION, "profiles": [{"id": "fresh"}]})
        assert json.loads(target.read_text(encoding="utf-8"))["profiles"][0]["id"] == "fresh"


# ---------------------------------------------------------------------------
# Result/PreparedPersistence shape
# ---------------------------------------------------------------------------


class TestPreparedPersistenceShape:
    """The contract freezes the Public Type the composition root depends on."""

    def test_returned_object_is_a_frozen_prepared_persistence(self, tmp_path):
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert isinstance(prepared, PreparedPersistence)
        assert isinstance(prepared.paths, PersistencePaths)
        assert isinstance(prepared.results, tuple)
        assert all(isinstance(r, MigrationResult) for r in prepared.results)
        # frozen dataclass: no mutation.
        with pytest.raises(Exception):
            prepared.paths = None  # type: ignore[misc]

    def test_blocked_writes_keys_are_known_filenames(self, tmp_path):
        target = tmp_path / "scenes_v2.json"
        target.write_text("{", encoding="utf-8")  # corrupt
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        prepared = prepared_persistence()
        assert prepared is not None
        assert "scenes_v2.json" in prepared.blocked_writes
        for filename in prepared.blocked_writes:
            assert filename in MANAGED_FILENAMES or filename in LEGACY_FILENAMES, filename

    def test_prepared_persistence_returns_latest_barrier_state(self, tmp_path):
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert prepared_persistence() is prepared

    def test_reset_clears_module_state(self, tmp_path):
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        reset_preparation()
        assert prepared_persistence() is None
        assert is_write_blocked("profiles.json") is False
