"""The integration's own services: recall_preset, switch_input, send_cec_command."""

from __future__ import annotations

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hdmi_matrix.const import DOMAIN

from .helpers import MockHub

HA_01 = (
    "HA-01: service handlers call hass.helpers.aiohttp_client, which no longer exists (AttributeError), "
    "so every service fails"
)


async def _call(hass: HomeAssistant, service: str, data: dict) -> None:
    await hass.services.async_call(DOMAIN, service, data, blocking=True)


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_recall_preset(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, "recall_preset", {"preset": 3})
    assert len(hub.posts("/api/preset/3")) == 1


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_switch_input(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, "switch_input", {"output": 2, "input": 5})
    assert hub.posts("/api/output/2/source") == [{"input": 5}]


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_send_cec_command(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, "send_cec_command", {"port_type": "input", "port_num": 2, "command": "power_on"})
    assert len(hub.posts("/api/cec/input/2/power_on")) == 1


@pytest.mark.parametrize(
    ("service", "data"),
    [
        ("recall_preset", {"preset": 9}),
        ("switch_input", {"output": 0, "input": 1}),
        ("switch_input", {"output": 1}),
        ("send_cec_command", {"port_type": "hdmi", "port_num": 1, "command": "power_on"}),
    ],
)
async def test_service_schema_rejects_invalid_data(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry, service: str, data: dict
) -> None:
    """Out-of-range or missing fields are rejected before anything is sent to the hub."""
    hub.mock.mock_calls.clear()
    with pytest.raises(vol.Invalid):
        await _call(hass, service, data)
    assert not [c for c in hub.mock.mock_calls if c[0].lower() == "post"]
