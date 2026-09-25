"""The feature ledger (``docs/validation/LEDGER.md``) and the CI gate.

Per feature:

* **recorded** - the registry's ``current`` level (the honest baseline, raised
  deliberately when evidence is committed);
* **proven** - the highest level of *fresh passing* evidence;
* **level** - proven if there is fresh passing evidence, else recorded;
  capped at V1 while an open critical/high finding is linked to the feature.

Evidence is **stale** when a file in its ``covers`` paths changed in a commit
after the evidence commit (or has uncommitted changes recorded in the record).
Evidence from a commit that is not an ancestor of HEAD counts as stale.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import gitinfo
from .evidence import COMMITTED_EVIDENCE, LoadedRecord, iter_records
from .model import LEVEL_NAMES, Level
from .registry import AREA_TITLES, AREAS, Finding

ROOT = Path(__file__).resolve().parents[2]
LEDGER_FILE = ROOT / "docs" / "validation" / "LEDGER.md"


def freshness(record: LoadedRecord, head: str | None = None, repo: Path = ROOT) -> str:
    """``fresh`` | ``stale`` | ``unknown`` (commit not in this history)."""
    covers = record.data.get("covers") or []
    dirty = record.data.get("commit", {}).get("dirty_files") or []
    if any(gitinfo.matches(p, covers) for p in dirty):
        return "stale"
    sha = record.sha
    if head is not None and sha == head:
        return "fresh"
    changed = gitinfo.changed_since(sha, repo)
    if changed is None:
        return "unknown"
    return "stale" if any(gitinfo.matches(p, covers) for p in changed) else "fresh"


@dataclass
class FeatureRow:
    feature: dict[str, Any]
    recorded: Level
    target: Level
    level: Level
    proven: Level | None
    fresh_pass: list[LoadedRecord] = field(default_factory=list)
    fresh_fail: list[LoadedRecord] = field(default_factory=list)
    stale: list[LoadedRecord] = field(default_factory=list)
    open_findings: list[str] = field(default_factory=list)
    capped_by: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return str(self.feature["id"])

    @property
    def freshness(self) -> str:
        if self.fresh_pass or self.fresh_fail:
            return "fresh"
        if self.stale:
            return "stale"
        return "—"

    @property
    def dropped(self) -> list[str]:
        """Reasons this feature is below its recorded level (the CI 'no regression' rule)."""
        reasons = []
        if self.level < self.recorded:
            reasons.append(f"level {self.level} < recorded {self.recorded}")
        for r in self.fresh_fail:
            if r.level <= self.recorded:
                reasons.append(f"{r.data['scenario']} [{r.data['client']}] failed at {r.level} "
                               f"(recorded {self.recorded})")
        return reasons


def compute(features: list[dict[str, Any]], findings: dict[str, Finding],
            evidence_roots: list[Path], repo: Path = ROOT) -> list[FeatureRow]:
    head = gitinfo.head_sha(repo)
    by_feature: dict[str, list[LoadedRecord]] = defaultdict(list)
    for rec in iter_records(evidence_roots):
        for fid in rec.features:
            by_feature[fid].append(rec)
    rows = []
    for f in features:
        recorded, target = Level.parse(f["current"]), Level.parse(f["target"])
        row = FeatureRow(f, recorded, target, recorded, None)
        for rec in by_feature.get(f["id"], []):
            fr = freshness(rec, head, repo)
            if fr != "fresh":
                row.stale.append(rec)
            elif rec.result == "pass":
                row.fresh_pass.append(rec)
            elif rec.result == "fail":
                row.fresh_fail.append(rec)
        if row.fresh_pass:
            row.proven = max(r.level for r in row.fresh_pass)
            row.level = row.proven
        row.open_findings = [x for x in f.get("findings", []) if x in findings and findings[x].open]
        row.capped_by = [x for x in row.open_findings if findings[x].blocking]
        if row.capped_by and row.level > Level.V1:
            row.level = Level.V1
        rows.append(row)
    return rows


# --------------------------------------------------------------------------- gate


def gate(rows: list[FeatureRow], run_summary: dict[str, Any] | None) -> list[str]:
    """CI failures: (a) a scenario failed without a linked open finding, (b) a feature dropped."""
    errors: list[str] = []
    if run_summary:
        for o in run_summary.get("outcomes", []):
            if o.get("gate") == "regression":
                checks = "; ".join(c["description"] for c in o.get("failed_checks", []) if not c.get("finding"))
                why = o.get("reason") or checks
                errors.append(f"(a) {o['scenario']} [{o['client']}] {o['status']} without a linked open finding: {why}")
        if run_summary.get("aborted"):
            errors.append(f"run aborted: {run_summary['aborted']}")
    for row in rows:
        for reason in row.dropped:
            errors.append(f"(b) {row.id} dropped below its recorded level: {reason}")
    return errors


# --------------------------------------------------------------------------- markdown


def _link(rec: LoadedRecord, base: Path) -> str:
    try:
        rel = rec.path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        rel = rec.path.as_posix()
    return f"[{rec.data['scenario']}·{rec.data['client']}·{rec.result}]({rel})"


def render(rows: list[FeatureRow], findings: dict[str, Finding], *, out_path: Path = LEDGER_FILE,
           run_summary: dict[str, Any] | None = None, generated_at: str = "") -> str:
    base = out_path.parent
    head = gitinfo.head_sha()
    lines = [
        "# Feature ledger",
        "",
        "> **Generated** by `python -m tools.validate ledger` — do not edit by hand. Registry:"
        " [`features.yaml`](features.yaml) · Plan: [`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) ·"
        " How to add evidence: [`README.md`](README.md).",
        f"> Commit `{head[:8]}`" + (f" · generated {generated_at}" if generated_at else ""),
        "",
        "**Level** = highest level with fresh passing evidence, else the recorded baseline (the registry's"
        " `current`), capped at V1 while an open critical/high finding is linked. **Recorded** = the registry"
        " baseline. **Fresh** = evidence commit not older than the last change to the scenario's `covers` paths.",
        "",
        "## Summary",
        "",
    ]
    levels = list(Level)
    lines.append("| Area | Features | " + " | ".join(str(v) for v in levels) + " | Below target | Stale evidence |")
    lines.append("| --- | ---: | " + " | ".join("---:" for _ in levels) + " | ---: | ---: |")
    total: Counter[str] = Counter()
    for area in AREAS:
        arows = [r for r in rows if r.feature["area"] == area]
        if not arows:
            continue
        c = Counter(str(r.level) for r in arows)
        below = sum(1 for r in arows if r.level < r.target)
        stale = sum(1 for r in arows if r.freshness == "stale")
        total.update(c)
        total["_n"] += len(arows)
        total["_below"] += below
        total["_stale"] += stale
        lines.append(f"| {AREA_TITLES[area]} | {len(arows)} | " + " | ".join(str(c.get(str(v), 0)) for v in levels)
                     + f" | {below} | {stale} |")
    lines.append(f"| **All** | **{total['_n']}** | " + " | ".join(f"**{total.get(str(v), 0)}**" for v in levels)
                 + f" | **{total['_below']}** | **{total['_stale']}** |")
    lines += ["", "Levels: " + " · ".join(f"**{v}** {LEVEL_NAMES[v]}" for v in levels), ""]

    lines += [
        "Recorded baseline (the registry's `current`: proof that existed before scenario evidence, "
        "see [`README.md`](README.md#recorded-baseline-c-pre-2026-09-25)):",
        "",
        "| Area | " + " | ".join(str(v) for v in levels) + " |",
        "| --- | " + " | ".join("---:" for _ in levels) + " |",
    ]
    rec_total: Counter[str] = Counter()
    for area in AREAS:
        arows = [r for r in rows if r.feature["area"] == area]
        if not arows:
            continue
        c = Counter(str(r.recorded) for r in arows)
        rec_total.update(c)
        lines.append(f"| {AREA_TITLES[area]} | " + " | ".join(str(c.get(str(v), 0)) for v in levels) + " |")
    lines += ["| **All** | " + " | ".join(f"**{rec_total.get(str(v), 0)}**" for v in levels) + " |", ""]

    capped = [r for r in rows if r.capped_by]
    proven = [r for r in rows if r.proven is not None]
    failing = [r for r in rows if r.fresh_fail]
    lines += [
        f"- Features with fresh passing scenario evidence: **{len(proven)}** of {len(rows)}.",
        f"- Features with a fresh failing scenario: **{len(failing)}**"
        + (": " + ", ".join(f"`{r.id}`" for r in failing) if failing else "") + ".",
        f"- Features capped at V1 by an open critical/high finding: **{len(capped)}**.",
        "",
    ]
    if run_summary:
        c = Counter(o["status"] for o in run_summary.get("outcomes", []))
        lines += [
            f"Last run: target `{run_summary.get('target')}`, clients {run_summary.get('clients')}, "
            f"commit `{run_summary.get('commit', {}).get('short', '')}` — "
            + ", ".join(f"{k}: {v}" for k, v in sorted(c.items())),
            "",
        ]
    for area in AREAS:
        arows = [r for r in rows if r.feature["area"] == area]
        if not arows:
            continue
        lines += [
            f"## {AREA_TITLES[area]} ({AREAS[area]})",
            "",
            "| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in arows:
            ev = [*r.fresh_pass, *r.fresh_fail][:4] or r.stale[:2]
            evid = "<br>".join(_link(e, base) for e in ev) or "—"
            level = f"**{r.level}**" if r.level >= r.target else f"{r.level} ⚠" if r.level < r.recorded else str(r.level)
            if r.capped_by:
                level += " (capped)"
            fnd = ", ".join(f"{x}({findings[x].severity})" for x in r.open_findings) or "—"
            title = str(r.feature["title"]).replace("|", "\\|")
            lines.append(f"| {r.id} | {title} | {r.target} | {level} | {r.recorded} | {r.freshness} | {evid} | {fnd} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def load_run_summary(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return dict(json.loads(path.read_text(encoding="utf-8")))


def default_roots(extra: list[Path] | None = None) -> list[Path]:
    return [COMMITTED_EVIDENCE, *(extra or [])]
