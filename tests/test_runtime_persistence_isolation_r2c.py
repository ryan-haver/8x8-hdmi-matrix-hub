"""Synthetic unrelated installations must never supply an explicit fresh volume."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cec_macros import MacroManager
from config import ProfileManager
from config import SceneManager as LegacySceneManager
from dashboard_layout import DashboardLayoutManager
from hub.persistence import MigrationError, prepare_runtime_storage, reset_preparation
from hub.persistence.migrations import save_versioned_json
from persistence import migrate_legacy_file
from scene_manager import SceneManager
from system_shortcuts import SystemShortcutManager
from tests.runtime_persistence_fixtures_r2c import CATALOGS

READERS = {
    "profiles.json": ProfileManager,
    "scenes.json": LegacySceneManager,
    "cec_macros.json": MacroManager,
    "scenes_v2.json": SceneManager,
    "system_shortcuts.json": SystemShortcutManager,
    "dashboard_layout.json": DashboardLayoutManager,
}


@pytest.fixture(autouse=True)
def _reset_barrier():
    reset_preparation()
    yield
    reset_preparation()


@pytest.fixture
def unrelated_installation(tmp_path, monkeypatch):
    """Represent ignored checkout catalogs without opening any real user data."""
    legacy = tmp_path / "unrelated" / "data"
    legacy.mkdir(parents=True)
    for name, payload in CATALOGS.items():
        (legacy / name).write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr("persistence.get_legacy_data_paths", lambda: [legacy])
    before = {p: p.read_bytes() for p in legacy.iterdir()}
    yield legacy
    assert {p: p.read_bytes() for p in legacy.iterdir()} == before


def test_fresh_preparation_ignores_unrelated_legacy_catalogs(tmp_path, unrelated_installation):
    prepared = prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=tmp_path / "data")
    assert all(r.status == "missing" for r in prepared.results)
    assert list(prepared.paths.config_dir.iterdir()) == []
    assert list(prepared.paths.data_dir.iterdir()) == []


def test_explicit_managers_and_restart_ignore_unrelated_catalogs(tmp_path, unrelated_installation):
    from hub.runtime.managers import create_managers

    config, data = tmp_path / "config", tmp_path / "data"
    config.mkdir()
    data.mkdir()
    assert MacroManager(str(config)).list_macros() == []
    assert ProfileManager(str(config)).list_profiles() == []
    assert SceneManager(data).list_scenes() == []
    shortcuts = SystemShortcutManager(data)
    assert shortcuts.get("mute_all_audio").favorite is False
    assert shortcuts.get("mute_all_audio").dashboard_visible is False
    assert "foreign" not in json.dumps(DashboardLayoutManager(data).get_layout().to_dict())
    managers = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    assert managers.macros.list_macros() == []
    assert managers.profiles.create_profile("local", "Local", {}) is not None
    assert managers.profiles.delete_profile("local")
    snapshot = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.rglob("*.json")}
    restarted = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    assert restarted.profiles.list_profiles() == []
    assert snapshot == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.rglob("*.json")}


def test_local_shortcut_alias_wins_without_foreign_canonical(tmp_path, unrelated_installation):
    data = tmp_path / "data"
    data.mkdir()
    source = data / "shortcuts.json"
    original = b'{ "mute_all_audio": {"label": "Local"}, "private": 7 }'
    source.write_bytes(original)
    prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=data)
    manager = SystemShortcutManager(data)
    assert manager.get("mute_all_audio").label == "Local"
    assert manager.update_prefs("mute_all_audio", label="Edited")
    prepare_runtime_storage(config_dir=tmp_path / "config", data_dir=data)
    assert SystemShortcutManager(data).get("mute_all_audio").label == "Edited"
    assert source.read_bytes() == source.with_name("shortcuts.json.v0.bak").read_bytes() == original
    assert json.loads((data / "system_shortcuts.json").read_text(encoding="utf-8"))["private"] == 7


@pytest.mark.parametrize("filename", CATALOGS)
@pytest.mark.parametrize("unsafe", [b"{broken original", b'{"schema_version":999}', b'"invalid catalog"', b"\xff"])
def test_unsafe_target_refuses_even_explicit_valid_old_volume(tmp_path, filename, unsafe):
    legacy, config, data = tmp_path / "legacy", tmp_path / "config", tmp_path / "data"
    for directory in (legacy, config, data):
        directory.mkdir()
    source = legacy / filename
    source.write_text(json.dumps(CATALOGS[filename]), encoding="utf-8")
    target = (config if filename in ("profiles.json", "cec_macros.json") else data) / filename
    target.write_bytes(unsafe)
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=config, data_dir=data, legacy_data_dirs=(legacy,))
    assert target.read_bytes() == unsafe
    assert list(legacy.iterdir()) == [source]
    assert not list(tmp_path.rglob("*.bak"))
    assert not list(tmp_path.rglob("*.corrupt"))
    with pytest.raises(MigrationError):
        save_versioned_json(target, CATALOGS[filename])
    assert target.read_bytes() == unsafe


@pytest.mark.parametrize("filename", READERS)
def test_standalone_reader_refuses_corrupt_target_despite_ambient_source(tmp_path, unrelated_installation, filename):
    target = tmp_path / filename
    original = b"{broken original"
    target.write_bytes(original)
    with pytest.raises(MigrationError):
        READERS[filename](tmp_path)
    assert target.read_bytes() == original
    assert not list(tmp_path.glob("*.corrupt"))


def test_explicit_old_volume_import_and_same_installation_data_remain_supported(tmp_path):
    legacy, config, data = tmp_path / "old-volume", tmp_path / "config", tmp_path / "data"
    legacy.mkdir()
    data.mkdir()
    source = legacy / "cec_macros.json"
    source.write_bytes(b'{ "macros": [{"id":"old", "name":"Old", "steps":[], "private":8}] }')
    profiles = data / "profiles.json"
    profiles.write_bytes(b'{ "profiles": [{"id":"old", "name":"Old", "outputs":{}, "private":9}] }')
    before = {p: p.read_bytes() for p in (source, profiles)}
    prepare_runtime_storage(config_dir=config, data_dir=data, legacy_data_dirs=(legacy,))
    assert MacroManager(str(config)).get_macro("old").name == "Old"
    manager = ProfileManager(str(config))
    assert manager.get_profile("old").name == "Old"
    assert manager.update_profile("old", name="Edited") is not None
    assert MacroManager(str(config)).delete_macro("old")
    prepare_runtime_storage(config_dir=config, data_dir=data, legacy_data_dirs=(legacy,))
    assert MacroManager(str(config)).list_macros() == []
    assert ProfileManager(str(config)).get_profile("old").name == "Edited"
    for path, original in before.items():
        assert path.read_bytes() == path.with_name(path.name + ".v0.bak").read_bytes() == original


def test_legacy_output_scenes_in_same_installation_data_supply_profiles(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    source = data / "scenes.json"
    source.write_bytes(b'{"scenes":[{"id":"old","name":"Old","outputs":{}}]}')
    original = source.read_bytes()
    config = tmp_path / "config"
    prepare_runtime_storage(config_dir=config, data_dir=data)
    assert ProfileManager(str(config)).get_profile("old").name == "Old"
    assert source.read_bytes() == source.with_name("scenes.json.v0.bak").read_bytes() == original


def test_explicit_migration_helper_refuses_unsafe_managed_target(tmp_path):
    source = tmp_path / "legacy"
    source.mkdir()
    (source / "profiles.json").write_text('{"profiles":[]}', encoding="utf-8")
    target = tmp_path / "profiles.json"
    target.write_bytes(b"{broken")
    with pytest.raises(MigrationError):
        migrate_legacy_file(target, target.name, legacy_dirs=(source,))
    assert target.read_bytes() == b"{broken"
    assert not list(tmp_path.rglob("*.bak"))


def test_default_config_managers_use_test_private_config():
    """The shared fixture must isolate config as well as MATRIX_DATA_DIR."""
    import os

    config = Path(os.environ["UC_CONFIG_HOME"])
    assert Path(MacroManager().macros_file).parent == config
    assert MacroManager().list_macros() == []


@pytest.mark.parametrize("mode", ["runtime", "standalone"])
def test_unreadable_target_refuses_valid_explicit_source_portably(tmp_path, monkeypatch, mode):
    import builtins

    legacy, config = tmp_path / "legacy", tmp_path / "config"
    legacy.mkdir()
    config.mkdir()
    source = legacy / "profiles.json"
    source.write_bytes(b'{"profiles":[]}')
    target = config / "profiles.json"
    original = b'{"profiles":[{"id":"local","outputs":{}}]}'
    target.write_bytes(original)
    real_open = builtins.open

    def unreadable(file, *args, **kwargs):
        if Path(file) == target:
            raise OSError("synthetic read failure")
        return real_open(file, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(builtins, "open", unreadable)
        with pytest.raises(MigrationError):
            if mode == "runtime":
                prepare_runtime_storage(config_dir=config, data_dir=tmp_path / "data", legacy_data_dirs=(legacy,))
            else:
                migrate_legacy_file(target, target.name, legacy_dirs=(legacy,))
    assert target.read_bytes() == original
    assert not list(tmp_path.rglob("*.bak"))
    assert not list(tmp_path.rglob("*.corrupt"))
