"""Tests for rest_api.ws_request_work (CR-01 candidate component, not yet wired).

These tests exercise the component on its own. Where they model the future
call site they drive the *existing, unmodified* ``websocket._reply_status``
with a fake event stream; they do not open an HTTP/WebSocket connection and do
not show that ``/ws`` is fixed. ``websocket.py`` still has no admission bound.

Evidence is taken from real asyncio effects (tasks that exist in
``asyncio.all_tasks()``, factory calls, refresh calls, messages sent, task
states, loop exception-handler calls, RuntimeWarnings), not from the
component's own counters alone. No test uses a timing delay as evidence: waits
are on events, and "let pending callbacks run" uses a FIFO ``call_soon``
barrier. Every task a test creates is finished or cancelled and awaited before
the test ends; the ``make_work`` fixture fails a test that leaves one behind.
"""

from __future__ import annotations

import ast
import asyncio
import gc
import inspect
import json
import logging
import subprocess
import sys
import time
import warnings
from collections.abc import AsyncIterator, Callable, Coroutine
from pathlib import Path
from typing import Any

import pytest

from rest_api import websocket
from rest_api.ws_request_work import (
    LOGGER_NAME,
    DrainReport,
    RejectReason,
    WorkOwner,
    WsRequestWork,
)

MODULE_PATH = Path(__file__).resolve().parent.parent / "src" / "rest_api" / "ws_request_work.py"
BURST = 1000
#: Outer guard (s) so a broken bound fails a test instead of hanging the run. Not evidence of timing.
GUARD = 10


# --------------------------------------------------------------------------- helpers


async def flush_callbacks() -> None:
    """Let every callback already scheduled with ``call_soon`` run (FIFO barrier, not a delay)."""
    loop = asyncio.get_running_loop()
    barrier = loop.create_future()
    loop.call_soon(barrier.set_result, None)
    await barrier


async def within(awaitable: Any) -> Any:
    """Await with the outer ``GUARD``: under a bug this fails the test instead of hanging the run."""
    return await asyncio.wait_for(awaitable, GUARD)


class Factory:
    """A coroutine factory that records every call and every coroutine it made."""

    def __init__(self, coro_fn: Callable[[], Coroutine[Any, Any, Any]]) -> None:
        self.coro_fn = coro_fn
        self.calls = 0

    def __call__(self) -> Coroutine[Any, Any, Any]:
        self.calls += 1
        return self.coro_fn()


def never_call() -> Coroutine[Any, Any, Any]:
    raise AssertionError("a rejected factory was called")


class FakeStream:
    """Stands in for ``EventStream`` at the ``_reply_status`` call site.

    Every ``refresh()`` blocks on its own gate until the test opens it, like a
    matrix read that has not answered yet.
    """

    def __init__(self) -> None:
        self.gates: list[asyncio.Event] = []
        self.started = asyncio.Event()
        self.sent: list[tuple[object, str, dict[str, Any]]] = []

    async def refresh(self) -> dict[str, Any] | None:
        gate = asyncio.Event()
        self.gates.append(gate)
        self.started.set()
        await gate.wait()
        return {"routing": {"1": 1}}

    def send(self, ws: object, event: str, data: dict[str, Any]) -> None:
        self.sent.append((ws, event, data))

    def events_for(self, ws: object) -> list[str]:
        return [event for target, event, _ in self.sent if target is ws]


def reply_factory(stream: FakeStream, ws: object) -> Factory:
    """The future ``_handle_command`` factory: the real, unmodified ``_reply_status``."""
    return Factory(lambda: websocket._reply_status(stream, ws))  # type: ignore[arg-type]


async def blocked(gate: asyncio.Event) -> str:
    await gate.wait()
    return "done"


async def returns(value: Any) -> Any:
    return value


@pytest.fixture
async def make_work() -> AsyncIterator[Callable[..., WsRequestWork]]:
    """Create controllers; fail the test if it leaves any task alive."""
    before = asyncio.all_tasks()
    created: list[WsRequestWork] = []

    def make(**kwargs: Any) -> WsRequestWork:
        kwargs.setdefault("application_limit", 4)
        work = WsRequestWork(**kwargs)
        created.append(work)
        return work

    yield make

    me = asyncio.current_task()
    leaked = [t for t in asyncio.all_tasks() if t not in before and t is not me and not t.done()]
    still_owned = [w for w in created if w.active_count]
    # Clean up regardless, so one failure cannot poison later tests ...
    for task in leaked:
        task.cancel()
    if leaked:
        await asyncio.wait(leaked, timeout=5)
    # ... but a test that did not drain its own work fails.
    assert not leaked, f"test left tasks running: {leaked}"
    assert not still_owned, f"test left work holding capacity: {still_owned}"


# --------------------------------------------------------------------------- bounds (acceptance 1, 3)


async def test_one_socket_burst_of_1000_get_status_starts_one_read(make_work):
    """CR-01 shape: a pending read plus 1,000 more frames from the same socket."""
    work = make_work(application_limit=8, name="ws_get_status")
    stream, ws_a = FakeStream(), object()
    owner = work.open_owner()
    factory = reply_factory(stream, ws_a)
    before = asyncio.all_tasks()

    results = [owner.try_start(factory) for _ in range(BURST + 1)]

    started = [r for r in results if isinstance(r, asyncio.Task)]
    assert len(started) == 1
    assert results[1:] == [RejectReason.OWNER_BUSY] * BURST
    assert factory.calls == 1
    assert asyncio.all_tasks() - before == {started[0]}
    assert started[0].get_name() == "ws_get_status"
    await stream.started.wait()
    assert len(stream.gates) == 1  # one matrix read in flight, not 1,001

    # A second client is served while the first one's read is still pending.
    ws_b = object()
    other = work.open_owner()
    task_b = other.try_start(reply_factory(stream, ws_b))
    assert isinstance(task_b, asyncio.Task)
    while len(stream.gates) < 2:
        stream.started.clear()
        await stream.started.wait()
    stream.gates[1].set()
    await task_b
    assert stream.events_for(ws_b) == ["status"]
    assert not started[0].done() and stream.events_for(ws_a) == []

    stream.gates[0].set()
    await started[0]
    assert stream.events_for(ws_a) == ["status"]  # exactly one answer for the burst
    assert work.active_count == 0
    # Capacity came back: the same socket can ask again.
    again = owner.try_start(reply_factory(stream, ws_a))
    assert isinstance(again, asyncio.Task)
    await owner.aclose()
    assert again.cancelled()


async def test_1000_sockets_are_held_to_the_application_limit(make_work):
    work = make_work(application_limit=5)
    stream = FakeStream()
    clients = [(work.open_owner(), object()) for _ in range(BURST)]
    factories = [reply_factory(stream, ws) for _, ws in clients]
    before = asyncio.all_tasks()

    results = [owner.try_start(f) for (owner, _), f in zip(clients, factories, strict=True)]

    started = [r for r in results if isinstance(r, asyncio.Task)]
    assert len(started) == 5
    assert results[5:] == [RejectReason.APPLICATION_BUSY] * (BURST - 5)
    assert [f.calls for f in factories[:5]] == [1] * 5
    assert sum(f.calls for f in factories[5:]) == 0
    assert asyncio.all_tasks() - before == set(started)
    assert work.diagnostics()["owners_active"] == 5

    # One finishing frees exactly one slot, which the next client can take.
    while len(stream.gates) < 5:
        stream.started.clear()
        await stream.started.wait()
    stream.gates[0].set()
    await started[0]
    late_owner, late_ws = clients[700]
    late = late_owner.try_start(reply_factory(stream, late_ws))
    assert isinstance(late, asyncio.Task)
    assert clients[701][0].try_start(never_call) is RejectReason.APPLICATION_BUSY

    report = await work.shutdown(timeout=5)
    assert report == DrainReport(requested=5, remaining=0) and report.drained
    # _reply_status lets cancellation through: cancelled reads answer nothing.
    assert all(t.cancelled() for t in started[1:]) and late.cancelled()
    assert [e for _, e, _ in stream.sent] == ["status"]


async def test_owner_limit_above_one_is_respected(make_work):
    work = make_work(application_limit=10, owner_limit=3)
    owner, gate = work.open_owner(), asyncio.Event()
    factory = Factory(lambda: blocked(gate))
    results = [owner.try_start(factory) for _ in range(BURST)]
    assert sum(isinstance(r, asyncio.Task) for r in results) == 3
    assert factory.calls == 3
    gate.set()
    assert await asyncio.gather(*owner.tasks()) == ["done"] * 3


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({}, TypeError),  # application_limit is required
        ({"application_limit": 0}, ValueError),
        ({"application_limit": -1}, ValueError),
        ({"application_limit": True}, TypeError),
        ({"application_limit": 2.0}, TypeError),
        ({"application_limit": "4"}, TypeError),
        ({"application_limit": 4, "owner_limit": 0}, ValueError),
        ({"application_limit": 4, "owner_limit": False}, TypeError),
        ({"application_limit": 2, "owner_limit": 3}, ValueError),
        ({"application_limit": 2, "name": ""}, ValueError),
    ],
)
def test_limits_are_validated(kwargs, error):
    with pytest.raises(error):
        WsRequestWork(**kwargs)


# --------------------------------------------------------------------------- rejected work is never created


async def test_every_rejection_reason_leaves_the_factory_uncalled(make_work):
    work = make_work(application_limit=1)
    gate = asyncio.Event()
    busy_owner, other, closed = work.open_owner(), work.open_owner(), work.open_owner()
    first = busy_owner.try_start(lambda: blocked(gate))
    assert isinstance(first, asyncio.Task)
    closed.close()
    before = asyncio.all_tasks()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert busy_owner.try_start(never_call) is RejectReason.OWNER_BUSY
        assert other.try_start(never_call) is RejectReason.APPLICATION_BUSY
        assert closed.try_start(never_call) is RejectReason.OWNER_CLOSED
        work.begin_shutdown()
        for owner in (busy_owner, other, closed, work.open_owner()):
            assert owner.try_start(never_call) is RejectReason.SHUTTING_DOWN
        gc.collect()

    assert asyncio.all_tasks() - before == set()
    assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]
    assert await work.shutdown() == DrainReport(requested=1, remaining=0)
    assert first.cancelled()
    counts = work.diagnostics()
    assert counts["rejected_owner_busy"] == counts["rejected_application_busy"] == 1
    assert counts["rejected_owner_closed"] == 1 and counts["rejected_shutting_down"] == 4


def test_unawaited_coroutine_detection_works():
    """Negative control for the RuntimeWarning check above: a dropped coroutine *is* reported."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        coro = returns(1)
        del coro
        gc.collect()
    assert any("never awaited" in str(w.message) for w in caught)


async def test_factory_errors_and_bad_returns_keep_no_capacity(make_work):
    work = make_work(application_limit=1)
    owner = work.open_owner()
    before = asyncio.all_tasks()

    def explode() -> Coroutine[Any, Any, Any]:
        raise LookupError("factory failed")

    with pytest.raises(LookupError):
        owner.try_start(explode)
    for not_a_coroutine in (lambda: 42, lambda: None):
        with pytest.raises(TypeError):
            owner.try_start(not_a_coroutine)

    # An awaitable that is not a coroutine is closed rather than leaked.
    class Closable:
        closed = False

        def close(self) -> None:
            self.closed = True

    closable = Closable()
    with pytest.raises(TypeError):
        owner.try_start(lambda: closable)
    assert closable.closed

    assert asyncio.all_tasks() - before == set()
    assert work.active_count == 0 and owner.active_count == 0
    ok = owner.try_start(lambda: returns("ok"))
    assert isinstance(ok, asyncio.Task)
    assert await ok == "ok"


async def test_task_creation_failure_closes_the_coroutine(make_work):
    work = make_work(application_limit=1)
    owner = work.open_owner()
    loop = asyncio.get_running_loop()
    previous = loop.get_task_factory()
    made: list[Coroutine[Any, Any, Any]] = []

    def failing_task_factory(_loop, coro, **_kwargs):
        made.append(coro)
        raise RuntimeError("task creation refused")

    loop.set_task_factory(failing_task_factory)
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with pytest.raises(RuntimeError, match="task creation refused"):
                owner.try_start(lambda: returns(1))
            gc.collect()
    finally:
        loop.set_task_factory(previous)
    assert len(made) == 1 and inspect.getcoroutinestate(made[0]) == inspect.CORO_CLOSED
    assert not [w for w in caught if "never awaited" in str(w.message)]
    assert work.active_count == 0
    ok = owner.try_start(lambda: returns(2))
    assert isinstance(ok, asyncio.Task) and await ok == 2


def test_admission_needs_the_running_loop():
    work = WsRequestWork(application_limit=1)
    with pytest.raises(RuntimeError):
        work.open_owner().try_start(never_call)
    assert work.active_count == 0


def test_a_controller_stays_on_its_first_loop():
    work = WsRequestWork(application_limit=2)
    owner = work.open_owner()

    async def first_loop() -> Any:
        task = owner.try_start(lambda: returns("first"))
        assert isinstance(task, asyncio.Task)
        return await task

    async def second_loop() -> None:
        with pytest.raises(RuntimeError, match="different event loop"):
            owner.try_start(never_call)

    assert asyncio.run(first_loop()) == "first"
    asyncio.run(second_loop())
    assert work.active_count == 0


# --------------------------------------------------------------------------- outcomes release capacity


async def test_completion_failure_and_cancellation_each_release_the_slot(make_work, caplog):
    work = make_work(application_limit=1)
    owner = work.open_owner()

    done = owner.try_start(lambda: returns("value"))
    assert isinstance(done, asyncio.Task) and await done == "value"
    assert work.active_count == 0

    async def fails() -> None:
        raise RuntimeError("api_key=SECRET-TOKEN-123 frame={'command': 'get_status'}")

    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        failed = owner.try_start(fails)
        assert isinstance(failed, asyncio.Task)
        await within(asyncio.wait([failed]))  # does not retrieve the exception itself
        await flush_callbacks()
    assert work.active_count == 0
    messages = [r.getMessage() for r in caplog.records if r.name == LOGGER_NAME]
    assert messages == ["ws_request_work task failed: RuntimeError (details withheld)"]
    assert "SECRET" not in caplog.text and "SECRET" not in json.dumps(work.diagnostics())

    gate = asyncio.Event()
    cancelled = owner.try_start(lambda: blocked(gate))
    assert isinstance(cancelled, asyncio.Task)
    assert owner.try_start(never_call) is RejectReason.OWNER_BUSY
    cancelled.cancel()  # cancelled by someone else, not by the controller
    await within(asyncio.wait([cancelled]))
    await flush_callbacks()
    assert cancelled.cancelled() and work.active_count == 0

    counts = work.diagnostics()
    assert (counts["admitted"], counts["completed"], counts["failed"], counts["cancelled"]) == (3, 1, 1, 1)
    last = owner.try_start(lambda: returns(None))
    assert isinstance(last, asyncio.Task)
    await last


async def test_failed_task_exception_is_retrieved(make_work):
    """The loop's 'exception was never retrieved' report fires for a plain task, not for ours."""
    loop = asyncio.get_running_loop()
    previous = loop.get_exception_handler()
    reports: list[dict[str, Any]] = []
    loop.set_exception_handler(lambda _loop, context: reports.append(context))

    async def fails() -> None:
        raise ValueError("boom")

    try:
        work = make_work(application_limit=1)
        ours = work.open_owner().try_start(fails)
        assert isinstance(ours, asyncio.Task)
        await within(asyncio.wait([ours]))
        await flush_callbacks()
        del ours
        gc.collect()
        assert reports == []

        # Negative control: the same failure in an untracked task is reported.
        plain = loop.create_task(fails())
        await within(asyncio.wait([plain]))
        del plain
        gc.collect()
        assert [r["message"] for r in reports] == ["Task exception was never retrieved"]
    finally:
        loop.set_exception_handler(previous)


# --------------------------------------------------------------------------- disconnect and shutdown (acceptance 2)


async def test_disconnect_cancels_only_that_socket_and_closes_it_for_good(make_work):
    work = make_work(application_limit=4)
    stream = FakeStream()
    (a, ws_a), (b, ws_b) = (work.open_owner(), object()), (work.open_owner(), object())
    task_a = a.try_start(reply_factory(stream, ws_a))
    task_b = b.try_start(reply_factory(stream, ws_b))
    assert isinstance(task_a, asyncio.Task) and isinstance(task_b, asyncio.Task)
    while len(stream.gates) < 2:
        stream.started.clear()
        await stream.started.wait()

    report = await a.aclose(timeout=5)

    assert report == DrainReport(requested=1, remaining=0) and report.drained
    assert task_a.cancelled() and stream.events_for(ws_a) == []
    assert not task_b.done() and not task_b.cancelling()
    assert a.closed and a.active_count == 0 and a.tasks() == frozenset()
    assert work.tasks() == {task_b}
    assert a.try_start(never_call) is RejectReason.OWNER_CLOSED
    # Idempotent: nothing left to cancel, still closed, still bounded.
    assert await a.aclose(timeout=5) == DrainReport(requested=0, remaining=0)
    a.close()
    assert a.try_start(never_call) is RejectReason.OWNER_CLOSED

    stream.gates[1].set()
    await task_b
    assert stream.events_for(ws_b) == ["status"]
    await b.aclose()


async def test_shutdown_stops_all_admission_and_drains(make_work):
    work = make_work(application_limit=3)
    gate = asyncio.Event()
    owners = [work.open_owner() for _ in range(3)]
    tasks = [o.try_start(lambda: blocked(gate)) for o in owners]
    assert all(isinstance(t, asyncio.Task) for t in tasks)

    report = await work.shutdown(timeout=5)

    assert report == DrainReport(requested=3, remaining=0)
    assert all(t.cancelled() for t in tasks)
    assert work.closing and work.active_count == 0 and work.tasks() == frozenset()
    late = work.open_owner()
    assert late.closed
    assert late.try_start(never_call) is RejectReason.SHUTTING_DOWN
    assert all(o.try_start(never_call) is RejectReason.SHUTTING_DOWN for o in owners)
    assert await work.shutdown(timeout=5) == DrainReport(requested=0, remaining=0)
    work.begin_shutdown()
    assert await owners[0].aclose() == DrainReport(requested=0, remaining=0)


async def test_admission_is_refused_from_the_moment_shutdown_starts(make_work):
    """While shutdown waits for slow cancellation cleanup, nothing new is admitted."""
    work = make_work(application_limit=2)
    owner = work.open_owner()
    cancel_seen, cleanup_may_finish = asyncio.Event(), asyncio.Event()

    async def slow_cleanup() -> None:
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancel_seen.set()
            await cleanup_may_finish.wait()
            raise

    task = owner.try_start(slow_cleanup)
    assert isinstance(task, asyncio.Task)
    await flush_callbacks()  # the task's first step was scheduled before this barrier: it is now suspended
    stopper = asyncio.get_running_loop().create_task(work.shutdown(timeout=30))
    await within(cancel_seen.wait())

    assert not stopper.done()
    assert owner.try_start(never_call) is RejectReason.SHUTTING_DOWN
    assert work.open_owner().try_start(never_call) is RejectReason.SHUTTING_DOWN

    cleanup_may_finish.set()
    assert await within(stopper) == DrainReport(requested=1, remaining=0)
    assert task.cancelled() and work.active_count == 0


async def test_disconnect_does_not_wait_for_other_sockets(make_work):
    """An unrelated owner's never-ending task does not block this owner's aclose."""
    work = make_work(application_limit=2)
    stuck_gate, own_gate = asyncio.Event(), asyncio.Event()
    stuck, mine = work.open_owner(), work.open_owner()
    stuck_task = stuck.try_start(lambda: blocked(stuck_gate))
    my_task = mine.try_start(lambda: blocked(own_gate))
    assert isinstance(stuck_task, asyncio.Task) and isinstance(my_task, asyncio.Task)

    assert await mine.aclose(timeout=30) == DrainReport(requested=1, remaining=0)
    assert not stuck_task.done() and not stuck_task.cancelling()

    stuck_gate.set()
    assert await stuck_task == "done"


# --------------------------------------------------------------------------- resistant cancellation


class Resistant:
    """A task body that swallows every cancellation until ``finish`` is set."""

    def __init__(self) -> None:
        self.finish = asyncio.Event()
        self.cancellations = 0
        self.running = asyncio.Event()
        self.task: asyncio.Task[Any] | None = None

    async def run(self) -> str:
        self.task = asyncio.current_task()
        self.running.set()
        while not self.finish.is_set():
            try:
                await self.finish.wait()
            except asyncio.CancelledError:
                self.cancellations += 1
                asyncio.current_task().uncancel()
        return "finished anyway"


@pytest.fixture
async def resistant(make_work) -> AsyncIterator[Callable[[], Resistant]]:
    """Make resistant bodies; teardown lets every one finish, so a failing test fails instead of hanging.

    (No cancellation can end a resistant task: left alive, it would block the
    event loop's own teardown. Depends on ``make_work`` so this runs first.)
    """
    bodies: list[Resistant] = []

    def make() -> Resistant:
        bodies.append(Resistant())
        return bodies[-1]

    yield make

    for body in bodies:
        body.finish.set()
    tasks = [body.task for body in bodies if body.task is not None]
    if tasks:
        await asyncio.wait_for(asyncio.wait(tasks), GUARD)


async def test_resistant_task_is_reported_held_and_never_hidden(make_work, resistant):
    work = make_work(application_limit=1)
    owner, bystander = work.open_owner(), work.open_owner()
    body = resistant()
    task = owner.try_start(body.run)
    assert isinstance(task, asyncio.Task)
    await body.running.wait()

    started = time.monotonic()
    report = await asyncio.wait_for(owner.aclose(timeout=0.2), GUARD)  # a hang fails, it does not stall
    elapsed = time.monotonic() - started

    assert report == DrainReport(requested=1, remaining=1) and not report.drained
    assert elapsed < 5  # bounded: it returned although the task is still alive
    assert not task.done() and body.cancellations == 1
    # Still owned, still referenced, still counted against the application limit.
    assert owner.tasks() == {task} and work.tasks() == {task}
    assert owner.active_count == work.active_count == 1
    assert bystander.try_start(never_call) is RejectReason.APPLICATION_BUSY
    assert owner.try_start(never_call) is RejectReason.OWNER_CLOSED

    # Repeating close asks again and stays bounded; a zero timeout does not wait at all.
    assert await owner.aclose(timeout=0) == DrainReport(requested=1, remaining=1)
    await flush_callbacks()
    assert body.cancellations == 2
    assert (await work.shutdown(timeout=0)).remaining == 1

    body.finish.set()
    assert await task == "finished anyway"
    assert work.active_count == 0 and owner.tasks() == frozenset()
    assert owner.closed  # finishing never reopens the owner
    assert bystander.try_start(never_call) is RejectReason.SHUTTING_DOWN


async def test_resistant_task_does_not_block_another_owners_disconnect(make_work, resistant):
    work = make_work(application_limit=2)
    stubborn, polite = work.open_owner(), work.open_owner()
    body, gate = resistant(), asyncio.Event()
    stubborn_task = stubborn.try_start(body.run)
    polite_task = polite.try_start(lambda: blocked(gate))
    assert isinstance(stubborn_task, asyncio.Task) and isinstance(polite_task, asyncio.Task)
    await body.running.wait()
    assert (await stubborn.aclose(timeout=0)).remaining == 1

    assert await polite.aclose(timeout=30) == DrainReport(requested=1, remaining=0)
    assert polite_task.cancelled() and not stubborn_task.done()

    body.finish.set()
    await stubborn_task


async def test_cancelling_the_closer_keeps_the_owner_closed_and_tracked(make_work):
    work = make_work(application_limit=1)
    owner = work.open_owner()
    cancel_seen, may_finish = asyncio.Event(), asyncio.Event()

    async def slow_cleanup() -> None:
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancel_seen.set()
            await may_finish.wait()
            raise

    task = owner.try_start(slow_cleanup)
    assert isinstance(task, asyncio.Task)
    await flush_callbacks()
    closer = asyncio.get_running_loop().create_task(owner.aclose(timeout=30))
    await within(cancel_seen.wait())
    closer.cancel()
    with pytest.raises(asyncio.CancelledError):
        await closer

    assert owner.closed and owner.tasks() == {task} and not task.done()
    assert owner.try_start(never_call) is RejectReason.OWNER_CLOSED
    may_finish.set()
    await within(asyncio.wait([task]))
    await flush_callbacks()
    assert task.cancelled() and work.active_count == 0


@pytest.mark.parametrize("timeout", [-1, float("nan"), float("inf"), True, "1", None])
async def test_drain_timeouts_are_validated_before_acting(make_work, timeout):
    work = make_work(application_limit=1)
    owner = work.open_owner()
    gate = asyncio.Event()
    task = owner.try_start(lambda: blocked(gate))
    assert isinstance(task, asyncio.Task)
    with pytest.raises((TypeError, ValueError)):
        await owner.aclose(timeout=timeout)
    with pytest.raises((TypeError, ValueError)):
        await work.shutdown(timeout=timeout)
    assert not owner.closed and not work.closing and not task.cancelling()
    gate.set()
    await task


# --------------------------------------------------------------------------- races


@pytest.fixture
async def eager_tasks():
    """Run the test with ``asyncio.eager_task_factory``: a task's first step runs inside create_task."""
    loop = asyncio.get_running_loop()
    previous = loop.get_task_factory()
    loop.set_task_factory(asyncio.eager_task_factory)
    yield
    loop.set_task_factory(previous)


async def test_completion_before_release_holds_the_slot_and_frees_only_itself(make_work, eager_tasks):
    work = make_work(application_limit=2, owner_limit=1)
    owner = work.open_owner()

    first = owner.try_start(lambda: returns("eager"))
    assert isinstance(first, asyncio.Task) and first.done()  # finished inside try_start
    # Its done callback has not run yet: the slot is still (conservatively) held.
    assert owner.active_count == 1 and owner.try_start(never_call) is RejectReason.OWNER_BUSY
    await flush_callbacks()
    assert owner.active_count == 0

    gate = asyncio.Event()
    successor = owner.try_start(lambda: blocked(gate))
    assert isinstance(successor, asyncio.Task) and not successor.done()
    # Fault injection: a stale or duplicated done callback for the finished task.
    work._release(first)
    assert owner.tasks() == {successor} and work.tasks() == {successor}
    assert work.diagnostics()["completed"] == 1  # not counted twice
    assert owner.try_start(never_call) is RejectReason.OWNER_BUSY

    gate.set()
    assert await successor == "done"


async def test_close_racing_a_completion_does_not_reopen_or_miscount(make_work, eager_tasks):
    work = make_work(application_limit=1)
    owner = work.open_owner()
    task = owner.try_start(lambda: returns("raced"))
    assert isinstance(task, asyncio.Task) and task.done()

    report = await owner.aclose(timeout=5)  # cancel() of an already finished task is a no-op
    await flush_callbacks()

    assert report == DrainReport(requested=0, remaining=0)
    assert task.result() == "raced"
    assert work.diagnostics()["completed"] == 1 and work.diagnostics()["cancelled"] == 0
    assert owner.closed and owner.active_count == 0
    assert owner.try_start(never_call) is RejectReason.OWNER_CLOSED


async def test_reentrant_admission_from_factory_and_eager_step_is_bounded(make_work, eager_tasks):
    work = make_work(application_limit=1)
    owner, other = work.open_owner(), work.open_owner()
    seen: list[RejectReason | asyncio.Task[Any]] = []
    gate = asyncio.Event()

    async def first_step_reenters() -> str:
        # Runs inside create_task (eager), before try_start has returned.
        seen.append(owner.try_start(never_call))
        seen.append(other.try_start(never_call))
        await gate.wait()
        return "ok"

    def factory_reenters() -> Coroutine[Any, Any, str]:
        seen.append(owner.try_start(never_call))  # before the coroutine even exists
        return first_step_reenters()

    task = owner.try_start(factory_reenters)
    assert isinstance(task, asyncio.Task)
    assert seen == [RejectReason.OWNER_BUSY, RejectReason.OWNER_BUSY, RejectReason.APPLICATION_BUSY]
    assert work.active_count == 1 and work.tasks() == {task}
    gate.set()
    assert await task == "ok"


async def test_scope_closed_during_admission_cancels_the_new_task(make_work, eager_tasks):
    work = make_work(application_limit=2)
    owner = work.open_owner()

    async def closes_its_own_owner() -> None:
        owner.close()  # e.g. the socket went away while this request was being admitted
        await asyncio.Event().wait()

    task = owner.try_start(closes_its_own_owner)
    assert isinstance(task, asyncio.Task)
    await within(asyncio.wait([task]))
    await flush_callbacks()
    assert task.cancelled() and work.active_count == 0

    other = work.open_owner()

    def factory_begins_shutdown() -> Coroutine[Any, Any, Any]:
        work.begin_shutdown()
        return blocked(asyncio.Event())

    late = other.try_start(factory_begins_shutdown)
    assert isinstance(late, asyncio.Task)
    await within(asyncio.wait([late]))
    await flush_callbacks()
    assert late.cancelled() and work.active_count == 0


# --------------------------------------------------------------------------- isolation (acceptance 4)


async def test_application_instances_share_nothing(make_work):
    one, two = make_work(application_limit=1), make_work(application_limit=1)
    gate = asyncio.Event()
    a1 = one.open_owner().try_start(lambda: blocked(gate))
    assert isinstance(a1, asyncio.Task)
    assert one.open_owner().try_start(never_call) is RejectReason.APPLICATION_BUSY
    b1 = two.open_owner().try_start(lambda: blocked(gate))
    assert isinstance(b1, asyncio.Task)

    await one.shutdown(timeout=5)
    assert a1.cancelled() and not b1.done() and not two.closing
    assert two.open_owner().owner_id == 2  # its own sequence
    gate.set()
    assert await b1 == "done"


def test_module_imports_only_the_standard_library():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "no relative imports"
            roots.add((node.module or "").split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"__future__"}, roots


def test_loading_the_module_alone_has_no_side_effects():
    """Load the file by path in a fresh, isolated interpreter (no rest_api package __init__)."""
    probe = r"""
import importlib.util, json, logging, sys, threading
modules, loggers, threads = set(sys.modules), set(logging.root.manager.loggerDict), threading.active_count()
spec = importlib.util.spec_from_file_location("ws_request_work_probe", sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
print(json.dumps({
    "origin": module.__file__,
    "modules": sorted(set(sys.modules) - modules - {spec.name}),
    "loggers": sorted(set(logging.root.manager.loggerDict) - loggers),
    "threads": threading.active_count() - threads,
    "handlers": len(logging.root.handlers),
}))
"""
    result = subprocess.run([sys.executable, "-I", "-c", probe, str(MODULE_PATH)],
                            capture_output=True, text=True, timeout=60, check=False)
    assert result.returncode == 0, result.stderr
    loaded = json.loads(result.stdout)
    assert Path(loaded["origin"]).resolve() == MODULE_PATH
    roots = {name.split(".")[0] for name in loaded["modules"]}
    assert roots <= set(sys.stdlib_module_names), roots - set(sys.stdlib_module_names)
    assert not {"rest_api", "aiohttp", "orei_matrix", "ucapi", "homeassistant"} & roots
    assert LOGGER_NAME not in loaded["loggers"]
    assert loaded["threads"] == 0 and loaded["handlers"] == 0


def test_imports_resolve_to_this_checkout():
    from rest_api import ws_request_work

    assert Path(ws_request_work.__file__).resolve() == MODULE_PATH
    assert Path(websocket.__file__).resolve() == MODULE_PATH.parent / "websocket.py"


def test_the_existing_websocket_module_does_not_use_the_component_yet():
    """Calibration: this candidate is not wired in; /ws still has its original unbounded path."""
    source = (MODULE_PATH.parent / "websocket.py").read_text(encoding="utf-8")
    assert "ws_request_work" not in source
    assert "_replies.add(task)" in source
    assert isinstance(websocket._replies, set)


async def test_repr_and_diagnostics_carry_no_client_data(make_work):
    work = make_work(application_limit=1, name="ws_get_status")
    owner: WorkOwner = work.open_owner()
    secret_ws = type("Ws", (), {"__repr__": lambda self: "<ws api_key=SECRET>"})()
    task = owner.try_start(lambda: websocket._reply_status(FakeStream(), secret_ws))
    assert isinstance(task, asyncio.Task)
    text = " ".join([repr(work), repr(owner), json.dumps(work.diagnostics())])
    assert "SECRET" not in text and "ws_get_status" in text
    assert (await owner.aclose()).drained and task.cancelled()


# =========================================================================== CORRECTION-01 regressions
#
# Added by WS-C01 (CORRECTION-01, same original author). Everything above is the
# original 44-case suite, unchanged. These cases cover WSR-01 (a cleanup that runs
# while an admission still holds its reservation must not report "drained") and
# WSR-02 (the lifecycle methods respect the bound event loop). Evidence comes
# from test-owned gates (factory entry/return, body entry, release), actual task
# states and cancellation requests, not from the controller's counters alone.


SCOPES = ("owner", "application")
#: A small but non-zero drain timeout.
SMALL = 0.001


def _configured_asyncio_debug(config: pytest.Config) -> bool:
    """pytest-asyncio's own precedence: ``--asyncio-debug``, else the ``asyncio_debug`` ini value."""
    value = config.getoption("asyncio_debug")
    if value is None:
        value = config.getini("asyncio_debug")
    return value if isinstance(value, bool) else value == "true"


@pytest.fixture
async def debug_checked(request) -> asyncio.AbstractEventLoop:
    """The running test loop, whose debug mode must be the configured one (recorded in JUnit).

    (``user_properties`` directly: the ``record_property`` fixture warns under xunit2.)
    """
    loop = asyncio.get_running_loop()
    configured = _configured_asyncio_debug(request.config)
    request.node.user_properties.append(("asyncio_debug_configured", configured))
    request.node.user_properties.append(("asyncio_loop_debug", loop.get_debug()))
    assert loop.get_debug() is configured
    return loop


def _cleanup(work: WsRequestWork, owner: WorkOwner, scope: str) -> Callable[..., Coroutine[Any, Any, DrainReport]]:
    return owner.aclose if scope == "owner" else work.shutdown


def _closed_reason(scope: str) -> RejectReason:
    return RejectReason.OWNER_CLOSED if scope == "owner" else RejectReason.SHUTTING_DOWN


class AdmissionProbe:
    """Test-owned gates around one admitted body.

    ``factory_entered``/``factory_returned`` are set by the test's factory,
    ``body_entered`` and ``task`` by the body itself, and ``release`` lets the
    body finish. A *resistant* body swallows every cancellation until released;
    a cooperative one lets the first cancellation end it.
    """

    def __init__(self) -> None:
        self.factory_entered = False
        self.factory_returned = False
        self.body_entered = False
        self.task: asyncio.Task[Any] | None = None
        self.release = asyncio.Event()
        self.cancel_seen = asyncio.Event()
        self.cancellations = 0
        self.reports: list[DrainReport] = []
        self.snapshots: list[dict[str, Any]] = []

    async def body(self, *, resistant: bool,
                   before: Callable[[], Coroutine[Any, Any, None]] | None = None) -> str:
        self.body_entered = True
        self.task = asyncio.current_task()
        if before is not None:
            await before()
        while not self.release.is_set():
            try:
                await self.release.wait()
            except asyncio.CancelledError:
                self.cancellations += 1
                self.cancel_seen.set()
                if not resistant:
                    raise
                asyncio.current_task().uncancel()
        return "released"


@pytest.fixture
async def probes(make_work) -> AsyncIterator[Callable[[], AdmissionProbe]]:
    """Make probes; teardown releases and awaits every body, even after a failed assertion.

    (Depends on ``make_work`` so this teardown runs before its leak check.)
    """
    made: list[AdmissionProbe] = []

    def make() -> AdmissionProbe:
        made.append(AdmissionProbe())
        return made[-1]

    yield make

    for probe in made:
        probe.release.set()
    tasks = [p.task for p in made if p.task is not None and not p.task.done()]
    if tasks:
        await asyncio.wait_for(asyncio.wait(tasks), GUARD)
    await flush_callbacks()


# --------------------------------------------------------------------------- WSR-01: the four judge shapes


@pytest.mark.parametrize("timeout", [0, SMALL], ids=["timeout0", "small"])
@pytest.mark.parametrize("resistant_body", [True, False], ids=["resistant", "cooperative"])
@pytest.mark.parametrize("scope", SCOPES)
async def test_cleanup_from_an_eager_cleaner_spawned_by_the_factory_is_not_drained(
        make_work, eager_tasks, probes, debug_checked, scope, resistant_body, timeout):
    """Judge shapes 1/3: the factory starts an eager cleaner while the admission holds its reservation."""
    loop = debug_checked
    work = make_work(application_limit=1)
    owner, bystander = work.open_owner(), work.open_owner()
    cleanup = _cleanup(work, owner, scope)
    probe = probes()
    cleaners: list[asyncio.Task[DrainReport]] = []

    def factory() -> Coroutine[Any, Any, str]:
        probe.factory_entered = True
        # Factory-cleaner window: the body coroutine does not exist yet, so there is
        # no task of it anywhere (all_tasks() could not show it); only the reservation is held.
        probe.snapshots.append({"body_entered": probe.body_entered, "active": work.active_count,
                                "tracked": len(work.tasks())})
        cleaners.append(loop.create_task(cleanup(timeout=timeout)))  # eager: runs here
        probe.snapshots.append({"cleaner_done": cleaners[0].done(), "body_entered": probe.body_entered})
        coro = probe.body(resistant=resistant_body)
        probe.factory_returned = True
        return coro

    task = owner.try_start(factory)

    assert isinstance(task, asyncio.Task)
    assert probe.snapshots == [{"body_entered": False, "active": 1, "tracked": 0},
                               {"cleaner_done": True, "body_entered": False}]
    report = cleaners[0].result()
    # The admitted request was unfinished when the cleanup returned: never "drained".
    assert report == DrainReport(requested=0, remaining=1) and not report.drained
    # The body is real and alive; the admission cancelled it after registration.
    assert probe.factory_returned and probe.body_entered and probe.task is task
    assert not task.done() and task.cancelling() == 1
    assert owner.closed and work.tasks() == {task} and owner.tasks() == {task}
    assert work.active_count == 1  # capacity still held
    assert bystander.try_start(never_call) is (
        RejectReason.APPLICATION_BUSY if scope == "owner" else RejectReason.SHUTTING_DOWN)

    if resistant_body:
        await within(probe.cancel_seen.wait())
        # A later drain is truthful too: the task is alive, so it is requested and remaining.
        assert await within(cleanup(timeout=timeout)) == DrainReport(requested=1, remaining=1)
        assert not task.done() and work.active_count == 1
        probe.release.set()
        assert await within(task) == "released"
    else:
        second = await within(cleanup(timeout=GUARD))
        assert second == DrainReport(requested=1, remaining=0) and second.drained
        assert task.cancelled() and probe.cancellations == 1
    await flush_callbacks()
    assert work.active_count == 0
    assert await within(cleanup(timeout=GUARD)) == DrainReport(requested=0, remaining=0)


@pytest.mark.parametrize("timeout", [0, SMALL], ids=["timeout0", "small"])
@pytest.mark.parametrize("resistant_body", [True, False], ids=["resistant", "cooperative"])
@pytest.mark.parametrize("scope", SCOPES)
async def test_cleanup_awaited_in_the_eager_first_step_is_not_drained(
        make_work, eager_tasks, probes, debug_checked, scope, resistant_body, timeout):
    """Judge shapes 2/4: the admitted coroutine's eager first step awaits its own scope's cleanup."""
    work = make_work(application_limit=1)
    owner = work.open_owner()
    cleanup = _cleanup(work, owner, scope)
    probe = probes()
    in_admission = True

    async def clean_first() -> None:
        # The task exists (it is running this step) but is not attached yet.
        probe.snapshots.append({"current_is_body": asyncio.current_task() is probe.task,
                                "tracked": probe.task in work.tasks(), "active": work.active_count})
        probe.reports.append(await cleanup(timeout=timeout))
        probe.snapshots.append({"inside_admission": in_admission})

    def factory() -> Coroutine[Any, Any, str]:
        probe.factory_entered = True
        coro = probe.body(resistant=resistant_body, before=clean_first)
        probe.factory_returned = True
        return coro

    task = owner.try_start(factory)
    in_admission = False

    assert isinstance(task, asyncio.Task) and probe.task is task
    assert probe.snapshots == [{"current_is_body": True, "tracked": False, "active": 1},
                               {"inside_admission": True}]
    # The caller itself was the unfinished admitted work.
    assert probe.reports == [DrainReport(requested=0, remaining=1)]
    assert not probe.reports[0].drained
    assert not task.done() and task.cancelling() == 1 and owner.closed
    assert work.tasks() == {task} and work.active_count == 1

    if resistant_body:
        await within(probe.cancel_seen.wait())
        assert await within(cleanup(timeout=SMALL)) == DrainReport(requested=1, remaining=1)
        probe.release.set()
        assert await within(task) == "released"
    else:
        assert await within(cleanup(timeout=GUARD)) == DrainReport(requested=1, remaining=0)
        assert task.cancelled()
    await flush_callbacks()
    assert work.active_count == 0
    assert (await within(cleanup(timeout=GUARD))).drained


@pytest.mark.parametrize("scope", SCOPES)
async def test_cleanup_inside_an_admission_does_not_wait_for_attached_siblings(
        make_work, eager_tasks, probes, debug_checked, scope):
    """With other work attached, a cleanup inside an admission still returns at once (no self-wait)."""
    loop = debug_checked
    work = make_work(application_limit=2, owner_limit=2)
    owner = work.open_owner()
    cleanup = _cleanup(work, owner, scope)
    sibling, probe = probes(), probes()
    sibling_task = owner.try_start(lambda: sibling.body(resistant=True))
    assert isinstance(sibling_task, asyncio.Task) and not sibling_task.done()
    in_admission = True
    loop_ran: list[str] = []

    async def clean_first() -> None:
        loop.call_soon(loop_ran.append, "ran")  # runs only if the cleanup suspends
        probe.reports.append(await cleanup(timeout=GUARD))
        probe.snapshots.append({"inside_admission": in_admission, "loop_ran": bool(loop_ran)})

    task = owner.try_start(lambda: probe.body(resistant=True, before=clean_first))
    in_admission = False

    assert isinstance(task, asyncio.Task)
    # Returned without suspending: the sibling (requested) plus the caller's own reservation.
    assert probe.reports == [DrainReport(requested=1, remaining=2)]
    assert probe.snapshots == [{"inside_admission": True, "loop_ran": False}]
    assert sibling_task.cancelling() == 1 and task.cancelling() == 1
    await within(sibling.cancel_seen.wait())
    await within(probe.cancel_seen.wait())
    assert await within(cleanup(timeout=0)) == DrainReport(requested=2, remaining=2)

    sibling.release.set()
    probe.release.set()
    assert await within(asyncio.gather(sibling_task, task)) == ["released", "released"]
    await flush_callbacks()
    assert work.active_count == 0


@pytest.mark.parametrize("scope", SCOPES)
async def test_a_task_cleaning_its_own_scope_returns_at_once_and_counts_itself(
        make_work, probes, debug_checked, scope):
    """Self dependency on an attached task: no wait on itself, the caller is in ``remaining``."""
    loop = debug_checked
    work = make_work(application_limit=3, owner_limit=2)
    owner, other = work.open_owner(), work.open_owner()
    cleanup = _cleanup(work, owner, scope)
    sibling, bystander = probes(), probes()
    sibling_task = owner.try_start(lambda: sibling.body(resistant=False))
    other_task = other.try_start(lambda: bystander.body(resistant=False))
    assert isinstance(sibling_task, asyncio.Task) and isinstance(other_task, asyncio.Task)
    go = asyncio.Event()
    seen: list[Any] = []

    async def cleans_its_own_scope() -> None:
        await go.wait()
        loop_ran: list[str] = []
        loop.call_soon(loop_ran.append, "ran")
        report = await cleanup(timeout=GUARD)
        seen.append((report, bool(loop_ran), asyncio.current_task().cancelling()))
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            seen.append("cancelled")
            raise

    me = owner.try_start(cleans_its_own_scope)
    assert isinstance(me, asyncio.Task)
    await flush_callbacks()
    assert sibling_task.cancelling() == 0 and not owner.closed  # nothing closed before ``go``
    go.set()
    await within(asyncio.wait([me]))

    expected = DrainReport(requested=2, remaining=2) if scope == "owner" else DrainReport(requested=3, remaining=3)
    assert seen == [(expected, False, 1), "cancelled"] and me.cancelled()
    await within(asyncio.wait([sibling_task]))
    assert sibling_task.cancelled()
    if scope == "owner":
        assert not other_task.done() and other_task.cancelling() == 0  # other owner untouched
        bystander.release.set()
        assert await within(other_task) == "released"
    else:
        await within(asyncio.wait([other_task]))
        assert other_task.cancelled()
    await flush_callbacks()
    assert work.active_count == 0


@pytest.mark.parametrize("scope", SCOPES)
async def test_nested_reentrant_admissions_are_each_counted_exactly(make_work, probes, debug_checked, scope):
    """Several nested reservations at once, with failure/creation-failure/completion boundaries between them."""
    loop = debug_checked
    work = make_work(application_limit=6, owner_limit=4)
    owner, other = work.open_owner(), work.open_owner()
    cleanup = _cleanup(work, owner, scope)
    outer, middle, inner, unrelated = probes(), probes(), probes(), probes()
    refused_coros: list[Coroutine[Any, Any, Any]] = []
    log: list[tuple[str, int, int, int]] = []
    cleaners: list[asyncio.Task[DrainReport]] = []
    made: dict[str, asyncio.Task[Any]] = {}

    async def refused() -> None:
        raise AssertionError("a coroutine whose task was refused ran")

    def selective_eager_factory(loop_: asyncio.AbstractEventLoop, coro: Any, **kwargs: Any) -> asyncio.Task[Any]:
        if getattr(coro, "__name__", "") == "refused":
            refused_coros.append(coro)
            raise RuntimeError("task creation refused")
        return asyncio.eager_task_factory(loop_, coro, **kwargs)

    def counts(label: str) -> None:
        log.append((label, owner.active_count, work.active_count, len(owner.tasks())))

    def explode() -> Coroutine[Any, Any, Any]:
        raise LookupError("nested factory failed")

    def inner_factory() -> Coroutine[Any, Any, str]:
        counts("inner-entered")
        cleaners.append(loop.create_task(cleanup(timeout=SMALL)))  # eager: completes here
        counts("inner-after-cleanup")
        return inner.body(resistant=True)

    def middle_factory() -> Coroutine[Any, Any, str]:
        counts("middle-entered")
        with pytest.raises(LookupError):
            owner.try_start(explode)
        counts("middle-after-factory-failure")
        with pytest.raises(RuntimeError, match="task creation refused"):
            owner.try_start(refused)
        counts("middle-after-creation-failure")
        made["done"] = owner.try_start(lambda: returns("eager-done"))
        assert made["done"].done()  # completed inside create_task; its release callback has not run
        counts("middle-after-eager-completion")
        made["inner"] = owner.try_start(inner_factory)
        counts("middle-after-inner")
        assert owner.try_start(never_call) is _closed_reason(scope)  # closed now: factory uncalled
        return middle.body(resistant=True)

    def outer_factory() -> Coroutine[Any, Any, str]:
        counts("outer-entered")
        made["middle"] = owner.try_start(middle_factory)
        counts("outer-after-middle")
        return outer.body(resistant=True)

    previous = loop.get_task_factory()
    loop.set_task_factory(selective_eager_factory)
    try:
        other_task = other.try_start(lambda: unrelated.body(resistant=True))
        assert isinstance(other_task, asyncio.Task)
        made["outer"] = owner.try_start(outer_factory)
        counts("after-outer")
    finally:
        loop.set_task_factory(previous)

    # (owner.active_count, work.active_count, attached owner tasks) at every boundary.
    assert log == [
        ("outer-entered", 1, 2, 0),
        ("middle-entered", 2, 3, 0),
        ("middle-after-factory-failure", 2, 3, 0),
        ("middle-after-creation-failure", 2, 3, 0),
        ("middle-after-eager-completion", 3, 4, 1),
        ("inner-entered", 4, 5, 1),
        ("inner-after-cleanup", 4, 5, 1),
        ("middle-after-inner", 4, 5, 2),
        ("outer-after-middle", 4, 5, 3),
        ("after-outer", 4, 5, 4),
    ]
    assert len(refused_coros) == 1 and inspect.getcoroutinestate(refused_coros[0]) == inspect.CORO_CLOSED
    (cleaner,) = cleaners
    # Three reservations were open (outer, middle, inner); the completed task is not unfinished
    # and is not "requested" (cancel() of a done task does nothing). Shutdown also requested the
    # other owner's live task and counts it.
    first = cleaner.result()
    assert first == (DrainReport(requested=0, remaining=3) if scope == "owner"
                     else DrainReport(requested=1, remaining=4))
    live = [made["outer"], made["middle"], made["inner"]]
    assert all(not t.done() and t.cancelling() == 1 for t in live)
    assert made["done"].result() == "eager-done"
    assert other_task.cancelling() == (0 if scope == "owner" else 1)

    await flush_callbacks()
    assert owner.active_count == 3 and work.active_count == 4
    work._release(made["done"])  # a stale, duplicated done callback frees and counts nothing
    assert owner.active_count == 3 and work.active_count == 4
    counters = work.diagnostics()
    assert (counters["admitted"], counters["completed"]) == (5, 1)
    assert counters[f"rejected_{_closed_reason(scope).value}"] == 1

    second = await within(cleanup(timeout=SMALL))
    assert second == (DrainReport(requested=3, remaining=3) if scope == "owner"
                      else DrainReport(requested=4, remaining=4))
    for probe in (outer, middle, inner, unrelated):
        probe.release.set()
    assert await within(asyncio.gather(*live, other_task)) == ["released"] * 4
    await flush_callbacks()
    assert work.active_count == 0
    assert await within(cleanup(timeout=GUARD)) == DrainReport(requested=0, remaining=0)


async def test_cleanup_of_another_owner_inside_an_admission_still_waits_for_it(
        make_work, eager_tasks, probes, debug_checked):
    """Other-owner progress: only this scope's own admissions make a cleanup return early."""
    loop = debug_checked
    work = make_work(application_limit=3)
    a, b = work.open_owner(), work.open_owner()
    a_probe, b_probe = probes(), probes()
    a_task = a.try_start(lambda: a_probe.body(resistant=False))
    assert isinstance(a_task, asyncio.Task)
    cleaners: list[asyncio.Task[DrainReport]] = []

    def b_factory() -> Coroutine[Any, Any, str]:
        cleaners.append(loop.create_task(a.aclose(timeout=GUARD)))  # eager; suspends in its wait
        b_probe.snapshots.append({"cleaner_done": cleaners[0].done()})
        return b_probe.body(resistant=False)

    b_task = b.try_start(b_factory)

    assert isinstance(b_task, asyncio.Task)
    assert b_probe.snapshots == [{"cleaner_done": False}]
    report = await within(cleaners[0])
    assert report == DrainReport(requested=1, remaining=0) and report.drained
    assert a_task.cancelled() and a.closed
    assert not b.closed and not b_task.done() and b_task.cancelling() == 0
    b_probe.release.set()
    assert await within(b_task) == "released"
    await flush_callbacks()
    assert work.active_count == 0


@pytest.mark.parametrize("scope", SCOPES)
async def test_cancelling_a_cleanup_waiter_keeps_resistant_work_tracked(make_work, probes, debug_checked, scope):
    """Waiter cancellation at both scopes: it propagates, the fence stays closed, nothing is forgotten."""
    loop = debug_checked
    work = make_work(application_limit=1)
    owner, bystander = work.open_owner(), work.open_owner()
    cleanup = _cleanup(work, owner, scope)
    probe = probes()
    task = owner.try_start(lambda: probe.body(resistant=True))
    assert isinstance(task, asyncio.Task)
    await flush_callbacks()
    assert probe.body_entered

    waiter = loop.create_task(cleanup(timeout=GUARD * 3))
    await within(probe.cancel_seen.wait())  # the waiter has requested cancellation and is waiting
    assert not waiter.done()
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await within(waiter)

    assert owner.closed and (work.closing is (scope == "application"))
    assert work.tasks() == {task} and not task.done() and work.active_count == 1
    assert owner.try_start(never_call) is _closed_reason(scope)
    assert bystander.try_start(never_call) is (
        RejectReason.APPLICATION_BUSY if scope == "owner" else RejectReason.SHUTTING_DOWN)
    assert await within(cleanup(timeout=0)) == DrainReport(requested=1, remaining=1)
    probe.release.set()
    assert await within(task) == "released"
    await flush_callbacks()
    assert await within(cleanup(timeout=GUARD)) == DrainReport(requested=0, remaining=0)


# --------------------------------------------------------------------------- WSR-02: lifecycle event-loop boundary


def test_bound_lifecycle_refuses_a_foreign_or_missing_loop_before_changing_state():
    work = WsRequestWork(application_limit=2)
    owner = work.open_owner()
    home = asyncio.new_event_loop()
    home.set_debug(True)
    gate = asyncio.Event()
    task: asyncio.Task[Any] | None = None

    async def admit() -> asyncio.Task[Any]:
        assert asyncio.get_running_loop().get_debug()
        started = owner.try_start(lambda: blocked(gate))
        assert isinstance(started, asyncio.Task)
        return started

    def unchanged() -> None:
        assert task is not None
        assert not owner.closed and not work.closing
        assert not task.done() and task.cancelling() == 0 and work.active_count == 1

    try:
        task = home.run_until_complete(admit())

        # No running loop at all (the bound loop exists but is not running).
        for sync_call in (owner.close, work.begin_shutdown):
            with pytest.raises(RuntimeError, match="no event loop is running"):
                sync_call()
            unchanged()

        async def foreign() -> None:
            assert asyncio.get_running_loop().get_debug()
            for sync_call in (owner.close, work.begin_shutdown):
                with pytest.raises(RuntimeError, match="different event loop"):
                    sync_call()
                unchanged()
            for async_call in (owner.aclose, work.shutdown):
                with pytest.raises(ValueError):  # timeout validation still comes first
                    await async_call(timeout=-1)
                with pytest.raises(RuntimeError, match="different event loop"):
                    await async_call(timeout=0)
                unchanged()
            with pytest.raises(RuntimeError, match="different event loop"):
                owner.try_start(never_call)
            unchanged()

        asyncio.run(foreign(), debug=True)

        async def stop_at_home() -> DrainReport:
            return await work.shutdown(timeout=GUARD)

        assert home.run_until_complete(stop_at_home()) == DrainReport(requested=1, remaining=0)
        assert task.cancelled() and work.active_count == 0
    finally:
        if task is not None and not task.done():
            task.cancel()
            home.run_until_complete(asyncio.wait([task], timeout=GUARD))
        home.close()


def test_unbound_owner_close_closes_the_fence_without_binding():
    work = WsRequestWork(application_limit=2)
    closed_without_loop = work.open_owner()
    closed_without_loop.close()  # no running loop, never admitted: allowed
    assert closed_without_loop.closed and not work.closing

    async def on_loop_a() -> WorkOwner:
        assert asyncio.get_running_loop().get_debug()
        closed_in_loop = work.open_owner()
        closed_in_loop.close()  # unbound, inside loop A: must not bind to A
        report = await work.open_owner().aclose(timeout=0)  # truthful: nothing was admitted
        assert report == DrainReport(requested=0, remaining=0)
        assert await work.open_owner().aclose(timeout=GUARD) == DrainReport(requested=0, remaining=0)
        return closed_in_loop

    closed_in_loop = asyncio.run(on_loop_a(), debug=True)
    assert closed_in_loop.closed

    async def on_loop_b() -> None:
        assert asyncio.get_running_loop().get_debug()
        # Not bound to loop A: admission works here (and binds this loop).
        assert closed_without_loop.try_start(never_call) is RejectReason.OWNER_CLOSED
        assert closed_in_loop.try_start(never_call) is RejectReason.OWNER_CLOSED
        task = work.open_owner().try_start(lambda: returns("loop b"))
        assert isinstance(task, asyncio.Task)
        assert await task == "loop b"
        await flush_callbacks()

    asyncio.run(on_loop_b(), debug=True)
    assert work.active_count == 0


def test_unbound_begin_shutdown_closes_admission_without_binding():
    without_loop = WsRequestWork(application_limit=1)
    without_loop.begin_shutdown()  # no running loop, never admitted: allowed
    assert without_loop.closing and without_loop.open_owner().closed
    in_loop = WsRequestWork(application_limit=1)

    async def on_loop_a() -> None:
        assert asyncio.get_running_loop().get_debug()
        in_loop.begin_shutdown()  # unbound, inside loop A: must not bind to A
        assert await in_loop.shutdown(timeout=0) == DrainReport(requested=0, remaining=0)
        assert await in_loop.shutdown(timeout=GUARD) == DrainReport(requested=0, remaining=0)

    asyncio.run(on_loop_a(), debug=True)

    async def on_loop_b() -> None:
        assert asyncio.get_running_loop().get_debug()
        # A refusal, not "bound to a different event loop".
        assert without_loop.open_owner().try_start(never_call) is RejectReason.SHUTTING_DOWN
        assert in_loop.open_owner().try_start(never_call) is RejectReason.SHUTTING_DOWN

    asyncio.run(on_loop_b(), debug=True)


def test_a_rejected_admission_binds_the_loop_too():
    """Prebinding: the first try_start binds even when it is refused; lifecycle then follows that loop."""
    work = WsRequestWork(application_limit=1)
    owner = work.open_owner()
    owner.close()

    async def on_loop_a() -> None:
        assert owner.try_start(never_call) is RejectReason.OWNER_CLOSED

    asyncio.run(on_loop_a(), debug=True)

    async def on_loop_b() -> None:
        with pytest.raises(RuntimeError, match="different event loop"):
            work.begin_shutdown()
        with pytest.raises(RuntimeError, match="different event loop"):
            await work.shutdown(timeout=0)
        assert not work.closing

    asyncio.run(on_loop_b(), debug=True)
    with pytest.raises(RuntimeError, match="no event loop is running"):
        work.begin_shutdown()
    assert not work.closing
