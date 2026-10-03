import json,sys
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
sys.path.insert(0,str(Path.cwd()))
from tools.validate.__main__ import _rows
from tools.validate import ledger
archive=Path('docs/validation/evidence/F-DOM-019/2026-10-02-domain-management')
rows,findings,summary=_rows(SimpleNamespace(evidence=[],run_summary=str(archive/'run-summary.json')))
errors=ledger.gate(rows,summary);assert not errors,errors
assert len(summary['outcomes'])==117 and summary['clients']==['api']
assert sum(o['status']=='pass' and o['gate']=='ok' for o in summary['outcomes'])==116
assert sum(o['status']=='fail' and o['gate']=='known-failure' for o in summary['outcomes'])==1
metrics={'levels':dict(Counter(str(r.level) for r in rows)), 'fresh_passing_features':sum(r.proven is not None for r in rows),'fresh_failing_features':sum(bool(r.fresh_fail) for r in rows),'stale_features':sum(r.freshness=='stale' for r in rows),'below_target':sum(r.level<r.target for r in rows),'capped_features':sum(bool(r.capped_by) for r in rows)}
assert metrics['fresh_passing_features']==150 and metrics['fresh_failing_features']==9 and metrics['stale_features']==0,metrics
assert metrics['levels']=={'V0':26,'V1':86,'V2':64,'V3':92},metrics
promoted=['F-DOM-018','F-DOM-019','F-DOM-021','F-DOM-022','F-API-023']
for fid in promoted:
    row=next(r for r in rows if r.id==fid);assert str(row.level)=='V2' and row.proven is not None
assert {r.id for r in rows if r.fresh_fail}=={'F-MTX-030','F-CEC-010','F-API-015','F-DOM-001','F-API-019','F-DOM-009','F-API-020','F-DOM-019','F-API-023'}
assert all(findings[f].open for f in ('API-28','API-27','API-22','SEC-04','BE-36','BE-37'))
ledger.LEDGER_FILE.write_text(ledger.render(rows,findings,out_path=ledger.LEDGER_FILE,run_summary=summary))
(archive/'ledger-check.json').write_text(json.dumps({'gate':'ok','batch_records':117,'batch_passes':116,'batch_known_failures':1,'unlinked_regressions':0,'promoted_to_V2':promoted,**metrics},indent=2)+'\n')
print(json.dumps(metrics,indent=2));print('Gate OK; five features gain V2 and API-28 remains open.')
