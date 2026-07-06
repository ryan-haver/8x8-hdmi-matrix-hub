"""Tests for the OREI HDMI Matrix HACS integration.

These tests require Home Assistant to be installed.
Install with: ``pip install homeassistant``

They validate that the coordinator correctly processes REST API response shapes.
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Skip all tests in this file if homeassistant is not installed.
try:
    import homeassistant  # noqa: F401
    from homeassistant.config_entries import ConfigFlowResult  # noqa: F401
    from homeassistant.core import HomeAssistant  # noqa: F401

    from custom_components.hdmi_matrix.config_flow import OreiMatrixConfigFlow
    from custom_components.hdmi_matrix.const import DOMAIN
    from custom_components.hdmi_matrix.coordinator import OreiMatrixCoordinator

    HAS_HOMEASSISTANT = True
except ImportError:
    HAS_HOMEASSISTANT = False

pytestmark = pytest.mark.skipif(
    not HAS_HOMEASSISTANT,
    reason="Home Assistant is not installed. Install with: pip install homeassistant",
)


@pytest.mark.asyncio
async def test_config_flow_success():
    """Test successful config flow setup."""
    flow = OreiMatrixConfigFlow()
    flow.hass = MagicMock()

    # Mock response for /api/health
    mock_resp = MagicMock()
    mock_resp.status = 200

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_resp)

    with patch("custom_components.hdmi_matrix.config_flow.async_get_clientsession", return_value=mock_session):
        result = await flow.async_step_user({"host": "192.168.1.100", "port": 8080})

        assert result["type"] == "create_entry"
        assert result["title"] == "HDMI Matrix (192.168.1.100)"
        assert result["data"] == {"host": "192.168.1.100", "port": 8080}


@pytest.mark.asyncio
async def test_coordinator_update_success():
    """Test DataUpdateCoordinator successful state update."""
    hass = MagicMock()
    coordinator = OreiMatrixCoordinator(hass, "192.168.1.100", 8080)

    # Mock responses for parallel fetches
    # routing is now an array: [input_for_output_1, input_for_output_2, ...]
    mock_status_resp = AsyncMock()
    mock_status_resp.status = 200
    mock_status_resp.json = AsyncMock(
        return_value={
            "success": True,
            "data": {
                "connected": True,
                "routing": [2, 3, 3, 3, 3, 3, 3, 3],
                "input_names": {"1": "NES", "2": "SNES", "3": "Sega"},
                "output_names": {"1": "TV", "2": "Projector"},
            },
        }
    )

    mock_outputs_resp = AsyncMock()
    mock_outputs_resp.status = 200
    mock_outputs_resp.json = AsyncMock(
        return_value={
            "success": True,
            "data": {
                "outputs": [
                    {"number": 1, "name": "TV", "connected": True, "muted": False, "enabled": True},
                    {"number": 2, "name": "Projector", "connected": True, "muted": False, "enabled": True},
                ]
            },
        }
    )

    mock_inputs_resp = AsyncMock()
    mock_inputs_resp.status = 200
    mock_inputs_resp.json = AsyncMock(
        return_value={
            "success": True,
            "data": {
                "inputs": [
                    {"number": 1, "name": "NES", "signal_active": True, "cable_connected": True},
                    {"number": 2, "name": "SNES", "signal_active": True, "cable_connected": True},
                ]
            },
        }
    )

    mock_session = MagicMock()
    mock_session.get = MagicMock(side_effect=[mock_status_resp, mock_outputs_resp, mock_inputs_resp])

    with patch("custom_components.hdmi_matrix.coordinator.async_get_clientsession", return_value=mock_session):
        data = await coordinator._async_update_data()

        assert data["status"]["connected"] is True
        # routing is now an array
        assert data["status"]["routing"][0] == 2
        assert data["status"]["routing"][1] == 3
        assert data["outputs"][0]["number"] == 1
        assert data["inputs"][0]["signal_active"] is True
