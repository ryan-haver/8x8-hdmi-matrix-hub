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
