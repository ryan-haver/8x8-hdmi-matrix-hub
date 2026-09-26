"""Preset recall buttons and the reboot button."""

from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import PRESET_COUNT
from .coordinator import HdmiMatrixConfigEntry
from .entity import HdmiMatrixEntity, call_hub, port_label

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: HdmiMatrixConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entities: list[ButtonEntity] = [HdmiMatrixPresetButton(entry, n) for n in range(1, PRESET_COUNT + 1)]
    entities.append(HdmiMatrixRebootButton(entry))
    async_add_entities(entities)


class HdmiMatrixPresetButton(HdmiMatrixEntity, ButtonEntity):
    """Recall one of the matrix's preset slots."""

    def __init__(self, entry: HdmiMatrixConfigEntry, preset: int) -> None:
        data = entry.runtime_data.coordinator.data
        label = port_label(preset, data.preset_name(preset), f"Preset {preset}")
        super().__init__(entry, f"preset_{preset}", "preset", {"preset": label})
        self.preset = preset

    async def async_press(self) -> None:
        await self._write(self.client.recall_preset(self.preset))


class HdmiMatrixRebootButton(HdmiMatrixEntity, ButtonEntity):
    """Restart the matrix."""

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry: HdmiMatrixConfigEntry) -> None:
        super().__init__(entry, "reboot", "reboot")

    async def async_press(self) -> None:
        # No refresh: the matrix is going away for a while.
        await call_hub(self.client.reboot())
