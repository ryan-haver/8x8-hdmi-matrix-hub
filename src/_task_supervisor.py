"""
Background Task Supervisor.

Wraps long-lived asyncio tasks so that a single unhandled exception cannot
permanently kill a critical background loop (push listener, reconnect loop,
status polling).

Rules (BE-01):

* A coroutine that **returns** has finished its job: supervision ends and the
  task completes. It is never restarted (restarting a returning coroutine
  with no delay used to spin the event loop at 100% CPU).
* A coroutine that **raises** is restarted after a delay that doubles on each
  consecutive crash (``INITIAL_RESTART_DELAY`` up to ``MAX_RESTART_DELAY``).
  The delay resets once a run survives longer than ``MAX_RESTART_DELAY``.
* ``asyncio.CancelledError`` always propagates, so ``task.cancel()`` stops
  the supervised task (and the loop inside it) promptly.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

_LOG = logging.getLogger(__name__)

#: First restart delay after a crash (seconds).
INITIAL_RESTART_DELAY = 1.0
#: Upper bound for the exponential restart delay (seconds).
MAX_RESTART_DELAY = 30.0


async def _supervised_loop(
    coro_fn: Callable[[], Awaitable[Any]],
    name: str,
    on_error: Callable[[BaseException], Any] | None = None,
) -> None:
    """
    Run ``coro_fn()`` and restart it only if it raises.

    :param coro_fn: Async callable (factory) returning a coroutine.
    :param name: Human-readable name for logging.
    :param on_error: Optional callback(error) for metrics/monitoring.
    """
    loop = asyncio.get_running_loop()
    delay = INITIAL_RESTART_DELAY
    while True:
        started = loop.time()
        try:
            await coro_fn()
        except asyncio.CancelledError:
            _LOG.debug("Supervised task '%s' cancelled", name)
            raise
        except Exception as e:
            if loop.time() - started > MAX_RESTART_DELAY:
                # The last run was healthy for a while: start the backoff over.
                delay = INITIAL_RESTART_DELAY
            _LOG.exception("Task '%s' crashed, restarting in %.1fs: %s", name, delay, e)
            if on_error:
                try:
                    on_error(e)
                except Exception:
                    _LOG.debug("on_error callback for '%s' failed", name, exc_info=True)
            await asyncio.sleep(delay)
            delay = min(delay * 2, MAX_RESTART_DELAY)
            continue

        _LOG.debug("Supervised task '%s' finished", name)
        return


async def cancel_and_wait(task: asyncio.Task | None, name: str = "", timeout: float = 2.0) -> None:
    """Cancel ``task`` and wait until it has finished.

    Unlike ``task.cancel(); await task`` this never swallows a cancellation
    of the *calling* task (it propagates), and it gives up after ``timeout``
    seconds instead of hanging on a task that ignores cancellation.
    Cancelling the current task (a task stopping itself) is a no-op.
    """
    if task is None or task.done() or task is asyncio.current_task():
        return
    task.cancel()
    done, _ = await asyncio.wait([task], timeout=timeout)
    if not done:
        _LOG.warning("Task '%s' did not stop within %.1fs of being cancelled", name or task.get_name(), timeout)


def create_supervised_task(
    coro_fn: Callable[[], Awaitable[Any]],
    name: str,
    on_error: Callable[[BaseException], Any] | None = None,
) -> asyncio.Task:
    """
    Create an asyncio.Task that restarts ``coro_fn`` when it crashes.

    A normal return ends the task; cancelling the task stops it.

    :param coro_fn: Async callable (factory) returning a coroutine.
    :param name: Human-readable name for logging.
    :param on_error: Optional callback(error) for metrics.
    :return: asyncio.Task
    """
    return asyncio.create_task(
        _supervised_loop(coro_fn, name, on_error),
        name=name,
    )
