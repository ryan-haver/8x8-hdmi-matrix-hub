"""Evidence records for the deployment tests (docs/validation/README.md, evidence.schema.json).

With ``DEPLOY_EVIDENCE_DIR`` set, each deployment scenario (one image mode, or the
compose files) writes one record: every test is one check, the HTTP exchanges the
tests made are the requests, and the simulator routing before and after is the
device state. Commit records from a milestone run into docs/validation/evidence/
(``DEPLOY_EVIDENCE_DIR=docs/validation/evidence``); CI uploads its own.
"""

from __future__ import annotations

import datetime
import os
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.validate import gitinfo
from tools.validate.evidence import SCHEMA_VERSION, redact, write_record

#: Files whose change makes deployment evidence stale.
COVERS_COMMON = [
    "Dockerfile", ".dockerignore", "run.py", "driver.json", "requirements.txt", "requirements-uc.txt",
    "src/rest_api/app.py", "src/rest_api/core.py", "src/rest_api/static.py", "src/persistence.py",
]

SCENARIOS: dict[str, dict[str, Any]] = {
    "deploy.image_core": {
        "title": "Shipped image, integrations off (UC_ENABLED unset), against the simulator container",
        "client": "api",
        "features": ["F-OPS-001", "F-OPS-002", "F-OPS-005", "F-OPS-006", "F-OPS-011", "F-OPS-015"],
        "covers": COVERS_COMMON,
    },
    "deploy.image_uc": {
        "title": "Shipped image, Remote 3 integration on (bridge, mDNS off, UC_DRIVER_URL), against the simulator",
        "client": "uc",
        "features": ["F-OPS-001", "F-OPS-005", "F-OPS-011", "F-OPS-015"],
        "covers": [*COVERS_COMMON, "src/driver.py"],
    },
    "deploy.compose": {
        "title": "docker-compose.yml alone, with the UC bridge override and with the UC host override",
        "client": "api",
        "features": ["F-OPS-003"],
        "covers": [*COVERS_COMMON, "docker-compose.yml", "docker-compose.uc-host.yml", "docker-compose.uc-bridge.yml"],
    },
}


def _now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@dataclass
class ScenarioRecord:
    scenario: str
    started: str = field(default_factory=_now)
    procedure: list[str] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)
    requests: list[dict[str, Any]] = field(default_factory=list)
    state_before: dict[str, Any] = field(default_factory=dict)
    state_after: dict[str, Any] = field(default_factory=dict)
    hub_env: dict[str, str] = field(default_factory=dict)
    entry: str = ""
    image_digest: str | None = None
    notes: list[str] = field(default_factory=list)

    def check(self, description: str, outcome: str, detail: str) -> None:
        result = {"passed": "pass", "failed": "fail"}.get(outcome, "n/a")
        self.checks.append({"description": description, "result": result, "detail": detail[:2000],
                            "finding": None, "linked_finding": None, "note": None})

    def build(self) -> dict[str, Any]:
        spec = SCENARIOS[self.scenario]
        failed = any(c["result"] == "fail" for c in self.checks)
        diff = [{"path": k, "before": self.state_before.get(k), "after": v}
                for k, v in self.state_after.items() if self.state_before.get(k) != v]
        sha = gitinfo.head_sha()
        return redact({
            "schema_version": SCHEMA_VERSION,
            "features": spec["features"],
            "level": "V3",
            "scenario": self.scenario,
            "scenario_title": spec["title"],
            "scenario_kind": "happy",
            "target": "sim",
            "client": spec["client"],
            "result": "fail" if failed else "pass",
            "gate": "regression" if failed else "ok",
            "blocked_reason": None,
            "commit": {"sha": sha, "short": sha[:8], "branch": gitinfo.branch(), "dirty": bool(gitinfo.dirty_files()),
                       "dirty_files": gitinfo.dirty_files()},
            "timestamp": {"started": self.started, "finished": _now()},
            "operator": "automation",
            "environment": {
                "target": "sim",
                "python": platform.python_version(),
                "platform": platform.platform(),
                "hub": {"entry": self.entry, "version": None, "api_version": None,
                        "image_digest": self.image_digest, "env": self.hub_env},
                "client": {"name": spec["client"], "runner": "pytest tests/deploy (HTTP, docker CLI"
                           + (", tools/uc_remote_sim.py)" if spec["client"] == "uc" else ")")},
                "simulator": {"seed_state": "tools/simulator/states/default.json", "container": True},
            },
            "procedure": self.procedure,
            "observations": {
                "requests": self.requests,
                "response_status": None,
                "hub_reads": [],
                "state_before": self.state_before,
                "state_after": self.state_after,
                "state_diff": diff,
                "device_log": [],
                "ws_events": [],
                "screenshots": [],
                "operator": [],
                "restore": None,
                "notes": self.notes,
            },
            "checks": self.checks,
            "findings": [],
            "covers": spec["covers"],
        })


class Recorder:
    """Collects one record per scenario; writes them when DEPLOY_EVIDENCE_DIR is set."""

    def __init__(self) -> None:
        self.records: dict[str, ScenarioRecord] = {}
        self.current: ScenarioRecord | None = None

    def get(self, scenario: str) -> ScenarioRecord:
        return self.records.setdefault(scenario, ScenarioRecord(scenario))

    def start(self, scenario: str) -> ScenarioRecord:
        """Make ``scenario`` the one HTTP exchanges are recorded for."""
        self.current = self.get(scenario)
        return self.current

    def request(self, method: str, path: str, status: int | None) -> None:
        if self.current is not None:
            self.current.requests.append({"method": method, "path": path, "status": status})

    def write(self) -> list[Path]:
        out = os.environ.get("DEPLOY_EVIDENCE_DIR")
        if not out:
            return []
        return [write_record(Path(out), rec.build()) for rec in self.records.values() if rec.checks]


RECORDER = Recorder()
