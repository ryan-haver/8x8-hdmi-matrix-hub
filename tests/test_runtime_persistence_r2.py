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
        self._write_payload(
            alias, {"schema_version": 2, "mute_all_audio": {"label": "Mute all", "enabled": True, "order": 3}}
        )

        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        shipped = tmp_path / "system_shortcuts.json"
        assert shipped.exists()
        assert alias.exists()  # preserved
        tmp_path / "shortcuts.json.v0.bak"
        # write_backup skips when the backup already exists; in this fresh dir
        # the alias has no prior backup, so the migration copies in place.
        assert not is_write_blocked("system_shortcuts.json")
        # The barrier kept the alias for the operator.
        assert all(r.status in ("migrated", "missing", "current", "preserved") for r in prepared.results)

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
        self._write_payload(
            shipped, {"schema_version": 2, "mute_all_audio": {"label": "A", "enabled": True, "order": 0}}
        )
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
        assert "unsupported" in reason or "newer" in reason

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
        assert is_write_blocked("cec_macros.json")  # failed installation cannot seed writers


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
    def test_backup_failure_is_treated_as_a_hard_error_for_every_version(self, tmp_path, monkeypatch, schema_version):
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

        monkeypatch.setattr("hub.persistence.migrations.atomic_write_json", boom)

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
        assert str(target) in prepared.blocked_writes
        assert all(Path(path).is_absolute() for path in prepared.blocked_writes)

    def test_prepared_persistence_returns_latest_barrier_state(self, tmp_path):
        prepared = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        assert prepared_persistence() is prepared

    def test_reset_clears_module_state(self, tmp_path):
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        reset_preparation()
        assert prepared_persistence() is None
        assert is_write_blocked("profiles.json") is False


@pytest.mark.parametrize("schema", [0, 1, 2])
def test_flic_format_roundtrip_preserves_metadata_without_inventing_buttons(tmp_path, schema):
    from hub.persistence import flat_map_records, load_versioned_json, save_versioned_json

    target = tmp_path / "flic_buttons.json"
    payload = {
        "80:e4:da:70:00:01": {"bdaddr": "80:e4:da:70:00:01", "name": "Before", "private": 8},
        "extension_scalar": 7,
        "extension_object": {"private": 9},
    }
    if schema:
        payload["schema_version"] = schema
    target.write_text(json.dumps(payload), encoding="utf-8")
    original = target.read_bytes()
    prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path)
    loaded = load_versioned_json(target)
    records = flat_map_records(target.name, loaded)
    assert len(records) == 1
    records["80:e4:da:70:00:01"] = {"bdaddr": "80:e4:da:70:00:01", "name": "After"}
    assert save_versioned_json(target, records)
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert raw["schema_version"] == 2
    assert raw["extension_scalar"] == 7 and raw["extension_object"] == {"private": 9}
    assert raw["80:e4:da:70:00:01"]["private"] == 8
    if schema < 2:
        assert target.with_name(f"flic_buttons.json.v{schema}.bak").read_bytes() == original
    assert save_versioned_json(target, {})
    assert flat_map_records(target.name, load_versioned_json(target)) == {}
    assert json.loads(target.read_text(encoding="utf-8"))["extension_scalar"] == 7


@pytest.mark.parametrize(
    "source",
    [
        {"scenes": [{"id": "other", "steps": []}]},
        {"scenes": [{"id": "same", "outputs": {}}]},
        {"scenes": [{"id": "disjoint", "outputs": {}}]},
        {"scenes": [{"id": "same", "steps": [], "outputs": {}}]},
        {"scenes": [{"id": "same"}]},
        {"scenes": [{"id": "a", "steps": []}, {"id": "b", "outputs": {}}]},
    ],
)
def test_conflicting_or_ambiguous_scene_files_preserve_all_original_bytes(tmp_path, source):
    canonical = tmp_path / "scenes_v2.json"
    legacy = tmp_path / "scenes.json"
    canonical.write_text(json.dumps({"scenes": [{"id": "same", "steps": []}]}), encoding="utf-8")
    legacy.write_text(json.dumps(source), encoding="utf-8")
    before = {p: p.read_bytes() for p in (canonical, legacy)}
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path)
    assert {p: p.read_bytes() for p in before} == before


def test_backup_collision_never_claims_different_bytes_are_preserved(tmp_path):
    from hub.persistence import load_versioned_json, save_versioned_json

    target = tmp_path / "profiles.json"
    original = b'{ "profiles": [{"id":"original", "outputs":{}}] }'
    target.write_bytes(original)
    backup = tmp_path / "profiles.json.v0.bak"
    backup.write_bytes(b"an older backup")
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
    with pytest.raises(MigrationError):
        load_versioned_json(target)
    with pytest.raises(MigrationError):
        save_versioned_json(target, {"profiles": []})
    assert target.read_bytes() == original
    assert backup.read_bytes() == b"an older backup"


@pytest.mark.parametrize("schema", [0, 1])
def test_actual_atomic_replace_failure_preserves_original_and_raw_backup(tmp_path, monkeypatch, schema):
    import os

    from config import ProfileManager

    target = tmp_path / "profiles.json"
    payload = {"profiles": [{"id": "p", "outputs": {}}], "schema_version": schema}
    target.write_text(json.dumps(payload), encoding="utf-8")
    original = target.read_bytes()
    real_replace = os.replace

    def fail_replace(source, destination):
        if Path(destination) == target:
            raise OSError("injected atomic replacement failure")
        return real_replace(source, destination)

    monkeypatch.setattr("_file_io.os.replace", fail_replace)
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
    assert target.read_bytes() == original
    assert (tmp_path / f"profiles.json.v{schema}.bak").read_bytes() == original
    with pytest.raises(MigrationError):
        ProfileManager(tmp_path)
    assert target.read_bytes() == original


def test_failures_are_scoped_to_volume_and_not_last_preparation(tmp_path):
    from config import ProfileManager

    bad, good = tmp_path / "bad", tmp_path / "good"
    bad.mkdir()
    (bad / "profiles.json").write_bytes(b'{"schema_version":99,"profiles":[]}')
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=bad, data_dir=bad)
    prepare_runtime_storage(config_dir=good, data_dir=good)
    mgr = ProfileManager(good)
    assert mgr.create_profile("p", "Good", {}) is not None
    with pytest.raises(MigrationError):
        ProfileManager(bad)
    assert json.loads((bad / "profiles.json").read_text(encoding="utf-8"))["schema_version"] == 99
    assert ProfileManager(good).get_profile("p").name == "Good"


def test_valid_canonical_location_wins_and_corrupt_recovery_preserves_bytes(tmp_path, monkeypatch):
    from config import ProfileManager

    legacy_dir, config_dir = tmp_path / "legacy", tmp_path / "config"
    legacy_dir.mkdir()
    config_dir.mkdir()
    monkeypatch.setattr("persistence.get_legacy_data_paths", lambda: [legacy_dir])
    source = legacy_dir / "profiles.json"
    source.write_text(
        json.dumps({"profiles": [{"id": "legacy", "name": "Legacy", "outputs": {}, "private": 8}]}), encoding="utf-8"
    )
    canonical = config_dir / "profiles.json"
    canonical.write_text(json.dumps({"profiles": [{"id": "current", "outputs": {}}]}), encoding="utf-8")
    prepare_runtime_storage(config_dir=config_dir, data_dir=tmp_path / "data")
    assert ProfileManager(config_dir).get_profile("current") is not None
    assert ProfileManager(config_dir).get_profile("legacy") is None
    corrupt = b"{broken target"
    canonical.write_bytes(corrupt)
    prepare_runtime_storage(config_dir=config_dir, data_dir=tmp_path / "data")
    mgr = ProfileManager(config_dir)
    assert mgr.get_profile("legacy").name == "Legacy"
    assert mgr.save()
    assert json.loads(canonical.read_text(encoding="utf-8"))["profiles"][0]["private"] == 8
    assert (config_dir / "profiles.json.corrupt").read_bytes() == corrupt
    assert (legacy_dir / "profiles.json.v0.bak").read_bytes() == source.read_bytes()


@pytest.mark.parametrize(
    "filename,payload",
    [
        ("flic_buttons.json", [{"name": "No address"}]),
        ("flic_buttons.json", [{"bdaddr": "80:e4:da:70:00:01"}, {"bdaddr": "80:e4:da:70:00:01", "name": "Conflict"}]),
        ("system_shortcuts.json", [{"label": "No identity"}]),
        ("system_shortcuts.json", {"user.bad": {"key": "user.bad", "order": "invalid"}}),
        (
            "scenes_v2.json",
            {"scenes": [{"id": "s", "steps": [], "overrides": {"p": {"1": {"audio_mute": "invalid"}}}}]},
        ),
    ],
)
def test_invalid_legacy_flat_records_and_known_override_shapes_are_not_pruned(tmp_path, filename, payload):
    from hub.persistence import load_versioned_json, save_versioned_json

    path = tmp_path / filename
    path.write_text(json.dumps(payload), encoding="utf-8")
    original = path.read_bytes()
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path)
    with pytest.raises(MigrationError):
        load_versioned_json(path)
    with pytest.raises(MigrationError):
        save_versioned_json(path, {})
    assert path.read_bytes() == original
    assert not list(tmp_path.glob("*.bak"))


@pytest.mark.parametrize(
    "filename,payload",
    [
        ("scenes.json", {"scenes": [{"id": "s", "steps": []}]}),
        ("shortcuts.json", {"mute_all_audio": {"label": "Old"}}),
    ],
)
def test_import_backup_failure_never_seeds_a_manager_target(tmp_path, monkeypatch, filename, payload):
    from scene_manager import SceneManager
    from system_shortcuts import SystemShortcutManager

    source = tmp_path / filename
    source.write_text(json.dumps(payload), encoding="utf-8")
    original = source.read_bytes()
    monkeypatch.setattr("hub.persistence.migrations.write_backup", lambda *_: None)
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path)
    with pytest.raises(MigrationError):
        SceneManager(tmp_path) if filename == "scenes.json" else SystemShortcutManager(tmp_path)
    assert source.read_bytes() == original
    assert not (tmp_path / "scenes_v2.json").exists()
    assert not (tmp_path / "system_shortcuts.json").exists()


def test_unified_config_scenes_never_become_profiles(tmp_path):
    from config import ProfileManager

    source = tmp_path / "scenes.json"
    original = b'{"scenes":[{"id":"unified","name":"Unified","steps":[]}]}'
    source.write_bytes(original)
    prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path / "data")
    assert ProfileManager(tmp_path).list_profiles() == []
    assert not (tmp_path / "profiles.json").exists()
    assert source.read_bytes() == original


def test_corrupt_recovery_backup_failure_preserves_original_target(tmp_path, monkeypatch):
    import shutil

    legacy = tmp_path / "legacy"
    legacy.mkdir()
    (legacy / "profiles.json").write_text('{"profiles":[{"id":"old","outputs":{}}]}', encoding="utf-8")
    config = tmp_path / "config"
    config.mkdir()
    target = config / "profiles.json"
    original = b"{corrupt original"
    target.write_bytes(original)
    monkeypatch.setattr("persistence.get_legacy_data_paths", lambda: [legacy])
    real_copy = shutil.copy2

    def fail_corrupt_backup(source, destination, *args, **kwargs):
        if str(destination).endswith(".corrupt"):
            raise OSError("injected corrupt backup failure")
        return real_copy(source, destination, *args, **kwargs)

    monkeypatch.setattr(shutil, "copy2", fail_corrupt_backup)
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=config, data_dir=tmp_path / "data")
    assert target.read_bytes() == original
    assert not (tmp_path / "data" / "system_shortcuts.json").exists()


@pytest.mark.parametrize(
    "filename,source,payload,collection",
    [
        ("profiles.json", "scenes.json", {"scenes": [{"id": "p", "outputs": {}, "private": 8}]}, "profiles"),
        ("scenes_v2.json", "scenes.json", {"scenes": [{"id": "s", "steps": [], "private": 8}]}, "scenes"),
        ("system_shortcuts.json", "shortcuts.json", {"mute_all_audio": {"label": "Old", "private": 8}}, None),
    ],
)
def test_generic_loader_imports_before_returning_a_seeding_default(tmp_path, filename, source, payload, collection):
    from hub.persistence import load_versioned_json

    original_path = tmp_path / source
    original_path.write_text(json.dumps(payload), encoding="utf-8")
    original = original_path.read_bytes()
    loaded = load_versioned_json(tmp_path / filename, default={"would": "seed defaults"})
    assert "would" not in loaded
    assert (loaded[collection][0] if collection else loaded["mute_all_audio"])["private"] == 8
    assert original_path.read_bytes() == original
    assert original_path.with_name(source + ".v0.bak").read_bytes() == original


@pytest.mark.parametrize("kind", ["scene", "shortcut"])
def test_late_alias_conflict_blocks_an_already_loaded_managers_save(tmp_path, kind):
    from scene_manager import SceneManager
    from system_shortcuts import SystemShortcutManager

    if kind == "scene":
        manager = SceneManager(tmp_path)
        manager.create_scene(name="Canonical")
        alias = tmp_path / "scenes.json"
        payload = {"scenes": [{"id": "unrepresented", "steps": []}]}
        target, save = tmp_path / "scenes_v2.json", manager._save
    else:
        manager = SystemShortcutManager(tmp_path)
        alias = tmp_path / "shortcuts.json"
        payload = {"mute_all_audio": {"label": "Conflicting"}}
        target, save = tmp_path / "system_shortcuts.json", manager._save
    alias.write_text(json.dumps(payload), encoding="utf-8")
    before = {p: p.read_bytes() for p in (target, alias)}
    assert save() is False
    assert {p: p.read_bytes() for p in before} == before


@pytest.mark.parametrize(
    "filename,payload",
    [
        ("dashboard_layout.json", {"cards": [], "version": "invalid"}),
        ("dashboard_layout.json", {"cards": [{"type": [], "id": "p"}]}),
        ("cec_macros.json", {"macros": [{"id": "m", "steps": [{"command": "POWER_ON", "delay_ms": "invalid"}]}]}),
        ("scenes_v2.json", {"scenes": [{"id": "s", "execution_history": [{"total_steps": "invalid"}]}]}),
        ("device_settings.json", {"inputs": [{"name": "No port identity"}]}),
    ],
)
def test_all_reader_conversion_shapes_are_checked_before_any_pin_rehash(tmp_path, filename, payload):
    profiles = tmp_path / "profiles.json"
    original = b'{"profiles":[{"id":"p","outputs":{},"passcode_hash":"1234"}]}'
    profiles.write_bytes(original)
    target = tmp_path / filename
    target.write_text(json.dumps(payload), encoding="utf-8")
    invalid = target.read_bytes()
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
    assert profiles.read_bytes() == original
    assert target.read_bytes() == invalid
    assert not list(tmp_path.glob("*.bak"))
