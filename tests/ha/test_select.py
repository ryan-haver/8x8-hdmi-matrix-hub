"""Output source select entities."""

from __future__ import annotations

import aiohttp
import pytest
from homeassistant.components.select import ATTR_OPTION, ATTR_OPTIONS, SERVICE_SELECT_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import MockHub, entity_id, refresh

INPUT_NAMES = ["PS3", "AppleTV", "Computer", "Switch", "Shield", "PS5", "Analogue", "Input 8"]


async def _select(hass: HomeAssistant, output: int, option: str) -> None:
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: entity_id(hass, SELECT_DOMAIN, f"output_{output}_source"), ATTR_OPTION: option},
        blocking=True,
    )


async def test_select_entities_and_options(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """One select per output; its options are the hub's input names."""
    for output in range(1, 9):
        state = hass.states.get(entity_id(hass, SELECT_DOMAIN, f"output_{output}_source"))
        assert state is not None
        assert state.attributes[ATTR_OPTIONS] == INPUT_NAMES
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_1_source")).name == "HDMI Matrix Output 1 (TV) source"
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_3_source")).name == "HDMI Matrix Output 3 source"


async def test_select_current_option_follows_routing(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """HA-02: contract routing ({"1": 2, ...}): TV and Soundbar watch AppleTV (2); output 3 watches PS5 (6)."""
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_1_source")).state == "AppleTV"
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_2_source")).state == "AppleTV"
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_3_source")).state == "PS5"


async def test_select_follows_a_routing_change(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    status = hub.fixture_copy("/api/status")
    status["data"]["routing"]["1"] = 4
    hub.set_response("/api/status", status)
    await refresh(hass, setup_integration)
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_1_source")).state == "Switch"


async def test_select_unknown_routing_value(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    """An input number outside 1-8 (or none) shows as unknown, not a wrong name."""
    status = hub.fixture_copy("/api/status")
    status["data"]["routing"]["1"] = 255
    del status["data"]["routing"]["2"]
    hub.set_response("/api/status", status)
    await refresh(hass, setup_integration)
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_1_source")).state == STATE_UNKNOWN
    assert hass.states.get(entity_id(hass, SELECT_DOMAIN, "output_2_source")).state == STATE_UNKNOWN


async def test_select_option_routes_input(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    """HA-01: selecting 'PS5' on output 1 POSTs {"input": 6} to /api/output/1/source."""
    await _select(hass, 1, "PS5")
    assert hub.posts("/api/output/1/source") == [{"input": 6}]


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

    await _select(hass, 1, "PS5")
    assert hub.posts("/api/output/1/source") == [{"input": 2}]
    # Inputs 1, 2 and 6 are all "PS5" now; output 3 is routed to input 6 and keeps it.
    await _select(hass, 3, "PS5")
    assert hub.posts("/api/output/3/source") == [{"input": 6}]
    # Output 4 watches Switch (4): no current match, the first "PS5" wins.
    await _select(hass, 4, "PS5")
    assert hub.posts("/api/output/4/source") == [{"input": 1}]


async def test_select_unknown_option_is_rejected(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """HA validates the option before calling the entity, so nothing reaches the hub."""
    with pytest.raises(ServiceValidationError):
        await _select(hass, 1, "Betamax")
    assert hub.posts("/api/output/1/source") == []


async def test_select_hub_error_is_raised(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    """A routing the hub refuses is an error the user sees, not a log line."""
    hub.set_post("/api/output/1/source", {"success": False, "data": None, "error": "Failed to route"}, status=500)
    with pytest.raises(HomeAssistantError, match="Failed to route"):
        await _select(hass, 1, "PS5")


async def test_select_hub_unreachable_is_raised(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    hub.set_post("/api/output/1/source", exc=aiohttp.ClientConnectionError("refused"))
    with pytest.raises(HomeAssistantError, match="Cannot reach"):
        await _select(hass, 1, "PS5")
