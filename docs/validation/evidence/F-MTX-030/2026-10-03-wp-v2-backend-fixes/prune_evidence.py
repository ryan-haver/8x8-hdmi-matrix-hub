"""Plan (or apply with --apply) pruning of superseded evidence records.

Keep the newest record per (scenario, client, target, level, result); verify the
ledger computed from the kept set equals the ledger from all records.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, ".")
from tools.validate import ledger, registry  # noqa: E402
from tools.validate.evidence import iter_records  # noqa: E402

roots = ledger.default_roots()
records = iter_records(roots)
groups = {}
for r in records:
    d = r.data
    key = (d["scenario"], d["client"], d.get("target"), d["level"], d["result"])
    if key not in groups or (r.started, str(r.path)) > (groups[key].started, str(groups[key].path)):
        groups[key] = r
keep = {id(r) for r in groups.values()}
# Records linked from any markdown doc (reports, plan, README) are cited too.
import re as _re
cited_names = set()
for md in Path("docs").rglob("*.md"):
    for m in _re.finditer(r"evidence/[^)\s\]]+?\.json", md.read_text(encoding="utf-8", errors="ignore")):
        cited_names.add(Path(m.group(0)).name)
keep |= {id(r) for r in records if r.path.name in cited_names}
print("cited by docs:", len(cited_names))
# Records listed in features.yaml `evidence:` are cited by the registry.
_reg = set()
for _f in registry.load_features():
    for _e in _f.get("evidence") or []:
        _reg.add(Path(str(_e)).name)
# (features.yaml lists are updated below instead of pinning records)
print("cited by features.yaml:", len(_reg))
kept = [r for r in records if id(r) in keep]
drop = [r for r in records if id(r) not in keep]

features = registry.load_features()
findings = registry.load_findings()

def summary(recs):
    with mock.patch.object(ledger, "iter_records", lambda _roots: recs):
        rows = ledger.compute(features, findings, roots)
    return {r.id: (str(r.level), str(r.proven), r.freshness, bool(r.fresh_fail), tuple(r.dropped)) for r in rows}

full, pruned = summary(records), summary(kept)
diff = {k: (full[k], pruned[k]) for k in full if full[k] != pruned[k]}
print(f"records {len(records)}  keep {len(kept)}  drop {len(drop)}  ledger differences {len(diff)}")
for k, v in list(diff.items())[:10]:
    print(" ", k, v)
if "--apply" in sys.argv and not diff:
    import shutil
    for r in drop:
        art = r.path.with_suffix("")
        r.path.unlink()
        if art.is_dir():
            shutil.rmtree(art)
    drop_names = {r.path.name for r in drop}
    fy = Path("docs/validation/features.yaml")
    out, removed = [], 0
    lines = fy.read_text(encoding="utf-8").splitlines(keepends=True)
    for line in lines:
        st = line.strip()
        if st.startswith("- docs/validation/evidence/") and Path(st[2:]).name in drop_names:
            removed += 1
            continue
        out.append(line)
    # an emptied block list becomes `evidence: []`
    fixed = []
    for i, line in enumerate(out):
        if line.rstrip() == "  evidence:" and (i + 1 >= len(out) or not out[i + 1].lstrip().startswith("- ")):
            fixed.append(line.replace("evidence:", "evidence: []"))
        else:
            fixed.append(line)
    fy.write_text("".join(fixed), encoding="utf-8")
    print("applied; features.yaml lines removed:", removed)
