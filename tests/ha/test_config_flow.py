"""Config flow: user step, reconfigure, options (ported from tests/test_hacs_integration.py, now with a real hass)."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import aiohttp
import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hdmi_matrix.const import DOMAIN

from .helpers import BASE_URL, HOST, MAC, PORT, MockHub, coordinator

USER_INPUT = {"host": HOST, "port": PORT}


@pytest.fixture
async def mock_setup_entry(hass: HomeAssistant):
    """Keep the flow tests independent of entry setup.

    Entries created here never ran the real setup, so they are also unloaded
    with the real unload patched out, before the patches are removed.
    """
    with (
        patch("custom_components.hdmi_matrix.async_setup_entry", return_value=True) as mocked,
        patch("custom_components.hdmi_matrix.async_unload_entry", return_value=True),
    ):
        yield mocked
        for entry in hass.config_entries.async_entries(DOMAIN):
            await hass.config_entries.async_unload(entry.entry_id)


async def _start_flow(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result["errors"]
    return result


async def test_user_flow_success(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """A reachable hub creates an entry identified by the matrix MAC (HA-11)."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"HDMI Matrix ({HOST})"
    assert result["data"] == USER_INPUT
    assert result["result"].unique_id == MAC
    assert len(mock_setup_entry.mock_calls) == 1
    assert [c[1].path for c in hub.mock.mock_calls] == ["/api/health", "/api/status/device"]


async def test_user_flow_matrix_offline_uses_address(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """The hub answers but cannot read the matrix yet: the entry is keyed by host:port until setup learns the MAC."""
    hub.set_response("/api/status/device", {"success": False, "data": None, "error": "Matrix not connected"}, 503)
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == f"{HOST}:{PORT}"


async def test_user_flow_cannot_connect_http_error(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """A non-200 health check shows cannot_connect."""
    hub.set_response("/api/health", status=500)
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert not mock_setup_entry.mock_calls


async def test_user_flow_cannot_connect_network_error(hass: HomeAssistant, aioclient_mock, mock_setup_entry) -> None:
    """A network error shows cannot_connect, and the user can retry successfully."""
    aioclient_mock.get(f"{BASE_URL}/api/health", exc=aiohttp.ClientConnectionError())
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    # Recover: the hub comes back.
    aioclient_mock.clear_requests()
    MockHub(aioclient_mock)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_timeout(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    hub.set_read_error("/api/health", TimeoutError())
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_unexpected_error(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    with patch("custom_components.hdmi_matrix.config_flow.HubClient.health", side_effect=RuntimeError("bug")):
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["errors"] == {"base": "unknown"}


async def test_user_flow_already_configured(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """HA-05: adding the same matrix twice aborts with already_configured (AbortFlow is not swallowed)."""
    MockConfigEntry(domain=DOMAIN, data=USER_INPUT, unique_id=MAC).add_to_hass(hass)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_same_matrix_new_address_updates_entry(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry
) -> None:
    """The matrix is already set up under an old hub address: the entry follows it (keyed by MAC)."""
    entry = MockConfigEntry(domain=DOMAIN, data={"host": "192.0.2.99", "port": 8080}, unique_id=MAC)
    entry.add_to_hass(hass)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data == USER_INPUT


async def test_user_flow_same_address_aborts_before_probing(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry
) -> None:
    MockConfigEntry(domain=DOMAIN, data=USER_INPUT, unique_id=f"{HOST}:{PORT}").add_to_hass(hass)
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert not hub.mock.mock_calls


@pytest.mark.parametrize("port", [0, 65536, -1])
async def test_user_flow_rejects_invalid_port(hass: HomeAssistant, hub: MockHub, mock_setup_entry, port: int) -> None:
    """HA-11: the port must be 1-65535."""
    result = await _start_flow(hass)
    with pytest.raises(InvalidData):
        await hass.config_entries.flow.async_configure(result["flow_id"], {"host": HOST, "port": port})
    assert not hub.mock.mock_calls


# ------------------------------------------------------------------ reconfigure


async def test_reconfigure_changes_address(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"host": "192.0.2.20", "port": 8081})
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data == {"host": "192.0.2.20", "port": 8081}
    assert coordinator(entry).client.base_url == "http://192.0.2.20:8081"  # reloaded with the new address


async def test_reconfigure_other_matrix_aborts(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    device = hub.fixture_copy("/api/status/device")
    device["data"]["device"]["mac_address"] = "02:00:00:00:00:99"
    hub.set_response("/api/status/device", device)

    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"host": "192.0.2.20", "port": 8081})

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "wrong_device"
    assert entry.data == USER_INPUT


async def test_reconfigure_cannot_connect(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    hub.set_read_error("/api/health", aiohttp.ClientConnectionError())
    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"host": "192.0.2.20", "port": 8081})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


# ------------------------------------------------------------------ options


async def test_options_flow_sets_polling_interval(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    assert coordinator(entry).update_interval == timedelta(seconds=15)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"scan_interval": 30})
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {"scan_interval": 30}
    assert coordinator(entry).update_interval == timedelta(seconds=30)


async def test_options_flow_rejects_out_of_range(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    result = await hass.config_entries.options.async_init(setup_integration.entry_id)
    with pytest.raises(InvalidData):
        await hass.config_entries.options.async_configure(result["flow_id"], {"scan_interval": 1})
