# Developer Guide & Template: Building Modular Hub Integrations

This guide explains how to develop, test, and register new modular integrations for the 8x8 HDMI Matrix Hub.

---

## 1. Architectural Principles

Modular integrations allow the hub to interface with external ecosystems (e.g., MQTT, Home Assistant Zeroconf discovery, Flic smart buttons, webhook forwarders, automation schedulers) without coupling the core matrix switching logic to external protocol libraries.

Every modular integration follows these core invariants:

1. **Opt-in by Default**:
   - Each integration is governed by a dedicated environment variable (e.g. `MQTT_ENABLED`, `HA_DISCOVERY_ENABLED`).
   - When disabled, external modules and network dependencies are **never imported or initiated**.
   - Note on existing routes: legacy routes that were previously built into the REST API (such as `FLIC_ENABLED`) default to `True` for backward compatibility, while supporting explicit opt-out (`FLIC_ENABLED=false`).
2. **Transport-Independent Client**:
   - Integrations receive an instance of `HubClient` upon `start(hub_client)`.
   - The integration interacts with the matrix exclusively through the `HubClient` async interface (`snapshot()`, `switch()`, `recall_preset()`, `power()`, `send_cec()`, `subscribe()`), whether the hub client is in-process (`HubClientLocal`) or remote (`HubClientHttp`).
3. **Structured Lifecycle & State Management**:
   - `start(hub_client)`: Setup resources, connect to external brokers, subscribe to events, load persistent caches.
   - `stop()`: Cleanly unregister services, unsubscribe from event listeners, cancel asyncio tasks, and release connections.
   - `health()`: Provide real-time diagnostics exposed via `/api/health`.
   - `routes()`: (Optional) Expose custom aiohttp HTTP endpoints mounted when the integration is active.

---

## 2. Integration Interface Contract

Integrations inherit from `hub.integrations.base.Integration` (or implement the equivalent duck-typed protocol):

```python
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from hub.integrations.hub_client import HubClient


@dataclass(frozen=True)
class ExampleConfig:
    enabled: bool = False
    # Additional configuration fields...


class Integration(ABC):
    """Abstract base class for all hub integrations."""

    name: str
    env_flag: str

    @classmethod
    @abstractmethod
    def config_from_env(cls, environ: Mapping[str, str]) -> Any:
        """Parse configuration from an environment variable mapping."""
        ...

    @abstractmethod
    async def start(self, hub: HubClient) -> None:
        """Initialize the integration, connect to services, and subscribe to events."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Tear down all resources, cancel background tasks, and unregister services."""
        ...

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """Return diagnostic health status."""
        ...

    def routes(self) -> list[tuple[str, str, Callable]]:
        """Return optional list of (HTTP_METHOD, PATH, HANDLER_CALLABLE)."""
        return []
```

---

## 3. Production Copy-Paste Skeleton

Save this template under `src/hub/integrations/<integration_name>/__init__.py`:

```python
"""<Integration Name> integration for the 8x8 HDMI Matrix Hub."""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from aiohttp import web

_LOG = logging.getLogger(__name__)

# Base class fallback if integration framework base is not yet merged
try:
    from hub.integrations.base import Integration
except ImportError:
    try:
        from src.hub.integrations.base import Integration  # type: ignore[no-redef]
    except ImportError:
        class Integration:  # type: ignore[no-redef]
            """Fallback base class when integration framework base is not present."""

            name: str
            env_flag: str

            def routes(self) -> list[Any]:
                return []


def _parse_bool(value: str | None, default: bool = False) -> bool:
    """Helper to parse boolean environment variable flags."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class CustomIntegrationConfig:
    """Immutable configuration for the integration."""

    enabled: bool = False
    endpoint_url: str = ""
    retry_interval_seconds: float = 5.0

    @classmethod
    def config_from_env(
        cls, environ: Mapping[str, str] | None = None
    ) -> CustomIntegrationConfig:
        """Parse configuration from environment mapping."""
        if environ is None:
            environ = os.environ

        enabled = _parse_bool(environ.get("CUSTOM_INTEGRATION_ENABLED"), default=False)
        endpoint_url = environ.get("CUSTOM_INTEGRATION_URL", "").strip()

        raw_interval = environ.get("CUSTOM_INTEGRATION_RETRY_INTERVAL", "5.0")
        try:
            retry_interval = float(raw_interval)
        except ValueError:
            retry_interval = 5.0

        return cls(
            enabled=enabled,
            endpoint_url=endpoint_url,
            retry_interval_seconds=retry_interval,
        )


class CustomIntegration(Integration):
    """Custom modular integration implementation."""

    name: str = "custom"
    env_flag: str = "CUSTOM_INTEGRATION_ENABLED"

    def __init__(self, config: CustomIntegrationConfig | None = None) -> None:
        self.config = config or self.config_from_env({})
        self.hub_client: Any = None
        self._unsubscribe: Callable[[], None] | None = None
        self._background_tasks: set[asyncio.Task[Any]] = set()
        self._connected: bool = False
        self._started: bool = False

    @classmethod
    def config_from_env(cls, environ: Mapping[str, str]) -> CustomIntegrationConfig:
        return CustomIntegrationConfig.config_from_env(environ)

    async def start(self, hub_client: Any) -> None:
        """Start the integration and subscribe to matrix state changes."""
        self.hub_client = hub_client
        self._started = True

        if not self.config.enabled:
            _LOG.info("%s integration is disabled", self.name)
            return

        _LOG.info("Starting %s integration with endpoint %s", self.name, self.config.endpoint_url)

        # 1. Subscribe to HubClient events
        if hasattr(self.hub_client, "subscribe"):
            self._unsubscribe = self.hub_client.subscribe(self._on_hub_event)

        # 2. Spawn any required background worker tasks
        worker_task = asyncio.create_task(self._worker_loop())
        self._background_tasks.add(worker_task)
        worker_task.add_done_callback(self._background_tasks.discard)

        self._connected = True

    async def stop(self) -> None:
        """Stop background tasks, unsubscribe from events, and release resources."""
        # 1. Unsubscribe from HubClient events
        if self._unsubscribe is not None:
            try:
                self._unsubscribe()
            except Exception as e:
                _LOG.warning("Error unsubscribing from hub events: %s", e)
            finally:
                self._unsubscribe = None

        # 2. Cancel and await all background tasks
        for task in list(self._background_tasks):
            task.cancel()
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            self._background_tasks.clear()

        self._connected = False
        self._started = False
        self.hub_client = None
        _LOG.info("%s integration stopped", self.name)

    def health(self) -> dict[str, Any]:
        """Report integration health status."""
        return {
            "status": "ok" if (self._connected or not self.config.enabled) else "error",
            "enabled": self.config.enabled,
            "connected": self._connected,
            "tasks_running": len(self._background_tasks),
        }

    def _on_hub_event(self, event: Any) -> None:
        """Handle incoming event from HubClient."""
        _LOG.debug("Received hub event: %s -> %s", getattr(event, "kind", "unknown"), getattr(event, "data", {}))
        # Forward event to external service or queue

    async def _worker_loop(self) -> None:
        """Background worker loop (e.g. heartbeat, queue polling)."""
        while True:
            try:
                await asyncio.sleep(self.config.retry_interval_seconds)
                # Periodic processing logic
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOG.warning("Unhandled error in %s worker loop: %s", self.name, e)

    # Optional HTTP Routes
    async def handle_status_endpoint(self, request: web.Request) -> web.Response:
        """Handle GET /api/integrations/custom/status."""
        return web.json_response({
            "success": True,
            "health": self.health(),
        })

    def routes(self) -> list[tuple[str, str, Callable]]:
        """Return HTTP routes to register on the web router."""
        return [
            ("GET", "/api/integrations/custom/status", self.handle_status_endpoint),
        ]
```

---

## 4. Registration and Discovery

Integrations are registered with the central `IntegrationRegistry` in `src/hub/integrations/__init__.py` using import strings (`"package.module:Class"`), keeping imports strictly lazy:

```python
from hub.integrations.base import IntegrationRegistry

registry = IntegrationRegistry()

# Register integrations lazily
registry.register(
    name="flic",
    env_flag="FLIC_ENABLED",
    import_path="hub.integrations.flic:FlicIntegration",
)
registry.register(
    name="homeassistant",
    env_flag="HA_DISCOVERY_ENABLED",
    import_path="hub.integrations.homeassistant:HomeAssistantDiscoveryIntegration",
)
registry.register(
    name="custom",
    env_flag="CUSTOM_INTEGRATION_ENABLED",
    import_path="hub.integrations.custom:CustomIntegration",
)
```

---

## 5. Testing Requirements

Every integration must include comprehensive unit and route tests:

1. **Configuration Tests**:
   - Verify defaults when environment variables are unset.
   - Verify boolean parsing (`1`, `true`, `yes`, `on` vs `0`, `false`, `no`, `off`).
   - Verify type coercions and fallback defaults on malformed input.
2. **Lifecycle Tests**:
   - Verify `start()` is a no-op when `enabled=False`.
   - Verify `start()` initializes resources and event listeners when `enabled=True`.
   - Verify `stop()` cleanly cleans up tasks, handles cancellation, and closes sessions.
3. **Health Tests**:
   - Verify `health()` output under normal operation, disabled state, and error states.
4. **Route Tests**:
   - Test route status codes (200, 400, 500) and response formats using `aiohttp.test_utils`.
