"""The integration's own services: recall_preset, switch_input, send_cec_command."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import aiohttp
import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hdmi_matrix.const import CEC_INPUT_COMMANDS, CEC_OUTPUT_COMMANDS, DOMAIN

from .helpers import MAC, PORT, MockHub

ROOT = Path(__file__).resolve().parents[2]


async def _call(hass: HomeAssistant, service: str, data: dict) -> None:
    await hass.services.async_call(DOMAIN, service, data, blocking=True)


async def test_recall_preset(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    """HA-01: the service reaches the hub."""
    await _call(hass, "recall_preset", {"preset": 3})
    assert len(hub.posts("/api/preset/3")) == 1


async def test_switch_input(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, "switch_input", {"output": 2, "input": 5})
    assert hub.posts("/api/output/2/source") == [{"input": 5}]


async def test_send_cec_command(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, "send_cec_command", {"port_type": "input", "port_num": 2, "command": "power_on"})
    assert len(hub.posts("/api/cec/input/2/power_on")) == 1


async def test_send_cec_command_to_display(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    await _call(hass, "send_cec_command", {"port_type": "output", "port_num": 1, "command": "VOLUME_UP"})
    assert len(hub.posts("/api/cec/output/1/volume_up")) == 1


@pytest.mark.parametrize(
    ("service", "data"),
    [
        ("recall_preset", {"preset": 9}),
        ("switch_input", {"output": 0, "input": 1}),
        ("switch_input", {"output": 1}),
        ("send_cec_command", {"port_type": "hdmi", "port_num": 1, "command": "power_on"}),
        # HA-12: only commands the hub knows; nothing is interpolated into the URL unchecked.
        ("send_cec_command", {"port_type": "input", "port_num": 1, "command": "power_on/../../system/reboot"}),
        ("send_cec_command", {"port_type": "input", "port_num": 1, "command": "self_destruct"}),
    ],
)
async def test_service_schema_rejects_invalid_data(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry, service: str, data: dict
) -> None:
    """Out-of-range, unknown, or missing fields are rejected before anything is sent to the hub."""
    hub.mock.mock_calls.clear()
    with pytest.raises(vol.Invalid):
        await _call(hass, service, data)
    assert hub.all_posts() == []


@pytest.mark.parametrize(
    ("port_type", "command"),
    [("output", "play"), ("output", "menu"), ("input", "active")],
)
async def test_cec_command_must_fit_the_port(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry, port_type: str, command: str
) -> None:
    """Displays have their own, smaller table (BE-14); a mismatch is a validation error, nothing is sent."""
    hub.mock.mock_calls.clear()
    with pytest.raises(ServiceValidationError):
        await _call(hass, "send_cec_command", {"port_type": port_type, "port_num": 1, "command": command})
    assert hub.all_posts() == []


def test_cec_tables_match_the_hub() -> None:
    """The component's command lists equal the hub's tables in src/device_codes.py."""
    spec = importlib.util.spec_from_file_location("device_codes", ROOT / "src" / "device_codes.py")
    assert spec and spec.loader
    codes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(codes)
    assert list(CEC_INPUT_COMMANDS) == [c.lower() for c in codes.CEC_INPUT_COMMANDS]
    assert list(CEC_OUTPUT_COMMANDS) == [c.lower() for c in codes.CEC_OUTPUT_COMMANDS]
    options = (ROOT / "custom_components/hdmi_matrix/services.yaml").read_text(encoding="utf-8")
    for command in {*CEC_INPUT_COMMANDS, *CEC_OUTPUT_COMMANDS}:
        assert f"- {command}\n" in options, command


async def test_hub_error_is_raised(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    """HA-06: a hub failure is a HomeAssistantError the caller sees, not a log line."""
    hub.set_post("/api/preset/3", {"success": False, "data": None, "error": "Matrix not connected"}, status=503)
    with pytest.raises(HomeAssistantError, match="Matrix not connected"):
        await _call(hass, "recall_preset", {"preset": 3})


async def test_hub_unreachable_is_raised(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    hub.set_post("/api/output/2/source", exc=aiohttp.ClientConnectionError("refused"))
    with pytest.raises(HomeAssistantError, match="Cannot reach"):
        await _call(hass, "switch_input", {"output": 2, "input": 5})


async def test_success_false_with_http_200_is_an_error(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry
) -> None:
    hub.set_post("/api/cec/input/2/power_on", {"success": False, "data": None, "error": "CEC failed"}, status=200)
    with pytest.raises(HomeAssistantError, match="CEC failed"):
        await _call(hass, "send_cec_command", {"port_type": "input", "port_num": 2, "command": "power_on"})


# ------------------------------------------------------------------ targeting (HA-06)


@pytest.fixture
async def two_matrices(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> MockConfigEntry:
    """A second matrix behind another hub (192.0.2.11), with its own MAC."""
    device = hub.fixture_copy("/api/status/device")
    device["data"]["device"]["mac_address"] = "02:00:00:00:00:11"
    hub.host_responses[("http://192.0.2.11:8080", "/api/status/device")] = device
    hub.register()
    other = MockConfigEntry(domain=DOMAIN, data={"host": "192.0.2.11", "port": PORT}, unique_id="02:00:00:00:00:11")
    other.add_to_hass(hass)
    assert await hass.config_entries.async_setup(other.entry_id)
    await hass.async_block_till_done()
    return other


def _posted_hosts(hub: MockHub, path: str) -> list[str]:
    return [url.host for method, url, _d, _h in hub.mock.mock_calls if method.lower() == "post" and url.path == path]


async def test_ambiguous_target_is_rejected(hass: HomeAssistant, hub: MockHub, two_matrices) -> None:
    with pytest.raises(ServiceValidationError):
        await _call(hass, "recall_preset", {"preset": 1})
    assert hub.all_posts() == []


async def test_target_by_config_entry(hass: HomeAssistant, hub: MockHub, two_matrices: MockConfigEntry) -> None:
    await _call(hass, "recall_preset", {"preset": 1, "config_entry_id": two_matrices.entry_id})
    assert _posted_hosts(hub, "/api/preset/1") == ["192.0.2.11"]


async def test_target_by_device(
    hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry, two_matrices: MockConfigEntry
) -> None:
    device = dr.async_get(hass).async_get_device(identifiers={(DOMAIN, MAC)})
    await _call(hass, "switch_input", {"output": 1, "input": 3, "device_id": device.id})
    assert _posted_hosts(hub, "/api/output/1/source") == ["192.0.2.10"]


async def test_unknown_targets_are_rejected(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    with pytest.raises(ServiceValidationError):
        await _call(hass, "recall_preset", {"preset": 1, "config_entry_id": "nope"})
    with pytest.raises(ServiceValidationError):
        await _call(hass, "recall_preset", {"preset": 1, "device_id": "nope"})
    assert hub.all_posts() == []


async def test_unloaded_entry_is_rejected(hass: HomeAssistant, hub: MockHub, setup_integration: MockConfigEntry) -> None:
    assert await hass.config_entries.async_unload(setup_integration.entry_id)
    with pytest.raises(ServiceValidationError):
        await _call(hass, "recall_preset", {"preset": 1, "config_entry_id": setup_integration.entry_id})
    with pytest.raises(ServiceValidationError):
        await _call(hass, "recall_preset", {"preset": 1})  # nothing loaded
