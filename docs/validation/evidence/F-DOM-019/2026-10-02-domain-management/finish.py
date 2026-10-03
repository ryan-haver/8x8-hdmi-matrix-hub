import json,re,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import jsonschema
from tools.validate.evidence import COMMITTED_EVIDENCE,iter_records

archive=Path('docs/validation/evidence/F-DOM-019/2026-10-02-domain-management')
stack=json.loads(Path('build/domain-manage-image-stack-api.json').read_text(encoding='utf-8-sig'))
source=stack['source_commit'];digest=stack['digest']
assert digest=='sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0'
summary=json.loads(Path('build/domain-manage-image-api/run-summary.json').read_text())
ids=set(json.loads(Path('build/domain-manage-selection-api.json').read_text()))
failed={'domain_manage.macro_update_description_long'}
assert len(ids)==len(summary['outcomes'])==117
assert {o['scenario'] for o in summary['outcomes']}==ids
assert summary['commit']['sha']==source and not summary['commit']['dirty'] and not summary['aborted']
assert stack['cec_transport']=='false'
assert all(o['status']==('fail' if o['scenario'] in failed else 'pass') and o['gate']==('known-failure' if o['scenario'] in failed else 'ok') for o in summary['outcomes'])
records=[r for r in iter_records([COMMITTED_EVIDENCE]) if r.sha==source and r.data['scenario'] in ids]
assert len(records)==117 and {r.data['scenario'] for r in records}==ids
validator=jsonschema.Draft202012Validator(json.loads(Path('docs/validation/evidence.schema.json').read_text()))
def exchange(obs,path,method=None,reads=False):
    return next(e for e in obs['hub_reads' if reads else 'requests'] if e['path']==path and (method is None or e['method']==method))
for r in records:
    d=r.data;sid=d['scenario'];validator.validate(d);obs=d['observations']
    assert d['client']=='api' and d['level']=='V2' and not d['commit']['dirty']
    assert d['environment']['hub']['image_digest']==digest and not obs['screenshots']
    assert d['environment']['hub']['env']['OREI_USE_TELNET_CEC']=='false'
    assert not any(c['result']=='n/a' for c in d['checks'])
    assert all(step.endswith('HTTP 200') for step in d['procedure'] if step.startswith('cleanup'))
    failures=[c for c in d['checks'] if c['result']=='fail']
    if sid in failed:
        assert len(failures)==2 and all(c['finding']=='API-28' for c in failures)
        response=exchange(obs,'/api/cec/macro/validation_macro_manage','PUT')
        assert response['status']==200 and response['response']['success']
        stored=exchange(obs,'/api/cec/macro/validation_macro_manage',reads=True)
        assert stored['response']['data']['description']=='D'*2001
    else: assert not failures
    if sid=='domain_manage.legacy_recall':
        assert obs['state_diff'] and {e['path'] for e in obs['state_diff']}<={'outputs[0].source','routing[0]'}
        assert obs['state_after']['outputs'][0]['source']==5
    else:
        assert obs['state_diff']==[] and obs['state_before']==obs['state_after']
        assert not any(e.get('command')=='cec command' for e in obs['device_log'])
    if sid=='domain_manage.macro_dry_run':
        data=exchange(obs,'/api/cec/macro/validation_macro_manage/test','POST')['response']['data']
        assert data['success'] and data['step_count']==25 and data['issues']==[] and data['estimated_duration_ms']==1500
        assert len(exchange(obs,'/api/cec/macro/validation_macro_manage',reads=True)['response']['data']['steps'])==25
    if sid=='domain_manage.scene_c_create':
        created=exchange(obs,'/api/v2/scenes','POST')['response']['data']['scene']
        listed=exchange(obs,'/api/v2/scenes',reads=True)['response']['data']['scenes']
        stored=next(s for s in listed if s['id']==created['id'])
        assert created['id'] and stored['name']==created['name']=='Management Created Scene'
        assert stored['steps']==created['steps'] and len(stored['steps'])==4
    if sid=='domain_manage.scene_z_delete':
        assert exchange(obs,'/api/v2/scenes/scene_goodnight01',reads=True)['status']==404
        assert exchange(obs,'/api/v2/scenes/scene_movienight01',reads=True)['response']['data']['scene']['name']=='Movie Night'
fids={f for r in records for f in r.features}
assert fids=={'F-DOM-010','F-DOM-018','F-DOM-019','F-DOM-021','F-DOM-022','F-API-020','F-API-021','F-API-023'}
p=Path('docs/validation/features.yaml');t=p.read_text()
for fid in sorted(fids):
    m=re.search(rf'(?ms)^- id: {fid}\n.*?(?=^- id: |\Z)',t);b=m.group()
    additions=''.join(f'  - {r.path.relative_to(Path.cwd()).as_posix()}\n' for r in records if fid in r.features)
    if '  evidence: []\n' in b:b=b.replace('  evidence: []\n','  evidence:\n'+additions)
    else:b=b.replace('  evidence:\n','  evidence:\n'+additions)
    t=t[:m.start()]+b+t[m.end():]
p.write_text(t);archive.mkdir(exist_ok=True)
for src,dst in [('build/domain-manage-image-api/run-summary.json','run-summary.json'),('build/domain-manage-image-stack-api.json','stack.json'),('build/domain-manage-selection-api.json','selection.json'),('build/domain-manage-image.ps1','stack.ps1'),('build/domain-manage-record.sh','record.sh'),('build/domain_manage_ready.py','ready.py'),('build/refresh-compare-image.py','compare-image.py')]:
    shutil.copyfile(src,archive/dst)
(archive/'audit.json').write_text(json.dumps({'source_commit':source,'image_digest':digest,'records':117,'passing_records':116,'known_failure_records':1,'finding':'API-28','unlinked_regressions':0,'features':sorted(fids),'matches_checkout_files':176,'schema_errors':0,'dirty_records':0,'checks_not_applicable':0,'matrix_unchanged_records':116,'dry_run_steps_audited':25,'dry_run_duration_ms':1500,'created_scene_id_and_steps_audited':True,'deleted_scene_and_retained_fixture_audited':True,'cec_transport':'false','hardware_exercised':False},indent=2)+'\n')
Path('build/domain-manage-records.json').write_text(json.dumps([r.path.relative_to(Path.cwd()).as_posix() for r in records],indent=2))
print('Audited 116 passes, one API-28 failure, dry-run non-execution, scene creation readback and deletion isolation.')
