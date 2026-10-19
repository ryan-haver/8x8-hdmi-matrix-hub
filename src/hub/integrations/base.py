"""Lazy, opt-in integration discovery and lifecycle management.

Register import strings (``package.module:Class``), never imported classes, so
an integration's dependencies and module side effects stay behind its flag.
The hub owns the shared client and mounts ``loader.routes()`` before serving.
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
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


async def _await_cleanup(task: asyncio.Task[None]) -> None:
    """Join owned cleanup even after repeated cancellation of its caller."""
    cancelled: asyncio.CancelledError | None = None
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError as exc:
            cancelled = exc
        except BaseException:
            break  # Retrieve and propagate the cleanup failure below.
    try:
        task.result()
    except BaseException as exc:
        if cancelled is not None and not isinstance(exc, asyncio.CancelledError):
            raise BaseExceptionGroup("Integration shutdown failed", [exc, cancelled]) from None
        raise
    if cancelled is not None:
        raise cancelled


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
    Each cleanup has a deadline. Failed or unfinished owners prevent restart
    until a later stop retry or the pending cleanup has settled successfully.
    """

    def __init__(
        self, registry: IntegrationRegistry, environ: Mapping[str, str], *,
        cleanup_timeout: float = 5.0, cleanup_cancel_timeout: float = 1.0,
    ) -> None:
        self.registry = registry
        self.environ = dict(environ)
        self.integrations: dict[str, Integration] = {}
        self._started: list[Integration] = []
        self._cleanup_timeout = cleanup_timeout
        self._cleanup_cancel_timeout = cleanup_cancel_timeout
        self._cleanup_task: asyncio.Task[None] | None = None
        self._pending_cleanup: dict[Integration, asyncio.Task[None]] = {}
        self._failed_cleanup: dict[Integration, None] = {}
        self._cleanup_errors: dict[str, dict[str, Any]] = {}

    def load(self) -> dict[str, Integration]:
        if self._pending_cleanup or self._failed_cleanup:
            raise RuntimeError("Integration cleanup is unresolved; retry stop before loading")
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
        if self._cleanup_task is not None and not self._cleanup_task.done():
            await _await_cleanup(self._cleanup_task)
        if self._pending_cleanup:
            raise RuntimeError("Integration cleanup is still pending")
        if self._failed_cleanup:
            raise RuntimeError("Integration cleanup failed; retry stop before restart")
        if self._started:
            return
        self._cleanup_errors.clear()
        self.load()
        try:
            for integration in self.integrations.values():
                self._started.append(integration)
                await integration.start(hub)
        except BaseException as startup_error:
            try:
                await self.stop()
            except BaseException:
                startup_error.add_note("Integration rollback encountered a shutdown failure or cancellation")
            raise

    async def stop(self) -> None:
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._stop_all(), name="integration-cleanup")
        await _await_cleanup(self._cleanup_task)

    async def _stop_all(self) -> None:
        failures: list[BaseException] = []
        if self._pending_cleanup:
            await asyncio.wait(set(self._pending_cleanup.values()), timeout=self._cleanup_timeout)
            for integration, task in tuple(self._pending_cleanup.items()):
                if task.done():
                    self._cleanup_finished(integration, task)
                else:
                    failures.append(TimeoutError(f"Integration cleanup still pending: {integration.name}"))
        for integration in self._failed_cleanup:
            self._started.insert(0, integration)
        self._failed_cleanup.clear()
        while self._started:
            integration = self._started[-1]
            task = asyncio.create_task(integration.stop(), name=f"integration-stop:{integration.name}")
            self._pending_cleanup[integration] = task
            done, _ = await asyncio.wait({task}, timeout=self._cleanup_timeout)
            timed_out = not done
            if timed_out:
                task.cancel()
                await asyncio.wait({task}, timeout=self._cleanup_cancel_timeout)
                failures.append(TimeoutError(f"Integration cleanup timed out: {integration.name}"))
                self._cleanup_errors[integration.name] = {"status": "error", "error": "shutdown timed out"}
                if task.done():
                    self._failed_cleanup[integration] = None
            try:
                if task.done():
                    task.result()
            except BaseException as exc:
                self._failed_cleanup[integration] = None
                if not (timed_out and isinstance(exc, asyncio.CancelledError)):
                    failures.append(exc)
                    self._cleanup_errors[integration.name] = {"status": "error", "error": "shutdown failed"}
            finally:
                if task.done():
                    self._pending_cleanup.pop(integration, None)
                    if integration not in self._failed_cleanup:
                        self._cleanup_errors.pop(integration.name, None)
                else:
                    # A coroutine can suppress cancellation. Keep ownership and
                    # refuse restart until it exits; never spawn a replacement.
                    task.add_done_callback(partial(self._cleanup_finished, integration))
                self._started.pop()
        self.integrations.clear()
        if failures:
            if len(failures) == 1 and isinstance(failures[0], asyncio.CancelledError):
                raise failures[0]
            raise BaseExceptionGroup("Integration shutdown failed", failures)

    def _cleanup_finished(self, integration: Integration, task: asyncio.Task[None]) -> None:
        if self._pending_cleanup.get(integration) is not task:
            return
        self._pending_cleanup.pop(integration, None)
        try:
            task.result()
        except BaseException:
            self._failed_cleanup[integration] = None
            # The deadline has already been reported, but task exceptions must
            # still be retrieved when delayed cancellation finally finishes.
        else:
            self._cleanup_errors.pop(integration.name, None)

    def routes(self) -> list[Any]:
        return [route for integration in self.integrations.values() for route in integration.routes()]

    def health_summary(self) -> dict[str, dict[str, Any]]:
        result = {}
        for name, integration in self.integrations.items():
            try:
                result[name] = integration.health()
            except Exception:
                result[name] = {"status": "error"}
        result.update(self._cleanup_errors)
        for integration in self._pending_cleanup:
            result[integration.name] = {"status": "error", "error": "shutdown still pending"}
        return result


