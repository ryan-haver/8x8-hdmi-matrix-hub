"""End-to-end: hub REST app + real OreiMatrix + simulator."""

import pytest

import rest_api.utils as api_utils
from rest_api import reset_rate_limiter, set_matrix_device
from rest_api.app import create_rest_app

_GLOBALS = (
    "_matrix_device",
    "_input_names",
    "_output_names",
    "_config_file",
    "_scene_manager",
    "_profile_manager",
    "_macro_manager",
    "_system_shortcut_manager",
    "_dashboard_layout_manager",
)


@pytest.fixture
async def hub(aiohttp_client, matrix, monkeypatch, tmp_path):
    """REST test client wired to a real, connected OreiMatrix."""
    # Restore every REST module global this test touches.
    for name in _GLOBALS:
        monkeypatch.setattr(api_utils, name, getattr(api_utils, name))
    monkeypatch.setattr(api_utils, "_input_names", {})
    monkeypatch.setattr(api_utils, "_output_names", {})
    reset_rate_limiter()
    assert await matrix.connect()
    set_matrix_device(matrix, config_dir=str(tmp_path), data_dir=str(tmp_path))
    client = await aiohttp_client(create_rest_app(data_dir=tmp_path))
    yield client
    reset_rate_limiter()


async def test_status_reflects_simulator(hub, simulator):
    resp = await hub.get("/api/status")
    assert resp.status == 200
    data = (await resp.json())["data"]
    assert data["connected"] is True
    assert data["input_names"]["1"] == "PS3" and data["input_names"]["6"] == "PS5"
    assert data["output_names"]["1"] == "TV" and data["output_names"]["2"] == "Soundbar"
    assert data["routing"] == {str(i + 1): s for i, s in enumerate(simulator.state.routing)}
    assert data["preset_names"]["1"] == "Apple TV"


async def test_switch_changes_simulator_state(hub, simulator):
    resp = await hub.post("/api/switch", json={"input": 6, "output": 1})
    assert resp.status == 200, await resp.text()
    assert simulator.state.outputs[0].source == 6
    status = (await (await hub.get("/api/status")).json())["data"]
    # /api/status may serve the 3 s cache; the write invalidated it
    assert status["routing"]["1"] == 6


async def test_switch_all_and_preset(hub, simulator):
    assert (await hub.post("/api/switch", json={"input": 4})).status == 200
    assert simulator.state.routing == [4] * 8
    assert (await hub.post("/api/preset/3")).status == 200
    assert simulator.state.routing == [6] * 8


async def test_output_setting_via_rest(hub, simulator):
    resp = await hub.post("/api/output/2/mute", json={"muted": True})
    assert resp.status == 200, await resp.text()
    assert simulator.state.outputs[1].audio_mute == 1


async def test_health_reports_matrix_and_runtime(hub, simulator):
    await hub.get("/api/status")  # performs a poll
    data = (await (await hub.get("/api/health")).json())["data"]
    assert data["status"] == "healthy"
    assert data["matrix"]["connected"] is True
    assert data["matrix"]["host"] == "127.0.0.1"
    assert data["matrix"]["last_successful_poll"] is not None
    assert data["matrix"]["telnet_connected"] is False  # HTTP-only fixture
    assert data["runtime"]["task_count"] >= 1
    assert simulator.unrecognised() == []


async def test_status_cache_hits_share_one_background_refresh(hub, simulator):
    """API-11: cache hits used to spawn an untracked 4-request refresh each."""
    from rest_api import core

    simulator.faults.update({"latency_ms": 30})  # keep the refresh running for a while
    assert (await hub.get("/api/status")).status == 200  # fills the cache
    simulator.log.clear()
    for _ in range(5):
        assert (await hub.get("/api/status")).status == 200  # cache hits
    refresh = core._refresh_task
    assert refresh is not None  # referenced, so it cannot be garbage-collected mid-run
    await refresh
    video_reads = [e for e in simulator.log if e["channel"] == "http" and e["command"] == "get video status"]
    assert len(video_reads) == 1  # one refresh, not five
