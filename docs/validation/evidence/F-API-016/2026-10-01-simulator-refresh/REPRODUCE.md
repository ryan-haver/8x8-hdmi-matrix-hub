# Reproduce the refresh

The source and image identity are recorded in the adjacent summaries and stack
metadata. Use disposable fixture data and the recorded source checkout. These
checks target only the simulator.

Copy these files to the checkout's ignored `build` directory:

| Archived file | Destination |
| --- | --- |
| `stack.ps1` | `build/refresh-image.ps1` |
| `ha-stack.ps1` | `build/refresh-ha-image.ps1` |
| `record.sh` | `build/refresh-record.sh` |
| `ha-record.sh` | `build/refresh-ha-record.sh` |
| `uc-record.py` | `build/refresh-uc.py` |
| `stage-cli.ps1` | `build/refresh-stage-cli.ps1` |
| `selection-{api,browser,ha,uc}.json` | `build/refresh-selection-{api,browser,ha,uc}.json` |
| `finish.py` | `build/refresh-finish.py` |
| `compare-image.py` | `build/refresh-compare-image.py` |

Adjust the `$taskRoot` paths on another machine. Preserve LF shell-script line
endings. Required local images are `hdmi-matrix-hub-sim:deploy-test`,
`mcr.microsoft.com/playwright:v1.63.0-noble`, pinned Home Assistant
`homeassistant/home-assistant:2026.9.3`, and `docker:29-cli`. The harness uses
the `hdmi-hub-ui-cache` volume's `/cache/venv` and the
`hdmi-hub-ui-node-modules` volume. The former needs the repository dependencies,
Ruff, pytest and jsonschema; the latter needs the pinned Playwright package.

Build the hub with `docker build --target hub -t
hdmi-matrix-hub:wp-simulator-evidence-refresh .`. Run the image comparison with
`/app` from that image, this checkout mounted at `/checkout:ro`, and the
comparison helper under `/checkout/build`.

In PowerShell run `build/refresh-image.ps1 -TaskClient api`, then the same
harness with `-TaskClient browser`. Each gets fresh data and its own stack.
Run `build/refresh-stage-cli.ps1`, then
`build/refresh-ha-image.ps1 -TaskClient ha`. The HA runner mounts the Docker
socket to create its temporary real HA container. Its wrapper reaches HA's
published host port via `host.docker.internal` and waits for both hub transports
and the HA reboot button to be available after fault injection. These wrappers
change validation plumbing only.

For the scripted Remote, run `build/refresh-uc.py` with `/cache/venv/bin/python`
inside the Playwright image, with this checkout at `/work` and the cache volume
at `/cache`, working directory `/work`. Install Git LFS and apply the same Git
settings as `record.sh`; set `GIT_CONFIG_PARAMETERS` to
`'core.hooksPath=.githooks'`. The runner starts the simulator and actual legacy
hub source entry point as subprocesses. It does not claim a Docker-image test
for that client.

After all four runs, `build/refresh-finish.py` validates the exact selected
pairs, schemas, source identity and image IDs, merges summaries and links the
new records. Regenerate the ledger and run the validation gate with expected
clients `api,browser,ha,uc`. Stage every JSON record and all referenced PNGs
through Git LFS. The archived route inventory was produced by the full backend
suite with `ROUTE_COVERAGE_STRICT=1`.

The selection audit predates the CEC fix. Seven previously fresh reboot checks
were added to the recorded per-client selections after that shared driver
change. `cec-snapshot-check.json` preserves the comparison with the original
CEC failure. `ha-unavailable-diagnostic.txt` is the raw first HA reboot result,
retained as a harness diagnostic rather than a passing feature record.