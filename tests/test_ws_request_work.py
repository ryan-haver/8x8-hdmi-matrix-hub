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
