"""Tests for the atomic file I/O helper (``src/_file_io.py``).

Validates the core guarantees:

1. Writes are atomic — the target file is never observed in a partial
   state, even if the process is killed mid-write.
2. Cross-platform file locking — concurrent writers serialize properly.
3. Migration safety — corrupt target files are detected and replaced.
"""

from __future__ import annotations

import json
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


class TestWriterSerialization:
    """PER-01: writers serialize on a stable sidecar lock, not the temp file."""

    def test_sidecar_lock_path_is_stable_and_hidden(self, tmp_data_dir: Path):
        target = tmp_data_dir / "settings.json"
        assert _file_io.lock_path_for(target) == tmp_data_dir / ".settings.json.lock"
        atomic_write_json(target, {"a": 1})
        atomic_write_json(target, {"a": 2})
        assert _file_io.lock_path_for(target).exists()
        # Only the target and its sidecar remain — no temp files.
        assert sorted(p.name for p in tmp_data_dir.iterdir()) == [".settings.json.lock", "settings.json"]

    def test_writer_waits_for_foreign_sidecar_lock(self, tmp_data_dir: Path):
        """A writer blocks (then times out) while another handle holds the sidecar lock."""
        import os

        target = tmp_data_dir / "settings.json"
        atomic_write_json(target, {"v": 1})

        fd = os.open(_file_io.lock_path_for(target), os.O_RDWR)
        try:
            _file_io._lock_file_exclusive(fd)
            with pytest.raises(TimeoutError):
                atomic_write_json(target, {"v": 2}, lock_timeout=0.2)
            # The sidecar lock never locks the target itself.
            assert json.loads(target.read_text(encoding="utf-8")) == {"v": 1}
        finally:
            _file_io._unlock_file(fd)
            os.close(fd)

        atomic_write_json(target, {"v": 3}, lock_timeout=0.2)
        assert atomic_read_json(target) == {"v": 3}

    def test_readers_never_see_partial_content_during_writes(self, tmp_data_dir: Path):
        target = tmp_data_dir / "settings.json"
        payload = {"list": list(range(500))}
        atomic_write_json(target, {"writer": -1, **payload})
        stop = threading.Event()
        errors: list[BaseException] = []

        def reader() -> None:
            while not stop.is_set():
                try:
                    data = atomic_read_json(target)
                    assert data["list"] == payload["list"]
                except BaseException as exc:  # pragma: no cover - we want all errors
                    errors.append(exc)
                    return

        readers = [threading.Thread(target=reader) for _ in range(4)]
        for t in readers:
            t.start()
        try:
            for i in range(100):
                atomic_write_json(target, {"writer": i, **payload})
        finally:
            stop.set()
            for t in readers:
                t.join()
        assert not errors, errors

    def test_concurrent_writer_processes_dont_corrupt_file(self, tmp_data_dir: Path):
        """Several processes hammering one file serialize via the sidecar lock."""
        import subprocess

        target = tmp_data_dir / "shared.json"
        script = (
            "import sys; sys.path.insert(0, sys.argv[1]);"
            "from _file_io import atomic_write_json, atomic_read_json;"
            "idx = int(sys.argv[3]);"
            "[atomic_write_json(sys.argv[2], {'writer': idx, 'n': n, 'list': list(range(200))}) for n in range(25)];"
            "[atomic_read_json(sys.argv[2]) for _ in range(25)]"
        )
        procs = [
            subprocess.Popen(
                [sys.executable, "-c", script, str(_PROJECT_ROOT / "src"), str(target), str(i)],
                stderr=subprocess.PIPE,
            )
            for i in range(4)
        ]
        failures = []
        for proc in procs:
            _, err = proc.communicate(timeout=60)
            if proc.returncode != 0:
                failures.append(err.decode(errors="replace"))
        assert not failures, "\n".join(failures)
        data = atomic_read_json(target)
        assert data["list"] == list(range(200))
        assert data["n"] == 24
        assert list(tmp_data_dir.glob(".shared.json.*.tmp")) == []


class TestReplaceRetry:
    """PER-01: Windows sharing violations on os.replace are retried."""

    def test_transient_permission_error_on_replace(self, tmp_data_dir: Path, monkeypatch):
        target = tmp_data_dir / "settings.json"
        real_replace = _file_io.os.replace
        calls = {"n": 0}

        def flaky_replace(src, dst):
            calls["n"] += 1
            if calls["n"] <= 2:
                raise PermissionError(13, "The process cannot access the file")
            return real_replace(src, dst)

        monkeypatch.setattr(_file_io.os, "replace", flaky_replace)
        if sys.platform == "win32":
            assert atomic_write_json(target, {"ok": True}) is True
            assert calls["n"] == 3
            assert atomic_read_json(target) == {"ok": True}
        else:
            # On POSIX a PermissionError is a real permission problem.
            with pytest.raises(PermissionError):
                atomic_write_json(target, {"ok": True})
            assert calls["n"] == 1
        assert list(tmp_data_dir.glob(".settings.json.*.tmp")) == []

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows sharing semantics")
    def test_replace_succeeds_once_reader_closes_handle(self, tmp_data_dir: Path):
        """A reader holding the target open delays, but does not fail, the write."""
        target = tmp_data_dir / "settings.json"
        atomic_write_json(target, {"v": 1})
        f = open(target, encoding="utf-8")  # noqa: SIM115 - held open deliberately
        timer = threading.Timer(0.2, f.close)
        timer.start()
        try:
            atomic_write_json(target, {"v": 2})
        finally:
            timer.join()
            f.close()
        assert atomic_read_json(target) == {"v": 2}


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
            import msvcrt  # noqa: F401  (platform must provide it)

            assert hasattr(_file_io, "msvcrt")
        else:
            import fcntl  # noqa: F401  (platform must provide it)

            assert hasattr(_file_io, "fcntl")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
