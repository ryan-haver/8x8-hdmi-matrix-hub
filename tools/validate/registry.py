"""The feature registry (``docs/validation/features.yaml``) and the findings register.

Findings come from the register tables in ``docs/REMEDIATION_PLAN.md`` §4 plus
``docs/validation/findings_pending.yaml`` (rows found by validation that are
waiting to be added to the register). A register row is *closed* when its ID
cell is struck through (``~~BE-01~~``) or its Phase column (the last cell)
carries ``✅`` or the word ``closed`` (e.g. ``1 ✅ closed #12``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .model import Level

ROOT = Path(__file__).resolve().parents[2]
FEATURES_FILE = ROOT / "docs" / "validation" / "features.yaml"
PENDING_FINDINGS_FILE = ROOT / "docs" / "validation" / "findings_pending.yaml"
REMEDIATION_PLAN = ROOT / "docs" / "REMEDIATION_PLAN.md"

AREAS: dict[str, str] = {
    "matrix": "F-MTX",
    "cec": "F-CEC",
    "api": "F-API",
    "domain": "F-DOM",
    "ui": "F-UI",
    "kiosk": "F-KIO",
    "uc": "F-UC",
    "ha": "F-HA",
    "flic": "F-FLIC",
    "ops": "F-OPS",
    "security": "F-SEC",
    "reliability": "F-REL",
}
AREA_TITLES: dict[str, str] = {
    "matrix": "Matrix control",
    "cec": "CEC control",
    "api": "REST/WebSocket contract",
    "domain": "Domain features",
    "ui": "Web UI",
    "kiosk": "Kiosk",
    "uc": "Remote 3 integration",
    "ha": "Home Assistant component",
    "flic": "Flic",
    "ops": "Deployment, configuration, persistence",
    "security": "Security controls",
    "reliability": "Reliability",
}
#: v1.0.0 target per area (VALIDATION_PLAN §2). A feature may raise its target
#: (e.g. a domain core flow at V4) or, for the API area, target V3 for routes a
#: client uses; lowering below the area default needs ``target_note``.
AREA_TARGETS: dict[str, Level] = {
    "matrix": Level.V4,
    "cec": Level.V4,
    "api": Level.V2,
    "domain": Level.V3,
    "ui": Level.V3,
    "kiosk": Level.V3,
    "uc": Level.V4,
    "ha": Level.V4,
    "flic": Level.V3,
    "ops": Level.V4,
    "security": Level.V3,
    "reliability": Level.V4,
}
INTERFACE_KEYS = ("device", "telnet", "rest", "ws", "ui", "kiosk", "uc", "ha", "flic", "env", "files", "docs")
REQUIRED_FIELDS = ("id", "area", "title", "claim", "interfaces", "target", "current", "basis", "evidence",
                   "findings", "scenarios")
SEVERITIES = ("C", "H", "M", "L", "—")


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    text: str
    open: bool
    source: str

    @property
    def blocking(self) -> bool:
        """Open critical/high findings cap the affected feature at V1."""
        return self.open and self.severity in ("C", "H")


def _yaml() -> Any:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - dev dependency
        raise SystemExit("PyYAML is required for the registry: pip install -e '.[dev]'") from exc
    return yaml


def load_features(path: Path = FEATURES_FILE) -> list[dict[str, Any]]:
    doc = _yaml().safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        raise ValueError(f"{path}: expected a mapping with a 'features' list")
    return list(doc["features"])


_ROW = re.compile(r"^\|\s*(?P<id>~~)?(?P<fid>[A-Z]+-\d+)(?:~~)?\s*\|(?P<rest>.*)\|\s*$")


def parse_register(text: str, source: str = "docs/REMEDIATION_PLAN.md") -> dict[str, Finding]:
    """Findings from the §4 register tables (every ``| ID | Sev | ... |`` row)."""
    findings: dict[str, Finding] = {}
    in_register = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_register = line.startswith("## 4.")
            continue
        if not in_register:
            continue
        m = _ROW.match(line.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group("rest").split("|")]
        has_sev = bool(cells) and cells[0] in SEVERITIES
        sev = cells[0] if has_sev else "—"  # DOC rows have no severity column
        body = cells[1] if has_sev and len(cells) > 1 else cells[0]
        # Closed: struck-through ID, or a ✅/"closed" marker in the last (Phase) column. The finding text
        # itself may contain those words ("closed drawers", "falsely ✅"), so it is not searched.
        last = cells[-1] if cells else ""
        closed = bool(m.group("id")) or "✅" in last or re.search(r"\bclosed\b", last, re.IGNORECASE) is not None
        fid = m.group("fid")
        findings[fid] = Finding(fid, sev, body, not closed, source)
    return findings


def load_pending(path: Path = PENDING_FINDINGS_FILE) -> dict[str, Finding]:
    if not path.exists():
        return {}
    doc = _yaml().safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, Finding] = {}
    for row in doc.get("findings", []):
        out[row["id"]] = Finding(
            row["id"], row.get("severity", "M"), row.get("title", ""), row.get("status", "open") == "open",
            "docs/validation/findings_pending.yaml",
        )
    return out


def load_findings() -> dict[str, Finding]:
    findings = parse_register(REMEDIATION_PLAN.read_text(encoding="utf-8"))
    for fid, f in load_pending().items():
        findings.setdefault(fid, f)
    return findings


def validate_features(features: list[dict[str, Any]], findings: dict[str, Finding],
                      scenario_ids: set[str] | None = None) -> list[str]:
    """Every problem with the registry, as human-readable strings (empty = valid)."""
    problems: list[str] = []
    seen: set[str] = set()
    for i, f in enumerate(features):
        fid = f.get("id", f"<entry {i}>")
        missing = [k for k in REQUIRED_FIELDS if k not in f]
        if missing:
            problems.append(f"{fid}: missing fields {missing}")
            continue
        if fid in seen:
            problems.append(f"{fid}: duplicate id")
        seen.add(fid)
        area = f["area"]
        if area not in AREAS:
            problems.append(f"{fid}: unknown area {area!r}")
            continue
        if not re.fullmatch(rf"{AREAS[area]}-\d{{3}}", fid):
            problems.append(f"{fid}: id must be {AREAS[area]}-NNN for area {area}")
        for key in ("title", "claim", "basis"):
            if not isinstance(f[key], str) or not f[key].strip():
                problems.append(f"{fid}: '{key}' must be a non-empty string")
        try:
            target, current = Level.parse(f["target"]), Level.parse(f["current"])
        except ValueError as exc:
            problems.append(f"{fid}: {exc}")
            continue
        if target < AREA_TARGETS[area] and not f.get("target_note"):
            problems.append(f"{fid}: target {target} below the area target {AREA_TARGETS[area]} without target_note")
        if current > target:
            problems.append(f"{fid}: current {current} above target {target}")
        if not isinstance(f["interfaces"], dict) or not f["interfaces"]:
            problems.append(f"{fid}: interfaces must be a non-empty mapping")
        else:
            for k, v in f["interfaces"].items():
                if k not in INTERFACE_KEYS:
                    problems.append(f"{fid}: unknown interface kind {k!r}")
                if not isinstance(v, list) or not v:
                    problems.append(f"{fid}: interfaces.{k} must be a non-empty list")
        for key in ("evidence", "findings", "scenarios"):
            if not isinstance(f[key], list):
                problems.append(f"{fid}: '{key}' must be a list")
        for ref in f["findings"]:
            if ref not in findings:
                problems.append(f"{fid}: finding {ref} is not in the register or findings_pending.yaml")
        blocking = [ref for ref in f["findings"] if ref in findings and findings[ref].blocking]
        if blocking and current > Level.V1:
            problems.append(f"{fid}: current {current} but open critical/high finding(s) {blocking} cap it at V1")
        if current >= Level.V2 and "test" not in f["basis"] and ".spec" not in f["basis"] and not f["evidence"]:
            problems.append(f"{fid}: current {current} needs a basis naming the proving test(s) or evidence")
        if scenario_ids is not None:
            for sid in f["scenarios"]:
                if sid not in scenario_ids:
                    problems.append(f"{fid}: scenario {sid!r} does not exist in tests/validation/scenarios")
        for ev in f["evidence"]:
            if not (ROOT / ev).exists():
                problems.append(f"{fid}: evidence file {ev} does not exist")
    return problems
