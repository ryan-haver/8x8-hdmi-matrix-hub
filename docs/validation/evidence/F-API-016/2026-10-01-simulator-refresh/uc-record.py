import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.validate.runner import Runner,RunOptions
from tools.validate.scenarios import discover
from tools.validate.registry import load_findings
ids=json.loads(Path('build/refresh-selection-uc.json').read_text());sc=discover()
opts=RunOptions(target='sim',clients=('uc',),out_dir=Path('build/refresh-uc').resolve(),
 evidence_dir=Path('docs/validation/evidence').resolve(),findings=load_findings())
r=Runner(opts); outcomes=asyncio.run(r.run([sc[sid] for sid in ids]))
assert len(outcomes)==len(ids)
assert all(o.status=='pass' and o.gate=='ok' for o in outcomes),[(o.scenario,o.status,o.reason) for o in outcomes if o.status!='pass']
print('Refreshed',len(outcomes),'scripted Remote checks through the real driver.')