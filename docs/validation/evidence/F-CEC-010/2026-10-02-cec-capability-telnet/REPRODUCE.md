# Reproduce CEC capability and Telnet baseline proof

Use the clean source commit and measured image in `stack-caps.json` and
`stack-telnet.json`. Verify the retained image with `compare-image.py` (176
application/web/runtime/dependency files after LF normalization), or build
that source. Every operation uses disposable simulator state and fixture data.

Copy the following archive files to the ignored build directory:

| Archive file | Destination |
| --- | --- |
| stack.ps1 | build/cec-cap-image.ps1 |
| record.sh | build/cec-cap-record.sh |
| ready.py | build/cec_cap_ready.py |
| selection-caps.json | build/cec-cap-selection-caps.json |
| selection-telnet.json | build/cec-cap-selection-telnet.json |
| compare-image.py | build/refresh-compare-image.py |
| finish.py | build/cec-cap-finish.py |
| ledger.py | build/cec-cap-ledger.py |

Adjust the PowerShell checkout root on another machine. Preserve LF shell
line endings. Required images are the recorded hub image,
`hdmi-matrix-hub-sim:deploy-test` (deployment simulator fixture), and
`mcr.microsoft.com/playwright:v1.63.0-noble`. `hdmi-hub-ui-cache` must contain
`/cache/venv` with repository dependencies, pytest, Ruff and jsonschema. The
stack also mounts `hdmi-hub-ui-node-modules`; this API batch opens no browser.

Run in PowerShell, with no tracked source edits between runs:

```powershell
& .\build\cec-cap-image.ps1 -TaskMode caps
& .\build\cec-cap-image.ps1 -TaskMode telnet
```

Each invocation creates unique containers/network/volume, fresh fixture data
and ephemeral loopback ports. The runs can use independent stacks concurrently.
UC is disabled. The harness verifies the actual Docker CEC environment before
recording it: false for capability reads, true for Telnet. The readiness helper
waits for both matrix HTTP and Telnet connections, including after injected
faults. The runner accesses host ports through `host.docker.internal`. Original
summaries remain separate by mode. External hubs reconnect after faults; the
runner's generic procedure line saying restart does not describe an actual
restart of those packaged containers.

`record.sh` installs Git LFS, applies the Linux mount Git options, and exports
`GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"`. Dirty tracked source is
rejected. All 88 capability cases must pass. The 202 Telnet cases must have
exactly 200 passes and the two named BE-37 known failures. Do not relabel them
as passes. Each stack removes its own containers/network/data volume in `finally`.

Run `build/cec-cap-finish.py` with Linux Python from the checkout root. It
checks both original summaries, exact IDs, schemas, clean source, image and
transport identities, enable-before-Telnet ordering in all 200 healthy cases,
and both interrupted-reply resends. It links five features without dropping
historical evidence and archives the original and combined summaries. Run
this additive helper once; use a new archive and avoid duplicate links on a
later checkpoint. `build/cec-cap-ledger.py` generates the ledger and gate from
one snapshot. At this checkpoint it expects 137 fresh passing features,
three fresh failing features (BE-36/BE-37), zero stale features and the two new
CEC features at V2. Review checkpoint assertions for later runs.

Ordinary `python -m tools.validate ledger` and
`check --run-summary <summary> --expect-clients api` use the same ledger/gate
functions. Commit the evidence/archive/handoff through `.githooks/pre-commit`
with Ruff, full backend pytest and strict route coverage. Known failures stay
open in C0. Actual device acknowledgement shapes, physical CEC effects and
scaler writes remain hardware proof. No real matrix is contacted.