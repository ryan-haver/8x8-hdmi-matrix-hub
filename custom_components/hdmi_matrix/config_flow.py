"""Config flow: add the hub (user), change its address or API key (reconfigure), options.

The API key lives in one place, ``entry.data``. Every step that accepts a key
asks the hub whether it accepts it before the key is stored.
"""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .api import HubClient, HubError, HubResponseError
from .const import (
    CONF_API_KEY,
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


def _schema(host: str = "", port: int = DEFAULT_PORT, api_key: str = "") -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_IP_ADDRESS, default=host): str,
            vol.Required(CONF_PORT, default=port): _PORT,
            vol.Optional(CONF_API_KEY, default=api_key): str,
        }
    )


def _entered_key(user_input: dict[str, Any]) -> str | None:
    """The API key of a submitted form; an empty field means "no key"."""
    return (user_input.get(CONF_API_KEY) or "").strip() or None


def stored_api_key(entry: ConfigEntry) -> str | None:
    """The API key the entry uses.

    ``entry.data`` holds it. Options written by earlier versions of this
    integration may still carry a copy, which took precedence then and does
    until setup moves it into ``entry.data`` (``_async_adopt_options_api_key``).
    """
    return entry.options.get(CONF_API_KEY, entry.data.get(CONF_API_KEY)) or None


def _with_api_key(data: dict[str, Any], api_key: str | None) -> dict[str, Any]:
    """``data`` with the key set, or without one: an empty key is never stored."""
    data = {key: value for key, value in data.items() if key != CONF_API_KEY}
    if api_key:
        data[CONF_API_KEY] = api_key
    return data


async def async_probe(
    hass: HomeAssistant, host: str, port: int, api_key: str | None = None
) -> tuple[str | None, dict[str, str]]:
    """Check the hub answers and accepts the key; return ``(matrix MAC or None, errors)``.

    The MAC (``/api/status/device``) is the entry's unique id, so the entry
    survives an address change (HA-11). A hub whose matrix is offline has no
    MAC yet: the entry then uses ``host:port`` until setup learns the MAC.

    Health and device information need no key, so they say nothing about it.
    ``/api/auth/status`` does: with the hub's control lock set, a missing,
    wrong or revoked key is ``invalid_auth`` here, not a 401 on every command
    after setup. A hub without a control lock accepts any (or no) key.
    """
    client = HubClient(async_get_clientsession(hass), host, port, api_key)
    try:
        await client.health()
    except HubError:
        return None, {"base": "cannot_connect"}
    except Exception:  # noqa: BLE001 - shown as "unknown", logged for the user
        LOGGER.exception("Unexpected error talking to the hub at %s:%s", host, port)
        return None, {"base": "unknown"}
    try:
        if not await client.control_allowed():
            return None, {"base": "invalid_auth"}
    except HubResponseError as err:
        if err.status != 404:  # 404: a hub from before the access model, which has no locks
            return None, {"base": "cannot_connect"}
    except HubError:
        return None, {"base": "cannot_connect"}
    try:
        mac = (await client.device()).get("mac_address")
    except HubError:
        mac = None
    return (format_mac(str(mac)) if mac else None), {}


class HdmiMatrixConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the HDMI Matrix hub."""

    VERSION = 1
    MINOR_VERSION = 1

    async def _probe(self, host: str, port: int, api_key: str | None = None) -> tuple[str | None, dict[str, str]]:
        return await async_probe(self.hass, host, port, api_key)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host, port = user_input[CONF_IP_ADDRESS].strip(), user_input[CONF_PORT]
            self._async_abort_entries_match({CONF_IP_ADDRESS: host, CONF_PORT: port})
            api_key = _entered_key(user_input)
            mac, errors = await self._probe(host, port, api_key)
            if not errors:
                # Outside any try/except: AbortFlow must reach the flow manager (HA-05).
                await self.async_set_unique_id(mac or f"{host}:{port}")
                entry_data = {CONF_IP_ADDRESS: host, CONF_PORT: port}
                if api_key:
                    entry_data[CONF_API_KEY] = api_key
                self._abort_if_unique_id_configured(updates=entry_data)
                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} ({host})", data=entry_data
                )
            user_input = {CONF_IP_ADDRESS: host, CONF_PORT: port, CONF_API_KEY: api_key or ""}
        defaults = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=_schema(defaults.get(CONF_IP_ADDRESS, ""), defaults.get(CONF_PORT, DEFAULT_PORT), defaults.get(CONF_API_KEY, "")),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Point an existing entry at a new hub address (same matrix), or change its API key."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            host, port = user_input[CONF_IP_ADDRESS].strip(), user_input[CONF_PORT]
            api_key = _entered_key(user_input)
            mac, errors = await self._probe(host, port, api_key)
            if not errors:
                if mac and is_mac(entry.unique_id):
                    # The new address must reach the matrix this entry controls.
                    await self.async_set_unique_id(mac)
                    self._abort_if_unique_id_mismatch(reason="wrong_device")
                # The whole data, not an update: a cleared key is removed, not stored as "".
                # Options lose their old copy of the key, which would otherwise win at setup.
                return self.async_update_reload_and_abort(
                    entry,
                    data=_with_api_key({**entry.data, CONF_IP_ADDRESS: host, CONF_PORT: port}, api_key),
                    options={key: value for key, value in entry.options.items() if key != CONF_API_KEY},
                )
            user_input = {CONF_IP_ADDRESS: host, CONF_PORT: port, CONF_API_KEY: api_key or ""}
        defaults = user_input or {
            CONF_IP_ADDRESS: entry.data[CONF_IP_ADDRESS],
            CONF_PORT: entry.data[CONF_PORT],
            CONF_API_KEY: stored_api_key(entry) or "",
        }
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_schema(defaults[CONF_IP_ADDRESS], defaults[CONF_PORT], defaults[CONF_API_KEY]),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> HdmiMatrixOptionsFlow:
        return HdmiMatrixOptionsFlow()


class HdmiMatrixOptionsFlow(OptionsFlow):
    """Polling interval, and the API key (stored in ``entry.data``, never in the options)."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        entry = self.config_entry
        errors: dict[str, str] = {}
        current = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        api_key = stored_api_key(entry)
        if user_input is not None:
            current = user_input[CONF_SCAN_INTERVAL]
            entered = _entered_key(user_input)
            if entered != api_key:
                # A changed key is checked like at setup. An unchanged one is not: the
                # polling interval can be changed while the hub is unreachable.
                _mac, errors = await async_probe(
                    self.hass, entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT], entered
                )
            if not errors:
                options = {CONF_SCAN_INTERVAL: current}
                # One update for data and options, so the entry reloads once.
                self.hass.config_entries.async_update_entry(
                    entry, data=_with_api_key(dict(entry.data), entered), options=options
                )
                return self.async_create_entry(data=options)
            api_key = entered
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                    ),
                    vol.Optional(CONF_API_KEY, default=api_key or ""): str,
                }
            ),
            errors=errors,
        )
