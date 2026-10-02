import json,sys
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
sys.path.insert(0,str(Path.cwd()))
from tools.validate.__main__ import _rows
from tools.validate import ledger
archive=Path('docs/validation/evidence/F-CEC-002/2026-10-02-cec-controls')
rows,findings,summary=_rows(SimpleNamespace(evidence=[],run_summary=str(archive/'run-summary.json')))
errors=ledger.gate(rows,summary)
assert not errors,errors
assert len(summary['outcomes'])==273 and summary['clients']==['api']
assert all(o['status']=='pass' and o['gate']=='ok' for o in summary['outcomes'])
metrics={'levels':dict(Counter(str(r.level) for r in rows)), 'fresh_passing_features':sum(r.proven is not None for r in rows),'fresh_failing_features':sum(bool(r.fresh_fail) for r in rows),'stale_features':sum(r.freshness=='stale' for r in rows),'below_target':sum(r.level<r.target for r in rows),'capped_features':sum(bool(r.capped_by) for r in rows)}
assert metrics['fresh_passing_features']==135 and metrics['fresh_failing_features']==1 and metrics['stale_features']==0,metrics
assert metrics['levels']=={'V0':27,'V1':98,'V2':51,'V3':92},metrics
promoted=['F-CEC-002','F-CEC-003','F-CEC-004','F-CEC-008','F-CEC-009']
assert all(str(r.level)=='V2' and r.proven is not None for r in rows if r.id in promoted)
r=next(r for r in rows if r.id=='F-MTX-030')
assert str(r.level)=='V1' and r.proven is None and len(r.fresh_fail)==8
assert findings['BE-36'].open
ledger.LEDGER_FILE.write_text(ledger.render(rows,findings,out_path=ledger.LEDGER_FILE,run_summary=summary))
(archive/'ledger-check.json').write_text(json.dumps({'gate':'ok','batch_records':273,'batch_failures':0,'existing_known_failure_records':8,'unlinked_regressions':0,'promoted_to_V2':promoted,**metrics},indent=2)+'\n')
print(json.dumps(metrics,indent=2));print('Gate OK; five CEC features gain first committed V2 evidence; BE-36 remains open.')