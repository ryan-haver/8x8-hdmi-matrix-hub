# Documentation Index

Start with the deployment and client guides below. The architecture documents
describe the shared runtime, optional integrations and storage behavior. The
[feature ledger](validation/LEDGER.md) records feature proof; the
[runtime validation index](validation/RUNTIME_VALIDATION_INDEX.md) references
exact-commit integrated campaigns. Hardware, field and soak gates remain
pending owner evidence.

For the next release-validation work, use the
[evidence-gap inventory](validation/RELEASE_EVIDENCE_GAPS.md) and
[release checklist](validation/RELEASE_VALIDATION_CHECKLIST.md). These distinguish
software proof, hardware gates and field qualification; they do not promote
feature levels or authorize execution.

The next development work is specified in the
[runtime-completion plan](planning/NEXT_DEVELOPMENT_PHASES.md), with a
[model/agent inventory](planning/MODEL_AND_AGENT_INVENTORY.md). The future roster
excludes Claude/Anthropic, including fallback and helper roles.

Agent entry points: [root instructions](../AGENTS.md),
[standing Orca coordination protocol](ORCHESTRATION_PROTOCOL.md) and
[agent allocation ledger](production/AGENT_ALLOCATION.md). The protocol governs
authorized execution; reading or maintaining it does not start a phase.

---

## 1. Start here

| Document                                                          | What you get                                                                                                       | Owner / source |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------- |
| [`../README.md`](../README.md)                                    | Project pitch, quick start, hardware list, env-var cheat-sheet                                                      | Maintained documentation (DOC-02) |
| [`../ROADMAP.md`](../ROADMAP.md)                                  | Phases, tags, what shipped, what is pending, what is not on the plan, framework-wiring gap                          | Maintained documentation (DOC-01) |
| [`../CHANGELOG.md`](../CHANGELOG.md)                              | v0.3.0 Secure, v0.4.0 Consolidate, v0.5.0 Focused UI and the RC, with pending-hardware and pending-wiring sections | Maintained documentation (DOC-12) |
| [`ARCHITECTURE.md`](ARCHITECTURE.md)                              | Shared startup, runtime state, action and persistence flow                                                          | Maintained documentation |
| [`INTEGRATIONS.md`](INTEGRATIONS.md)                              | Runtime flags, lazy loading, shared state, and integration evidence limits                                         | Maintained documentation |

---

## 2. Generated reference

The OpenAPI route catalog and ledger are generated from code and evidence.
The configuration reference is maintained against the source and checked by tests:

| Document                                       | Generated from                                                                                       | Mount point / status                                                                                     | Owner / source |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------- |
| [`API_REFERENCE.md`](API_REFERENCE.md)         | `src/hub/openapi.py::build_openapi_spec(app)` (framework library) + the WebSocket schema at [`api/websocket.schema.json`](api/websocket.schema.json) | Shipped today at `GET /api/openapi.json` (raw document) and Swagger UI at `GET /api/docs`, wired by the `wp-g2-openapi-swagger-config-docs` track. | `wp-g2-openapi-swagger-config-docs` (DOC-03) |
| [`CONFIGURATION.md`](CONFIGURATION.md)         | `src/hub/env.py::CORE_ENV_VARS` and `INTEGRATION_ENV_VARS` (DI-12)                                  | Documents runtime variables and aliases separately from framework-only flags           | `wp-g2-openapi-swagger-config-docs` (DOC-12) |
| `validation/LEDGER.md`                         | `python -m tools.validate ledger` over `validation/features.yaml` + `validation/evidence/`            | generated; do not edit by hand                                                                          | generated    |
| [`validation/RUNTIME_VALIDATION_INDEX.md`](validation/RUNTIME_VALIDATION_INDEX.md) | Exact-commit integrated runtime campaigns and remaining gates | Maintained from coordinator reports |

When one of these moves, regenerate it from the source and commit
the diff together with the source change.

---

## 3. Operator & user guides

The user-facing guides a homeowner, integrator or Remote 3 operator
needs:

| Document                                                            | Audience                       | Owner / source |
| ------------------------------------------------------------------- | ------------------------------ | -------------- |
| [`DOCKER.md`](DOCKER.md)                                            | Anyone deploying with Docker   | `wp-g2-client-guides-doc-archive` (DOC-05) |
| [`HOME_ASSISTANT.md`](HOME_ASSISTANT.md)                            | Home Assistant users           | `wp-g2-client-guides-doc-archive` (DOC-04) |
| [`FLIC_SETUP.md`](FLIC_SETUP.md)                                    | Flic Hub owners                | `wp-g2-client-guides-doc-archive` |
| [`UNFOLDED_CIRCLE.md`](UNFOLDED_CIRCLE.md) | Remote 3 operators             | `wp-g2-client-guides-doc-archive` (UC-20) |
| `SECURITY.md` (project root)                                        | Threat model, two-level access, always-on protections, vulnerability disclosure | `wp-f1-security-policy-doc` |

---

## 4. Developer & contributor guides

| Document                                                         | Audience                          | Owner / source |
| ---------------------------------------------------------------- | --------------------------------- | -------------- |
| `CONTRIBUTING.md` (project root)                                 | Contributors                      | `wp-g2-client-guides-doc-archive` (DOC-13) |
| [`INTEGRATION_TEMPLATE.md`](INTEGRATION_TEMPLATE.md)             | New framework integration authors | merged in Phase 4 (track 4) |
| [`INTEGRATIONS.md`](INTEGRATIONS.md)                             | Runtime integration flags, lifecycle and shared state | Maintained documentation |
| [`ARCHITECTURE.md`](ARCHITECTURE.md)                             | Anyone reading the runtime source or the `src/hub/` framework | Maintained documentation |

---

## 5. Protocol & matrix reference

| Document                                                  | What you get                                                                                                  |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [`OREI_API_COMMANDS.md`](OREI_API_COMMANDS.md)            | The OREI / HDCVT matrix protocol, command formats, the command inventory from Control4/RTI drivers and HIL-A captures |
| [`api/WEBSOCKET.md`](api/WEBSOCKET.md)                    | WebSocket envelope + event payload reference                                                                   |
| [`api/websocket.schema.json`](api/websocket.schema.json)  | The schema; tests reject frames that violate it                                                                |
| [`remote3-rest-core-api.md`](remote3-rest-core-api.md)    | The Unfolded Circle Remote 3 REST surface (vendor reference)                                                  |
| [`remote3-websocket-core-api.md`](remote3-websocket-core-api.md) | The Remote 3 WebSocket core protocol (vendor reference)                                                   |
| [`remote3-websocket-integration-api.md`](remote3-websocket-integration-api.md) | The Remote 3 integration protocol (vendor reference)                                              |
| [`CEC_CONTROL_ARCHITECTURE.md`](CEC_CONTROL_ARCHITECTURE.md) | CEC command and capability map                                                                                |
| [`IR_CONTROL_ROADMAP.md`](IR_CONTROL_ROADMAP.md)         | Background on the IR investigation (legacy)                                                                   |

---

## 6. Validation evidence — the ledger

> **Every claim in this folder that says a feature works is
> anchored to the evidence ledger. If a row in the ledger is below
> target, the docs that describe that feature must say so.**

| Document                                                          | What it is                                                                                                  |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| [`validation/README.md`](validation/README.md)                    | How the proof of function works here — what the levels (V0..V5) mean, how to add a scenario, how to add a client |
| [`validation/VALIDATION_PLAN.md`](validation/VALIDATION_PLAN.md)  | The validation plan: principles, levels, release gates                                                      |
| [`validation/LEDGER.md`](validation/LEDGER.md)                    | Generated row-by-row report: each feature's level, freshness, linked evidence and open findings            |
| [`validation/features.yaml`](validation/features.yaml)            | The registry: every feature (268 today), its interfaces, recorded level, linked findings and scenarios — full path `docs/validation/features.yaml` |
| [`validation/findings_pending.yaml`](validation/findings_pending.yaml) | Findings discovered by validation that still need a register row in `REMEDIATION_PLAN.md` §4 — full path `docs/validation/findings_pending.yaml`            |
| [`validation/evidence.schema.json`](validation/evidence.schema.json) | The JSON schema of an evidence record                                                                       |
| [`validation/evidence/`](validation/evidence)                     | Committed evidence records (115 today); each is a JSON file plus an artifact folder of screenshots / device logs |
| [`validation/HIL_SESSION_2_RUNBOOK.md`](validation/HIL_SESSION_2_RUNBOOK.md) | The operator-present runbook for the next hardware session                                      |

The full ledger is the answer to "is feature X really working?".
The plan that defines the levels lives at `docs/validation/VALIDATION_PLAN.md`
and is linked everywhere it matters in [`ROADMAP.md`](../ROADMAP.md) and
[`CHANGELOG.md`](../CHANGELOG.md).
The levels are:

* **V0 — Claimed.** Documented or coded only.
* **V1 — Unit.** Unit tests using doubles built from captured
  fixtures.
* **V2 — Simulated integration.** The real hub code path drives a
  device simulator and the effect happens (request / response,
  simulator command log, state before / after).
* **V3 — End-to-end.** A real client (browser, Home Assistant
  container, scripted Remote, Flic request replay) drives the
  shipped Docker image and the effect happens.
* **V4 — Hardware.** The same scenario against the real OREI
  BK-808, with operator observation (TV turning on, etc.),
  firmware versions recorded.
* **V5 — Field.** A 72 h soak with flat resource metrics, plus
  the owner's sign-off after a week of daily use.

The runtime campaign index links fresh software evidence for the integrated
runtime source/image candidate `1baac3dec660f41345869c126cfca94d6731c5a0`, with run-level provenance in the archive. The accepted R8D review and software evidence do not establish physical hardware, owner deployment, field, or 72-hour soak acceptance; those remain external gates.

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
| [`MASTER_INDEX.md`](MASTER_INDEX.md)              | Compatibility link to this index |
| `WEB_UI_IMPLEMENTATION_PLAN.md`                   | The pre-Phase-5 web UI plan; superseded by the architecture and the WP-E2 commits |
| [`PHASE_8_SPEC.md`](PHASE_8_SPEC.md)               | Compatibility link to a historical domain/UI proposal; final release gates are in `validation/VALIDATION_PLAN.md` |
| `docs/ui/LOOK_AND_FEEL.md`                        | The Focused-UI visual baseline reference |

Protocol captures used by the simulator are retained under `tests/fixtures/device/`.
The repository guard rejects newly committed HAR captures and binary executables.

## Current plan and retained references

- [Unified master plan](planning/UNIFIED_MASTER_PLAN.md)
- [Release validation report](validation/VALIDATION_REPORT.md)
- [Validation plan and release gates](validation/VALIDATION_PLAN.md)
- [Historical design archive](archive/design/WEB_UI_IMPLEMENTATION_PLAN.md)
- [IR proposal](proposals/IR_CONTROL.md)
- [Upstream UC reference guide](vendor/UNFOLDED_CIRCLE.md)
