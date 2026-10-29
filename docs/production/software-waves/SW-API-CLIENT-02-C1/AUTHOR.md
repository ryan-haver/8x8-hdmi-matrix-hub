# SW-API-CLIENT-02-C1 author record

## Authority and boundaries

- Task `task_036936ee9cd3`, Dispatch `ctx_a7ac1a749cac`, existing Run
  `run_37205f6095b3`; dispatched terminal
  `term_cfff08f2-b0aa-4a24-933a-62a18d78baf6`, coordinator terminal
  `term_259c5526-02c2-44a8-b469-bf171aa435a0`.
- Exact base: `411c66429df3b813072e736c41c3a8aa83043a70` on the dedicated
  child branch `ryan-haver/wp-sw-api-offline-events`, dedicated Orca child
  worktree `wp-sw-api-offline-events` on the local Windows host. Origin:
  `https://github.com/ryan-haver/8x8-hdmi-matrix-hub.git`.
- Requested and observed effective launch: DeepSeek `deepseek-v4-pro/default`,
  native configured route, no effort override. No helper, subagent, alternate
  model, Claude/Anthropic, MCP, plugin or fallback was used. Project ceiling
  remains four active, including coordinator, one older external reservation,
  this author and the parallel Sol header author.
- Provider preflight (coordinator-supplied observation, not an author
  measurement): DeepSeek `45.40 USD` available at 22:50Z, with `3 USD` author
  plus `1.50 USD` corrections/review reserved; shared external use/limits/reset
  unreported and refreshed by the coordinator before launch. OpenAI pool 62%
  weekly remaining, reset `2026-10-27T06:33:16Z`, with a separate review
  reservation; no same-family approval substitution.
- Exclusive serial lease: `src/rest_api/control.py`,
  `tests/sim/test_sim_rest_reads.py`, new
  `tests/sim/test_sim_offline_switch_events.py`, new
  `docs/production/software-waves/SW-API-CLIENT-02-C1/AUTHOR.md` and the ignored
  `build/software-waves/SW-API-CLIENT-02-C1/**`. All other source, tests, shared
  contracts, root manifests, lockfiles, registry, ledger, evidence, failures,
  private configuration, baselines and other packages are READONLY. No push,
  merge, tag, cleanup or ledger generation. Coordinator alone owns finding
  metadata/registration/closure/import.

## Contract and correction

`docs/production/software-waves/SW-API-CLIENT-02-C1/FINDING.md` records the
provisional VAL-14 defect on the `failures.unreachable_switch` scenario: a valid
`POST /api/switch {"input":3,"output":1}` submitted while the matrix is already
disconnected answers 503 "Matrix not connected" and leaves the device unchanged,
but the observer sees `matrix_connection`/`status` and no `switch_failed` event.
The failing CI record is preserved byte-for-byte under
`docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci` and is not
imported as accepted feature evidence.

`src/rest_api/control.py` returned 503 before parsing a request when
`matrix_device.connected` was false, so neither `handle_switch` nor
`handle_output_source` reached their failed-command branches. The documented
WebSocket contract (`docs/api/WEBSOCKET.md`, `switch_failed` / `switch_all_failed`)
says a refused route emits that event.

The correction parses and validates the body first, then branches on the captured
connection state. An **unavailable** matrix is either unconfigured
(`matrix_device is None`, body "Matrix device not configured") or disconnected
(configured but not connected, body "Matrix not connected"); both are refused
routes for the purposes of the contract:

- **Unavailable + syntactically valid** route emits the documented event
  (`switch_failed` for a single output or the alternate output-source path,
  `switch_all_failed` for a route-to-all) and answers 503 with the distinct
  unavailable body, with no device mutation.
- **Unavailable + malformed/invalid** route still answers 503 with the distinct
  unavailable body but emits **no** event, so invalid ports are never published.
- **Connected** routing, validation and the existing inside-command failure event
  (a refused write answering 500 with exactly one `switch_failed`) are unchanged.
  Connected invalid input still answers 400.

Valid inputs reuse the existing parser semantics exactly (`parse_json_object`,
`require_field`, `validate_port` including their boolean/integer behaviour);
no contract was tightened and no parsing or side effect is duplicated.

A body-read error on an unavailable matrix (for example an over-limit body that
`parse_json_object` rejects as `aiohttp`'s `HTTPRequestEntityTooLarge`) keeps
unavailable precedence: it answers 503 with the distinct unavailable body, never
a 500. A connected matrix keeps the existing opaque 500 sanitization for the same
error (R1, an observed draft regression caught by the coordinator's differential).

## Reproduction (red, then green)

A disposable real `run.py` + simulator probe
(`build/software-waves/SW-API-CLIENT-02-C1/repro_offline_switch.py`) starts the
hub through its real entry point (`run.py` subprocess, `UC_ENABLED=false`) against
the simulator, connects a `/ws` observer, waits until `/api/health` reports a
connected-positive state, injects `drop_http` through the simulator control API,
waits until health reports disconnected, then POSTs a single route, a route-to-all
and an output-source route. It records the full source SHA, reads the routing back
from the simulator before and after, and reads the simulator command log so routing
writes are distinguished from background reconnect logins.

- **RED** (base `411c6642`): 503 for all three, no `switch_failed` /
  `switch_all_failed`, routing unchanged — reproduced the finding.
- **GREEN** (corrected source): 503 for all three, with `switch_failed`
  `{"input":3,"output":1}`, `switch_all_failed` `{"input":4}` and
  `switch_failed` `{"input":5,"output":2}`, routing unchanged and no mutating
  routing write in the simulator log.

Each invocation writes to a fresh timestamped `attempt-*` directory so attempts
are immutable; the initial red and green results are preserved separately.

## Focused verification

Commands run from the dedicated author worktree with Python 3.12.10 at
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
and process-local `PYTHONPATH` pointing at this worktree's `src` and root
(abbreviated `PYTHON` below; `-p no:tests.route_inventory` disables the shared
route report for partial runs).

- `PYTHON -m ruff check src/rest_api/control.py tests/sim/test_sim_offline_switch_events.py tests/sim/test_sim_rest_reads.py` — exit 0.
- `PYTHON -m pytest tests/sim/test_sim_offline_switch_events.py tests/sim/test_sim_rest_reads.py -p no:tests.route_inventory -p no:cacheprovider -q --tb=short` — **72 passed**.
- `PYTHON -m pytest tests/sim/test_sim_ws_contract.py tests/sim/test_sim_rest_writes.py tests/sim/test_sim_offline_switch_events.py -p no:tests.route_inventory -p no:cacheprovider -q --tb=short` — **72 passed** (WS contract and write behaviour preserved).
- `USE_MOCK_MATRIX=1 PYTHON -m pytest tests/test_rest_api.py tests/test_security_hardening.py tests/test_security_v3_hardening_scenarios.py -p no:tests.route_inventory -p no:cacheprovider -q --tb=short` — **434 passed, 1 skipped** (opaque internal-error and invalid-input behaviour preserved).
- `npm ci --ignore-scripts --no-audit --no-fund` — **added 190 packages** (local, gitignored), so the complete core suite's JavaScript ESLint check runs in this worktree.
- R1 focus: `USE_MOCK_MATRIX=1 PYTHON -m pytest tests/sim/test_sim_offline_switch_events.py tests/sim/test_sim_rest_reads.py tests/test_security_hardening.py tests/test_rest_api.py -p no:tests.route_inventory -p no:cacheprovider -q --tb=short` — **441 passed, 1 skipped** (over-limit 503 vs 500 regression plus the original contract and opaque-error coverage).

New `tests/sim/test_sim_offline_switch_events.py` covers: single output, route-to-all
and the alternate output-source path while disconnected (event + 503 + no
mutation); malformed/invalid offline requests (503, no event, no invalid ports);
an unconfigured-matrix boundary (valid single/all/alternate route emits the exact
event with the "Matrix device not configured" body, malformed publishes nothing);
an unavailable over-limit body (503, not 500, both handlers) with the connected
over-limit control (still opaque 500); a connected positive control; and a
connected inside-command refusal (500 + exactly one `switch_failed`).
`tests/sim/test_sim_rest_reads.py` adds a read-coverage test that reads routing
unchanged, a 503 `/api/status` with `connected=false`, and the restored routing
after a refused offline route.

## Completed verification and delivery

Implementation commits (dedicated child branch `ryan-haver/wp-sw-api-offline-events`):

- **`64e10a160fceb9eccf861a89f64b014ebe210dfa`** — `fix(rest): emit switch_failed/switch_all_failed for unavailable routes`
  (control.py + both test modules).
- **`3788353ef2ef92cf52cf266f3e356dd6840d00da`** — `fix(rest): keep 503 for oversized bodies on unavailable routes`
  (R1 over-limit precedence + its regression tests).

The normal configured hook ran unmodified for the final commit (Ruff, then the
complete core suite excluding the separate HA and scripted-Remote jobs, with
`ROUTE_COVERAGE_STRICT=1`, `USE_MOCK_MATRIX=1`, `PYTHONUTF8=1` and isolated
`MATRIX_DATA_DIR`/`UC_CONFIG_HOME`/`TEMP`/`TMP` under the assigned build tree).
Result: Ruff passed; **4060 passed, 6 skipped, 35 deselected, 4 warnings in
1048.89 s**; strict route coverage **177/177 (100%), zero uncovered** (confirmed
from the terminal summary and `route-coverage.json`). The six skips are the
documented limits (POSIX permission enforcement, POSIX unlink-while-open race,
missing Home Assistant dependencies, unavailable Windows symlink privilege, and
two opt-in real-Chromium bridge tests). No ledger generation or canonical
evidence mutation ran. The intermediate hook on `64e10a16` (4057 passed, same
route coverage) and the earlier aborted/npm-blocked attempts are preserved
separately under the build tree; `npm ci --ignore-scripts --no-audit --no-fund`
(190 packages, gitignored) supplied the JavaScript lint dependencies.

Clean-source actual campaign against the final commit:

`PYTHON -m tools.validate run --target sim --client api --scenario failures.unreachable_switch --out build/software-waves/SW-API-CLIENT-02-C1/campaign-clean-01`

Exit 0; `failures.unreachable_switch [api] V2` **PASS**. The record and summary
identify full source `3788353ef2ef92cf52cf266f3e356dd6840d00da`, `dirty: false`,
`dirty_files: []`, entry `run.py -> hub.cli shared runtime (UC_ENABLED=false)`,
`image_digest: null`. The scenario's `switch_failed` WebSocket check passes
(`events after the action: ['matrix_connection', 'switch_failed']`).

Offline boundary regression (the same disposable `run.py` + simulator probe) on
the clean final source `3788353ef2ef92cf52cf266f3e356dd6840d00da`: connected-positive
health observed before the fault, disconnected observed after; a valid single
route emits `switch_failed {"input":3,"output":1}`, a route-to-all emits
`switch_all_failed {"input":4}`, the alternate output-source emits
`switch_failed {"input":5,"output":2}`; routing read back unchanged and no
mutating routing write in the simulator log (background login entries excluded).
Results are preserved in a fresh timestamped `attempt-*` directory.

Final tracked package consists of `src/rest_api/control.py` (modified),
`tests/sim/test_sim_rest_reads.py` (modified),
`tests/sim/test_sim_offline_switch_events.py` (new) and this author record (new).
No registry, ledger, manifest, lockfile, contract, failure, evidence or baseline
was edited, and no push, merge, tag, cleanup or ledger generation was performed.

Independent different-family review at the submitted SHA remains **pending**, as
do coordinator acceptance, finding registration/closure, evidence preservation
and integration/publication. Browser/Remote/HA, image builds, physical HIL,
72-hour soak, week field and final release gates remain outside this bounded
API V2 proof. Actual native model: DeepSeek `deepseek-v4-pro` (default route).


---

# 2026-10-29 declarative assertion follow-up

Bounded child of existing SW-API-CLIENT-02, F-API-034 only; primary ownership
unchanged. OpenAI `gpt-6.1-sol/high` author, Task `task_c0d26e9e563e`, Dispatch
`ctx_0f27082dc4eb`, existing Run `run_37205f6095b3`. Frozen published base
`938ae30339790c361abdda6fdd01b11a4e498518`; actual task branch
`ryan-haver/wp-api-client-02-c1` on local Windows.

## Scope and assertion design

The product handler already refuses a valid canonical `POST /api/switch`
route-all request when unavailable with HTTP 503 and `switch_all_failed` carrying
the validated input. This package adds declarative scenario
`sw_api_client_02_c1.switch_all_failed` and simulator-backed tests; product source,
the shared runner/model/client, existing scenarios/tests and fixtures are unchanged.

The scenario checks the exact status and refusal body, failure event input,
absence of `routing_change` and the single-output `switch_failed`, no `video switch`
command (including an attempted nonmutating write), no device write, and unchanged
full simulator state. Direct tests use a real simulator, real `OreiMatrix`
transport, real hub app, existing `ApiClient`, `WsObserver`, `SimDevice` and
the runner's actual expectation checker. Inputs 1, 4, 8 and `" 6 "` prove ports
are validated and normalized rather than hardcoded. Invalid range/type/missing/
unknown-field controls retain unavailable precedence and publish no invalid ports.
The connected per-output positive control proves the no-command, unchanged-state
and no-success-event assertions each fail on an actual successful route. Wrong
response/status/event expectations fail against the actual refused exchange.

## Coordinator registry contribution

The author never edited or staged the registry. In response to the blocking
registry handshake, the coordinator independently inspected these source files,
changed and staged only the F-API-034 scenario-link list in this checkout, and
explicitly authorized including that already-staged contribution in the normal
source commit. Its sole change appends the new scenario ID; `current`, `target`,
basis, evidence, findings and other features are unchanged. This is composite
authorship: new source/tests/report by the dispatched author, registry link by
the coordinator. The private coordinator receipt is
`build/p1-fanout-20261028/fapi034-registry-contribution-01/receipt.json` in the
coordinator checkout, not a portable path in this task checkout.

## Preserved initial preparation failure

The first focused run passed 12 direct simulator regressions and failed the
managed-source-runner assertion: the outcome was BLOCKED because the managed
runner requires a healthy Telnet link before starting any simulator scenario.
Requiring certificate verification against the disposable simulator's self-signed
TLS certificate correctly keeps the actual matrix client disconnected, so that
managed preparation cannot complete. No shared-runner edit or product defect
is inferred. Original log: `build/software-waves/SW-API-CLIENT-02-C1/focused-first.log`.
The original raw failed record/hub logs were created under
`C:/t/f034-20261029-a/pytest-of-ryanh/pytest-0/test_registered_scenario_with_0/`,
but subsequent pytest automatic retention removed that temporary directory before
the author's preservation copy. This is a preservation failure: the raw JSON/hub
logs are unavailable, not preserved. The failed pytest log retains the count,
assertion and BLOCKED outcome; the native tool transcript records the actual
Telnet blocked reason observed from that original JSON. The coordinator was
notified; no reconstructed raw record or qualification retry substitutes for it.

## Verification and disposition

The coordinator explicitly approved the existing external-stack interface in a
second blocking ask after the initial preparation failure. The owned helper
launches a new disposable `SimulatorProcess` and `HubProcess` from this checkout
with free loopback ports, applies the declared TLS-verification environment, and
passes their actual URLs to the unchanged runner through `hub_url` and
`sim_control_url`. This external mode skips the managed-stack healthy-Telnet
preparation by its existing contract. It does not falsify link health, weaken
assertions or repair the managed preparation limit. Normal managed all-scenario
CI compatibility remains UNRESOLVED and is an additional integration blocker.
The explicit external source mode is neither an image nor a hardware campaign.

Each new external attempt records `external-stack-receipt.json` with actual
source root, Python executable, parent/child argv, PIDs, loopback ports, source
hashes, declared and recorded hub settings, initial disconnected health, source
commit and process exit codes. Hub data is retained in the private allocated
temp tree. External runner metadata alone omits these settings; the sidecar
provides that attribution rather than inferring it from an API result.

Before source commit: scoped Ruff passed; 52 registry/model/schema tests passed
in 4.11 s; Mypy passed all 91 source files; 38 existing offline-switch/WebSocket
contract tests passed in 28.38 s; the corrected external-mode focused module
passed all 13 tests in 24.42 s. Focused pytest invocations use
`-p no:tests.route_inventory -p no:cacheprovider` so they do not overwrite full
route proof. Logs are under `build/software-waves/SW-API-CLIENT-02-C1/`.
The normal configured source-commit hook and clean committed-source campaign
are pending at this source report write; final actual results will follow in
a report-only commit after execution.

Actual source API plus `/ws` observation is V2 only. F-API-034 retains its V3
target and recorded current V2; neither the full parent unit nor the per-output
success branch nor shipped-image/browser behavior is qualified by this package.
Qualified different-family review, integration and qualification remain HELD;
DeepSeek Pro is only the retained candidate with current quota UNKNOWN. Raw
captures remain private with admission HOLD under VAL-15. No canonical evidence
import, ledger generation, publication, integration, cleanup or release is performed
by this worker.

## Final source verification and partial disposition — 2026-10-29

Useful source commit: `386872316cb60130b06dd704557ae6ca1a92b5c8`
(`test(validation): assert unavailable route-all refusal`), parent exactly
`938ae30339790c361abdda6fdd01b11a4e498518`. This follow-up is append-only to the
historical report: its original 11,878-byte Git blob remains the exact prefix,
SHA-256 `c25692409f8d4f7ae38a21695571821475b1ec097de995517b266c2b59c4e9ff`.
The coordinator corrected the brief's mistaken NEW designation and explicitly
granted this append-only lease in message `msg_6b90fae7a341`.

All current commands used the root `.venv/Scripts/python.exe` from this checkout
with its own root/src `PYTHONPATH`, bytecode disabled and UTF-8 output. Data/config
were isolated under the owned build tree or retained disposable hub temp;
`TEMP`/`TMP` stayed within `C:/t/f034-20261029-a`. The committed-source campaign
used NEW empty `campaign-parent-01`, and the gate check used NEW empty
`check-parent-01`, both below that allocated parent. No install or dependency
update ran; the supplied ignored `node_modules` junction was used read-only.

Normal source commit used the configured hook at
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.githooks`, with
`ROUTE_COVERAGE_STRICT=1`, `USE_MOCK_MATRIX=1` and `PYTHONUTF8=1`, without bypass.
Ruff passed over the configured full paths. Complete core pytest (excluding the
separate HA and UC jobs) passed **4,095 tests, 6 skipped, 35 deselected, 4 warnings
in 899.75 s**. Route coverage was **177/177, 100%, strict true, zero uncovered**.
Commit/hook exit was 0. Original output and exit are
`source-commit-hook.log` / `source-commit-hook.exit`; exact route proof is copied
to `full-route-coverage.json` under the owned build directory.

One clean committed-source campaign ran with:

```text
PYTHON build/software-waves/SW-API-CLIENT-02-C1/campaign.py build/software-waves/SW-API-CLIENT-02-C1/campaign-clean-01
```

The script invokes the committed owned helper through existing external-stack
runner interfaces and then inspects the actual summary and records. Exit 0;
**one outcome PASS/ok, one schema-valid record, all eight checks PASS, zero n/a**;
actual client `api`, target `sim`, level **V2**, source full SHA above,
`dirty: false`, `dirty_files: []`, image digest null. It checks the actual captured
`POST /api/switch` body `{"input":6}`, exact 503 refusal body, exact single
`switch_all_failed {"input":6}`, absence of success/single-output events, full
device state equality, empty state diff and no routing command/write. It also
checks recorded source hashes against current files and the committed text.
The 30 live counterfactual oracle checks are exercised by the focused module
and the normal complete core hook, rather than fabricated into campaign evidence.

Private campaign artifacts are under
`build/software-waves/SW-API-CLIENT-02-C1/campaign-clean-01/`:
`run-summary.json`, `evidence/F-API-034/2026-10-29-V2-38687231-sw_api_client_02_c1.switch_all_failed-api.json`,
`external-stack-receipt.json`, `artifact-checks.json` and original process logs.
The evidence record SHA-256 is
`11849d40b89ad90b2a554577e26df9ac62f154d67c55f2b5ecaa935a218e0492`;
the artifact-check receipt lists all campaign member hashes. Actual child
return codes after the existing Windows stop helper were hub **1**, simulator
**1**; these are recorded separately and are not represented as graceful exit 0.

The final tracked base diff is limited to the two new assigned source/test
modules, this append-only author report, and the coordinator-authored one-line
F-API-034 registry mapping. `precommit-ownership-audit.json` records the exact
path/semantic/prefix audit and five hash-verified preserved files from the
successful focused external attempt. No product/shared source, other tests,
fixture, canonical evidence, ledger, finding, current/target level, manifest,
lockfile or baseline changed. Build artifacts remain ignored/private.

**Acceptance is partial/UNMET, and the required worker outcome is FAILED.**
The original managed BLOCKED raw JSON/hub logs could not be recovered honestly;
the coordinator explicitly requires failed/partial outcome for this preservation
failure despite useful functional passes. `preservation-status.json` records the
exact lost paths, surviving diagnostic references and observed copy error,
explicitly as an authored status receipt, not reconstructed original evidence.
The surviving `focused-first.log` retains the initial **12 passed, 1 failed,
exit 1**. There was no rerun or relabeling of that failed managed qualification.
The separately approved external campaign does not repair default managed-runner
preparation or normal all-scenario CI compatibility, which remains an integration
blocker. Qualified different-family review, integration/qualification, VAL-15
privacy admission and all cleanup remain HELD. No push, merge, tag, task-ref
publication, worker release, worktree removal or canonical import was performed;
those decisions remain coordinator-owned. F-API-034's V3 target and parent scope
remain open.

### Current invocation and exit inventory

`PYTHON` below is the root virtual-environment interpreter specified above;
all relative commands ran in the assigned task checkout. Logs named below are
under `build/software-waves/SW-API-CLIENT-02-C1/`.

| Invocation | Exit and actual result | Surviving artifact |
| --- | --- | --- |
| `PYTHON -m pytest tests/validation/test_sw_api_client_02_c1.py -q -p no:tests.route_inventory -p no:cacheprovider` (initial managed attempt) | 1; 12 passed, 1 failed; BLOCKED managed preparation | `focused-first.log`; original raw JSON/logs LOST as recorded above |
| Same focused invocation, after explicit external-mode approval | 0; 13 passed | `focused-external.log`, hash-verified `focused-external-raw/` |
| `PYTHON -m ruff check tests/validation/scenarios/sw_api_client_02_c1.py tests/validation/test_sw_api_client_02_c1.py` | 0; all checks passed | Native tool transcript; full Ruff repeated by normal hook |
| `PYTHON -m pytest tests/sim/test_sim_offline_switch_events.py tests/sim/test_sim_ws_contract.py -q -p no:tests.route_inventory -p no:cacheprovider` | 0; 38 passed | `existing-regressions.log` |
| `PYTHON -m pytest tests/validation/test_registry.py tests/validation/test_model.py tests/validation/test_evidence_schema.py -q -p no:tests.route_inventory -p no:cacheprovider` | 0; 52 passed | `registry.log` |
| `PYTHON -m mypy src/ --cache-dir build/software-waves/SW-API-CLIENT-02-C1/mypy-cache` | 0; 91 source files passed | `mypy.log` |
| `git commit -m "test(validation): assert unavailable route-all refusal"` with normal configured hook and strict route environment | 0; Ruff and 4,095 complete-core passes; 177/177 routes | `source-commit-hook.log`, `.exit`, `full-route-coverage.json` |
| Committed-source external campaign command above | 0; one PASS API V2 outcome, one valid record, eight PASS checks | `campaign-clean-01.log`, `.exit`, campaign directory and member hash receipt |
| `PYTHON -m tools.validate check --evidence build/software-waves/SW-API-CLIENT-02-C1/campaign-clean-01/evidence --run-summary build/software-waves/SW-API-CLIENT-02-C1/campaign-clean-01/run-summary.json --expect-clients api` | 0; gate OK, zero known failures in supplied summary | `campaign-check.log`, `.exit` |
| `PYTHON -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -q -p no:tests.route_inventory -p no:cacheprovider` | 0; 489 passed in 3.10 s | `report-docs.log`, `.exit`; NEW empty `docs-parent-01` |
| `git -c core.whitespace=cr-at-eol diff --check` | 0 | Native tool transcript |

The actual validation CLI gate pass reads registry/evidence and evaluates its
existing rules; it does not admit private artifacts, establish different-family
review, solve managed-runner preparation or promote API V2 to V3. No ledger was
generated. The final closeout changes this report only and uses the documented
invocation-only documentation hook exception after the actual checks above;
the source implementation commit used its complete normal hook. No global or
repository hook configuration is changed. The coordinator owns final artifact/
native-transcript/bundle preservation and exact task publication; surviving
worktree/temp resources must remain retained because preservation acceptance
is UNMET.
