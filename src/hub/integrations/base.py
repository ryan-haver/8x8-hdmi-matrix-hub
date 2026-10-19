"""Lazy, opt-in integration discovery and lifecycle management.

Register import strings (``package.module:Class``), never imported classes, so
an integration's dependencies and module side effects stay behind its flag.
The hub owns the shared client and mounts ``loader.routes()`` before serving.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from .hub_client import HubClient


@dataclass(frozen=True)
class IntegrationConfig:
    """Default configuration for integrations with no additional settings."""

    enabled: bool = False


class Integration(ABC):
    name: str
    env_flag: str

    @classmethod
    def config_from_env(cls, environ: Mapping[str, str]) -> Any:
        return IntegrationConfig(enabled=_enabled(environ.get(cls.env_flag, "")))

    @abstractmethod
    async def start(self, hub: HubClient) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    def health(self) -> dict[str, Any]: ...

    def routes(self) -> list[Any]:
        return []


def _enabled(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class _Registration:
    name: str
    env_flag: str
    import_path: str


class IntegrationRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, _Registration] = {}

    def register(self, name: str, env_flag: str, import_path: str) -> None:
        """Declare an integration without importing it. Factories accept config."""
        if name in self._entries:
            raise ValueError(f"Integration already registered: {name}")
        if not name or not env_flag or ":" not in import_path:
            raise ValueError("Expected name, env_flag and module:Class import path")
        self._entries[name] = _Registration(name, env_flag, import_path)

    def enabled(self, environ: Mapping[str, str]) -> list[_Registration]:
        return [entry for entry in self._entries.values() if _enabled(environ.get(entry.env_flag, ""))]


class IntegrationLoader:
    """Load once, start in registration order and stop in reverse order.

    Startup is transactional: a partial start is stopped, as are earlier
    integrations. Stop attempts every integration even when one stop fails.
    A stopped loader can be loaded and started again.
    """

    def __init__(self, registry: IntegrationRegistry, environ: Mapping[str, str]) -> None:
        self.registry = registry
        self.environ = dict(environ)
        self.integrations: dict[str, Integration] = {}
        self._started: list[Integration] = []

    def load(self) -> dict[str, Integration]:
        if self.integrations:
            return dict(self.integrations)
        loaded: dict[str, Integration] = {}
        for entry in self.registry.enabled(self.environ):
            module, attribute = entry.import_path.split(":", 1)
            cls = getattr(import_module(module), attribute)
            if cls.name != entry.name or cls.env_flag != entry.env_flag:
                raise ValueError(f"Integration registration mismatch: {entry.name}")
            loaded[entry.name] = cls(cls.config_from_env(self.environ))
        self.integrations = loaded
        return dict(loaded)

    async def start(self, hub: HubClient) -> None:
        if self._started:
            return
        self.load()
        try:
            for integration in self.integrations.values():
                self._started.append(integration)
                await integration.start(hub)
        except BaseException:
            try:
                import asyncio
                await asyncio.shield(self.stop())
            except Exception:
                pass  # Preserve the startup error after attempting all cleanup.
            raise

    async def stop(self) -> None:
        import asyncio
        failures: list[Exception] = []
        cancelled: asyncio.CancelledError | None = None
        while self._started:
            integration = self._started.pop()
            try:
                await integration.stop()
            except asyncio.CancelledError as exc:
                cancelled = exc
            except Exception as exc:
                failures.append(exc)
        self.integrations.clear()
        if failures:
            if cancelled is not None:
                raise BaseExceptionGroup("Integration shutdown failed", [*failures, cancelled])
            raise ExceptionGroup("Integration shutdown failed", failures)
        if cancelled is not None:
            raise cancelled

    def routes(self) -> list[Any]:
        return [route for integration in self.integrations.values() for route in integration.routes()]

    def health_summary(self) -> dict[str, dict[str, Any]]:
        result = {}
        for name, integration in self.integrations.items():
            try:
                result[name] = integration.health()
            except Exception:
                result[name] = {"status": "error"}
        return result


