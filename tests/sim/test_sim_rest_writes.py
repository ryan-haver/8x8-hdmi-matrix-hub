"""Registered REST writes: saved readback, reload, and actual simulator effects."""

from __future__ import annotations

import json
from copy import deepcopy

import pytest

from .conftest import sim_writes

pytestmark = pytest.mark.asyncio


async def _request(client, method, path, payload=None, status=200):
    response = await client.request(method, path, json=payload)
    assert response.status == status, await response.text()
    assert response.content_type == "application/json"
    result = await response.json()
    assert set(result) == {"success", "data", "error"}
    assert result["success"] is (status < 400)
    if status < 400:
        assert result["error"] is None
    return result["data"]


def _saved(client, name):
    return json.loads((client.data_dir / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("kind,port", [(kind, port) for kind in ("input", "output") for port in (1, 8)])
async def test_port_settings_save_reload_and_leave_device_unchanged(data_hub, simulator, kind, port):
    from rest_api.device_settings import init_device_settings

    before = deepcopy(simulator.state.to_dict())
    value = {"name": "Saved room", "icon": "tv", "color": "#123456"}
    data = await _request(data_hub, "POST", f"/api/device-settings/{kind}/{port}", value)
    assert {key: data[key] for key in value} == value
    assert _saved(data_hub, "device_settings.json")[f"{kind}s"][str(port)] == value
    init_device_settings(data_hub.data_dir)
    assert await _request(data_hub, "GET", f"/api/device-settings/{kind}/{port}") == {kind: port, **value}
    assert simulator.state.to_dict() == before
    assert sim_writes(simulator) == []


async def test_bulk_settings_updates_valid_ports_and_reports_invalid_entries(data_hub, simulator):
    value = {"inputs": {"1": {"name": "New source"}, "0": {}, "oops": {}, "8": "bad"},
             "outputs": {"8": {"name": "New room", "icon": "tv"}, "9": {}}}
    result = await _request(data_hub, "POST", "/api/device-settings", value)
    assert result["updated_inputs"] == [1]
    assert result["updated_outputs"] == [8]
    assert result["errors"] == ["inputs.0: port must be 1-8", "inputs.oops: not an integer",
                                "inputs.8: must be an object", "outputs.9: port must be 1-8"]
    saved = _saved(data_hub, "device_settings.json")
    assert saved == result["settings"]
    assert saved["inputs"]["1"]["name"] == "New source"
    assert saved["outputs"]["8"]["name"] == "New room"
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("path", ["/api/device-settings/input/0", "/api/device-settings/output/9",
                                  "/api/device-settings/preset/0/name"])
async def test_settings_invalid_ports_do_not_save(data_hub, simulator, path):
    before = _saved(data_hub, "device_settings.json")
    await _request(data_hub, "POST", path, {"name": "Rejected"}, 400)
    assert _saved(data_hub, "device_settings.json") == before
    assert sim_writes(simulator) == []


async def test_preset_rename_is_persisted_and_used_by_presets_read(data_hub, simulator):
    await _request(data_hub, "POST", "/api/device-settings/preset/8/name", {"name": "Evening"})
    assert _saved(data_hub, "device_settings.json")["presets"]["8"]["name"] == "Evening"
    presets = await _request(data_hub, "GET", "/api/presets")
    assert next(p for p in presets["presets"] if p["number"] == 8)["name"] == "Evening"
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("port", [1, 8])
async def test_output_rename_updates_device_and_saved_name(data_hub, simulator, port):
    await _request(data_hub, "POST", f"/api/output/{port}/name", {"name": "  Living Room  "})
    assert simulator.state.outputs[port - 1].name == "Living Room"
    assert len(sim_writes(simulator, "set output name")) == 1
    status = await _request(data_hub, "GET", "/api/status")
    assert status["output_names"][str(port)] == "Living Room"
    assert _saved(data_hub, "config.json")["output_names"][str(port)] == "Living Room"


@pytest.mark.parametrize("port", [1, 8])
async def test_cec_output_enable_changes_only_requested_port(data_hub, simulator, port):
    before = [bool(p.cec_enabled) for p in simulator.state.outputs]
    inputs = [p.cec_enabled for p in simulator.state.inputs]
    enabled = not before[port - 1]
    result = await _request(data_hub, "POST", f"/api/cec/output/{port}/enable", {"enabled": enabled})
    assert result["cec_enabled"] is enabled
    before[port - 1] = enabled
    assert [bool(p.cec_enabled) for p in simulator.state.outputs] == before
    assert [p.cec_enabled for p in simulator.state.inputs] == inputs
    observed = await _request(data_hub, "GET", "/api/status/cec")
    assert [p["cec_enabled"] for p in observed["cec_config"]["outputs"]] == before
    assert len(sim_writes(simulator, "set cec index")) == 1


async def test_profile_cec_and_macro_puts_survive_manager_reload(data_hub, simulator):
    from config import ProfileManager

    cec = {"nav_targets": ["input:5"], "volume_targets": ["output:8"], "auto_resolved": False}
    await _request(data_hub, "PUT", "/api/profile/movie_night/cec", {"cec_config": cec})
    macros = {"macros": ["macro_all_off"], "power_on_macro": None, "power_off_macro": "macro_all_off"}
    await _request(data_hub, "PUT", "/api/profile/movie_night/macros", macros)
    profile = ProfileManager(config_dir=str(data_hub.data_dir)).get_profile("movie_night")
    assert profile.cec_config.nav_targets == ["input:5"]
    assert profile.cec_config.volume_targets == ["output:8"]
    assert profile.macros == macros["macros"]
    assert profile.power_on_macro is None
    assert profile.power_off_macro == "macro_all_off"
    observed = await _request(data_hub, "GET", "/api/profile/movie_night/macros")
    assert {k: observed[k] for k in macros} == macros
    assert sim_writes(simulator) == []


async def test_profile_reorder_persists_only_requested_fields(data_hub, simulator):
    from config import ProfileManager

    result = await _request(data_hub, "POST", "/api/profiles/reorder", {"profiles": [
        {"id": "game_day", "pinned": True, "pin_order": 0, "name": "Ignored"},
        {"id": "movie_night", "pinned": False, "pin_order": 1}, {"id": "missing"}, {},
    ]})
    assert result == {"updated": ["game_day", "movie_night"],
                      "errors": ["Profile 'missing' not found", "Missing profile id"]}
    manager = ProfileManager(config_dir=str(data_hub.data_dir))
    assert manager.get_profile("game_day").pin_order == 0
    assert manager.get_profile("game_day").name == "Game Day"
    assert manager.get_profile("movie_night").pinned is False
    assert manager.get_profile("movie_night").pin_order == 1
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("suffix", ["", "/macros"])
@pytest.mark.parametrize("field,other,value", [("power_on_macro", "power_off_macro", "macro_all_off"),
                                              ("power_off_macro", "power_on_macro", "macro_tv_on")])
async def test_profile_null_clears_power_macro_and_omitted_field_is_preserved(data_hub, suffix, field, other, value):
    await _request(data_hub, "PUT", f"/api/profile/movie_night{suffix}", {field: None})
    result = await _request(data_hub, "GET", "/api/profile/movie_night")
    assert result.get(field) is None and result[other] == value
    profile = next(p for p in _saved(data_hub, "profiles.json")["profiles"] if p["id"] == "movie_night")
    assert profile.get(field) is None and profile[other] == value


async def test_shortcut_create_edit_flags_reorder_delete_survive_reload(data_hub, simulator):
    from system_shortcuts import SystemShortcutManager

    created = await _request(data_hub, "POST", "/api/shortcuts", {
        "name": "Saved action", "type": "route_all_to_output", "params": {"input": 5, "output": 8},
    }, 201)
    key = created["key"]
    assert key.startswith("user.") and created["builtin"] is False
    assert SystemShortcutManager(data_dir=data_hub.data_dir).get(key).params == {"input": 5, "output": 8}
    update = {"label": "Evening", "icon": "tv", "enabled": True, "favorite": False, "dashboard_visible": False}
    await _request(data_hub, "PUT", f"/api/shortcuts/{key}", update)
    for endpoint, field in (("favorite", "favorite"), ("dashboard", "dashboard_visible")):
        assert (await _request(data_hub, "POST", f"/api/shortcuts/{key}/{endpoint}"))[field] is True
    await _request(data_hub, "PUT", "/api/shortcuts/reorder", {"ordered_ids": [key, "builtin.one_to_one"]})
    saved = SystemShortcutManager(data_dir=data_hub.data_dir)
    sc = saved.get(key)
    assert (sc.label, sc.icon, sc.favorite, sc.dashboard_visible, sc.order) == ("Evening", "tv", True, True, 0)
    assert saved.get("builtin.one_to_one").order == 1
    await _request(data_hub, "DELETE", f"/api/shortcuts/{key}")
    assert SystemShortcutManager(data_dir=data_hub.data_dir).get(key) is None
    await _request(data_hub, "GET", f"/api/shortcuts/{key}", status=404)
    assert sim_writes(simulator) == []


async def test_shortcut_execute_legacy_route_applies_parameters(data_hub, simulator):
    await _request(data_hub, "POST", "/api/shortcuts/route_all_to_output/execute", {"params": {"input": 7, "output": 8}})
    assert simulator.state.outputs[7].source == 7
    assert len(sim_writes(simulator, "video switch")) == 1


@pytest.mark.parametrize("method,path,payload,status", [
    ("POST", "/api/shortcuts", {"name": "Invalid", "type": "nope"}, 400),
    ("DELETE", "/api/shortcuts/builtin.one_to_one", None, 400),
    ("PUT", "/api/shortcuts/nope", {"label": "Invalid"}, 404),
    ("POST", "/api/shortcuts/nope/favorite", None, 404),
    ("POST", "/api/shortcuts/nope/dashboard", None, 404),
    ("POST", "/api/shortcuts/system_reboot/execute", None, 400),
    ("PUT", "/api/shortcuts/reorder", {"ordered_ids": "bad"}, 400),
])
async def test_invalid_shortcut_writes_preserve_storage(data_hub, simulator, method, path, payload, status):
    before = _saved(data_hub, "system_shortcuts.json")
    await _request(data_hub, method, path, payload, status)
    assert _saved(data_hub, "system_shortcuts.json") == before
    assert sim_writes(simulator) == []


async def test_theme_save_normalizes_values_and_reset_is_persisted(data_hub, simulator):
    from rest_api.themes import DEFAULT_THEMES

    value = {"presets": [{"primaryH": i * 10, "secondaryH": i * 20} for i in range(4)],
             "activePresetIndex": 5, "cardOpacity": 2, "hoverPreference": "invalid"}
    data = await _request(data_hub, "PUT", "/api/themes", value)
    assert data["activePresetIndex"] == 1 and data["cardOpacity"] == 1 and data["hoverPreference"] == "primary"
    assert data["presets"][0]["name"] == "Preset 1" and data["presets"][0]["id"] == "preset-1"
    assert _saved(data_hub, "themes.json") == data == await _request(data_hub, "GET", "/api/themes")
    assert await _request(data_hub, "POST", "/api/themes/reset") == DEFAULT_THEMES
    assert _saved(data_hub, "themes.json") == DEFAULT_THEMES
    assert sim_writes(simulator) == []


async def test_ui_preferences_are_saved_and_read_back(data_hub, simulator):
    value = {"pinnedTabs": ["profiles", "matrix"], "tabOrder": ["profiles", "matrix", "dashboard", "inputs", "outputs"]}
    assert await _request(data_hub, "PUT", "/api/ui/preferences", value) == value
    assert _saved(data_hub, "ui_preferences.json") == value == await _request(data_hub, "GET", "/api/ui/preferences")
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("path,payload,filename", [
    ("/api/themes", {"presets": []}, "themes.json"),
    ("/api/ui/preferences", {"pinnedTabs": "bad", "tabOrder": []}, "ui_preferences.json"),
])
async def test_invalid_preferences_leave_saved_values_unchanged(data_hub, path, payload, filename):
    if not (data_hub.data_dir / filename).exists():
        (data_hub.data_dir / filename).write_text(json.dumps(await _request(data_hub, "GET", path)))
    before = _saved(data_hub, filename)
    await _request(data_hub, "PUT", path, payload, 400)
    assert _saved(data_hub, filename) == before


async def test_flic_register_adds_and_renames_buttons_and_survives_reload(data_hub, simulator, monkeypatch):
    from rest_api import integrations

    existing = _saved(data_hub, "flic_buttons.json")
    buttons = [{"bdaddr": "80:e4:da:70:00:01", "name": "Renamed", "serial": "BG12-A00001"},
               {"bdaddr": "80:e4:da:70:00:03", "name": "New button", "serial": "BG12-A00003"}]
    assert await _request(data_hub, "POST", "/api/integrations/flic/register", {"buttons": buttons}) == {"count": 3}
    expected = {**existing, **{btn["bdaddr"]: btn for btn in buttons}}
    assert _saved(data_hub, "flic_buttons.json") == expected
    monkeypatch.setattr(integrations, "_loaded", False)
    monkeypatch.setattr(integrations, "_registered_buttons", {})
    assert (await _request(data_hub, "GET", "/api/integrations/flic/buttons"))["buttons"] == list(expected.values())
    assert sim_writes(simulator) == []


async def test_connection_test_reconnects_and_reads_simulator_info(data_hub, matrix, simulator):
    await matrix.disconnect()
    result = await _request(data_hub, "POST", "/api/settings/test-connection")
    info = await matrix.get_device_info()
    assert result == {"connected": True, "host": matrix.host, "port": matrix.port,
                      "model": info["model"], "firmware_version": info["version"]}
    assert matrix.connected
    assert sim_writes(simulator) == []


def _deny_save(*args, **kwargs):
    raise OSError("Storage unavailable")


@pytest.mark.parametrize("path,payload", [
    ("/api/device-settings", {"inputs": {"1": {"name": "Unsaved"}}, "outputs": {"8": {"name": "Unsaved"}}}),
    ("/api/device-settings/input/1", {"name": "Unsaved"}),
    ("/api/device-settings/output/8", {"name": "Unsaved"}),
    ("/api/device-settings/preset/8/name", {"name": "Unsaved"}),
])
async def test_settings_storage_failure_is_not_success_and_keeps_readback(data_hub, monkeypatch, path, payload):
    before = _saved(data_hub, "device_settings.json")
    monkeypatch.setattr("_file_io.atomic_write_json", _deny_save)
    result = await _request(data_hub, "POST", path, payload, 500)
    if path == "/api/device-settings":
        assert result["updated_inputs"] == [] and result["updated_outputs"] == []
        assert result["errors"] == ["inputs.1: failed to save settings", "outputs.8: failed to save settings"]
    assert _saved(data_hub, "device_settings.json") == before
    assert await _request(data_hub, "GET", "/api/device-settings") == before


async def test_bulk_settings_partial_save_reports_only_persisted_ports(data_hub, monkeypatch):
    import _file_io

    original = _file_io.atomic_write_json
    before = _saved(data_hub, "device_settings.json")
    calls = 0

    def fail_second_save(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("Storage unavailable")
        return original(*args, **kwargs)

    monkeypatch.setattr(_file_io, "atomic_write_json", fail_second_save)
    result = await _request(data_hub, "POST", "/api/device-settings", {
        "inputs": {"1": {"name": "Saved"}}, "outputs": {"8": {"name": "Unsaved"}},
    }, 500)
    expected = deepcopy(before)
    expected["inputs"]["1"]["name"] = "Saved"
    assert result["updated_inputs"] == [1] and result["updated_outputs"] == []
    assert result["errors"] == ["outputs.8: failed to save settings"]
    assert result["settings"] == expected == _saved(data_hub, "device_settings.json")
    assert await _request(data_hub, "GET", "/api/device-settings") == expected


async def test_flic_storage_failure_is_not_success_and_keeps_readback(data_hub, monkeypatch):
    before = _saved(data_hub, "flic_buttons.json")
    monkeypatch.setattr("rest_api.integrations.atomic_write_json", _deny_save)
    await _request(data_hub, "POST", "/api/integrations/flic/register", {
        "buttons": [{"bdaddr": "80:e4:da:70:00:01", "name": "Unsaved rename"},
                    {"bdaddr": "80:e4:da:70:00:03", "name": "Unsaved"}],
    }, 500)
    assert _saved(data_hub, "flic_buttons.json") == before
    assert (await _request(data_hub, "GET", "/api/integrations/flic/buttons"))["buttons"] == list(before.values())
