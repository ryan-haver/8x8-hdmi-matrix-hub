"""Fixtures for tests that run the real hub code against the BK-808 simulator.

* ``simulator``          - a fresh :class:`tools.simulator.Simulator` per test on
                           ephemeral ports (HTTPS, Telnet, control), seeded from
                           ``tools/simulator/states/default.json``.
* ``matrix``             - a real ``OreiMatrix`` pointed at the simulator,
                           HTTP only (Telnet disabled so connect() is instant).
* ``matrix_with_telnet`` - same, but with the real Telnet client connected
                           (costs ~0.5 s: the client sleeps before reading the banner).

Retry/back-off and Telnet timeouts are shortened so fault tests stay fast.

``SIM_GOLDEN=<capture folder>`` (e.g. ``tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03``)
runs the whole suite against the simulator in golden mode: seeded from the real
device's captures and answering with its captured bytes (tools/simulator/README.md).
Tests that assume the default seed state then fail by design; the run shows
which hub paths still work on real device output.
"""

from __future__ import annotations

import asyncio
import os
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
from tools.simulator.golden import GoldenSet  # noqa: E402

#: Short Telnet command timeout used by these tests (the client default is 5 s);
#: it only matters for commands the simulator never answers (telnet_silent).
FAST_TELNET_TIMEOUT = 0.4


#: The real BK-808 captures (MCU V1.10.01, web V2.00.03, HIL Session 1).
DEVICE_CAPTURES = ROOT / "tests" / "fixtures" / "device" / "BK-808_V1.10.01_web-V2.00.03"


def make_simulator(golden_dir: str | Path | None = None) -> Simulator:
    """A simulator on ephemeral ports; with ``golden_dir``, seeded from and answering with those captures."""
    state = DeviceState.default()
    golden = None
    if golden_dir:
        golden = GoldenSet.load(golden_dir)
        golden.seed(state)
        assert not golden.warnings, golden.warnings
    return Simulator(
        state,
        host="127.0.0.1",
        https_port=0,
        telnet_port=0,
        control_port=0,
        reboot_seconds=0.3,
        golden=golden,
    )


@pytest.fixture
async def simulator():
    sim = make_simulator(os.environ.get("SIM_GOLDEN") or None)
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
    monkeypatch.setattr(telnet_client, "RECONNECT_DELAY", 0.05)
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


@pytest.fixture
async def matrix_with_telnet(fast_hub):
    """Real OreiMatrix with the real Telnet client (not yet connected)."""
    m = _new_matrix(fast_hub)
    try:
        yield m
    finally:
        await asyncio.wait_for(m.disconnect(), 5)


class LoopLagProbe:
    """Measures event-loop lag: a ticker that should wake every ``interval`` s.

    ``max_lag`` is the worst extra delay seen. A busy loop that never yields
    (SIM-02 / BE-28) shows up as lag of seconds, or as the probe never running.
    """

    def __init__(self, interval: float = 0.02) -> None:
        self.interval = interval
        self.max_lag = 0.0
        self._task: asyncio.Task | None = None

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            before = loop.time()
            await asyncio.sleep(self.interval)
            self.max_lag = max(self.max_lag, loop.time() - before - self.interval)

    def __enter__(self) -> LoopLagProbe:
        self._task = asyncio.ensure_future(self._run())
        return self

    def __exit__(self, *exc: object) -> None:
        if self._task is not None:
            self._task.cancel()


#: The hub data the validation runner and the browser tests use (profiles,
#: macros, scenes, shortcuts): ``tests/e2e/fixtures/data``.
FIXTURE_DATA = ROOT / "tests" / "e2e" / "fixtures" / "data"

#: REST module globals a hub fixture replaces (restored by monkeypatch).
REST_GLOBALS = (
    "_matrix_device",
    "_input_names",
    "_output_names",
    "_config_file",
    "_scene_manager",
    "_profile_manager",
    "_macro_manager",
    "_system_shortcut_manager",
    "_dashboard_layout_manager",
)


@pytest.fixture
async def data_hub(aiohttp_client, matrix, monkeypatch, tmp_path):
    """REST test client on the real hub app, a connected OreiMatrix and the fixture hub data.

    Wired the way ``run.py`` modular mode wires it (``set_matrix_device`` then
    ``create_rest_app``), so what these tests prove is what the shipped hub does.
    """
    import shutil

    import rest_api.utils as api_utils
    from rest_api import reset_rate_limiter, set_matrix_device
    from rest_api.app import create_rest_app

    for name in REST_GLOBALS:
        monkeypatch.setattr(api_utils, name, getattr(api_utils, name))
    monkeypatch.setattr(api_utils, "_input_names", {})
    monkeypatch.setattr(api_utils, "_output_names", {})
    for src in FIXTURE_DATA.glob("*.json"):
        shutil.copy(src, tmp_path / src.name)
    reset_rate_limiter()
    assert await matrix.connect()
    set_matrix_device(matrix, config_dir=str(tmp_path), data_dir=str(tmp_path))
    client = await aiohttp_client(create_rest_app(data_dir=tmp_path))
    client.data_dir = tmp_path  # type: ignore[attr-defined]
    yield client
    reset_rate_limiter()


def sim_writes(sim: Simulator, command: str | None = None) -> list[dict]:
    """HTTP commands the simulator received that changed its state (optionally one comhead)."""
    return [
        e for e in sim.log
        if e.get("channel") == "http" and e.get("mutated") and (command is None or e.get("command") == command)
    ]


def sim_commands(sim: Simulator, command: str) -> list[dict]:
    """Payloads of every HTTP ``command`` the simulator received, mutating or not (e.g. ``cec command``)."""
    return [e.get("payload") or {} for e in sim.log if e.get("channel") == "http" and e.get("command") == command]


# CEC tables (BE-14): displays (``object`` 1) 0 on, 1 off, 2 mute, 3 vol-, 4 vol+, 5 active;
# sources (``object`` 0) 1 power on, 2 power off, ...
CEC_OUT_POWER_ON, CEC_OUT_POWER_OFF, CEC_OUT_VOL_UP = 0, 1, 4
CEC_IN_POWER_ON, CEC_IN_POWER_OFF = 1, 2


def cec_frames(sim: Simulator, *, obj: int, index: int, to: int) -> int:
    """How many ``cec command`` frames with this object/index the simulator received for port ``to``."""
    port = [1 if i == to else 0 for i in range(1, 9)]
    return sum(
        1 for p in sim_commands(sim, "cec command")
        if p.get("object") == obj and p.get("index") == index and p.get("port") == port
    )


async def body(resp) -> dict:
    """The JSON body of an aiohttp test-client response."""
    import json

    return json.loads(await resp.text())
