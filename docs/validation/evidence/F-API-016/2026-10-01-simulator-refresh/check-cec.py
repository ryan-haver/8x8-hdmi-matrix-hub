import json
from pathlib import Path
old_path=Path('docs/validation/evidence/F-API-016/2026-10-01-V2-72cc71dc-writes.cec_output_enable-api.json')
old=json.loads(old_path.read_text()); summary=json.loads(Path('build/refresh-image-api/run-summary.json').read_text())
new_out=next(o for o in summary['outcomes'] if o['scenario']=='writes.cec_output_enable')
new_path=Path(new_out['record']); new=json.loads(new_path.read_text())
assert old['result']=='fail' and new['result']=='pass'
assert old['observations']['state_before']['inputs'][0]['cec_enabled']==0
assert old['observations']['state_after']['inputs'][0]['cec_enabled']==1
assert new['observations']['state_before']['inputs'][0]['cec_enabled']==0
assert new['observations']['state_after']['inputs'][0]['cec_enabled']==0
logs=new['observations']['device_log']
sets=[e for e in logs if e.get('command')=='set cec index' and e.get('channel')=='http']
assert len(sets)==1
write=sets[0]
assert any(e.get('command')=='get cec status' and e['t']<write['t'] for e in logs)
state=new['observations']['state_before']
assert write['payload']['inputindex']==[p['cec_enabled'] for p in state['inputs']]
expected=[p['cec_enabled'] for p in state['outputs']]; expected[7]=1
assert write['payload']['outputindex']==expected
Path('build/refresh-cec-snapshot-check.json').write_text(json.dumps({'result':'pass','before_fix_record':old_path.as_posix(),
 'after_fix_record':new_path.as_posix(),'source_commit':summary['commit']['sha'],
 'preserved_input_1':0,'current_snapshot_read_before_write':True,'port_write_count':1},indent=2))
print('CEC write now preserves the current flags in the originally failing sequence.')