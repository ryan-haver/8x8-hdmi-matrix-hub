# Reproduce profile CRUD and visibility proof

Use the clean source commit and image digest in `stack.json`. The retained
hub image matches 176 application/web/runtime/dependency files after LF
normalization (`compare-image.py`). These scenarios use disposable simulator
state and fresh hub fixture data; they never contact real hardware.

Copy archive files into the ignored build directory:

| Archive file | Destination |
| --- | --- |
| stack.ps1 | build/profile-crud-image.ps1 |
| record.sh | build/profile-crud-record.sh |
| ready.py | build/profile_crud_ready.py |
| selection.json | build/profile-crud-selection-api.json |
| compare-image.py | build/refresh-compare-image.py |
| finish.py | build/profile-crud-finish.py |
| ledger.py | build/profile-crud-ledger.py |

Adjust the PowerShell checkout root on another machine. Preserve LF shell
line endings. Required images: the recorded hub image,
`hdmi-matrix-hub-sim:deploy-test`, and
`mcr.microsoft.com/playwright:v1.63.0-noble`. The `hdmi-hub-ui-cache` volume
must provide `/cache/venv` with repository dependencies, pytest, Ruff and
jsonschema. The stack also mounts `hdmi-hub-ui-node-modules`; no browser is
opened by this API batch.

Run from a clean checkout in PowerShell:

```powershell
& .\build\profile-crud-image.ps1
```

The helper creates unique containers/network/volume, fresh fixture data and
loopback ports. UC is disabled and the actual hub environment is checked for
`OREI_USE_TELNET_CEC=false`. Readiness waits for both matrix connections. No
faults or restarts occur in this batch. CRUD saves are verified through a
separate API read in the running hub; persistence across restart is not proved.
Every temporary profile is deleted during scenario cleanup.

`record.sh` installs Git LFS, applies Linux mount Git settings and exports
`GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"`. Dirty tracked source is
rejected. Exactly 49 of the 51 scenarios must pass. The create/edit scaler-ARC
checks must retain one API-22 known failure each. Do not turn those desired
round-trip expectations into passing checks for discarded fields. The stack
removes only its own resources in `finally`.

Run `build/profile-crud-finish.py` with Linux Python from the checkout root.
It audits exact IDs, schemas, source/image identity, unchanged matrix snapshots
and both API-22 failures, adds feature evidence links and archives the original
summary and helpers. This is an additive helper: run it once at a checkpoint,
and use a new archive and avoid duplicate links for later evidence.
`build/profile-crud-ledger.py` generates the ledger/gate from one snapshot.
It expects 139 fresh passing features, five fresh failing features, zero stale
features and two domain features gaining V2; review those assertions for later
runs. Ordinary `python -m tools.validate ledger` and
`check --run-summary <summary> --expect-clients api` use the same functions.

Commit source and evidence through `.githooks/pre-commit`: Ruff, full backend
pytest and strict route coverage. API-20 layout reconciliation, API-22 saved
scaler/ARC fields and SEC-04 remain open. C0 is not complete. Browser rendering,
restart/storage failures and exhaustive invalid request shapes are outside
this proof batch.