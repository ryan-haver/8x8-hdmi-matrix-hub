"""(scenario, client) pairs whose newest record is stale at HEAD, per client, with the hub env they need."""
import json
import sys
from collections import defaultdict

sys.path.insert(0, ".")
from tools.validate import gitinfo, ledger  # noqa: E402
from tools.validate.evidence import iter_records  # noqa: E402

head = gitinfo.head_sha()
by = defaultdict(list)
for r in iter_records(ledger.default_roots()):
    by[(r.data["scenario"], r.data["client"])].append(r)
stale = defaultdict(list)
for (sc, cl), recs in by.items():
    if not any(ledger.freshness(r, head) == "fresh" for r in recs):
        stale[cl].append(sc)
for cl, scs in sorted(stale.items()):
    print(cl, len(scs), sorted(scs)[:8])
json.dump({k: sorted(v) for k, v in stale.items()}, open("build/stale.json", "w"), indent=1)
