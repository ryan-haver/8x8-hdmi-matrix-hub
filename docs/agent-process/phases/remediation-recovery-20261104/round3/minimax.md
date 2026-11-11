# Remediation recovery 2026-11-04 — R3 final decision (MiniMax)

**Verdict: ACCEPT** — of the complete `FINAL_PACKET.json`, canonical LF SHA-256
`f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e`, version 1,
at `docs/agent-process/phases/remediation-recovery-20261104/FINAL_PACKET.json`,
blob `55f001df27fdf7027a5e8de0e81ae97cb5305808`, tree of
`wp-runtime-completion` at `daf7916744dc4aad5df2fa9442bcee3b8e82a97b`.

This is the third genuine decision round: three independent R1 assessments and
three all-peer R2 challenges were already preserved before this report. It is
**not** source implementation, model qualification, a retake, source acceptance,
a launch authorisation, or a release. It grants no route competence and expands
no assessment budget. My acceptance is one of three required same-hash
acceptances; it becomes nothing on its own, and adoption still requires the
other two families to accept this exact hash.

## 1. Entry bindings, pins and verified digests

| Item | Value |
| --- | --- |
| Contributor | MiniMax family, OpenCode 2 route, `minimax-coding-plan/MiniMax-M3`, thinking inherited, CLI effort override unsupported |
| Task / Dispatch / terminal | `task_dfe340b7113e` / `ctx_500618559004` / `term_fcc8b5d8-1708-4a8b-aa0b-f7c9b4d79ccb` |
| Coordinator handle | `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| Checkout | Reused settled tree `wp-remediation-recovery-r1-minimax`, branch `planning/remediation-recovery-r1-minimax` |
| My HEAD at entry / parent | `6671c92789d0de0590609590aeebc73772c00069` (exactly my own R2 head) / `9ed4b0c294ba3db06dc56f886e59ff2e99b3f601` |
| Working tree at entry | clean (`git status --porcelain` empty); no reset, checkout, cherry-pick or source import |
| Integration pin | `wp-runtime-completion` resolved **once** at entry → `daf7916744dc4aad5df2fa9442bcee3b8e82a97b`; never re-resolved, never followed as a moving ref |
| Tracked write | this file only: `docs/agent-process/phases/remediation-recovery-20261104/round3/minimax.md` |
| Owned scratch | `build/remediation-recovery-20261104/minimax-r3/**` (ignored) and `C:/t/remediation-recovery/minimax-r3/**` |
| Helpers / subagents / nesting | none; no plugin/MCP routing; no other models; no source edits, probes or persistent tooling |

### 1.1 Packet digests recomputed by me (canonical LF)

| Input | Expected in packet | Mine | Match |
| --- | --- | --- | --- |
| `FINAL_PACKET.json` (`f8fe93c8…`) | `f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e` | same, 50 426 bytes, 0 CR | yes |
| `INPUT_PACKET.json` (`original_input_sha256`) | `40526f127575feead63c94058250a868e0452ccb19b5552f60be66b6b82b77dc` | same, 10 876 bytes | yes |
| `ROUND2_PACKET.json` (`R2_packet_sha256`) | `25aeccfe87568ccba0e424e8bc7b21f85854fac6410a472c710af05b30ae63f7` | same, 9 269 bytes | yes |
| Accepted program packet (`accepted_program_packet_sha256`) | `52ed758e711891ee57be0bbadb87c688333049733e697a52829cf0ba87d7b15e` | same — `docs/agent-process/phases/execution-pinning-20261101/FINAL_PACKET.json`, blob `ba3c31025e312cc0d6b73e7d6726c47ffc066c11` | yes |

Every provenance field in the packet that names a digest therefore resolves to a
real object in this repository. Nothing in the packet was edited or reinterpreted
by me.

### 1.2 The three R2 reports, read completely at the exact commits

Fetched with `git cat-file` at the exact commits named in the packet; canonical
LF SHA-256 recomputed by me; every file read in full.

| Family | Commit | Parent | LF SHA-256 | Match |
| --- | --- | --- | --- | --- |
| OpenAI | `949d12cae8e1fe1db7bc8ccf57dc498ba72e1ac8` | `480a27bd3e65ff657ef878abf11242be0360f735` | `ff24c5c725ab8f0411089ddbc9fe83f03bddc032aab56bd0a2521ccd33e3e58c` | yes |
| MiniMax (mine) | `6671c92789d0de0590609590aeebc73772c00069` | `9ed4b0c294ba3db06dc56f886e59ff2e99b3f601` | `563e7d8672723c8890ce54c8886edc88f55aceafbbe0fd8d13b91679848b970e` | yes |
| Anthropic | `4b3605fdd35b5e536a73026209b5ef2ae008212e` | `3e7a83a191923ff393a14a2e93801e58fa8977a3` | `0c8fb2b6dae659bd78716637af4a8cc0044d36e215644531160b7c9d414816e8` | yes |

All three commits exist in this repository with the claimed parents. I read the
OpenAI report (434 lines), the Anthropic report (425 lines) and my own MiniMax
report (945 lines) end to end. I did **not** open any peer R3 report. I observed
incidentally, from a branch listing, that the Anthropic branch tip carries the
subject "record Anthropic R3 same-packet decision"; I did not read that file
and it forms no part of this decision.

### 1.3 What I actually read this round, and how

Reads are of pinned objects; a digest match proves identity, not comprehension.

| Read | Pin | Mode |
| --- | --- | --- |
| `FINAL_PACKET.json` | `daf79167` | full file, read as source (423 lines) |
| `FINAL_PLAN.md` (derived reading aid) | `daf79167` | full file; checked for drift against the JSON — it defers to the same hash and does not contradict the packet |
| `AGENTS.md` | `daf79167` | full file; digest `f09377ad…`, unchanged from the R2 pin |
| `docs/ORCHESTRATION_PROTOCOL.md` | `daf79167` | targeted ranges (capacity/quota 168–217, independent review 259–290) plus keyword sweep; digest `714fd177…`, unchanged from the R2 pin |
| `docs/agent-process/PROTOCOL.md` | `daf79167` | digest `4aeb2351…`, unchanged from the R2 pin; reviewed for the covered-correction and attempt-budget rules |
| `docs/agent-process/REPO_CONFIG.json` | `daf79167` | full file (`f09377ad`/`67dd58d9` class records read); route/scope/hook/path rules |
| `docs/production/remediation-20261104/WS_WORK_TASK.md` | `daf79167` | full file (5 818 bytes, `5cee3eb8…`) |
| `src/rest_api/ws_request_work.py` | `15c069bd` | **full file** (412 lines, `3bc116d8…`), read as source |
| `tools/validate/evidence.py` | `2d02004d` | **full file** (133 lines, `688cbb5e…`), read as source |
| `tools/validate/clients/ha.py` | `2d02004d` | targeted ranges (`_http`, `perform`, credential constants), `bf5f2b61…` |
| `docs/planning/software-waves/EXECUTION_PINS.json` | `daf79167` | hash and keyword sweep only (`e68f1ff2…`) |
| `docs/agent-process/phases/execution-pinning-20261101/CONSENSUS.json` | `daf79167` | keyword sweep for the program-packet binding; full file not re-read |

**Limits, stated plainly.** I did not read the WS **test** bodies, the C1–C3
privacy test bodies, the judge review's gap-probe scripts, any candidate native
transcript, `src/rest_api/websocket.py`, `src/rest_api/app.py`,
`src/hub/runtime/composition.py`, the HA product `config_flow.py` schema beyond
`const.py`, `AGENT_ALLOCATION.md` beyond its hash, or any private/root runtime
data. I executed **no** product probe, no project test and no product code in
this round; the only execution is the scoped documentation-module run in §8.
The WS and privacy **defects**, their severities and the "no owner-secret
incident" calibration remain the two completed reviews'. Where I re-derived a
mechanism below I say so and cite the source line; where I did not, I attribute.

## 2. Verdict

**ACCEPT** of the exact full hash
`f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e`.

I accept the plan **and** the staffing, qualification gates, exclusive leases,
attempt budgets, correction reserves and explicitly held gates **as a whole**.
There is no unresolved material blocker in the packet. The held gates are
held on purpose, and are held in the right places.

This acceptance does not become adoption. The packet's `adoption` rule requires
each of the three actual independent model-family participants to accept the
same canonical hash; the coordinator is not a participant, and majority,
coordinator synthesis, a timer or one family's agreement is not consent. Any
material revision produces a new version and hash, and requires fresh
same-packet decisions from all three.

## 3. Disposition of each decision

### D1 — product correction versus immutable failed authorship and owner-only retake

**Accepted.** The packet keeps the original first-authorship
FAIL/PASS/FAIL/PASS/PASS-bounded/HOLD record and WSR03 unchanged, grants no
retrospective PASS, no new all-six judgement, no broad author grant and no
existing-handler lease, and spends exactly one initial correction delivery plus
one component-only review plus one explicitly budgeted material product-fix
re-review. That is the same unbundling OpenAI R2 reached when it revised its
own earlier owner gate, and the same separation Anthropic R2 §2.1 drew. The
controlling rules are present and verified: `WS_WORK_TASK.md` states "No
automatic rewrite/retry or implied PASS" and "Any material fail/unknown holds
bounded authorship and component acceptance", while `ORCHESTRATION_PROTOCOL.md`
lines 278–280 state "Reviewers **report; authors fix**. Re-review material
fixes and material integration/conflict-resolution changes at their final
commits." A bounded product correction plus an exact-commit component review is
that mechanism, not a disguised exam retake. The limit that forbids smuggling
an exam into the reserve is written into `D1.limits` and into the WS-C01
reserve verbatim ("No competence assessment or further automatic source
rounds"). The exhausted Opus privacy attempt budget and the owner-only retake
precedent are untouched: `owner_questions` states that a budget expansion
"remains owner-only if ever chosen later; not requested or authorized here".

### D2 — two-field semantics and bounded conservative cleanup

**Accepted.** `requested` counts attached live tasks for which this cleanup
actually requested cancellation; `remaining` counts all unfinished admitted
work at return, including outstanding reservations and the caller itself when
applicable; `remaining` may exceed `requested`; `drained` iff
`remaining == 0`. This is the documented component-local semantic correction
my own R2 §4.1 argued for, combined with the caller-as-live rule Anthropic R2
raised and I accepted against my R1. The packet records the change honestly
("This prospectively changes old remaining='of those' wording instead of
pretending it was unchanged") and keeps the interface at two fields, which is
the smaller contract change on a `frozen=True, slots=True` dataclass for a
component that nothing imports yet — I verified `src/rest_api/ws_request_work.py`
is **absent** at the packet's own `integration_baseline` `12ad507e`, and the
module docstring says "Nothing imports it yet".

The limits are the ones I would insist on: conservative immediate non-drained
return when reentrant reservations or self-dependence prevent useful waiting;
otherwise one monotonic bounded wait and a final unfinished-work recount; never
await own settlement; never hide resistant work; never double-count
reserve/attach transitions; no notification state machine; no detached watchers
or unbounded queues.

I verified the source facts that make this contract necessary. In
`ws_request_work.py` at `15c069bd`, `aclose` (241–249) and `shutdown`
(407–412) snapshot `self._tasks` **before** calling `close()`/`begin_shutdown()`,
so in the factory-cleaner and eager-first-step shapes the newly admitted task
is not in the snapshot and the report can be `drained=True` while that task is
alive. The post-registration cancel at 376–379 covers the *cancellation*, as my
R2 said; the defect is the *report*. The packet's contract fixes the report.

### D3 — bound-loop lifecycle checks before mutation, and the unbound-close fence

**Accepted, and my own R2 wording is withdrawn.** I re-read
`ws_request_work.py` at `15c069bd` and confirm `_check_loop` is called **only**
from `_admit` (line 339), while `close` (235–239), `aclose` (241–249),
`begin_shutdown` (401–405) and `shutdown` (407–412) never check the loop, so
today they can mutate foreign-loop state and cancel foreign-loop tasks. The
packet's rule — check the bound loop before mutation; lifecycle never binds a
previously unbound controller; an unbound synchronous `close`/`begin_shutdown`
may run without a running loop but **must** close the relevant admission fence
and must not bind; a bound controller raises on wrong-loop or no-running-loop
use before any state or `cancelling()` count changes — is the correct
enforcement.

My R2 §3.5 rule 2 called the unbound close "a no-op that must not bind the
loop", and rule 3 said an unbound lifecycle call "does nothing". That was
wrong: `WorkOwner.close()` sets `_closed = True` and `WsRequestWork.begin_shutdown()`
sets `_closing = True`; both are admission fences, and WS-WORK-01 acceptance
item 1 requires "Reject admission after owner/application shutdown begins".
The packet explicitly rejects my wording and is right to. The preserved bounds
— timeout validation before mutation, repeated-cancellation behaviour, owner
locality, exception retrieval, and every original factory/admission bound —
are all retained.

### D4 — C4-first with an explicitly held review gate, versus OpenAI's prior order

**Accepted.** The packet chooses the original-author privacy correction first
in a dedicated isolated tree with an **explicitly HELD** qualified
privacy-review/acceptance gate, then the genuinely new-family assessment on the
exact corrected tip. That is my R2 §3.6.2 order and Anthropic R2 §2.5's
subject, and it is recorded as a decision OpenAI must make explicitly in R3,
with OpenAI's preference (assess the uncorrected tip) stated and not chosen. I
accept that disposition: OpenAI's order is defensible for judging the original
defect set, but the corrected tip yields a materially useful assessment rather
than credit for repeating public old findings, and the correction is an
ordinary author fix that needs no qualified reviewer to begin.

The limits are the load-bearing part and they are correct: C4 source stays
unaccepted and unintegrated; no canonical privacy or security evidence is
admitted until qualification PASS, a separate actual full-chain review and the
applicable combined checks; route and headroom are reserved explicitly for
candidate, judge, actual review and corrections, but a conditional future M3 is
**not** called a qualified review fallback; and if the author route is
unavailable the package is **held** rather than handed to Astra, which would
compromise Astra's judge role. That last limit matches Anthropic R2 §3
("Prefer holding C4 over using Astra") and my R2 §3.6.7.

### D5 — M3's first useful corrected-chain privacy assessment, with no novel-bug quota

**Accepted, with my conflict of interest disclosed in full.**

The packet selects `minimax-coding-plan/MiniMax-M3` (thinking inherited, CLI
override unsupported) as **one** privacy-review-domain candidate after C4, with
one fresh `gpt-6-astra` judge. I must state plainly that my own R2 §3.6.3
**declined to propose my own family** for this role and recorded a conflict of
interest: the structural need for a third family is real, but the *selection*
must not be settled by interest. The packet selects my family anyway, on the
stated grounds that "Actual M3 native identity and adequate dated route
observations exist; planning/prose work is a weak task-fit prior, NOT
qualification". I accept that reasoning as written, because the plan does not
treat my family's planning record as competence:

- the six privacy axes are frozen in the packet before C4 implementation and
  the source hash/path delta is bound in the dispatch artifact before the
  candidate starts;
- the candidate must independently enumerate carriers, sinks, callers and
  assertions and design its own positive and negative controls;
- public findings are "attributed inputs, not proof", and "copying/replaying
  supplied conclusions alone cannot qualify";
- there is **no** novel-bug quota and no requirement to judge counterexamples
  only by unpublished findings;
- a FAIL or unknown is terminal for that attempt — "no rewrite/retry/replacement
  judge or automatic family substitution";
- a PASS earns only the actually demonstrated diagnostic-review scope, and a
  separate actual `RV-PRIVACY-CHAIN` review is still mandatory.

I disclose the residual structural overlap rather than hide it: the M3
candidate's family also produced public privacy *designs* in R1/R2 (mine among
them), so the assessment cannot be blind. The packet's attribution and
independent-reasoning rules, plus an independent different-family judge, are
the correct response to that, not a redesign of the slot. The independent judge
is Astra; the source author is Sol; MiniMax is neither, so
`ORCHESTRATION_PROTOCOL.md` lines 261–267 (Sol/Astra/Luna one family; M3 and
M3.1 one family) is satisfied. My acceptance of this allocation is one of
three family votes and is not the deciding voice for my own family.

I also record a narrowing of my own R2 rule and accept it: my R2 §3.6.5 said
the counterexamples axis would be "scored on findings that were not already
published". The packet drops that scoring and keeps the anti-replay purpose
through the attribution, independent-reasoning and independently-chosen-controls
clauses instead. That is the sounder construction, because it does not penalise
a candidate for a genuinely clean corrected chain.

### D6 — a distinct FIRST existing-lifecycle REVIEW candidate, with provenance and conflict gating before dispatch

**Accepted, and my own R2 inference is withdrawn.** My R2 §3.2 and §7.1 argued
that the wiring gates are "the accepted component, a leased implementation owner
and a qualified different-family reviewer" and **not** authorship competence,
because `WS_WORK_TASK.md` says a pass would qualify "only this component-level
asyncio WS-work authorship, not … existing handler wiring". I now read the
lease sentence of the same file against that reading:

> "This is specifically not a shared existing-API lease before authorship
> competence is demonstrated."

Both peers (OpenAI R2's four-outcome table; Anthropic R2 §2.2 route table) read
that as a live pre-competence gate on the existing API. The plain text plus two
independent readings against mine is the better-supported position, and the
packet therefore rejects my inference. I accept that rejection.

Critically, the packet resolves it **without** an owner retake and **without**
granting a lease: D6 grants no immediate CR-01 wiring lease. Instead it
prepares a distinct **FIRST** review-role assessment — not the failed
component-AUTHORSHIP assessment, not the exhausted privacy review — of original
non-Anthropic existing WS/app/runtime lifecycle source, excluding every
authored controller and correction path, judged by Astra. That is Anthropic
R2's route A, and it honours my R2's substantive point that a failed
authorship attempt should not be laundered and that a retake would be a
wasteful ritual.

The gates are the right ones and are stated in the right order: prove before
dispatch that the actual target source is not Anthropic-authored; freeze the six
`async_review_assessment` standards; a conflict-boundary that excludes the
candidate's own controller and corrections; PASS earns only the exact
demonstrated existing-lifecycle **review** competence, not authorship, privacy,
browser/kiosk or product-security competence; after any PASS the Sol-authored
wiring still needs its own exact-commit independent review; any change to the
Anthropic controller returns to its author plus Astra and never to Opus
self-review; and if provenance, independence or genuinely new scope cannot be
proved, the candidate **and** the wiring are held while other packages
continue. "No owner retake is requested/authorized" is stated explicitly, and
`owner_questions` confirms none is needed.

**One concrete provenance caveat I must name.** The provenance gate cannot be
discharged from Git authorship metadata in this repository: every file in
`src/rest_api/` is committed under the single committer "Ryan Haver", so
`git log` cannot distinguish an Anthropic-authored file from an OpenAI-authored
one. The gate must therefore be discharged from the *recorded attribution* —
`WS_WORK_TASK.md` ("Existing OpenAI code remains attributed and unmodified";
its ONLY tracked writable was the three NEW files), the peer reports and the
allocation ledger. I verified corroboration, not proof:
`src/rest_api/ws_request_work.py` is **absent** at the packet's
`integration_baseline` `12ad507e`, and `src/rest_api/websocket.py` and
`src/rest_api/app.py` have no commits after October 2026. That is consistent
with non-Anthropic authorship; it is not the attribution record itself. The
packet already anticipates this ("Before dispatch prove exact target source is
not Anthropic-authored"); I am naming the correct *source of proof* so the gate
is not mistakenly discharged by `git log`.

### D7 — public-value, sensitive-Hub and error-context preservation

**Accepted, and two of my own R2 prescriptions are withdrawn.**

The packet places the `ha.py` diagnostic/error sinks inside C4 under an
**explicit serial lease**, excludes the product HA `config_flow` source,
preserves the public shortcut/flag values through *proven display context*
rather than a global bare-key or bool/None exemption, keeps raw
transport/comparisons/`ActionResult` memory raw, permits context-aware
display-copy helpers and default-compatible diagnostic parameters inside the
leased functions, forbids new required API arguments or any external public-wire
contract change, and requires a coordinator lease amendment before touching
broader shared APIs or unrelated callers. That resolves the three-way
disagreement (Anthropic and OpenAI R2 wanted `ha.py` inside C4; my R1 wanted a
separate HA package) in the form my R2 §2.2 A15 already accepted ("separate
serial lease, same redaction domain"), and it matches OpenAI R2 exactly: "a
separate exact `ha.py` diagnostic lease is required; it does not authorize
editing product `config_flow.py` for CR-02".

Two corrections to my own R2, both of which I accept:

1. **My prescribed remedy `redact(text)[:300]` was not a safety remedy.** I
   re-read `tools/validate/evidence.py` at `2d02004d`: `redact()` handles
   `dict` and `list` structurally, and for a plain `str` it applies only
   `_SECRET_QUERY` — a `?key=`/`&token=`-style query pattern (lines 115–133).
   A bare credential in an opaque error body is therefore unmasked by
   `redact(text)`. The concrete sink is `tools/validate/clients/ha.py:273`,
   `raise RuntimeError(f"{method} {path}: HTTP {resp.status} {text[:300]}")`,
   where truncation happens before any masking, and `ha.py:267` truncates at
   `text[:500]`. The packet's rejection of "literal `redact(text)[:300]` as
   blanket remedy" is correct; my R2 §3.4.4 prescription is withdrawn.
2. **My blanket "never redact `Hub.equals` by name" is superseded.** My R2
   §3.4.3 Trap 2 argued that adding `redact()` to `Hub.equals` would corrupt
   the public `data.shortcuts[0].key` value asserted by the shortcut-alias
   contract. The packet instead requires that "Hub path/query and sensitive
   equals both need safe display copies" and "reject a blanket never-redact-Hub.equals
   exemption", while preserving the public value through *proven display
   context*. My underlying trap survives as a required control — the public
   shortcut value must still come through verbatim, and the created/unknown
   credential key must stay masked — but my blanket rule is replaced by a
   contextual one, which is the better construction because `Hub.equals` may
   carry a sensitive value in other contexts.

I verified the compatibility trap the packet encodes: `_SECRET_KEYS` is
`^(key|pin|pin_hash|authorization|cookie|x-admin-pin)$` with the whole group
anchored, so `X-Admin-PIN-Policy` is **not** matched today in any casing. Any
C4 credential rule must stay exact-name and case-insensitive so that public
header survives. The packet's "Exact credential headers must not swallow public
X-Admin-PIN-Policy in any casing" is therefore a required regression control,
not a preference.

### D8 — API034 stays complete; the broader gates stay open

**Accepted.** The packet keeps the API034 bounded source review and its
report-quality evaluation COMPLETE, keeps M-1 security freshness, broader
WS040 evidence and the combined holds open, and uses Astra for the secondary
quality evaluation of a future M3 privacy review rather than the original source
author Sol. I verified both completed records exist in this repository as
distinct trees at `12eeef938857bfd740854ccbaad34f9bc1b6ce36` and
`c3fcace6260e31d6c176f9feb6ab0dfd6ead849e`, and all three R2 reports agree
that the earlier stale `accepted_reviewer_artifact: null` pin fields must be
reconciled against the later execution record. The packet's correction of that
stale pin reading is right, and it is the disposition of my own R1 wording
("needs a qualified security review"), which my R2 §3.7 had already corrected.
Astra as the secondary evaluator matches Anthropic R2 §2.5's recommendation over
the pin's `reviewer_route: sol`, and matches my R2 P5.

### D9 — dispatch records are operational authority, not a new permission ritual

**Accepted.** Every future source dispatch needs a concrete coordinator record
of the exact full base, exclusive lexical paths/functions, a real Task and
Dispatch, prospective acceptance, role limitations, correction reserve and pool
observations — operational authority inside the adopted plan, not an extra owner
permission. Launch additionally requires all three genuine R3 participants to
accept this same complete packet hash, fresh preflight/environment/qualification
checks to pass, and the prior integration checkpoint to be pushed and exactly
verified. This is the unbundled form of OpenAI R2's "prepared owner choice" and
my R2 §8: covered corrections need no owner step, while an expansion of a spent
competence-attempt budget would.

### D10 — instruction-only maintenance of the stale Anthropic exclusion

**Accepted.** I confirmed the premise in the pinned
`docs/ORCHESTRATION_PROTOCOL.md`: line 177 still reads "No Anthropic/Claude or
opaque fallback is permitted." in the quota section, in the same file that
records the owner's 2026-11-01 supersession at lines 14–16 and that
`REPO_CONFIG.json` records as `excluded_underlying_families: []`. A stale
present-tense sentence inside a current file is a real internal inconsistency.
The limits are correct: documentation checks only, preserving immutable
historical instructions and records and the original accepted plan hashes; no
phase launch, no release, no visual baseline from instruction edits. This
matches `ORCHESTRATION_PROTOCOL.md` lines 286–288 ("Pure prose maintenance uses
applicable documentation checks and policy inspection; it does not establish
fresh runtime or model qualification").

## 4. Staffing, leases, budgets, reserves and held gates

**Staffing and family independence.** I checked every author/reviewer pairing
against `ORCHESTRATION_PROTOCOL.md` lines 261–267 (Sol, Astra, older Sol and
Luna are one OpenAI family; M3 and M3.1 are one MiniMax family; a different
harness or provider does not change the underlying family):

| Pair | Families | Independent? |
| --- | --- | --- |
| WS-C01 (Claude) → WS-R01 (Astra) | Anthropic → OpenAI | yes |
| PRIV-C4 (Sol) → future qualified reviewer (M3) → judge Astra | OpenAI → MiniMax, judged by OpenAI on a MiniMax report | yes |
| PRIV-ASSESS (M3) → PRIV-JUDGE (Astra) | MiniMax → OpenAI | yes |
| RV-PRIVACY-CHAIN (M3) → secondary evaluation Astra | MiniMax reviews OpenAI source; Astra evaluates the report | yes |
| ASYNC-REVIEW-ASSESS (Anthropic) → judge Astra | Anthropic → OpenAI | yes |
| WS-WIRING (Sol) → Anthropic, after earned conflict-free review competence | OpenAI → Anthropic | yes |

No pair is same-family, and no slot is filled by an unverified family. The
packet's own discipline is explicit in every row: the judge "is not source
author"; the report-quality evaluator "cannot replace different-family actual
source review"; and "Planning never grants source competence or automatic retry
budgets".

**Attempt budgets.** Privacy: exactly one candidate and one judge, FAIL/HOLD
terminal for that attempt, no rewrite, retry, replacement judge or automatic
family substitution, and the exhausted Opus attempt budget preserved with its
`e8ce3966` FAIL intact. Async review: exactly one first review-role candidate
plus one fresh Astra judge, with no reopening of the prior authorship or privacy
failures. WS: one correction delivery plus one component-only review plus one
explicitly budgeted material fix/re-review, with no competence assessment and
no further automatic source rounds. No exhausted budget is expanded anywhere in
the packet, and no budget expansion is requested of the owner.

**Correction reserves.** Each product package carries one author fix and one
independent exact-commit re-review, re-gated; the reserved session is stated
explicitly per task rather than implied, and the privacy reserve is explicitly
conditional ("reserved conditionally and re-gated"), matching the pin's
`correction_reserve`.

**Explicitly held gates.** Wiring is held until an accepted component, an
earned conflict-free lifecycle reviewer, a qualified Sol author match and an
explicit coordinator API lease — with "No immediate lease from this plan".
Privacy acceptance and admission are held until genuine qualification, a
separate actual full-chain review and acceptance/admission. API034 M-1
freshness, WS040 broader browser/client/effect coverage, HA/UI qualified pairs
and environments, and the combined proof/build/version gates stay open. Every
owner gate — Tron/visual approval, physical HIL, the 72-hour soak, the field
week and final version/artifact release — stays open and separate, and software
passes do not approve any of them.

**Sequencing and writer exclusivity.** Wave A pairs WS-C01 with PRIV-C4 on
disjoint paths (`src/rest_api/ws_request_work.py` plus its test and a new
correction report, versus `tools/validate/*` plus a new C4 test module and a new
C4 report) — no path overlap. Wave B pairs WS-R01 with PRIV-ASSESS; both write
new files in different directories. Privacy/model/runner/registry integration
and the ledger/registry sequence stay coordinator-only and serial, which
matches `AGENTS.md` ("Do not run ledger generation concurrently with registry
checks") and `ORCHESTRATION_PROTOCOL.md` line 232 ("Parallel tasks must not
overlap writers").

**Capacity.** The packet's ceiling — two current workers plus coordinator plus
protected external = 4 — is at or below the standing ceiling in
`ORCHESTRATION_PROTOCOL.md` line 99 ("coordinator plus at most three workers,
reviewers included"), so it is stricter, not looser. The fallback statement is
honest: no qualified privacy or whole-wiring fallback exists today; Google
route/headroom/domain are unknown or unavailable and discovery does not
authorise login or spend; DeepSeek is excluded; there is no automatic model or
family substitution and no capacity-based qualification retry. Unknown, stale
or below-30% capacity holds **only the affected dispatch**, with a verified
fallback required first, and fresh headroom and a qualification gate before
each creation/start with checkpoints at least every 15 minutes. That is exactly
the repository's standing capacity rule and it correctly treats capacity as a
routing constraint rather than a project-wide stop.

## 5. My own prior dissent, preserved and dispositioned

My R2 report is preserved unchanged at
`6671c92789d0de0590609590aeebc73772c00069`. Its dissent is not softened here;
each position is either carried forward, corrected by evidence, or withdrawn.

| My R2 position | Disposition |
| --- | --- |
| At-most-one pending reservation; `_admit` "is `async def`" | **Withdrawn as factually wrong.** `_admit` at `15c069bd` is a synchronous `def` (line 337), and nested re-entrant admissions can hold `controller._reserved` above 1. The packet's rejection of this claim is correct and D2's "outstanding reservations" plural plus the explicit no-double-counting limit carry the corrected behaviour. This correction matters to the implementation, not just the prose. |
| The "admission settled" future is "structurally deadlocked" | **Reason withdrawn, outcome retained.** Because `_admit` is synchronous, an eagerly started drain that suspends lets registration proceed and the reservation release — so my deadlock proof was wrong. The packet rejects the notification mechanism for complexity and proof burden (and for requiring a notification state machine), which is the sounder ground. The conservative path and its contract stand. |
| Unbound `close`/`begin_shutdown` is "a no-op" | **Withdrawn.** Both close real admission fences; D3 corrects it. |
| `redact(text)[:300]` is the required form at `ha.py:_http` | **Withdrawn.** `redact()` on a string applies only the query regex; D7's rejection of the literal call as proof is correct. |
| Never redact `Hub.equals` by name | **Superseded** by D7's contextual display-copy rule; my public-fidelity trap survives as a required control. |
| Counterexamples axis scored on unpublished findings | **Narrowed** by D5, accepted; the anti-replay purpose is retained by other clauses. |
| Wiring is not gated on author competence (§7.1) | **Withdrawn.** The task's "not a shared existing-API lease before authorship competence is demonstrated" is a live gate; D6 rejects the inference and resolves it without any retake. |
| MiniMax should not be proposed as the privacy candidate (§3.6.3) | **Overruled by the coordinator's allocation**; accepted under D5 with my conflict disclosed. |
| Two-field `DrainReport`; conservative non-drained return | **Carried into D2 unchanged.** |
| Corrected-tip privacy assessment order (§3.6.2) | **Carried into D4 unchanged.** |
| `ha.py` as a separate serial lease in the same redaction domain | **Carried into D7 unchanged.** |
| API034 source review and evaluation complete; M-1 held (§3.7) | **Carried into D8 unchanged.** |
| No owner decision required; only a spent-budget expansion would be (§8) | **Carried into D1/D9/D5 unchanged.** |
| Instruction-only maintenance of the stale Anthropic exclusion (§3.8) | **Carried into D10 unchanged.** |

## 6. Named material errors and unknowns — honestly

1. **My own R2 factual error on `_admit`** (see §5). Corrected here and in the
   packet. It does not change the D2 contract, but the author and reviewer must
   handle `reserved > 1` and must not double-count the reserve→attach
   transition.
2. **My own R2 factual error on `redact(text)`** (see §5 and D7). The literal
   call is not a safety proof; the packet carries the corrected requirement.
3. **My own R2 over-strong reasoning on the notification future** (see §5).
4. **My own R2 over-strong reading of the wiring lease** (see §5, D6).
5. **Provenance must not be discharged from Git metadata.** Every
   `src/rest_api/` commit in this repository shares one committer identity, so
   `git log` cannot establish which family authored a file. The D6 provenance
   gate and the WS-WIRING "qualified Sol author match" must be discharged from
   the recorded attribution (WS task, peer reports, allocation ledger).
   Corroboration obtained, proof not obtained — stated in D6.
6. **D5 is non-blind and that is disclosed, not eliminated.** The M3
   candidate's family produced public privacy designs in R1/R2. The packet's
   attribution rule, independent-reasoning rule, independent judge and terminal
   FAIL disposition are the mitigation; the candidate must disclose the
   overlap in its own report.
7. **Route availability is unverified at adoption time.** "Route/headroom must
   be revalidated" is stated per task, but I did not query quota or launch
   catalogues in this round, and the packet's capacity figures are dated
   observations. Unknown is not headroom; the per-dispatch gate governs.
8. **A failed integration push holds new worker launch.** The packet's
   `environment_and_preservation.publication` records that the MiniMax R2 task
   ref was held after two GitHub server errors. My dated observation today:
   `git ls-remote origin refs/heads/planning/remediation-recovery-r1-minimax`
   returns `6671c92789d0de0590609590aeebc73772c00069`, so that ref appears to
   be published now. That is my observation, not a publication claim; the
   coordinator must independently re-verify the branch and the integration
   head before any wave, because D9's launch condition requires the prior
   integration checkpoint to be pushed and exactly verified.
9. **Documentation consequence of adoption.** `docs/agent-process/REPO_CONFIG.json`
   currently records the MiniMax scope as "Bounded evidence inventories only".
   Adopting D5 expands that scope to a prospective privacy candidate. Updating
   that coordinator-owned record is part of post-adoption documentation
   maintenance, not a blocker and not something I may edit.
10. **Not independently recomputed.** I did not recompute the
    `integration_baseline` `12ad507e` and `source_unchanged_floor` `e2161484`
    tree digests against a full tree diff; I confirmed both commits exist with
    those SHAs and confirmed the absence of `src/rest_api/ws_request_work.py`
    at `12ad507e`. I did not re-verify `EXECUTION_PINS.json` field by field
    beyond the keyword sweep and the digest.

## 7. Conditions and notes carried into adoption

These are execution notes for the coordinator, not conditions on the plan and
not blockers:

- The D9 launch gate — three same-hash acceptances, fresh preflight and
  environment and qualification checks, and a pushed, exactly verified
  integration checkpoint — must be satisfied before wave A. My acceptance is
  one of the three and becomes nothing alone.
- `REPO_CONFIG.json`'s MiniMax scope line should be updated to match the
  adopted D5 allocation.
- `ORCHESTRATION_PROTOCOL.md` line 177 should be corrected under D10 as
  documentation-only maintenance, preserving the historical supersession text
  and the original accepted plan hashes.
- The stale `accepted_reviewer_artifact: null` pin fields for API034 should be
  reconciled against the later completed execution records, per D8.
- The D6 provenance gate should name the attribution records as the proof
  source, not Git authorship metadata.

## 8. Checks actually run

Run **once**, after this prose, in this checkout, using the root virtual
environment `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
this checkout as the working directory, explicit `-B`, a copied Windows OS
environment (`os.environ.copy()`), fresh owned data/config/TEMP/TMP/basetemp/
JUnit roots under `C:/t/remediation-recovery/minimax-r3/`, and the
route-inventory and cache plugins disabled, exactly as
`REPO_CONFIG.json`'s `documentation_checks.command` specifies:

```
<root venv python> -B -m pytest \
  tests/test_core_documentation.py tests/test_client_guides_docs.py \
  tests/test_openapi_and_config_docs.py tests/test_security_docs.py \
  tests/test_license_and_protocol_docs.py -q \
  -p no:tests.route_inventory -p no:cacheprovider \
  --basetemp=<owned>/docs/pytest-tmp --junitxml=<owned>/docs/junit.xml
```

Measured import origins, the direct argv, the child exit code, the complete
stdout and stderr streams, the timings, the safe subset of the environment and
the original ordinary and hidden temp contents are retained under
`C:/t/remediation-recovery/minimax-r3/docs01/`. Results are recorded in
§8.1 below, which is the only part of this document written after that run and
is written to record the run, not to change any recommendation.

### 8.1 Actual result — from the single run

| Field | Value |
| --- | --- |
| Interpreter | root venv `python.exe`, Python **3.12.10**; pytest **9.1.1**; pytest-asyncio **1.4.0** |
| Direct child exit code | **0** |
| pytest summary | **489 passed** in 3.07 s — 0 failed, 0 errors, 0 skipped, 0 xfailed, 0 deselected |
| stdout | 580 bytes, complete (seven progress lines plus the summary line) |
| stderr | **empty** (0 bytes) |
| Wall clock | 3.605 s, `2026-11-04T10:30:00Z` → `2026-11-04T10:30:04Z` |
| JUnit | 63 691 bytes; `tests="489" failures="0" errors="0" skipped="0"`; suite time 3.046 s; timestamp `2026-11-04T03:30:01.053497-07:00` |
| Runs | **one**. No retry, no softened assertion, no skipped test counted as a pass, no unchanged failed test re-run |
| Import-origin probe | separate child, exit **0**, stderr 0 bytes, 0.413 s |
| Measured import origins | `tests.conftest`, `tools.validate`, `tools.validate.evidence`, `tools.validate.runner`, `tools.validate.model`, `tools.validate.clients.api`, `tools.validate.clients.ha` **and `hub`** all resolve to **this checkout** (`…/wp-remediation-recovery-r1-minimax/…`) |
| Isolation | `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`, `HIDDEN_TEMP`, `--basetemp` and `--junitxml` all under `C:/t/remediation-recovery/minimax-r3/docs01/`; copied OS environment via `os.environ.copy()`; bytecode disabled by explicit `-B` and `PYTHONDONTWRITEBYTECODE=1`; route-inventory and cache providers disabled by `-p no:tests.route_inventory -p no:cacheprovider` |
| Original temp contents retained | `original_temp_contents.json` — ordinary temp **3 465** entries, hidden temp (`<root>/.agent`) **8** entries, captured before the run; owned data 0 entries, owned config 0 entries; 987 basetemp entries created by the run inside the owned root |
| Errors preserved | none: both children exited 0 with empty stderr |
| Receipts | `C:/t/remediation-recovery/minimax-r3/docs01/` — `argv.json`, `result.json`, `exit_code.txt`, `stdout.txt`, `stderr.txt`, `junit.xml`, `import_origins_stdout.txt`, `import_origins_stderr.txt`, `original_temp_contents.json`; runner script `C:/t/remediation-recovery/minimax-r3/scripts/run_docs01.py` |

This is scoped documentation maintenance for one prose file. It is **not** a
source-hook pass, **not** a full-suite result, **not** a runtime, model or
qualification pass, and it claims no route-coverage or evidence admission.

### 8.2 Commit

Scoped documentation commit of this single new file, made with the authorised
**invocation-only empty `core.hooksPath`** exception (`git -c core.hooksPath=…`
against an empty owned directory). The exception is used because the configured
repository `pre-commit` hook runs broad Ruff lint plus the fast unit-test
suite, which is out of scope for a prose-only change; **no source hook was
bypassed for any source change and no hook result is claimed**. Real checks on
the new file were performed first: strict UTF-8 decode without BOM, LF-only
line endings, no trailing whitespace, no tab characters, no markdown link
targets to resolve, and the file is the only change staged. The commit
contains only
`docs/agent-process/phases/remediation-recovery-20261104/round3/minimax.md`.
The commit message file is kept in my owned roots
(`C:/t/remediation-recovery/minimax-r3/`).

## 9. Scope of this report

- Prose and reasoning only. No product code, privacy reproduction, asyncio probe
  or project test was executed by me in this round. The only execution is the
  scoped documentation-module run in §8.
- The invariants and mechanisms in the packet are a correction **design**, not a
  validated patch. The eventual author must confirm feasibility; the eventual
  reviewer must confirm behaviour at the exact commit.
- The WS and privacy **defects**, their severities and the "no owner-secret
  incident" calibration remain the two completed reviews'. I re-derived only the
  specific mechanisms cited in §3, with line references, and I did not re-grade
  any completed review.
- This is a planning decision. It qualifies no route, authorises no launch,
  expands no attempt budget, and approves no release. Tron/visual approval,
  physical HIL, the 72-hour soak, the field week and final version/artifact
  release remain owner gates that software work does not touch.
- Coordinator owns ledger updates, preservation, release, publication and
  integration. I did not edit the packet, the ledger, the registry, manifests,
  locks or any other worktree, and I did not read any peer R3 report.
