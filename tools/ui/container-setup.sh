#!/usr/bin/env bash
# Prepare the pinned Playwright container (mcr.microsoft.com/playwright:v1.63.0-noble)
# to run the UI suites: a Python venv with the hub + simulator dependencies and
# the npm dev dependencies. Used by tools/ui/run-in-container.mjs (local) and
# the `ui` job in .github/workflows/ci.yml, so both run the same setup.
#
# Env:
#   UI_CACHE_DIR   where the venv and pip cache live (default /cache; a named
#                  Docker volume locally, a throw-away dir in CI)
# Prints the venv python path as the last line: E2E_PYTHON=<path>
set -euo pipefail

cd "$(dirname "$0")/../.."
CACHE="${UI_CACHE_DIR:-/cache}"
VENV="$CACHE/venv"
export PIP_CACHE_DIR="$CACHE/pip"
export npm_config_cache="$CACHE/npm"
mkdir -p "$CACHE"

# --- Python: the image has python3 3.12 but no pip/ensurepip ---------------
req_hash=$(cat requirements.txt requirements-dev.txt tools/ui/container-setup.sh | sha256sum | cut -d' ' -f1)
if [ ! -x "$VENV/bin/python" ] || [ "$(cat "$VENV/.req-hash" 2>/dev/null)" != "$req_hash" ]; then
    echo "[ui-setup] creating Python venv in $VENV"
    rm -rf "$VENV"
    python3 -m venv --without-pip "$VENV"
    # Pin the official bootstrap to an immutable commit and verify its bytes.
    bootstrap_sha=fb24e693bab954209a063d90953621412ccad4a500905a726286e038f508ddf6
    if [ ! -f "$CACHE/get-pip.py" ] || ! echo "$bootstrap_sha  $CACHE/get-pip.py" | sha256sum --check --status; then
        python3 -c "import urllib.request; urllib.request.urlretrieve('https://raw.githubusercontent.com/pypa/get-pip/f6f644156f23dfe9acc06e7b9ca75eee311f2e37/public/get-pip.py', '$CACHE/get-pip.py')"
    fi
    echo "$bootstrap_sha  $CACHE/get-pip.py" | sha256sum --check --status
    "$VENV/bin/python" "$CACHE/get-pip.py" --quiet --no-setuptools --no-wheel 'pip==26.2.1'
    "$VENV/bin/python" -m pip install --quiet --require-hashes -r requirements-dev.txt
    "$VENV/bin/python" -m pip check
    echo "$req_hash" > "$VENV/.req-hash"
else
    echo "[ui-setup] Python venv up to date ($VENV)"
fi

# --- Node: install only when package-lock.json changed ------------------------
lock_hash=$(sha256sum package-lock.json | cut -d' ' -f1)
if [ ! -d node_modules/@playwright/test ] || [ "$(cat node_modules/.lock-hash 2>/dev/null)" != "$lock_hash" ]; then
    echo "[ui-setup] npm ci"
    npm ci --no-audit --no-fund --loglevel=error
    echo "$lock_hash" > node_modules/.lock-hash
else
    echo "[ui-setup] node_modules up to date"
fi

echo "E2E_PYTHON=$VENV/bin/python"
