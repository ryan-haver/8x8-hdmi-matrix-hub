# Unfolded Circle Remote 3 — Setup & Integration Guide

> **Audience**: owners who want to control the hub from a Unfolded Circle
> Remote 3, and integrators wiring the hub into an existing UC setup.
>
> **Sources of truth**:
> - `src/driver.py` — retained legacy reference; not launched by the shared runtime
> - `src/hub/integrations/unfolded_circle/` — Remote adapter (`config.py`,
>   `entities.py`, `state.py`, `handlers.py`, `mdns.py`, `migration.py`)
> - `hub.cli` and `hub.runtime/` — entry point, address resolution and shared runtime
> - `src/hub/env.py` — framework environment inventory; runtime uses `hub.cli`
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
imported when `UC_ENABLED=true`; otherwise `ucapi` is not imported and port
9095 stays closed. Both modes use the same `hub.cli` runtime and matrix owner.

| Variable | Default | Effect |
| --- | --- | --- |
| `UC_ENABLED` | `false` | `true` imports `ucapi`, starts the integration and binds port 9095. |
| `UC_INTEGRATION_HTTP_PORT` (alias `UC_PORT`) | `9095` (`driver.json` → `port`) | The WebSocket port the Remote 3 dials. |
| `UC_INTEGRATION_INTERFACE` | all interfaces | Bind address; also the address mDNS announces (set to your LAN IP for mDNS to be useful). |
| `UC_DISABLE_MDNS_PUBLISH` (alias `UC_DISABLE_MDNS`) | `false` | `true`: do not announce the integration by mDNS (bridge networking). |
| `UC_DRIVER_URL` | not set | `ws://host:port` advertised to the Remote (bridge networking); must start with `ws://` or `wss://`. |
| `UC_CONFIG_HOME` | `DATA_DIR` | Remote configuration/state directory (`config_state.json`, `driver.lock`). Data catalogs can be separate. |
| `UC_AUTH_TOKEN` | unset | When set, the adapter advertises `pwd: true` and requires a "Hub setup token" on every setup request. Falls back to `ADMIN_PIN` when unset. |
| `API_PORT` | `8080` | REST API / web UI / kiosk port (only relevant for the host-networking compose override that needs to set it explicitly). |
| `MATRIX_HOST` | UC off: `192.168.0.100`; UC on: saved setup or unconfigured | Matrix IP / host name. In UC mode saved setup wins; an environment host is an unsaved bootstrap. |
| `DATA_DIR` | image: `/data` | Persistent directory and default UC config home; data stores resolve separately when paths differ. |
| `STATUS_POLL_INTERVAL` | `5` | Seconds between the hub's own status reads. |
| `FLIC_ENABLED` | `true` | Enables Flic registration/list routes. Explicit false/0/no/off disables those routes and registry lifecycle. |
| `HA_DISCOVERY_ENABLED` | `false` | Enables optional HA discovery; manual HACS installation remains available when disabled. |

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

The setup is handled by `src/hub/integrations/unfolded_circle/setup.py` and
applied through the shared runtime:

1. **First page — matrix address.** The Remote collects `host` + `port`.
   - **Existing address** (already in `config_state.json`): the shared runtime
     can reuse the login for that address.
   - **New address**: the adapter probes reachability before asking for
     credentials; it does not send the previous matrix login to the new host. On
     `CONNECTION_REFUSED` / `NOT_FOUND` / `TIMEOUT` it returns the
     matching `IntegrationSetupError`; otherwise it asks for the matrix's
     login (its own web-interface login, factory default `Admin` / `admin`).
     The configured login is **never** sent to a new address.
2. **Login page** — `user` + hidden `password`. Sent *only* to the
   address from step 1. A failed login/connect returns its setup error and
   rolls the shared runtime back to the previous address and session.
3. **`SetupComplete`** — the shared runtime reconfigures every surface and
   atomically persists `config_state.json` under `UC_CONFIG_HOME`. The address
   and credentials become active immediately and win on later UC startups.

A **Reconfigure** with the same address needs no login page. A reconfigure
that changes the address triggers the credential step again.

The adapter keeps the Remote setup server available when the matrix is
unconfigured or disconnected. An unconfigured runtime has an empty catalog;
after setup, a configured but offline matrix retains its 74 entity definitions
as unavailable. The shipped `ucapi` 0.7 SDK does not advertise the optional
select entities. Direct dispatcher cycle tests do not establish Remote UI
cycling.

### Setup token (`UC_AUTH_TOKEN` / `ADMIN_PIN` fallback)

When `UC_AUTH_TOKEN` is set (or `ADMIN_PIN` is set and `UC_AUTH_TOKEN` is
not), the adapter:

- advertises **`pwd: true`** in the mDNS TXT record (the Remote then asks
  for a password on the setup page instead of running an unauthenticated
  setup);
- adds a **"Hub setup token"** field to the setup page and *removes* the
  legacy "Current matrix password (when changing address)" field;
- requires the token on **every** `DriverSetupRequest` — first setup and
  reconfigure. A missing or wrong token returns
  `ucapi.SetupError(error_type=ucapi.IntegrationSetupError.AUTHORIZATION_ERROR)`
  and changes nothing on the hub.

The adapter accepts the token as `auth_token`, `token`, or `pin` and compares
it with `hmac.compare_digest`; the value is never logged. ucapi's sensitive
key list (`auth_token`, `token`, `pin`, `current_password`) redacts it in
the Remote's message log too.

Without a token, changing an already configured address requires the
**"Current matrix password (when changing address)"** field to authorize the
setup request, then the new matrix's own credentials on the login page. The
stored password is never sent to a new address.

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

The bridge logs a line similar to this on startup:

```
UCBridge started on port 9095 (74 available entities)
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

With `UC_ENABLED=true`, the saved `config_state.json` address is authoritative.
An explicit `MATRIX_HOST` is an unsaved bootstrap only when no valid saved
address exists. With neither, REST health/UI and the Remote setup service start
without connecting to the core-only default. Successful setup atomically saves
the candidate and immediately changes the shared runtime address. A failed or
aborted setup restores the prior address/session. Same-address reconfiguration
retains its working login; a different address requires its own login. REST
matrix-host changes are transient and do not rewrite Remote setup state.

With UC disabled, address resolution prefers explicit `MATRIX_HOST`, then a
valid saved address, then `192.168.0.100`. This core-only saved-address fallback
does not load saved credentials.

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

`driver.lock` is a single-instance lock held by the shared runtime while the
Remote integration is running. If a previous container was killed without
releasing it, remove `data/driver.lock` alongside `config_state.json`.

If the hub refuses to start with `Configuration error: UC_DRIVER_URL=…`,
fix the variable — `hub.cli.load_settings` raises `ConfigError` on a
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
- Setup returns `AUTHORIZATION_ERROR` for a missing/invalid setup token or
  missing/invalid current matrix password when one is required.
- A port-9095 firewall rule blocking the Remote produces the same
  "setup does nothing" symptom from the Remote's side — check
  reachability before changing tokens.

### The matrix address changed but the hub still talks to the old one

- Restart the hub: `config_state.json` under `UC_CONFIG_HOME` is the source
  of truth in UC mode; core-only mode uses explicit host, then a valid saved
  address, then the default.
- Reset the Remote integration (§6) and re-run the setup on the Remote.

### `ucapi` not installed

- `UC_ENABLED=true` requires `ucapi` in the environment. The Docker image
  installs it via `requirements-uc.txt`. On a local dev install:
  `pip install -r requirements-uc.txt`.
- The hub exits with
  `UC_ENABLED=true but the ucapi package is not installed
   (pip install -r requirements-uc.txt)`
  (the shared runtime imports `ucapi` only when UC is enabled).

---

## 8. References

The scripted Remote harness and SDK-stub tests are software evidence only.
They do not prove a physical Remote's behavior. See the
[runtime validation index](validation/RUNTIME_VALIDATION_INDEX.md) for fresh
coordinator campaign artifacts and pending hardware/field/soak gates.

- **Unfolded Circle core API**: pinned at `vendor:core-api` (see
  [`docs/vendor/UNFOLDED_CIRCLE.md`](vendor/UNFOLDED_CIRCLE.md) for the pin).
- **Python SDK (`ucapi`)**: `v0.7.0` (pinned in
  `requirements-uc.txt`, `pyproject.toml`).
- **Integration cookbook** (entity shapes, button mapping, UI pages):
  [`docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md).
- **Audit & register of findings**: [`docs/REMEDIATION_PLAN.md`](REMEDIATION_PLAN.md) §4.9
  (`UC-01`..`UC-16`, `UC-20`, `UC-26`, `UC-28`).
- **Threat model and port-9095 firewall guidance**: [`SECURITY.md`](../SECURITY.md).
