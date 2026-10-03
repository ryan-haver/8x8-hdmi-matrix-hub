import json,re,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import jsonschema
from tools.validate.evidence import COMMITTED_EVIDENCE,iter_records
stack=json.loads(Path('build/output-image-stack-api.json').read_text(encoding='utf-8-sig'))
source=stack['source_commit'];digest=stack['digest']
summary=json.loads(Path('build/output-image-api/run-summary.json').read_text())
ids=set(json.loads(Path('build/output-selection-api.json').read_text()))
assert len(ids)==len(summary['outcomes'])==62
assert summary['commit']['sha']==source and not summary['commit']['dirty'] and not summary['aborted']
assert {o['scenario'] for o in summary['outcomes']}==ids
assert all(o['status']=='pass' and o['gate']=='ok' for o in summary['outcomes'])
schema=json.loads(Path('docs/validation/evidence.schema.json').read_text())
records=[r for r in iter_records([COMMITTED_EVIDENCE]) if r.sha==source and r.data['scenario'] in ids]
assert len(records)==62
for r in records:
 d=r.data
 jsonschema.Draft202012Validator(schema).validate(d)
 assert d['client']=='api' and d['level']=='V2' and d['result']=='pass' and not d['commit']['dirty']
 assert d['environment']['hub']['image_digest']==digest
 assert not d['observations']['screenshots']
 assert all(c['result']!='fail' for c in d['checks'])
fids={f for r in records for f in r.features}
assert fids=={f'F-MTX-{i:03}' for i in range(8,15)}
p=Path('docs/validation/features.yaml');t=p.read_text()
for fid in sorted(fids):
 m=re.search(rf'(?ms)^- id: {fid}\n.*?(?=^- id: |\Z)',t);b=m.group()
 assert '  evidence: []\n' in b
 addition='  evidence:\n'+''.join(f'  - {r.path.relative_to(Path.cwd()).as_posix()}\n' for r in records if fid in r.features)
 b=b.replace('  evidence: []\n',addition)
 t=t[:m.start()]+b+t[m.end():]
p.write_text(t)
archive=Path('docs/validation/evidence/F-MTX-008/2026-10-01-output-edid');archive.mkdir(exist_ok=True)
for a,b in [('build/output-image-api/run-summary.json','run-summary.json'),('build/output-image-stack-api.json','stack.json'),
 ('build/output-selection-api.json','selection-api.json'),('build/output-image.ps1','stack.ps1'),
 ('build/output-record.sh','record.sh'),('build/refresh-compare-image.py','compare-image.py')]:
 shutil.copyfile(a,archive/b)
(archive/'audit.json').write_text(json.dumps({'source_commit':source,'image_digest':digest,'result':'pass',
 'records':len(records),'features':sorted(fids),'matches_checkout_files':176,
 'schema_errors':0,'dirty_records':0,'failed_checks':0,'hardware_exercised':False},indent=2)+'\n')
Path('build/output-records.json').write_text(json.dumps([r.path.relative_to(Path.cwd()).as_posix() for r in records],indent=2))
print('Validated and linked 62 clean packaged-image records for seven output/EDID features.')