# Unfolded Circle core-simulator: evaluation

> **Date:** 2026-09-25 · **Work package:** WP-B1 (UC-21) · **Source:** the pinned clone `reference/unfoldedcircle/core-simulator` (`5104764`, "build: v0.74.1 release", 2026-07-15; fetch with `python tools/uc_reference.py`), the sibling `core-api` spec, and Docker Hub / GitHub as of 2026-09-25.
>
> **Question:** can the real Remote core software serve as a stronger V3 client than our scripted Remote (`tools/uc_remote_sim.py`), locally and in CI (`docs/validation/VALIDATION_PLAN.md` §4, audit §7)?
>
> **Answer:** it is technically usable, but the licence is not clear. **It is not integrated.** Use it locally by hand. Ask Unfolded Circle before running it in CI.

## 1. What it is

- **What it is:** the Remote's core service ("remote-core") built for x86 as a developer tool. From `README.md:6-8`: it "simulates the functionality of the core-services running on the embedded device and provides the same Core-APIs as a real device… using the same code base". `README.md:12` labels it "a preview version and work-in-progress".
- **What the image contains:**
  - the core
  - the Web Configurator (`/configurator`)
  - the REST Core-API (`/api`, 8080 http / 8443 https)
  - the WebSocket Core-API (`/ws`)
  - a WS test console (`/ws.html`)
- **What the image does not contain:** the Qt remote UI. It ships only in the Linux VM.
- **Model:** a Remote 3 by default (`UC_MODEL=UCR3`).
- **Versions:**
  - The pin is v0.74.1: Core 0.74.1 and Web-Configurator 2.1.0 (`CHANGELOG.md`). The CHANGELOG version is the Docker image version.
  - Docker Hub is ahead of the repo docs. `latest` = `0.81.2-bt`, pushed 2026-09-12.
  - No file maps an image version to the Integration-API version it implements. At runtime, `GET /api/pub/version` reports it.

## 2. How it is distributed

| | |
| --- | --- |
| Image | `unfoldedcircle/core-simulator` on Docker Hub. Anonymous pull, no account needed. About 80 MB compressed. |
| Tags | 245 tags: `-alpha` 0.6.0–0.32.0 (2022–2023), `-beta` 0.33–0.44 (to 2024-06), `-bt` since 0.45. Recent: 0.74.1-bt (2026-07-14), 0.75.0-bt (08-07), 0.80.0-bt (09-01), 0.81.2-bt = `latest` (09-12). About 7 releases in 2 months, so pin tag + digest. |
| Architectures | **linux/amd64 only**. arm64 (Apple silicon, Raspberry Pi) needs emulation (`docker/README.md:60-61`). |
| Compose | `docker/docker-compose.yml`: ports 8080/8443; volumes `simulator-data:/data`, `./ui-env`, `./upload`; env `UC_MODEL`, `RUST_LOG`, `UC_API_MSG_TRACING`, `UC_TOKEN_PATH`; optional `network_mode: host`. It also bundles integration-hass, Home Assistant (privileged) and speech-to-phrase, none of which we need. |
| Linux VM | OVA on Google Drive (VirtualBox 7, Ubuntu 22.04, 2 cores / 4 GB), including the Qt UI (`linux-vm/README.md`). Not usable in CI. |
| GitHub releases | Only old ones (v0.21.3-alpha, 2023). Releases are Docker tags. |
| Built-in credentials | Basic auth `web-configurator:1234`, a published admin API key (`README.md:51-89`). |

## 3. Licence status (read literally)

- **No licence is declared for the simulator.**
  - The repo has no `LICENSE` file, and GitHub reports `license: null`.
  - Docker Hub carries no terms.
- **What `README.md:91-104` says:**
  - The API specs and docs are CC BY-SA 4.0.
  - Code *examples* are Apache-2.0.
  - "Remote-core simulator and all graphics copyright © Unfolded Circle ApS 2022-2023."
  - **"The remote-core simulator is provided for development use only. It is prohibited to use the remote-core simulator application as part of other products, services and like."**
- **What `licenses/` holds:** only third-party notices (Rust crates, web-configurator dependencies, Qt, SQLite, …). It grants no rights to the simulator itself.
- **What this means for us:**
  - Pulling and running it to develop and test our driver is "development use" on a plain reading.
  - Running it in our public CI is neither clearly allowed nor forbidden.
  - Redistributing it is not allowed: no mirroring or re-pushing the image, and no bundling it into our artifacts or docs.
  - **Before any CI job: get written confirmation from Unfolded Circle** (e.g. an issue on `unfoldedcircle/core-simulator` or developer support).

## 4. Can it drive our driver?

Yes. The Remote core connects to an *external* integration driver exactly as a Remote 3 does.

### Discovery

mDNS does not cross Docker's default bridge network (`docker/README.md:12-13,148-162`). Use one of these instead:

- register the driver manually over REST (below), or
- run with `--network host` (Linux only).

### Driver side

- The driver must bind a reachable address, not `127.0.0.1` when the core runs in a container. For us that means `UC_INTEGRATION_INTERFACE=0.0.0.0` (or the host IP) and `UC_INTEGRATION_HTTP_PORT`.
- Set `UC_DISABLE_MDNS_PUBLISH=true`. These are the variables `HubProcess(mode="uc")` in `tools/validate/stack.py` already sets.

### Core REST API

Endpoints from `core-api/core-api/rest/UCR-core-openapi.yaml`. Auth is `-u web-configurator:1234`; `/api/pub/*` needs none.

- `GET /api/pub/health_check`, `GET /api/pub/version`
- `POST /api/intg/drivers`: manual registration, `{driver_id, driver_url: "ws://host:port", name, enabled}`. The driver must be running at that moment.
- `POST /api/intg/setup` `{driver_id, setup_data}`
  - poll `GET /api/intg/setup/{driver_id}`
  - answer pages with `PUT … {input_values}` or `{confirm}`
  - states: NEW / SETUP / WAIT_USER_ACTION / OK / ERROR
- `GET /api/intg/instances`, then `POST /api/intg/instances/{id}/entities` with `[]`, which configures all available entities.
- `GET /api/entities?integration_ids=…`: configured ids carry the instance prefix, so read them back instead of guessing.
- `PUT /api/entities/{entity_id}/command` `{cmd_id, params}` and `GET /api/entities/{entity_id}`: commands and state as the Remote UI sees them.

### Environments

| Environment | Does it work? | How |
| --- | --- | --- |
| GitHub Actions `ubuntu-latest` | Technically yes: amd64, Docker available, no privileges needed for the core container | `docker run --network host` with `driver_url=ws://127.0.0.1:<port>`, or `--add-host host.docker.internal:host-gateway` with the driver bound to `0.0.0.0` |
| Windows / macOS with Docker Desktop | Yes | `ws://host.docker.internal:<port>`, or run the hub image and the simulator on one compose network. `network_mode: host` does not behave the same there. |

Startup time and memory use are not documented. Measure them by polling `health_check`.

## 5. What it would add over the scripted Remote

The scripted Remote (`tools/uc_remote_sim.py`) sends messages as the pinned AsyncAPI spec describes them. The real core adds what the spec does not say:

- the exact order and timing of `connect`, `subscribe_events`, standby and reconnects
- how the core reacts to our bugs, e.g. marking entities unavailable after UC-01's 1011 close, or a setup that ends in ERROR (BE-02)
- the Web Configurator's setup quirks that ucapi works around (`sleep(0.5)`)
- entity-id prefixing
- the entity state the Remote UI would show

This is the stronger V3 evidence the validation plan asks for.

## 6. Recommendation

1. **Now (WP-B1):** do not integrate. The licence is not clear, and it is not trivial: Docker, driver registration and a multi-step REST setup. The scripted Remote covers the protocol in CI (`tests/uc`, the `uc` validation client).
2. **Local, by hand (allowed as development use):** run the smoke test below against a branch before real-Remote sessions (HIL-E) to catch integration surprises early.
3. **Later (WP-B3 or HIL-E prep), once Unfolded Circle confirms CI use in writing:** add an opt-in `workflow_dispatch`/nightly job, not a PR gate.
   - Pin `unfoldedcircle/core-simulator:<tag>@sha256:<digest>` and only pull it.
   - The job runs the steps below and uploads `docker logs`.
   - Run the §7 cases as a second client once `HubClient` exists (audit §7, "V3 addition").

### Smoke test (local)

```bash
# 1. Core (Linux host networking; on Docker Desktop publish 8080 and use host.docker.internal instead)
docker run -d --name ucsim --network host -e UC_MODEL=UCR3 unfoldedcircle/core-simulator:0.81.2-bt
curl -sf http://localhost:8080/api/pub/health_check && curl -s http://localhost:8080/api/pub/version

# 2. The matrix simulator (off the core's 8080/8443), then our hub with the integration, the way
#    tools/validate/stack.py HubProcess(mode="uc") starts it (tools/dev_stack.py only runs API-only mode):
python -m tools.simulator --https-port 9443 --telnet-port 2323 --control-port 9444 &
UC_ENABLED=true USE_MODULAR=false UC_INTEGRATION_INTERFACE=0.0.0.0 UC_INTEGRATION_HTTP_PORT=9095 \
  UC_DISABLE_MDNS_PUBLISH=true REST_API_PORT=8090 OREI_TELNET_PORT=2323 \
  UC_CONFIG_HOME=.dev-uc MATRIX_DATA_DIR=.dev-uc python run.py &

# 3. Register, set up, configure entities, send a command
A='-u web-configurator:1234 -H Content-Type:application/json'
curl $A -X POST localhost:8080/api/intg/drivers \
     -d '{"driver_id":"hdmi_matrix_dev","driver_url":"ws://127.0.0.1:9095","name":{"en":"HDMI Matrix (dev)"},"enabled":true}'
curl $A -X POST localhost:8080/api/intg/setup -d '{"driver_id":"hdmi_matrix_dev","setup_data":{"host":"127.0.0.1","port":9443}}'
curl $A localhost:8080/api/intg/setup/hdmi_matrix_dev          # today: ERROR (BE-02), although setup worked
curl $A localhost:8080/api/intg/instances                       # -> instance id
curl $A -X POST localhost:8080/api/intg/instances/<id>/entities -d '[]'
curl $A 'localhost:8080/api/entities?integration_ids=<id>'      # real, prefixed entity ids
curl $A -X PUT localhost:8080/api/entities/<media_player id>/command -d '{"cmd_id":"select_source","params":{"source":"PS5"}}'
# check the matrix simulator: curl localhost:9444/_sim/state
docker rm -f ucsim
```

Expect today's known bugs to show up here as well: setup reports ERROR (BE-02), and a `remote.*_cec` power command drops the integration (UC-01).
