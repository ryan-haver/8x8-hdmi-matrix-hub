"""Helpers for the HIL capture tool tests (tools/hil/capture) against the simulator.

No test here talks to real hardware: every capture targets an in-process
simulator on ephemeral 127.0.0.1 ports.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

from tools.hil.capture import Console, Options
from tools.hil.capture.fixtures import iter_exchanges, response_body
from tools.simulator import DeviceState, Simulator

#: Folder name the capture tool derives from the default simulator state.
FW = "BK-808_V1.10.01_web-V2.00.03"

#: Short timings: the simulator answers every Telnet command in one write.
FAST: dict[str, Any] = {
    "telnet_idle": 0.05,
    "banner_idle": 0.1,
    "telnet_timeout": 1.0,
    "http_timeout": 1.5,  # also how long the unanswered `get routing status` / `preset get` cost
    "push_seconds": 0,
    "push_grace": 0.0,
}


def make_opts(sim: Simulator, out: Path | str, **overrides: Any) -> Options:
    """Capture options pointed at ``sim``; ``out`` may contain ``{firmware}``."""
    kw = {
        **FAST,
        "host": "127.0.0.1",
        "port": sim.https_port,
        "telnet_port": sim.telnet_port,
        "tls": sim.tls,
        "password": sim.state.auth["password"],
        "out": str(out),
        "yes": True,
        **overrides,
    }
    return Options(**kw)


class ScriptedConsole(Console):
    """Interactive console whose answers come from a script or a callback."""

    def __init__(self, answers: list[str] | None = None, on_ask: Any = None) -> None:
        super().__init__(interactive=True, stream=io.StringIO())
        self.answers = list(answers or [])
        self.prompts: list[str] = []
        self.on_ask = on_ask

    def ask(self, prompt: str) -> str | None:
        self.prompts.append(prompt)
        if self.on_ask is not None:
            answer = self.on_ask(prompt)
            if answer is not None:
                return answer
        return self.answers.pop(0) if self.answers else ""

    @property
    def text(self) -> str:
        return self.stream.getvalue()


def quiet() -> Console:
    return Console(interactive=False, stream=io.StringIO())


def load(root: Path, record_id: str) -> dict[str, Any]:
    return json.loads((root / f"{record_id}.json").read_text(encoding="utf-8"))


def bodies(record: dict[str, Any]) -> list[bytes | None]:
    return [response_body(ex) for ex in iter_exchanges(record)]


def new_sim(state: DeviceState | None = None, **kw: Any) -> Simulator:
    return Simulator(state or DeviceState.default(), host="127.0.0.1", https_port=0, telnet_port=0,
                     control_port=0, reboot_seconds=0.2, **kw)
