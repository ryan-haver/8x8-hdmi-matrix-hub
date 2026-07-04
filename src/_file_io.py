"""
Atomic file I/O with cross-platform file locking.

Eliminates the data corruption risk from non-atomic JSON writes by:
1. Writing to a temporary file in the same directory
2. Flushing + fsyncing to ensure durability
3. Atomically renaming temp file to target
4. Cross-platform file locking to prevent torn reads/writes from concurrent writers

Used by all persistence modules (config, scene_manager, profile_manager, etc.)
that previously used `with open(path, "w") as f: json.dump(...)` directly.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

_LOG = logging.getLogger("_file_io")

# Cross-platform file locking. POSIX uses fcntl.flock, Windows uses msvcrt.locking.
if sys.platform == "win32":
    import msvcrt

    _LOCK_REGION_SIZE = 1  # msvcrt.locking requires bytes, not just any size

    def _lock_file_exclusive(f) -> None:
        """Acquire an exclusive lock on the file."""
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, _LOCK_REGION_SIZE)
        except OSError as exc:
            raise BlockingIOError(f"File is locked by another writer: {exc}") from exc

    def _lock_file_shared(f) -> None:
        """Acquire a shared (read) lock on the file."""
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBRLCK, _LOCK_REGION_SIZE)
        except OSError as exc:
            raise BlockingIOError(f"File is locked by another writer: {exc}") from exc

    def _unlock_file(f) -> None:
        """Release the lock."""
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, _LOCK_REGION_SIZE)
        except OSError:
            # Already unlocked — fine
            pass
else:
    import fcntl

    def _lock_file_exclusive(f) -> None:
        """Acquire an exclusive lock (POSIX fcntl)."""
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise BlockingIOError(f"File is locked by another writer: {exc}") from exc

    def _lock_file_shared(f) -> None:
        """Acquire a shared lock (POSIX fcntl)."""
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
        except OSError as exc:
            raise BlockingIOError(f"File is locked by another writer: {exc}") from exc

    def _unlock_file(f) -> None:
        """Release the lock (POSIX fcntl)."""
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (OSError, ValueError):
            # Already unlocked or file closed — fine
            pass


def atomic_write_json(path: Path | str, data: Any, *, indent: int = 2, ensure_ascii: bool = False) -> bool:
    """
    Atomically write JSON to a file with cross-platform exclusive locking.

    The write is atomic at the filesystem level: the file either contains the
    complete new content, or the original content. A crash mid-write cannot
    leave a partial/corrupt JSON file.

    :param path: Target file path.
    :param data: Any JSON-serializable Python object.
    :param indent: JSON indentation level (default 2).
    :param ensure_ascii: Pass-through to json.dump (default False for unicode support).
    :returns: True on success.
    :raises: OSError on filesystem errors. BlockingIOError if another writer holds the lock.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create temp file in same directory as target so os.replace is atomic
    # (cross-filesystem rename is not atomic).
    fd, tmp_path_str = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    tmp_path = Path(tmp_path_str)

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            _lock_file_exclusive(f)
            try:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
                f.flush()
                os.fsync(f.fileno())
            finally:
                _unlock_file(f)
        # Atomic rename — replaces target in one filesystem operation
        os.replace(tmp_path, path)
        return True
    except Exception:
        # Clean up the temp file on any failure
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass
        raise


def atomic_read_json(path: Path | str, default: Any = None) -> Any:
    """
    Read JSON from a file with cross-platform shared locking.

    Uses a shared lock so multiple readers can proceed concurrently, but
    blocks if an exclusive writer holds the lock.

    :param path: Source file path.
    :param default: Value to return if the file doesn't exist.
    :returns: Parsed JSON content, or default if file is missing.
    :raises: json.JSONDecodeError if the file is corrupt.
    :raises: OSError on filesystem errors.
    """
    path = Path(path)
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        _lock_file_shared(f)
        try:
            return json.load(f)
        finally:
            _unlock_file(f)
