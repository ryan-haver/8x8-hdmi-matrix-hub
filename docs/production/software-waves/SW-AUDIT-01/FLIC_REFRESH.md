# SW-AUDIT-01 / SW-CLI-FLIC: bounded four-case proof refresh

Four existing scenarios completed through the genuine `flic` client: **4 pass / 4 gate=ok**, V3, **25 passing assertions and one n/a**. Run exit **0**; supported evidence-check exit **0**. **Artifact admission: HOLD** because raw simulator state snapshots retain eight unmasked fixture-password fields. Raw bytes remain private and unchanged; this report contains no credential values.

## Authority and attribution

- Existing Run `run_37205f6095b3`; Task `task_442e2245e0a1`; Dispatch `ctx_33cdb9118f04`; worker `term_2085a94f-b9c4-4a36-9823-4497561dc5b7`; coordinator `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`.
- Exact published source/base: `865ec9c6d0df56e0a0b72dcaee8cc0b5c95f468b`; actual branch `ryan-haver/wp-flic-proof-refresh`; Windows local task checkout `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-flic-proof-refresh`.
- Requested route: OpenAI `gpt-6.1-sol` / high. Live Orca Dispatch/worker receipt is retained privately; provider execution attestation and independent exact-commit metadata review remain coordinator responsibilities. No helper or alternate provider was launched.
- This continues bounded P1 SW-AUDIT-01/SW-CLI-FLIC evidence work. Exclusive writes are this new report and the new ignored `build/software-waves/SW-AUDIT-01-flic-refresh/` subtree. Coordinator retains canonical ledger/allocation/evidence ownership.
- Initial Git porcelain and patch were empty. Every evidence record and summary attributes a clean source tree (`dirty=false`, `dirty_files=[]`) to the exact source SHA above. The report is authored after execution; no evidence SHA was relabeled.
- The launch supplied Codex 84% weekly remaining and correction/review reserve; that is a coordinator preflight observation, not a new worker quota measurement. No new spend, settings, dependencies, installs, junctions, devices, branches, push, merge or canonical record/import was performed.

## Actual execution

Executed once, 2026-10-29 UTC (Oct 28 local); record times below are authoritative. Scenario selection follows discovery order: preset, power_off, power_on, all_outputs. No failing qualification was retried.

```powershell
& 'C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe' -m tools.validate run --target sim --client flic --scenario flic.all_outputs --scenario flic.power_off --scenario flic.power_on --scenario flic.preset --out build/software-waves/SW-AUDIT-01-flic-refresh/attempt-01
& 'C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe' -m tools.validate check --evidence build/software-waves/SW-AUDIT-01-flic-refresh/attempt-01/evidence --run-summary build/software-waves/SW-AUDIT-01-flic-refresh/attempt-01/run-summary.json --expect-clients flic
```

The actual absolute argv/cwd are retained in `run-command.json` and `check-command.json`; stdout, stderr, exact exits and timestamps are separate immutable files. `private-invocation.py` and `private-inspection.py` are private invocation diagnostics, not implementation/tooling deliverables. The supported check reads canonical committed evidence plus this extra directory, applies registry/finding/recorded-level regression logic and this run summary, and requires at least one executed flic scenario; it is not a global release acceptance test. No ledger generation ran.

Check stdout:

```text
[validate] gate OK (0 known failure(s) linked to open findings)
```

Check stderr:

```text
(empty)
```

Python 3.12.10; Windows-11-10.0.26300-SP0; Node `v24.22.1` at `C:\Program Files\nodejs\node.EXE`. `package.json` supports Node >=20. No npm install or dependency update was needed. Hub/API version 2.10.0; aiohttp 3.13.3; native `run.py -> hub.cli` shared runtime with UC disabled and Flic enabled; no container/image digest is claimed. Simulator fingerprint `23f7439ea94f5fcc`, seed `tools/simulator/states/default.json`, BK-808 / firmware V1.10.01 / web V2.00.03 are simulator-reported metadata.

Invocation-only isolation set `PYTHONPATH=<task checkout>/src;<task checkout>`, `PYTHONIOENCODING=utf-8`, `PYTHONDONTWRITEBYTECODE=1`; TEMP/TMP, MATRIX_DATA_DIR, DATA_DIR and UC_CONFIG_HOME are new directories under this attempt. Inherited NODE_PATH was removed for the scenario/check subprocesses; no global environment was changed. `SimStack` starts disposable local simulator/hub processes on free ports, copies fixture data to a fresh child directory under isolated TEMP, and overrides its own DATA_DIR/UC_CONFIG_HOME there. Its normal lifecycle removes disposable child data; all emitted records/logs remain retained. Parent isolation directories remain. No owner runtime data or hardware URLs/credentials were used.

## Outcomes and assertions

Every record is `client=flic`, `target=sim`, `level=V3`, `result=pass`, `gate=ok`, with no blocked reason, failed check, finding, note, screenshot or operator observation. Four schema validations and four exact expected-versus-actual scenario/feature/covers/source/Node/drawer comparisons passed. The records make generated, keyless drawer requests via the Flic client's own aiohttp transport. The runner's existing ApiClient helper performs setup/readback only; it does not substitute for the action transport.

| Scenario | Features (expected = actual) | Checks | Actual generated request | Disposition |
| --- | --- | --- | --- | --- |
| `flic.preset` | `F-FLIC-001`, `F-FLIC-010` | 6 pass | `POST /api/preset/3` -> 200 | Functional pass; artifact HOLD |
| `flic.power_off` | `F-FLIC-002`, `F-FLIC-010` | 6 pass; 1 n/a | `POST /api/power/off` -> 200 | Functional pass; artifact HOLD |
| `flic.power_on` | `F-FLIC-002`, `F-FLIC-010` | 6 pass | `POST /api/power/on` -> 200 | Functional pass; artifact HOLD |
| `flic.all_outputs` | `F-FLIC-008`, `F-FLIC-010` | 7 pass | `POST /api/switch` -> 200 | Functional pass; artifact HOLD |

### flic.preset

UTC: `2026-10-29T00:17:23.403Z` to `2026-10-29T00:17:23.710Z`.

- **pass**: response HTTP 200.
- **pass**: device routing == the routing preset 3 stores on the device.
- **pass**: device otherwise unchanged (allowed: outputs[*].source, routing).
- **pass**: device received http 'preset set' with {'index': 3} exactly 1x.
- **pass**: WebSocket event 'preset_recall' with {'preset': 3}.
- **pass**: every WebSocket message follows docs/api/websocket.schema.json.

### flic.power_off

UTC: `2026-10-29T00:17:23.802Z` to `2026-10-29T00:17:24.100Z`.

- **pass**: response HTTP 200.
- **pass**: device system.power == 0.
- **pass**: device otherwise unchanged (allowed: system.power).
- **pass**: device received http 'set poweronoff' with {'power': 0} exactly 1x.
- **pass**: hub GET /api/status/system -> data.power == 'off' (HTTP 200).
- **n/a**: WebSocket event 'power_change' with {'power': 'off'}.
- **pass**: every WebSocket message follows docs/api/websocket.schema.json.

### flic.power_on

UTC: `2026-10-29T00:17:24.165Z` to `2026-10-29T00:17:24.426Z`.

- **pass**: response HTTP 200.
- **pass**: device system.power == 1.
- **pass**: device otherwise unchanged (allowed: system.power).
- **pass**: device received http 'set poweronoff' with {'power': 1} exactly 1x.
- **pass**: hub GET /api/status/system -> data.power == 'on' (HTTP 200).
- **pass**: every WebSocket message follows docs/api/websocket.schema.json.

### flic.all_outputs

UTC: `2026-10-29T00:17:24.491Z` to `2026-10-29T00:17:24.685Z`.

- **pass**: response HTTP 200.
- **pass**: device routing == [4, 4, 4, 4, 4, 4, 4, 4].
- **pass**: device otherwise unchanged (allowed: outputs[*].source, routing).
- **pass**: device received http 'video switch' with {'source': [0, 4]} exactly 1x.
- **pass**: WebSocket event 'routing_change' with {'output': 8, 'input': 4}.
- **pass**: hub GET /api/status -> data.routing.8 == 4 (HTTP 200).
- **pass**: every WebSocket message follows docs/api/websocket.schema.json.

The n/a is specifically the inherited `power_change` expectation restricted to the api client; flic power-off state, exact device command, hub readback and WebSocket schema assertions passed. WebSocket schema checks covered 13 preset, 4 power-off, 4 power-on and 11 all-output messages. These are message counts, not extra assertions.

## Exact record inventory

Paths are relative to the private attempt root; names retain the actual source SHA.

| Record | Bytes | SHA-256 |
| --- | ---: | --- |
| `evidence/F-FLIC-001/2026-10-29-V3-865ec9c6-flic.preset-flic.json` | 43315 | `ecb55542ac239f383c26ec8da569d1b2f8d1c64909cfe11a2549a068a9c090ff` |
| `evidence/F-FLIC-002/2026-10-29-V3-865ec9c6-flic.power_off-flic.json` | 33723 | `28a4934b2b511784feb97a84345d6ff9427977bf5c3168bf8806402eca51e1e4` |
| `evidence/F-FLIC-002/2026-10-29-V3-865ec9c6-flic.power_on-flic.json` | 33497 | `a12583e4e6ba0a88ab87273fd4484c4d8ccba5dd344bb24d4e5b5cac5c678355` |
| `evidence/F-FLIC-008/2026-10-29-V3-865ec9c6-flic.all_outputs-flic.json` | 37907 | `a31bd1d180ee14e29f6d250d220dc3724eade9eda6f98992988c87796458bc8d` |

## Covered paths and source hashes

Expected and actual ordered `covers` arrays match the existing declarations exactly, including repeated entries inherited by `_replay`; no coverage list was expanded or rewritten. The distinct common paths are:

- `run.py`
- `src/hub/cli.py`
- `src/hub/runtime_paths.py`
- `src/hub/runtime`
- `src/hub/core`
- `src/hub/persistence`
- `src/hub/domain/action_runner.py`
- `src/hub/integrations/hub_client_local.py`
- `src/orei_matrix.py`
- `src/telnet_client.py`
- `src/_task_supervisor.py`
- `src/rest_api/app.py`
- `src/rest_api/utils.py`
- `src/rest_api/websocket.py`
- `src/rest_api/events.py`
- `docs/api/websocket.schema.json`
- `src/rest_api/control.py`
- `tools/validate/clients/flic.py`
- `tools/validate/clients/flic_driver.mjs`
- `web/js/components/integrations-drawer.js`

Additional paths for `flic.preset`: `web/index.html`, `web/js/app.js`, `web/js/api.js`, `web/js/state.js`, `web/js/websocket.js`, `web/js/components/side-nav-drawer.js`, `web/js/components/routing-drawer.js`, `web/js/components/presets-drawer.js`.

Additional paths for `flic.power_off`: `src/rest_api/audio.py`.

Additional paths for `flic.power_on`: `src/rest_api/audio.py`.

Additional paths for `flic.all_outputs`: `src/rest_api/core.py`, `web/index.html`, `web/js/app.js`, `web/js/api.js`, `web/js/state.js`, `web/js/websocket.js`, `web/js/components/side-nav-drawer.js`, `web/js/components/routing-drawer.js`, `web/js/components/presets-drawer.js`.

Hash file `covered-source-and-fixture-hashes.json` contains 64 exact on-disk covered-source/fixture/harness/simulator file digests; `invocation-environment.json` contains CLI/stack/runner/scenario/driver/template/schema/package digests and sanitized environment bindings. Key digests:

| Input | SHA-256 |
| --- | --- |
| `tools/validate/clients/flic.py` | `95a7785df2f86e47491fbc300a1a6841983f52ba5f7c1de825e5e21b7bc86c45` |
| `tools/validate/clients/flic_driver.mjs` | `2b2ffe5f69a33686021172499bf735b6da4e567109e7164e3a836ef7fa37f93b` |
| `web/js/components/integrations-drawer.js` | `7611f24baea47c81496ef18a57172d72e819c48fb5593f40d178e41fb87d6224` |
| `web/js/utils/api-copy.js` | `43c7c4c91d15aef3b15135645ac3c25f15254f76efda99d18cc61f6d57ad0ef8` |
| `tests/validation/scenarios/flic_replay.py` | `941a4d524f37008d8ac273e802fbf309be744e46fe8183eb83d1002dad098c05` |
| Node executable | `d702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5` |

## Artifact privacy and acceptance boundaries

**Artifact admission/publication HOLD.** A conservative structural scan found eight unmasked `observations.state_before.auth.password` / `observations.state_after.auth.password` string fields, before and after in every record. Local comparison confirms all eight equal the checked-in simulator seed fixture value; only field presence, counts and equality booleans were emitted, never values. The original records were not sanitized, rewritten, imported or published. Escalation `msg_9a78f922fb8b` and the coordinator's explicit private-retention/report-only follow-up were processed. This establishes fixture attribution, not privacy clearance.

The initial conservative scanner/classification are retained separately as `private-redaction-assessment.json` and `private-redaction-classification.json`. Stack logs contain two WARNING markers, zero ERROR/CRITICAL markers and ten loopback HTTP URL occurrences under a narrow lexical scan; their full bytes remain private. That scan is not a complete free-form-string audit. No owner credential use or exposure is inferred.

Known VAL-15 free-form Action/Response string gaps remain open; source11f is unintegrated pending qualified different-family code/privacy review. This fixture-state observation is separately reported and does not grant repair authority or close VAL-15. Reserved native MiniMax-M3 review is limited to evidence metadata and cannot clear privacy or code gates.

This is actual Node execution of the shipped drawer generator with narrow DOM/state stubs followed by local HTTP request replay and simulator device readback. These four cases do not execute SDK gesture/startup scenarios and do not observe a physical Flic Hub, SDK version, button, display or physical CEC effect. V3 is the existing runner's simulator/client level, not HIL attestation.

F-API-034 remains a separate assertion gap: these successful route-all requests do not assert the disconnected `switch_all_failed` event/payload, 503, unchanged device and no routing write. Its target is not proven by this refresh; see [the existing gap analysis](FRESHNESS_DELTA.md). Existing closed original Tron approvals remain closed. No new visual baseline/Tron approval, physical HIL, 72-hour soak, week field sign-off or final version/artifact release gate is asserted.

## Retained receipts and handback

[Private attempt directory](../../../../build/software-waves/SW-AUDIT-01-flic-refresh/attempt-01/) contains the four exact records, run summary, original hub starts 1/2 and simulator logs, command/exit/stdout/stderr files, environment/source digests, live Run/Dispatch receipts, initial empty Git status/patch and private invocation/audit diagnostics. `artifact-hashes.json` indexes retained attempt files by byte size and SHA-256 (excluding itself and later closeout receipts). No emitted screenshot/media artifact was produced. The runner's normal pre-scenario environment restart accounts for two hub logs; it is not a retry of a failed qualification.

Only this secret-free assigned report is eligible for the scoped report-only commit. UTF-8, local links, exact path/source scope and CR-aware whitespace checks are recorded privately before commit; the invocation-only `core.hooksPath=` exception is authorized for this prose-only delivery. No source-hook, full suite, ledger generation or release pipeline success is claimed. An earlier read-only rg probe used a missing findings path and an unsupported Windows wildcard; those discovery errors did not run qualification or modify source.

Coordinator owns exact-report-commit independent metadata review, privacy disposition, canonical admission, artifact preservation/bundles, worker release, publication and integration. Functional refresh is complete; evidence admission remains held.
