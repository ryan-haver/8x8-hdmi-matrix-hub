# Docker Deployment Guide

One image runs the whole hub. The **core** (matrix control, REST API, web UI at
`/ui`, kiosk at `/kiosk`) always runs. **Integrations** are switched on with
environment variables; a disabled integration is not imported and opens no
port. Today there is one: the Unfolded Circle Remote 3 integration
(`UC_ENABLED=true`, WebSocket port 9095).

## Quick start (Docker Compose)

```bash
git clone https://github.com/ryan-haver/8x8-hdmi-matrix-hub.git && cd 8x8-hdmi-matrix-hub
mkdir -p data && sudo chown 1000:1000 data     # Linux: the container runs as UID 1000
MATRIX_HOST=192.168.1.50 docker compose up -d  # your matrix's IP address
docker compose logs -f
```

Open `http://<docker-host>:8080/ui` (web UI) or `http://<docker-host>:8080/kiosk`
(kiosk). `curl http://<docker-host>:8080/api/health` answers `"status": "healthy"`.

Settings can live in a `.env` file next to `docker-compose.yml` instead of the
command line:

```ini
# .env
MATRIX_HOST=192.168.1.50      # the matrix's IP address
MATRIX_DATA_DIR=./data        # host folder for persistent data (default ./data)
HUB_PORT=8080                 # host port of the web UI / REST API (default 8080)
LOG_LEVEL=INFO
HUB_HOST_IP=192.168.1.20      # this machine's LAN IP; only needed for the Remote 3 files below
```

Stop with `docker compose down`. Upgrade with `git pull && docker compose up -d --build`.

## Compose files

| Command | What runs | Networking |
| --- | --- | --- |
| `docker compose up -d` | core only | bridge, `HUB_PORT` → 8080 |
| `docker compose -f docker-compose.yml -f docker-compose.uc-host.yml up -d` | core + Remote 3 integration, discovered by mDNS (**recommended for the Remote**) | host network: 8080 (`HUB_PORT`) and 9095 directly on the host |
| `docker compose -f docker-compose.yml -f docker-compose.uc-bridge.yml up -d` | core + Remote 3 integration, registered by URL | bridge, `HUB_PORT` → 8080, `UC_HOST_PORT` (9095) → 9095 |

Both Remote 3 files need `HUB_HOST_IP` (this machine's LAN address) and refuse to
start without it. To avoid typing the `-f` options, put them in `.env`:
`COMPOSE_FILE=docker-compose.yml:docker-compose.uc-host.yml` (use `;` as the
separator on Windows).

The old profiles (`--profile api-only`, `--profile full`) are gone: there is one
service and `docker compose up -d` starts it.

## Remote 3 integration and networking

The Remote 3 finds integrations by mDNS (`_uc-integration._tcp`) and then opens a
WebSocket to them. mDNS multicast does not leave a Docker bridge network, so there
are two ways to run the integration in Docker.

### Host networking (recommended)

`docker-compose.uc-host.yml` sets `network_mode: host`, `UC_ENABLED=true` and
`UC_INTEGRATION_INTERFACE=$HUB_HOST_IP`. The integration listens on
`HUB_HOST_IP:9095` and mDNS announces that address, so the Remote shows
"HDMI Matrix" under *Integrations → Add new*. Host networking needs a Linux Docker
host; on Docker Desktop enable it under *Settings → Resources → Network*, or use
bridge mode. If the Remote shows the integration with a wrong host name, also set
`UC_MDNS_LOCAL_HOSTNAME` (read by the `ucapi` library).

### Bridge networking (no mDNS)

`docker-compose.uc-bridge.yml` publishes port 9095 (`UC_HOST_PORT`), switches mDNS
off (`UC_DISABLE_MDNS_PUBLISH=true`) and sets
`UC_DRIVER_URL=ws://$HUB_HOST_IP:$UC_HOST_PORT`, the address the integration
advertises in its metadata. The Remote does not discover the integration by
itself; register it once through the Remote's REST API (user `web-configurator`,
password = the web configurator PIN; curl prompts for it):

```bash
curl -u web-configurator -H 'Content-Type: application/json' \
  http://<remote-ip>/api/intg/drivers \
  -d '{"driver_id": "hdmi_matrix", "driver_url": "ws://192.168.1.20:9095"}'
```

Then set it up in the web configurator like a discovered integration.
(`driver_url` is the only required field; the Remote fetches the rest from the
integration. The registration API is described in the pinned core-api docs,
`doc/integration-driver/driver-registration.md`; see `docs/vendor/UNFOLDED_CIRCLE.md`.)

### The matrix address with the Remote integration on

With `UC_ENABLED=true` the Remote's setup asks for the matrix address and the
integration saves it in `/data/config_state.json`; that saved address is the one
the whole hub uses (`MATRIX_HOST` is ignored in this mode and the log says so).
Until the Remote has been set up, the web UI has no matrix. Moving the matrix
address to the core is planned (docs/audits/UC_INTEGRATION_AUDIT.md §5).

## Environment variables

run.py reads these; deprecated names still work and one warning at start-up lists
them. Compose-only variables (`MATRIX_DATA_DIR` as the host folder, `HUB_PORT`,
`HUB_HOST_IP`, `UC_HOST_PORT`, `HUB_CONTAINER_NAME`) only change the compose files.

| Variable | Deprecated names | Default | Effect |
| --- | --- | --- | --- |
| `MATRIX_HOST` | `OREI_HOST` | the address a Remote setup saved, else `192.168.0.100` | Matrix IP/host name (core only; see above for UC) |
| `MATRIX_PORT` | `OREI_PORT` | `443` | Matrix HTTPS port |
| `API_PORT` | `REST_API_PORT`, `OREI_API_PORT` | `8080` | REST API, web UI and kiosk port (in the container) |
| `DATA_DIR` | `MATRIX_DATA_DIR` (in the container) | image: `/data`; local: the modules' defaults | Persistent data directory; must be writable |
| `LOG_LEVEL` | | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `UC_ENABLED` | | `false` | `true` starts the Remote 3 integration; otherwise `ucapi` is not imported and 9095 stays closed |
| `UC_INTEGRATION_HTTP_PORT` | `UC_PORT` | `9095` (driver.json) | Integration WebSocket port |
| `UC_INTEGRATION_INTERFACE` | | all interfaces | Bind address, also the address mDNS announces: set it to the LAN IP |
| `UC_DISABLE_MDNS_PUBLISH` | `UC_DISABLE_MDNS` | `false` | `true`: do not announce by mDNS (bridge networking) |
| `UC_DRIVER_URL` | | not set | `ws://host:port` advertised to the Remote (bridge networking); must start with `ws://` or `wss://` |
| `UC_CONFIG_HOME` | | `DATA_DIR` | Integration state (`config_state.json`, `driver.lock`) and the profile/macro/scene files |
| `OREI_USER`, `OREI_PASSWORD` | | `Admin` / `admin` | Matrix login |
| `OREI_VERIFY_SSL` | | `false` | Verify the matrix's TLS certificate |
| `OREI_TELNET_PORT`, `OREI_USE_TELNET_CEC` | | `23` / `false` | Matrix Telnet options |
| `POLLING_INTERVAL`, `POLLING_ENABLED` | | `30` / `true` | Status polling while a Remote is connected (UC mode) |

No longer used (logged and ignored): `USE_MODULAR` (the mode follows
`UC_ENABLED`), `WEBUI_ENABLED` (the web UI and kiosk are part of the core and
always served), `REST_API_ENABLED=false` (the REST API is the core).
A bad port number or a `UC_DRIVER_URL` that is not a WebSocket URL stops the hub
with exit code 2 and a message saying what to fix.

## Persistent storage

Everything the hub saves is under `/data` in the container, mounted from the host
folder `MATRIX_DATA_DIR` (compose default `./data`):

| File in `/data` | What it contains |
| --- | --- |
| `device_settings.json` | Input/output names, icons, colours |
| `themes.json`, `ui_preferences.json` | Theme and web UI preferences |
| `system_shortcuts.json`, `dashboard_layout.json` | Shortcuts and dashboard cards |
| `profiles.json`, `cec_macros.json`, `scenes.json` | Profiles, CEC macros, legacy scenes |
| `config_state.json`, `driver.lock` | Remote 3 integration: matrix address and names from its setup; single-instance lock |

The container runs as UID/GID 1000 (build-time `--build-arg APP_UID=… APP_GID=…`
to change it). A host folder must be writable by that user: `sudo chown -R
1000:1000 ./data`. If it is not, the hub stops at start-up with a message naming
the folder and the chown command. When Docker creates a missing bind-mount folder
it belongs to root, so create it first. Docker Desktop (Windows, macOS) does not
need this. A named volume (`-v hub-data:/data`) also works without it.

Check what the running hub uses:

```bash
curl http://localhost:8080/api/system/storage
# "data_dir": "/data", "config_dir": "/data", "matrix_data_dir_env": "/data", "uc_config_home_env": "/data", ...
```

Earlier versions kept `device_settings.json`, `themes.json` and
`ui_preferences.json` in a project-local `data/` folder; on first start they are
copied (not moved) into the data directory.

## docker run

```bash
docker build -t hdmi-matrix-hub .

# core only
docker run -d --name hdmi-matrix-hub --restart unless-stopped \
  -p 8080:8080 -v /srv/hdmi-matrix:/data -e MATRIX_HOST=192.168.1.50 hdmi-matrix-hub

# core + Remote 3 integration, host networking
docker run -d --name hdmi-matrix-hub --restart unless-stopped --network host \
  -v /srv/hdmi-matrix:/data -e UC_ENABLED=true -e UC_INTEGRATION_INTERFACE=192.168.1.20 hdmi-matrix-hub
```

The image has a `HEALTHCHECK` (`python run.py healthcheck`, which calls
`/api/health` on `API_PORT`), so `docker ps` shows `healthy` and orchestrators can
restart an unhealthy hub. `docker stop` stops it cleanly (SIGTERM is handled) within a few seconds.

## Upgrading from the earlier image

- **The Remote integration is now off by default.** If you use the Remote 3, start
  with one of the `docker-compose.uc-*.yml` files (or `-e UC_ENABLED=true`). Your
  Remote setup in `/data/config_state.json` is kept. If you turn UC off and
  do not set `MATRIX_HOST`, the core uses the matrix address from that file.
- **One image.** `--target api-only` and `--target full` still build, as aliases of
  the same image; they will be removed later. `full` no longer turns UC on.
- **Environment names.** The old names keep working with a warning (table above).
  `docker-compose.yml` no longer passes `UC_CONFIG_HOME`, `MATRIX_DATA_DIR`,
  `REST_API_PORT` or `WEBUI_ENABLED` into the container.
- **User.** The container user is now UID 1000 (was a system UID). On Linux, `sudo
  chown -R 1000:1000 ./data` once.
- **Compose profiles are gone.** `docker compose up -d` starts the hub.

## Deployment options

### Synology / QNAP NAS

Use Container Manager with `docker-compose.yml`, set `MATRIX_DATA_DIR` to a shared
folder (for example `/volume1/docker/hdmi-matrix`) and give UID 1000 write access
to it. Most NAS Docker packages cannot do host networking and mDNS well: use the
bridge file for the Remote 3.

### Raspberry Pi / Linux server

```bash
cd ~/8x8-hdmi-matrix-hub
echo "MATRIX_HOST=192.168.1.50" > .env
echo "MATRIX_DATA_DIR=/srv/hdmi-matrix" >> .env
sudo mkdir -p /srv/hdmi-matrix && sudo chown 1000:1000 /srv/hdmi-matrix
docker compose up -d
```

### Portainer

Create a stack from `docker-compose.yml` and add `MATRIX_HOST` and
`MATRIX_DATA_DIR` under the stack's environment variables.

## Troubleshooting

### The Remote 3 does not discover the integration

- Use host networking (`docker-compose.uc-host.yml`) with `HUB_HOST_IP` set to the
  LAN address the Remote can reach; check the log line
  `Integrations: Unfolded Circle Remote (port 9095, mDNS on, address …)`.
- Make sure the firewall allows TCP 9095 and mDNS (UDP 5353).
- Or register it by URL (bridge networking, above).

### The container keeps restarting

```bash
docker compose logs --tail 50
```

- `Configuration error: data directory /data is not writable …`: chown the host
  folder (see Persistent storage).
- `Configuration error: UC_DRIVER_URL=…` or a port error: fix the variable.
- Port already in use: change `HUB_PORT` (bridge) or `API_PORT` (host networking).

### Reset the Remote integration's configuration

```bash
docker compose down
rm data/config_state.json
docker compose up -d
```

## Deployment tests

`tests/deploy` starts this image the ways described here and checks it
(`pytest -m docker tests/deploy`; CI runs it in the `docker-build` job): health
and the image health check, web UI and kiosk, `/api/status` against the BK-808
simulator in a container, port 9095 only with UC, `ucapi` not imported without
UC, non-root user, data kept across a restart, clean stop, and each compose file.
