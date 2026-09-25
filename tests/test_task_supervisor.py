"""BE-01: the background task supervisor.

A coroutine that returns is finished (never restarted); one that raises is
restarted after a backoff delay; cancelling always stops the task.
"""

import asyncio

import pytest

import _task_supervisor
from _task_supervisor import create_supervised_task


@pytest.fixture
def fast_backoff(monkeypatch):
    monkeypatch.setattr(_task_supervisor, "INITIAL_RESTART_DELAY", 0.05)
    monkeypatch.setattr(_task_supervisor, "MAX_RESTART_DELAY", 0.2)


async def test_returning_coroutine_is_not_restarted():
    calls = 0

    async def job():
        nonlocal calls
        calls += 1

    task = create_supervised_task(job, "returns")
    await asyncio.wait_for(task, 1)
    await asyncio.sleep(0.05)
    assert calls == 1
    assert task.done() and not task.cancelled() and task.exception() is None


async def test_cancel_stops_supervised_task():
    started = asyncio.Event()

    async def job():
        started.set()
        await asyncio.sleep(3600)

    task = create_supervised_task(job, "long")
    await started.wait()
    task.cancel()
    done, _ = await asyncio.wait([task], timeout=1)
    assert task in done and task.cancelled()


async def test_cancel_during_restart_delay_stops_task(fast_backoff, monkeypatch):
    monkeypatch.setattr(_task_supervisor, "INITIAL_RESTART_DELAY", 10.0)
    crashed = asyncio.Event()

    async def job():
        crashed.set()
        raise RuntimeError("boom")

    task = create_supervised_task(job, "crash-then-cancel")
    await crashed.wait()
    await asyncio.sleep(0)  # now sleeping in the restart delay
    task.cancel()
    done, _ = await asyncio.wait([task], timeout=1)
    assert task in done and task.cancelled()


async def test_crash_restarts_after_delay(fast_backoff):
    loop = asyncio.get_running_loop()
    times: list[float] = []
    errors: list[BaseException] = []

    async def job():
        times.append(loop.time())
        if len(times) < 3:
            raise RuntimeError("boom")

    task = create_supervised_task(job, "crashy", on_error=errors.append)
    await asyncio.wait_for(task, 2)
    assert len(times) == 3
    assert [str(e) for e in errors] == ["boom", "boom"]
    # First restart waits INITIAL_RESTART_DELAY, the second one twice that.
    assert times[1] - times[0] >= 0.03  # loose: Windows clock resolution is ~16 ms
    assert times[2] - times[1] >= 0.07


async def test_backoff_is_capped(fast_backoff, monkeypatch):
    delays: list[float] = []
    real_sleep = asyncio.sleep

    async def fake_sleep(delay, *args, **kwargs):
        delays.append(delay)
        await real_sleep(0)

    count = 0

    async def job():
        nonlocal count
        count += 1
        if count < 7:
            raise RuntimeError("boom")

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    await asyncio.wait_for(create_supervised_task(job, "capped"), 2)
    assert delays == [0.05, 0.1, 0.2, 0.2, 0.2, 0.2]


async def test_on_error_failure_does_not_kill_supervisor(fast_backoff):
    count = 0

    async def job():
        nonlocal count
        count += 1
        if count == 1:
            raise RuntimeError("boom")

    def bad_callback(_err):
        raise ValueError("callback broken")

    await asyncio.wait_for(create_supervised_task(job, "cb", on_error=bad_callback), 1)
    assert count == 2
