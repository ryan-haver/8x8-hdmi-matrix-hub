# OpenAI R1: recovery after the two failed assessments

Independent proposal only, not consensus or implementation authority. Preserve
the accepted P0-P5 program and 65 units. Establish a real independent privacy
review route, correct supported privacy leaks through the original author lane,
and resolve the WS reservation lifecycle before wiring it. Planning competence
and passing test counts do not grant source qualification.

## Exact inputs and visibility

Checkout/base `b13ddc4de461b7e1072fead0d39361bcb079282f`, branch
`planning/remediation-recovery-r1-openai`. At entry I resolved
`wp-runtime-completion` once to `56f1b4ee71aaace0afd690d834e0822e90a8ba88`.
Packet and necessary coordination records came from that fixed snapshot, not
later moving refs. Packet canonical LF SHA-256 verified exactly:
`40526f127575feead63c94058250a868e0452ccb19b5552f60be66b6b82b77dc`.
Accepted program packet remains
`52ed758e711891ee57be0bbadb87c688333049733e697a52829cf0ba87d7b15e`.

| Input | Exact identity |
| --- | --- |
| WS component/tests/AUTHOR | `15c069bdeb3a9ace37bf68033812ff72659bfbd1`, parent `460a190575e905f8350c454e63c4d570c8b560fa` |
| WS REVIEW | `1cc442207d54b0ad1c5887f6c4e9d5d17b7c8b19`; verified LF SHA-256 `6ee8bbec66ebdb7e650aa8b08e8f75026ec8580c40ed89b1a2f06e6104d85adb` |
| Privacy source | `2d02004d3108953a302e1a49aab9a5f24e944136`, base `d6e78e0b6ab1dab5216443584d810a7a24af32b2`; six commits/ten paths |
| Privacy assessment AUTHOR | `1a38e2851f0223627f5377fa5e32584c233e1223`; LF SHA-256 `7b469ade0388e0de5a46051528992bfb675ba43addd871c48fdaeaf48aa01f2c` |
| Privacy REVIEW | `e8ce39660a37d277e735adce680b848210c8d9b4`; verified LF SHA-256 `e9efab38d4eb81c2d352195d33952559f2fee0139a989f43a3e4dd1524920582` |

WS module SHA-256 is `3bc116d88029aeecdbec5fdce7590e5d623442e37049a9bc4c7bf9489d3031c5`,
tests `2628c0734fa4860ba53fc30d53a246408dbc4b88fc9b2d5a9ba16c500ea7945b`.
Privacy source Git blobs: evidence `d19de24f9ae5c7281ab22fa5fb6ac5d780796b95`,
API `e4cbc54b66fc2e97fd09420c7db1f325beb8e780`, model
`53d2741d0ab14c616ee341bab9c76ce82b174317`, runner
`e3375bca95942f927d34b912f8fc111843b96dac`, HA
`d2561d8e5b31a82599cc97b5444d69895d0df781`.
Ignored `build/remediation-recovery-20261104/openai-r1/input-manifest.json`
retains exact blob IDs/hashes and copied public inputs.

I read the complete WS module/tests and both assessment AUTHOR/REVIEW reports;
websocket/events source; privacy changed source hunks, complete redactor/API/model
and C1-C3 tests; relevant runner check/summary, HA HTTP/config/options/perform and
product auth/config-flow functions. App/runtime composition reads are lifecycle
excerpts, not a full runtime audit. Current handoff/ledger/execution entries,
protocols/configuration, execution pins, remediation order and relevant
validation/contributing guidance supply policy. Long historical plans/ledgers
were read selectively. Broad terminal output sometimes truncated; relevant
technical functions were reread in bounded portions. Copying a blob is not a
claim of full semantic inspection. No peer R1, private native/runtime archive,
owner data or hardware was inspected. Historical execution, provenance and
preservation claims remain attributed to the pinned reports; no source probe
was rerun here.

Assigned route: native Codex `gpt-6-astra/high`, Task `task_3533f742d143`, Dispatch
`ctx_ad93f7ebf306`. Live worker-show confirms this workspace, Task/Dispatch and
Run `run_37205f6095b3`; it does not expose model/effort. Packet/dispatch selection
is visible; independent backend/native per-turn attestation is not performed.
No helpers or alternate models were used. Coordinator configuration stays
untouched/untracked. The first report write failed because its parent directory
was absent; the error is retained in owned scratch and no test was involved.

## Preserve the actual outcomes

WS correctness FAIL, component/first-authorship HOLD: axes
FAIL/PASS/FAIL/PASS/PASS-bounded/HOLD. Reported 44 focused and 4,126 full-core
passes do not defeat the four eager/reserved false-drain controls. Privacy
qualification FAIL: provenance/counterexamples PASS; dataflow, behavior/tools,
calibration and review quality FAIL. Its 18 focused passes and 76 compatibility
passes/two skips do not establish complete redaction. Opus5.5's earned narrow
API-refusal runner/model review competence survives; broad privacy/async source
roles were not earned. Neither failure proves family-wide incapacity. Preserve
old reports, failed controls, missing raw outputs, scratch-boundary violations
and earlier Opus4.7 failures unchanged.

## Technical recovery

**WSR-01: account for admitted work throughout reservation and registration.**
At the WS candidate, `_admit` reserves at lines 352-370 while `aclose` 241-249
and `shutdown` 407-412 snapshot only registered tasks. Factory/eager execution
can finish cleanup before registration; cancelling afterward cannot repair the
completed false report.

Maintain one logical admission record before invoking caller code, with
reservation/task/terminal states, or prove equivalent accounting. No admitted
nonterminal operation may disappear from owner/app capacity or drain reporting;
transition must not double-count it. Closing fences new admission synchronously.
Cancel attached tasks and apply cancellation when outstanding reservations attach;
factory failure releases only its reservation. Final reporting includes unresolved
admissions and live tasks. If `requested` means actual cancellation calls, expose
unresolved reservations separately; never claim they were cancelled. `drained`
must be false for either. This is a behavioral fix, not redefining success to
exclude the four old counterexamples.

Use one monotonic deadline per cleanup. Reentrant/self cleanup must not wait
unboundedly for its own admission to finish registering. An immediate conservative
non-drained result for an unresolved reservation is preferable to false success,
if explicitly specified. Waiter cancellation leaves fences, references and
capacity intact; repeated cleanup can request cancellation again. Do not replace
bounded work with detached watchers or an unbounded queue. Count-only diagnostics
should expose unresolved/resistant work. Synchronous event-loop blocking defeats
elapsed-time guarantees and must remain an explicit limitation.

Retain the four public-API controls: owner/app cleanup from a factory-created
eager cleaner and from the admitted eager first step. Use resistant bodies,
observe real tasks/factory calls, assert non-drained/held capacity and bounded
return, then release/await everything. Add zero timeout, factory failure after
close, task-factory refusal, registered-task control, cancelled cleanup waiters
at both scopes, completion/registration races and stale callbacks. Preserve
1,000-attempt bounds, unrelated-owner progress and unawaited-coroutine detection.
A selective counterfactual omitting reservations must fail the new controls;
retain original failures and restored-source outcomes without rubric softening.

**WSR-02/03/04:** enforce the intended loop boundary before lifecycle mutation,
not only admission. Wrong-loop close/aclose/begin_shutdown/shutdown must neither
cancel foreign tasks nor alter fences. Specify pre-binding behavior/read-only
diagnostics separately; do not claim thread safety. Test both loops and state
before/after refusal. Keep every future script/message/temp in assigned roots;
this cannot erase WSR-03. Configure pytest-asyncio debug explicitly and measure
`get_debug()` inside exercised loops. `-X dev`/environment flags alone are not
proof; preserve versions/full streams/child exits and the old inaccurate claim.

**Wiring is a separate package.** The real `_handle_command` remains unbounded;
`EventStream.refresh` serialization does not bound allocated callers. Socket
removal cancels its writer, not reply work. Prefer a fixed existing-schema busy
error over silent coalescing, which can answer a later request with an earlier
read; explicitly review reply counts/freshness. Use socket owners/app limits and
cancellation-safe finally cleanup, with real aiohttp burst/disconnect/app-stop,
second-client and ping/status tests. A component pass cannot close CR-01.

`RestApiServer.stop()` explicitly stops the event stream before runner cleanup.
Appending a cleanup context alone therefore cannot guarantee request-work drain
first. Include this method and runtime `_stop` dependency ordering in later
serial leases/review. Resistant work stays owned/reported after timeout; destroying
its dependencies is not evidence it stopped.

**Privacy: preserve raw requests/comparisons while sanitizing every display sink.**
At the privacy tip, `evidence.py:115-133` omits `current_pin`, traverses only
dict/list and query-masks strings. `security.py:297-305` accepts `current_pin`;
`security_auth.py:34-35,120-128` uses it. Fixture values do not make the supported
inherited defect hypothetical.

| Boundary | Fix and decisive negative/positive controls |
| --- | --- |
| Fields/shapes | Cover current_pin/current_passcode, accepted credential headers/cookies and returned API keys before repr/serialization/truncation. Traverse supported tuple JSON; normalize accepted header pairs only in diagnostic copies. Verify nested/root cases, unchanged caller objects and actual wire values. Arbitrary mappings require their own acceptance analysis, not extrapolation from tuples. |
| JSON string `data=` | Sanitize a parsed display copy using transport/content-type context while transmitting original bytes. Exercise real loopback JSON strings, escapes, malformed JSON and public text. Do not ban accepted shapes to pass tests. Define safe opaque-body/error handling without promising arbitrary prose-secret detection. |
| Procedure/expected/actual detail | Cover Action.describe, API steps, Response.describe and runner detail. Raw matching secrets pass; mismatches and expected `***` against a real secret fail. Compare before masking. Retain header-name presence and masked-value equality rules. |
| Summary/failures | Runner 777-779 copies failed descriptions into Outcome; `_write_summary` 1026-1037 bypasses record masking. Sanitize before formatting and defend summary persistence too. Exercise failing Hub `?key=`, blocked reasons, setup/cleanup/errors through `_run_one` and actual record/summary writes. Safe records alone are insufficient. |
| HA options | `ha.py:_config_flow` forwards options to `_http`; perform 490-492 stringifies raw recorded bodies. Product config_flow 134-153 accepts `api_key` (const.py:18). Mask copied step bodies, inspect response/errors, and test options through HTTP/perform/runner artifacts with raw identity/transmission checks. Reconfigure currently sends host/port; do not invent the same credential path there. Actual HA acceptance needs its supported environment. |
| Public values | Preserve contracts.shortcut_alias data.key and profile/scene password_protected booleans, public headers and neighboring fields. Replace broad substring policy with explicit credential names and trusted context for ambiguous keys. Unknown key contexts stay conservative. Test public shortcut key and secret API key side by side, wrong types/nesting; never globally exempt key or all protected-looking names. |

Each leak needs byte-level synthetic-marker absence across procedure, requests,
responses, checks, diagnostics and summary, including failures, plus independent
schema/raw identity/verdict/public-value assertions. Selective controls must fail
when the corresponding sink/shape protection is removed. Calling `redact` is
not the oracle. Tuple/pair/JSON-body/summary/HA disclosures are supported but
conditional; arbitrary text/mapping extensions have narrower proof. No owner
exposure or public incident is established.

## Authority and model choices

Standing **Independent review and qualification** requires qualified different-
family exact-commit review: authors fix, reviewers report. Adopted PROTOCOL
sections 4/6/8 distinguish useful competence assessment, ordinary correction and
material allocation change; section 6 says capacity pressure does not authorize
failed-qualification retries. EXECUTION_PINS qualification_failure_policy agrees.
This prospective cycle addresses changed recovery staffing, not all 65 units.

Ordinary privacy source corrections fall within broad remediation authority:
those source authors did not fail a new authorship assessment here. Return them
to the original Sol lane, preserve the chain, issue exact serial leases and
reserve independent review. Astra is a possible author handover only after
settlement/remaining-scope transfer, never an independent reviewer of OpenAI
source. Missing review reserve can hold affected dispatch; acceptance stays held.

WS was expressly a first-authorship assessment, with no automatic rewrite/retry
and no competence earned. Reissuing it to Opus under another Task as an ordinary
accepted-author fix evades that limit. Revising the failed privacy report for
another judge likewise does not earn qualification. Product correction and
competence reassessment are distinct decisions even when they touch the same code.

| Exact route | Evidence/limits | Proposed role and fallback |
| --- | --- | --- |
| Codex gpt-6.1-sol/high, OpenAI | Original privacy author; bounded source/assertion work. Same family as Astra/Luna. | Privacy correction author; Astra handover only with settlement and task match. Neither can independently accept this chain. |
| Codex gpt-6-astra/high, OpenAI | Packet cites accepted lifecycle/restoration and substantive WS/privacy assessment analysis. | Judge new non-OpenAI domain work; review genuinely different-family source within demonstrated scope. Same-family advice only supplements review. |
| Native Claude claude-opus-5-5/high, Anthropic | Earned API-refusal runner/model review; privacy FAIL, WS authorship HOLD. High launch/config visible, cited native per-turn effort unexposed. | Keep narrow qualified API work. No privacy/async role by default; WS continuation needs the specific decision below. |
| OpenCode2 minimax-coding-plan/MiniMax-M3, MiniMax | Accepted planning/prose/inventory only. Thinking inherited; CLI effort override unsupported. | First useful privacy-review assessment, provisional; source review only after competence earned. No M3.1/Flash substitution. |
| Google/Gemini | Allowed; exact current route/model/helpers/access/effort/quota/domain unverified. Old broker candidate opencode/gemini-3.1-pro is not native proof. | Route discovery useful; not available qualified fallback. |
| Other variants / DeepSeek | Variant names do not confer independence or competence. Opus4.7 history unchanged. DeepSeek credit exhausted. | No silent substitutions, new spend/credentials or DeepSeek dispatch. |

Recommend a **first MiniMax privacy-review domain assessment** as the useful
alternative to retaking Opus privacy. Freeze criteria before launch: complete
retained chain, supported carrier/sink reasoning, public-value preservation,
independently chosen meaningful counterexamples and honest full tool evidence.
Qualified Astra judges the exact new report. Repeating supplied findings is not
competence. This is new-family work, not another judge of Opus or a regrade of its
rubric. Broad remediation authority plus accepted prospective allocation covers
it without a new owner permission ritual. A PASS earns only demonstrated review
scope; a separate actual review must still cover the corrected complete chain.
A FAIL remains failed, with no automatic retry or assumed backup.

For WS, an explicitly authorized Opus correction preserves useful actual
Anthropic work and permits qualified OpenAI review. Alternatively a genuinely
new MiniMax bounded component can establish first authorship under Astra
judgement, but costs a fresh author-domain assessment and grants no privacy
review or handler-wiring competence. It must be new work, not copied/relabelled
OpenAI code. An OpenAI correction of the Anthropic component yields mixed-family
authorship and needs an independently qualified third-family reviewer: Astra
cannot fix then approve. That route currently has a larger review gap. Verified
Google may eventually help; none is evidenced now.

**Concrete owner choice, only if choosing Opus WS continuation:** authorize one
bounded correction of preserved 15c069bd by native Opus5.5/high and one exact
corrected-commit Astra judgement under unchanged six-axis criteria, preserving
original FAIL/HOLD and WSR findings, with no further automatic attempt, handler
lease or broad grant. Specific authority is needed because WS_WORK_TASK says
“No automatic rewrite/retry or implied PASS” for its first assessment, reinforced
by adopted section 6; broad remediation does not silently erase that limit.
If declined, retain the candidate and pursue the genuinely new-family route
after qualification/capacity gates. No Opus privacy retake is recommended. This
prepares a coordinator decision; it neither asks the owner nor launches work.

## Package boundaries and safe order

Proposed names below are reservations, not created worktrees or Task IDs.
Each has distinct new reports/ignored artifacts/fresh temp roots. Reviewers
cannot edit product source. Prove prior writer settlement and exact full bases
before creation; never replace an uncertain writer.

| Task/status | Base and exclusive scope | Review/acceptance/reserve |
| --- | --- | --- |
| M3 privacy assessment: provisional after R3/preflight | New wp-recovery-privacy-m3-assess at full 2d02004d above, review base d6e78e0; sole new assessment report/own artifacts. | M3 candidate, separate Astra exact-report judge, unchanged mandatory competence standard; no source acceptance. Reserve both stages; failure stops attempt. |
| Privacy correction: technically ready, review reserve unresolved | New wp-recovery-privacy-fix at 2d02004d or its explicitly reviewed correction descendant. Sol serial lease: tools/validate/evidence.py, model.py, runner.py, clients/api.py, clients/ha.py, named new regression module/new AUTHOR. Existing reports immutable; extra test edits need exact lease. | M3 only after earned privacy-review scope; Google only after verified qualification. Review entire chain from d6e78e0 and fixes, focused controls/normal source hook; reserve initial review, one author fix and one re-review. |
| WS correction: held chosen-route decision | Opus option: wp-recovery-ws-fix at full 15c069bd above; component, its tests, new AUTHOR/owned artifacts only. | Astra exact review if specifically authorized, all old criteria; explicitly budget attempt and correction/review, no assessment retry inferred from ordinary reserve. |
| New WS author alternative: provisional | Separate new tree at published integration full SHA after R3, ancestor floor e2161484459da65aee14433136a14963507b499c; explicit disposition of rejected candidate. Named new standalone component/tests/report only. | M3 first-authorship candidate and Astra judge, not prequalified author. Never two component writers. |
| WS wiring: held component and staffing | wp-recovery-ws-wire at accepted published integration after component intake; exact coordinator serial lease of websocket.py, app.py and demonstrated necessary lifecycle functions/tests. | Actually qualified author plus different-family lifecycle reviewer; component authorship alone does not qualify wiring. Real aiohttp/runtime/client controls, normal hook/combined proof. |
| Independent inventories: technically ready within accepted scope | Existing SW-AUDIT-01, SW-FINDINGS-01, SW-REPO-01, SW-DOCS-01, EV-CI-ATTRIBUTION, EV-PRESERVATION-GAPS reservations; frozen published integration, exclusive reports. | M3/OpenAI bounded prose/factual work; no new tooling masquerading as docs. Preserve completion dependencies and already accepted work. |

Coordinator retains contracts/APIs, manifests/locks, registry, ledger and
integration. Shared privacy model/runner/evidence leases serialize against
retained API/WS client edits. HA diagnostic fixes are not CR-02 credential-flow
acceptance: later product changes require their own lease, qualified HA review,
supported HA environment, valid/wrong/missing/revoked-key and unlocked/offline
controls. Independent UI/shortcut/accessibility work can proceed with its own
qualified pair; this R1 has not audited those sources and grants no qualification.

Minimal sequence: preserve three genuine R1s before all-peer R2; then three
explicit R3 decisions on one hashed complete plan/allocation. Continue already
covered ready inventory/API work meanwhile. Validate new review route and chosen
WS authority; stage corrections/component work with actual capacity and exclusive
leases; correct, review and integrate sequentially; then wire and verify the app.
Failed assessments hold dependent routes, not unrelated packages. Do not fill
idle slots with speculative rewrites or reopen accepted units.

Packet observation 08:32Z reports weekly remaining OpenAI92%, Anthropic75%,
MiniMax67%; Anthropic session100%, MiniMax85%, OpenAI session unknown. These
are dated observations, not future headroom. Absolute allowances/other-host
demand remain unknown. Coordinator refreshes supported usage/reset windows,
routes/helpers, all fleet pages/inbox and protected resources before creation/
dispatch, at natural checkpoints at least every15 minutes and after limit or
commitment changes. At most two active workers plus coordinator plus protected
external. Reserve assessment/judge separately from actual source review/fix/
re-review. Unknown/below30%/insufficient headroom needs a suitable independently
checked fallback or holds only that dispatch. No qualified privacy fallback is
currently verified; catalogue models are not reserve capacity. No guaranteed
dates, token budgets, prices or new spend.

## Dependencies and exit

Retain RV-WS040 at `1fbfee112cc503ffa273c19dc565092d01fe2d6b`, source
`5331d5471a9d319c134e6798645d6ba8cf8466fc`, base
`938ae30339790c361abdda6fdd01b11a4e498518`; its browser/client/effect review is
not the new WS-controller review. API034 at
`caaa4faabe9ede1e3aed37d2269efd4a4d691e04` has a completed report-quality
evaluation per current handoff, not a duplicate pending evaluation. Keep M-1
security freshness, historical FSEC007/lost originals and combined-proof holds.
Privacy C1/C2 are already in C3; API C1 is in C2. Do not duplicate integration or
infer whole-P1 acceptance.

Only after accepted A1/A2 composition and source freeze should A4 regenerate
candidate-bound canonical security evidence: eight browser scenarios plus API
controls, source/image/real-client identity, independent effects and privacy
admission. Keep raw/combined summaries and failures; never edit commit fields to
repair ancestry. Apply relevant full core/Ruff/Mypy, UC, supported HA, browser/UI,
image/build and client verification. REST changes require coordinator
features.yaml and tests/sim/test_sim_rest_reads.py treatment, 100% actual routes,
ledger then registry/checks serially. Reassess freshness after material fixes.

Source acceptance, evidence admission, qualification and publication remain
separate. Coordinator preserves native/artifact/hidden-temp originals and verified
full Git bundles, settles/releases workers, publishes/verifies task refs before
destructive Orca cleanup, and pushes/verifies exact integration equality before
another execution wave. Protect root/private data, unresolved workspaces,
baselines and negatives. Existing Tron decisions are not reopened; physical HIL,
real72-hour soak, field week and final version/artifact release retain owner gates.

Only this new report is tracked. After final prose, run the five existing docs
modules once with root-venv Python, explicit -B, measured checkout imports,
copied Windows environment, owned isolated data/config/TEMP/TMP/basetemp/JUnit
and disabled route/cache plugins. Retain full direct argv/exit/streams and
original ordinary/hidden temp. Actual checks/report hash/commit/parent/diff belong
in the external completion receipt. The authorized invocation-only empty
core.hooksPath docs commit follows UTF-8/link/CR-aware whitespace/scope checks;
no source-hook/runtime/qualification pass is claimed.
