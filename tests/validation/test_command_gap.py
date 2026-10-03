"""Timed evidence must fail for missing, reversed, or too-early commands."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import ActionResult
from tools.validate.device import SimDevice
from tools.validate.model import CommandGap, Scenario, act
from tools.validate.runner import Runner, RunOptions


@pytest.mark.parametrize("commands,expected", [
    ([("a", 10), ("b", 10.5)], "pass"),
    ([("a", 10), ("b", 10.1)], "fail"),
    ([("b", 10), ("a", 11)], "fail"),
    ([("a", 10)], "fail"),
])
async def test_command_gap_requires_order_and_duration(tmp_path, commands, expected):
    runner = Runner(RunOptions(out_dir=tmp_path))
    runner.device = MagicMock(spec=SimDevice)
    runner.device.log = AsyncMock(return_value=[{"command": name, "t": t} for name, t in commands])
    scenario = Scenario(id="selftest.gap", title="Timed proof", features=("F-DOM-013",), action=act("request"),
                        expect=(CommandGap("a", "b", 0.5),), covers=("tools/validate/runner.py",))
    result = await runner._check(CommandGap("a", "b", 0.5), scenario, ApiClient(),
                                 ActionResult(intent="request", ok=True), {}, 0, None, None, 0, [])
    assert result["result"] == expected
