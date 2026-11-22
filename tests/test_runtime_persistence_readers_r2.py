"""Per-manager round-trip + barrier-gated write tests.

These tests prove the contract §4 promise that the runtime composition
root's barrier interacts with each legacy manager in three predictable
ways:

* on disk: every manager's :meth:`save` round-trips records and never
  drops unknown fields;
* on the public surface: API projections never expose ``passcode_hash``
  even when it is present on disk;
* under blockage: when :func:`hub.persistence.startup.prepare_runtime_storage`
  flags the relevant file unsafe, the manager's :meth:`save` returns
  ``False`` without touching the pre-barrier bytes.

The tests deliberately exercise real constructions of every manager
(``SceneManager``, ``ProfileManager``, ``MacroManager``,
``SystemShortcutManager``, ``DashboardLayoutManager``, the device
settings module) and assert against the on-disk bytes, not just the
in-memory representation.
"""

from __future__ import annotations

import json

import pytest

from cec_macros import MacroManager
from config import ProfileManager
from dashboard_layout import (
    CARD_PROFILE,
    DashboardLayoutManager,
)
from hub.persistence import (
    MigrationError,
    prepare_runtime_storage,
    reset_preparation,
)
from scene_manager import STEP_TYPE_PROFILE, SceneManager, SceneStep
from system_shortcuts import SystemShortcutManager

PIN = "1234"


@pytest.fixture(autouse=True)
def _reset_barrier_state():
    reset_preparation()
    yield
    reset_preparation()


# ===========================================================================
# SceneManager (Phase 8 unified scene manager)
# ===========================================================================


class TestSceneManagerRoundtrip:
    """scene_manager.SceneManager: scenes_v2.json + private/public separation."""

    def test_create_then_reload_keeps_scene_and_unknown_fields(self, tmp_path):
        mgr = SceneManager(data_dir=tmp_path)
        scene, err = mgr.create_scene(name="Demo", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")])
        assert err is None
        # add a field the dataclass doesn't know about, save it on the way through
        scene_dict = scene.to_dict(include_hash=True)
        scene_dict["operator_note"] = "preserved through save"
        scene_data_path = tmp_path / "scenes_v2.json"
        raw = json.loads(scene_data_path.read_text(encoding="utf-8"))
        raw["scenes"][0]["operator_note"] = "preserved through save"
        scene_data_path.write_text(json.dumps(raw), encoding="utf-8")

        reloaded = SceneManager(data_dir=tmp_path)
        assert reloaded.update_scene(scene.id, name="Edited")[1] is None
        assert SceneManager(data_dir=tmp_path).get_scene(scene.id).name == "Edited"
        payload = json.loads(scene_data_path.read_text(encoding="utf-8"))
        assert payload["scenes"][0]["operator_note"] == "preserved through save"

    def test_public_to_dict_never_exposes_passcode_hash(self, tmp_path):
        mgr = SceneManager(data_dir=tmp_path)
        scene, _ = mgr.create_scene(name="Locked", password_protected=True, passcode=PIN)
        assert scene.passcode_hash.startswith("pbkdf2_sha256$")
        public = scene.to_dict()
        assert "passcode_hash" not in public
        assert public["password_protected"] is True
        # Disk still has the hash.
        on_disk = json.loads((tmp_path / "scenes_v2.json").read_text(encoding="utf-8"))
        assert on_disk["scenes"][0]["passcode_hash"].startswith("pbkdf2_sha256$")

    def test_disk_and_public_projection_are_separated(self, tmp_path):
        """The same scene must produce:
        * a public representation (no hash, available to API clients)
        * a private disk representation (with hash + unknown fields)
        """
        mgr = SceneManager(data_dir=tmp_path)
        scene, _ = mgr.create_scene(name="Both")
        scene.passcode_hash = "pbkdf2_sha256$1000$AA$BB"
        public = scene.to_dict()
        private = scene.to_dict(include_hash=True)
        assert "passcode_hash" not in public
        assert private["passcode_hash"] == "pbkdf2_sha256$1000$AA$BB"


class TestSceneManagerWrites:
    """Save under barrier conditions: missing, blocked, restore."""

    def test_first_run_seeds_an_empty_scenes_v2(self, tmp_path):
        SceneManager(data_dir=tmp_path)
        assert (tmp_path / "scenes_v2.json").exists()
        payload = json.loads((tmp_path / "scenes_v2.json").read_text(encoding="utf-8"))
        assert payload["scenes"] == []

    def test_save_refused_after_barrier_blocks_writes(self, tmp_path):
        target = tmp_path / "scenes_v2.json"
        original = b"{corrupt pre-barrier bytes"
        target.write_bytes(original)
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        with pytest.raises(MigrationError):
            SceneManager(data_dir=tmp_path)
        assert target.read_bytes() == original


# ===========================================================================
# ProfileManager (config.ProfileManager)
# ===========================================================================


class TestProfileManagerRoundtrip:
    """ProfileManager: profiles.json + private/public separation."""

    def test_password_profile_keeps_its_hash_on_disk(self, tmp_path):
        from password import hash_passcode

        mgr = ProfileManager(config_dir=tmp_path)
        mgr.create_profile(
            "p1",
            "Locked",
            {1: {"input": 1}},
            password_protected=True,
            passcode_hash=hash_passcode(PIN),
        )
        payload = json.loads((tmp_path / "profiles.json").read_text(encoding="utf-8"))
        assert payload["profiles"][0]["passcode_hash"].startswith("pbkdf2_sha256$")
        # Public summary must NOT include the hash.
        assert "passcode_hash" not in mgr.list_profiles()[0]

    def test_unknown_profile_fields_round_trip(self, tmp_path):
        mgr = ProfileManager(config_dir=tmp_path)
        mgr.create_profile("p1", "Profile 1", {1: {"input": 1}})
        raw = json.loads((tmp_path / "profiles.json").read_text(encoding="utf-8"))
        raw["profiles"][0]["custom_field"] = "preserved"
        raw["profiles"][0]["nested_field"] = {"a": 1, "b": "two"}
        (tmp_path / "profiles.json").write_text(json.dumps(raw), encoding="utf-8")

        # Reload
        reloaded = ProfileManager(config_dir=tmp_path)
        reloaded.update_profile("p1", name="Edited")
        profile = ProfileManager(config_dir=tmp_path).get_profile("p1")
        # The profile object still parses. The disk payload keeps the unknown keys.
        on_disk = json.loads((tmp_path / "profiles.json").read_text(encoding="utf-8"))
        assert on_disk["profiles"][0]["custom_field"] == "preserved"
        assert on_disk["profiles"][0]["nested_field"] == {"a": 1, "b": "two"}
        assert profile is not None

    def test_save_refused_when_barrier_blocks_profiles(self, tmp_path):
        target = tmp_path / "profiles.json"
        original = b"{corrupt pre-barrier bytes"
        target.write_bytes(original)
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        with pytest.raises(MigrationError):
            ProfileManager(config_dir=tmp_path)
        assert target.read_bytes() == original


# ===========================================================================
# MacroManager
# ===========================================================================


class TestMacroManagerRoundtrip:
    """CEC macros: cec_macros.json + private/public separation."""

    def test_macro_with_steps_and_unknown_fields_round_trips(self, tmp_path):
        mgr = MacroManager(config_dir=tmp_path)
        mgr.create_macro(
            name="Power On TV",
            steps=[
                {"command": "POWER_ON", "targets": ["input_1"], "delay_ms": 0},
                {"command": "VOLUME_UP", "targets": ["output_1"], "delay_ms": 250},
            ],
            macro_id="m1",
        )
        raw = json.loads((tmp_path / "cec_macros.json").read_text(encoding="utf-8"))
        raw["macros"][0]["custom_marker"] = "preserved"
        (tmp_path / "cec_macros.json").write_text(json.dumps(raw), encoding="utf-8")

        reloaded = MacroManager(config_dir=tmp_path)
        macro = reloaded.get_macro("m1")
        assert macro is not None
        assert len(macro.steps) == 2
        assert macro.steps[0].command == "POWER_ON"
        assert macro.steps[1].delay_ms == 250
        on_disk = json.loads((tmp_path / "cec_macros.json").read_text(encoding="utf-8"))
        assert on_disk["macros"][0]["custom_marker"] == "preserved"

    def test_save_refused_when_barrier_blocks_macros(self, tmp_path):
        target = tmp_path / "cec_macros.json"
        original = b"{corrupt pre-barrier bytes"
        target.write_bytes(original)
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        with pytest.raises(MigrationError):
            MacroManager(config_dir=tmp_path)
        assert target.read_bytes() == original


# ===========================================================================
# SystemShortcutManager
# ===========================================================================


class TestSystemShortcutManagerRoundtrip:
    """system_shortcuts.json: built-in defaults + user prefs + alias import."""

    def test_manager_seeds_and_persists_built_in_defaults(self, tmp_path):
        mgr = SystemShortcutManager(data_dir=tmp_path)
        assert (tmp_path / "system_shortcuts.json").exists()
        keys = sorted(s.key for s in mgr.list_shortcuts())
        assert "route_all_to_output" in keys
        assert "system_reboot" in keys

    def test_user_prefs_persist_across_instances(self, tmp_path):
        mgr = SystemShortcutManager(data_dir=tmp_path)
        mgr.update_prefs("mute_all_audio", label="My Mute")
        # Reload
        reload = SystemShortcutManager(data_dir=tmp_path)
        assert reload.get("mute_all_audio").label == "My Mute"

    def test_unknown_top_level_keys_round_trip(self, tmp_path):
        # The system_shortcuts.json is a flat-map of prefs; the writer must preserve
        # unknown top-level entries rather than rewriting the file in a different shape.
        (tmp_path / "system_shortcuts.json").write_text(
            json.dumps(
                {
                    "mute_all_audio": {"label": "Mute", "icon": "🔇", "enabled": True, "order": 0},
                    "preset_custom_key": {"label": "Custom", "icon": "⚡", "enabled": True, "order": 99},
                }
            ),
            encoding="utf-8",
        )
        mgr = SystemShortcutManager(data_dir=tmp_path)
        assert mgr.get("mute_all_audio").label == "Mute"
        # The custom unknown-top-level key is preserved through load.
        payload = json.loads((tmp_path / "system_shortcuts.json").read_text(encoding="utf-8"))
        assert "preset_custom_key" in payload

    def test_save_refused_when_barrier_blocks_shortcuts(self, tmp_path):
        target = tmp_path / "system_shortcuts.json"
        original = b"{corrupt pre-barrier bytes"
        target.write_bytes(original)
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        with pytest.raises(MigrationError):
            SystemShortcutManager(data_dir=tmp_path)
        assert target.read_bytes() == original

    def test_flat_map_non_mapping_unknown_metadata_does_not_become_a_shortcut(self, tmp_path):
        """Sentinel/non-mapping top-level metadata survives edits without being
        interpreted as a shortcut or user-shortcut (the contract §4 line:
        "flat-map non-mapping unknown metadata survives without becoming a shortcut/button").
        """
        # A non-dict (string) top-level value is the harshest case: the legacy
        # readers would mistake it for a key/value entry.
        (tmp_path / "system_shortcuts.json").write_text(
            json.dumps(
                {
                    "mute_all_audio": {"label": "Mute", "icon": "🔇", "enabled": True, "order": 0},
                    "feature_flag_a": True,
                    "version_marker": "1.2.3",
                    "team_owner": "operator-Z",
                }
            ),
            encoding="utf-8",
        )
        mgr = SystemShortcutManager(data_dir=tmp_path)
        # No spurious shortcut / user-shortcut was created from those keys.
        assert all(
            key not in mgr._defaults and not key.startswith("user.")
            for key in ("feature_flag_a", "version_marker", "team_owner")
        )
        mgr.update_prefs("mute_all_audio", label="Mute renamed")
        # The non-default top-level metadata survives the rewrite.
        payload = json.loads((tmp_path / "system_shortcuts.json").read_text(encoding="utf-8"))
        assert payload.get("feature_flag_a") is True
        assert payload.get("version_marker") == "1.2.3"
        assert payload.get("team_owner") == "operator-Z"
        # And the actual prefs entry was updated.
        assert payload["mute_all_audio"]["label"] == "Mute renamed"


# ===========================================================================
# DashboardLayoutManager
# ===========================================================================


class TestDashboardLayoutManagerRoundtrip:
    """dashboard_layout.json: ordered cards, retired widget cards, unknown cards."""

    def test_drop_retired_widget_cards_preserves_user_cards(self, tmp_path):
        (tmp_path / "dashboard_layout.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "cards": [
                        {"type": "aggregate_widget", "id": "cec-tray", "order": 0},
                        {"type": "profile", "id": "movie_night", "order": 1},
                        {"type": "aggregate_widget", "id": "quick-actions", "order": 2},
                    ],
                }
            ),
            encoding="utf-8",
        )
        mgr = DashboardLayoutManager(data_dir=tmp_path)
        cards = mgr.list_cards()
        assert [(c.type, c.id) for c in cards] == [(CARD_PROFILE, "movie_night")]

    def test_replace_layout_preserves_unknown_card_types(self, tmp_path):
        """Cards with unknown types in a stored layout are silently skipped on read,
        and unknown top-level keys persist through save/edit."""
        (tmp_path / "dashboard_layout.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "cards": [{"type": CARD_PROFILE, "id": "p1", "order": 0}],
                    "extra_field": "preserved through save",
                }
            ),
            encoding="utf-8",
        )
        mgr = DashboardLayoutManager(data_dir=tmp_path)
        assert mgr.add_card(CARD_PROFILE, "p2")
        # The manager's save did not strip the extra field.
        payload = json.loads((tmp_path / "dashboard_layout.json").read_text(encoding="utf-8"))
        assert payload.get("extra_field") == "preserved through save"

    def test_save_refused_when_barrier_blocks_layout(self, tmp_path):
        target = tmp_path / "dashboard_layout.json"
        original = b"{corrupt pre-barrier bytes"
        target.write_bytes(original)
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        with pytest.raises(MigrationError):
            DashboardLayoutManager(data_dir=tmp_path)
        assert target.read_bytes() == original


# ===========================================================================
# device_settings (REST module)
# ===========================================================================


class TestDeviceSettingsReader:
    """rest_api.device_settings: device_settings.json, presets, favourites, paths."""

    @pytest.fixture
    def device_settings_module(self, monkeypatch):
        from rest_api import device_settings

        # Reset module-level state.
        device_settings._settings_path = None
        device_settings._settings_cache = {}
        yield device_settings

    def test_init_uses_configured_dir_and_loads_existing_settings(self, device_settings_module, monkeypatch, tmp_path):
        existing = tmp_path / "device_settings.json"
        existing.write_text(
            json.dumps(
                {
                    "version": 2,
                    "inputs": {"1": {"name": "Apple TV", "icon": None, "color": None}},
                    "outputs": {},
                    "favorite_presets": [1, 3],
                    "dashboard_presets": [2],
                    "presets": {"1": {"name": "Apple TV preset"}},
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        from persistence import reset_data_dir_cache

        reset_data_dir_cache()
        device_settings_module.init_device_settings()

        assert device_settings_module._settings_path == existing.resolve()
        settings = device_settings_module.get_device_settings()
        assert settings["inputs"]["1"]["name"] == "Apple TV"
        assert device_settings_module.get_favorite_presets() == [1, 3]

    def test_set_input_writes_and_invalidates_unknown_settings(self, device_settings_module, monkeypatch, tmp_path):
        existing = tmp_path / "device_settings.json"
        existing.write_text(
            json.dumps(
                {
                    "version": 2,
                    "inputs": {"1": {"name": "Apple TV", "icon": None, "color": None}},
                    "outputs": {},
                    "favorite_presets": [],
                    "dashboard_presets": [],
                    "presets": {"1": {"name": "P"}},
                    "future_extension": "preserved",
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        from persistence import reset_data_dir_cache

        reset_data_dir_cache()
        device_settings_module.init_device_settings()
        device_settings_module.set_input_setting(1, name="AppleTV4K")
        payload = json.loads(existing.read_text(encoding="utf-8"))
        assert payload["inputs"]["1"]["name"] == "AppleTV4K"
        # Unknown top-level keys are preserved.
        assert payload.get("future_extension") == "preserved"

    def test_save_refused_when_barrier_blocks_device_settings(self, monkeypatch, tmp_path):
        from rest_api import device_settings

        target = tmp_path / "device_settings.json"
        original = b"{corrupt pre-barrier bytes"
        target.write_bytes(original)
        with pytest.raises(MigrationError):
            prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        with pytest.raises(MigrationError):
            device_settings.init_device_settings(data_dir=tmp_path)
        assert target.read_bytes() == original


# ===========================================================================
# Barrier state integrity
# ===========================================================================


class TestBarrierManagerGateIdempotence:
    """Repeating the barrier over an already-prepared dir produces no further migrations
    (or no manager writes for the test scenario)."""

    def test_barrier_run_twice_writes_no_extra_files(self, tmp_path):
        target = tmp_path / "profiles.json"
        target.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "profiles": [{"id": "p", "name": "P", "pinned": True, "pin_order": 0}],
                }
            ),
            encoding="utf-8",
        )
        first = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        before_bytes = target.read_bytes()
        reset_preparation()
        # Second run.
        second = prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        # The file is unchanged.
        assert target.read_bytes() == before_bytes
        # Both prepared states record status=current.
        result = next(r for r in first.results if r.path == target)
        assert result.status == "current"
        result = next(r for r in second.results if r.path == target)
        assert result.status == "current"

    def test_unknown_record_metadata_in_flat_maps_passes_through(self, tmp_path):
        """CEC macros + device settings + dashboard layout: unknown scalars at the record
        level must persist through edit/save."""
        target = tmp_path / "cec_macros.json"
        target.write_text(
            json.dumps(
                {
                    "version": 2,
                    "macros": [
                        {
                            "id": "m1",
                            "name": "Starter",
                            "icon": "⚡",
                            "description": "",
                            "steps": [],
                            "created_at": "2026-10-18T00:00:00Z",
                            "updated_at": "2026-10-18T00:00:00Z",
                            "favorite": False,
                            "dashboard_visible": False,
                            "dashboard_order": 0,
                            "continue_on_error": False,
                            "team_owner": "operator-A",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        reset_preparation()
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        mgr = MacroManager(config_dir=tmp_path)
        mgr.update_macro("m1", name="Starter renamed")
        payload = json.loads(target.read_text(encoding="utf-8"))
        assert payload["macros"][0]["team_owner"] == "operator-A"
        assert payload["macros"][0]["name"] == "Starter renamed"


# ===========================================================================
# Private-disk vs public-API separation / lossless rehash preservation
# ===========================================================================


class TestLosslessPrivateDiskVsPublicAPI:
    """Concrete negative + restart cases the coordinator asked for as acceptance evidence.

    Every test in this class loads a file with operator / forward-compat
    metadata + a plaintext PIN, runs the barrier + the manager's save path
    (which hashes the PIN), then re-reads the file and asserts the
    on-disk bytes preserved *both* sets of unknown metadata and the new
    PBKDF2 hash, while the public projection the manager returns does
    not include the hash. Restarting the manager reloads the file and
    verifies the metadata survives a second rehash round.
    """

    def test_profile_unknown_top_level_and_item_fields_survive_rehash(self, tmp_path):

        target = tmp_path / "profiles.json"
        target.write_text(
            json.dumps(
                {
                    "version": 2,
                    "future_top": 42,  # unknown top-level
                    "schema_version": 2,
                    "profiles": [
                        {
                            "id": "p1",
                            "name": "Locked",
                            "icon": "📺",
                            "outputs": {"1": {"input": 1, "enabled": True, "audio_mute": False}},
                            "macros": [],
                            "pinned": True,
                            "pin_order": 0,
                            "favorite": False,
                            "dashboard_visible": False,
                            "dashboard_order": 0,
                            "password_protected": True,
                            "passcode_hash": "1234",  # plaintext PIN (F-SEC-004)
                            "execution_log": [],
                            "future_item": {"v": 3},  # unknown record-level
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        reset_preparation()
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        mgr = ProfileManager(config_dir=tmp_path)

        # The PIN rehashed in memory and the file was rewritten
        # on load (F-SEC-004). Both sets of unknowns must survive.
        on_disk = json.loads(target.read_text(encoding="utf-8"))
        assert on_disk.get("future_top") == 42, "unknown top-level dropped"
        profile = on_disk["profiles"][0]
        assert profile.get("future_item") == {"v": 3}, "unknown record-level dropped"
        assert profile["passcode_hash"].startswith("pbkdf2_sha256$")
        assert profile["passcode_hash"] != "1234"

        # Public summary never exposes the hash.
        public = mgr.list_profiles()[0]
        assert "passcode_hash" not in public
        assert public["password_protected"] is True

        # Restart idempotence: a fresh manager must still see the same
        # preserved unknowns and still verify the PIN.
        reset_preparation()
        mgr2 = ProfileManager(config_dir=tmp_path)
        on_disk2 = json.loads(target.read_text(encoding="utf-8"))
        assert on_disk2.get("future_top") == 42
        assert on_disk2["profiles"][0].get("future_item") == {"v": 3}
        # The new manager sees the hashed PIN and verifies it.
        assert mgr2.get_profile("p1") is not None
        assert mgr2.get_profile("p1").passcode_hash.startswith("pbkdf2_sha256$")

    def test_scene_unknown_top_level_and_item_fields_survive_rehash(self, tmp_path):
        target = tmp_path / "scenes_v2.json"
        target.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "version": 2,
                    "team_owner": "operator-X",  # unknown top-level
                    "scenes": [
                        {
                            "id": "s1",
                            "name": "Locked",
                            "icon": "🎬",
                            "steps": [{"type": "macro", "id": "m1"}],
                            "overrides": {},
                            "favorite": False,
                            "dashboard_visible": False,
                            "dashboard_order": 0,
                            "password_protected": True,
                            "passcode_hash": "4321",  # plaintext PIN (F-SEC-004)
                            "last_executed": None,
                            "execution_history": [],
                            "future_item": {"v": 1},  # unknown record-level
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        reset_preparation()
        prepare_runtime_storage(config_dir=tmp_path, data_dir=tmp_path)
        mgr = SceneManager(data_dir=tmp_path)

        on_disk = json.loads(target.read_text(encoding="utf-8"))
        assert on_disk.get("team_owner") == "operator-X", "unknown top-level dropped"
        assert on_disk.get("version") == 2, "legacy 'version' file-format marker lost"
        scene = on_disk["scenes"][0]
        assert scene.get("future_item") == {"v": 1}, "unknown record-level dropped"
        assert scene["passcode_hash"].startswith("pbkdf2_sha256$")
        assert scene["passcode_hash"] != "4321"

        # Public projection must not carry the hash.
        public = mgr.get_scene("s1").to_dict()
        assert "passcode_hash" not in public
        assert public["password_protected"] is True

        # Restart idempotence.
        reset_preparation()
        SceneManager(data_dir=tmp_path)
        on_disk2 = json.loads(target.read_text(encoding="utf-8"))
        assert on_disk2.get("team_owner") == "operator-X"
        assert on_disk2["scenes"][0].get("future_item") == {"v": 1}
        assert on_disk2["scenes"][0]["passcode_hash"].startswith("pbkdf2_sha256$")


# ===========================================================================
# Legacy fallback: original-byte recovery + lossless canonical storage
# ===========================================================================


class TestLegacySceneFallbackBytewiseImport:
    """Without the runtime barrier, the manager's fallback import must
    *bytewise* preserve the legacy ``scenes.json`` (raw backup before
    stamping the canonical target) and reject the legacy config.Scene
    shape (outputs-only, no steps)."""

    def test_unified_legacy_scene_import_writes_lossless_canonical_target(self, tmp_path):
        legacy = tmp_path / "scenes.json"
        original_bytes = (
            json.dumps(
                {
                    "version": 2,
                    "schema_version": 1,
                    "scenes": [
                        {
                            "id": "scene_demo",
                            "name": "Imported",
                            "icon": "🎬",
                            "steps": [{"type": "profile", "id": "p1"}],
                            "overrides": {},
                            "favorite": False,
                            "dashboard_visible": False,
                            "dashboard_order": 0,
                            "password_protected": False,
                            "passcode_hash": "",
                            "last_executed": None,
                            "execution_history": [],
                            "operator_note": "preserved by import",
                        }
                    ],
                    "team_owner": "operator-Y",
                }
            )
        ).encode("utf-8")
        legacy.write_bytes(original_bytes)

        SceneManager(data_dir=tmp_path)

        # The canonical target exists and carries every unknown top-level key.
        canonical = json.loads((tmp_path / "scenes_v2.json").read_text(encoding="utf-8"))
        assert canonical.get("version") == 2, "legacy version marker dropped"
        assert canonical.get("team_owner") == "operator-Y", "unknown top-level dropped"
        scene = canonical["scenes"][0]
        assert scene.get("operator_note") == "preserved by import", "unknown record-level dropped"

        # The original legacy file is recovered byte-for-byte in the backup.
        backup = (tmp_path / "scenes.json.v1.bak").read_bytes()
        assert backup == original_bytes, "backup must be a byte-for-byte copy of the original"

        # The legacy file itself is preserved too.
        assert legacy.read_bytes() == original_bytes

    def test_legacy_config_scene_shape_is_not_imported(self, tmp_path):
        """``config.SceneManager`` records have ``outputs`` instead of ``steps``;
        the unified scene manager's fallback must NOT import them — doing so
        would rewrite the operator's data into a shape R4 owns.
        """
        legacy = tmp_path / "scenes.json"
        legacy.write_text(
            json.dumps(
                {
                    "version": 2,
                    "scenes": [
                        {
                            "id": "legacy_scene",
                            "name": "Legacy config.Scene",
                            "outputs": {"1": {"input": 1, "enabled": True, "audio_mute": False}},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        SceneManager(data_dir=tmp_path)
        # The manager initialises empty; the legacy file is untouched and a
        # bytewise backup is *not* taken (we never wrote to scenes_v2.json).
        assert not (tmp_path / "scenes_v2.json").exists()
        # The original legacy file is still on disk for the runtime barrier
        # to detect / for the operator to recover.
        assert "outputs" in legacy.read_text(encoding="utf-8")
        assert not (tmp_path / "scenes.json.v0.bak").exists()


@pytest.mark.parametrize("kind", ["profile", "scene", "macro", "shortcut", "layout", "settings"])
def test_actual_edit_save_restart_preserves_private_extensions(tmp_path, kind):
    """Exercise actual manager writes, with disjoint config/data paths."""
    from hub.runtime.managers import create_managers
    from password import verify_passcode
    from rest_api import device_settings

    config_dir, data_dir = tmp_path / "config", tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    private = {"credentials": {"password": "private-extension"}, "operator_note": "retain"}
    fixtures = {
        config_dir / "profiles.json": {
            "profiles": [
                {
                    "id": "p",
                    "name": "Before",
                    "outputs": {"1": {"input": 2, "hdr_mode": 3, **private}},
                    "passcode_hash": PIN,
                    "password_protected": True,
                    **private,
                }
            ],
            **private,
        },
        config_dir / "cec_macros.json": {
            "macros": [
                {
                    "id": "m",
                    "name": "Before",
                    "steps": [{"command": "POWER_ON", "targets": ["output:1"], **private}],
                    **private,
                }
            ],
            **private,
        },
        data_dir / "scenes_v2.json": {
            "scenes": [
                {
                    "id": "s",
                    "name": "Before",
                    "steps": [{"type": "profile", "id": "p", **private}],
                    "passcode_hash": PIN,
                    "password_protected": True,
                    **private,
                }
            ],
            **private,
        },
        data_dir / "system_shortcuts.json": {
            "mute_all_audio": {"label": "Before", **private},
            "extension_scalar": 17,
            "extension_object": private,
        },
        data_dir / "dashboard_layout.json": {
            "cards": [{"type": "profile", "id": "p", "order": 0, **private}],
            **private,
        },
        data_dir / "device_settings.json": {"inputs": {"1": {"name": "Before", **private}}, **private},
    }
    for path, raw in fixtures.items():
        path.write_text(json.dumps(raw), encoding="utf-8")
    prepared = prepare_runtime_storage(config_dir=config_dir, data_dir=data_dir)
    managers = create_managers(prepared)
    device_settings.init_device_settings(data_dir)
    if kind == "profile":
        assert managers.profiles.update_profile("p", name="After") is not None
        assert verify_passcode(PIN, managers.profiles.get_profile("p").passcode_hash)
        public = managers.profiles.get_profile("p").to_dict()
        path, collection = config_dir / "profiles.json", "profiles"
    elif kind == "scene":
        assert managers.scenes.update_scene("s", name="After")[1] is None
        assert verify_passcode(PIN, managers.scenes.get_scene("s").passcode_hash)
        public = managers.scenes.get_scene("s").to_dict()
        path, collection = data_dir / "scenes_v2.json", "scenes"
    elif kind == "macro":
        assert managers.macros.update_macro("m", name="After") is not None
        public = managers.macros.get_macro("m").to_dict()
        path, collection = config_dir / "cec_macros.json", "macros"
    elif kind == "shortcut":
        assert managers.shortcuts.update_prefs("mute_all_audio", label="After") is not None
        public = managers.shortcuts.get("mute_all_audio").to_dict()
        path, collection = data_dir / "system_shortcuts.json", None
    elif kind == "layout":
        assert managers.dashboard.add_card(CARD_PROFILE, "p2")
        public = managers.dashboard.get_layout().to_dict()
        path, collection = data_dir / "dashboard_layout.json", "cards"
    else:
        assert device_settings.set_input_setting(1, name="After")
        public = device_settings.get_device_settings()
        path, collection = data_dir / "device_settings.json", None
    encoded = json.dumps(public)
    assert "private-extension" not in encoded
    assert "operator_note" not in encoded
    assert "passcode_hash" not in encoded
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["schema_version"] == 2
    if collection:
        assert raw["operator_note"] == "retain"
        assert raw[collection][0]["credentials"] == private["credentials"]
    elif kind == "shortcut":
        assert raw["extension_scalar"] == 17
        assert raw["mute_all_audio"]["operator_note"] == "retain"
        assert not any(s.key.startswith("extension") for s in managers.shortcuts.list_shortcuts())
    else:
        assert raw["credentials"] == private["credentials"]
        assert raw["inputs"]["1"]["operator_note"] == "retain"
    before_restart = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.rglob("*.json")}
    create_managers(prepare_runtime_storage(config_dir=config_dir, data_dir=data_dir))
    device_settings.init_device_settings(data_dir)
    assert before_restart == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.rglob("*.json")}


def test_profile_optional_clears_and_deletion_do_not_resurrect_old_fields(tmp_path):
    target = tmp_path / "profiles.json"
    target.write_text(
        json.dumps(
            {
                "profiles": [
                    {
                        "id": "keep",
                        "name": "Keep",
                        "outputs": {"1": {"input": 1, "hdr_mode": 3, "private": 4}},
                        "cec_config": {"nav_targets": ["input:1"], "private": 5},
                        "power_on_macro": "m",
                        "private": 6,
                    },
                    {"id": "delete", "outputs": {}, "private": 7},
                ]
            }
        ),
        encoding="utf-8",
    )
    mgr = ProfileManager(tmp_path)
    profile = mgr.get_profile("keep")
    profile.cec_config = None
    profile.power_on_macro = None
    profile.outputs[1].hdr_mode = None
    assert mgr.delete_profile("delete")
    assert mgr.save()
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert [r["id"] for r in raw["profiles"]] == ["keep"]
    kept = raw["profiles"][0]
    assert "cec_config" not in kept and "power_on_macro" not in kept
    assert "hdr_mode" not in kept["outputs"]["1"]
    assert kept["private"] == 6 and kept["outputs"]["1"]["private"] == 4
    reloaded = ProfileManager(tmp_path).get_profile("keep")
    assert reloaded.cec_config is None and reloaded.power_on_macro is None


def test_step_deletion_reorder_does_not_move_private_fields_between_records(tmp_path):
    from scene_manager import SceneStep

    target = tmp_path / "scenes_v2.json"
    target.write_text(
        json.dumps(
            {
                "scenes": [
                    {
                        "id": "s",
                        "steps": [
                            {"type": "profile", "id": "a", "private": "A"},
                            {"type": "profile", "id": "b", "private": "B"},
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    mgr = SceneManager(tmp_path)
    mgr.get_scene("s").steps = [SceneStep("profile", "b"), SceneStep("profile", "c")]
    assert mgr._save()
    steps = json.loads(target.read_text(encoding="utf-8"))["scenes"][0]["steps"]
    assert steps[0]["private"] == "B"
    assert "private" not in steps[1]
    assert [step.id for step in SceneManager(tmp_path).get_scene("s").steps] == ["b", "c"]


@pytest.mark.parametrize("shape", ["profile", "scene", "macro", "shortcut", "layout", "settings"])
@pytest.mark.parametrize("bad", ["corrupt", "future", "invalid"])
def test_standalone_readers_refuse_unsafe_input_without_barrier(tmp_path, shape, bad):
    from rest_api import device_settings

    table = {
        "profile": ("profiles.json", {"profiles": "invalid"}, lambda: ProfileManager(tmp_path)),
        "scene": ("scenes_v2.json", {"scenes": "invalid"}, lambda: SceneManager(tmp_path)),
        "macro": ("cec_macros.json", {"macros": "invalid"}, lambda: MacroManager(tmp_path)),
        "shortcut": ("system_shortcuts.json", {"user.bad": 9}, lambda: SystemShortcutManager(tmp_path)),
        "layout": ("dashboard_layout.json", {"cards": "invalid"}, lambda: DashboardLayoutManager(tmp_path)),
        "settings": (
            "device_settings.json",
            {"inputs": "invalid"},
            lambda: device_settings.init_device_settings(tmp_path),
        ),
    }
    filename, invalid, construct = table[shape]
    target = tmp_path / filename
    original = (
        b"{bad" if bad == "corrupt" else json.dumps({"schema_version": 99} if bad == "future" else invalid).encode()
    )
    target.write_bytes(original)
    with pytest.raises(MigrationError):
        construct()
    assert target.read_bytes() == original
    assert not list(tmp_path.glob("*.bak"))


@pytest.mark.parametrize("shape", ["profile", "scene", "macro", "shortcut", "layout", "settings"])
def test_already_loaded_manager_cannot_overwrite_replaced_future_file(tmp_path, shape):
    from rest_api import device_settings

    if shape == "profile":
        mgr = ProfileManager(tmp_path)
        target, save = tmp_path / "profiles.json", mgr.save
    elif shape == "scene":
        mgr = SceneManager(tmp_path)
        target, save = tmp_path / "scenes_v2.json", mgr._save
    elif shape == "macro":
        mgr = MacroManager(tmp_path)
        target, save = tmp_path / "cec_macros.json", mgr.save
    elif shape == "shortcut":
        mgr = SystemShortcutManager(tmp_path)
        target, save = tmp_path / "system_shortcuts.json", mgr._save
    elif shape == "layout":
        mgr = DashboardLayoutManager(tmp_path)
        target, save = tmp_path / "dashboard_layout.json", mgr._save
    else:
        device_settings.init_device_settings(tmp_path)
        target, save = tmp_path / "device_settings.json", device_settings._save_settings
    original = b'{"schema_version": 99, "private": "original"}'
    target.write_bytes(original)
    assert save() is False
    assert target.read_bytes() == original


def test_legacy_plaintext_scene_import_rehashes_privately_and_restarts(tmp_path):
    from password import verify_passcode

    legacy = tmp_path / "scenes.json"
    original = b'{ "scenes": [{"id":"old", "name":"Old", "steps":[], "passcode_hash":"1234", "password_protected":true, "credentials":{"password":"keep"}}], "private": 9 }'
    legacy.write_bytes(original)
    prepared = prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path)
    mgr = SceneManager(prepared.paths.data_dir)
    assert verify_passcode(PIN, mgr.get_scene("old").passcode_hash)
    assert mgr.update_scene("old", name="Edited")[1] is None
    assert "credentials" not in mgr.get_scene("old").to_dict()
    canonical = tmp_path / "scenes_v2.json"
    raw = json.loads(canonical.read_text(encoding="utf-8"))
    assert raw["scenes"][0]["credentials"] == {"password": "keep"}
    assert legacy.read_bytes() == original
    assert (tmp_path / "scenes.json.v0.bak").read_bytes() == original
    before = (canonical.read_bytes(), canonical.stat().st_mtime_ns)
    prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path)
    assert SceneManager(tmp_path).get_scene("old").name == "Edited"
    assert (canonical.read_bytes(), canonical.stat().st_mtime_ns) == before


def test_shortcut_alias_edit_delete_and_restart_keep_source_and_metadata(tmp_path):
    alias = tmp_path / "shortcuts.json"
    original = json.dumps(
        {
            "user.custom": {"key": "user.custom", "label": "Custom", "private": 5},
            "mute_all_audio": {"label": "Old", "private": 6},
            "extension": 7,
        }
    ).encode()
    alias.write_bytes(original)
    mgr = SystemShortcutManager(tmp_path)
    assert mgr.update_prefs("mute_all_audio", label="Edited") is not None
    assert mgr.delete("user.custom")
    before = (tmp_path / "system_shortcuts.json").read_bytes()
    prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path)
    restarted = SystemShortcutManager(tmp_path)
    assert restarted.get("mute_all_audio").label == "Edited"
    assert restarted.get("user.custom") is None
    assert (tmp_path / "system_shortcuts.json").read_bytes() == before
    assert alias.read_bytes() == original
    assert (tmp_path / "shortcuts.json.v0.bak").read_bytes() == original
    assert json.loads(before)["mute_all_audio"]["private"] == 6


def test_override_extensions_stay_private_and_known_clear_survives_restart(tmp_path):
    target = tmp_path / "scenes_v2.json"
    target.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "scenes": [
                    {
                        "id": "s",
                        "name": "Before",
                        "steps": [],
                        "overrides": {
                            "p": {"1": {"audio_mute": True, "credentials": {"password": "synthetic-private"}}}
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path)
    mgr = SceneManager(tmp_path)
    scene = mgr.get_scene("s")
    assert scene.get_overrides_for_profile("p") == {1: {"audio_mute": True}}
    assert scene.to_dict()["overrides"] == {"p": {"1": {"audio_mute": True}}}
    assert mgr.update_scene("s", name="Edited")[1] is None
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert raw["scenes"][0]["overrides"]["p"]["1"]["credentials"] == {"password": "synthetic-private"}
    assert mgr.clear_override("s", "p", 1, "audio_mute")[1] is None
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert raw["scenes"][0]["overrides"]["p"]["1"] == {"credentials": {"password": "synthetic-private"}}
    restarted = SceneManager(tmp_path).get_scene("s")
    assert restarted.get_overrides_for_profile("p") == {}
    assert restarted.to_dict()["overrides"] == {}
    assert "synthetic-private" not in json.dumps(restarted.to_dict())
    assert "passcode_hash" not in restarted.to_dict()


async def test_real_composition_reads_old_catalogs_privately_and_restarts_without_churn(tmp_path, monkeypatch):
    """Real R1 composition, real managers/REST and simulator; no migration substitute."""
    import socket
    from dataclasses import asdict

    import aiohttp

    import run
    from hub.runtime.composition import build_runtime
    from tools.simulator import DeviceState, Simulator

    config_dir, data_dir = tmp_path / "config", tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    private = {"credentials": {"password": "synthetic-private"}}
    catalogs = {
        config_dir / "profiles.json": {
            "profiles": [
                {
                    "id": "p",
                    "name": "Profile old",
                    "outputs": {},
                    "password_protected": True,
                    "passcode_hash": PIN,
                    **private,
                }
            ],
            **private,
        },
        config_dir / "cec_macros.json": {
            "macros": [{"id": "m", "name": "Macro old", "steps": [], **private}],
            **private,
        },
        data_dir / "scenes.json": {
            "scenes": [
                {
                    "id": "s",
                    "name": "Scene old",
                    "steps": [],
                    "password_protected": True,
                    "passcode_hash": PIN,
                    **private,
                }
            ],
            **private,
        },
        data_dir / "shortcuts.json": {"mute_all_audio": {"label": "Muted old", **private}, "extension_scalar": 9},
        data_dir / "dashboard_layout.json": {"cards": [{"type": "profile", "id": "p", **private}], **private},
        data_dir / "device_settings.json": {"inputs": {"1": {"name": "Input old", **private}}, **private},
        data_dir / "flic_buttons.json": {"80:e4:da:70:00:01": {"name": "Button old"}, "extension_scalar": 11},
    }
    for path, payload in catalogs.items():
        path.write_text(json.dumps(payload), encoding="utf-8")
    originals = {path: path.read_bytes() for path in catalogs}
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        api_port = sock.getsockname()[1]
    async with Simulator(DeviceState.default(), https_port=0, telnet_port=0, control_port=0) as simulator:
        env = {
            "DATA_DIR": str(data_dir),
            "UC_CONFIG_HOME": str(config_dir),
            "MATRIX_HOST": "127.0.0.1",
            "MATRIX_PORT": str(simulator.https_port),
            "API_PORT": str(api_port),
            "UC_ENABLED": "false",
            "FLIC_ENABLED": "false",
            "HA_DISCOVERY_ENABLED": "false",
            "STATUS_POLL_INTERVAL": "60",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        monkeypatch.setenv("OREI_VERIFY_SSL", "false")
        monkeypatch.setenv("OREI_TELNET_PORT", str(simulator.telnet_port))
        monkeypatch.delenv("MATRIX_CA_CERT", raising=False)
        monkeypatch.delenv("MATRIX_TLS_FINGERPRINT", raising=False)
        stable = None
        for _ in range(2):
            runtime = build_runtime(run.load_settings(env), environ=env)
            try:
                await runtime.start()
                async with aiohttp.ClientSession() as client:
                    for route, expected in {
                        "/api/profiles": "Profile old",
                        "/api/v2/scenes": "Scene old",
                        "/api/cec/macros": "Macro old",
                        "/api/system-shortcuts": "Muted old",
                        "/api/dashboard/layout": "profile",
                        "/api/device-settings": "Input old",
                    }.items():
                        async with client.get(f"http://127.0.0.1:{api_port}{route}") as response:
                            assert response.status == 200
                            text = await response.text()
                            assert expected in text
                            assert "synthetic-private" not in text and "passcode_hash" not in text
                snapshot = json.dumps(asdict(runtime.snapshot()))
                assert "synthetic-private" not in snapshot and "passcode_hash" not in snapshot
            finally:
                await runtime.stop()
            # R0 excludes security/theme/UI files from catalog migration.
            targets = [*catalogs, data_dir / "scenes_v2.json", data_dir / "system_shortcuts.json"]
            now = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in targets}
            if stable is not None:
                assert now == stable
            stable = now
    assert (data_dir / "scenes.json").read_bytes() == originals[data_dir / "scenes.json"]
    assert (data_dir / "shortcuts.json").read_bytes() == originals[data_dir / "shortcuts.json"]
    for path, original in originals.items():
        assert path.with_name(path.name + ".v0.bak").read_bytes() == original
