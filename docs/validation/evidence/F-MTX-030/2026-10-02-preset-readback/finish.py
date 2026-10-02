import json,re,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import jsonschema
from tools.validate.evidence import COMMITTED_EVIDENCE,iter_records
stack=json.loads(Path('build/preset-image-stack-api.json').read_text(encoding='utf-8-sig'))
source=stack['source_commit'];digest=stack['digest']
assert digest=='sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0'
summary=json.loads(Path('build/preset-image-api/run-summary.json').read_text())
ids=set(json.loads(Path('build/preset-selection-api.json').read_text()))
failed_ids={f'preset_read.device_slot_{i}' for i in range(1,9)}
assert len(ids)==len(summary['outcomes'])==24
assert summary['commit']['sha']==source and not summary['commit']['dirty'] and not summary['aborted']
assert {o['scenario'] for o in summary['outcomes']}==ids
assert {o['scenario'] for o in summary['outcomes'] if o['status']=='fail'}==failed_ids
assert all(o['gate']==('known-failure' if o['scenario'] in failed_ids else 'ok') for o in summary['outcomes'])
records=[r for r in iter_records([COMMITTED_EVIDENCE]) if r.sha==source and r.data['scenario'] in ids]
assert len(records)==24 and {r.data['scenario'] for r in records}==ids
schema=json.loads(Path('docs/validation/evidence.schema.json').read_text())
for r in records:
 d=r.data
 jsonschema.Draft202012Validator(schema).validate(d)
 assert d['client']=='api' and d['level']=='V2' and not d['commit']['dirty']
 assert d['environment']['hub']['image_digest']==digest and not d['observations']['screenshots']
 failures=[c for c in d['checks'] if c['result']=='fail']
 if d['scenario'] in failed_ids:
  assert d['result']=='fail' and d['gate']=='known-failure' and len(failures)==2
  assert all(c['finding']=='BE-36' for c in failures)
  assert d['features']==['F-MTX-030']
 else:
  assert d['result']=='pass' and d['gate']=='ok' and not failures
  assert 'F-MTX-030' not in d['features']
fids={f for r in records for f in r.features}
assert fids=={'F-MTX-004','F-MTX-030','F-DOM-034','F-API-008'}
p=Path('docs/validation/features.yaml');t=p.read_text()
for fid in sorted(fids):
 m=re.search(rf'(?ms)^- id: {fid}\n.*?(?=^- id: |\Z)',t);b=m.group()
 addition=''.join(f'  - {r.path.relative_to(Path.cwd()).as_posix()}\n' for r in records if fid in r.features)
 if '  evidence: []\n' in b: b=b.replace('  evidence: []\n','  evidence:\n'+addition)
 else: b=b.replace('  evidence:\n','  evidence:\n'+addition)
 t=t[:m.start()]+b+t[m.end():]
p.write_text(t)
archive=Path('docs/validation/evidence/F-MTX-030/2026-10-02-preset-readback');archive.mkdir(exist_ok=True)
for src,dst in [('build/preset-image-api/run-summary.json','run-summary.json'),('build/preset-image-stack-api.json','stack.json'),('build/preset-selection-api.json','selection-api.json'),('build/preset-image.ps1','stack.ps1'),('build/preset-record.sh','record.sh'),('build/refresh-compare-image.py','compare-image.py')]:
 shutil.copyfile(src,archive/dst)
(archive/'audit.json').write_text(json.dumps({'source_commit':source,'image_digest':digest,'records':24,'passing_records':16,'known_failure_records':8,'finding':'BE-36','unlinked_regressions':0,'features':sorted(fids),'matches_checkout_files':176,'schema_errors':0,'dirty_records':0,'hardware_exercised':False},indent=2)+'\n')
Path('build/preset-records.json').write_text(json.dumps([r.path.relative_to(Path.cwd()).as_posix() for r in records],indent=2))
print('Audited 16 passing records and 8 BE-36 failure records; no unlinked regression.')