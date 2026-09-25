"""Config flow tests (ported from tests/test_hacs_integration.py, now with a real hass)."""

from __future__ import annotations

from unittest.mock import patch

import aiohttp
import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hdmi_matrix.const import DOMAIN

from .helpers import BASE_URL, HOST, PORT, MockHub

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
    """A reachable hub creates an entry titled after the host."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"HDMI Matrix ({HOST})"
    assert result["data"] == USER_INPUT
    assert result["result"].unique_id == HOST
    assert len(mock_setup_entry.mock_calls) == 1
    assert hub.mock.mock_calls[0][1].path == "/api/health"


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


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="HA-05: AbortFlow from _abort_if_unique_id_configured() is swallowed by the broad "
    "`except Exception` in config_flow.py and shown as errors={'base': 'unknown'}",
)
async def test_user_flow_already_configured(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """Adding the same hub twice aborts with already_configured."""
    MockConfigEntry(domain=DOMAIN, data=USER_INPUT, unique_id=HOST).add_to_hass(hass)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
