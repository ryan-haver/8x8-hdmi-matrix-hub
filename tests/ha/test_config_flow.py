"""Config flow: user step, reconfigure, options (ported from tests/test_hacs_integration.py, now with a real hass)."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Any
from unittest.mock import patch

import aiohttp
import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from homeassistant.helpers import translation
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMockResponse

from custom_components import hdmi_matrix
from custom_components.hdmi_matrix.const import CONF_API_KEY, CONF_SCAN_INTERVAL, DOMAIN

from .helpers import BASE_URL, HOST, MAC, PORT, MockHub, coordinator

USER_INPUT = {"host": HOST, "port": PORT}
COMPONENT = Path(__file__).resolve().parents[2] / "custom_components" / "hdmi_matrix"
_MALFORMED_AUTH_BODIES = (
    "not-json",
    "null",
    "[]",
    "{}",
    '{"success": true, "data": {}}',
    '{"control_pin_set": "false", "session_level": "none"}',
    '{"control_pin_set": 0, "session_level": "none"}',
    '{"control_pin_set": false}',
    '{"control_pin_set": false, "session_level": "bogus"}',
)


@pytest.fixture
async def mock_setup_entry(hass: HomeAssistant):
    """Keep the flow tests independent of entry setup.

    Entries created here never ran the real setup, so they are also unloaded
    with the real unload patched out, before the patches are removed.
    """
    with (
        patch("custom_components.hdmi_matrix.async_setup_entry", return_value=True) as mocked,
        patch("custom_components.hdmi_matrix.async_unload_entry", return_value=True),
    ):
        yield mocked
        for entry in hass.config_entries.async_entries(DOMAIN):
            await hass.config_entries.async_unload(entry.entry_id)


async def _start_flow(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result["errors"]
    return result


async def test_user_flow_success(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """A reachable hub creates an entry identified by the matrix MAC (HA-11)."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"HDMI Matrix ({HOST})"
    assert result["data"] == USER_INPUT
    assert result["result"].unique_id == MAC
    assert len(mock_setup_entry.mock_calls) == 1
    assert [c[1].path for c in hub.mock.mock_calls] == ["/api/health", "/api/auth/status", "/api/status/device"]


async def test_user_flow_with_api_key(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """A keyed hub receives the key during probing and stores it for runtime requests."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, CONF_API_KEY: "ha-key"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_API_KEY] == "ha-key"
    assert all(headers.get("X-API-Key") == "ha-key" for _, _, _, headers in hub.mock.mock_calls)


async def test_user_flow_matrix_offline_uses_address(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """The hub answers but cannot read the matrix yet: the entry is keyed by host:port until setup learns the MAC."""
    hub.set_response("/api/status/device", {"success": False, "data": None, "error": "Matrix not connected"}, 503)
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == f"{HOST}:{PORT}"


async def test_user_flow_cannot_connect_http_error(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """A non-200 health check shows cannot_connect."""
    hub.set_response("/api/health", status=500)
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert not mock_setup_entry.mock_calls


async def test_user_flow_cannot_connect_network_error(hass: HomeAssistant, aioclient_mock, mock_setup_entry) -> None:
    """A network error shows cannot_connect, and the user can retry successfully."""
    aioclient_mock.get(f"{BASE_URL}/api/health", exc=aiohttp.ClientConnectionError())
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    # Recover: the hub comes back.
    aioclient_mock.clear_requests()
    MockHub(aioclient_mock)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_timeout(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    hub.set_read_error("/api/health", TimeoutError())
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_unexpected_error(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    with patch("custom_components.hdmi_matrix.config_flow.HubClient.health", side_effect=RuntimeError("bug")):
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["errors"] == {"base": "unknown"}


async def test_user_flow_already_configured(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    """HA-05: adding the same matrix twice aborts with already_configured (AbortFlow is not swallowed)."""
    MockConfigEntry(domain=DOMAIN, data=USER_INPUT, unique_id=MAC).add_to_hass(hass)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_same_matrix_new_address_updates_entry(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry
) -> None:
    """The matrix is already set up under an old hub address: the entry follows it (keyed by MAC)."""
    entry = MockConfigEntry(domain=DOMAIN, data={"host": "192.0.2.99", "port": 8080}, unique_id=MAC)
    entry.add_to_hass(hass)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data == USER_INPUT


async def test_user_flow_same_address_aborts_before_probing(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry
) -> None:
    MockConfigEntry(domain=DOMAIN, data=USER_INPUT, unique_id=f"{HOST}:{PORT}").add_to_hass(hass)
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert not hub.mock.mock_calls


@pytest.mark.parametrize("port", [0, 65536, -1])
async def test_user_flow_rejects_invalid_port(hass: HomeAssistant, hub: MockHub, mock_setup_entry, port: int) -> None:
    """HA-11: the port must be 1-65535."""
    result = await _start_flow(hass)
    with pytest.raises(InvalidData):
        await hass.config_entries.flow.async_configure(result["flow_id"], {"host": HOST, "port": port})
    assert not hub.mock.mock_calls


# ------------------------------------------------------------------ reconfigure


async def test_reconfigure_changes_address(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"host": "192.0.2.20", "port": 8081})
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data == {"host": "192.0.2.20", "port": 8081}
    assert coordinator(entry).client.base_url == "http://192.0.2.20:8081"  # reloaded with the new address


async def test_reconfigure_other_matrix_aborts(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    device = hub.fixture_copy("/api/status/device")
    device["data"]["device"]["mac_address"] = "02:00:00:00:00:99"
    hub.set_response("/api/status/device", device)

    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"host": "192.0.2.20", "port": 8081})

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "wrong_device"
    assert entry.data == USER_INPUT


async def test_reconfigure_cannot_connect(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    hub.set_read_error("/api/health", aiohttp.ClientConnectionError())
    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"host": "192.0.2.20", "port": 8081})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


# ------------------------------------------------------------------ options


async def test_options_flow_sets_polling_interval(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    assert coordinator(entry).update_interval == timedelta(seconds=15)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"scan_interval": 30})
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {"scan_interval": 30}
    assert coordinator(entry).update_interval == timedelta(seconds=30)


async def test_options_flow_rejects_out_of_range(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    result = await hass.config_entries.options.async_init(setup_integration.entry_id)
    with pytest.raises(InvalidData):
        await hass.config_entries.options.async_configure(result["flow_id"], {"scan_interval": 1})


# ------------------------------------------------------------------ API key (control lock)
#
# Health and device information need no key, so a probe that reads only those accepted any
# key. With the hub's control lock set, setup then "worked" and every command answered 401.


@pytest.mark.parametrize("entered", [{}, {CONF_API_KEY: ""}, {CONF_API_KEY: "wrong-key"}, {CONF_API_KEY: "revoked"}])
async def test_user_flow_locked_hub_rejects_a_missing_wrong_or_revoked_key(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry, entered: dict
) -> None:
    hub.lock_control("ha-key")

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, **entered})

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
    assert not hass.config_entries.async_entries(DOMAIN)
    assert not mock_setup_entry.mock_calls


async def test_user_flow_locked_hub_accepts_its_key(hass: HomeAssistant, hub: MockHub, mock_setup_entry) -> None:
    hub.lock_control("ha-key")

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, CONF_API_KEY: " ha-key "})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {**USER_INPUT, CONF_API_KEY: "ha-key"}


async def test_user_flow_locked_hub_with_its_key_and_the_matrix_offline(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry
) -> None:
    """The key check does not need the matrix: an offline matrix still sets up (by address)."""
    hub.lock_control("ha-key")
    hub.set_response("/api/status/device", {"success": False, "data": None, "error": "Matrix not connected"}, 503)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, CONF_API_KEY: "ha-key"})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == f"{HOST}:{PORT}"


async def test_user_flow_unlocked_hub_needs_no_key_and_ignores_one(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry
) -> None:
    """Negative control: without a control PIN the hub accepts every request, so any key passes."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, CONF_API_KEY: "anything"})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_API_KEY] == "anything"


async def test_user_flow_fails_closed_when_auth_status_is_404(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry
) -> None:
    """Missing ``/api/auth/status`` (404) fails closed instead of assuming the hub is unlocked."""
    hub.auth_status_code = 404

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth_status"}
    assert not hass.config_entries.async_entries(DOMAIN)
    assert not mock_setup_entry.mock_calls


async def test_reconfigure_locked_hub_rejects_a_wrong_key(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    hub.lock_control("ha-key")

    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, CONF_API_KEY: "wrong-key"})

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
    assert entry.data == USER_INPUT


async def test_reconfigure_stores_a_new_key_and_uses_it(hass: HomeAssistant, hub: MockHub, setup_integration) -> None:
    entry = setup_integration
    hub.lock_control("ha-key")

    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, CONF_API_KEY: "ha-key"})
    await hass.async_block_till_done()

    assert result["reason"] == "reconfigure_successful"
    assert entry.data == {**USER_INPUT, CONF_API_KEY: "ha-key"}
    assert coordinator(entry).client.api_key == "ha-key"  # reloaded with the new key


async def test_reconfigure_replaces_a_key_that_options_used_to_shadow(hass: HomeAssistant, hub: MockHub) -> None:
    """An API key saved in the options took precedence for good: Reconfigure changed nothing."""
    # Arrange: an entry as earlier versions stored it, the key in use held by the options
    hub.lock_control("old-key", "new-key")
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={**USER_INPUT, CONF_API_KEY: "stale-key"},
        options={CONF_SCAN_INTERVAL: 30, CONF_API_KEY: "old-key"},
        unique_id=MAC,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Assert: setup kept the key that was in use and moved it to the one place it now lives
    assert coordinator(entry).client.api_key == "old-key"
    assert entry.data == {**USER_INPUT, CONF_API_KEY: "old-key"}
    assert entry.options == {CONF_SCAN_INTERVAL: 30}

    # Act: the user enters a new key in Reconfigure
    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, CONF_API_KEY: "new-key"})
    await hass.async_block_till_done()

    # Assert: it is the key the integration uses
    assert result["reason"] == "reconfigure_successful"
    assert entry.data == {**USER_INPUT, CONF_API_KEY: "new-key"}
    assert entry.options == {CONF_SCAN_INTERVAL: 30}
    assert coordinator(entry).client.api_key == "new-key"


async def test_reconfigure_with_the_key_cleared_removes_it(hass: HomeAssistant, hub: MockHub) -> None:
    """A cleared field stored ``""``; the key is removed from the entry."""
    entry = MockConfigEntry(domain=DOMAIN, data={**USER_INPUT, CONF_API_KEY: "ha-key"}, unique_id=MAC)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**USER_INPUT, CONF_API_KEY: ""})
    await hass.async_block_till_done()

    assert result["reason"] == "reconfigure_successful"
    assert entry.data == USER_INPUT
    assert coordinator(entry).client.api_key is None


async def test_options_flow_checks_a_changed_key_and_stores_it_in_the_entry_data(
    hass: HomeAssistant, hub: MockHub, setup_integration
) -> None:
    entry = setup_integration
    hub.lock_control("ha-key")

    # Act: a key the hub does not accept
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30, CONF_API_KEY: "wrong-key"}
    )

    # Assert: refused, nothing stored
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
    assert (entry.data, entry.options) == (USER_INPUT, {})

    # Act: the right key
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30, CONF_API_KEY: "ha-key"}
    )
    await hass.async_block_till_done()

    # Assert: the key is in the entry data, never in the options, and in use
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.data == {**USER_INPUT, CONF_API_KEY: "ha-key"}
    assert entry.options == {CONF_SCAN_INTERVAL: 30}
    assert coordinator(entry).client.api_key == "ha-key"
    assert coordinator(entry).update_interval == timedelta(seconds=30)


async def test_options_flow_changes_the_interval_while_the_hub_is_unreachable(
    hass: HomeAssistant, hub: MockHub, setup_integration
) -> None:
    """An unchanged key is not checked again, so the hub is not needed to change the interval."""
    entry = setup_integration
    hub.mock.mock_calls.clear()
    hub.set_read_error("/api/health", aiohttp.ClientConnectionError())

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {CONF_SCAN_INTERVAL: 45})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {CONF_SCAN_INTERVAL: 45}
    assert "/api/auth/status" not in [call[1].path for call in hub.mock.mock_calls]


async def test_reconfigure_and_options_fail_closed_when_auth_status_is_404(
    hass: HomeAssistant, hub: MockHub, setup_integration
) -> None:
    """Reconfigure and changed-key Options checks also fail closed when ``/api/auth/status`` is 404."""
    entry = setup_integration
    hub.auth_status_code = 404

    reconf = await entry.start_reconfigure_flow(hass)
    reconf = await hass.config_entries.flow.async_configure(
        reconf["flow_id"], {**USER_INPUT, CONF_API_KEY: "new-key"}
    )
    assert reconf["type"] is FlowResultType.FORM
    assert reconf["errors"] == {"base": "invalid_auth_status"}
    assert entry.data == USER_INPUT

    opt = await hass.config_entries.options.async_init(entry.entry_id)
    opt = await hass.config_entries.options.async_configure(
        opt["flow_id"], {CONF_SCAN_INTERVAL: 30, CONF_API_KEY: "new-key"}
    )
    assert opt["type"] is FlowResultType.FORM
    assert opt["errors"] == {"base": "invalid_auth_status"}
    assert (entry.data, entry.options) == (USER_INPUT, {})


@pytest.mark.parametrize("raw_body", _MALFORMED_AUTH_BODIES)
async def test_user_flow_fails_closed_when_auth_status_is_malformed_200(
    hass: HomeAssistant, hub: MockHub, mock_setup_entry, raw_body: str
) -> None:
    """Malformed HTTP 200 answers on ``/api/auth/status`` fail closed in the user step."""

    async def _malformed(method: str, url: Any, _data: Any) -> AiohttpClientMockResponse:
        return AiohttpClientMockResponse(method, url, status=200, text=raw_body)

    with patch.object(hub, "_auth_status", side_effect=_malformed):
        hub.register()
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth_status"}
    assert not hass.config_entries.async_entries(DOMAIN)
    assert not mock_setup_entry.mock_calls


@pytest.mark.parametrize("raw_body", _MALFORMED_AUTH_BODIES)
async def test_reconfigure_and_options_fail_closed_when_auth_status_is_malformed_200(
    hass: HomeAssistant, hub: MockHub, setup_integration, raw_body: str
) -> None:
    """Malformed HTTP 200 answers on ``/api/auth/status`` fail closed in Reconfigure and Options."""
    entry = setup_integration

    async def _malformed(method: str, url: Any, _data: Any) -> AiohttpClientMockResponse:
        return AiohttpClientMockResponse(method, url, status=200, text=raw_body)

    with patch.object(hub, "_auth_status", side_effect=_malformed):
        hub.register()
        reconf = await entry.start_reconfigure_flow(hass)
        reconf = await hass.config_entries.flow.async_configure(
            reconf["flow_id"], {**USER_INPUT, CONF_API_KEY: "new-key"}
        )
        assert reconf["type"] is FlowResultType.FORM
        assert reconf["errors"] == {"base": "invalid_auth_status"}
        assert entry.data == USER_INPUT

        opt = await hass.config_entries.options.async_init(entry.entry_id)
        opt = await hass.config_entries.options.async_configure(
            opt["flow_id"], {CONF_SCAN_INTERVAL: 30, CONF_API_KEY: "new-key"}
        )
        assert opt["type"] is FlowResultType.FORM
        assert opt["errors"] == {"base": "invalid_auth_status"}
        assert (entry.data, entry.options) == (USER_INPUT, {})


async def test_options_flow_clearing_key_removes_it_or_rejects_when_locked(
    hass: HomeAssistant, hub: MockHub
) -> None:
    """Clearing the API key in Options fails closed on a locked hub and removes it on an unlocked hub."""
    hub.lock_control("ha-key")
    entry = MockConfigEntry(domain=DOMAIN, data={**USER_INPUT, CONF_API_KEY: "ha-key"}, unique_id=MAC)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30, CONF_API_KEY: ""}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
    assert entry.data == {**USER_INPUT, CONF_API_KEY: "ha-key"}
    assert coordinator(entry).client.api_key == "ha-key"

    hub.control_pin_set = False
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30, CONF_API_KEY: "   "}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.data == USER_INPUT
    assert entry.options == {CONF_SCAN_INTERVAL: 30}
    assert coordinator(entry).client.api_key is None


async def test_reconfigure_and_options_each_reload_exactly_once(
    hass: HomeAssistant, hub: MockHub
) -> None:
    """Setup migration, Reconfigure (changed or unchanged), and Options each run setup once."""
    setup_calls = 0
    real_setup_entry = hdmi_matrix.async_setup_entry

    async def _counting_setup(hass_arg: HomeAssistant, entry_arg: Any) -> bool:
        nonlocal setup_calls
        setup_calls += 1
        return await real_setup_entry(hass_arg, entry_arg)

    hub.lock_control("old-key", "new-key")
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={**USER_INPUT, CONF_API_KEY: "stale-key"},
        options={CONF_SCAN_INTERVAL: 20, CONF_API_KEY: "old-key"},
        unique_id=MAC,
    )
    entry.add_to_hass(hass)

    with patch("custom_components.hdmi_matrix.async_setup_entry", side_effect=_counting_setup):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert setup_calls == 1

        reconf = await entry.start_reconfigure_flow(hass)
        reconf = await hass.config_entries.flow.async_configure(
            reconf["flow_id"], {"host": "192.0.2.20", "port": 8081, CONF_API_KEY: "new-key"}
        )
        await hass.async_block_till_done()
        assert reconf["type"] is FlowResultType.ABORT
        assert reconf["reason"] == "reconfigure_successful"
        assert setup_calls == 2
        assert entry.data == {"host": "192.0.2.20", "port": 8081, CONF_API_KEY: "new-key"}
        assert entry.options == {CONF_SCAN_INTERVAL: 20}
        assert coordinator(entry).client.api_key == "new-key"

        reconf_same = await entry.start_reconfigure_flow(hass)
        reconf_same = await hass.config_entries.flow.async_configure(
            reconf_same["flow_id"], {"host": "192.0.2.20", "port": 8081, CONF_API_KEY: "new-key"}
        )
        await hass.async_block_till_done()
        assert reconf_same["reason"] == "reconfigure_successful"
        assert setup_calls == 3

        hub.control_pin_set = False
        opt = await hass.config_entries.options.async_init(entry.entry_id)
        opt = await hass.config_entries.options.async_configure(
            opt["flow_id"], {CONF_SCAN_INTERVAL: 45, CONF_API_KEY: ""}
        )
        await hass.async_block_till_done()
        assert opt["type"] is FlowResultType.CREATE_ENTRY
        assert setup_calls == 4
        assert entry.data == {"host": "192.0.2.20", "port": 8081}
        assert entry.options == {CONF_SCAN_INTERVAL: 45}
        assert coordinator(entry).client.api_key is None


async def test_localized_auth_error_messages_are_truthful(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """Every flow error code has a distinct, truthful localized message in strings and English translations."""
    assert setup_integration.domain == DOMAIN
    strings = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
    en = json.loads((COMPONENT / "translations" / "en.json").read_text(encoding="utf-8"))
    assert strings == en

    for section in ("config", "options"):
        errors = strings[section]["error"]
        assert {"cannot_connect", "invalid_auth", "invalid_auth_status", "unknown"} <= set(errors)
        assert len(set(errors.values())) == len(errors)
        assert "/api/auth/status" in errors["invalid_auth_status"]
        assert "Cannot connect" not in errors["invalid_auth_status"]
        assert "control PIN" not in errors["invalid_auth_status"]
        assert "control PIN" in errors["invalid_auth"]
        assert "Cannot connect" in errors["cannot_connect"]

    config_tr = await translation.async_get_translations(hass, "en", "config", {DOMAIN}, config_flow=True)
    options_tr = await translation.async_get_translations(hass, "en", "options", {DOMAIN})
    assert config_tr[f"component.{DOMAIN}.config.error.invalid_auth_status"] == (
        strings["config"]["error"]["invalid_auth_status"]
    )
    assert options_tr[f"component.{DOMAIN}.options.error.invalid_auth_status"] == (
        strings["options"]["error"]["invalid_auth_status"]
    )
