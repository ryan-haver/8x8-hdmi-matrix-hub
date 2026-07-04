"""Support for OREI HDMI Matrix output source selection."""
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OREI Matrix select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create a select entity for each output port
    entities = []
    output_count = coordinator.data["status"].get("outputs", [0]*8)
    for i in range(1, len(output_count) + 1):
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
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        routing = self.coordinator.data["status"].get("routing", {})
        # routing is a dict: {str(output_num): input_num}
        input_num = routing.get(str(self.output_num)) or routing.get(self.output_num)
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
        # Find input number matching the option name
        input_names = self.coordinator.data["status"].get("input_names", {})
        input_num = None
        for i in range(1, 9):
            name = input_names.get(str(i)) or input_names.get(i) or f"Input {i}"
            if name == option:
                input_num = i
                break
                
        if input_num is None:
            LOGGER.error("Selected option %s does not match any input names", option)
            return

        session = self.coordinator.hass.helpers.aiohttp_client.async_get_clientsession()
        url = f"{self.coordinator.base_url}/api/output/{self.output_num}/source"
        payload = {"input": input_num}
        
        try:
            async with session.post(url, json=payload) as resp:
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
