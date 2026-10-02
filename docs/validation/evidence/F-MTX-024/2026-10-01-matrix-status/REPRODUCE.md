# Reproduce matrix status and cycling proof

Use the source commit and image recorded in `stack.json`, with a clean tracked
checkout. Build the image from that source or verify the retained image's 176
application files with `compare-image.py`. These scenarios use only disposable
simulator state and fixture data.

Copy the archived files into the ignored build directory:

| File | Destination |
| --- | --- |
| stack.ps1 | build/status-image.ps1 |
| record.sh | build/status-record.sh |
| selection-api.json | build/status-selection-api.json |
| compare-image.py | build/refresh-compare-image.py |
| finish.py | build/status-finish.py |
| ledger.py | build/status-ledger.py |

Adjust the checkout root in `stack.ps1` on another machine and preserve LF
shell line endings. Required local images are the recorded hub image,
`hdmi-matrix-hub-sim:deploy-test` (built by the deployment simulator fixture)
and `mcr.microsoft.com/playwright:v1.63.0-noble`. The `hdmi-hub-ui-cache` volume's
`/cache/venv` needs the repository dependencies, pytest, Ruff and jsonschema.
The stack also mounts the existing `hdmi-hub-ui-node-modules` volume; these
API-only scenarios do not open a browser.

Run in PowerShell:

```powershell
& .\build\status-image.ps1 -TaskClient api
```

The harness creates a unique network, simulator alias and fresh data volume,
publishes ephemeral loopback ports and leaves UC disabled. It waits for both matrix HTTP and Telnet connections before running the checks. The runner reaches
those ports through `host.docker.internal`. It installs Git LFS and uses the
Linux mount settings in `record.sh`, with
`GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"`. It rejects a dirty tracked
checkout, runs exactly the 183 selected scenarios, records evidence and the
summary, and requires every outcome to pass. The harness removes its own proof
containers, network and volume in `finally`.

Run `build/status-finish.py` with Linux Python from the checkout root. It
checks schemas, the selected scenarios, clean source, exact image identities
and results, then links the six features and archives the run. Its evidence
lists are empty in the recorded source. For a later checkout, use a new archive
and add links while preserving historical records; update this helper's empty
list assertion accordingly. It never promotes recorded baselines or caps.

Run `build/status-ledger.py` to generate the ledger and check the gate from the
same snapshot. The expected fresh-feature count is 128 at this checkpoint;
review that expectation for a later run. The ordinary `python -m tools.validate
ledger` and `check --run-summary <summary> --expect-clients api` commands use
the same ledger/gate functions. Stage the records, archive and handoff and
commit through `.githooks/pre-commit` (Ruff and the full backend suite).

Physical signals, displays, cables and Flic behavior remain separate hardware
proof. Preserve existing hardware findings and caps and use no real matrix address in this harness.
