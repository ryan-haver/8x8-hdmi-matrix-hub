# 8×8 HDMI Matrix Hub

> A unified API bridge for controlling 8×8 HDMI Matrix switches from
> Unfolded Circle Remote 3, Flic smart buttons, and Home Assistant.
>
> **One shared runtime.** The source entry point `run.py` and installed
> `orei-matrix-driver` console command compose one matrix client, persistence layer, REST API,
> WebSocket, web UI and kiosk. `UC_ENABLED=true` adds the Remote 3 adapter
> to that runtime; `src/driver.py` remains a legacy reference and is not
> launched. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
>
> **Version:** `src/hub/__init__.py::__version__` is the canonical source.
> `python scripts/bump_version.py --check` verifies release manifests;
> `--tag` prints the matching release tag.

---

## 🔌 Compatible devices

The hub targets the **OREI BK-808** HTTPS/Telnet protocol, anchored by the
checked-in real-device captures. The other HDCVT HDP-MXC88A family models below
are compatibility candidates; their hardware/firmware behavior has not been
validated for this release.

| Brand                  | Model         | Product                                                                                                                            | Status        |
| ---------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **OREI**               | BK-808        | [orei.com/bk-808](https://orei.com/products/8k-8x8-hdmi-matrix-switcher-4k-120hz-hdcp-2-3-hdr-edid-dolby-vision-atmos-downscaling-bk-808) | Captured protocol baseline |
| HDCVT (OEM)            | HDP-MXC88A    | [hdcvt.com](https://www.hdcvt.com/HDMIMatrix/328.html)                                                                            | 🔲 Untested   |
| Simplified MFG         | M88-8K        | [simplifiedmfg.com](https://www.simplifiedmfg.com/simplified-products/m88-8k)                                                                            | 🔲 Untested   |
| BZBGEAR                | BG-8K-88MA    | [bzbgear.com](https://bzbgear.com/product/bg-8k-88ma-8x8-8k-uhd-hdmi-2-1-matrix-switcher-with-auto-downscaling-audio-de-embedding-8k60-4k120-and-vrr-fva-allm-support/) | 🔲 Untested   |
| WolfPack (HDTV Supply) | HDTVHDPMXC88A | [hdtvsupply.com](https://www.hdtvsupply.com/wolfpack-8k-60-hz-8x8-hdmi-matrix-switch.html)                                         | 🔲 Untested   |
| A-NeuVideo             | ANI-8-8K60-S  | [a-neuvideo.com](https://www.a-neuvideo.com/shop/product_info.php?products_id=269)                                                  | 🔲 Untested   |

> The BK-808 protocol baseline comes from the checked-in real-device captures.
> The full release hardware campaign is not complete yet: Phase 8 / WP-V3
> still requires owner-observed V4 checks and the V5 soak. See the
> [validation report](docs/validation/VALIDATION_REPORT.md) and
> [feature ledger](docs/validation/LEDGER.md). Other listed models are
> compatibility candidates with no release hardware validation on file.
> Report results through [GitHub issues](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/issues).

### Hardware requirements

* HDMI 2.1 8×8 Matrix Switch (a model from the list above).
* Network connectivity (HTTPS on port `443`, Telnet on port `23` for
  CEC and cable detection).
* Control interface: web GUI, RS-232 or TCP/IP.

---

## 🎯 Features

> The matrix is the focus; the matrix is the API. The architecture
> document ([`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)) describes
> the shared runtime and integration boundaries.

### ✅ Shipped

* **Unfolded Circle Remote 3 integration** — `UC_ENABLED=true` adds the
  shared-runtime adapter. It provides:
  * 8 preset buttons with dynamic names from the matrix.
  * Matrix remote entity with preset-selection UI.
  * CEC control for all 8 inputs (navigation, playback, power).
  * Per-input CEC remote entities.
  * Fast reconnection via the `UC_DRIVER_URL` setup field.
  * mDNS advertisement (or explicit `UC_DRIVER_URL` for bridge
    networking).
  * See [`docs/UNFOLDED_CIRCLE.md`](docs/UNFOLDED_CIRCLE.md).

* **REST API** — full matrix control documented in
  [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) (generated from
  `src/hub/openapi.py::build_openapi_spec(app)`; **in this release the
  shipped REST app mounts `/api/openapi.json` (raw OpenAPI 3.1 document)
  and `/api/docs` (Swagger UI)**, wired by the
  `wp-g2-openapi-swagger-config-docs` track).
  * WebSocket at `/ws` for real-time status updates, schema in
    [`docs/api/websocket.schema.json`](docs/api/websocket.schema.json).
  * Rate limiting, CORS, and the unified `{success, data, error}`
    envelope (`API-21`).
  * Three authentication paths: admin session cookie, `X-API-Key`
    header, `?key=` query for clients that cannot set headers
    (see [`SECURITY.md`](SECURITY.md)).

* **Advanced output control** — HDCP mode (1.4 / 2.2 / follow sink/source),
  HDR mode (passthrough, HDR→SDR, auto), scaler settings (4K / 8K
  downscaling, audio-only), ARC per output, audio mute per output.

* **EDID management** — per-input EDID configuration, copy-EDID-from-display,
  4K60 HDR, 8K, Atmos.

* **External audio routing** — independent audio matrix control,
  bind to input/output or matrix mode, per-output audio source.

* **Profiles (activity-based routing)** — named routing configurations
  with HDR / HDCP / audio settings, CEC macros, and power automation.
  Unlimited profiles (the matrix has eight hardware presets; profiles
  are software).

* **Focused UI (the `/ui` page)** — installed at the project root.
  See *Focused UI* below.

* **Kiosk (`/kiosk`)** — shared `KioskController` (`web/js/components/
  kiosk-controller.js`) with `switch` / `switch_all` live WebSocket
  updates and a remembered-device PIN unlock.

* **Docker deployment** — single image that contains the shared runtime and
  optional integrations. Core starts with `docker compose up -d`; UC mode is
  added with `docker-compose.uc-host.yml` (host networking, mDNS)
  or `docker-compose.uc-bridge.yml` (bridge networking, fixed driver
  URL).

* **Flic integration** — enabled by default; it registers
  itself via `POST /api/integrations/flic/register` and is read via
  `GET /api/integrations/flic/buttons`. Set `FLIC_ENABLED=false` to omit
  these integration routes and its registry lifecycle; core actions stay
  available. The user-facing guide at
  [`docs/FLIC_SETUP.md`](docs/FLIC_SETUP.md) describes Flic Hub
  configuration with the operator.

* **Home Assistant** — the HACS component at
  [`custom_components/hdmi_matrix/`](custom_components/hdmi_matrix/)
  remains manually installable. Optional runtime discovery advertises the
  REST service through `hub.integrations.homeassistant`; it does not install
  or configure the component. See
  [`docs/HOME_ASSISTANT.md`](docs/HOME_ASSISTANT.md).

* **CEC macro system** — custom multi-step CEC command sequences
  (power on/off, volume, inputs, delays), test/dry-run via the API.

### 🔲 Not on the current plan

See [`ROADMAP.md`](ROADMAP.md) §6 for the things the project
deliberately does not promise:

* Native Alexa skill (control it through Home Assistant instead).
* Schedule / cron-like triggers for profile recall.
* MQTT broker integration (the framework supports one; no worktree
  exists and no `/api/integrations` general endpoint exists).
* React / Vue rewrite of the web UI.
* Other matrix brands beyond the HDCVT HDP-MXC88A family.

---

## 🎨 Focused UI

The `/ui` page is built from the ES modules in
[`web/js/core/`](web/js/core/) (`api`, `ws`, `state`, `html` with
XSS-safe auto-escape, `overlay`, `toast`), the unified components in
[`web/js/components/`](web/js/components/) (`unified-settings-drawer`,
`editor-shell`, `cec-remote`, `kiosk-controller`, `dashboard-store`),
and the design tokens in
[`web/css/tokens.css`](web/css/tokens.css).

What that means for the user:

* A single `UnifiedSettingsController` with `#settings/*` hash routing
  replaces nine page-specific drawers.
* The `OverlayStack` keeps `#side-nav`, `#settings-drawer`,
  `#hardware-drawer`, confirm modals and the editor shell on a single
  z-index scale (`UI-59`); `Escape` dismisses one layer at a time
  and restores focus to its trigger.
* `EditorShell` replaces `window.prompt()` with a searchable command
  / step picker for every macro/scene/profile edit.
* `prefers-reduced-motion`, `:focus-visible`, **44 px touch targets**
  (`UI-15`) and four Tron background presets
  (`classic`, `neon`, `glass`, `matrix`) are part of the design
  token sheet.
* The background caps at **30 fps** (`UI-16`) and a low-power mode
  turns the Tron grid off when the tab is hidden.
* `web/manifest.json` makes the UI installable as a PWA; the icon
  provenance record lives in
  [`web/assets/icons/PROVENANCE.md`](web/assets/icons/PROVENANCE.md).

> The Focused UI ships with v0.5.0. V1 unit + V3 (simulator, browser)
> evidence is in [`docs/validation/LEDGER.md`](docs/validation/LEDGER.md);
> V4 (hardware tablet, see `UI-44`) is not yet recorded for v0.5.x —
> that gate is Phase 8 / WP-V3.

---

## 📚 Documentation

| Document                                              | Description                                                |
| ----------------------------------------------------- | ---------------------------------------------------------- |
| [ROADMAP.md](ROADMAP.md)                              | Phases, tags, what shipped, what is pending, what's off-plan |
| [CHANGELOG.md](CHANGELOG.md)                          | v0.3.0 Secure, v0.4.0 Consolidate, v0.5.0 Focused UI, the pending-hardware section |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)          | Shared runtime startup, state, actions and persistence |
| [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)          | Integration flags, lifecycle and shared runtime access |
| [docs/README.md](docs/README.md)                      | This folder's unified index (DOC-10)                        |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md)        | REST + WS contract (generated from `src/hub/openapi.py`; shipped at `GET /api/openapi.json` + Swagger UI at `GET /api/docs`) |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md)        | Runtime environment variables, aliases and storage paths |
| [docs/HOME_ASSISTANT.md](docs/HOME_ASSISTANT.md)      | HA integration guide                                       |
| [docs/DOCKER.md](docs/DOCKER.md)                      | Docker deployment guide                                    |
| [docs/FLIC_SETUP.md](docs/FLIC_SETUP.md)              | Flic button configuration                                  |
| [docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md](docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md) | UC Remote 3 setup and usage                |
| [docs/INTEGRATION_TEMPLATE.md](docs/INTEGRATION_TEMPLATE.md) | Developer guide: build a new modular integration     |
| [docs/validation/LEDGER.md](docs/validation/LEDGER.md) | The proof of function — what works today, at which level, with what freshness, with which open findings |
| [docs/validation/RUNTIME_VALIDATION_INDEX.md](docs/validation/RUNTIME_VALIDATION_INDEX.md) | Exact-commit runtime campaigns and remaining gates |
| [docs/OREI_API_COMMANDS.md](docs/OREI_API_COMMANDS.md) | Matrix protocol reference                                 |
| [SECURITY.md](SECURITY.md)                            | Threat model, access model, disclosure                     |

---

## 🚀 Quick start

### Docker (recommended)

```bash
mkdir -p data && sudo chown 1000:1000 data     # Linux: the container runs as UID 1000
MATRIX_HOST=192.168.1.50 docker compose up -d  # your matrix's IP address
docker compose logs -f
# Web UI: http://<docker-host>:8080/ui   Kiosk: http://<docker-host>:8080/kiosk
```

That starts the **core** (REST API + web UI + kiosk) from one image.

| Setup                                                                                   | Command                                                              |
| --------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Core** (web UI, kiosk, REST for HA / Flic / scripts)                                  | `docker compose up -d`                                               |
| **+ Remote 3**, host networking, found via mDNS                                        | `HUB_HOST_IP=<this host's LAN IP> docker compose -f docker-compose.yml -f docker-compose.uc-host.yml up -d` |
| **+ Remote 3**, bridge networking, fixed `UC_DRIVER_URL`                               | `HUB_HOST_IP=<this host's LAN IP> docker compose -f docker-compose.yml -f docker-compose.uc-bridge.yml up -d` |

Flic registration/list routes are enabled by default and can be disabled with
the Flic integration setting. Install the HACS component separately in Home Assistant. See
[`docs/DOCKER.md`](docs/DOCKER.md) for persistent storage, networking
and upgrading.

### Manual install

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
python -m pip install --require-hashes -r requirements.txt

export MATRIX_HOST=192.168.1.50
python run.py                                        # core only
UC_ENABLED=true python run.py                        # core + Remote 3 (port 9095)
```

On PowerShell, activate with `.venv\Scripts\Activate.ps1` and set
`$env:MATRIX_HOST = "192.168.1.50"`; use `$env:UC_ENABLED = "true"` for UC mode.
The runtime lock includes UC dependencies; `requirements-uc.txt` remains a
compatibility include. Locks are validated on Python 3.12.

An installed wheel uses the `orei-matrix-driver` command and requires an explicit writable
`DATA_DIR` or `MATRIX_DATA_DIR`; source checkout defaults are not inferred from
the current working directory.

### Core environment variables

See [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) (checked against
the source) for the full table with defaults,
retired aliases and the `OREI_*` knobs that are *deliberately not*
aliases.

| Variable        | Default                                       | Description                                              |
| --------------- | --------------------------------------------- | -------------------------------------------------------- |
| `MATRIX_HOST`   | Core-only `192.168.0.100`; UC: saved setup or unconfigured | Matrix host; explicit UC address is an unsaved bootstrap |
| `MATRIX_PORT`   | `443`                                         | Matrix HTTPS port                                       |
| `API_PORT`      | `8080`                                        | REST API + web UI + kiosk                               |
| `DATA_DIR`      | image: `/data`                                | Writable config path and default Remote config home; data may be separate |
| `UC_ENABLED`    | `false`                                       | Add the Remote 3 adapter to the shared runtime |
| `LOG_LEVEL`     | `INFO`                                        | Logging verbosity                                        |
| `OREI_VERIFY_SSL` | `false`                                     | Verify the matrix's TLS certificate                      |

`FLIC_ENABLED` defaults true and disables the Flic registration/list routes
when false. `HA_DISCOVERY_ENABLED` defaults false and enables optional service
discovery when true. See [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) for
the full defaults and address/storage behavior.

The deprecated names (`OREI_HOST`, `OREI_PORT`, `REST_API_PORT`,
`OREI_API_PORT`, `MATRIX_DATA_DIR`, `UC_PORT`, `UC_DISABLE_MDNS`,
`USE_MODULAR`, `WEBUI_ENABLED`) are read once at start-up and
produce a single deprecation message — see
[`docs/CONFIGURATION.md`](docs/CONFIGURATION.md).

---

## 🏗️ Architecture

The deep dive lives in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
The one-screen version, on purpose honest about what is shipped today
and where integration boundaries sit under `src/hub/`:

```
       ┌─────────────────────────────────────────────────────────────┐
       │           web/  (Focused UI: /ui, /kiosk, PWA)            │
       └────────────────────────┬────────────────────────────────────┘
                                │ REST + WebSocket
                                ▼
       ┌─────────────────────────────────────────────────────────────┐
       │  src/rest_api/  (22 modules in src/rest_api/)               │
       │  src/rest_api/app.py::create_rest_app                      │
       │  src/rest_api/RestApiServer.start                          │   ← always
       └────────────────────────┬────────────────────────────────────┘
                                │ delegates to
                                ▼
       ┌─────────────────────────────────────────────────────────────┐
       │  src/orei_matrix.py  +  src/telnet_client.py               │
       │  (HTTPS / Telnet transports; the only matrix client)        │
       └────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  OREI Matrix  │
                        └───────────────┘

  Shared composition (both modes): hub.cli → runtime storage barrier →
  MatrixService + ActionRunner + IntegrationLoader → RestApiServer. UC mode
  adds its SDK WebSocket adapter on port 9095; Flic and HA discovery follow
  their integration flags.

  ┌─────────────────────────────────────────────────────────────┐
  │  src/hub/                                                    │
  │    core/             MatrixService, MatrixModel, NameStore,    │
  │                      EventBus  (shared runtime)                │
  │    domain/           ActionRunner, VisibilityStore             │
  │                      (shared runtime)                           │
  │    integrations/     Integration / IntegrationRegistry /        │
  │                      IntegrationLoader + HubClient (Local/Http)│
  │                      (shared runtime)                           │
  │    persistence/      hub.persistence.migrations                │
  │                      (startup migration barrier)                │
  │    cli.py            source + installed entry point             │
  │    openapi.py        build_openapi_spec (mounted at            │
  │                      /api/openapi.json and /api/docs)          │
  │                      (live REST app)                             │
  └─────────────────────────────────────────────────────────────┘
```

Three guarantees hold end-to-end on the *shipped* runtime:

1. **One startup path.** `run.py` and the installed `orei-matrix-driver` command enter
   `hub.cli` and `hub.runtime.composition` for both integration modes.
2. **One matrix client.** Whether UC mode is on or off, the actual
   matrix is reached through `src/orei_matrix.py.OreiMatrix`.
3. **One REST surface.** Both modes bind `RestApiServer` on the same
   `API_PORT` with the same routes from `src/rest_api/`.

Three claims are *intentionally* not made:

* That scripted, simulator or SDK-stub runs prove physical matrix, Remote,
  Flic, LAN discovery, field recovery or soak behavior; those gates remain
  pending owner evidence.

---

## 🧪 Validation

Every shipped feature in the table above is in the registry at
[`docs/validation/features.yaml`](docs/validation/features.yaml), and
its row-by-row status is in
[`docs/validation/LEDGER.md`](docs/validation/LEDGER.md). What the
levels mean and how evidence is recorded is in
[`docs/validation/VALIDATION_PLAN.md`](docs/validation/VALIDATION_PLAN.md)
(short version: [docs/validation/README.md](docs/validation/README.md)).

Earlier ledger and candidate records remain attached to their tested commits.
The integrated runtime campaign is pending the coordinator's fresh report and
will be indexed at [`docs/validation/RUNTIME_VALIDATION_INDEX.md`](docs/validation/RUNTIME_VALIDATION_INDEX.md).
Physical hardware, field/recovery and 72-hour soak evidence remain pending.

---

## 📡 Ports

| Port  | Protocol   | Purpose                                                  |
| ----- | ---------- | -------------------------------------------------------- |
| 8080  | HTTP / WS  | REST API, web UI (`/ui`), kiosk (`/kiosk`)               |
| 9095  | WebSocket  | Unfolded Circle Remote 3 integration (only with `UC_ENABLED=true`) |

> **Do not expose either port to the public internet.** Behind a
> reverse proxy on `127.0.0.1`, on a LAN behind a firewall, or on a
> VPN (Tailscale / WireGuard). The full security baseline is in
> [SECURITY.md](SECURITY.md).

---

## 📁 Project structure

```
.
├── run.py                       # compatibility entry point to hub.cli
├── src/
│   ├── driver.py                # retained legacy reference; not launched
│   ├── orei_matrix.py           # the matrix client (HTTPS / Telnet) — the shipped transport
│   ├── telnet_client.py         # async Telnet client (CEC, cable detection)
│   ├── persistence.py           # data-dir resolution + atomic writes (shipped path)
│   ├── config.py                # configuration management
│   ├── scene_manager.py         # scenes / profiles / macros persistence
│   ├── scene_execution.py       # scene executor
│   ├── cec_macros.py            # CEC macro definitions
│   ├── cec_commands.py          # CEC byte-level protocol
│   ├── cec_resolver.py          # CEC address resolution
│   ├── system_shortcuts.py      # built-in quick-actions
│   ├── dashboard_layout.py      # dashboard layout helpers
│   ├── password.py              # PIN / passcode hashing
│   ├── _file_io.py              # atomic JSON read / write
│   ├── _task_supervisor.py      # task supervision and error handling
│   ├── _telnet_proto.py         # Telnet protocol implementation
│   ├── rest_api/                # 22-module aiohttp app (the shipped REST surface)
│   ├── integrations/            # retained legacy integration support modules
│   │   └── unfolded_circle/     #   legacy code, not launched by runtime
│   └── hub/                     # packaged shared runtime
│       ├── core/                #   MatrixService, MatrixModel, NameStore, EventBus
│       ├── domain/              #   ActionRunner, VisibilityStore
│       ├── integrations/        #   Integration framework + HubClient + 3 integrations
│       ├── persistence/         #   migration barrier for managed runtime files
│       ├── runtime/             #   shared composition and startup
│       ├── env.py               # canonical runtime environment table
│       ├── cli.py               # source and installed entry point
│       └── openapi.py           # OpenAPI 3.1 generator (mounted at /api/openapi.json + /api/docs)
├── web/                         # Focused UI (ES modules + tokens)
│   ├── js/core/                 #   the unified client surface
│   ├── js/components/           #   the unified drawer, editor shell, CEC remote, kiosk controller
│   ├── css/tokens.css           # design tokens + 4 Tron presets + 44 px touch targets
│   ├── index.html               # /ui
│   ├── kiosk.html               # /kiosk
│   └── manifest.json            # PWA install
├── custom_components/hdmi_matrix/  # Home Assistant HACS component
├── docs/                        # every doc lives here; see docs/README.md
│   ├── ARCHITECTURE.md          # shared runtime composition and boundaries
│   ├── INTEGRATIONS.md
│   ├── API_REFERENCE.md         # generated from src/hub/openapi.py
│   ├── CONFIGURATION.md         # runtime flags, aliases and storage paths
│   ├── validation/              # the proof of function
│   └── ...
├── tests/                       # pytest suite + Playwright + scenario runner
├── driver.json                  # UC driver metadata
├── docker-compose.yml           # core
├── docker-compose.uc-host.yml   # + UC, host networking
├── docker-compose.uc-bridge.yml # + UC, bridge networking
├── pyproject.toml               # one source of packaging + versioning
├── requirements.txt             # core
├── requirements-uc.txt          # + UC
└── README.md                    # this file
```

---

## 🆘 Troubleshooting

* **Integration shows "Unavailable"** — verify the matrix IP in the
  matrix's own `IP INFO` menu, that port `443` is reachable, then
  restart the hub (`docker compose restart`). See the integration
  log with `docker compose logs -f`.
* **Scene / profile / macro does not change anything** — verify the
  scene / profile / macro is saved (`GET /api/profiles`,
  `GET /api/cec/macros`), check the hub logs for the failure reason,
  and recall once more with `--allow-writes` on the hardware validator
  if you are against a real matrix.
* **Remote 3 will not pair** — confirm the integration WebSocket is
  reachable from the Remote (use `UC_DRIVER_URL` and the integration
  status at `GET /api/health` — the `matrix` block tells you the
  connection summary).
* **Home Assistant does not see entities** — re-add the integration
  through *Devices & Services → Add Integration → HDMI Matrix*; the
  HACS component installs from `custom_components/hdmi_matrix/`.
  `HA_DISCOVERY_ENABLED=true` advertises the optional REST service over mDNS;
  it does not install or configure the HACS component. Install HACS manually.
* **Something else** — open an issue with the hub log, the matrix
  model / firmware, and the `GET /api/info` JSON; the maintainers
  read [SECURITY.md](SECURITY.md) §"Reporting a vulnerability" for
  the private path when it's a security finding.

---

## 📜 License

This integration is provided as-is under the **Mozilla Public License
v2.0**. See [LICENSE](LICENSE).

Dependency licenses, original icon provenance, and upstream document attribution
are recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

## 🤝 Credits

* Based on the
  [Unfolded Circle Integration API](https://github.com/unfoldedcircle/integration-python-library).
* Inspired by the
  [Denon AVR integration](https://github.com/unfoldedcircle/integration-denonavr).
* Built for the Unfolded Circle Remote Two / Remote 3 community.
