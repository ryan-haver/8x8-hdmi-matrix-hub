# Remediation recovery R1: Anthropic independent assessment

**Status: R1 independent prose assessment only.** This is not consensus, a source
correction, a qualification retake, source acceptance or permission to launch any
worker. It was written without reading any peer R1 report. Prior negative results
are restated unchanged. The recommendations favour some Anthropic roles; R2 peers
should challenge them on structure and evidence, not on family.

## 1. Bindings and visibility

| Item | Value |
| --- | --- |
| Contributor | Anthropic `claude-opus-5-5`, Task `task_ad18152bbe0f`, Dispatch `ctx_af51d4d4295c`, native Claude Code session. Effort `high` is the dispatch assignment; I cannot measure per-turn effort. No helpers, subagents, plugins or MCP routing used |
| Checkout | `wp-remediation-recovery-r1-anthropic`, branch `planning/remediation-recovery-r1-anthropic`, base `b13ddc4de461b7e1072fead0d39361bcb079282f`, clean at entry |
| Integration pin | `wp-runtime-completion` resolved once at entry: `e0c6978423d4b04fcd82bbba8aca37c9f2e8f8f3` (local and `origin` equal) |
| Input packet | `INPUT_PACKET.json` blob at the pin, 10,876 bytes, LF SHA-256 `40526f127575feead63c94058250a868e0452ccb19b5552f60be66b6b82b77dc` (matches the assignment) |
| Peer isolation | `ROUND1_DELIVERY_METADATA.json` and any peer round1 report were not opened. Only my own `tasks/anthropic-r1.md` from the pin was read |

Immutable inputs I read at their exact commits (canonical LF SHA-256):

| Record | Commit | SHA-256 |
| --- | --- | --- |
| WS-WORK-01 `REVIEW.md` (full) | `1cc44220` | `6ee8bbec66ebdb7e650aa8b08e8f75026ec8580c40ed89b1a2f06e6104d85adb` |
| `src/rest_api/ws_request_work.py` (all 412 lines) | `15c069bd` | `3bc116d88029aeecdbec5fdce7590e5d623442e37049a9bc4c7bf9489d3031c5` |
| `tests/test_ws_request_work.py` (test list and fixtures only) | `15c069bd` | `2628c0734fa4860ba53fc30d53a246408dbc4b88fc9b2d5a9ba16c500ea7945b` |
| WS-WORK-01 `AUTHOR.md` (full) | `15c069bd` | `028d80071084a988f47e07272785a8ec72940a8302808c907f1b57beea8c24fc` |
| Privacy `REVIEW.md` judgement (full) | `e8ce3966` | `e9efab38d4eb81c2d352195d33952559f2fee0139a989f43a3e4dd1524920582` |
| Privacy candidate `AUTHOR.md` (full) | `1a38e285` | `7b469ade0388e0de5a46051528992bfb675ba43addd871c48fdaeaf48aa01f2c` |
| Privacy chain source (`evidence.py` redactor, `clients/api.py` request/perform, `model.py` describes, `runner.py` record/check/summary ranges, `clients/ha.py` HTTP/flow/steps ranges) | `2d02004d` | ranges only, see limits |

Coordinator records read from the pin (LF SHA-256): `ORCHESTRATION_PROTOCOL.md`
`714fd177…34c4`; `agent-process/PROTOCOL.md` `4aeb2351…c052`; `REPO_CONFIG.json`
`67dd58d9…3843`; `COMPREHENSIVE_REMEDIATION_20261104.md` `af3ca3de…831e`;
`EXECUTION_PINS.json` `e68f1ff2…5b1d` (the `RV-PRIVACY-CHAIN`, `RV-WS040`,
`RV-API034`, `EV-API034-SECURITY-REFRESH` pins and the global, bottleneck and
qualification-failure policies only); `WS_WORK_TASK.md` `5cee3eb8…8998`; privacy
`ASSESSMENT_PACKET.json` `17327093…7dd8`; Opus 5.5 `COORDINATOR_DISPOSITION.json`
`d2096e6e…9e79`; `AGENTS.md` `f09377ad…3d94`. `AGENTS.md` and both protocols are
byte-identical between my base and the pin.

**Limits.** I did not read native transcripts, private roots, the privacy chain's
test modules, product `security.py`, HA `config_flow.py`, or the full `runner.py`
and `model.py`. Statements about `current_pin` consumers, the HA options
`api_key` schema, the real-loopback `gap01` result and the WS `02-gap-probes`
result are the judges' attributed evidence; I did not rerun them. I read the WS
test file's function list and fixtures, not every assertion. I did not query
quota. Capacity figures below are the packet's 08:32:18Z observation.

## 2. Prior results, unchanged

- **WS-WORK-01 (Opus 5.5 first authorship, candidate `15c069bd`):** component
  correctness FAIL; component acceptance and bounded first-authorship HOLD. Axes:
  provenance/boundaries FAIL (WSR-03), admission PASS, lifecycle FAIL (WSR-01),
  isolation PASS, tests PASS (bounded), calibration HOLD. 44 focused and the full
  4,126-test hook pass. The four eager reentrant drain probes fail. Not wired.
- **Privacy-review assessment (Opus 5.5, report `1a38e285`):** two PASS
  (provenance, counterexamples) and four FAIL (dataflow, behaviour/tools,
  calibration, review quality). J-1 `current_pin` missed. HA options `api_key`
  missed. N-1 to N-5 and N-7 were under-classified. No owner-secret incident is
  claimed. The privacy source chain stays unreviewed and unaccepted.
- **Opus 5.5 API-refusal qualification (`dda63d66`):** PASS for its bounded
  runner/model refusal-preparation review scope only. Not regraded or extended.
- Earlier Opus 4.7 FAILs and every recorded failed run stay as recorded.

## 3. WS component: correction invariants and tests

The source confirms the review. `WorkOwner.aclose` (`ws_request_work.py:246-249`)
and `WsRequestWork.shutdown` (`:409-412`) snapshot only registered `_tasks`.
`_admit` (`:352-373`) holds `_reserved` while `factory()` and an eager first step
run. A cleanup coroutine running in that window sees no tasks, and
`_wait_bounded([])` returns 0 without suspending. The post-registration cancel at
`:376-379` cannot change a report that has already been returned. A reservation
can only exist during one synchronous `_admit` stack. An eager task that suspends
makes `create_task` return, and registration follows. So a drain can observe a
reservation only reentrantly: from the factory, from an eager cleaner it spawns,
or from the admitted task's own eager first step.

**WSR-01 invariant D1 (truthful drain).** When `aclose`/`shutdown` returns,
`remaining` equals the scope's live count. The live count is not-done tracked tasks
plus outstanding reservations for that owner (or for the application).
`drained` therefore implies no live task and no reservation in scope at return.
Keep the `DrainReport` fields and meanings. `requested` should count the
admissions that this call's close covered, including reservations. This is a
semantic correction, not a new public field.

**Mechanism (author's choice; reviewer judges behaviour).** After `close()`, take
a fresh snapshot of tasks and reservations in a loop until a single monotonic
deadline (`loop.time()`). Wait on the scope's live tasks plus an "admission
settled" future that `_admit` resolves in its `finally`. Exclude
`asyncio.current_task()` from the wait set, but count it as live. Return at once
when the only live item is the caller itself or the deadline has passed. With
`timeout=0`, a pending reservation is counted, not ignored. A stricter fallback
also preserves truth: report every outstanding reservation as remaining without
waiting. A drain awaited inside the admitted task's first step may instead
receive the post-registration cancellation, propagating `CancelledError` as
documented. That is truthful as long as no `drained` report is produced. Clearing
or omitting a reservation, or "cancel after registration" alone, does not satisfy
D1.

**WSR-02 invariant L1 (lifecycle loop binding).** Once a loop is bound,
`close`, `aclose`, `begin_shutdown` and `shutdown` raise `RuntimeError` before any
state change when called from a different running loop. Recommend enforcement:
the planned wiring calls these on the app loop, so it costs little and makes the
documented guarantee true. Narrowing the prose to admission-only is an acceptable
alternative only as a calibrated correction with an explicit reason, not to pass
the rubric. Calls made before any binding, or with no running loop, need one
documented, tested rule.

**WSR-04 calibration.** The correction report must say plainly that receipt 45
was not asyncio-debug coverage. Any debug claim needs a run that actually enables
plugin debug (the reviewer cites `--asyncio-debug` / `asyncio_debug=true` for
pytest-asyncio 1.4.0; verify, don't assume) and an in-test
`loop.get_debug() is True` observation. Old runs are not relabelled.

**WSR-03 process boundary.** The correction assignment must state that the harness
default scratchpad is outside the lease. Every script, message file and probe goes
in the assigned roots. The re-reviewer audits the native transcript for writes
outside those roots. The original WSR-03 violation stays recorded.

Required new negative tests (additive; the 44 existing assertions are not weakened):

| ID | Case | Oracle |
| --- | --- | --- |
| W1 | The four probe shapes (owner/application cleanup from a synchronous factory via an eager cleaner, and awaited in the admitted eager first step), each with resistant and cooperative bodies, `timeout` 0 and small positive | Real `eager_task_factory`; `remaining` equals an independent live count from `asyncio.all_tasks()` and gates; resistant implies `drained is False` and `active_count` still held; cooperative `drained` only when the task is actually done |
| W2 | Self-drain from inside the admitted task | Never `drained` while the caller lives; bounded, observed by actual return or propagated cancel, not by sleep |
| W3 | Drain-waiter cancellation while a reservation is outstanding | Scope stays closed, the task stays tracked, capacity held; a later drain is truthful |
| W4 | Owner scope ignores other owners' reservations; application scope includes them | Per-scope counts |
| W5 | Each lifecycle method from a second loop (if L1 is enforced) | `RuntimeError`; `closing`, `owner.closed` and `task.cancelling()` unchanged; same-loop call still works |
| W6 | Debug-enabled focused run | Recorded `get_debug()` true |
| M | Mutants: drain snapshot without reservations; no re-snapshot; reservation omitted from `remaining`; no post-registration cancel; loop check removed | Each detected by W1-W5 with direct non-zero child exit |

Unchanged acceptance: items 1-6 of `WS_WORK_TASK.md`, the normal source hook once
at the final candidate, and the existing websocket/events/lifecycle regression set.

## 4. Privacy chain: correction invariants and tests

Source facts at `2d02004d`: `_SECRET_KEYS` (`evidence.py:115-118`) anchors
`pin` but not `current_pin`. Its unanchored `pass(word|code)?` over-masks public
booleans. `redact` (`:125-133`) traverses only `dict` and `list`, and strings get
query masking only. `ApiClient.request` accepts header pair lists through
`dict.update` and forwards `data=` untouched (`api.py:121,110-111`).
`_write_summary` (`runner.py:1026-1037`) writes `Outcome` through plain
`json.dumps`, and `Outcome.reason` carries raw blocked-exception text.
`Hub.describe` (`model.py:343-350`) formats the raw path. HA `perform`
(`ha.py:490-492,516`) formats raw `r['body']`, including flow `options`, into
steps. `_http` raises with response `text[:300]` (`ha.py:273`).

| ID | Invariant | Addresses |
| --- | --- | --- |
| P1 | Contract-driven credential names: one enumerated set taken from product carriers (headers `X-Admin-PIN`, `X-API-Key`, `X-Passcode`, `Cookie`, `Set-Cookie`, `Authorization`; query `key`/`api_key`/`token`/`passcode`/`password`/`pin`; body `pin`, `current_pin`, `passcode`, `current_passcode`, created-key `key`; HA options `api_key`) is masked in every casing at every sink | J-1, N-7 |
| P2 | Shape completeness: tuples and any `Mapping` are traversed. Header pair lists are either masked or rejected before transmission. A `data=` string that decodes as a JSON object or array is masked structurally for diagnostics only. Arbitrary non-JSON text is a documented Low limitation with query masking | N-1, N-2, N-3 |
| P3 | Sink completeness: every persisted or emitted byte goes through structured masking before formatting. That covers `write_record`, `run-summary.json` (`failed_checks`, `reason`), notes, `blocked_reason`, cleanup procedure lines, `Hub` describe/detail, HA steps and HA error text | N-4, N-7 |
| P4 | Raw preservation: on-wire method/path/headers/body unchanged; raw `ActionResult` and request captures keep identity; `_subset` and header checks compare raw values; verdicts unchanged | Raw request and verdict fidelity |
| P5 | Public fidelity: named public fields stay byte-identical. One option is to leave `bool`/`None` values of matching names unmasked (`password_protected`, `passcode_locked`, `requires_scene_passcode`). The created-key `key` stays masked even though this loses `shortcut_alias` `data.key` fidelity, unless a route-aware rule is tested both ways | N-5 |

Tests (new `test_sw_sec_data_02_c4.py`; C1-C3 tests stay unchanged and must still pass):

- **End-to-end byte oracle:** a synthetic marker in every P1 carrier and P2 shape,
  across matched, mismatched, blocked and cleanup-failure lifecycles through the
  real `ApiClient.perform`, `Runner._run_one`, `_check`, `write_record` and summary
  writer. Scan every file under the output and evidence roots, plus captured
  log records, for zero marker hits. Assert that public controls are present.
- **HA path:** a loopback fake of the HA flow endpoints driving
  `ha_config_flow(options={"api_key": marker})`. Synthetic only; not HA review
  qualification.
- **Catalogue sweep** over the real scenario definitions. Over-mask counts are
  unchanged or each change is justified. `current_pin` actions and cleanups mask.
- **Selective in-memory reversion** of each new mask (ignored-root plugin, not a
  committed tool). Each must fail the byte oracle with a direct non-zero child exit.

Severity stays as judged (J-1 Medium, N-1 to N-4 and N-7 Medium conditional, N-5
Low, N-6 Info). Fixtures are not owner secrets, and no incident is asserted.

## 5. What existing authority covers

| Step | Authority | Basis |
| --- | --- | --- |
| Opus 5.5 corrects its own unaccepted WS component | Covered | Orchestration protocol "Reviewers report; authors fix. Re-review exact corrected source"; comprehensive plan A2 exit; owner "remediate all findings". A deliberate coordinator assignment, not the "automatic rewrite/retry" barred by `WS_WORK_TASK.md` |
| `gpt-6.1-sol` (original author) corrects the privacy chain as C4 | Covered | Same rules. The `ha.py` addition is a coordinator serial lease under the shared-path rule |
| Astra re-reviews the corrected WS component | Covered | Same reviewer, different family, exact commit |
| A first privacy-review assessment by Gemini or MiniMax | Needs this cycle's R3 | It changes the `RV-PRIVACY-CHAIN` reviewer-family allocation (claude review, sol evaluation in the pins); adopted protocol §6 requires a three-round cycle, which this is. No owner step, unless the route needs login, credentials or spend, which are not authorized |
| Treating the corrected WS re-review as a first-authorship PASS | Not allowed | It would be a retrospective PASS. Axis 1 (WSR-03) is an attempt-level failure that correction cannot erase |
| A second Opus 5.5 privacy-review or WS-authorship assessment | Owner choice, held | Assessment packet `attempt_authority` allows one candidate and one judge; the privacy judgement says no retake or additional assessment is authorized; adopted protocol §4 and §6 and AGENTS bar automatic or capacity-driven retries. A coordinator-chosen retake is the automatic retry the rules prohibit. Owner remediation authority targets findings, not qualification budgets |

A correction can earn **component** acceptance. It does not earn Opus 5.5 **WS
authorship** competence. Under `WS_WORK_TASK.md`, an existing-handler (wiring)
lease needs demonstrated authorship competence, so wiring stays held.

## 6. Model and family assessment

| Model / route | Family | Accepted evidence | Not granted or failed | Proposed use |
| --- | --- | --- | --- | --- |
| `claude-opus-5-5`, native, high assigned | Anthropic | API-refusal review PASS; planning prose | Privacy review FAIL; WS authorship not earned; no wiring lease | WS correction author; in-domain API-refusal work only after a fresh exact domain match (provisional) |
| `gpt-6-astra`, Codex, high | OpenAI | R8D async review; WS-WORK-01 review; privacy judge | Cannot review OpenAI source | WS re-reviewer; judge of a new-family privacy assessment; fallback C4 author (then it cannot judge) |
| `gpt-6.1-sol`, Codex, high | OpenAI | Authored C1-C3 (unreviewed); core implementation role | Current route and selection not in the packet | C4 author after route verification |
| `MiniMax-M3`, opencode2, effort override unsupported | MiniMax | Planning, prose, inventory | No code-review or privacy competence | Independent inventory routes; fallback first privacy-review assessment, with a weak prior stated up front |
| Gemini (exact route unknown) | Google | None in project for this domain | Route, helpers, family, access and quota unverified | Preferred first privacy-review candidate if read-only discovery verifies it; possible later async-review candidate |
| Another catalogued Anthropic model | Anthropic | None | Unverified | A genuine first candidate only with exact catalogue and launch proof; not preferred |
| DeepSeek | DeepSeek | n/a | Owner-excluded | None |

Structural constraint: every retained privacy, WS040 and API034 chain is OpenAI
source, so it needs a non-OpenAI qualified reviewer. Today only Opus 5.5 has one,
and only within the API-refusal scope. For WS, the reviewable pairing is
Anthropic author with OpenAI reviewer. An OpenAI fix to Opus's component would
need a non-OpenAI reviewer that does not exist. Capacity at 08:32Z: Codex 8%
weekly used, Claude 25% weekly / 0% session, MiniMax 33% weekly / 15% session;
Google unknown. All are above the 30%-remaining line, but absolute allowance and
other-host demand are unknown. Codex hosts Sol and Astra in one shared pool.

## 7. Task matrix

| Task | State | Author / reviewer (fallback) | Base rule | Exclusive writable | Exit |
| --- | --- | --- | --- | --- | --- |
| T1 `WS-WORK-01` correction 1 | Technically ready (covered) | Opus 5.5 / Astra (Sol 6.1 only after explicit async-domain match; otherwise hold review) | Fixed candidate `15c069bd` | `src/rest_api/ws_request_work.py`, `tests/test_ws_request_work.py` (additive), NEW `docs/production/remediation-20261104/WS-WORK-01/CORRECTION-01.md`, own ignored build and fresh `C:/t` roots | D1, L1 and WSR-04 met; W1-W6 and M; hook once; original AUTHOR unchanged |
| T2 WS exact-commit re-review | After T1 | Astra / Opus is author | T1 commit against `460a1905` | New review file plus reviewer roots | Every WSR disposition recorded; component-only verdict |
| T3 `SW-SEC-DATA-02-C4` | Technically ready (covered); review held | Sol 6.1 (Astra fallback) / held: no qualified non-OpenAI privacy reviewer | Fixed `2d02004d` | `tools/validate/evidence.py`, `clients/api.py`, `clients/ha.py` (new serial lease), sink hunks of `runner.py`/`model.py`, NEW C4 test and C4 AUTHOR | P1-P5, byte oracle, reversions; source hook once |
| T4 Gemini route discovery | Ready (coordinator, read-only) | Coordinator | n/a | Coordinator records | Catalogue, access, launch selection, family, helpers, quota recorded, or held |
| T5 first privacy-review assessment | Provisional (needs R3, plus T3 and T4) | Gemini, else MiniMax / Astra judge | Exact C4 tip against `d6e78e0b` | New assessment report plus roots | Six unchanged axes, one judge, no retry |
| T6 `RV-PRIVACY-CHAIN` source review | Held (needs T5 PASS) | Qualified T5 family / evaluation per pins | Exact C4, or a later corrected tip | Pinned review paths | Different-family exact review; Sol fixes; re-review |
| T7 CR-01 wiring | Held | No qualified route today | Accepted component | Coordinator-leased `websocket.py`/`app.py` | Section 5 constraint |
| T8 Opus in-domain `RV-API034` portion | Provisional | Opus 5.5 / Sol evaluation per pins | Pinned `caaa4faa` against `938ae303` | Pinned paths | Coordinator confirms the scope is fully inside the qualified domain; serial with T1 |
| T9 MiniMax inventory routes | Ready per existing pins | MiniMax / per pins | Per pins | Per pins | Unchanged |

Overlap the coordinator must own: `tools/validate/runner.py` changes in the privacy
chain (~918), API034 (~466-622) and WS040 (~536). `model.py` changes in privacy
(~318) and API034 (~446-471). `features.yaml` changes in API034 and WS040.
Resolve these sequentially in A3, and give the resolved hunks independent review.
Keep C4's runner/model edits minimal and put masking logic in `evidence.py`.
Also: the pins have Sol evaluating reviews of Sol's own privacy chain. R2 should
decide whether Astra should evaluate instead; that is still the same family.

## 8. Order, dependencies and exit conditions

Ceiling: at most two workers, plus the coordinator and the protected external
reservation; no nesting. Each wave closes out (preserve, publish, verify heads)
before the next wave fans out.

1. **Wave R-A:** T1 and T3 in parallel (disjoint paths); the coordinator runs T4.
   Exit: both commits delivered, preserved and published.
2. **Wave R-B:** T2, plus T5 if R3 accepted it and T4 verified a route (otherwise
   T5 on MiniMax, or hold). Exit: re-review verdict and assessment report preserved.
3. **Wave R-C:** the T5 judge (Astra, serial after T2), plus T1 correction round 2
   only if T2 requires changes. Reserve exactly one further correction and
   re-review per package, then re-plan; no open-ended loops.
4. **Wave R-D:** T6 if T5 passed; Sol corrections; re-review.

Preserved dependencies: no canonical security evidence regeneration
(`EV-API034-SECURITY-REFRESH`, the API034 M-1 freshness hold) until A3 source
freeze. C4 changes the runner/model inputs to that evidence. CR-02 real-HA
credential tests must not capture or admit evidence before the C4 HA-steps fix,
because they put a real-shaped `api_key` through the options flow. WS040 and
API034 chains stay retained and unreviewed. Combined A3/A4 proof, Tron, HIL, the
72-hour soak, the week of field use and release gates are not reinterpreted. Use
no dates or token forecasts.

Alternatives, named: review the uncorrected chain first and correct once. This
avoids a second correction pass, but any new-family assessment of `2d02004d` is
contaminated by the public J-1 judgement. OpenAI could author a fresh WS
component, but it would have no qualified reviewer. Opus 5.5 could author a C4
privacy fix: that mixes authorship, needs privacy authorship it lacks, and
duplicates the chain. I recommend none of these.

## 9. Prepared owner choices (conditional; do not ask yet)

Ask only if the condition occurs.

- **Q1, if T5 yields no qualified non-OpenAI privacy reviewer:** authorize one
  second `claude-opus-5-5` privacy-review assessment (new Task, unchanged six-axis
  rubric, the `e8ce3966` FAIL preserved, one Astra judge, at the corrected tip), or
  keep `RV-PRIVACY-CHAIN` and dependent privacy admission held. Disclosure: this R1
  read the judgement, so such an attempt is not blind.
- **Q2, if the component is accepted and no non-OpenAI async reviewer exists:**
  authorize one bounded second WS-authorship assessment for Opus 5.5 (unchanged
  rubric, WS-WORK-01 preserved) to unlock a wiring lease, or keep CR-01 wiring held.

## 10. Unresolved blockers for R2

- No qualified non-OpenAI reviewer exists for privacy, WS wiring or the out-of-domain parts of WS040/API034.
- The Gemini route is unverified; Sol 6.1's current route is not in the packet.
- `ORCHESTRATION_PROTOCOL.md:177` still says "No Anthropic/Claude ... fallback". Lines 15-17 explicitly supersede it, so the coordinator should schedule instruction maintenance.
- The review's "HOLD" wording for first authorship is worth an explicit coordinator note: I read it as "not earned at this attempt".
