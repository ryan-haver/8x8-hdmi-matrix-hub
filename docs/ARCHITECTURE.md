# Architecture

`run.py` is a compatibility entry point to `hub.cli`; the installed
`orei-matrix-driver` console command uses the same asynchronous composition
root. Core and UC modes share one `OreiMatrix` client, `MatrixService`,
persistence barrier, REST server,
event state and action runner. UC is an optional adapter, not the legacy
`src/driver.py` runtime. OpenAPI and Swagger are served at `/api/openapi.json`
and `/api/docs`.

The [feature registry](validation/features.yaml) and [ledger](validation/LEDGER.md)
record proof levels. The release hardware campaign has no completed V4/V5
records yet; see [the validation report](validation/VALIDATION_REPORT.md).

---

## 1. Runtime — what `python run.py` actually does

```
             run.py / orei-matrix-driver
                         │
                         ▼
        hub.cli → startup storage migration barrier
                         │
                         ▼
   IntegrationLoader + ActionRunner + MatrixService
                         │ shared client
                         ▼
        REST API + WebSocket + optional adapters
                         │
                         ▼
              OreiMatrix → OREI Matrix
```

### Entry points

| Mode                        | What runs                                                       | Where                                          |
| --------------------------- | --------------------------------------------------------------- | ---------------------------------------------- |
| `UC_ENABLED` unset / `false` | `python run.py` or `orei-matrix-driver` → shared runtime composition. REST API, `/ui`, `/kiosk`, `/ws` listen on `API_PORT` (default `8080`); UC is not imported. | `hub.cli`, `hub.runtime.composition` |
| `UC_ENABLED=true`           | The same composition adds the Remote adapter and its SDK WebSocket (default `9095`) alongside REST. | `hub.runtime.integrations`, `hub.integrations.unfolded_circle` |

Both modes instantiate `RestApiServer` with the shared runtime, which owns
`MatrixService`, `ActionRunner`, `HubClientLocal`, and the enabled
`IntegrationLoader`. REST health/UI starts before the runtime's initial matrix
connect. `src/driver.py` remains a legacy reference and is not started.

### Persistence — shipped path

`hub.persistence.startup.prepare_runtime_storage()` runs before managers,
REST stores or Flic are constructed. It migrates supported legacy files with
backups and blocks writes when inputs are corrupt, ambiguous, unsafe or from
a future schema. Managed JSON files carry a top-level `schema_version`; the
current migration schema is version 2, and older files migrate through ordered
steps after a backup. Unknown keys are retained. `src/persistence.py` still
resolves compatible data paths
and copies selected legacy preferences; it no longer searches other checkouts
for catalogs. Not every managed JSON file is schema-wrapped: per-file reader
and migration behavior is described in the storage contract below.

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

## 2. Shared runtime and framework modules

The composition is organized in `src/hub/core`, `src/hub/domain`,
`src/hub/integrations`, and `src/hub/persistence`; these modules are active
runtime components. Fresh end-to-end campaign evidence is still pending.

> Modules: `hub.core.event_bus`, `hub.core.matrix_service`,
> `hub.core.models`, `hub.core.name_store`,
> `hub.domain.action_runner`, `hub.domain.visibility`,
> `hub.integrations.base`, `hub.integrations.hub_client`,
> `hub.integrations.hub_client_local`, `hub.integrations.hub_client_http`,
> `hub.persistence.migrations`, `hub.openapi`, `hub.env`.

The runtime uses the `src/hub/` modules through the composition root. Unit
tests continue to exercise component contracts directly; startup and
cross-surface tests cover their wiring. The two scopes are distinct. The
[runtime validation index](validation/RUNTIME_VALIDATION_INDEX.md) tracks
fresh integrated campaign evidence for the exact candidate commit.

### `hub.core` — framework owner of matrix state

#### `MatrixService` (`hub.core.matrix_service`)

* **Status:** instantiated by the shared composition as matrix state owner
  and publisher of cached changes.
* **Role:** owns the single matrix client and last-known snapshot. REST and
  integrations consume the same service state through adapters.
* **Public methods:** async `connect()`, `disconnect()`,
  `refresh_snapshot()`, `switch(input_num, output_num=None)`,
  `recall_preset(slot)`, `save_preset(slot)`, `set_power(on)`,
  `rename_port(kind, port, name)`, `rename_preset(slot, name)`; synchronous
  `snapshot()`. Raw status reads such as `get_video_status()` belong to the
  wrapped matrix-client protocol and are used by the service to refresh state.
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

* **Status:** registry of port counts and capabilities for matrix models;
  services consume it where capability-aware ranges apply. Other listed
  device families remain candidates until hardware validation.

#### `NameStore` (`hub.core.name_store`)

* **Status:** shared runtime store of input, output and preset names, projected
  to REST and Remote clients from common state.

#### `EventBus` (`hub.core.event_bus`)

* **Status:** runtime event bus; `subscribe(cb, topics=None)` returns
  an idempotent unsubscribe function. Sync callbacks run inside
  `publish(topic, data)`; async callbacks are scheduled as tasks.
  Failures in one subscriber do not block the others.

### `hub.domain` — framework action executor

#### `ActionRunner` (`hub.domain.action_runner`)

* **Status:** shared runtime dispatcher used by REST and Remote action
  adapters, with compatibility projections at each public surface.
* **Role:** the executor of `profile`, `scene`,
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

* **Status:** utility for centralizing `favorite` / `dashboard_visible` state;
  route ownership remains manager-specific where existing REST contracts
  require it.

### `hub.integrations` — framework opt-in surface + transport clients

> Modules: `hub.integrations.base`,
> `hub.integrations.hub_client`, `hub.integrations.hub_client_local`,
> `hub.integrations.hub_client_http`,
> `hub.integrations.{unfolded_circle,flic,homeassistant}`.

* **`Integration` base class (`hub.integrations.base`)** — the
  `start(hub)` / `stop()` / `health()` / `routes()` lifecycle, plus
  `IntegrationRegistry` (`register(name, env_flag, import_path)`)
  and `IntegrationLoader` (`load()`, `start(hub)`, `stop()`,
  `routes()`, `health_summary()`). The runtime uses the loader to start
  enabled adapters. `src/driver.py` and its legacy integration modules remain
  in the tree as reference code but are not launched.
* **`HubClient` (Protocol) + `HubClientLocal` + `HubClientHttp`**
  (`hub.integrations.{hub_client,hub_client_local,hub_client_http}`)
  — the transport-independent async hub contract. `HubClientLocal` connects
  the runtime service to local integrations, while the HTTP client remains
  available for remote integrations and tests.
* **`src/hub/integrations/unfolded_circle/`**, **`flic/`**,
  **`homeassistant/`** — the framework modules that ship the same
  lifecycle on top of `HubClient`. The shared runtime registers and loads them
  by environment flag. The HACS component at `custom_components/hdmi_matrix/`
  is separately installed and uses REST.

### `hub.persistence.migrations` — framework versioned JSON

> Module: `hub.persistence.migrations`.

* **Status:** runtime startup preparation uses migration chains and atomic
  backups before managers or Flic are constructed. `src/persistence.py`
  continues to resolve data paths and selected legacy preferences. Not every
  persisted file has a schema envelope; see the startup storage contract.
* **Managed file names:** `scenes_v2.json`,
  `profiles.json`, `cec_macros.json`, `shortcuts.json`,
  `dashboard_layout.json`, `device_settings.json`,
  `flic_buttons.json`; the legacy shortcuts filename remains supported.

### `hub.openapi` — framework contract generator

> Module: `hub.openapi`.

* **Status:** the REST application serves the generated document. `build_openapi_spec(app)` introspects
  the live `aiohttp.web.Application` and returns the OpenAPI 3.1
  JSON document; `validate_openapi_spec` is the structural validator.
* **Mount points:** `GET /api/openapi.json` for the raw document and
  `GET /api/docs` for Swagger UI.

### `hub.env` — framework canonical env table

> Module: `hub.env`.

* **Status:** framework inventory. Exports `CORE_ENV_VARS` and
  `INTEGRATION_ENV_VARS`, the `EnvVar` dataclass, and
  `resolve_hub_env()`. Runtime parsing and alias warnings are owned by
  `hub.cli`; the inventory is useful reference material but is not the
  runtime source of truth.
* **Full operator-facing table:** owned by the `wp-g2-openapi-swagger-
  config-docs` worktree as [`docs/CONFIGURATION.md`](CONFIGURATION.md).

---

## 3. Integration flags and optional imports

The runtime loader lazily imports each integration when enabled. A disabled
integration creates no listener or lifecycle work. Flic defaults enabled for
compatibility; UC and HA discovery default disabled.

| Flag | Unset default | Enabled behavior | Disabled behavior |
| --- | --- | --- | --- |
| `UC_ENABLED` | `false` | Starts the Remote 3 SDK adapter on its configured port (9095 default). | No UC/`ucapi` import, listener or advertisement. |
| `FLIC_ENABLED` | `true` | Loads Flic registry and registration/list routes. | Omits only Flic routes and registry lifecycle; core REST actions remain. |
| `HA_DISCOVERY_ENABLED` | `false` | Starts optional mDNS discovery for the REST service. | No HA discovery import or Zeroconf dependency for HA. Manual HACS setup remains available. |

Boolean spellings are trimmed and case-insensitive: `1`, `true`, `yes`, `on`
enable; `0`, `false`, `no`, `off` disable. Unknown nonblank Flic values warn
and retain the enabled default.

### `/api/integrations` route

There is **no `/api/integrations` general route** in the shipped app.
The only `/api/integrations/*` paths are Flic-specific and are mounted only
when Flic is enabled:

* `POST /api/integrations/flic/register` — Flic Hub button discovery.
* `GET  /api/integrations/flic/buttons` — read registered Flic buttons.

There is no `/api/integrations/<name>/status` route. `/api/health` includes
an `integrations` lifecycle mapping under `data.integrations`; it does not
create a separate integrations endpoint. The response also returns:

* `status`, `service`, `api_version`, `version` (legacy shape),
* `matrix` (connection summary, see `src/rest_api/core.py`),
* `runtime` (event-loop lag, uptime, task count),
* `integrations` (integration lifecycle mapping, commonly empty when none
  report health).

The mapping is supplied by `IntegrationLoader.health_summary()` and remains
inside the existing health response envelope.

---

## 4. Event topics — `hub.core.EventBus.STANDARD_TOPICS`

The eight topics are used by the runtime event bus and local subscribers. They
are listed here because the
`hub.integrations.{flic,homeassistant,unfolded_circle}` framework
modules publish and consume them and the
[`docs/api/websocket.schema.json`](api/websocket.schema.json) frames
named after them; the actual REST `install_event_stream` poll uses a
subset of those names.

The `EventBus.subscribe(cb, topics=None)` signature is implemented in
`hub.core.event_bus`. Runtime services and local clients subscribe through
this interface; WebSocket consumers receive their existing REST frame format.

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

## 6. Validation status and evidence provenance

The feature ledger records its own commit and freshness for each row. Earlier
RC1 API/browser/Remote/HA/Flic records remain evidence for their recorded
candidate; they do not validate runtime completion. The coordinator's fresh
integrated software campaign is pending and will be indexed by exact commit in
the [runtime validation index](validation/RUNTIME_VALIDATION_INDEX.md).

Simulator, scripted Remote, HA-container, browser and request-replay evidence
are limited to their exercised software paths. They do not prove physical
matrix/TV effects, Remote or Flic device behavior, physical-LAN HA discovery,
field recovery, or the 72-hour soak. Those owner-observed gates remain pending.
The [feature ledger](validation/LEDGER.md) and
[validation report](validation/VALIDATION_REPORT.md) retain feature-level and
historical evidence.

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
