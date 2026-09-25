"""Preset recall and reboot buttons."""

from __future__ import annotations

import pytest
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.components.button import SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import MockHub, entity_id

HA_01 = (
    "HA-01: entities call hass.helpers.aiohttp_client, which no longer exists (AttributeError), so every write fails"
)


async def _press(hass: HomeAssistant, unique_suffix: str) -> None:
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: entity_id(hass, BUTTON_DOMAIN, unique_suffix)},
        blocking=True,
    )


async def test_preset_buttons_named_from_hub(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Eight preset buttons, named after the hub's preset names."""
    for preset in range(1, 9):
        assert hass.states.get(entity_id(hass, BUTTON_DOMAIN, f"preset_{preset}")) is not None
    assert hass.states.get(entity_id(hass, BUTTON_DOMAIN, "preset_1")).name == "Recall Preset 1 (Movie Night)"
    assert hass.states.get(entity_id(hass, BUTTON_DOMAIN, "preset_2")).name == "Recall Preset 2 (Gaming)"
    assert hass.states.get(entity_id(hass, BUTTON_DOMAIN, "reboot")).name == "Reboot Matrix"


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_preset_button_press(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _press(hass, "preset_2")
    assert len(hub.posts("/api/preset/2")) == 1


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_reboot_button_press(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _press(hass, "reboot")
    assert len(hub.posts("/api/system/reboot")) == 1
