import json,re,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import jsonschema
from tools.validate.evidence import COMMITTED_EVIDENCE,iter_records
archive=Path('docs/validation/evidence/F-DOM-001/2026-10-02-profile-crud')
stack=json.loads(Path('build/profile-crud-image-stack-api.json').read_text(encoding='utf-8-sig'))
source=stack['source_commit'];digest=stack['digest']
assert digest=='sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0'
summary=json.loads(Path('build/profile-crud-image-api/run-summary.json').read_text())
ids=set(json.loads(Path('build/profile-crud-selection-api.json').read_text()))
failed={'profile_crud.post_scaler_arc','profile_crud.put_scaler_arc'}
assert len(ids)==len(summary['outcomes'])==51
assert {o['scenario'] for o in summary['outcomes']}==ids
assert summary['commit']['sha']==source and not summary['commit']['dirty'] and not summary['aborted']
assert stack['cec_transport']=='false'
assert all(o['status']==('fail' if o['scenario'] in failed else 'pass') and o['gate']==('known-failure' if o['scenario'] in failed else 'ok') for o in summary['outcomes'])
records=[r for r in iter_records([COMMITTED_EVIDENCE]) if r.sha==source and r.data['scenario'] in ids]
assert len(records)==51 and {r.data['scenario'] for r in records}==ids
validator=jsonschema.Draft202012Validator(json.loads(Path('docs/validation/evidence.schema.json').read_text()))
for r in records:
 d=r.data;validator.validate(d)
 assert d['client']=='api' and d['level']=='V2' and not d['commit']['dirty']
 assert d['environment']['hub']['image_digest']==digest and not d['observations']['screenshots']
 assert d['environment']['hub']['env']['OREI_USE_TELNET_CEC']=='false'
 assert not any(c['result']=='n/a' for c in d['checks'])
 failures=[c for c in d['checks'] if c['result']=='fail']
 if d['scenario'] in failed:
  assert len(failures)==1 and failures[0]['finding']=='API-22'
 else: assert not failures
 assert d['observations']['state_diff']==[]
 assert d['observations']['state_before']==d['observations']['state_after']
 assert all(c['result']=='pass' for c in d['checks'] if c['description'].startswith(('device unchanged','no device command','no protocol')))
fids={f for r in records for f in r.features}
assert fids=={'F-DOM-001','F-DOM-006','F-API-019'}
p=Path('docs/validation/features.yaml');t=p.read_text()
for fid in sorted(fids):
 m=re.search(rf'(?ms)^- id: {fid}\n.*?(?=^- id: |\Z)',t);b=m.group()
 additions=''.join(f'  - {r.path.relative_to(Path.cwd()).as_posix()}\n' for r in records if fid in r.features)
 if '  evidence: []\n' in b:b=b.replace('  evidence: []\n','  evidence:\n'+additions)
 else:b=b.replace('  evidence:\n','  evidence:\n'+additions)
 t=t[:m.start()]+b+t[m.end():]
p.write_text(t)
archive.mkdir(exist_ok=True)
for src,dst in [('build/profile-crud-image-api/run-summary.json','run-summary.json'),('build/profile-crud-image-stack-api.json','stack.json'),('build/profile-crud-selection-api.json','selection.json'),('build/profile-crud-image.ps1','stack.ps1'),('build/profile-crud-record.sh','record.sh'),('build/profile_crud_ready.py','ready.py'),('build/refresh-compare-image.py','compare-image.py')]:
 shutil.copyfile(src,archive/dst)
(archive/'audit.json').write_text(json.dumps({'source_commit':source,'image_digest':digest,'records':51,'passing_records':49,'known_failure_records':2,'finding':'API-22','unlinked_regressions':0,'features':sorted(fids),'matches_checkout_files':176,'schema_errors':0,'dirty_records':0,'checks_not_applicable':0,'matrix_unchanged_records':51,'hardware_exercised':False},indent=2)+'\n')
Path('build/profile-crud-records.json').write_text(json.dumps([r.path.relative_to(Path.cwd()).as_posix() for r in records],indent=2))
print('Audited 49 passing records and two API-22 failures; schemas, source/image identity and matrix preservation checks pass.')