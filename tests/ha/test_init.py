"""Setup/unload and coordinator tests.

Ported from tests/test_hacs_integration.py::test_coordinator_update_success and
tests/test_ha_robustness.py::TestCoordinatorNullDataHandling (F10.1). They now
run with a real hass against the contract fixtures.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hdmi_matrix.const import DOMAIN

from .helpers import MockHub, load_fixture

SERVICES = ("recall_preset", "switch_input", "send_cec_command")


async def test_setup_and_unload_entry(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """The entry loads, registers the services, and unloads cleanly."""
    entry = setup_integration
    assert entry.state is ConfigEntryState.LOADED
    for service in SERVICES:
        assert hass.services.has_service(DOMAIN, service)

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED
    for service in SERVICES:
        assert not hass.services.has_service(DOMAIN, service)


async def test_setup_retries_when_hub_unreachable(
    hass: HomeAssistant, hub: MockHub, config_entry: MockConfigEntry
) -> None:
    """If the first refresh fails, setup is retried (ConfigEntryNotReady)."""
    hub.set_response("/api/status", status=500)
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_coordinator_data_matches_contract(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """The coordinator exposes the hub's real response shapes, unchanged."""
    coordinator = hass.data[DOMAIN][setup_integration.entry_id]

    assert coordinator.last_update_success
    assert coordinator.data["status"] == load_fixture("status.json")["data"]
    assert coordinator.data["outputs"] == load_fixture("status_outputs.json")["data"]["outputs"]
    assert coordinator.data["inputs"] == load_fixture("status_inputs.json")["data"]["inputs"]


async def test_coordinator_refresh_picks_up_changes(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """A refresh re-polls all three endpoints and stores the new state."""
    coordinator = hass.data[DOMAIN][setup_integration.entry_id]
    outputs = hub.fixture_copy("/api/status/outputs")
    outputs["data"]["outputs"][0]["muted"] = True
    hub.set_response("/api/status/outputs", outputs)

    await coordinator.async_refresh()
    await hass.async_block_till_done()

    polled = sorted(url.path for method, url, _d, _h in hub.mock.mock_calls if method.lower() == "get")
    assert polled == ["/api/status", "/api/status/inputs", "/api/status/outputs"]
    assert coordinator.data["outputs"][0]["muted"] is True


async def _refresh_with_status(hass, hub, entry, body=None, status=200):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    hub.set_response("/api/status", body, status=status)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    return coordinator


async def test_status_null_data_marks_update_failed(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """F10.1: {"success": true, "data": null} fails the update instead of crashing entities."""
    coordinator = await _refresh_with_status(
        hass, hub, setup_integration, {"success": True, "data": None, "error": None}
    )
    assert coordinator.last_update_success is False
    assert "null status data" in str(coordinator.last_exception)


async def test_status_api_error_marks_update_failed(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """{"success": false, "error": ...} fails the update and surfaces the error."""
    coordinator = await _refresh_with_status(
        hass, hub, setup_integration, {"success": False, "data": None, "error": "Matrix not connected"}, status=200
    )
    assert coordinator.last_update_success is False
    assert "Matrix not connected" in str(coordinator.last_exception)


async def test_status_http_error_marks_update_failed(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """An HTTP 503 from /api/status fails the update."""
    coordinator = await _refresh_with_status(hass, hub, setup_integration, status=503)
    assert coordinator.last_update_success is False
    assert "503" in str(coordinator.last_exception)
