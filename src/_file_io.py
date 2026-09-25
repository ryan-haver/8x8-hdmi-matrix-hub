"""
Atomic JSON file I/O with in-process and cross-process writer serialization.

Eliminates the data-corruption risk from non-atomic JSON writes (PER-01):

1. Writers to the same path are serialized twice over:

   * in-process by a per-path :class:`threading.Lock` (threads, executor
     jobs and event-loop callers all share it; it is never held across an
     ``await``, so it is safe to call from coroutines), and
   * cross-process by an OS advisory lock on a *stable* sidecar file
     (``.<name>.lock`` next to the target). Locking the target itself does
     not work because ``os.replace`` swaps the inode, and locking the unique
     temp file (the old behaviour) excludes nobody.

2. Content is written to a unique temp file in the same directory, flushed
   and fsynced, then atomically renamed over the target with ``os.replace``.
   Readers therefore see either the complete old file or the complete new
   one and never need a lock of their own.

3. On Windows ``os.replace`` (and ``open``) fail with ``PermissionError``
   while another process briefly holds the target open without
   ``FILE_SHARE_DELETE`` (other readers, AV scanners, indexers), or while the
   old file is still delete-pending. Both are retried with a short backoff.

4. On POSIX the containing directory is fsynced after the rename so the new
   directory entry survives a power loss.

Used by all persistence modules (config, scene_manager, profile_manager, etc.).
"""
from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
import threading
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Any, TypeVar

_LOG = logging.getLogger("_file_io")

_T = TypeVar("_T")

# How long a writer waits for the cross-process sidecar lock before giving up.
LOCK_TIMEOUT_SECONDS = 10.0
# Retry budget for Windows sharing violations on replace/open.
_REPLACE_RETRY_SECONDS = 2.0
_RETRY_INITIAL_DELAY = 0.002
_RETRY_MAX_DELAY = 0.05
_LOCK_POLL_INTERVAL = 0.01

# ---------------------------------------------------------------------------
# Low-level, non-blocking lock primitives on an open file object.
# Both raise BlockingIOError when the lock is held elsewhere.
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    import msvcrt

    # msvcrt.locking locks a byte range starting at the current file
    # position; we always lock byte 0 (locking beyond EOF is permitted).
    _LOCK_REGION_SIZE = 1

    def _locking(fd: int, mode: int) -> None:
        pos = os.lseek(fd, 0, os.SEEK_CUR)
        os.lseek(fd, 0, os.SEEK_SET)
        try:
            msvcrt.locking(fd, mode, _LOCK_REGION_SIZE)
        finally:
            os.lseek(fd, pos, os.SEEK_SET)

    def _lock_file_exclusive(f: IO[Any] | int) -> None:
        """Acquire an exclusive lock (non-blocking)."""
        fd = f if isinstance(f, int) else f.fileno()
        try:
            _locking(fd, msvcrt.LK_NBLCK)
        except OSError as exc:
            raise BlockingIOError(f"File is locked by another writer: {exc}") from exc

    def _lock_file_shared(f: IO[Any] | int) -> None:
        """Acquire a "shared" lock (non-blocking).

        Windows byte-range locks via msvcrt have no shared mode
        (``LK_NBRLCK`` is identical to ``LK_NBLCK``), so this is exclusive.
        """
        fd = f if isinstance(f, int) else f.fileno()
        try:
            _locking(fd, msvcrt.LK_NBRLCK)
        except OSError as exc:
            raise BlockingIOError(f"File is locked by another writer: {exc}") from exc

    def _unlock_file(f: IO[Any] | int) -> None:
        """Release the lock."""
        try:
            fd = f if isinstance(f, int) else f.fileno()
            _locking(fd, msvcrt.LK_UNLCK)
        except (OSError, ValueError):
            # Already unlocked or file closed — fine
            pass

else:
    import fcntl

    def _lock_file_exclusive(f: IO[Any] | int) -> None:
        """Acquire an exclusive lock (POSIX flock, non-blocking)."""
        fd = f if isinstance(f, int) else f.fileno()
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise BlockingIOError(f"File is locked by another writer: {exc}") from exc

    def _lock_file_shared(f: IO[Any] | int) -> None:
        """Acquire a shared lock (POSIX flock, non-blocking)."""
        fd = f if isinstance(f, int) else f.fileno()
        try:
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except OSError as exc:
            raise BlockingIOError(f"File is locked by another writer: {exc}") from exc

    def _unlock_file(f: IO[Any] | int) -> None:
        """Release the lock (POSIX flock)."""
        try:
            fd = f if isinstance(f, int) else f.fileno()
            fcntl.flock(fd, fcntl.LOCK_UN)
        except (OSError, ValueError):
            # Already unlocked or file closed — fine
            pass


# ---------------------------------------------------------------------------
# Writer serialization
# ---------------------------------------------------------------------------
_path_locks: dict[str, threading.Lock] = {}
_path_locks_guard = threading.Lock()


def _path_key(path: Path) -> str:
    return os.path.normcase(os.path.abspath(path))


def _in_process_lock(path: Path) -> threading.Lock:
    """Return the per-path in-process writer lock (created on first use)."""
    key = _path_key(path)
    with _path_locks_guard:
        lock = _path_locks.get(key)
        if lock is None:
            lock = _path_locks[key] = threading.Lock()
        return lock


def lock_path_for(path: Path | str) -> Path:
    """Return the stable sidecar lock-file path used to serialize writers of ``path``."""
    path = Path(path)
    return path.with_name(f".{path.name}.lock")


@contextmanager
def _sidecar_lock(path: Path, timeout: float, *, create: bool = True) -> Generator[None]:
    """Hold the cross-process exclusive lock on ``path``'s sidecar.

    The sidecar is never deleted: removing a lock file while others may have
    it open re-introduces the very race it exists to prevent. With
    ``create=False`` (readers) a missing or unopenable sidecar means no
    writer has ever used it, and the block runs unlocked.
    """
    try:
        fd = os.open(lock_path_for(path), os.O_RDWR | (os.O_CREAT if create else 0), 0o644)
    except OSError:
        if create:
            raise
        yield
        return
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                _lock_file_exclusive(fd)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"Timed out after {timeout:.1f}s waiting for write lock on {path}"
                    ) from None
                time.sleep(_LOCK_POLL_INTERVAL)
        try:
            yield
        finally:
            _unlock_file(fd)
    finally:
        os.close(fd)


def _retry_on_permission_error(op: Callable[[], _T], what: str) -> _T:
    """Run ``op``, retrying Windows sharing violations with a short backoff.

    On POSIX a PermissionError is a real permission problem and is raised
    immediately.
    """
    if sys.platform != "win32":
        return op()
    deadline = time.monotonic() + _REPLACE_RETRY_SECONDS
    delay = _RETRY_INITIAL_DELAY
    while True:
        try:
            return op()
        except PermissionError:
            if time.monotonic() >= deadline:
                _LOG.warning("Giving up on %s after %.1fs of sharing violations", what, _REPLACE_RETRY_SECONDS)
                raise
            time.sleep(delay)
            delay = min(delay * 2, _RETRY_MAX_DELAY)


def _fsync_directory(directory: Path) -> None:
    """fsync a directory so a rename inside it is durable (POSIX only)."""
    if sys.platform == "win32":
        return
    try:
        dir_fd = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(dir_fd)
    except OSError:
        # Some filesystems (e.g. certain network/overlay mounts) refuse this.
        pass
    finally:
        os.close(dir_fd)


def atomic_write_json(
    path: Path | str,
    data: Any,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    lock_timeout: float = LOCK_TIMEOUT_SECONDS,
) -> bool:
    """
    Atomically write JSON to a file, serialized against other writers.

    The write is atomic at the filesystem level: the file either contains the
    complete new content, or the original content. A crash mid-write cannot
    leave a partial/corrupt JSON file. Concurrent writers (threads in this
    process or other processes) are serialized; the last one to acquire the
    lock wins.

    :param path: Target file path.
    :param data: Any JSON-serializable Python object.
    :param indent: JSON indentation level (default 2).
    :param ensure_ascii: Pass-through to json.dump (default False for unicode support).
    :param lock_timeout: Seconds to wait for another process's write to finish.
    :returns: True on success.
    :raises TimeoutError: if another process holds the write lock for too long.
    :raises OSError: on filesystem errors.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with _in_process_lock(path), _sidecar_lock(path, lock_timeout):
        # Temp file lives in the target's directory so os.replace is a
        # same-filesystem (atomic) rename.
        fd, tmp_path_str = tempfile.mkstemp(
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        tmp_path = Path(tmp_path_str)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
                f.flush()
                os.fsync(f.fileno())
            _retry_on_permission_error(lambda: os.replace(tmp_path, path), f"replace of {path}")
        except BaseException:
            # Clean up the temp file on any failure
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise
        _fsync_directory(path.parent)
    return True


def atomic_read_json(path: Path | str, default: Any = None) -> Any:
    """
    Read JSON written by :func:`atomic_write_json`.

    Writers only ever swap in a complete file with an atomic rename, so a
    reader sees either the old or the new content and needs no lock for
    consistency. On Windows, however, an open read handle makes the writer's
    ``os.replace`` fail, so readers there queue behind writers (same
    in-process and sidecar locks) to avoid starving them; a transient
    sharing violation (e.g. a third-party handle) is retried.

    :param path: Source file path.
    :param default: Value to return if the file doesn't exist.
    :returns: Parsed JSON content, or default if file is missing.
    :raises: json.JSONDecodeError if the file is corrupt.
    :raises: OSError on filesystem errors.
    """
    path = Path(path)

    def _read() -> Any:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    try:
        if sys.platform == "win32":
            with _in_process_lock(path), _sidecar_lock(path, LOCK_TIMEOUT_SECONDS, create=False):
                return _retry_on_permission_error(_read, f"read of {path}")
        return _read()
    except FileNotFoundError:
        return default
