import json,sys
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
sys.path.insert(0,str(Path.cwd()))
from tools.validate.__main__ import _rows
from tools.validate import ledger
archive=Path('docs/validation/evidence/F-MTX-030/2026-10-02-preset-readback')
rows,findings,summary=_rows(SimpleNamespace(evidence=[],run_summary=str(archive/'run-summary.json')))
errors=ledger.gate(rows,summary)
assert not errors,errors
assert len(summary['outcomes'])==24 and summary['clients']==['api']
assert sum(o['status']=='pass' for o in summary['outcomes'])==16
assert sum(o['status']=='fail' and o['gate']=='known-failure' for o in summary['outcomes'])==8
r=next(r for r in rows if r.id=='F-MTX-030')
assert str(r.level)=='V1' and r.proven is None and not r.fresh_pass and len(r.fresh_fail)==8
assert 'BE-36' in r.open_findings and findings['BE-36'].open
metrics={'levels':dict(Counter(str(r.level) for r in rows)), 'fresh_passing_features':sum(r.proven is not None for r in rows),'fresh_failing_features':sum(bool(r.fresh_fail) for r in rows),'stale_features':sum(r.freshness=='stale' for r in rows),'below_target':sum(r.level<r.target for r in rows),'capped_features':sum(bool(r.capped_by) for r in rows)}
assert metrics['fresh_passing_features']==130 and metrics['fresh_failing_features']==1 and metrics['stale_features']==0,metrics
assert metrics['levels']=={'V0':27,'V1':103,'V2':46,'V3':92},metrics
ledger.LEDGER_FILE.write_text(ledger.render(rows,findings,out_path=ledger.LEDGER_FILE,run_summary=summary))
(archive/'ledger-check.json').write_text(json.dumps({'gate':'ok','known_failure_records':8,'unlinked_regressions':0,'device_preset_readback_level':'V1',**metrics},indent=2)+'\n')
print(json.dumps(metrics,indent=2));print('Gate OK: all eight failures explicitly tracked as BE-36; no feature promoted by failed readback.')