"""BE-18: single-instance lock backed by an OS advisory lock."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from _process_lock import ProcessLock, ProcessLockError, read_holder_pid

SRC = str(Path(__file__).resolve().parent.parent / "src")

# On Windows a venv's python.exe is a launcher that runs the base interpreter
# as a *child*; terminate() would kill only the launcher. The children below
# need nothing but the stdlib and src/, so run the real interpreter directly.
PYTHON = getattr(sys, "_base_executable", sys.executable) if sys.platform == "win32" else sys.executable

# Child that tries to take the lock once and reports the outcome.
_TRY_ACQUIRE = textwrap.dedent(
    """
    import sys
    sys.path.insert(0, sys.argv[1])
    from _process_lock import ProcessLock, ProcessLockError
    try:
        ProcessLock(sys.argv[2]).acquire()
    except ProcessLockError as exc:
        print(f"HELD {exc.holder_pid} :: {exc}")
        sys.exit(3)
    print("ACQUIRED")
    """
)

# Child that takes the lock and then blocks until killed.
_HOLD_FOREVER = textwrap.dedent(
    """
    import os, sys, time
    sys.path.insert(0, sys.argv[1])
    from _process_lock import ProcessLock
    lock = ProcessLock(sys.argv[2])
    lock.acquire()
    print("LOCKED", os.getpid(), flush=True)
    while True:
        time.sleep(1)
    """
)


def _try_in_subprocess(lock_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, "-c", _TRY_ACQUIRE, SRC, str(lock_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture
def lock_path(tmp_path: Path) -> Path:
    return tmp_path / "driver.lock"


def test_acquire_writes_pid_and_release_removes_file(lock_path: Path):
    lock = ProcessLock(lock_path)
    lock.acquire()
    try:
        assert lock.held
        assert read_holder_pid(lock_path) == os.getpid()
    finally:
        lock.release()
    assert not lock.held
    assert not lock_path.exists()
    lock.release()  # idempotent


def test_second_handle_in_same_process_is_refused(lock_path: Path):
    with ProcessLock(lock_path):
        with pytest.raises(ProcessLockError) as info:
            ProcessLock(lock_path).acquire()
    assert info.value.holder_pid == os.getpid()
    assert "already holds it" in str(info.value)


def test_second_process_is_refused_while_first_holds(lock_path: Path):
    with ProcessLock(lock_path):
        result = _try_in_subprocess(lock_path)
        assert result.returncode == 3, result.stderr
        assert result.stdout.startswith(f"HELD {os.getpid()} ")
        assert "another instance is already running" in result.stdout
        # The refused attempt must not have clobbered the holder's PID.
        assert read_holder_pid(lock_path) == os.getpid()

    result = _try_in_subprocess(lock_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ACQUIRED" in result.stdout


def test_lock_is_released_when_holder_process_is_killed(lock_path: Path):
    holder = subprocess.Popen(
        [PYTHON, "-c", _HOLD_FOREVER, SRC, str(lock_path)],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None
        status, holder_pid = holder.stdout.readline().split()
        assert status == "LOCKED"
        assert int(holder_pid) == holder.pid

        with pytest.raises(ProcessLockError) as info:
            ProcessLock(lock_path).acquire()
        assert info.value.holder_pid == int(holder_pid)
    finally:
        holder.terminate()
        holder.wait(timeout=30)
        if holder.stdout is not None:
            holder.stdout.close()

    # The killed holder never cleaned up: its lock file (and PID) remain,
    # but the OS dropped the lock with the process, so it is acquirable.
    assert lock_path.exists()
    assert read_holder_pid(lock_path) == int(holder_pid)
    lock = ProcessLock(lock_path)
    # Windows releases a dead process's locks asynchronously, shortly after
    # the process object is signalled; allow a brief grace period.
    deadline = time.monotonic() + 5
    while True:
        try:
            lock.acquire()
            break
        except ProcessLockError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.05)
    try:
        assert read_holder_pid(lock_path) == os.getpid()
    finally:
        lock.release()


def test_leftover_file_with_unrelated_pid_does_not_block(lock_path: Path):
    """No PID-liveness logic: a file without a live OS lock is simply free."""
    lock_path.write_text(f"{os.getpid()}\n")  # even our own PID
    with ProcessLock(lock_path):
        assert read_holder_pid(lock_path) == os.getpid()


def test_garbage_lock_file_contents_are_tolerated(lock_path: Path):
    lock_path.write_text("not-a-pid")
    assert read_holder_pid(lock_path) is None
    with ProcessLock(lock_path):
        assert read_holder_pid(lock_path) == os.getpid()


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX unlink-while-open race")
def test_orphaned_inode_is_detected_and_retried(lock_path: Path, monkeypatch):
    """If the file is unlinked between open() and flock(), acquire retries on a fresh file."""
    import _process_lock

    real_try_lock = _process_lock._try_lock
    calls = {"n": 0}

    def try_lock_after_unlink(f):
        calls["n"] += 1
        if calls["n"] == 1:
            os.unlink(lock_path)  # simulate the previous holder's release()
        return real_try_lock(f)

    monkeypatch.setattr(_process_lock, "_try_lock", try_lock_after_unlink)
    with ProcessLock(lock_path):
        assert calls["n"] == 2
        assert read_holder_pid(lock_path) == os.getpid()
