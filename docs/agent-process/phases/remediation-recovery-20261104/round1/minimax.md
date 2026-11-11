# Remediation recovery 2026-11-04 — R1 independent assessment (MiniMax)

Independent round-1 prose assessment of prospective recovery after two actual
failed assessments. Not consensus, not source correction, not a qualification
retake, not source acceptance, not model qualification, not permission to start
implementation.

## 0. Identity, bindings, hashes and what I actually read

### 0.1 Route and authority

| Item | Value |
| --- | --- |
| Contributor | MiniMax family, OpenCode 2 route, dedicated worktree `wp-remediation-recovery-r1-minimax` |
| Task / Dispatch / terminal | `task_30e8158c02a5` / `ctx_ba59b5829abe` / `term_9da3a863-ed14-4869-9fec-3802a45e8c9d` |
| Coordinator handle | `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| Run / runtime / Orca | `run_37205f6095b3` / `35d5d4fb-e6bd-4756-9d7b-24632ba727d7` / 1.4.247 (runtime and version confirmed live at 2026-11-04T08:41Z) |
| My checkout base / branch | `b13ddc4de461b7e1072fead0d39361bcb079282f` / `planning/remediation-recovery-r1-minimax` (HEAD = base, clean tree, no untracked files) |
| Model binding | `minimax-coding-plan/MiniMax-M3`; effort: thinking inherited, CLI effort override unsupported (no effort value can be set or observed) |
| Coordinator's recorded MiniMax routing digest | `62e6f5ab100bffe9aa802a380f3860612ba1aedf5e760ae443d5040984b18096` (packet) |
| Helpers / subagents / other models | none used; no plugin/MCP routing; no side work |

Two route facts I must record rather than smooth over:

1. The OpenCode model listing available to this session exposes exactly one
   provider (`minimax-coding-plan`) and one catalogued model
   (`minimax-coding-plan/MiniMax-M3.1-Flash`). The bound `MiniMax-M3` is **not**
   in that listing. I therefore cannot independently confirm the effective
   underlying model from the catalog; the task binding and the coordinator's
   routing digest are the only authority I have. The packet already requires
   native entry attestation after start; that attestation remains the binding
   evidence for the effective family.
2. `MiniMax-M3` is not `MiniMax-M3.1` evidence. Whatever this session's
   effective variant is, the accepted MiniMax scope in `REPO_CONFIG.json` is
   "bounded evidence inventories only", and the packet records
   "MiniMax-M3 accepted planning/inventory competence is not code-review
   competence". I treat MiniMax as a planning/inventory contributor only.

### 0.2 Input hashes (all byte-verified by me)

| Input | Binding | SHA-256 (canonical LF) |
| --- | --- | --- |
| `docs/agent-process/phases/remediation-recovery-20261104/INPUT_PACKET.json` | blob `5b3000388574150dc8d98ba90f74427bac085af1` in pinned snapshot `56f1b4ee71aaace0afd690d834e0822e90a8ba88` | `40526f127575feead63c94058250a868e0452ccb19b5552f60be66b6b82b77dc` — matches the packet's stated digest |
| Pinned snapshot | `refs/heads/wp-runtime-completion` = `56f1b4ee71aaace0afd690d834e0822e90a8ba88`, resolved once at entry | — |
| Source baseline | `b13ddc4de461b7e1072fead0d39361bcb079282f` (= my checkout base; ancestor of the pinned snapshot) | — |
| WS component module | `15c069bdeb3a9ace37bf68033812ff72659bfbd1`:`src/rest_api/ws_request_work.py` | `3bc116d88029aeecdbec5fdce7590e5d623442e37049a9bc4c7bf9489d3031c5` |
| WS component tests | same commit:`tests/test_ws_request_work.py` | `2628c0734fa4860ba53fc30d53a246408dbc4b88fc9b2d5a9ba16c500ea7945b` |
| WS component AUTHOR | same commit:`docs/production/remediation-20261104/WS-WORK-01/AUTHOR.md` | `028d80071084a988f47e07272785a8ec72940a8302808c907f1b57beea8c24fc` |
| WS independent review | `1cc442207d54b0ad1c5887f6c4e9d5d17b7c8b19`:`docs/production/remediation-20261104/WS-WORK-01/REVIEW.md` | `6ee8bbec66ebdb7e650aa8b08e8f75026ec8580c40ed89b1a2f06e6104d85adb` — matches the packet |
| Privacy review (judge) | `e8ce39660a37d277e735adce680b848210c8d9b4`:`docs/production/remediation-20261104/PRIVACY-REVIEW-ASSESSMENT/REVIEW.md` | `e9efab38d4eb81c2d352195d33952559f2fee0139a989f43a3e4dd1524920582` — matches the packet |
| Privacy assessment AUTHOR | `1a38e2851f0223627f5377fa5e32584c233e1223`:`docs/production/remediation-20261104/PRIVACY-REVIEW-ASSESSMENT/AUTHOR.md` | `7b469ade0388e0de5a46051528992bfb675ba43addd871c48fdaeaf48aa01f2c` |
| Privacy assessment packet | `56f1b4ee…`:`docs/production/remediation-20261104/PRIVACY-REVIEW-ASSESSMENT/ASSESSMENT_PACKET.json` | `1732709314f8c6639ff9e136277861abaf444075227734a0b7d9e2d38b7c4dd8` |
| Opus5.5 coordinator disposition | `56f1b4ee…`:`docs/production/software-waves/QUAL-ANTHROPIC-CORE-01/replacement-opus55-20261103/COORDINATOR_DISPOSITION.json` | `d2096e6edcf63cf7ca0fc7fd8c5fd58ea45222527c59b66d6cb44fede0949e79` |
| `docs/ORCHESTRATION_PROTOCOL.md` | `56f1b4ee…` | `714fd1774d14fa6604aea8cd6ce78c85b122bda9f37a865ea6f56ec2a7f534c4` |
| `docs/agent-process/PROTOCOL.md` | `56f1b4ee…` | `4aeb2351edec0da278c0c330c4df0e852fed0335cff2e35a4e835895ab1ac052` |
| `docs/agent-process/REPO_CONFIG.json` | `56f1b4ee…` | `67dd58d963e44bed6a31db4f90a4de44c1936b9e3711997966a180bff8c03843` |
| `docs/planning/COMPREHENSIVE_REMEDIATION_20261104.md` | `56f1b4ee…` | `af3ca3deb2b487b83c6f215b523c4bfaf2ac8eb323c1d63b1e64a07f2ca1831e` |
| `docs/planning/software-waves/EXECUTION_PINS.json` | `56f1b4ee…` | `e68f1ff2843676e24d8a9f6757edf78e90bc5bf167c0c53ae591b552a9615b1d` |
| `docs/production/remediation-20261104/WS_WORK_TASK.md` | `56f1b4ee…` | `5cee3eb86bf788e1640d6021ad4384aeeed392daafefd0a2203e9e51e5d68998` |
| `docs/production/AGENT_ALLOCATION.md` | `56f1b4ee…` | `4227df4977c2a70fa662d17c9d25b1967d32a7f5e7a4732ebfe37f8e42077575` |
| Retained privacy chain tip / review base | `2d02004d3108953a302e1a49aab9a5f24e944136` / `d6e78e0b6ab1dab5216443584d810a7a24af32b2` | chain of 6 commits: `8b9f5623`, `11f305b1`, `47b0bbb8`, `615d3c84`, `8fc65e05`, `2d02004d` |

My extraction manifest, the pinned copies and the extract script are retained
under my ignored root `build/remediation-recovery-20261104/minimax-r1/`
(`snapshot/EXTRACT_MANIFEST.json`).

### 0.3 Reads actually performed, and their limits

Read in full: the pinned `ORCHESTRATION_PROTOCOL.md`, `agent-process/PROTOCOL.md`,
`REPO_CONFIG.json`, `ADOPTION_REPORT.md` (skimmed), `COMPREHENSIVE_REMEDIATION_20261104.md`,
`WS_WORK_TASK.md`, `ASSESSMENT_PACKET.json`, the Opus5.5 `COORDINATOR_DISPOSITION.json`,
the WS independent review (all 339 lines), the privacy judge review (all 319 lines),
the privacy assessment AUTHOR (skimmed for the contract claims it makes), the full
WS module (412 lines), the WS test module (887 lines; the 44 test bodies, with the
resistant/eager/race sections read closely), the four changed privacy source files
at `2d02004d` (`tools/validate/evidence.py` in full, `model.py`, `runner.py`,
`clients/api.py` in the cited ranges), the `RV-PRIVACY-CHAIN`, `RV-WS040` and
`RV-API034` pin entries, and the top of the pinned allocation ledger.

Limits, stated honestly:

- I did **not** read the WS module's callers (`websocket.py`, `events.py`,
  `app.py`) or the `ha.py` HA client at the pinned commits; the WS reviewer's
  reading of them is used as attributed evidence, not as my own verification.
- I did **not** read the privacy chain's *test* modules
  (`tests/validation/test_sw_sec_data_02_c1/c2/c3.py`), so I cannot assert which
  existing assertions would break under my proposed masking change; the author
  and the eventual reviewer must check that.
- I did **not** read the judge's gap-probe scripts or the candidate's native
  transcripts, so the judge's reproductions are attributed evidence. The
  mechanism claims below that I state as mine are derived from the *source* I
  read, and are marked as such.
- I ran **no** native/private runtime scans and no product code; the
  documentation module run in §9 is the only execution in this task.
- I did not read the peer R1 reports (none existed) and did not read the peer
  task briefs.

## 1. What the two negative results actually establish (restated, unchanged)

**WS component** (`1cc44220…`, review by OpenAI `gpt-6-astra`/high, Task
`task_b9f4d569ee06`): component correctness **FAIL**, component acceptance and
bounded first-authorship acceptance **HOLD**. The 44 focused cases and the
4,126-case hook run pass; four deterministic eager/reserved-admission cleanups
report `drained=True` while admitted work is alive. WSR-01 Medium (blocking),
WSR-02/03/04 Low. No wiring exists; CR-01 remains open; no retake, new judge
or retry is authorised by that review.

**Privacy review domain** (`e8ce3966…`, judge OpenAI `gpt-6-astra`/high, Task
`task_8c32e92975a4`): overall **FAIL** — two axes PASS (provenance,
counterexamples), four FAIL (dataflow invariants, behaviour/tools, calibration,
review quality). The candidate did substantial work but missed the supported
`current_pin` credential, under-classified the tuple/header-pair/string/summary
residuals, and mis-stated the HA options path. The candidate's existing
API-refusal qualification is neither regraded nor extended. The privacy source
is unaccepted. One candidate and one judge are spent.

Both remain the authoritative negative results. Nothing below rewrites them, and
no rubric is softened.

## 2. Decision request 1 — concrete source-correction invariants and tests

### 2.1 WS component (`src/rest_api/ws_request_work.py`, 412 lines, frozen at `15c069bd`)

**Root cause, read from the source (mine).** `_admit` reserves capacity at
lines 352-353, then calls the user factory (356) and `loop.create_task` (363),
and only registers the task at 369-370; the reservation is released in the
`finally` at 371-373. `WorkOwner.aclose` (241-249) and `WsRequestWork.shutdown`
(407-412) snapshot **only** `self._tasks` (247, 410) and wait on that snapshot
(249, 412). `close()`/`begin_shutdown()` likewise cancel only registered tasks
(238-239, 404-405). Therefore, while the reservation window is open, a cleanup
that executes *inside* that window sees an empty task set and reports
`DrainReport(requested=0, remaining=0)`. The post-registration cancel at 376-380
does cancel the eventual task (because `close()`/`begin_shutdown()` already set
`owner._closed`/`_closing`), but it cannot retract the report that was already
returned. `_wait_bounded` (170-180) returns immediately for an empty list, so
there is no scheduling point at which the reservation could be observed.

The three in-repo test bodies confirm the gap: `test_scope_closed_during_admission_cancels_the_new_task`
(777-801) closes the scope *synchronously* and never drains;
`test_reentrant_admission_from_factory_and_eager_step_is_bounded` (752-774)
re-enters admission but not cleanup; `test_resistant_task_is_reported_held_and_never_hidden`
(602-633) drains a resistant task that is already registered. No test combines
reentrant cleanup with an unresolved reservation.

Proposed invariants (all must hold at the corrected commit):

- **WS-I1 — a drain report may never claim `drained` while admitted work is
  alive or unresolved.** `DrainReport.drained` (147-150) must be `False`
  whenever the scope still owns a live task *or* an in-flight admission. This
  restores the module's own promise at docstring lines 49-61 ("the report never
  says drained while it is alive") and the review's acceptance item 2.
- **WS-I2 — the reservation window is visible to cleanup.** The controller must
  expose in-flight admissions to drain, per owner and application-wide. The
  counters already exist and are already correct for capacity
  (`owner._reserved` at 191, `controller._reserved` at 273, used by
  `active_count` at 210-212 and 292-294); they are simply not consulted by the
  drain. The minimum change is to make `aclose`/`shutdown` include the relevant
  `_reserved` count in `requested` and `remaining`. Using `_reserved` alone is
  sufficient and avoids new mutable state.
- **WS-I3 — a pending admission is always cancelled, never silently inherited.**
  The existing 376-380 check must be kept and must cover the case where the
  scope was closed during the window; the eventual task must be cancelled
  exactly once and must still be counted by the *next* drain.
- **WS-I4 — a drain never waits for the admission that is calling it.** The
  reentrant cleanup runs *inside* the pending admission's own frame, so
  awaiting that admission would deadlock until the timeout and would still
  report a non-drained result. The correct behaviour is to count the pending
  admission as outstanding and return within `timeout`. This must be stated in
  the contract, not discovered later.
- **WS-I5 — truthful loop boundary (WSR-02).** The docstring (71-75) claims
  every method must run on the controller's loop and that a call from another
  loop raises `RuntimeError` before the factory is called, but `_check_loop`
  (325-331) is called only from `_admit` (339). The probe showed
  `shutdown(timeout=0)` on a second loop in the same thread does not raise; it
  sets `closing` and calls `task.cancel()` on another loop's task, which is not
  thread-safe. Prefer **enforcing** the documented boundary in `close`,
  `aclose`, `begin_shutdown` and `shutdown` (raising before any state mutation
  or cancellation) over narrowing the prose: the current behaviour mutates
  foreign-loop state and cancels foreign-loop tasks, which is a genuine hazard,
  not a documentation nicety. If the author instead narrows the guarantee, that
  is a *contract change* and must be recorded as such, not as a docstring edit.
- **WS-I6 — truthful debug/evidence claim (WSR-04).** `-X dev` is Python
  development mode; pytest-asyncio 1.4.0 passes `asyncio_debug=False`
  explicitly for plugin-owned loops, so the 44-case and hook runs are **not**
  asyncio-debug coverage. The correction report must not relabel them. If
  asyncio-debug coverage is wanted, it must be produced with
  `asyncio.run(debug=True)` or `-o asyncio_debug=true` and must record
  `loop.get_debug() == True` as the reviewer did in its gap probe.
- **WS-I7 — bounded and measured reservations.** A factory that blocks
  synchronously cannot be preempted; the honest bound is that the drain
  *returns* within `timeout` and reports the reservation as outstanding, and
  that the reservation keeps consuming capacity (`active_count` already
  includes it). To make a resistant reservation observable rather than
  invisible, the controller should expose in-flight admission count and the
  observed admission-hold duration in `diagnostics()` (300-310), which today
  carries counts only and no client data. A duration counter is a measurement,
  not a guarantee, and the contract must say so.

Negative tests to add (failure-sensitive, not counter-mirroring):

- **WS-T1 — reentrant drain during the reservation window.** Under
  `asyncio.eager_task_factory`, the admitted coroutine's first step (or the
  factory itself) triggers `owner.aclose(timeout=…)` and
  `work.shutdown(timeout=…)`. Assert: the returned report has
  `drained is False`, `remaining >= 1`, the admitted task is cancelled once it
  registers, the capacity slot is released only after the task actually ends,
  and a *second* drain after the task has settled reports `remaining == 0`.
  This is the exact case the four gap probes covered and the 44 cases missed.
- **WS-T2 — owner-level and application-level variants.** Repeat WS-T1 for
  `aclose` and for `shutdown`, and for a cleanup triggered from a synchronous
  factory that schedules an eager cleaner task. The report must remain truthful
  in all four shapes.
- **WS-T3 — foreign-loop rejection (WSR-02).** With a second loop in the same
  thread: `close`, `aclose`, `begin_shutdown`, `shutdown` must raise
  `RuntimeError` *before* mutating `_closed`/`_closing` and before cancelling
  any task of the first loop; the first loop's tasks must be unaffected and
  still tracked.
- **WS-T4 — resistance and no false release.** A resistant body that swallows
  cancellation must keep its slot and be reported `remaining >= 1` across
  repeated drains, while the *other* owner's drain is unaffected (the existing
  636-651 case, kept).
- **WS-T5 — truthful evidence claims.** The correction report must state the
  actual asyncio-debug status of every run it cites, and any claim of asyncio
  debug must be backed by a recorded `loop.get_debug() == True`.

### 2.2 Privacy chain residuals (`tools/validate/*` at `2d02004d`)

Mechanism, read from the source (mine, with the judge's findings as the
authoritative severity/attribution):

- `evidence.py:115-118`: `_SECRET_KEYS = re.compile(r"pass(word|code)?|secret|token|api[_-]?key|^(key|pin|pin_hash|authorization|cookie|x-admin-pin)$", re.IGNORECASE)`.
  The first alternatives are unanchored; the second group is anchored to the
  **whole** key. `current_pin` matches none of them — hence J-1. Conversely
  `key` (the `contracts.shortcut_alias` `data.key` field) and
  `password_protected` **do** match — hence the judge's N-5 compatibility loss.
  Name-based masking is therefore simultaneously too weak (J-1) and too strong
  (N-5).
- `evidence.py:125-133` `redact` traverses `dict` and `list` only. A **tuple**
  is returned unchanged, and `model.py:147` then renders it with `!r` into the
  persisted description — hence N-1. A `str` body is only query-masked, and
  `clients/api.py:160` interpolates `redact(body)` into the client step, so a
  JSON string body keeps its credential — hence N-3.
- `runner.py:635-638` builds a check description with
  `f"client shows {exp.key} == {exp.before!r} before the action"`: the
  expectation's *value* is interpolated raw. `runner.py:766` puts
  `result.body` into `observations.client_diagnostics` unredacted; it survives
  only because `write_record` (`evidence.py:59-66`) applies `redact(record)` at
  persistence. `runner.py:777` copies failed descriptions into `Outcome`
  verbatim, and `runner.py:1026-1037` `_write_summary` writes
  `run-summary.json` with `json.dumps(...)` and **no** redaction — hence the
  record/summary asymmetry in N-4. This raw-value interpolation at
  `runner.py:635` is an observation of mine, not named in the judge's report;
  the eventual author must confirm it against the real expectation shapes.

Proposed invariants:

- **PRIV-I1 — no credential value the harness transmits may appear in any
  persisted diagnostic byte** (procedure, action/request, check description,
  response detail, expected description, steps, observations, `run-summary.json`).
  This is a value-level invariant, and it is the only one that holds across
  all the shapes the judge reproduced: tuple (N-1), header pair (N-2), JSON
  string body (N-3), query/summary path (N-4), and the raw interpolation at
  `runner.py:635`. Implementation direction: the client layer knows the
  credential it sends, so register the exact secret value(s) with the
  redactor, and mask those values wherever they occur in a string, including
  inside `repr` output and inside the summary writer. Two caveats to be
  designed for and reviewed: a short secret can over-mask a coincidentally
  equal public value (documented, narrow), and the registry must be
  process-local and per-run.
- **PRIV-I2 — name-based masking is restricted to a verified credential-name
  list**, and the bare `^(key)$` rule is removed or narrowed so that the
  confirmed public values (`contracts.shortcut_alias` `data.key`, the two
  protected profile/scene reads `password_protected`) stay verbatim while the
  raw verdict and equality assertions remain correct. The list must be derived
  from the real supported interfaces (the product consumer at
  `src/rest_api/security.py:297-305` and the scenario definition
  `tests/validation/scenarios/security_auth.py:34-35,120-128`) and must include
  `current_pin`. Removing a rule can unmask another field, so the change must
  be justified per name, not by dropping the regex.
- **PRIV-I3 — shape completeness.** `redact` must traverse tuples (and any
  other non-str sequence that `json.dumps` accepts), must normalise a
  header container given as a sequence of pairs before masking, and must
  handle a JSON-content-type string body by parsing and masking the structure.
  Where a shape cannot be masked, the contract must say so explicitly instead
  of claiming universal coverage — the judge's own N-1 wording ("retain that
  part as an unproven extension rather than generalizing the tuple proof")
  is the right calibration and must survive the correction.
- **PRIV-I4 — one masking boundary on the way out.** Every write path applies
  the same masker: `write_record` (already does), the summary writer
  (`runner.py:1026-1037`, currently does not), and the description builders
  (`model.py:142-148`, `318-325`, `runner.py:635`). The record-level
  `redact(record)` must remain as defence in depth, not as the only barrier.
- **PRIV-I5 — scope of the HA sibling (N-7) stays narrow.** The HA path
  (`ha.py` raw body recording, `ha_config_flow(options={"api_key": …})` via
  `custom_components/hdmi_matrix/config_flow.py:134-153` and `const.py:18`) is
  real but is **outside** the C1/C2/C3 lease and is a separate HA domain. It
  needs its own explicit lease and its own evidence; the correction must not
  silently widen into HA, and the claim must not be generalised to every HA
  flow (Reconfigure's body is host/port).

Negative tests to add:

- **PRIV-T1 — `current_pin` end-to-end (J-1).** Reproduce the judge's
  matched/mismatched `security_auth.clear_pin_restores_open` action through
  the real `ApiClient.perform`, `Runner._run_one`, `_check`, `write_record` and
  the summary writer at the corrected commit. Assert the synthetic marker
  appears in **no** persisted byte of procedure, request, response detail,
  expected description or `run-summary.json`, in both the matched and the
  mismatched case, while public metadata and the raw request/verdict are
  preserved.
- **PRIV-T2 — tuple / header-pair / JSON-string bodies (N-1, N-2, N-3).**
  One test per shape, each asserting absence of the marker in the persisted
  record *and* in the summary, plus a positive control proving the shape was
  actually transmitted (not merely rejected).
- **PRIV-T3 — summary/record equivalence (N-4).** Assert that everything the
  record masks is also masked in `run-summary.json`, and that the summary
  contains no raw failed description.
- **PRIV-T4 — public-value compatibility (N-5).** Assert that
  `contracts.shortcut_alias`'s `data.key` and the `password_protected` reads
  stay verbatim in the persisted description while the raw verdict, equality
  and schema assertions stay correct. This test is the regression guard
  against re-introducing N-5 while fixing J-1.
- **PRIV-T5 — HA options credential (N-7) and its scope limit.** A bounded
  test of the options/`api_key` path in the HA lease only, with an explicit
  statement that no live HA execution is claimed.

The severity/attribution of J-1 and N-1..N-7, the "no owner-secret incident"
calibration and the two-PASS/four-FAIL axis record remain the judge's; my
invariants are a correction design, not a re-judgement, and they are not
validated code.

## 3. Decision request 2 — lawful next routes, and what current authority covers

Three things are being conflated in the recovery question. They have different
answers and must be separated.

**(a) Ordinary author fix.** The protocol states plainly: "Reviewers report;
authors fix. Re-review material fixes … at their final commits"
(`ORCHESTRATION_PROTOCOL.md`, *Independent review and qualification*), and the
adopted protocol §8 repeats it. The WS review failed on **component
correctness** — axes 2 (admission/factory) and 5 (tests) passed, and the
failing axis 3 is the behaviour of the delivered code. Fixing that code and
re-reviewing it at the corrected commit is the ordinary covered correction; it
is not a failed-qualification retry, and it needs no new authority beyond the
owner's "enact comprehensive remediation" direction and this accepted plan.
The same applies to the privacy chain: the judge reported source defects
(J-1, N-1..N-7) in OpenAI-authored source, so the OpenAI authors fix them and
a qualified different-family reviewer reviews the fix.

**(b) Held first-authorship / failed-domain assessment.** These stay failed.
The WS component's *acceptance* and the bounded *first-authorship* grant remain
HOLD until a qualified different-family reviewer passes the corrected commit;
the failed assessment is not re-labelled and the HOLD is not converted into a
PASS by the act of correcting. The Anthropic privacy-review domain assessment
remains FAIL; the Opus5.5 API-refusal qualification remains exactly the
bounded domain it earned and is neither regraded nor extended.

**(c) Genuinely new-family work.** Where the needed competence does not exist
in any family, the only lawful route is a *first* attempt by a family with no
prior record in that domain, judged by a qualified family that is not the
source's. That is what the privacy-reviewer qualification gap requires today.

**What the current broad authority already covers (no new authorisation
needed):** the WS author correction and its re-review; the privacy source
correction and its re-review; the WS wiring package within the accepted A2
scope and the existing public WS schema; coordinator-owned contract decisions
(the rejection-vs-coalescing choice changes reply counts and freshness but
keeps the documented `error` event, so it is a coordinator contract decision,
not an owner gate); the registry/ledger updates named in the protocol; and the
route-verification work in §7 below.

**What genuinely needs one specific new authorisation** (see §8): a *second*
Anthropic Opus5.5 privacy-domain candidate, because that attempt budget is
exhausted (`COORDINATOR_DISPOSITION.json` → `future_automatic_retry_authorized:
false`, `attempt_budget.candidate_evaluations: 1`, `independent_judges: 1`;
`ASSESSMENT_PACKET.json` → "ONE new domain-assessment candidate and ONE fresh
judge. No automatic rewrite/retry/extra judge"). A *different* family's first
attempt is not a retry of a failed qualification; it is new-family work, and it
is a material family-allocation change, which is exactly what this three-round
cycle exists to decide. If this plan is accepted at R3, that route needs no
further owner statement.

## 4. Decision request 3 — exact models, families, effort, qualification, capacity

Evidence used, not catalogue prose:

| Family | Route / model / effort | Demonstrated evidence (exact artifact) | Qualification limit |
| --- | --- | --- | --- |
| OpenAI | `gpt-6-astra`/high, native Codex (`codex/gpt-6-astra` in the live worker list) | WS component independent review at `1cc44220…` (all six axes, real gap probes, 44-case run); privacy domain judge at `e8ce3966…` (all six axes); RV-API034 report evaluation | **Qualified reviewer** for the WS component and for the privacy-review *domain*. **Not** usable to review OpenAI-authored source (same family). Author competence demonstrated for OpenAI's own chain is the retained authorship, not a general grant |
| Anthropic | `claude-opus-5-5`/high (effort = explicit launch/local config; native per-turn effort unexposed) | `COORDINATOR_DISPOSITION.json` PASS, scope "bounded Python validation-runner/model offline simulator API refusal preparation"; the RV-API034 source review it performed; the WS component authorship (candidate, failed on correctness); privacy domain assessment **FAIL** | **Qualified reviewer** only in the API-refusal domain. **Not** a privacy reviewer (FAIL). **Not** a concurrency/WS reviewer (no artifact). **Not** a qualified author for new product domains; its WS authorship is held |
| MiniMax | `minimax-coding-plan/MiniMax-M3`, thinking inherited, CLI effort override unsupported | Accepted planning/prose/inventory contributions only | **Planning/inventory only.** Not a code reviewer, not a privacy or concurrency author or reviewer. Catalog/effort discrepancy recorded in §0.1 |
| Google | `gemini` reports **unavailable** in the supported usage source at 2026-11-04T08:41Z; `antigravity` reports ok (24% weekly used) but its underlying backend/helper routing and family are unresolved in `REPO_CONFIG.json` (`adoption_conflicts_and_unknowns.routing`) | none for this domain | **Not usable as a third family today** without route verification. The standing pin rule is explicit: "Unknown Gemini is not spare capacity and same-family review is prohibited" |
| DeepSeek | owner-reported exhausted credit | — | Excluded; no dispatch, no purchase |

Capacity, observed live at 2026-11-04T08:41:54Z from the supported account usage
source (fresh, dated, weekly windows of 10,080 minutes): claude 25% used /
75% remaining, session 0%; codex 9% used / 91% remaining, no session window;
minimax 33% used / 67% remaining, session 15%; antigravity 24% used / 76%
remaining but family unresolved; gemini, opencodeGo, grok, kimi, cursor
`unavailable`. All three planning families are above the local 30% floor, so
the "verified fallback" clause is not triggered for them; the reservation
requirement still applies. These are dated observations, not future guarantees,
and absolute allowance plus other-host demand remain unknown. No fabricated
token or cost forecast is offered.

Family coverage is complete for this cycle only because the three planning
contributors are three different families. **There is currently no fourth
verified family route available for implementation work.** That single fact
drives the staffing below: the WS component can be corrected and reviewed
today (Anthropic author → OpenAI reviewer), while the privacy chain's
*acceptance* cannot be, because its source is OpenAI-authored and no
non-OpenAI privacy reviewer is qualified.

## 5. Decision request 4 — task / model / reviewer matrix, bases, paths, acceptance, reserve

| # | Package | Author | Reviewer | Exact base rule | Exclusive writable paths | Evidence / acceptance | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | WS-WORK-01 component correction (WSR-01..04) | Anthropic `claude-opus-5-5`/high — **the actual author of `15c069bd`**, continuity, no relabelling | OpenAI `gpt-6-astra`/high (already qualified in this domain; did not author the component) | Base = `15c069bdeb3a9ace37bf68033812ff72659bfbd1` exactly, so the reviewed diff is only the fix; `resolve_to_exact_full_sha_before_creation` per the pin rule; coordinator integrates later onto `wp-runtime-completion` | `src/rest_api/ws_request_work.py`, `tests/test_ws_request_work.py`, NEW `docs/production/remediation-20261104/WS-WORK-01/CORRECTION-01.md`; ignored `build/remediation-recovery-20261104/ws-correction/**`; fresh `C:/t/remediation-recovery/ws-correction/**`. The original AUTHOR.md (`028d8007…`) is immutable | WS-I1..I7 hold; WS-T1..T5 fail on the unfixed candidate and pass on the fix; focused run + relevant websocket/events/lifecycle regressions; the preserved WSR-01 gap reproductions re-run at the corrected commit; correction report records the honest asyncio-debug status (WSR-04) and the WSR-03 boundary compliance | **Technically ready.** Ordinary author fix + qualified different-family re-review. CR-01 still open |
| B | Privacy source correction on the retained C1/C2/C3 chain (J-1, N-1..N-7) | OpenAI family, **the actual chain authors** (C1 `task_cf272c0e3b6c`, C2 `task_4e33d0624489`, C3 `task_242c1cc61b92`, `gpt-6.1-sol`/high) — continuity preferred; a new OpenAI-family author is acceptable if the originals are unavailable | **Qualified non-OpenAI privacy reviewer — none exists today.** OpenAI cannot review its own source; Anthropic failed the domain; MiniMax is not qualified; Gemini is unavailable/unverified | Base = chain tip `2d02004d3108953a302e1a49aab9a5f24e944136`, review base `d6e78e0b6ab1dab5216443584d810a7a24af32b2`; correct on top of the tip so the chain stays linear | `tools/validate/evidence.py`, `tools/validate/model.py`, `tools/validate/runner.py`, `tools/validate/clients/api.py`, `tests/validation/test_sw_sec_data_02_c1.py`/`_c2.py`/`_c3.py`, NEW correction report. **Coordinator serial lease required** (see below) | PRIV-I1..I5 + PRIV-T1..T5; the judge's gap reproductions re-run at the corrected commit; existing C1/C2/C3 assertions must still pass (the author must check, I did not) | **Authoring technically ready; acceptance held** on a qualified non-OpenAI reviewer |
| C | Privacy reviewer qualification (the long pole) | Step C1: a *new* family's first privacy-review candidate — only if the route is verified. Step C2: the qualified candidate performs RV-PRIVACY-CHAIN source review | Judge for C1: OpenAI `gpt-6-astra`/high (qualified in this domain; not the source author) | C1 on the **corrected** chain tip; C2 at the exact corrected commit | NEW assessment report; NEW `docs/production/software-waves/RV-PRIVACY-CHAIN/execution-20261101/REVIEW.md`; own ignored/temp | C1: all six mandatory axes, judged independently, no expected PASS; an accepted reviewer artifact bound to the privacy domain. C2: qualified different-family exact-commit review, reviewers report only | **Provisional.** Blocked on route verification (§7 W3a). Not a retake: a first attempt by a family with no prior record |
| D | WS wiring / CR-01 closure | Anthropic (continuity) or OpenAI `gpt-6.1-sol`/high — but see the reviewer constraint | If OpenAI authors, the reviewer must be Anthropic/MiniMax/Gemini, none qualified for concurrency; therefore **Anthropic author + OpenAI Astra reviewer** is the only currently sound pairing | Gated on A's accepted commit; the wiring base is the coordinator's frozen combined candidate | Existing `src/rest_api/websocket.py`, `src/rest_api/app.py` → **coordinator-owned contract + exact serial lease**; `docs/validation/features.yaml` and `tests/sim/test_sim_rest_reads.py` are coordinator-owned; `python -m tools.validate ledger` run serially with registry checks | Real aiohttp `/ws` burst, disconnect and shutdown tests; app-owned key; cleanup order drains request work before destroying the event stream/runtime; cancellation-safe `finally`; truthful remaining-work handling; public WS schema unchanged; 100% route coverage preserved | **Provisional**, gated on A + a coordinator contract decision (rejection vs coalescing) |
| E | API034 M-1 security freshness | — | — | existing pin `caaa4faa…` | existing | branch-correct new browser/API proof + qualified security review + combined input/admission checks | **Held** — unchanged, see §6 |
| F | RV-WS040 | `claude` reviewer route per pin | `sol` evaluation per pin | pin `1fbfee11…`, review base `938ae303…` | pin paths | its domain is "rendered browser/kiosk websocket/persistence/accessibility behavior" and `accepted_reviewer_artifact` is `null` | **Held** on the same class of gap as C (no qualified reviewer artifact for that domain); the Opus5.5 API-refusal artifact does not cover browser/kiosk rendering |

**Shared-path and ordering facts I verified myself (not in the packet).**

- The privacy chain and the retained API034 chain **both** modify
  `tools/validate/model.py` and `tools/validate/runner.py`
  (`git diff --stat 938ae303… caaa4faa… -- tools/` shows model.py +12 and
  runner.py +28/−3; the privacy chain's changed paths include the same two
  files). Any privacy correction therefore collides with the retained API034
  source and needs **coordinator-sequential integration** (the accepted plan's
  A3 "compose and freeze — resolving shared runner/model/evidence/API
  conflicts"). The two packages must not be edited in parallel by two writers.
- `RV-PRIVACY-CHAIN`, `RV-WS040` and `RV-API034` all carry
  `dispatch_allowed_now: false` and `accepted_reviewer_artifact: null` /
  `accepted_author_artifact: null`, with the gate text "existing bounded
  competence or candidate-domain evaluation must be recorded, not inferred
  from model/catalog/plan approval" and "null is not qualified". This is the
  machine-readable form of the blocker, and it applies to **three** review
  units, not only privacy.
- `RV-WS040`'s `original_implementation_author_family` is OpenAI and its
  `source_reviewer_route` is `claude`; its accepted reviewer artifact is null.
- The WS component is **not wired** and nothing imports it; the wiring package
  (D) is therefore genuinely separate work, not a continuation of the
  correction.

**Reserve.** One reviewer slot must be reserved for each correction (A needs an
OpenAI Astra re-review; B needs a non-OpenAI privacy reviewer once one exists),
plus material-correction capacity if a reviewer returns findings. Under the
ceiling of four active agents (coordinator + at most three workers, and the
standing reservation of at most two *new* workers plus one protected external
process) the arithmetic is tight and it decides the ordering: two new workers
can run while the coordinator and the protected external reservation hold the
other two slots, so **a reviewer cannot run concurrently with two authors**. One
author must settle before its reviewer starts.

## 6. Decision request 5 — holds, dependencies and other ready work preserved

- **API034 M-1 security freshness stays held.** Static diagnosis is not unit
  completion; it needs branch-correct new browser/API proof, a qualified
  security review and combined input/admission checks. Nothing here proposes
  regenerating canonical security evidence before the source freeze, and the
  earlier below-30% OpenAI observation that held the affected dispatches is
  superseded by the fresh 91%-remaining reading — but capacity was never the
  binding reason for that hold and is not treated as one now.
- **The retained WS040 and privacy chains keep their actual authorship and
  bytes.** No relabelling, no rewriting of `AUTHOR.md` (`028d8007…`,
  `7b469ade…`), no replacement of the OpenAI chain authorship with another
  family, no replacement judge for the failed privacy assessment.
- **Combined-source proof dependencies are preserved.** Privacy C1/C2 are
  already contained in C3 and API-client C1 in C2; the corrected privacy source
  must be merged with the retained API034 source by the coordinator before any
  candidate-specific evidence is regenerated, because both chains touch
  `tools/validate/model.py` and `runner.py`.
- **Physical/HIL/soak/week/final-release gates are untouched.** Nothing in this
  assessment proposes approving a Tron snapshot, physical HIL, the 72-hour
  soak, week field sign-off, a version or an artifact.
- **Other ready packages.** The A2 items for HA credentials (CR-02) and UI
  shortcuts/accessibility (CR-03) are separate units with their own
  environment and evidence needs (real HA; real browser) and are **not** blocked
  by either qualification gap in §5. They are technically ready and the
  standing rule is explicit: capacity constrains routing, not continued
  development. They should be scheduled into whatever worker slots the
  recovery sequence leaves, rather than being queued behind the privacy
  reviewer gap, which is the only genuinely blocked item.

## 7. Decision request 6 — minimal recovery wave order, exit conditions, alternatives

| Wave | Content | Exit condition | Slots |
| --- | --- | --- | --- |
| W0 | This planning cycle: R1 (OpenAI + MiniMax, then Anthropic on the same frozen packet) → R2 (every participant reads every preserved peer report) → R3 (one hashed final plan/allocation, each participant states accept / require_changes / blocked) | One final packet hash; three recorded explicit verdicts; no unresolved material blocker | 2 new workers + coordinator + protected external; no nesting |
| W1 | Package A — WS component correction by the original author | Corrected commit + correction report; WS-I1..I7 hold; WS-T1..T5 fail pre-fix and pass post-fix; component acceptance granted **only** if the qualified OpenAI re-review at that exact commit passes | 1 author, then 1 reviewer (after the author settles) |
| W2 | Package B — privacy source correction by the OpenAI chain authors | Corrected commit + correction report; PRIV-I1..I5; PRIV-T1..T5; existing C1/C2/C3 assertions still pass; **acceptance explicitly still held** | 1 author, concurrent with W1 |
| W3a | Route verification for a third family (read-only): catalog presence, account/entitlement, supported launch selection, observed native model ID, family attestation, fresh headroom | A written record: verified usable route, or a recorded negative. `gemini` currently reports `unavailable`; `antigravity`'s family is unresolved — an unresolved family cannot satisfy cross-family review | coordinator only, no new worker |
| W3b | Package C1 — first privacy-review candidate of the verified new family, on the corrected chain | Six mandatory axes judged independently by a fresh OpenAI Astra judge; an accepted reviewer artifact for the privacy domain, or a recorded failure | 1 candidate + 1 judge (sequential) |
| W3c | Package C2 — RV-PRIVACY-CHAIN source review by the qualified candidate | Qualified different-family exact-commit review of the corrected chain; privacy evidence admission decided then, not before | 1 reviewer |
| W4 | Package D — WS wiring / CR-01 closure | Accepted component + coordinator contract decision + real aiohttp lifecycle tests + registry/ledger updates | 1 author + 1 reviewer |
| W5 | Coordinator-only compose/freeze and candidate-specific evidence | One combined candidate with resolved shared paths; no evidence regenerated before the freeze | coordinator |

**Why implementation starts after W0, not during it.** The ceiling is four
active agents: coordinator, the protected external reservation, and at most two
new workers. R2 needs all three families to read peers and respond, and R3
needs all three on the final packet; with two worker slots, those rounds
consume both slots, staggered. No implementation worker can exist during R1,
R2 or R3. Since the packet itself states that no implementation is authorised
by a planning report, the honest reading is that W1 starts when the R3 verdict
settles — not sooner. I flag this because it is easy to believe a wave can be
overlapped.

**Alternative routes and trade-offs.**

- *Alternative 1 — a new OpenAI-family author for the WS component.* Rejected:
  it would forfeit the only qualified reviewer pairing available (a non-OpenAI
  concurrency reviewer does not exist) and would relabel authorship for no
  gain.
- *Alternative 2 — MiniMax authoring the WS correction.* Technically possible
  (MiniMax is a distinct family from OpenAI, so OpenAI Astra could review),
  but it discards continuity with the failing component, and MiniMax has no
  demonstrated asyncio authorship competence and no effort control. Only
  justified if the Anthropic route becomes unavailable.
- *Alternative 3 — a second Anthropic privacy candidate (owner decision, §8).*
  Available but the weakest of the three: the failed axes were dataflow,
  calibration and review quality — i.e. overclaiming breadth — which a repeat
  attempt under the same model does not obviously fix.
- *Alternative 4 — hold the privacy chain entirely until the WS work
  finishes.* Costs nothing but delays A1; acceptable as a fallback, not as a
  first choice, because the privacy source currently leaks a supported
  credential into persisted evidence and is therefore not admissible.
- *Alternative 5 — use Antigravity as the third family without verification.*
  Rejected: unresolved underlying-backend identity is explicitly not
  cross-family proof.

**Unresolved blockers, stated plainly.**

1. No verified non-OpenAI privacy reviewer exists; the supported usage source
   reports `gemini` unavailable, so W3b may never become launchable.
2. The `antigravity` surface reports usable headroom but its family/routing is
   unresolved; it cannot be counted as a family until observed.
3. The privacy chain's correction touches files shared with the retained
   API034 chain; a coordinator merge step is mandatory and its outcome is not
   predictable from here.
4. The WS component remains unwired, so CR-01 cannot close in W1; W4's real
   aiohttp lifecycle evidence is the actual proof and it does not exist yet.
5. Whether the Opus5.5 WS author can be re-dispatched on the same route with
   verified capacity and native entry attestation is a coordinator preflight
   fact, not something this assessment can establish.

## 8. Concrete authorization question for the owner

One question genuinely needs the owner. Everything else in §7 is covered by
the existing "enact comprehensive remediation" authority plus this accepted
plan.

**Question.** The Anthropic Opus5.5 privacy-review domain assessment is
exhausted: one candidate and one fresh judge were used, and
`COORDINATOR_DISPOSITION.json` records `future_automatic_retry_authorized:
false` with `attempt_budget.candidate_evaluations: 1` and
`independent_judges: 1`, while `ASSESSMENT_PACKET.json` states "ONE new
domain-assessment candidate and ONE fresh judge. No automatic rewrite/retry/
extra judge." A *second* Opus5.5 privacy candidate therefore needs an explicit
owner authorisation that expands that attempt budget. Do you authorise it?

Prepared choices, with the rule each one rests on:

- **Option 1 (recommended): authorise the new-family route in this plan.**
  Authorise the coordinator to run W3a route verification and, if and only if a
  third family is verified, ONE first privacy-review candidate of that family
  plus ONE fresh OpenAI Astra judge, then that candidate's RV-PRIVACY-CHAIN
  review. This is *not* a failed-qualification retry: it is a first attempt by
  a family with no prior record, and a material family-allocation change,
  which is what this three-round cycle exists to decide. If this plan is
  accepted at R3, this option needs no separate owner statement. If W3a finds
  no verifiable route, Option 1 collapses and Option 3 applies.
- **Option 2: authorise one additional Opus5.5 privacy candidate + one fresh
  Astra judge.** This explicitly expands a failed assessment's attempt budget.
  It repeats a model whose failure was in overclaiming breadth, so it is the
  weakest of the available routes even though it is the easiest to schedule.
- **Option 3: hold the privacy acceptance.** The WS correction, the WS wiring
  and the other A2 packages proceed; the privacy chain and its evidence
  admission stay held until a qualified non-OpenAI privacy reviewer exists.
  Cost: A1 stays open and the supported `current_pin` disclosure stays
  uncorrected in the retained source.

My assessment: Option 1, with Option 3 as the fallback and Option 2 only if
the owner prefers one family over the delay. I do not recommend asking for
confirmation of facts already settled by the owner's direction, and I do not
treat every option as blocked: W1, W2, W3a and the other A2 packages need no
owner decision at all.

## 9. Readiness classification

| Item | State | Reason |
| --- | --- | --- |
| WS component correction (A) | **Technically ready** | Ordinary author fix + an already qualified different-family reviewer; no new authority |
| Privacy source correction authoring (B) | **Technically ready (author side)** | Ordinary author fix; acceptance explicitly held |
| WS wiring (D) | **Provisional** | Gated on A's acceptance and a coordinator contract decision |
| New-family privacy reviewer (C) | **Provisional** | Gated on W3a route verification; `gemini` currently unavailable |
| RV-PRIVACY-CHAIN acceptance | **Held** | No qualified non-OpenAI privacy reviewer |
| RV-WS040 | **Held** | `accepted_reviewer_artifact` null for the browser/kiosk domain |
| API034 M-1 security freshness | **Held** | Needs branch-correct proof + qualified security review |
| HA credentials (CR-02), UI shortcuts (CR-03) | **Technically ready, independent** | Not blocked by either qualification gap |
| All hardware / HIL / 72-hour soak / week / version / artifact gates | **Open and untouched** | Outside every route above |

## 10. Limits of this assessment

- Prose and reasoning only. I ran no product code, no privacy reproduction and
  no asyncio probe; the WS and privacy *defects* are attributed to the two
  completed reviews, and the mechanisms I restate are read from the frozen
  source I read myself at the exact commits named.
- The invariants in §2 are a correction design, not a validated patch. The
  eventual author must confirm feasibility, and the eventual reviewer must
  confirm correctness at the exact commit.
- I did not read the WS callers, the HA client, the privacy chain's test
  modules, or any native transcript; those limits are listed in §0.3 and are
  real.
- No peer R1 report was read; no consensus is claimed, no permission to start
  implementation is granted, and no prior negative result is altered.

### 10.1 Checks actually run

One invocation of the five existing documentation modules, after this prose,
in this checkout, with the root virtual environment
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(Python 3.12.10, pytest 9.1.1) and the checkout as the working directory:

`python -B -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -q -p no:tests.route_inventory -p no:cacheprovider --basetemp=<owned>/docs/pytest-tmp --junitxml=<owned>/docs/junit.xml`

with a copied Windows OS environment and isolated owned `MATRIX_DATA_DIR`,
`UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`, bytecode disabled, fresh basetemp
and JUnit under `C:/t/remediation-recovery/minimax-r1/`.

Result, actual: **489 passed, 0 failed, 0 errors, 0 skipped, direct child exit
0**, stdout 588 bytes, stderr empty, 3.47 s, 2026-11-04T08:47:16Z to
08:47:20Z. JUnit 63,691 bytes. The direct argv, the child exit code and the
full stdout/stderr streams are retained under
`C:/t/remediation-recovery/minimax-r1/docs01/` (`argv.json`, `result.json`,
`exit_code.txt`, `stdout.txt`, `stderr.txt`, `junit.xml`). One run only; no
retry and no softened assertion.

Measured import origins (`import_origins2.json`): the five documentation test
modules, `tests/conftest.py` and `tools/validate` resolve to **this checkout**;
the `hub` package resolves to the root checkout
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/src/hub` through the
root venv's editable install. That difference is path-only: the root
checkout's `src` tree object at its HEAD `30631e62…` is `5b78baa117e7511a34c641f0f37bf9c9cfff7134`,
**identical** to this checkout's `src` tree, and the root working tree has no
modification under `src`. My first origin-measurement script failed with
`AttributeError: module 'sys' has no attribute 'getcwd'` (exit 1, stderr
retained as `import_origins.stderr.txt`); it was a measurement-script error,
not a test result, and no test was re-run.

This is scoped documentation maintenance, not a source-hook pass, not a
full-suite result and not a runtime or model qualification.
