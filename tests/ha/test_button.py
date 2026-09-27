"""Preset recall and reboot buttons."""

from __future__ import annotations

import aiohttp
import pytest
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.components.button import SERVICE_PRESS, ButtonDeviceClass
from homeassistant.const import ATTR_DEVICE_CLASS, ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import MockHub, entity_id


async def _press(hass: HomeAssistant, unique_suffix: str) -> None:
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: entity_id(hass, BUTTON_DOMAIN, unique_suffix)},
        blocking=True,
    )


async def test_preset_buttons_named_from_hub(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Eight preset buttons, named after the hub's preset names; a reboot button."""
    for preset in range(1, 9):
        assert hass.states.get(entity_id(hass, BUTTON_DOMAIN, f"preset_{preset}")) is not None
    assert hass.states.get(entity_id(hass, BUTTON_DOMAIN, "preset_1")).name == "HDMI Matrix Recall preset 1 (Movie Night)"
    assert hass.states.get(entity_id(hass, BUTTON_DOMAIN, "preset_2")).name == "HDMI Matrix Recall preset 2 (Gaming)"
    assert hass.states.get(entity_id(hass, BUTTON_DOMAIN, "preset_3")).name == "HDMI Matrix Recall preset 3"
    reboot = hass.states.get(entity_id(hass, BUTTON_DOMAIN, "reboot"))
    assert reboot.name == "HDMI Matrix Reboot"
    assert reboot.attributes[ATTR_DEVICE_CLASS] == ButtonDeviceClass.RESTART
    assert er.async_get(hass).async_get(reboot.entity_id).entity_category == "config"


async def test_preset_button_press(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    """HA-01: the press reaches the hub through Home Assistant's shared session."""
    await _press(hass, "preset_2")
    assert len(hub.posts("/api/preset/2")) == 1


async def test_reboot_button_press(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _press(hass, "reboot")
    assert len(hub.posts("/api/system/reboot")) == 1


async def test_preset_press_hub_error_is_reported(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """A failed recall raises instead of only logging (the user sees it)."""
    hub.set_post("/api/preset/2", {"success": False, "data": None, "error": "Matrix not connected"}, status=503)
    with pytest.raises(HomeAssistantError, match="Matrix not connected"):
        await _press(hass, "preset_2")


async def test_press_hub_unreachable_is_reported(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    hub.set_post("/api/system/reboot", exc=aiohttp.ClientConnectionError("refused"))
    with pytest.raises(HomeAssistantError, match="Cannot reach the HDMI Matrix hub"):
        await _press(hass, "reboot")
