"""Fixtures for tests that run the real hub code against the BK-808 simulator.

* ``simulator``          - a fresh :class:`tools.simulator.Simulator` per test on
                           ephemeral ports (HTTPS, Telnet, control), seeded from
                           ``tools/simulator/states/default.json``.
* ``matrix``             - a real ``OreiMatrix`` pointed at the simulator,
                           HTTP only (Telnet disabled so connect() is instant).
* ``matrix_with_telnet`` - same, but with the real Telnet client connected
                           (costs ~0.5 s: the client sleeps before reading the banner).

Retry/back-off and Telnet timeouts are shortened so fault tests stay fast.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import orei_matrix  # noqa: E402
import telnet_client  # noqa: E402
from tools.simulator import DeviceState, Simulator  # noqa: E402

#: Short Telnet command timeout used by these tests (the client default is 5 s
#: and, per BE-07, every successful set/CEC command waits the full timeout).
FAST_TELNET_TIMEOUT = 0.4


@pytest.fixture(scope="session")
def default_state() -> DeviceState:
    return DeviceState.default()


@pytest.fixture
async def simulator(default_state: DeviceState):
    sim = Simulator(
        default_state,
        host="127.0.0.1",
        https_port=0,
        telnet_port=0,
        control_port=0,
        reboot_seconds=0.3,
    )
    await sim.start()
    try:
        yield sim
    finally:
        await sim.stop()


@pytest.fixture
def fast_hub(monkeypatch, simulator):
    """Point the hub's env-driven settings at the simulator and shorten timeouts."""
    monkeypatch.setenv("OREI_TELNET_PORT", str(simulator.telnet_port))
    monkeypatch.delenv("OREI_USER", raising=False)
    monkeypatch.delenv("OREI_PASSWORD", raising=False)
    monkeypatch.delenv("OREI_USE_TELNET_CEC", raising=False)
    monkeypatch.delenv("OREI_VERIFY_SSL", raising=False)
    monkeypatch.setattr(orei_matrix, "INITIAL_RETRY_DELAY", 0.01)
    monkeypatch.setattr(orei_matrix, "MAX_RETRY_DELAY", 0.05)
    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", FAST_TELNET_TIMEOUT)
    return simulator


def _new_matrix(sim: Simulator) -> orei_matrix.OreiMatrix:
    return orei_matrix.OreiMatrix("127.0.0.1", port=sim.https_port, use_https=sim.tls)


@pytest.fixture
async def matrix(fast_hub, monkeypatch):
    """Real OreiMatrix against the simulator, HTTP only (not yet connected)."""
    m = _new_matrix(fast_hub)
    monkeypatch.setattr(m, "_connect_telnet", AsyncMock(return_value=False))
    try:
        yield m
    finally:
        await m.disconnect()


async def _raise_cancelled() -> None:
    raise asyncio.CancelledError


def defuse_telnet_supervisor(m: orei_matrix.OreiMatrix) -> None:
    """Test-only workaround for BE-01.

    ``TelnetClient._listen_for_push`` swallows ``CancelledError`` and returns,
    and ``_task_supervisor`` restarts coroutines that return, so
    ``TelnetClient.disconnect()`` waits forever for the listener task. The
    supervisor looks the coroutine up through ``self`` on every restart, so
    swapping it for one that raises ``CancelledError`` lets the task end.
    """
    telnet = m._telnet
    if telnet is not None:
        telnet._listen_for_push = _raise_cancelled
        telnet._reconnect_loop = _raise_cancelled


async def safe_disconnect(m: orei_matrix.OreiMatrix) -> None:
    defuse_telnet_supervisor(m)
    await asyncio.wait_for(m.disconnect(), 5)


@pytest.fixture
async def matrix_with_telnet(fast_hub):
    """Real OreiMatrix with the real Telnet client (not yet connected)."""
    m = _new_matrix(fast_hub)
    try:
        yield m
    finally:
        await safe_disconnect(m)
