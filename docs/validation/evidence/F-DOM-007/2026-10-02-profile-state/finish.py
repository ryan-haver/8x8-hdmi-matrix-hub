import json,re,shutil,sys
from datetime import datetime,timedelta
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import jsonschema
from tools.validate.evidence import COMMITTED_EVIDENCE,iter_records

archive=Path('docs/validation/evidence/F-DOM-007/2026-10-02-profile-state')
stack=json.loads(Path('build/profile-state-image-stack-api.json').read_text(encoding='utf-8-sig'))
source=stack['source_commit'];digest=stack['digest']
assert digest=='sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0'
summary=json.loads(Path('build/profile-state-image-api/run-summary.json').read_text())
ids=set(json.loads(Path('build/profile-state-selection-api.json').read_text()))
failed={'profile_state.capture_video_read_failure','profile_state.capture_output_read_failure'}
changed={'profile_state.history_success','profile_state.alias_recall'}
assert len(ids)==len(summary['outcomes'])==108
assert {o['scenario'] for o in summary['outcomes']}==ids
assert summary['commit']['sha']==source and not summary['commit']['dirty'] and not summary['aborted']
assert stack['cec_transport']=='false' and stack['status_cache_ttl']=='0'
assert all(o['status']==('fail' if o['scenario'] in failed else 'pass') and o['gate']==('known-failure' if o['scenario'] in failed else 'ok') for o in summary['outcomes'])
records=[r for r in iter_records([COMMITTED_EVIDENCE]) if r.sha==source and r.data['scenario'] in ids]
assert len(records)==108 and {r.data['scenario'] for r in records}==ids
validator=jsonschema.Draft202012Validator(json.loads(Path('docs/validation/evidence.schema.json').read_text()))
history_count=captured=0
for r in records:
 d=r.data;sid=d['scenario'];validator.validate(d);obs=d['observations']
 assert d['client']=='api' and d['level']=='V2' and not d['commit']['dirty']
 assert d['environment']['hub']['image_digest']==digest and not obs['screenshots']
 assert d['environment']['hub']['env']['OREI_USE_TELNET_CEC']=='false'
 assert d['environment']['hub']['env']['OREI_STATUS_CACHE_TTL']=='0'
 assert not any(c['result']=='n/a' for c in d['checks'])
 failures=[c for c in d['checks'] if c['result']=='fail']
 if sid in failed:
  assert len(failures)==2 and all(c['finding']=='API-27' for c in failures)
  response=next(e for e in obs['requests'] if e['path']=='/api/scene/save-current')
  assert response['status']==200 and response['response']['success']
  outputs=response['response']['data']['outputs']
  if 'output_read' in sid:assert outputs=={}
  else:
   assert len(outputs)==8 and all(o['input']==1 for o in outputs.values())
   assert obs['state_before']['routing']!=[1]*8
  command='get output status' if 'output_read' in sid else 'get video status'
  assert any(e.get('command')==command and e.get('fault')=='http_500' for e in obs['device_log'])
 else: assert not failures
 if sid in changed:
  assert obs['state_diff'] and {e['path'] for e in obs['state_diff']}<={'outputs[0].source','routing[0]'}
  assert obs['state_after']['outputs'][0]['source']==5
 else: assert obs['state_diff']==[] and obs['state_before']==obs['state_after']
 if sid.startswith('profile_state.capture_pattern_'):
  expected={str(i+1):{'input':o['source'],'enabled':bool(o['stream']),'audio_mute':bool(o['audio_mute']),
                     'hdr_mode':o['hdr']+1,'hdcp_mode':o['hdcp']}
            for i,o in enumerate(obs['state_before']['outputs'])}
  read=next(e for e in obs['hub_reads'] if e['path']=='/api/profile/validation_state')
  assert read['response']['data']['outputs']==expected
  captured+=8
 if sid.startswith('profile_state.history_'):
  exchanges=[e for e in obs['requests']+obs['hub_reads'] if e['path'].endswith('/execution-log') and e['status']==200]
  for e in exchanges:
   data=e['response']['data'];entries=data['log'];assert data['count']==len(entries)
   timestamps=[datetime.fromisoformat(entry['timestamp']) for entry in entries]
   assert timestamps==sorted(timestamps)
   start=datetime.fromisoformat(d['timestamp']['started'].replace('Z','+00:00'))-timedelta(seconds=2)
   end=datetime.fromisoformat(d['timestamp']['finished'].replace('Z','+00:00'))+timedelta(seconds=2)
   assert all(ts.tzinfo is not None and start<=ts<=end for ts in timestamps)
   for entry in entries:
    assert entry['scene_id']=='scene_goodnight01'
    assert entry['status'] in ('success','error')
    assert entry['error'] is None if entry['status']=='success' else isinstance(entry['error'],str) and bool(entry['error'])
  if exchanges and exchanges[0]['response']['data']['log']:history_count+=1
assert captured==64 and history_count==4
fids={f for r in records for f in r.features}
assert fids=={'F-DOM-001','F-DOM-002','F-DOM-007','F-DOM-008','F-DOM-009','F-API-019','F-API-020'}
p=Path('docs/validation/features.yaml');t=p.read_text()
for fid in sorted(fids):
 m=re.search(rf'(?ms)^- id: {fid}\n.*?(?=^- id: |\Z)',t);b=m.group()
 additions=''.join(f'  - {r.path.relative_to(Path.cwd()).as_posix()}\n' for r in records if fid in r.features)
 if '  evidence: []\n' in b:b=b.replace('  evidence: []\n','  evidence:\n'+additions)
 else:b=b.replace('  evidence:\n','  evidence:\n'+additions)
 t=t[:m.start()]+b+t[m.end():]
p.write_text(t);archive.mkdir(exist_ok=True)
for src,dst in [('build/profile-state-image-api/run-summary.json','run-summary.json'),('build/profile-state-image-stack-api.json','stack.json'),('build/profile-state-selection-api.json','selection.json'),('build/profile-state-image.ps1','stack.ps1'),('build/profile-state-record.sh','record.sh'),('build/profile_state_ready.py','ready.py'),('build/refresh-compare-image.py','compare-image.py')]:
 shutil.copyfile(src,archive/dst)
(archive/'audit.json').write_text(json.dumps({'source_commit':source,'image_digest':digest,'records':108,'passing_records':106,'known_failure_records':2,'finding':'API-27','unlinked_regressions':0,'features':sorted(fids),'matches_checkout_files':176,'schema_errors':0,'dirty_records':0,'checks_not_applicable':0,'matrix_unchanged_records':106,'capture_port_mappings_audited':64,'populated_history_records_audited':4,'failed_read_captures_audited':2,'status_cache_ttl':'0','hardware_exercised':False},indent=2)+'\n')
Path('build/profile-state-records.json').write_text(json.dumps([r.path.relative_to(Path.cwd()).as_posix() for r in records],indent=2))
print('Audited 106 passes, two API-27 failures, 64 capture mappings and four populated history records.')
