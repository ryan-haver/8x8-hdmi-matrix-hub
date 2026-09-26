"""Config flow: add the hub (user), change its address (reconfigure), polling interval (options)."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .api import HubClient, HubError
from .const import (
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_PORT = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))  # HA-11
_MAC = re.compile(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")


def is_mac(unique_id: str | None) -> bool:
    """Entries created before HA-11 (or while the matrix was offline) use the address instead."""
    return bool(unique_id and _MAC.match(unique_id))


def _schema(host: str = "", port: int = DEFAULT_PORT) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_IP_ADDRESS, default=host): str,
            vol.Required(CONF_PORT, default=port): _PORT,
        }
    )


class HdmiMatrixConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the HDMI Matrix hub."""

    VERSION = 1
    MINOR_VERSION = 1

    async def _probe(self, host: str, port: int) -> tuple[str | None, dict[str, str]]:
        """Check the hub answers; return ``(matrix MAC or None, errors)``.

        The MAC (``/api/status/device``) is the entry's unique id, so the entry
        survives an address change (HA-11). A hub whose matrix is offline has no
        MAC yet: the entry then uses ``host:port`` until setup learns the MAC.
        """
        client = HubClient(async_get_clientsession(self.hass), host, port)
        try:
            await client.health()
        except HubError:
            return None, {"base": "cannot_connect"}
        except Exception:  # noqa: BLE001 - shown as "unknown", logged for the user
            LOGGER.exception("Unexpected error talking to the hub at %s:%s", host, port)
            return None, {"base": "unknown"}
        try:
            mac = (await client.device()).get("mac_address")
        except HubError:
            mac = None
        return (format_mac(str(mac)) if mac else None), {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host, port = user_input[CONF_IP_ADDRESS].strip(), user_input[CONF_PORT]
            self._async_abort_entries_match({CONF_IP_ADDRESS: host, CONF_PORT: port})
            mac, errors = await self._probe(host, port)
            if not errors:
                # Outside any try/except: AbortFlow must reach the flow manager (HA-05).
                await self.async_set_unique_id(mac or f"{host}:{port}")
                self._abort_if_unique_id_configured(updates={CONF_IP_ADDRESS: host, CONF_PORT: port})
                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} ({host})", data={CONF_IP_ADDRESS: host, CONF_PORT: port}
                )
            user_input = {CONF_IP_ADDRESS: host, CONF_PORT: port}
        defaults = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=_schema(defaults.get(CONF_IP_ADDRESS, ""), defaults.get(CONF_PORT, DEFAULT_PORT)),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Point an existing entry at a new hub address (same matrix)."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            host, port = user_input[CONF_IP_ADDRESS].strip(), user_input[CONF_PORT]
            mac, errors = await self._probe(host, port)
            if not errors:
                if mac and is_mac(entry.unique_id):
                    # The new address must reach the matrix this entry controls.
                    await self.async_set_unique_id(mac)
                    self._abort_if_unique_id_mismatch(reason="wrong_device")
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_IP_ADDRESS: host, CONF_PORT: port}
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_schema(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT]),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> HdmiMatrixOptionsFlow:
        return HdmiMatrixOptionsFlow()


class HdmiMatrixOptionsFlow(OptionsFlow):
    """Polling interval."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                    ),
                }
            ),
        )
