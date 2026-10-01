import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from tools.validate.evidence import COMMITTED_EVIDENCE, iter_records
from tools.validate.gitinfo import changed_since
from tools.validate.ledger import freshness
from tools.validate.scenarios import discover
scenarios=discover()
latest={}
for r in iter_records([COMMITTED_EVIDENCE]):
    key=(r.data['scenario'],r.data['client'])
    if key not in latest or r.started > latest[key].started:
        latest[key]=r
pairs=[]; unavailable=[]
for key,r in sorted(latest.items()):
    if r.result != 'pass' or freshness(r) == 'fresh':
        continue
    sid,client=key
    changes=changed_since(r.sha)
    if not changes or 'src/telnet_client.py' not in changes or 'src/telnet_client.py' not in r.data['covers']:
        continue
    if client not in ('api','browser'):
        unavailable.append({'scenario':sid,'client':client,'prior_record':r.path.as_posix()}); continue
    sc=scenarios.get(sid)
    assert sc and client in sc.clients and 'sim' in sc.targets,key
    pairs.append({'scenario':sid,'client':client,'prior_record':r.path.as_posix(), 'features':r.features})
selected=sorted({p['scenario'] for p in pairs})
expected=[{'scenario':sid,'client':client} for sid in selected for client in ('api','browser') if client in scenarios[sid].clients]
Path('build/refresh-selection.json').write_text(json.dumps(selected,indent=2))
Path('build/refresh-selection-audit.json').write_text(json.dumps({'selected':pairs,'expected':expected,'other_clients':unavailable},indent=2))
print('Refreshing',len(pairs),'stale pairs,',len(selected),'scenarios;',len(expected),'runs:',dict(Counter(p['client'] for p in expected)))
print('Additional clients with stale transport evidence:',dict(Counter(p['client'] for p in unavailable)))
print('Features covered:',len({fid for p in pairs for fid in p['features']}))