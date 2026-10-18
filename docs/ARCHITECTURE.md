# Architecture

The shipped runtime starts `OreiMatrix` and `RestApiServer` directly from
`run.py`; UC mode invokes `src/driver.py` in the same process through `runpy`.
`src/hub/core/matrix_service.py`, `src/hub/domain/action_runner.py`, the
integration loader and persistence migrations are implemented framework
libraries with pending runtime wiring. OpenAPI generation is connected to the
REST app at `/api/openapi.json` and `/api/docs`.

The [feature registry](validation/features.yaml) and [ledger](validation/LEDGER.md)
record proof levels. The release hardware campaign has no completed V4/V5
records yet; see [the validation report](validation/VALIDATION_REPORT.md).

---

## 1. Shipped runtime — what `python run.py` actually does

```
                  ┌─────────────────────────────────────┐
                  │           web/  (Focused UI: /ui,   │
                  │           /kiosk, PWA, /manifest.json)│
                  └────────────────┬────────────────────┘
                                   │ REST + /ws
                                   ▼
                  ┌─────────────────────────────────────┐
                  │  src/rest_api/  (22 modules)          │
                  │  src/rest_api/app.py::create_rest_app│
                  │  src/rest_api/RestApiServer.start    │  ← actually instantiated
                  └────────────────┬────────────────────┘
                                   ▼
                  ┌─────────────────────────────────────┐
                  │  src/orei_matrix.py  OreiMatrix      │  ← the matrix client
                  │  src/telnet_client.py                │     (HTTPS + Telnet)
                  └────────────────┬────────────────────┘
                                   ▼
                           ┌───────────────┐
                           │  OREI Matrix  │
                           │  HTTPS : 443  │
                           │  Telnet : 23  │
                           └───────────────┘
```

### Entry points

| Mode                        | What runs                                                       | Where                                          |
| --------------------------- | --------------------------------------------------------------- | ---------------------------------------------- |
| `UC_ENABLED` unset / `false` | `python run.py` → `run_core()` → `OreiMatrix(...)` and `RestApiServer(host, port)`. REST API, `/ui`, `/kiosk`, `/ws` listen on `API_PORT` (default `8080`). | `run.py::run_core` (line ~266 onward)        |
| `UC_ENABLED=true`           | `python run.py` → `run_uc()` → `runpy.run_path("src/driver.py", run_name="__main__")`. The legacy UC driver loads `driver.json`, starts the integration's WebSocket on `9095`, and runs the same `OreiMatrix` + `RestApiServer` underneath. | `run.py::run_uc`; `src/driver.py`             |

Both branches start `RestApiServer` straight from `src/rest_api/`,
**not** from `hub.integrations.IntegrationLoader` and **not** through
`hub.core.MatrixService`. The hub framework classes are not in the
imports of either path. This is the line between "shipped" and
"framework library" that this document watches.

### Persistence — shipped path

The shipped runtime persists data through `src/persistence.py` (and the
hand-rolled `system_shortcuts.json → shortcuts.json` rename and the
`scene_manager.py` + `device_settings.py` + `themes.py` + `ui.py`
managers in `src/rest_api/`), **not** through
`src/hub/persistence/migrations.py`. `hub.persistence` is a framework
library that ships the file-versioning machinery; it is intentionally
not yet what `OreiMatrix` state or the existing JSON stores call. The
`tests/test_hub_persistence_openapi_env.py` exercises the
framework's migrations in isolation; that is not the same thing as
saying every persisted JSON today is `schema_version`-wrapped.

### OpenAPI spec — shipped path

`src/hub/openapi.py` is a generator (`build_openapi_spec`) that
introspects an `aiohttp.web.Application` and produces an OpenAPI 3.1
JSON document. With the Phase 6/7 WP-G wiring (`wp-g2-openapi-swagger-config-docs`)
the same release ships:

* **`GET /api/openapi.json`** — the raw generated OpenAPI 3.1 JSON
  document for the shipped REST app.
* **`GET /api/docs`** — Swagger UI rendered from the same document.

The generator also remains usable as a library: `build_openapi_spec` accepts
an `aiohttp` application and derives the specification from its live router.

Generated reference: [`docs/API_REFERENCE.md`](API_REFERENCE.md)
(owned by `wp-g2-openapi-swagger-config-docs`).

---

## 2. Framework layer — what `src/hub/` ships, what is not yet wired

> Modules: `hub.core.event_bus`, `hub.core.matrix_service`,
> `hub.core.models`, `hub.core.name_store`,
> `hub.domain.action_runner`, `hub.domain.visibility`,
> `hub.integrations.base`, `hub.integrations.hub_client`,
> `hub.integrations.hub_client_local`, `hub.integrations.hub_client_http`,
> `hub.persistence.migrations`, `hub.openapi`, `hub.env`.

The `src/hub/` package is the unification Phase 4 (WP-C3) target. The
tests live under `tests/test_hub_*_integration.py`,
`tests/test_hub_core_matrix_service.py`,
`tests/test_hub_domain_action_runner.py`,
`tests/test_hub_persistence_openapi_env.py` and
`tests/test_hub_integrations_framework.py`, and they pass against the
hub modules in isolation. **What is not yet wired is the rest of the
runtime calling those classes instead of `OreiMatrix` / `RestApiServer`
directly.** That is the next consolidation step on the WP-G1/G2 path
and is tracked under `BE-*` / `API-*` in
[`docs/REMEDIATION_PLAN.md`](REMEDIATION_PLAN.md).

### `hub.core` — framework owner of matrix state

#### `MatrixService` (`hub.core.matrix_service`)

* **Status:** framework library; unit-tested; **not yet instantiated
  by `run.py` or `src/driver.py`**. The shipped code path passes
  `OreiMatrix` and `OreiMatrix.get_full_status()` straight to REST
  handlers.
* **Role (intended):** the *one* component that would own the matrix
  client and the last-known snapshot, with the EventBus publishing
  each change on a topic.
* **Public methods (all `async`):** `switch(input, output=None)`,
  `switch_all(input)`, `recall_preset(slot)`, `save_preset(slot)`,
  `power_on()`, `power_off()`, `set_input_name`,
  `set_output_name`, `set_preset_name`, `get_video_status`,
  `get_input_status`, `get_output_status`, `get_all_cable_status`.
* **Event topics** it is designed to publish to `EventBus` (every
  change):

  | Topic           | When it would publish                                |
  | --------------- | --------------------------------------------------- |
  | `hub_connection`| the link to the matrix comes up / goes down         |
  | `routing`       | an output's source changes (switch / refresh)        |
  | `power`         | the matrix power state changes                      |
  | `names`         | any effective name changes (NameStore)              |
  | `presets`       | a preset is recalled / saved                        |
  | `signal`        | an input's signal detection changes                 |
  | `cable`         | a cable is plugged / unplugged                      |
  | `display`       | an output's display / enable / ARC / mute state changes |

#### `MatrixModel` (`hub.core.models`)

* **Status:** framework library; registry of port counts and
  capabilities for the BK-808 (`BK808_MODEL`) and the 4-port BK-404
  (`BK404_MODEL`). One call site in the codebase would consume it
  (the future wiring of `MatrixService`); the shipped paths still
  hard-code `range(1, 9)`.

#### `NameStore` (`hub.core.name_store`)

* **Status:** framework library; would be the *one* store of input /
  output / preset names. The shipped `OreiMatrix.get_all_input_names`
  + `device_settings.json` flow performs the same role today.

#### `EventBus` (`hub.core.event_bus`)

* **Status:** framework library; `subscribe(cb, topics=None)` returns
  an idempotent unsubscribe function. Sync callbacks run inside
  `publish(topic, data)`; async callbacks are scheduled as tasks.
  Failures in one subscriber do not block the others.

### `hub.domain` — framework action executor

#### `ActionRunner` (`hub.domain.action_runner`)

* **Status:** framework library; unit-tested. **Not yet the dispatcher
  used by REST handlers.** The shipped REST routes call the per-kind
  manager directly (e.g. `apply_profile_state`, `SceneExecutor`,
  `MacroManager`, `execute_shortcut`, `OreiMatrix.recall_preset`).
* **Role (intended):** the *one* executor of `profile`, `scene`,
  `macro`, `shortcut` and `preset` actions, returning the same
  `ActionRunResult` shape with the same normalised status code:

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

* **Kinds (intended):** each kind is executed by the manager that
  already owns it, so this class owns **no** matrix logic of its own:

  | Kind       | Owner                                              |
  | ---------- | -------------------------------------------------- |
  | `profile`  | the shared `apply_profile_state` writer (`DI-11`)  |
  | `scene`    | `src.scene_execution.SceneExecutor`                |
  | `macro`    | `MacroManager`                                     |
  | `shortcut` | `execute_shortcut`                                 |
  | `preset`   | `MatrixService.recall_preset` / `save_preset`      |

  A custom kind can be added with `runner.register("<kind>", fn)`.

#### `VisibilityStore` (`hub.domain.visibility`)

* **Status:** framework library; would centralise `favorite` /
  `dashboard_visible` reads and writes. The shipped REST routes write
  these flags directly against each manager today.

### `hub.integrations` — framework opt-in surface + transport clients

> Modules: `hub.integrations.base`,
> `hub.integrations.hub_client`, `hub.integrations.hub_client_local`,
> `hub.integrations.hub_client_http`,
> `hub.integrations.{unfolded_circle,flic,homeassistant}`.

* **`Integration` base class (`hub.integrations.base`)** — the
  `start(hub)` / `stop()` / `health()` / `routes()` lifecycle, plus
  `IntegrationRegistry` (`register(name, env_flag, import_path)`)
  and `IntegrationLoader` (`load()`, `start(hub)`, `stop()`,
  `routes()`, `health_summary()`). The loader is unit-tested under
  `tests/test_hub_integrations_framework.py`; **it is not what
  `run.py` invokes.** The shipped Unfolded Circle integration under
  `src/integrations/unfolded_circle/` is a separate implementation
  started by `src/driver.py`.
* **`HubClient` (Protocol) + `HubClientLocal` + `HubClientHttp`**
  (`hub.integrations.{hub_client,hub_client_local,hub_client_http}`)
  — the transport-independent async hub contract. Used by the Flic
  and Home Assistant framework modules under `hub.integrations.*`. Not
  currently inserted between `OreiMatrix` and the REST app.
* **`src/hub/integrations/unfolded_circle/`**, **`flic/`**,
  **`homeassistant/`** — the framework modules that ship the same
  lifecycle on top of `HubClient`. They follow `Integration`'s
  contract and the registry would discover them by env flag; the
  shipped UC integration in `src/integrations/unfolded_circle/` is
  the legacy `driver.py`-driven implementation, separate from
  `hub.integrations.unfolded_circle`.

### `hub.persistence.migrations` — framework versioned JSON

> Module: `hub.persistence.migrations`.

* **Status:** framework library. Implements `CURRENT_SCHEMA_VERSION`,
  per-file migration chains and atomic backups (`PER-04`). Ships
  side-by-side with `src/persistence.py`. The shipped REST handlers
  persist via `src/persistence.py` (no `schema_version` envelope), not
  via `hub.persistence.migrations`.
* **Managed file names (intended):** `scenes_v2.json`,
  `profiles.json`, `cec_macros.json`, `shortcuts.json`,
  `dashboard_layout.json`, `device_settings.json`,
  `flic_buttons.json`. Today each REST module manages its own file
  directly.

### `hub.openapi` — framework contract generator

> Module: `hub.openapi`.

* **Status:** framework library. `build_openapi_spec(app)` introspects
  the live `aiohttp.web.Application` and returns the OpenAPI 3.1
  JSON document; `validate_openapi_spec` is the structural validator.
* **Mount points (planned):** `GET /api/openapi.json` for the raw
  document, `GET /api/docs` for Swagger UI. Neither is wired in the
  shipped REST app at this commit. Generation happens in the unit
  suite (`tests/test_hub_persistence_openapi_env.py`).

### `hub.env` — framework canonical env table

> Module: `hub.env`.

* **Status:** framework library. Exports `CORE_ENV_VARS` and
  `INTEGRATION_ENV_VARS`, the `EnvVar` dataclass, and
  `resolve_hub_env()`. The shipped `run.py` keeps its own retired-name
  warning table (`RETIRED_ENV`) because it has not yet been
  re-implemented through `hub.env`.
* **Full operator-facing table:** owned by the `wp-g2-openapi-swagger-
  config-docs` worktree as [`docs/CONFIGURATION.md`](CONFIGURATION.md).

---

## 3. Opt-in env flags — what each actually does today

Honest summary. The "framework default" column reflects what the
`hub.integrations.*` module would do if it owned startup; the
"shipped default" column reflects what `run.py` and `src/driver.py`
do today.

| Flag                  | Framework default (what the library would do)                          | Shipped behaviour                                                                                |
| --------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `UC_ENABLED`          | register `unfolded_circle` integration; let it drive Remote 3          | `run.py` switches to `run_uc()`, which `runpy.run_path`s `src/driver.py`. The integration is the legacy driver, *not* `hub.integrations.unfolded_circle`. |
| `FLIC_ENABLED`         | framework: opt-in flag on `FlicIntegration`; **library default `True`**; behind `IntegrationRegistry`. | `FLIC_ENABLED` is a `hub.integrations.flic` env flag, not part of the shipped startup; the REST handlers `POST /api/integrations/flic/register` and `GET /api/integrations/flic/buttons` are *always* mounted (see `src/rest_api/app.py`). |
| `HA_DISCOVERY_ENABLED` | framework: opt-in flag on `HomeAssistantDiscoveryIntegration`; **not wired to startup**. | There is no startup code that reads `HA_DISCOVERY_ENABLED`. The HA component is the HACS install at `custom_components/hdmi_matrix/` (manual setup). |

These three rows are the ones the previous round of docs got wrong.
The README, the changelog and this document's earlier revision said
"set `FLIC_ENABLED=true` to start the Flic integration"; the shipped
behaviour is different: setting `FLIC_ENABLED=false` *does not*
disable the Flic REST handlers. Always-mounted handlers are the
contract; the flag is framework-level state.

### `/api/integrations` route

There is **no `/api/integrations` general route** in the shipped app.
The only `/api/integrations/*` paths are:

* `POST /api/integrations/flic/register` — Flic Hub button discovery.
* `GET  /api/integrations/flic/buttons` — read registered Flic buttons.

There is no `/api/integrations/<name>/status` and no per-integration
health block in `/api/health`. The health endpoint returns:

* `status`, `service`, `api_version`, `version` (legacy shape),
* `matrix` (connection summary, see `src/rest_api/core.py`).
* `runtime` (event-loop lag, uptime, task count).

This is the contract today. The framework's `IntegrationLoader.
health_summary()` is not currently plugged in.

---

## 4. Event topics — `hub.core.EventBus.STANDARD_TOPICS`

The eight topics listed in §2.2.1 are part of the framework's public
contract for any future subscriber, not part of today's shipped
transport. They are listed here because the
`hub.integrations.{flic,homeassistant,unfolded_circle}` framework
modules publish and consume them and the
[`docs/api/websocket.schema.json`](api/websocket.schema.json) frames
named after them; the actual REST `install_event_stream` poll uses a
subset of those names.

The `EventBus.subscribe(cb, topics=None)` signature is framework and
is documented in `hub.core.event_bus`. There is no runtime code path
that subscribes to it today; it is exercised by
`tests/test_hub_core_matrix_service.py` only.

---

## 5. The Focused UI — `web/`

### Modules — `web/js/core/`

| Module                              | Role                                                                                                  |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `core/api.js` (`MatrixApi`)         | thin REST wrapper; surfaces `ApiError` for the unified error envelope.                                |
| `core/ws.js` (`MatrixWebSocket`)    | WebSocket client; reconnect with exponential backoff; emits typed `HubEvent` frames.                  |
| `core/state.js` (`MatrixState`)     | reducers for routing, names, presets, visibility, signals, etc.                                       |
| `core/html.js` (`html` template)    | XSS-safe escape; `raw()` marks known-safe HTML.                                                       |
| `core/overlay.js` (`OverlayStack`)  | stack-aware overlay manager; focus restore on pop; `UI-59` z-index.                                   |
| `core/toast.js` (`ToastManager`)    | success / warning / error / info toasts with the design-token palette.                                |
| `core/index.js`                     | barrel for `import { html, api, ws, state, overlayStack, toast } from './core/index.js'`.             |

### Components — `web/js/components/`

| Component                        | Phase / register          | Backed by                                                            |
| -------------------------------- | ------------------------- | -------------------------------------------------------------------- |
| `unified-settings-drawer.js`     | `DI-7`, `UI-05`, `UI-14`  | `UnifiedSettingsController` (9-section `#settings/*`)                |
| `editor-shell.js`                | `UI-19`                   | searchable command / step picker                                      |
| `cec-remote.js`                  | `UI-12`                   | shared CEC component + `cecMacroEditor` bridge                       |
| `kiosk-controller.js`            | `UI-11`, `D7`             | shared Kiosk with live WS, PIN unlock                                 |
| `dashboard-store.js`             | `DI-5`, `UI-08`           | server-backed `DashboardStore`                                        |
| `keyboard-shortcuts.js`          | `UI-06`                   | text-input guard                                                      |
| `api-copy.js`                    | `UI-18`                   | `window.location.origin` at runtime                                   |

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

> The Focused UI ships with v0.5.0. V1 unit + V3 (simulator, browser)
> evidence is in [`docs/validation/LEDGER.md`](validation/LEDGER.md);
> V4 (hardware tablet, see `UI-44`) is not yet recorded for v0.5.x —
> that gate is HIL Session 2 / Phase 8 / WP-V3.

---

## 6. Validation status today (honest)

| Surface                                  | Today (Ledger row)                  | Why not yet a v1.0.0 claim                          |
| ---------------------------------------- | ----------------------------------- | --------------------------------------------------- |
| `OreiMatrix` + `RestApiServer` (shipped) | V1 unit + V2 sim                    | not (yet) the running device under a real load      |
| `/api/...` REST contract                 | V2 + V3 (browser / HA / UC)         | not (yet) a network under load, not (yet) a real deployment host |
| `/ws` event stream                       | V2 sim + V3 browser observer        | not (yet) on real hardware                           |
| Focused UI (`web/`)                      | V3 (Playwright on simulator)        | not (yet) a tablet in a living room (`UI-44`)        |
| Unfolded Circle integration (shipped)    | V3 (scripted Remote)                | not (yet) the operator's Remote 3 against a real matrix |
| Home Assistant HACS component            | V3 (real HA container)              | not (yet) the operator's HA deployment                |
| Flic REST handlers (`/api/integrations/flic/*`) | V3 (request replay)        | not (yet) a real Flic Hub                             |
| `hub.core` / `hub.domain` / `hub.integrations` | V1 unit                      | framework only — runtime wiring is pending             |
| `hub.openapi`                            | V1 unit (introspects an aiohttp app) | not yet mounted at `/api/openapi.json` or `/api/docs` |
| `hub.persistence.migrations`             | V1 unit                              | shipped runtime persists via `src/persistence.py`    |
| Security controls                        | V3 (all three auth configs)         | not (yet) the V4 spot check with an admin PIN         |
| Reliability                              | V1 (fault injection on sim)         | not (yet) the 72 h soak (`HIL-D`, Phase 8 / WP-V3)     |

The full row-by-row state, with the freshness of each piece of
evidence and the open findings, is in
[`docs/validation/LEDGER.md`](validation/LEDGER.md). The v1.0.0 tag
will not land until the ledger says every row is at target with fresh
evidence.

---

## 7. Where to read next

* **The unified doc index** — [`docs/README.md`](README.md).
* **The opt-in integrations (framework view)** —
  [`docs/INTEGRATIONS.md`](INTEGRATIONS.md).
* **The REST contract** — [`docs/API_REFERENCE.md`](API_REFERENCE.md)
  (generated; owned by `wp-g2-openapi-swagger-config-docs`).
* **Every environment variable** — [`docs/CONFIGURATION.md`](CONFIGURATION.md)
  (generated; owned by `wp-g2-openapi-swagger-config-docs`).
* **The validation evidence** — [`docs/validation/LEDGER.md`](validation/LEDGER.md).
* **The status, next steps, and what is not on the roadmap** —
  [`../ROADMAP.md`](../ROADMAP.md).
