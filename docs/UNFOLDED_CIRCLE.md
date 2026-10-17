# Unfolded Circle Remote 3 — Setup & Integration Guide

> **Audience**: owners who want to control the hub from a Unfolded Circle
> Remote 3, and integrators wiring the hub into an existing UC setup.
>
> **Sources of truth**:
> - `src/driver.py` — driver setup, login flow, entity handlers
> - `src/hub/integrations/unfolded_circle/` — modular integration (`config.py`,
>   `entities.py`, `state.py`, `handlers.py`, `mdns.py`, `migration.py`)
> - `run.py` and `src/hub/env.py` — environment-variable resolution
> - `driver.json` — driver metadata (`port`, `setup_data_schema`, `min_core_api`)
>
> **Companion documents**:
> - [`docs/DOCKER.md`](DOCKER.md) — `docker compose` for the Remote 3
> - [`docs/vendor/UNFOLDED_CIRCLE.md`](vendor/UNFOLDED_CIRCLE.md) — pinned UC reference sources
> - [`docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md) — development cookbook for the integration itself (entity shapes, button mapping, UI pages)
> - [`docs/INTEGRATION_TEMPLATE.md`](INTEGRATION_TEMPLATE.md) — building a new modular integration
> - [`docs/REMEDIATION_PLAN.md`](REMEDIATION_PLAN.md) §4.9 — the UC register of findings
> - [`SECURITY.md`](../SECURITY.md) §"Unfolded Circle Remote 3" — port-9095 firewall guidance

This guide focuses on the **operational** side of the integration:

- the modular setup (`UC_ENABLED` / `UC_PORT` / `UC_DISABLE_MDNS`)
- the two networking modes (host networking vs. bridge networking)
- the setup token (`UC_AUTH_TOKEN` / `ADMIN_PIN` fallback)
- the matrix-address lifecycle on the Remote's setup page
- the matrix login flow (`auth_token` vs. `current_password`)
- firewall expectations for TCP 9095

For the *development* cookbook (entity types, button mapping, UI pages,
event handling) see
[`docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md)
and the pinned references in
[`docs/vendor/UNFOLDED_CIRCLE.md`](vendor/UNFOLDED_CIRCLE.md).

---

## 1. Modular setup: what each variable does

The hub has **one** image. The core (REST API, web UI at `/ui`, kiosk at
`/kiosk`) always runs. The Remote 3 integration is **opt-in**: it is only
imported when `UC_ENABLED=true`; otherwise `ucapi` is never imported and
port 9095 stays closed (`run.py:run_uc_driver`,
`src/driver.py:handle_setup_*`). The variables resolve through one table
(`src/hub/env.py`) so this guide and the code agree.

| Variable | Default | Effect |
| --- | --- | --- |
| `UC_ENABLED` | `false` | `true` imports `ucapi`, starts the integration and binds port 9095. |
| `UC_INTEGRATION_HTTP_PORT` (alias `UC_PORT`) | `9095` (`driver.json` → `port`) | The WebSocket port the Remote 3 dials. |
| `UC_INTEGRATION_INTERFACE` | all interfaces | Bind address; also the address mDNS announces (set to your LAN IP for mDNS to be useful). |
| `UC_DISABLE_MDNS_PUBLISH` (alias `UC_DISABLE_MDNS`) | `false` | `true`: do not announce the integration by mDNS (bridge networking). |
| `UC_DRIVER_URL` | not set | `ws://host:port` advertised to the Remote (bridge networking); must start with `ws://` or `wss://`. A bad value stops the hub with exit code 2 and a clear message (`run.py:load_settings`). |
| `UC_CONFIG_HOME` | `DATA_DIR` | Integration state directory (`config_state.json`, `driver.lock`, profile / macro / scene files). |
| `UC_AUTH_TOKEN` | unset | When set, the driver advertises `pwd: true` and requires a "Hub setup token" on every `DriverSetupRequest`. Falls back to `ADMIN_PIN` when unset. |
| `API_PORT` | `8080` | REST API / web UI / kiosk port (only relevant for the host-networking compose override that needs to set it explicitly). |
| `MATRIX_HOST` | the address a Remote setup saved, else `192.168.0.100` | Matrix IP / host name. With `UC_ENABLED=true` the Remote's setup wins once a setup is saved. |
| `DATA_DIR` | image: `/data` | Persistent data directory (UC state and integration settings live here). |
| `STATUS_POLL_INTERVAL` | `5` | Seconds between the hub's own status reads. |
| `FLIC_ENABLED` | `true` | Accept button registrations from a Flic Hub. |
| `HA_DISCOVERY_ENABLED` | `false` | Publish the hub to Home Assistant over mDNS / zeroconf. |

`POLLING_INTERVAL`, `POLLING_ENABLED` and the retired names (`USE_MODULAR`,
`WEBUI_ENABLED`, `REST_API_ENABLED=false`) are documented in
[`docs/DOCKER.md`](DOCKER.md#environment-variables).

### How to start the integration locally

```bash
UC_ENABLED=true UC_INTEGRATION_INTERFACE=192.168.1.20 python run.py
```

### How to start the integration in Docker (host networking, recommended)

```bash
HUB_HOST_IP=192.168.1.20 \
  docker compose -f docker-compose.yml -f docker-compose.uc-host.yml up -d
```

`docker-compose.uc-host.yml` sets `network_mode: host`, `UC_ENABLED=true`,
`UC_INTEGRATION_INTERFACE=$HUB_HOST_IP` and leaves mDNS alone.

### How to start the integration in Docker (bridge networking)

```bash
HUB_HOST_IP=192.168.1.20 \
  docker compose -f docker-compose.yml -f docker-compose.uc-bridge.yml up -d
```

`docker-compose.uc-bridge.yml` publishes port 9095 (`UC_HOST_PORT`),
sets `UC_DISABLE_MDNS_PUBLISH=true`, and sets
`UC_DRIVER_URL=ws://$HUB_HOST_IP:$UC_HOST_PORT`. mDNS does not cross a
Docker bridge network, so the Remote does not discover the integration by
itself — register it through the Remote's REST API
([see §3](#3-bridge-networking-no-mdns-register-by-url)).

---

## 2. The Remote's setup flow (modular)

The setup is handled by `src/driver.py:setup_handler`:

1. **First page — matrix address.** The Remote collects `host` + `port`.
   - **Existing address** (already in `config_state.json`): the driver
     reuses the saved login and skips the credential step. If the saved
     login is rejected after a reconnect, the driver asks for it.
   - **New address**: the driver probes it with a plain TCP connect
     (nothing is sent — `src/driver.py:probe_address`). On
     `CONNECTION_REFUSED` / `NOT_FOUND` / `TIMEOUT` it returns the
     matching `IntegrationSetupError`; otherwise it asks for the matrix's
     login (its own web-interface login, factory default `Admin` / `admin`).
     The configured login is **never** sent to a new address.
2. **Login page** — `user` + hidden `password`. Sent *only* to the
   address from step 1. Compared with `hmac.compare_digest`; rejected
   logins return `AUTHORIZATION_ERROR` and change nothing on the hub.
3. **`SetupComplete`** — entities are installed, the saved configuration
   (`config_state.json`) is updated with the host/port/login, the poller
   starts, and the Remote sees the integration.

A **reconfigure** with the same address needs no login page. A reconfigure
that changes the address triggers the credential step again.

### Setup token (`UC_AUTH_TOKEN` / `ADMIN_PIN` fallback)

When `UC_AUTH_TOKEN` is set (or `ADMIN_PIN` is set and `UC_AUTH_TOKEN` is
not), the driver (`src/driver.py:handle_driver_setup`):

- advertises **`pwd: true`** in the mDNS TXT record (the Remote then asks
  for a password on the setup page instead of running an unauthenticated
  setup);
- adds a **"Hub setup token"** field to the setup page and *removes* the
  legacy "Current matrix password (when changing address)" field;
- requires the token on **every** `DriverSetupRequest` — first setup and
  reconfigure. A missing or wrong token returns
  `ucapi.SetupError(error_type=ucapi.IntegrationSetupError.AUTHORIZATION_ERROR)`
  and changes nothing on the hub.

The driver accepts the token as `auth_token`, `token`, or `pin` and compares
it with `hmac.compare_digest`; the value is never logged. ucapi's sensitive
key list (`auth_token`, `token`, `pin`, `current_password`) redacts it in
the Remote's message log too.

Without a token and with no admin PIN, the setup page keeps the **"Current
matrix password (when changing address)"** field, and changing the matrix
host or port requires re-entering that matrix's password. The stored
password is never sent to a new address — `probe_address` checks reachability
first.

The token guards *setup*, not the transport. Anything that can reach TCP
9095 can still subscribe to entities and control the matrix. Restrict the
port to the Remote's IP at the firewall (see §5 below).

---

## 3. Networking

### Host networking (recommended)

`docker-compose.uc-host.yml` sets `network_mode: host`, `UC_ENABLED=true`
and `UC_INTEGRATION_INTERFACE=$HUB_HOST_IP`. The integration listens on
`HUB_HOST_IP:9095` and mDNS announces that address, so the Remote shows
"HDMI Matrix" under *Integrations → Add new*. Host networking needs a
Linux Docker host; on Docker Desktop enable it under
*Settings → Resources → Network*, or use bridge mode.

If the Remote shows the integration with a wrong host name, also set
`UC_MDNS_LOCAL_HOSTNAME` (read by the `ucapi` library).

The hub log line on a healthy start:

```
Integrations: Unfolded Circle Remote (port 9095, mDNS on, address 192.168.1.20)
```

### Bridge networking (no mDNS, register by URL)

`docker-compose.uc-bridge.yml` publishes port 9095 (`UC_HOST_PORT`),
switches mDNS off (`UC_DISABLE_MDNS_PUBLISH=true`) and sets
`UC_DRIVER_URL=ws://$HUB_HOST_IP:$UC_HOST_PORT`. The Remote does not
discover the integration by itself; register it once through the Remote's
REST API (user `web-configurator`, password = the web configurator PIN;
prompts for it):

```bash
curl -u web-configurator -H 'Content-Type: application/json' \
  http://<remote-ip>/api/intg/drivers \
  -d '{"driver_id": "hdmi_matrix", "driver_url": "ws://192.168.1.20:9095"}'
```

Then set it up in the web configurator like a discovered integration.
`driver_url` is the only required field; the Remote fetches the rest from
the integration. The registration API is described in the pinned core-api
docs (`doc/integration-driver/driver-registration.md`).

### Changing networking mode after install

- Host → bridge: stop the hub, switch the compose file, restart. The
  integration state in `config_state.json` is kept.
- Bridge → host: same. The Remote may need to be re-discovered because
  mDNS was off.

---

## 4. The matrix address — who owns it

With `UC_ENABLED=true` the Remote's setup is the **owner** of the matrix
address (`config_state.json`):

- **Before the Remote has been set up**: `MATRIX_HOST` (env) gives the
  hub its matrix; it is never saved. `run.py` logs
  `MATRIX_HOST not set: using <host>:<port> from the saved Remote
  integration setup` if a setup is saved.
- **After the Remote has been set up**: the saved host/port/login is
  authoritative. `MATRIX_HOST` is logged but unused unless the saved
  address disappears (`run.py:saved_matrix_address`).
- **Reconfigure with the same address**: no login page, the saved login
  is reused.
- **Reconfigure with a new address**: probe first, then a login page,
  then `SetupComplete`. Nothing changes until the login succeeds.

Moving the matrix-address ownership to the core (and away from the Remote
setup) is on the roadmap — see
`docs/audits/UC_INTEGRATION_AUDIT.md` §5.

---

## 5. Firewall and exposure

The integration guards on *setup*, not on *transport*:

- TCP **9095** — integration WebSocket (Remote dials the hub). Anyone who
  can reach 9095 can subscribe to entities and control the matrix.
- UDP **5353** — mDNS multicast, only used in host-networking mode. The
  Remote does not need to dial 9095 over mDNS when `UC_DRIVER_URL` is
  set, but mDNS is what the Remote uses to discover the integration in
  the first place. The integration advertises itself as
  `_uc-integration._tcp.local.` so the Remote's
  *Integrations → Add new* menu lists it by name.

Restrict the port to the Remote's IP. The right place to do this depends
on the network mode:

```yaml
# docker-compose.uc-bridge.yml (bridge networking): replace the published
# port so 9095 is reachable on the hub's LAN address only.
services:
  hdmi-matrix-hub:
    ports:
      - "192.168.1.20:${UC_HOST_PORT:-9095}:9095"   # Remote 3 only
      # was: "${UC_HOST_PORT:-9095}:9095"  (every interface)
```

```bash
# docker-compose.uc-host.yml (host networking): 9095 is the host's own
# port, so the firewall is the only place to restrict it.
sudo ufw allow from 192.168.1.60 to any port 9095 proto tcp   # the Remote
sudo ufw deny 9095/tcp                                        # everyone else
```

Apply the rule on the host that actually terminates the port — with host
networking that is the Docker host itself, not the container. A Remote on
another subnet or VLAN should reach the hub over a VPN rather than through
an open port.

If you change the port the hub advertises, keep `UC_DRIVER_URL` in step:
it is the `driver_url` the Remote is registered with, and it must name
the address you just allowed.

---

## 6. Reset and recovery

Reset the Remote integration's configuration (matrix address, saved
login, single-instance lock):

```bash
docker compose down
rm data/config_state.json
docker compose up -d
```

`driver.lock` is a single-instance lock held by `src/driver.py` while the
integration is running. If a previous container was killed without
releasing it, remove `data/driver.lock` alongside `config_state.json`.

If the hub refuses to start with `Configuration error: UC_DRIVER_URL=…`,
fix the variable — `run.py:load_settings` raises `ConfigError` on a
non-WebSocket URL and the process exits with code 2.

---

## 7. Troubleshooting

### The Remote 3 does not discover the integration

- Use host networking (`docker-compose.uc-host.yml`) with `HUB_HOST_IP`
  set to the LAN address the Remote can reach; check the log line
  `Integrations: Unfolded Circle Remote (port 9095, mDNS on, address …)`.
- Make sure the firewall allows TCP 9095 and mDNS (UDP 5353).
- Or register it by URL (bridge networking, §3 above).

### The Remote 3 reports `AUTHORIZATION_ERROR` on setup

- `UC_AUTH_TOKEN` (or `ADMIN_PIN`) is set on the hub and the Remote sent
  no token or the wrong one — enter the **"Hub setup token"** on the
  setup page. A reconfigure needs it too, not just the first setup.
- The token was changed on the hub, so Remotes still hold the old value.
  Keep the token stable, or re-enter it on every Remote after changing
  it.
- No token is configured, but the matrix address was changed: re-enter
  the **current matrix password** in the field the setup page shows.
- Hub log lines: `Setup: authorization token missing or invalid` or
  `Setup: current matrix password required to change its address`.
- A port-9095 firewall rule blocking the Remote produces the same
  "setup does nothing" symptom from the Remote's side — check
  reachability before changing tokens.

### The matrix address changed but the hub still talks to the old one

- Restart the hub: `config_state.json` is the source of truth once a setup
  is saved. With `UC_ENABLED=false` the hub reads it from `DATA_DIR`;
  with `UC_ENABLED=true` the driver reads it from `UC_CONFIG_HOME`.
- Reset the Remote integration (§6) and re-run the setup on the Remote.

### `ucapi` not installed

- `UC_ENABLED=true` requires `ucapi` in the environment. The Docker image
  installs it via `requirements-uc.txt`. On a local dev install:
  `pip install -r requirements-uc.txt`.
- The hub exits with
  `UC_ENABLED=true but the ucapi package is not installed
   (pip install -r requirements-uc.txt)`
  (`run.py:run_uc_driver`).

---

## 8. References

- **Unfolded Circle core API**: pinned at `vendor:core-api` (see
  [`docs/vendor/UNFOLDED_CIRCLE.md`](vendor/UNFOLDED_CIRCLE.md) for the pin).
- **Python SDK (`ucapi`)**: `v0.7.0` (pinned in
  `requirements-uc.txt`, `pyproject.toml`).
- **Integration cookbook** (entity shapes, button mapping, UI pages):
  [`docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md).
- **Audit & register of findings**: [`docs/REMEDIATION_PLAN.md`](REMEDIATION_PLAN.md) §4.9
  (`UC-01`..`UC-16`, `UC-20`, `UC-26`, `UC-28`).
- **Threat model and port-9095 firewall guidance**: [`SECURITY.md`](../SECURITY.md).