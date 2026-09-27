"""The integration's services, registered once in ``async_setup`` (HA-06).

Each call targets one matrix: ``config_entry_id`` or ``device_id``, or nothing
when exactly one matrix is set up. Bad input is a ``ServiceValidationError``
(nothing is sent); a hub failure is a ``HomeAssistantError`` shown to the user.
"""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import (
    ATTR_COMMAND,
    ATTR_CONFIG_ENTRY_ID,
    ATTR_DEVICE_ID,
    ATTR_INPUT,
    ATTR_OUTPUT,
    ATTR_PORT_NUM,
    ATTR_PORT_TYPE,
    ATTR_PRESET,
    CEC_COMMANDS,
    CEC_INPUT_COMMANDS,
    CEC_OUTPUT_COMMANDS,
    DOMAIN,
    PORT_COUNT,
    PRESET_COUNT,
    SERVICE_RECALL_PRESET,
    SERVICE_SEND_CEC_COMMAND,
    SERVICE_SWITCH_INPUT,
)
from .coordinator import HdmiMatrixConfigEntry
from .entity import call_hub

_PORT = vol.All(vol.Coerce(int), vol.Range(min=1, max=PORT_COUNT))

_TARGET = {
    vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
    vol.Optional(ATTR_DEVICE_ID): cv.string,
}

RECALL_PRESET_SCHEMA = vol.Schema(
    {**_TARGET, vol.Required(ATTR_PRESET): vol.All(vol.Coerce(int), vol.Range(min=1, max=PRESET_COUNT))}
)
SWITCH_INPUT_SCHEMA = vol.Schema({**_TARGET, vol.Required(ATTR_OUTPUT): _PORT, vol.Required(ATTR_INPUT): _PORT})
SEND_CEC_SCHEMA = vol.Schema(
    {
        **_TARGET,
        vol.Required(ATTR_PORT_TYPE): vol.In(["input", "output"]),
        vol.Required(ATTR_PORT_NUM): _PORT,
        # Only commands the hub knows (HA-12); never interpolated unchecked into the URL.
        vol.Required(ATTR_COMMAND): vol.All(cv.string, vol.Lower, vol.In(CEC_COMMANDS)),
    }
)


def _entry(hass: HomeAssistant, call: ServiceCall) -> HdmiMatrixConfigEntry:
    """The loaded entry a call targets."""
    entry_id = call.data.get(ATTR_CONFIG_ENTRY_ID)
    device_id = call.data.get(ATTR_DEVICE_ID)
    if device_id and not entry_id:
        device = dr.async_get(hass).async_get(device_id)
        entry_id = next(
            (e for e in (device.config_entries if device else ()) if (ce := hass.config_entries.async_get_entry(e))
             and ce.domain == DOMAIN),
            None,
        )
        if entry_id is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="unknown_device", translation_placeholders={"device_id": device_id}
            )
    if entry_id:
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None or entry.domain != DOMAIN:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="unknown_entry", translation_placeholders={"entry_id": entry_id}
            )
        if entry.state is not ConfigEntryState.LOADED:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="entry_not_loaded", translation_placeholders={"title": entry.title}
            )
        return entry
    loaded = [e for e in hass.config_entries.async_entries(DOMAIN) if e.state is ConfigEntryState.LOADED]
    if len(loaded) == 1:
        return loaded[0]
    raise ServiceValidationError(
        translation_domain=DOMAIN, translation_key="no_target" if not loaded else "ambiguous_target"
    )


async def _recall_preset(hass: HomeAssistant, call: ServiceCall) -> None:
    entry = _entry(hass, call)
    await call_hub(entry.runtime_data.client.recall_preset(call.data[ATTR_PRESET]))
    await entry.runtime_data.coordinator.async_request_refresh()


async def _switch_input(hass: HomeAssistant, call: ServiceCall) -> None:
    entry = _entry(hass, call)
    await call_hub(entry.runtime_data.client.route(call.data[ATTR_OUTPUT], call.data[ATTR_INPUT]))
    await entry.runtime_data.coordinator.async_request_refresh()


async def _send_cec_command(hass: HomeAssistant, call: ServiceCall) -> None:
    port_type, command = call.data[ATTR_PORT_TYPE], call.data[ATTR_COMMAND]
    if port_type == "output" and command not in CEC_OUTPUT_COMMANDS:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="cec_command_not_for_outputs",
            translation_placeholders={"command": command, "allowed": ", ".join(CEC_OUTPUT_COMMANDS)},
        )
    if port_type == "input" and command not in CEC_INPUT_COMMANDS:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="cec_command_not_for_inputs",
            translation_placeholders={"command": command},
        )
    entry = _entry(hass, call)
    await call_hub(entry.runtime_data.client.send_cec(port_type, call.data[ATTR_PORT_NUM], command))


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the services (once, for every entry)."""

    async def recall_preset(call: ServiceCall) -> None:
        await _recall_preset(hass, call)

    async def switch_input(call: ServiceCall) -> None:
        await _switch_input(hass, call)

    async def send_cec_command(call: ServiceCall) -> None:
        await _send_cec_command(hass, call)

    hass.services.async_register(DOMAIN, SERVICE_RECALL_PRESET, recall_preset, schema=RECALL_PRESET_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SWITCH_INPUT, switch_input, schema=SWITCH_INPUT_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SEND_CEC_COMMAND, send_cec_command, schema=SEND_CEC_SCHEMA)
