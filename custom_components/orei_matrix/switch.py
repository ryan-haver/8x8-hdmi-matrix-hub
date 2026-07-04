"""Support for OREI HDMI Matrix switches."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OREI Matrix switch entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # 1. Power Switch
    entities.append(OreiPowerSwitch(coordinator))
    
    # 2. Output Mute and Stream Switches
    output_count = coordinator.data["status"].get("outputs", [0]*8)
    for i in range(1, len(output_count) + 1):
        entities.append(OreiOutputMuteSwitch(coordinator, i))
        entities.append(OreiOutputStreamSwitch(coordinator, i))
        
    async_add_entities(entities)

class OreiPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of the OREI Matrix power switch."""

    def __init__(self, coordinator):
        """Initialize the power switch."""
        super().__init__(coordinator)
        self._attr_name = "Matrix Power"
        self._attr_unique_id = f"{coordinator.host}_power"

    @property
    def is_on(self) -> bool:
        """Return true if matrix is powered on."""
        return self.coordinator.data["status"].get("power") == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Power on the matrix."""
        session = self.coordinator.hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{self.coordinator.base_url}/api/power/on"
        try:
            async with session.post(url) as resp:
                if resp.status == 200:
                    json_resp = await resp.json()
                    if json_resp.get("success"):
                        await self.coordinator.async_request_refresh()
                    else:
                        LOGGER.error("Failed to power on: %s", json_resp.get("error"))
        except Exception as err:
            LOGGER.error("Error powering on: %s", err)

    async def async_turn_off(self, **kwargs) -> None:
        """Power off the matrix."""
        session = self.coordinator.hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{self.coordinator.base_url}/api/power/off"
        try:
            async with session.post(url) as resp:
                if resp.status == 200:
                    json_resp = await resp.json()
                    if json_resp.get("success"):
                        await self.coordinator.async_request_refresh()
                    else:
                        LOGGER.error("Failed to power off: %s", json_resp.get("error"))
        except Exception as err:
            LOGGER.error("Error powering off: %s", err)


class OreiOutputMuteSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an OREI Matrix output mute toggle."""

    def __init__(self, coordinator, output_num):
        """Initialize the mute switch."""
        super().__init__(coordinator)
        self.output_num = output_num
        self._attr_name = f"Output {output_num} Mute"
        self._attr_unique_id = f"{coordinator.host}_output_{output_num}_mute"

    @property
    def is_on(self) -> bool:
        """Return true if output audio is muted."""
        outputs = self.coordinator.data.get("outputs", [])
        for out in outputs:
            if out.get("number") == self.output_num:
                return out.get("muted") is True
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """Mute output audio."""
        await self._set_mute_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Unmute output audio."""
        await self._set_mute_state(False)

    async def _set_mute_state(self, muted: bool) -> None:
        """Send mute POST request."""
        session = self.coordinator.hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{self.coordinator.base_url}/api/output/{self.output_num}/mute"
        payload = {"muted": muted}
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    json_resp = await resp.json()
                    if json_resp.get("success"):
                        await self.coordinator.async_request_refresh()
                    else:
                        LOGGER.error("Failed to set mute: %s", json_resp.get("error"))
        except Exception as err:
            LOGGER.error("Error setting mute: %s", err)


class OreiOutputStreamSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an OREI Matrix output stream toggle."""

    def __init__(self, coordinator, output_num):
        """Initialize the stream switch."""
        super().__init__(coordinator)
        self.output_num = output_num
        self._attr_name = f"Output {output_num} Stream"
        self._attr_unique_id = f"{coordinator.host}_output_{output_num}_stream"

    @property
    def is_on(self) -> bool:
        """Return true if output stream is enabled."""
        outputs = self.coordinator.data.get("outputs", [])
        for out in outputs:
            if out.get("number") == self.output_num:
                return out.get("enabled") is True
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """Enable output stream."""
        await self._set_stream_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable output stream."""
        await self._set_stream_state(False)

    async def _set_stream_state(self, enabled: bool) -> None:
        """Send enable POST request."""
        session = self.coordinator.hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{self.coordinator.base_url}/api/output/{self.output_num}/enable"
        payload = {"enabled": enabled}
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    json_resp = await resp.json()
                    if json_resp.get("success"):
                        await self.coordinator.async_request_refresh()
                    else:
                        LOGGER.error("Failed to set stream: %s", json_resp.get("error"))
        except Exception as err:
            LOGGER.error("Error setting stream: %s", err)
