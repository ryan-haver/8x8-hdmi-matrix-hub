"""
Background Task Supervisor.

Wraps long-lived asyncio tasks with automatic crash restart,
ensuring that a single unhandled exception cannot permanently
kill critical background loops (push listener, reconnect loop,
status polling).
"""

import asyncio
import logging

_LOG = logging.getLogger(__name__)

async def _supervised_loop(coro_fn, name: str, on_error=None):
    """
    Run ``coro_fn()`` in an infinite restart loop.

    On any exception other than CancelledError, logs the error and
    restarts the coroutine after a 5-second backoff.

    :param coro_fn: Async callable (factory) returning a coroutine.
    :param name: Human-readable name for logging.
    :param on_error: Optional callback(error) for metrics/monitoring.
    """
    while True:
        try:
            await coro_fn()
        except asyncio.CancelledError:
            _LOG.debug(f"Supervised task '{name}' cancelled")
            raise
        except Exception as e:
            _LOG.exception(f"Task '{name}' crashed, restarting in 5s: {e}")
            if on_error:
                try:
                    on_error(e)
                except Exception:
                    pass
            await asyncio.sleep(5)


def create_supervised_task(coro_fn, name: str, on_error=None):
    """
    Create an asyncio.Task that auto-restarts on failure.

    :param coro_fn: Async callable (factory) returning a coroutine.
    :param name: Human-readable name for logging.
    :param on_error: Optional callback(error) for metrics.
    :return: asyncio.Task
    """
    return asyncio.create_task(
        _supervised_loop(coro_fn, name, on_error),
        name=name,
    )
