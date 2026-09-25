"""Shared helpers for the scripted-Remote tests (tests/uc)."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
SEED_STATE = json.loads((ROOT / "tools" / "simulator" / "states" / "default.json").read_text(encoding="utf-8"))
DRIVER_JSON = json.loads((ROOT / "driver.json").read_text(encoding="utf-8"))

#: Status polling interval for the hub under test (seconds; driver.py reads it with int()).
POLL = 1
#: How long "one poll cycle" may take end to end on a slow CI runner.
CYCLE = POLL + 3.0

#: Seed names (tools/simulator/states/default.json).
INPUT_NAMES = [p["name"] for p in SEED_STATE["inputs"]]
OUTPUT_NAMES = [p["name"] for p in SEED_STATE["outputs"]]


def known_bug(finding: str, reason: str, *, raises: type[BaseException] | tuple[type[BaseException], ...]
              = AssertionError) -> pytest.MarkDecorator:
    """Strict xfail for behaviour that a register row says is wrong today.

    The test asserts the *correct* behaviour. It must fail now, and only in the
    expected way (``raises``, an assertion by default: a timeout or a crashed
    fixture is a real failure, not the known bug). When the fix lands the test
    passes, ``strict`` turns that into a failure (XPASS), and the marker is
    removed in the fixing PR (docs/REMEDIATION_PLAN.md §8).
    """
    return pytest.mark.xfail(strict=True, reason=f"{finding}: {reason}", raises=raises)


async def wait_for(predicate: Callable[[], Awaitable[bool]], timeout: float = CYCLE, interval: float = 0.2) -> bool:
    """Poll an async predicate until it is true or ``timeout`` passes; returns the last result."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        if await predicate():
            return True
        if loop.time() >= deadline:
            return False
        await asyncio.sleep(interval)


def sent(log: list[dict[str, Any]], command: str, channel: str = "http") -> list[dict[str, Any]]:
    """Payloads of every ``command`` the simulator received on ``channel`` (reads and writes)."""
    return [e.get("payload") or {} for e in log if e.get("command") == command and e.get("channel") == channel]


def writes(log: list[dict[str, Any]]) -> list[tuple[Any, Any]]:
    """``(command, payload)`` of every command that changed the device."""
    return [(e.get("command"), e.get("payload")) for e in log if e.get("mutated")]


def cec_frames(log: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The CEC frames the simulator received over HTTP, without the constant fields."""
    return [{k: p[k] for k in ("object", "port", "index") if k in p} for p in sent(log, "cec command")]


def port_mask(port: int) -> list[int]:
    return [1 if i == port else 0 for i in range(1, 9)]
