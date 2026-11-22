"""R5 Integration Lifecycle Tests.

Validates:
- Transactional startup rollback on failure and cancellation (asyncio.shielded stop).
- Reverse shutdown order (LIFO).
- Stop failure handling (collecting multiple errors into ExceptionGroup).
- Stop cancellation handling (stopping remaining integrations and propagating cancellation).
- Idempotent stop and repeated start/stop.
- HomeAssistant discovery start/stop lifecycle and degraded health under simulated failure.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hub.integrations.base import (
    HubClient,
    Integration,
    IntegrationConfig,
    IntegrationLoader,
    IntegrationRegistry,
)
from hub.integrations.homeassistant import (
    HomeAssistantDiscoveryConfig,
    HomeAssistantDiscoveryIntegration,
)


class DummyIntegration(Integration):
    name = "dummy"
    env_flag = "DUMMY_ENABLED"

    def __init__(self, config: IntegrationConfig) -> None:
        self.config = config
        self.started = False
        self.stopped = False
        self.fail_start: Exception | None = None
        self.fail_stop: Exception | None = None
        self.cancel_start: bool = False
        self.cancel_stop: bool = False

    async def start(self, hub: HubClient) -> None:
        if self.cancel_start:
            raise asyncio.CancelledError("Dummy cancelled during start")
        if self.fail_start:
            raise self.fail_start
        self.started = True

    async def stop(self) -> None:
        self.stopped = True
        if self.cancel_stop:
            raise asyncio.CancelledError("Dummy cancelled during stop")
        if self.fail_stop:
            raise self.fail_stop

    def routes(self) -> list[Any]:
        return []

    def health(self) -> dict[str, Any]:
        return {"status": "ok"}


class OrderTrackingIntegration(DummyIntegration):
    order_log: list[str] = []

    async def start(self, hub: HubClient) -> None:
        OrderTrackingIntegration.order_log.append(f"start:{self.name}")
        await super().start(hub)

    async def stop(self) -> None:
        OrderTrackingIntegration.order_log.append(f"stop:{self.name}")
        await super().stop()


class DummyHubClient(HubClient):
    pass


# ---------------------------------------------------------------------------
# Startup Rollback & Cancellation Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transactional_startup_rollback_on_failure(monkeypatch):
    """When an integration fails to start, previously started integrations are stopped in reverse order."""
    OrderTrackingIntegration.order_log = []

    class First(OrderTrackingIntegration):
        name = "first"
        env_flag = "FIRST_ENABLED"

    class Second(OrderTrackingIntegration):
        name = "second"
        env_flag = "SECOND_ENABLED"

        async def start(self, hub: HubClient) -> None:
            OrderTrackingIntegration.order_log.append(f"start:{self.name}")
            raise RuntimeError("Second integration crashed on startup")

    monkeypatch.setattr(sys.modules[__name__], "First", First, raising=False)
    monkeypatch.setattr(sys.modules[__name__], "Second", Second, raising=False)

    registry = IntegrationRegistry()
    registry.register("first", "FIRST_ENABLED", f"{__name__}:First")
    registry.register("second", "SECOND_ENABLED", f"{__name__}:Second")

    loader = IntegrationLoader(
        registry,
        {"FIRST_ENABLED": "true", "SECOND_ENABLED": "true"},
    )
    hub = DummyHubClient()

    with pytest.raises(RuntimeError, match="Second integration crashed on startup"):
        await loader.start(hub)

    # First started, Second attempted start and failed, then First and Second were rolled back via stop()
    assert OrderTrackingIntegration.order_log == [
        "start:first",
        "start:second",
        "stop:second",
        "stop:first",
    ]
    assert loader._started == []
    assert loader.integrations == {}


@pytest.mark.asyncio
async def test_transactional_startup_rollback_on_cancellation(monkeypatch):
    """When startup is cancelled, shield(self.stop()) rolls back previously started integrations."""
    OrderTrackingIntegration.order_log = []

    class IntA(OrderTrackingIntegration):
        name = "inta"
        env_flag = "INTA_ENABLED"

    class IntB(OrderTrackingIntegration):
        name = "intb"
        env_flag = "INTB_ENABLED"

        async def start(self, hub: HubClient) -> None:
            OrderTrackingIntegration.order_log.append(f"start:{self.name}")
            raise asyncio.CancelledError("Startup task was cancelled")

    monkeypatch.setattr(sys.modules[__name__], "IntA", IntA, raising=False)
    monkeypatch.setattr(sys.modules[__name__], "IntB", IntB, raising=False)

    registry = IntegrationRegistry()
    registry.register("inta", "INTA_ENABLED", f"{__name__}:IntA")
    registry.register("intb", "INTB_ENABLED", f"{__name__}:IntB")

    loader = IntegrationLoader(
        registry,
        {"INTA_ENABLED": "true", "INTB_ENABLED": "true"},
    )
    hub = DummyHubClient()

    with pytest.raises(asyncio.CancelledError, match="Startup task was cancelled"):
        await loader.start(hub)

    assert OrderTrackingIntegration.order_log == [
        "start:inta",
        "start:intb",
        "stop:intb",
        "stop:inta",
    ]
    assert loader._started == []
    assert loader.integrations == {}


# ---------------------------------------------------------------------------
# Reverse Shutdown Order & Multi-error ExceptionGroup Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reverse_shutdown_order_lifo(monkeypatch):
    """Stop executes in strictly reverse order (LIFO) of startup."""
    OrderTrackingIntegration.order_log = []

    class Int1(OrderTrackingIntegration):
        name = "int1"
        env_flag = "INT1_ENABLED"

    class Int2(OrderTrackingIntegration):
        name = "int2"
        env_flag = "INT2_ENABLED"

    class Int3(OrderTrackingIntegration):
        name = "int3"
        env_flag = "INT3_ENABLED"

    monkeypatch.setattr(sys.modules[__name__], "Int1", Int1, raising=False)
    monkeypatch.setattr(sys.modules[__name__], "Int2", Int2, raising=False)
    monkeypatch.setattr(sys.modules[__name__], "Int3", Int3, raising=False)

    registry = IntegrationRegistry()
    registry.register("int1", "INT1_ENABLED", f"{__name__}:Int1")
    registry.register("int2", "INT2_ENABLED", f"{__name__}:Int2")
    registry.register("int3", "INT3_ENABLED", f"{__name__}:Int3")

    loader = IntegrationLoader(
        registry,
        {"INT1_ENABLED": "true", "INT2_ENABLED": "true", "INT3_ENABLED": "true"},
    )
    hub = DummyHubClient()

    await loader.start(hub)
    assert OrderTrackingIntegration.order_log == ["start:int1", "start:int2", "start:int3"]

    await loader.stop()
    assert OrderTrackingIntegration.order_log == [
        "start:int1",
        "start:int2",
        "start:int3",
        "stop:int3",
        "stop:int2",
        "stop:int1",
    ]


@pytest.mark.asyncio
async def test_stop_failure_collects_exception_group(monkeypatch):
    """When multiple integrations fail during stop, all are attempted and an ExceptionGroup is raised."""
    OrderTrackingIntegration.order_log = []

    class Clean(OrderTrackingIntegration):
        name = "clean"
        env_flag = "CLEAN_ENABLED"

    class BadA(OrderTrackingIntegration):
        name = "bada"
        env_flag = "BADA_ENABLED"

        async def stop(self) -> None:
            OrderTrackingIntegration.order_log.append(f"stop:{self.name}")
            raise ValueError("BadA stop failed")

    class BadB(OrderTrackingIntegration):
        name = "badb"
        env_flag = "BADB_ENABLED"

        async def stop(self) -> None:
            OrderTrackingIntegration.order_log.append(f"stop:{self.name}")
            raise TypeError("BadB stop failed")

    monkeypatch.setattr(sys.modules[__name__], "Clean", Clean, raising=False)
    monkeypatch.setattr(sys.modules[__name__], "BadA", BadA, raising=False)
    monkeypatch.setattr(sys.modules[__name__], "BadB", BadB, raising=False)

    registry = IntegrationRegistry()
    registry.register("clean", "CLEAN_ENABLED", f"{__name__}:Clean")
    registry.register("bada", "BADA_ENABLED", f"{__name__}:BadA")
    registry.register("badb", "BADB_ENABLED", f"{__name__}:BadB")

    loader = IntegrationLoader(
        registry,
        {"CLEAN_ENABLED": "true", "BADA_ENABLED": "true", "BADB_ENABLED": "true"},
    )
    hub = DummyHubClient()
    await loader.start(hub)

    with pytest.raises(ExceptionGroup) as exc_info:
        await loader.stop()

    assert "Integration shutdown failed" in str(exc_info.value)
    # Check that both exceptions were captured
    assert len(exc_info.value.exceptions) == 2
    types = {type(e) for e in exc_info.value.exceptions}
    assert ValueError in types
    assert TypeError in types

    # And critically, Clean (started first, stopped last) WAS stopped despite earlier failures
    assert "stop:clean" in OrderTrackingIntegration.order_log


@pytest.mark.asyncio
async def test_stop_cancellation_cleans_up_all_and_propagates(monkeypatch):
    """When stop is cancelled mid-way, remaining integrations are still stopped, and CancelledError is raised."""
    OrderTrackingIntegration.order_log = []

    class First(OrderTrackingIntegration):
        name = "first"
        env_flag = "FIRST_ENABLED"

    class Second(OrderTrackingIntegration):
        name = "second"
        env_flag = "SECOND_ENABLED"

        async def stop(self) -> None:
            OrderTrackingIntegration.order_log.append(f"stop:{self.name}")
            raise asyncio.CancelledError("Stop operation was cancelled at Second")

    monkeypatch.setattr(sys.modules[__name__], "First", First, raising=False)
    monkeypatch.setattr(sys.modules[__name__], "Second", Second, raising=False)

    registry = IntegrationRegistry()
    registry.register("first", "FIRST_ENABLED", f"{__name__}:First")
    registry.register("second", "SECOND_ENABLED", f"{__name__}:Second")

    loader = IntegrationLoader(
        registry,
        {"FIRST_ENABLED": "true", "SECOND_ENABLED": "true"},
    )
    hub = DummyHubClient()
    await loader.start(hub)

    with pytest.raises(asyncio.CancelledError, match="Stop operation was cancelled"):
        await loader.stop()

    # Even though Second was cancelled, First was still stopped!
    assert OrderTrackingIntegration.order_log == [
        "start:first",
        "start:second",
        "stop:second",
        "stop:first",
    ]


# ---------------------------------------------------------------------------
# Idempotent Stop and Repeated Start/Stop
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_loader_idempotent_stop_and_repeated_start_stop(monkeypatch):
    """Calling stop repeatedly is idempotent, and loader can be reloaded and restarted cleanly."""
    OrderTrackingIntegration.order_log = []

    class Reusable(OrderTrackingIntegration):
        name = "reusable"
        env_flag = "REUSABLE_ENABLED"

    monkeypatch.setattr(sys.modules[__name__], "Reusable", Reusable, raising=False)
    registry = IntegrationRegistry()
    registry.register("reusable", "REUSABLE_ENABLED", f"{__name__}:Reusable")

    loader = IntegrationLoader(registry, {"REUSABLE_ENABLED": "true"})
    hub = DummyHubClient()

    # First cycle
    await loader.start(hub)
    assert len(loader._started) == 1
    await loader.stop()
    assert len(loader._started) == 0

    # Second stop call is idempotent no-op
    await loader.stop()

    # Second cycle: reload and start
    await loader.start(hub)
    assert len(loader._started) == 1
    await loader.stop()

    assert OrderTrackingIntegration.order_log == [
        "start:reusable",
        "stop:reusable",
        "start:reusable",
        "stop:reusable",
    ]


# ---------------------------------------------------------------------------
# Home Assistant Discovery Lifecycle and Degraded Health Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ha_discovery_start_stop_clean_lifecycle():
    """HA discovery starts, registers service with Zeroconf, and cleanly unregisters/closes on stop."""
    config = HomeAssistantDiscoveryConfig(
        enabled=True,
        api_port=8080,
        service_name="Test Matrix",
        host_ip="192.168.1.50",
    )
    mock_zc = MagicMock()
    mock_zc.async_register_service = AsyncMock()
    mock_zc.async_unregister_service = AsyncMock()
    mock_zc.async_close = AsyncMock()

    ha = HomeAssistantDiscoveryIntegration(config=config, zeroconf=mock_zc)
    hub = DummyHubClient()

    # Health before start
    assert ha.health()["status"] == "error"  # enabled but not yet registered

    await ha.start(hub)
    assert ha._registered is True
    assert ha._service_info is not None
    mock_zc.async_register_service.assert_awaited_once()

    # Health after start
    health = ha.health()
    assert health["status"] == "ok"
    assert health["enabled"] is True
    assert health["registered"] is True
    assert health["service_name"] == "Test Matrix"
    assert health["port"] == 8080
    assert "error" not in health

    # Stop unregisters service
    service_info = ha._service_info
    await ha.stop()
    mock_zc.async_unregister_service.assert_awaited_once_with(service_info)
    assert ha._registered is False
    assert ha._started is False


@pytest.mark.asyncio
async def test_ha_discovery_degraded_health_zeroconf_missing():
    """When zeroconf package is missing, HA discovery does not crash startup; reports degraded health."""
    config = HomeAssistantDiscoveryConfig(
        enabled=True,
        api_port=8080,
        service_name="Test Matrix",
    )
    ha = HomeAssistantDiscoveryIntegration(config=config)
    hub = DummyHubClient()

    with patch.dict(sys.modules, {"zeroconf": None, "zeroconf.asyncio": None}):
        await ha.start(hub)

    # Must NOT crash, must be in error status
    health = ha.health()
    assert health["status"] == "error"
    assert health["registered"] is False
    assert "zeroconf library not available" in health.get("error", "")


@pytest.mark.asyncio
async def test_ha_discovery_degraded_health_registration_failure():
    """When Zeroconf registration throws an error, discovery records failure and reports degraded health."""
    config = HomeAssistantDiscoveryConfig(
        enabled=True,
        api_port=8080,
        service_name="Test Matrix",
    )
    mock_zc = MagicMock()
    mock_zc.async_register_service = AsyncMock(side_effect=RuntimeError("mDNS port 5353 conflict"))
    mock_zc.async_unregister_service = AsyncMock()
    mock_zc.async_close = AsyncMock()

    ha = HomeAssistantDiscoveryIntegration(config=config, zeroconf=mock_zc)
    hub = DummyHubClient()

    # Start should not raise; it degrades gracefully
    await ha.start(hub)
    assert ha._registered is False

    health = ha.health()
    assert health["status"] == "error"
    assert health["registered"] is False
    assert health["error"] == "Failed to register discovery service"

    # Clean stop should still succeed
    await ha.stop()
    assert ha._started is False


@pytest.mark.asyncio
async def test_ha_repeated_start_stop():
    """Repeated start/stop cycles with owned Zeroconf do not crash or leak."""
    config = HomeAssistantDiscoveryConfig(
        enabled=True,
        api_port=8080,
        service_name="Test Matrix",
    )
    mock_zc = MagicMock()
    mock_zc.async_register_service = AsyncMock()
    mock_zc.async_unregister_service = AsyncMock()
    mock_zc.async_close = AsyncMock()

    with patch("zeroconf.asyncio.AsyncZeroconf", return_value=mock_zc):
        ha = HomeAssistantDiscoveryIntegration(config=config)
        hub = DummyHubClient()

        # Cycle 1
        await ha.start(hub)
        assert ha._registered is True
        assert ha.health()["status"] == "ok"
        await ha.stop()
        assert ha._registered is False

        # Cycle 2
        await ha.start(hub)
        assert ha._registered is True
        assert ha.health()["status"] == "ok"
        await ha.stop()
        assert ha._registered is False
