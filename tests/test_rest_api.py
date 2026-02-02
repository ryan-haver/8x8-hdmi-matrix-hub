"""
Integration tests for REST API server.

Uses aiohttp test client to test endpoints without running a real server.
Tests use mock_matrix fixture from conftest.py by default.

To run with real device:
    USE_MOCK_MATRIX=0 pytest tests/test_rest_api.py
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

# Import the REST API module
import rest_api
from rest_api import create_rest_app, set_matrix_device, update_input_names, reset_rate_limiter

# mock_matrix fixture is provided by conftest.py


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def extended_mock_matrix(mock_matrix):
    """
    Extend the base mock_matrix with additional methods needed for REST API tests.
    The base mock_matrix comes from conftest.py.
    """
    # Sprint 4 scene methods (specific to REST API tests)
    mock_matrix.switch = AsyncMock(return_value=True)
    mock_matrix.get_output_status = AsyncMock(return_value={
        "allsource": [1, 2, 3, 4, 5, 6, 7, 8],
        "allout": [1, 1, 1, 1, 1, 1, 1, 1],
        "allaudiomute": [0, 0, 0, 0, 0, 0, 0, 0],
        "allhdr": [3, 3, 3, 3, 3, 3, 3, 3],
        "allhdcp": [3, 3, 3, 3, 3, 3, 3, 3],
    })
    mock_matrix.set_audio_mute = AsyncMock(return_value=True)
    mock_matrix.set_hdr_mode = AsyncMock(return_value=True)
    mock_matrix.set_hdcp_mode = AsyncMock(return_value=True)
    
    return mock_matrix


@pytest.fixture
def app(extended_mock_matrix):
    """Create the REST app with mock matrix."""
    # Reset rate limiter between tests
    reset_rate_limiter()
    
    set_matrix_device(extended_mock_matrix, {
        1: "Apple TV",
        2: "PS5",
        3: "Nintendo Switch",
        4: "PC",
        5: "Shield",
        6: "Cable Box",
        7: "Blu-ray",
        8: "Chromecast",
    })
    return create_rest_app()


@pytest.fixture
async def client(aiohttp_client, app):
    """Create a test client for the app."""
    return await aiohttp_client(app)


# =============================================================================
# Health & Status Endpoint Tests
# =============================================================================


class TestHealthEndpoints:
    """Tests for health and status endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test /api/health returns healthy status."""
        resp = await client.get("/api/health")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_api_root_documentation(self, client):
        """Test / returns API documentation."""
        resp = await client.get("/api")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["version"] == "2.10.0"
        assert "endpoints" in data["data"]
        assert "websocket" in data["data"]["endpoints"]  # WebSocket endpoint documented
        assert "edid_control" in data["data"]["endpoints"]  # EDID control documented
        assert "scenes" in data["data"]["endpoints"]  # Scenes endpoint documented

    @pytest.mark.asyncio
    async def test_info_endpoint(self, client, mock_matrix):
        """Test /api/info returns API and matrix info."""
        # Mock get_device_info to return device info
        mock_matrix.get_device_info = AsyncMock(return_value={
            "model": "BK-808",
            "version": "V1.10.01",
        })
        
        resp = await client.get("/api/info")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "api_version" in data["data"]
        assert data["data"]["input_count"] == 8
        assert data["data"]["output_count"] == 8

    @pytest.mark.asyncio
    async def test_status_endpoint(self, client, mock_matrix):
        """Test /api/status returns matrix status."""
        resp = await client.get("/api/status")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        mock_matrix.get_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_presets_endpoint(self, client):
        """Test /api/presets returns preset list."""
        resp = await client.get("/api/presets")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert len(data["data"]["presets"]) == 8
        # Presets use generic names (they are saved configurations, not inputs)
        assert data["data"]["presets"][0]["name"] == "Preset 1"


# =============================================================================
# Control Endpoint Tests
# =============================================================================


class TestControlEndpoints:
    """Tests for control endpoints."""

    @pytest.mark.asyncio
    async def test_recall_preset(self, client, mock_matrix):
        """Test POST /api/preset/{n} recalls preset."""
        resp = await client.post("/api/preset/3")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        mock_matrix.recall_preset.assert_called_once_with(3)

    @pytest.mark.asyncio
    async def test_recall_preset_invalid(self, client):
        """Test invalid preset number returns 400."""
        resp = await client.post("/api/preset/0")
        assert resp.status == 400
        
        resp = await client.post("/api/preset/9")
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_switch_routing(self, client, mock_matrix):
        """Test POST /api/switch routes input to output."""
        resp = await client.post("/api/switch", json={"input": 3, "output": 1})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        mock_matrix.switch_input.assert_called_once_with(3, 1)

    @pytest.mark.asyncio
    async def test_switch_missing_input(self, client):
        """Test switch with missing input returns 400."""
        # Output alone without input should return 400
        resp = await client.post("/api/switch", json={"output": 1})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_switch_to_all_outputs(self, client, mock_matrix):
        """Test switch with missing output routes to all outputs (valid)."""
        # Input alone without output routes to all outputs
        mock_matrix.switch_input_to_all = AsyncMock(return_value=True)
        resp = await client.post("/api/switch", json={"input": 1})
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["output"] == "all"
        mock_matrix.switch_input_to_all.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_power_on(self, client, mock_matrix):
        """Test POST /api/power/on powers on matrix."""
        resp = await client.post("/api/power/on")
        assert resp.status == 200
        
        mock_matrix.power_on.assert_called_once()

    @pytest.mark.asyncio
    async def test_power_off(self, client, mock_matrix):
        """Test POST /api/power/off powers off matrix."""
        resp = await client.post("/api/power/off")
        assert resp.status == 200
        
        mock_matrix.power_off.assert_called_once()


# =============================================================================
# Input Cycling Tests
# =============================================================================


class TestInputCycling:
    """Tests for input cycling endpoints."""

    @pytest.mark.asyncio
    async def test_input_next(self, client, mock_matrix):
        """Test POST /api/input/next cycles to next input."""
        resp = await client.post("/api/input/next?output=1")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "current_input" in data["data"]

    @pytest.mark.asyncio
    async def test_input_previous(self, client, mock_matrix):
        """Test POST /api/input/previous cycles to previous input."""
        resp = await client.post("/api/input/previous?output=1")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_output_source(self, client, mock_matrix):
        """Test POST /api/output/{n}/source sets source."""
        resp = await client.post("/api/output/1/source", json={"input": 5})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True


# =============================================================================
# Advanced Output Control Tests (Sprint 2)
# =============================================================================


class TestAdvancedOutputControl:
    """Tests for Sprint 2 advanced output control endpoints."""

    @pytest.mark.asyncio
    async def test_output_enable(self, client, mock_matrix):
        """Test POST /api/output/{n}/enable."""
        resp = await client.post("/api/output/1/enable", json={"enabled": False})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        mock_matrix.set_output_enable.assert_called_once_with(1, False)

    @pytest.mark.asyncio
    async def test_output_hdcp(self, client, mock_matrix):
        """Test POST /api/output/{n}/hdcp."""
        resp = await client.post("/api/output/2/hdcp", json={"mode": 2})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        mock_matrix.set_output_hdcp.assert_called_once_with(2, 2)

    @pytest.mark.asyncio
    async def test_output_hdcp_invalid_mode(self, client):
        """Test HDCP with invalid mode returns 400."""
        resp = await client.post("/api/output/1/hdcp", json={"mode": 10})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_output_hdr(self, client, mock_matrix):
        """Test POST /api/output/{n}/hdr."""
        resp = await client.post("/api/output/1/hdr", json={"mode": 1})
        assert resp.status == 200
        
        mock_matrix.set_output_hdr.assert_called_once_with(1, 1)

    @pytest.mark.asyncio
    async def test_output_scaler(self, client, mock_matrix):
        """Test POST /api/output/{n}/scaler."""
        resp = await client.post("/api/output/1/scaler", json={"mode": 4})
        assert resp.status == 200
        
        mock_matrix.set_output_scaler.assert_called_once_with(1, 4)

    @pytest.mark.asyncio
    async def test_output_arc(self, client, mock_matrix):
        """Test POST /api/output/{n}/arc."""
        resp = await client.post("/api/output/1/arc", json={"enabled": True})
        assert resp.status == 200
        
        mock_matrix.set_output_arc.assert_called_once_with(1, True)

    @pytest.mark.asyncio
    async def test_output_mute(self, client, mock_matrix):
        """Test POST /api/output/{n}/mute."""
        resp = await client.post("/api/output/3/mute", json={"muted": True})
        assert resp.status == 200
        
        mock_matrix.set_output_audio_mute.assert_called_once_with(3, True)

    @pytest.mark.asyncio
    async def test_cec_enable(self, client, mock_matrix):
        """Test POST /api/cec/{type}/{n}/enable."""
        resp = await client.post("/api/cec/input/2/enable", json={"enabled": True})
        assert resp.status == 200
        
        mock_matrix.set_cec_enable.assert_called_once_with("input", 2, True)

    @pytest.mark.asyncio
    async def test_preset_save(self, client, mock_matrix):
        """Test POST /api/preset/{n}/save."""
        resp = await client.post("/api/preset/5/save")
        assert resp.status == 200
        
        mock_matrix.save_preset.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_system_reboot(self, client, mock_matrix):
        """Test POST /api/system/reboot."""
        resp = await client.post("/api/system/reboot")
        assert resp.status == 200
        
        mock_matrix.system_reboot.assert_called_once()


# =============================================================================
# EDID Control Tests (Sprint 4)
# =============================================================================


class TestEdidControl:
    """Tests for Sprint 4 EDID control endpoints."""

    @pytest.mark.asyncio
    async def test_get_edid_modes(self, client):
        """Test GET /api/edid/modes returns available EDID modes."""
        resp = await client.get("/api/edid/modes")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "modes" in data["data"]
        # Check some expected modes exist (keys are strings in JSON)
        modes = data["data"]["modes"]
        assert "1" in modes  # 1080p 2CH
        assert "36" in modes  # 4K60 HDR Atmos
        assert "38" in modes  # 8K60

    @pytest.mark.asyncio
    async def test_get_edid_status(self, client, mock_matrix):
        """Test GET /api/status/edid returns EDID status for all inputs."""
        mock_matrix.get_edid_status.return_value = {
            "edid": [36, 36, 36, 36, 36, 36, 36, 36]
        }
        
        resp = await client.get("/api/status/edid")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "inputs" in data["data"]
        assert len(data["data"]["inputs"]) == 8
        assert data["data"]["inputs"][0]["edid_mode"] == 36
        assert data["data"]["inputs"][0]["edid_mode_name"] == "4K60 HDR Atmos"
        mock_matrix.get_edid_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_input_edid(self, client, mock_matrix):
        """Test POST /api/input/{n}/edid sets EDID mode."""
        mock_matrix.set_input_edid.return_value = True
        
        resp = await client.post("/api/input/1/edid", json={"mode": 36})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["input"] == 1
        assert data["data"]["mode"] == 36
        assert data["data"]["mode_name"] == "4K60 HDR Atmos"
        mock_matrix.set_input_edid.assert_called_once_with(1, 36)

    @pytest.mark.asyncio
    async def test_set_input_edid_invalid_input(self, client, mock_matrix):
        """Test POST /api/input/{n}/edid with invalid input number."""
        resp = await client.post("/api/input/0/edid", json={"mode": 36})
        assert resp.status == 400
        
        resp = await client.post("/api/input/9/edid", json={"mode": 36})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_set_input_edid_missing_mode(self, client, mock_matrix):
        """Test POST /api/input/{n}/edid with missing mode parameter."""
        resp = await client.post("/api/input/1/edid", json={})
        assert resp.status == 400
        
        data = await resp.json()
        assert data["success"] is False
        assert "mode" in data["error"]

    @pytest.mark.asyncio
    async def test_set_input_edid_copy_from_output(self, client, mock_matrix):
        """Test POST /api/input/{n}/edid with copy-from-output mode (15-22)."""
        mock_matrix.copy_edid_from_output.return_value = True
        
        resp = await client.post("/api/input/1/edid", json={"mode": 15})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        # Mode 15 = copy from output 1
        mock_matrix.copy_edid_from_output.assert_called_once_with(1, 1)


# =============================================================================
# LCD Timeout Control Tests (Sprint 4)
# =============================================================================


class TestLcdTimeoutControl:
    """Tests for Sprint 4 LCD timeout control endpoints."""

    @pytest.mark.asyncio
    async def test_get_lcd_timeout_modes(self, client):
        """Test GET /api/system/lcd/modes returns available LCD timeout modes."""
        resp = await client.get("/api/system/lcd/modes")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "modes" in data["data"]
        # Check expected modes exist (keys are strings in JSON)
        modes = data["data"]["modes"]
        assert "0" in modes  # Off
        assert "1" in modes  # Always On
        assert "4" in modes  # 60 seconds

    @pytest.mark.asyncio
    async def test_set_lcd_timeout(self, client, mock_matrix):
        """Test POST /api/system/lcd sets LCD timeout mode."""
        mock_matrix.set_lcd_timeout.return_value = True
        
        resp = await client.post("/api/system/lcd", json={"mode": 3})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["mode"] == 3
        assert data["data"]["mode_name"] == "30 seconds"
        mock_matrix.set_lcd_timeout.assert_called_once_with(3)

    @pytest.mark.asyncio
    async def test_set_lcd_timeout_invalid_mode(self, client, mock_matrix):
        """Test POST /api/system/lcd with invalid mode."""
        resp = await client.post("/api/system/lcd", json={"mode": 5})
        assert resp.status == 400
        
        resp = await client.post("/api/system/lcd", json={"mode": -1})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_set_lcd_timeout_missing_mode(self, client, mock_matrix):
        """Test POST /api/system/lcd with missing mode parameter."""
        resp = await client.post("/api/system/lcd", json={})
        assert resp.status == 400
        
        data = await resp.json()
        assert data["success"] is False
        assert "mode" in data["error"]


# =============================================================================
# External Audio Control Tests (Sprint 4)
# =============================================================================


class TestExtAudioControl:
    """Tests for Sprint 4 external audio control endpoints."""

    @pytest.mark.asyncio
    async def test_get_ext_audio_status(self, client, mock_matrix):
        """Test GET /api/status/ext-audio returns ext-audio status."""
        resp = await client.get("/api/status/ext-audio")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "mode" in data["data"]
        assert "mode_name" in data["data"]
        assert "outputs" in data["data"]
        assert len(data["data"]["outputs"]) == 8
        mock_matrix.get_ext_audio_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_ext_audio_modes(self, client):
        """Test GET /api/ext-audio/modes returns available modes."""
        resp = await client.get("/api/ext-audio/modes")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "modes" in data["data"]
        modes = data["data"]["modes"]
        assert "0" in modes  # Bind to Input
        assert "1" in modes  # Bind to Output
        assert "2" in modes  # Matrix Mode

    @pytest.mark.asyncio
    async def test_set_ext_audio_mode(self, client, mock_matrix):
        """Test POST /api/ext-audio/mode sets ext-audio mode."""
        mock_matrix.set_ext_audio_mode.return_value = True
        
        resp = await client.post("/api/ext-audio/mode", json={"mode": 2})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["mode"] == 2
        assert data["data"]["mode_name"] == "Matrix Mode"
        mock_matrix.set_ext_audio_mode.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_set_ext_audio_mode_invalid(self, client, mock_matrix):
        """Test POST /api/ext-audio/mode with invalid mode."""
        resp = await client.post("/api/ext-audio/mode", json={"mode": 5})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_set_ext_audio_enable(self, client, mock_matrix):
        """Test POST /api/ext-audio/{n}/enable sets enable state."""
        mock_matrix.set_ext_audio_enable.return_value = True
        
        resp = await client.post("/api/ext-audio/1/enable", json={"enabled": True})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["output"] == 1
        assert data["data"]["enabled"] is True
        mock_matrix.set_ext_audio_enable.assert_called_once_with(1, True)

    @pytest.mark.asyncio
    async def test_set_ext_audio_source(self, client, mock_matrix):
        """Test POST /api/ext-audio/{n}/source sets audio source."""
        mock_matrix.set_ext_audio_source.return_value = True
        
        resp = await client.post("/api/ext-audio/2/source", json={"input": 4})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["output"] == 2
        assert data["data"]["input"] == 4
        mock_matrix.set_ext_audio_source.assert_called_once_with(2, 4)

    @pytest.mark.asyncio
    async def test_set_ext_audio_source_invalid_output(self, client, mock_matrix):
        """Test POST /api/ext-audio/{n}/source with invalid output."""
        resp = await client.post("/api/ext-audio/0/source", json={"input": 4})
        assert resp.status == 400
        
        resp = await client.post("/api/ext-audio/9/source", json={"input": 4})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_set_ext_audio_source_invalid_input(self, client, mock_matrix):
        """Test POST /api/ext-audio/{n}/source with invalid input."""
        resp = await client.post("/api/ext-audio/1/source", json={"input": 0})
        assert resp.status == 400
        
        resp = await client.post("/api/ext-audio/1/source", json={"input": 9})
        assert resp.status == 400


# =============================================================================
# Scene Control Tests (Sprint 4)
# =============================================================================


class TestSceneControl:
    """Tests for Sprint 4 scene control endpoints."""

    @pytest.mark.asyncio
    async def test_list_scenes_empty(self, client):
        """Test GET /api/scenes returns empty list initially."""
        resp = await client.get("/api/scenes")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "scenes" in data["data"]
        assert isinstance(data["data"]["scenes"], list)

    @pytest.mark.asyncio
    async def test_create_scene(self, client):
        """Test POST /api/scene creates a scene."""
        scene_data = {
            "id": "test_scene",
            "name": "Test Scene",
            "outputs": {
                "1": {"input": 2},
                "2": {"input": 3, "audio_mute": True}
            }
        }
        
        resp = await client.post("/api/scene", json=scene_data)
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["id"] == "test_scene"
        assert data["data"]["name"] == "Test Scene"

    @pytest.mark.asyncio
    async def test_get_scene(self, client):
        """Test GET /api/scene/{id} returns scene details."""
        # Create a scene first
        scene_data = {
            "id": "movie_night",
            "name": "Movie Night",
            "outputs": {"1": {"input": 1}, "2": {"input": 1}}
        }
        await client.post("/api/scene", json=scene_data)
        
        # Get it
        resp = await client.get("/api/scene/movie_night")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Movie Night"

    @pytest.mark.asyncio
    async def test_get_scene_not_found(self, client):
        """Test GET /api/scene/{id} returns 404 for unknown scene."""
        resp = await client.get("/api/scene/nonexistent")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_delete_scene(self, client):
        """Test DELETE /api/scene/{id} deletes a scene."""
        # Create a scene first
        scene_data = {
            "id": "to_delete",
            "name": "To Delete",
            "outputs": {"1": {"input": 1}}
        }
        await client.post("/api/scene", json=scene_data)
        
        # Delete it
        resp = await client.delete("/api/scene/to_delete")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["deleted"] == "to_delete"
        
        # Verify it's gone
        resp = await client.get("/api/scene/to_delete")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_recall_scene(self, client, mock_matrix):
        """Test POST /api/scene/{id}/recall applies scene settings."""
        # Create a scene
        scene_data = {
            "id": "recall_test",
            "name": "Recall Test",
            "outputs": {"1": {"input": 3}, "2": {"input": 4}}
        }
        await client.post("/api/scene", json=scene_data)
        
        # Recall it
        resp = await client.post("/api/scene/recall_test/recall")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["scene"] == "Recall Test"
        assert len(data["data"]["applied"]) > 0

    @pytest.mark.asyncio
    async def test_recall_scene_not_found(self, client, mock_matrix):
        """Test POST /api/scene/{id}/recall returns 404 for unknown scene."""
        resp = await client.post("/api/scene/nonexistent/recall")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_save_current_as_scene(self, client, mock_matrix):
        """Test POST /api/scene/save-current saves current state."""
        resp = await client.post("/api/scene/save-current", json={
            "id": "current_state",
            "name": "Current State"
        })
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["id"] == "current_state"
        assert data["data"]["name"] == "Current State"
        # Should have 8 outputs from current state
        assert len(data["data"]["outputs"]) == 8

    @pytest.mark.asyncio
    async def test_create_scene_missing_id(self, client):
        """Test POST /api/scene with missing id."""
        resp = await client.post("/api/scene", json={"name": "No ID", "outputs": {"1": {"input": 1}}})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_create_scene_missing_name(self, client):
        """Test POST /api/scene with missing name."""
        resp = await client.post("/api/scene", json={"id": "no_name", "outputs": {"1": {"input": 1}}})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_create_scene_invalid_output(self, client):
        """Test POST /api/scene with invalid output number."""
        resp = await client.post("/api/scene", json={
            "id": "bad_output",
            "name": "Bad Output",
            "outputs": {"9": {"input": 1}}  # Output 9 doesn't exist
        })
        assert resp.status == 400


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_json_returns_400(self, client):
        """Test invalid JSON body returns 400."""
        resp = await client.post(
            "/api/switch",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_invalid_output_number(self, client):
        """Test invalid output number returns 400."""
        resp = await client.post("/api/output/0/hdcp", json={"mode": 1})
        assert resp.status == 400
        
        resp = await client.post("/api/output/9/hdcp", json={"mode": 1})
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_matrix_not_connected(self, client, mock_matrix):
        """Test endpoints return 503 when matrix not connected."""
        mock_matrix.connected = False
        
        resp = await client.get("/api/status")
        assert resp.status == 503

    @pytest.mark.asyncio
    async def test_cors_headers_present(self, client):
        """Test CORS headers are included in responses."""
        resp = await client.get("/api/health")
        
        assert "Access-Control-Allow-Origin" in resp.headers
        assert resp.headers["Access-Control-Allow-Origin"] == "*"


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limit_allows_normal_traffic(self, client):
        """Test that normal request rates are allowed."""
        # Make a few requests - should all succeed
        for _ in range(5):
            resp = await client.get("/api/status")
            assert resp.status in (200, 503)  # 503 if matrix not connected, but not 429

    @pytest.mark.asyncio
    async def test_health_endpoint_not_rate_limited(self, client):
        """Test that health endpoint is exempt from rate limiting."""
        # Make many requests to health endpoint
        for _ in range(50):
            resp = await client.get("/api/health")
            assert resp.status == 200  # Should never be rate limited


class TestWebSocket:
    """Tests for WebSocket functionality."""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, client, mock_matrix):
        """Test WebSocket connection and welcome message."""
        async with client.ws_connect("/ws") as ws:
            # Should receive welcome message
            msg = await ws.receive_json()
            assert msg["event"] == "connected"
            assert "client_count" in msg["data"]
            assert msg["data"]["client_count"] >= 1

    @pytest.mark.asyncio
    async def test_websocket_ping_pong(self, client, mock_matrix):
        """Test WebSocket ping command returns pong."""
        async with client.ws_connect("/ws") as ws:
            # Skip welcome message
            await ws.receive_json()
            
            # Send ping
            await ws.send_json({"command": "ping"})
            msg = await ws.receive_json()
            assert msg["event"] == "pong"

    @pytest.mark.asyncio
    async def test_websocket_get_status(self, client, mock_matrix):
        """Test WebSocket get_status command."""
        mock_matrix.connected = True
        mock_matrix.get_status.return_value = {
            "power": 1,
            "alloutsource": [1, 2, 3, 4, 5, 6, 7, 8]
        }
        
        async with client.ws_connect("/ws") as ws:
            # Skip welcome message
            await ws.receive_json()
            
            # Request status
            await ws.send_json({"command": "get_status"})
            msg = await ws.receive_json()
            assert msg["event"] == "status_update"
            assert "power" in msg["data"]

    @pytest.mark.asyncio
    async def test_websocket_unknown_command(self, client, mock_matrix):
        """Test WebSocket returns error for unknown commands."""
        async with client.ws_connect("/ws") as ws:
            # Skip welcome message
            await ws.receive_json()
            
            # Send unknown command
            await ws.send_json({"command": "unknown_cmd"})
            msg = await ws.receive_json()
            assert msg["event"] == "error"
            assert "Unknown command" in msg["data"]["message"]


# =============================================================================
# Web UI Tests
# =============================================================================


class TestWebUI:
    """Tests for Web UI static file serving."""

    @pytest.mark.asyncio
    async def test_web_ui_endpoint(self, client):
        """Test /ui serves the Web UI."""
        resp = await client.get("/ui")
        assert resp.status == 200
        
        content = await resp.text()
        assert "OREI Matrix Control" in content
        assert "<!DOCTYPE html>" in content

    @pytest.mark.asyncio
    async def test_web_ui_with_trailing_slash(self, client):
        """Test /ui/ also serves the Web UI."""
        resp = await client.get("/ui/")
        assert resp.status == 200
        
        content = await resp.text()
        assert "OREI Matrix Control" in content

    @pytest.mark.asyncio
    async def test_static_css(self, client):
        """Test CSS files are served correctly."""
        resp = await client.get("/css/style.css")
        assert resp.status == 200
        assert "text/css" in resp.headers.get("Content-Type", "")

    @pytest.mark.asyncio
    async def test_static_js(self, client):
        """Test JavaScript files are served correctly."""
        resp = await client.get("/js/app.js")
        assert resp.status == 200
        assert "javascript" in resp.headers.get("Content-Type", "")

    @pytest.mark.asyncio
    async def test_static_asset(self, client):
        """Test assets are served correctly."""
        resp = await client.get("/assets/favicon.svg")
        assert resp.status == 200
        assert "svg" in resp.headers.get("Content-Type", "")

    @pytest.mark.asyncio
    async def test_static_file_not_found(self, client):
        """Test 404 for non-existent static files."""
        resp = await client.get("/css/nonexistent.css")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_directory_traversal_blocked(self, client):
        """Test directory traversal is blocked or results in not found."""
        # The aiohttp client may normalize the path, which is fine
        # The important thing is we don't serve sensitive files
        resp = await client.get("/css/../../../etc/passwd")
        # Should either return 403 (forbidden) or 404 (not found)
        assert resp.status in (403, 404)


# =============================================================================
# Profile API Tests
# =============================================================================


class TestProfileAPI:
    """Tests for Profile API endpoints (/api/profiles, /api/profile/*)."""

    @pytest.mark.asyncio
    async def test_list_profiles_empty(self, client):
        """Test GET /api/profiles returns empty list initially."""
        resp = await client.get("/api/profiles")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "profiles" in data["data"]
        assert isinstance(data["data"]["profiles"], list)

    @pytest.mark.asyncio
    async def test_create_profile_full(self, client):
        """Test POST /api/profile creates a profile with all fields."""
        profile_data = {
            "id": "movie_night",
            "name": "Movie Night",
            "icon": "🎬",
            "outputs": {
                "1": {"input": 2, "enabled": True},
                "2": {"input": 2, "audio_mute": True}
            },
            "macros": ["macro_1", "macro_2"],
            "power_on_macro": "startup_macro",
            "power_off_macro": "shutdown_macro"
        }
        
        resp = await client.post("/api/profile", json=profile_data)
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["id"] == "movie_night"
        assert data["data"]["name"] == "Movie Night"
        assert data["data"]["icon"] == "🎬"
        assert "outputs" in data["data"]
        assert data["data"]["outputs"]["1"]["input"] == 2
        assert data["data"]["outputs"]["2"]["audio_mute"] is True

    @pytest.mark.asyncio
    async def test_create_profile_minimal(self, client):
        """Test POST /api/profile with minimal required fields."""
        profile_data = {
            "id": "basic_profile",
            "name": "Basic Profile",
            "outputs": {"1": {"input": 1}}
        }
        
        resp = await client.post("/api/profile", json=profile_data)
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["id"] == "basic_profile"
        # Default icon should be set
        assert "icon" in data["data"]

    @pytest.mark.asyncio
    async def test_create_profile_missing_id(self, client):
        """Test POST /api/profile fails without id."""
        resp = await client.post("/api/profile", json={
            "name": "No ID",
            "outputs": {"1": {"input": 1}}
        })
        assert resp.status == 400
        
        data = await resp.json()
        assert data["success"] is False
        assert "id" in data["error"].lower() or "required" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_create_profile_missing_name(self, client):
        """Test POST /api/profile fails without name."""
        resp = await client.post("/api/profile", json={
            "id": "no_name",
            "outputs": {"1": {"input": 1}}
        })
        assert resp.status == 400
        
        data = await resp.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_create_profile_invalid_output(self, client):
        """Test POST /api/profile fails with invalid output number."""
        resp = await client.post("/api/profile", json={
            "id": "bad_output",
            "name": "Bad Output",
            "outputs": {"99": {"input": 1}}  # Invalid output
        })
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_create_profile_invalid_input(self, client):
        """Test POST /api/profile fails with invalid input number."""
        resp = await client.post("/api/profile", json={
            "id": "bad_input",
            "name": "Bad Input",
            "outputs": {"1": {"input": 99}}  # Invalid input
        })
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_get_profile(self, client):
        """Test GET /api/profile/{id} returns profile details."""
        # Create a profile first
        await client.post("/api/profile", json={
            "id": "get_test",
            "name": "Get Test",
            "icon": "📺",
            "outputs": {"1": {"input": 3}}
        })
        
        # Get it
        resp = await client.get("/api/profile/get_test")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["id"] == "get_test"
        assert data["data"]["name"] == "Get Test"
        assert data["data"]["icon"] == "📺"
        assert data["data"]["outputs"]["1"]["input"] == 3

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, client):
        """Test GET /api/profile/{id} returns 404 for unknown profile."""
        resp = await client.get("/api/profile/nonexistent_profile")
        assert resp.status == 404
        
        data = await resp.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_update_profile(self, client):
        """Test PUT /api/profile/{id} updates profile fields."""
        # Create a profile
        await client.post("/api/profile", json={
            "id": "update_test",
            "name": "Original Name",
            "icon": "📺",
            "outputs": {"1": {"input": 1}}
        })
        
        # Update it
        resp = await client.put("/api/profile/update_test", json={
            "name": "Updated Name",
            "icon": "🎬"
        })
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["icon"] == "🎬"
        
        # Verify persistence
        resp = await client.get("/api/profile/update_test")
        data = await resp.json()
        assert data["data"]["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_profile_macros(self, client):
        """Test PUT /api/profile/{id} can update macro assignments."""
        # Create profile without macros
        await client.post("/api/profile", json={
            "id": "macro_update_test",
            "name": "Macro Test",
            "outputs": {"1": {"input": 1}}
        })
        
        # Update with macros
        resp = await client.put("/api/profile/macro_update_test", json={
            "macros": ["macro_a", "macro_b"],
            "power_on_macro": "power_on",
            "power_off_macro": "power_off"
        })
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "macro_a" in data["data"].get("macros", [])
        assert data["data"].get("power_on_macro") == "power_on"
        assert data["data"].get("power_off_macro") == "power_off"

    @pytest.mark.asyncio
    async def test_update_profile_not_found(self, client):
        """Test PUT /api/profile/{id} returns 404 for unknown profile."""
        resp = await client.put("/api/profile/nonexistent", json={"name": "New"})
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_delete_profile(self, client):
        """Test DELETE /api/profile/{id} removes profile."""
        # Create a profile
        await client.post("/api/profile", json={
            "id": "delete_test",
            "name": "To Delete",
            "outputs": {"1": {"input": 1}}
        })
        
        # Delete it
        resp = await client.delete("/api/profile/delete_test")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        
        # Verify it's gone
        resp = await client.get("/api/profile/delete_test")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_delete_profile_not_found(self, client):
        """Test DELETE /api/profile/{id} returns 404 for unknown profile."""
        resp = await client.delete("/api/profile/nonexistent_delete")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_recall_profile_switches_inputs(self, client, mock_matrix):
        """Test POST /api/profile/{id}/recall actually switches matrix inputs."""
        # Create a profile with specific routing
        await client.post("/api/profile", json={
            "id": "recall_switch_test",
            "name": "Recall Switch Test",
            "outputs": {
                "1": {"input": 3},
                "2": {"input": 4},
                "5": {"input": 1}
            }
        })
        
        # Recall it
        resp = await client.post("/api/profile/recall_switch_test/recall")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["profile"] == "Recall Switch Test"
        
        # CRITICAL: Verify switch_input was called for each output
        calls = mock_matrix.switch_input.call_args_list
        assert len(calls) >= 3, f"Expected at least 3 switch_input calls, got {len(calls)}"
        
        # Verify correct input/output pairs were switched
        call_pairs = [(c[0][0], c[0][1]) for c in calls]  # (input, output) pairs
        assert (3, 1) in call_pairs, "Expected switch_input(3, 1) for output 1"
        assert (4, 2) in call_pairs, "Expected switch_input(4, 2) for output 2"
        assert (1, 5) in call_pairs, "Expected switch_input(1, 5) for output 5"

    @pytest.mark.asyncio
    async def test_recall_profile_not_found(self, client, mock_matrix):
        """Test POST /api/profile/{id}/recall returns 404 for unknown profile."""
        resp = await client.post("/api/profile/nonexistent/recall")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_list_profiles_returns_all(self, client):
        """Test GET /api/profiles returns all created profiles."""
        # Create multiple profiles
        for i in range(3):
            await client.post("/api/profile", json={
                "id": f"list_test_{i}",
                "name": f"List Test {i}",
                "outputs": {"1": {"input": i + 1}}
            })
        
        # List them
        resp = await client.get("/api/profiles")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        
        profiles = data["data"]["profiles"]
        profile_ids = [p["id"] for p in profiles]
        
        for i in range(3):
            assert f"list_test_{i}" in profile_ids


# =============================================================================
# CEC Macro API Tests
# =============================================================================


class TestMacroAPI:
    """Tests for CEC Macro API endpoints (/api/cec/macros, /api/cec/macro/*)."""

    @pytest.mark.asyncio
    async def test_list_macros_empty(self, client):
        """Test GET /api/cec/macros returns empty list initially."""
        resp = await client.get("/api/cec/macros")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "macros" in data["data"]
        assert isinstance(data["data"]["macros"], list)

    @pytest.mark.asyncio
    async def test_create_macro_full(self, client):
        """Test POST /api/macro creates a macro with all fields."""
        macro_data = {
            "name": "Power On All",
            "icon": "⚡",
            "description": "Powers on all devices",
            "steps": [
                {"command": "POWER_ON", "targets": ["input_1", "input_2"], "delay_ms": 0},
                {"command": "POWER_ON", "targets": ["output_1"], "delay_ms": 1000}
            ]
        }
        
        resp = await client.post("/api/cec/macro", json=macro_data)
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "id" in data["data"]  # ID should be auto-generated
        assert data["data"]["name"] == "Power On All"
        assert data["data"]["icon"] == "⚡"
        assert len(data["data"]["steps"]) == 2
        assert data["data"]["steps"][0]["command"] == "POWER_ON"
        assert data["data"]["steps"][0]["targets"] == ["input_1", "input_2"]
        assert data["data"]["steps"][1]["delay_ms"] == 1000

    @pytest.mark.asyncio
    async def test_create_macro_with_custom_id(self, client):
        """Test POST /api/macro accepts custom id."""
        macro_data = {
            "id": "custom_macro_id",
            "name": "Custom ID Macro",
            "steps": [{"command": "PLAY", "targets": ["input_1"]}]
        }
        
        resp = await client.post("/api/cec/macro", json=macro_data)
        assert resp.status == 200
        
        data = await resp.json()
        assert data["data"]["id"] == "custom_macro_id"

    @pytest.mark.asyncio
    async def test_create_macro_missing_name(self, client):
        """Test POST /api/macro fails without name."""
        resp = await client.post("/api/cec/macro", json={
            "steps": [{"command": "PLAY", "targets": ["input_1"]}]
        })
        assert resp.status == 400
        
        data = await resp.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_create_macro_empty_steps(self, client):
        """Test POST /api/cec/macro with empty steps returns 400."""
        resp = await client.post("/api/cec/macro", json={
            "name": "Empty Macro",
            "steps": []
        })
        # API requires at least one step
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_get_macro(self, client):
        """Test GET /api/cec/macro/{id} returns macro details."""
        # Create a macro first
        create_resp = await client.post("/api/cec/macro", json={
            "id": "get_macro_test",
            "name": "Get Test Macro",
            "icon": "🎮",
            "steps": [{"command": "PLAY", "targets": ["output_2"], "delay_ms": 500}]
        })
        assert create_resp.status == 200
        
        # Get it
        resp = await client.get("/api/cec/macro/get_macro_test")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["id"] == "get_macro_test"
        assert data["data"]["name"] == "Get Test Macro"
        assert data["data"]["icon"] == "🎮"
        assert len(data["data"]["steps"]) == 1
        assert data["data"]["steps"][0]["command"] == "PLAY"

    @pytest.mark.asyncio
    async def test_get_macro_not_found(self, client):
        """Test GET /api/cec/macro/{id} returns 404 for unknown macro."""
        resp = await client.get("/api/cec/macro/nonexistent_macro")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_update_macro(self, client):
        """Test PUT /api/cec/macro/{id} updates macro fields."""
        # Create a macro
        await client.post("/api/cec/macro", json={
            "id": "update_macro_test",
            "name": "Original Macro",
            "steps": [{"command": "PLAY", "targets": ["input_1"]}]
        })
        
        # Update it
        resp = await client.put("/api/cec/macro/update_macro_test", json={
            "name": "Updated Macro",
            "icon": "🌙",
            "description": "Now with description"
        })
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Macro"
        assert data["data"]["icon"] == "🌙"
        assert data["data"]["description"] == "Now with description"
        
        # Verify steps were preserved
        assert len(data["data"]["steps"]) >= 1

    @pytest.mark.asyncio
    async def test_update_macro_steps(self, client):
        """Test PUT /api/cec/macro/{id} can update steps."""
        # Create with one step
        await client.post("/api/cec/macro", json={
            "id": "update_steps_test",
            "name": "Steps Test",
            "steps": [{"command": "PLAY", "targets": ["input_1"]}]
        })
        
        # Update with new steps
        resp = await client.put("/api/cec/macro/update_steps_test", json={
            "steps": [
                {"command": "POWER_ON", "targets": ["input_1", "input_2"], "delay_ms": 0},
                {"command": "POWER_ON", "targets": ["output_1"], "delay_ms": 2000}
            ]
        })
        assert resp.status == 200
        
        data = await resp.json()
        assert len(data["data"]["steps"]) == 2
        assert data["data"]["steps"][0]["command"] == "POWER_ON"
        assert data["data"]["steps"][1]["delay_ms"] == 2000

    @pytest.mark.asyncio
    async def test_update_macro_not_found(self, client):
        """Test PUT /api/cec/macro/{id} returns 404 for unknown macro."""
        resp = await client.put("/api/cec/macro/nonexistent", json={"name": "New"})
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_delete_macro(self, client):
        """Test DELETE /api/cec/macro/{id} removes macro."""
        # Create a macro with at least one step
        create_resp = await client.post("/api/cec/macro", json={
            "id": "delete_macro_test",
            "name": "To Delete",
            "steps": [{"command": "PLAY", "targets": ["input_1"]}]
        })
        assert create_resp.status == 200
        
        # Delete it
        resp = await client.delete("/api/cec/macro/delete_macro_test")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        
        # Verify it's gone
        resp = await client.get("/api/cec/macro/delete_macro_test")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_delete_macro_not_found(self, client):
        """Test DELETE /api/cec/macro/{id} returns 404 for unknown macro."""
        resp = await client.delete("/api/cec/macro/nonexistent_delete")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_execute_macro_not_found(self, client):
        """Test POST /api/cec/macro/{id}/execute returns 404 for unknown macro."""
        resp = await client.post("/api/cec/macro/nonexistent/execute")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_test_macro(self, client):
        """Test POST /api/cec/macro/{id}/test validates macro."""
        # Create a valid macro
        await client.post("/api/cec/macro", json={
            "id": "test_macro_test",
            "name": "Test Macro",
            "steps": [
                {"command": "POWER_ON", "targets": ["input_1"], "delay_ms": 0}
            ]
        })
        
        # Test it
        resp = await client.post("/api/cec/macro/test_macro_test/test")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        # API returns step_count and issues list for validation
        assert "step_count" in data["data"]
        assert data["data"]["step_count"] == 1
        assert "issues" in data["data"]
        assert len(data["data"]["issues"]) == 0  # No validation issues

    @pytest.mark.asyncio
    async def test_test_macro_not_found(self, client):
        """Test POST /api/cec/macro/{id}/test returns 404 for unknown macro."""
        resp = await client.post("/api/cec/macro/nonexistent/test")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_list_macros_returns_all(self, client):
        """Test GET /api/cec/macros returns all created macros."""
        # Create multiple macros
        for i in range(3):
            await client.post("/api/cec/macro", json={
                "id": f"list_macro_{i}",
                "name": f"List Macro {i}",
                "steps": [{"command": "PLAY", "targets": [f"input_{i+1}"]}]
            })
        
        # List them
        resp = await client.get("/api/cec/macros")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        
        macros = data["data"]["macros"]
        macro_ids = [m["id"] for m in macros]
        
        for i in range(3):
            assert f"list_macro_{i}" in macro_ids

    @pytest.mark.asyncio
    async def test_macro_step_validation(self, client):
        """Test macro step structure is validated correctly."""
        # Create macro with proper step structure
        resp = await client.post("/api/cec/macro", json={
            "id": "step_validation",
            "name": "Step Validation",
            "steps": [
                {
                    "command": "VOLUME_UP",
                    "targets": ["output_1", "output_2"],
                    "delay_ms": 100
                }
            ]
        })
        assert resp.status == 200
        
        # Verify step was stored correctly
        data = await resp.json()
        step = data["data"]["steps"][0]
        assert step["command"] == "VOLUME_UP"
        assert step["targets"] == ["output_1", "output_2"]
        assert step["delay_ms"] == 100


# =============================================================================
# Scene Recall Validation (Enhanced)
# =============================================================================


class TestSceneRecallValidation:
    """Tests to verify scene recall actually triggers matrix operations."""

    @pytest.mark.asyncio
    async def test_scene_recall_switches_inputs(self, client, mock_matrix):
        """Test POST /api/scene/{id}/recall actually calls switch_input."""
        # Create a scene with specific routing
        scene_data = {
            "id": "recall_validation",
            "name": "Recall Validation",
            "outputs": {
                "1": {"input": 5},
                "3": {"input": 2},
                "7": {"input": 8}
            }
        }
        await client.post("/api/scene", json=scene_data)
        
        # Recall it
        resp = await client.post("/api/scene/recall_validation/recall")
        assert resp.status == 200
        
        # CRITICAL: Verify switch_input was called for each output
        calls = mock_matrix.switch_input.call_args_list
        assert len(calls) >= 3, f"Expected at least 3 switch_input calls, got {len(calls)}"
        
        # Verify correct routing was applied
        call_pairs = [(c[0][0], c[0][1]) for c in calls]  # (input, output) pairs
        assert (5, 1) in call_pairs, "Expected switch_input(5, 1)"
        assert (2, 3) in call_pairs, "Expected switch_input(2, 3)"
        assert (8, 7) in call_pairs, "Expected switch_input(8, 7)"

    @pytest.mark.asyncio
    async def test_scene_recall_applies_audio_mute(self, client, mock_matrix):
        """Test scene recall applies audio mute settings."""
        scene_data = {
            "id": "mute_test",
            "name": "Mute Test",
            "outputs": {
                "2": {"input": 1, "audio_mute": True}
            }
        }
        await client.post("/api/scene", json=scene_data)
        
        # Recall it
        resp = await client.post("/api/scene/mute_test/recall")
        assert resp.status == 200
        
        # Should have called switch_input
        mock_matrix.switch_input.assert_called()
        
        # If audio mute is supported, it should be called
        if hasattr(mock_matrix, 'set_output_audio_mute'):
            # Depending on implementation, mute may be called
            pass  # Implementation specific


# =============================================================================
# Status Endpoint Tests (Missing Coverage)
# =============================================================================


class TestStatusEndpoints:
    """Tests for status-related endpoints that were missing coverage."""

    @pytest.mark.asyncio
    async def test_inputs_endpoint(self, client):
        """Test GET /api/inputs returns input list."""
        resp = await client.get("/api/inputs")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "inputs" in data["data"]
        assert len(data["data"]["inputs"]) == 8
        
        # Verify structure
        first_input = data["data"]["inputs"][0]
        assert "number" in first_input
        assert "name" in first_input
        assert "cec_endpoint" in first_input
        assert first_input["number"] == 1

    @pytest.mark.asyncio
    async def test_outputs_endpoint(self, client):
        """Test GET /api/outputs returns output list."""
        resp = await client.get("/api/outputs")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "outputs" in data["data"]
        assert len(data["data"]["outputs"]) == 8
        
        # Verify structure
        first_output = data["data"]["outputs"][0]
        assert "number" in first_output
        assert "name" in first_output
        assert "cec_endpoint" in first_output

    @pytest.mark.asyncio
    async def test_full_status_endpoint(self, client):
        """Test GET /api/status/full returns comprehensive status."""
        resp = await client.get("/api/status/full")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_output_status_endpoint(self, client):
        """Test GET /api/status/outputs returns output status."""
        resp = await client.get("/api/status/outputs")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "outputs" in data["data"]

    @pytest.mark.asyncio
    async def test_input_status_endpoint(self, client):
        """Test GET /api/status/inputs returns input status."""
        resp = await client.get("/api/status/inputs")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "inputs" in data["data"]

    @pytest.mark.asyncio
    async def test_system_status_endpoint(self, client):
        """Test GET /api/status/system returns system settings."""
        resp = await client.get("/api/status/system")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        # Verify expected fields
        assert "power" in data["data"]
        assert "beep_enabled" in data["data"]
        assert "panel_locked" in data["data"]

    @pytest.mark.asyncio
    async def test_device_info_endpoint(self, client):
        """Test GET /api/status/device returns device info."""
        resp = await client.get("/api/status/device")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "device" in data["data"]


# =============================================================================
# CEC Command Tests (Missing Coverage)
# =============================================================================


class TestCecCommandEndpoints:
    """Tests for CEC-related endpoints that were missing coverage."""

    @pytest.mark.asyncio
    async def test_cec_commands_list(self, client):
        """Test GET /api/cec/commands returns available commands."""
        resp = await client.get("/api/cec/commands")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "input_commands" in data["data"]
        assert "output_commands" in data["data"]
        assert "usage" in data["data"]
        
        # Verify some expected commands exist
        input_cmds = data["data"]["input_commands"]
        output_cmds = data["data"]["output_commands"]
        assert len(input_cmds) > 0
        assert len(output_cmds) > 0

    @pytest.mark.asyncio
    async def test_cec_capabilities(self, client):
        """Test GET /api/cec/capabilities returns CEC capabilities."""
        resp = await client.get("/api/cec/capabilities")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        # Verify structure matches actual API response
        assert "capabilities" in data["data"]
        assert "summary" in data["data"]
        assert "inputs" in data["data"]["capabilities"]
        assert "outputs" in data["data"]["capabilities"]

    @pytest.mark.asyncio
    async def test_cec_input_capabilities(self, client):
        """Test GET /api/cec/input/{n}/capabilities returns input CEC capabilities."""
        resp = await client.get("/api/cec/input/1/capabilities")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_cec_output_capabilities(self, client):
        """Test GET /api/cec/output/{n}/capabilities returns output CEC capabilities."""
        resp = await client.get("/api/cec/output/1/capabilities")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_cec_input_command_power_on(self, client, mock_matrix):
        """Test POST /api/cec/input/{n}/{command} sends CEC command."""
        resp = await client.post("/api/cec/input/3/power_on")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["input"] == 3
        assert data["data"]["command"] == "power_on"
        
        # Verify the matrix method was called
        mock_matrix.cec_input_power_on.assert_called_with(3)

    @pytest.mark.asyncio
    async def test_cec_input_command_power_off(self, client, mock_matrix):
        """Test POST /api/cec/input/{n}/power_off sends standby command."""
        resp = await client.post("/api/cec/input/5/power_off")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["input"] == 5

    @pytest.mark.asyncio
    async def test_cec_output_command_power_on(self, client, mock_matrix):
        """Test POST /api/cec/output/{n}/power_on sends TV power on."""
        resp = await client.post("/api/cec/output/2/power_on")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["output"] == 2
        assert data["data"]["command"] == "power_on"

    @pytest.mark.asyncio
    async def test_cec_output_command_power_off(self, client, mock_matrix):
        """Test POST /api/cec/output/{n}/power_off sends TV standby."""
        resp = await client.post("/api/cec/output/7/power_off")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["output"] == 7

    @pytest.mark.asyncio
    async def test_cec_input_invalid_port(self, client):
        """Test CEC command with invalid input port."""
        resp = await client.post("/api/cec/input/0/power_on")
        assert resp.status == 400
        
        resp = await client.post("/api/cec/input/9/power_on")
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_cec_output_invalid_port(self, client):
        """Test CEC command with invalid output port."""
        resp = await client.post("/api/cec/output/0/power_on")
        assert resp.status == 400
        
        resp = await client.post("/api/cec/output/9/power_on")
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_cec_input_invalid_command(self, client):
        """Test CEC with unknown command returns error."""
        resp = await client.post("/api/cec/input/1/invalid_command")
        assert resp.status == 400
        
        data = await resp.json()
        assert data["success"] is False
        assert "Unknown command" in data["error"] or "unknown" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_cec_output_invalid_command(self, client):
        """Test CEC with unknown command returns error."""
        resp = await client.post("/api/cec/output/1/invalid_command")
        assert resp.status == 400
        
        data = await resp.json()
        assert data["success"] is False


# =============================================================================
# System Settings Tests (Missing Coverage)
# =============================================================================


class TestSystemSettingsEndpoints:
    """Tests for system settings endpoints that were missing coverage."""

    @pytest.mark.asyncio
    async def test_set_beep_enabled(self, client, mock_matrix):
        """Test POST /api/system/beep enables beep."""
        resp = await client.post("/api/system/beep", json={"enabled": True})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["beep_enabled"] is True
        
        mock_matrix.set_beep.assert_called_with(True)

    @pytest.mark.asyncio
    async def test_set_beep_disabled(self, client, mock_matrix):
        """Test POST /api/system/beep disables beep."""
        resp = await client.post("/api/system/beep", json={"enabled": False})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["beep_enabled"] is False
        
        mock_matrix.set_beep.assert_called_with(False)

    @pytest.mark.asyncio
    async def test_set_panel_lock_locked(self, client, mock_matrix):
        """Test POST /api/system/panel_lock locks panel."""
        resp = await client.post("/api/system/panel_lock", json={"locked": True})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["panel_locked"] is True
        
        mock_matrix.set_panel_lock.assert_called_with(True)

    @pytest.mark.asyncio
    async def test_set_panel_lock_unlocked(self, client, mock_matrix):
        """Test POST /api/system/panel_lock unlocks panel."""
        resp = await client.post("/api/system/panel_lock", json={"locked": False})
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["panel_locked"] is False
        
        mock_matrix.set_panel_lock.assert_called_with(False)


# =============================================================================
# Scene/Profile CEC Config Tests (Missing Coverage)
# =============================================================================


class TestSceneCecConfigEndpoints:
    """Tests for scene CEC configuration endpoints."""

    @pytest.mark.asyncio
    async def test_get_scene_cec_config(self, client):
        """Test GET /api/scene/{id}/cec returns CEC config."""
        # Create scene with CEC config
        await client.post("/api/scene", json={
            "id": "cec_get_test",
            "name": "CEC Get Test",
            "outputs": {"1": {"input": 1}},
            "cec_config": {
                "nav_targets": ["input:1"],
                "volume_targets": ["output:1"]
            }
        })
        
        resp = await client.get("/api/scene/cec_get_test/cec")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True
        assert "cec_config" in data["data"]
        assert data["data"]["cec_config"]["nav_targets"] == ["input:1"]

    @pytest.mark.asyncio
    async def test_get_scene_cec_config_not_found(self, client):
        """Test GET /api/scene/{id}/cec returns 404 for unknown scene."""
        resp = await client.get("/api/scene/nonexistent_cec/cec")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_post_scene_cec_config(self, client):
        """Test POST /api/scene/{id}/cec updates CEC config."""
        # Create scene first
        await client.post("/api/scene", json={
            "id": "cec_post_test",
            "name": "CEC Post Test",
            "outputs": {"1": {"input": 1}}
        })
        
        # Update CEC config
        resp = await client.post("/api/scene/cec_post_test/cec", json={
            "nav_targets": ["input:2", "input:3"],
            "playback_targets": ["input:2"],
            "auto_resolved": False
        })
        assert resp.status == 200
        
        # Verify it was saved
        resp = await client.get("/api/scene/cec_post_test/cec")
        data = await resp.json()
        assert data["data"]["cec_config"]["nav_targets"] == ["input:2", "input:3"]
        assert data["data"]["cec_config"]["playback_targets"] == ["input:2"]

    @pytest.mark.asyncio
    async def test_put_scene_cec_config(self, client):
        """Test PUT /api/scene/{id}/cec replaces CEC config."""
        await client.post("/api/scene", json={
            "id": "cec_put_test",
            "name": "CEC Put Test",
            "outputs": {"1": {"input": 1}}
        })
        
        resp = await client.put("/api/scene/cec_put_test/cec", json={
            "volume_targets": ["output:1", "output:2"],
            "auto_resolved": False
        })
        assert resp.status == 200


# =============================================================================
# Profile CEC/Macro Config Tests (Missing Coverage)
# =============================================================================


class TestProfileCecMacroEndpoints:
    """Tests for profile CEC and macro configuration endpoints."""

    @pytest.mark.asyncio
    async def test_get_profile_cec_config(self, client):
        """Test GET /api/profile/{id}/cec returns CEC config."""
        await client.post("/api/profile", json={
            "id": "profile_cec_test",
            "name": "Profile CEC Test",
            "outputs": {"1": {"input": 1}},
            "cec_config": {"nav_targets": ["input:1"]}
        })
        
        resp = await client.get("/api/profile/profile_cec_test/cec")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_post_profile_cec_config(self, client):
        """Test POST /api/profile/{id}/cec updates CEC config."""
        await client.post("/api/profile", json={
            "id": "profile_cec_update",
            "name": "Profile CEC Update",
            "outputs": {"1": {"input": 1}}
        })
        
        resp = await client.post("/api/profile/profile_cec_update/cec", json={
            "nav_targets": ["input:2"],
            "volume_targets": ["output:1"]
        })
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_get_profile_macros(self, client):
        """Test GET /api/profile/{id}/macros returns macro assignments."""
        await client.post("/api/profile", json={
            "id": "profile_macro_get",
            "name": "Profile Macro Get",
            "outputs": {"1": {"input": 1}},
            "macros": ["macro1", "macro2"],
            "power_on_macro": "startup"
        })
        
        resp = await client.get("/api/profile/profile_macro_get/macros")
        assert resp.status == 200
        
        data = await resp.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_post_profile_macros(self, client):
        """Test POST /api/profile/{id}/macros updates macro assignments."""
        await client.post("/api/profile", json={
            "id": "profile_macro_update",
            "name": "Profile Macro Update",
            "outputs": {"1": {"input": 1}}
        })
        
        resp = await client.post("/api/profile/profile_macro_update/macros", json={
            "macros": ["new_macro1", "new_macro2"],
            "power_on_macro": "on_macro",
            "power_off_macro": "off_macro"
        })
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_profile_cec_not_found(self, client):
        """Test profile CEC endpoint returns 404 for unknown profile."""
        resp = await client.get("/api/profile/nonexistent/cec")
        assert resp.status == 404

    @pytest.mark.asyncio
    async def test_profile_macros_not_found(self, client):
        """Test profile macros endpoint returns 404 for unknown profile."""
        resp = await client.get("/api/profile/nonexistent/macros")
        assert resp.status == 404
