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
    assert layout["data_dir"] == str(data_hub.data_dir)
    if path.endswith("info"):
        assert data["platform"] == os.name
        assert data["python_version"] == ".".join(str(n) for n in sys.version_info[:3])
        assert data["rest_api_version"] == "2.10.0"
    else:
        assert data["data_dir_exists"] is True
        assert set(src.name for src in FIXTURE_DATA.glob("*.json")) <= set(data["data_dir_files"])


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
