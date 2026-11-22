# Remediation recovery 2026-11-04 — R2 all-peer challenge (MiniMax)

Genuine round-2 all-peer challenge. Prose only: no source correction, no
qualification retake, no source/domain acceptance, no R3 consensus, no
launch. Written after all three R1 originals were preserved and published, so
peer reports are public and are challenged here by name and by evidence.

This report does **not** grant competence, does not convert any failed
assessment into a PASS, and does not authorise a worker. It proposes to the
coordinator's R3 packet a revised matrix, explicit dispositions of every peer
recommendation, corrected statements of my own R1 claims, and the residual
disagreements.

---

## 0. Identity, bindings and verified hashes

| Item | Value |
| --- | --- |
| Contributor | MiniMax family, OpenCode 2 route, worktree `wp-remediation-recovery-r1-minimax`, branch `planning/remediation-recovery-r1-minimax` |
| Task / Dispatch / terminal | `task_24b952fffacf` / `ctx_67cb65bc4f6e` / `term_fc452bef-89b5-4f1b-8580-50e1809ccf19` |
| Coordinator handle | `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| My checkout HEAD / parent | `9ed4b0c294ba3db06dc56f886e59ff2e99b3f601` / `b13ddc4de461b7e1072fead0d39361bcb079282f` (my own R1 head; reused, not reset) |
| Model binding | `minimax-coding-plan/MiniMax-M3`; effort *thinking inherited*, CLI effort override unsupported |
| Helpers / subagents / other models | none; no plugin/MCP routing; no nesting; no side work |
| Entry-pinned integration ref | `refs/heads/wp-runtime-completion` resolved **once** at entry → `5b8fcb17838714cbaf2974378e47cffe68c5079e`; I did not re-resolve and did not follow a moving ref |
| Tracked write | this file only: `docs/agent-process/phases/remediation-recovery-20261104/round2/minimax.md` |
| Owned scratch | `build/remediation-recovery-20261104/minimax-r2/**` (ignored) and `C:/t/remediation-recovery/minimax-r2/**` |

### 0.1 Packet digests (recomputed by me, canonical LF)

| Input | Expected | Mine | Match |
| --- | --- | --- | --- |
| `ROUND2_PACKET.json` (canonical LF SHA-256) | `25aeccfe87568ccba0e424e8bc7b21f85854fac6410a472c710af05b30ae63f7` | same | yes |
| `INPUT_PACKET.json` (canonical LF SHA-256) | `40526f127575feead63c94058250a868e0452ccb19b5552f60be66b6b82b77dc` | same | yes |

The R2 packet's `original_packet_sha256` equals the INPUT_PACKET digest, so the
original input is unchanged.

### 0.2 Peer R1 reports — exact commit, parent, blob and canonical digest

All three were re-fetched by `git cat-file` at the exact commits named in the
R2 packet, and each canonical LF SHA-256 was recomputed. All three parents are
`b13ddc4de461b7e1072fead0d39361bcb079282f`.

| Family | Commit | Git blob | Canonical LF SHA-256 | Match |
| --- | --- | --- | --- | --- |
| OpenAI | `480a27bd3e65ff657ef878abf11242be0360f735` | `f19fff78b2bc741b65b6128d4de5a349366a15f0` | `d961a81627ace27b48e84774ff0284e12a5faf4184e1dd5d7e3d5c8e57e2b9cd` | yes |
| MiniMax (mine) | `9ed4b0c294ba3db06dc56f886e59ff2e99b3f601` | `3b9e713d19572be484e0690dce746e0627ef8f39` | `8c3298edd367228b2dd60b05d4d752247c4d5f7537468243ee9d527dff0517b2` | yes |
| Anthropic | `3e7a83a191923ff393a14a2e93801e58fa8977a3` | `c823287e77c365f302370a677393a61e9b7d2f98` | `a83644445efaa1f666a4d7d40d05e32f8ddc095013593379ee3a74512913e59c` | yes |

I did **not** open any R2 peer report, and no future-round material was read.

### 0.3 What I actually read this round, and how

`blob` is the Git blob id; `LF` is the canonical LF SHA-256 I recomputed.

| Read | Commit | blob | LF SHA-256 | Mode |
| --- | --- | --- | --- | --- |
| `src/rest_api/ws_request_work.py` | `15c069bd` | `41232b1f33f7` | `3bc116d88029aeecdbec5fdce7590e5d623442e37049a9bc4c7bf9489d3031c5` | full file, read as source |
| `tests/test_ws_request_work.py` | `15c069bd` | `47c9f690732f` | `2628c0734fa4860ba53fc30d53a246408dbc4b88fc9b2d5a9ba16c500ea7945b` | targeted grep only this round |
| `tools/validate/evidence.py` | `2d02004d` | `d19de24f9ae5` | `688cbb5e5c65453a0bf2ef68f7c558aca59f7d7d81de7a034109fcd34bab0283` | full file, read as source |
| `tools/validate/model.py` | `2d02004d` | `53d2741d0ab1` | `dd51f504f5787b213735e78c346638c03a049d733fac88b5f727a339541e4cd8` | targeted ranges (`Action.describe`, `Response.describe`, `Hub.describe`) |
| `tools/validate/runner.py` | `2d02004d` | `e3375bca9594` | `58e766a4cd1518609a5c700db56fc946124684cf5f3649b609e01153287490d9` | targeted ranges (procedure/checks/observations, `_subset`, `_write_summary`) |
| `tools/validate/clients/api.py` | `2d02004d` | `e4cbc54b66fc` | `41b46f95a8bb5746c33a508e8b348d4cd4e6ac1bd86df833d25b759cf901b006` | full file, read as source |
| `tools/validate/clients/ha.py` | `2d02004d` | `d2561d8e5b31` | `bf5f2b61c1cb8e35c085c671f0f201fa1a1b06e6000743c997698bc84eda7144` | targeted ranges (`_http`, `_config_flow`, `perform`, `_reconfigure`) |
| `tests/validation/test_sw_sec_data_02_c1.py` | `2d02004d` | `8be26bf20c96` | `84d85157fe3b433ff83960a58bf3828085b3853aa78d63e583b41d66b339eccd` | redaction-relevant ranges, read as source |
| `tests/validation/test_sw_sec_data_02_c2.py` | `2d02004d` | `2e9da21368ea` | `2c11de0c81e91a4e2efe1af3512661cfdad867241c33e883737fa25ac30c0836` | grep only (2 matching lines) |
| `tests/validation/test_sw_sec_data_02_c3.py` | `2d02004d` | `e224c9dd5014` | `1dc874e4df9ff72667481450e21f725993940f3f995e2ec001e21429a6824840` | payload + oracle ranges, read as source |
| `tests/validation/scenarios/security_auth.py` | `2d02004d` | `a5bb572389ae` | `b09b6d7a7faeb8a147494c010e505b57573e8f3d4eb4c750c7b27040cf22b210` | grep + ranges (`current_pin`, `?key=`) |
| `tests/validation/scenarios/contracts.py` | `2d02004d` | `7aa82d53c09b` | `797c02455862c404b209c7e3685a6151a570772a91c714c1a407ce3b823d6f44` | `shortcut_alias` / `Hub(...)` ranges |
| `src/rest_api/security.py` | `2d02004d` | `6c25f61d2819` | `7e50325131f999de5af6ad6dcaacd837caead923a1c0fd59a381aae5da9fca52` | `auth_pin` range |
| `custom_components/hdmi_matrix/const.py` | `2d02004d` | — | — | full file |
| `src/rest_api/websocket.py` | `5b8fcb17` | `2c757cac0f62` | `c6df8125f116b0d503899b365b5b4b0d12dce98c3e10d22a0e1cd94baea249bd` | `_handle_command` / `_reply_status` ranges |
| `src/rest_api/app.py` | `5b8fcb17` | `68b7af996aa6` | `b3264ba25e8f3a6540c0809f61258a1bcd198988e646a3a9828d67c9b0c32539` | `RestApiServer.stop()` range |
| `docs/production/remediation-20261104/WS_WORK_TASK.md` | `5b8fcb17` | `3b35075080b3` | `5cee3eb86bf788e1640d6021ad4384aeeed392daafefd0a2203e9e51e5d68998` | full file |
| `.../WS-WORK-01/REVIEW.md` | `5b8fcb17` | `63f69c66bdd8` | `6ee8bbec66ebdb7e650aa8b08e8f75026ec8580c40ed89b1a2f06e6104d85adb` | full file |
| `.../PRIVACY-REVIEW-ASSESSMENT/REVIEW.md` | `5b8fcb17` | `325fbfa8919` | `e9efab38d4eb81c2d352195d33952559f2fee0139a989f43a3e4dd1524920582` | full file |
| `.../PRIVACY-REVIEW-ASSESSMENT/ASSESSMENT_PACKET.json` | `5b8fcb17` | `734f08dc9b80` | `1732709314f8c6639ff9e136277861abaf444075227734a0b7d9e2d38b7c4dd8` | full file |
| `docs/planning/software-waves/EXECUTION_PINS.json` | `5b8fcb17` | `07ac549c0dd4` | `e68f1ff2843676e24d8a9f6757edf78e90bc5bf167c0c53ae591b552a9615b1d` | parsed (unit + policy entries) |
| `docs/planning/COMPREHENSIVE_REMEDIATION_20261104.md` | `5b8fcb17` | `c490667514eb` | `af3ca3deb2b487b83c6f215b523c4bfaf2ac8eb323c1d63b1e64a07f2ca1831e` | full file |
| `docs/agent-process/PROTOCOL.md` | `5b8fcb17` | `50767c35b412` | `4aeb2351edec0da278c0c330c4df0e852fed0335cff2e35a4e835895ab1ac052` | full file |
| `docs/ORCHESTRATION_PROTOCOL.md` | `5b8fcb17` | `ebac397f6fb3` | `714fd1774d14fa6604aea8cd6ce78c85b122bda9f37a865ea6f56ec2a7f534c4` | full file |
| `docs/agent-process/REPO_CONFIG.json` | `5b8fcb17` | `259a148bb567` | `67dd58d963e44bed6a31db4f90a4de44c1936b9e3711997966a180bff8c03843` | full file |
| `.../RV-API034/execution-20261101/SOURCE_REVIEW_DISPOSITION_20261103.json` | `5b8fcb17` | `805fd03c27c5` | `2240e9a8dd095f41bcb0b6f363e89e76b6ac6d73724828aa705bd519818fcbb7` | full file |
| `.../RV-API034/execution-20261101/EVALUATION.md` | `5b8fcb17` | `544d56942dba` | `9d3825744f43985efa65dd373778d1036891d8cd8696daca05dc70adfa0e67f4` | head + verdict |
| `docs/production/remediation-20261104/ROUND2_PACKET.json`, `INPUT_PACKET.json` | `5b8fcb17` | — | see §0.1 | full files |
| installed `pytest_asyncio/plugin.py` (1.4.0) and `_pytest/config` (9.1.1) | root venv | — | — | targeted source read |

**Limits, stated plainly.** I did not read the WS test bodies beyond targeted
grep this round, the C2 test beyond two matching lines, the judge\'s gap-probe
scripts, the candidate\'s native transcripts, `src/rest_api/profiles.py` or
`config.py` beyond the `password_protected` occurrences, the HA product
`config_flow.py` options schema beyond `const.py`, or any private/root runtime
data. I re-ran no project test, no probe and no product code. The WS and
privacy *defects*, their severities and the "no owner-secret incident"
calibration remain the two completed reviews\'. The mechanism claims below are
mine, derived from the frozen source I read above. I did not re-verify
Anthropic\'s `--stat` overlap figures between the API034 and privacy chains; that
overlap is supported here by the pins and the plan\'s A3 exit text, not by a
diff I ran.

---

## 1. Live route and capacity observation (dated, this round)

From the supported usage source (`orca account list --json`, sanitised, no
credential material read), observed during this round:

| Route | Status | Session | Weekly | Note |
| --- | --- | --- | --- | --- |
| `claude` (Anthropic) | ok | 2% used (300 min) | 25% used (10080 min) | above the 30% floor; `fableWeekly` 0% used |
| `codex` (OpenAI) | ok | no session window | 11% used (10080 min) | above the floor; 2 rate-limit reset credits available |
| `minimax` (MiniMax) | ok | 18% used (300 min) | 34% used (10080 min) | above the floor |
| `gemini` (Google) | **unavailable** | — | — | "Gemini CLI OAuth is disabled in settings" — unknown, **not** headroom |
| `antigravity` | ok | 16% used | **77% used (23% remaining)** | its "Claude and GPT models · Five Hour Limit" bucket shows 0% remaining; underlying backend/family unresolved in `REPO_CONFIG.json` |
| `opencodeGo`, `kimi`, `grok`, `cursor`, `zcode` | unavailable | — | — | not routes |
| DeepSeek | absent from the source | — | — | owner-excluded; no dispatch, no purchase |

No family is below the 30% floor, so the local "verified fallback" clause is not
triggered for the three required families. `antigravity` is below it **and**
family-unresolved, so it is not a fallback for anything. Absolute allowance and
other-host demand remain unknown; no spend, account, credential or route change
is proposed. Capacity constrains routing, not continued development.

**Catalogue observation, dated.** The in-session OpenCode catalogue now lists
**two** MiniMax models: `minimax-coding-plan/MiniMax-M3` (variants `none`,
`thinking`) and `minimax-coding-plan/MiniMax-M3.1-Flash`. My R1 recorded that
the bound `MiniMax-M3` was *absent* from that listing; that was true at R1 entry
and is **no longer true** now. The catalogue now corroborates the binding
model and its `thinking` variant. This changes only *selection* evidence, not
*execution* evidence, and the `MiniMax-M3.1-Flash` entry is **not** M3 evidence
and no M3.1 result may be substituted for it.

---

## 2. Dispositions of peer recommendations

### 2.1 OpenAI R1 (`480a27bd`)

| # | OpenAI recommendation | Disposition | Evidence / reason |
| --- | --- | --- | --- |
| O1 | Ordinary privacy source corrections are within broad remediation authority; return them to the original Sol lane, preserve the chain, issue exact serial leases, reserve independent review | **Accept** | Plan A2 exit "Author fixes plus meaningful negative controls and qualified independent exact-commit review"; plan header "covered corrections retain normal qualification/review/launch gates"; `ORCHESTRATION_PROTOCOL.md` "Reviewers **report; authors fix**. Re-review material fixes … at their final commits". Agreed, with O2 below. |
| O2 | "Astra is a possible author handover only after settlement/remaining-scope transfer, never an independent reviewer of OpenAI source" | **Accept** | `REPO_CONFIG.json` `independent_review_requires_different_family: true`; plan "OpenAI source authors cannot review their own implementation through another OpenAI variant"; plan package 1 "Reviewers report; authors correct". Sol/Astra/Luna are one family. |
| O3 | "WS was expressly a first-authorship assessment, with no automatic rewrite/retry and no competence earned. Reissuing it to Opus under another Task as an ordinary accepted-author fix evades that limit." | **Modify → partly reject** | The limit is real but narrower than OpenAI states: `WS_WORK_TASK.md` bars *automatic* rewrite/retry and the failed **assessment**; the same file scopes the grant ("Passing would qualify only this component-level asyncio WS-work authorship"). The WS review itself names the remedy: "Required correction is an author/coordinator decision about truthful bounded cleanup during reservations/eager admission, with tests of that combined case." A deliberate, bounded, single-attempt correction + exact-commit re-review is the covered path (§3.1). What OpenAI gets right and I keep: the correction must not be re-dispatched as a new *assessment*, must not produce a retrospective PASS, and must be budgeted as one attempt. |
| O4 | "Concrete owner choice, only if choosing Opus WS continuation: authorize one bounded correction … Specific authority is needed because WS_WORK_TASK says 'No automatic rewrite/retry or implied PASS' … broad remediation does not silently erase that limit." | **Reject as an owner ritual; keep the constraints** | The corrected component + exact-commit re-review is covered by plan A2/A3/A4 and the standing protocol (§3.1). The task direction for this cycle is explicit that broad remediation authority must be used where it actually covers a step and that permission rituals must not be created from preference. The constraints OpenAI wants (bounded, explicit, one attempt, no retrospective PASS, no handler lease implied) belong in the **coordinator dispatch scope**, not in a new owner approval. |
| O5 | WSR-01 mechanics: "Maintain one logical admission record before invoking caller code … If `requested` means actual cancellation calls, expose unresolved reservations separately; never claim they were cancelled. `drained` must be false for either." | **Accept the truthfulness requirement; modify the mechanism** | `requested` must keep its documented meaning (`ws_request_work.py:141-142`: "live tasks cancellation was requested for by this call"); a pending admission has no task yet, so no cancellation was requested for it. `remaining` can carry the unresolved admission, so no new public field is required; a new `DrainReport` field is a contract change on a `frozen=True, slots=True` dataclass. The "one logical admission record" is **not needed**: `_admit` has no `await`, so at most one admission is pending per controller at any suspension point (§3.3). |
| O6 | "Do not replace bounded work with detached watchers or an unbounded queue"; "an immediate conservative non-drained result for an unresolved reservation is preferable to false success"; "Waiter cancellation leaves fences, references and capacity intact"; "a selective counterfactual omitting reservations must fail the new controls" | **Accept** | Consistent with `_wait_bounded` semantics (`asyncio.wait` neither raises nor cancels on waiter cancellation) and with the requirement that the four preserved probes stay meaningful (§3.6). |
| O7 | WSR-02: "Wrong-loop close/aclose/begin_shutdown/shutdown must neither cancel foreign tasks nor alter fences. Specify pre-binding behavior/read-only diagnostics separately" | **Accept, and supply the missing rule** | `_check_loop` is called only from `_admit` (`ws_request_work.py:325-331, 339`), so `close/aclose/begin_shutdown/shutdown` mutate foreign-loop state today. I give the concrete pre-binding/no-loop rule in §3.5. |
| O8 | "Configure pytest-asyncio debug explicitly and measure `get_debug()` inside exercised loops. `-X dev`/environment flags alone are not proof" | **Accept; now resolved with a decisive answer** | Verified in the installed pytest-asyncio 1.4.0: `--asyncio-debug` is a `store_true` option with `default=None`, the ini `asyncio_debug` is `type="bool", default="false"`, and `_get_asyncio_debug()` prefers the CLI option, falls back to the ini, and is passed to `Runner(debug=…)` for plugin-owned loops (plugin lines 119-132, 235-241, 1034-1037). pytest 9.1.1 converts an ini/`-o` value through `_strtobool`, so **both `--asyncio-debug` and `-o asyncio_debug=true` work**, while `-X dev` / `PYTHONASYNCIODEBUG=1` alone do not. Anthropic\'s "verify, don\'t assume" is now verified. |
| O9 | Privacy sink table (fields/shapes, JSON `data=`, procedure/expected/actual detail, summary/failures, HA options, public values) | **Accept, with one mechanism correction and two added traps** | §3.4. My R1 described the `data=` string body as reaching the client step via `redact(body)`; that is wrong (see §4.2). Two added hard constraints the peers missed: the existing C1 public-header assertion and the existing C3 exact-description assertion (§3.4.4). |
| O10 | "Tuple/pair/JSON-body/summary/HA disclosures are supported but conditional; arbitrary text/mapping extensions have narrower proof" | **Accept** | Matches the judge's own calibration (N-1 "retain that part as an unproven extension rather than generalizing the tuple proof") and `AGENTS.md` "unknown … is not proof". |
| O11 | "Recommend a **first MiniMax privacy-review domain assessment** … Qualified Astra judges the exact new report. Repeating supplied findings is not competence." | **Accept the structure; modify the family and the order; declare my conflict** | The structure is the only lawful filler the pin allows (`EXECUTION_PINS.json` RV-PRIVACY-CHAIN `qualification.artifact_binding`: "bind exact prior accepted task/domain proof or genuine candidate evaluation; null is not qualified"). The **order** should be *correct first, assess the corrected tip* (§3.6.2). The **family** must not be fixed by my interest: I am MiniMax-M3; `REPO_CONFIG.json` scopes `minimax-coding-plan/MiniMax-M3` to "Bounded evidence inventories only"; I have no privacy-review artifact and no effort control. OpenAI names my family because a third family is *structurally* needed, not because my family is *competent*; R3 must not read it as the latter. |
| O12 | "Freeze criteria before launch … Broad remediation authority plus accepted prospective allocation covers it without a new owner permission ritual" | **Accept** | Plan header: "New material contracts, strategy or **author/reviewer-family changes require the actual prospective three-provider/three-round process** before dependent execution" — that process is this cycle. `PROTOCOL.md` §6: material author/reviewer-family allocation changes "require a fresh three-round cycle for the affected plan unless that exact fallback was already accepted". |
| O13 | "A genuinely new MiniMax bounded component can establish first authorship under Astra judgement, but costs a fresh author-domain assessment and grants no privacy review or handler-wiring competence" | **Accept the caveat; reject the route as unnecessary** | Plan package 2 already provides the wiring path ("Bound WS `get_status`. One leased implementation owner for dispatch and lifecycle changes") and the WS review lists the wiring gates without an authorship qualification gate. A brand-new component authored only to manufacture a qualification is exactly the "ceremonial work" `PROTOCOL.md` §4 forbids ("do not create ceremonial work or automatic exam retries"). |
| O14 | "An OpenAI correction of the Anthropic component yields mixed-family authorship and needs an independently qualified third-family reviewer: Astra cannot fix then approve. That route currently has a larger review gap." | **Accept, and add the symmetric fact** | Symmetrically, an **Anthropic** correction is reviewed by Astra (different family, already qualified in this exact domain by the failed review) — that pairing has **no** review gap, while an OpenAI correction has an unclosable gap today because no non-OpenAI concurrency reviewer exists. The WS correction should therefore stay with the original author. |
| O15 | "Do not call the entire API034 chain unreviewed" is not stated by OpenAI but is implied by its "API034 … has a completed report-quality evaluation per current handoff" | **Accept** | §3.7. |
| O16 | Wire `RestApiServer.stop()` ordering as a real hazard | **Accept, independently verified** | `src/rest_api/app.py` `RestApiServer.stop()` awaits `self.app["event_stream"].stop()` **before** `await self.runner.cleanup()` in the `finally`. So request-work drain cannot be guaranteed by appending a cleanup context. |
| O17 | "Coordinator refreshes … at least every 15 minutes"; "Reserve assessment/judge separately from actual source review/fix/re-review"; "No qualified privacy fallback is currently verified" | **Accept** | `ORCHESTRATION_PROTOCOL.md` quota section; `EXECUTION_PINS.json` `correction_reserve` (1 author-fix + 1 independent re-review session per unit, plus an explicit re-budget for additional material findings). |

### 2.2 Anthropic R1 (`3e7a83a1`)

| # | Anthropic recommendation | Disposition | Evidence / reason |
| --- | --- | --- | --- |
| A1 | WS invariant D1 (truthful drain) and the "admission settled" notification mechanism; exclude `current_task()` from the wait set but count it live | **Accept D1; modify the mechanism; accept the `current_task` rule** | D1 is right. The notification-future mechanism is **not usable**: `_admit` contains no `await`, so an outstanding reservation is always the pending admission that is an ancestor frame of the drain call and can never settle while the drain runs (§3.3). The `current_task()` exclusion is right and is an improvement on my R1 (§4.1). |
| A2 | "Return at once when the only live item is the caller itself or the deadline has passed"; "`timeout=0`, a pending reservation is counted, not ignored" | **Accept** | With `timeout=0`, `_wait_bounded` returns immediately; counting the unresolved admission keeps the report truthful. |
| A3 | "Clearing or omitting a reservation, or 'cancel after registration' alone, does not satisfy D1" | **Accept, with a precision** | Correct that the *report* must not omit it. But the *cancellation* is already correct in the candidate: `_admit` cancels the task after registration when `self._closing or owner._closed` is already true. The defect is the report, not the cancellation. |
| A4 | WSR-02 L1: enforce the loop boundary in `close/aclose/begin_shutdown/shutdown`, raising before any state change; narrow-to-admission-only is an acceptable calibrated alternative | **Accept enforcement; reject the alternative as a pass-the-rubric move** | The current behaviour mutates foreign-loop state and cancels foreign-loop tasks — a real hazard, not a documentation nicety. Narrowing the prose would be a contract change and must be recorded as such, not slipped in as a docstring edit. I supply the missing pre-binding/no-running-loop rule (§3.5). |
| A5 | WSR-04: the correction report must say receipt 45 was not asyncio-debug coverage; verify `--asyncio-debug` / `asyncio_debug=true` | **Accept; now resolved** | §2.1 O8: both forms are verified supported in the installed pytest-asyncio 1.4.0, and `loop.get_debug()` must be asserted on the loop actually under test. |
| A6 | WSR-03: the correction assignment must state the harness default scratchpad is outside the lease; the re-reviewer audits the native transcript for writes outside the assigned roots; the original violation stays recorded | **Accept, and sharpen** | The audit must cover the **whole** attempt, including the new one: any scratch write outside the assigned roots is an attempt-level finding, exactly as WSR-03 was. The original violation stays recorded and is not re-litigated by the correction (§3.2). |
| A7 | Test table W1-W6 + mutants M; W1 uses `remaining` equal to an independent live count from `asyncio.all_tasks()` and gates | **Accept** | An independent `asyncio.all_tasks()` cross-check is the strongest available oracle for "the report must not claim drained while work is alive", and it does not mirror the implementation counter. Keep the mutants: they are the failure-sensitivity evidence the reviewer credited. |
| A8 | Privacy invariants P1-P5: enumerated credential names, shape completeness, sink completeness, raw preservation, public fidelity | **Accept, with a corrected P1 and an added P5 trap** | An enumerated **name** list must be exact-name (anchored) and case-insensitive, or the existing C1 control breaks (`X-Admin-PIN-Policy` is public) — §3.4.3. P5 must also keep `Hub.equals` unmasked: `Hub.describe()` performs no redaction at all today, and redacting it would mask the public `data.shortcuts[0].key` value asserted by `contracts.py:71`. |
| A9 | "The created-key `key` stays masked even though this loses `shortcut_alias` `data.key` fidelity, unless a route-aware rule is tested both ways" | **Modify** | Prefer a **value-blind, name-exact** rule plus a declared public-field allowlist, not a route-aware rule: a route-aware rule is a second policy surface with its own review burden. The concrete public loss is at `contracts.py:76-77` → `Response.describe()` → `redact(self.json)` → the bare key `key` matches `^(key\|…)$` → the value `route_one_to_one` becomes `***` in the persisted description. |
| A10 | "Mask a structured copy before formatting" / "mask … then truncate" discipline | **Accept, and add the concrete instance** | `tools/validate/clients/ha.py` `_http` raises `RuntimeError(f"{method} {path}: HTTP {resp.status} {text[:300]}")` — **truncation happens before any masking**. The required order is mask-then-truncate, so that call site must become `redact(text)[:300]`. |
| A11 | Authority table: "Opus 5.5 corrects its own unaccepted WS component — Covered"; "A first privacy-review assessment by Gemini or MiniMax — Needs this cycle\'s R3"; "A second Opus 5.5 privacy-review or WS-authorship assessment — Owner choice, held" | **Accept the first two; modify the third** | The WS correction is covered (§3.1). The new-family assessment needs exactly this R3 (author/reviewer-family allocation change). The "second WS-authorship assessment" is **not** a useful lever at all — see A13. |
| A12 | "A correction can earn **component** acceptance. It does not earn Opus 5.5 **WS authorship** competence." | **Accept and sharpen** | "The negative result is restricted to this candidate" (`WS-WORK-01/REVIEW.md`) — so the *correctness* FAIL binds `15c069bd` and a re-review can accept the corrected source; the *attempt-level* axis-1 failure (WSR-03) is not erasable by any commit (§3.2). |
| A13 | Owner choice Q2: "authorize one bounded second WS-authorship assessment for Opus 5.5 … to unlock a wiring lease, or keep CR-01 wiring held" | **Reject** | `WS_WORK_TASK.md` scopes the grant explicitly: "Passing would qualify only this component-level asyncio WS-work authorship, **not** broad security/privacy/HA/UI authorship **or existing handler wiring**." A second assessment could not unlock the wiring lease even if it passed. The wiring gates are the accepted component, a leased implementation owner (plan package 2) and a qualified different-family reviewer (§3.2). This is an unnecessary ritual built on a misread scope. |
| A14 | Owner choice Q1: if no qualified non-OpenAI privacy reviewer emerges, authorise one second `claude-opus-5-5` privacy assessment (new Task, unchanged six-axis rubric, `e8ce3966` FAIL preserved, one Astra judge, at the corrected tip) | **Modify → keep as a conditional fallback only, not a recommendation** | The attempt budget is genuinely exhausted (`ASSESSMENT_PACKET.json` `attempt_authority`; `COORDINATOR_DISPOSITION.json` `future_automatic_retry_authorized: false`), so taking it *is* an owner decision. But the failed axes were dataflow, calibration and review quality — i.e. overclaiming breadth — which a repeat under the same model does not obviously fix; and the attempt cannot be blind, because the judgement is public to every participant in this cycle. The pin\'s own `fallback_disposition` (hold the affected review, continue independent routes) is the lawful default (§3.6.3). |
| A15 | T-matrix: T1/T2 WS correction + re-review; T3 privacy C4 with review held; T4 Gemini route discovery; T5 first privacy assessment; T6 RV-PRIVACY-CHAIN source review; T7 CR-01 wiring "Held — No qualified route today"; T8 Opus in-domain RV-API034 portion; T9 MiniMax inventory routes | **Accept T1-T6 and T9; modify T4/T5 gating; modify T7; accept T8 with a correction** | T5 must not be gated on T4 (Gemini is currently **unavailable**, and `EXECUTION_PINS.json` says "Unknown Gemini is not spare capacity") — the assessment must be able to run on a verified available route while Gemini discovery continues in parallel as a coordinator-only, read-only task (§3.6). T7 is not "no qualified route today": an Anthropic-authored wiring change is reviewable by Astra, and OpenAI-authored wiring is the pair with the gap (O14). T8 is right in substance but the RV-API034 **source review and secondary evaluation are already complete**; the residual is the M-1 freshness hold and the refresh unit\'s own reviewer qualification (§3.7). |
| A16 | "the pins have Sol evaluating reviews of Sol\'s own privacy chain. R2 should decide whether Astra should evaluate instead; that is still the same family." | **Accept the observation, correct its framing** | The pin is explicit: `author_route: claude` (the review), `reviewer_route: sol` (the evaluation), `source_reviewer_route: claude`, `original_implementation_author_family: OpenAI`. So Sol evaluates a **Claude-authored** review of Sol-authored source — the primary review is properly independent; only the evaluation step is same-family as the source, which `secondary_evaluation_scope` already constrains ("it cannot substitute for independent qualified source review of OpenAI implementation"). The real issue is upstream: the `claude` source-reviewer route is the one that failed. |
| A17 | "`ORCHESTRATION_PROTOCOL.md:177` still says \'No Anthropic/Claude … fallback\'. Lines 15-17 explicitly supersede it, so the coordinator should schedule instruction maintenance." | **Accept; verified and made precise** | In the pinned blob `ebac397f…` the sentence appears in the quota section as "No Anthropic/Claude or opaque fallback is permitted.", in the **same file** as the owner\'s 2026-11-01 supersession paragraph and the `REPO_CONFIG.json` `excluded_underlying_families: []`. This is a real internal inconsistency inside one current file. It is instruction-only documentation maintenance (no launch implied); I did not edit it — those documents are coordinator-owned (§3.9). |
| A18 | "the review\'s \'HOLD\' wording for first authorship is worth an explicit coordinator note: I read it as \'not earned at this attempt\'" | **Accept, and sharpen** | Correct, and I make it operative: "not earned at this attempt" means the *component* may still be accepted at a corrected commit while the *authorship grant* for that attempt stays withheld (§3.2). |

### 2.3 My own R1 (`9ed4b0c2`) — corrected claims

See §4. Six of my R1 statements are corrected or materially sharpened here.

---

## 3. Challenge topics, resolved with evidence

All seven `challenge_topics` of the R2 packet are addressed below, in packet
order: topic 1 → §3.1; topic 2 → §3.2; topic 3 → §3.3 and §3.5 (the
cross-loop fence is part of the WS-mechanism topic); topic 4 → §3.4; topic 5 →
§3.6; topic 6 → §3.7; topic 7 → §3.8. §3.9 records what is preserved.

### 3.1 Challenge topic 1 — correction versus qualification/attempt budget/owner-only continuation

**Four objects that the R1s ran together.** They have different rules and must be
separated:

| Object | What it is | Controlling rule | Who decides | Verdict |
| --- | --- | --- | --- | --- |
| (a) bounded source correction of the WS component | fix WSR-01/02/04 in `src/rest_api/ws_request_work.py` + additive tests | plan A2 "Author fixes plus meaningful negative controls and qualified independent exact-commit review"; plan A4 "If A4 reveals a source defect, return that bounded correction to its author and exact changed-commit reviewer"; `ORCHESTRATION_PROTOCOL.md` "Reviewers **report; authors fix**. Re-review material fixes … at their final commits"; `PROTOCOL.md` §6 "Ordinary covered corrections/wave splits do not require ceremonial repeats" | coordinator (ordinary wave dispatch) | **Covered. No new authority.** |
| (b) component acceptance of the corrected commit | a qualified different-family exact-commit re-review of the corrected source | `ORCHESTRATION_PROTOCOL.md` "Review the exact author commit … Re-review exact corrected source"; `PROTOCOL.md` §8 "Re-review exact corrected source"; the WS review: "The negative result is restricted to this candidate" | qualified reviewer (Astra, different family, already qualified in this exact domain) | **Earnable at the corrected commit.** |
| (c) the failed first-authorship assessment | the *attempt* that produced `15c069bd` and its axis-1 failure (WSR-03) | `WS_WORK_TASK.md` "No automatic rewrite/retry or implied PASS"; the review "This review therefore grants **no component acceptance and no new authorship competence**" | nobody — it is a recorded negative result | **Stays failed and immutable.** |
| (d) a second assessment attempt | a new candidate/judge cycle for the same competence question | `WS_WORK_TASK.md` "No automatic rewrite/retry"; `ASSESSMENT_PACKET.json` "ONE new domain-assessment candidate and ONE fresh judge. No automatic rewrite/retry/extra judge"; `PROTOCOL.md` §4 "Preserve failed qualifications and do not relabel them as PASS"; §6 "Capacity pressure does not authorize failed-qualification retries"; `AGENTS.md` "no automatic rewrite/retry, no extra judge" | owner (budget expansion) | **Not requested, not smuggled in.** |

**How the correction honours (c) and (d) rather than waiving them.** (a) does not
re-judge the author\'s competence; it fixes code. (b) is a *component* verdict
on a *different commit*, which the review\'s own "restricted to this candidate"
wording permits. (c) stays on the record; the corrected commit cannot erase a
host-write-boundary violation of the first attempt. (d) is not what (a) is: a
correction is dispatched against a source defect with an acceptance oracle; a
retake is dispatched against a person with a competence rubric. Conflating them
is what OpenAI's R1 warns against — I keep that warning and reject only its
owner-ritual conclusion.

**Which decisions R3 can adopt without an owner step:** (a) and (b) directly,
because they are covered corrections; a **new-family reviewer allocation** for
`RV-PRIVACY-CHAIN`, because the plan header says "author/reviewer-family changes
require the actual prospective three-provider/three-round process", and this
*is* that process; and the wave order and serial leases, because they are
coordinator-owned implementation choices. **Which genuinely need an owner
choice:** only an expansion of a spent attempt budget (§3.9), and I recommend
against taking it.

**This is neither a project-wide stop nor a cosmetic waiver.** The task-local
limit is honoured precisely: it is not expanded to block the component
correction, and it is not ignored by pretending the correction is the assessment.

### 3.2 Challenge topic 2 — WSR-03 stays attempt-level; component acceptance vs authorship HOLD; the lawful wiring route

**WSR-03 is a property of an execution, not of a commit.** The review records
native tool indices 22/23, 59/60 and 83 writing `scratchpad/fix1.py`,
`scratchpad/fix2.py` and `scratchpad/commit-msg.txt` under the harness temp
root — outside both assigned writable roots — and concludes "the exclusive
host-write boundary was not met". No commit can undo a host-write violation.
Axis 1 therefore remains FAIL **for that attempt**, and no corrected commit may
be presented as having passed it. A re-review of a corrected commit is scoped
to the corrected source and the corrected attempt\'s own process; it must not
re-issue or erase the first attempt\'s axis-1 finding.

**Can a subsequent component review earn corrected-source acceptance while the
original first-authorship stays HOLD? Yes — and the two are separate verdicts.**
"Component correctness: FAIL **at the exact candidate**. Component acceptance and
bounded first-authorship acceptance: HOLD" and "The negative result is restricted
to this candidate". A qualified different-family re-review at the corrected
commit can accept the corrected *component*; it cannot convert the failed
first-authorship assessment into a PASS, and its report must say so explicitly.

**Which route can lawfully perform the existing-handler wiring?** Not by
qualification inheritance:

- `WS_WORK_TASK.md`: "Passing would qualify only this component-level asyncio
  WS-work authorship, not broad security/privacy/HA/UI authorship **or existing
  handler wiring**." So the WS-WORK-01 competence does not extend to the
  wiring — even a pass would not have unlocked it.
- The wiring\'s real gates (`WS-WORK-01/REVIEW.md`, closing section): "a
  separately accepted exact component, an app-owned key and cleanup order that
  drains request work before destroying the event stream/runtime, owner
  creation/closure at the real socket boundary, cancellation-safe finally
  handling, chosen limits/timeouts and truthful remaining-work handling … real
  aiohttp `/ws` burst/disconnect/shutdown tests and coordinator-owned
  contract/registry/combined acceptance"; plus plan package 2: "**One leased
  implementation owner** for dispatch and lifecycle changes".
- Therefore the wiring needs (i) an accepted component, (ii) a coordinator
  **lease** of `src/rest_api/websocket.py` / `src/rest_api/app.py` to a single
  implementation owner, and (iii) a qualified different-family reviewer of the
  wiring change.
- Reviewer availability decides the pair. Today the only qualified
  concurrency/lifecycle reviewer is OpenAI Astra (WS component review; R8D async
  restoration). An **Anthropic-authored** wiring change is therefore reviewable
  by Astra with no qualification gap; an **OpenAI-authored** wiring change has
  no eligible reviewer at all (Anthropic is scoped to the API-refusal
  runner/model domain and "Current scoped Opus eligibility cannot be promoted
  into broad security/privacy/UI/HA qualification by assertion"). So the
  recommended pair is **Anthropic author + Astra reviewer**, with the reviewer
  qualification gap closed only by OpenAI authorship.
- The ordering hazard is real and verified: `RestApiServer.stop()` stops the
  event stream **before** `runner.cleanup()`, so request-work drain cannot be
  guaranteed by appending a cleanup context; resistant work must stay owned and
  reported after a timeout rather than having its dependencies destroyed.

**No disguise is used anywhere in this route:** no new Task framed as an
assessment, no author relabelling (the component stays Anthropic-authored),
no retrospective PASS, and the WSR-03 finding stays on the record.

### 3.3 Challenge topic 3 — WS mechanisms compared, with the pitfall that decides them

**The mechanism comparison, at source level.**

| Candidate mechanism | What it does | Verdict |
| --- | --- | --- |
| M-A (my R1, WS-I2) | add the relevant `_reserved` count to `requested` and `remaining` | **half right**: `remaining` yes; `requested` **no** — it would assert a cancellation request that was never made. Corrected in §4.1. |
| M-B (OpenAI O5) | one logical admission record with reservation/task/terminal states; `requested` = actual cancellation calls; unresolved reservations exposed separately | **truthfulness accepted; the record machinery is not needed** — and "expose separately" implies a new `DrainReport` field, a contract change on a `frozen=True, slots=True` dataclass, for information `remaining` can carry. |
| M-C (Anthropic A1) | after `close()`, re-snapshot tasks and reservations in a loop to one monotonic deadline; wait on live tasks plus an "admission settled" future resolved in `_admit`\'s `finally`; exclude `current_task()` from the wait set but count it live | **`current_task()` rule accepted**; **the admission-settled future is not usable** — see the no-yield proof below. |
| M-D (conservative non-drained return) | if an admission is outstanding, report it as outstanding and return within `timeout` without waiting | **Accepted — and it is not merely conservative, it is exact.** |

**The decisive source fact (`ws_request_work.py:336-381`).** `_admit` contains
**no `await`**. It is `async def`, but between `owner._reserved += 1` and the
`finally` that decrements it, it only calls synchronous user code (`factory()`),
`loop.create_task()` and dictionary/set mutation. `factory()` is a synchronous
callable returning a coroutine; with `asyncio.eager_task_factory`,
`loop.create_task()` runs the coroutine\'s first step **synchronously** and that
step suspends at its first `await`, returning control to `_admit`. Therefore:

1. **At most one admission is pending per controller at any suspension point**,
   and `controller._reserved` is exactly 1 when it is pending.
2. **An outstanding reservation observed by any drain is, by construction, the
   pending admission whose frame is an ancestor of the drain call.** The two
   counterexample shapes are exactly this: a synchronous factory that schedules
   an eager cleaner (the cleaner\'s first step runs inside `factory()`), and the
   admitted task\'s own eager first step (it runs inside `create_task()`), both
   inside `_admit`\'s frame.
3. Consequently the pending admission **cannot settle while the drain runs** —
   it settles only after the drain returns and control unwinds to `_admit`. Any
   "admission settled" future would therefore never resolve during the drain:
   M-C\'s wait would burn the whole timeout and still be truthful but
   structurally deadlocked. **M-C\'s future must be dropped; M-D is correct.**
4. **No double counting is possible** with the bare `_reserved` counter: the
   increment and the decrement are in the same non-awaiting frame, so a drain can
   never see the same admission both as a reservation and as a tracked task. A
   per-admission registry (M-B) would need an exact unresolved→tracked
   transition to avoid counting the same work across two drains; the counter
   avoids the problem entirely.
5. **The cancellation is already correct.** `_admit` ends with
   `if self._closing or owner._closed: task.cancel()` — after registration, so
   the task is cancelled exactly once if the scope was closed during the
   reservation window. OpenAI lists "apply cancellation when outstanding
   reservations attach" as a requirement; it is already present. The defect is
   **only the report**.
6. **`current_task()` exclusion is a real improvement** (Anthropic A1, W2). If a
   drain is called from inside the admitted task\'s own body *after* registration,
   that task is in `_tasks`; `asyncio.wait` would await the caller. The wait can
   only end by timeout — bounded and truthful, but it burns the whole timeout
   for nothing. Excluding the current task from the wait set while still
   counting it as live is truthful and cheap. **I accept this against my own
   R1.**
7. **The `requested` semantics must not be inflated.** The dataclass documents
   `requested` as "live tasks cancellation was requested for by this call". A
   pending admission has no task yet, so no cancellation was requested for it.
   Counting it in `requested` asserts a cancellation that never happened — the
   exact "never claim they were cancelled" failure mode. So: `requested` =
   tracked live tasks for which `cancel()` was actually called; `remaining` =
   tracked-not-done **plus** outstanding admissions; `drained` = false whenever
   either is non-zero. The `remaining` docstring ("of those, tasks still not
   finished when the wait ended") needs a precise, non-weakening update — and
   it is a **documented semantic correction of a public dataclass**, which the
   reviewer\'s "no cosmetic contract changes used to pass old rubric" rule
   forbids *unless* it is recorded as such. Adding a third field is the heavier
   version of the same fix and is not required.
8. **Diagnostics pitfalls.** `diagnostics()` returns counts only and states "no
   client identity, payload, exception message or credential"; `active` already
   includes `_reserved`; `owners_active` counts only owners with **tracked**
   tasks, so an owner holding only a reservation is invisible in that counter.
   Any new diagnostic (e.g. an admission-hold duration) must stay count-only and
   must not become a client-data channel.
9. **A durable "reserved" count is not a leak of the admission\'s identity**,
   but if the author wants per-admission identity (to cancel it, or to report
   which owner holds it), that is M-B and needs its own review.

**Deadlock / leak pitfalls to avoid in the correction:** awaiting the pending
admission from inside its own frame (M-C); awaiting the current task (fixed by
the `current_task()` exclusion); a second drain counting the same work twice
(avoided by the counter, but a *per-admission* registry must decrement exactly
once at the unresolved→tracked transition); replacing bounded waiting with a
detached watcher or an unbounded queue; and reporting `drained=True` because a
later drain happened to see an empty task list — the durable defect is the
**false** report, not the eventual cleanup.

### 3.4 Challenge topic 4 — privacy: carriers, sinks, traps, oracles

**3.4.1 The real supported carriers (verified at `2d02004d`).**

- `current_pin`: a **JSON body field** of the admin PIN-change action —
  `src/rest_api/security.py:304` `if not await security.verify_pin("admin", body.get("current_pin"), …)`,
  driven by the real scenario `tests/validation/scenarios/security_auth.py:35`
  `json={"level": "admin", "pin": None, "current_pin": ADMIN_PIN}`. It is
  therefore **not** hypothetical and **not** covered by `_SECRET_KEYS`.
- Query credential: `security_auth.py:136-155` really puts `?key={API_KEY}` into
  the action path for `/api/switch`, `/api/settings/test-connection` and
  `/api/auth/status`.
- HA options credential: `custom_components/hdmi_matrix/const.py` defines
  `CONF_API_KEY = "api_key"`; `tools/validate/clients/ha.py` `_config_flow`
  posts `options` (lines 334-338) to `/api/config/config_entries/options/flow/{flow_id}`
  with `record=record`.
- Public fields that must survive: `password_protected` is a real boolean
  (`src/config.py:452`, `src/rest_api/profiles.py:38`) and the public shortcut
  key is real (`tests/validation/scenarios/contracts.py:71-77`).

**3.4.2 The sink map, corrected.** `current_pin` reaches **three** persisted
sinks, not one:

1. **procedure** — `runner.py` `procedure.append(f"action ({client.name}): {sc.action.describe()}")`
   → `model.py:142-149` `Action.describe()` → `redact(self.params)` → the
   nested `"current_pin"` key is not matched by `_SECRET_KEYS` → the raw value
   is rendered by `!r`.
2. **client step** — `clients/api.py` `perform`:
   `result.steps.append(f"{method} {path}" + (f" {redact(body)}" if body is not None else "") + f" -> HTTP {status}")`.
   `redact(body)` masks by key name only → the raw `current_pin` value appears.
3. **persisted record** — `clients/api.py` `request` records
   `"body": body if body is not None else data`; `runner.py` records
   `"requests": redact(result.requests)`; `evidence.py` `write_record` persists
   `redact(record)`. All three are name-based and all three miss `current_pin`.

Plus the **summary**: `runner.py` `_write_summary` writes
`json.dumps(summary)` with **no** redaction, and `Outcome.__dict__` carries
`reason` and the `failed` check descriptions — so the record can be clean while
the summary is not. OpenAI\'s "Runner 777-779 copies failed descriptions into
Outcome; `_write_summary` 1026-1037 bypasses record masking" is **confirmed from
source** (I read both).

**Correction to my R1 (see §4.2):** I wrote that a JSON-string body reaches the
client step via `redact(body)`. Reading `clients/api.py` `rest_call` (lines
26-66) shows that for the `request` intent `body` comes **only** from
`p.get("json")`, while `data` is read separately in `perform`
(`data = action.params.get("data")`). So for a `data=` string body `body is
None` → the **step contains no body at all**; the string body leaks through
`record["body"] = data` and through `Action.describe()` (the raw `data` string
is a parameter value, and `_SECRET_QUERY` does not mask it). Two different
leaks, and I conflated them. The `current_pin` leak, by contrast, reaches the
step because the body is a JSON **dict**.

**3.4.3 Shape coverage — with the concrete compatibility traps.** `redact`
traverses `dict` and `list` only. A **tuple** value is returned unchanged, and
`clients/api.py` `request` accepts headers through `dict.update(headers)`,
which accepts an iterable of pairs → a list of pairs is a list, but each pair
is a **tuple** → the pair list leaks. Anthropic\'s "tuples and any Mapping are
traversed" and OpenAI\'s "normalise accepted header pairs only in diagnostic
copies" are both **accepted**, with one hard constraint neither stated:

> **Do not normalise or reject header pairs before transmission.** The existing
> C1/C3 controls assert the **raw** headers were transmitted
> (`transmitted == [{"method": "POST", "path": "/synthetic-expected", "headers": headers, "body": body_original}]`).
> Normalisation must happen only on the diagnostic copy.

**Trap 1 (breaks an existing control if implemented naively).** The C1 control
at `2d02004d` asserts `all(where[case(k)] == v for k, v in PUBLIC.items())` where
`PUBLIC` contains **`"X-Admin-PIN-Policy": "public-policy"`**, and is
parametrised over `str.lower`, `str.upper`, `str.swapcase`. Any credential-name
rule must therefore be **exact-name (anchored) and case-insensitive**. An
unanchored `x-admin-pin` rule — the natural reading of the header lists in
Anthropic P1 and OpenAI\'s fields/shapes row — would mask
`X-Admin-PIN-Policy` and **break the existing C1 control**. The same applies
to `Cookie` vs `Set-Cookie` (response headers are handled by an explicit
`PUBLIC_RESPONSE_HEADERS` allowlist in `clients/api.py`, not by a name list, so
that path is unaffected).

**Trap 2 (a new public regression if `redact` is applied too widely).**
`model.py` `Hub.describe()` (lines 343-350) performs **no redaction at all**:
it renders `self.path` and `self.equals` raw. Two consequences:

- a Hub expectation whose path carries a query credential persists it
  **unmasked** — and, unlike `Action.describe()`, `Hub.describe()` does not even
  apply `_SECRET_QUERY`. That is a distinct residual from the action path.
- a correction that adds `redact()` to `Hub.equals` would mask the **public**
  `data.shortcuts[0].key == 'route_all_to_output'` value asserted by
  `contracts.py:71`. So: **mask the Hub path\'s query credentials, never redact
  `Hub.equals` by name.**

**Trap 3 (the concrete public loss).** `contracts.py:76-77` expects
`{"data": {"key": "route_one_to_one", "id": "builtin.one_to_one", "enabled": True}}`
for `shortcut_alias`. `Response.describe()` renders `f"body contains {redact(self.json)}"`,
and `redact` matches the bare key `key` through `^(key|…)$` → the public value
becomes `***` **in the persisted description**. The *verdict* is unaffected
(`_subset` compares raw values), so this is a description/public-fidelity loss,
exactly as the judge classified it — but it is concrete and testable.

**3.4.4 Oracles that must be preserved.**

- **Raw identity**: `_subset(expected, actual)` compares raw values; the C3
  control asserts `expected == expected_original`, `action.params == action_original`
  and the exact transmitted body/headers. Masking must never move upstream of
  these comparisons.
- **Exact description text is a pinned oracle**: C3 asserts
  `record["checks"][0]["description"] == description` where
  `description = expectation.describe()`. Both sides use the same function, so
  the equality survives a masking change — but the *persisted description text*
  changes, which is a public evidence surface and must be re-pinned explicitly,
  not silently.
- **Mask-before-format, and mask-before-truncation**: `Response.describe()`
  already masks a copy before formatting — keep that pattern. The concrete
  violation is `clients/ha.py` `_http`: `raise RuntimeError(f"{method} {path}: HTTP {resp.status} {text[:300]}")`
  truncates **before** any masking, so a credential in the first 300 characters
  of an error body is exposed raw in the exception message. Required form:
  `redact(text)[:300]`.
- **Synthetic markers only, zero-hit across every persisted byte**, plus a
  positive control proving the shape was actually transmitted (not rejected) —
  OpenAI\'s "Do not ban accepted shapes to pass tests" is **accepted**: the
  correction must not narrow the accepted request shapes.
- **Selective reversion** per new mask (in-memory, ignored-root, not committed
  tooling) must fail the byte oracle with a non-zero child exit.
- **Public-value regression guards**: `data.key` and `password_protected` stay
  verbatim in the persisted description while the raw verdict and equality
  assertions stay correct.

**3.4.5 What remains uncertain, honestly.** I did not read the judge\'s
gap-probe scripts or the candidate\'s native transcript, so the reproductions
and severities are attributed. I did not read the C2 test beyond two matching
lines. I did not verify the HA product `config_flow.py` options schema beyond
`const.py`. I executed no probe. The "no owner-secret incident" calibration is
the judge\'s and is not re-graded here.

### 3.5 Challenge topic 3 (continued) — cross-loop lifecycle fence: the concrete rule

`ws_request_work.py:325-331` binds the controller to a loop on the first
admission and raises `RuntimeError` on a later mismatch; `_check_loop` is called
**only** from `_admit` (line 339). So `close()`, `aclose()`, `begin_shutdown()`
and `shutdown()` can mutate a foreign loop\'s state and call `task.cancel()` on
a foreign loop\'s task. The rule I propose (author\'s choice, reviewer judges
behaviour):

1. The controller binds its loop **only** in `_admit`. No lifecycle method may
   bind it.
2. `aclose` and `shutdown` check the bound loop **before any state mutation**
   and raise `RuntimeError` if the current running loop differs. `close` and
   `begin_shutdown` perform the same check **only when the controller is already
   bound**; if it is unbound there is no foreign state to protect and the call
   is a no-op that must not bind the loop.
3. A lifecycle call with **no running loop** on a **bound** controller is
   rejected (cancelling tasks of a non-running foreign loop is unsafe); on an
   **unbound** controller it is allowed and does nothing.
4. On rejection, `closing`, `owner.closed` and every task\'s `cancelling()`
   count are unchanged — this is the reviewer\'s W5 oracle.
5. No thread-safety claim is made, and the module prose must say so.

### 3.6 Challenge topic 5 — different-family source-review recovery

**3.6.1 What the pins actually permit.** `EXECUTION_PINS.json`,
`RV-PRIVACY-CHAIN`: `qualification.status` = "existing bounded competence or
candidate-domain evaluation must be recorded, not inferred from model/catalog/plan
approval"; `artifact_binding` = "Before the actual wave bind exact prior accepted
task/domain proof or genuine candidate evaluation; null is not qualified."
`qualification_failure_policy` = "All currently Claude-dependent source reviews
hold after failed/declined/unknown qualification; **no automatic
failed-qualification retry or same-family substitution**"; `fallback_disposition`
= "If primary qualification/capacity fails, hold only affected dispatch/review;
continue independent task-qualified routes. Unknown Gemini is not spare capacity
and same-family review is prohibited." The source is OpenAI-authored, so the
reviewer must be non-OpenAI; Anthropic failed the privacy domain; therefore the
**only** lawful filler today is a **genuine candidate-domain evaluation** by a
family with no prior record in that domain, judged by a qualified independent
judge. **OpenAI\'s structural answer is accepted.**

**3.6.2 Order — modify OpenAI.** OpenAI places the assessment "at full
`2d02004d` above" (the **uncorrected** tip). Assessing the uncorrected tip
re-derives the published J-1/N-1…N-7, so the assessment is partly redundant and
runs straight into the packet\'s "must not … merely repeat published judge
findings as proof". Assessing the **corrected** chain makes it a genuine
residual-discovery exercise on a chain that is not already known-leaky, and its
output is directly reusable as the `RV-PRIVACY-CHAIN` source review of the
corrected tip (the pin already requires "After any PASS a separate qualified
actual RV-PRIVACY-CHAIN source review must still occur at exact tip"). The
correction is an ordinary author fix that needs **no** qualified reviewer to
start, so this ordering costs nothing.

**3.6.3 The candidate family — and my conflict of interest.** The *structural*
need for a third family is real and I accept it. The *selection* of that family
must not be decided by interest. **I am MiniMax-M3**; my family\'s
`REPO_CONFIG.json` scope is "Bounded evidence inventories only"; I have no
privacy-review artifact, no demonstrated source-review competence, and an
unsupported effort control. I therefore do **not** propose my family as the
privacy-review candidate, and I record that OpenAI\'s R1 names my family for
structural, not competence, reasons. If R3 selects any candidate family, it must
select it on a **verified route**, a **frozen rubric**, and a stated willingness
to accept a FAIL — and it must treat a FAIL as a terminal outcome for that
family, not as a reason to re-dispatch.

**3.6.4 Do not wait for Gemini.** The live usage source reports `gemini`
**unavailable** ("Gemini CLI OAuth is disabled in settings"), and the pin says
"Unknown Gemini is not spare capacity". `ORCHESTRATION_PROTOCOL.md`: "capacity
constrains routing, not continued development … Queue only the affected
assignment or acceptance gate when no suitable verified route is available".
So: run the read-only Gemini route discovery **in parallel** as a coordinator-only
task, but **do not gate** the assessment on it (Anthropic\'s T5 "needs R3, plus
T3 and T4" is modified for this reason).

**3.6.5 Freeze before implementation.** The assessment must run against: the
exact **corrected** chain commit; the six-axis rubric **frozen before launch**
(`ASSESSMENT_PACKET.json` `all_mandatory_axes` is the closest existing artifact
and should be reused verbatim); synthetic markers only; the real C1/C2/C3
controls at the exact checkout; and **independently chosen** counterexamples.
The rule that makes this honest: **rediscovering an already-published finding
does not count as competence** — the report must state, for each finding, whether
it was public at entry, and the "counterexamples" axis is scored on findings
that were **not** already published.

**3.6.6 Reserve.** `EXECUTION_PINS.json` `correction_reserve` per unit: 1
author-fix session + 1 independent re-review session, with "additional material
findings" explicitly re-budgeted, and `reviewer_session_budget` = "one bounded
independent review plus one material-fix re-review". The privacy chain
therefore needs, at minimum, five sequential sessions: correction → assessment →
judge → source review → fix → re-review. With the ceiling (coordinator +
protected external + ≤2 new workers) that is about three waves for privacy
alone; under-reserving is the realistic failure mode.

**3.6.7 If no new family can be qualified.** The pin\'s own fallback applies:
hold the affected review, continue independent routes. The privacy **authoring**
correction still proceeds; only `RV-PRIVACY-CHAIN` **acceptance** and the
privacy evidence admission stay held. That is a held gate, not a project stop.

### 3.7 Challenge topic 6 — API034 / WS040: what is already complete, what still holds

**API034 — both the bounded source review and the secondary evaluation are
complete.** `SOURCE_REVIEW_DISPOSITION_20261103.json`: reviewer Anthropic
`claude-opus-5-5` (different family), source `caaa4faabe9ede1e3aed37d2269efd4a4d691e04`,
review base `938ae30339790c361abdda6fdd01b11a4e498518`, verdict "PASS for
bounded runner/model/offline refusal preparation and relevant compatibility
guards; no blocking logic defect or author change requested"; disposition
"SOURCE_REVIEW_DELIVERED; RV-API034 PARTIAL / SOURCE_INTEGRATION_HOLD".
`EVALUATION.md`: "Verdict: accept, for the report-quality pin only"
(evaluator OpenAI `gpt-6-astra`, Task `task_dca414868333`). **Nothing here
reopens them, and I do not call the chain unreviewed.**

**What still holds.** `M-1` (Medium) — INTEGRATION_HOLD: "all 16 F-SEC-007 V3
records stale under existing covers; freshest 310d8b65 browser set was fresh at
938 base. Four unmatching V2 records remain fresh, hence V2<V3. Static
diagnosis corroborates historical failed gate; no fresh global gate run." The
next pin is `EV-API034-SECURITY-REFRESH` (`author_route: sol`,
`reviewer_route: claude`, `dispatch_allowed_now: false`), and its prerequisites
say "verify exact security-task author/reviewer qualification … Existing Opus
scoped runner qualification is not broad security entitlement".

**Correction to my R1 (see §4.4):** my R1 wrote that API034 "needs … a qualified
security review", which could be read as calling the completed chain
unreviewed. The accurate statement is: the bounded source review and the
report-quality evaluation are **complete and accepted for their pins**; the
**M-1 evidence-freshness hold** and the **refresh unit** remain; and the refresh
unit\'s reviewer route is `claude`, whose *scoped* eligibility "cannot be
promoted into broad security/privacy/UI/HA qualification by assertion" — so the
refresh unit carries the **same class** of qualification gap as the privacy
chain, which my R1 under-weighted.

**WS040 is a different unit from the new component.** Pin `RV-WS040`: source
`5331d5471a9d319c134e6798645d6ba8cf8466fc` against base
`938ae30339790c361abdda6fdd01b11a4e498518` at submitted `1fbfee11`; scope
"inspect simulator/API device_change refusal helper and actual nine checks plus
eight fresh browser records/two new gates; **source and artifact review
distinct**"; `source_reviewer_route: claude`; `accepted_reviewer_artifact: null`;
qualification domain "rendered browser/kiosk websocket/persistence/accessibility
behavior and independent client/effect controls". So the WS040 **client-runner
review is a separate unit** with a different source, base, artifact class and
qualification domain from the new WS component; neither substitutes for the
other, and one may not be used to close the other. Its gap is the same *class*
as the privacy gap (no accepted reviewer artifact for its domain) → **held**,
with its own rubric, its own judge and its own evidence.

**Shared model/runner/registry integration stays serial.** The privacy chain\'s
`changed_paths` include `tools/validate/model.py` and `tools/validate/runner.py`
(`ASSESSMENT_PACKET.json`), and the API034 chain changes the same two files;
plan A3 is "compose and freeze — resolving shared runner/model/evidence/API
conflicts". `docs/validation/features.yaml`, `docs/validation/LEDGER.md` and
`docs/validation/findings_pending.yaml` are coordinator-only
(`REPO_CONFIG.json` `coordinator_only_paths`), and `AGENTS.md` requires
"`python -m tools.validate ledger`" and the registry checks to run **serially**.
Two writers must never edit `model.py`/`runner.py` in parallel.

### 3.8 Challenge topic 7 — route and provenance

See §1 (dated capacity and catalogue). Three separations matter:

- **Selection evidence vs execution evidence.** The catalogue now lists
  `minimax-coding-plan/MiniMax-M3` (variants `none`/`thinking`); that
  corroborates *selection* and the effort shape ("thinking inherited; CLI effort
  override unsupported"). It says nothing about the effective underlying model
  of this turn, which is the coordinator\'s native-entry attestation\'s job. My
  R1 blurred the two; the correct reading is that the two are different
  observations (challenge topic 7\'s own distinction). `MiniMax-M3.1-Flash` is
  not M3 evidence and no M3.1 result may be substituted.
- **Availability is not headroom.** `gemini` unavailable, `antigravity` below
  30% weekly with a 0%-remaining Claude/GPT five-hour bucket and an unresolved
  backend family: none of these is a fallback. All three required families are
  above the floor, so no dispatch is held for quota reasons; only the
  *qualification* gates hold (§3.6).
- **The standing supersession governs.** `ORCHESTRATION_PROTOCOL.md` (pinned
  blob `ebac397f…`): "The owner\'s 2026-11-01 direction allows Anthropic, Gemini,
  OpenAI Codex and MiniMax via OpenCode 2 for future assignments and supersedes
  the earlier Anthropic exclusion, including older exclusion wording elsewhere
  in this repository." `REPO_CONFIG.json`: `excluded_underlying_families: []`,
  `exclusion_basis` = the same owner direction. Historical routing, reviews,
  exclusions and failures keep their dates and provenance. **Instruction-only
  inconsistency:** the same pinned `ORCHESTRATION_PROTOCOL.md` blob still
  contains "No Anthropic/Claude or opaque fallback is permitted." in its quota
  section. The supersession paragraph and `REPO_CONFIG.json` govern the current
  direction; the stale sentence should be corrected by the coordinator as
  documentation-only maintenance (no launch, no phase, no visual baseline
  implied). I did not edit it — that file is coordinator-owned.

### 3.9 Preserved negatives and owner gates

Untouched by this report: the WS WSR-01/02/03/04 findings and the
correctness-FAIL/first-authorship-HOLD record; the privacy two-PASS/four-FAIL
axes, J-1, N-1…N-7 and the "no owner-secret incident" calibration; the
`ASSESSMENT_PACKET.json` spent attempt budget; the Opus 4.7 history; the API034
M-1 hold and the historical failed FSEC007 gate; the lost original bytes and
the conditional disconnect reproduction; the accepted P0-P5/65-unit scope; and
every owner gate — visual/Tron approval, physical HIL-B/C/E, HIL-D 72-hour
soak, a week of field use and sign-off, final version and artifact release.
Software passes do not approve any of them, and nothing here reinterprets them.

---

## 4. Corrected self-claims (from my R1 `9ed4b0c2`)

1. **WS-I2 (`requested`)** — my R1 said the minimal change is to include the
   `_reserved` count in **`requested` and `remaining`**. That is wrong for
   `requested`: no cancellation is requested for a pending admission, so
   counting it there asserts a cancellation that never happened. Corrected:
   `requested` = tracked live tasks actually cancelled; `remaining` = tracked
   not-done **plus** outstanding admissions; `drained` false if either is
   non-zero; the `remaining` docstring is updated as a recorded semantic
   correction. (§3.3)
2. **N-3 mechanism** — my R1 said a JSON-string body reaches the client step
   via `redact(body)` at `clients/api.py:160`. Reading `rest_call` shows `body`
   comes only from `p.get("json")`; for a `data=` string body `body is None`,
   so the step contains no body and the leak is via `record["body"] = data` and
   `Action.describe()`. The `current_pin` leak does reach the step (JSON dict
   body). (§3.4.2)
3. **Wiring is not gated on WS authorship competence.** My R1 wrote that the
   wiring is "gated on A\'s acceptance and a coordinator contract decision" and
   left the author qualification implicit; Anthropic inferred a qualification
   gate from that silence and proposed an owner question about it. The controlling
   text says the opposite: `WS_WORK_TASK.md` "Passing would qualify only this
   component-level asyncio WS-work authorship, not … **existing handler
   wiring**". The real gates are an accepted component, a leased implementation
   owner (plan package 2) and a qualified different-family reviewer. (§3.2)
4. **API034 wording** — my R1\'s "needs … a qualified security review" could be
   read as calling the completed chain unreviewed. Corrected: the bounded source
   review and the report-quality evaluation are complete and accepted for their
   pins; the M-1 freshness hold and the refresh unit\'s own reviewer
   qualification remain. (§3.7)
5. **Catalogue observation** — my R1 recorded that the bound `MiniMax-M3` was
   absent from the in-session catalogue. At R2 entry the catalogue lists both
   `MiniMax-M3` (variants `none`/`thinking`) and `MiniMax-M3.1-Flash`; the
   R1 observation was true then and is superseded now. Selection evidence only.
   (§1, §3.8)
6. **Wiring row under-specified** — my R1 marked the wiring "Provisional"
   without naming the author/reviewer pair or the ordering hazard. Now named:
   Anthropic author + Astra reviewer, with the `RestApiServer.stop()` ordering
   hazard verified, and the shared-path serial lease stated. (§3.2)

---

## 5. Recommended recovery / staffing / authority matrix

"Technically ready" = launchable on ordinary authority. "Provisional" = useful
but gated. "Held" = a gate that must not be passed by assertion. Nothing here
is a launch.

| ID | Package | State | Author (family / model / effort) | Independent reviewer | Exact base-selection rule | Exclusive writable paths | Worktree / branch | Acceptance and negative controls | Correction & re-review reserve | Capacity notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **P1** | WS component correction (WSR-01, WSR-02, WSR-04) | **Technically ready** | Anthropic `claude-opus-5-5` / high — the original author of `15c069bd` (continuity, no relabelling) | OpenAI `gpt-6-astra` / high — different family, already qualified in this exact domain by the failed review | base = **exact** `15c069bdeb3a9ace37bf68033812ff72659bfbd1` (review base `460a190575e905f8350c454e63c4d570c8b560fa`); resolve to the exact full SHA before creation; the reviewed diff is only the fix | `src/rest_api/ws_request_work.py`; `tests/test_ws_request_work.py` (**additive only**); NEW `docs/production/remediation-20261104/WS-WORK-01/CORRECTION-01.md`; own ignored `build/remediation-recovery-20261104/ws-correction/**`; fresh `C:/t/remediation-recovery/ws-correction/**`. The original `AUTHOR.md` (`028d8007…`) is immutable | NEW `wp-recovery-ws-fix`, branch `remediation/ws-work-01-fix`, from `15c069bd` (the earlier writer is positively released) | corrected invariants §3.3/§3.5; the four preserved probes re-run at the corrected commit and **must still fail before the fix and pass after it**; independent `asyncio.all_tasks()` cross-check; zero-timeout, factory-failure-after-close, task-factory-refusal, registered-task control, cancelled-cleanup waiter at both scopes, completion/registration race, stale callback, foreign-loop rejection (with `closing`/`owner.closed`/`cancelling()` unchanged), and an in-test `loop.get_debug() is True` under `--asyncio-debug`; existing websocket/events/lifecycle regressions; Ruff + mypy | 1 author fix + 1 independent re-review + 1 material-fix re-review (pin `correction_reserve`); the WSR-03 attempt-level finding is **not** re-litigated and stays recorded | Anthropic weekly 75% remaining; run after the R3 verdict, one author then one reviewer (sequential) |
| **P2** | WS exact-commit re-review of P1 | After P1 | — (reviewer role) | OpenAI `gpt-6-astra` / high | P1 commit vs `460a1905` | NEW review file + reviewer-owned ignored/temp only | NEW `wp-recovery-ws-fix-review` | every WSR disposition recorded; verdict is **component-only**; must state that the first-authorship HOLD for that attempt is unchanged | 1 session; no extra judge; a FAIL stops the package | same pool as P1; schedule after the author settles |
| **P3** | Privacy source correction on the retained C1/C2/C3 chain (J-1, N-1…N-7) | **Technically ready (authoring); acceptance held** | OpenAI family — the actual chain authors, continuity preferred (`gpt-6.1-sol` / high, subject to route verification) | **none exists today** — must be non-OpenAI; Anthropic failed the domain; MiniMax unqualified; Gemini unavailable | base = **exact** `2d02004d3108953a302e1a49aab9a5f24e944136`; review base `d6e78e0b6ab1dab5216443584d810a7a24af32b2`; correct on top of the tip so the chain stays linear | `tools/validate/evidence.py`, `tools/validate/model.py`, `tools/validate/runner.py`, `tools/validate/clients/api.py`; NEW `tests/validation/test_sw_sec_data_02_c4.py`; NEW correction report. **Do not edit** `tests/validation/test_sw_sec_data_02_c1/c2/c3.py` — they are the compatibility oracle. `clients/ha.py` only under a **separate coordinator serial lease** | NEW `wp-recovery-privacy-fix`, branch `remediation/privacy-c4` | PRIV invariants §3.4: three-sink `current_pin` coverage (procedure, step, record) + summary; tuple/header-pair/`data=`-string shapes with a positive transmission control; mask-before-truncate at `ha.py` `_http`; `Hub.describe()` path masked but `equals` not; `data.key` and `password_protected` public-preservation guards; C1/C2/C3 unchanged and passing; selective in-memory reversion per mask failing the byte oracle with non-zero child exit | 1 fix + 1 re-review (reserve held until a qualified reviewer exists); **coordinator-sequential** integration with the API034 chain (`model.py`/`runner.py` overlap) | OpenAI weekly 89% remaining; the author slot is independent of the reviewer gap — start it |
| **P4** | First privacy-review **domain assessment** by a genuinely new family | **Provisional** (route-verified; after P3) | candidate family selected at R3 on a verified route — **not fixed by me**; my own family is not proposed by me (§3.6.3) | OpenAI `gpt-6-astra` / high (qualified in this domain; not the source author) | the **corrected** P3 tip (modified from OpenAI\'s uncorrected tip), review base `d6e78e0` | NEW assessment report; own ignored/temp | NEW `wp-recovery-privacy-assess` | the six `ASSESSMENT_PACKET.json` axes, frozen before launch; synthetic markers only; real C1/C2/C3 controls at the exact checkout; independently chosen counterexamples; **rediscovering a published finding does not count** — the report states, per finding, whether it was public at entry; no expected PASS | assessment + judge + later source review + 1 fix + 1 re-review ≈ 5 sequential sessions; budget them, do not compress | OpenAI judge pool 89% weekly; the candidate family\'s own route/headroom must be verified at preflight; **do not gate on Gemini** |
| **P5** | `RV-PRIVACY-CHAIN` source review | **Held** | the P4-qualified candidate (non-OpenAI) | — | the exact corrected P3 tip | the pin\'s `exclusive_writable` / `reviewer_writable` | the pin\'s reserved worktrees | qualified different-family exact-commit review; reviewer reports only; the separate secondary evaluation does **not** substitute | per pin: 1 fix + 1 re-review | hold only this acceptance; unrelated packages continue |
| **P6** | WS wiring / CR-01 closure | **Provisional** | Anthropic `claude-opus-5-5` / high — **one leased implementation owner** (plan package 2) | OpenAI `gpt-6-astra` / high | the **accepted** component\'s integrated commit on the integration branch; resolve to the exact full SHA before creation | `src/rest_api/websocket.py`, `src/rest_api/app.py` under an explicit **coordinator serial lease**; `docs/validation/features.yaml`, `docs/validation/LEDGER.md`, `tests/sim/test_sim_rest_reads.py` are coordinator-only | NEW `wp-recovery-ws-wire` | real aiohttp `/ws` burst, disconnect, app-stop and second-client tests; **request-work drained before the event stream/runtime is destroyed** (the current `RestApiServer.stop()` order is the reverse); owner creation/closure at the socket boundary; cancellation-safe `finally`; truthful remaining-work after timeout; public WS schema unchanged; 100% actual route coverage retained; `python -m tools.validate ledger` run serially with registry checks | 1 fix + 1 re-review | gated on P2\'s component acceptance; if OpenAI authors instead, the reviewer gap is unclosable today (§2.1 O14) |
| **P7** | `EV-API034-SECURITY-REFRESH` | **Held** | OpenAI `sol` (author route per pin) | `claude` per pin — but scoped Opus eligibility is **not** broad security entitlement | pin `caaa4faa`, candidate base `938ae303` | pin paths | pin-reserved worktrees | new browser/API proof at a branch-correct post-change candidate; both original summaries and combined-input checks; no unchanged failed-gate retry; no canonical import | pin `correction_reserve` | M-1 stays; no evidence regeneration before the source freeze |
| **P8** | `RV-WS040` | **Held** | OpenAI (original author family) | `claude` per pin; `accepted_reviewer_artifact: null` | pin `1fbfee11`, review base `938ae303` | pin paths | pin-reserved worktrees | distinct from the new component (different source/base/artifact class/domain) | pin `correction_reserve` | needs its own domain qualification; the privacy assessment does **not** cover it |
| **P9** | Independent inventories (`SW-AUDIT-01`, `SW-FINDINGS-01`, `SW-REPO-01`, `SW-DOCS-01`, `EV-CI-ATTRIBUTION`, `EV-PRESERVATION-GAPS`) | **Technically ready** | MiniMax / OpenAI bounded prose per the pins (`author_route: m3`) | per the pins (different family) | pin base rules; `accepted_integration_after_dependencies`, exact SHA before creation | pin `exclusive_writable` | pin-reserved worktrees | unchanged acceptance; "no new tooling masquerading as docs" | n/a | this is the scope in which my family has an accepted record (`REPO_CONFIG.json`: "Bounded evidence inventories only") |
| **P10** | CR-02 HA credentials; CR-03 UI shortcuts/accessibility | **Technically ready, independent** | per pins | per pins | per pins | per pins | per pins | real HA environment / real browser; a HA diagnostic fix is **not** CR-02 credential-flow acceptance | per pins | not blocked by any qualification gap above; keep them moving |

**Concurrency and reserve.** Ceiling: coordinator + protected external + at most
two new workers = 4, no nesting. Authors and reviewers count together, so a
reviewer cannot run concurrently with two authors. Reserve, per pin,
1 author-fix + 1 independent re-review session before dispatch, plus an explicit
re-budget for additional material findings. The privacy chain alone needs about
five sequential sessions (§3.6.6).

---

## 6. Readiness separation

| Class | Items | Why |
| --- | --- | --- |
| **Technically ready (launchable on ordinary authority)** | P1 WS correction, P3 privacy authoring, P9 inventories, P10 CR-02/CR-03 | covered corrections / already-accepted scope / independent units |
| **Provisional (useful, gated)** | P2 (after P1), P4 (route-verified, after P3), P6 (after P2 + lease + contract decision) | each has a named gate and a named owner |
| **Held dispatch or acceptance** | P5, P7, P8 — plus `RV-PRIVACY-CHAIN` evidence admission | a qualified reviewer does not exist for the domain; `accepted_reviewer_artifact: null` is machine-readable evidence of the blocker, and `fallback_disposition` says to hold only the affected dispatch |
| **Hardware / release / owner gates (untouched)** | Tron/visual approval, physical HIL-B/C/E, HIL-D 72-hour soak, week of field use and sign-off, final version and artifact release | outside every route above; no software pass implies them |

---

## 7. Unresolved disagreements (explicit; no forced consensus)

1. **Does the failed first-authorship attempt bar Anthropic from the wiring
   implementation lease?** My reading: no — the wiring gates are the accepted
   component, a leased implementation owner and a qualified reviewer, and
   `WS_WORK_TASK.md` explicitly excludes the handler wiring from that
   qualification\'s scope. Counter-reading: the WS-WORK-01 framing ("This is
   specifically not a shared existing-API lease **before authorship competence is
   demonstrated**") can be read as making the wiring depend on demonstrated
   authorship competence. This is a **coordinator** decision under plan package
   2, not an owner decision; I recommend my reading.
2. **Privacy assessment order**: at the uncorrected tip (OpenAI) or the corrected
   tip (me). I recommend the corrected tip for non-redundant evidence and direct
   reusability; OpenAI\'s order is defensible for judging the *original* defect
   set. R3 decides.
3. **Is a second `claude-opus-5-5` privacy candidate ever justified?** I do not
   recommend it (§3.6.4, A14); Anthropic offers it as a conditional fallback.
   If it is ever taken it is an owner budget expansion, and the attempt cannot be
   blind because the judgement is public to this cycle.
4. **Does the WS correction need a separate written coordinator authorisation
   before dispatch, to avoid being read as a disguised retake?** I think yes — a
   bounded dispatch scope stating the attempt budget, the exclusion of any
   authorship verdict, and the reserved re-review. OpenAI asks for an *owner*
   authorisation; I ask for the coordinator record only (§3.1).
5. **`requested`/`remaining` semantics**: whether the correction keeps two
   fields with a clarified `remaining` (my recommendation, smaller contract
   change) or adds a third field for unresolved admissions (OpenAI\'s wording).
   The re-reviewer should judge behaviour, not the field count; I prefer the
   smaller change.

---

## 8. Owner decision

**No owner decision is required for any step I recommend.** The WS component
correction and its exact-commit re-review are covered corrections (plan A2/A3/A4,
`ORCHESTRATION_PROTOCOL.md` "reviewers report; authors fix", `PROTOCOL.md` §6
"Ordinary covered corrections/wave splits do not require ceremonial repeats", and
the WS review\'s own "Required correction is an author/coordinator decision"); the
privacy authoring correction is covered the same way; a new-family reviewer
allocation is exactly what this three-round cycle exists to decide (plan header;
`PROTOCOL.md` §6 on material author/reviewer-family allocation changes).

**One conditional owner choice genuinely remains, and I recommend against taking
it.** If no genuinely new family can be qualified as the privacy reviewer (P4
fails to launch or FAILs), the pin\'s own fallback is to hold
`RV-PRIVACY-CHAIN` acceptance and continue other work. The owner's choice would
be to **expand a spent attempt budget**: authorise exactly one additional
`claude-opus-5-5` privacy-domain candidate plus one fresh Astra judge, at the
**corrected** tip, with the `e8ce3966` FAIL preserved and no further attempt.

- Controlling rule: `ASSESSMENT_PACKET.json` `attempt_authority` — "ONE new
  domain-assessment candidate and ONE fresh judge. No automatic rewrite/retry/extra
  judge"; `COORDINATOR_DISPOSITION.json` — `future_automatic_retry_authorized:
  false`, `attempt_budget.candidate_evaluations: 1`, `independent_judges: 1`;
  `PROTOCOL.md` §4 — "Preserve failed qualifications and do not relabel them as
  PASS after a provider or account change"; §6 — "Capacity pressure does not
  authorize failed-qualification retries or weaker review"; `AGENTS.md` — "no
  automatic rewrite/retry, no extra judge".
- Recommended answer: **do not take it.** The failed axes were dataflow,
  calibration and review quality — overclaiming breadth — which a repeat under
  the same model does not obviously fix, and the attempt could not be blind.
- If taken anyway, it must be recorded as a budget expansion, must not be
  described as a retake of the failed assessment, must not unblock `RV-WS040` or
  `EV-API034-SECURITY-REFRESH` (different domains), and must carry the
  disclosure that the published judgement was available to the candidate and to
  every participant in this cycle.

**One instruction-only maintenance item for the coordinator** (not an owner
decision, not a launch): the pinned `ORCHESTRATION_PROTOCOL.md` blob contains
both the owner\'s 2026-11-01 Anthropic supersession and a later "No
Anthropic/Claude or opaque fallback is permitted." in its quota section
(§3.8). Correcting that prose is documentation-only maintenance; I did not edit
it.

---

## 9. Checks actually run

Run **once**, after this prose, in this checkout, with the root virtual
environment `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(Python 3.12.10, pytest 9.1.1, pytest-asyncio 1.4.0), the checkout as the
working directory, bytecode disabled, a copied Windows OS environment
(`os.environ.copy()`), fresh isolated owned `MATRIX_DATA_DIR` / `UC_CONFIG_HOME` /
`TEMP` / `TMP` / `TMPDIR` / basetemp / JUnit under `C:/t/remediation-recovery/minimax-r2/`,
and the route-inventory and cache plugins disabled:

```
<B root venv python> -B -m pytest \
  tests/test_core_documentation.py tests/test_client_guides_docs.py \
  tests/test_openapi_and_config_docs.py tests/test_security_docs.py \
  tests/test_license_and_protocol_docs.py -q \
  -p no:tests.route_inventory -p no:cacheprovider \
  --basetemp=<owned>/docs/pytest-tmp --junitxml=<owned>/docs/junit.xml
```

Measured import origins, the direct argv, the child exit code, the complete
stdout and stderr streams, the timings, the safe subset of the environment and
the original ordinary and hidden temp contents are retained under
`C:/t/remediation-recovery/minimax-r2/docs01/` (`argv.json`, `result.json`,
`exit_code.txt`, `stdout.txt`, `stderr.txt`, `junit.xml`,
`import_origins.json`, `env.json`).

**Actual result — from the single run** (this paragraph is the only part of the
document edited after that run, and it is edited to record the run, not to change
any recommendation):

| Field | Value |
| --- | --- |
| Direct child exit code | **0** |
| pytest summary | **489 passed** in 3.03 s — 0 failed, 0 errors, 0 skipped, 0 xfailed, 0 deselected |
| stdout | 580 bytes, complete (seven progress lines + the summary line) |
| stderr | **empty** (0 bytes) |
| Wall clock | 3.579 s, 2026-11-04T09:46:06Z → 09:46:10Z |
| JUnit | 63,691 bytes; `tests="489" errors="0" failures="0" skipped="0"`; timestamp `2026-11-04T02:46:07.138026-07:00` |
| Runs | **one**. No retry, no softened assertion, no skipped test counted as a pass |
| Measured import origins | the five documentation modules, `tests/conftest.py` and `tools/validate` (package plus `evidence`, `runner`, `model`, `clients.api`, `clients.ha`) all resolve to **this checkout**; `hub` resolves to the root venv's editable install `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/src/hub/__init__.py`. That is a path-only difference: the root checkout\'s `src` tree object is `5b78baa117e7511a34c641f0f37bf9c9cfff7134`, **identical** to this checkout\'s `src` tree, and the root working tree has no modification under `src` |
| Isolation | `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`, `HIDDEN_TEMP`, basetemp and JUnit all under `C:/t/remediation-recovery/minimax-r2/docs01/`; copied OS environment; bytecode disabled via `-B` and `PYTHONDONTWRITEBYTECODE` |
| Original temp contents retained | `original_temp_contents.json` — ordinary temp 0 entries, hidden temp 0 entries, pytest basetemp 1089 entries, data 0, config 0 (the run created its basetemp artifacts inside the owned root) |
| Errors preserved | none: the import-origin probe and the pytest child both exited 0 with empty stderr |

This is scoped documentation maintenance for one prose file. It is **not** a
source-hook pass, **not** a full-suite result, **not** a runtime, model or
qualification pass, and it claims no route-coverage or evidence admission.

**Commit.** Scoped documentation commit using the authorised invocation-only
empty-`core.hooksPath` exception, after real checks on the new file: UTF-8
without BOM, LF-only line endings (945 LF, 0 CRLF), no trailing whitespace, no
tab characters, no markdown link targets to resolve, and the file is the only
change staged. The exception is used because the repository hook runs broad
Python tests, which are out of scope for this prose-only change;
**no source hook was bypassed for any source change and no hook result is
claimed**. The commit contains only
`docs/agent-process/phases/remediation-recovery-20261104/round2/minimax.md`.

**Integration head note.** My entry pin was `5b8fcb17…`; the integration branch
subsequently advanced to `12ad507eb3c0b24bd896b3bf1757d03980d19696`
("launch final recovery peer challenge in reused worktree"). I did **not**
re-resolve or follow it: every read, hash and quote in this report comes from
the pinned `5b8fcb17…` snapshot, and the packet digests were verified against
that snapshot.

---

## 10. Limits of this report

- Prose and reasoning only. No product code, privacy reproduction, asyncio
  probe or project test was executed by me in this round; the only execution is
  the documentation-module run in §9. The WS and privacy *defects*, severities
  and the "no owner-secret incident" calibration remain the two completed
  reviews\'.
- The invariants and mechanisms in §3 are a correction **design**, not a
  validated patch. The eventual author must confirm feasibility; the eventual
  reviewer must confirm behaviour at the exact commit.
- I did not read: the WS test bodies beyond targeted grep this round, the C2
  test beyond two matching lines, the judge\'s gap-probe scripts, the
  candidates\' native transcripts, `src/rest_api/profiles.py`/`config.py` beyond
  the `password_protected` occurrences, the HA product `config_flow.py` beyond
  `const.py`, or any private/root runtime data. I did not verify Anthropic\'s
  `--stat` overlap figures between the API034 and privacy chains.
- No peer R2 report was read; no R3 consensus is claimed; no implementation,
  qualification, dispatch or acceptance is authorised by this report.
