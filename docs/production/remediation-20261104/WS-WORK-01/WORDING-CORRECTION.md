# WS-WORK-01 wording correction: C01-R01 no-progress rationale

Date: 2026-11-04. Author: original correction author, Anthropic `claude-opus-5-5`
(launch effort `high`; per-turn effort is not visible to the author natively).

| Item | Value |
| --- | --- |
| Authority | Task `task_c4e3c9018634`, Dispatch `ctx_5c6661149549`; the one bounded original-author correction/re-review reserve of adopted recovery `FINAL_PACKET.json` v1 |
| Finding | C01-R01 (Low, documentation/calibration, nonblocking) in `CORRECTION-01-REVIEW.md`, review commit `ed69708325f9e10a2ae2784179303016acbd69d0`, OpenAI `gpt-6-astra/high` |
| Base | `24c5170458200209836228646fdfc8784a967ad1` on `remediation/ws-work-c01`, the exact component that was reviewed |
| Integration snapshot read at entry | `wp-runtime-completion` = `85b797a403ba3f9bf4c56deb92c4ccba11042710`, resolved once |
| Packet digest | Raw blob SHA256 `f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e`, matches |
| Lease | Module docstring and `_drain` comments in `src/rest_api/ws_request_work.py`, plus this new file |
| Commit and hook | Reported in the completion receipt and `worker_done`. This file cannot name its own commit or hook result |

This is a prose-only correction. It changes no runtime behaviour, no `DrainReport`
contract and no test. It is not privacy work. It grants no first-authorship
competence. These findings stay as recorded: M3 privacy qualification FAIL, the
old Opus FAIL, first-authorship NOT_GRANTED and the historical WSR-03 failure.

## What was wrong

At `24c51704`, the module docstring ("Truthful drain", former lines 59-64) said that
a cleanup running inside an admission "cannot usefully wait: what it would wait for
cannot progress until it returns". The matching `_drain` comment said "what it
would wait for cannot progress before it returns".

As a general statement, that is false. The reviewer's `progress_control` probe
(`build/remediation-recovery-20261104/ws-r01/probe.py` in the review tree, results
in `C:/t/remediation-recovery/ws-r01/03-independent-current`) shows the case.
Under `asyncio.eager_task_factory`, a factory creates a separate cleaner task. That
cleaner runs eagerly and then suspends. The factory continues, the admission
attaches, and a sibling task finishes, all before the cleaner returns. The existing
test `test_cleanup_of_another_owner_inside_an_admission_still_waits_for_it` shows
the same suspension for another owner's cleanup.

**The old explanation in `CORRECTION-01.md` is also corrected here.** Under
"Mechanism and invariants", step 1 of that report says that an outstanding
reservation means "the admission cannot finish before the cleanup returns". That
is the same overly broad claim, and I wrote it. The historical report is not
edited. This file supersedes that sentence as an explanation. The behaviour it
describes does not change.

## Corrected explanation

- **What the code does (unchanged).** `_drain` returns at once, without
  awaiting, when an admission of its own scope still holds a reservation. That
  work is counted in `remaining`, so the result is never `drained`.
  - `try_start` is a plain `def` and never awaits. A reservation can therefore
    only be seen from code that runs synchronously inside that admission: a task
    step started there. Examples are the eager first step of a cleaner task that
    the factory creates, or of the admitted task itself.
- **Why it returns at once.** This is the adopted, conservative and bounded
  policy. It is not a proof that the admission cannot progress.
  - A reservation has no attached task that `asyncio.wait` could wait on.
  - An independently spawned eager cleaner that suspended would let the factory
    continue, the admission attach and other work finish before that cleaner
    returns.
- **Self-dependency (unchanged and still exact).** A cleanup called from one of
  the scope's own attached tasks cannot finish its caller while that caller
  waits for itself. No wait could report that scope drained, so it returns at
  once.
- **Everything else (unchanged).** In all other cases there is one ordinary
  `asyncio.wait`, bounded by `timeout`, followed by a fresh recount.

The `shutdown`/`aclose` docstrings already describe only this observable
behaviour ("Returns at once, not drained, when called inside ... or from one of
its tasks"). They make no impossibility claim, so they were left unchanged.

These are unchanged:

- **D2.** `remaining` counts all unfinished attached tasks plus all in-progress
  reservations of the scope, including the calling task. `requested` counts only
  the cancellation requests that took effect. Owner scope uses only that owner's
  reservations.
- **The single bounded ordinary wait.**
- **D3.** The lifecycle loop guard runs before any mutation.

## Exact change

`src/rest_api/ws_request_work.py` has three hunks of prose:

1. **Module docstring, "Truthful drain".** The former single paragraph (lines
   59-64) is replaced by two paragraphs. The first covers the reservation case
   and labels the immediate return as the adopted policy, with the
   independent-cleaner counterexample. The second covers self-dependency and
   the one bounded wait.
2. **`_drain`, first early-return comment.** It now names the condition (an
   admission of the scope is still in progress) and states the policy and the
   counterexample, instead of a no-progress claim.
3. **`_drain`, self-dependency comment.** It adds "so no wait here could report
   the scope drained".

No other tracked file changes, apart from this new report.

## Proof that behaviour is unchanged

All runs used `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
with explicit `-B` (and `-I` for the child). Each run inherited the Windows
environment, then got its own fresh `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`,
`TMP` and `TMPDIR` under a new root `C:/t/remediation-recovery/ws-wording/<label>/`.
`PYTHONPATH` and `PYTEST_ADDOPTS` were removed. Every root keeps the argv, cwd,
safe environment, UTC times, direct exit code, full stdout/stderr with their
hashes, and an inventory of its temporary files. The runner, proof and
import-measurement scripts are in the ignored
`build/remediation-recovery-20261104/ws-wording/`.

| Root | Direct exit | Result |
| --- | --- | --- |
| `02-prove-ast-hash` | 1 | **Own proof-script defect, kept.** It compared raw CRLF working bytes (`core.autocrlf=true`) with LF blobs, so every file mismatched. The AST checks in that same run passed |
| `03-prove-ast-hash` | 0 | All proof checks pass, but on an **intermediate** wording. One docstring phrase ("no attached task") was refined and rewrapped after this run, so it does not prove the final module |
| `04-ruff-ci-paths` | 0 | `ruff check src tests custom_components tools run.py run_server.py --no-cache`: all checks passed |
| `05-mypy-src` | 0 | `mypy src/` with its own cache dir: no issues in 92 source files |
| `06-focused-debug` | 0 | 73 passed, 0 failed, 0 skipped, 0 errors. Flags: `--asyncio-debug`; RuntimeWarning, ResourceWarning, unraisable and thread exceptions as errors; route and cache plugins disabled; fresh basetemp and JUnit. 25 JUnit pairs record `asyncio_debug_configured=True` and `asyncio_loop_debug=True`, and the fixture asserts they are equal |
| `07-import-origin` | none | **Own runner defect, kept.** Braces in an inline `-c` probe clashed with the runner's `{ROOT}` substitution, so Python never launched. The empty root is preserved |
| `08-import-origin` | 0 | The imported module is this checkout's `src/rest_api/ws_request_work.py`, using the root venv interpreter (CPython 3.12.10). Its SHA256 is `95fe2a40e281658e0af9bd003b299df99ce8b14d00f1c52368f13084306c9921` with CRLF working bytes, which is the final module |
| `09-prove-final` | 0 | All proof checks pass on the final module (the same SHA256 as in `08`) |

Runs 04-09 all used the final module text. `09-prove-final` checks:

- The module ASTs are identical at `24c51704` and in the candidate, after
  removing only the module docstring statement and omitting location
  attributes. Both dumps have SHA256
  `73ea0540fea5374108a705bac848f0c3ef619da70204c88e41d045eb0d10d5fa`.
  - Function and class docstrings stay in the comparison, so they are proven
    unchanged.
  - Comments are not part of the AST. Their change is shown by the diff.
- All 4,728 non-leased tracked files have Git blob ids equal to the base.
- Their raw working bytes are equal to the snapshot taken in `03`.
- The focused tests' blob is unchanged.
- The working-tree status contains only the leased paths.

No new test was added: this is prose only. No mutation campaign was run.

The one normal configured source commit hook runs at the frozen candidate. It
runs Ruff plus the full core, with `ROUTE_COVERAGE_STRICT=1`, no `hooksPath`
override, and fresh JUnit and basetemp through `PYTEST_ADDOPTS`. This file
predates that commit. The receipt under `.../ws-wording/` records the hook's
exit, counts, route inventory and streams.

## Limits

- Windows CPython 3.12 only.
- The focused run proves the adopted behaviour of the component at this
  candidate. It is not wiring, CR-01 closure, source intake or canonical
  evidence.
- Tool outputs outside the owned roots are not suppressed:
  - Ruff, mypy and pytest caches, and pytest bytecode, from runs not
    controlled by `-B`.
  - The worktree's ignored `route-coverage.json`, which the hook rewrites; a
    copy is kept in its own root.
  - Harness files under the session profile.

  This is an audit of authored paths, not of every write on the host.
- The reviewer's probe and roots, the original AUTHOR, CORRECTION-01 and REVIEW
  files, and all earlier `ws-c01` evidence were only read.
- The different-family Astra/high review of the changed commit is reserved for
  after delivery. There are no automatic further correction rounds.
