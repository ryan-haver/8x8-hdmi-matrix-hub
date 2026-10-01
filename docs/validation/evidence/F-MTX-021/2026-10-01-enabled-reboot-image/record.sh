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
import json, sys
from pathlib import Path
from tools.validate.__main__ import main
args = ['run', '--client', 'api', '--client', 'browser', '--out', 'build/reboot-image', '--record', *sys.argv[1:]]
for sid in json.loads(Path('build/reboot-selection.json').read_text()):
    args += ['--scenario', sid]
raise SystemExit(main(args))
PY
/cache/venv/bin/python -m tools.validate check --run-summary build/reboot-image/run-summary.json --expect-clients api,browser
/cache/venv/bin/python build/reboot-check-lifecycle.py
