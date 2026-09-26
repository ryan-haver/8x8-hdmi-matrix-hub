"""Input signal and output display binary sensors.

Includes the F10.3 cases ported from tests/test_ha_robustness.py::TestBinarySensorAvailableState.
"""

from __future__ import annotations

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import MockHub, entity_id, refresh


def _state(hass: HomeAssistant, unique_suffix: str):
    return hass.states.get(entity_id(hass, BINARY_SENSOR_DOMAIN, unique_suffix))


async def test_input_signal_sensors(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract: AppleTV (2), Switch (4), and PS5 (6) have signal; the others do not."""
    for number in range(1, 9):
        expected = STATE_ON if number in (2, 4, 6) else STATE_OFF
        assert _state(hass, f"input_{number}_signal").state == expected, number
    assert _state(hass, "input_2_signal").name == "HDMI Matrix Input 2 (AppleTV) signal"
    assert _state(hass, "input_8_signal").name == "HDMI Matrix Input 8 signal"  # default name: number only


async def test_output_display_sensors(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract: TV (1) and Soundbar (2) are connected; outputs 3-8 are not."""
    for number in range(1, 9):
        expected = STATE_ON if number in (1, 2) else STATE_OFF
        assert _state(hass, f"output_{number}_connected").state == expected, number
    assert _state(hass, "output_1_connected").name == "HDMI Matrix Output 1 (TV) display"


async def test_sensors_follow_the_hub(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    """A signal appearing on input 3 and the TV being unplugged show after the next poll."""
    inputs = hub.fixture_copy("/api/status/inputs")
    inputs["data"]["inputs"][2]["signalActive"] = True
    hub.set_response("/api/status/inputs", inputs)
    outputs = hub.fixture_copy("/api/status/outputs")
    outputs["data"]["outputs"][0]["connected"] = False
    outputs["data"]["outputs"][0]["cableConnected"] = False
    hub.set_response("/api/status/outputs", outputs)
    await refresh(hass, setup_integration)

    assert _state(hass, "input_3_signal").state == STATE_ON
    assert _state(hass, "output_1_connected").state == STATE_OFF


async def test_display_uses_connected_without_cable_status(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """Without Telnet the hub reports cableConnected = null; the sensor then uses `connected`."""
    outputs = hub.fixture_copy("/api/status/outputs")
    for out in outputs["data"]["outputs"]:
        out["cableConnected"] = None
    hub.set_response("/api/status/outputs", outputs)
    await refresh(hass, setup_integration)

    assert _state(hass, "output_1_connected").state == STATE_ON
    assert _state(hass, "output_3_connected").state == STATE_OFF


async def test_sensors_unavailable_when_update_fails(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """F10.3: a failed poll marks sensors unavailable instead of a misleading 'off'."""
    hub.set_response("/api/status", status=503)
    await refresh(hass, setup_integration)

    assert _state(hass, "input_2_signal").state == STATE_UNAVAILABLE
    assert _state(hass, "output_1_connected").state == STATE_UNAVAILABLE


async def test_input_sensors_unavailable_without_input_data(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """F10.3: when /api/status/inputs fails, input sensors go unavailable, not off."""
    hub.set_response("/api/status/inputs", {"success": False, "data": None, "error": "boom"}, status=500)
    await refresh(hass, setup_integration)

    assert _state(hass, "input_2_signal").state == STATE_UNAVAILABLE
    # Output sensors don't depend on the inputs endpoint.
    assert _state(hass, "output_1_connected").state == STATE_ON


async def test_output_sensors_unavailable_without_output_data(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    hub.set_response("/api/status/outputs", {"success": False, "data": None, "error": "boom"}, status=500)
    await refresh(hass, setup_integration)

    assert _state(hass, "output_1_connected").state == STATE_UNAVAILABLE
    assert _state(hass, "input_2_signal").state == STATE_ON


async def test_sensors_recover_after_failure(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    hub.set_response("/api/status", status=503)
    await refresh(hass, setup_integration)
    hub.set_response("/api/status", status=200)
    await refresh(hass, setup_integration)

    assert _state(hass, "input_2_signal").state == STATE_ON
