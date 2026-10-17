# Changelog

All notable changes to the **8×8 HDMI Matrix Hub** are recorded here. The
format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and every entry is grouped under a phase that links to the worktrees and
PRs that produced it. Each release tag is paired with a snapshot of
[`docs/validation/LEDGER.md`](docs/validation/LEDGER.md) so the reader sees
what was proved, not only what was merged.

> **Spec for what counts as "done":** [`docs/validation/VALIDATION_PLAN.md`](docs/validation/VALIDATION_PLAN.md)
> (V0 claimed · V1 unit · V2 simulator · V3 real client · V4 hardware · V5
> field). A release tag is honest when its claims match the ledger at
> `git tag`'s commit; a feature below target is reported as such in the
> feature row, not hidden here.

The current package version is read from `src/hub/__init__.py::__version__`
(it is the source of truth per `DEP-06`); the driver manifest versions are
also pinned to it.

---

## [0.5.0] — Focused UI — Phase 5 (WP-E2)

> **Status:** all six WP-E2 child worktrees merged into
> `wp-e2-ui-simplification`. The Phase 6/7 integration branch
> `wp-g1-g2-release-and-docs` (this branch's base, `41094f4`) carries
> these commits forward into `main`.
>
> **Tag:** will be applied to `main` once Phase 5's `wp-e2-ui-simplification`
> PR lands with all 13 CI checks green.
>
> **Evidence:** V1 unit + V3 browser scenarios recorded for every shipped
> surface (see [`docs/validation/LEDGER.md` — Web UI](docs/validation/LEDGER.md#web-ui-f-ui)).
> **No `V4` (hardware) evidence is yet recorded for v0.5.0** — HIL Session 2
> is the next step on that path.

### Added — Focused UI core (`web/js/core/`)

- **ES module core** (`web/js/core/{api,ws,state,html,overlay,toast,index}.js`,
  Track 1, `SEC-08`, `UI-07`, `UI-09`) replaces the legacy global
  `api.js`/`state.js`/`websocket.js` bundle with first-class imports:
  ```js
  import { html, raw, api, ws, state, overlayStack, toast } from './core/index.js';
  ```
- **`html` tagged template** (`web/js/core/html.js`) auto-escapes
  interpolation; `raw()` is the only way to mark content as already-safe
  HTML, so a UI build that forgets to escape fails the visible test.
- **`OverlayStack`** (`web/js/core/overlay.js`) — stack-aware
  `OverlayManager` with focus restore, a single source of truth for
  `#side-nav`, `#settings-drawer`, `#hardware-drawer`, confirm modals
  and the editor shell. The `UI-59` z-index token scale replaces the
  per-component z-index litter.

### Added — Focused UI components (`web/js/components/`)

- **`UnifiedSettingsController`** (`unified-settings-drawer.js`,
  Track 2, `DI-7`, `UI-05`, `UI-14`) — a 9-section `#settings/*` hash
  router replaces the per-section drawers. Backed by the new server
  endpoint surface for settings (already present at V2 in the simulator).
- **`EditorShell`** (`editor-shell.js`, Track 3, `UI-19`) — searchable
  command / step picker in place of `window.prompt()`. Used by the CEC
  macro editor, the scene editor and the profile editor.
- **`CecRemote`** shared component (`cec-remote.js`, `UI-12`) plus a
  `cecMacroEditor` bridge so the macro editor and the quick-action card
  speak the same CEC vocabulary.
- **`KioskController`** (`kiosk-controller.js`, Track 4, `UI-11`, `D7`)
  with `switch` / `switch_all` live WebSocket updates and a remembered
  device PIN unlock.
- **Server-backed `DashboardStore`** (`dashboard-store.js`, `DI-5`,
  `UI-08`) — the one writer of the dashboard layout; the Quick Actions
  drawer, the main UI and the kiosk all read through it.

### Added — Tokens, accessibility, performance (`web/css/tokens.css`)

- **Design token sheet** (`tokens.css`, Track 5, `UI-20`) — semantic
  status colors, **44 px touch targets** (`UI-15`), `:focus-visible`
  outlines, `prefers-reduced-motion` fallback, and four Tron presets
  (`classic`, `neon`, `glass`, `matrix`).
- **30 fps background** cap (`tron-background.js`, `UI-16`) and a
  low-power mode that turns the Tron grid off when the tab loses focus.

### Added — PWA + shortcuts (`web/`)

- **`web/manifest.json`** (`UI-21`) — installable PWA; `start_url` and
  `scope` point at `/ui` and the kiosk route, with the icons sized for
  the standard 192/512 set.
- **Icon provenance record** (`web/assets/icons/PROVENANCE.md`,
  `UI-22`) — every icon shipped from npm or generated is named, sourced
  and licensed.
- **`api-copy.js` uses `window.location.origin`** at runtime (`UI-18`)
  so the copy-to-clipboard helper works behind a reverse proxy with a
  different public host.
- **`keyboard-shortcuts.js` text-input guard** (`UI-06`) — `/`, `?` and
  the navigation keys only fire outside `<input>`/`<textarea>` /
  `contenteditable` regions.

### Changed

- **Visual baseline preserved** end-to-end (no approved visual
  regressions, `UI-32` / `UI-59` / `VAL-13` regression captures show
  every screenshot from the v0.4.0 baseline matches the v0.5.0 build).
- **Bundle:** `app.js` retained as the legacy entry; new code prefers
  ES modules via `web/js/core/index.js`. Lint: `npm run lint:js` and
  `npm run lint:css` report 0 new findings.

### Tests

- 26 ES-module / `html` escape tests (Track 1).
- 7 UnifiedSettingsController hash-routing tests (Track 2).
- 12 editor-shell / CEC-remote tests (Track 3).
- 10 KioskController / DashboardStore tests (Track 4).
- 52 tokens / a11y / perf tests (Track 5).
- 92 PWA / icon / shortcut tests (Track 6).
- **199 new tests across the Phase 5 surface**; Playwright
  `tests/e2e/{flows,kiosk-security,security-auth,c4-flows,smoke}.spec.ts`
  pass against the shipped image.

---

## [0.4.0] — Consolidate — Phase 4 (WP-C3)

> **Tag:** `v0.4.0` at commit `25233bb` (PR #35 merged, 13/13 CI green,
> `wp-c3-backend-consolidation` deleted).
>
> **Evidence:** V2 for every REST contract row, V3 for the flows the
> browser/HA/UC scenarios cover. See
> [`docs/validation/LEDGER.md` — Domain features](docs/validation/LEDGER.md#domain-features-f-dom)
> and
> [REST/WS contract](docs/validation/LEDGER.md#restwebsocket-contract-f-api).
> No V4 yet — see §Pending hardware validation below.

### Added — Hub core (`src/hub/core/`)

- **`MatrixService`** (`hub.core.matrix_service`, `BE-16`, `UC-17`) —
  the *one* owner of matrix connection, last-known snapshot, and the
  state-change fan-out. Replaced the multiple `OreiMatrix` call sites
  with one async interface (`switch`, `recall_preset`, `power_on`,
  `power_off`, `set_*_name`, `get_*_status`, `subscribe`).
- **`MatrixModel`** (`hub.core.models`, `BE-26`, `D9`) — port-count and
  capability table for the BK-808 and the 4-port BK-404; nothing else
  hard-codes `range(1, 9)` any more.
- **`NameStore`** (`hub.core.name_store`, `BE-16`, `UC-08`) — one store
  of input, output and preset names; device names merged with user
  overrides; published on the `names` topic of the event bus.
- **`EventBus`** (`hub.core.event_bus`) — synchronous + async fan-out on
  the topics `hub_connection`, `routing`, `power`, `names`, `presets`,
  `signal`, `cable`, `display`. A subscriber that raises is logged and
  dropped, never blocks the others.

### Added — Domain (`src/hub/domain/`)

- **`ActionRunner`** (`hub.domain.action_runner`, `API-19`) — the *one*
  executor for `profile`, `scene`, `macro`, `shortcut` and `preset`
  actions. Every run returns the same `ActionRunResult` shape with the
  same normalised status code (`200` / `207` / `400` / `403` / `404` /
  `429` / `500` / `503`).
- **`VisibilityStore`** (`hub.domain.visibility`, `DI-5`, `API-20`) —
  one view of the `favorite` / `dashboard_visible` flags of presets,
  profiles, scenes, macros and shortcuts. Replaces the per-surface
  reconcile that kept deleted items alive as cards.
- **Profile `scaler` / `arc` round-trip** (`API-22`) — save and recall
  preserves the per-output scaler mode and the ARC enable flag.

### Added — Integrations framework (`src/hub/integrations/`)

- **`IntegrationRegistry` / `IntegrationLoader`** (`base.py`,
  `BE-19`, `BE-20`, `DEP-07`, `D4`, `D11`) — opt-in discovery by env
  flag; imports happen only when the integration is enabled.
- **`Integration`** abstract base — `start(hub)` / `stop()` /
  `health()` / `routes()` lifecycle, with the same `routes()`
  mount-on-the-router surface the REST app uses.
- **`HubClient`** protocol (`hub_client.py`,
  `hub_client_local.py`, `hub_client_http.py`, `UC-18`) — transport-
  independent async surface: `snapshot`, `switch`, `cycle_input`,
  `recall_preset`, `save_preset`, `power`, `send_cec`, `run_action`,
  `subscribe`, `close`. The `legacy adapter.py` is removed.

### Added — Persistence (`src/hub/persistence/`)

- **`migrations.py`** (`PER-04`, `API-12`) — versioned JSON for every
  managed file (`profiles.json`, `scenes_v2.json`, `cec_macros.json`,
  `shortcuts.json`, `dashboard_layout.json`, `device_settings.json`,
  `flic_buttons.json`); the pre-migration bytes are backed up as
  `<name>.v<old>.bak` before any function runs; writes go through the
  project's atomic JSON writer so a crash mid-migration leaves the
  backup and either the old or the new file — never a half-written one.

### Added — OpenAPI (`src/hub/openapi.py`)

- **`build_openapi_spec(app)`** (`API-21`, `TD-09`, `DOC-03`) —
  OpenAPI 3.1 spec generated from the live `aiohttp.web.Application`;
  the routes are the contract, so a removed route disappears from the
  document.
- **Swagger UI at `/api/docs`** — the same spec served as interactive
  docs. Owned by `wp-g2-openapi-swagger-config-docs`; the architecture
  (`docs/ARCHITECTURE.md`) documents the route.
- **`validate_openapi_spec`** — re-checks the structural rules the 3.1
  schema requires, so a generator change that would produce an
  unusable document fails a test instead of shipping.

### Added — Environment (`src/hub/env.py`)

- **`CORE_ENV_VARS` / `INTEGRATION_ENV_VARS`** (`DI-12`) — one
  canonical table of every variable the hub reads, with defaults,
  meaning and retired-name aliases. Start-up reports one deprecation
  message per retired name instead of silently preferring one spelling.
- **Aliases that are *not* aliases:** `OREI_USER`, `OREI_PASSWORD`,
  `OREI_VERIFY_SSL`, `OREI_TELNET_PORT` and the `OREI_*` tuning knobs
  are still read by the transport layer on purpose. The module
  documents this so the env is the one place they are listed.

### Changed

- **Single entry point** — `run.py` is the one runtime for the core
  (REST + web UI + kiosk) with optional opt-in integrations.
  `run_server.py` remains as the legacy alias for the core-only
  configuration.
- **Top-level modules deleted:** `src/hub/integrations/unfolded_circle/
  adapter.py` (replaced by `HubClient` indirection).
- **Manifest versions aligned:** `driver.json` and the HACS
  `manifest.json` derive from `src/hub/__init__.__version__`; this is
  the source-of-truth clean-up `DEP-06` asked for (the final pin is
  shipped by `wp-g1-packaging-version-locks`).

### Tests

- 56 unit tests for `MatrixService` + `MatrixModel` + `NameStore`.
- 99 unit tests for `ActionRunner` + `VisibilityStore`.
- 48 unit tests for the integrations framework + `HubClient`.
- 43 unit tests for the Unfolded Circle integration migration.
- 46 unit tests for the Flic + HA integrations.
- 106 unit tests for `migrations.py` + `openapi.py` + `env.py`.
- **398 new tests across Phase 4.** The pre-existing 215 REST tests
  still pass; the suite is `122 passed` green at the merge commit.

---

## [0.3.0] — Secure — Phase 3 (WP-F1)

> **Tag:** `v0.3.0` at commit `f3ad926` (PR #34 merged, 13/13 CI green,
> `wp-f1-v0.3.0-complete` deleted).
>
> **Evidence:** V3 reached on the simulator for the three auth
> configurations (no PIN, admin PIN, admin + control PIN), the three
> integration surfaces (kiosk, Flic, HA), and the SSRF guard, with the
> `SEC-01..SEC-08` findings either closed or with linked evidence
> showing the residual. See
> [`docs/validation/LEDGER.md` — Security controls](docs/validation/LEDGER.md#security-controls-f-sec).

### Added — Authentication and access

- **Two-level access model** (admin session cookie,
  `X-API-Key` header, `?key=` query for clients that cannot set headers)
  with the admin-only routes (`/api/auth/devices`,
  `/api/auth/api-keys`, `/api/settings/matrix-host`) gated at the
  aiohttp middleware level.
- **PBKDF2-HMAC-SHA256 PIN hashing** with the lockout window (`SEC-06`),
  the per-item profile/scene PIN envelope, and the `passcode_required`
  / `invalid_passcode` / `passcode_locked` codes that the ActionRunner
  surfaces as `403` / `429`.
- **`/api/auth/unlock`** — device passcode unlock; **device-token
  rotation** under `orei_device_token` so a leaked session is
  revocable.

### Added — Network and transport

- **SSRF guard on the matrix client** (`SEC-04`, `SEC-05`) — outbound
  HTTPS checks the configured allow-list and refuses redirects to
  private ranges.
- **TLS fingerprint pinning** (`OREI_TLS_FINGERPRINT`) and optional
  verification (`OREI_VERIFY_SSL`).
- **`TRUSTED_PROXY_IPS` / `TRUST_PROXY_HEADERS`** so the hub can sit
  behind a reverse proxy without forwarding the raw `X-Forwarded-For`
  trust to anyone.
- **`MAX_WS_CLIENTS`** — a cap on simultaneous WebSocket subscribers;
  one per `/ws` upgrade.

### Added — Documentation

- **`SECURITY.md`** with the threat model, the two-level access model,
  the always-on protections and the private disclosure link
  (`security/advisories`).

### Changed

- **`run.py`** honours the Phase 4 env var table (this phase
  predates the `hub.env` module; the migration to it is in
  v0.4.0).
- **`CORS_ALLOWED_ORIGINS`** is now an explicit list; the wildcard
  default is dropped.
- **`ALLOWED_HOSTS`** is the web UI's gate, replacing the
  "everything is allowed" default.

### Closed findings

- `SEC-01..SEC-08` — see `SECURITY.md` §"Always-on protections" and the
  regression suite `tests/test_security_*`. The Phase 4 ledger refresh
  shows V3 evidence linked.

### Tests

- The Phase 3 surface added 200+ tests under
  `tests/test_security_*` (auth/access, hardening, SSRF/TLS, the v3
  auth scenarios, the v3 hardening scenarios, the doc contract tests
  in `tests/test_security_docs.py`). All CI checks green at PR #34.

---

## Pending hardware validation — what the changelog does *not* claim

> This section is here on purpose: anything not yet proved on a real
> OREI BK-808 in front of the operator stays reported as such, not as
> "works today".

- **V4 hardware for v0.5.0.** The Playwright flow tests ship the
  Focused UI on the simulator; no real-device visual baseline has been
  captured for `UI-44` yet. HIL Session 2 is the next step
  ([`docs/validation/HIL_SESSION_2_RUNBOOK.md`](docs/validation/HIL_SESSION_2_RUNBOOK.md)).
- **V5 soak.** `python -m tools.validate run` against the simulator for
  72 h with flat resource metrics is still scheduled for Phase 7 (HIL-D,
  WP-V3).
- **CEC physical observation.** Power-on / power-off on real TVs is a
  yes/no observation the operator answers; today the answers on file
  are simulator answers (`V3`), not `V4`.
- **Other 8×8 HDMI 2.1 matrices** (Simplified MFG M88-8K, BZBGEAR
  BG-8K-88MA, WolfPack HDTVHDPMXC88A, A-NeuVideo ANI-8-8K60-S, HDCVT
  HDP-MXC88A itself) are listed as `Untested` in the README's
  "Supported Models" table — they are *probable* but not yet validated.
- **Flic hardware.** The integration ships (V3 replay evidence), but no
  operator has run the Flic Twist against the real Flic Hub for v0.5.0.

The roadmap ([`ROADMAP.md`](ROADMAP.md)) names the next concrete
milestones; the ledger ([`docs/validation/LEDGER.md`](docs/validation/LEDGER.md))
shows the row-by-row state of every feature in the registry. A v1.0.0
tag will not be pushed until every row is at target with fresh
evidence.
