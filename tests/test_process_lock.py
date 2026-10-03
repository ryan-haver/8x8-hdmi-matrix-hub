"""BE-18: single-instance lock backed by an OS advisory lock."""

from __future__ import annotations

import os
import queue
import stat
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path

import pytest

from _process_lock import ProcessLock, ProcessLockError, read_holder_pid

SRC = str(Path(__file__).resolve().parent.parent / "src")

# Bound on starting a child (CreateProcess / fork+exec) and on each wait for it.
SPAWN_TIMEOUT = 30.0
CHILD_TIMEOUT = 30.0


def _is_app_execution_alias(path: Path) -> bool:
    """True for a Windows app-execution alias (e.g. the Microsoft Store python.exe in WindowsApps)."""
    try:
        tag = os.stat(path, follow_symlinks=False).st_reparse_tag  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        return False
    return tag == getattr(stat, "IO_REPARSE_TAG_APPEXECLINK", 0x8000001B)


def _child_interpreter() -> str | None:
    """The interpreter to start the lock children with, or None if none is safe to start.

    The children need nothing but the stdlib and src/. POSIX: sys.executable.
    Windows (TST-11): not a venv's python.exe, which is a launcher that runs the
    base interpreter as a *child* (terminate() would kill only the launcher),
    and not an app-execution alias: with the Microsoft Store Python,
    sys._base_executable is the WindowsApps alias, and CreateProcess on it can
    block inside Popen, where no subprocess timeout applies, hanging the whole
    pytest session. The real python.exe lives in sys.base_prefix.
    """
    if sys.platform != "win32":
        return sys.executable
    for candidate in (
        Path(sys.base_prefix) / "python.exe",
        Path(getattr(sys, "_base_executable", sys.executable)),
    ):
        if candidate.is_file() and not _is_app_execution_alias(candidate):
            return str(candidate)
    return None


PYTHON = _child_interpreter()
needs_child_python = pytest.mark.skipif(
    PYTHON is None,
    reason="no interpreter that can be started safely: only a venv launcher or an app-execution "
    "alias was found (Microsoft Store Python); starting those can hang the session (TST-11)",
)


def _spawn(args: list[str], **kwargs) -> subprocess.Popen:
    """subprocess.Popen whose *start* is bounded too.

    subprocess timeouts only apply once the child exists; a CreateProcess that
    blocks (TST-11) would hang the session. Popen runs in a daemon thread; if it
    has not returned within SPAWN_TIMEOUT the test fails, the thread is
    abandoned, and a child it starts later is killed at once.
    """
    box: dict = {}
    given_up = threading.Event()

    def start() -> None:
        try:
            proc = subprocess.Popen(args, **kwargs)
        except BaseException as exc:  # noqa: BLE001 - re-raised in the caller
            box["exc"] = exc
            return
        box["proc"] = proc
        if given_up.is_set():
            proc.kill()
            proc.wait()

    thread = threading.Thread(target=start, name="spawn-child", daemon=True)
    thread.start()
    thread.join(SPAWN_TIMEOUT)
    if thread.is_alive():
        given_up.set()
        if "proc" in box:  # started between join() timing out and given_up being set
            box["proc"].kill()
        pytest.fail(
            f"starting {args[0]} did not return within {SPAWN_TIMEOUT:.0f}s "
            "(process creation blocked, TST-11); abandoned so the session goes on"
        )
    if "exc" in box:
        raise box["exc"]
    return box["proc"]


def _readline(proc: subprocess.Popen, timeout: float) -> str:
    """One line of the child's stdout, or fail after `timeout` (readline() itself never times out)."""
    lines: queue.Queue[str] = queue.Queue()
    assert proc.stdout is not None
    stdout = proc.stdout
    threading.Thread(target=lambda: lines.put(stdout.readline()), daemon=True).start()
    try:
        return lines.get(timeout=timeout)
    except queue.Empty:
        proc.kill()
        pytest.fail(f"child wrote nothing within {timeout:.0f}s")


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
    assert PYTHON is not None
    args = [PYTHON, "-c", _TRY_ACQUIRE, SRC, str(lock_path)]
    proc = _spawn(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        stdout, stderr = proc.communicate(timeout=CHILD_TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        pytest.fail(f"lock child did not finish within {CHILD_TIMEOUT:.0f}s")
    return subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)


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


@needs_child_python
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


@needs_child_python
def test_lock_is_released_when_holder_process_is_killed(lock_path: Path):
    assert PYTHON is not None
    holder = _spawn([PYTHON, "-c", _HOLD_FOREVER, SRC, str(lock_path)], stdout=subprocess.PIPE, text=True)
    try:
        status, holder_pid = _readline(holder, CHILD_TIMEOUT).split()
        assert status == "LOCKED"
        assert int(holder_pid) == holder.pid

        with pytest.raises(ProcessLockError) as info:
            ProcessLock(lock_path).acquire()
        assert info.value.holder_pid == int(holder_pid)
    finally:
        holder.terminate()
        holder.wait(timeout=CHILD_TIMEOUT)
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


def test_blocked_process_creation_fails_instead_of_hanging(monkeypatch):
    """TST-11: if process creation itself blocks, the test fails within SPAWN_TIMEOUT; nothing hangs."""
    release = threading.Event()
    created: list[str] = []

    def blocking_popen(args, **kwargs):  # a CreateProcess that does not return
        release.wait(60)
        created.append(args[0])
        raise OSError("released")

    monkeypatch.setattr(subprocess, "Popen", blocking_popen)
    monkeypatch.setattr(sys.modules[__name__], "SPAWN_TIMEOUT", 0.5)
    started = time.monotonic()
    with pytest.raises(pytest.fail.Exception, match="did not return within"):
        _spawn(["python-that-never-starts"])
    assert time.monotonic() - started < 5
    assert created == []  # it really was still blocked when the test gave up
    release.set()
