"""Support for OREI HDMI Matrix output source selection."""

import aiohttp
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER

# 10s timeout for all matrix HTTP calls.
_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OREI Matrix select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a select entity for each output port
    entities = []
    # BK-808 always has 8 output ports
    for i in range(1, 9):
        entities.append(OreiOutputSelect(coordinator, i))

    async_add_entities(entities)


class OreiOutputSelect(CoordinatorEntity, SelectEntity):
    """Representation of an OREI Matrix output source selector."""

    def __init__(self, coordinator, output_num):
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.output_num = output_num
        self._attr_name = f"Output {output_num} Source"
        self._attr_unique_id = f"{coordinator.host}_output_{output_num}_source"

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
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        routing = self.coordinator.data["status"].get("routing", [])
        # routing is an array: [input_for_output_1, input_for_output_2, ...]
        if isinstance(routing, list) and 0 <= self.output_num - 1 < len(routing):
            input_num = routing[self.output_num - 1]
        else:
            input_num = None
        if input_num is not None:
            return (
                self.coordinator.data["status"].get("input_names", {}).get(str(input_num))
                or self.coordinator.data["status"].get("input_names", {}).get(input_num)
                or f"Input {input_num}"
            )
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        input_names = self.coordinator.data["status"].get("input_names", {})
        options = []
        for i in range(1, 9):
            name = input_names.get(str(i)) or input_names.get(i) or f"Input {i}"
            options.append(name)
        return options

    async def async_select_option(self, option: str) -> None:
        """Change the active source."""
        # Find input number matching the option name. If two inputs share
        # the same name, prefer the one currently routed to this output;
        # fall back to the first match if no routing data is available.
        # FIX (F10.4): previously the first match always won, making the
        # second identically-named input unreachable.
        input_names = self.coordinator.data.get("status", {}).get("input_names", {})
        matches = [
            i
            for i in range(1, 9)
            if (input_names.get(str(i)) or input_names.get(i) or f"Input {i}") == option
        ]
        if len(matches) > 1:
            routing = self.coordinator.data.get("status", {}).get("routing", [])
            if isinstance(routing, list) and 0 <= self.output_num - 1 < len(routing):
                current = routing[self.output_num - 1]
                if current in matches:
                    input_num = current
                else:
                    LOGGER.warning(
                        "Multiple inputs share name '%s': %s. Using first.",
                        option,
                        matches,
                    )
                    input_num = matches[0]
            else:
                input_num = matches[0]
        elif len(matches) == 1:
            input_num = matches[0]
        else:
            LOGGER.error("Selected option %s does not match any input names", option)
            return

        session = self.coordinator.hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{self.coordinator.base_url}/api/output/{self.output_num}/source"
        payload = {"input": input_num}

        try:
            async with session.post(url, json=payload, timeout=_TIMEOUT) as resp:
                if resp.status == 200:
                    json_resp = await resp.json()
                    if json_resp.get("success"):
                        # Force refresh
                        await self.coordinator.async_request_refresh()
                    else:
                        LOGGER.error("Failed to set routing: %s", json_resp.get("error"))
                else:
                    LOGGER.error("HTTP error setting routing: %s", resp.status)
        except Exception as err:
            LOGGER.error("Error setting routing: %s", err)
