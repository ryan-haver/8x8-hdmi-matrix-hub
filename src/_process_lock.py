"""
Single-instance process lock backed by an OS advisory lock (BE-18).

The lock is an OS lock on an open handle (``fcntl.flock`` on POSIX,
``msvcrt.locking`` on Windows) that is held for as long as the handle stays
open. The kernel drops it when the process exits for *any* reason — clean
shutdown, crash, ``kill -9`` — so there is no such thing as a stale lock and
no PID-liveness guessing (which PID reuse makes unreliable).

The holder's PID is still written into the file, purely so an operator (and
the error message) can see who holds it.

Usage::

    lock = ProcessLock(path)
    lock.acquire()          # raises ProcessLockError if another process holds it
    ...
    lock.release()          # optional; process exit releases it too
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import IO

if sys.platform == "win32":
    import msvcrt

    # Lock one byte well past the PID text. Windows byte-range locks are
    # mandatory, so locking byte 0 would stop other processes from reading
    # the holder PID; locking beyond EOF is allowed.
    _WIN_LOCK_OFFSET = 1 << 20

    def _try_lock(f: IO[bytes]) -> bool:
        f.seek(_WIN_LOCK_OFFSET)
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return False
        finally:
            f.seek(0)
        return True

    def _unlock(f: IO[bytes]) -> None:
        f.seek(_WIN_LOCK_OFFSET)
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            f.seek(0)

else:
    import fcntl

    def _try_lock(f: IO[bytes]) -> bool:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        return True

    def _unlock(f: IO[bytes]) -> None:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


class ProcessLockError(RuntimeError):
    """Raised when another process (or another handle in this one) holds the lock."""

    def __init__(self, path: Path, holder_pid: int | None) -> None:
        self.path = path
        self.holder_pid = holder_pid
        if holder_pid == os.getpid():
            who = f"this process (PID {holder_pid}) already holds it through another handle"
        elif holder_pid is not None:
            who = f"another instance is already running (PID {holder_pid})"
        else:
            who = "another instance is already running"
        super().__init__(
            f"Cannot acquire single-instance lock {path}: {who}. "
            "Stop that instance first; the lock is released automatically when it exits."
        )


def read_holder_pid(path: Path | str) -> int | None:
    """Return the PID recorded in a lock file (diagnostics only), or None."""
    try:
        with open(path, "rb") as f:
            return int(f.read(64).decode("ascii", "replace").strip())
    except (OSError, ValueError):
        return None


class ProcessLock:
    """An exclusive, process-lifetime OS lock on ``path``."""

    # Bounded retries for the POSIX unlink race (see acquire()).
    _MAX_ATTEMPTS = 10

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._file: IO[bytes] | None = None

    @property
    def held(self) -> bool:
        return self._file is not None

    def acquire(self) -> None:
        """Acquire the lock without blocking.

        :raises ProcessLockError: if the lock is held elsewhere.
        :raises OSError: if the lock file cannot be created/opened.
        """
        if self._file is not None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(self._MAX_ATTEMPTS):
            # No O_TRUNC: truncating before we own the lock would wipe the
            # current holder's PID.
            fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
            f = os.fdopen(fd, "r+b", buffering=0)
            try:
                if not _try_lock(f):
                    raise ProcessLockError(self.path, read_holder_pid(self.path))
                if not self._still_linked(f):
                    # POSIX: the previous holder unlinked the file between our
                    # open() and flock(); we locked an orphaned inode. Retry.
                    _unlock(f)
                    f.close()
                    continue
                f.truncate(0)
                f.write(f"{os.getpid()}\n".encode("ascii"))
                f.flush()
            except BaseException:
                if not f.closed:
                    f.close()
                raise
            self._file = f
            return
        raise OSError(f"Lock file {self.path} kept being replaced while acquiring it")

    def _still_linked(self, f: IO[bytes]) -> bool:
        if sys.platform == "win32":
            return True  # an open file cannot be deleted on Windows
        try:
            st_path = os.stat(self.path)
        except FileNotFoundError:
            return False
        st_fd = os.fstat(f.fileno())
        return (st_path.st_dev, st_path.st_ino) == (st_fd.st_dev, st_fd.st_ino)

    def release(self) -> None:
        """Release the lock and remove the lock file. Idempotent."""
        f, self._file = self._file, None
        if f is None:
            return
        try:
            if sys.platform != "win32":
                # Unlink while still holding the lock so a waiter that locks
                # the old inode afterwards notices (see _still_linked).
                try:
                    self.path.unlink()
                except FileNotFoundError:
                    pass
            try:
                _unlock(f)
            except OSError:
                pass
        finally:
            f.close()
        if sys.platform == "win32":
            try:
                self.path.unlink()
            except (FileNotFoundError, PermissionError):
                # PermissionError: another process has it open (and may be
                # about to lock it) — leave it for them.
                pass

    def __enter__(self) -> ProcessLock:
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()
