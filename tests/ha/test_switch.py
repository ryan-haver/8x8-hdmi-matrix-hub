"""Power, output mute, and output stream switches."""

from __future__ import annotations

import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import MockHub, entity_id, refresh


async def _call(hass: HomeAssistant, service: str, unique_suffix: str) -> None:
    await hass.services.async_call(
        SWITCH_DOMAIN,
        service,
        {ATTR_ENTITY_ID: entity_id(hass, SWITCH_DOMAIN, unique_suffix)},
        blocking=True,
    )


def _state(hass: HomeAssistant, unique_suffix: str) -> str:
    return hass.states.get(entity_id(hass, SWITCH_DOMAIN, unique_suffix)).state


async def test_switch_entities_created(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """One power switch, plus a mute switch and a stream switch per output."""
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "power")).name == "HDMI Matrix Power"
    for output in range(1, 9):
        assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, f"output_{output}_mute")) is not None
        assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, f"output_{output}_stream")) is not None
    assert hass.states.get(entity_id(hass, SWITCH_DOMAIN, "output_2_mute")).name == "HDMI Matrix Output 2 (Soundbar) mute"


async def test_power_switch_reflects_matrix_power(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """HA-03: the contract device is powered on (/api/status "power": "on")."""
    assert _state(hass, "power") == STATE_ON


@pytest.mark.parametrize(("power", "expected"), [("off", STATE_OFF), (None, STATE_UNAVAILABLE)])
async def test_power_switch_standby_and_unknown(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry, power, expected
) -> None:
    """Standby shows off; a hub that reports no power makes the switch unavailable, not a guess."""
    status = hub.fixture_copy("/api/status")
    if power is None:
        del status["data"]["power"]
    else:
        status["data"]["power"] = power
    hub.set_response("/api/status", status)
    await refresh(hass, setup_integration)
    assert _state(hass, "power") == expected


async def test_power_switch_turn_on(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_ON, "power")
    assert len(hub.posts("/api/power/on")) == 1


async def test_power_switch_turn_off(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_OFF, "power")
    assert len(hub.posts("/api/power/off")) == 1


async def test_power_switch_error_is_raised(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    hub.set_post("/api/power/off", {"success": False, "data": None, "error": "Matrix not connected"}, status=503)
    with pytest.raises(HomeAssistantError, match="Matrix not connected"):
        await _call(hass, SERVICE_TURN_OFF, "power")


async def test_mute_switch_state(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract: the Soundbar (output 2) is muted; the TV (output 1) is not."""
    assert _state(hass, "output_1_mute") == STATE_OFF
    assert _state(hass, "output_2_mute") == STATE_ON


async def test_stream_switch_state(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract: output 8's stream is disabled; the others are enabled."""
    assert _state(hass, "output_1_stream") == STATE_ON
    assert _state(hass, "output_8_stream") == STATE_OFF


async def test_switch_state_follows_coordinator(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """After a refresh, the switch states reflect the new outputs payload."""
    outputs = hub.fixture_copy("/api/status/outputs")
    outputs["data"]["outputs"][0]["muted"] = True
    outputs["data"]["outputs"][7]["enabled"] = True
    hub.set_response("/api/status/outputs", outputs)
    await refresh(hass, setup_integration)

    assert _state(hass, "output_1_mute") == STATE_ON
    assert _state(hass, "output_8_stream") == STATE_ON


async def test_output_switches_unavailable_without_output_data(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """No /api/status/outputs in this poll: mute/stream are unknown, not 'off'."""
    hub.set_response("/api/status/outputs", {"success": False, "data": None, "error": "boom"}, status=500)
    await refresh(hass, setup_integration)
    assert _state(hass, "output_2_mute") == STATE_UNAVAILABLE
    assert _state(hass, "output_1_stream") == STATE_UNAVAILABLE
    assert _state(hass, "power") == STATE_ON


async def test_mute_switch_turn_on(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_ON, "output_1_mute")
    assert hub.posts("/api/output/1/mute") == [{"muted": True}]


async def test_mute_switch_turn_off(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_OFF, "output_2_mute")
    assert hub.posts("/api/output/2/mute") == [{"muted": False}]


async def test_stream_switch_turn_off(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_OFF, "output_1_stream")
    assert hub.posts("/api/output/1/enable") == [{"enabled": False}]


async def test_stream_switch_turn_on(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, SERVICE_TURN_ON, "output_8_stream")
    assert hub.posts("/api/output/8/enable") == [{"enabled": True}]
