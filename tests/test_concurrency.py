"""Tests for concurrency protection in the REST API state.

Validates that:

1. Concurrent ``set_matrix_device`` / ``update_input_names`` /
   ``update_output_names`` calls don't trigger
   ``RuntimeError: dictionary changed size during iteration``.
2. The rate limiter dict is safe under concurrent access.
3. WebSocket client add/remove doesn't corrupt the broadcast iteration.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# Import the REST API utils module to exercise its locks.
from rest_api import utils as api_utils  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_module_state():
    """Reset module-level globals between tests so they don't bleed."""
    api_utils._matrix_device = None
    api_utils._input_names = {}
    api_utils._output_names = {}
    api_utils._ws_clients.clear()
    api_utils.reset_rate_limiter()
    yield
    api_utils._matrix_device = None
    api_utils._input_names = {}
    api_utils._output_names = {}
    api_utils._ws_clients.clear()
    api_utils.reset_rate_limiter()


class TestRateLimitUnderConcurrency:
    """Verify the rate limiter doesn't corrupt under high concurrency."""

    @pytest.mark.asyncio
    async def test_rate_limit_under_concurrent_requests(self):
        """100 concurrent checks from distinct IPs should not raise."""
        results = await asyncio.gather(
            *[api_utils._check_rate_limit(f"192.168.0.{i % 255}") for i in range(100)],
            return_exceptions=True,
        )
        # None of the calls should raise RuntimeError or KeyError
        errors = [r for r in results if isinstance(r, BaseException)]
        assert not errors, f"Rate limiter raised: {errors}"

    @pytest.mark.asyncio
    async def test_rate_limit_same_ip_many_requests(self):
        """60 requests from the same IP — first 60 pass, rest are rejected."""
        results = []
        for _ in range(80):
            results.append(await api_utils._check_rate_limit("192.168.0.99"))
        # RATE_LIMIT_REQUESTS is 60 — first 60 should pass, next 20 rejected
        assert sum(results) == api_utils.RATE_LIMIT_REQUESTS, (
            f"Expected exactly {api_utils.RATE_LIMIT_REQUESTS} passes, got {sum(results)}"
        )


class TestSetMatrixDeviceUnderConcurrency:
    """Verify that set_matrix_device mutations don't cause iteration errors."""

    @pytest.mark.asyncio
    async def test_concurrent_set_matrix_device(self):
        """50 concurrent set_matrix_device calls don't raise."""
        async def call_sync(i):
            return api_utils.set_matrix_device(
                device=f"device_{i}",  # placeholder, only None-checks
                input_names={1: f"name_{i}"},
                output_names={1: f"output_{i}"},
            )

        results = await asyncio.gather(
            *[call_sync(i) for i in range(50)],
            return_exceptions=True,
        )
        errors = [r for r in results if isinstance(r, BaseException)]
        assert not errors, f"set_matrix_device raised: {errors}"

    @pytest.mark.asyncio
    async def test_concurrent_reads_during_mutation(self):
        """Readers iterating input_names while writers mutate don't raise."""
        stop = asyncio.Event()

        async def writer() -> None:
            i = 0
            while not stop.is_set():
                i += 1
                await api_utils.update_input_names({1: f"name_{i}"})
                await asyncio.sleep(0)

        async def reader() -> None:
            iterations = 0
            while not stop.is_set():
                iterations += 1
                # This is what rest_api handlers do
                names = api_utils.get_input_names()
                # Touch the dict to trigger resize detection
                _ = list(names.items())
                if iterations > 200:
                    break
                await asyncio.sleep(0)
            return iterations

        writer_task = asyncio.create_task(writer())
        reader_task = asyncio.create_task(reader())
        try:
            reader_result = await asyncio.wait_for(reader_task, timeout=5.0)
        finally:
            stop.set()
            await writer_task

        assert reader_result > 0, "Reader should have completed iterations"


class TestWebSocketClientSetConcurrency:
    """Verify that WebSocket client set mutations are safe."""

    def test_ws_clients_add_and_discard(self):
        """Add and discard clients from multiple threads shouldn't raise."""
        errors = []

        class FakeWS:
            def __init__(self, idx: int) -> None:
                self.idx = idx
                self.closed = False

            def __hash__(self) -> int:
                return self.idx

            def __eq__(self, other) -> bool:
                return isinstance(other, FakeWS) and other.idx == self.idx

        def worker(start: int) -> None:
            try:
                for i in range(start, start + 100):
                    ws = FakeWS(i)
                    api_utils._ws_clients.add(ws)
                    api_utils._ws_clients.discard(ws)
            except Exception as e:  # pragma: no cover
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i * 100,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, f"WS client set raised: {errors}"
        assert api_utils._ws_clients == set()

    @pytest.mark.asyncio
    async def test_get_input_names_returns_copy(self):
        """get_input_names must return a copy, not the live reference."""
        await api_utils.update_input_names({1: "original"})
        names = api_utils.get_input_names()
        names[2] = "mutated"
        # The underlying _input_names must not see the mutation
        assert 2 not in api_utils._input_names


# Need threading import
import threading  # noqa: E402

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
