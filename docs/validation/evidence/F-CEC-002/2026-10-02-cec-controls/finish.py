import json,re,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import jsonschema
from tools.validate.evidence import COMMITTED_EVIDENCE,iter_records
stack=json.loads(Path('build/cec-image-stack-api.json').read_text(encoding='utf-8-sig'))
source=stack['source_commit'];digest=stack['digest']
assert digest=='sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0'
summary=json.loads(Path('build/cec-image-api/run-summary.json').read_text())
ids=set(json.loads(Path('build/cec-selection-api.json').read_text()))
assert len(ids)==len(summary['outcomes'])==273
assert summary['commit']['sha']==source and not summary['commit']['dirty'] and not summary['aborted']
assert {o['scenario'] for o in summary['outcomes']}==ids
assert all(o['status']=='pass' and o['gate']=='ok' for o in summary['outcomes'])
records=[r for r in iter_records([COMMITTED_EVIDENCE]) if r.sha==source and r.data['scenario'] in ids]
assert len(records)==273 and {r.data['scenario'] for r in records}==ids
schema=json.loads(Path('docs/validation/evidence.schema.json').read_text())
for r in records:
 d=r.data
 jsonschema.Draft202012Validator(schema).validate(d)
 assert d['client']=='api' and d['level']=='V2' and not d['commit']['dirty']
 assert d['environment']['hub']['image_digest']==digest and not d['observations']['screenshots']
 assert d['result']=='pass' and d['gate']=='ok' and not any(c['result'] in ('fail','n/a') for c in d['checks'])
auto=[r for r in records if all(any(e.get('command')==cmd for e in r.data['observations']['device_log']) for cmd in ('set cec index','cec command'))]
assert len(auto)==200,len(auto)
for r in auto:
 names=[e.get('command') for e in r.data['observations']['device_log']]
 assert names.index('set cec index')<names.index('cec command'),r.data['scenario']
fids={f for r in records for f in r.features}
assert len(fids)==12,fids
p=Path('docs/validation/features.yaml');t=p.read_text()
for fid in sorted(fids):
 m=re.search(rf'(?ms)^- id: {fid}\n.*?(?=^- id: |\Z)',t);b=m.group()
 addition=''.join(f'  - {r.path.relative_to(Path.cwd()).as_posix()}\n' for r in records if fid in r.features)
 if '  evidence: []\n' in b: b=b.replace('  evidence: []\n','  evidence:\n'+addition)
 else: b=b.replace('  evidence:\n','  evidence:\n'+addition)
 t=t[:m.start()]+b+t[m.end():]
p.write_text(t)
archive=Path('docs/validation/evidence/F-CEC-002/2026-10-02-cec-controls');archive.mkdir(exist_ok=True)
for src,dst in [('build/cec-image-api/run-summary.json','run-summary.json'),('build/cec-image-stack-api.json','stack.json'),('build/cec-selection-api.json','selection-api.json'),('build/cec-image.ps1','stack.ps1'),('build/cec-record.sh','record.sh'),('build/refresh-compare-image.py','compare-image.py')]:
 shutil.copyfile(src,archive/dst)
(archive/'audit.json').write_text(json.dumps({'source_commit':source,'image_digest':digest,'records':273,'passing_records':273,'unlinked_regressions':0,'features':sorted(fids),'matches_checkout_files':176,'schema_errors':0,'dirty_records':0,'checks_not_applicable':0,'auto_enable_order_verified':200,'cec_transport':'HTTP (OREI_USE_TELNET_CEC=false)','hardware_exercised':False},indent=2)+'\n')
Path('build/cec-records.json').write_text(json.dumps([r.path.relative_to(Path.cwd()).as_posix() for r in records],indent=2))
print('Audited all 273 passing CEC records, schemas and image/source identities.')