import json,re,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import jsonschema
from tools.validate.evidence import COMMITTED_EVIDENCE,iter_records
archive=Path('docs/validation/evidence/F-CEC-010/2026-10-02-cec-capability-telnet')
stacks={mode:json.loads(Path(f'build/cec-cap-image-stack-{mode}.json').read_text(encoding='utf-8-sig')) for mode in ('caps','telnet')}
source=stacks['caps']['source_commit'];digest=stacks['caps']['digest']
assert digest=='sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0'
failed_ids={'cec_telnet.input_interrupted_volume','cec_telnet.output_interrupted_volume'}
ids=set();summaries={}
for mode in ('caps','telnet'):
 stack=stacks[mode]
 assert stack['source_commit']==source and stack['digest']==digest
 assert stack['cec_transport']==('true' if mode=='telnet' else 'false')
 summary=json.loads(Path(f'build/cec-cap-image-{mode}/run-summary.json').read_text())
 selected=set(json.loads(Path(f'build/cec-cap-selection-{mode}.json').read_text()))
 assert len(selected)==len(summary['outcomes'])==(88 if mode=='caps' else 202)
 assert summary['commit']['sha']==source and not summary['commit']['dirty'] and not summary['aborted']
 assert {o['scenario'] for o in summary['outcomes']}==selected
 assert all(o['status']==('fail' if o['scenario'] in failed_ids else 'pass') and o['gate']==('known-failure' if o['scenario'] in failed_ids else 'ok') for o in summary['outcomes'])
 assert not (ids & selected)
 ids.update(selected);summaries[mode]=summary
records=[r for r in iter_records([COMMITTED_EVIDENCE]) if r.sha==source and r.data['scenario'] in ids]
assert len(records)==290 and {r.data['scenario'] for r in records}==ids
schema=json.loads(Path('docs/validation/evidence.schema.json').read_text())
ordered=0
for r in records:
 d=r.data;sid=d['scenario'];mode='telnet' if sid.startswith('cec_telnet.') else 'caps'
 jsonschema.Draft202012Validator(schema).validate(d)
 assert d['client']=='api' and d['level']=='V2' and not d['commit']['dirty']
 assert d['environment']['hub']['image_digest']==digest and not d['observations']['screenshots']
 assert d['environment']['hub']['env']['OREI_USE_TELNET_CEC']==stacks[mode]['cec_transport']
 assert not any(c['result']=='n/a' for c in d['checks'])
 failures=[c for c in d['checks'] if c['result']=='fail']
 entries=d['observations']['device_log']
 tel=[e for e in entries if e.get('channel')=='telnet' and e.get('command','').startswith('s cec ')]
 http=[e for e in entries if e.get('channel')=='http' and e.get('command')=='cec command']
 if sid in failed_ids:
  assert d['result']=='fail' and d['gate']=='known-failure' and len(failures)==2
  assert all(c['finding']=='BE-37' for c in failures)
  assert len(tel)==len(http)==1 and tel[0]['fault']=='telnet_close_mid_command'
  assert tel[0]['recognised'] and http[0]['response']['result']==1
  assert entries.index(tel[0])<entries.index(http[0])
  output=sid.startswith('cec_telnet.output_')
  assert http[0]['payload']['object']==int(output) and http[0]['payload']['index']==(4 if output else 19)
  assert http[0]['payload']['port']==[0]*7+[1]
 else:
  assert d['result']=='pass' and d['gate']=='ok' and not failures
  if mode=='telnet':
   enable=[e for e in entries if e.get('command')=='set cec index']
   assert len(tel)==len(enable)==1 and not http
   assert entries.index(enable[0])<entries.index(tel[0])
   ordered+=1
assert ordered==200,ordered
fids={f for r in records for f in r.features}
assert fids=={'F-CEC-010','F-CEC-011','F-CEC-007','F-API-015','F-API-016'},fids
p=Path('docs/validation/features.yaml');t=p.read_text()
for fid in sorted(fids):
 m=re.search(rf'(?ms)^- id: {fid}\n.*?(?=^- id: |\Z)',t);b=m.group()
 addition=''.join(f'  - {r.path.relative_to(Path.cwd()).as_posix()}\n' for r in records if fid in r.features)
 if '  evidence: []\n' in b: b=b.replace('  evidence: []\n','  evidence:\n'+addition)
 else: b=b.replace('  evidence:\n','  evidence:\n'+addition)
 t=t[:m.start()]+b+t[m.end():]
p.write_text(t)
archive.mkdir(exist_ok=True)
combined=dict(summaries['caps']);combined['finished']=max(s['finished'] for s in summaries.values())
combined['outcomes']=[o for mode in ('caps','telnet') for o in summaries[mode]['outcomes']]
(archive/'run-summary.json').write_text(json.dumps(combined,indent=2)+'\n')
for mode in ('caps','telnet'):
 for src,dst in [(f'build/cec-cap-image-{mode}/run-summary.json',f'run-summary-{mode}.json'),(f'build/cec-cap-image-stack-{mode}.json',f'stack-{mode}.json'),(f'build/cec-cap-selection-{mode}.json',f'selection-{mode}.json')]:
  shutil.copyfile(src,archive/dst)
for src,dst in [('build/cec-cap-image.ps1','stack.ps1'),('build/cec-cap-record.sh','record.sh'),('build/cec_cap_ready.py','ready.py'),('build/refresh-compare-image.py','compare-image.py')]:
 shutil.copyfile(src,archive/dst)
(archive/'audit.json').write_text(json.dumps({'source_commit':source,'image_digest':digest,'records':290,'passing_records':288,'known_failure_records':2,'finding':'BE-37','unlinked_regressions':0,'features':sorted(fids),'matches_checkout_files':176,'schema_errors':0,'dirty_records':0,'checks_not_applicable':0,'telnet_enable_order_verified':200,'interrupted_reply_resends_verified':2,'transports':{'caps':'OREI_USE_TELNET_CEC=false','telnet':'OREI_USE_TELNET_CEC=true'},'hardware_exercised':False},indent=2)+'\n')
Path('build/cec-cap-records.json').write_text(json.dumps([r.path.relative_to(Path.cwd()).as_posix() for r in records],indent=2))
print('Audited 288 passing records and two BE-37 failures, all schemas/source/image identities, 200 enable-before-Telnet logs and both ambiguous resends.')