"""Support for OREI HDMI Matrix binary sensors."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OREI Matrix binary sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # 1. Input Signal Sensors
    input_count = len(coordinator.data["status"].get("input_names", {})) or 8
    for i in range(1, input_count + 1):
        entities.append(OreiInputSignalSensor(coordinator, i))

    # 2. Output Connection Sensors
    output_count = len(coordinator.data["status"].get("outputs", [0] * 8))
    for i in range(1, output_count + 1):
        entities.append(OreiOutputConnectionSensor(coordinator, i))

    async_add_entities(entities)


class OreiInputSignalSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for HDMI input video signal active status."""

    def __init__(self, coordinator, input_num):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.input_num = input_num
        self._attr_unique_id = f"{coordinator.host}_input_{input_num}_signal"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        input_names = self.coordinator.data["status"].get("input_names", {})
        custom_name = input_names.get(str(self.input_num)) or input_names.get(self.input_num)
        if custom_name:
            return f"Input {self.input_num} ({custom_name}) Signal"
        return f"Input {self.input_num} Signal"

    @property
    def is_on(self) -> bool:
        """Return true if video signal is active."""
        inputs = self.coordinator.data.get("inputs", [])
        for inp in inputs:
            if inp.get("number") == self.input_num:
                return inp.get("signalActive") is True
        return False

    @property
    def device_class(self):
        """Return the device class."""
        return "connectivity"


class OreiOutputConnectionSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for HDMI output display connection status."""

    def __init__(self, coordinator, output_num):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.output_num = output_num
        self._attr_unique_id = f"{coordinator.host}_output_{output_num}_connected"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        output_names = self.coordinator.data["status"].get("output_names", {})
        custom_name = output_names.get(str(self.output_num)) or output_names.get(self.output_num)
        if custom_name:
            return f"Output {self.output_num} ({custom_name}) Display"
        return f"Output {self.output_num} Display"

    @property
    def is_on(self) -> bool:
        """Return true if display is connected."""
        outputs = self.coordinator.data.get("outputs", [])
        for out in outputs:
            if out.get("number") == self.output_num:
                # Prefer cableConnected, fallback to connected
                if out.get("cableConnected") is not None:
                    return out.get("cableConnected") is True
                return out.get("connected") is True
        return False

    @property
    def device_class(self):
        """Return the device class."""
        return "plug"
