"""Polls the hub's REST API for the matrix state."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HubClient, HubError
from .const import CONF_SCAN_INTERVAL, DOMAIN, LOGGER, PORT_COUNT, PRESET_COUNT, scan_interval


@dataclass
class MatrixData:
    """One poll of the hub.

    ``status`` is ``/api/status`` (routing ``{"1": 2, ...}``, names, ``power``).
    ``outputs``/``inputs`` are ``None`` when their endpoint failed in this poll,
    so the entities that depend on them report unavailable instead of "off".
    """

    status: dict[str, Any]
    outputs: list[dict[str, Any]] | None = None
    inputs: list[dict[str, Any]] | None = None
    errors: dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------ helpers

    @staticmethod
    def _name(names: Any, number: int) -> str | None:
        if not isinstance(names, dict):
            return None
        value = names.get(str(number), names.get(number))  # JSON keys are strings
        return str(value) if value else None

    def input_name(self, number: int) -> str:
        return self._name(self.status.get("input_names"), number) or f"Input {number}"

    def output_name(self, number: int) -> str:
        return self._name(self.status.get("output_names"), number) or f"Output {number}"

    def preset_name(self, number: int) -> str:
        return self._name(self.status.get("preset_names"), number) or f"Preset {number}"

    def routed_input(self, output: int) -> int | None:
        """The input routed to ``output`` (``/api/status`` ``routing`` is a mapping, HA-02)."""
        routing = self.status.get("routing")
        value: Any = None
        if isinstance(routing, dict):
            value = routing.get(str(output), routing.get(output))
        elif isinstance(routing, list) and 0 < output <= len(routing):  # older hubs: a list
            value = routing[output - 1]
        return value if isinstance(value, int) and not isinstance(value, bool) else None

    def output(self, number: int) -> dict[str, Any] | None:
        for out in self.outputs or ():
            if out.get("number") == number:
                return out
        return None

    def input(self, number: int) -> dict[str, Any] | None:
        for inp in self.inputs or ():
            if inp.get("number") == number:
                return inp
        return None

    @property
    def power(self) -> str | None:
        power = self.status.get("power")
        return power if power in ("on", "off") else None

    def names(self) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
        """Every hub-side name, to notice renames (entity names include them)."""
        return (
            tuple(self.input_name(n) for n in range(1, PORT_COUNT + 1)),
            tuple(self.output_name(n) for n in range(1, PORT_COUNT + 1)),
            tuple(self.preset_name(n) for n in range(1, PRESET_COUNT + 1)),
        )


class HdmiMatrixCoordinator(DataUpdateCoordinator[MatrixData]):
    """Fetches ``/api/status``, ``/api/status/outputs`` and ``/api/status/inputs`` together."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: HubClient) -> None:
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=scan_interval(entry.options.get(CONF_SCAN_INTERVAL)),
        )
        self.client = client

    async def _async_update_data(self) -> MatrixData:
        # DataUpdateCoordinator never runs two refreshes at once, so no extra lock (HA-09).
        status, outputs, inputs = await asyncio.gather(
            self.client.status(), self.client.outputs(), self.client.inputs(), return_exceptions=True
        )
        if isinstance(status, BaseException):
            if isinstance(status, HubError):
                raise UpdateFailed(f"Error communicating with the hub: {status}") from status
            raise status
        data = MatrixData(status=status)
        for key, result in (("outputs", outputs), ("inputs", inputs)):
            if isinstance(result, HubError):
                LOGGER.warning("Could not read %s from the hub: %s", key, result)
                data.errors[key] = str(result)
            elif isinstance(result, BaseException):
                raise result
            else:
                setattr(data, key, result)
        return data


@dataclass
class HdmiMatrixRuntimeData:
    """What a loaded entry keeps in ``entry.runtime_data`` (HA-07)."""

    client: HubClient
    coordinator: HdmiMatrixCoordinator
    #: ``/api/status/device`` at setup (model, firmware_version, mac_address); empty if unavailable.
    device: dict[str, Any] = field(default_factory=dict)


HdmiMatrixConfigEntry = ConfigEntry[HdmiMatrixRuntimeData]
