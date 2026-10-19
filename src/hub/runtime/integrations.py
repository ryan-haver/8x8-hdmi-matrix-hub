"""Lazy integration registration. Lifecycle refinements transfer to R5."""

from __future__ import annotations

import logging
from collections.abc import Mapping

from hub.integrations.base import IntegrationLoader, IntegrationRegistry


def build_integration_loader(environ: Mapping[str, str]) -> IntegrationLoader:
    effective = dict(environ)
    raw = effective.get("FLIC_ENABLED", "").strip().lower()
    if raw and raw not in {"1", "true", "yes", "on", "0", "false", "no", "off"}:
        logging.getLogger(__name__).warning("Unrecognized FLIC_ENABLED spelling; retaining enabled default")
    effective["FLIC_ENABLED"] = "false" if raw in {"0", "false", "no", "off"} else "true"
    registry = IntegrationRegistry()
    registry.register("unfolded_circle", "UC_ENABLED", "hub.integrations.unfolded_circle:UnfoldedCircleIntegration")
    registry.register("flic", "FLIC_ENABLED", "hub.integrations.flic:FlicIntegration")
    registry.register(
        "homeassistant", "HA_DISCOVERY_ENABLED", "hub.integrations.homeassistant:HomeAssistantDiscoveryIntegration"
    )
    return IntegrationLoader(registry, effective)


def bind_integrations(loader, runtime) -> None:
    uc = loader.integrations.get("unfolded_circle")
    if uc is not None:
        uc.bind_runtime(
            reconfigure=runtime.reconfigure,
            current_address=lambda: runtime.address,
            driver_metadata=runtime.driver_metadata,
        )
    flic = loader.integrations.get("flic")
    if flic is not None:
        import rest_api.integrations as _rest_int

        _rest_int._default_registry = flic.registry
        _rest_int._default_integration = flic
        _rest_int._registered_buttons = flic.registry._buttons
        _rest_int._loaded = flic.registry._loaded

