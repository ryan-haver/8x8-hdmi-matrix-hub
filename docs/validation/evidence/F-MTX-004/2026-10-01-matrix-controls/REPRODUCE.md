# Reproduce matrix-control proof

Use the recorded source commit, a clean tracked checkout and the image in
`stack.json`. Build the image from that source, or verify the retained image's
176 application files with `compare-image.py`. These scenarios target only
the simulator and disposable fixture data.

Copy the archived helpers into the ignored build directory:

| File | Destination |
| --- | --- |
| stack.ps1 | build/matrix-image.ps1 |
| record.sh | build/matrix-record.sh |
| selection-api.json | build/matrix-selection-api.json |
| compare-image.py | build/refresh-compare-image.py |
| finish.py | build/matrix-finish.py |
| ledger.py | build/matrix-ledger.py |

Adjust the checkout root in `stack.ps1` on another machine. Preserve LF shell
line endings. Required local images are the recorded hub image,
`hdmi-matrix-hub-sim:deploy-test` (the simulator deployment fixture builds this),
and `mcr.microsoft.com/playwright:v1.63.0-noble`. The
`hdmi-hub-ui-cache` volume's `/cache/venv` needs the repository's dependencies,
pytest, Ruff and jsonschema. `hdmi-hub-ui-node-modules` is reused by the stack
harness, although these API-only scenarios do not open a browser.

Run in PowerShell:

```powershell
& .\build\matrix-image.ps1 -TaskClient api
```

The stack uses a unique Docker network, simulator alias, fresh data volume,
loopback-published ephemeral ports and UC disabled. The runner reaches those
ports through `host.docker.internal`. Git LFS and Linux mount settings are
applied in the runner, with `GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"`.
It rejects a dirty tracked checkout, runs exactly the 29 selected scenarios,
writes committed evidence and a summary, and asserts that every outcome passes.
The stack harness removes its own containers, network and volume in `finally`.

Run `build/matrix-finish.py` under Linux Python from the checkout root. It
validates the selected records, their schemas, source/image identities and
results, links the six features and archives the run. The helper expects fresh
unlinked records and an empty evidence list for these features in the recorded
source; on a later checkout, use a new archive and link additional records
without replacing historical proof. It does not promote recorded baselines.

Run `build/matrix-ledger.py` from the same root to generate the ledger and
check the gate using the same snapshot. Its expected fresh-feature count is
112 at this checkpoint; review that expectation for later runs. The ordinary
`python -m tools.validate ledger` and `check --run-summary <summary>
--expect-clients api` commands use the same ledger/gate functions.

Stage every record, archive and handoff, and commit through
`.githooks/pre-commit` (Ruff plus the full backend suite). Physical behavior,
browser settings and physical Remote/HA name propagation are separate proof;
keep existing hardware caps. No real matrix address is used by this harness.
