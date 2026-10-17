# Project Roadmap

> Status of every phase of the **8×8 HDMI Matrix Hub** project. Each entry
> links to the merged code paths, the validation evidence, and the related
> docs under `docs/`.
>
> **Spec for "done":** [`docs/validation/VALIDATION_PLAN.md`](docs/validation/VALIDATION_PLAN.md). A release
> tag is only honest when every claim is backed by a passing evidence record
> at the level the plan requires (`V2` on the simulator, `V3` from a real
> client, `V4` on hardware with the operator present, `V5` after the 72 h
> soak). Where evidence is not at target the ledger says so under
> [`docs/validation/LEDGER.md`](docs/validation/LEDGER.md).

---

## 1. Release channels

| Channel | State | Next tag | Source of truth |
| --- | --- | --- | --- |
| **Latest** | merged work | **`v0.5.0` ("Focused UI")** once Phase 5 ships to `main` | tagged commit on `origin/main` |
| **Stable** | merged work | **`v0.4.0` ("Consolidate")** already tagged | `git tag -l` reports `v0.3.0`, `v0.4.0` |
| **Long-term** | open | **`v1.0.0` ("Release")** — Phase 8 validation campaign | this document |

Only `v1.0.0` carries a public "all features at target, hardware signed off"
claim. Every earlier tag is a milestone that records what was merged, with
the ledger honest about which features still need real-device proof.

---

## 2. Release history

The history is **read from the ledger**, not written here by hand, so the
roadmap cannot drift from the registry. Each phase links to the tags it
produced and the evidence directory it populated.

### v0.5.0 — "Focused UI" — Phase 5 (WP-E2) — *ready for Phase 6/7 merge*

- **Goal.** Drop the side-nav drawer + nine-page Settings drawer + three
  editor shells for one `UnifiedSettingsController` (9-section `#settings/*`
  hash routing), one stack-aware `OverlayManager`, one `EditorShell` (with a
  searchable command/step picker in place of `window.prompt()`), one shared
  `CecRemote`, one shared `KioskController` plus a server-backed
  `DashboardStore`, and a design-token sheet (`web/css/tokens.css`,
  `:focus-visible`, 44 px touch targets, 4 Tron presets, 30 fps background).
- **Source.** `web/js/core/` (ES modules: `api.js`, `ws.js`, `state.js`,
  `html.js`, `overlay.js`, `toast.js`, `index.js`), `web/js/components/`
  (`unified-settings-drawer.js`, `editor-shell.js`, `cec-remote.js`,
  `kiosk-controller.js`, `dashboard-store.js`), `web/css/tokens.css`.
- **CI gate.** `npm run lint:js` 0 new findings, `npm run lint:css` 0 new
  findings, Playwright smoke (`tests/e2e/`) green, visual baselines
  preserved. See the WP-E2 tracks in
  [`orca-phased-roadmap.md`](orca-phased-roadmap.md) §Phase 5.
- **Evidence.** [Ledger — Web UI](docs/validation/LEDGER.md#web-ui-f-ui) shows
  V1 unit + V3 browser scenarios for every shipped surface; **V4 hardware is
  not yet recorded for v0.5.0** (HIL Session 2 is the next step, see §5).

### v0.4.0 — "Consolidate" — Phase 4 (WP-C3) — **tagged** at commit `25233bb`

- **Goal.** One runtime entry point (`run.py`), one owner of state
  (`hub.core.MatrixService`), one executor
  (`hub.domain.ActionRunner`), modular opt-in integrations
  (`hub.integrations.{flic,homeassistant,unfolded_circle}`), versioned
  persistence (`hub.persistence.migrations`, `schema_version`), and the
  OpenAPI 3.1 spec generator (`hub.openapi.build_openapi_spec`).
- **Source.** `src/hub/core/{matrix_service,models,name_store,event_bus}.py`,
  `src/hub/domain/{action_runner,visibility}.py`,
  `src/hub/integrations/{hub_client,hub_client_local,hub_client_http,base}.py`
  and the three integration packages, `src/hub/persistence/migrations.py`,
  `src/hub/{env,openapi}.py`.
- **CI gate.** 401 new unit tests; `python -m ruff check`, `python -m mypy`,
  targeted `pytest` per track; PR #35 13/13 green.
- **Evidence.** [Ledger — Domain features](docs/validation/LEDGER.md#domain-features-f-dom),
  [REST/WS contract](docs/validation/LEDGER.md#restwebsocket-contract-f-api). Profile
  / scene / macro / shortcut / preset CRUD paths each have V2 simulator
  evidence; a feature the ledger lists as `stale` is one whose scenario
  covers files that have changed since the evidence was committed.

### v0.3.0 — "Secure" — Phase 3 (WP-F1) — **tagged**

- **Goal.** Bring the access model, the SSRF guard, the PIN/lockout flow,
  TLS fingerprint pinning, and the public `SECURITY.md` policy up to a
  publishable baseline. Auth comes in three forms: admin session cookie,
  `X-API-Key` header, `?key=` query for clients that cannot set headers.
- **Source.** `src/hub/integrations/unfolded_circle/{config,entities,handlers,state,mdns,migration}.py`,
  `custom_components/hdmi_matrix/` (HA config flow, services, binary
  sensors), `SECURITY.md`, `tests/test_security_*.py`.
- **CI gate.** 13/13 CI checks green on PR #34; release tag `v0.3.0` pushed.
- **Evidence.** [Ledger — Security controls](docs/validation/LEDGER.md#security-controls-f-sec),
  [Reliability](docs/validation/LEDGER.md#reliability-f-rel). V3 reached for the
  three auth configurations (no PIN, admin PIN, admin + control PIN); V4
  spot check with an admin PIN pending HIL Session 2.

---

## 3. What this repo ships today

The flagship of the runtime is the **modular hub package** under `src/hub/`.
The README (`README.md`, DOC-02) and the architecture document
([`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)) describe it in full; the
short version is:

- `hub.core` — the single owner of matrix state.
- `hub.domain` — the single executor of profiles, scenes, macros, shortcuts
  and hardware presets, with one normalized `ActionRunResult` shape.
- `hub.integrations` — the opt-in `Integration` framework + the
  transport-independent `HubClient` (`HubClientLocal`, `HubClientHttp`).
- `hub.persistence` — versioned migrations for every JSON file (`PER-04`).
- `hub.env` — one canonical table of every environment variable, with
  aliases warned about at start-up (`DI-12`).
- `hub.openapi` — OpenAPI 3.1 spec generator (`API-21`, `TD-09`, `DOC-03`).
- `src/rest_api/` (22 modules) and `src/driver.py` (the legacy
  UC-driver entry) — thin adapters that delegate all state to the hub
  package above.
- `web/js/core/` — the Focused-UI ES modules
  (`api`, `ws`, `state`, `html` with XSS-safe escape, `overlay`, `toast`).
- `web/js/components/` — the unified drawer, the editor shell, the CEC
  remote, the kiosk controller, the dashboard card picker (WP-E2 tracks).

The web UI at `/ui` and the kiosk at `/kiosk` are part of the core (they do
**not** require `UC_ENABLED=true`).

---

## 4. What is shipped but pending real-device proof

This is the gap the roadmap must be honest about: every claim in the
README and the changelog that says a feature "works" is, today, a
**simulator** claim. The simulation matrix runs the same command set as a
real OREI BK-808; the hub code path is real; the response envelopes are
real; the device readback is from a real `OreiMatrix` instance against a
real matrix simulator running on the hub host. None of that is a real
TV, a real OREI BK-808 with the firmware the field ships, or a remote
operator watching the display change.

| Area | Today (Ledger row) | Why that is not yet v1.0.0 evidence |
| --- | --- | --- |
| **Matrix control** (routing, presets, output settings, EDID, audio, system) | mostly **V3** (simulator + browser/HA/UC), some **V1** (settings still capped at V1 by HIL-09 / `hdcvt-port-led` flicker) | No recorded `V4` (real OREI BK-808) for any v0.5.x build. |
| **CEC control** (sources, TVs, Telnet path) | mostly **V3**, **V1** on the Telnet-CEC path | Physical observation (TV turns on, source switches) requires the operator-present sessions in §5. |
| **REST/WS contract** | all routes **V2** or **V3** | nothing caps it; re-runs are cheap. |
| **Web UI / kiosk flows** | mostly **V3** on simulator; **V1** for hardware (`UI-44` real-device visual baselines) | Playwright drives the shipped image, not a tablet in a living room. |
| **Remote 3 integration** | entities defined, scripted Remote at **V3** | V4 still wants the operator's Remote 3 against a real matrix. |
| **Home Assistant component** | mostly **V3** (real HA container at the registry versions), **V1** for HA-YAML | no HA deployment is run by the validation framework yet. |
| **Flic** | **V3** (request replay), **V4 if hardware is available, otherwise reported as "not validated on hardware"** | Flic hardware sits in the "available when the owner plugs it in" bucket. |
| **Security controls** | **V3** with the three auth configurations; **V4** spot check pending HIL Session 2 | covers `SEC-01..SEC-08` plus the device-token rotation. |
| **Reliability** | mostly **V1** (fault-injection on the simulator); **V5 soak not yet run** | V5 needs 72 h of `python -m tools.validate run` against the sim with flat resource metrics and a real-device spot check. |

The full row-by-row state, with the freshness of each piece of evidence
and the open findings, is in [`docs/validation/LEDGER.md`](docs/validation/LEDGER.md).
A feature is "below target" when the ledger says it is.

---

## 5. What comes next

### Phase 6 — Repository hygiene (WP-G1) — *in flight on `wp-g1-g2-release-and-docs`*

- **`wp-g1-packaging-version-locks`** — delete `setup.py`, single
  `hub.__init__.__version__` (DEP-04, DEP-06), hashed `requirements.txt`
  + `requirements-dev.txt` (DEP-08, SEC-15).
- **`wp-g1-ci-multiarch-hygiene`** — CI binary/size guard rejecting
  `*.bin`/`*.exe`/`*.c4z`/`*.har` and >2 MB non-LFS files; digest-pinned
  base images + SHA-pinned GitHub Actions; multi-arch (`amd64` + `arm64`,
  `DI-10`); repo cleanup (DEP-09, DEP-12, DEP-13, BE-27, API-17).
- **`wp-g1-license-asset-audit`** — license audit of every bundled icon,
  font and asset; `THIRD_PARTY_NOTICES.md` (UI-22); update
  `docs/OREI_API_COMMANDS.md` from HIL-A captures + Telnet section
  (DOC-11).
- **Documentation deliverables:**
  - `README.md` rewrite (DOC-02) — done in this branch.
  - `docs/ARCHITECTURE.md` rewrite — done in this branch.
  - `docs/INTEGRATIONS.md` new — done in this branch.
  - `CHANGELOG.md` new — done in this branch.
  - `ROADMAP.md` new (DOC-01) — this document.
  - `docs/README.md` unified index (DOC-10) — done in this branch.
  - `docs/CONFIGURATION.md` generated against `src/hub/env.py` — owned by
    `wp-g2-openapi-swagger-config-docs`.
  - `docs/API_REFERENCE.md` generated from OpenAPI + WebSocket schema
    (DOC-03) — owned by `wp-g2-openapi-swagger-config-docs`.
  - `HOME_ASSISTANT.md` (DOC-04), `DOCKER.md` (DOC-05), `FLIC_SETUP.md`,
    `CONTRIBUTING.md` (DOC-13), `UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`
    (UC-20) — owned by `wp-g2-client-guides-doc-archive`.
- **Tests:** `tests/test_core_documentation.py` (structural checks on
  every owned doc) — done in this branch.

### Phase 7 — Validation campaign (WP-V3) — *after Phase 6*

- **HIL Session 2** — owner-present V4 runs of routing, presets, matrix
  power, CEC power/volume on the TV, one profile recall (see
  [`docs/validation/HIL_SESSION_2_RUNBOOK.md`](docs/validation/HIL_SESSION_2_RUNBOOK.md)).
- **HIL-B** — regression; **HIL-C** — fault injection on the real device;
  **HIL-D** — 72 h soak (V5 evidence); **HIL-E** — real clients.
- **`docs/validation/VALIDATION_REPORT.md`** — feature × client matrix,
  firmware versions, the CEC table.
- **Supported Models table** trimmed to what was validated on hardware.
- **Tag `v1.0.0`** when every `F-*` row in the ledger is at or above
  target with fresh evidence.

---

## 6. What is **not** on the roadmap

A short list of things the project deliberately does not promise, so users
do not wait for them:

- **Other matrix brands.** The protocol covers OREI BK-808 / HDCVT
  HDP-MXC88A class; other 8×8 HDMI 2.1 matrices from the same OEM family
  are *probable*, but they are not on the supported list until HIL evidence
  shows the read/write surfaces match. See the "Supported Models" table in
  the README.
- **Scheduling.** Cron-like triggers for profile recall are not in any
  in-flight worktree; they are a research item, not a project promise.
- **MQTT broker integration.** The opt-in `Integration` framework can
  carry it (one integration module, one env flag), but no MQTT worktree
  exists; do not assume it will ship.
- **A native Alexa skill.** The path is "control it through Home
  Assistant"; a skill that bypasses HA is not on the plan.
- **A full rewrite of the web UI in a heavy framework.** The Focused UI
  is ES modules + tokens + the unified drawer; no React/Vue rewrite is
  scoped.

If something you want is in this list, open an issue with what the use
case is and what protocol/API the device exposes.

---

## 7. How to read this roadmap

- **What shipped is true today.** A tag is a snapshot of the merge branch,
  not a forward promise. The changelog records what changed in each tag;
  the ledger records what the tag did and did not prove.
- **What is pending is dated.** HIL Session 2 is the next concrete step
  on the V4 path; the ledger's "Stale evidence" column is what we will
  refresh there.
- **What is not promised stays out.** This is the list above; if a feature
  is not listed in §3, §5 or this repo's issues, it is not on the plan.

For everything that did not fit here — the validation evidence tree, the
scenario mechanics, the contribution rules — see
[`docs/README.md`](docs/README.md).
