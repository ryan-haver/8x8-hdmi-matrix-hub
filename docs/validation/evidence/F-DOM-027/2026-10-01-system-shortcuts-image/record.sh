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
git status --porcelain --untracked-files=no
test -z "$(git status --porcelain --untracked-files=no)"
/cache/venv/bin/python -m tools.validate run --client api --client browser --feature F-DOM-027 --feature F-DOM-028 --out build/system-shortcuts-image --record "$@"
/cache/venv/bin/python -m tools.validate check --run-summary build/system-shortcuts-image/run-summary.json --expect-clients api,browser
