"""The HDMI Matrix integration: an OREI HDMI matrix through the hub's REST API."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import HubClient, HubError
from .const import CONF_IP_ADDRESS, CONF_PORT, DOMAIN, LOGGER, PLATFORMS
from .coordinator import HdmiMatrixConfigEntry, HdmiMatrixCoordinator, HdmiMatrixRuntimeData
from .services import async_setup_services

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the services once, whatever the number of entries (HA-06)."""
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: HdmiMatrixConfigEntry) -> bool:
    """Connect to the hub, fetch the first state, and set up the platforms."""
    client = HubClient(async_get_clientsession(hass), entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])

    device: dict = {}
    try:
        device = await client.device()
    except HubError as err:  # the matrix may be offline; firmware and MAC are optional
        LOGGER.debug("No device information from the hub yet: %s", err)
    await _async_migrate_unique_id(hass, entry, device.get("mac_address"))

    coordinator = HdmiMatrixCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = HdmiMatrixRuntimeData(client=client, coordinator=coordinator, device=device)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Entity names include the hub's input/output/preset names: reload when they change.
    names = coordinator.data.names()

    @callback
    def _names_changed() -> None:
        if coordinator.last_update_success and coordinator.data.names() != names:
            LOGGER.debug("Names changed on the hub; reloading %s", entry.title)
            hass.config_entries.async_schedule_reload(entry.entry_id)

    entry.async_on_unload(coordinator.async_add_listener(_names_changed))
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: HdmiMatrixConfigEntry) -> bool:
    """Unload the platforms (the services stay: they belong to the integration)."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_options_updated(hass: HomeAssistant, entry: HdmiMatrixConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_migrate_unique_id(hass: HomeAssistant, entry: HdmiMatrixConfigEntry, mac: str | None) -> None:
    """Move an entry identified by its address (before HA-11) to the matrix MAC.

    Entities and the device keep their history: their unique ids / identifiers
    are rewritten from the old prefix to the new one.
    """
    if not mac:
        return
    new = dr.format_mac(mac)
    old = entry.unique_id
    host, port = entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT]
    if old == new or old not in (host, f"{host}:{port}"):
        return
    if any(e.unique_id == new for e in hass.config_entries.async_entries(DOMAIN) if e.entry_id != entry.entry_id):
        LOGGER.warning("Another entry already uses matrix %s; keeping %s for %s", new, old, entry.title)
        return

    @callback
    def _rename(reg_entry: er.RegistryEntry) -> dict[str, str] | None:
        if reg_entry.unique_id.startswith(f"{old}_"):
            return {"new_unique_id": f"{new}_{reg_entry.unique_id[len(old) + 1:]}"}
        return None

    await er.async_migrate_entries(hass, entry.entry_id, _rename)
    registry = dr.async_get(hass)
    if device := registry.async_get_device(identifiers={(DOMAIN, old)}):
        registry.async_update_device(device.id, new_identifiers={(DOMAIN, new)})
    hass.config_entries.async_update_entry(entry, unique_id=new)
    LOGGER.info("Matrix %s is now identified by its MAC %s", old, new)
