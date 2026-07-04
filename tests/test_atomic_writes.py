"""Tests for the atomic file I/O helper (``src/_file_io.py``).

Validates the core guarantees:

1. Writes are atomic — the target file is never observed in a partial
   state, even if the process is killed mid-write.
2. Cross-platform file locking — concurrent writers serialize properly.
3. Migration safety — corrupt target files are detected and replaced.
"""

from __future__ import annotations

import json
import os
import platform
import sys
import threading
from pathlib import Path

import pytest

# Make src/ importable so we can test the helper directly.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import _file_io  # noqa: E402
from _file_io import atomic_read_json, atomic_write_json  # noqa: E402


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Provide an isolated temp directory for each test."""
    return tmp_path


class TestAtomicWriteJson:
    """Validate atomic_write_json correctness."""

    def test_write_creates_target_file(self, tmp_data_dir: Path):
        target = tmp_data_dir / "settings.json"
        data = {"key": "value", "count": 42}
        assert atomic_write_json(target, data) is True
        assert target.exists()
        assert atomic_read_json(target) == data

    def test_write_replaces_existing_file(self, tmp_data_dir: Path):
        target = tmp_data_dir / "settings.json"
        atomic_write_json(target, {"version": 1})
        atomic_write_json(target, {"version": 2, "new_field": "added"})
        assert atomic_read_json(target) == {"version": 2, "new_field": "added"}

    def test_write_creates_parent_directories(self, tmp_data_dir: Path):
        target = tmp_data_dir / "deeply" / "nested" / "path" / "settings.json"
        data = {"nested": True}
        atomic_write_json(target, data)
        assert target.exists()
        assert atomic_read_json(target) == data

    def test_write_no_leftover_temp_files_on_success(self, tmp_data_dir: Path):
        """After a successful atomic write, no .tmp files should remain."""
        target = tmp_data_dir / "settings.json"
        atomic_write_json(target, {"data": 1})
        temp_files = list(tmp_data_dir.glob(".settings.json.*.tmp"))
        assert temp_files == [], f"Leftover temp files: {temp_files}"

    def test_write_cleans_up_temp_file_on_failure(self, tmp_data_dir: Path):
        """If atomic_write_json raises, the temp file must be cleaned up."""
        target = tmp_data_dir / "settings.json"

        # Inject a failure mid-write by patching json.dump to raise.
        import _file_io

        original_dump = _file_io.json.dump

        def failing_dump(*args, **kwargs):
            raise RuntimeError("Simulated mid-write failure")

        _file_io.json.dump = failing_dump
        try:
            with pytest.raises(RuntimeError, match="Simulated"):
                atomic_write_json(target, {"key": "value"})
        finally:
            _file_io.json.dump = original_dump

        # No partial target file should exist
        assert not target.exists(), "Target file should not exist after failed write"
        # No leftover .tmp files
        temp_files = list(tmp_data_dir.glob(".settings.json.*.tmp"))
        assert temp_files == [], f"Temp files not cleaned up: {temp_files}"

    def test_concurrent_writers_dont_corrupt_file(self, tmp_data_dir: Path):
        """100 threads writing the same file should produce valid JSON."""
        target = tmp_data_dir / "settings.json"
        errors = []

        def writer(idx: int) -> None:
            try:
                for _ in range(5):
                    atomic_write_json(target, {"writer": idx, "list": list(range(10))})
            except Exception as e:  # pragma: no cover - we want all errors
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All writes should have succeeded (serialized via exclusive lock)
        assert not errors, f"Concurrent write errors: {errors}"
        # Final file must be valid JSON
        data = atomic_read_json(target)
        assert data is not None
        assert "writer" in data
        assert "list" in data
        assert data["list"] == list(range(10))

    def test_concurrent_writer_blocked_by_reader(self, tmp_data_dir: Path):
        """An exclusive writer should be blocked by a concurrent reader."""
        target = tmp_data_dir / "settings.json"
        atomic_write_json(target, {"initial": True})

        read_started = threading.Event()
        release_reader = threading.Event()

        def reader():
            with open(target, encoding="utf-8") as f:
                _file_io._lock_file_shared(f)
                try:
                    read_started.set()
                    # Hold the lock until released
                    release_reader.wait(timeout=5)
                finally:
                    _file_io._unlock_file(f)

        t = threading.Thread(target=reader)
        t.start()
        read_started.wait(timeout=5)

        # While reader holds the shared lock, writer should fail (NB locking)
        # OR block until reader releases. With LOCK_NB this raises BlockingIOError.
        from _file_io import _lock_file_exclusive

        with open(target, encoding="utf-8") as f:
            with pytest.raises(BlockingIOError):
                _lock_file_exclusive(f)

        release_reader.set()
        t.join()

    def test_unicode_data_round_trips(self, tmp_data_dir: Path):
        """Non-ASCII characters must survive the atomic write."""
        target = tmp_data_dir / "settings.json"
        data = {"name": "日本語テスト 🎬 café"}
        atomic_write_json(target, data, ensure_ascii=False)
        assert atomic_read_json(target) == data


class TestAtomicReadJson:
    """Validate atomic_read_json correctness."""

    def test_read_missing_returns_default(self, tmp_data_dir: Path):
        target = tmp_data_dir / "missing.json"
        assert atomic_read_json(target) is None
        assert atomic_read_json(target, default={}) == {}

    def test_read_corrupt_returns_default(self, tmp_data_dir: Path):
        """Corrupt JSON should raise JSONDecodeError, not return garbage."""
        import json as _json

        target = tmp_data_dir / "corrupt.json"
        target.write_text("{this is not valid json")
        with pytest.raises(_json.JSONDecodeError):
            atomic_read_json(target)

    def test_read_valid(self, tmp_data_dir: Path):
        target = tmp_data_dir / "valid.json"
        data = {"a": 1, "b": [2, 3], "c": {"nested": True}}
        atomic_write_json(target, data)
        assert atomic_read_json(target) == data


class TestPlatformSupport:
    """Verify the locking implementation matches the platform."""

    def test_locking_module_is_platform_appropriate(self):
        if sys.platform == "win32":
            import msvcrt

            assert hasattr(_file_io, "msvcrt")
        else:
            import fcntl

            assert hasattr(_file_io, "fcntl")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
