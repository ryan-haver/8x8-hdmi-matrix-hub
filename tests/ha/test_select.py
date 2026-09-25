"""Output source select entities."""

from __future__ import annotations

import pytest
from homeassistant.components.select import ATTR_OPTION, ATTR_OPTIONS, SERVICE_SELECT_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import MockHub, entity_id

INPUT_NAMES = ["PS3", "AppleTV", "Computer", "Switch", "Shield", "PS5", "Analogue", "Input 8"]

HA_01 = (
    "HA-01: entities call hass.helpers.aiohttp_client, which no longer exists (AttributeError), so every write fails"
)
HA_02 = "HA-02: select expects `routing` as a list, but /api/status returns a dict keyed by output, so current_option is None"


async def test_select_entities_and_options(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """One select per output; its options are the hub's input names."""
    for output in range(1, 9):
        state = hass.states.get(entity_id(hass, SELECT_DOMAIN, f"output_{output}_source"))
        assert state is not None
        assert state.attributes[ATTR_OPTIONS] == INPUT_NAMES
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_1_source")).name == "Output 1 Source"


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=HA_02)
async def test_select_current_option_follows_routing(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """Contract routing: TV and Soundbar watch AppleTV (2); output 3 watches PS5 (6)."""
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_1_source")).state == "AppleTV"
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_2_source")).state == "AppleTV"
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_3_source")).state == "PS5"


@pytest.mark.xfail(strict=True, raises=AttributeError, reason=HA_01)
async def test_select_option_routes_input(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """Selecting 'PS5' on output 1 POSTs {"input": 6} to /api/output/1/source."""
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: entity_id(hass, SELECT_DOMAIN, "output_1_source"), ATTR_OPTION: "PS5"},
        blocking=True,
    )
    assert hub.posts("/api/output/1/source") == [{"input": 6}]


@pytest.mark.xfail(strict=True, raises=(AttributeError, AssertionError), reason=f"{HA_01}; {HA_02}")
async def test_duplicate_input_names_prefer_current_routing(
    hass: HomeAssistant, hub: MockHub, config_entry: MockConfigEntry
) -> None:
    """F10.4: with two inputs named 'PS5', selecting it keeps the currently routed one.

    Ported from tests/test_ha_robustness.py::TestSelectDuplicateInputNames.
    """
    status = hub.fixture_copy("/api/status")
    status["data"]["input_names"]["1"] = "PS5"
    status["data"]["input_names"]["2"] = "PS5"  # output 1 is routed to input 2
    hub.set_response("/api/status", status)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    select_id = entity_id(hass, SELECT_DOMAIN, "output_1_source")
    assert hass.states.get(select_id).state == "PS5"

    await hass.services.async_call(
        SELECT_DOMAIN, SERVICE_SELECT_OPTION, {ATTR_ENTITY_ID: select_id, ATTR_OPTION: "PS5"}, blocking=True
    )
    assert hub.posts("/api/output/1/source") == [{"input": 2}]


async def test_select_unknown_option_is_rejected(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """HA validates the option before calling the entity, so nothing reaches the hub."""
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {ATTR_ENTITY_ID: entity_id(hass, SELECT_DOMAIN, "output_1_source"), ATTR_OPTION: "Betamax"},
            blocking=True,
        )
    assert hub.posts("/api/output/1/source") == []
