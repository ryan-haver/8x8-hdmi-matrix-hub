"""List new evidence records in docs/validation/features.yaml (each feature the record proves).

Usage (repo root): python link_evidence.py <since-commit-short-sha> [--apply]
Selects committed-evidence records whose file name carries that short SHA.
"""
import sys
from pathlib import Path

sys.path.insert(0, ".")
from tools.validate import ledger  # noqa: E402
from tools.validate.evidence import iter_records  # noqa: E402

sha = sys.argv[1]
apply = "--apply" in sys.argv
new = [r for r in iter_records(ledger.default_roots()) if f"-{sha}-" in r.path.name]
by_feature: dict[str, list[str]] = {}
for r in new:
    rel = r.path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    for fid in r.features:
        by_feature.setdefault(fid, []).append(rel)
fy = Path("docs/validation/features.yaml")
lines = fy.read_text(encoding="utf-8").splitlines(keepends=True)
out: list[str] = []
i = 0
current = None
added = 0
existing = set(line.strip()[2:] for line in lines if line.strip().startswith("- docs/validation/evidence/"))
while i < len(lines):
    line = lines[i]
    if line.startswith("- id: "):
        current = line.split(":", 1)[1].strip()
    stripped = line.rstrip("\r\n")
    if current in by_feature and stripped.startswith("  evidence: [") and stripped != "  evidence: []":
        items = [x.strip() for x in stripped[len("  evidence: ["):-1].split(",") if x.strip()]
        out.append("  evidence:\n")
        for x in items:
            out.append(f"  - {x}\n")
        for p in sorted(p for p in by_feature[current] if p not in existing and p not in items):
            out.append(f"  - {p}\n")
            added += 1
        i += 1
        continue
    if current in by_feature and stripped in ("  evidence:", "  evidence: []"):
        paths = sorted(p for p in by_feature[current] if p not in existing)
        out.append("  evidence:\n")
        i += 1
        if stripped == "  evidence:":
            while i < len(lines) and lines[i].startswith("  - "):
                out.append(lines[i])
                i += 1
        for p in paths:
            out.append(f"  - {p}\n")
            added += 1
        continue
    out.append(line)
    i += 1
print(f"records {len(new)}, features {len(by_feature)}, lines to add {added}")
if apply:
    fy.write_text("".join(out), encoding="utf-8")
    print("applied")
