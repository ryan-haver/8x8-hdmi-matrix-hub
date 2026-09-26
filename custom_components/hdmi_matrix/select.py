"""Output source selects: which input each output shows."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER, PORT_COUNT
from .coordinator import HdmiMatrixConfigEntry
from .entity import HdmiMatrixEntity, port_label

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: HdmiMatrixConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(HdmiMatrixOutputSource(entry, n) for n in range(1, PORT_COUNT + 1))


class HdmiMatrixOutputSource(HdmiMatrixEntity, SelectEntity):
    """The source of one output; the options are the hub's input names."""

    def __init__(self, entry: HdmiMatrixConfigEntry, output: int) -> None:
        data = entry.runtime_data.coordinator.data
        label = port_label(output, data.output_name(output), f"Output {output}")
        super().__init__(entry, f"output_{output}_source", "output_source", {"output": label})
        self.output = output

    @property
    def options(self) -> list[str]:
        data = self.coordinator.data
        return [data.input_name(n) for n in range(1, PORT_COUNT + 1)]

    @property
    def current_option(self) -> str | None:
        input_num = self.coordinator.data.routed_input(self.output)
        if input_num is None or not 1 <= input_num <= PORT_COUNT:
            return None
        return self.coordinator.data.input_name(input_num)

    async def async_select_option(self, option: str) -> None:
        data = self.coordinator.data
        matches = [n for n in range(1, PORT_COUNT + 1) if data.input_name(n) == option]
        if not matches:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="unknown_source", translation_placeholders={"source": option}
            )
        # Two inputs with the same name: keep the one already routed here (F10.4), else the first.
        current = data.routed_input(self.output)
        input_num = current if current in matches else matches[0]
        if len(matches) > 1 and current not in matches:
            LOGGER.warning("Inputs %s are all named %r; routing input %s", matches, option, input_num)
        await self._write(self.client.route(self.output, input_num))
