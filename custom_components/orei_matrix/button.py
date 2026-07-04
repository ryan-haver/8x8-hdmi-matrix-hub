"""Support for OREI HDMI Matrix buttons."""

import aiohttp
from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER

# 10s timeout for all matrix HTTP calls.
_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OREI Matrix button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # 1. Preset Recall Buttons
    for i in range(1, 9):
        entities.append(OreiPresetButton(coordinator, i))

    # 2. Reboot Button
    entities.append(OreiRebootButton(coordinator))

    async_add_entities(entities)


class OreiPresetButton(CoordinatorEntity, ButtonEntity):
    """Button to recall a matrix preset."""

    def __init__(self, coordinator, preset_num):
        """Initialize the button."""
        super().__init__(coordinator)
        self.preset_num = preset_num
        self._attr_unique_id = f"{coordinator.host}_preset_{preset_num}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            name=f"OREI HDMI Matrix ({self.coordinator.host})",
            manufacturer="OREI",
            model="BK-808",
            sw_version="1.0.0",
        )

    @property
    def name(self) -> str:
        """Return the name of the button."""
        preset_names = self.coordinator.data["status"].get("preset_names", {})
        custom_name = preset_names.get(str(self.preset_num)) or preset_names.get(self.preset_num)
        if custom_name:
            return f"Recall Preset {self.preset_num} ({custom_name})"
        return f"Recall Preset {self.preset_num}"

    async def async_press(self) -> None:
        """Press the button."""
        session = self.coordinator.hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{self.coordinator.base_url}/api/preset/{self.preset_num}"
        try:
            async with session.post(url, timeout=_TIMEOUT) as resp:
                if resp.status == 200:
                    json_resp = await resp.json()
                    if json_resp.get("success"):
                        await self.coordinator.async_request_refresh()
                    else:
                        LOGGER.error("Failed to recall preset: %s", json_resp.get("error"))
                else:
                    LOGGER.error("HTTP error recalling preset: %s", resp.status)
        except Exception as err:
            LOGGER.error("Error recalling preset: %s", err)


class OreiRebootButton(CoordinatorEntity, ButtonEntity):
    """Button to reboot the matrix."""

    def __init__(self, coordinator):
        """Initialize the reboot button."""
        super().__init__(coordinator)
        self._attr_name = "Reboot Matrix"
        self._attr_unique_id = f"{coordinator.host}_reboot"
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            name=f"OREI HDMI Matrix ({self.coordinator.host})",
            manufacturer="OREI",
            model="BK-808",
            sw_version="1.0.0",
        )

    async def async_press(self) -> None:
        """Press the button."""
        session = self.coordinator.hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{self.coordinator.base_url}/api/system/reboot"
        try:
            async with session.post(url, timeout=_TIMEOUT) as resp:
                if resp.status == 200:
                    json_resp = await resp.json()
                    if not json_resp.get("success"):
                        LOGGER.error("Failed to reboot matrix: %s", json_resp.get("error"))
                else:
                    LOGGER.error("HTTP error rebooting matrix: %s", resp.status)
        except Exception as err:
            LOGGER.error("Error rebooting matrix: %s", err)
