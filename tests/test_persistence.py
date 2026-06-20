"""
Tests for the persistence module and init functions in themes/ui/device_settings.

Verifies:
- ``MATRIX_DATA_DIR`` env var takes priority over ``UC_CONFIG_HOME``
- ``UC_CONFIG_HOME`` is honored as a fallback (backward compat)
- ``<project_root>/data`` is the local development default
- Legacy files at the old hardcoded ``data/`` path are migrated transparently
- The new init functions (``init_themes``, ``init_ui_preferences``) and the
  existing ``init_device_settings`` all resolve to the same configured dir
- The ``/api/system/storage`` endpoint returns the resolved layout
"""

import importlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


PROJECT_ROOT = Path(__file__).parent.parent
LEGACY_DATA_DIR = PROJECT_ROOT / "data"


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch, tmp_path):
    """Snapshot env vars and clear persistence cache around every test."""
    # Clear the three persistence-controlling env vars
    for var in ("MATRIX_DATA_DIR", "UC_CONFIG_HOME", "HOME"):
        monkeypatch.delenv(var, raising=False)

    # Reset the module-level caches so each test resolves fresh
    from persistence import reset_data_dir_cache
    reset_data_dir_cache()

    yield

    reset_data_dir_cache()


# =============================================================================
# get_data_dir resolution
# =============================================================================


class TestGetDataDir:
    """``persistence.get_data_dir`` resolution priority."""

    def test_returns_project_data_when_no_env_vars(self, monkeypatch):
        """No env vars set → fall back to <project_root>/data."""
        from persistence import get_data_dir, get_project_root

        result = get_data_dir()
        assert result == (get_project_root() / "data").resolve()

    def test_matrix_data_dir_takes_priority(self, monkeypatch, tmp_path):
        """``MATRIX_DATA_DIR`` env var wins when set."""
        target = tmp_path / "explicit-data"
        monkeypatch.setenv("MATRIX_DATA_DIR", str(target))

        from persistence import get_data_dir

        assert get_data_dir() == target.resolve()

    def test_uc_config_home_used_when_matrix_data_dir_unset(self, monkeypatch, tmp_path):
        """``UC_CONFIG_HOME`` is honored as the next-priority signal."""
        monkeypatch.setenv("UC_CONFIG_HOME", str(tmp_path))

        from persistence import get_data_dir

        result = get_data_dir()
        # data_dir = $UC_CONFIG_HOME/data
        assert result == (tmp_path / "data").resolve()

    def test_matrix_data_dir_overrides_uc_config_home(self, monkeypatch, tmp_path):
        """``MATRIX_DATA_DIR`` wins over ``UC_CONFIG_HOME`` when both are set."""
        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path / "preferred"))
        monkeypatch.setenv("UC_CONFIG_HOME", str(tmp_path / "ignored"))

        from persistence import get_data_dir

        assert get_data_dir() == (tmp_path / "preferred").resolve()

    def test_result_is_cached_until_reset(self, monkeypatch, tmp_path):
        """Second call returns the same Path object (cached)."""
        target = tmp_path / "cached-data"
        monkeypatch.setenv("MATRIX_DATA_DIR", str(target))

        from persistence import get_data_dir, reset_data_dir_cache

        first = get_data_dir()
        second = get_data_dir()
        assert first == second
        assert first is second  # identical object (cached)

        # After resetting, a new env var takes effect
        new_target = tmp_path / "after-reset"
        monkeypatch.setenv("MATRIX_DATA_DIR", str(new_target))
        reset_data_dir_cache()
        assert get_data_dir() == new_target.resolve()


# =============================================================================
# get_config_dir resolution
# =============================================================================


class TestGetConfigDir:
    """``persistence.get_config_dir`` resolution."""

    def test_uc_config_home_used(self, monkeypatch, tmp_path):
        """``UC_CONFIG_HOME`` is the primary signal."""
        monkeypatch.setenv("UC_CONFIG_HOME", str(tmp_path))

        from persistence import get_config_dir

        assert get_config_dir() == tmp_path.resolve()

    def test_home_used_when_uc_config_home_unset(self, monkeypatch, tmp_path):
        """``$HOME`` is the fallback when UC_CONFIG_HOME is unset."""
        monkeypatch.setenv("HOME", str(tmp_path))

        from persistence import get_config_dir

        assert get_config_dir() == (tmp_path / "config").resolve()

    def test_relative_fallback_when_no_env(self, monkeypatch):
        """Falls back to ``./config`` when neither env var is set."""
        # We're running with HOME cleared in the autouse fixture
        from persistence import get_config_dir

        result = get_config_dir()
        # Resolved absolute path; we just check it ends with /config
        assert result.name == "config"


# =============================================================================
# Legacy migration
# =============================================================================


class TestLegacyMigration:
    """``migrate_legacy_file`` copies legacy data to the new location."""

    def test_migrates_existing_legacy_file(self, monkeypatch, tmp_path):
        """If legacy file exists and target doesn't, copy it over."""
        from persistence import get_data_dir, migrate_legacy_file

        # Pre-populate the legacy location
        LEGACY_DATA_DIR.mkdir(parents=True, exist_ok=True)
        legacy_file = LEGACY_DATA_DIR / "test-legacy-file.json"
        legacy_file.write_text('{"legacy": true}', encoding="utf-8")

        try:
            # Point resolution at tmp_path
            monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
            new_target = tmp_path / "test-legacy-file.json"

            migrated = migrate_legacy_file(new_target, "test-legacy-file.json")

            assert migrated is True
            assert new_target.exists()
            assert json.loads(new_target.read_text(encoding="utf-8")) == {"legacy": True}
        finally:
            legacy_file.unlink(missing_ok=True)

    def test_no_op_when_target_exists(self, monkeypatch, tmp_path):
        """If target already exists, skip migration."""
        from persistence import migrate_legacy_file

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        target = tmp_path / "already-here.json"
        target.write_text('{"new": true}', encoding="utf-8")

        result = migrate_legacy_file(target, "already-here.json")
        assert result is False
        assert json.loads(target.read_text(encoding="utf-8")) == {"new": True}

    def test_no_op_when_legacy_absent(self, monkeypatch, tmp_path):
        """If neither target nor legacy exists, no-op."""
        from persistence import migrate_legacy_file

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        target = tmp_path / "doesnt-exist.json"

        result = migrate_legacy_file(target, "doesnt-exist.json")
        assert result is False
        assert not target.exists()


# =============================================================================
# describe_storage_layout
# =============================================================================


class TestDescribeStorageLayout:
    """``describe_storage_layout`` returns the resolved paths."""

    def test_returns_all_keys(self, monkeypatch, tmp_path):
        from persistence import describe_storage_layout

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        layout = describe_storage_layout()

        assert "data_dir" in layout
        assert "config_dir" in layout
        assert "matrix_data_dir_env" in layout
        assert "uc_config_home_env" in layout
        assert layout["matrix_data_dir_env"] == str(tmp_path)


# =============================================================================
# init_themes / init_ui_preferences / init_device_settings
# =============================================================================


class TestInitFunctions:
    """The three init functions all honor the configured data_dir."""

    def test_init_themes_uses_configured_dir(self, monkeypatch, tmp_path):
        from rest_api import themes

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        themes.init_themes()

        assert themes._theme_path == (tmp_path / "themes.json").resolve()
        assert themes._theme_path.parent.exists()

    def test_init_ui_preferences_uses_configured_dir(self, monkeypatch, tmp_path):
        from rest_api import ui

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        ui.init_ui_preferences()

        assert ui._ui_prefs_path == (tmp_path / "ui_preferences.json").resolve()
        assert ui._ui_prefs_path.parent.exists()

    def test_init_device_settings_uses_configured_dir(self, monkeypatch, tmp_path):
        from rest_api import device_settings

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        device_settings.init_device_settings()

        assert device_settings._settings_path == (tmp_path / "device_settings.json").resolve()
        assert device_settings._settings_path.parent.exists()

    def test_all_three_init_to_same_dir(self, monkeypatch, tmp_path):
        """All three storage modules share the resolved data_dir."""
        from rest_api import device_settings, themes, ui

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        themes.init_themes()
        ui.init_ui_preferences()
        device_settings.init_device_settings()

        assert themes._theme_path.parent == tmp_path.resolve()
        assert ui._ui_prefs_path.parent == tmp_path.resolve()
        assert device_settings._settings_path.parent == tmp_path.resolve()


class TestLegacyMigrationOnInit:
    """Init functions transparently migrate legacy files."""

    def test_init_themes_migrates_legacy_themes_json(self, monkeypatch, tmp_path):
        """Old themes.json at project-root/data/ is migrated to new dir."""
        from rest_api import themes

        # Pre-populate legacy file
        LEGACY_DATA_DIR.mkdir(parents=True, exist_ok=True)
        legacy = LEGACY_DATA_DIR / "themes.json"
        legacy.write_text(
            json.dumps({
                "presets": [{"id": "preset-1", "name": "Migrated",
                             "primaryH": 100, "secondaryH": 200}],
                "activePresetIndex": 0,
                "cardOpacity": 0.5,
                "hoverPreference": "secondary",
            }),
            encoding="utf-8",
        )

        try:
            monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
            themes.init_themes()

            new_file = tmp_path / "themes.json"
            assert new_file.exists()
            data = json.loads(new_file.read_text(encoding="utf-8"))
            assert data["presets"][0]["name"] == "Migrated"
            assert data["hoverPreference"] == "secondary"
        finally:
            legacy.unlink(missing_ok=True)

    def test_init_ui_preferences_migrates_legacy(self, monkeypatch, tmp_path):
        """Old ui_preferences.json is migrated to the new dir."""
        from rest_api import ui

        LEGACY_DATA_DIR.mkdir(parents=True, exist_ok=True)
        legacy = LEGACY_DATA_DIR / "ui_preferences.json"
        legacy.write_text(
            json.dumps({
                "pinnedTabs": ["matrix", "inputs"],
                "tabOrder": ["matrix", "inputs"],
            }),
            encoding="utf-8",
        )

        try:
            monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
            ui.init_ui_preferences()

            new_file = tmp_path / "ui_preferences.json"
            assert new_file.exists()
            data = json.loads(new_file.read_text(encoding="utf-8"))
            assert data["pinnedTabs"] == ["matrix", "inputs"]
        finally:
            legacy.unlink(missing_ok=True)

    def test_init_device_settings_migrates_legacy(self, monkeypatch, tmp_path):
        """Old device_settings.json is migrated to the new dir."""
        from rest_api import device_settings

        LEGACY_DATA_DIR.mkdir(parents=True, exist_ok=True)
        legacy = LEGACY_DATA_DIR / "device_settings.json"
        legacy.write_text(
            json.dumps({
                "version": 1,
                "inputs": {"1": {"name": "Migrated PS5", "icon": None, "color": None}},
                "outputs": {},
            }),
            encoding="utf-8",
        )

        try:
            monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
            device_settings.init_device_settings()

            new_file = tmp_path / "device_settings.json"
            assert new_file.exists()
            data = json.loads(new_file.read_text(encoding="utf-8"))
            assert data["inputs"]["1"]["name"] == "Migrated PS5"
        finally:
            legacy.unlink(missing_ok=True)


class TestPersistenceRoundTrip:
    """End-to-end: write a value, re-init in the same dir, read it back."""

    def test_themes_persist_across_init(self, monkeypatch, tmp_path):
        from rest_api import themes

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))

        # First init + write
        themes.init_themes()
        themes._save_themes({
            "presets": [
                {"id": "preset-1", "name": "Persisted", "primaryH": 42, "secondaryH": 99},
            ] * 1 + [
                {"id": f"preset-{i}", "name": f"Default {i}",
                 "primaryH": 0, "secondaryH": 0} for i in range(2, 5)
            ],
            "activePresetIndex": 0,
            "cardOpacity": 0.9,
            "hoverPreference": "primary",
        })

        # Simulate a process restart: clear module-level path so init resolves again
        themes._theme_path = None
        themes.init_themes()

        loaded = themes._load_themes()
        assert loaded["presets"][0]["name"] == "Persisted"
        assert loaded["cardOpacity"] == 0.9

    def test_ui_preferences_persist_across_init(self, monkeypatch, tmp_path):
        from rest_api import ui

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))

        ui.init_ui_preferences()
        ui._save_preferences({
            "pinnedTabs": ["matrix", "profiles"],
            "tabOrder": ["profiles", "matrix"],
        })

        ui._ui_prefs_path = None
        ui.init_ui_preferences()

        loaded = ui._load_preferences()
        assert loaded["pinnedTabs"] == ["matrix", "profiles"]
        assert loaded["tabOrder"] == ["profiles", "matrix"]


# =============================================================================
# /api/system/storage endpoint
# =============================================================================


class TestStorageEndpoint:
    """The new ``/api/system/storage`` diagnostic endpoint."""

    @pytest.mark.asyncio
    async def test_storage_endpoint_returns_layout(self, monkeypatch, tmp_path):
        from rest_api.system import handle_get_storage

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        # Also reset the persistence cache so the handler sees the new env
        from persistence import reset_data_dir_cache
        reset_data_dir_cache()

        request = MagicMock()
        response = await handle_get_storage(request)

        body = json.loads(response.body)
        assert body["success"] is True
        assert body["data"]["data_dir"] == tmp_path.resolve().__str__()
        assert body["data"]["matrix_data_dir_env"] == str(tmp_path)
        # The new dir was created; it should be empty or have any migrated files
        assert "data_dir_files" in body["data"]

    @pytest.mark.asyncio
    async def test_info_endpoint_includes_storage(self, monkeypatch, tmp_path):
        from rest_api.system import handle_get_info
        from persistence import reset_data_dir_cache

        monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
        reset_data_dir_cache()

        request = MagicMock()
        response = await handle_get_info(request)

        body = json.loads(response.body)
        assert body["success"] is True
        assert "python_version" in body["data"]
        assert "platform" in body["data"]
        assert "rest_api_version" in body["data"]
        assert "storage" in body["data"]
        assert body["data"]["storage"]["data_dir"] == tmp_path.resolve().__str__()