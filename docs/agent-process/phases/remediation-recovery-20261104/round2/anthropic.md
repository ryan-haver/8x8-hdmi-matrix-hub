# Remediation recovery R2: Anthropic all-peer challenge

**Status: R2 prose challenge only.** This is not an R3 vote, consensus, source
correction, qualification retake, source or domain acceptance, or permission to
launch a worker. All earlier negative results stand unchanged. Where this report
agrees with a peer, the reason is source or policy evidence cited here, not
majority. Recommendations that favour an Anthropic role are flagged so that
peers can test them.

## 1. Bindings, inputs and limits

| Item | Value |
| --- | --- |
| Contributor | Anthropic `claude-opus-5-5`, native Claude Code session, Task `task_da8abc159b3e`, Dispatch `ctx_afe84a0eaa12`. Effort `high` is the dispatch assignment; I cannot observe per-turn effort. No helpers, subagents, plugins, MCP or alternate models |
| Checkout | Reused settled R1 tree `wp-remediation-recovery-r1-anthropic`, branch `planning/remediation-recovery-r1-anthropic`, HEAD `3e7a83a191923ff393a14a2e93801e58fa8977a3` at entry, clean. No reset, checkout, cherry-pick or source import |
| Integration pin | `wp-runtime-completion` resolved once at entry: `de1e344b2f1f874159e3ffa2c1f13962e3fa92e0` (local equals `origin`). All coordinator records below were read from this SHA with `git show` |
| R2 packet | `ROUND2_PACKET.json`, 9,269 bytes, LF SHA-256 `25aeccfe87568ccba0e424e8bc7b21f85854fac6410a472c710af05b30ae63f7` (matches) |
| Original packet | `INPUT_PACKET.json`, 10,876 bytes, LF SHA-256 `40526f127575feead63c94058250a868e0452ccb19b5552f60be66b6b82b77dc` (matches, unchanged) |

R1 reports, read in full at the commits the packet names. Blob IDs at each
commit equal the blobs at the pin, and each LF SHA-256 matches the packet:

| Family | Commit (parent `b13ddc4d…`) | Blob | LF SHA-256 |
| --- | --- | --- | --- |
| OpenAI | `480a27bd3e65ff657ef878abf11242be0360f735` | `f19fff78` | `d961a81627ace27b48e84774ff0284e12a5faf4184e1dd5d7e3d5c8e57e2b9cd` |
| MiniMax | `9ed4b0c294ba3db06dc56f886e59ff2e99b3f601` | `3b9e713d` | `8c3298edd367228b2dd60b05d4d752247c4d5f7537468243ee9d527dff0517b2` |
| Anthropic (own) | `3e7a83a191923ff393a14a2e93801e58fa8977a3` | `c823287e` | `a83644445efaa1f666a4d7d40d05e32f8ddc095013593379ee3a74512913e59c` |

Policy read at the pin (LF SHA-256 prefix; the first five are byte-identical to
my base): `AGENTS.md` `f09377ad`, `ORCHESTRATION_PROTOCOL.md` `714fd177`
(lines 10-20, 140-200, 225-292), `agent-process/PROTOCOL.md` `4aeb2351`
(sections 4-8), `REPO_CONFIG.json` `67dd58d9` (hash only),
`COMPREHENSIVE_REMEDIATION_20261104.md` `af3ca3de` (full), `WS_WORK_TASK.md`
(full), privacy `ASSESSMENT_PACKET.json` (selected keys), Opus 5.5
`COORDINATOR_DISPOSITION.json` (selected keys), `EXECUTION_PINS.json` `e68f1ff2`
(only the `RV-PRIVACY-CHAIN`, `RV-WS040` and `RV-API034` entries), and
`RUNTIME_EXECUTION.md` `11f29c11` (lines 52, 100-135, 155-177, 432-436, plus
grep hits), and grep hits in `ROUND1_DELIVERY_METADATA.json`,
`ROUND1_COMPLETE.json` and `ROUND2_PREFLIGHT.json`. I did not open `tasks/openai-r2.md`, `tasks/minimax-r2.md` or any
R2 peer report.

Source was read semantically, in bounded ranges, at the pinned commits:
`ws_request_work.py` at `15c069bd` (lines 40-80, 128-412); the WS `REVIEW.md` at
`1cc44220` (lines 1-12, 126-205, 288-339); privacy `evidence.py` (50-70,
105-140), `clients/api.py` (90-175), `runner.py` (180-200, 518-532, 625-700,
735-790, 1020-1040, plus grep), `model.py` (138-150, 333-352, 395-402) and
`clients/ha.py` (257-345, 482-520) at `2d02004d`; and grep-located assertions
in the C1-C3 tests plus C1 lines 1-55 and C3 lines 155-163. At
`b13ddc4d` I ran targeted greps of `security.py`, `profiles.py`,
`scenes_v2.py`, `system_shortcuts.py`, HA `config_flow.py` and validation
scenario fixtures. I read the installed pytest-asyncio 1.4.0 `plugin.py` option
names from the root venv. Copies under my temp root (`runner_2d02.py`,
`ha_2d02.py`) were made for bounded reading only.

**Limits.** I did not reread the full WS test module, the privacy judge review
beyond its N-5/N-7 rows, transcripts, private roots, or `AGENT_ALLOCATION.md`
beyond its hash. Gap-probe results, the `current_pin` matched/mismatched
reproduction and the `RestApiServer.stop()` ordering are attributed to their
authors. I ran no probe, no product code and no quota query. Capacity figures
are the R2 packet's 09:08:57Z observation: Codex 10% weekly used; Claude 25%
weekly and 1% session used; MiniMax 34% weekly and 17% session used; Google
unknown; DeepSeek excluded. These are dated observations, not headroom
guarantees.

## 2. Challenge topics

### 2.1 Correction versus qualification and attempt budget

Controlling text, quoted exactly:

- `WS_WORK_TASK.md`: "useful bounded FIRST AUTHORSHIP assessment and
  implementation component"; "independently judged … before authorship
  competence or component acceptance can be earned. No automatic rewrite/retry
  or implied PASS."; "Any material fail/unknown holds bounded authorship and
  component acceptance. Passing would qualify only this component-level asyncio
  WS-work authorship, not … existing handler wiring."
- WS `REVIEW.md`: "Required correction is an author/coordinator decision …
  I have not implemented a remedy or authorized a correction/retry." and "No
  automatic exam retry, new worker, additional judge or existing-handler lease
  follows."
- Standing protocol: "Reviewers **report; authors fix**. … Re-review material
  fixes … at their final commits." Adopted protocol section 6: "Capacity
  pressure does not authorize failed-qualification retries or weaker review."
  Section 4: "do not create ceremonial work or automatic exam retries."
- Project precedent: on 2026-11-03 the owner reply "approved" authorized "ONE
  manual qualification retake" for Opus 4.7, recorded in
  `QUALIFICATION_MANUAL02_AUTHORIZATION.json` (`RUNTIME_EXECUTION.md` line 432).
  In this project a retake of a failed qualification has been an owner decision.

The task text names four different things. They have different answers:

| Thing | Status | Who can decide |
| --- | --- | --- |
| Bounded code correction of `15c069bd` by its author | Covered | R3 under the owner's "remediate all findings" authority. The review assigns the decision to "author/coordinator". A deliberate, R3-adopted assignment is not "automatic" |
| Component correctness acceptance at a corrected commit | Earnable by a qualified exact-commit re-review | The WS task already separates component acceptance from authorship competence |
| Opus 5.5 WS first-authorship competence | Not earned at attempt 1, permanently for that attempt. WSR-03 is an attempt-level failure that source changes cannot cure | A second authorship judgement is a retake: **owner only**, by the precedent above and the "No automatic rewrite/retry or implied PASS" budget |
| Existing-handler wiring lease | Held for every current route | Even a PASS "would qualify only this component-level … authorship, not … existing handler wiring". It needs its own qualified pair (section 2.2) |

**Resolution of the R1 conflict.** OpenAI's R1 is right that a six-axis
authorship re-judgement needs specific authority. MiniMax's R1 and mine were
right that a correction plus a component-only re-review is covered. OpenAI's
prepared owner choice bundles the two: "one exact corrected-commit Astra
judgement under unchanged six-axis criteria". That bundle is the problem.
Unbundled, R3 can adopt the correction and a component review without any owner
step. Only an authorship retake remains owner-only. I recommend not asking for
that retake now, because its payoff is weak: it would not by itself unlock
wiring.

The re-review must be labelled "WS-WORK-01 correction 01 component review". Its
rubric covers correctness (WSR-01/02/04 and the old four counterexamples), the
correction attempt's own boundary compliance, calibration and tests. Its
verdict does not touch the attempt-1 axes. Task-local limits stay task-local.
They hold WS authorship and wiring only, not the project.

### 2.2 WSR-03, corrected-source acceptance and wiring routes

Yes: a later qualified review can accept the corrected component at that exact
commit while first authorship stays HOLD. The WS task makes them separate
earnables. Preserve WSR-03, the scratch originals and the "not earned" result
unchanged. The correction assignment must say that the harness default
scratchpad is outside the lease. The re-reviewer audits the correction
transcript for writes outside the assigned roots. Any new violation is recorded
against the correction attempt, not merged into attempt 1.

Lawful wiring routes, with their real gaps:

| Route | Author qualification | Reviewer | Gap |
| --- | --- | --- | --- |
| A. OpenAI Sol authors wiring | OpenAI authored the existing `websocket.py`/`app.py` runtime (historical, same-family reviewed) | A non-OpenAI async-lifecycle reviewer is needed. None is qualified: Opus holds only the API-refusal scope; MiniMax has planning only; Gemini is unverified | Needs a first new-family async-review assessment. A genuine first Opus async-*review* assessment would be lawful (it is a new domain, not a retake), but it carries a conflict: the reviewer would judge wiring around its own component |
| B. Opus authors wiring, Astra reviews | Opus WS authorship not earned | Astra is qualified | Needs the owner-only authorship retake **and** a later wiring lease. Two gates |
| C. MiniMax authors | No async authorship evidence; effort control unsupported | Astra | Weak prior. A new first-authorship assessment |

MiniMax's R1 claim that "Anthropic author + OpenAI Astra reviewer is the only
currently sound pairing" is **challenged**: it skips the WS task's explicit
wiring exclusion. My R1 Q2 also overstated what a retake would unlock. Wiring
stays held. Choose its route at a later decision point, with the component
outcome and the Gemini discovery result in hand.

### 2.3 WS mechanism comparison

Source facts at `15c069bd`: `_admit` (337-380) contains no `await`. The
reservation exists only during the synchronous `factory()` call and
`loop.create_task` (eager first step), lines 352-373. Registration (369-370)
happens while the reservation is still held, so for that instant both counts
include the work. No caller code runs in that window. `_wait_bounded`
(170-180) returns 0 with no suspension for an empty list. So a drain can only
observe a reservation reentrantly, as all three R1s found.

| Mechanism | Truthfulness | Risks | Disposition |
| --- | --- | --- | --- |
| Conservative: count outstanding admissions in scope; do not wait for them; `drained` false while any exist | Truthful in all four shapes and at `timeout=0` | Less useful: a cooperative reentrant case reports non-drained even though it would finish shortly. A second drain gives the true result | **Preferred** (OpenAI and MiniMax already preferred it; I revise my R1, see section 3) |
| Settlement wait: re-snapshot until one monotonic deadline, awaiting an "admission settled" signal plus live tasks | Truthful if the self-case is excluded or propagates `CancelledError` | Self-drain inside the admitted eager first step suspends, then receives the post-registration cancel. A resistant body that catches it produces no report. Waiter futures leak if not removed in `finally`. A synchronous notification inside 369-373 would double-count | Acceptable alternative only with tests for waiter cancellation, the self-case and no leaked futures |
| Abort-before-create: after `factory()`, if the scope closed, close the coroutine and do not create the task | Removes the post-close eager first step | Contradicts the doc line "On rejection factory is not called". It needs an explicitly documented new outcome | Optional. Never a substitute for truthful reporting |
| Admission-duration diagnostics (MiniMax WS-I7) | Not a correctness property | A reservation spans synchronous code only, so a duration mostly measures factory CPU time. It adds clock calls on the hot path | **Challenge**: optional. An `admitting` count in `diagnostics()` is enough |

**Report fields.** `DrainReport.requested` is documented as "live tasks
cancellation was requested for by this call", and `remaining` as "of those".
Folding reservations into `remaining` alone would make `remaining > requested`
possible and contradict "of those". Preferred: a separate count of unresolved
admissions, with `drained` true only when both counts are zero (OpenAI's R1).
Acceptable: fold reservations into both fields with a documented change of
meaning (MiniMax's R1 and mine). The component is unwired, so either option is a
component-local contract decision. Neither may be justified as passing the old
rubric.

**Loop fence (WSR-02).** `_check_loop` (325-331) binds on first use. Lifecycle
methods must *check without binding*. When a loop is bound and a different
running loop calls, raise `RuntimeError` before any state change. When no loop
is bound, `close`/`begin_shutdown` must keep working with no running loop
(nothing is tracked yet), and that rule must be tested. No thread-safety claim.

**Debug (WSR-04).** pytest-asyncio 1.4.0 exposes `--asyncio-debug` and ini
`asyncio_debug` (root venv `plugin.py` lines 119, 131, 235). Any debug claim
needs that option in the recorded argv plus an in-test assertion that
`asyncio.get_running_loop().get_debug()` is true. `-X dev` and
`PYTHONASYNCIODEBUG` alone are not evidence (the reviewer's run printed
`debug=False`).

**Test oracles.** The four original probe shapes become committed tests with
fixed expectations: owner and application cleanup, each triggered from a
synchronous factory through an eager cleaner and awaited in the admitted eager
first step, under real `asyncio.eager_task_factory`. Revised prose must not
declare any of the four "unsupported". Oracles are test-owned gates: factory
called, body started, body finished, and a release gate for resistant bodies.
Assert `drained is False` and held `active_count` at return. Release and await
every task, then assert that a second drain is truthful. In the factory-cleaner
shape the admitted task **does not exist yet** when the report returns, so an
`asyncio.all_tasks()` oracle (my R1 W1) is wrong there. The self-case asserts
exactly the behaviour documented for the chosen mechanism, never "either".
Mutants: omit reservations from the report, remove the loop check, remove the
post-registration cancel, and (if settlement waiting is chosen) skip the
re-snapshot. Each must give a direct non-zero child exit. The 44 existing
assertions stay unweakened.

### 2.4 Privacy correction strategy

Carrier and sink coverage, verified at `2d02004d` and `b13ddc4d`:

| Carrier or sink | Evidence | Strategy |
| --- | --- | --- |
| `current_pin` body | `security.py:304`; scenario `security_auth.py:35`. `_SECRET_KEYS` anchors only `pin` (`evidence.py:115-118`) | Explicit credential-name set including `current_pin` (all R1s) |
| `current_passcode`, `passcode`, `X-Passcode` | `profiles.py`, `scenes_v2.py`. Already matched by the unanchored `pass(word\|code)` | Keep |
| Created API key `key` | `security.py:341` returns `{"id","key"}` | Keep masked. **Challenge** MiniMax PRIV-I2's "removed or narrowed" `^key$`: removing it unmasks this secret |
| Public `key` | `contracts.shortcut_alias` expects `data.key = "route_one_to_one"` with a different `id`. `system_shortcuts.py` returns `key` equal to `id` | Low fidelity loss. Conservative masking is acceptable. An optional path-scoped public exemption must be tested side by side with `/api/security/keys` |
| Public booleans | `password_protected`, `remove_passcode`, `passcode_locked` | Leave `bool` and `None` unmasked under credential names. Pitfall: `bool` is a subclass of `int`. Integer PINs such as `{"pin": 1234}` must stay masked, so test both |
| Header pairs, tuples | `api.py:120-121` `req_headers.update(headers)` accepts pairs; `redact` traverses only `dict`/`list` | Traverse tuples. Normalize header pairs in diagnostic copies only. Arbitrary `Mapping` types need their own analysis (OpenAI) |
| JSON string `data=` | `api.py:110-111,133` records the raw `data` | Mask a parsed display copy, transmit the original bytes |
| Response headers | `api.py:136-143` already allowlists public names and masks the rest | No change needed. My R1 P1 should not have listed `Set-Cookie` as a gap |
| `Hub` describe, `?key=` | `model.py:343-350` formats the raw path and `equals!r` | Mask before formatting |
| Run summary | `runner.py:776-778` copies failed descriptions and `blocked`; 503/505/516 put `str(exc)` into `reason`; `_write_summary` (1026-1037) uses plain `json.dumps` | Mask at `Outcome` construction **and** in `_write_summary` |
| `ClientState` check | `runner.py:632-636` interpolates `exp.before!r` and `pre['value']!r` | Real raw sink (MiniMax R1 verified). Whether credentials reach it is unproven; cover it in the byte oracle |
| HA options `api_key` steps | `ha.py:490-492,516` format raw `r['body']` | Mask the copied step body |
| HA error and truncated text | `ha.py:267` `text[:500]`, `273` `text[:300]`; `api.py:129` `text[:2000]` | Mask the complete value, then format, then truncate. `runner.py:920` already does this |
| HA form defaults (new, unverified) | Product `config_flow.py:96,119,138,146` builds forms with the stored `api_key` as `default`. `_http` records the raw `response` (`ha.py:269-270`), and `redact` would see `{"name": "api_key", "default": …}` with no secret-named key | **Latent.** The current client sequence makes a fresh entry before one options flow, so the default is empty. I did not verify HA's schema serialization. The supported-HA reviewer must check it. This also qualifies OpenAI's "do not invent the same credential path there": the client body is host/port, but the product forms carry the stored key as a default |

**Value registry (MiniMax PRIV-I1): challenge as the primary mechanism.**
Fixture PINs are four digits (`"1234"`, `"4826"`, `"1357"`, `"5678"`,
`"9999"`). Masking those values everywhere would corrupt public digits in
`elapsed_ms`, ports, IDs and timestamps. That breaks the public-fidelity
invariant. It also cannot know server-issued secrets (created keys, cookies)
before receipt. Modified acceptance: use value masking only as defence in depth
for free-text exception and error strings (`blocked_reason`, `reason`, notes,
HA error text). Structured fields stay name- and context-driven.

**Oracles (kept from all R1s):** synthetic markers in every carrier, through the
real `ApiClient.perform`, `_run_one`, `_check`, `write_record` and
`_write_summary`. Cover matched, mismatched, blocked, skipped and
cleanup-failure lifecycles. Scan every output byte, including retained
stdout/stderr and log records, because streams are retained evidence here. Add
raw on-wire identity, raw-value verdicts (a matching secret passes; `***`
against a real secret fails), public-field byte identity and selective
in-memory reversions with direct non-zero exits. Calling `redact` is not the
oracle.

**Existing tests.** The C1-C3 assertions I located (`***` on credential names,
`X-Admin-PIN-Policy` kept public, the set-cookie mask, public `Response`
descriptions) do not conflict with P1-P5. New coverage goes in a new C4 module.
Editing C1-C3 needs a recorded lease amendment, and no edit may weaken an
assertion. **Challenge** MiniMax package B's lease of all three test files as
writable by default.

### 2.5 Different-family privacy-review recovery

- **Ready route now:** a first MiniMax-M3 privacy-review-domain assessment.
  Native attestation records `minimax-coding-plan/MiniMax-M3`, variant
  `thinking` (`ROUND1_DELIVERY_METADATA.json`). MiniMax has no prior attempt in
  this domain, so this is not a retake. The standing rule says "never wait for a
  preferred provider while a suitable route is ready". My R1 ordering ("Gemini
  if verified, else MiniMax") is revised so that Gemini discovery runs in
  parallel and is not a wait condition. Prior: weak. MiniMax's R1 shows real
  source reading (the `runner.py:635` sink, an accurate WS root cause) but also
  a mis-cited budget and an overreaching value-registry design (sections 2.4
  and 4).
- **Subject: the corrected C4 tip, not `2d02004d`.** **Challenge** OpenAI's
  base. All J-1 and N-1..N-7 findings at `2d02004d` are public, and MiniMax's
  own R1 has already published correction designs for them. An assessment of
  that commit can mostly restate findings and has little discriminative power.
  At the C4 tip the candidate must find what the correction missed or prove it
  complete. The cost is a serial dependency on C4. Freeze before launch: the six
  unchanged axes from `ASSESSMENT_PACKET.json`; the rule that restating
  published findings earns nothing; independent carrier and sink enumeration
  covering `ha.py` (now in scope); full chain `d6e78e0b..C4`; synthetic markers
  only; direct child exits. Disclose that the candidate already read the judge
  review.
- **Judge:** one fresh Astra/high. It did not author the chain. Sol cannot
  judge.
- **Gemini:** coordinator read-only discovery (catalogue, access, launch
  selection, native model, family, helpers, quota). MiniMax's R1 recorded
  `gemini` as unavailable at 08:41Z and `antigravity` with an unresolved family.
  Unknown is not headroom. A verified Gemini is a separate first attempt, not a
  backup that the MiniMax result can be transferred to.
- **No Opus retake** (budget: "ONE new domain-assessment candidate and ONE fresh
  judge. No automatic rewrite/retry/extra judge"). See section 6 for the
  conditional owner choice.
- **Evaluation of the eventual `RV-PRIVACY-CHAIN` review:** the pin names Sol as
  evaluator of a review of Sol's own chain (`reviewer_route: sol`). Recommend
  Astra, as actually happened for API034. Same family, but not the author.

### 2.6 API034, WS040 and serial integration

- **API034:** the bounded source review (Opus, `12eeef93`, against `938ae303`)
  and its report-quality evaluation (Astra, `c3fcace6`, accepted, "evaluation
  substep no longer pending") are **complete**. M-1 security freshness
  (`EV-API034-SECURITY-REFRESH`), the privacy hold and the combined holds remain.
  My R1 row T8 (an Opus "in-domain API034 portion" as provisional) duplicated
  completed work and is withdrawn. MiniMax's "null artifacts on three units"
  reads `EXECUTION_PINS.json` entries that still show `state: reserved` and null
  artifacts. The execution record supersedes them for API034, so I modify that
  claim and ask the coordinator to reconcile the pin.
- **WS040:** its pinned domain is "rendered browser/kiosk
  websocket/persistence/accessibility behavior and independent client/effect
  controls". That is distinct from the asyncio component. It stays held, with no
  qualified non-OpenAI reviewer for that domain.
- **Serial integration:** C4 leases `runner.py` and `model.py`, which API034
  (`caaa4faa`, `runner.py` +28/-3, `model.py` +12) also changes, and WS040 also
  changes `runner.py`. One writer per path. The coordinator composes in A3, and
  the resolved hunks get independent review. Freeze source before any canonical
  security or privacy evidence. C4 changes the runner and model inputs to that
  evidence.

### 2.7 Route and provenance

The coordinator's native attestation (M3, `thinking`) and MiniMax's in-session
catalogue (only `MiniMax-M3.1-Flash` listed) are two different observations.
Native attestation binds the effective family. The catalogue gap stays a
recorded discrepancy, and no M3.1 evidence substitutes for M3. Older wording at
`ORCHESTRATION_PROTOCOL.md:177` ("No Anthropic/Claude … fallback") is
superseded by lines 14-16. Instruction maintenance should reconcile it without
editing history. Every dispatch needs fresh route and quota verification. The
Codex pool hosts both Sol and Astra, so variants do not multiply quota.

## 3. Corrected self-claims (own R1)

| R1 claim | Correction |
| --- | --- |
| T8: Opus `RV-API034` portion provisional | Withdrawn. The review and evaluation are complete; only M-1 and the combined holds remain |
| Q2: an Opus authorship retake would unlock wiring | Overstated. A PASS is necessary but not sufficient for wiring under the WS task |
| D1 mechanism: settlement-wait loop as primary | Revised. The conservative non-drained rule is preferred; the wait loop is an alternative with extra tests |
| "`requested` counts reservations … not a new public field" | Revised. A separate count is preferred; folding requires a documented change of meaning |
| W1 oracle uses `asyncio.all_tasks()` | Wrong for the factory-cleaner shape. Use test-owned gates |
| P2 "any `Mapping`" | Narrowed to supported shapes |
| P1 listed `Set-Cookie` as a gap | Response headers are already allowlist-masked (`api.py:136-143`) |
| C4 `ha.py` "serial lease" | Kept. Add that `ha.py` is outside the 10-path chain (`git diff --stat d6e78e0b 2d02004d`), so the lease is an explicit scope expansion and assessment criteria must name it |
| "Gemini preferred, else MiniMax" | MiniMax is the ready route; Gemini discovery runs in parallel |
| Astra as fallback C4 author | Kept, but that would leave no judge for the privacy assessment. Prefer holding C4 over using Astra |

## 4. Peer dispositions

| Peer recommendation | Disposition | Reason |
| --- | --- | --- |
| OpenAI: admission-record accounting; conservative non-drained result | Accept; a full state machine is optional | Existing `_reserved` counters already exist (`:192,273`) |
| OpenAI: expose unresolved reservations separately | Accept as preferred | Section 2.3 |
| OpenAI: Opus WS continuation needs specific authority | Modify | Covered correction; owner-only authorship retake (section 2.1) |
| OpenAI: owner choice bundling correction with a six-axis judgement | Challenge | The bundle turns covered work into a retake |
| OpenAI: first MiniMax privacy assessment | Accept; base modified | C4 tip, frozen anti-restatement rule |
| OpenAI: assessment at full `2d02004d` | Challenge | Findings already public |
| OpenAI: reconfigure sends only host/port | Modify | True for the client body; product forms default to the stored key (latent) |
| OpenAI: shortcut `key` via trusted context | Accept as an option | Conservative masking is also acceptable (Low) |
| OpenAI: JSON `data=` display copy; arbitrary mappings separate | Accept | Section 2.4 |
| OpenAI: `RestApiServer.stop()` ordering, busy error versus coalescing | Accept as wiring input (attributed, not verified by me) | Busy versus coalescing is a coordinator contract decision |
| OpenAI: new MiniMax WS first-authorship alternative | Challenge as the primary route | It would be a second writer of the same component; fallback only if the Opus correction is not adopted |
| OpenAI: API034 evaluation complete; inventories ready | Accept | Section 2.6 |
| MiniMax WS-I2, folding `_reserved` into the report | Modify | The "of those" semantics (section 2.3) |
| MiniMax WS-I4, never waiting for the caller's own admission | Accept | |
| MiniMax WS-I7, duration diagnostics | Challenge | Optional only |
| MiniMax PRIV-I1, value registry | Challenge, then modify | Four-digit PINs; free-text defence in depth only |
| MiniMax PRIV-I2, narrow `^key$` | Challenge | `security.py:341` |
| MiniMax PRIV-I3, shape completeness | Accept | |
| MiniMax PRIV-I5, separate HA domain | Modify | Separate serial lease, same redaction domain |
| MiniMax: `runner.py:635` raw sink | Accept | Verified; credential relevance unproven |
| MiniMax: lease C1-C3 tests | Challenge | Not needed by the located assertions |
| MiniMax: attempt budget cited from `COORDINATOR_DISPOSITION.json` | Correct the citation | Those fields belong to the `QUAL-ANTHROPIC-CORE-01` API-refusal record. The privacy budget is `ASSESSMENT_PACKET.json` `attempt_authority`. The conclusion is unchanged |
| MiniMax: three units' null artifacts | Modify | API034 pin is stale |
| MiniMax: WS040 held, browser/kiosk domain | Accept | |
| MiniMax: "Anthropic author + Astra" is the sound wiring pair | Challenge | WS task wiring exclusion |
| MiniMax: CR-02/CR-03 technically ready and independent | Modify | Ready to author. Review is held without qualified non-OpenAI HA/UI reviewers. CR-02 evidence capture must follow the C4 `ha.py` fix |
| MiniMax: no implementation worker during R1-R3 | Modify | True for this cycle's subjects and the current slot arithmetic. Unrelated pinned inventory work may use a slot that planning does not need |
| MiniMax Option 1 as an owner question | Modify | R3 adopts it; it needs no owner step (MiniMax says so too) |
| MiniMax: a reviewer cannot run alongside two authors | Accept | 2 + coordinator + protected external = 4 |

## 5. Recommended matrix (for R3 synthesis)

Common rules: verify the exact full base before creation. Use new dedicated
Orca worktrees for source work; the original attempt trees keep their originals
immutable and are not reused. Fresh ignored and `C:/t` roots. The harness
default scratchpad is outside every lease. Reviewers are read-only on product
paths. The coordinator alone owns registry, ledger, manifests and integration.
Reserve per source package: one review, one correction, one re-review. A second
round needs a coordinator decision within this plan; then re-plan, with no
open-ended loop.

| ID | State | Author / reviewer | Base and branch | Exclusive writable | Acceptance and negative controls |
| --- | --- | --- | --- | --- | --- |
| WS-C01 | Technically ready after R3 | Opus 5.5/high native (component author; gaps: reentrant lifecycle, calibration, boundary) / Astra/high (previous WS reviewer, no conflict) | `15c069bd` exact; new `wp-remediation-ws-work-01-c01`, branch `remediation/ws-work-01-correction-01` | `src/rest_api/ws_request_work.py`; `tests/test_ws_request_work.py` (additive); NEW `docs/production/remediation-20261104/WS-WORK-01/CORRECTION-01.md`; `build/remediation-20261104/ws-work-correction-01/**`; `C:/t/remediation-ws-work-c01/**` | Section 2.3 rules, four committed counterexamples, loop-fence tests, recorded debug run, mutants, existing websocket/events/lifecycle regressions, source hook once. Original `AUTHOR.md` unchanged |
| WS-R01 | After WS-C01 settles | Astra/high; no fallback reviewer (Sol async-review competence is unverified, so hold instead) | Correction commit against `15c069bd` | NEW `…/WS-WORK-01/CORRECTION-01-REVIEW.md` plus reviewer roots | Component-only verdict. Attempt-1 authorship stays not earned. Correction-attempt boundary audited |
| PRIV-C4 | Author ready after R3; review held | Sol 6.1/high (route not yet verified; original chain author) / held until a privacy reviewer qualifies | `2d02004d` exact; new `wp-sec-data-02-c4`, branch `execution/wp-sec-data-02-c4` | Serial leases: `tools/validate/evidence.py`, `clients/api.py`, `model.py` (describe hunks), `runner.py` (Outcome, check and summary hunks), `clients/ha.py` (scope expansion); NEW `tests/validation/test_sw_sec_data_02_c4.py`; NEW `docs/production/software-waves/SW-SEC-DATA-02-C4/AUTHOR.md`; own ignored and temp roots | Section 2.4 oracles and reversions; C1-C3 unchanged and passing; source hook once. If Sol is unavailable, hold rather than use Astra |
| G-DISC | Ready now | Coordinator, read-only | n/a | Coordinator records | Verified route record, or a recorded negative |
| PRIV-ASSESS | Provisional (R3 adoption, C4 delivered, criteria frozen) | MiniMax-M3 (effort override unsupported) / one fresh Astra judge | C4 tip against `d6e78e0b` | NEW assessment report plus own roots | Six unchanged axes; restatement earns nothing; one candidate, one judge, no retry |
| RV-PRIV | Held (needs a PASS) | Qualified assessment family / Astra evaluation (recommended over Sol) | Exact C4 tip (or later corrected tip) | Pinned review paths | Sol fixes; exact re-review |
| CR-01 wire | Held | No qualified pair (section 2.2) | Accepted component on the integration head | Coordinator-leased `websocket.py`, `app.py`, `RestApiServer.stop` path | Real aiohttp `/ws` burst, disconnect, stop and second-client tests; registry and ledger serial |
| RV-WS040 | Held | No qualified browser/kiosk non-OpenAI reviewer | `1fbfee11` against `938ae303` | Pinned | Unchanged |
| API034 M-1 | Held to A3 freeze | Per existing pin | `caaa4faa` | Pinned | Branch-correct proof after freeze; review and evaluation not repeated |
| Inventories | Ready per existing pins | Existing routes | Per pins | Per pins | Unchanged; fill slots that planning does not need |
| CR-02/CR-03 | Author-ready; review held | Not staffed here | Per pins | Per pins | CR-02 capture after the C4 `ha.py` fix |

**Order:** after R3, run WS-C01 alongside PRIV-C4 (disjoint paths), with
G-DISC running in the coordinator. Then WS-R01 alongside PRIV-ASSESS. Then the
Astra judge, plus WS correction 02 only if WS-R01 requires changes. Then RV-PRIV
if the assessment passed. Then A3 serial composition and source freeze, then A4
evidence. The Codex pool carries Sol, Astra review and Astra judge, so sequence
or check them jointly. Each wave closes out (preserve, release, publish, verify
heads) before the next. Tron baselines, physical HIL, the 72-hour soak, the
field week and final version/artifact release keep their owner gates.

## 6. Owner choices (prepared; ask only if the condition occurs)

- **OC-1, if both the MiniMax assessment and any verified Gemini route fail or
  are unavailable.** Rule: `ASSESSMENT_PACKET.json` `attempt_authority` ("ONE new
  domain-assessment candidate and ONE fresh judge. No automatic
  rewrite/retry/extra judge"), plus the 2026-11-03 owner-retake precedent.
  Choice: (a) authorize exactly one second Opus 5.5 privacy-review assessment
  at the C4 tip, with unchanged axes, one Astra judge, the `e8ce3966` FAIL
  preserved and disclosed non-blindness; or (b) keep `RV-PRIVACY-CHAIN` and
  privacy admission held, which blocks A4 privacy admission.
- **OC-2, only if wiring route A cannot be staffed.** Rule: `WS_WORK_TASK.md`
  "No automatic rewrite/retry or implied PASS", plus the same precedent. Choice:
  (a) one bounded Opus WS authorship re-assessment, with WS-WORK-01 preserved;
  a PASS would still need a separate wiring lease; or (b) keep CR-01 wiring held.

Neither choice is needed for the recommended next wave.

## 7. Unresolved disagreements for the R3 packet

1. Privacy assessment subject: the C4 tip (this report, MiniMax R1) or
   `2d02004d` (OpenAI R1). A parallelism benefit trades against discriminative
   power.
2. `DrainReport` shape: a separate unresolved-admission count or folded counts.
   Both can be truthful; the R3 plan should pick one.
3. Wiring route: none is currently qualified. The A/B/C trade-offs need the
   component outcome and the Gemini discovery result.
4. Whether `ha.py` belongs in C4 (OpenAI R1 and this report) or in a separate HA
   package (MiniMax R1).
5. Secondary evaluator for `RV-PRIVACY-CHAIN`: Sol per the pin, or Astra.
6. Unverified: Sol 6.1 route; Gemini route; HA form-default serialization;
   whether credentials reach `ClientState` values.
