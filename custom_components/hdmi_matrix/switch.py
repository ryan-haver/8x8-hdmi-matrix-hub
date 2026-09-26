"""Matrix power, and per-output audio mute and stream switches."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import PORT_COUNT
from .coordinator import HdmiMatrixConfigEntry
from .entity import HdmiMatrixEntity, port_label

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: HdmiMatrixConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entities: list[SwitchEntity] = [HdmiMatrixPowerSwitch(entry)]
    for n in range(1, PORT_COUNT + 1):
        entities.append(HdmiMatrixOutputMuteSwitch(entry, n))
        entities.append(HdmiMatrixOutputStreamSwitch(entry, n))
    async_add_entities(entities)


class HdmiMatrixPowerSwitch(HdmiMatrixEntity, SwitchEntity):
    """Matrix power (on / standby), read from ``/api/status`` ``power`` (HA-03)."""

    def __init__(self, entry: HdmiMatrixConfigEntry) -> None:
        super().__init__(entry, "power", "power")

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data.power is not None

    @property
    def is_on(self) -> bool | None:
        power = self.coordinator.data.power
        return None if power is None else power == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._write(self.client.set_power(True))

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._write(self.client.set_power(False))


class _OutputSwitch(HdmiMatrixEntity, SwitchEntity):
    """A switch backed by one field of ``/api/status/outputs``."""

    field: str
    suffix: str

    def __init__(self, entry: HdmiMatrixConfigEntry, output: int) -> None:
        data = entry.runtime_data.coordinator.data
        label = port_label(output, data.output_name(output), f"Output {output}")
        super().__init__(entry, f"output_{output}_{self.suffix}", f"output_{self.suffix}", {"output": label})
        self.output = output

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data.output(self.output) is not None

    @property
    def is_on(self) -> bool | None:
        out = self.coordinator.data.output(self.output)
        return None if out is None else out.get(self.field) is True


class HdmiMatrixOutputMuteSwitch(_OutputSwitch):
    """Audio mute of one output (on = muted)."""

    field = "muted"
    suffix = "mute"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._write(self.client.set_mute(self.output, True))

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._write(self.client.set_mute(self.output, False))


class HdmiMatrixOutputStreamSwitch(_OutputSwitch):
    """Video stream of one output (off = the output is disabled)."""

    field = "enabled"
    suffix = "stream"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._write(self.client.set_stream(self.output, True))

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._write(self.client.set_stream(self.output, False))
