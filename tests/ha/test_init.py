"""Setup/unload, runtime data, the coordinator, and the unique-id migration.

Ported from tests/test_hacs_integration.py::test_coordinator_update_success and
tests/test_ha_robustness.py::TestCoordinatorNullDataHandling (F10.1). They run
with a real hass against the contract fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path

import aiohttp
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hdmi_matrix.api import HubConnectionError, HubResponseError
from custom_components.hdmi_matrix.const import DOMAIN

from .helpers import BASE_URL, HOST, MAC, PORT, MockHub, coordinator, entity_id, load_fixture, refresh

SERVICES = ("recall_preset", "switch_input", "send_cec_command")
COMPONENT = Path(__file__).resolve().parents[2] / "custom_components" / "hdmi_matrix"


async def test_setup_and_unload_entry(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """The entry loads with its runtime data, and unloads cleanly (HA-07)."""
    entry = setup_integration
    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.client.base_url == BASE_URL
    assert entry.runtime_data.device["mac_address"] == "02:00:00:0B:08:08"
    assert DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]  # no legacy hass.data storage

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_services_registered_once_for_the_integration(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """HA-06: services belong to the integration (async_setup), not to an entry."""
    for service in SERVICES:
        assert hass.services.has_service(DOMAIN, service)
    assert await hass.config_entries.async_unload(setup_integration.entry_id)
    await hass.async_block_till_done()
    for service in SERVICES:
        assert hass.services.has_service(DOMAIN, service)


async def test_setup_retries_when_hub_unreachable(
    hass: HomeAssistant, hub: MockHub, config_entry: MockConfigEntry
) -> None:
    """If the first refresh fails, setup is retried (ConfigEntryNotReady)."""
    hub.set_response("/api/status", status=500)
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_without_device_info(hass: HomeAssistant, hub: MockHub, config_entry: MockConfigEntry) -> None:
    """Firmware version and MAC are optional: setup works when /api/status/device fails."""
    hub.set_response("/api/status/device", {"success": False, "data": None, "error": "Matrix not connected"}, 503)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.runtime_data.device == {}


async def test_coordinator_data_matches_contract(hass: HomeAssistant, setup_integration: MockConfigEntry) -> None:
    """The coordinator exposes the hub's real response shapes, unchanged."""
    coord = coordinator(setup_integration)

    assert coord.last_update_success
    assert coord.data.status == load_fixture("status.json")["data"]
    assert coord.data.outputs == load_fixture("status_outputs.json")["data"]["outputs"]
    assert coord.data.inputs == load_fixture("status_inputs.json")["data"]["inputs"]
    # HA-02: routing is a mapping keyed by output number (JSON string keys).
    assert coord.data.routed_input(1) == 2 and coord.data.routed_input(3) == 6
    assert coord.data.power == "on"  # HA-03


async def test_coordinator_refresh_picks_up_changes(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """A refresh re-polls all three endpoints and stores the new state."""
    coord = coordinator(setup_integration)
    outputs = hub.fixture_copy("/api/status/outputs")
    outputs["data"]["outputs"][0]["muted"] = True
    hub.set_response("/api/status/outputs", outputs)

    await refresh(hass, setup_integration)

    polled = sorted(url.path for method, url, _d, _h in hub.mock.mock_calls if method.lower() == "get")
    assert polled == ["/api/status", "/api/status/inputs", "/api/status/outputs"]
    assert coord.data.outputs[0]["muted"] is True


async def _refresh_with_status(hass, hub, entry, body=None, status=200):
    hub.set_response("/api/status", body, status=status)
    await refresh(hass, entry)
    return coordinator(entry)


async def test_status_null_data_marks_update_failed(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """F10.1: {"success": true, "data": null} fails the update instead of crashing entities."""
    coord = await _refresh_with_status(hass, hub, setup_integration, {"success": True, "data": None, "error": None})
    assert coord.last_update_success is False
    assert "null status data" in str(coord.last_exception)


async def test_status_api_error_marks_update_failed(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """{"success": false, "error": ...} fails the update and surfaces the error; the cause is chained (HA-09)."""
    coord = await _refresh_with_status(
        hass, hub, setup_integration, {"success": False, "data": None, "error": "Matrix not connected"}, status=200
    )
    assert coord.last_update_success is False
    assert "Matrix not connected" in str(coord.last_exception)
    assert isinstance(coord.last_exception.__cause__, HubResponseError)


async def test_status_http_error_marks_update_failed(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """An HTTP 503 from /api/status fails the update."""
    coord = await _refresh_with_status(hass, hub, setup_integration, status=503)
    assert coord.last_update_success is False
    assert "503" in str(coord.last_exception)


async def test_status_network_error_marks_update_failed(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    hub.set_read_error("/api/status", aiohttp.ClientConnectionError("refused"))
    await refresh(hass, setup_integration)
    coord = coordinator(setup_integration)
    assert coord.last_update_success is False
    assert isinstance(coord.last_exception.__cause__, HubConnectionError)


async def test_renamed_preset_reloads_with_the_new_name(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    """Entity names include hub names; a rename on the hub shows after the next poll."""
    status = hub.fixture_copy("/api/status")
    status["data"]["preset_names"]["3"] = "Party"
    hub.set_response("/api/status", status)
    await refresh(hass, setup_integration)
    await hass.async_block_till_done()

    button = entity_id(hass, "button", "preset_3")
    assert hass.states.get(button).name == "HDMI Matrix Recall preset 3 (Party)"
    assert setup_integration.state is ConfigEntryState.LOADED


# ------------------------------------------------------------------ device (HA-10)


async def test_one_device_with_firmware_and_configuration_url(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), setup_integration.entry_id)
    assert len(devices) == 1
    device = devices[0]
    assert device.identifiers == {(DOMAIN, MAC)}
    assert device.connections == {(dr.CONNECTION_NETWORK_MAC, MAC)}
    assert (device.manufacturer, device.model, device.sw_version) == ("OREI", "BK-808", "V1.10.01")
    assert device.configuration_url == BASE_URL
    assert device.name == "HDMI Matrix"

    entities = er.async_entries_for_config_entry(er.async_get(hass), setup_integration.entry_id)
    assert len(entities) == 8 + 17 + 9 + 16  # selects, switches, buttons, binary sensors
    assert {e.device_id for e in entities} == {device.id}
    assert all(e.has_entity_name and e.translation_key for e in entities)


# ------------------------------------------------------------------ unique-id migration (HA-11)


async def test_address_keyed_entry_moves_to_the_mac(hass: HomeAssistant, hub: MockHub) -> None:
    """An entry created before HA-11 (unique_id = host) keeps its entities and device, now keyed by the MAC."""
    entry = MockConfigEntry(domain=DOMAIN, data={"host": HOST, "port": PORT}, unique_id=HOST)
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    old = registry.async_get_or_create("button", DOMAIN, f"{HOST}_preset_1", config_entry=entry,
                                       suggested_object_id="my_movie_button")
    devices = dr.async_get(hass)
    old_device = devices.async_get_or_create(config_entry_id=entry.entry_id, identifiers={(DOMAIN, HOST)})

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.unique_id == MAC
    migrated = registry.async_get(old.entity_id)
    assert migrated is not None and migrated.unique_id == f"{MAC}_preset_1"
    assert old.entity_id == "button.my_movie_button"  # history kept: same entity_id
    assert devices.async_get(old_device.id).identifiers == {(DOMAIN, MAC)}
    assert registry.async_get_entity_id("button", DOMAIN, f"{HOST}_preset_1") is None


async def test_migration_skipped_when_the_mac_is_taken(hass: HomeAssistant, hub: MockHub) -> None:
    MockConfigEntry(domain=DOMAIN, data={"host": "192.0.2.99", "port": PORT}, unique_id=MAC).add_to_hass(hass)
    entry = MockConfigEntry(domain=DOMAIN, data={"host": HOST, "port": PORT}, unique_id=HOST)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.unique_id == HOST


# ------------------------------------------------------------------ packaging (HA-04, HA-13, HA-14)


def test_translations_match_strings() -> None:
    """HA-04: custom integrations are not compiled; translations/en.json must equal strings.json."""
    strings = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
    en = json.loads((COMPONENT / "translations" / "en.json").read_text(encoding="utf-8"))
    assert en == strings


def test_manifest_and_hacs() -> None:
    manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["integration_type"] == "hub"  # HA-13
    assert manifest["iot_class"] == "local_polling"
    assert "zeroconf" not in manifest  # the hub does not advertise itself yet
    hacs = json.loads((COMPONENT.parents[1] / "hacs.json").read_text(encoding="utf-8"))
    assert hacs["name"] == "HDMI Matrix" and hacs["homeassistant"] == "2025.1.0"  # D8
