# Project Roadmap

The runtime-completion implementation is integrated in the current candidate:
shared startup, persistence wiring, UC integration, action dispatch and optional
Flic/HA lifecycle. The fresh integrated software campaign is coordinator-owned;
physical hardware, field and soak gates remain pending. See the
[runtime validation index](docs/validation/RUNTIME_VALIDATION_INDEX.md) and
[next development phases](docs/planning/NEXT_DEVELOPMENT_PHASES.md).


> Status of every phase of the **8×8 HDMI Matrix Hub** project. Each
> entry links to the merged code paths, the validation evidence, and
> the related docs under `docs/`.
>
> **Spec for "done":** [`docs/validation/VALIDATION_PLAN.md`](docs/validation/VALIDATION_PLAN.md).
> A release tag is only honest when every claim is backed by a
> passing evidence record at the level the plan requires (`V2` on
> the simulator, `V3` from a real client, `V4` on hardware with the
> operator present, `V5` after the 72 h soak). Where evidence is not
> at target the ledger says so under
> [`docs/validation/LEDGER.md`](docs/validation/LEDGER.md).
>
> **Runtime status:** `run.py` and the installed `orei-matrix-driver` command enter the same
> composition. The current runtime uses `MatrixService`, `ActionRunner`, the
> integration loader and persistence startup barrier; `src/driver.py` remains
> a legacy reference. Fresh integrated software evidence is pending and will
> be recorded in the [runtime validation index](docs/validation/RUNTIME_VALIDATION_INDEX.md).

---

## 1. Release channels

| Channel    | State                                      | Next tag                                                                                      | Source of truth               |
| ---------- | ------------------------------------------ | --------------------------------------------------------------------------------------------- | ----------------------------- |
| **Candidate** | Phases 6–7 integrated for review | `v1.0.0-rc1` after the integration PR passes CI and merges | Canonical version and bump-script checks |
| **Milestone** | Phase 5 PR #36 | `v0.5.0` after its final CI check and merge | GitHub PR and annotated Git tag |
| **Stable milestone** | Phases 0–4 merged | `v0.4.0` already tagged | Git history |
| **Final** | Phase 8 / WP-V3 gates pending | `v1.0.0` after hardware, field and feature-target evidence | Validation report and ledger |

Only `1.0.0` carries a public "all features at target, hardware
signed off" claim. Every earlier tag is a milestone that records what
was merged, with the ledger honest about which features still need
real-device proof.

---

## 2. Release history

Release history is summarized here. Consult Git tags for release commits and
the ledger for proof levels; this document is maintained alongside them.

### `0.5.0` — "Focused UI" — Phase 5 (WP-E2) — *pending tag*

- **Goal.** Drop the side-nav drawer + nine-page Settings drawer +
  three editor shells for one `UnifiedSettingsController`
  (9-section `#settings/*` hash routing), one stack-aware
  `OverlayStack` overlay manager, one `EditorShell` (searchable
  command / step picker in place of `window.prompt()`), one shared
  `CecRemote`, one shared `KioskController` plus a server-backed
  `DashboardStore`, and a design-token sheet (`web/css/tokens.css`,
  `:focus-visible`, 44 px touch targets, 4 Tron presets, 30 fps
  background).
- **Source.** `web/js/core/` (ES modules), `web/js/components/`
  (`unified-settings-drawer.js`, `editor-shell.js`, `cec-remote.js`,
  `kiosk-controller.js`, `dashboard-store.js`),
  `web/css/tokens.css`.
- **Runtime note.** This describes the v0.5.0 candidate at its recorded
  commit; runtime completion is integrated in the current candidate.
- **Tag status.** PR #36 awaits its final CI check before merge and `v0.5.0`.

- **Evidence.** Web UI rows are V1 unit + V3 browser. **V4 (real
  hardware tablet) is not recorded for v0.5.x** — HIL Session 2 is
  the next step; see §5.

### `v0.4.0` — "Consolidate" — Phase 4 (WP-C3) — **tagged** at `25233bb`

- **Goal.** One set of framework libraries under `src/hub/`
  (`MatrixService` in `hub.core`, `ActionRunner` in `hub.domain`,
  `IntegrationRegistry` / `IntegrationLoader` / `HubClient` in
  `hub.integrations`, `hub.persistence.migrations`,
  `hub.openapi.build_openapi_spec`, `hub.env` canonical table).
- **Historical runtime note.** At the v0.4.0 commit, the framework was not
  wired into startup. That record remains historical; the current runtime
  composition is documented in §3 and `docs/ARCHITECTURE.md`.
- **CI gate.** 401 new unit tests; `python -m ruff check`,
  `python -m mypy`, targeted `pytest` per track; PR #35 13/13
  green.

### `v0.3.0` — "Secure" — Phase 3 (WP-F1) — **tagged**

- **Goal.** Bring the access model, the SSRF guard, the
  PIN/lockout flow, TLS fingerprint pinning, and the public
  `SECURITY.md` policy up to a publishable baseline.
- **Source.** `src/hub/integrations/unfolded_circle/`,
  `custom_components/hdmi_matrix/`, `SECURITY.md`,
  `tests/test_security_*`.
- **Evidence.** [Ledger — Security controls](docs/validation/LEDGER.md#security-controls-f-sec),
  [Reliability](docs/validation/LEDGER.md#reliability-f-rel).

---

## 3. What this repo ships today

The flagship of the runtime is the **`run.py` entry point** plus the
**modular hub package** under `src/hub/`. The README
([`README.md`](README.md), DOC-02) and the architecture document
([`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)) describe them in full;
the short version is:

**Current runtime composition:**

- `run.py` is a compatibility entry point to `hub.cli`; the installed `orei-matrix-driver`
  command uses the same composition. `hub.runtime.composition` wires one
  matrix client, `MatrixService`, `ActionRunner`, persistence barrier and REST
  application. `src/driver.py` remains a legacy reference, not a launch path.
- `UC_ENABLED` adds the Remote adapter to the shared runtime. Flic routes and
  HA service discovery follow their integration flags.
- `src/rest_api/` (22 modules) — the one REST surface,
  `RestApiServer` binds it on `API_PORT` (default `8080`).
- `src/orei_matrix.py` + `src/telnet_client.py` — the only matrix
  transports.
- `hub.persistence.migrations` — startup migration barrier for managed runtime
  files; legacy data locations are handled by explicit migration inputs.
- `web/js/core/` — the Focused-UI ES modules
  (`api`, `ws`, `state`, `html` with XSS-safe escape, `overlay`,
  `toast`).
- `web/js/components/` — the unified drawer, the editor shell, the
  CEC remote, the kiosk controller, the dashboard card picker (WP-E2
  tracks).

**Runtime services and integration boundaries:**

- `hub.core` — `MatrixService`, `MatrixModel`, `NameStore`,
  `EventBus`.
- `hub.domain` — `ActionRunner`, `VisibilityStore`.
- `hub.integrations` — `Integration` / `IntegrationRegistry` /
  `IntegrationLoader` + `HubClient` (`HubClientLocal`,
  `HubClientHttp`) + the three integration modules
  (`unfolded_circle`, `flic`, `homeassistant`).
- `src/persistence.py` — legacy data-dir resolution and atomic JSON utilities
  still used by existing storage paths.
- `hub.openapi.build_openapi_spec` — OpenAPI 3.1 generator; in
  v0.5.0 the generator is mounted at **`GET /api/openapi.json`**
  with Swagger UI at **`GET /api/docs`**, wired by the
  `wp-g2-openapi-swagger-config-docs` track.
- `hub.env` — canonical runtime environment table and aliases.

The web UI at `/ui` and the kiosk at `/kiosk` are part of the core
(they do **not** require `UC_ENABLED=true`).

---

## 4. What is shipped but pending fresh and real-device proof

The table below preserves the earlier ledger snapshot; it is not evidence
for the runtime-completion candidate. The coordinator's fresh software
campaign will be indexed separately. Simulator claims remain distinct from
physical-device evidence. The simulation matrix runs the same command set
as a real OREI BK-808; the hub code path is real; the response
envelopes are real; the device readback is from a real `OreiMatrix`
instance against a real matrix simulator running on the hub host.
None of that is a real TV, a real OREI BK-808 with the firmware the
field ships, or a remote operator watching the display change.

| Area                                                                        | Today (Ledger row)                                   | Why that is not yet v1.0.0 evidence                                                       |
| --------------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **Matrix control** (routing, presets, output settings, EDID, audio, system) | mostly **V3** (simulator + browser/HA/UC), some **V1** (settings still capped at V1 by HIL-09) | No recorded `V4` (real OREI BK-808) for any tag. |
| **CEC control** (sources, TVs, Telnet path)                                 | mostly **V3**, **V1** on the Telnet-CEC path         | Physical observation (TV turns on, source switches) requires the operator-present sessions. |
| **REST/WS contract**                                                        | all routes **V2** or **V3**                         | nothing caps it; re-runs are cheap.                                                        |
| **Web UI / kiosk flows**                                                    | mostly **V3** on simulator; **V1** for hardware (`UI-44`) | Playwright drives the shipped image, not a tablet in a living room.                          |
| **Remote 3 integration**                                                    | historical candidate records                         | Fresh runtime campaign and physical Remote evidence are tracked separately.                 |
| **Home Assistant HACS component**                                           | mostly **V3** (real HA container)                    | no HA deployment is run by the validation framework yet.                                    |
| **Flic REST handlers**                                                      | **V3** (request replay)                              | Flic hardware sits in the "available when the owner plugs it in" bucket.                   |
| **Security controls**                                                       | **V3** with the three auth configurations; **V4** spot check pending HIL Session 2 | covers `SEC-01..SEC-08` plus the device-token rotation.                       |
| **Reliability**                                                             | mostly **V1** (fault-injection on the simulator); **V5 soak not yet run** | V5 needs 72 h of `python -m tools.validate run` against the sim with flat resource metrics and a real-device spot check. |
| **Runtime composition**                                                     | fresh integrated campaign pending                   | Physical matrix, field and 72-hour soak gates remain pending.                              |

The full row-by-row state lives in
[`docs/validation/LEDGER.md`](docs/validation/LEDGER.md). A feature
is "below target" when the ledger says so.

---

## 5. What comes next

### Phases 6–7 — Repository hygiene, runtime completion and documentation

- **`wp-g1-packaging-version-locks`** — delete `setup.py`, single
  `hub.__init__.__version__` (DEP-04, DEP-06), hashed
  `requirements.txt` + `requirements-dev.txt` (DEP-08, SEC-15).
- **`wp-g1-ci-multiarch-hygiene`** — CI binary/size guard
  rejecting `*.bin`/`*.exe`/`*.c4z`/`*.har` and >2 MB non-LFS
  files; digest-pinned base images + SHA-pinned GitHub Actions;
  multi-arch (`amd64` + `arm64`, `DI-10`); repo cleanup (DEP-09,
  DEP-12, DEP-13, BE-27, API-17).
- **`wp-g1-license-asset-audit`** — license audit of every
  bundled icon, font and asset; `THIRD_PARTY_NOTICES.md`
  (UI-22); update `docs/OREI_API_COMMANDS.md` from HIL-A captures
  + Telnet section (DOC-11).
- **Documentation deliverables owned by this track:**
  - `README.md` rewrite (DOC-02) — done in this branch.
  - `docs/ARCHITECTURE.md` rewrite (shipped vs framework split) —
    done in this branch.
  - `docs/INTEGRATIONS.md` new — done in this branch.
  - `CHANGELOG.md` new (DOC-12) — done in this branch.
  - `ROADMAP.md` new (DOC-01) — this document.
  - `docs/README.md` unified index (DOC-10) — done in this branch.
  - `docs/CONFIGURATION.md` generated against `src/hub/env.py` —
    owned by `wp-g2-openapi-swagger-config-docs`.
  - `docs/API_REFERENCE.md` generated from OpenAPI + WebSocket
    schema (DOC-03) — owned by `wp-g2-openapi-swagger-config-docs`.
    In this release the shipped REST app exposes
    `GET /api/openapi.json` and Swagger UI at `GET /api/docs`.
  - `HOME_ASSISTANT.md` (DOC-04), `DOCKER.md` (DOC-05),
    `FLIC_SETUP.md`, `CONTRIBUTING.md` (DOC-13),
    `UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md` (UC-20) — owned by
    `wp-g2-client-guides-doc-archive`.
- **Tests:** `tests/test_core_documentation.py` (structural checks
  on every owned doc) — done in this branch.

### Phase 8 — Validation campaign (WP-V3)

The integrated software campaign is coordinator-owned. Hardware and field
validation follow that campaign.

- **HIL Session 2** — owner-present V4 runs of routing, presets,
  matrix power, CEC power/volume on the TV, one profile recall
  (see [`docs/validation/HIL_SESSION_2_RUNBOOK.md`](docs/validation/HIL_SESSION_2_RUNBOOK.md)).
- **HIL-B** — regression; **HIL-C** — fault injection on the real
  device; **HIL-D** — 72 h soak (V5 evidence); **HIL-E** — real
  clients.
- **`docs/validation/VALIDATION_REPORT.md`** — feature × client
  matrix, firmware versions, the CEC table.
- **Supported Models table** trimmed to what was validated on
  hardware.
- **Runtime completion:** integrated in the current candidate; see
  [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and the runtime validation
  index for fresh exact-commit evidence and limitations.
- **Tag `v1.0.0`** when every `F-*` row in the ledger is at or
  above target with fresh evidence and owner-observed hardware/field gates pass.

---

## 6. What is **not** on the roadmap

A short list of things the project deliberately does not promise,
so users do not wait for them:

- **Other matrix brands.** The protocol covers OREI BK-808 /
  HDCVT HDP-MXC88A class; other 8×8 HDMI 2.1 matrices from the
  same OEM family are *probable*, but they are not on the
  supported list until HIL evidence shows the read/write surfaces
  match.
- **Scheduling.** Cron-like triggers for profile recall are not in
  any in-flight worktree; they are a research item, not a project
  promise.
- **MQTT broker integration.** The framework supports one (the
  `hub.integrations` `Integration` contract fits), but no
  dedicated module is wired today and there is no shipped
  `/api/integrations` general endpoint.
- **A native Alexa skill.** The path is "control it through Home
  Assistant"; a skill that bypasses HA is not on the plan.
- **A full rewrite of the web UI in a heavy framework.** The
  Focused UI is ES modules + tokens + the unified drawer; no
  React/Vue rewrite is scoped.

If something you want is in this list, open an issue with what the
use case is and what protocol/API the device exposes.

---

## 7. How to read this roadmap

- **What shipped is true today.** A tag is a snapshot of the merge
  branch, not a forward promise. The changelog records what
  changed in each tag; the ledger records what the tag did and did
  not prove. Pending tags remain identified until their CI gates pass and
  the annotated tags are pushed.
- **What is pending is dated.** HIL Session 2 is the next concrete
  step on the V4 path; the ledger's "Stale evidence" column is
  what we will refresh there.
- **What is not promised stays out.** This is the list above; if
  a feature is not listed in §3, §5 or this repo's issues, it is
  not on the plan.

For everything that did not fit here — the validation evidence tree,
the scenario mechanics, the contribution rules — see
[`docs/README.md`](docs/README.md).
