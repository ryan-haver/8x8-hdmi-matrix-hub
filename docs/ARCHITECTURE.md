# Architecture

> Where the code lives, how the layers talk to each other, and what the
> public contract of each layer is. The implementation moves; the
> principles in this document do not.
>
> **Validation:** every layer below is exercised by the registered
> scenarios under [`docs/validation/features.yaml`](validation/features.yaml);
> the row-by-row evidence lives in
> [`docs/validation/LEDGER.md`](validation/LEDGER.md).
> **No claim in this document is "proved on hardware" today** — that
> gate is Phase 7 / WP-V3, see [`../ROADMAP.md`](../ROADMAP.md) §5 and
> [`../CHANGELOG.md`](../CHANGELOG.md) §"Pending hardware validation".

---

## 1. Goals and non-goals

### Goals

1. **One owner of matrix state.** Every reading of "what is the matrix
   doing right now" goes through `hub.core.MatrixService`. REST handlers,
   WebSocket subscribers, the Flic integration, the Unfolded Circle
   Remote 3 integration and the Home Assistant component all read the
   same snapshot.
2. **One executor of every action.** Recalling a profile, running a
   scene, executing a macro, triggering a shortcut and pressing a
   hardware preset each return the same normalised result from
   `hub.domain.ActionRunner`. A REST handler, a WebSocket frame and a
   Remote entity command are interchangeable views of the same run.
3. **One opt-in surface for integrations.** `hub.integrations.base`
   defines `Integration` (`start` / `stop` / `health` / `routes`); the
   `IntegrationRegistry` discovers them by env flag; a disabled
   integration is never imported. See
   [`docs/INTEGRATIONS.md`](INTEGRATIONS.md).
4. **One place to validate the REST contract.** The OpenAPI 3.1 spec
   is generated from the live `aiohttp.web.Application` and served both
   as `GET /openapi.json` and as the Swagger UI at `GET /api/docs`. A
   route that ships without a description in the spec fails a test.
5. **No half-written JSON on disk.** Every persisted file carries a
   `schema_version`; the migration chain adds what is missing without
   deleting what an operator or a fork added that the schema does not
   know about.

### Non-goals

- **A heavy frontend framework.** The Focused UI is plain HTML +
  ES modules (`web/js/core/`) plus a design-token sheet (`web/css/
  tokens.css`). React / Vue are not on the plan.
- **A second runtime.** `run.py` is the one entry point. There is no
  `serve.py` / `api.py` / `worker.py` distinction; UC integration is
  an opt-in module loaded into the same process.
- **Other matrix brands.** The protocol covers the OREI BK-808 / HDCVT
  HDP-MXC88A class. Other 8×8 HDMI 2.1 matrices from the same OEM
  family are *probable* but not validated; the supported list is in
  the README.

---

## 2. Package map

```
src/
├── driver.py                 # legacy UC-driver entry (still loaded with UC_ENABLED=true)
├── orei_matrix.py            # the OreiMatrix client + HTTPS / Telnet transport (DI-12)
├── telnet_client.py          # async Telnet client (CEC, cable detection)
├── rest_api/                 # 22-module aiohttp app, delegates all state to src/hub
└── hub/                      # src/hub = the one modular hub package (this document's focus)
    ├── __init__.py           # __version__ = "0.5.0"  # DEP-06 source of truth
    ├── env.py                # canonical env vars and aliases             (DI-12)
    ├── openapi.py            # OpenAPI 3.1 generator + /api/docs          (API-21)
    ├── core/                 # src/hub/core = state owner + event bus
    │   ├── __init__.py
    │   ├── event_bus.py      # sync + async EventBus
    │   ├── matrix_service.py # MatrixService (state), MatrixClient (Protocol)
    │   ├── models.py         # MatrixModel port/capability table          (BE-26, D9)
    │   └── name_store.py     # NameStore (one name per input/output/preset)
    ├── domain/               # src/hub/domain = action execution + visibility
    │   ├── __init__.py
    │   ├── action_runner.py  # ActionRunner, ActionRunResult, StepResult  (API-19)
    │   └── visibility.py     # VisibilityStore                           (DI-5, API-20)
    ├── integrations/         # src/hub/integrations = opt-in framework + transport-independent client
    │   ├── __init__.py
    │   ├── base.py           # Integration, IntegrationRegistry, IntegrationLoader
    │   ├── hub_client.py     # HubClient (Protocol), HubSnapshot, HubEvent
    │   ├── hub_client_local.py   # in-process client (no network)
    │   ├── hub_client_http.py    # over-HTTP client (cross-process / remote)
    │   ├── unfolded_circle/  # UC Remote 3 integration                  (UC-10..13, UC-18, UC-20, DI-9)
    │   ├── flic/             # Flic buttons integration                  (FLIC_ENABLED)
    │   └── homeassistant/    # HA discovery integration                  (HA_DISCOVERY_ENABLED)
    └── persistence/          # src/hub/persistence = versioned JSON migrations (PER-04, API-12)
        ├── __init__.py
        └── migrations.py     # CURRENT_SCHEMA_VERSION, MANAGED_FILENAMES (PER-04, API-12)
web/                          # the Focused UI
├── js/core/                  # ES modules (api, ws, state, html, overlay, toast, index)
├── js/components/            # unified-settings, editor-shell, cec-remote, kiosk-controller, dashboard-store
├── css/tokens.css            # design tokens, 4 Tron presets, a11y         (UI-20)
├── index.html                # /ui
├── kiosk.html                # /kiosk
└── manifest.json             # PWA install
custom_components/hdmi_matrix/   # Home Assistant HACS component          (DOC-04)
docs/
├── ARCHITECTURE.md           # this file
├── INTEGRATIONS.md           # the opt-in integration surface (DI-9, D4, D11)
├── API_REFERENCE.md          # generated from hub.openapi (DOC-03)
├── CONFIGURATION.md          # generated from hub.env    (DOC-12)
├── validation/
│   ├── features.yaml         # the registry
│   ├── LEDGER.md             # generated row-by-row status
│   ├── VALIDATION_PLAN.md    # the levels (V0..V5) and the rules
│   ├── evidence/             # committed evidence records (115 today)
│   └── HIL_SESSION_2_RUNBOOK.md
└── audit/, vendor/           # historical references
```

Nothing else in the runtime speaks to the matrix directly; everything
goes through `hub.core.MatrixService` (state) and
`hub.domain.ActionRunner` (writes that need to be reported in a
normalised shape).

---

## 3. Layering

```
                 ┌───────────────────────────────────────────────┐
   clients ───►  │  REST + WebSocket (src/rest_api/, web/js/)    │  ← uses
                 │  Unfolded Circle Remote 3 (UC_ENABLED=true)    │     HubClient
                 │  Flic buttons (FLIC_ENABLED=true)             │     + EventBus
                 │  Home Assistant (HA_DISCOVERY_ENABLED=true)    │
                 └─────────────┬─────────▲─────────┬─────────────┘
                               │         │         │
                               ▼         │         ▼
                  ┌──────────────────────────────────────┐
                  │  hub.domain.ActionRunner             │  ← one executor
                  │  hub.domain.VisibilityStore          │     of every action
                  └────────────────┬─────────────────────┘
                                   ▼
                  ┌──────────────────────────────────────┐
                  │  hub.core.MatrixService              │  ← one owner
                  │  hub.core.MatrixModel                │     of matrix state
                  │  hub.core.NameStore                  │
                  │  hub.core.EventBus                   │
                  └────────────────┬─────────────────────┘
                                   ▼
                  ┌──────────────────────────────────────┐
                  │  src/orei_matrix.py (OreiMatrix)     │  ← the only
                  │  src/telnet_client.py                │     transport
                  └──────────────────────────────────────┘
```

* **Upward arrows (`▲`)** are event topics the lower layer publishes
  (`hub_connection`, `routing`, `power`, `names`, `presets`, `signal`,
  `cable`, `display`). A subscriber may be sync or async; a failing
  subscriber is logged and dropped, never blocks the others.
* **Downward arrows (`▼`)** are API calls. The ActionRunner never
  bypasses `MatrixService`; `MatrixService` never bypasses
  `OreiMatrix`; nothing below `OreiMatrix` talks TCP/HTTP directly
  except the transport layer.

---

## 4. `hub.core` — state owner

> Modules: `hub.core.event_bus`, `hub.core.matrix_service`,
> `hub.core.models`, `hub.core.name_store`.

### `MatrixService` (`hub.core.matrix_service`)

* **Role:** the *one* component that owns the matrix client and the
  last-known snapshot. REST handlers, WebSocket subscribers and every
  integration query this service for state.
* **Public methods** (all `async`): `switch(input, output=None)`,
  `switch_all(input)`, `recall_preset(slot)`, `save_preset(slot)`,
  `power_on()`, `power_off()`, `set_input_name`, `set_output_name`,
  `set_preset_name`, `get_video_status`, `get_input_status`,
  `get_output_status`, `get_all_cable_status`.
* **Port loops** go through the [`MatrixModel`](#matrixmodel) the
  service is constructed with; nothing else hard-codes `range(1, 9)`.
* **Snapshot delivery** is wrapped in a single `apply_status()` helper
  that both `HubClientLocal` and `HubClientHttp` consume; the same dict
  shape fills both an in-process subscriber and a remote WebSocket
  frame.
* **Event topics** published to `EventBus` (every change):

  | Topic           | When                                        |
  | --------------- | ------------------------------------------- |
  | `hub_connection`| the link to the matrix comes up / goes down |
  | `routing`       | an output's source changes (switch / refresh) |
  | `power`         | the matrix power state changes               |
  | `names`         | any effective name changes (NameStore)       |
  | `presets`       | a preset is recalled / saved                 |
  | `signal`        | an input's signal detection changes          |
  | `cable`         | a cable is plugged / unplugged               |
  | `display`       | an output's display / enable / ARC / mute state changes |

### `MatrixModel` (`hub.core.models`)

* **Role:** the port-count and capability table for the matrixes the
  project supports. Registered in
  `hub.core.models.get_matrix_model(<class_id>)`. The service asks the
  model for `model.inputs` / `model.outputs`; tests that want a
  smaller fixture ask for `BK404_MODEL`.
* **Why it's here:** "8 ports" was hard-coded across five modules;
  `BE-26` was the request to stop pretending.

### `NameStore` (`hub.core.name_store`)

* **Role:** the *one* store of input / output / preset names. Device
  names are merged with user overrides; a write is published on the
  `names` topic.
* **Modules that consume it:** REST routes (`/api/inputs`,
  `/api/outputs`, `/api/presets`), WebSocket frames
  (`presets` payload), the Unfolded Circle entity factory (so the
  Remote 3 shows the right button label), the dashboard card picker.

### `EventBus` (`hub.core.event_bus`)

* **Role:** fan-out of `HubEvent` to sync + async subscribers.
* **Modes:** `subscribe(cb, topics=None)` returns an idempotent
  unsubscribe function. `publish(topic, data)` iterates over a copy
  of the subscription list, so a subscriber may subscribe or
  unsubscribe from inside its own callback. `drain()` waits for
  outstanding async deliveries (used in tests).
* **Errors:** an exception in a callback is logged and dropped. An
  async callback without a running loop is logged and dropped.

---

## 5. `hub.domain` — action execution

> Modules: `hub.domain.action_runner`, `hub.domain.visibility`.

### `ActionRunner` (`hub.domain.action_runner`)

* **Role:** the *one* executor of `profile`, `scene`, `macro`,
  `shortcut` and `preset` actions. Every run returns an
  `ActionRunResult` with the same normalised status code:

  | Outcome     | Status | Meaning                                    |
  | ----------- | ------ | ------------------------------------------ |
  | full success| `200`  | every step was applied                     |
  | partial     | `207`  | some steps were, `success` is `False`      |
  | nothing     | `500`  | no step was applied                        |
  | refused     | `403`  | `passcode_required` / `invalid_passcode`   |
  | locked out  | `429`  | too many wrong passcodes (`SEC-06`)        |
  | unknown     | `404`  | no such profile / scene / macro / shortcut / preset |
  | bad request | `400`  | unknown kind, or a shortcut that is disabled |
  | not ready   | `503`  | the manager or matrix this kind needs is absent |

* **Kinds:** each kind is executed by the manager that already owns
  it, so this class owns **no** matrix logic of its own:

  | Kind       | Owner                                              |
  | ---------- | -------------------------------------------------- |
  | `profile`  | the shared `apply_profile_state` writer (`DI-11`)  |
  | `scene`    | `src.scene_execution.SceneExecutor`                |
  | `macro`    | `MacroManager`                                     |
  | `shortcut` | `execute_shortcut`                                 |
  | `preset`   | `MatrixService.recall_preset` / `save_preset`      |

  A custom kind can be added with `runner.register("<kind>", fn)`.
* **Use:** every REST handler that runs an action (`/api/profile/{id}/
  recall`, `/api/scene/{id}/run`, `/api/cec/macro/{id}/execute`,
  `/api/shortcut/{name}/execute`, `/api/preset/{n}`), the WebSocket
  bridge, and the `HubClient.run_action` indirection reach for
  `ActionRunner` — never for the manager directly.

### `VisibilityStore` (`hub.domain.visibility`)

* **Role:** the *one* view of `favorite` / `dashboard_visible` flags
  for presets, profiles, scenes, macros and shortcuts.
* **Why it's here:** the dashboard, the Quick Actions drawer and the
  Remote integration each reconciled those five sources themselves,
  which is how a deleted item kept a card alive. The VisibilityStore
  reads them all through one interface and writes both flags of an
  item in a single manager call, so a surface can ask "what is
  visible?" and change it without knowing where it is stored.

---

## 6. `hub.integrations` — opt-in framework + transports

> Modules: `hub.integrations.base`,
> `hub.integrations.hub_client`, `hub.integrations.hub_client_local`,
> `hub.integrations.hub_client_http`.

See [`docs/INTEGRATIONS.md`](INTEGRATIONS.md) for the per-integration
walkthroughs. The architecture-level summary is:

### `Integration` base class (`hub.integrations.base`) — lifecycle contract

```python
class Integration(ABC):
    name: str          # registry name
    env_flag: str      # env var that turns it on

    @classmethod
    def config_from_env(cls, environ) -> Any: ...

    async def start(self, hub: HubClient) -> None: ...
    async def stop(self) -> None: ...
    def health(self) -> dict[str, Any]: ...
    def routes(self) -> list[tuple[str, str, Callable]]: ...   # mounted when active
```

* **`start(hub)`** — receive the hub-owned `HubClient`. The
  integration must not touch `OreiMatrix` directly; it talks to the
  matrix only through the client.
* **`stop()`** — release subscriptions, cancel background tasks,
  close any client the integration owns. Re-entrant on loader
  recovery.
* **`health()`** — dict included by `/api/health`'s per-integration
  block. Optional fields: `enabled`, `connected`, `tasks_running`,
  `last_error`.
* **`routes()`** — list of `(METHOD, PATH, HANDLER)` registered on
  the aiohttp app after the core REST routes (see
  `IntegrationLoader.routes()`).

### `IntegrationRegistry` / `IntegrationLoader`

* **Discovery:** register by `name`, `env_flag`, `import_path`
  (`module:Class`). Imports happen at `load()` time, **only** when the
  flag is enabled. A disabled integration is never imported.
* **Lifecycle:** `loader.start(hub)` is transactional — a partial
  start is stopped (and so are earlier integrations); `loader.stop()`
  attempts every integration even when one stop fails, and aggregates
  the exceptions into an `ExceptionGroup`.

### `HubClient`

* **Role:** transport-independent async hub contract. Every
  integration sees the same surface, whether the client is in-process
  (`HubClientLocal`) or remote (`HubClientHttp`).
* **Methods (all `async`):** `snapshot`, `switch`, `cycle_input`,
  `recall_preset`, `save_preset`, `power`, `send_cec`, `run_action`,
  `subscribe(callback) → unsubscribe_fn`, `close`.
* **Snapshot shape:** `HubSnapshot` has one-based integer port
  numbers; unknown signals / cables / displays are **absent**, not
  `false`; subscribers receive an initial snapshot projection, then
  changes.
* **Event projection:** `project(snapshot) -> list[HubEvent]` is
  stable across both transports; the WebSocket schema
  ([`docs/api/websocket.schema.json`](api/websocket.schema.json))
  describes the frames.

### `HubClientLocal`

* **Use:** in-process (the integration lives in the same Python
  process as the core). Inherits from `EventPublisher` so subscribers
  get the snapshot-then-events model. Wires the optional
  `snapshot_provider` / `action_runner` / `event_subscribe` callbacks
  for adapters that don't implement `HubClient` themselves.

### `HubClientHttp`

* **Use:** integration running in a separate process or container.
  Implements the same surface over the hub's REST + WebSocket. Used
  by remote-host integrations (and by the test suite to drive an
  isolated hub container).

---

## 7. `hub.persistence` — versioned JSON

> Module: `hub.persistence.migrations`.

* **Schema:** every managed file carries `schema_version` at the top
  level. `CURRENT_SCHEMA_VERSION = 2` today; `LEGACY_FILENAMES`
  renames `system_shortcuts.json` → `shortcuts.json` in flight.
* **Migrations:** ordered, pure-function chain per file. Unknown keys
  are kept; a fork with extra fields does not lose them.
* **Safety:** the pre-migration bytes are copied to
  `<name>.v<old>.bak` **before** any function runs. The migrated
  payload is written through `_file_io.atomic_write_json`, so a crash
  mid-migration leaves the backup and either the old or the new
  file.
* **Managed files:**
  `scenes_v2.json`, `profiles.json`, `cec_macros.json`,
  `shortcuts.json`, `dashboard_layout.json`, `device_settings.json`,
  `flic_buttons.json`.

---

## 8. `hub.openapi` — contract generation

* **Spec generator:** `build_openapi_spec(app)` introspects the live
  `aiohttp.web.Application`; a registered route becomes a path in
  the document, a removed route disappears.
* **Two assertions, not derivations:**
  - `components.schemas.ApiResponseEnvelope` — every JSON endpoint
    answers with `{success, data, error, error_id}` (API-21).
    Endpoints that answer with something else (the web UI, static
    assets, the WebSocket upgrade) are described as such instead of
    being forced into the envelope.
  - `components.securitySchemes` — admin session cookie,
    `X-API-Key`, `?key=`.
* **Serving:** `GET /openapi.json` returns the spec; `GET /api/docs`
  serves Swagger UI. Generated from the same generator the tests
  validate against, so a generator regression breaks the build.

---

## 9. `hub.env` — one canonical env table

See [`docs/CONFIGURATION.md`](CONFIGURATION.md) (owned by
`wp-g2-openapi-swagger-config-docs`) for the per-variable reference.
The architecture-level summary:

* **Two tables:** `CORE_ENV_VARS` (the core hub) and
  `INTEGRATION_ENV_VARS` (the opt-in integrations). Precedence is
  canonical-name wins; an alias is only read when the canonical
  name is unset or empty. An alias that disagrees with an explicit
  canonical value is reported as ignored at start-up.
* **Retired aliases:** `OREI_HOST`, `OREI_PORT`, `REST_API_PORT`,
  `OREI_API_PORT`, `MATRIX_DATA_DIR`, `UC_PORT`, `UC_DISABLE_MDNS`,
  plus `USE_MODULAR` and `WEBUI_ENABLED` (the modular mode is the
  only mode; the web UI is part of the core). All are read once
  and produce a single deprecation warning.
* **Deliberately *not* aliases:** `OREI_USER`, `OREI_PASSWORD`,
  `OREI_VERIFY_SSL`, `OREI_TELNET_PORT` and the `OREI_*` tuning
  knobs are still read by the transport layer on purpose. The
  module documents this so the env table is the one place a reader
  finds them.

---

## 10. The Focused UI — `web/`

### Modules — `web/js/core/`

| Module                       | Role                                                                        |
| ---------------------------- | --------------------------------------------------------------------------- |
| `core/api.js` (class `MatrixApi`)| thin REST wrapper; surfaces `ApiError` for the unified error envelope.   |
| `core/ws.js` (class `MatrixWebSocket`) | WebSocket client; reconnect with exponential backoff; emits typed `HubEvent` frames. |
| `core/state.js` (class `MatrixState`)  | reducers for routing, names, presets, visibility, signals, etc.        |
| `core/html.js` (tagged template `html`)| XSS-safe escape; `raw()` marks known-safe HTML.                        |
| `core/overlay.js` (class `OverlayStack`)| stack-aware overlay manager; focus restore on pop; `UI-59` z-index.   |
| `core/toast.js` (class `ToastManager`) | success / warning / error / info toasts with the design-token palette. |
| `core/index.js`              | single barrel for `import { html, api, ws, state, overlayStack, toast } from './core/index.js'`. |

### Components — `web/js/components/`

| Component                                | Phase / register          | Backed by                              |
| ---------------------------------------- | ------------------------- | -------------------------------------- |
| `unified-settings-drawer.js`             | `DI-7`, `UI-05`, `UI-14`  | `UnifiedSettingsController` (9-section `#settings/*`) |
| `editor-shell.js`                        | `UI-19`                   | searchable command / step picker       |
| `cec-remote.js`                          | `UI-12`                   | shared CEC component + `cecMacroEditor` bridge |
| `kiosk-controller.js`                    | `UI-11`, `D7`             | shared Kiosk with live WS, PIN unlock  |
| `dashboard-store.js`                     | `DI-5`, `UI-08`           | server-backed `DashboardStore`         |
| `keyboard-shortcuts.js`                  | `UI-06`                   | text-input guard                       |
| `api-copy.js`                            | `UI-18`                   | `window.location.origin` at runtime    |

### Tokens and performance — `web/css/tokens.css` + `tron-background.js`

* **Design tokens** with semantic status colors, **`44 px` touch
  targets** (`UI-15`), `:focus-visible` outlines, four Tron presets
  (`classic`, `neon`, `glass`, `matrix`) and a
  `prefers-reduced-motion` fallback.
* **Tron background** — 30 fps cap (`UI-16`) and a low-power mode
  that turns the Tron grid off when the tab loses focus.

### PWA — `web/manifest.json`

* `start_url` / `scope` point at `/ui` (and the kiosk route). Icons
  at the standard 192/512 set; the provenance record lives in
  `web/assets/icons/PROVENANCE.md` (`UI-22`).

---

## 11. Simulator vs. hardware — what the architecture proves today

> This section is here on purpose.

| Surface                       | Today (Ledger row)            | What that does not prove                                              |
| ----------------------------- | ----------------------------- | --------------------------------------------------------------------- |
| `hub.core` + `hub.domain`     | V1 unit + V2 simulator        | not (yet) the running device under a real load                        |
| `src/rest_api/` (HubClient)   | V2 + V3 (browser/HA/UC)       | not (yet) a network under load, not (yet) a real deployment host      |
| Focused UI (`web/`)           | V3 (Playwright on simulator)  | not (yet) a tablet in a living room (`UI-44` visual baseline)          |
| Unfolded Circle integration   | V3 (scripted Remote)          | not (yet) the operator's Remote 3 against a real matrix               |
| Home Assistant component      | V3 (real HA container)        | not (yet) the operator's HA deployment                                |
| Flic integration              | V3 (request replay)           | not (yet) a real Flic Hub                                             |
| Security controls             | V3 (all three auth configs)   | not (yet) the V4 spot check with an admin PIN                         |
| Reliability                   | V1 (fault injection on sim)   | not (yet) the 72 h soak (`HIL-D`)                                     |

The full row-by-row state, with the freshness of each piece of
evidence and the open findings, lives in
[`docs/validation/LEDGER.md`](validation/LEDGER.md). HIL Session 2 is the
next concrete step on the V4 path (see
[`docs/validation/HIL_SESSION_2_RUNBOOK.md`](validation/HIL_SESSION_2_RUNBOOK.md));
the v1.0.0 tag will not land until the ledger says every row is at
target with fresh evidence.

---

## 12. Where to read next

* **The unified doc index** — [`docs/README.md`](README.md).
* **The opt-in integrations** — [`docs/INTEGRATIONS.md`](INTEGRATIONS.md).
* **The REST contract** — [`docs/API_REFERENCE.md`](API_REFERENCE.md) (generated).
* **Every environment variable** — [`docs/CONFIGURATION.md`](CONFIGURATION.md) (generated).
* **The validation evidence** — [`docs/validation/LEDGER.md`](validation/LEDGER.md).
* **The status, next steps, and what is not on the roadmap** —
  [`../ROADMAP.md`](../ROADMAP.md).
