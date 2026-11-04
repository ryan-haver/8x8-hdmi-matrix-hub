"""Bounded, owner-scoped admission for work started by /ws client frames (CR-01).

Status: **internal component only**. Nothing imports it yet; ``websocket.py``
still starts one ``ws_get_status`` task per frame. Wiring it in is a later,
separately reviewed change, and this module does not close CR-01 by itself.

What it is for
    ``_handle_command`` in ``websocket.py`` is a plain function that runs in the
    event loop for every TEXT frame. For ``get_status`` it must start a task
    (the reply needs a fresh matrix read) without awaiting it. This module gives
    that call site an admission decision with two bounds:

    * per owner (one owner per WebSocket connection): at most ``owner_limit``
      tasks in flight, default 1;
    * per application (one :class:`WsRequestWork` per aiohttp app, held by the
      app, never module-global): at most ``application_limit`` tasks in flight
      across all owners. This limit is required and has no default.

    A rejected request starts nothing: the coroutine factory is **not called**,
    so no coroutine object exists that could go unawaited, and nothing is queued.
    The caller decides how to answer a rejection (see "Wiring" below).

Ownership
    The controller owns every task it admits. It keeps a strong reference from
    admission until the task's done callback has run, so a task cannot be
    garbage collected mid-flight and cannot be forgotten. Each done callback
    removes exactly the task it was registered for; it can never remove another
    (successor) task, and nothing ever reopens a closed owner.

    Owners are not registered with the controller. The controller maps each live
    task to its owner; an owner with no live tasks is referenced only by its
    caller, so a disconnected socket leaves nothing behind once its tasks finish.

Lifecycle
    * :meth:`WorkOwner.close` (synchronous, idempotent): stop admitting for this
      owner and request cancellation of its live tasks. Other owners are untouched.
    * :meth:`WorkOwner.aclose`: ``close()`` then wait, at most ``timeout``
      seconds, for this owner's tasks only.
    * :meth:`WsRequestWork.begin_shutdown` (synchronous, idempotent): stop
      admitting for every owner, including owners opened later, and request
      cancellation of every live task.
    * :meth:`WsRequestWork.shutdown`: ``begin_shutdown()`` then wait, at most
      ``timeout`` seconds, for every task.

    Both waits are bounded and return a :class:`DrainReport`. Calling them again
    requests cancellation again for whatever is still alive and waits again,
    bounded each time; it never reopens admission.

Cooperative and resistant cancellation
    ``Task.cancel()`` is a request. A cooperative task (the normal case: it is
    suspended in an ``await`` and lets ``CancelledError`` propagate) finishes
    within the wait and its capacity is released. A *resistant* task (it catches
    ``CancelledError`` and keeps running, or blocks the loop) cannot be stopped
    from here. Such a task stays referenced, stays counted against both limits
    and is reported in ``DrainReport.remaining``; the report never says
    ``drained`` while it is alive. Its capacity is released only when it
    actually ends. Nothing here kills it or hides it.

    If the coroutine awaiting ``aclose``/``shutdown`` is itself cancelled, the
    cancellation propagates to that caller; the owner/controller stays closed and
    the tasks stay tracked (``asyncio.wait`` does not cancel what it waits for).

Failures
    Every done callback retrieves the task's result, so a failed task never
    produces "Task exception was never retrieved". A failure is logged at
    WARNING with the exception **type name only**: exception messages and the
    task's arguments may carry request payloads, matrix data or credentials and
    are never logged or kept. The coroutine itself should still handle its own
    errors (``_reply_status`` already answers ``error`` to the client).

Threading
    Not thread-safe by design: every method must be called from the event loop
    the controller first admitted work on (aiohttp handlers already are). A call
    from another loop raises ``RuntimeError`` before the factory is called.

Admission is atomic with respect to the event loop: :meth:`WorkOwner.try_start`
never awaits, and it reserves capacity *before* calling the factory or creating
the task. A factory, or an eagerly started task (``asyncio.eager_task_factory``),
that re-enters ``try_start`` therefore sees the reservation and cannot exceed
either bound.

Wiring (proposed, not done here)
    ``create_rest_app`` creates one ``WsRequestWork(application_limit=N,
    name="ws_get_status")``, stores it under an ``web.AppKey`` and appends a
    ``cleanup_ctx`` whose exit awaits ``shutdown(timeout=...)``. ``handle_websocket``
    opens one owner after ``ws.prepare`` and awaits ``owner.aclose(timeout=...)``
    in its ``finally``. ``_handle_command`` replaces ``create_task`` with
    ``owner.try_start(lambda: _reply_status(stream, ws))`` and answers a
    rejection with the existing ``error`` event (``{"message": <str>}``), which
    keeps the public schema unchanged. Whether an ``OWNER_BUSY`` rejection should
    instead be coalesced with the in-flight read is a wiring decision with a
    freshness consequence, recorded in the author report.

Import side effects: none. The module imports only the standard library, keeps
no module-level mutable state and looks up its logger only when it logs.
"""

from __future__ import annotations

import asyncio
import enum
import itertools
import logging
import math
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any, TypeVar

__all__ = ["DrainReport", "RejectReason", "WorkOwner", "WsRequestWork"]

_T = TypeVar("_T")

#: Logger name used for the (rare) failure messages. Looked up lazily.
LOGGER_NAME = "rest_api.ws_request_work"

#: Default bounded wait for :meth:`WorkOwner.aclose` (seconds).
DEFAULT_OWNER_CLOSE_TIMEOUT = 1.0
#: Default bounded wait for :meth:`WsRequestWork.shutdown` (seconds).
DEFAULT_SHUTDOWN_TIMEOUT = 5.0


class RejectReason(enum.Enum):
    """Why :meth:`WorkOwner.try_start` did not start the work."""

    #: This owner already has ``owner_limit`` tasks in flight.
    OWNER_BUSY = "owner_busy"
    #: All owners together already have ``application_limit`` tasks in flight.
    APPLICATION_BUSY = "application_busy"
    #: This owner was closed (its socket disconnected).
    OWNER_CLOSED = "owner_closed"
    #: The application began shutting down.
    SHUTTING_DOWN = "shutting_down"


@dataclass(frozen=True, slots=True)
class DrainReport:
    """Outcome of one bounded :meth:`WorkOwner.aclose` / :meth:`WsRequestWork.shutdown`.

    :ivar requested: live tasks cancellation was requested for by this call
    :ivar remaining: of those, tasks still not finished when the wait ended
        (cancellation-resistant or slow); they stay referenced and counted
    """

    requested: int
    remaining: int

    @property
    def drained(self) -> bool:
        """Every task this call cancelled has finished."""
        return self.remaining == 0


def _validate_limit(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int, not {type(value).__name__}")
    if value < 1:
        raise ValueError(f"{name} must be at least 1, got {value}")
    return value


def _validate_timeout(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"timeout must be a number of seconds, not {type(value).__name__}")
    seconds = float(value)
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError(f"timeout must be finite and not negative, got {value!r}")
    return seconds


async def _wait_bounded(tasks: list[asyncio.Task[Any]], timeout: float) -> int:
    """Wait at most ``timeout`` s for ``tasks``; return how many are still running.

    ``asyncio.wait`` neither raises the tasks' exceptions nor cancels them when
    this waiter is cancelled, which is what a bounded drain needs.
    """
    if not tasks:
        return 0
    if timeout > 0:
        await asyncio.wait(tasks, timeout=timeout)
    return sum(1 for task in tasks if not task.done())


class WorkOwner:
    """The admission scope of one WebSocket connection. Create with :meth:`WsRequestWork.open_owner`."""

    __slots__ = ("_closed", "_controller", "_id", "_reserved", "_tasks", "__weakref__")

    def __init__(self, controller: WsRequestWork, owner_id: int) -> None:
        self._controller = controller
        self._id = owner_id
        self._closed = False
        self._reserved = 0
        self._tasks: set[asyncio.Task[Any]] = set()

    def __repr__(self) -> str:
        return (f"<WorkOwner #{self._id} active={len(self._tasks)} "
                f"{'closed' if self.closed else 'open'}>")

    @property
    def owner_id(self) -> int:
        """A per-controller sequence number (diagnostics only; carries no client data)."""
        return self._id

    @property
    def closed(self) -> bool:
        """No further work will be admitted (closed, or the application is shutting down)."""
        return self._closed or self._controller.closing

    @property
    def active_count(self) -> int:
        """Tasks of this owner that hold capacity (admitted and not yet released)."""
        return len(self._tasks) + self._reserved

    def tasks(self) -> frozenset[asyncio.Task[Any]]:
        """A snapshot of this owner's live tasks (for diagnostics and tests)."""
        return frozenset(self._tasks)

    def try_start(self, factory: Callable[[], Coroutine[Any, Any, _T]], *,
                  name: str | None = None) -> asyncio.Task[_T] | RejectReason:
        """Start ``factory()`` as a task if both bounds allow it; never awaits.

        On rejection ``factory`` is not called and nothing is scheduled.

        :param factory: called with no arguments, at most once, only when
            admitted; must return a coroutine
        :param name: the task name (defaults to the controller's ``name``)
        :returns: the started task, or why nothing was started
        :raises RuntimeError: no running event loop, or not the controller's loop
            (the factory is not called)
        :raises TypeError: ``factory()`` did not return a coroutine (any
            awaitable it returned is closed if it can be; no capacity is kept)
        """
        return self._controller._admit(self, factory, name)

    def close(self) -> None:
        """Stop admitting and request cancellation of this owner's live tasks. Idempotent."""
        self._closed = True
        for task in list(self._tasks):
            task.cancel()

    async def aclose(self, timeout: float = DEFAULT_OWNER_CLOSE_TIMEOUT) -> DrainReport:
        """:meth:`close`, then wait at most ``timeout`` s for this owner's tasks only.

        Unrelated owners are neither cancelled nor waited for.
        """
        seconds = _validate_timeout(timeout)
        tasks = [task for task in self._tasks if not task.done()]
        self.close()
        return DrainReport(requested=len(tasks), remaining=await _wait_bounded(tasks, seconds))


class WsRequestWork:
    """Bounded application-owned work for /ws requests (see the module docstring).

    :param application_limit: tasks in flight across all owners (required, >= 1)
    :param owner_limit: tasks in flight per owner (default 1, at most
        ``application_limit``)
    :param name: default task name, e.g. ``"ws_get_status"``
    """

    def __init__(self, *, application_limit: int, owner_limit: int = 1, name: str = "ws_request_work") -> None:
        self.application_limit = _validate_limit("application_limit", application_limit)
        self.owner_limit = _validate_limit("owner_limit", owner_limit)
        if self.owner_limit > self.application_limit:
            raise ValueError(f"owner_limit ({owner_limit}) must not exceed application_limit ({application_limit})")
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        self.name = name
        self._closing = False
        self._loop: asyncio.AbstractEventLoop | None = None
        #: Live task -> its owner. Insertion ordered; the only strong task references.
        self._tasks: dict[asyncio.Task[Any], WorkOwner] = {}
        self._reserved = 0
        self._ids = itertools.count(1)
        self._counts: dict[str, int] = {
            "admitted": 0, "completed": 0, "failed": 0, "cancelled": 0,
            **{f"rejected_{reason.value}": 0 for reason in RejectReason},
        }

    def __repr__(self) -> str:
        return (f"<WsRequestWork {self.name!r} active={self.active_count}/{self.application_limit} "
                f"{'closing' if self._closing else 'open'}>")

    # ------------------------------------------------------------------ state

    @property
    def closing(self) -> bool:
        """Shutdown has begun; nothing more is admitted, ever."""
        return self._closing

    @property
    def active_count(self) -> int:
        """Tasks holding application capacity (admitted and not yet released)."""
        return len(self._tasks) + self._reserved

    def tasks(self) -> frozenset[asyncio.Task[Any]]:
        """A snapshot of every live task (for diagnostics and tests)."""
        return frozenset(self._tasks)

    def diagnostics(self) -> dict[str, Any]:
        """Counts only: no client identity, payload, exception message or credential."""
        return {
            "name": self.name,
            "closing": self._closing,
            "active": self.active_count,
            "owners_active": len(set(self._tasks.values())),
            "application_limit": self.application_limit,
            "owner_limit": self.owner_limit,
            **self._counts,
        }

    # ------------------------------------------------------------------ owners

    def open_owner(self) -> WorkOwner:
        """A new owner for one connection.

        Never raises: an owner opened after shutdown began is already
        ``closed`` (it follows the controller), so a socket that connects during
        shutdown gets ``SHUTTING_DOWN`` rejections rather than an exception.
        """
        return WorkOwner(self, next(self._ids))

    # ------------------------------------------------------------------ admission

    def _check_loop(self) -> asyncio.AbstractEventLoop:
        loop = asyncio.get_running_loop()  # RuntimeError outside the loop
        if self._loop is None:
            self._loop = loop
        elif self._loop is not loop:
            raise RuntimeError(f"{self!r} is bound to a different event loop")
        return loop

    def _reject(self, reason: RejectReason) -> RejectReason:
        self._counts[f"rejected_{reason.value}"] += 1
        return reason

    def _admit(self, owner: WorkOwner, factory: Callable[[], Coroutine[Any, Any, _T]],
               name: str | None) -> asyncio.Task[_T] | RejectReason:
        loop = self._check_loop()
        # Order matters: a closed scope reports why it is closed, not that it is busy.
        if self._closing:
            return self._reject(RejectReason.SHUTTING_DOWN)
        if owner._closed:
            return self._reject(RejectReason.OWNER_CLOSED)
        if owner.active_count >= self.owner_limit:
            return self._reject(RejectReason.OWNER_BUSY)
        if self.active_count >= self.application_limit:
            return self._reject(RejectReason.APPLICATION_BUSY)

        # Reserve before anything can run code of the caller's (the factory, or an
        # eager task's first step): a re-entrant try_start then sees this slot taken.
        owner._reserved += 1
        self._reserved += 1
        task: asyncio.Task[_T] | None = None
        try:
            coro = factory()
            if not asyncio.iscoroutine(coro):
                close = getattr(coro, "close", None)
                if callable(close):
                    close()
                raise TypeError(f"factory must return a coroutine, not {type(coro).__name__}")
            try:
                task = loop.create_task(coro, name=name or self.name)
            except BaseException:
                coro.close()  # never leave an unawaited coroutine behind
                raise
            # Registered while the reservation still holds the slot, so the count
            # never dips between "reserved" and "tracked".
            self._tasks[task] = owner
            owner._tasks.add(task)
        finally:
            owner._reserved -= 1
            self._reserved -= 1
        task.add_done_callback(self._release)
        self._counts["admitted"] += 1
        if self._closing or owner._closed:
            # The factory or an eager first step closed the scope before the task was
            # tracked, so that close() could not see it: cancel it now, as close() would have.
            task.cancel()
        return task

    def _release(self, task: asyncio.Task[Any]) -> None:
        """Done callback of one task: free exactly its slot and retrieve its outcome."""
        owner = self._tasks.pop(task, None)
        if owner is None:
            return  # not (or no longer) tracked: a stale call frees nothing and counts nothing
        owner._tasks.discard(task)
        if task.cancelled():
            self._counts["cancelled"] += 1
            return
        exc = task.exception()  # marks the exception retrieved
        if exc is None:
            self._counts["completed"] += 1
            return
        self._counts["failed"] += 1
        logging.getLogger(LOGGER_NAME).warning(
            "%s task failed: %s (details withheld)", self.name, type(exc).__name__)

    # ------------------------------------------------------------------ shutdown

    def begin_shutdown(self) -> None:
        """Stop admitting for every owner (also owners opened later) and cancel all live tasks. Idempotent."""
        self._closing = True
        for task in list(self._tasks):
            task.cancel()

    async def shutdown(self, timeout: float = DEFAULT_SHUTDOWN_TIMEOUT) -> DrainReport:
        """:meth:`begin_shutdown`, then wait at most ``timeout`` s for every task."""
        seconds = _validate_timeout(timeout)
        tasks = [task for task in self._tasks if not task.done()]
        self.begin_shutdown()
        return DrainReport(requested=len(tasks), remaining=await _wait_bounded(tasks, seconds))
