# Reproduce scene and macro management proof

Use the clean source commit and image identity in `stack.json`. The image
matches 176 application/web/runtime/dependency files after LF normalization
(`compare-image.py`). No real hardware is contacted.

Copy the archive files to the ignored build directory:

| Archive file | Destination |
| --- | --- |
| stack.ps1 | build/domain-manage-image.ps1 |
| record.sh | build/domain-manage-record.sh |
| ready.py | build/domain_manage_ready.py |
| selection.json | build/domain-manage-selection-api.json |
| compare-image.py | build/refresh-compare-image.py |
| finish.py | build/domain-manage-finish.py |
| ledger.py | build/domain-manage-ledger.py |

Adjust the PowerShell checkout root on another machine. Preserve LF shell
line endings. Required images are the recorded hub image,
`hdmi-matrix-hub-sim:deploy-test` and `mcr.microsoft.com/playwright:v1.63.0-noble`.
`hdmi-hub-ui-cache` must contain `/cache/venv` with repository dependencies,
pytest, Ruff and jsonschema. The stack also mounts `hdmi-hub-ui-node-modules`;
this API batch does not open a browser.

Run from a clean checkout in PowerShell:

```powershell
& .\build\domain-manage-image.ps1
```

The stack uses unique containers/network/volume, fresh fixture data and
loopback ports. UC is disabled and actual Docker configuration is checked
for `OREI_USE_TELNET_CEC=false`. The default status cache TTL is retained.
The readiness helper waits for both matrix transports. No faults or hub
restarts are used in this batch.

`record.sh` installs Git LFS, applies Linux mount Git settings, exports
`GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"` and rejects dirty tracked
source. Exactly 116 of 117 scenarios must pass. The description edit case
must retain two failed safeguards linked to API-28: HTTP 400 rejection and
preservation of the prior description. Do not change the expectations to
accept the observed false success. The stack removes its own resources.

Run the entire selection sorted by scenario ID on fresh data. The runner
resets matrix state between scenarios but keeps hub data. Invalid scene
creates run before the one successful create; independent list reads verify
the created random ID and complete step sequence. The final delete consumes
the Good Night fixture and checks that Movie Night survives. These changes
exist only in the disposable volume. Other scene edits are restored and
temporary macros/profiles are deleted. Legacy recall is the only case that
changes matrix routing (Output 1 to Input 5).

Run `build/domain-manage-finish.py` with Linux Python from the checkout root.
It audits exact IDs, schemas, clean source, image identity, matrix state,
description persistence, dry-run non-execution and scene create/delete
readback. It adds eight feature evidence links while preserving history
and archives the summary/helpers. Run this additive helper once per
checkpoint; use a new archive and avoid duplicate links on later runs.
`build/domain-manage-ledger.py` generates the ledger/gate from one snapshot.
At this checkpoint it expects 150 fresh passing features, nine fresh failing
features, zero stale features and five features gaining V2. Review those
assertions on later runs. Ordinary `python -m tools.validate ledger` and
`check --run-summary <summary> --expect-clients api` use the same functions.

Commit through `.githooks/pre-commit` with Ruff, full backend pytest and
strict route coverage. Browser rendering, restart persistence, storage
failure handling, scene execution and physical CEC effects are outside
this management batch. API-20 dashboard layout and API-28 remain open.
