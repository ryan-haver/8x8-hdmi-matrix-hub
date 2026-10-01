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
/cache/venv/bin/python -m tools.validate run --client api --feature F-API-004 --feature F-API-014 --feature F-API-016 --feature F-API-017 --feature F-API-024 --feature F-API-026 --feature F-API-027 --feature F-API-028 --out build/rest-reads-image --record "$@"
/cache/venv/bin/python -m tools.validate check --run-summary build/rest-reads-image/run-summary.json --expect-clients api
