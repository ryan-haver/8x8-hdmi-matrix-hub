# Remediation recovery R3: Anthropic same-packet decision

**Verdict: ACCEPT** `FINAL_PACKET.json` version 1, canonical LF SHA-256
`f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e`.

This accepts the plan and its staffing, qualification limits, leases, attempt
budgets, correction reserves and held gates. I found no unresolved material
blocker. This is one family's decision. It is not adoption, a launch, a
qualification or source acceptance. Adoption still needs the other two families
to accept this same hash. Section 4 records one factual finding against the D6
premise. The packet's own fail-closed gate already handles it, so it does not
block acceptance.

## 1. Bindings and read limits

| Item | Value |
| --- | --- |
| Participant | Anthropic `claude-opus-5-5`, native Claude Code, Task `task_79d0d9028045`, Dispatch `ctx_9d313bb15f8b`. Effort `high` is the dispatch assignment; I cannot observe per-turn effort. No helpers, subagents, plugins, MCP or other models |
| Checkout | Reused settled tree `wp-remediation-recovery-r1-anthropic`, branch `planning/remediation-recovery-r1-anthropic`, HEAD at entry `4b3605fdd35b5e536a73026209b5ef2ae008212e` (my R2 head), clean. No reset or import |
| Integration pin | `wp-runtime-completion` resolved once at entry: `f1ca6f932caec64e6567abf68b125164cda7ded3` (local equals `origin`). Every coordinator record below came from this SHA |
| Packet | `FINAL_PACKET.json` at the pin: 50,426 bytes, 0 CR, LF SHA-256 matches. Read in full |
| Coordinator status `msg_fb53d60ccd8f` | Operational only: the MiniMax R2 task ref was published after freeze (`6671c927` verified). The hash and the substance are unchanged. I treat the "held" wording in `/environment_and_preservation/publication` as dated history |

The three R2 reports were read in full. Each was extracted at the commit the
packet names and checked against its packet digest. The blob at the pin is
identical:

| Family | Commit / parent | LF SHA-256 | Lines |
| --- | --- | --- | --- |
| OpenAI | `949d12cae8e1fe1db7bc8ccf57dc498ba72e1ac8` / `480a27bd3e65ff657ef878abf11242be0360f735` | `ff24c5c725ab8f0411089ddbc9fe83f03bddc032aab56bd0a2521ccd33e3e58c` | 434 |
| MiniMax | `6671c92789d0de0590609590aeebc73772c00069` / `9ed4b0c294ba3db06dc56f886e59ff2e99b3f601` | `563e7d8672723c8890ce54c8886edc88f55aceafbbe0fd8d13b91679848b970e` | 945 |
| Anthropic (own) | `4b3605fdd35b5e536a73026209b5ef2ae008212e` / `3e7a83a191923ff393a14a2e93801e58fa8977a3` | `0c8fb2b6dae659bd78716637af4a8cc0044d36e215644531160b7c9d414816e8` | 425 |

Other reads at the pin: `AGENTS.md`, `ORCHESTRATION_PROTOCOL.md` (lines 10-22,
170-200 and 232-275, plus a grep), `agent-process/PROTOCOL.md` (lines 80-125)
and a `REPO_CONFIG.json` grep. All are byte-identical to my R2 base. I also read
`tasks/anthropic-r3.md` and the head of `ROUND3_PREFLIGHT.json`. Consequential
source checks were Git reads only, with no execution:

- `ws_request_work.py` at `15c069bd`: the function list and `_admit` (lines 337-380).
- `ls-tree` of `src/rest_api/` at `12ad507e`.
- `git log` trailers of `websocket.py` and `app.py` up to `12ad507e`.

**Limits.** I did not read `FINAL_PLAN.md`, because the packet is the sole
authority. I did not read any peer R3, any transcript, private data or quota
interface, and I did not re-read privacy source beyond my R2 reads. Capacity
figures are the coordinator's dated observations, not verified future headroom.
I ran no probe.

## 2. Decision dispositions (D1-D10)

| Pointer | Decision | Basis |
| --- | --- | --- |
| `/decisions/0` D1 | **Accept.** Bounded component-only product correction by the original author, with exact component review. The original FAIL/PASS/FAIL/PASS/PASS-bounded/HOLD record and WSR-03 stay immutable. No all-six re-judgement and no handler lease | Matches my R2 §2.1 unbundling. OpenAI R2 revised its owner gate. "Reviewers report; authors fix" is standing protocol. An authorship retake stays owner-only and is not requested |
| `/decisions/1` D2 | **Accept two fields.** `requested` counts attached live tasks this cleanup actually cancelled. `remaining` counts all unfinished admitted work, including reservations and the caller. `drained` iff `remaining == 0` | My R2 preferred a third field but called folding "acceptable" with a documented change of meaning. `/tasks/0` records the change of meaning prospectively, so my preference is withdrawn, not overridden |
| `/decisions/2` D3 | **Accept.** Unbound `close`/`begin_shutdown` close the fence without binding. Bound wrong-loop or no-loop calls raise before any mutation | Rejecting MiniMax's "unbound no-op" is correct: a closed scope must refuse later admissions |
| `/decisions/3` D4 | **Accept C4 first, with an explicitly HELD review gate** | `ORCHESTRATION_PROTOCOL.md:241` permits "a recorded held review gate". Lines 175-176: "A blocked reviewer need not block authors … but unreviewed implementation cannot be integrated or qualified". See §3 for OpenAI's dissent |
| `/decisions/4` D5 | **Accept.** One MiniMax-M3/thinking candidate and one Astra judge, at the corrected C4 tip. No novel-bug quota, and replayed public conclusions cannot qualify | This is a new family's first attempt in the domain. `REPO_CONFIG.json` scopes M3 to "Bounded evidence inventories only" as its *current* qualification, and an assessment is the lawful way to test a wider scope. A FAIL is terminal for this attempt |
| `/decisions/5` D6 | **Accept as provisional and gated**, with the §4 finding | "Authorship competence is not review competence" (`PROTOCOL.md` §4). The packet makes provenance a pre-dispatch HOLD condition |
| `/decisions/6` D7 | **Accept.** A serial `ha.py` diagnostic-sink lease. Public `data.key`/`password_protected` are preserved through proven display context. No type-wide bool/None exemption, no blanket never-redact `Hub.equals` | This supersedes my R2 bool/None suggestion (see §3) |
| `/decisions/7` D8 | **Accept.** API034 review (`12eeef93`) and evaluation (`c3fcace6`) are complete. M-1 freshness, WS040 broader evidence and combined holds stay open. Astra, not Sol, evaluates the future M3 review | Matches my R2 §2.6 and §2.5 |
| `/decisions/8` D9 | **Accept.** Concrete coordinator records per dispatch, with no extra owner ritual | |
| `/decisions/9` D10 | **Accept.** Scoped documentation-only maintenance for the stale exclusion text. Pinned evidence: `ORCHESTRATION_PROTOCOL.md:177` "No Anthropic/Claude … fallback", and the Run objective "no Anthropic models" in `ROUND3_PREFLIGHT.json` | Both are superseded by `ORCHESTRATION_PROTOCOL.md:13-16` and `AGENTS.md`. Historical records stay unedited |

**Staffing and reserves accepted:**

- `/tasks/0`-`/tasks/7` as written: authors, reviewers, bases, reserved trees and exclusive paths.
- Correction reserves: one delivery, one review, one material fix and re-review per product package.
- Assessment budgets: one candidate and one judge each, with no retry.
- `/capacity`: at most two new workers plus coordinator plus protected external. This matches `REPO_CONFIG.json` `max_new_active_workers: 2`.
- `/wave_order` A-E.
- `/remaining_gates` and `/owner_questions`.

Two allocations carry no verified backup: WS-R01, whose reviewer is Astra, and
the privacy review fallback. Both are stated honestly, and the response to a
failure is to hold, not to substitute.

## 3. Prior dissent and its disposition

- **OpenAI R2 order (qualify M3 at `2d02004d` before C4; hold C4 dispatch until
  a qualified review reserve exists).** Not adopted. I agree, on policy:
  - Protocol line 241 lets a recorded held gate stand in for a reviewer at
    authoring time.
  - The C4 source stays unintegrated and unaccepted (`/tasks/2/state`).
  - Assessing the corrected tip asks the candidate for new analysis, not a
    replay of public J-1/N-1..N-7.
  - The cost is a serial dependency, already shown in `/wave_order/1`.
  OpenAI must decide on the record; I do not treat its R2 as consent.
- **OpenAI R2 conditional owner choice for a second Opus WS authorship
  attempt.** Not prepared now (`/owner_questions`). I agree: my own R2 OC-1 and
  OC-2 were conditional, and neither condition has occurred.
- **MiniMax R2 §3.3 ("at most one admission pending", "`async def`", "can never
  settle while the drain runs").** I independently confirm the packet's
  rejection at `15c069bd`:
  - `_admit` is a plain `def` (line 337).
  - The reservation is held across the synchronous `factory()` call. A
    reentrant `try_start` on another owner inside that call can therefore stack
    a second reservation.
  - An eager cleaner started inside `factory()` that suspends hands control back
    to `_admit`, so registration can proceed while that drain waits.
  MiniMax's narrower point stands, and the conservative path in `/decisions/1`
  covers it: when the drain is synchronously inside the ancestor frame and never
  suspends, the reservation cannot settle.
- **MiniMax R2 Anthropic-author wiring pair (P6) and "rediscovered findings
  score nothing".** Rejected by `/rejected_or_calibrated_peer_claims/0` and `/4`.
  I agree: the pre-competence API lease is explicit, and a required novel
  defect would make a clean corrected chain impossible to pass.
- **My own R2 positions that the packet modifies:**
  - The third `DrainReport` field (§2, D2).
  - The bool/None exemption: OpenAI's challenge is right that it is broader
    than the verified schema.
  - Route A's premise that OpenAI authored the existing WS runtime: wrong, see §4.
  I accept all three modifications.

## 4. Finding: the D6 provenance premise is not supportable on current Git evidence

`/decisions/5/choice` describes the target as "original non-Anthropic existing
WS/app/runtime lifecycle source". `/tasks/6/base_selection` requires the
coordinator to "prove actual target existing source is non-Anthropic before
launch". The `Co-Authored-By` trailers up to `12ad507e` show:

- `src/rest_api/websocket.py`: 3 of 8 commits are co-authored by
  "Claude Opus 5.5":
  - `323af8e4` "hub-owned event stream, /ws contract and truthful /api/status"
  - `c39ee8d5` "get_status reads the matrix fresh"
  - `dbf5349e`, a style fix
- `src/rest_api/app.py`: 2 of 20 commits are co-authored by Claude Opus 5.5:
  `323af8e4` and `bc3b9353`.

The controller itself is absent at `12ad507e`, so that exclusion holds. But the
core `/ws` lifecycle that the candidate would review includes code co-authored
by this same model. My R2 §2.2 route A said "OpenAI authored the existing
`websocket.py`/`app.py` runtime", and that statement was wrong. I correct it
here. The other R2s did not depend on that premise.

**Why this does not block acceptance.** The packet already fails closed:

- `/decisions/5/limits`: "If provenance/independence or useful new scope cannot
  be proved, HOLD this candidate and wiring, continue other packages".
- `/tasks/6/acceptance/2`: "Conflict/provenance … unproven means HOLD, not a
  retake relabel".
- `/async_review_assessment/axes/provenance`.

On today's evidence, ASYNC-REVIEW-ASSESS and therefore WS-WIRING should be
expected to stay HELD. No resource is committed before that gate. The rest of
the plan does not depend on it.

**Binding interpretation of my ACCEPT.** I accept D6 only with this reading:

1. The coordinator records this evidence at the provenance gate.
2. Changing the D6 target, for example by narrowing it to hunks that Anthropic
   did not co-author or by relabelling co-authorship, is a material change. It
   needs a new packet version and fresh same-hash decisions. It cannot be
   decided at dispatch time.

This reading follows `/adoption`, so it adds no requirement to the packet. If
other participants read D6 as allowing that narrowing at dispatch time, our
readings differ materially, and the coordinator must reconcile that through a
new version.

I declare a conflict of interest: D6 allocates a qualification opportunity to my
own family. This finding weighs against that allocation.

## 5. Unchanged failures and held gates

The following stay exactly as recorded (`/remaining_gates`):

- Privacy assessment: two PASS / four FAIL, with J-1 and N-1..N-7.
- WS component: correctness FAIL at `15c069bd`, first-authorship HOLD, WSR-01..04 including the attempt-level WSR-03.
- The old Opus 4.7 failures and lost originals.
- The narrow scope of the API-refusal qualification.

These gates remain held:

- Privacy review, acceptance and admission.
- WS wiring.
- API034 M-1 freshness.
- WS040 broader evidence.
- HA/UI qualified pairs.
- Combined proof, build and version.
- All owner gates: Tron/visual, physical HIL, the 72-hour soak, the field week and final version/artifact release.

R3 does not expand any exhausted assessment budget. This decision qualifies no
route. Every launch remains future and freshly gated, including quota, native
route, exact base and published, verified integration.

## 6. Delivery checks

After this prose was final, the five existing documentation modules were run
once with the root venv Python and this checkout's measured imports. The run
used a copied environment, `-B`, fresh owned data, config, TEMP/TMP, basetemp
and JUnit roots, and `-p no:tests.route_inventory -p no:cacheprovider`. The
results and receipt paths are in the external `worker_done` report, not here,
so this file stays unchanged after the run. This file is the only tracked
change. It is committed with the authorized invocation-only empty `hooksPath`
prose exception. No source-hook pass is claimed.
