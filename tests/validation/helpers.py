"""Builders for synthetic evidence records used by the framework tests."""

from __future__ import annotations

import copy
from typing import Any

from tools.validate.evidence import SCHEMA_VERSION


def make_record(**over: Any) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "features": ["F-MTX-001"],
        "level": "V2",
        "scenario": "routing.switch_one",
        "scenario_title": "t",
        "scenario_kind": "happy",
        "target": "sim",
        "client": "api",
        "result": "pass",
        "gate": "ok",
        "blocked_reason": None,
        "commit": {"sha": "0" * 40, "short": "00000000", "branch": "b", "dirty": False, "dirty_files": []},
        "timestamp": {"started": "2026-09-25T10:00:00.000Z", "finished": "2026-09-25T10:00:01.000Z"},
        "operator": "automation",
        "environment": {
            "target": "sim", "python": "3.12", "platform": "x", "hub": {"entry": "run.py", "env": {}},
            "client": {"name": "api"}, "simulator": {"source_sha256": "abc", "seed_state": "default.json"},
        },
        "procedure": ["reset", "action"],
        "observations": {
            "requests": [{"method": "POST", "path": "/api/switch", "body": {"input": 6, "output": 1}, "status": 200,
                          "response": {"success": True}, "elapsed_ms": 3.2}],
            "response_status": 200,
            "hub_reads": [],
            "state_before": {"outputs": [{"source": 2}]},
            "state_after": {"outputs": [{"source": 6}]},
            "state_diff": [{"path": "outputs[0].source", "before": 2, "after": 6}],
            "device_log": [{"channel": "http", "command": "video switch"}],
            "ws_events": [{"t_ms": 5, "event": "switch", "data": {"input": 6, "output": 1}}],
            "screenshots": [],
            "client_diagnostics": None,
            "operator": [],
            "restore": None,
            "notes": [],
        },
        "checks": [{"description": "device outputs[0].source == 6", "result": "pass", "detail": "ok",
                    "finding": None, "linked_finding": None, "note": None}],
        "findings": [],
        "covers": ["src/rest_api/control.py"],
    }
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(rec.get(key), dict):
            merged = copy.deepcopy(rec[key])
            merged.update(value)
            rec[key] = merged
        else:
            rec[key] = value
    return rec
