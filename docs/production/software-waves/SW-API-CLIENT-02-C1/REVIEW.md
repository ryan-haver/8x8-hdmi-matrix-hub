# SW-API-CLIENT-02-C1 independent review

Disposition: **ACCEPT the bounded source correction at exact candidate
`4baef5743b0e970328a979f181d701361f58da70`.** No blocking product finding was
identified. This accepts the unavailable-route event correction, not canonical
evidence assembly, full feature targets, integration, publication or release.

## Authority and exact scope

- Task `task_8bedb7d1234c`, Dispatch `ctx_314709206275`, Run
  `run_37205f6095b3`; reviewer terminal
  `term_17b3c7db-3d10-4d81-9d03-f67cc3c89409`, coordinator
  `term_259c5526-02c2-44a8-b469-bf171aa435a0`.
- Injected reviewer route: Codex `gpt-6.1-sol/high`; source author: DeepSeek
  `deepseek-v4-pro/default`, different underlying model families. Coordinator
  owns native launch/export attestation. No other model, helper, subagent,
  fallback or Anthropic/Claude was used in this review.
- Original base `411c66429df3b813072e736c41c3a8aa83043a70`; functional source
  `3788353ef2ef92cf52cf266f3e356dd6840d00da`; submitted candidate above. Git
  proves the functional-source-to-candidate diff adds only `AUTHOR.md`; the
  handler and both test blobs are identical. All reviewer executions preceded
  this new report and identify clean candidate `4baef574...`, dirty files `[]`.
- Dedicated review branch `ryan-haver/wp-sw-api-offline-review`, Windows Orca
  worktree `wp-sw-api-offline-review`. Writes were confined to this new report
  and new ignored `build/software-waves/SW-API-CLIENT-02-C1-review/**`.
  Product, registry, ledger and allocation-ledger paths remained read-only under
  the explicit dispatch lease. No push, merge, tag or resource cleanup occurred.
- Coordinator preflight supplied at dispatch: official pool 52% weekly remaining,
  ordinary usage allowed, reset 2026-10-27 06:33:16 UTC; shared external
  commitments unreported. Review stayed within the dispatched route and
  four-active ceiling; no launch or quota headroom was inferred by this worker.

The base-to-candidate audit contains exactly four paths: modified
`src/rest_api/control.py`, modified `tests/sim/test_sim_rest_reads.py`, new
`tests/sim/test_sim_offline_switch_events.py`, and new author report. Routes,
WebSocket/REST schemas, parser/port helpers, shared runtime contracts, transport,
reconnect/lifecycle, root manifests, lockfiles, validation scenarios and evidence
are unchanged. Full diff, blob identities, command receipts and hashes are in
the ignored review `audit.json`.

## Findings and reasoning

**No critical, high or medium finding; no required source correction.** Both
availability boundaries were inspected and exercised through actual aiohttp.

`handle_switch` and `handle_output_source` retain the availability decision made
at handler entry. They parse once using the existing helpers, validate ports
before publishing, and take a mutually exclusive offline/command path. Valid
already-disconnected and unconfigured requests publish one failure event and
retain their distinct 503 envelopes. The offline branch never invokes
`direct_command`; no duplicate event or routing write was observed. Moving
output validation into the parsing block preserves accepted port coercion,
including integer strings, rejection of booleans/floats, omitted/null output
meaning all outputs, and the alternate handler's established ignored-field
behavior. A later link change cannot turn an entry-offline request into a write;
entry-connected command refusal remains handled by the existing command branch.

Malformed JSON, non-object bodies, invalid/unknown fields where historically
rejected, invalid path ports and body-read failures retain offline 503 precedence
without publishing invalid ports. Connected malformed requests remain 400.
Connected oversized/read failures remain opaque 500 responses. Cancellation is
not swallowed by `except Exception`: six controlled handler checks propagated
`CancelledError`, without a command or event. Those controlled exception checks
are supplemental fault stubs, not hardware or network-cancellation proof.

**Low, optional test hardening:** the three new disconnected tests and the
parameterized unconfigured test wait for matching fields but do not permanently
assert exactly one failure event or full payload equality. A future duplicate
failure publication, or extra payload field, could pass those particular tests.
Source: `tests/sim/test_sim_offline_switch_events.py`, `_Ws.wait`,
`test_offline_single_output_emits_switch_failed`,
`test_offline_route_all_emits_switch_all_failed`,
`test_offline_output_source_emits_switch_failed`, and
`test_unconfigured_matrix_valid_route_emits_event`. This is a regression-test
coverage limitation, not an observed product defect: this review independently
checked full failure payload equality, multiplicity and schema on the candidate.
The existing inside-command refusal test does assert its single event. No future
change is a condition of this exact-source acceptance.

## Independent execution

Python was `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
3.12.10 on Windows 11. Every command used this review worktree as CWD and
process-local `PYTHONPATH=<own worktree>/src;<own worktree>`, UTF-8 and disabled
bytecode writes. Configuration/data/temp, pytest base temp and mypy cache were
isolated under the assigned new build subtree. Actual hubs and simulators used
loopback and ephemeral ports; no owner LAN, hardware or private root data was
used. Source execution has `image_digest: null` throughout.

`execute.py` captures exact argv, CWD, environment, source/dirty state,
start/end UTC and exit in separate `*-receipt.json` files, with raw `*.log`
files. All six executed jobs exited **0**, without a behavioral retry:

| Job | Actual command after the interpreter | Result |
| --- | --- | --- |
| focused | `-m pytest tests/sim/test_sim_offline_switch_events.py tests/sim/test_sim_rest_reads.py tests/sim/test_sim_ws_contract.py tests/sim/test_sim_rest_writes.py -p no:tests.route_inventory -p no:cacheprovider --basetemp <own build>/pt -q --tb=short` | 138 passed, two existing deprecation warnings, 43.62 s |
| ruff | `-m ruff check --no-cache src tests custom_components tools run.py run_server.py` | All checks passed |
| mypy | `-m mypy src/ --cache-dir <own build>/mc` | No issues in 91 source files |
| campaign | `-m tools.validate run --target sim --client api --scenario failures.unreachable_switch --out <own build>/campaign` | 1/1 scenario, 7/7 checks PASS, V2 API |
| probe | `<own build>/probe.py` | 38 actual HTTP route cases PASS; 24 observed WS envelopes schema-checked |
| boundary | `<own build>/boundary.py` | 9 actual aiohttp cases, 6 cancellation and 6 body-read exception checks PASS; 6 raw WS messages schema-checked |

Partial pytest explicitly disabled `tests.route_inventory`; it did not replace
the author's complete 177-route report. No broad whole-suite rerun followed the
verified final normal author hook. Diagnostic scripts are ignored review
artifacts, not shipped tooling or additions to the regression suite.

The clean campaign retained the existing `failures.unreachable_switch` scenario
and all its assertions, including `switch_failed`; it returned 503, checked
device output 1 remained input 2, checked no other state change, observed the
failure event, checked disconnected health and unavailable status, and passed
the WS schema check. Its record and summary identify full clean source
`4baef5743b0e970328a979f181d701361f58da70`, actual `run.py -> hub.cli shared
runtime (UC_ENABLED=false)`, and no image. This is new exact-source evidence,
not a pass-only waiver for historical CI.

The separate actual-entry probe first observed both connected HTTP health and
Telnet health, synchronized `/ws`, injected `drop_http`, and waited for observed
disconnected health before submitting routes. It proves the already-offline
boundary rather than mistaking startup unready for a fault transition:

- Concrete simulator routing before and after offline operations was
  `[2, 2, 1, 1, 5, 6, 1, 1]`; full simulator state also compared equal.
- Single input 3/output 1, all input 4, alternate input 5/output 2, and coerced
  string input 3/output 2 each returned the exact disconnected 503 envelope and
  emitted exactly its own expected failure payload. Twelve invalid/malformed
  requests and two oversized requests emitted no routing/failure event.
- The complete offline event window contained exactly those four failure
  events and no routing change. Command-log inspection excluded nonmutating
  background login activity and required no routing command or non-login write.
- After clearing faults and observing reconnection, twelve malformed controls
  returned 400; both oversized controls returned opaque 500. Connected single,
  all and alternate routes produced concrete simulator readback, ending at
  `[7, 8, 7, 7, 7, 7, 7, 7]`. Connected simulator write refusal for each route
  returned 500 and exactly one appropriate failure event, preserving state.

The distinct aiohttp body-limit probe used an actual app configured with
`client_max_size=1024` and a 2,084-byte JSON body for **both** handlers in all
three availability states. Disconnected and unconfigured responses stayed 503
with their distinct bodies and no route event; connected responses stayed
opaque 500. It also checked all three valid unconfigured route forms emitted
their exact event once, with unchanged concrete simulator routing and no write.
This independently closes the coordinator's original R1 differential on final
source; the dispatch-provided private differential itself was not modified.

## Author evidence and historical failures

Inspected actual author report, source/tests, configured `.githooks/pre-commit`,
normal hook logs, route inventory, clean campaign, and timestamped final probe.
The configured hook is the shared repository `.githooks` path. Its final actual
log `hook-commit-03.log` contains full CI-path Ruff, normal core pytest,
**4060 passed, 6 skipped, 35 deselected, four warnings, 1048.89 s**, and strict
**177/177, zero uncovered**, followed by successful commit `3788353e...`.
Source/test blob identity ties that tested working tree to submitted `4bae...`.
The six skips retain their stated Windows/HA-dependency/opt-in-browser limits;
they are not HA or actual-browser acceptance. Configured mypy was independently
run here; it is separate from the normal hook.

Earlier `hook-commit.log` genuinely failed the JavaScript lint test without
`node_modules`: 1 failed, 3832 passed, 22 skipped, 35 deselected. Author then
installed the existing lock's 190 packages without modifying manifest/lockfiles.
The intermediate `hook-commit-02.log` passed 4057 tests on `64e10a16...`; that
pre-R1 source is not final acceptance. The dispatch-reported premature hook
stopped after pending inbox is aborted, not a PASS; its full native transcript
remains coordinator preservation work, not a newly verified log here.

Early diagnostic results with null source attribution or startup-disconnected
health do not establish a connected-to-offline transition. The initial null
routing/coordinator overstrict login calibration remains rejected diagnostic
history. The final author attempt `attempt-20261021T001742Z/result.json` does
contain full source `3788353e...`, connected-positive then disconnected health,
concrete nonempty routing and exact failure payloads. The reviewer initially
misread which attempt had null routing and corrected that statement immediately;
no null-to-null comparison is used as acceptance evidence. Final concrete proof
was independently established above. An interim status message said 39 probe
cases; the actual preserved result contains **38**, as reported here.

Original CI39500840835 failed record remains unchanged outside accepted feature
evidence. Its 37,876 bytes hash to
`a3ff5c68c366334e6b0c647396745ffa5e9021fa00219be1c6bdf358eb490a04`, matching
the committed receipt. It preserves the real missing-event failure. Hashes of
author logs/results and source diffs are recorded in review `audit.json`; this
audit is not a substitute for coordinator-owned full native/workspace/Git backup.

Read-only inspection had harmless wrong-path/glob errors for the author's
route-report location and nested campaign evidence, and one rejected Orca
`--type message` attempt (unsupported type). Correct paths and supported
`--type status` succeeded; no test failure, source change, unsupported fallback
or lifecycle duplication followed those inspection errors.

## Acceptance boundary and delivery

SW-API-CLIENT-02 keeps primary allocation. This is bounded F-API-033 API V2
correction proof, with F-REL-009 and F-API-034 affected secondarily through
single/all-output failure behavior; it does not promote their complete targets.
No browser/Remote/HA V3, image, physical HIL, 72-hour soak, week field sign-off,
Tron visual approval or final version/artifact release is established. The
parallel F-SEC-007 freshness failure reported by the coordinator is an evidence
freshness issue outside this product correction; this review neither repairs it
nor treats an unrelated stale record as a product failure.

Coordinator owns finding registration/closure, feature metadata, evidence import,
serial ledger/registry checks, integration/combined validation and exact remote
publication. No provisional finding link was added to weaken a gate. Source
acceptance here is complete and exact; later material source or integration
corrections require exact re-review, and canonical evidence assembly remains a
separate reviewable outcome.

Only this report is committed. Its report-only commit uses the documented
invocation-only `git -c core.hooksPath= commit` exception after report structure,
local path and CR-aware staged whitespace checks; no implementation hook was
bypassed and no persistent hook configuration changed. Reviewer artifacts,
native transcripts and full Git bundles must be preserved by the coordinator,
with publication/release ownership unchanged. This worker does not retain or
release its own resource.
