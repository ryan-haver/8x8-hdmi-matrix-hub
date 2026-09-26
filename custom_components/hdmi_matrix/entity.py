"""Base entity: one device per config entry, names from translations (HA-10)."""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo, format_mac
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import HubConnectionError, HubError, HubResponseError
from .const import DEFAULT_MODEL, DEFAULT_NAME, DOMAIN, MANUFACTURER
from .coordinator import HdmiMatrixConfigEntry, HdmiMatrixCoordinator


def device_info(entry: HdmiMatrixConfigEntry) -> DeviceInfo:
    """The matrix behind the hub, shared by every entity of the entry."""
    runtime = entry.runtime_data
    device = runtime.device
    info = DeviceInfo(
        identifiers={(DOMAIN, entry_key(entry))},
        name=DEFAULT_NAME,
        manufacturer=MANUFACTURER,
        model=device.get("model") or DEFAULT_MODEL,
        configuration_url=runtime.client.base_url,
    )
    if device.get("firmware_version"):
        info["sw_version"] = str(device["firmware_version"])
    if device.get("mac_address"):
        info["connections"] = {(CONNECTION_NETWORK_MAC, format_mac(str(device["mac_address"])))}
    return info


def entry_key(entry: HdmiMatrixConfigEntry) -> str:
    """Prefix of every unique_id and the device identifier: the entry's unique_id (the MAC, HA-11)."""
    return entry.unique_id or entry.entry_id


def port_label(number: int, name: str, default: str) -> str:
    """``"1 (TV)"`` for a named port, ``"3"`` when the hub has its default name."""
    return f"{number} ({name})" if name and name != default else str(number)


async def call_hub(coro: Any) -> None:
    """Run a hub write; turn its failure into an error Home Assistant shows the user."""
    try:
        await coro
    except HubConnectionError as err:
        raise HomeAssistantError(
            translation_domain=DOMAIN, translation_key="cannot_connect", translation_placeholders={"error": str(err)}
        ) from err
    except HubResponseError as err:
        raise HomeAssistantError(
            translation_domain=DOMAIN, translation_key="hub_error", translation_placeholders={"error": err.error}
        ) from err
    except HubError as err:  # pragma: no cover - every HubError is one of the two above
        raise HomeAssistantError(str(err)) from err


class HdmiMatrixEntity(CoordinatorEntity[HdmiMatrixCoordinator]):
    """Common base: ``has_entity_name``, translation-keyed names, shared DeviceInfo."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: HdmiMatrixConfigEntry,
        key: str,
        translation_key: str,
        placeholders: dict[str, str] | None = None,
    ) -> None:
        super().__init__(entry.runtime_data.coordinator)
        self.entry = entry
        self.client = entry.runtime_data.client
        self._attr_unique_id = f"{entry_key(entry)}_{key}"
        self._attr_translation_key = translation_key
        if placeholders:
            self._attr_translation_placeholders = placeholders
        self._attr_device_info = device_info(entry)

    async def _write(self, coro: Any) -> None:
        """Send a write to the hub, then refresh so the new state shows at once."""
        await call_hub(coro)
        await self.coordinator.async_request_refresh()
