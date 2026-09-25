"""Lightweight runtime health metrics for ``/api/health``.

A background task measures event-loop lag (how late ``asyncio.sleep`` wakes
up); HIL-C/HIL-D use it to prove the loop never stalls. The task is started
with the aiohttp app and cancelled on cleanup.
"""

import asyncio
import contextlib
import time
from collections import deque
from collections.abc import AsyncIterator
from typing import Any

from aiohttp import web


class LoopLagMonitor:
    """Samples asyncio sleep drift every ``interval`` seconds."""

    def __init__(self, interval: float = 1.0, window: int = 60) -> None:
        self.interval = interval
        self.started_at = time.monotonic()
        self._samples: deque[float] = deque(maxlen=window)
        self._task: asyncio.Task | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self) -> None:
        if not self.running:
            self._task = asyncio.get_running_loop().create_task(self._run(), name="loop-lag-monitor")

    async def stop(self) -> None:
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            before = loop.time()
            await asyncio.sleep(self.interval)
            lag = loop.time() - before - self.interval
            self._samples.append(max(0.0, lag) * 1000.0)

    def snapshot(self) -> dict[str, Any]:
        last = self._samples[-1] if self._samples else None
        peak = max(self._samples) if self._samples else None
        return {
            "uptime_s": round(time.monotonic() - self.started_at, 1),
            "loop_lag_ms": None if last is None else round(last, 2),
            "loop_lag_max_ms": None if peak is None else round(peak, 2),
            "task_count": len(asyncio.all_tasks()),
        }


RUNTIME_MONITOR_KEY = web.AppKey("runtime_monitor", LoopLagMonitor)


def install_runtime_monitor(app: web.Application, interval: float = 1.0) -> LoopLagMonitor:
    """Attach a :class:`LoopLagMonitor` that runs for the app's lifetime."""
    monitor = LoopLagMonitor(interval=interval)
    app[RUNTIME_MONITOR_KEY] = monitor

    async def _ctx(app: web.Application) -> AsyncIterator[None]:
        monitor.start()
        yield
        await monitor.stop()

    app.cleanup_ctx.append(_ctx)
    return monitor


def runtime_snapshot(app: web.Application) -> dict[str, Any]:
    monitor = app.get(RUNTIME_MONITOR_KEY)
    if monitor is None:
        return {"uptime_s": None, "loop_lag_ms": None, "loop_lag_max_ms": None, "task_count": len(asyncio.all_tasks())}
    return monitor.snapshot()
