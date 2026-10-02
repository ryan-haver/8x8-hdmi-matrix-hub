import json,sys
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
sys.path.insert(0,str(Path.cwd()))
from tools.validate.__main__ import _rows
from tools.validate import ledger
archive=Path('docs/validation/evidence/F-MTX-004/2026-10-01-matrix-controls')
rows,findings,summary=_rows(SimpleNamespace(evidence=[],run_summary=str(archive/'run-summary.json')))
errors=ledger.gate(rows,summary)
assert not errors,errors
assert summary['clients']==['api'] and len(summary['outcomes'])==29
assert all(o['status']=='pass' for o in summary['outcomes'])
metrics={'levels':dict(Counter(str(r.level) for r in rows)),
 'fresh_passing_features':sum(r.proven is not None for r in rows),
 'stale_features':sum(r.freshness=='stale' for r in rows),
 'below_target':sum(r.level<r.target for r in rows),
 'capped_features':sum(bool(r.capped_by) for r in rows),
 'selected':[{ 'id':r.id,'level':str(r.level),'proven':str(r.proven),'capped_by':r.capped_by}
             for r in rows if r.id in {f'F-MTX-{i:03}' for i in (4,18,19,20,22,23)}]}
assert metrics['stale_features']==0,metrics
assert metrics['fresh_passing_features']==112,metrics
ledger.LEDGER_FILE.write_text(ledger.render(rows,findings,out_path=ledger.LEDGER_FILE,run_summary=summary))
(archive/'ledger-check.json').write_text(json.dumps({'gate':'ok','known_failures':0,**metrics},indent=2)+'\n')
print(json.dumps(metrics,indent=2));print('Generated ledger and validation gate OK from the same registry/evidence snapshot.')