"""Input signal and output display binary sensors.

Includes the F10.3 cases ported from tests/test_ha_robustness.py::TestBinarySensorAvailableState.
"""

from __future__ import annotations

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hdmi_matrix.const import DOMAIN

from .helpers import MockHub, entity_id


def _state(hass: HomeAssistant, unique_suffix: str):
    return hass.states.get(entity_id(hass, BINARY_SENSOR_DOMAIN, unique_suffix))


async def _refresh(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await hass.data[DOMAIN][entry.entry_id].async_refresh()
    await hass.async_block_till_done()


async def test_input_signal_sensors(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract: AppleTV (2), Switch (4), and PS5 (6) have signal; the others do not."""
    for number in range(1, 9):
        expected = STATE_ON if number in (2, 4, 6) else STATE_OFF
        assert _state(hass, f"input_{number}_signal").state == expected, number
    assert _state(hass, "input_2_signal").name == "Input 2 (AppleTV) Signal"


async def test_output_display_sensors(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract: TV (1) and Soundbar (2) are connected; outputs 3-8 are not."""
    for number in range(1, 9):
        expected = STATE_ON if number in (1, 2) else STATE_OFF
        assert _state(hass, f"output_{number}_connected").state == expected, number
    assert _state(hass, "output_1_connected").name == "Output 1 (TV) Display"


async def test_sensors_unavailable_when_update_fails(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """F10.3: a failed poll marks sensors unavailable instead of a misleading 'off'."""
    hub.set_response("/api/status", status=503)
    await _refresh(hass, setup_integration)

    assert _state(hass, "input_2_signal").state == STATE_UNAVAILABLE
    assert _state(hass, "output_1_connected").state == STATE_UNAVAILABLE


async def test_input_sensors_unavailable_without_input_data(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """F10.3: when /api/status/inputs fails, input sensors go unavailable, not off."""
    hub.set_response("/api/status/inputs", {"success": False, "data": None, "error": "boom"}, status=500)
    await _refresh(hass, setup_integration)

    assert _state(hass, "input_2_signal").state == STATE_UNAVAILABLE
    # Output sensors don't depend on the inputs endpoint.
    assert _state(hass, "output_1_connected").state == STATE_ON


async def test_sensors_recover_after_failure(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    hub.set_response("/api/status", status=503)
    await _refresh(hass, setup_integration)
    hub.set_response("/api/status", status=200)
    await _refresh(hass, setup_integration)

    assert _state(hass, "input_2_signal").state == STATE_ON
