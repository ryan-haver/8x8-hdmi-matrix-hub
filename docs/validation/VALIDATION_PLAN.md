# Validation Plan — Proof of Function

> **Created:** 2026-09-25 · **Companion to:** [`docs/REMEDIATION_PLAN.md`](../REMEDIATION_PLAN.md) (findings and work) and [`docs/audits/UC_INTEGRATION_AUDIT.md`](../audits/UC_INTEGRATION_AUDIT.md).
>
> **Goal:** every claim this project makes about what it does is backed by reproducible evidence of the real effect. Passing tests show that code behaves as its tests expect. They do not show the product works. This plan defines what counts as proof, records the proof status of every feature honestly, and makes releases depend on it.

---

## 1. Principles

1. **No claim without evidence.** A README feature, a release-note line, a ticked checkbox, or a "fixed" finding must link to an evidence record. Anything without one is reported as *claimed*, not *working*.
2. **Prove the effect, not the call.** An HTTP 200 proves nothing. A routing change is proven by the device's state read back (simulator or real matrix) and, on hardware, by what the display shows. A CEC power command is proven by the TV turning on.
3. **Tests guard; evidence proves.** Unit tests and tests with mocks protect against regressions. They count only as level V1 and never as validation.
4. **Mocks come from reality.** Test doubles are built only from captured behaviour: contract fixtures generated from the real server, and golden captures from the real BK-808.
5. **Failure paths are features too.** Each feature is validated for its failure behaviour as well: matrix unreachable, bad input, client disconnect.
6. **Evidence is reproducible and kept fresh.** Simulator-level evidence is regenerated on every PR. Hardware evidence is regenerated at each milestone. Evidence older than a code change that affects the feature is flagged as stale.
7. **Honest status beats a good-looking status.** The ledger shows the current level, even when it's low. Finding that a feature doesn't work is a success of this process, and it goes into the findings register.

## 2. Verification levels

| Level | Name | What it proves | Accepted evidence |
| --- | --- | --- | --- |
| **V0** | Claimed | Nothing; documented or coded only | — |
| **V1** | Unit | The logic is correct in isolation | Unit test using doubles built from captured fixtures |
| **V2** | Simulated integration | The real hub code path drives a device and the effect happens | Scenario run: real hub modules + matrix simulator; request/response, simulator command log, state before/after |
| **V3** | End-to-end | A real client, using the shipped Docker image, gets the effect | Scenario run through a real client: a browser (Playwright), a real Home Assistant container, a scripted Remote (and the Unfolded Circle core simulator if available), replayed Flic Hub requests. Against the simulator. Includes screenshots, logs, and simulator state diff. |
| **V4** | Hardware | It works on the real device | Same scenario against the real BK-808 (and real TV/sources for physical effects): device readback, plus operator observation (timestamped attestation, photo or video for physical effects), firmware versions recorded |
| **V5** | Field | It keeps working | V4 plus a 72 h soak with flat resource metrics, plus the owner's sign-off after a week of daily use |

**Target levels by area:**

| Area | Target at v1.0.0 |
| --- | --- |
| Matrix control (routing, presets, power, output settings, EDID, audio, system) | V4 |
| CEC control (inputs and outputs) | V4, with physical observation |
| REST/WebSocket contract | V2 for every route and event; V3 for the routes each client uses |
| Domain features (profiles, scenes, macros, shortcuts, dashboard, passcodes) | V3, plus V4 for the core flows |
| Web UI and kiosk flows | V3 with approved visual baseline; V4 spot checks on real devices |
| Remote 3 integration | V3 (scripted Remote); V4 on a real Remote 3 (UC audit §9 checklist) |
| Home Assistant component | V3 (real HA container); V4 on the owner's HA |
| Flic | V3 (request replay); V4 if hardware is available, otherwise reported as "not validated on hardware" |
| Deployment, configuration, persistence, migration | V3 on the shipped image; V4 on the real deployment host |
| Security controls (after Phase 3) | V3, including negative tests in all three auth configurations |
| Reliability (reconnect, outages, soak) | V4 fault injection on hardware; V5 soak |

## 3. Feature ledger

**Registry:** `docs/validation/features.yaml`, one entry per user-facing feature (about 200). Fields:

```yaml
- id: F-MTX-001
  area: matrix            # matrix | cec | api | domain | ui | kiosk | uc | ha | flic | ops | security | reliability
  title: Route one input to one output
  claim: README.md "Full matrix control via HTTP endpoints"; docs/API_REFERENCE.md POST /api/switch
  interfaces:
    rest: [POST /api/switch, POST /api/output/{n}/source]
    ws: [routing_change]
    ui: [matrix/grid/default, kiosk/routing/default]
    uc: [media_player.output_N select_source]
    ha: [select.output_N_source]
  target: V4
  current: V1            # maintained by the ledger generator from evidence records
  evidence: []           # evidence record paths
  findings: []           # register IDs affecting this feature
  scenarios: [routing.switch_one]
```

**Areas and ID prefixes:** `F-MTX` matrix control · `F-CEC` CEC · `F-API` REST/WS contract · `F-DOM` domain features · `F-UI` web UI · `F-KIO` kiosk · `F-UC` Remote integration · `F-HA` Home Assistant · `F-FLIC` Flic · `F-OPS` deployment/config/persistence · `F-SEC` security · `F-REL` reliability.

**Sources used to build it (so nothing is missed):** the 32 matrix commands the hub sends, the 163 REST routes, the WebSocket events, the 170 UI catalog entries, the 74 Remote entities and their commands, the HA entities and 3 services, the Flic request templates in `docs/FLIC_SETUP.md`, the README feature list, and the environment variables and deployment modes.

**Report:** `docs/validation/LEDGER.md` is generated from the registry and evidence. It shows a table per area (feature, target, current, freshness, evidence link, open findings) and a summary: counts per level, features below target, and stale evidence. It is regenerated in CI and at every release.

## 4. Evidence records

**Location:** `docs/validation/evidence/<feature-id>/<YYYY-MM-DD>-<level>-<shortsha>-<scenario>-<client>.json` (the scenario and client suffix keeps records from colliding when several scenarios or clients prove a feature on the same day and commit; a record that proves several features is stored once, under its first feature). Artifacts go alongside, in a folder with the record's name: screenshots, logs, and captures in Git LFS. Simulator-level runs in CI are uploaded as artifacts, and only the summary record is committed at milestones.

**Record fields:** feature ID(s), level, scenario ID, commit SHA, environment (simulator version or matrix firmware versions, hub image digest, client versions: browser, HA, Remote firmware), procedure steps, observations (requests/responses, device state before/after, simulator command log excerpt or device readback, WebSocket events received, screenshots, operator observation text and media), result (pass/fail/blocked), linked findings, operator (`automation` or a named person), timestamp.

**Scenario runner:** `tools/validate/`. Scenarios live in `tests/validation/scenarios/`. Each is tied to one or more feature IDs and declares:

- **target:** `sim` or `hardware`;
- **client:** `api`, `browser`, `ha`, `uc`, or `flic`;
- **steps:** setup, action, expected effect, and failure-path checks.

The same scenario runs against the simulator in CI and against the real matrix in hardware sessions. Hardware runs reuse the capture tool's snapshot/restore safety. They prompt the operator for physical observations, for example "Does the TV on output 1 now show Apple TV? [y/n] (optional photo path)".

**Real clients for V3:**

- **Browser:** Playwright against the Docker image and the simulator. Flows assert the simulator state, not just screenshots.
- **Home Assistant:** a real `homeassistant/home-assistant` container with the custom component installed and configured through HA's own API. Service calls and entity changes are checked against simulator state.
- **Remote 3:** the scripted Remote (`tools/uc_remote_sim.py`). If Unfolded Circle's core simulator Docker image is available and licensed for this use (*to verify*), it is added as a stronger V3 client that runs the real Remote core software.
- **Flic:** exact replay of the HTTP requests the Flic Hub sends, as documented in `docs/FLIC_SETUP.md`.

## 5. Campaigns

| Campaign | When | What | Output |
| --- | --- | --- | --- |
| **C0 — Baseline truth** | Now, against the current code (v0.1.0 plus merged fixes) | Build the ledger. Run every feature's scenario at V2 and V3 on the simulator. Record the real current level. Failures become findings; they are not fixed during C0. | First `LEDGER.md`, new register rows, a realistic picture of what works today |
| **C0-HW — Hardware anchor** | HIL Session 1 | Capture (read, probe, write-with-restore), then V4 runs of the most-used features: routing, presets, matrix power, CEC power/volume on the TV, one profile recall | Golden captures, first V4 evidence, protocol questions answered |
| **C1…C7 — Phase campaigns** | End of each remediation phase | Re-run all simulator scenarios (automatic in CI). Features touched by the phase must reach their phase target. No feature may drop below its previous level. | Updated ledger; phase exit evidence |
| **C8 — Release validation** | Phase 8 | Every feature at target; hardware session (HIL-B/C/E), 72 h soak (HIL-D), real Remote, real HA, real kiosk, real deployment host | `docs/validation/VALIDATION_REPORT.md`; v1.0.0 |

## 6. Release gates

| Release | Gate |
| --- | --- |
| **v0.2.0 "Stabilize"** | C0 and C0-HW complete. Every matrix, CEC, domain, Remote, and HA feature at V3 or better on the simulator. Routing, presets, matrix power, and TV CEC power at V4. No open critical findings. No feature lower than in C0. |
| **v0.3.0 "Secure"** | Every security feature at V3 with negative tests in all three auth configurations (no PIN, admin PIN, admin + control PIN). Kiosk, Flic, and HA flows at V3 with and without a control PIN. V4 spot check with an admin PIN set. |
| **v1.0.0** | Every feature at its target level with fresh evidence. V5 soak passed. `VALIDATION_REPORT.md` published. The supported-hardware table lists only what was validated. |

Any release note line or README feature without evidence at V3 or better is either removed or labelled experimental.

## 7. Continuous enforcement

- **CI (every PR):** run all simulator scenarios (V2/V3), regenerate `LEDGER.md` as an artifact, and fail if any feature drops below its recorded level or a scenario fails without a linked open finding.
- **PR template:** each PR lists the features it affects and links its evidence (CI artifact or hardware record).
- **Definition of done** (remediation plan §8): a finding is closed only when its regression test exists *and* the affected features have fresh evidence at their phase target.
- **Staleness:** evidence is stale when the code paths declared by the feature's scenarios changed after the evidence commit. Stale features show as such in the ledger until re-validated.
