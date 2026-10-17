"""Modular Unfolded Circle Remote 3 integration package (Phase 4 / WP-C3)."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from .config import UCIntegrationConfig, config_from_env
from .entities import (
    CEC_COMMAND_ALIASES,
    INPUT_CEC_SIMPLE_COMMANDS,
    OUTPUT_CEC_SIMPLE_COMMANDS,
    STANDARD_CEC_COMMANDS,
    SURVIVING_GOLDEN_ENTITY_IDS,
    build_entities,
)
from .handlers import UCCommandDispatcher
from .mdns import UC_MDNS_SERVICE_TYPE, UCMdnsPublisher
from .migration import migrate_legacy_config_state
from .state import EntityStateProjector

_LOG = logging.getLogger("uc.integration")

__all__ = [
    "CEC_COMMAND_ALIASES",
    "EntityStateProjector",
    "INPUT_CEC_SIMPLE_COMMANDS",
    "OUTPUT_CEC_SIMPLE_COMMANDS",
    "STANDARD_CEC_COMMANDS",
    "SURVIVING_GOLDEN_ENTITY_IDS",
    "UCCommandDispatcher",
    "UCIntegrationConfig",
    "UCMdnsPublisher",
    "UC_MDNS_SERVICE_TYPE",
    "UnfoldedCircleIntegration",
    "build_entities",
    "config_from_env",
    "migrate_legacy_config_state",
]


class UnfoldedCircleIntegration:
    """Modular Unfolded Circle Remote 3 integration driven by ``HubClient``."""

    name: str = "unfolded_circle"
    env_flag: str = "UC_ENABLED"
    config_from_env = staticmethod(config_from_env)

    def __init__(
        self,
        config: UCIntegrationConfig | None = None,
        *,
        mdns_publisher: UCMdnsPublisher | None = None,
        include_select: bool = True,
        include_legacy_sensors: bool = False,
    ) -> None:
        self.config: UCIntegrationConfig = config if config is not None else config_from_env()
        self.projector: EntityStateProjector = EntityStateProjector(
            include_select=include_select,
            include_legacy_sensors=include_legacy_sensors,
        )
        self.mdns: UCMdnsPublisher = (
            mdns_publisher if mdns_publisher is not None else UCMdnsPublisher(self.config)
        )
        self.hub_client: Any = None
        self.dispatcher: UCCommandDispatcher | None = None
        self.entities: list[dict[str, Any]] = []
        self.migrated_config: dict[str, Any] | None = None
        self._running: bool = False
        self._unsubscribe: Callable[[], Any] | None = None
        self.pushed_updates: list[dict[str, dict[str, Any]]] = []

    @property
    def running(self) -> bool:
        return self._running

    @property
    def standby(self) -> bool:
        return self.projector.standby

    async def start(self, hub_client: Any) -> None:
        """Start the integration against ``hub_client``: migrate legacy state, project snapshot, subscribe, and publish mDNS."""
        self.migrated_config = migrate_legacy_config_state(self.config.config_home)
        self.hub_client = hub_client
        self.dispatcher = UCCommandDispatcher(hub_client, self.projector)

        snapshot = await self._fetch_snapshot()
        self.dispatcher.update_pin_blocks(snapshot)
        self.entities = build_entities(
            snapshot,
            include_select=self.projector.include_select,
            include_legacy_sensors=self.projector.include_legacy_sensors,
        )
        for desc in self.entities:
            eid = desc["entity_id"]
            self.projector.available_entities[eid] = dict(desc)
            self.projector.configured_entities[eid] = dict(desc)
            self.projector.entity_names[eid] = dict(desc["name"])

        initial_diff = self.projector.project_snapshot(snapshot, force=True)
        if initial_diff:
            self.pushed_updates.append(initial_diff)

        if hasattr(hub_client, "subscribe"):
            sub_res = hub_client.subscribe(self._on_hub_event)
            if asyncio.iscoroutine(sub_res):
                sub_res = await sub_res
            if callable(sub_res):
                self._unsubscribe = sub_res

        await self.mdns.start()
        self._running = True
        _LOG.info("UnfoldedCircleIntegration started (%d entities)", len(self.entities))

    async def stop(self) -> None:
        """Stop the integration, unsubscribe from hub events, and unregister mDNS (`UC-11`)."""
        unsub, self._unsubscribe = self._unsubscribe, None
        if unsub is not None:
            res = unsub()
            if asyncio.iscoroutine(res):
                await res

        await self.mdns.stop()
        self._running = False
        _LOG.info("UnfoldedCircleIntegration stopped")

    async def on_enter_standby(self) -> None:
        """Pause entity/device pushes while the Remote sleeps without disconnecting the matrix (`UC-06`, `UC-17`)."""
        self.projector.enter_standby()

    async def on_exit_standby(self) -> dict[str, dict[str, Any]]:
        """Resume pushes on wake and resync state from the hub (`UC-06`, `UC-17`)."""
        flushed = self.projector.exit_standby()
        if self.hub_client is not None:
            snapshot = await self._fetch_snapshot()
            if snapshot:
                extra = self.projector.project_snapshot(snapshot)
                for eid, attrs in extra.items():
                    flushed.setdefault(eid, {}).update(attrs)
        if flushed:
            self.pushed_updates.append(flushed)
        return flushed

    def health(self) -> dict[str, Any]:
        """Return structured health information for `/api/health`."""
        if not self._running:
            status = "stopped"
        elif self.projector.connected:
            status = "ok"
        else:
            status = "degraded"

        return {
            "name": self.name,
            "enabled": self.config.enabled,
            "running": self._running,
            "status": status,
            "connected": self.projector.connected,
            "device_state": self.projector.device_state,
            "standby": self.projector.standby,
            "entity_count": len(self.entities),
            "port": self.config.port,
            "mdns_published": self.mdns.published,
        }

    async def _fetch_snapshot(self) -> dict[str, Any]:
        if self.hub_client is None or not hasattr(self.hub_client, "snapshot"):
            return {}
        res = self.hub_client.snapshot()
        data = await res if asyncio.iscoroutine(res) else res
        return data if isinstance(data, dict) else {}

    def _on_hub_event(self, event: str | dict[str, Any], data: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
        diff = self.projector.apply_event(event, data)
        if diff:
            self.pushed_updates.append(diff)
        return diff
