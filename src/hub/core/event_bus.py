"""In-process event bus for hub state changes.

Producers (:class:`~hub.core.MatrixService`, :class:`~hub.core.NameStore`)
publish a topic and a data dict; REST, WebSocket and the integrations
subscribe. Callbacks may be plain functions or coroutine functions. A
subscriber that raises is logged and never stops delivery to the others.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import time
from collections.abc import Awaitable, Callable, Iterable
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

_LOG = logging.getLogger(__name__)

TOPIC_ROUTING = "routing"
TOPIC_SIGNAL = "signal"
TOPIC_CABLE = "cable"
TOPIC_DISPLAY = "display"
TOPIC_POWER = "power"
TOPIC_NAMES = "names"
TOPIC_PRESETS = "presets"
TOPIC_HUB_CONNECTION = "hub_connection"

STANDARD_TOPICS: frozenset[str] = frozenset(
    {
        TOPIC_ROUTING,
        TOPIC_SIGNAL,
        TOPIC_CABLE,
        TOPIC_DISPLAY,
        TOPIC_POWER,
        TOPIC_NAMES,
        TOPIC_PRESETS,
        TOPIC_HUB_CONNECTION,
    }
)


@dataclass(frozen=True)
class HubEvent:
    """One published state change."""

    topic: str
    data: dict[str, Any]
    timestamp: float = field(default_factory=time.time)


EventCallback = Callable[[HubEvent], Awaitable[None] | None]


@dataclass(frozen=True)
class _Subscription:
    callback: EventCallback
    topics: frozenset[str] | None  # None = every topic

    def wants(self, topic: str) -> bool:
        return self.topics is None or topic in self.topics


class EventBus:
    """Fan-out of :class:`HubEvent` to sync and async subscribers.

    Sync callbacks run inside :meth:`publish`, in subscription order. An async
    callback is started as a task on the running loop; :meth:`drain` waits for
    those tasks. Without a running loop an async callback cannot run and the
    event is dropped for it (logged).
    """

    def __init__(self) -> None:
        self._subscriptions: list[_Subscription] = []
        self._tasks: set[asyncio.Task[None]] = set()

    def subscribe(self, callback: EventCallback, topics: Iterable[str] | None = None) -> Callable[[], None]:
        """Call ``callback`` for every event on ``topics`` (all topics if None).

        Returns a function that removes this subscription; calling it again
        does nothing.
        """
        if isinstance(topics, str):
            topics = (topics,)  # subscribe(cb, "routing") means one topic, not seven letters
        sub = _Subscription(callback, frozenset(topics) if topics is not None else None)
        self._subscriptions.append(sub)

        def unsubscribe() -> None:
            try:
                self._subscriptions.remove(sub)
            except ValueError:
                pass

        return unsubscribe

    @property
    def subscriber_count(self) -> int:
        return len(self._subscriptions)

    def publish(self, topic: str, data: dict[str, Any]) -> None:
        """Deliver ``data`` on ``topic`` to every matching subscriber."""
        event = HubEvent(topic=topic, data=deepcopy(data))
        # A callback may (un)subscribe while we deliver: iterate over a copy.
        for sub in list(self._subscriptions):
            if sub.wants(topic):
                self._deliver(sub.callback, HubEvent(event.topic, deepcopy(event.data), event.timestamp))

    def _deliver(self, callback: EventCallback, event: HubEvent) -> None:
        try:
            result = callback(event)
        except Exception:
            _LOG.exception("Event subscriber %r failed on %r", callback, event.topic)
            return
        if not inspect.isawaitable(result):
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            _LOG.error("Async subscriber %r needs a running event loop; %r dropped", callback, event.topic)
            if inspect.iscoroutine(result):
                result.close()  # no "never awaited" warning
            return
        task: asyncio.Task[None] = loop.create_task(self._run_async(callback, event, result))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    @staticmethod
    async def _run_async(callback: EventCallback, event: HubEvent, awaitable: Awaitable[None]) -> None:
        try:
            await awaitable
        except Exception:
            _LOG.exception("Async event subscriber %r failed on %r", callback, event.topic)

    async def drain(self, timeout: float | None = None) -> None:
        """Wait until every async delivery started so far has finished."""
        async def finish():
            while self._tasks:
                await asyncio.gather(*list(self._tasks), return_exceptions=True)

        if timeout is None:
            await finish()
            return
        deadline = asyncio.get_running_loop().time() + timeout
        while self._tasks:
            remaining = max(0.0, deadline - asyncio.get_running_loop().time())
            _, pending = await asyncio.wait(set(self._tasks), timeout=remaining)
            if pending:
                for task in pending:
                    task.cancel()
                # Give cooperative cancellations their cleanup turn without
                # letting a subscriber extend the shutdown deadline.
                await asyncio.sleep(0)
                return
