"""Independent follow-up boundary reproductions, without production changes."""

from __future__ import annotations

import asyncio

import pytest

from tests import test_runtime_review_r8 as review
from tests.test_runtime_rollback_reconnect_r1g import (
    assert_no_candidate_owner,
    outage,
)
from tests.test_runtime_rollback_reconnect_r1g import (
    runtime_sim as runtime_sim,
)
from tools.simulator import Simulator


async def test_rollback_login_exceeding_cleanup_deadline_recovers_automatically(runtime_sim):
    """The real rollback response arrives after cleanup, then the SIM is healthy."""
    runtime, sim, clients, saved = await runtime_sim()
    original, address = clients[0], runtime.address
    before = saved.read_bytes()
    sim.hold_login = 3
    outage(sim)
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    await asyncio.wait_for(sim.received.wait(), 3)
    # Keep the production five-second cleanup limit. The simulator dispatches
    # the second 503 but holds its socket response until rollback has timed out.
    result = await asyncio.wait_for(setup, 7)
    assert not result.success and not result.connected
    assert not runtime._stopping and not runtime._refresh_task.done()
    assert runtime.address == address and runtime.service.client is original
    assert original.credentials() == ("original-user", "original-secret")
    assert saved.read_bytes() == before
    assert_no_candidate_owner(clients)
    assert not sim.faults.any_http
    sim.release.set()
    # Drain the real shielded login attempt, ensuring its delayed failure has
    # completed before evaluating recovery. No manual connect is invoked.
    assert not await asyncio.wait_for(asyncio.shield(original._connect_task), 2)
    deadline = asyncio.get_running_loop().time() + 2
    while asyncio.get_running_loop().time() < deadline and not runtime.snapshot().connected:
        await asyncio.sleep(0.02)
    assert runtime.snapshot().connected, (
        "Rollback cleanup timeout abandoned automatic reconnect after the SIM healed; "
        f"reconnect={original._reconnect_task!r}, logins={sim.login_count}"
    )
    assert saved.read_bytes() == before


class DelayedRollbackSimulator(Simulator):
    """Hold the third real HTTP login response without changing application code."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login_count = 0
        self.received = asyncio.Event()
        self.release = asyncio.Event()

    async def _handle_instr(self, request):
        login = (await request.json()).get("comhead") == "login"
        if login:
            self.login_count += 1
        hold = login and self.login_count == 3
        response = await super()._handle_instr(request)
        if hold:
            self.received.set()
            await self.release.wait()
        return response


@pytest.mark.docker
async def test_image_rollback_cleanup_timeout_recovers_automatically(tmp_path, monkeypatch):
    monkeypatch.setattr(review, "Simulator", DelayedRollbackSimulator)
    async with review.shipped_image(tmp_path) as (sim, session, url, name, _):
        outage(sim)

        async def reconfigure():
            async with session.post(
                url + "/api/settings/matrix-host",
                json={"host": "host.docker.internal", "port": sim.https_port, "telnet_port": sim.telnet_port},
            ) as response:
                body = await response.json()
                assert response.status == 200 and body["data"]["connected"] is False, body

        setup = asyncio.create_task(reconfigure())
        try:
            await asyncio.wait_for(sim.received.wait(), 3)
            await asyncio.wait_for(setup, 7)
        finally:
            sim.release.set()
        assert not sim.faults.any_http
        recovered = await review.wait_health(session, url, seconds=12)
        assert sum(entry.get("fault") == "http_503" for entry in sim.log) == 2
        # Only after the automatic-recovery window, diagnose reachability with
        # the existing manual workaround. Its success cannot satisfy the oracle.
        async with session.post(url + "/api/settings/test-connection") as response:
            manual = await response.json()
            assert response.status == 200 and manual["data"]["connected"], manual
        assert recovered, f"Cleanup timeout required manual recovery\n{await review.docker('logs', name)}"
