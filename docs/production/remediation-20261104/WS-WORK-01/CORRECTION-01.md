# WS-WORK-01 CORRECTION-01: original-author product correction (WS-C01)

**Status: corrected candidate component, not wired, CR-01 not closed, not accepted.**
This is a bounded product correction by the original author. It is **not** an exam, a
qualification attempt or a retry of the failed assessment. **Original first-authorship
remains NOT_GRANTED.** The original six-axis record stays as recorded by the review:
route/provenance FAIL, bounded admission PASS, lifecycle FAIL, isolation PASS, tests/tools
PASS-bounded, calibration HOLD. WSR-03 remains a historical failure. A later independent
exact-commit review (WS-R01, OpenAI Astra/high, reserved and not launched; no verified
backup reviewer) can at most grant source acceptance for the corrected component. It cannot
grant authorship competence, an existing-API lease or wiring. `src/rest_api/websocket.py` is
unchanged and still starts one unbounded `ws_get_status` task per frame.

The original [AUTHOR.md](AUTHOR.md), the independent `REVIEW.md` (on branch
`remediation/ws-work-01-review`), the original receipts 01–68, the review receipts and every
earlier failed, aborted or lost run remain unchanged originals. Original normal hook 67 (green)
and 66 (failed, missing `@eslint/js`) are history; this correction did not re-run them.

## Authority, route and provenance

| Item | Value |
| --- | --- |
| Task / Dispatch | `task_92d47e338d62` / `ctx_15d1617958e2` (Orca worker; coordinator `term_6ed8131e-…`) |
| Author | Native Anthropic `claude-opus-5-5`, the original WS component author. High effort is the assigned launch setting; the native session does not expose per-turn effort to me. No helpers, subagents, teams, plugins, MCP, nesting or model switch |
| Plan authority | FINAL_PACKET v1 of `remediation-recovery-20261104`, read at the entry-pinned `wp-runtime-completion` commit `ff27f7a8b157b9255acab5f76db931d2970a52e0`. Its raw blob (LF) SHA-256 is `f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e`, equal to the assigned digest. `CONSENSUS.json` at the same commit records ADOPTED: three families ACCEPTED that same hash. Applied: D1 (bounded correction), D2 (drain semantics), D3 (loop boundary), task `WS-C01` and its acceptance list |
| Exact base | `15c069bdeb3a9ace37bf68033812ff72659bfbd1` (worktree `wp-remediation-ws-work-c01`, branch `remediation/ws-work-c01`) |
| Tracked lease | `src/rest_api/ws_request_work.py`, `tests/test_ws_request_work.py` (additive), this new file. Nothing else tracked is changed |
| Commit | the commit adding this file; its hash and hook receipt are reported in `worker_done` (a file cannot name its own commit or hook result) |

Read in full for this correction: the module (412 lines at base), all 887 original test lines,
AUTHOR.md, REVIEW.md, the reviewer probe (`probe.py`) and its original receipt
`C:/t/remediation-ws-review/02-gap-probes`, `websocket.py` (all 124 lines), plus the caller
lifecycle in `app.py` (`create_rest_app`, `RestApiServer.stop`) and `events.py`
(`EventStream.start/stop`, `install_event_stream`). I also read the FINAL_PACKET decisions,
the WS tasks and the async review assessment, and pytest-asyncio 1.4.0's debug option/runner
code. None of those callers was changed. The component is still not imported by product code.

## Finding dispositions

| Finding | Disposition |
| --- | --- |
| **WSR-01** (Medium, false drain during a reservation) | **Corrected (D2).** A cleanup now counts the scope's in-progress admissions (reservations) in `remaining`. If it runs inside an admission of its scope, or from one of the scope's own tasks, it returns at once without awaiting. All four judge shapes now report `DrainReport(requested=0, remaining=1)`, and they are committed regression cases |
| **WSR-02** (Low, loop check covered admission only) | **Corrected (D3), not narrowed.** `close`, `aclose`, `begin_shutdown` and `shutdown` refuse a foreign loop or a missing running loop on a bound controller *before* any fence, cancellation or count changes. Lifecycle never binds. Unbound sync close/shutdown work with or without a loop and do close their fence. No thread-safety claim |
| **WSR-03** (Low, writes outside the lease) | **Historical failure, unchanged.** It is not curable by this correction. My own write audit for this correction is below |
| **WSR-04** (Low, receipt 45 called asyncio debug) | **Corrected here only.** Original receipt 45 (`-X dev`) was **not** pytest-asyncio test-loop debug. pytest-asyncio passes its own `debug=False` to the runner. AUTHOR.md is not edited. This correction uses `--asyncio-debug` and records `loop.get_debug()` per test in JUnit (see Evidence) |

## Mechanism and invariants

`DrainReport` keeps its two fields. Their meaning is **explicitly changed going forward**
(the old docstring said `remaining` meant "of those" requested tasks):

- `requested`: attached live tasks of the scope for which this call's `Task.cancel()`
  took effect. A done-but-not-yet-released task is excluded (`cancel()` returns `False`).
  A reservation is never counted as cancelled.
- `remaining`: all unfinished admitted work of the scope at return. That is attached tasks
  not done, plus in-progress admissions, including the calling task when it belongs to the
  scope. It may exceed `requested`. `drained` is true iff `remaining == 0`.

`_drain` (module-private) runs after timeout validation, the lifecycle loop check and the
fence/cancel step:

1. Return at once, with a recount, when `timeout == 0`, when nothing attached is pending,
   or when the scope has a reservation. `_admit` is a plain `def` that never awaits, so an
   outstanding reservation means this cleanup is running inside that admission (a factory
   or an eager first step), and the admission cannot finish before the cleanup returns.
2. Return at once when the current task is one of the scope's pending tasks (self
   dependency: it cannot finish while waiting for itself).
3. Otherwise, one `asyncio.wait(pending, timeout)`, then a final recount of reservations plus
   attached tasks that are not done.

No new queue, watcher, notification state machine or detached task is created. `asyncio.wait`
removes its own callbacks. Owner scope uses only the owner's reservations; application scope
uses the controller's. So an owner A cleanup that runs inside owner B's admission still waits
for A's work (tested). These are unchanged: reserve-before-factory; registration while the
reservation holds the slot (the count never dips or double-counts across reserve→task); the
post-admission cancel when the scope closed during admission; `_release` removing exactly its
own task, ignoring stale calls and retrieving exceptions; resistant tasks staying referenced
and counted; repeated cleanup cancelling again; timeout validation before any change; owner
locality; rejected factories never called; all `RejectReason` values and their precedence.

Event loops (D3): only `try_start` binds, including a rejected one (existing behaviour, now
tested). `_check_lifecycle_loop` returns early on an unbound controller, never assigns
`_loop`, and raises `RuntimeError` ("different event loop" or "no event loop is running")
on a bound one.

## New regression cases (29, additive; original 44 unchanged)

The original 887 lines are a byte-identical prefix of the new test file (`git diff --numstat`:
615 added, 0 deleted). New helpers are `AdmissionProbe` (test-owned `factory_entered`/
`factory_returned`/`body_entered`/`release`/`cancel_seen` gates and the body's own task), the
`probes` fixture (releases and awaits every body even after a failure; runs before
`make_work`'s leak check) and `debug_checked`.

- `test_cleanup_from_an_eager_cleaner_spawned_by_the_factory_is_not_drained` (owner/application ×
  resistant/cooperative × timeout 0/0.001; real `asyncio.eager_task_factory`). In the factory
  window the body coroutine does not exist yet (`body_entered` False, 1 reserved, 0 tracked).
  The cleaner completes inside the factory with `(0, 1)`. After admission the real task is
  alive with `cancelling() == 1`, capacity is held and the bystander gets `APPLICATION_BUSY`
  or `SHUTTING_DOWN`. A later drain is truthful: resistant `(1, 1)`, then release and await;
  cooperative `(1, 0)`. The final drain is `(0, 0)`.
- `test_cleanup_awaited_in_the_eager_first_step_is_not_drained` (same matrix). The task exists
  and is the current task, but it is not attached. The report is `(0, 1)`, obtained inside
  the admission, and later drains are truthful.
- `test_cleanup_inside_an_admission_does_not_wait_for_attached_siblings`: an eager-step cleanup
  with a resistant sibling attached returns `(1, 2)` without suspending (a `call_soon` marker
  has not run).
- `test_a_task_cleaning_its_own_scope_returns_at_once_and_counts_itself`: owner `(2, 2)`,
  application `(3, 3)`. There is no suspension, the caller is then cancelled, and the other
  owner is untouched at owner scope.
- `test_nested_reentrant_admissions_are_each_counted_exactly`: three nested reservations, with
  a raising nested factory, a task-factory refusal (its coroutine is `CORO_CLOSED`), an eager
  task that completes in its step, a rejected uncalled factory and a stale `_release` in
  between. `(owner, application, attached)` counts are asserted at all ten boundaries. The
  cleaner reports owner `(0, 3)` / application `(1, 4)`, the second drain `(3, 3)` / `(4, 4)`,
  and after release `(0, 0)`.
- `test_cleanup_of_another_owner_inside_an_admission_still_waits_for_it`: other-owner progress
  gives `(1, 0)`, and the admitting owner is unaffected.
- `test_cancelling_a_cleanup_waiter_keeps_resistant_work_tracked` (both scopes).
- `test_bound_lifecycle_refuses_a_foreign_or_missing_loop_before_changing_state`: no running
  loop, a foreign loop for all four lifecycle calls plus `try_start`, timeout validation first.
  `closed`/`closing`/`cancelling()`/`active_count` stay unchanged, then a home-loop shutdown
  gives `(1, 0)`.
- `test_unbound_owner_close_closes_the_fence_without_binding`,
  `test_unbound_begin_shutdown_closes_admission_without_binding`,
  `test_a_rejected_admission_binds_the_loop_too`.

Every new async test asserts `loop.get_debug()` equals pytest-asyncio's configured value and
records both values in JUnit. The sync tests assert `get_debug()` inside `asyncio.run(..., debug=True)`.

## Evidence (ignored or outside the repository; originals preserved)

Toolchain: root `.venv` (`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv`):
Python 3.12.10, pytest 9.1.1, pytest-asyncio 1.4.0, aiohttp 3.13.3. Imports of product code and
tests came from this checkout: `tests/conftest.py` puts this `src` first, the unchanged
`test_imports_resolve_to_this_checkout` passed, and the probe printed `origins` under
`wp-remediation-ws-work-c01/src`. Every invocation went through
`build/remediation-recovery-20261104/ws-c01/run.py`, adapted with attribution from the
original WS-WORK-01 runner (sha256 `d29b917a…b3cd`). It copies the Windows OS environment and
gives each run a fresh, never reused or deleted root `C:/t/remediation-recovery/ws-c01/NN-label/`
with its own native TEMP/TMP/TMPDIR, data and config, plus `{T}` basetemp/JUnit. It runs the
child directly (no shell) with explicit `-B` and returns the child's exit code. Each root has
`manifest.json` (argv, cwd, UTC times, duration, exit, file hashes, safe env), raw stdout/stderr,
JUnit and the untouched native temp. Copies are in `build/remediation-recovery-20261104/ws-c01/receipts/`.

Frozen candidate (canonical LF): module sha256 `2352c7d66e281599659bfbdb81c14dab12455f64be6a04fcd2260dc09075e266`
(506 lines), tests sha256 `69ac419d6513888831239816e5a7c2dd20e6a5654bafe7d506e3719fdb619776`
(1,502 lines).

| Run | Command (abridged) | Exit | Result |
| --- | --- | --- | --- |
| 24-final-focused-debug | `pytest tests/test_ws_request_work.py -vv --asyncio-debug -W error::RuntimeWarning/ResourceWarning/PytestUnraisable…/PytestUnhandledThread…` | 0 | 73 passed (44 original + 29 new). Header `asyncio: mode=Mode.AUTO, debug=True`; JUnit has 25 × `asyncio_loop_debug=True`; JUnit `4fe117e7…7fbdc9` |
| 25-final-focused-default-config | same file, repository configuration | 0 | 73 passed; JUnit records 25 × `asyncio_loop_debug=False` (configured false), `686a4ae5…20e4` |
| 30-final-regress-ws-events-server-runtime | `test_hub_events`, `test_runtime_websocket_sync_r3e`, `test_runtime_shutdown_r1`, `test_runtime_composition_r1`, `test_runtime_integration_lifecycle_r5`, `sim/test_sim_ws_contract`, `sim/test_sim_status_broadcast`, `test_rest_api`, this file | 0 | 320 passed; JUnit `981e0225…ad62d` |
| 26-final-ruff-ci-paths | `ruff check src tests custom_components tools run.py run_server.py` | 0 | All checks passed |
| 27-final-mypy-src | `mypy src/` (CI job) | 0 | no issues, 92 files |
| 28-final-mypy-new-strict | `mypy --check-untyped-defs --warn-unused-ignores --follow-imports=silent` (both files) | 0 | no issues |
| 29-final-judge-probe-control | attributed control copy of the reviewer probe, `-X dev`, `asyncio.run(debug=True)` | 0 | four judge shapes `DrainReport(requested=0, remaining=1)`, `truthful_drain: true`, `loop_debug: true`; cross-loop shutdown `rejected: true, closing: false, cancellation_requests: 0` |

**Selective reversions** (in-memory pytest plugin `mutants/ws_c01_mutant_plugin.py`: mutated
text is exec'd into the already-imported checkout module object; the source file is never
written, and its sha256 is printed before and after each session, unchanged in every run).
Each run is the whole 73-case file with `--asyncio-debug`. All exited 1 and none hung.

| Run | Reversion | Detected by (intended reason) |
| --- | --- | --- |
| 06 | **whole pre-correction module** (blob `3bc116d8…`) | 24 new fail; 44 original + 5 behaviour-preserving new pass. Failures: false `remaining=0` in all 16 judge-shape cases, sibling wait, self-wait `CancelledError`, nested `(0,0)`, missing loop refusals |
| 07 | `remaining` omits reservations | 20 (all judge shapes, siblings, nested) |
| 08 | no reservation short-circuit | siblings ×2, nested[application] |
| 09 | no self-dependency check | self-cleanup ×2 |
| 10 | owner drain uses controller reservations | other-owner progress |
| 11 | `begin_shutdown` without loop check | bound-lifecycle, rejected-binds |
| 12 | `close` mutates before check | bound-lifecycle |
| 13 | `shutdown` mutates before check | bound-lifecycle, rejected-binds |
| 14 | lifecycle binds an unbound controller | both unbound tests |
| 15 | unbound `close` is a no-op | unbound owner close, rejected-binds |
| 16 | bound controller allows no running loop | bound-lifecycle, rejected-binds |
| 17 | `requested` counts done tasks | original `test_close_racing…`, nested ×2 |
| 18 | `remaining` counts done-unreleased tasks | original `test_close_racing…`, nested ×2 |

These show failure sensitivity for the corrected invariants. They do not prove exhaustive
lifecycle coverage.

**Iterations and failures (kept as originals, not hidden):**

- 01-existing44-iter1: exit 0, 44 passed on the corrected module before any test was added.
- **02-judge-probe-copy-corrected: ABORTED.** The unmodified probe copy hung in its own
  `cross_loop` teardown: it awaits a task that the now-refused foreign-loop shutdown no longer
  cancels. After about 134 s I killed exactly that child and its venv launcher. The manifest
  records exit 4294967295, stdout is empty (block-buffered) and stderr is 60 bytes. Note:
  `build/…/ws-c01/notes/02-ABORTED.md`. 03 and 29 use the control copy, whose only change is
  an explicit bounded release on its own loop, run with `-u`.
- **04-focused-iter1-debug: exit 1** (1 failed, 72 passed). These were my own test defects:
  the owner-scope waiter test used `application_limit=2`, so the bystander was legitimately
  admitted (`never_call` raised). `record_property` also warned under xunit2. Fixed: limit 1,
  `user_properties` used directly. 05: 73 passed.
- **21-mypy-new-strict-iter1: exit 1.** Six unused `type: ignore` comments in new tests were
  removed. 22: exit 0.
- 19/20/23 were earlier ruff/mypy-src/regression runs (all exit 0), superseded by 26/27/30 on
  the frozen bytes.
- Removing those comments with `sed -i` normalized the test file's working-tree line endings
  to LF. The Git blob is LF either way, and the prefix/additive check above was run afterwards.

## Write audit for this correction

All authored files are in the tracked lease, in `build/remediation-recovery-20261104/ws-c01/**`
(runner, receipts, controls, mutants, notes, entry packet copies, commit message) or in
`C:/t/remediation-recovery/ws-c01/**`. No script, message body or receipt was written under the
harness scratchpad or `/tmp`. Disclosed side effects, all kept as they are:

- Harness automatic artifacts I did not author: a background-command output file
  `C:/Users/ryanh/AppData/Local/Temp/claude/9f7c7235537d150f/48219381-d4ac-4e1a-8cb1-97fdf25364aa/tasks/bzh3zo8z3.output`
  (from aborted run 02), the shell's cwd marker files, and a persisted tool-output preview of
  my full read of the original test file under the Claude profile `tool-results` directory.
  The originals are untouched, and nothing was reconstructed from previews.
- Ignored tool side effects inside this worktree: `.mypy_cache/`, `.ruff_cache/`,
  `route-coverage.json` (route-inventory plugin), and
  `src/rest_api/__pycache__/ws_request_work.cpython-312.pyc`. The `.pyc` is written by the
  unchanged original `test_loading_the_module_alone_has_no_side_effects`: its `python -I`
  subprocess ignores `PYTHONDONTWRITEBYTECODE`. That test was not modified (lease).
- Untouched: the coordinator-supplied ignored `node_modules` junction (not traversed) and
  `.claude/settings.local.json`.

## Limitations and honest scope

- Not wired. The `/ws` handler remains unbounded and CR-01 stays open. No aiohttp/socket test
  was added, and wiring stays HELD (`WS-WIRING`).
- No thread-safety. A controller bound to a loop that has since closed cannot be shut down
  from another loop (by design: one controller per app loop). A rejected first `try_start`
  binds too.
- A synchronously blocking coroutine can still defeat any elapsed bound. A
  `KeyboardInterrupt`/`SystemExit` raised inside an eager first step is still not addressed.
- Verified on CPython 3.12 only (eager tasks need 3.12). No Python 3.11, HA, UI, LAN,
  hardware or soak evidence.
- Default timeouts are unchanged proposals for the wiring package.

## Commit-time gate

The final source commit runs the normal configured `.githooks/pre-commit` (ruff + `pytest tests/
--ignore=tests/ha --ignore=tests/uc -x`) through `run.py`. It sets `ROUTE_COVERAGE_STRICT=1`,
sends JUnit/basetemp into a fresh root via `PYTEST_ADDOPTS`, and has no hook bypass. Its
label, exit, counts, strict route result and hashes appear in `worker_done` and in
`build/remediation-recovery-20261104/ws-c01/completion.json`, not here. A hook failure means
no commit. No feature registry, ledger generation, global `tools.validate` gate, canonical
evidence admission, physical/LAN/owner-HA/hardware/soak or release work was run.
