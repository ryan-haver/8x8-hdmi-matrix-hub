"""Independent rollback-phase review with real sockets and a gated real close."""

from __future__ import annotations

import asyncio
import json

import aiohttp
import pytest

import hub.runtime.composition as composition
from hub.runtime.config import MatrixAddress
from tests.test_runtime_rollback_deadline_r1h import storage
from tests.test_runtime_rollback_reconnect_r1g import ready
from tests.test_runtime_rollback_reconnect_r1g import runtime_sim as runtime_sim


@pytest.mark.parametrize("interruption", ["release", "cancel", "deadline", "cancel_at_close"])
async def test_candidate_close_interruption_restores_original(runtime_sim, monkeypatch, tmp_path, interruption):
    """Cancel/expire rollback while its real candidate session is closing.

    Only the scheduling of aiohttp close is gated; it really closes afterward.
    No connect result, transport drain, production deadline or state is replaced.
    cancel_at_close schedules cancellation at entry to the un-delayed real close.
    The release-only control proves the same failed candidate restores normally.
    """
    runtime, sim, clients, _ = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = storage(runtime)
    entered, release = asyncio.Event(), asyncio.Event()
    real_close = aiohttp.ClientSession.close

    async def close(session):
        if len(clients) == 2 and session is clients[1]._session:
            entered.set()
            if interruption == "cancel_at_close":
                asyncio.get_running_loop().call_soon(setup.cancel)
            else:
                await release.wait()
        await real_close(session)

    monkeypatch.setattr(aiohttp.ClientSession, "close", close)
    sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 1})
    candidate_address = MatrixAddress(
        "localhost", sim.https_port, sim.telnet_port, "candidate-user", "candidate-secret"
    )
    started = asyncio.get_running_loop().time()
    setup = asyncio.create_task(runtime.reconfigure(candidate_address, persist=True))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        candidate = clients[1]
        assert runtime.service.client is candidate and not sim.faults.any_http
        assert candidate._disconnect_task is not None
        if interruption != "cancel_at_close":
            assert not candidate._disconnect_task.done()
        if interruption == "cancel":
            setup.cancel()
            await ready(lambda: setup.cancelling() > 0)
        elif interruption == "deadline":
            assert composition.CLEANUP_TIMEOUT == 5.0
            async with asyncio.timeout(7):
                while not setup.cancelling():
                    await asyncio.sleep(0.01)
            assert asyncio.get_running_loop().time() - started >= 5
        release.set()
        if interruption in {"cancel", "cancel_at_close"}:
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(asyncio.shield(setup), 3)
            assert setup.cancelled()
        else:
            result = await asyncio.wait_for(asyncio.shield(setup), 3)
            assert not result.success
        elapsed = asyncio.get_running_loop().time() - started
        assert elapsed < (7 if interruption == "deadline" else 3)
        assert candidate._disconnect_task.done()
        assert candidate._session is None and candidate._telnet is None
        assert candidate._connect_task is None and candidate._reconnect_task is None
        assert storage(runtime) == before
        assert not runtime._stopping and not runtime.reconfiguring and setup not in runtime._operations
        assert runtime._refresh_task is not None and not runtime._refresh_task.done()
        deadline = asyncio.get_running_loop().time() + 2
        while asyncio.get_running_loop().time() < deadline and not runtime.snapshot().connected:
            await asyncio.sleep(0.02)
        evidence = {
            "interruption": interruption,
            "elapsed": elapsed,
            "caller_cancelled": setup.cancelled(),
            "original_identity": runtime.service.client is original,
            "original_address": runtime.address == address,
            "original_names_identity": runtime.service.names is names,
            "original_effective_credentials": runtime.service.client.credentials() == original.credentials(),
            "connected": runtime.snapshot().connected,
            "login_count": sim.login_count,
            "original_reconnect_owner": original._reconnect_task is not None,
            "candidate_closed": candidate._session is None and candidate._telnet is None,
            "storage_unchanged": storage(runtime) == before,
        }
        (tmp_path / "observation.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        assert runtime.service.client is original, evidence
        assert runtime.address == address and runtime.service.names is names
        assert runtime.snapshot().connected
        assert runtime.snapshot().input_names[1] == "Saved console"
        assert runtime.snapshot().output_names[1] == "Saved screen"
        assert sim.login_count == 3
    finally:
        release.set()
        await asyncio.gather(setup, return_exceptions=True)
