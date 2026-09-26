"""Runner plumbing for real clients that *show* state (WP-D1): ``device_change`` and ``ClientState``.

A small observing client stands in for Home Assistant (whose own runs need
Docker, ``python -m tools.validate run --client ha``): it reads what it
"shows" from the hub's REST API, the way the Home Assistant component does.
The real hub (run.py) and the simulator run as in every runner test.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from tools.validate import runner as runner_mod
from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import ActionResult, Client, HubInfo, NotSupportedError
from tools.validate.evidence import iter_records
from tools.validate.model import Action, ClientState, Device, Scenario, act
from tools.validate.registry import load_findings
from tools.validate.runner import Runner, RunOptions


class ObservingClient(Client):
    """Shows input signals as ``on``/``off``, read through the hub (registered as ``flic`` for the run)."""

    name = "flic"
    observes = True
    intents = frozenset()

    def __init__(self) -> None:
        super().__init__()
        self.api = ApiClient()

    async def start(self, hub: HubInfo) -> None:
        await self.api.start(hub)

    async def stop(self) -> None:
        await self.api.stop()

    async def perform(self, action: Action) -> ActionResult:
        raise NotSupportedError(action.intent)

    async def observe(self, key: str) -> Any:
        number = int(key.split("_")[1])  # "input_3_signal"
        _status, body, _record = await self.api.request("GET", "/api/status/inputs")
        inputs = (body or {}).get("data", {}).get("inputs", [])
        active = next((i["signalActive"] for i in inputs if i["number"] == number), None)
        return None if active is None else ("on" if active else "off")


SIGNAL_ON = act("device_change", event={"type": "signal", "port": 3, "present": True})


def _scenario(sid: str, *expect, **kw) -> Scenario:
    return Scenario(id=sid, title=sid, features=("F-HA-008",), clients=("flic", "api"), targets=("sim",),
                    action=SIGNAL_ON, expect=expect, covers=("src/rest_api/core.py",), **kw)


@pytest.fixture
def observing(monkeypatch):
    monkeypatch.setitem(runner_mod.CLIENTS, "flic", ObservingClient)
    import tools.validate.clients as clients_pkg

    monkeypatch.setitem(clients_pkg.CLIENTS, "flic", ObservingClient)


def test_device_change_is_seen_by_the_client(tmp_path: Path, observing):
    seen = _scenario("selftest.signal_seen", Device("inputs[2].signal", equals=1),
                     ClientState("input_3_signal", before="off", equals="on", timeout=15))
    # Input 4 never has a signal here, so "on" before the action cannot be met.
    wrong_precondition = _scenario("selftest.wrong_before",
                                   ClientState("input_4_signal", before="on", equals="off", timeout=1))
    never = _scenario("selftest.never_shown", ClientState("input_4_signal", equals="on", timeout=1))
    runner = Runner(RunOptions(target="sim", clients=("flic", "api"), out_dir=tmp_path, findings=load_findings()))
    asyncio.run(runner.run([seen, wrong_precondition, never]))
    out = {(o.scenario, o.client): o for o in runner.outcomes}

    assert (out[("selftest.signal_seen", "flic")].status, out[("selftest.signal_seen", "flic")].level) == ("pass", "V3")
    assert out[("selftest.wrong_before", "flic")].status == "fail"
    assert out[("selftest.never_shown", "flic")].status == "fail"
    # The api client cannot observe: device_change scenarios are not for it.
    assert out[("selftest.signal_seen", "api")].status == "skipped"
    assert "cannot observe" in out[("selftest.signal_seen", "api")].reason

    records = {r.data["scenario"]: r.data for r in iter_records([tmp_path / "evidence"])}
    rec = records["selftest.signal_seen"]
    assert "client showed input_3_signal = 'off' before the action" in rec["procedure"]
    assert any("simulator event" in step for step in rec["procedure"])
    assert {"path": "inputs[2].signal", "before": 0, "after": 1} in rec["observations"]["state_diff"]
    assert [c["result"] for c in rec["checks"]] == ["pass", "pass"]
    pre = records["selftest.wrong_before"]["checks"][0]
    assert pre["description"].endswith("before the action") and pre["result"] == "fail"
