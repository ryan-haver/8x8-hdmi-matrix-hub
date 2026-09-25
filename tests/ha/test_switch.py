"""Power, output mute, and output stream switches."""

from __future__ import annotations

import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import MockHub, entity_id

HA_01 = (
    "HA-01: entities call hass.helpers.aiohttp_client, which no longer exists (AttributeError), so every write fails"
)
HA_03 = "HA-03: the power switch reads status['power'], which /api/status never returns, so it is always off"


async def _call(hass: HomeAssistant, service: str, unique_suffix: str) -> None:
    await hass.services.async_call(
        SWITCH_DOMAIN,
        service,
        {ATTR_ENTITY_ID: entity_id(hass, SWITCH_DOMAIN, unique_suffix)},
        blocking=True,
    )


async def test_switch_entities_created(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """One power switch, plus a mute switch and a stream switch per output."""
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "power")).name == "Matrix Power"
    for output in range(1, 9):
        assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, f"output_{output}_mute")) is not None
        assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, f"output_{output}_stream")) is not None


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=HA_03)
async def test_power_switch_reflects_matrix_power(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """The contract device is powered on (raw power=1)."""
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "power")).state == STATE_ON


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_power_switch_turn_on(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_ON, "power")
    assert len(hub.posts("/api/power/on")) == 1


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_power_switch_turn_off(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_OFF, "power")
    assert len(hub.posts("/api/power/off")) == 1


async def test_mute_switch_state(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract: the Soundbar (output 2) is muted; the TV (output 1) is not."""
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "output_1_mute")).state == STATE_OFF
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "output_2_mute")).state == STATE_ON


async def test_stream_switch_state(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract: output 8's stream is disabled; the others are enabled."""
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "output_1_stream")).state == STATE_ON
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "output_8_stream")).state == STATE_OFF


async def test_switch_state_follows_coordinator(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """After a refresh, the switch states reflect the new outputs payload."""
    from custom_components.hdmi_matrix.const import DOMAIN

    outputs = hub.fixture_copy("/api/status/outputs")
    outputs["data"]["outputs"][0]["muted"] = True
    outputs["data"]["outputs"][7]["enabled"] = True
    hub.set_response("/api/status/outputs", outputs)
    await hass.data[DOMAIN][setup_integration.entry_id].async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "output_1_mute")).state == STATE_ON
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "output_8_stream")).state == STATE_ON


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_mute_switch_turn_on(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_ON, "output_1_mute")
    assert hub.posts("/api/output/1/mute") == [{"muted": True}]


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_mute_switch_turn_off(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_OFF, "output_2_mute")
    assert hub.posts("/api/output/2/mute") == [{"muted": False}]


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_stream_switch_turn_off(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_OFF, "output_1_stream")
    assert hub.posts("/api/output/1/enable") == [{"enabled": False}]


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_stream_switch_turn_on(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_ON, "output_8_stream")
    assert hub.posts("/api/output/8/enable") == [{"enabled": True}]
