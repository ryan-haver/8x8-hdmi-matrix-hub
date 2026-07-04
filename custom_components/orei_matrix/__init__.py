"""The OREI HDMI Matrix integration."""

import asyncio

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_IP_ADDRESS, CONF_PORT, DOMAIN, PLATFORMS
from .coordinator import OreiMatrixCoordinator

# 10s timeout for all matrix HTTP calls.
_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OREI HDMI Matrix from a config entry."""
    host = entry.data[CONF_IP_ADDRESS]
    port = entry.data[CONF_PORT]

    coordinator = OreiMatrixCoordinator(hass, host, port)

    # Fetch initial data to ensure the connection is working
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to the platforms (select, switch, button, binary_sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    import voluptuous as vol
    from homeassistant.helpers import config_validation as cv

    # Services schemas
    RECALL_PRESET_SCHEMA = vol.Schema({vol.Required("preset"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8))})

    SWITCH_INPUT_SCHEMA = vol.Schema(
        {
            vol.Required("output"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
            vol.Required("input"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
        }
    )

    SEND_CEC_SCHEMA = vol.Schema(
        {
            vol.Required("port_type"): vol.In(["input", "output"]),
            vol.Required("port_num"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
            vol.Required("command"): cv.string,
        }
    )

    # Register custom services
    async def handle_recall_preset(call):
        preset = call.data["preset"]
        session = hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{coordinator.base_url}/api/preset/{preset}"
        try:
            async with session.post(url, timeout=_TIMEOUT) as resp:
                if resp.status == 200:
                    await coordinator.async_request_refresh()
        except Exception as err:
            coordinator.logger.error("Error recalling preset via service: %s", err)

    async def handle_switch_input(call):
        output = call.data["output"]
        input_num = call.data["input"]
        session = hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{coordinator.base_url}/api/output/{output}/source"
        try:
            async with session.post(url, json={"input": input_num}, timeout=_TIMEOUT) as resp:
                if resp.status == 200:
                    await coordinator.async_request_refresh()
        except Exception as err:
            coordinator.logger.error("Error switching input via service: %s", err)

    async def handle_send_cec_command(call):
        port_type = call.data["port_type"]
        port_num = call.data["port_num"]
        command = call.data["command"]
        session = hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{coordinator.base_url}/api/cec/{port_type}/{port_num}/{command}"
        try:
            async with session.post(url, timeout=_TIMEOUT):
                pass
        except Exception as err:
            coordinator.logger.error("Error sending CEC command via service: %s", err)

    hass.services.async_register(DOMAIN, "recall_preset", handle_recall_preset, schema=RECALL_PRESET_SCHEMA)
    hass.services.async_register(DOMAIN, "switch_input", handle_switch_input, schema=SWITCH_INPUT_SCHEMA)
    hass.services.async_register(DOMAIN, "send_cec_command", handle_send_cec_command, schema=SEND_CEC_SCHEMA)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # If no other entries exist, deregister services
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "recall_preset")
            hass.services.async_remove(DOMAIN, "switch_input")
            hass.services.async_remove(DOMAIN, "send_cec_command")

    return unload_ok
