# WS-WORK-01: author report (CR-01 internal component, candidate only)

**Status: candidate component, not wired, CR-01 not closed.** This change adds a new
internal module and its tests. `src/rest_api/websocket.py` is unchanged and still starts
one `ws_get_status` task per frame with no admission bound. Nothing in the app uses the
new module yet. Neither authorship competence nor component acceptance exists until a
qualified independent OpenAI Astra/high review of the exact commit passes.

## Route and provenance

| Item | Value |
| --- | --- |
| Task / Dispatch | `task_38756b76bd12` / `ctx_14a660b697ab` (genuine Orca worker; coordinator `term_6ed8131e-…`) |
| Author | Native Anthropic `claude-opus-5-5`, high effort; no helpers, subagents, teams, plugins, MCP or nesting |
| Exact base | `460a190575e905f8350c454e63c4d570c8b560fa` (branch `remediation/ws-work-01`) |
| Tracked changes | three NEW files only: `src/rest_api/ws_request_work.py`, `tests/test_ws_request_work.py`, this report |
| Commit | the commit that adds these files; its hash is reported in `worker_done` (a file cannot name its own commit) |
| Authorship | All three files are new Anthropic authorship. No existing (OpenAI-attributed or other) source was modified, moved or relabelled |

Read (not changed): `src/rest_api/websocket.py`, `events.py`, `app.py`
(`create_rest_app`, `install_event_stream`), `runtime.py` (`cleanup_ctx` pattern), `__init__.py`,
`docs/api/websocket.schema.json` (`error` event), `docs/audits/COMPREHENSIVE_PROJECT_REVIEW_20261104.md`
(CR-01), `tests/sim/test_sim_ws_contract.py`, `tests/test_hub_events.py`, `tests/route_inventory.py`,
`tests/conftest.py`, `.githooks/pre-commit`, `pyproject.toml`.

## Problem this component addresses (CR-01)

`_handle_command` is a synchronous function run in the event loop for every TEXT frame.
For `get_status` it calls `create_task(_reply_status(stream, ws))` and parks the task in the
module-global `_replies` set. That set keeps tasks alive. It is not an admission limit,
and socket cleanup neither owns nor cancels these tasks. The review's probe saw 1,000 frames
with a pending refresh create 1,000 pending tasks. There is no claim of a production outage
or a memory threshold. This component supplies the missing primitive. It does not fix the
handler.

## Internal API (`rest_api.ws_request_work`)

```python
work = WsRequestWork(application_limit=N, owner_limit=1, name="ws_get_status")  # one per app
owner = work.open_owner()                      # one per WebSocket connection; never raises
result = owner.try_start(lambda: coro_fn(...))  # sync, never awaits
#   -> asyncio.Task            admitted (factory called exactly once)
#   -> RejectReason.OWNER_BUSY | APPLICATION_BUSY | OWNER_CLOSED | SHUTTING_DOWN  (factory NOT called)
owner.close()                                  # sync, idempotent: stop admitting, cancel this owner's tasks
report = await owner.aclose(timeout=1.0)       # close() + bounded wait for THIS owner only
work.begin_shutdown()                          # sync, idempotent: stop all admission, cancel all tasks
report = await work.shutdown(timeout=5.0)      # begin_shutdown() + bounded wait for all
report.requested, report.remaining, report.drained   # DrainReport
work.diagnostics()                             # counts only
```

* `application_limit` is required. Both limits must be `int` ≥ 1 (bool rejected), and
  `owner_limit ≤ application_limit`. Timeouts must be finite numbers ≥ 0 and are validated
  before anything is closed or cancelled.
* The controller is held by the application. There is no module-level mutable state, and
  owner ids come from a per-controller counter. The module imports only the standard library
  and looks its logger up lazily.

## Invariants (with the tests that exercise them)

1. **Admission is synchronous and atomic in the loop.** `try_start` never awaits. It checks
   scope, then the owner bound, then the application bound. It reserves the slot *before*
   calling the factory or creating the task, so a factory or an eager first step
   (`asyncio.eager_task_factory`) that re-enters `try_start` cannot exceed either bound
   (`test_reentrant_admission_from_factory_and_eager_step_is_bounded`).
2. **A rejected request creates nothing.** No factory call, no coroutine object, no task and no
   queue (`test_every_rejection_reason_leaves_the_factory_uncalled`, which also checks for no
   `RuntimeWarning` after `gc.collect()`; negative control `test_unawaited_coroutine_detection_works`).
3. **Factory or creation failure leaves no capacity held and no unawaited coroutine.** A factory
   exception propagates. A non-coroutine return raises `TypeError` (and is closed if it has
   `close`). If `create_task` fails, the coroutine is closed
   (`test_factory_errors_and_bad_returns_keep_no_capacity`, `test_task_creation_failure_closes_the_coroutine`).
4. **Bounds hold under a pending workload.** With one read pending, 1,000 more frames from the same
   socket start nothing and the real `_reply_status` makes one refresh call. A second socket is
   served meanwhile. 1,000 sockets are held to `application_limit`, and a freed slot is reusable
   (`test_one_socket_burst_of_1000_get_status_starts_one_read`,
   `test_1000_sockets_are_held_to_the_application_limit`, `test_owner_limit_above_one_is_respected`).
   Evidence is real tasks in `asyncio.all_tasks()`, factory calls, refresh calls and messages sent.
5. **Each task frees exactly its own slot.** The done callback pops only its own task. A stale
   or duplicate callback frees and counts nothing, so it cannot remove a successor
   (`test_completion_before_release_holds_the_slot_and_frees_only_itself`).
6. **Completion, failure and cancellation all release capacity.** Failures are retrieved, so
   there is no "Task exception was never retrieved", with a negative control on a plain task.
   Failures are logged by exception *type name only*
   (`test_completion_failure_and_cancellation_each_release_the_slot`,
   `test_failed_task_exception_is_retrieved`, `test_repr_and_diagnostics_carry_no_client_data`).
7. **Disconnect is owner-local.** `aclose` cancels and waits for this owner's tasks only. It is
   idempotent and bounded, and a closed owner never reopens, even after a completion/close race
   (`test_disconnect_cancels_only_that_socket_and_closes_it_for_good`,
   `test_disconnect_does_not_wait_for_other_sockets`, `test_close_racing_a_completion_does_not_reopen_or_miscount`).
8. **Shutdown stops all admission from its first step.** Admission stays refused while shutdown
   waits on slow cleanup, owners opened later are closed, and repeated shutdown is safe
   (`test_shutdown_stops_all_admission_and_drains`, `test_admission_is_refused_from_the_moment_shutdown_starts`).
9. **A scope closed during admission still cancels the new task.** If the factory or an eager
   first step closes the owner or begins shutdown before the task is tracked, the task is
   cancelled right after registration (`test_scope_closed_during_admission_cancels_the_new_task`).
10. **Resistant work is never hidden.** See below (`test_resistant_task_is_reported_held_and_never_hidden`,
    `test_resistant_task_does_not_block_another_owners_disconnect`,
    `test_cancelling_the_closer_keeps_the_owner_closed_and_tracked`).
11. **Isolation.** Two controllers share nothing. A controller is bound to its first event loop,
    and use from another loop raises before the factory is called. Loading the file alone in a
    fresh `python -I` adds only stdlib modules, no `rest_api`/`aiohttp`/integration imports,
    no logger, thread or handler (`test_application_instances_share_nothing`,
    `test_a_controller_stays_on_its_first_loop`, `test_admission_needs_the_running_loop`,
    `test_module_imports_only_the_standard_library`, `test_loading_the_module_alone_has_no_side_effects`).

## Cooperative versus resistant cancellation

`Task.cancel()` is only a request. A **cooperative** task lets `CancelledError` propagate, as
`_reply_status` does: its `except Exception` does not catch it, which a test confirms with the
real function. Such a task finishes within the bounded wait and releases its slot.

A **resistant** task catches `CancelledError` and keeps running. Nothing here can stop it, so:

- it stays referenced by the owner and the controller;
- it stays counted against both limits (other owners may see `APPLICATION_BUSY`);
- every `DrainReport` reports it in `remaining`, with `drained == False`;
- repeating `close`/`aclose`/`shutdown` requests cancellation again, and each call stays bounded;
- its slot is released only when it really ends.

If the coroutine awaiting `aclose`/`shutdown` is itself cancelled, that cancellation propagates.
The scope stays closed and the tasks stay tracked. A task that blocks the loop synchronously is
outside any asyncio remedy.

## Limitations and honest scope

- **Not wired.** No HTTP/WebSocket behaviour changed, and no test opens `/ws`. The tests model the
  future call site by driving the existing, unmodified `websocket._reply_status` with a fake stream.
- Single event loop, not thread-safe (documented; cross-loop use is refused).
- A task that finished but whose done callback has not run yet still holds its slot until the
  next loop iteration. This is conservative and tested.
- `import rest_api.ws_request_work` runs the existing package `__init__` (which imports `websocket`,
  `utils`, `aiohttp` …). The module itself is stdlib-only and side-effect-free, verified in isolation.
- Not addressed: event-loop closure while resistant tasks remain, and a `KeyboardInterrupt`/`SystemExit`
  raised inside an eager first step.
- Default drain timeouts (1 s owner, 5 s shutdown) are proposals for the wiring package.

## Proposed later wiring (separate, coordinator-gated package; not done here)

1. `create_rest_app`: `work = WsRequestWork(application_limit=N, name="ws_get_status")`, stored under
   a `web.AppKey`, plus a `cleanup_ctx` that awaits `work.shutdown(timeout=…)` on exit. `N` must
   be decided at wiring time. Sockets are already capped by `MAX_WS_CLIENTS` (default 32), and
   runtime refresh may serialise reads, so a small value such as 4–8 is plausible.
2. `handle_websocket`: `owner = work.open_owner()` after `ws.prepare`, then `owner.close()` followed by
   `await owner.aclose(timeout=…)` in the `finally` (the synchronous close keeps admission shut
   even if that `finally` is cancelled again).
3. `_handle_command` (needs the owner): replace `create_task`/`_replies` with
   `owner.try_start(lambda: _reply_status(stream, ws))`.
4. **Overload response.** This decision has freshness consequences, so it belongs to the wiring review:
   - (a) *Recommended:* answer a rejection with the existing `error` event and a fixed message
     (e.g. `"Status request already in progress"` / `"Hub busy, retry"`). The schema is unchanged,
     every `status` still comes from a read started after its request, and a spamming client gets
     one `status` plus errors instead of N `status` replies.
   - (b) Silent coalescing: one reply covers several requests. This weakens "fresh read after
     the request" for the later frames.
   - (c) One trailing re-read per owner (≤ 1 active + 1 pending). This keeps freshness but needs a
     small extension and changes the reply count.
5. Wiring then needs its own tests through a real aiohttp `/ws` client: burst, disconnect, app stop
   and a second client. It also needs `features.yaml`/ledger treatment if the protocol behaviour
   changes, and exact-commit re-review.

## Evidence (all ignored or outside the repo; originals preserved)

Toolchain: Python 3.12.10, aiohttp 3.13.3, pytest 9.1.1, pytest-asyncio 1.4.0, run from the main
checkout's `.venv` (`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv`; the worktree has
no venv). Every invocation went through `build/remediation-20261104/ws-work/run.py`. Each one got a
fresh root `C:/t/remediation-ws-work/NN-label/` with its own `native-temp` (TEMP/TMP), `data`
(`MATRIX_DATA_DIR`), `config` (`UC_CONFIG_HOME`) and `pytest-temp`, and the inherited Windows
environment. The child was run directly with no shell, and its exit code is the runner's exit
code. Each root keeps `manifest.json` (argv, cwd, UTC times, duration, exit, sha256/bytes, safe
env), raw `stdout.txt`/`stderr.txt`, `junit.xml` and the untouched temp trees. Copies are in
`build/remediation-20261104/ws-work/receipts/`. No root was reused or deleted. `run.py` gained the
`PYTEST_ADDOPTS` `{T}` substitution after receipt 49, and `mutants.py` gained hang handling after
the first attempt.

Frozen candidate bytes (LF):
`src/rest_api/ws_request_work.py` sha256 `3bc116d88029aeecdbec5fdce7590e5d623442e37049a9bc4c7bf9489d3031c5`;
`tests/test_ws_request_work.py` sha256 `2628c0734fa4860ba53fc30d53a246408dbc4b88fc9b2d5a9ba16c500ea7945b`.

| Receipt | Command (abridged) | Exit | Result |
| --- | --- | --- | --- |
| 49-final-focused | `python -I -m pytest tests/test_ws_request_work.py -vv` | 0 | 44 passed; junit `533563fe…096b`, manifest `d28ce895…5e1b` |
| 45-focused-xdev-targeted | same, `-X dev`, `-W error::RuntimeWarning/ResourceWarning/Pytest{Unraisable,UnhandledThread}…` | 0 | 44 passed (asyncio debug mode) |
| 46-regress-ws-events-lifecycle | `test_hub_events`, `test_runtime_websocket_sync_r3e`, `test_runtime_shutdown_r1`, `test_runtime_composition_r1`, `sim/test_sim_ws_contract`, `sim/test_sim_status_broadcast`, `test_rest_api` | 0 | 237 passed; junit `5d002508…ff77` |
| 47-final-ruff-ci-paths | `ruff check src tests custom_components tools run.py run_server.py` | 0 | All checks passed |
| 48-final-mypy-src | `mypy src/` (CI job) | 0 | no issues, 92 files |
| 42-mypy-new-strict2 | `mypy --check-untyped-defs --warn-unused-ignores --follow-imports=silent` (new files) | 0 | no issues |
| 50–65, `mutants-summary-final.json` | 16 single-invariant mutants of the module against the frozen tests | all 1 | 16/16 detected, 0 hangs; module restored to `3bc116…`; summary `7e2fe917…4219` |

Failures and aborted runs are kept as evidence:

- **03-mutant-no-application-bound: aborted hang (test-design defect, fixed).** A failing
  assertion left a resistant task alive, and loop teardown waited forever. The harness timeout
  restored the module and the worker killed the orphaned pytest; see `receipts/03-…/ABORTED.md`.
  Fix: a `resistant` fixture that always lets those bodies finish.
- **12–14 (attempt 2): `close-does-not-close`, `shutdown-does-not-close`, `no-post-admission-cancel` hung.**
  The harness killed them as `timeout`. Unguarded `asyncio.wait([task])` calls now go through
  `within(...)` (10 s outer guard), so these mutants fail cleanly (29–31, 57–59).
- **20 (attempt 2): equivalent mutant survived.** `open_owner(closed=...)` duplicated the
  controller's shutdown check, so the redundant parameter was removed and replaced by a
  meaningful mutant (`owner-ignores-shutdown`, detected).
- **39 `ruff format --diff`: exit 1.** Formatting is not a CI or hook gate (CI runs `ruff check` only),
  and existing `websocket.py` is not format-clean either. The new files were left in repository style.
- **41 strict mypy: exit 1.** Test-file findings were fixed (→ 42). Remaining findings are
  pre-existing `src` ones outside the CI configuration (unused ignores in `orei_matrix.py`,
  `system.py`, `scenes_v2.py`, `hub/cli.py`; `hub/runtime/composition.py:175` arg-type).
- **44 `-X dev -W error`: exit 3, pre-existing.** pytest-asyncio raises `PytestDeprecationWarning`
  (`asyncio_default_fixture_loop_scope` unset in `pyproject.toml`) at configure time, which aborts
  under a blanket `-W error`. Targeted errors were used instead (→ 45).

Commit-time gate: the normal `.githooks/pre-commit` (ruff + `pytest tests/ --ignore=tests/ha
--ignore=tests/uc -x`) runs at commit through `run.py`. `ROUTE_COVERAGE_STRICT=1` is set so the
same full-core run also enforces strict route coverage, and `PYTEST_ADDOPTS` sends its
JUnit/basetemp to the fresh root.

- **66-commit-hook-strict: exit 1, no commit made (environment).** It ran 07:23:46Z–07:35:02Z.
  Ruff passed, and pytest gave 1 failed, 3,835 passed, 22 skipped, 35 deselected, with route
  coverage 177/177. JUnit sha256 `ed8cf971268b28196600e30e724f4fa202d30181b5fde44901d8c564d6550a1d`.
  The only failure was `tests/test_ui_unified_settings_overlay.py::TestJavaScriptLinting::test_npm_run_lint_js_passes`:
  `eslint.config.js` could not import `@eslint/js` (`ERR_MODULE_NOT_FOUND`). The worktree had no
  `node_modules`, and the shared `NODE_PATH` fallback does not resolve ESM imports. This was the
  same environmental cause as the ledger precedent. It is a partial run, not a full-suite pass,
  and all its originals are preserved.
- **Environment repair (coordinator, not author).** The worktree's ignored `node_modules` is now a
  Junction to `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/node_modules`. The coordinator
  checked package/lock bytes and blob equality, made no install, download or root edit, and ran
  `npm run lint:js` from this worktree with exit 0. Receipt:
  `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/remediation-execution-20261104/ws-environment-recovery/environment-fix-receipt.json`.
  The junction is untracked/ignored and must be preserved as link metadata, without traversal.
  The author verified the junction type and target, that `@eslint/js` resolves, and that the
  frozen source/test hashes are unchanged.
- **One authorized fresh hook run** after the repair, in a new root. Its label, exit and result are
  reported in `worker_done`; this file cannot quote its own commit's hook result. A failure
  there means no commit.

No feature registry, ledger generation, global validation gate, physical or LAN work was run.
