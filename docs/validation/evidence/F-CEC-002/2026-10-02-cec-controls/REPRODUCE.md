# Reproduce HTTP CEC controls proof

Use the clean source commit and hub image recorded in `stack.json`. Verify the
retained image against the checkout with `compare-image.py` (176 application,
web, runtime and dependency files after line-ending normalization), or build
that source. This harness uses disposable simulator state and fixture data.

Copy these archive files into the ignored build directory:

| File | Destination |
| --- | --- |
| stack.ps1 | build/cec-image.ps1 |
| record.sh | build/cec-record.sh |
| selection-api.json | build/cec-selection-api.json |
| compare-image.py | build/refresh-compare-image.py |
| finish.py | build/cec-finish.py |
| ledger.py | build/cec-ledger.py |

Adjust the checkout root in the PowerShell script on another machine. Preserve
LF shell line endings. Required images are the recorded hub image,
`hdmi-matrix-hub-sim:deploy-test` (deployment simulator fixture), and
`mcr.microsoft.com/playwright:v1.63.0-noble`. The `hdmi-hub-ui-cache` volume must
contain `/cache/venv` with repository dependencies, pytest, Ruff and jsonschema.
The stack also mounts `hdmi-hub-ui-node-modules`; this API batch opens no browser.

Run in PowerShell:

```powershell
& .\build\cec-image.ps1 -TaskClient api
```

The harness creates unique container/network/volume names, fresh fixture data,
and ephemeral loopback ports. UC is disabled and `OREI_USE_TELNET_CEC=false`
selects HTTP frames. Both matrix HTTP and Telnet connections must be ready.
The runner reaches host ports through `host.docker.internal`. It installs Git
LFS and sets the Linux mount Git options in `record.sh`, including
`GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"`. Dirty tracked source is
rejected. Exactly 273 selected scenarios must pass with gate `ok`. The stack
removes its own containers, network and data volume in `finally`.

Run `build/cec-finish.py` with Linux Python from the checkout root. It audits
schemas, exact selected IDs, clean source, image identity and all checks, links
the 12 affected features while preserving existing evidence, and archives the
run. Run this additive helper once; on another checkpoint use a new archive
and avoid duplicate evidence links. `build/cec-ledger.py` generates the ledger
and checks the gate from one snapshot. It expects 135 fresh passing features,
one existing fresh failing feature (BE-36), zero stale features, and five new
CEC features at V2 at this checkpoint. Review those expectations on later runs.

The ordinary `python -m tools.validate ledger` and
`check --run-summary <summary> --expect-clients api` commands use the same
ledger/gate functions. Stage records, archive and handoff, then commit through
`.githooks/pre-commit` (Ruff and full backend pytest with strict route coverage).

CEC frame receipt and enable-flag readback are simulator software proof.
Physical power/navigation/playback/volume effects, Telnet transport and
capability reporting are outside this batch. No real matrix is contacted.