import json,sys
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
sys.path.insert(0,str(Path.cwd()))
from tools.validate.__main__ import _rows
from tools.validate import ledger
archive=Path('docs/validation/evidence/F-DOM-001/2026-10-02-profile-crud')
rows,findings,summary=_rows(SimpleNamespace(evidence=[],run_summary=str(archive/'run-summary.json')))
errors=ledger.gate(rows,summary)
assert not errors,errors
assert len(summary['outcomes'])==51 and summary['clients']==['api']
assert sum(o['status']=='pass' and o['gate']=='ok' for o in summary['outcomes'])==49
assert sum(o['status']=='fail' and o['gate']=='known-failure' for o in summary['outcomes'])==2
metrics={'levels':dict(Counter(str(r.level) for r in rows)), 'fresh_passing_features':sum(r.proven is not None for r in rows),'fresh_failing_features':sum(bool(r.fresh_fail) for r in rows),'stale_features':sum(r.freshness=='stale' for r in rows),'below_target':sum(r.level<r.target for r in rows),'capped_features':sum(bool(r.capped_by) for r in rows)}
assert metrics['fresh_passing_features']==139 and metrics['fresh_failing_features']==5 and metrics['stale_features']==0,metrics
assert metrics['levels']=={'V0':27,'V1':94,'V2':55,'V3':92},metrics
for fid in ('F-DOM-001','F-DOM-006'):
 row=next(r for r in rows if r.id==fid)
 assert str(row.level)=='V2' and row.proven is not None
assert {r.id for r in rows if r.fresh_fail}=={'F-MTX-030','F-CEC-010','F-API-015','F-DOM-001','F-API-019'}
assert findings['API-22'].open and findings['SEC-04'].open and findings['API-20'].open and findings['BE-36'].open and findings['BE-37'].open and findings['BE-15'].open
ledger.LEDGER_FILE.write_text(ledger.render(rows,findings,out_path=ledger.LEDGER_FILE,run_summary=summary))
(archive/'ledger-check.json').write_text(json.dumps({'gate':'ok','batch_records':51,'batch_passes':49,'batch_known_failures':2,'existing_preset_known_failures':8,'unlinked_regressions':0,'promoted_to_V2':['F-DOM-001','F-DOM-006'],**metrics},indent=2)+'\n')
print(json.dumps(metrics,indent=2));print('Gate OK: CRUD and surface settings gain V2; API-22 and existing caps/findings remain open.')