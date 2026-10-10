"""Preset slots read from the device itself, independently of the hub (HIL session 2, BE-36 on hardware).

A real BK-808 answers no HTTP preset read (HIL-01), so :class:`HardwareDevice` reads every slot over
its own Telnet session (``r preset N``; a second concurrent session works, HIL session 1). The tests
use the simulator as the "matrix", as the other hardware-mode tests do; no test contacts real hardware.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from tools.validate.device import HardwareDevice, SimDevice
from tools.validate.evidence import iter_records
from tools.validate.registry import load_findings
from tools.validate.runner import Runner, RunOptions, compare_preset_catalog, preset_routing_verdict
from tools.validate.scenarios import discover
from tools.validate.stack import SimulatorProcess

#: Independent slots, one empty: what a matrix in use may hold
_SLOTS = {
    "0": {"routing": [2, 4, 4, 4, 4, 4, 4, 4], "saved": True},
    "3": {"routing": [8, 7, 6, 5, 4, 3, 2, 1], "saved": True},
    "7": {"routing": [1, 1, 1, 1, 1, 1, 1, 1], "saved": False},
}


@pytest.fixture
def fake_matrix(tmp_path: Path):
    sim = SimulatorProcess(log_dir=tmp_path / "sim-logs")
    sim.start()
    try:
        yield sim
    finally:
        sim.stop()


async def _both(sim: SimulatorProcess) -> tuple[dict, dict]:
    async with SimDevice(sim.control_url) as dev:
        await dev.reset({"presets": _SLOTS})
        truth = await dev.preset_slots()
    async with HardwareDevice("127.0.0.1", sim.https_port, telnet_port=sim.telnet_port) as hw:
        read = await hw.preset_slots()
    return truth, read


def test_hardware_device_reads_every_slot_over_telnet(fake_matrix):
    truth, read = asyncio.run(_both(fake_matrix))
    assert truth[1] == [2, 4, 4, 4, 4, 4, 4, 4] and truth[4] == [8, 7, 6, 5, 4, 3, 2, 1] and truth[8] is None
    assert read == truth


def test_compare_preset_catalog_reports_each_disagreement():
    device = {n: [n] * 8 for n in range(1, 9)}
    device[8] = None
    hub = [{"number": n, "routing": {str(o): n for o in range(1, 9)}, "routing_source": "matrix"} for n in range(1, 9)]
    hub[7]["routing"] = {}
    assert compare_preset_catalog(hub, device) == []
    hub[2]["routing"]["5"] = 1           # the hub reports a different route than the slot holds
    hub[5]["routing_source"] = "saved"   # the hub fell back to its saved copy
    hub[7]["routing"] = {"1": 8}         # the hub reports routing for an empty slot
    problems = compare_preset_catalog(hub, device)
    assert [p["slot"] for p in problems] == [3, 6, 8]
    assert compare_preset_catalog(hub[:7], device)[-1] == {"slot": 8, "problem": "missing from the hub's catalog"}


def test_catalog_scenario_is_read_only_and_proves_v4_on_a_matrix(tmp_path: Path, fake_matrix):
    scenario = discover()["preset_read.catalog_matches_device"]
    assert "hardware" in scenario.targets and not scenario.writes
    asyncio.run(_both(fake_matrix))  # the "matrix" holds independent slots and an empty one
    runner = Runner(RunOptions(target="hardware", clients=("api",), out_dir=tmp_path, findings=load_findings(),
                               operator="pytest (simulator as fake matrix)", matrix_host="127.0.0.1",
                               matrix_port=fake_matrix.https_port, telnet_port=fake_matrix.telnet_port))
    outcome = asyncio.run(runner.run([scenario]))[0]
    assert (outcome.status, outcome.level) == ("pass", "V4"), outcome.failed_checks
    record = iter_records([tmp_path / "evidence"])[0].data
    check = next(c for c in record["checks"] if "every slot" in c["description"])
    assert check["result"] == "pass" and "8 slots agree" in check["detail"]


def test_preset_routing_verdict():
    slot = [4] * 8
    assert preset_routing_verdict([1] * 8, slot, slot) == ("pass", "routing = the slot's stored routing [4, 4, 4, 4, 4, 4, 4, 4]")
    assert preset_routing_verdict([1] * 8, [1] * 8, slot)[0] == "fail"
    assert preset_routing_verdict(slot, slot, slot) == (
        "fail", "inconclusive: the live routing already equalled the slot before the recall; route something else first")
    assert preset_routing_verdict([1] * 8, [1] * 8, None) == ("fail", "the slot is empty on the device")


def test_preset_recall_proves_v4_whatever_the_slot_holds(tmp_path: Path, fake_matrix):
    """On a real matrix preset 3 holds the owner's routing, not the simulator seed's [6] * 8."""
    async def seed() -> None:
        async with SimDevice(fake_matrix.control_url) as dev:
            await dev.reset({"presets": {"2": {"routing": [4, 3, 4, 3, 4, 3, 4, 3], "saved": True}}})
    asyncio.run(seed())
    runner = Runner(RunOptions(target="hardware", clients=("api",), out_dir=tmp_path, findings=load_findings(),
                               operator="pytest (simulator as fake matrix)", matrix_host="127.0.0.1",
                               matrix_port=fake_matrix.https_port, telnet_port=fake_matrix.telnet_port,
                               allow_writes=True, answers={"presets.recall": [{"answer": "y"}]}))
    outcome = asyncio.run(runner.run([discover()["presets.recall"]]))[0]
    assert (outcome.status, outcome.level) == ("pass", "V4"), outcome.failed_checks
