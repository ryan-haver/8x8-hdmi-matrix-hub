# Documentation Index

> The unified entry point for the **8×8 HDMI Matrix Hub** docs. Every
> doc on this page is either owned by a phase worktree or generated
> from the source; both kinds are tagged as such so the reader knows
> what to trust and where to validate.
>
> **The single rule for what gets claimed in this folder:** any feature
> that is described as "works" must have a passing evidence record at
> the level the validation plan requires. The ledger
> ([`validation/LEDGER.md`](validation/LEDGER.md)) — also reachable at
> [`docs/validation/LEDGER.md`](validation/LEDGER.md) — lists every
> feature row with the level, the freshness, and the open findings.
> The plan it implements is [`docs/validation/VALIDATION_PLAN.md`](validation/VALIDATION_PLAN.md).
> That is the one place the docs are forced to stay honest.

---

## 1. Start here

| Document                            | What you get | Owner / source |
| ----------------------------------- | ------------ | -------------- |
| [`../README.md`](../README.md)      | Project pitch, quick start, hardware list, env-var cheat-sheet | `wp-g2-readme-architecture-changelog` (DOC-02) |
| [`../ROADMAP.md`](../ROADMAP.md)    | Phases, tags, what shipped, what is pending, what is not on the plan | `wp-g2-readme-architecture-changelog` (DOC-01) |
| [`../CHANGELOG.md`](../CHANGELOG.md) | v0.3.0 "Secure", v0.4.0 "Consolidate", v0.5.0 "Focused UI" and the pending-hardware section | `wp-g2-readme-architecture-changelog` (DOC-12) |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | The modular hub package (`src/hub/`): `MatrixService`, `ActionRunner`, `HubClient`, the event topics, the REST/WS contract | `wp-g2-readme-architecture-changelog` |
| [`INTEGRATIONS.md`](INTEGRATIONS.md) | The opt-in `Integration` framework + the three shipped integrations (Unfolded Circle, Flic, Home Assistant discovery) | `wp-g2-readme-architecture-changelog` |

---

## 2. Generated reference

These docs are produced from the source by tools that ship in the
repo. They live here too so readers can search them, but the source of
truth is the code:

| Document                                  | Generated from                                            | Owner / source |
| ----------------------------------------- | --------------------------------------------------------- | -------------- |
| [`API_REFERENCE.md`](API_REFERENCE.md)    | `src/hub/openapi.py::build_openapi_spec(app)` + the WebSocket schema at [`api/websocket.schema.json`](api/websocket.schema.json) | `wp-g2-openapi-swagger-config-docs` (DOC-03) |
| [`CONFIGURATION.md`](CONFIGURATION.md)    | `src/hub/env.py::CORE_ENV_VARS` and `INTEGRATION_ENV_VARS` (DI-12) | `wp-g2-openapi-swagger-config-docs` (DOC-12) |
| `validation/LEDGER.md`                    | `python -m tools.validate ledger` over `validation/features.yaml` + `validation/evidence/` | generated; do not edit by hand |

When one of these moves, regenerate it from the source and commit the
diff together with the source change.

---

## 3. Operator & user guides

The user-facing guides a homeowner, integrator or Remote 3 operator
needs:

| Document                                                | Audience                       | Owner / source |
| ------------------------------------------------------- | ------------------------------ | -------------- |
| [`DOCKER.md`](DOCKER.md)                                | Anyone deploying with Docker   | `wp-g2-client-guides-doc-archive` (DOC-05) |
| [`HOME_ASSISTANT.md`](HOME_ASSISTANT.md)                | Home Assistant users           | `wp-g2-client-guides-doc-archive` (DOC-04) |
| [`FLIC_SETUP.md`](FLIC_SETUP.md)                        | Flic Hub owners                | `wp-g2-client-guides-doc-archive` |
| [`UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md) | Remote 3 operators             | `wp-g2-client-guides-doc-archive` (UC-20) |
| `SECURITY.md` (project root)                            | Threat model, two-level access, always-on protections, vulnerability disclosure | `wp-f1-security-policy-doc` |

---

## 4. Developer & contributor guides

| Document                                                         | Audience                | Owner / source |
| ---------------------------------------------------------------- | ----------------------- | -------------- |
| `CONTRIBUTING.md` (project root)                                 | Contributors            | `wp-g2-client-guides-doc-archive` (DOC-13) |
| [`INTEGRATION_TEMPLATE.md`](INTEGRATION_TEMPLATE.md)             | New integration authors | merged in Phase 4 (track 4) |
| [`INTEGRATIONS.md`](INTEGRATIONS.md)                             | Operating the opt-in framework | this worktree |
| [`ARCHITECTURE.md`](ARCHITECTURE.md)                             | Anyone reading the runtime source | this worktree |

---

## 5. Protocol & matrix reference

| Document                                  | What you get                                              |
| ----------------------------------------- | --------------------------------------------------------- |
| [`OREI_API_COMMANDS.md`](OREI_API_COMMANDS.md) | The OREI / HDCVT matrix protocol, command formats, the command inventory from Control4/RTI drivers and HIL-A captures |
| [`api/WEBSOCKET.md`](api/WEBSOCKET.md)     | WebSocket envelope + event payload reference |
| [`api/websocket.schema.json`](api/websocket.schema.json) | The schema; tests reject frames that violate it |
| [`remote3-rest-core-api.md`](remote3-rest-core-api.md) | The Unfolded Circle Remote 3 REST surface (vendor reference) |
| [`remote3-websocket-core-api.md`](remote3-websocket-core-api.md) | The Remote 3 WebSocket core protocol (vendor reference) |
| [`remote3-websocket-integration-api.md`](remote3-websocket-integration-api.md) | The Remote 3 integration protocol (vendor reference) |
| [`CEC_CONTROL_ARCHITECTURE.md`](CEC_CONTROL_ARCHITECTURE.md) | CEC command and capability map |
| [`IR_CONTROL_ROADMAP.md`](IR_CONTROL_ROADMAP.md)     | Background on the IR investigation (legacy) |

---

## 6. Validation evidence — the ledger

> **Every claim in this folder that says a feature works is anchored to
> the evidence ledger. If a row in the ledger is below target, the docs
> that describe that feature must say so.**

| Document                                                       | What it is |
| -------------------------------------------------------------- | ---------- |
| [`validation/README.md`](validation/README.md)                 | How the proof of function works here — what the levels (V0..V5) mean, how to add a scenario, how to add a client |
| [`validation/VALIDATION_PLAN.md`](validation/VALIDATION_PLAN.md) | The validation plan: principles, levels, release gates |
| [`validation/LEDGER.md`](validation/LEDGER.md)                 | Generated row-by-row report: each feature's level, freshness, linked evidence and open findings |
| [`validation/features.yaml`](validation/features.yaml)         | The registry: every feature (268 today), its interfaces, recorded level, linked findings and scenarios |
| [`validation/findings_pending.yaml`](validation/findings_pending.yaml) | Findings discovered by validation that still need a register row in `REMEDIATION_PLAN.md` §4 |
| [`validation/evidence.schema.json`](validation/evidence.schema.json) | The JSON schema of an evidence record |
| [`validation/evidence/`](validation/evidence)                  | Committed evidence records (115 today); each is a JSON file plus an artifact folder of screenshots / device logs |
| [`validation/HIL_SESSION_2_RUNBOOK.md`](validation/HIL_SESSION_2_RUNBOOK.md) | The operator-present runbook for the next hardware session |

The full ledger is the answer to "is feature X really working?". The
levels are:

* **V0 — Claimed.** Documented or coded only.
* **V1 — Unit.** Unit tests using doubles built from captured fixtures.
* **V2 — Simulated integration.** The real hub code path drives a
  device simulator and the effect happens (request / response, simulator
  command log, state before / after).
* **V3 — End-to-end.** A real client (browser, Home Assistant
  container, scripted Remote, Flic request replay) drives the shipped
  Docker image and the effect happens.
* **V4 — Hardware.** The same scenario against the real OREI BK-808,
  with operator observation (TV turning on, etc.), firmware versions
  recorded.
* **V5 — Field.** A 72 h soak with flat resource metrics, plus the
  owner's sign-off after a week of daily use.

The ledger currently records a mix of V1, V2 and V3 across the 268
features. **No row is at V4 or V5 yet** — Phase 7 / WP-V3 is where those
levels start to be filled.

---

## 7. Plan & remediation references

| Document                                                | What it is |
| ------------------------------------------------------- | ---------- |
| [`../orca-phased-roadmap.md`](../orca-phased-roadmap.md) | The phase-by-phase worktree fan-out, the 6-model roster, and the lifecycle protocol |
| [`REMEDIATION_PLAN.md`](REMEDIATION_PLAN.md)            | The findings / register / row-by-row plan that the validation scenarios come from |
| `audit/UC_INTEGRATION_AUDIT.md`                         | Historical audit of the Unfolded Circle integration (pre-Phase-4) |
| `audit/UC_CORE_SIMULATOR.md`                            | Notes on the UC core simulator (vendor) |

---

## 8. Legacy & historical references

| Document                                          | What it is |
| ------------------------------------------------- | ---------- |
| [`PROJECT_ROADMAP.md`](PROJECT_ROADMAP.md)        | The pre-Phase-1 roadmap (Sprints 1–9, etc.). Kept for context; **see [`../ROADMAP.md`](../ROADMAP.md) for the current plan** |
| [`MASTER_INDEX.md`](MASTER_INDEX.md)              | An older doc index; kept until [`ARCHITECTURE.md`](ARCHITECTURE.md), [`INTEGRATIONS.md`](INTEGRATIONS.md), [`API_REFERENCE.md`](API_REFERENCE.md) and [`CONFIGURATION.md`](CONFIGURATION.md) are all populated |
| `WEB_UI_IMPLEMENTATION_PLAN.md`                   | The pre-Phase-5 web UI plan; superseded by the architecture and the WP-E2 commits |
| `PHASE_8_SPEC.md`                                 | The Phase 8 (v1.0.0) validation campaign spec |
| `docs/ui/LOOK_AND_FEEL.md`                        | The Focused-UI visual baseline reference |

The legacy `*.har` files in this folder are kept as historical HTTP
capture artifacts (they are not loaded by the code); they will be
moved to `archive/` by the coordinator after the doc merges land.
