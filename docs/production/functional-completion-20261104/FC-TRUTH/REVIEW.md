# FC-TRUTH independent factual review

**Verdict: REQUIRE_CHANGES.** Reviewed exact author commit
`99e72bd9ac9c592afde5fd3b110f8b56e7c3d5d4`, parent
`a07cf94211486150fa8222c5aad43ecb9f938bf3`, on 2026-11-04.
The inventory's arithmetic reproduces, but its claimed privacy-history loss and
five resolved dispositions do not. Its feature table is a sound ledger index,
not the complete source/assertion/acceptance map claimed for this assignment.
Do not apply its canonical reconciliation proposals until the actual author
corrects the report and the exact corrected commit receives factual re-review.

Reviewer: assigned OpenAI `gpt-6.1-sol/high`, independent of the MiniMax author;
Task `task_999c32971b04`, Dispatch `ctx_465cf8734afd`. This is a factual prose
review, not a model assessment, qualification decision or source acceptance.
No helper, other reviewer decision, subagent, browser, plugin or alternate model
was used. No source, tests, canonical records or author evidence were changed.

## Pinned inputs and method

The dedicated branch was `review/wp-fc26-fc-truth-review`, with the exact author
HEAD at entry. Initial Git status contained only pre-existing untracked
`.codex/`; that configuration remains protected and unstaged. No checkout,
reset, import, fetch, rebase, cherry-pick or moving-ref follow occurred.

| Input | Canonical Git-LF SHA-256 |
| --- | --- |
| Author `INVENTORY.md`, 233537 bytes | `d7a8e0e48f24b8ba8291ec75cda2bc2d830c3eaf60f141ff6c764ff1f1c6c2bd` |
| Adopted complete packet, 616751 bytes | `933166c3925e38e748bb4b78e15bb488c90e43bb12807b2f02ffd65b7ea6f2f4` |
| Adopted plan text, 13195 bytes | `90f8459b050577acb4fd6b55e195288380a1586780dd3eba05accf2159da00bb` |

I read the full author report, current AGENTS/storage policy, standing and
adopted protocols, current handoff/ledger, adopted plan, CONSENSUS,
ADOPTION_NOTES, FC-TRUTH staffing/acceptance, and the 65 original unit scopes
and current reservations. The packet's correction reserve is one actual-author
factual correction and one exact corrected-commit re-review; this verdict
neither starts that work nor creates an assessment retry or extra judge.

I read the actual registry parser and level/freshness/evidence implementations
and called existing `load_features`, `load_findings` and `ledger.compute`
read-only over `default_roots()` in this checkout. I compared every reported
feature's title, target, recorded/effective level, cap, freshness, gap flags,
package, cited fresh proof path/SHA/client/level and stale-record count with
those results. All 30 package aggregates were compared independently.
No render, gate, ledger generation, registry campaign or canonical import ran.

The 61 disposition rows were checked against the parser-open set, original
register assertions and the accepted triage records, with direct source reads
for consequential differences below. Unchanged register/registry/pending bytes
since `3602a4e` and the integrated triage blob mapping were checked as identity
facts. They do not independently validate historical dispositions. The only
product-source addition in the inspected `src/web/tools/tests/run.py/run_server.py`
diff from that base is the unwired WS component (with its test addition).

The original author completion, known native/session metadata, ancestry helper
and result, documentation-run originals, coordinator counterpoint and retained
manifest were read without changing them. All 151 manifest members matched
their retained original byte lengths and SHA-256 values. That verifies retained
bytes, not the truth of every statement inside them. The full Git bundle and
native export remain in the coordinator's registered storage; I did not import
the bundle or make redundant workspace/build copies. Private raw paths and
native contents are excluded from this tracked review.

## Required factual corrections

### R1 — Medium: a mistyped SHA is presented as lost history

**Location:** inventory lines 54/69, VAL-15 at 312, privacy chain in section 4.4,
R-02 at 996, and section 10.3; also the author's separate completion receipt.

Independent direct Git observations were:

| Operation | Actual result |
| --- | --- |
| `git rev-parse 615d3c84` | exit 0, `615d3c8403b237dd117c8032697c9b58895f9217` |
| `git cat-file -t 615d3c8403b237dd117c8032697c9b58895f9217` | exit 0, `commit` |
| `git cat-file -t 615d3c8403b237dd117c803269c7b9b58895f9217` | exit 128, invalid object name |
| Both named local and origin C2 refs via `git show-ref` | exit 0, point to the **first**, valid SHA |
| Actual C2 ancestry against pinned parent `a07cf942...` | exit 1, non-ancestor, without an object error |
| Actual C2 ancestry against C3 `2d02004d...` | exit 0, ancestor |

The preserved author ancestry helper hard-codes the second, incorrect full SHA.
The coordinator's original counterpoint agrees with these independently observed
results. The committed [C4 delivery record](../../remediation-20261104/recovery-execution/PRIV_C4_DELIVERY.json)
already lists the correct C2 hash in the retained eight-commit C1-C4 chain.

**Impact:** the inventory invents an availability blocker and a coordinator
fetch/restore task. Its non-partial-clone observation cannot establish loss
when the tested identifier is wrong. This is a reference/transcription error,
not evidence that C2 was lost. It does not erase separately recorded lost
original evidence or make the privacy chain accepted.

**Necessary correction:** replace the incorrect C2 reference and all derived
absence/restore statements with the valid object, actual non-integration and
chain ancestry. Remove R-02's restoration/fetch acceptance requirement. Preserve
the original failed command and report bytes as historical evidence; issue a
corrected author receipt rather than rewriting those originals. No fetch or
history repair is required by this finding.

### R2 — Medium: five inherited leads are incorrectly labeled resolved

**Location:** inventory section 4.2, lines 264, 265, 268, 277 and 280; UI-05's
claimed absence of the synthetic-change mechanism also feeds section 7/8's
anchor-reconciliation rationale.

Both the accepted historical triage and its accepted execution delta classify
these five as `S`, source-inspection candidates with behavior not reproduced.
The execution delta's section 6 explicitly lists all five under that class.
The inventory instead attributes a resolved disposition to that input, despite
no relevant product-source change. Direct current-source reads corroborate the
retained conditions:

| Finding | Actual evidence at reviewed commit | Required inventory disposition |
| --- | --- | --- |
| API-16 | `sys.path.insert` remains inside nine request handlers: audio.py 45/82/105/371/394, outputs.py 263/293/316, cec.py 314. The audio handler body performs the insertion per request. | Preserve `reproduce`/source-inspection lead; do not say inherited resolved. |
| API-18 | `src/config.py:258` still defines the legacy `SceneManager`, including its legacy scenes reader and writer. No accepted deletion is identified. | Preserve the inherited source lead; class presence is not proof of active runtime use. |
| API-21 | `src/rest_api/scenes_v2.py:212` defines its own async response helper; its handlers await it. The shared sync helper remains in utils.py. | Preserve the inherited unification lead. |
| UI-05 | `hardware-drawer.js:145-168` forwards controls to legacy elements and dispatches `new Event("change")`; the cited range contains the mechanism, not merely unrelated comments. | Preserve the inherited source lead; correct the erroneous anchor explanation. |
| UI-08 | `dashboard-manager.js:1113-1140` reads/writes localStorage; kiosk.html 2856-2883 loads/migrates/defaults local shortcut/profile pin arrays and writes them to localStorage. | Preserve the inherited persistence/store lead; no resolution is established here. |

**Impact:** these recommendations falsely route unresolved source work toward
register-text reconciliation. The report's general non-closure disclaimer does
not make its row-level resolved assertions true.

**Necessary correction:** restore the actual inherited classifications and
limits, cite the surviving source accurately, and update dependent summaries
and proposed canonical prose. Report source-backed residuals without claiming
a new runtime reproduction or prescribing duplicate implementation. An author
may only assert resolution with actual accepted row-condition evidence.

### R3 — Medium: the 268-row ledger index omits the required semantic map

**Location:** sections 5 and 10.1 and the completion claim that all 268 feature
contracts have their actual source/evidence/acceptance map covered.

The table correctly indexes ledger results, but does not map the registry
`claim`, interfaces, recorded `basis`, actual source/assertions and remaining
acceptance for each feature. This matters particularly for the 102 rows labeled
no committed record: their baseline can still rest on a named test or historical
assertion, which the table never identifies. Examples read directly:

| Feature | Omitted consequential distinction |
| --- | --- |
| F-API-001 | Registry basis identifies health/runtime, integration-lifecycle and real OpenAPI response assertions; table only says no committed record. |
| F-API-039 | Basis names welcome/snapshot and get_status tests. The actual tests in `tests/sim/test_sim_ws_contract.py:281/295` assert those effects; absence of a committed scenario record is a different fact. |
| F-UI-015 | Recorded V3 rests on a scene-editor save flow; the registry explicitly retains prompt-based step editing (UI-19). A V3 baseline is not complete editor acceptance. |
| F-API-032 | Its fresh V3 record is `live.matrix_offline`: link/refusal/recovery and UI/kiosk connection-state checks, not every welcome/get_status requirement in its title. |
| F-FLIC-005 | The table's first selected V3 proof is `flic.cec_output_navigation_refused`, asserting 400/no write/no mutation; the positive volume proof is a different record. Its metadata explicitly says physical SDK/buttons/version are unknown. |

The [frozen contracts](../../../agent-process/phases/execution-pinning-20261101/FEATURE_CONTRACTS.json)
require actual interface action, independent effect, relevant negative controls
and source/client/image/covers attribution. They explicitly say a scenario
mapping is a claim, not accepted assertion or current capability. The FC-TRUTH
task requests an actual source/evidence/acceptance map, not just its cardinality.

**Impact:** a mechanically correct level or feature tag can be mistaken for
complete contract coverage. No new defect or incorrect ledger level is alleged.

**Necessary correction:** complete the bounded prose map for all 268, using
explicit grouped cross-references where appropriate: recorded basis and actual
assertion scope, supported source/client/image binding or unknown, and residual
acceptance. Keep inherited proof distinct from newly read assertions and fresh
records. Do not rerun campaigns, add tests/tooling, change caps or promote levels
to fill this prose gap. Narrow the completion claims to what was actually read.

### R4 — Low: the documentation import conclusion contradicts the original snapshot

**Location:** inventory section 12.3 and its assertion that the run did not
import `src/rest_api/*`; section 12.3 also says the same snapshot is captured
at interpreter exit.

The retained original `docs_result.json` has **25** `rest_api`/`rest_api.*`
entries in `imports_at_finish`, including `rest_api`, `rest_api.app` and
`rest_api.control`, all resolving to the author's own checkout `src/rest_api`.
The retained `docs_entry.py` filters `observed_product_imports` using `src.`
and `tools.validate` prefixes; the project's canonical import name is instead
`rest_api`. Its filtered zero does not establish absence of product imports.
The serialized `imports_atexit` is empty, so that file is not proof of a second
completed exit-time snapshot either.

**Impact:** execution provenance is misstated, though the direct exit/JUnit
pass remains valid and no source qualification follows from those imports.
**Necessary correction:** report the actual canonical module origins from the
original in-process snapshot and the actual exit-snapshot limit. Preserve the
original files and correct the prose/derived supplemental receipt; do not rerun
the unchanged documentation check or relabel it as behavior acceptance.

## Reproduced arithmetic and bounded conclusions

| Measurement | Verified result at exact reviewed commit |
| --- | --- |
| Parser population | 265 findings; 61 open = 59 register + VAL-14/15; severities C1/H2/M31/L27 |
| Raw registry ordering | 227/268 below target; 227 unequal; 0 above |
| Effective ordering | 210/268 below; 58 at/above; 2 above (F-API-032/040) |
| Effective inequality sensitivity control | **212**, not 210: it incorrectly counts the two above-target rows |
| No fresh passing record | 198/268 = 96 stale-only + 102 no record; fresh failures 0 |
| At/above target without fresh passing evidence | 16/268; recorded fallback remains distinct from fresh proof |
| Caps | Exactly twelve HIL-09 links, F-MTX-007 through 017 plus 020; UC-18/SEC-14 cap no linked feature |
| Effective levels | V0 18, V1 122, V2 32, V3 96; V4/V5 0 |
| UI/kiosk | 50 rows; raw V1-to-V3 subset 33; effective gaps 24 + 7 = 31; no fresh pass 30 + 11 = 41 |
| Packages and feature rows | 30/30 package aggregates and 268/268 reported metadata rows match; no proof-path/SHA/client/level/package mismatches found |

The dated 228 assertion does not reproduce at `9b783d72`'s identical registry;
227 is the verified raw numerator. The 210 value is the effective measure at
this snapshot, not a bug count. The 203/57 pair is explicitly a historical
wave02 snapshot in REPO_CONFIG, not an alternative current denominator or an
error established by comparing it to today's 210/96. The independent baseline
at `ac1dc745` was observed 2026-11-04T06:08:46Z; the adopted packet is dated
2026-11-04T18:57:44Z. Preserve those dates and the older snapshot's attribution.

The cap control also checks the parser's **last-cell** closure rule: HIL-09's
description-cell checkmark does not close it. Non-ancestor/unknown evidence
goes into `FeatureRow.stale`; do not redefine that aggregate as only
ancestor records whose covered files changed. The mechanical ledger semantics
were inspected, not replaced with a reviewer implementation.

## Coverage of dispositions, reservations and proposals

All 61 rows were considered. R2 identifies five unsupported resolutions; the
other 56 retain their stated bounded recommendations for this factual review,
subject to R1 and the inherited-proof limits. In particular BE-22/API-25 remain
unreproduced leads; BE-20/UC-18 remain unfinished architecture records, not
confirmed current product failures; SEC-14's MPL/license-stub correction does
not settle public-history/cache work; BE-14/15/25 and HIL-03/09/14 retain their
physical limits. UI accessibility/layout/deadness leads were not exercised in
a browser or on a device. An inherited resolved label among the remaining rows
still requires the original exact assertions and acceptance before closure.

All 65 IDs, packages/phases and current author/reviewer reservations match the
adopted packet: four inventory routes, eleven conditional UI routes, fifty
qualification/provenance-held routes. I read the unit focus/dependencies and
current held-readiness text. No reservation is a fresh qualification grant;
there is no accepted broad MiniMax source-review entitlement. UI, lifecycle
and HA first assessments still need exact unused-attempt/native/conflict and
qualified-judge gates; the 65-row shorthand is not a replacement for the ten
staffing rows. No source author/reviewer/judge is cleared by this review.

Two nonblocking precision refinements are needed when correcting the report:

- Section 6.3's four units “ready now” should mean bounded inventory task fit
  subject to normal gates. SW-REPO requires accepted findings intake; SW-DOCS
  retains numerous accepted/integrated/published package and unit dependencies.
  Its full completion/dispatch readiness was not established. The adopted
  packet preserves those dependencies even while allowing early bounded work.
- “No competence-assessment record” for MiniMax in section 6.1 should say no
  relevant **PASS** for the proposed source role. The terminal privacy candidate
  and judge records exist and must remain visible; section 4.4 preserves them.
- Reconcile the read-scope populations: section 2.3 carries 47 inherited rows
  and the supplemental receipt says 14 re-verified, whereas section 4.3 uses
  17 expanded/44 other rows and 27 table strength cells say re-verified.
  These can describe different measures, but they need explicit per-ID sets
  and definitions rather than interchangeable claims of semantic rereading.

I inspected all seven canonical-prose proposals. Proposal 1 correctly identifies
the stale active-wave/API-evaluation string; 2 preserves the owner budget hold;
3 distinguishes old staffing reservations from the adopted packet; 4 preserves
the dated 203/57 history; 5 correctly prohibits hand-editing the generated
ledger. Proposal 6 needs R2's corrected row-specific distinctions and must not
turn literal test-file occurrence counts into assertion adequacy. Proposal 7
correctly preserves HIL-09's open state and all twelve caps. None is applied here.

All five residual leads were examined: R-01's arithmetic reproduces; R-02 is
false (review finding R1); R-03's anchor claims need the UI-05 correction;
R-04's assertion inventory is an appropriate bounded follow-up, with file/text
presence insufficient for behavioral coverage; R-05 correctly refers to the
already planned WS wiring package and creates no duplicate implementation.

The three carried owner conditions are grounded in their named records:
privacy budget remains explicitly pending, API-07 retains its specific catalogue
visual close condition, and SEC-14 retains the support/cache action. No new
question or approval request was issued. Existing closed original Tron decisions
are not reopened; physical/changed-visual/continuous72h/field-week/final artifact
and release decisions remain separate.

## Preserved current records and review limits

RV-API034 bounded source review and its report evaluation are complete within
their recorded scope; full RV/source integration remains held. M1/F-SEC-007
candidate freshness is separate: current integration's V3 baseline and the
retained `caaa` candidate's V2 result are different snapshots. I read the recorded
disposition and relevant passing-proof scopes; I did not rerun the failed gate.
RV-WS040 remains a separate retained chain. The accepted component at `e54228c0`
is an ancestor, remains unwired, and its header and actual websocket.py task
creation agree with that limit. Presence of the module does not close CR-01.

Privacy C1-C4 remains unintegrated/unaccepted, with actual C4 tip `53853257...`
and its eight-commit/thirteen-path chain recorded in C4 delivery. Both terminal
privacy FAILs, WS NOT_GRANTED/WSR03, the complete D6 hold, real lost originals,
and pending owner budget remain unchanged. I did not judge qualification, review
privacy implementation for acceptance, reconstruct missing originals or waive
any domain/owner gate.

The original author opencode.json **exists** (1628 bytes, SHA-256
`62e6f5ab100bffe9aa802a380f3860612ba1aedf5e760ae443d5040984b18096`).
Its completion receipt's model-config-absent field is false. The review only
reads it and checks its hash again at closeout. A retained pre-author config
checkpoint was not supplied in the 151-member evidence manifest, so those
members alone do not prove author-entry equality. No config mutation is inferred.
The worktree `.git` is a pointer file: hashing a nonexistent `.git/config` as
empty does not establish the actual common/global configuration's identity.
Correct the supplemental receipt's evidentiary scope; preserve its original.

The author's section 13 host-wide “No other location ... was written” and
“no other agent's output ... was read” claims exceed its bounded inventories
and conflict with its declared historical-evidence reads. Replace those with
observed owned-root inventory and actual read/write scope. No all-host audit or
unobserved config history is claimed by this review.

Full semantic rereading of every historical feature assertion, every original
client campaign, every image layer, all historical privacy bytes and every UI
behavior was **not** performed. I read actual source/assertions for the disputed
rows and selected consequential proof bindings (Remote routing, WS link/live
effects, CORS, PIN refusal and Flic refusal), including their client/image/covers
metadata. These are bounded semantic checks, separate from the complete
268-row metadata comparison. Missing semantic map coverage is reported as R3,
not silently counted as completed source review. No runtime defect was
reproduced. Documentation passes cannot approve any source/feature/model gate.

## Verification and storage

The required five existing documentation modules are run once after this prose,
using the absolute root venv interpreter with `-B`, inherited Windows environment
and fresh registered payload data/config/TEMP/TMP/TMPDIR/basetemp/JUnit. Route
inventory and cacheprovider are disabled. The separate completion receipt
records actual direct argv/cwd/safe overlay, UTC, direct exit, full streams,
JUnit, in-run module origins, and ordinary/hidden owned-file inventories.
Any result paragraph appended after that run is identified as post-run prose.

Final strict UTF-8, local Markdown targets/anchors, CR-aware whitespace and exact
staged-scope checks cover the delivered bytes. Only this new REVIEW.md is
committed, using the authorized invocation-only empty hooksPath prose exception;
no persistent hook setting or source-hook success is claimed.

Registered task storage `02df1ad6c37b48a1b82a80dbf261e2e1` retains the smallest
useful review extraction, command/check receipts and documentation-run originals
for coordinator preservation and the exact author correction/re-review. The
completion receipt records measured bytes (approximately 3.4 MB retained).
Review date: **2026-12-04**; quarantined: **0**; actually removed: **11744 bytes**,
one redundant task-created reformatted completion copy; its protected original
remains directly readable. No other agent's evidence, cache,
branch or workspace was cleaned. Outside-payload task output is this sole
tracked report, the Git commit/index changes needed to deliver it, and supported
tool-managed storage lifecycle metadata. No publication, release, cleanup or
next worker is performed by this reviewer.

### Post-run result and final-byte limits

The single reviewer documentation invocation ran 2026-11-04T19:49:24.437142Z
through 19:49:28.084317Z: direct exit **0**, **489 passed**, JUnit failures **0**,
errors **0**, skipped **0**, and empty stderr. All five test modules,
tests.conftest, hub, hub.openapi and the observed canonical rest_api modules
resolved inside this reviewer checkout in the process's session-finish hook;
pytest resolved inside the specified root venv. The complete origins and raw
streams are retained with the run receipt. This is not new-Markdown parsing,
full source behavior, complete REST coverage or qualification evidence.

All prose edits after the one run, including R4, the precision refinements and
storage/result wording, receive strict UTF-8, local-target, whitespace and scope
checks only. R4 follows the read of the original author's full import snapshot
and filter; no second documentation run is claimed.
