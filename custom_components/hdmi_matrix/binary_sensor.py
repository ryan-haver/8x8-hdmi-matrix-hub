"""Input signal and output display binary sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import PORT_COUNT
from .coordinator import HdmiMatrixConfigEntry
from .entity import HdmiMatrixEntity, port_label

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: HdmiMatrixConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entities: list[BinarySensorEntity] = [HdmiMatrixInputSignal(entry, n) for n in range(1, PORT_COUNT + 1)]
    entities.extend(HdmiMatrixOutputDisplay(entry, n) for n in range(1, PORT_COUNT + 1))
    async_add_entities(entities)


class HdmiMatrixInputSignal(HdmiMatrixEntity, BinarySensorEntity):
    """On while the source on this input sends a video signal."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, entry: HdmiMatrixConfigEntry, number: int) -> None:
        data = entry.runtime_data.coordinator.data
        label = port_label(number, data.input_name(number), f"Input {number}")
        super().__init__(entry, f"input_{number}_signal", "input_signal", {"input": label})
        self.number = number

    @property
    def available(self) -> bool:
        # Unavailable, not "off", when the input status could not be read (F10.3).
        return super().available and self.coordinator.data.input(self.number) is not None

    @property
    def is_on(self) -> bool | None:
        inp = self.coordinator.data.input(self.number)
        if inp is None:
            return None
        return inp.get("signalActive", inp.get("signal_active")) is True


class HdmiMatrixOutputDisplay(HdmiMatrixEntity, BinarySensorEntity):
    """On while a display is connected to this output."""

    _attr_device_class = BinarySensorDeviceClass.PLUG

    def __init__(self, entry: HdmiMatrixConfigEntry, number: int) -> None:
        data = entry.runtime_data.coordinator.data
        label = port_label(number, data.output_name(number), f"Output {number}")
        super().__init__(entry, f"output_{number}_connected", "output_display", {"output": label})
        self.number = number

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data.output(self.number) is not None

    @property
    def is_on(self) -> bool | None:
        out = self.coordinator.data.output(self.number)
        if out is None:
            return None
        # cableConnected is None when the hub has no cable status (no Telnet); then use connected.
        cable = out.get("cableConnected", out.get("cable_connected"))
        if cable is not None:
            return cable is True
        return out.get("connected") is True
