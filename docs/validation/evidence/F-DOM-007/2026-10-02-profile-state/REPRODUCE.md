# Reproduce profile CEC, history and capture-current proof

Use the clean source commit and measured image in `stack.json`. The retained
hub image matches 176 application/web/runtime/dependency files after LF
normalization (`compare-image.py`). No real hardware is contacted.

Copy the archive files to the ignored build directory:

| Archive file | Destination |
| --- | --- |
| stack.ps1 | build/profile-state-image.ps1 |
| record.sh | build/profile-state-record.sh |
| ready.py | build/profile_state_ready.py |
| selection.json | build/profile-state-selection-api.json |
| compare-image.py | build/refresh-compare-image.py |
| finish.py | build/profile-state-finish.py |
| ledger.py | build/profile-state-ledger.py |

Adjust the PowerShell checkout root on another machine. Preserve LF shell
line endings. Required images are the recorded hub image,
`hdmi-matrix-hub-sim:deploy-test` and `mcr.microsoft.com/playwright:v1.63.0-noble`.
`hdmi-hub-ui-cache` must contain `/cache/venv` with repository dependencies,
pytest, Ruff and jsonschema. The stack also mounts `hdmi-hub-ui-node-modules`;
this API batch does not open a browser.

Run from a clean checkout in PowerShell:

```powershell
& .\build\profile-state-image.ps1
```

The stack uses unique containers/network/volume, fresh fixture data and
loopback ports. UC is disabled. Actual hub Docker environment is checked for
`OREI_USE_TELNET_CEC=false` and `OREI_STATUS_CACHE_TTL=0`. Disabling status
caching is deliberate: resolver/capture reads reach the seeded device and
the injected read failures. The readiness helper waits for both matrix
transports. External packaged hubs reconnect after faults; the runner's
generic restart procedure does not restart these externally managed hubs.

`record.sh` installs Git LFS, applies Linux mount Git settings, exports
`GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"` and rejects dirty tracked
source. Exactly 106 of 108 scenarios must pass. The two named capture read
failures must each retain two desired safeguards linked to API-27: HTTP 502
and no created profile. Do not replace those expectations with the observed
false success. The stack removes only its own resources in `finally`.

Run `build/profile-state-finish.py` with Linux Python from the checkout root.
It checks exact IDs, schemas, clean source, image/configuration identity,
matrix diffs, all 64 capture routing pairs, populated history timestamps/
order and both failed-read saved profiles. It adds seven feature evidence
links without dropping history and archives the original summary/helpers.
Run this additive helper once at a checkpoint; use a new archive and avoid
duplicate evidence links for later runs. `build/profile-state-ledger.py`
generates the ledger/gate from one snapshot. At this checkpoint it expects
143 fresh passing features, seven fresh failing features, zero stale
features and four features gaining V2. Review those assertions on later runs.
Ordinary `python -m tools.validate ledger` and
`check --run-summary <summary> --expect-clients api` use the same functions.

Commit through `.githooks/pre-commit` with Ruff, full backend pytest and
strict route coverage. C0 remains incomplete. This batch does not prove
browser behavior, restart persistence, seven-day expiry, target-string
semantic validation, physical CEC effects, disabled-stream capture or the
normal-cache capture behavior. Temporary profiles are deleted; the edited
fixture scene's name/steps/overrides are restored, while its new execution
history remains only in the disposable fixture volume.
