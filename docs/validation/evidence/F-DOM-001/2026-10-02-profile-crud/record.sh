#!/bin/bash
set -eo pipefail
cd /tmp
apt-get update -qq
apt-get install -y -qq --no-install-recommends git-lfs
cd /work
git config --global core.filemode false
git config --global core.autocrlf true
git config --global core.trustctime false
git config --global core.checkStat minimal
export PYTHONUNBUFFERED=1
export GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"
test -z "$(git status --porcelain --untracked-files=no)"
/cache/venv/bin/python - "$@" <<'PY'
import asyncio,json,sys
from pathlib import Path
from tools.validate.runner import RunOptions
from tools.validate.registry import load_findings
from tools.validate.scenarios import discover
from build.profile_crud_ready import ReadyRunner
args=sys.argv[1:]
val=lambda flag: args[args.index(flag)+1]
mode=val('--mode');assert mode=='api'
ids=json.loads(Path(f'build/profile-crud-selection-{mode}.json').read_text())
sc=discover();selected=[sc[sid] for sid in ids]
selected.sort(key=lambda s:(bool(s.faults),s.id))
opts=RunOptions(target='sim',clients=('api',),out_dir=Path(f'build/profile-crud-image-{mode}').resolve(),
 evidence_dir=Path('docs/validation/evidence').resolve(),findings=load_findings(),
 hub_url=val('--hub-url'),sim_control_url=val('--sim-control-url'),hub_image_digest=val('--hub-image-digest'))
r=ReadyRunner(opts);r.configured_cec_transport='false'
out=asyncio.run(r.run(selected))
assert len(out)==len(ids)==51
expected={'profile_crud.post_scaler_arc','profile_crud.put_scaler_arc'}
assert sum(o.status=='pass' and o.gate=='ok' for o in out)==49
assert {o.scenario for o in out if o.status=='fail'}==expected
assert all(o.gate==('known-failure' if o.scenario in expected else 'ok') for o in out)
print(f'Completed {len(out)} profile checks against the packaged image.')
PY