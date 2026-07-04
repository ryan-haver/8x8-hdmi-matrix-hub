"""Config flow for OREI HDMI Matrix integration."""

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_IP_ADDRESS, CONF_PORT, DEFAULT_NAME, DEFAULT_PORT, DOMAIN


class OreiMatrixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OREI HDMI Matrix."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_IP_ADDRESS]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)

            # Validate connection
            session = async_get_clientsession(self.hass)
            try:
                async with session.get(f"http://{host}:{port}/api/health", timeout=5) as resp:
                    if resp.status == 200:
                        # Set unique ID
                        await self.async_set_unique_id(host)
                        self._abort_if_unique_id_configured()

                        return self.async_create_entry(
                            title=f"{DEFAULT_NAME} ({host})",
                            data=user_input,
                        )
                    else:
                        errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        # Show config form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
