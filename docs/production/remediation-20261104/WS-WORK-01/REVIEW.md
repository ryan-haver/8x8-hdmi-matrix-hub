# WS-WORK-01 independent component review

**Component correctness: FAIL at the exact candidate. Component acceptance and
bounded first-authorship acceptance: HOLD.** Reentrant eager cleanup can report
`DrainReport(requested=0, remaining=0)` while admitted work remains alive. The
ordinary focused suite passes, but does not exercise this combination. This is a
completed independent review, not an implementation delivery, correction, retake
or request for another judge. CR-01 remains open.

## Exact subject, authority and provenance

Reviewed on 2026-11-04 UTC, beginning about 08:08Z, in
`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-remediation-ws-work-01-review`,
branch `remediation/ws-work-01-review`. Candidate and review base:
`15c069bdeb3a9ace37bf68033812ff72659bfbd1`; candidate parent:
`460a190575e905f8350c454e63c4d570c8b560fa`.
The complete parent-to-candidate diff is exactly three additions:

- `src/rest_api/ws_request_work.py`;
- `tests/test_ws_request_work.py`;
- [AUTHOR.md](AUTHOR.md).

Every pre-existing tracked file is unchanged in that diff. My source/tests/AUTHOR
remain unchanged; the only tracked review addition is this report. Coordinator
supplied `.codex/config.toml` remains untracked and untouched (`multi_agent=false`).
The allocation ledger, shared contracts, manifests, registry, original findings,
baselines and other worktrees remain outside my write lease.

Reviewer: OpenAI Codex, dispatched `gpt-6-astra/high`, Task
`task_b9f4d569ee06`, Dispatch `ctx_eae88fba1228`, terminal
`term_831bbd2d-c2b8-4d9c-b5b7-d02f3c8738e9`, existing Run
`run_37205f6095b3`. Live `worker-show` confirms that authority and this isolated
workspace. The pinned review preflight selects Astra/high; this is assignment
evidence, not a separate backend attestation. No helpers or nested workers were
used. Domain context is the accepted [R8D restoration review](../../../validation/RUNTIME_REVIEW_RESTORATION.md)
and the bounded judgement at `dda63d661d143a591d6d3d82346457fb52199795`;
neither is generic author/reviewer qualification for unrelated domains.

Actual candidate author: native Anthropic `claude-opus-5-5`, session
`2a593a53-f899-407f-a59d-862cd4c8e524`, Task `task_38756b76bd12`, Dispatch
`ctx_14a660b697ab`. I parsed the complete supplied native JSONL: 2,484,777 bytes,
SHA-256 `62c345ef6af80abe7eb302d868722f90b8895da359fd7bd8c1bad9b5e37a22e6`,
1,081 records, 204 assistant model fields identifying only that model. Deduplication
by tool-use ID yields 103 calls and 103 results: Skill 1, PowerShell 31, Bash 47,
Write 7, Edit 13, Read 4. No sidechain or helper/model-switch call appears. High
effort is explicit launch/config evidence; native per-turn effort is unexposed.
The two cwd values are the assigned author tree and its assigned receipts
subdirectory. That second cwd is not a boundary violation. Git's human author
field and Claude co-author trailer are distinct from native source authorship.

Coordinator delivery, author task and review task were read only through the
single pinned integration snapshot `9e26c302694c05d22b6f58db7616de4e44baff8a`.
No integration source was imported. Native inputs/results establish actual
construction and editing of the new source/tests, full existing websocket/events
reads, app/runtime lifecycle excerpts, schema/contract excerpts, and actual test
commands. They do not establish a full standing-protocol read: the initial ledger
read was only `head -5`, with later targeted precedent excerpts. AGENTS was injected
in the native context. I do not manufacture missing read proof from my own reads.

Canonical LF SHA-256 values independently match the supplied frozen candidate:

| File | SHA-256 |
| --- | --- |
| Module | `3bc116d88029aeecdbec5fdce7590e5d623442e37049a9bc4c7bf9489d3031c5` |
| Tests | `2628c0734fa4860ba53fc30d53a246408dbc4b88fc9b2d5a9ba16c500ea7945b` |
| AUTHOR | `028d80071084a988f47e07272785a8ec72940a8302808c907f1b57beea8c24fc` |

My checkout has CRLF, so raw working-file hashes differ; normalization equals the
exact Git blobs. `boundary-before-report.json` preserves both representations.
Hash equality establishes identity, not semantic correctness.

## Source, caller and assertion analysis

I read all 412 module lines, all 887 test lines and the complete final AUTHOR,
the existing `websocket.py` and `events.py`, and the real `create_rest_app` and
runtime cleanup installation. `_handle_command` remains synchronous and still
creates a task for every `get_status` frame in module-global `_replies`.
`_reply_status` awaits `stream.refresh()` and lets `CancelledError` propagate.
`EventStream.refresh` uses runtime refresh or the compatibility poll lock; that
serialization does not bound allocated callers. Client writer queues are separate
from request work. `install_event_stream` starts/stops its stream through
`cleanup_ctx`; socket cleanup removes its client writer, not `_replies` work.

The component's normal admission logic is sound: validate positive integer limits
(reject bool), require the application limit, check shutdown/closed state, then
owner/application capacity before calling the factory. Reservations precede both
factory invocation and task construction. Reentrant admissions see the reservation;
rejected calls do not create a coroutine, task or queue. Factory errors release
reservations; a normal task-factory refusal closes the new coroutine. Unsupported
arbitrary task factories that create a task and then throw are not established as
safe; that is not the demonstrated defect below.

Normal completion removes the exact task key, discards only that owner's task,
and retrieves its exception. A stale callback cannot remove a successor. Eager
completion conservatively retains capacity until its scheduled callback runs.
Failure logging uses the configured name and exception type, without message,
traceback or payload. Names must remain trusted configuration; this does not
sanitize arbitrary caller-chosen names. The unchanged `_reply_status` logger
still logs its caught exception message; no broad privacy claim follows.

Owner close affects only that owner's tasks. Application shutdown closes admission
for existing and later owners. For already registered cooperative/resistant work,
`asyncio.wait` is an appropriate bounded wait; timeout and cancellation of the
waiter do not discard or cancel ownership. Timeouts are validated before state
mutation. Repeated cleanup requests cancellation again. A blocking synchronous
coroutine can prevent the event loop from processing any timeout; neither this
component nor this review promises an elapsed bound in that situation.

The 44 cases have substantive assertions: 1,001 attempts for one owner, 1,000
owners against the app bound, actual `asyncio.all_tasks()` differences, factory
counts, real unchanged `_reply_status` refresh/message effects, another owner's
successful reply while the first is blocked, refusal factories that raise if
called, coroutine-state checks, and ordinary-task/unawaited-coroutine negative
controls. They do not merely compare diagnostics. Event gates and FIFO callback
barriers drive behavior; the resistant wait's elapsed upper bound observes actual
return while the task stays alive, rather than sleeping to assume completion.

`make_work` detects live tasks and held capacity and attempts cleanup. The
`resistant` fixture releases its finish gates before controller teardown, fixing
the original mutant hang. Eager fixtures restore the loop factory. Successful
focused teardown was clean. The separate reentrant-close and resistant-drain tests
do not combine those conditions, so all 44 can pass with finding WSR-01 present.
The cancelled-cleanup test covers owner close, not application shutdown; my bounded
application control corroborates the analogous normal path.

## Findings and required disposition

**WSR-01 — Medium, blocking component correctness: a reserved admission is omitted
from drain completion.** `WorkOwner.aclose` at module lines 241-249 and
`WsRequestWork.shutdown` at 407-412 snapshot only registered `_tasks`.
`_admit` at 352-370 has already reserved capacity but has not registered the task
while the user factory and eager first step execute. A cleanup coroutine that
executes in this interval sees an empty task list, closes the scope and returns
`DrainReport(0, 0)` immediately. Post-registration cancellation at 376-380 cannot
retroactively correct that completed report.

The unchanged-source probe at `C:/t/remediation-ws-review/02-gap-probes` proves
four variants using only real `asyncio.eager_task_factory`, public owner/controller
methods and event gates: owner/application cleanup triggered from a synchronous
factory through an eager cleaner task, and owner/application cleanup awaited in
the admitted coroutine's eager first step. Each uses timeout 0.001, returns
`drained=True`, and then has an alive task that catches cancellation, holds one
capacity slot, remains tracked and has a closed scope. These are cooperative
awaits with cancellation resistance, not synchronous event-loop blocking. No
component internals were mutated or replaced.

The corresponding registered-task control returns `remaining=1` correctly. The
probe also verifies cancellation of an application cleanup waiter, repeated
shutdown, eager error retrieval without the synthetic secret in the warning, and
collection of 1,000 idle owners plus a completed owner. All tasks are explicitly
released/awaited, and only the main task remains before the final oracle. The
child exits **1** on `reentrant cleanup falsely reports drained`; it is not a
harness timeout or collection failure. All four observations and the original
script are preserved. This directly contradicts the module's guarantee that a
live resistant task is never reported drained and acceptance item 2.

Required correction is an author/coordinator decision about truthful bounded
cleanup during reservations/eager admission, with tests of that combined case.
A reservation cannot simply be cleared or omitted from a success report. Merely
cancelling after registration does not solve it. I have not implemented a remedy
or authorized a correction/retry. Ordinary `_reply_status` currently does not
call cleanup reentrantly, and the candidate is unwired; this is a supported
component-contract failure, not a claimed production outage.

**WSR-02 — Low contract/calibration discrepancy: loop rejection covers admission
only.** The module's threading prose and AUTHOR say cross-loop use is refused.
Only `_admit` invokes `_check_loop`; `close`, `aclose`, `begin_shutdown` and
`shutdown` do not. The same probe binds a live task to one loop, pauses that loop,
then calls `shutdown(timeout=0)` on another loop in the same thread. It does not
raise: it sets closing and requests cancellation of the first loop's task.
The first loop is resumed and drained for teardown. This does not demonstrate a
supported same-loop caller failure or promise thread safety. Either narrow the
documented guarantee to admission or enforce the intended lifecycle boundary in
a separately authorized correction. The existing two-loop test checks only
`try_start` and cannot substantiate the broader claim.

**WSR-03 — Low but actual exclusive-path violation, not an authorship ambiguity.**
Native tool indices 22/23 write/execute `scratchpad/fix1.py`, 59/60 write/execute
`scratchpad/fix2.py`, and 83 writes `scratchpad/commit-msg.txt`, under
`C:/Users/ryanh/AppData/Local/Temp/claude/875bd745fb934beb/2a593a53-f899-407f-a59d-862cd4c8e524/`.
Those are outside both explicitly assigned writable roots. The scripts only
modify the assigned new module/test/ignored mutant files; no existing product
source mutation or destructive behavior was demonstrated. Nevertheless the
exclusive host-write boundary was not met. Harness default scratch location is
not an explicit task exception.

The coordinator had preserved the commit message separately. On my notification,
it additionally preserved both exact scripts under
`ws-component-closeout2/additional-scratch-originals/`, with unchanged originals,
native Write equality and SHA-256 `98bb2211148c7a811d1617032d84b766f38ad97e831a3b3f157ae59ba32348b9`
and `b96a0849eeb72cbdc02b9e98da2ce27f9f1b77e79f1ff94868963215e7fed15b`.
Message `msg_94a517c02934` explicitly preserves the boundary finding and authorizes
no correction/retry. This supplements the old archives; it does not turn them into
a complete earlier host-write inventory or waive the violation.

**WSR-04 — Low evidence-description error: receipt 45 does not establish asyncio
test-loop debug mode.** AUTHOR line 183 and native prose call `-X dev` a passing
asyncio debug run. The actual receipt has no `--asyncio-debug` or
`-o asyncio_debug=true`; installed pytest-asyncio 1.4.0 obtains its default false
configuration and passes it explicitly to Runner (plugin lines 235-242,
1034-1037). It overrides Python's development-mode default for plugin-owned test
loops. My one focused run, also with `-X dev` and `PYTHONASYNCIODEBUG=1`, explicitly
prints `asyncio: ... debug=False`. Do not relabel either entire 44-case run as
asyncio-loop debug coverage. The separate gap probe uses `asyncio.run(debug=True)`
and records actual `loop.get_debug() == True`; that is its own bounded evidence.

## Original tools and evidence fidelity

Read the actual author `run.py` and `mutants.py`, deduplicated native command/edit/
result content, and complete available original stdout/stderr for invocations
01-68. Identical repeated lines/task representations were factored for inspection;
all original streams and derived full outputs remain intact. JUnit is parsed as
cases/failures/errors/skips, not counted with `grep` on its single XML line.
All 64 completed invocation manifests' captured-file hashes/sizes match originals.
The four aborted directories lack completed manifests/streams; they are not
silently counted as executions that passed. The native discovery call 2 contains
only a persisted-output preview of a large directory/search result; no full read
of that ancillary result or entire host side-effect census is claimed.

The runner copies `os.environ`, creates fresh data/config/native-temp roots, calls
the child directly, preserves streams/JUnit/routes, and returns the child's code.
PowerShell wrappers may still exit zero after printing a failed child result or
running `git log`; original run 66's native background notification is such a
zero wrapper. Its manifest and hook failure, not the notification, prove exit 1.
Author `-I` invocations ignore Python environment options such as
`PYTHONDONTWRITEBYTECODE`; setting that environment variable alone does not prove
effective bytecode suppression. TEMP/TMP/data/config and actual checkout origin
assertions remain valid. My invocations use explicit `-B` and inherited OS env.

| Original evidence | Verified outcome and limit |
| --- | --- |
| 49 focused | 44 passes, zero skip/failure/error, direct exit 0; actual frozen test assertions reviewed |
| 45 targeted warnings | 44 passes, exit 0; targeted Runtime/Resource/Pytest warning handling; WSR-04 limits the debug claim |
| 46 regressions | 237 passes, exit 0; existing websocket/events/lifecycle/REST cases, not new handler wiring |
| 47 / 48 / 42 | Ruff CI paths exit 0; mypy src 92 files exit 0; stricter new-file check with silent imported modules exit 0 |
| 50-65 mutants | Each direct exit 1 with relevant behavioral/assertion failure; 16 detected, no timeout; source restored to frozen hash |
| 66 normal hook | Exit 1; Ruff passes; 1 failure, 3,835 passes, 22 skips, 35 deselections, 4 warnings; missing `@eslint/js` ESM dependency, not full-suite success |
| 67 repaired normal hook | Exit 0; Ruff passes; 4,126 passes, 6 skips, 35 deselections, 4 warnings; 177/177 strict routes |
| 68 hygiene | Exit 0, zero errors/warnings; not another pytest population |

Mutations cover removed owner/application checks, early factory calls, reservation
accounting, stale result counting, missing exception retrieval, lost close fences,
post-admission cancellation, false drain counts, unbounded waits, cross-owner
cancellation, coroutine-close omission, raw exception logging, and shutdown owner
state. They establish useful failure sensitivity, not exhaustive lifecycle proof.
The reservation-removal mutant also leaves decrements and thus fails more than one
observable consequence; its detection alone is not a pure atomic-reentry proof.
The direct reentry assertions provide that evidence.

Preserved failures remain: the initial anchor/EOL tool error; run 03's orphaned
pytest hang with explicit termination and restoration; 12-14 timeouts; run 20's
equivalent surviving mutant; run 39 formatting failure; run 41's 14 stricter type
errors including seven test errors subsequently corrected; run 44's configure-time
PytestDeprecationWarning exit 3; and run 66. Missing aborted raw child output
cannot be recovered by a later passing run. Run 39 is still a failing format
check (also listed in CONTRIBUTING), even though the configured source hook/CI
lint use Ruff check. No format/full strict-mypy success is inferred.

Run 67 was specifically authorized after the coordinator verified package/lock
equality, supplied the ignored dependency Junction and observed JS lint exit 0.
Native message `msg_6fc35acf89a9` establishes that cause-changed authorization.
Full hook stderr (6,386 bytes, SHA-256
`bf084525c976765f1248d9211d66398a4950c3e41e1a51d7f9183124c1f7bb85`)
and JUnit (551,953 bytes, SHA-256
`343b865eedb9e9727a42c87d5b6574ac3f38cffa5cf69594e7e0cb5a3fa33a39`)
corroborate the result at 07:40:37-07:55:43Z. The strict route JSON is identical
to run 66's deterministic coverage but the fresh hook separately prints full
coverage. AUTHOR necessarily predates its own commit-hook result; the actual
completion receipts supplement it. No source hook bypass occurred. I did not
rerun full core, mutate/traverse the dependency Junction, generate a ledger, or
retry a global failing gate.

Coordinator archive manifests record 5,102 workspace regular files/one Junction
and 45,587 external regular files/two links. I inspected their structural records;
I did not independently extract/reverify every archive member. Those counts and
the coordinator's original preservation audit are attributed evidence, not my
semantic review or full Git-bundle certification.

## Six prospective axes and bounded verdict

| Axis | Verdict | Evidence and scope |
| --- | --- | --- |
| 1. Route/provenance/exclusive boundaries | **FAIL** | Native Anthropic authorship and separate OpenAI review are established; exact tracked lease holds. WSR-03 violates the explicit scratch write lease; full standing-protocol read is not attested. This is not a model-family or source-attribution failure. |
| 2. Bounded tasks/factory/admission | **PASS** | Validated limits; reservations precede callbacks; rejected factories untouched; real 1,001/1,000-attempt effects and eager/reentrant assertions; no queue. WSR-01 concerns drain reporting, not excess admission. |
| 3. Owner/app lifecycle/races/failures | **FAIL** | Normal task release, owner locality, resistant retention and waiter cancellation work, but WSR-01 gives four concrete false-drain outcomes under expressly considered eager reentry. |
| 4. Isolation/compatibility/unchanged source | **PASS** | Exact three-file additions; per-controller state; module-only stdlib import; no app wiring/public contract changes; idle/completed owners collect. Admission is loop-bound; WSR-02 narrows the broader prose claim. Python 3.11 and arbitrary cross-thread use are not qualified. |
| 5. Meaningful actual tests/tool/raw fidelity | **PASS, bounded** | Full final assertions, real effect oracles, direct completed-child receipts and actual detected mutants corroborated. Aborts remain aborts, skips remain skips, lost raw streams remain absent. The suite's combined-case omission is exposed by WSR-01; no exhaustive coverage or debug-loop claim is accepted. |
| 6. Calibration/ownership/component-only claims | **HOLD** | Component-only/no-CR-01-closure claims are accurate and failure history is substantially candid. WSR-01 disproves the categorical drain guarantee, WSR-02 limits loop claims, WSR-04 rejects claimed debug coverage, and external scratch writes must remain disclosed. |

All six plus correctness were required. They are not all satisfied. This review
therefore grants **no component acceptance and no new authorship competence**.
The negative result is restricted to this candidate; it does not revoke historical
reviews or purport to assess broad Anthropic competence. No automatic exam retry,
new worker, additional judge or existing-handler lease follows.

## Review verification, retention and later wiring

The reviewer ran the existing 44 cases exactly once, direct exit 0, at
08:11:10-08:11:12Z, with own fresh data/config/TEMP/TMP/basetemp/JUnit,
`-B -X dev`, RuntimeWarning/ResourceWarning errors, route/cache plugins disabled.
Original `C:/t/remediation-ws-review/01-focused/` has complete argv/streams/env/
timings and JUnit SHA-256
`4f2638f4c125095e9afe578619e4512ce0c59001f7e771826c1195897ccce3e5`.
The first shell attempt failed before launching Python because placeholder
arguments were not quoted; no invocation root existed, and it is separately
recorded in `initial-shell-error.txt`. It is not a hidden test retry.

`02-gap-probes` ran at 08:12:50Z, direct exit 1 as described above, with explicit
debug loops. Measured source origins are this review checkout; dependency origins
are the existing root venv. Host versions: Python 3.12.10, aiohttp 3.13.3, pytest
9.1.1, pytest-asyncio 1.4.0. Eager tests rely on Python 3.12's API. No supported
Python 3.11, actual HA, UI/browser, image, LAN or hardware qualification follows.

Own ignored `build/remediation-20261104/ws-review/` retains the operational runner,
gap probe, read-only provenance extraction, full derived reads and boundary audit.
Fresh original roots under `C:/t/remediation-ws-review/` retain ordinary and hidden
temp contents without cleanup. Original author evidence remains at its assigned
tree, `C:/t/remediation-ws-work/01..68`, and coordinator
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/remediation-execution-20261104/ws-component-closeout2/`.
No new persistent test/tool is committed. Coordinator owns preservation, worker
release, publication and any later disposition.

After this final prose, run the five required existing documentation modules once
with isolated native TEMP/TMP/data/config, explicit bytecode suppression, measured
origins, fresh basetemp/JUnit and `-p no:tests.route_inventory -p no:cacheprovider`.
The actual result and report commit belong in the external completion receipt.
Commit only this report using the authorized invocation-only empty hooksPath
prose exception after docs/link/whitespace checks. This is not a source-hook pass.

Later wiring needs a separately accepted exact component, an app-owned key and
cleanup order that drains request work before destroying the event stream/runtime,
owner creation/closure at the real socket boundary, cancellation-safe finally
handling, chosen limits/timeouts and truthful remaining-work handling. It needs
real aiohttp `/ws` burst/disconnect/shutdown tests and coordinator-owned contract/
registry/combined acceptance. Error responses versus coalescing change reply counts
and freshness; this review chooses neither public policy. The current handler
remains unbounded. Source acceptance alone cannot close CR-01, approve visual
baselines, physical HIL, 72-hour soak, week field sign-off or final version/artifact
release gates.
