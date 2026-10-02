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
import asyncio, json, sys
from pathlib import Path
from tools.validate.runner import Runner, RunOptions
from tools.validate.registry import load_findings
from tools.validate.scenarios import discover
args=sys.argv[1:]
client=args[args.index('--client')+1]
if client == 'ha':
    from tools.validate.clients import CLIENTS
    from tools.validate.clients.ha import HomeAssistantClient
    class HostHomeAssistantClient(HomeAssistantClient):
        def _start_container(self):
            super()._start_container()
            # Published HA ports belong to the Docker host, outside this runner.
            self.url=self.url.replace('127.0.0.1', 'host.docker.internal')
            self.setup_steps.append('validation runner reaches published HA port via host.docker.internal')
    CLIENTS['ha']=HostHomeAssistantClient

val=lambda flag: args[args.index(flag)+1]
ids=json.loads(Path(f'build/cec-selection-{client}.json').read_text())
sc=discover()
selected=[sc[sid] for sid in ids]
# Run cases that leave the hub offline last; every client gets fresh fixture data.
selected.sort(key=lambda s: (s.restart_after, s.id))
opts=RunOptions(target='sim',clients=(client,),out_dir=Path(f'build/cec-image-{client}').resolve(),
 evidence_dir=Path('docs/validation/evidence').resolve(),findings=load_findings(),
 hub_url=val('--hub-url'),sim_control_url=val('--sim-control-url'),hub_image_digest=val('--hub-image-digest'))
r=Runner(opts)
out=asyncio.run(r.run(selected))
assert len(out)==len(ids),(len(out),len(ids))
assert len(out)==273
assert all(o.status=='pass' and o.gate=='ok' for o in out),[(o.scenario,o.status,o.gate,o.failed_checks) for o in out if o.status!='pass']
print(f'Completed {len(out)} {client} checks against the packaged image.')
PY
