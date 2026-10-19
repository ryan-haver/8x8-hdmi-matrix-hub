"""Read contracts through registered routes, real OreiMatrix and disposable data.

These reads must expose saved values or device observations, preserve the JSON
envelope, and reject unavailable/invalid data without changing the matrix.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from .conftest import FIXTURE_DATA, sim_writes

pytestmark = pytest.mark.asyncio


async def _get(client, path, status=200):
    response = await client.get(path)
    assert response.status == status, await response.text()
    assert response.content_type == "application/json"
    envelope = await response.json()
    assert set(envelope) == {"success", "data", "error"}
    assert envelope["success"] is (status == 200)
    if status == 200:
        assert envelope["error"] is None
    else:
        assert envelope["data"] is None
        assert isinstance(envelope["error"], str) and envelope["error"]
    return envelope


async def test_device_settings_returns_saved_customizations(data_hub, simulator):
    expected = json.loads((FIXTURE_DATA / "device_settings.json").read_text(encoding="utf-8"))
    assert (await _get(data_hub, "/api/device-settings"))["data"] == expected
    assert sim_writes(simulator) == []


async def test_device_settings_private_extensions_survive_edits_without_public_exposure(data_hub, simulator):
    from rest_api import device_settings

    path = data_hub.data_dir / "device_settings.json"
    stored = json.loads(path.read_text(encoding="utf-8"))
    private = {"password": "synthetic-private-extension"}
    stored["credentials"] = private
    for kind in ("inputs", "outputs", "presets"):
        stored[kind]["1"]["credentials"] = private
    path.write_text(json.dumps(stored), encoding="utf-8")
    device_settings.init_device_settings(data_hub.data_dir)

    for route in ("/api/device-settings", "/api/device-settings/input/1", "/api/device-settings/output/1"):
        public = await _get(data_hub, route)
        assert "synthetic-private-extension" not in json.dumps(public)
        assert "credentials" not in json.dumps(public)
        assert "schema_version" not in json.dumps(public)
    response = await data_hub.post("/api/device-settings/input/1", json={"name": "Edited display name"})
    assert response.status == 200, await response.text()
    assert (await _get(data_hub, "/api/device-settings/input/1"))["data"]["name"] == "Edited display name"
    device_settings.init_device_settings(data_hub.data_dir)
    assert (await _get(data_hub, "/api/device-settings/input/1"))["data"]["name"] == "Edited display name"
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["schema_version"] == 2 and saved["credentials"] == private
    assert all(saved[kind]["1"]["credentials"] == private for kind in ("inputs", "outputs", "presets"))
    assert sim_writes(simulator) == []


async def test_scene_override_private_extensions_survive_public_edit_and_reload(data_hub, simulator):
    from rest_api.scenes_v2 import set_phase8_scene_manager
    from scene_manager import SceneManager

    async def read_scene(route):
        response = await data_hub.get(route)
        assert response.status == 200 and response.content_type == "application/json"
        envelope = await response.json()
        assert set(envelope) == {"success", "data"} and envelope["success"] is True
        return envelope

    path = data_hub.data_dir / "scenes_v2.json"
    stored = json.loads(path.read_text(encoding="utf-8"))
    scene_id = "scene_movienight01"
    scene = next(row for row in stored["scenes"] if row["id"] == scene_id)
    private = {"password": "synthetic-private-scene-extension"}
    scene["credentials"] = private
    scene["overrides"]["movie_night"]["2"]["credentials"] = private
    path.write_text(json.dumps(stored), encoding="utf-8")
    set_phase8_scene_manager(SceneManager(data_dir=data_hub.data_dir))

    for route in ("/api/v2/scenes", f"/api/v2/scenes/{scene_id}"):
        public = await read_scene(route)
        assert "synthetic-private-scene-extension" not in json.dumps(public)
        assert "credentials" not in json.dumps(public)
        assert "passcode_hash" not in json.dumps(public)
    response = await data_hub.put(f"/api/v2/scenes/{scene_id}", json={"name": "Edited scene"})
    assert response.status == 200, await response.text()
    set_phase8_scene_manager(SceneManager(data_dir=data_hub.data_dir))
    public = (await read_scene(f"/api/v2/scenes/{scene_id}"))["data"]["scene"]
    assert public["name"] == "Edited scene"
    assert public["overrides"] == {"movie_night": {"2": {"audio_mute": True}}}
    saved = next(row for row in json.loads(path.read_text(encoding="utf-8"))["scenes"] if row["id"] == scene_id)
    assert saved["credentials"] == private
    assert saved["overrides"]["movie_night"]["2"]["credentials"] == private
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("direction,boundary,wrapped", [("next", 8, 1), ("previous", 1, 8)])
@pytest.mark.parametrize("explicit_true", [False, True])
async def test_cycle_clamp_and_wrap_read_back_exact_operation(
    data_hub, simulator, direction, boundary, wrapped, explicit_true,
):
    response = await data_hub.post("/api/switch", json={"input": boundary, "output": 1})
    assert response.status == 200, await response.text()
    response = await data_hub.post(f"/api/input/{direction}?output=1&cycle=false")
    assert response.status == 200, await response.text()
    result = (await response.json())["data"]
    assert (result["previous_input"], result["current_input"], result["output"]) == (boundary, boundary, 1)
    assert (await _get(data_hub, "/api/status"))["data"]["routing"]["1"] == boundary
    assert simulator.state.outputs[0].source == boundary
    suffix = "&cycle=true" if explicit_true else ""
    response = await data_hub.post(f"/api/input/{direction}?output=1{suffix}")
    assert response.status == 200, await response.text()
    result = (await response.json())["data"]
    assert (result["previous_input"], result["current_input"], result["output"]) == (boundary, wrapped, 1)
    assert (await _get(data_hub, "/api/status"))["data"]["routing"]["1"] == wrapped
    assert simulator.state.outputs[0].source == wrapped


async def test_save_current_reads_fresh_device_state_before_registered_profile_readback(
    data_hub, matrix, simulator,
):
    matrix._status_cache_ttl = 3600
    cached = await matrix.get_output_status()
    simulator.state.outputs[0].source = 8
    simulator.state.outputs[0].stream = 0
    simulator.state.outputs[0].audio_mute = 1
    assert await matrix.get_output_status() == cached
    simulator.log.clear()
    response = await data_hub.post("/api/scene/save-current", json={"id": "fresh_sim_capture"})
    assert response.status == 200, await response.text()
    captured = (await response.json())["data"]
    assert captured["outputs"]["1"]["input"] == 8
    assert captured["outputs"]["1"]["enabled"] is False
    assert captured["outputs"]["1"]["audio_mute"] is True
    public = (await _get(data_hub, "/api/profile/fresh_sim_capture"))["data"]
    assert public["outputs"] == captured["outputs"]
    saved = json.loads((data_hub.data_dir / "profiles.json").read_text(encoding="utf-8"))
    assert next(row for row in saved["profiles"] if row["id"] == "fresh_sim_capture")["outputs"] == public["outputs"]
    commands = {entry["command"] for entry in simulator.log if entry["channel"] == "http"}
    assert {"get output status", "get video status"} <= commands
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("direction", ["next", "previous"])
@pytest.mark.parametrize("spelling", ["yes", "TRUE", ""])
async def test_invalid_cycle_option_is_refused_before_any_write(data_hub, simulator, direction, spelling):
    before = (await _get(data_hub, "/api/status"))["data"]["routing"]
    response = await data_hub.post(f"/api/input/{direction}?output=1&cycle={spelling}")
    assert response.status == 400, await response.text()
    assert (await response.json())["success"] is False
    assert (await _get(data_hub, "/api/status"))["data"]["routing"] == before
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("kind,port", [(kind, port) for kind in ("input", "output") for port in (1, 8)])
async def test_individual_settings_match_saved_port(data_hub, simulator, kind, port):
    saved = json.loads((FIXTURE_DATA / "device_settings.json").read_text(encoding="utf-8"))
    data = (await _get(data_hub, f"/api/device-settings/{kind}/{port}"))["data"]
    assert data == {kind: port, **saved[f"{kind}s"][str(port)]}
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("kind,port", [(kind, port) for kind in ("input", "output") for port in (0, 9, "oops")])
async def test_invalid_settings_ports_are_json_400(data_hub, simulator, kind, port):
    await _get(data_hub, f"/api/device-settings/{kind}/{port}", 400)
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("suffix", ["", "/favorites", "/dashboard", "/builtin.one_to_one", "/route_one_to_one", "/nope"])
async def test_shortcut_read_aliases_have_identical_contracts(data_hub, simulator, suffix):
    status = 404 if suffix == "/nope" else 200
    legacy = await _get(data_hub, f"/api/shortcuts{suffix}", status)
    canonical = await _get(data_hub, f"/api/system-shortcuts{suffix}", status)
    assert legacy == canonical
    if suffix in ("", "/favorites", "/dashboard"):
        shortcuts = legacy["data"]["shortcuts"]
        assert legacy["data"]["count"] == len(shortcuts)
        assert shortcuts  # seeded favorites and dashboard lists are nonempty
        if suffix:
            field = "favorite" if suffix == "/favorites" else "dashboard_visible"
            assert all(sc[field] is True for sc in shortcuts)
    elif status == 200:
        assert legacy["data"]["key"] == "route_one_to_one"
        assert legacy["data"]["id"] == "builtin.one_to_one"
    assert sim_writes(simulator) == []


async def test_enabled_shortcut_filter_excludes_disabled_reboot(data_hub):
    all_items = (await _get(data_hub, "/api/shortcuts"))["data"]["shortcuts"]
    filtered = (await _get(data_hub, "/api/shortcuts?enabled_only=true"))["data"]
    assert any(sc["key"] == "system_reboot" and sc["enabled"] is False for sc in all_items)
    assert filtered["shortcuts"] == [sc for sc in all_items if sc["enabled"]]
    assert filtered["count"] == len(filtered["shortcuts"])


@pytest.mark.parametrize("path,filename,value", [
    ("/api/themes", "themes.json", {
        "presets": [{"id": f"preset-{i}", "name": f"Saved {i}", "primaryH": i * 20, "secondaryH": i * 30}
                    for i in range(1, 5)],
        "activePresetIndex": 2, "cardOpacity": 0.6, "hoverPreference": "secondary",
    }),
    ("/api/ui/preferences", "ui_preferences.json", {
        "pinnedTabs": ["profiles", "matrix"], "tabOrder": ["profiles", "matrix", "dashboard", "inputs", "outputs"],
    }),
])
async def test_preferences_reads_return_saved_values(data_hub, simulator, path, filename, value):
    (data_hub.data_dir / filename).write_text(json.dumps(value))
    assert (await _get(data_hub, path))["data"] == value
    assert sim_writes(simulator) == []


async def test_flic_read_returns_registered_fixture_buttons(data_hub, simulator):
    saved = json.loads((FIXTURE_DATA / "flic_buttons.json").read_text(encoding="utf-8"))
    assert (await _get(data_hub, "/api/integrations/flic/buttons"))["data"] == {"buttons": list(saved.values())}
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("path", ["/api/system/info", "/api/system/storage"])
async def test_runtime_diagnostics_describe_the_actual_data_directory(data_hub, path):
    data = (await _get(data_hub, path))["data"]
    layout = data["storage"] if path.endswith("info") else data
    # SEC-11: the state of the data directory, never its path or its file names.
    assert layout["source"] == "MATRIX_DATA_DIR"
    assert layout["data_dir_exists"] is True
    assert layout["writable"] is True
    assert layout["file_count"] >= len(list(FIXTURE_DATA.glob("*.json")))
    assert not {"data_dir", "config_dir", "matrix_data_dir_env", "data_dir_files"} & set(layout)
    assert str(data_hub.data_dir) not in json.dumps(data)
    if path.endswith("info"):
        assert data["platform"] == os.name
        assert data["python_version"] == ".".join(str(n) for n in sys.version_info[:3])
        assert data["rest_api_version"] == "2.10.0"


async def test_settings_read_tracks_connection_state(data_hub, matrix):
    expected = {"matrix_host": matrix.host, "matrix_port": matrix.port, "connected": True}
    assert (await _get(data_hub, "/api/settings"))["data"] == expected
    await matrix.disconnect()
    assert (await _get(data_hub, "/api/settings"))["data"] == {**expected, "connected": False}


@pytest.mark.parametrize("kind", ["input", "output"])
async def test_cec_catalog_distinguishes_sources_from_displays(data_hub, simulator, kind):
    data = (await _get(data_hub, f"/api/cec/commands/{kind}"))["data"]
    assert data["device_type"] == kind
    assert data["total_commands"] == len(data["commands"])
    categorized = [entry["command"] for entries in data["by_category"].values() for entry in entries]
    assert set(categorized) == set(data["commands"])
    assert len(categorized) == len(set(categorized))
    if kind == "output":
        assert set(data["commands"]) == {"POWER_ON", "POWER_OFF", "MUTE", "VOLUME_UP", "VOLUME_DOWN", "ACTIVE"}
    else:
        assert {"POWER_ON", "POWER_OFF", "UP", "DOWN", "SELECT", "PLAY", "PAUSE"} <= set(data["commands"])
    assert sim_writes(simulator) == []


async def test_invalid_cec_catalog_type_is_json_400(data_hub, simulator):
    await _get(data_hub, "/api/cec/commands/nope", 400)
    assert sim_writes(simulator) == []


async def test_cec_status_matches_all_device_ports(data_hub, simulator):
    data = (await _get(data_hub, "/api/status/cec"))["data"]
    for kind in ("inputs", "outputs"):
        observed = data["cec_config"][kind]
        ports = getattr(simulator.state, kind)
        assert [p["number"] for p in observed] == list(range(1, 9))
        assert [p["cec_enabled"] for p in observed] == [bool(p.cec_enabled) for p in ports]
    assert sim_writes(simulator) == []


async def test_cables_without_telnet_are_unavailable(data_hub, simulator):
    result = await _get(data_hub, "/api/status/cables", 503)
    assert "Telnet" in result["error"]
    assert sim_writes(simulator) == []


async def test_cables_with_telnet_match_device_connections(aiohttp_client, matrix_with_telnet, simulator, tmp_path):
    from rest_api import set_matrix_device
    from rest_api.app import create_rest_app

    assert await matrix_with_telnet.connect()
    assert matrix_with_telnet.telnet_connected
    set_matrix_device(matrix_with_telnet, config_dir=str(tmp_path), data_dir=str(tmp_path))
    client = await aiohttp_client(create_rest_app(data_dir=tmp_path))
    data = (await _get(client, "/api/status/cables"))["data"]
    assert data["telnetAvailable"] is True
    for kind, field in (("inputs", "cable"), ("outputs", "connected")):
        assert [p["number"] for p in data[kind]] == list(range(1, 9))
        assert [p["name"] for p in data[kind]] == [p.name for p in getattr(simulator.state, kind)]
        assert [p["cableConnected"] for p in data[kind]] == [bool(getattr(p, field)) for p in getattr(simulator.state, kind)]
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("path", ["/api/status/cables", "/api/status/cec"])
async def test_device_status_reads_after_disconnect_are_json_503(data_hub, matrix, simulator, path):
    await matrix.disconnect()
    result = await _get(data_hub, path, 503)
    assert result["error"] == "Matrix not connected"
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("path", ["/kiosk", "/kiosk/"])
async def test_kiosk_aliases_serve_the_shipped_html(data_hub, path):
    response = await data_hub.get(path)
    assert response.status == 200
    assert response.content_type == "text/html"
    expected = Path(__file__).resolve().parents[2] / "web" / "kiosk.html"
    assert await response.read() == expected.read_bytes()


async def test_health_includes_integration_lifecycle_mapping(data_hub, simulator, monkeypatch):
    assert (await _get(data_hub, "/api/health"))["data"]["integrations"] == {}
    states = {"flic": {"running": True, "button_count": 2}}
    monkeypatch.setitem(data_hub.server.app, "integration_health_provider", lambda: states)
    assert (await _get(data_hub, "/api/health"))["data"]["integrations"] == states
    states["flic"]["running"] = False
    assert (await _get(data_hub, "/api/health"))["data"]["integrations"]["flic"]["running"] is False
    assert sim_writes(simulator) == []


async def test_flic_registered_routes_preserve_private_storage_without_phantom_buttons(data_hub, simulator):
    from hub.persistence import CURRENT_SCHEMA_VERSION

    address = "80:e4:da:70:00:01"
    private = {"bdaddr": "metadata-only", "password": "synthetic-private-extension"}
    path = data_hub.data_dir / "flic_buttons.json"
    path.write_text(json.dumps({
        "schema_version": CURRENT_SCHEMA_VERSION, "extension_object": private,
        address: {"bdaddr": address, "name": "Before", "serial": "sim", "credentials": private},
    }), encoding="utf-8")
    public = (await _get(data_hub, "/api/integrations/flic/buttons"))["data"]
    assert public == {"buttons": [{"bdaddr": address, "name": "Before", "serial": "sim"}]}
    response = await data_hub.post("/api/integrations/flic/register", json={"buttons": [
        {"bdaddr": address, "name": "After", "serial": "updated"},
    ]})
    assert response.status == 200, await response.text()
    envelope = await response.json()
    assert envelope == {"success": True, "data": {"count": 1}, "error": None}
    assert (await _get(data_hub, "/api/integrations/flic/buttons"))["data"] == {
        "buttons": [{"bdaddr": address, "name": "After", "serial": "updated"}],
    }
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["extension_object"] == private and saved[address]["credentials"] == private
    assert saved["schema_version"] == CURRENT_SCHEMA_VERSION
    assert sim_writes(simulator) == []


async def test_disabled_flic_routes_leave_core_reads_available(
    data_hub, simulator, monkeypatch, aiohttp_client,
):
    from rest_api.app import create_rest_app

    monkeypatch.setenv("FLIC_ENABLED", "false")
    client = await aiohttp_client(create_rest_app(data_dir=data_hub.data_dir))
    assert (await client.get("/api/integrations/flic/buttons")).status == 404
    assert (await client.post("/api/integrations/flic/register", json={"buttons": []})).status == 404
    assert (await _get(client, "/api/health"))["data"]["status"] == "healthy"
    assert (await _get(client, "/api/status"))["data"]["connected"] is True
    assert sim_writes(simulator) == []


async def test_openapi_spec_and_swagger_docs_reads(data_hub, simulator):
    from hub.openapi import validate_openapi_spec

    spec_resp = await data_hub.get("/api/openapi.json")
    assert spec_resp.status == 200
    assert spec_resp.content_type == "application/json"
    spec = await spec_resp.json()
    assert spec["openapi"] == "3.1.0"
    assert validate_openapi_spec(spec) == []
    assert "/api/openapi.json" in spec["paths"]
    assert "/api/docs" in spec["paths"]
    assert spec["components"]["schemas"]["SceneV2ResponseEnvelope"]["required"] == ["success"]
    for direction in ("next", "previous"):
        parameters = spec["paths"][f"/api/input/{direction}"]["post"]["parameters"]
        cycle = next(parameter for parameter in parameters if parameter["name"] == "cycle")
        assert cycle["in"] == "query" and cycle["schema"] == {"type": "boolean", "default": True}

    docs_resp = await data_hub.get("/api/docs")
    assert docs_resp.status == 200
    assert docs_resp.content_type == "text/html"
    html = await docs_resp.text()
    assert "SwaggerUIBundle" in html
    assert "/api/openapi.json" in html
    assert 'id="swagger-ui"' in html
    assert sim_writes(simulator) == []


@pytest.mark.parametrize("corrupt", [False, True])
async def test_info_manifest_fallback_keeps_the_driver_identity(data_hub, simulator, tmp_path, monkeypatch, corrupt):
    import hub
    from rest_api import core

    manifest = tmp_path / "missing-driver.json"
    if corrupt:
        manifest.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(core, "DRIVER_JSON", manifest)
    info = (await _get(data_hub, "/api/info"))["data"]
    assert info["driver_id"] == "hdmi_matrix"
    assert info["driver_name"] == "HDMI Matrix"
    assert info["version"] == hub.__version__
    assert sim_writes(simulator) == []

