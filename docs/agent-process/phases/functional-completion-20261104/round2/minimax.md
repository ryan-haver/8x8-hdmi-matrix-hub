# functional-completion-20261104 — Round 2 all-peer challenge (MiniMax)

**Route:** `opencode2` / `minimax-coding-plan/MiniMax-M3` / thinking inherited / CLI effort
override unsupported. **Family:** MiniMax. Task `task_c512bb417e83`, Dispatch
`ctx_02b4c54eb1fa`, worker terminal `term_9b145a43-b8a9-41d3-bf6f-0f60d5b0f263`,
coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`.

This is a **Round-2 all-peer challenge**: it dispositions every challenge topic in
`ROUND2_PACKET.json` against the three complete R1 originals, and it reconsiders my
own R1 claims. It is **not** an implementation, **not** a qualification attempt or
retake, **not** an extra judge, **not** a budget request, **not** a source/feature
acceptance, and **not** an R3 vote. It authorises no lease and no launch. The
coordinator's one complete hashed final plan/staffing and the three explicit R3
decisions on that same hash remain future.

---

## 0. Bindings, digests and what I actually read

### 0.1 Exact bindings (all recomputed by me from raw Git blob bytes)

| Object | Value | Verification |
| --- | --- | --- |
| `wp-runtime-completion` | **resolved once at entry** → `d576437fe129b3b05cf9ca57a55dd86fbce99707` | local `refs/heads/wp-runtime-completion` == `refs/remotes/origin/wp-runtime-completion` == integration worktree HEAD, all equal at entry; **not re-resolved afterwards** |
| Product source baseline | `9b783d723c81cc56ec86810b789fa31be41e75cc` | ancestor of the resolved head; every source statement below is read at this SHA |
| `ROUND2_PACKET.json` (read **at the resolved integration SHA**) | canonical Git-LF SHA-256 `c37fc7200e6d6384e2b536132090c3affb2b0e98a08b95fc9e94ef8129b0e6fb`, 13 810 bytes, blob `1415bbab8df134302665ab73145dbedaf798a69e` | **MATCH** |
| `INPUT_PACKET.json` (original) at the same SHA | canonical Git-LF SHA-256 `cb6a9871fdf8a4adfb181ab1fbf3abafb6c265323c27b543ebd62f9c68857dc4`, 22 328 bytes | **MATCH** |
| My own base | `planning/remediation-recovery-r1-minimax` @ `32f911a576de0251b06e77a46a39681c7d7dc679` (parent `d9b575cc438f8473d96f106db03629aaa608cde5`) | worktree clean at entry |
| Peer R1 (OpenAI) | head `7baf8262976772ed3de6eac7a19d5fafc7b5a1b8`, parent `ff57e990c93d56ad4c050f399b5e49131949b647`, `round1/openai.md`, SHA-256 `57a634bc5f25c2d6a300e1509e49fa11ed47b5545e3c60bc5d8706132fd29777` | **MATCH**, blob `bcffcb47…` |
| Peer R1 (Anthropic) | head `4ae498baa200cf17f90430f6961c8f1fecd2b8d1`, parent `5097650314502686a845a714e638643d66087971`, `round1/anthropic.md`, SHA-256 `efe8219ca416b2f46b749a621793c4e0d4efe2057fc0958916c689203c3265c1` | **MATCH**, blob `854dcc6e…` |
| Peer R1 (MiniMax, mine) | head `32f911a576de0251b06e77a46a39681c7d7dc679`, parent `d9b575cc438f8473d96f106db03629aaa608cde5`, `round1/minimax.md`, SHA-256 `42bd18882437735caa278279fdf671365890d57a12c0fc0102947d13b71df653` | **MATCH**, blob `bd19c381…` |

All three report blobs are **byte-identical to the blobs preserved in the integration
tree at `d576437f…`**. The originals are preserved unchanged; nothing was regenerated
or edited.

**Extraction honesty.** My first extraction pass used a PowerShell redirection that
merged stderr and converted LF→CRLF, producing three *spurious* hash mismatches. I
discarded that method, re-extracted every blob byte-exactly (`git cat-file blob` via
`cmd /c` redirection, no stream merge), and the three mismatches became exact
matches. The failed method is recorded here rather than hidden.

**Scope of the only new tracked write:** `docs/agent-process/phases/functional-completion-20261104/round2/minimax.md`.
Owned ignored scratch `build/remediation-functional-20261104/minimax-r2/**` (ignored
via `.gitignore:7 build/`) and owned fresh temp `C:/t/remediation-functional/minimax-r2/**`.
No checkout/reset/rebase/cherry-pick; no source import; no helper, subagent, plugin,
MCP, alternate model or nesting; no global config change; no account, spend or
credential. The untracked `.codex/config.toml` is coordinator-owned and remains
unstaged. Source, tests, prior reports, root manifests, locks, registry, ledger,
integration, private data and visual baselines are read-only.

### 0.2 Native model visibility

The coordinator selected `opencode2` with model `minimax-coding-plan/MiniMax-M3`,
effort "unsupported; thinking inherited" (`ROUND2_PACKET.json` `preflight.capacity`
and the dispatch text). That is what the harness reports. It is **not** a backend
attestation of model identity, of the underlying family, or of the effort actually
applied. `native_final` bytes for this dispatch are the coordinator's to collect. I
make **no** independent family-identity claim.

### 0.3 What I read this round, and what that limits

Read **in full, semantically** (not grep/counter/hash claims), at
`9b783d72…` unless stated:

- `src/rest_api/websocket.py` (all 124 lines), `src/rest_api/ws_request_work.py`
  (all 519 lines — **I did not read past line 359 last round; I read the whole
  component this round**), `src/rest_api/events.py` (client registry, `send`/`publish`,
  `refresh`, `poll_once`, `install_event_stream` cleanup), `src/rest_api/app.py`
  (`create_rest_app`, `stop()`), `src/rest_api/security.py` (`route_level`,
  `api_key_valid`, `access_level`, `session_level`, `remembered`, `auth_status`,
  `security_middleware`), `src/hub/runtime/composition.py` (`operation`, `command`,
  `protocol`, `refresh`), `src/hub/runtime/adapters.py` (`TransactionLock`).
- `custom_components/hdmi_matrix/{config_flow,api,__init__,coordinator}.py`,
  `strings.json`, `tests/ha/{helpers,test_config_flow}.py`.
- `web/js/components/{keyboard-shortcuts,settings-panel,settings-drawer,side-nav-drawer,unified-settings-drawer,presets-drawer}.js`,
  `web/js/app.js`, `web/js/core/ws.js`, `web/index.html`.
- `docs/api/WEBSOCKET.md`, `docs/HOME_ASSISTANT.md`, `docs/validation/features.yaml`
  (parsed: 268 features, 50 `F-UI-*`/`F-KIO-*`, **33 at `current: V1` against
  `target: V3`** — my R1 number confirmed), `hacs.json`,
  `tools/validate/clients/ha.py` (version pins), `tools/validate/runner.py::sync`.
- Records: `docs/agent-process/phases/remediation-recovery-20261104/FINAL_PACKET.json`
  (authority, D1–D10, owner_questions, rejected_or_calibrated_peer_claims),
  `docs/production/remediation-20261104/WS-WORK-01/{CANDIDATE_DELIVERY,REVIEW_DELIVERY}.json`,
  `docs/production/remediation-20261104/recovery-execution/{WS_C01_DELIVERY,WS_COMPONENT_INTAKE_RESULT,D6_PROVENANCE_HOLD,PRIVACY_REASSESSMENT_BUDGET_REQUEST}.json`,
  `docs/production/software-waves/QUAL-ANTHROPIC-CORE-01/{execution-20261101,manual-attempt-02,replacement-opus55-20261103}/COORDINATOR_DISPOSITION.json`,
  `CORRECTION-01-REVIEW.md`.
- A **commit-and-trailer census** over the CR-01/02/03/04 target paths at the
  baseline (every commit's message body scanned for `Co-Authored-By`), plus the
  privacy tool paths `tools/validate/{runner,model,evidence}.py` and
  `tools/validate/clients/{api,ha}.py`.

**Semantic-read limits, named honestly.** I did not read
`tests/test_ws_request_work.py` bodies, the 1 502-line focused test corpus, the
`TransactionLock` call sites beyond `composition.py`, `tools/validate/evidence.py`'s
`redact` implementation, `docs/validation/LEDGER.md`, the 61 parser-open register
rows individually, the 545 KB `AGENT_ALLOCATION.md` beyond targeted qualification
searches, or the full comprehensive review report. I did **not** execute product
code, a project test, a runtime campaign, ledger generation or a source hook. The
only execution is the single scoped documentation-module run in §6. **Hashes are
identity, not comprehension**; the read inventory above is what my conclusions rest
on.

### 0.4 The packet-wording discrepancy from my R1 is now closed by the R2 packet itself

My R1 §1.1 recorded that `INPUT_PACKET.json` **does not exist at the product
baseline** and that the correct binding is "product baseline for source, phase
packet at the resolved integration head". `ROUND2_PACKET.json` now states this
explicitly: `original_input_packet.introduced_at = afe24d4d202e6a0ae0a5102b15f76fb95ea9fe22`
and `canonical_git_lf_sha256 = cb6a98…` (which I re-verified at the resolved SHA).
The R2 packet itself was introduced at `eaa05cee01b8ab448e3694fe1d80dc96a3054f44`
— **after** `afe24d4d`, hence **after** the product baseline, exactly as the packet
says. **Nothing is missing or changed; only the original wording was ambiguous, and
my R1 interpretation was the intended one.** The binding for this round is
unambiguous and I record it as: *source statements at `9b783d72…`; phase packets at
the resolved integration SHA `d576437f…`.*

---

## 1. Disposition summary — every packet challenge topic

| # | Packet topic | Anthropic R1 | OpenAI R1 | MiniMax R1 (mine) | **My R2 disposition** |
| --- | --- | --- | --- | --- | --- |
| 1 | CR-01 response policy | coalesce (trailing) | prefer explicit busy rejection + contract review | reject-only first | **MODIFY both, and modify my own**: coalescing is implementable **in the wiring** (component bytes can be untouched); reject-only is **not** contract-free and is worse for the `runner.sync()` first-answer semantics; application-level sharing needs a **start-time guard**; shutdown fence must precede the event-stream stop |
| 2 | CR-01 staffing dispute | Opus (original component author) authors the wiring; Astra reviews | MiniMax async-lifecycle *review* assessment, conditional on an attempt audit | no lawful pair today; propose a genuine first assessment | **REJECT the inversion as already-adopted-rejected**, ACCEPT its structural insight; keep the adopted **D6 review-role** route and supply the **trailer-free target** it needed |
| 3 | CR-02 HA behaviour | options bypass, no reauth, unlocked+bad-key → `invalid_auth`, 404 → old behaviour | options/data **effective-key precedence** after reload | bare-JSON contract, no API-key label/error string, MockHub gap | **ACCEPT both** and add two source-verified residuals neither stated: **empty options key shadows the data key** (sends *no* key), and the probe must be **cookie-free** or `session_level` is not a key verdict |
| 4 | CR-03 UI behaviour | `toggle()` missing, `?` shift mismatch, real settings surface, hidden-tab risk | real controllers, dynamic tabs, zoom suppression, `?` under a layout | `s` and `4` are no-ops; no behavioural test | **RETRACT my "?' is fine"**; accept `toggle()`/`?`/zoom findings; name the visible controller (`window.settingsDrawer.open()` via the overlay registry); split main-UI zoom (routine) from kiosk zoom (owner) |
| 5 | Authorship / independence | propose a prospective exact-change/context rule; trailers as indicators | reconcile native authorship, keep Git trailers as indicators only | D6 discharge is not Git metadata | **MODIFY Anthropic's rule**: keep the directional part, add *affirmative provenance* + *no qualification substitution*; add two facts Anthropic missed (a **third** co-author identity; a **mixed-family** privacy tool chain) |
| 6 | Authority / attempt budget | O-1 privacy; O-2 kiosk zoom; O-3/O-4 image downloads; O-5 advisory queries | privacy; compatibility only if proof requires change; new visuals; physical; field; release | "a first non-privacy assessment always requires owner funding"; one PASS unlocks all three | **RETRACT my owner-funding claim and my "one PASS unlocks all" claim**; first genuinely new-domain/family assessments are **inside** existing owner authority; image pulls and public advisory reads are **not** owner-only; **privacy stays owner-only** |
| 7 | CR-08/09/10 independent lane | M3→Sol truth lane; CR-09 report; CR-10 containers | M3 inventory; Sol/Opus implementation after qualification; compatibility proof | M3→Sol inventory lane; Python 3.11 hub proof | **CONVERGE**, and resolve the peers' inconsistency: the CR-09 *report* needs a **report-quality** reviewer (m3→sol), not a UI source-reviewer; source fixes stay held. Split CR-10 into **proof** (routine) vs **floor change** (policy); correct the target to **exactly 2025.1.0** |
| 8 | All CR01–14 / 30 packages / 65 units | retained, table by package | retained, table by package | retained | **CONFIRM retention**; API034 bounded review/evaluation complete and M-1 held; WS040 distinct from the new component; privacy FAILs terminal; serial shared-tool composition before frozen canonical proof; **no REST route change** in the recommended set, so 100 % route coverage is unaffected in planning |
| 9 | Acceptance evidence / report precision | prose checks are not product proof | same, plus import measurement | same, plus the packet-wording discrepancy | **CONFIRM and close**: the R2 packet itself encodes my R1 reading; R1 prose checks ran on historical checkouts and do **not** prove a new Markdown file parses |
| 10 | Final recommendation | package table with pairs/leases | package table with pairs/leases | phase table F0–F7 | **CONVERGE** on the §5 matrix below; no forced recommendation — the coordinator still owns the choice |

---

## 2. CR-01 — response policy, freshness, lifecycle order

### 2.1 Where I modify my own R1

**(a) "Coalescing necessarily changes the component bytes" — my R1 was too strong.
Anthropic is right, and the component itself says so.**
`src/rest_api/ws_request_work.py:116-126` (the *accepted, reviewed* blob
`145845f4`) records, in its own "Wiring (proposed, not done here)" section:
*"Whether an `OWNER_BUSY` rejection should instead be coalesced with the in-flight
read is a wiring decision with a freshness consequence, recorded in the author
report."* The component's public surface — `try_start(factory) -> Task | RejectReason`,
`RejectReason.{OWNER_BUSY, APPLICATION_BUSY, OWNER_CLOSED, SHUTTING_DOWN}`,
`open_owner()`, `close()/aclose()`, `begin_shutdown()/shutdown()` — is sufficient to
implement a **wiring-level** trailing/single-flight policy **without touching
`ws_request_work.py`**. So the two accepted different-family reviews of `78295ecd…`
can survive **if** the coalescing state machine lives in `websocket.py` (+ the
`app.py` lifecycle hunk). **Modified:** coalescing is *not* automatically a
component-byte change; it is a component-byte change **only** if the shared-refresh
coordination is pushed down into the component.

**(b) "Reject-only is free because the schema is unchanged" — my R1 was wrong on the
documented contract.** `docs/api/WEBSOCKET.md:88` reserves the `error` event for
*"reply to invalid JSON, an unknown command, or `get_status` **when the hub cannot
read the matrix**"*, and `:26` promises `get_status` → `status` *"after a fresh read
of the matrix (status caches bypassed)"*. A busy rejection is a **new documented
trigger**, so **both** policies need a coordinator-owned `docs/api/WEBSOCKET.md`
(+ `docs/api/websocket.schema.json`) lease. Reject-only is *more* contract-invasive
than coalescing: under coalescing `OWNER_BUSY` never reaches the client, while under
reject-only owner-busy becomes a **client-visible failure mode**. **Schema equality
alone does not preserve documented behaviour** — Anthropic's challenge here is
correct, and I adopt it.

**(c) My R1's read-path characterisation was wrong for the deployed path.** I wrote
that `poll_once` takes `self._poll_lock`. Verified: `events.py:313-319` `refresh()`
uses `self.runtime.refresh(force_refresh=True)` when a runtime is present, and
`_poll_lock` (`events.py:330-332`) is only the **no-runtime** fallback. In the real
path, `composition.py:265-272` `refresh()` runs inside `operation()` → `async with
self.transaction` (`composition.py:232`) — the **same `TransactionLock`** that
`command()` (`:245`) and `protocol()` (`:251`) acquire. `TransactionLock` is an
`asyncio.Lock`, reentrant within one task (`adapters.py`). So a `get_status` burst
**queues forced matrix reads that real user commands wait behind**. **Accept
Anthropic's and OpenAI's refinement**; the honest impact description is *forced-read
amplification that delays user commands*, not merely task accumulation. Magnitude
still unmeasured — I did not measure it.

**(d) My R1's shutdown proposal was insufficient.** I proposed "a `cleanup_ctx` that
awaits `shutdown(timeout)`". `app.py:598-616` `stop()` does
`await self.app["event_stream"].stop()` **inside a `try`**, and only in its `finally`
calls `await self.runner.cleanup()` — and `runner.cleanup()` is what runs the app's
`cleanup_ctx`. So the event stream is already stopped **before** any cleanup context
runs, and aiohttp's reverse-order cleanup-context rule cannot rescue the ordering.
**The admission fence must close before the event stream/runtime resources
disappear**, i.e. inside `stop()` (or before `event_stream.stop()`), with the drain
after. Anthropic's "application shutdown must fence all admission before underlying
runtime resources disappear" is the correct requirement. **Self-correction accepted.**

### 2.2 Where I challenge Anthropic's coalescing design

Anthropic proposes *"Per application, a single-flight forced refresh shared by every
waiting owner, plus at most one trailing refresh."* As stated, application-level
sharing can answer a **later** request with a read that **started before** that
request, which breaks `WEBSOCKET.md:26` ("after a fresh read"). Anthropic's own risk
item 2 names the hazard ("a trailing-read bug could silently answer with a
pre-request snapshot") but the design does not exclude it.

**Precise rule I propose (new content, not in any R1):** a request may be answered by
a shared read **only if that read's start time is at/after the request's arrival**;
otherwise a new read must be started. Per-**connection** trailing is safe by
construction (the trailing read starts after the triggering request). Application-level
sharing needs the start-time guard, and the guard is what makes the "≤2 forced reads
per burst" acceptance number meaningful rather than a freshness violation.

### 2.3 Why reject-only is materially worse than it looks (OpenAI's proposal)

`tools/validate/runner.py:253-275` `sync()` marks the event list, sends
`get_status`, then takes **`answers[0] == "status"`** — the **first** `status`-or-
`error` event after the mark — and returns `False` otherwise. A busy `error` therefore
becomes a **false scenario precondition failure** in the validation harness. The
browser client has the same double-send shape: `web/js/core/ws.js:223-225`
`requestStatus()` → `{command:'get_status'}`, and `docs/api/WEBSOCKET.md:112` records
that the UI asks for a fresh `status` after `*_failed` events. Under reject-only a
legitimate second request can be answered with a client-visible error; under
coalescing the client still gets a `status`.

### 2.4 Disposition and the exact contract lease

**Disposition: MODIFY both peers; my R2 preference is wiring-level coalescing
(trailing + start-time-guarded application sharing), because (i) the component bytes
can stay untouched, (ii) the client-visible failure mode disappears, and (iii) the
`runner.sync()` first-answer semantics are preserved.** I do **not** force this: the
choice is the coordinator's contract decision, and the evidence above is what I hand
it.

| Item | Value |
| --- | --- |
| **Coordinator contract lease (required, both policies)** | `docs/api/WEBSOCKET.md` **and** `docs/api/websocket.schema.json` — both are shared contracts and **both carry Anthropic co-author trailers on every commit** (`83e9be49`, `c39ee8d5`, `323af8e4`; schema: `323af8e4`). The author lease must **exclude** them; the coordinator applies the doc change in the same candidate. |
| Author exclusive paths (proposed) | `src/rest_api/websocket.py`; `src/rest_api/app.py` **serial hunk only** (`create_rest_app` owner creation + the `stop()` fence); new `tests/test_ws_get_status_bound.py`; new report path. **Prohibited:** `src/rest_api/ws_request_work.py` (bytes must stay `145845f4…`), `src/rest_api/security.py`, `docs/validation/features.yaml`, `docs/api/**`, root manifests. |
| Negative controls (all required) | (1) 1 000-frame burst on one socket ⇒ ≤2 forced `refresh_snapshot` calls **and** the second read's start ≥ the request that triggered it; (2) `sync()`-shaped double-send still yields `status`; (3) close one socket mid-read ⇒ that owner's tasks cancelled and drained (`remaining == 0` for cooperative work), **another client still works**; (4) app shutdown ⇒ admission fenced **before** `event_stream.stop()`, then drain, then runtime teardown; (5) **resistant** work stays counted and reported, never hidden; (6) no unbounded rejected-work queue and no abandoned coroutine (a rejected request must not call the factory); (7) the `_replies` module global is removed. |
| Acceptance evidence | exact argv/cwd/env/exit/JUnit per invocation; the applied REST/WS registry + route-coverage pipeline (100 % routes retained); `docs/api/WEBSOCKET.md` diff reviewed by the coordinator. |
| Correction reserve | 1 author fix + 1 exact changed-commit different-family re-review. |

---

## 3. CR-01 staffing dispute — the audit

### 3.1 What the records actually say (I read them; I do not infer)

| Record | Verbatim content that governs |
| --- | --- |
| `QUAL-ANTHROPIC-CORE-01/execution-20261101/COORDINATOR_DISPOSITION.json` | Opus 4.7 **FAIL**, `qualified_domains: []`, `further_retry_authorized: false` |
| `QUAL-ANTHROPIC-CORE-01/manual-attempt-02/COORDINATOR_DISPOSITION.json` | Opus 4.7 **FAIL**; `owner_approved_attempt_and_judge_consumed: true`; `further_retry_authorized: false`; `source_acceptance_granted: false`; `review_admission`: *"No qualified domain; RV-API034/RV-WS040/RV-PRIVACY-CHAIN and dependent source acceptance remain held until a suitable actual eligible qualified different-family route is established"* |
| `QUAL-ANTHROPIC-CORE-01/replacement-opus55-20261103/COORDINATOR_DISPOSITION.json` | Opus 5.5 **PASS**, *but* `scope`: *"bounded Python validation-runner/model offline simulator API refusal preparation and relevant compatibility guards"*; `role_limit`: *"bounded review/validation-preparation competence demonstrated; **no general implementation authorship or broad core-review entitlement**"*; `not_granted` includes *"implementation authorship qualification"* and *"authentication/privacy/UI/HA/image/physical domains"*; `automatic_reservation_unlock: false` |
| `WS-WORK-01/REVIEW_DELIVERY.json` (Astra review of the original candidate `15c069bd…`) | `correctness: FAIL`, `component_acceptance: HOLD`, **`bounded_first_authorship: NOT_GRANTED`**; WSR-03 (*"Two helper scripts and commit message written outside explicit scratch lease … violation not waived"*) **blocking**; disposition: *"Accept independent review as blocking negative report; reject candidate correctness. No component/source acceptance, CR-01 closure, **new authorship competence**, automatic correction/exam retake/new judge or existing-handler lease."* |
| `WS-WORK-01/CORRECTION-01-REVIEW.md` (independent review of the corrected source) | *"Original first-authorship qualification \| **NOT_GRANTED / HOLD**; no new competence grant"*; *"Existing handler / WS-WIRING / CR-01 closure \| **HELD**"*; WSR-03 *"**Historical FAIL**, neither waived nor rewritten; **correction does not grant first-authorship competence**"* |
| `recovery-execution/WS_C01_DELIVERY.json` | `qualification`: *"**NOT_GRANTED: original first-authorship HOLD/WSR03 FAIL remain immutable. Delivery/tests cannot close component review or CR01.**"* |
| `recovery-execution/WS_COMPONENT_INTAKE_RESULT.json` | component **integrated** (`e54228c0`), two different-family reviews (`ed697083`, `9817554e`), but `readiness`: *"Component only. Handler/app/events/runtime imports/wiring, CR-01 network bound, D6 reviewer independence … remain held."* |
| `recovery-execution/D6_PROVENANCE_HOLD.json` | `status: HELD / NOT_DISPATCHABLE_AS_SCOPED`; the trailers on `websocket.py`/`app.py` are *"conflict indicators, not a replacement for actual native source-family attribution"*; `candidate_attempts_launched: 0`; `wiring_leases_granted: 0` |
| **Adopted** `remediation-recovery-20261104/FINAL_PACKET.json` **D6** | *"**No immediate CR-01 wiring lease.** Prepare a distinct FIRST Anthropic **review-role** assessment of original non-Anthropic existing WS/app/runtime lifecycle source, excluding every authored controller/correction path; judge Astra/high."* Limits: *"Before dispatch prove exact target source is not Anthropic-authored… No owner retake is requested/authorized… After any PASS, Sol-authored wiring still needs separate exact-commit independent review; any change to the Anthropic controller returns to its author plus Astra, not Opus self-review."* |
| **Adopted** `FINAL_PACKET.json` `rejected_or_calibrated_peer_claims[0]` | *"**Reject immediate Opus wiring entitlement**: outside-scope wiring is not evidence of author competence and the original pre-competence existing-API lease is explicit. **No qualified complete wiring pair exists today.**"* |
| **Adopted** `FINAL_PACKET.json` **D1** limits | *"No new all-six authorship judgement, retrospective PASS, broad author grant or existing-handler lease."* |

### 3.2 Disposition

**ACCEPT Anthropic's structural insight** — the inversion does correctly identify that
the D6 conflict is a **review-side** conflict: if Anthropic authored the wiring,
Anthropic would not be reviewing it.

**REJECT Anthropic's conclusion.** It (i) repeats a claim the adopted plan **already
rejected in writing** (`rejected_or_calibrated_peer_claims[0]`), (ii) rests on a
record that **withholds** authorship competence (the Opus 5.5 `not_granted` list; the
WS-WORK-01 `NOT_GRANTED` / WSR-03 / "correction does not grant first-authorship
competence" chain; the coordinator's explicit *"No … new authorship competence …
or existing-handler lease"*), and (iii) offers a **second** attempt in the WS-runtime
implementation domain, where the **first** attempt (the original candidate) already
failed. A **corrected** component acceptance is a **source** acceptance; it is not an
authorisation record for new authorship, and the adopted plan says so explicitly
("outside-scope wiring is not evidence of author competence").

**ACCEPT MiniMax-R1/OpenAI's conclusion** that no lawful pair exists today — but
**modify the remedy**: the adopted **D6 review-role** route is not merely a fallback;
it is the **lawful** route, and my R1's framing of it as "one of two options" was
too weak. D6 already picks the reviewer side for Anthropic, and the open item was
never the *choice* of route — it was the **target provenance**.

### 3.3 New: a trailer-free D6 assessment target now exists (verified)

D6 requires *"original non-Anthropic existing WS/app/runtime lifecycle source,
excluding every authored controller/correction path"*, and *"prove exact target source
is not Anthropic-authored"*. I ran a full commit-and-trailer census at the baseline
(`Co-Authored-By` in every commit body):

| Path | commits | trailers | Anthropic | other |
| --- | --- | --- | --- | --- |
| `src/hub/runtime/composition.py` | 10 | **0** | 0 | — |
| `src/hub/runtime/adapters.py` | 4 | **0** | 0 | — |
| `src/rest_api/security.py` | 3 | **0** | 0 | — |
| `src/rest_api/events.py` | 4 | 2 | 2 | — |
| `src/rest_api/websocket.py` | 8 | 3 | 3 | — |
| `src/rest_api/app.py` | 20 | 4 | 2 | **2 × `Co-authored-by: Sisyphus <sisyphus@example.com>`** |
| `web/index.html` | 21 | 3 | 1 | **1 × `Co-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>`** |
| `web/js/components/settings-panel.js` | 6 | 2 | 1 | 1 × Sisyphus |
| `web/js/components/keyboard-shortcuts.js` | 2 | **0** | 0 | — |
| `custom_components/hdmi_matrix/{config_flow,api,__init__,coordinator,services,const}.py`, `strings.json`, `translations/en.json`, `manifest.json`, `icons.json` | — | all | **all** | — |

`src/hub/runtime/composition.py` + `src/hub/runtime/adapters.py` are the **runtime
lifecycle** (operation/command/protocol/refresh + `TransactionLock`) — exactly the
WS/app/runtime lifecycle semantics D6 names — carry **zero** co-author trailers, and
are **not** the Anthropic-authored controller or correction paths. They are the
**cleanest lawful D6 target**. `websocket.py`/`app.py`/`events.py` must stay
**excluded**.

**Corroboration is still required and is not optional:** trailer absence is *not*
provenance. D6's remedy must still be discharged from native/task/history records,
and the *acceptance claim* must be scoped to the reviewed target only. I flag this
rather than treating the census as proof.

---

## 4. CR-02, CR-03, authorship rule, authority and the independent lane

### 4.1 CR-02 — dispositions and two added residuals

**ACCEPT OpenAI's effective-key precedence** (verified at `__init__.py:28-31`:
`entry.options.get(CONF_API_KEY, entry.data.get(CONF_API_KEY))` — **options wins**;
`config_flow.py:100-116` reconfigure writes `data_updates`, i.e. **data** only) and
**ACCEPT Anthropic's options bypass** (`config_flow.py:132-136` stores an options key
with **no probe**) and **no-reauth** finding (no `async_step_reauth` and no
`ConfigEntryAuthFailed` anywhere in `custom_components/` or `tests/ha/`;
`coordinator.py:100-118` polls only public GETs, so a revoked key is invisible until
a write 401s). **ACCEPT my own R1's** bare-JSON contract trap (`security.py:267-269`
returns a bare object; `api.py:69-70` requires `success is True`), the missing
API-key label and error string (`strings.json` `config.step.user.data` has only
`host`/`port`; `config.error` has only `cannot_connect`/`unknown`), and the
`MockHub` gap (`tests/ha/helpers.py:39-43` registers five read routes and no
`/api/auth/status`; the catch-all at `:86` is a **POST** regex, so a GET there is
unrouted).

**Added residual 1 — the empty options key silently shadows the data key.** `api.py:54`
is `if self.api_key:` — an **empty string** sends **no** `X-API-Key` header at all.
`config_flow.py:134` only pops the key when it is absent from **both** data and
options; if the key is in `entry.data` and the user *clears* the options field, the
options flow stores `""`, and `entry.options.get(CONF_API_KEY, entry.data.get(...))`
returns the **present-but-empty** `""` — so the effective key becomes *no key*, and
the valid data key is discarded. Neither peer stated this mechanism; OpenAI listed
"empty-key removal" only as a case to test. It is an **acceptance case with a named
mechanism**.

**Added residual 2 — the probe must be cookie-free, or `session_level` is not a key
verdict.** `security.py:269` returns `"session_level": security.access_level(request)`
— the field name is misleading: it is the **effective** level, and `access_level`
(`:217-223`) is `"control"` if a session is control **or a device is remembered**
**or** `api_key_valid` is true. Home Assistant's shared `aiohttp` session is a
shared, cookie-carrying session; the hub sets its session/device cookies only from
its own browser-facing login/device endpoints, which this integration never calls —
so in practice the key signal is not masked, but that is an *assumption about the
client jar*, not a guarantee. A stray control cookie would make a **wrong** key look
valid. **Therefore the probe must be issued so that no session/device cookie can be
present** (a dedicated cookie-free session for the auth probe, or an equivalent
guarantee), and the tests must prove the negative case. Otherwise the *whole*
wrong/missing/revoked matrix rests on an unproven precondition.

**ACCEPT Anthropic's unlocked-hub recommendation, with a correction.** Anthropic
proposes `invalid_auth` when the hub is *not* control-locked but a supplied key
yields `"none"`. I concur, and correct the reason Anthropic gave ("the user typed a
key the hub does not recognize"): `api_key_valid` (`security.py:209-215`) checks
stored key hashes and the `API_KEY`/`CONTROL_API_KEY` environment variables
**regardless of lock state**, so a supplied key that yields `"none"` is
*demonstrably* invalid even on an unlocked hub — **this is not an owner choice**.
The genuinely undecided case is only **404 / capability unknown on an older hub**
(keep today's behaviour + a debug log), which must not be "solved" by changing the
hub's API shape. **No mutating probes**: no unlock/login/PIN attempts, so
`verify_pin` rate limits are never touched.

**CR-02 package shape (proposed).** Author: OpenAI `gpt-6.1-sol/high` (the recorded
core author; keeps the `SW-HA-PREP` reservation). Reviewer: **not yet available** —
see §5. Exclusive paths: `custom_components/hdmi_matrix/{api.py,config_flow.py,__init__.py,strings.json,translations/en.json}`,
`tests/ha/{helpers.py,test_config_flow.py,test_api.py}`, plus a named new auth test.
**Prohibited:** `src/rest_api/**` (the hub side needs no change — `/api/auth/status`
already exists), `tools/validate/**`, root manifests.

### 4.2 CR-03 — I retract one of my own R1 claims

**RETRACTION: my R1 said "`'?'` and `Escape` are fine." That was wrong.** Verified in
`keyboard-shortcuts.js:147-173`: `handleKeydown` builds
`{ctrl, shift, alt, meta, key: e.key.toLowerCase()}` and `keyToId` (`:103-111`)
prefixes active modifiers. On any layout where `?` requires Shift, `e.shiftKey` is
`true`, so the lookup id is **`"shift+?"`**, while `register('?')` (`:53-55`) stores
the id **`"?"`**. The lookup misses ⇒ **the help shortcut never fires**. Anthropic is
right and I adopt the correction (it matches the `dialog/keyboard-shortcuts` visual
catalogue note).

**ACCEPT Anthropic's "`SettingsPanel` has no `toggle()`"** — verified:
`settings-panel.js` exposes `open()` (`:380`) and `close()` (`:401`) only; `window.settingsPanel`
is **never assigned**; `window.SettingsPanel = SettingsPanel` (`:638`) is the **class**;
the instance is `window.app.components.settingsPanel` (`app.js:141-142`). So `'s'`
is a silent no-op today and would **throw** if the global were merely set.

**Name the real visible controller** (new, precise): the settings surface the UI
actually uses is the **unified settings drawer** — `unified-settings-drawer.js:201-202`
prefers `window.overlayManager.overlays?.get('settings-drawer')` and falls back to
`window.settingsDrawer.open(targetSection)`; the drawer is the *Profiles | Scenes |
System* surface (`settings-drawer.js:12, 67, 102`). `window.sideNavDrawer.open()`
(`presets-drawer.js:91-92`) is a **different** drawer (the nav drawer). The fix must
call **the same path the visible Settings button calls**, determined by browser
reproduction — not by name-matching, and not by reviving the legacy modal.

**ACCEPT the `'4'` correction**: `getTabSpecs()` returns exactly
`dashboard|matrix|inputs|outputs|profiles` (`side-nav-drawer.js`), `web/index.html`
carries the same five `data-tab` values, and the **only** `data-tab="scenes"` is the
**drawer tab** (`settings-drawer.js:67`), present only while the drawer is rendered.
So `'4'` must target `profiles` (keeping the "Profiles/Scenes" wording).

**ACCEPT OpenAI's dynamic-tab caution** (unverified, browser-only): `app.js:326`
renders tab buttons from `getTabSpecs()`, so `document.querySelector('[data-tab="matrix"]')`
returns the **first** document-order match, which may be a hidden or
preference-suppressed tab; clicking a hidden tab may navigate somewhere the user hid.
Label it as a hypothesis requiring a browser check, exactly as Anthropic did.

**ACCEPT OpenAI's zoom finding, which my R1 missed**: `web/index.html:5-8`
`content="width=device-width, initial-scale=1.0, user-scalable=no"` and
`web/kiosk.html:5` `maximum-scale=1.0, user-scalable=no`.

**Zoom scope split (my position):** restoring zoom on the **main** `/ui` is a routine
software correction (no owner device, no baseline change); the **kiosk** zoom
suppression is a genuine owner choice about their own wall panel. The main-UI fix
must not be gated on the kiosk decision.

**CR-03 package shape (proposed).** Author: OpenAI `gpt-6.1-sol/high` (keeps the
`SW-UI-PRESENT-01` reservation). Reviewer: **not yet available** (§5). Exclusive
paths: `web/js/components/keyboard-shortcuts.js` (+ only the named controller/drawer
call site), a new `tests/e2e/functional-keyboard.spec.ts`, report path.
**Prohibited:** `tests/e2e/visual/__snapshots__/**` and `web/css/**` (immutable
baselines), and `web/index.html` unless a named zoom lease is granted. Acceptance:
positive **and** negative browser controls for `s`, `4`, `?`, `1` (positive control),
editable-descendant / SELECT / textarea / contenteditable suppression, modifier
handling, Escape blur + topmost-overlay close, and the **personalized** tab case
(a hidden tab must not be navigated to). A reproduction report is **not** a qualified
source review.

### 4.3 Authorship / independence rule — MODIFY Anthropic's proposal

**ACCEPT the directional part.** Anthropic's rule — independence is assessed against
the authorship of the **exact change under review**; a historical co-author indicator
on unchanged surrounding lines is **disclosed** and blocks a review only when the
acceptance claim covers those historical lines — matches the D6 hold's own wording
(*"conflict indicators, not a replacement for actual native source-family
attribution"*). It is the right shape.

**REJECT three weaknesses**, and add two facts Anthropic did not report:

1. **It cannot substitute for affirmative provenance.** D6's remedy requires
   *"prove exact target source is not Anthropic-authored"*. The rule is about
   *disclosure of indicators*; it does not establish non-authorship. Any prospective
   use of it must be paired with an **affirmative native/task/history provenance
   record for the exact reviewed diff**.
2. **It cannot substitute for the qualification gate.** Anthropic's own §6 still
   requires a first-attempt HA/UI assessment; `QUAL-ANTHROPIC-CORE-01` `not_granted`
   lists *"authentication/privacy/UI/HA/image/physical domains"*. A **bounded domain
   PASS does not unlock unrelated domains** — this is a packet instruction and a
   repository rule, and it is the precise point on which my R1 §4.3 was wrong (§6).
3. **It must not be applied to the whole-target privacy review.** Anthropic already
   concludes the privacy proposal stays blocked under it, because the privacy
   acceptance claim necessarily covers the chain *plus* the redaction behaviour of
   pre-existing code. I concur and keep the **privacy whole-chain review distinct
   from any new bounded diff**.

**New fact 1 — the trailer set is not a family partition.** `src/rest_api/app.py`
carries `Co-authored-by: Sisyphus <sisyphus@example.com>` (commits `725ef268`,
`a148bd84`); `web/index.html` and `web/js/components/settings-panel.js` carry
`Co-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>`. There are therefore at
least **three** distinct co-author labels in the history. A trailer is **neither**
proof of family **nor** its absence proof of provenance.

**New fact 2 — the privacy tool chain is mixed-family.** At the baseline:
`tools/validate/runner.py` — 11 Anthropic + **2 `OpenAI Codex`** trailers (of 17
commits); `tools/validate/model.py` — 10 Anthropic + **2 `OpenAI Codex`**;
`tools/validate/clients/api.py` — 6 Anthropic; `tools/validate/clients/ha.py` — 1
Anthropic; `tools/validate/evidence.py` — 2 Anthropic. This corroborates OpenAI's
"prior OpenAI chain authorship" point (the chain `d6e78e0b…53853257` is
**Sol-authored**, 13 paths / 8 commits, and carries **no** trailers of its own)
while showing that the *subject paths* carry indicators from **two** families. That
is precisely why the pending extra-Opus privacy assessment would face a D6-class
indicator and why adopted **D4/D5** chose "a genuinely new family on the exact
corrected tip" instead.

**New fact 3 — the CR-01 contract file is fully indicator-bearing.**
`docs/api/WEBSOCKET.md` has an Anthropic trailer on **3 of 3** commits and
`docs/api/websocket.schema.json` on **1 of 1**. Under Anthropic's own rule, an
Anthropic reviewer of the CR-01 wiring must have its acceptance claim **scoped to
the diff**, with the contract doc change applied by the **coordinator**; otherwise
its own rule blocks the review.

**Note on `docs/validation/features.yaml`:** heavily indicator-bearing (≈40 Anthropic
+ 1 Codex trailers), but it is **coordinator-owned** and the CR-08/CR-09 deliverable
is prose/inventory, not source — so no source-review conflict arises there.

### 4.4 Authority and attempt budget — I retract two claims of my own

**RETRACTION 1 (material):** my R1 said the first non-privacy assessment "always
requires owner funding" and listed a "Gate Q (owner-funded)" and an owner decision
O-1 to fund it. **The controlling rule does not say that.** The adopted
`remediation-recovery-20261104/FINAL_PACKET.json` `owner_questions` reads: *"**None
for the next covered product corrections, first genuinely new-domain/family
assessments or read-only discovery.** An exhausted-competence-attempt budget
expansion remains owner-only if ever chosen later; not requested or authorized here.
Prepare exact bounded choice/cite controlling rule only if required after useful
alternatives fail, no automatic retakes."* And `authority`: *"Owner now enact the plan
and remediate all findings … No new accounts/spend/credentials, owner
hardware/visual/soak/field/final-release authority."* **A first genuinely
new-domain/family assessment is inside existing owner authority and needs no owner
budget action.** My R1 invented an owner gate the controlling rule does not impose.
The repository's standing direction says the same: *"Do not fabricate an owner budget
restriction for routine authorized software, downloads or public advisory reads."*

**RETRACTION 2:** my R1 said "running one first is enough to open CR-01/CR-02/CR-03,
because the reviewer's family is what matters". **Wrong.** A bounded domain PASS
unlocks **that domain only**. CR-01 (runtime lifecycle review), CR-02 (HA
authentication-capability review) and CR-03 (browser/UI-behaviour review) are
**three distinct domains**; no single earned qualification covers all three, and
`not_granted` names them separately. This is exactly the packet's warning that "one
bounded domain PASS does not unlock unrelated domains".

**Where the owner-only requirement genuinely bites** (unchanged, and I do not
reinterpret it): the **pending privacy extra assessment** — one Opus candidate + one
Astra judge under the unchanged six privacy axes — is an **exhausted-budget**
expansion and stays `OWNER_APPROVAL_REQUIRED` (`PRIVACY_REASSESSMENT_BUDGET_REQUEST.json`).
The Opus-first privacy FAIL and the M3-first privacy FAIL (judge `1b2b7c5f`, 2 PASS /
4 FAIL) remain **terminal**. No broad "continue"/wake instruction, elapsed time, or a
planning vote may be read as approval of that attempt.

**Where I challenge Anthropic's owner-asking (over-restriction):**

- **Image pulls for disposable environments** (Anthropic O-3/O-4): a digest-pinned
  `python:3.11-slim` / `homeassistant/home-assistant:2025.1.0` pull is **routine
  environment provision** — no spend, no account, no credential, no owner hardware.
  It is **not** owner-only; it is a coordinator dispatch decision. (Digest pinning
  and immutable image identity recording are still correct.)
- **Public advisory queries** (Anthropic O-5): the dependency inventory is already
  public in `requirements*.txt` / `package-lock.json`; a public OSV/npm query
  publishes nothing private. **Not** owner-only. *Caveat, to be measured rather than
  assumed:* a host configured with a private registry proxy would change this — so
  the environment is to be inspected first and the result recorded.
- **Kiosk zoom** (Anthropic O-2): split, as in §4.2 — main-UI zoom restore is
  routine; the kiosk zoom is a real owner choice.
- **Compatibility floor** (my R1 O-4 / Anthropic O-3/O-4): split — *proving* the
  declared floor is routine software work; *changing* the declared floor is an
  approved compatibility-policy decision, which CR-10's own acceptance explicitly
  contemplates.

**And the one of my own R1 items that survives:** the two **provisional kiosk
viewports** (`tests/e2e/support/viewports.ts`, explicitly *"PROVISIONAL: the browser's
CSS viewport is not confirmed"*, asking for a device reading) genuinely require the
owner's device. It stays an owner item.

### 4.5 The CR-08/09/10 independent lane — convergence and one correction

| Lane | Author | Reviewer | Independence | Ready? |
| --- | --- | --- | --- | --- |
| **TRUTH (CR-08)** — 61 parser-open rows → disposition; one dated authoritative current summary | **MiniMax M3** (earned planning/prose/inventory scope) | **OpenAI `gpt-6.1-sol/high`** | MiniMax → OpenAI, **cross-family** | **READY now** — deliverable is prose/registry metadata, not source; the coordinator alone applies canonical registry/ledger/summary edits. Corroborate the peers' stale-item finding: `EXECUTION_GATE_STATUS.json.remediation_authority.state` still says *"wave1 active: NEW bounded WS component authorship assessment…"* although the component is integrated (`e54228c0`) — add it to the dated correction. HIL-09 keeps its 12 caps; UC-18 / the old LICENSE-stub text are **not** current reproduced defects. |
| **A11Y-REPRO (CR-09)** — 33 `V1` UI/KIO features → per-feature reproduce plan; the 2 provisional kiosk viewports flagged as owner-device-dependent | **MiniMax M3** | **OpenAI `gpt-6.1-sol/high`** | cross-family | **READY as a report** (not source). **Resolves the peers' inconsistency:** Anthropic assigns Opus to review a UI reproduction report although Opus holds no UI qualification; OpenAI defers implementation/review to after UI qualification. My resolution: the *report* needs a **report-quality** reviewer, which the existing `m3 → sol` pairing already provides; **any source correction it motivates is a separate package needing a qualified different-family UI reviewer, which does not exist yet — so those corrections stay held.** |
| **SUPPORT (CR-10)** — declared-floor **proof** | **OpenAI `gpt-6.1-sol/high`** (compatibility author) or MiniMax for the run receipt | **OpenAI** for a MiniMax run receipt (cross-family) | cross-family | **READY as proof**, subject to a fresh quota check and image availability. Not owner-gated. |
| **SUPPORT-POLICY (CR-10)** — a *change* to the declared floor | — | — | — | **Owner/policy**, and only **if** the proof fails. |

**CR-10 corrections that matter (new):**

1. **The exact declared floor is `2025.1.0`** (`hacs.json`: `"homeassistant":
   "2025.1.0"`; `docs/HOME_ASSISTANT.md:3` and `:628` say *"Home Assistant 2025.1+"*).
2. **The tool's nominal minimum check is a *different* patch**: `tools/validate/clients/ha.py`
   documents *"``VALIDATE_HA_IMAGE=homeassistant/home-assistant:2025.1.4`` checks the
   minimum version (D8)"* and defaults to `DEFAULT_IMAGE =
   "homeassistant/home-assistant:2026.9.3"`. So even the tool's stated minimum check
   does **not** cover the declared floor — the proof must exercise **exactly
   2025.1.0**.
3. **The HA fixture pins a third version**: `requirements-test-ha.txt` pins
   `pytest-homeassistant-custom-component==0.13.316`, whose own comment maps it to
   `homeassistant==2026.2.3`, run on **Python 3.13**.
4. **Keep my R1's axis separation** (neither peer stated it): the hub package's
   `requires-python >= 3.11` claim is about **`src/`**, and CI's core job runs
   **Python 3.12** — 3.11 is never exercised. The HA 2025.1 claim is about the
   **custom component**, which runs inside HA's own Python (HA 2025.1 requires
   Python 3.13), so "prove Python 3.11" **cannot** mean "run the HA suite under
   3.11". Two independent axes, two separate proofs.
5. Fixture generator: `tools/gen_contract_fixtures.py` is **shared** → its outputs
   need an exact **serial** lease (Anthropic's TST-02 point, accepted).

---

## 5. Consolidated staffing / acceptance matrix (a proposal for the coordinator, not an adoption)

### 5.1 Gates

| Gate | Meaning | Status |
| --- | --- | --- |
| **G0** | Adopted plan + one complete hashed final plan + staffing, and three explicit R3 decisions on that hash | **pending** (not mine to give) |
| **G1** | One **first** review-role assessment in a bounded, **trailer-free** domain (§3.3), judged by a different family, under the frozen rubric, with the attempt-history audit recorded | **the only new qualification needed** |
| **G2** | D6 provenance hold discharged for the exact assessment target (native/task/history), not by trailers alone | required before G1 dispatches |
| **G3** | Coordinator contract lease for `docs/api/WEBSOCKET.md` + `websocket.schema.json` | required for CR-01 under **either** policy |
| **G4** | Owner decisions only: privacy extra attempt; kiosk viewports; kiosk zoom; declared-floor change (if the proof fails); physical/72 h/week; final release | see §6 |
| **G-HELD** | Privacy chain (CR-04/05 admission), M-1 (CR-06), WS040, canonical CR-07, all CR-11/12/13 owner gates | **unchanged, terminal as recorded** |

### 5.2 Packages

| Package | Scope | Author (family) | Reviewer (family) | Exclusive lexical lease | Exact base | Dependencies | Acceptance / negative controls | Correction reserve | Ready? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **P1 TRUTH** | CR-08 reconciliation | MiniMax M3 | OpenAI Sol | new prose only under the phase dir + a new report path; **read-only** on `docs/REMEDIATION_PLAN.md`, `docs/validation/features.yaml`, `LEDGER.md`, `findings_pending.yaml` | resolved integration SHA at dispatch | none | every parser-open row dispositioned with surviving condition + accepted proof ref; HIL-09 not closed, 12 caps kept; UC-18/LICENSE-stub not called current defects; one dated current summary; coordinator applies canonical edits | 1 fix + 1 re-review | **READY** |
| **P2 A11Y-REPRO** | CR-09 reproduce plan | MiniMax M3 | OpenAI Sol | new report + new inventory artifacts only; **no** `web/`, **no** `tests/e2e/visual/__snapshots__/**` | resolved integration SHA at dispatch | P1 | all 33 `V1` UI/KIO features enumerated with a reproduce plan; the 2 provisional kiosk viewports flagged owner-device-dependent and **not** re-baselined | 1 fix + 1 re-review | **READY** |
| **P3 SUPPORT-PROOF** | CR-10 declared-floor proof | OpenAI Sol | OpenAI Astra (if MiniMax authors the run receipt) | owned run roots + report path; `tools/validate/clients/ha.py` comment fix by lease only | resolved integration SHA at dispatch | fresh quota + image availability | **exactly** HA 2025.1.0 (by digest) install/setup/auth/reconfigure/options/unload/reload + HACS custom-repo upgrade, **and** the hub package's own suite under **Python 3.11**; raw argv/exit/JUnit/image digests; unavailable environment recorded as an explicit limitation, **not** as a pass or a failure | 1 fix + 1 re-review | **READY** (not owner-gated) |
| **P4 D6-ASSESS** | first Anthropic **review-role** assessment on `src/hub/runtime/composition.py` + `adapters.py` | Anthropic Opus 5.5/high **candidate** | OpenAI Astra/high **judge** | review-only: the named target files, a new report path | resolved integration SHA at dispatch | G2 | six frozen domain standards (lifecycle ordering, transaction/ownership discipline, truthful drain semantics, admission atomicity, failure handling, calibration); the exact target's non-Anthropic provenance discharged from native/task/history; a FAIL is **terminal for this attempt** and does not block P1–P3 | 1 correction + 1 re-review within the assessment's own reserve | after G1/G2 |
| **P5 CR-01 wiring** | CR-01 | OpenAI Sol (author) — **conditional** | Anthropic Opus 5.5/high **only after P4 PASS**; otherwise **held** | `src/rest_api/websocket.py`; `src/rest_api/app.py` **serial hunk**; new `tests/test_ws_get_status_bound.py`; report path. **Prohibited:** `src/rest_api/ws_request_work.py` (bytes stay `145845f4…`), `docs/api/**`, `docs/validation/features.yaml`, root manifests | resolved integration SHA at dispatch | G3 + P4 PASS + G0 | the §2.4 negative controls (1)–(7) | 1 fix + 1 re-review | **held** on P4 |
| **P6 CR-02** | CR-02 | OpenAI Sol | **not yet available** — a distinct HA authentication-capability review domain is needed | `custom_components/hdmi_matrix/{api.py,config_flow.py,__init__.py,strings.json,translations/en.json}`; `tests/ha/{helpers.py,test_config_flow.py,test_api.py}`; a named new auth test. **Prohibited:** `src/rest_api/**`, `tools/validate/**` | resolved integration SHA at dispatch | G0 + a reviewer | dedicated cookie-free probe; bare-JSON reader that does not bend `_request`; wrong/missing/revoked/valid on a **control-locked** hub ⇒ correctable error; unlocked/no-key and matrix-offline still work; **empty options key shadows the data key** (regression case); reconfigure-write vs stale-options precedence case; 404-capability case; `MockHub` gains `/api/auth/status`; the two existing assertions updated **deliberately** with the `X-API-Key`-on-every-call invariant preserved; **no mutating probe** | 1 fix + 1 re-review | **held** on a reviewer |
| **P7 CR-03** | CR-03 | OpenAI Sol | **not yet available** — a distinct browser/UI-behaviour review domain is needed | `web/js/components/keyboard-shortcuts.js` + the named controller/drawer call site; a new `tests/e2e/functional-keyboard.spec.ts`; report path. **Prohibited:** `tests/e2e/visual/__snapshots__/**`, `web/css/**`, `web/index.html` (unless a named zoom lease) | resolved integration SHA at dispatch | G0 + a reviewer | `s` reaches the **visible** settings surface; `4` reaches `profiles`; `?` works under the declared layout; `1` positive control; editable/SELECT/textarea/contenteditable suppression; modifier handling; Escape blur + topmost-overlay close; **personalized/hidden-tab** case; `isTypingTarget` semantics unchanged; **no baseline change** | 1 fix + 1 re-review | **held** on a reviewer |

### 5.3 Checked fallback matrix (the one staffing fact all three reports agree on)

| If… | Then | Fallback checked |
| --- | --- | --- |
| The Anthropic review-role assessment **PASSes** | Anthropic becomes a qualified runtime-lifecycle **reviewer** → P5 proceeds with Anthropic reviewing Sol's wiring, acceptance claim scoped to the diff, contract docs applied by the coordinator | Sol-authored wiring still needs separate exact-commit independent review (D6) |
| The Anthropic assessment **FAILs** | **Terminal for that attempt.** No retake, no extra judge, no alias escape, no family substitution. P5 stays held; P1–P3 continue | the only remaining candidate family is **MiniMax** as a *source reviewer* — a genuine **first** assessment (different role from inventory authorship, different domain from the failed privacy domain), judged by Astra, and **not** a relabelled retake. Its earned scope is *"bounded evidence inventories only"*, so this is a new role, not an extension |
| MiniMax's source-review assessment **PASSes** | MiniMax becomes a qualified source reviewer → P6/P7 may pair MiniMax-review against a Sol/OpenAI author, and P5's reviewer slot is no longer Anthropic-dependent | family must differ from the author; OpenAI-authored source cannot be reviewed by OpenAI |
| Both FAIL | P5/P6/P7 stay **held** for lack of a qualified different-family reviewer. P1–P3 continue unaffected | this is a **routing constraint, not a project-wide stop** |
| Google/Gemini becomes viable | only as a **prospective different-family** option after authentic native/helper/access/quota **and** domain qualification are established without unauthorised account changes | Gemini CLI OAuth disabled; Antigravity's weekly bucket was ~19–20 % remaining and its underlying family/helper identity unresolved ⇒ **not** a verified qualified fallback. **DeepSeek: never dispatch, never buy credit.** |

---

## 6. Unresolved material disagreements and the owner choices that actually exist

### 6.1 Material disagreements I did **not** resolve (for the coordinator and R3)

1. **CR-01 response policy.** Coalescing (Anthropic) vs explicit busy rejection
   (OpenAI) vs reject-only-first (my R1). My R2 position favours **wiring-level
   coalescing** on the `runner.sync()` first-answer evidence (§2.3) and the smaller
   contract delta, **but the choice is the coordinator's** and both policies need the
   same coordinator contract lease. The **only** sub-question I settle is that
   application-level sharing needs a **start-time guard** (§2.2).
2. **CR-01 staffing.** Anthropic's inversion (Opus authors, Astra reviews) vs the
   adopted **D6 review-role** route. My R2 position: **D6** (§3.2), now with a
   concrete trailer-free target (§3.3). Anthropic's inversion remains rejected on the
   record, but I record it as **live disagreement** rather than a settled point.
3. **The exact-change/context rule.** Anthropic's form vs a strict indicator rule.
   My R2 position: **modified** Anthropic — disclosure plus affirmative provenance
   plus no substitution for the qualification gate (§4.3). If R3 rejects the
   modification, CR-02's review and the pending privacy proposal both stay held,
   which is acceptable and is not a failure.
4. **The unbound vs locked "bad key" case** — Anthropic recommends `invalid_auth`;
   I concur and give the reason, and add the cookie-free-probe requirement that
   both peers' proposals need and neither stated (§4.1).
5. **The D6 assessment target.** I propose `composition.py` + `adapters.py`. Peers
   proposed no specific target. The coordinator must confirm the provenance record.

### 6.2 Owner-only decisions that **actually** exist (derived from the controlling rules only)

| # | Decision | Why it is genuinely owner-only | Options |
| --- | --- | --- | --- |
| **O-1** | The **pending privacy extra assessment** (one Opus candidate + one Astra judge, unchanged six axes) | **exhausted-competence-attempt budget expansion** — the adopted `FINAL_PACKET` `owner_questions` reserves this to the owner | (a) approve, knowing the subject paths carry Anthropic/OpenAI indicators (§4.3) and the D6 rule must be applied consistently; (b) decline and keep privacy HELD; (c) enable a third family for a first privacy assessment. **Anthropic recommends (b) or (c); I concur with (b)/(c) and note (a) risks a second D6-class conflict.** |
| **O-2** | The **two provisional kiosk viewports** | the readings are from the owner's own devices | confirm the two CSS viewports (a `whatismyviewport.com` reading in the kiosk browser mode actually used) |
| **O-3** | **Kiosk zoom suppression** (`web/kiosk.html:5`) | a deliberate choice about the owner's own wall panel | keep `user-scalable=no` on `/kiosk`, or allow zoom. **The main `/ui` zoom restore is *not* owner-gated** and must not wait on this. |
| **O-4** | The declared **HA / Python floor**, **only if** the CR-10 proof fails | a claim change is an approved compatibility-policy decision | keep HA 2025.1.0 / Python ≥3.11 and fix the incompatibility, or approve an evidenced new minimum with its upgrade impact. **The proof itself is not owner-gated.** |
| **O-5** | **Physical / field gates** (CR-11, CR-13) | owner devices, a continuous 72 h window and a field week | device access, topology/LAN, operator window, backup/restore and disruptive-action scope, one immutable candidate digest |
| **O-6** | **Final version / `main` / tag / artifact release** | reserved to the owner | separate, later authorisation |

**Explicitly *not* owner-only** (I retract the over-restrictions): a **first genuinely
new-domain/family assessment**; routine **container image pulls** for disposable
environments; **public advisory queries** against public OSV/npm databases (the
dependency inventory is already public); the **CR-01 response-policy choice**
(coordinator contract decision); and all CR-08/09/10 lane work.

### 6.3 Not resolved here, and not mine to resolve

The one complete hashed final plan and staffing allocation, and the three explicit R3
decisions on that same hash, remain **future** and belong to the coordinator and the
three R3 participants. This report is one R2 contribution of three. It grants no
lease, no qualification, no acceptance and no release.

---

## 7. Acceptance evidence, report precision and the scope of this report

- **No current implementation lease and no source/feature acceptance** is granted by
  this report.
- **All CR-01…CR-14, the 30 packages and the 65 units are retained.** API034's bounded
  source review and its report-quality evaluation stay **complete**, with M-1 still
  held. The retained **WS040** work stays distinct from the new CR-01 component. The
  privacy terminal Opus/M3 **FAILs** and the lost original bytes stay lost. The
  **shared-tool composition** (CR-04 → CR-05) stays **serial and before** any frozen
  canonical proof. **No REST route is added or changed** by the recommended packages,
  so the 100 % REST route pipeline is **unaffected in planning**; `docs/validation/features.yaml`,
  `tests/sim/test_sim_rest_reads.py` and `python -m tools.validate ledger` are
  **not** touched by this report, and ledger generation is **not** run concurrently
  with registry checks.
- **This is not a source hook, a canonical campaign, a ledger generation or a
  core-suite run.** The only execution is §8.
- **Evidence precision.** A digest match proves identity, not comprehension; my §0.3
  inventory names what I read semantically and what I did not. Shared-temp inventory
  changes are **not** proof of who wrote anything; unavailable originals (for example
  the WS-WORK-01 author's `02-judge-probe-copy-corrected` exit `4294967295`, and the
  M3 privacy originals) remain unavailable and are **not** reconstructed.
- **The R1 prose checks ran on historical checkouts.** They are prose/documentation
  checks. They are **not** current-product verification, **not** source
  qualification, and **not** proof that a NEW Markdown file parses; some documentation
  tests import local product code from the checkout that ran them.

---

## 8. The scoped prose check — run **once**, and what it is not

*(Protocol, fixed before the run; the measured outcome is recorded in the owned
completion receipt because a report cannot contain its own post-run results. The
bytes checked below are the bytes committed.)*

**Purpose:** show that this new Markdown file and the five existing documentation
modules run cleanly **in my own historical checkout**. It is explicitly **not**
product-baseline verification, **not** source qualification, **not** a route-coverage
pass, **not** an evidence admission and **not** a product test.

**Command (exactly the five named modules, with the two plugins the repository's
documentation-check convention disables):**

```
C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -B -m pytest \
  tests/test_core_documentation.py tests/test_client_guides_docs.py \
  tests/test_openapi_and_config_docs.py tests/test_security_docs.py \
  tests/test_license_and_protocol_docs.py -q \
  -p no:tests.route_inventory -p no:cacheprovider \
  --basetemp=<owned>/pytest-tmp --junitxml=<owned>/junit.xml
```

Working directory: **my own historical checkout**
`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-remediation-recovery-r1-minimax`.
Interpreter: the root virtual environment's `python.exe`.

**Isolation:** the child inherits the Windows environment and then gets a **fresh**
overlay: `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`, `HIDDEN_TEMP`,
`--basetemp` and `--junitxml` all under a new owned root
`C:/t/remediation-functional/minimax-r2/prose/`; `PYTEST_ADDOPTS`, `PYTEST_PLUGINS`
and `PYTHONPATH` are dropped; `PYTHONDONTWRITEBYTECODE=1`; `PYTHONNOUSERSITE=1`;
bytecode additionally disabled by the explicit `-B`.

**Import-origin measurement:** a **separate post-run** child process (not part of the
single pytest run) reports `__file__` for `tests.conftest`, `tools.validate`,
`tools.validate.evidence`, `tools.validate.runner`, `tools.validate.model`,
`tools.validate.clients.api`, `tools.validate.clients.ha` and `hub`. It is labelled
a **separate post-run probe**, not part of the run.

**Runs: one.** No retry, no softened assertion, no skipped test counted as a pass, no
unchanged failed check re-run, no bypass, no ledger generation, no source hook, no
canonical campaign. All artefacts stay inside the owned roots; the ordinary and
hidden pre-run inventory of the owned roots (and a read-only inventory of the
inherited system `TEMP`/`TMP`) is retained before and after.

**Recorded outcome:** argv, cwd, the inherited-Windows-environment declaration and the
fresh overlay, UTC start/end, direct exit code, full stdout and stderr, JUnit counts
and SHA-256, skip list, all failures, the ordinary/hidden original inventories and the
separate import-origin probe are in the owned completion receipt
`C:/t/remediation-functional/minimax-r2/prose/RECEIPT.json` (plus the raw
`stdout.txt`, `stderr.txt`, `junit.xml`, `argv.json` and `env.json` beside it).

---

## 9. Scope

Prose and reasoning only. This report **qualifies no route**, **authorises no
launch**, **expands no attempt budget**, **closes no finding**, **admits no
evidence**, **changes no source**, **grants no lease** and **approves no release**.
The D6 provenance hold, the privacy holds, the failed qualification history and the
lost original bytes are untouched; I neither widened nor narrowed them. Tron/visual
approval, physical HIL, the 72-hour soak, the field week and the final
version/artifact release remain owner gates that software work does not touch. The
coordinator owns the ledger, the registry, the manifests, the locks, the contracts,
the integration, the preservation, the publication and the settlement of this worker.
