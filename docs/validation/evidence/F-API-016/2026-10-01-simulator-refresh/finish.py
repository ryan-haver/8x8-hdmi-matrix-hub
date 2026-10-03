import json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import jsonschema
from tools.validate.evidence import COMMITTED_EVIDENCE,iter_records
metas={c:json.loads(Path(f'build/refresh-image-stack-{c}.json').read_text(encoding='utf-8-sig')) for c in ('api','browser','ha')}
source=metas['api']['source_commit']; digest=metas['api']['digest']
assert all(m['source_commit']==source and m['digest']==digest for m in metas.values())
summaries=[json.loads(Path(f'build/refresh-image-{c}/run-summary.json').read_text()) for c in ('api','browser','ha')]
summaries.append(json.loads(Path('build/refresh-uc/run-summary.json').read_text()))
assert all(s['commit']['sha']==source and not s['commit']['dirty'] and not s['aborted'] for s in summaries)
outcomes=[o for s in summaries for o in s['outcomes']]
expected={(sid,c) for c in ('api','browser','ha','uc') for sid in json.loads(Path(f'build/refresh-selection-{c}.json').read_text())}
assert len(outcomes)==len(expected)==192
assert {(o['scenario'],o['client']) for o in outcomes}==expected
assert all(o['status']=='pass' and o['gate']=='ok' for o in outcomes)
combined={**summaries[0],'clients':['api','browser','ha','uc'],'finished':max(s['finished'] for s in summaries),'outcomes':outcomes}
Path('build/refresh-run-summary.json').write_text(json.dumps(combined,indent=2))
schema=json.loads(Path('docs/validation/evidence.schema.json').read_text())
records=[]; artifacts=[]
for r in iter_records([COMMITTED_EVIDENCE]):
 if r.sha != source: continue
 d=r.data
 jsonschema.Draft202012Validator(schema).validate(d)
 assert d['result']=='pass' and not d['commit']['dirty']
 assert (d['scenario'],d['client']) in expected
 assert d['environment']['hub']['image_digest']==(None if d['client']=='uc' else digest)
 if d['client']=='ha':
  assert d['environment']['client']['home_assistant']=='2026.9.3'
  assert d['environment']['client']['image_digest']
 records.append((r.path.relative_to(Path.cwd()).as_posix(),d))
 for ref in d['observations']['screenshots']:
  p=r.path.parent/ref; assert p.is_file(),p; artifacts.append(p.relative_to(Path.cwd()).as_posix())
assert len(records)==192
registry=Path('docs/validation/features.yaml');text=registry.read_text()
for fid in sorted({fid for _,d in records for fid in d['features']}):
 m=re.search(rf'(?ms)^- id: {re.escape(fid)}\n.*?(?=^- id: |\Z)',text);block=m.group()
 paths=sorted(p for p,d in records if fid in d['features'] and p not in block)
 addition=''.join(f'  - {p}\n' for p in paths)
 updated=block.replace('  evidence: []\n','  evidence:\n'+addition) if '  evidence: []\n' in block else block.replace('  evidence:\n','  evidence:\n'+addition,1)
 text=text[:m.start()]+updated+text[m.end():]
registry.write_text(text)
Path('build/refresh-records.json').write_text(json.dumps([p for p,_ in records],indent=2))
Path('build/refresh-artifacts.json').write_text(json.dumps(artifacts,indent=2))
scan=Path('build/refresh-scan');scan.mkdir(exist_ok=True)
for p,d in records: (scan/Path(p).name).write_bytes(Path(p).read_bytes())
print('Validated/linked',len(records),'clean records and',len(artifacts),'captures,',len({fid for _,d in records for fid in d['features']}),'features.')