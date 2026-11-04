# FC-TRUTH — functional-completion truth inventory (2026-11-04)

**Package:** `FC-TRUTH` (phase `functional-completion-20261104`) · **Scope:** `prose_inventory` · **Author route:** MiniMax M3 (`minimax-coding-plan/MiniMax-M3`, variant `thinking`) via OpenCode 2 · **Reserved reviewer route:** OpenAI `gpt-6.1-sol` / `high` (`Sol`, OpenAI family).

This is a **bounded inventory and prose report**. It is the sole new tracked output of this package. It closes no finding, promotes no feature level, generates no ledger, admits no evidence, grants no competence, changes no canonical registry/ledger/register row, and approves no owner, hardware, visual, soak, field or release gate. Every canonical edit it suggests is a **proposal for the coordinator to apply after qualified different-family review** of this exact commit.

**This report is not self-accepted.** It requires an independent qualified different-family review at its exact commit before any coordinator action.

## 1. Scoped base, branch, inputs and verified hashes

| Item | Value |
| --- | --- |
| Exact entry base | `a07cf94211486150fa8222c5aad43ecb9f938bf3` |
| Branch | `execution/wp-fc26-fc-truth` |
| Worktree | `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-fc26-fc-truth` |
| Remote | `origin` → `https://github.com/ryan-haver/8x8-hdmi-matrix-hub.git` |
| Working-tree state at entry | clean (`git status --porcelain -uall` empty) |
| Task / Dispatch | `task_ae949bd12fff` / `ctx_2caca18359bf` |
| Coordinator terminal | `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| Author model | `minimax-coding-plan/MiniMax-M3` (variant `thinking`); CLI effort override unsupported; no helper/subagent/alternate model was dispatched or observed |
| New tracked output | `docs/production/functional-completion-20261104/FC-TRUTH/INVENTORY.md` (this file) |
| Owned ignored roots | `build/remediation-functional-20261104/fc-truth/**`, `C:/t/remediation-functional/fc-truth/**` |

### 1.1 Adopted-packet inputs verified at this base

| Input | Expected (assignment / packet) | Observed at `a07cf94` | Result |
| --- | --- | --- | --- |
| `docs/agent-process/phases/functional-completion-20261104/FINAL_PACKET.json` canonical Git-LF SHA-256 | `933166c3925e38e748bb4b78e15bb488c90e43bb12807b2f02ffd65b7ea6f2f4` | `933166c3925e38e748bb4b78e15bb488c90e43bb12807b2f02ffd65b7ea6f2f4` (616751 bytes, LF-only, 0 CRLF sequences) | **match** |
| `.../FINAL_PLAN.md` plan-text SHA-256 | `90f8459b` (prefix) | `90f8459b050577acb4fd6b55e195288380a1586780dd3eba05accf2159da00bb` (13195 bytes, LF-only) | **match** |

The packet's own `complete_final_plan_text_sha256` is the same value as the file on disk, so the packet's embedded plan text and the committed `FINAL_PLAN.md` are the same bytes. `ADOPTION_NOTES.md` and the adopted `CONSENSUS.json` were read in full before any extraction; the notes' constraints (no OpenAI self-review, MiniMax-specific facts cross-checked by a non-MiniMax coordinator, definitions published for every count, HIL-09's twelve caps preserved, UC-18/LICENSE-stub prose not recast as current defects, the existing owner privacy-budget question left pending) are honoured throughout this report.

### 1.2 Ancestry facts used in this report

`git merge-base --is-ancestor <sha> a07cf94211486150fa8222c5aad43ecb9f938bf3` was run for every commit this report cites.

| Referenced record | SHA | Relation to `a07cf94` |
| --- | --- | --- |
| SW-FINDINGS-01 execution base | `3602a4e4ad33` | ancestor |
| SW-FINDINGS-01 accepted author commit | `a2dab11cdc87` | NOT-ancestor |
| SW-FINDINGS-01 accepted review commit | `ac9c4d49fd3c` | NOT-ancestor |
| SW-FINDINGS-01 integration commit | `22fd6d10fa03` | ancestor |
| SW-AUDIT-01 accepted bounded inventory commit | `f2ee085a37a4` | NOT-ancestor |
| SW-AUDIT-01 re-review require_changes | `d44ad2bca78d` | NOT-ancestor |
| RV-API034 source-review report | `12eeef938857` | NOT-ancestor |
| RV-API034 evaluation report | `c3fcace6260e` | NOT-ancestor |
| RV-API034 reviewed source (C2) | `caaa4faabe9e` | NOT-ancestor |
| RV-API034 API-read/WS chain tip | `1fbfee112cc5` | NOT-ancestor |
| WS accepted UNWIRED component integration | `e54228c0e3a9` | ancestor |
| WS component wording fix | `78295ecdf8c4` | NOT-ancestor |
| WS wording independent re-review | `9817554ed6d7` | NOT-ancestor |
| WS component author base | `460a190575e9` | ancestor |
| privacy C1 | `11f305b16c4c` | NOT-ancestor |
| privacy C2 | `615d3c8403b2` | unknown-object |
| privacy C3 | `2d02004d3108` | NOT-ancestor |
| privacy Opus judge | `e8ce39660a37` | NOT-ancestor |
| privacy M3 judge | `1b2b7c5f0ff8` | NOT-ancestor |
| privacy M3 assessment | `f3a783b49778` | NOT-ancestor |
| VAL-14 source correction | `3788353ef2ef` | ancestor |
| VAL-14 independent review | `0bd3d76f8bc9` | ancestor |
| VAL-14 fresh source | `310d8b65a9fc` | ancestor |
| audit reviewed head (ac1dc745) | `ac1dc745ebf5` | ancestor |
| wave02 ledger commit | `28fce729ca4e` | ancestor |
| peer baseline commit 9b783d72 | `9b783d723c81` | ancestor |

Two ancestry facts deserve emphasis because several findings depend on them:

* **The accepted SW-FINDINGS-01 triage report is integrated as identical bytes.** The accepted author commit `a2dab11cdc871d6a98c563b019a361371a9af710` is *not* an ancestor, but the blob for `docs/production/software-waves/SW-FINDINGS-01/execution-20261101/AUTHOR.md` is **byte-identical** at that commit and at `HEAD` (git blob `f09c333636cb0d562806140b28b34568c3ae406d`). The content entered this history through the coordinator's integration commits (`7e21ed2b` report, `2862835c` R1–R8 corrections, `aeb906a3` R3/R5 residual correction, `22fd6d10` accepted correction 02 review). This is the protocol's *documented inspected equivalent commit mapping* case for an intentional squash/re-commit, not a content divergence.
* **The retained privacy C2 commit object is not present in this checkout's object database.** `refs/heads/ryan-haver/wp-sec-data-02-c2` and `refs/remotes/origin/ryan-haver/wp-sec-data-02-c2` both still point at `615d3c8403b237dd117c803269c7b9b58895f9217`, and its worktree still reports that HEAD, but `git cat-file -t 615d3c84...` fails with *Not a valid object name*. The commit is therefore **unreadable and unverifiable here**; this is recorded as an evidence-availability limit, not as a defect claim about the chain. The repository is **not** a partial clone (`remote.origin.promisor` and `extensions.partialclone` are unset), so the cause is a local object gap. Restoring that object is a coordinator action, not a worker action.

## 2. Method, actual reads and honest limits

### 2.1 What was actually read

The project owns the parser and the level semantics; this report **used those sources**, not a re-implementation of them.

| Source | How it was read | What it determined |
| --- | --- | --- |
| `tools/validate/registry.py` | read in full; `load_features()`, `parse_register()`, `load_pending()` and `load_findings()` called unchanged | which rows the project considers findings, and what 'open' means (struck-through ID, or a `✅`/`closed` marker in the last cell) |
| `tools/validate/ledger.py` | read in full; `compute()` called read-only with `default_roots()` (committed evidence only) | effective level, proven level, freshness, open findings, caps and dropped-level reasons |
| `tools/validate/model.py` | read (`Level`, `LEVEL_NAMES`, `level_for`) | the ordered level ladder V0…V5 and what a passing client proves |
| `tools/validate/gitinfo.py` | read (`freshness` semantics: `covers` path matching, `git diff --name-only sha..HEAD`, non-ancestor ⇒ stale/unknown) | how freshness is decided |
| `tools/validate/evidence.py` | read (`iter_records`, `redact`, `_SECRET_KEYS`, `_SECRET_QUERY`) | the committed-evidence record format and the redaction boundary |
| `docs/validation/features.yaml` | parsed whole (268 rows) | the canonical feature contracts |
| `docs/REMEDIATION_PLAN.md` | read whole; §4 register rows parsed with the project's own row regex (278 table rows, 263 unique IDs) | the original assertions and their recorded close conditions |
| `docs/validation/findings_pending.yaml` | read whole (2 rows) | VAL-14 and VAL-15 |
| `docs/validation/LEDGER.md` | read (generated at commit `28fce729`) | the committed canonical totals this report cross-checks against |
| `docs/planning/comprehensive-review-20261104/REMEDIATION_PLAN.json` and `REVIEW_BASELINE.json` | read whole | the 30 packages / 65 units / 268-feature crosswalk and the dated audit baseline |
| `docs/agent-process/phases/functional-completion-20261104/FINAL_PACKET.json` | read whole (616751 bytes) | the 65-unit allocation, the 10 staffing rows and the global invariants |
| `docs/production/software-waves/SW-FINDINGS-01/execution-20261101/AUTHOR.md` | read whole | the accepted 59-row triage that this report reconciles rather than repeats |
| `docs/planning/software-waves/EXECUTION_GATE_STATUS.json`, `EXECUTION_READINESS.md`, `docs/agent-process/REPO_CONFIG.json` | read | the current gate state, the 85-row dated reservations table and the dated readiness snapshot |
| `docs/audits/COMPREHENSIVE_PROJECT_REVIEW_20261104.md` | read whole | CR-01…CR-14 and the three disputed aggregates |
| product source (`src/`, `web/`, `tools/`, `tests/`, `.github/`, `Dockerfile`, `LICENSE`) | read in bounded complete chunks for every consequential claim below | the current source state of each finding |

### 2.2 Method

1. Resolve the pinned base once (`git rev-parse HEAD`, `git status --porcelain -uall`, `git worktree list --porcelain`, `git remote -v`). No checkout, reset, rebase, cherry-pick, import or moving-ref follow occurred.
2. Enumerate the parser-open set with the project's own parser at that base.
3. Recompute every level and freshness value with the project's own `ledger.compute()` over **committed evidence only**. `ledger.render()`, `gate()`, `tools.validate ledger`, `tools.validate check` and any evidence import were **not** run.
4. Read the consequential source for each finding's surviving condition and record the observed value with its file and line.
5. Cross-check the recomputed totals against the committed `LEDGER.md` and the dated audit baseline, and publish the differences rather than picking a convenient total.
6. Record what could **not** be read, and leave it unknown.

### 2.3 Limits that apply to every statement in this report

* **No runtime defect was reproduced.** No product test, scenario, browser session, container, device, simulator campaign, HIL session or image campaign was executed for any finding. "Source present" is a file/line observation, not an executed behaviour.
* **Hashes and counters are identity, not semantics.** Where a count is cited it identifies a population; it does not establish assertion strength. Assertion strength is stated separately for every finding.
* **The 47 no-material-delta register rows are inherited, not re-qualified.** Their disposition is carried from the accepted SW-FINDINGS-01 triage, which was accepted *as triage only, with limits*. This report re-verified the register-row byte-identity and the scoped source diff for them; it did not re-run their evidence, did not renew any acceptance, and did not re-qualify their evidence bytes.
* **Imported private/native evidence stays private.** No credential, token, private prompt, raw account dump, raw validation payload, image payload or archive payload was read. Only sanitised model/session/task/source references and hashes needed for review appear here.
* **This report makes no host-wide write claim, no route-coverage claim and no qualification claim.** It describes scoped metadata only.

## 3. Reconciled totals — definitions, numerators, denominators and unknown policy

### 3.1 The three figures in circulation are three different measures

| Figure | Definition | Denominator | Where it came from | Status at `a07cf94` |
| --- | --- | --- | --- | --- |
| **228** | rows whose registry `current != target` (an **inequality** test with no ordering) | 268 | MiniMax R3 packet review, §3.5 (`docs/agent-process/phases/functional-completion-20261104/round3/minimax.md:350`), measured at `9b783d72` | **Not reproduced.** The registry yields **227** rows with `current != target` and **227** with `current < target` (0 rows above target). `docs/validation/features.yaml` is byte-identical between `9b783d72` and `a07cf94` (`git diff --stat` empty), so the difference is **not** a base difference. The same peer's adjacent counts (268 unique IDs; 50 `F-UI`/`F-KIO`; 33 `F-UI`/`F-KIO` rows at V1→V3) **do** reproduce exactly at this base, so the +1 is isolated to that one numerator and is not explained by a different registry, a different parse target or a different base. I record it as an **open reconciliation item** for the coordinator and for the MiniMax fidelity review, not as a peer error. |
| **210** | rows whose **effective level** is below the target, using the project's own `ledger.compute()` rule (proven level if there is fresh passing evidence, else the recorded baseline, capped at V1 by an open critical/high finding) | 268 | the frozen per-package `below_target` values in `REMEDIATION_PLAN.json` (sum = 210) and the audit baseline | **Reproduced exactly**: 210/268 at this base, and every one of the 30 package aggregates recomputes to its published value (§3.4). |
| **203** | rows below target **as recorded in the last accepted wave02 ledger** | 268 | `docs/agent-process/REPO_CONFIG.json` → `readiness.current_values.below_target`, whose own `source` field says *"Last accepted wave02 ledger; wave03 qualification/evidence not yet applied. Adoption makes no readiness changes."* | **Superseded but still accurate as a dated snapshot.** It is a different measurement date and a different rule (the ledger as committed then), so it is neither wrong nor comparable to 210 without that context. |

**The rule this report uses.** `current != target` is *not* a below-target test. The ordered level ladder is V0 (Claimed) < V1 (Unit) < V2 (Simulated integration) < V3 (End-to-end) < V4 (Hardware) < V5 (Field). A feature is **below target** only when its effective level is strictly lower on that ladder than its target. At this base the two happen to coincide numerically at the *registry* level — 227 rows with `current != target` and 227 rows with `current < target`, because **no** registry row is above its target (the registry validator rejects `current > target`) — but they diverge at the *effective* level, where two features exceed their target (§3.3).

### 3.2 Exact numerators and denominators at `a07cf94`

| Measure | Numerator | Denominator | Rule |
| --- | ---: | ---: | --- |
| Features in the canonical registry | 268 | 268 | unique IDs in `docs/validation/features.yaml` |
| Registry rows with `current != target` (inequality) | 227 | 268 | raw string inequality on the registry fields |
| Registry rows with `current < target` (ordered) | 227 | 268 | `Level.parse` ordering |
| Registry rows with `current > target` | 0 | 268 | `Level.parse` ordering |
| **Effective level below target** (the project's rule) | **210** | 268 | `ledger.compute()` |
| … software targets (V2 or V3) below target | 89 | 147 | `ledger.compute()` |
| … hardware targets (V4) below target | 120 | 120 | `ledger.compute()` |
| … field target (V5) below target | 1 | 1 | `ledger.compute()` |
| Features with **no fresh passing** committed record | 198 | 268 | `ledger.compute()` |
| … stale-only (stale records exist, none fresh) | 96 | 268 | `ledger.compute()` |
| … no committed record of any kind | 102 | 268 | `ledger.compute()` |
| Features **capped at V1** by an open critical/high finding | 12 | 268 | `ledger.compute()` (`Finding.blocking`) |
| Features **at or above** target | 58 | 268 | `ledger.compute()` |
| … of those, without a fresh passing record | 16 | 268 | `ledger.compute()` |
| Features **above** target (over-achievement) | 2 | 268 | `ledger.compute()` |
| Features with fresh **failing** evidence | 0 | 268 | `ledger.compute()` |
| Finding register rows parsed | 278 table rows → 263 unique IDs | — | `parse_register()` |
| Findings total (263 register IDs + 2 pending rows) | 265 | — | `load_findings()` |
| **Parser-open findings** | **61** (1 critical, 2 high, 31 medium, 27 low) | 265 | `load_findings()` |
| Closed findings | 204 | 265 | `load_findings()` |

The audit baseline recorded at `ac1dc745` (`REVIEW_BASELINE.json`) and the committed ledger (`docs/validation/LEDGER.md`, generated at `28fce729`) report **the same** 210 / 198 / 96 / 12 / 58 / 16 figures. This report's independent recomputation at `a07cf94` reproduces every one of them, and reproduces the audit's 227 *recorded* below-target figure. The baseline's own method note reads *"Read-only existing ledger.compute over committed evidence only; no gate(), check(), ledger generation, campaign or feature promotion"* — the same constraint this package was given.

### 3.3 Ordered levels, caps and over-achievement

| Level | Meaning (`tools/validate/model.py`) | Features at this effective level |
| --- | --- | ---: |
| V0 | Claimed | 18 |
| V1 | Unit | 122 |
| V2 | Simulated integration | 32 |
| V3 | End-to-end | 96 |
| V4 | Hardware | 0 |
| V5 | Field | 0 |

* **Caps.** Exactly **12** features are capped at V1, and all twelve are capped by the *same* open critical finding, **HIL-09**: `F-MTX-007, F-MTX-008, F-MTX-009, F-MTX-010, F-MTX-011, F-MTX-012, F-MTX-013, F-MTX-014, F-MTX-015, F-MTX-016, F-MTX-017, F-MTX-020`. Their twelve caps are **preserved**, not removed; nothing in this report removes a cap, and source presence cannot decide which commands the firmware answers (§4, HIL-09).
* **Two other parser-open findings are *blocking* but cap nothing.** `UC-18` (H) and `SEC-14` (H) are open critical/high rows, but **no registry feature links either of them**, so they produce zero caps. "12 capped" is therefore a statement about HIL-09 alone, not about the two other high-severity rows.
* **Over-achievement.** Two features have an **effective** level above their target because fresh passing evidence exists at a higher level than the registry recorded: `F-API-032` (recorded V2, target V2, effective V3, 1 fresh-pass record) and `F-API-040` (recorded V2, target V2, effective V3, 4 fresh-pass records). This is exactly the case the adoption notes warn about: `current != target` is not a below-target test once evidence moves a level. Both are counted in the 210 below-target figure as **not** below target, and both are **not** evidence that any larger population is complete.

### 3.4 Per-area and per-package reconciliation

| Area | Features | Effective below target | Recorded below target | No fresh passing record |
| --- | ---: | ---: | ---: | ---: |
| Matrix control | 31 | 31 | 31 | 25 |
| CEC control | 11 | 11 | 11 | 8 |
| REST/WebSocket contract | 42 | 24 | 25 | 26 |
| Domain features | 36 | 25 | 32 | 19 |
| Web UI | 36 | 24 | 25 | 30 |
| Kiosk | 14 | 7 | 8 | 11 |
| Remote 3 integration | 17 | 17 | 17 | 9 |
| Home Assistant component | 18 | 18 | 18 | 18 |
| Flic | 10 | 3 | 10 | 3 |
| Deployment, configuration, persistence | 20 | 20 | 20 | 20 |
| Security controls | 15 | 12 | 12 | 14 |
| Reliability | 18 | 18 | 18 | 15 |
| **All** | **268** | **210** | **227** | **198** |

| Package | Phase | Features | Published `below_target` | Published `without_fresh_passing…` | Recomputed below target | Recomputed no-fresh | Match |
| --- | --- | ---: | ---: | ---: | ---: | ---: | :---: |
| SW-AUDIT | P0 | 0 | 0 | 0 | 0 | 0 | yes |
| SW-FINDINGS | P0 | 0 | 0 | 0 | 0 | 0 | yes |
| SW-HARNESS | P0 | 0 | 0 | 0 | 0 | 0 | yes |
| SW-API-READ | P1 | 10 | 0 | 2 | 0 | 2 | yes |
| SW-SEC-AUTH | P1 | 8 | 6 | 7 | 6 | 7 | yes |
| SW-API-WRITE | P1 | 20 | 13 | 14 | 13 | 14 | yes |
| SW-SEC-DATA | P1 | 7 | 6 | 7 | 6 | 7 | yes |
| SW-API-CLIENT | P1 | 12 | 11 | 10 | 11 | 10 | yes |
| SW-DOM-PROFILE | P1 | 7 | 6 | 6 | 6 | 6 | yes |
| SW-DOM-SCENE | P2 | 6 | 1 | 1 | 1 | 1 | yes |
| SW-DOM-MACRO | P2 | 3 | 3 | 3 | 3 | 3 | yes |
| SW-DOM-SHORTCUT | P2 | 8 | 3 | 3 | 3 | 3 | yes |
| SW-DOM-PRESENT | P2 | 6 | 6 | 6 | 6 | 6 | yes |
| SW-UI-CONTROL | P2 | 14 | 7 | 11 | 7 | 11 | yes |
| SW-UI-MANAGE | P2 | 12 | 8 | 9 | 8 | 9 | yes |
| SW-UI-PRESENT | P2 | 10 | 9 | 10 | 9 | 10 | yes |
| SW-KIOSK-CONTROL | P2 | 7 | 4 | 6 | 4 | 6 | yes |
| SW-KIOSK-STATE | P2 | 7 | 3 | 5 | 3 | 5 | yes |
| SW-FLIC | P2 | 10 | 3 | 3 | 3 | 3 | yes |
| SW-PROTOCOL-PREP | P3 | 42 | 42 | 33 | 42 | 33 | yes |
| SW-RUNTIME-PREP | P3 | 37 | 37 | 34 | 37 | 34 | yes |
| SW-UC-PREP | P3 | 17 | 17 | 9 | 17 | 9 | yes |
| SW-HA-PREP | P3 | 18 | 18 | 18 | 18 | 18 | yes |
| SW-DOM-HIL-PREP | P3 | 6 | 6 | 0 | 6 | 0 | yes |
| SW-SOAK-PREP | P3 | 1 | 1 | 1 | 1 | 1 | yes |
| SW-REPO | P4 | 0 | 0 | 0 | 0 | 0 | yes |
| SW-DOCS | P4 | 0 | 0 | 0 | 0 | 0 | yes |
| SW-VERSION | P4 | 0 | 0 | 0 | 0 | 0 | yes |
| SW-BUILD | P4 | 0 | 0 | 0 | 0 | 0 | yes |
| SW-SOFTWARE-GATE | P5 | 0 | 0 | 0 | 0 | 0 | yes |

All **30** package aggregates reproduce exactly at this base. **Seven** packages carry zero features (`SW-AUDIT`, `SW-FINDINGS`, `SW-REPO`, `SW-DOCS`, `SW-VERSION`, `SW-BUILD`, `SW-SOFTWARE-GATE`): they are cross-cutting or gate packages and carry no per-feature count.

### 3.5 Unknown policy

* **Unknown is a value, not a zero.** A feature with no committed record of any kind is reported as *no record* (102 features), not as *failed* and not as *passing*.
* **Stale is distinct from missing and from failing.** A stale record is evidence that existed and whose covered paths changed afterwards; it is neither current proof nor absence of proof.
* **A missing status is not an exit.** No record was read as "the work did not happen".
* **Raw CI evidence is not canonical freshness.** The audit found that 1,536 CI validation/HA/deployment records name a synthetic PR merge commit (`c9dac37abccbe66cfed383379c44cf6061cbc787`) that is not an ancestor of the branch head, although the two full file trees are identical. Those records are **not** counted as fresh canonical proof here, and **green CI is not closure**.
* **A merged PR is not a feature acceptance.** Merge evidence is not relabelled as proof.
* **Historical negative judgements stay negative.** Failed qualification attempts, terminal privacy FAILs, lost original bytes and the conditional disconnect reproduction limit are preserved as recorded.

## 4. The 61 parser-open findings

### 4.1 The parser set, recomputed at this base

`tools.validate.registry.load_findings()` at `a07cf94` returns **265** findings, of which **61** are open: **59** rows from the `docs/REMEDIATION_PLAN.md` §4 register tables plus **2** rows from `docs/validation/findings_pending.yaml` (`VAL-14`, `VAL-15`). This is the same 61 as the dated figure, and it is the same population: `docs/REMEDIATION_PLAN.md`, `docs/validation/findings_pending.yaml` and `docs/validation/features.yaml` are all **byte-identical** between the accepted triage base `3602a4e` and this base (`git diff --stat` empty for all three), and the intersection of the historical 59 with the current 59 is exactly the historical 59. No finding was added or removed.

Severity distribution of the 61 (as recorded by the parser): **1 critical, 2 high, 31 medium, 27 low**. These are **recorded severities**, not live-defect counts.

**Dispositions used below.** Each ID gets one of five recommendations:

| Recommendation | Meaning |
| --- | --- |
| **resolved** | the original register condition is met in current source and the accepted evidence path records it; only coordinator register-text reconciliation remains |
| **partial** | some elements are resolved and a residual remains (with an accepted owner-set direction or an independent closeout still owed) |
| **reproduce** | source presence only — the behaviour was **not** exercised here; a bounded reproduction is the next step |
| **hardware** | requires physical HIL / real Remote / real SDK observation |
| **owner** | requires an explicit owner action or decision |

**Strength labels.** *re-verified* means I re-read the cited source at this base. *inherited* means the disposition is carried from the accepted SW-FINDINGS-01 triage (accepted as triage only, with limits) and was **not** re-qualified here — unchanged bytes renew no acceptance.

### 4.2 Disposition table for all 61 parser-open IDs

| ID | Sev | Original assertion (register §4, verbatim) | Surviving condition at `a07cf94` | Current source / client / image / proof reference and ancestry | Assertion strength | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| **BE-14** | M | Output-side CEC uses the input command table/indices; captures show a different output table | Source uses the device web interface's 0-based output CEC table; the row stays open until a live CEC run on real hardware answers it. The simulator/fresh API evidence bound to the linked features proves the hub code path, not the television's reaction. | src/cec_commands.py, src/orei_matrix.py (unchanged between 3602a4e and a07cf94); linked features F-CEC-* carry 9 fresh-pass and 59 stale evidence records at their own evidence commits; register row docs/REMEDIATION_PLAN.md §4.1 line 117; linked features: F-CEC-005, F-CEC-006, F-UC-007, F-FLIC-005; fresh-pass example docs/validation/evidence/ev02-original-api/F-CEC-005/2026-10-19-V2-1baac3de-cec.output_power_on-api.json @ 1baac3dec660 (api V2); stale records: 59 | re-verified: product source unchanged in the scoped diff; fresh proof is simulator/client level, not physical CEC | **hardware** |
| **BE-15** | M | Audio-only detection uses scaler==4; docs and setter say 5 | The original assertion (scaler==4 vs docs/setter 5) is stale in source: detection reads device code 4 and the setter maps API 5 to device 4. The *write* still depends on the HIL-09 hardware proof, so the row cannot be closed by source reading. | src/device_codes.py:7-11 (the file header states that scaler 0 is pass-through and scaler 4 is audio-only in the Telnet status dump); src/orei_matrix.py; linked features carry 88 fresh-pass records at their evidence commits; linked features: F-MTX-011, F-CEC-011; fresh-pass example docs/validation/evidence/ev02-original-api/F-CEC-011/2026-10-19-V2-1baac3de-cec_caps.all_pattern_0-api.json @ 1baac3dec660 (api V2); stale records: 99 | re-verified at this base: source mapping confirmed by reading the file; device read is a captured observation, the write is not proven here | **hardware** |
| **BE-16** | M | Two name stores (driver vs REST); web renames never reach UC; failed name query rebuilds entities with generic names; stale `configured_entities` | Inherited accepted disposition: the two-name-store defect was resolved in source by the recorded WP-C2 work. Register text has not been reconciled. | src/driver.py, src/rest_api/utils.py; linked features carry 7 fresh-pass and 19 stale records; inherited from docs/production/software-waves/SW-FINDINGS-01/execution-20261101/AUTHOR.md §6 (blob f09c3336, byte-identical at HEAD); linked features: F-MTX-005, F-MTX-022, F-MTX-023, F-API-018, F-DOM-032, F-UC-016; fresh-pass example docs/validation/evidence/runtime-r8b/F-MTX-005/2026-10-19-V2-1baac3de-presets.rename-api.json @ 1baac3dec660 (api V2); stale records: 19 | inherited triage (accepted as triage only, with limits); register row byte-identical since the accepted triage base and product source outside the scoped diff unchanged - NOT re-qualified here | **resolved** |
| **BE-20** | M | `src/integrations/unfolded_circle` unused parallel path (to be **finished** per D4); adapter maps `current_input` into `allconnect` | src/integrations/unfolded_circle remains an unwired parallel integration path; run.py contains no reference to it, so the D4 'finish the integration framework' work is still outstanding. | src/integrations/{__init__.py,unfolded_circle/{__init__.py,api_client.py,entities.py}}; api_client.py is 5285 bytes at this base; linked feature has 0 fresh-pass and 2 stale records; linked features: F-OPS-011; stale records: 2 | re-verified: the path exists and is unreferenced by run.py (absence of a reference is not proof of deadness elsewhere) | **partial** |
| **BE-22** | L | Entity creation duplicated 3×, `cec_sender` closure 2× | Both original elements of the condition (entity creation duplicated 3x; cec_sender closure 2x) remain unverified: the cited driver.py ranges 516-590 and 1553-1598 contain no entity-creation or cec_sender code, and cec_sender appears once as an import and once as a single top-level async definition. | src/driver.py (103001 bytes at this base) cec_sender at lines 79 (import), 642 (def), 643 (docstring); no `window`/entity-factory equivalent reproduces the accepted 'single factory' wording, and a name absence is not an architectural conclusion | re-verified at this base; inherited `R` label is explicitly not inherited (neither R nor P) | **reproduce** |
| **BE-23** | L | Dead code: unused `DriverState` fields, non-existent entity IDs in `on_matrix_connected`, `handle_exit_signal`, duplicate `get_ext_audio_status`, `route_input_to_all_outputs`, 38 per-command CEC wrappers, `_push_buffer`, unwired `on_status_update`, `Events.RECONNECTING`, `_reconnect_task`; `ConnectionError` shadows builtin; shallow-copy default CEC config | Inherited accepted disposition: dead-code cleanup (unused DriverState fields, 38 per-command CEC wrappers, unwired on_status_update, RECONNECTING event, _reconnect_task, ...) was resolved in source; register text has not been reconciled. | src/driver.py, src/orei_matrix.py, src/telnet_client.py, src/config.py; inherited from docs/production/software-waves/SW-FINDINGS-01/execution-20261101/AUTHOR.md §6 | inherited triage (accepted as triage only, with limits); not re-qualified here | **partial** |
| **BE-24** | L | MediaPlayer state not updated by poller; first poll broadcasts `signal_change` for every active input | Inherited accepted disposition: the WebSocket half was fixed (a first reading is not announced as a change and the driver no longer broadcasts); the MediaPlayer poller state remains with Phase 4. | src/driver.py poller; linked features carry 6 fresh-pass and 13 stale records; inherited from SW-FINDINGS-01 §6; linked features: F-API-040, F-UC-009; fresh-pass example docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.display_unplugged-browser.json @ 1baac3dec660 (browser V3); stale records: 13 | inherited triage; the recorded /ws half is accepted prose, the MediaPlayer-state element is not re-verified here | **partial** |
| **BE-25** | L | `copy_edid_from_output` uses `set input edid` 14+N; docs describe `copy edid` | Inherited accepted disposition: copy is `set edid` 39+N (web-UI-derived); `copy edid` and `set input edid 14+N` get no answer. The write proof depends on HIL-09. | src/orei_matrix.py:2809 and :2872 carry the recorded 'no copy edid' comments, :2852 and :2865 build the `set edid` command; across src/ `copy_edid_from_output` occurs 2 times (src/orei_matrix.py:2868, src/rest_api/outputs.py:337) and `edid_copy_from_output` 6 times; linked feature has 0 fresh-pass and 11 stale records; linked features: F-MTX-014; stale records: 11 | re-verified at this base by reading the command construction; the physical behaviour is still unproven here | **hardware** |
| **BE-26** | L | Hard-coded default host `192.168.0.100`; ~62 `range(1, 9)` / `[0]*8` | The hard-coded default host and the hard-coded 1..8 range are still present in source; only the register's numeric figures are wrong. | src/hub/cli.py:54 `DEFAULT_MATRIX_HOST = "192.168.0.100"`; `range(1, 9)` occurs 68 times across 18 files under src/ and 13 times across 5 files under src/hub/; the literal `[0] * 8` occurs once (src/orei_matrix.py:1616); linked feature has 0 fresh-pass and 1 stale record; linked features: F-OPS-006; stale records: 1 | re-verified at this base by counting; the register's '~62 range(1, 9) / [0]*8' and the accepted '35x in src' figures are both unverified/approximate | **partial** |
| **BE-33** | L | With the Remote integration on, two pollers read the matrix: the hub's event stream and the driver's entity poller (`POLLING_INTERVAL`). They share the status caches (a `get video status` read by the driver now refreshes the cache the hub reads), but the driver should consume the hub's view instead of polling on its own (found in WP-C2) | Inherited accepted disposition: the driver still polls on its own POLLING_INTERVAL while the hub also holds the shared status caches; the driver should consume the hub's view. | src/driver.py status_polling_loop, src/rest_api/events.py; inherited from SW-FINDINGS-01 §6 | inherited triage; not re-qualified here | **partial** |
| **API-07** | M | LCD timeout mode map in shortcuts contradicts device mapping ("Always on" sets 60 s) | The shortcut map uses the device codes (0 off, 1 always, 2/3/4 = 15/30/60 s); the old {"time": N} payload is rejected and the hub sends {"lcd on time": N}. The label was renamed 'LCD: 15s' in WP-C1 and proven by scenario shortcuts.lcd_15s. The row's own close condition is an explicit owner approval of the affected catalogue visual diff. | src/orei_matrix.py:2755-2780 (LCD_TIMEOUT_MODES = dict(DEVICE_LCD_MODES); set_lcd_timeout sends the value under the key "lcd on time"), src/rest_api/audio.py:365-400 (handle_lcd_timeout_modes / handle_set_lcd_timeout); the register's own location anchors (system_shortcuts.py:22-34 vs orei_matrix.py:1972) are historical and carry no LCD map at this base; linked features carry 12 fresh-pass and 35 stale records; register row docs/REMEDIATION_PLAN.md §4.2 line 153; linked features: F-MTX-020, F-DOM-028; fresh-pass example docs/validation/evidence/runtime-r8b/F-DOM-028/2026-10-19-V2-1baac3de-shortcuts.lcd_15s-api.json @ 1baac3dec660 (api V2); stale records: 35 | re-verified at this base for the register condition; the owner-approval element is an owner action, not a source defect | **owner** |
| **API-12** | M | v1 and v2 scenes share `scenes.json` with different schemas; profile "migration" can ingest v2 scenes | Inherited accepted disposition: the v1/v2 scenes.json schema split and the profile 'migration' that can ingest v2 scenes were resolved in source; register text has not been reconciled. | src/scene_manager.py:28 (the file exists at this base, 967 lines), src/config.py:221,486; linked features carry 1 fresh-pass and 133 stale records; inherited from SW-FINDINGS-01 §6; linked features: F-API-020, F-DOM-009, F-DOM-010, F-DOM-018, F-OPS-017; fresh-pass example docs/validation/evidence/runtime-r8b/F-DOM-002/2026-10-19-V2-1baac3de-profile_state.alias_recall-api.json @ 1baac3dec660 (api V2); stale records: 133 | inherited triage; not re-qualified here | **resolved** |
| **API-16** | L | `sys.path.insert` on every request (9 handlers) | Inherited accepted disposition: the nine `sys.path.insert` handlers were resolved; register text has not been reconciled. | src/rest_api/{audio.py,outputs.py,cec.py}; inherited from SW-FINDINGS-01 §6 | inherited triage; not re-qualified here | **resolved** |
| **API-18** | L | `config.SceneManager` (v1) dead | Inherited accepted disposition: config.SceneManager (v1) was resolved as dead code; register text has not been reconciled. | src/config.py, src/rest_api/utils.py:388-395; inherited from SW-FINDINGS-01 §6 | inherited triage; not re-qualified here | **resolved** |
| **API-19** | M | Three divergent "apply profile" paths (recall handler, scene executor, shortcut executor) | Inherited accepted disposition: the three divergent 'apply profile' paths were resolved in source (run_rest_action is present twice in src/rest_api/control.py at this base); register text has not been reconciled. | src/rest_api/control.py (run_rest_action x2) and src/rest_api/profiles.py (run_rest_action x2); linked feature carries 6 fresh-pass and 17 stale records; inherited from SW-FINDINGS-01 §5; linked features: F-DOM-002; fresh-pass example docs/validation/evidence/runtime-r8b/F-DOM-002/2026-10-19-V2-1baac3de-profile_state.alias_recall-api.json @ 1baac3dec660 (api V2); stale records: 17 | re-verified at this base that the cited source is present; unchanged bytes support source presence only and renew no acceptance | **resolved** |
| **API-20** | M | Dashboard layout claims to be source of truth, but 5 entity types carry their own favorite/dashboard flags; deletes orphan cards | Inherited accepted disposition: dashboard layout as source of truth versus the five entity types with their own favourite/dashboard flags was resolved in source; register text has not been reconciled. | src/rest_api/dashboard_layout.py and the managers; linked features carry 0 fresh-pass and 31 stale records; inherited from SW-FINDINGS-01 §6; linked features: F-API-025, F-DOM-006, F-DOM-022, F-DOM-030, F-DOM-031, F-UI-009; stale records: 31 | inherited triage; not re-qualified here | **resolved** |
| **API-21** | L | Two response envelope implementations (sync `_json_response` vs async in `scenes_v2`) | Inherited accepted disposition: the two response-envelope implementations were resolved; register text has not been reconciled. | src/rest_api/utils.py, src/rest_api/scenes_v2.py; linked feature has 0 fresh-pass and 1 stale record; inherited from SW-FINDINGS-01 §6; linked features: F-API-022; stale records: 1 | inherited triage; not re-qualified here | **resolved** |
| **API-25** | M | Profile CEC targets have two formats: `config.CecConfig` documents (and its tests use) `"input:3"`, the resolver, CEC macros and the web UI use `"input_3"`, and the hub validates neither; the e2e fixture profile uses the colon form, which the CEC dialog shows as "Output NaN". Found in WP-E1 | The original condition has two elements: two CEC target formats in use, and 'the hub validates neither'. Element 1 still holds in the inspected scope; element 2 holds only partially, because _validate_cec_config checks known fields, string arrays and the auto_resolved boolean but not target syntax in that function. | src/rest_api/profiles.py:192 `_validate_cec_config`, called at :516; `input_` x4 and `input:` x0 in that file; the colon form appears in src/config.py and src/rest_api/static.py; register row §4.2 line 171 | re-verified at this base; the accepted `R` label does not meet the register's stated condition, so this stays a scoped source-inspection lead and not a resolution | **reproduce** |
| **PER-04** | M | No `schema_version` / migration framework for persisted JSON | Inherited accepted disposition: a schema_version / migration framework for persisted JSON was resolved in source; register text has not been reconciled. | all managers; linked feature has 0 fresh-pass and 0 stale records; inherited from SW-FINDINGS-01 §6; linked features: F-OPS-017 | inherited triage; not re-qualified here | **resolved** |
| **SEC-14** | H | Vendor firmware, `XP3.exe`, Control4/RTI drivers, and copyrighted manual committed (public) since the first commit; LICENSE is a stub | The register's element 'LICENSE is a stub' is obsolete at this base: LICENSE is the full Mozilla Public License 2.0. The vendor-firmware/manual element was purged from the tracked tree; the remaining owner action (GitHub-Support cache purge of public history) is unchanged. No legal conclusion is drawn here. | LICENSE (16726 bytes, contains 'Mozilla Public License', contains no 'stub'); no tracked .exe/.pdf and no docs/BK-808* payload at this base (only tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/http/*.json HTTP capture fixtures); register row §4.3 line 200; inherited from SW-FINDINGS-01 §5 | re-verified at this base for the licence clause and the tracked-tree absence; the public-history purge verification is inherited and was not re-run (no exhaustive history or secret-scan authority); no credentials, raw validation, image or archive payload read | **owner** |
| **SEC-15** | L | gitleaks configured but never run; CI actions tag-pinned; base image not digest-pinned | Both register clauses are obsolete at this base: gitleaks is configured and runs in CI, all 42 `uses:` entries are SHA-pinned (0 tag-pinned), and the external base image is digest-pinned. | .github/workflows/ci.yml: all 42 `uses:` values match a 40-hex SHA; Dockerfile:1 `FROM python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1` (other FROM lines are internal stages); register row §4.3 line 201; inherited from SW-FINDINGS-01 §5 | re-verified at this base by reading the workflow and Dockerfile; source declaration only, no fresh CI run is claimed here | **resolved** |
| **DEP-05** | M | CI: no `pull_request` trigger; ruff only on `src/`; mypy non-blocking; no hassfest/HACS validation; no gitleaks; QEMU set up but no multi-arch platforms | The register's cited workflow file no longer exists (only ci.yml is tracked) and four of its five clauses are obsolete: ci.yml has pull_request/push/workflow_dispatch triggers, hassfest, hacs and gitleaks jobs, and the ruff step iterates six separate candidate paths rather than src/ only. The mypy 'non-blocking' clause is not reproducible from the declared job: the four continue-on-error occurrences (lines 450, 454, 459, 527) are not on the typecheck mypy step. | .github/workflows/ci.yml (only tracked workflow); triggers at the top of the file; job names lint, typecheck, test, uc, ha-test, hassfest, hacs, hygiene, gitleaks, docker-build, ui, ui-comment, validation, validation-ha, publish; ruff loop at ci.yml:51-60; register row §4.5 line 232; inherited from SW-FINDINGS-01 §5 | re-verified at this base by reading the workflow; source declaration only - no fresh CI result and no multi-arch build claim | **resolved** |
| **DEP-07** | M | Env-var surface inconsistent: `API_PORT` vs `REST_API_PORT`, `MATRIX_HOST` ignored in default mode, `WEBUI_ENABLED` no-op, `USE_MODULAR` | Inherited accepted disposition with a surviving element: run.py reads one set of env names and warns the old names as aliases, but with the UC integration enabled driver.py takes the matrix address from the Remote setup rather than MATRIX_HOST. | run.py, src/driver.py:60; linked features carry 0 fresh-pass and 5 stale records; inherited from SW-FINDINGS-01 §6; linked features: F-OPS-006, F-OPS-007, F-OPS-011, F-OPS-015; stale records: 5 | inherited triage; the surviving element is source presence only and was not re-verified here | **partial** |
| **TST-03** | M | No tests: `/api/v2/scenes*`, `/api/integrations`, `/api/settings`, `_task_supervisor`, UC setup handler, poller, WS broadcast/state push, `api_client`/`entities` | The register's 'no tests' list is substantially obsolete at this base: the named surfaces now appear in the test tree (api/v2/scenes 151 occurrences, /api/integrations 91, /api/settings 40, _task_supervisor 7). Occurrence counts are not behavioural proof, so the claim 'these surfaces have no tests' is stale while 'these surfaces have adequate assertions' is not established here. | tests/ tree; linked features carry 2 fresh-pass and 48 stale records; register row §4.6 line 248; linked features: F-API-021, F-API-027, F-API-028, F-OPS-012; fresh-pass example docs/validation/evidence/ev02-original-api/F-API-028/2026-10-19-V2-1baac3de-contracts.flic_buttons-api.json @ 1baac3dec660 (api V2); stale records: 48 | re-verified at this base by counting occurrences; counts are identity/coverage hints, not semantic coverage - no assertion strength was reviewed per surface | **reproduce** |
| **TST-04** | M | No JS tests of any kind | The register's 'No JS tests of any kind' is obsolete in its literal form: the repository carries Playwright end-to-end specifications (tests/e2e/*.spec.ts, playwright.config.ts). There are still no JavaScript unit-test files under tests/ outside tests/e2e (0 .js/.mjs/.ts files). | tests/e2e/{smoke,flows,c4-flows,kiosk-security,security-auth}.spec.ts + playwright.config.ts; 0 JS/TS unit-test files outside tests/e2e; register row §4.6 line 249 | re-verified at this base by file inventory; the presence of e2e specs is not proof that the named product behaviours are asserted | **reproduce** |
| **UI-05** | M | New settings drawers drive a hidden legacy `#settings-modal` via synthetic `change` events | Inherited accepted disposition: the new settings drawers no longer drive the hidden legacy #settings-modal via synthetic change events; register text has not been reconciled. | web/js/components/hardware-drawer.js (the register's 145-178 anchor now carries form forwarding comments, not the synthetic-change mechanism), general-drawer.js, interface-drawer.js, web/index.html:352-598 (the register's anchors are historical); linked features carry 0 fresh-pass records; inherited from SW-FINDINGS-01 §6; linked features: F-UI-019, F-UI-020, F-UI-021 | inherited triage; not re-qualified here | **resolved** |
| **UI-06** | M | Keyboard shortcuts broken (`scenes` tab id, `window.settingsPanel` never set) | Both elements of the condition still hold in source at this base: shortcut '4' still targets `[data-tab="scenes"]` (web/js/components/keyboard-shortcuts.js:34) and the application exposes no such top-level tab (web/index.html data-tab values are dashboard, matrix, inputs, outputs, profiles plus drawer-local general/hardware/interface), and shortcut 's' still tests `window.settingsPanel` (keyboard-shortcuts.js:42-43) while no file under web/ assigns `window.settingsPanel =` (0 matches). | web/js/components/keyboard-shortcuts.js:34,42,43; web/index.html data-tab inventory; linked feature has 0 fresh-pass records; register row §4.7 line 275; also re-confirmed independently as CR-03 in docs/audits/COMPREHENSIVE_PROJECT_REVIEW_20261104.md; linked features: F-UI-028 | re-verified at this base by reading the handler and the DOM identifiers; no browser behaviour was executed - this is a source-confirmed wiring defect, not a full browser acceptance | **reproduce** |
| **UI-07** | M | Accessibility: 27 independent Escape listeners; few `role="dialog"`/`aria-modal`; focus trap missing on 9+ overlays; kiosk has no ARIA and `div onclick` tiles; `user-scalable=no`; 22 px hover-only preset actions; one reduced-motion rule | Inherited accepted disposition: the accessibility condition (27 Escape listeners, missing role=dialog/aria-modal, missing focus traps, kiosk ARIA, user-scalable=no, hover-only actions) was NOT reproduced in this inventory and is not a current confirmed defect; it remains a source-inspection candidate. | web/ (many files); linked features carry 0 fresh-pass records; inherited from SW-FINDINGS-01 §6; linked features: F-UI-029, F-KIO-014 | inherited triage as source-presence only; behaviour not exercised - NOT a current reproduced defect | **reproduce** |
| **UI-08** | M | Dashboard config in two stores (localStorage key still live after "migration"); kiosk pins localStorage-only | Inherited accepted disposition: the two dashboard-config stores and the localStorage-only kiosk pins were resolved in source; register text has not been reconciled. | web/js/app.js (the register's 74-78 anchor now shows a favourites loop), web/js/utils/dashboard-manager.js (1215 lines; the register's 71/1102/1126 anchors are historical), web/kiosk.html:2164; linked features carry 0 fresh-pass and 2 stale records; inherited from SW-FINDINGS-01 §6; linked features: F-DOM-031, F-UI-009, F-KIO-006, F-KIO-012; stale records: 2 | inherited triage; not re-qualified here | **resolved** |
| **UI-09** | M | ~2,800 lines of dead JS: `quick-actions-drawer.js`, `floatable.js`, `presets-panel.js`, `system-shortcuts-panel.js`, `about-dialog.js`, `setup-wizard.js`, `empty-state.js`, `context-menu.js` (mostly), `settings-panel.js` + hidden modal | The register's nine named dead-JS files are all present at this base, so the register text is not a file-absence claim; 'dead' is a behaviour claim that was not reproduced. The historical ~2,800-line figure was not re-measured here. | web/js/components/{quick-actions-drawer,presets-panel,system-shortcuts-panel,about-dialog,setup-wizard,empty-state,context-menu,settings-panel}.js and web/js/utils/floatable.js; linked feature has 0 fresh-pass records; register row §4.7 line 278; inherited from SW-FINDINGS-01 §5; linked features: F-UI-036 | re-verified at this base for file presence; file presence is not evidence of deadness and no dead-code behaviour was exercised | **reproduce** |
| **UI-10** | L | 15-25% of ~12k CSS lines unused; `components.css` is 6.8k lines | Inherited accepted disposition: the unused-CSS fraction and the components.css size are a source-inspection candidate whose behaviour was not reproduced; not a current confirmed defect. | web/css/; register row §4.7 line 279; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-11** | M | Kiosk is a parallel app (own API client, WS, theme, CEC remote, `escapeHtml`) | Inherited accepted disposition: the kiosk-as-parallel-app condition (own API client, WS, theme, CEC remote, escapeHtml) is a source-inspection candidate whose behaviour was not reproduced; not a current confirmed defect. | web/kiosk.html:1464-2754; register row §4.7 line 280; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-12** | M | Duplication: two trackpads in `cec-tray.js`, two render paths in `routing-drawer.js` | Inherited accepted disposition: the two trackpads in cec-tray.js and the two render paths in routing-drawer.js are a source-inspection candidate whose behaviour was not reproduced. | web/js/components/cec-tray.js (the register's 1468-1580 anchor is beyond this base's file) and web/js/components/routing-drawer.js (the 59-95/385-437 anchors now show render methods); linked feature has 0 fresh-pass records; register row §4.7 line 281; inherited from SW-FINDINGS-01 §6; linked features: F-UI-017 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-13** | L | No module system: ~50 ordered `<script>` tags, `window.*` globals | The '~50 ordered <script> tags' figure is approximate: there are exactly 53 <script tags and 0 type="module" tags in web/index.html at this base. | web/index.html (53 <script, 0 module); register row §4.7 line 282; inherited from SW-FINDINGS-01 §5 | re-verified at this base by counting tags; the absence of a module system is a source fact, the architectural consequence is not re-derived here | **partial** |
| **UI-14** | L | Three generations of settings UI; nine separate right-side drawers | Inherited accepted disposition: the three generations of settings UI and the nine right-side drawers are a source-inspection candidate whose behaviour was not reproduced. | web/js/components/side-nav-drawer.js and the drawers; register row §4.7 line 283; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-15** | L | `overlay-manager` hard-codes drawer list including dead `quick-actions-drawer` | Inherited accepted disposition: overlay-manager hard-coding a drawer list that includes the dead quick-actions-drawer is a source-inspection candidate whose behaviour was not reproduced. | web/js/utils/overlay-manager.js (303 lines; the register's 35-46 anchor is historical); register row §4.7 line 284; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-16** | L | `tron-background.js` redraws every frame with heavy `shadowBlur`; no reduced-motion check | The register text's 'no reduced-motion check' clause is obsolete at this base: web/js/tron-background.js contains 2 prefers-reduced-motion references, this.maxFps = 30, and setShadowBlur() with a 4 px low-power cap. The Phase column's WP-E2 claims are source-confirmed. The two residual items named in the Phase cell (render only while the cycles move; lazy-load the editors) were not verified here. | web/js/tron-background.js (39882 bytes; maxFps at :56-57, isPausedForReducedMotion and setShadowBlur present); register row §4.7 line 286; inherited from SW-FINDINGS-01 §5; linked features: F-UI-032 | re-verified at this base for the reduced-motion/fps/blur-cap clauses; the two residual items remain unverified - not a closure | **partial** |
| **UI-18** | L | `api-copy.js` hard-codes `http://host:8080` | Inherited accepted disposition: api-copy.js hard-coding http://host:8080 is a source-inspection candidate whose behaviour was not reproduced. | web/js/utils/api-copy.js (437 lines; the register's :13 anchor is historical); linked feature has 0 fresh-pass records; register row §4.7 line 287; inherited from SW-FINDINGS-01 §6; linked features: F-UI-035 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-19** | L | `scene-editor` uses `prompt()` for step targets | Inherited accepted disposition: scene-editor using prompt() for step targets is a source-inspection candidate whose behaviour was not reproduced. | web/js/components/scene-editor.js (the register's 263-278 anchor now carries scene-template markup, not a prompt() call); linked feature has 0 fresh-pass records; register row §4.7 line 288; inherited from SW-FINDINGS-01 §6; linked features: F-UI-015 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-20** | L | `about-dialog`/`integrations-drawer` call `fetch` directly | Inherited accepted disposition: about-dialog / integrations-drawer calling fetch directly is a source-inspection candidate whose behaviour was not reproduced. | register row §4.7 line 289 (register location cell is '-'); inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-21** | L | PWA manifest marked done in plan, not present | Inherited accepted disposition: the PWA manifest marked done in the plan but not present is a source-inspection candidate whose behaviour was not reproduced. | web/; register row §4.7 line 290; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-33** | L | Phone (390 px): matrix grid view clips the last column; kiosk footer and edit bar clip | Inherited accepted disposition: the 390 px matrix-grid clipping and the kiosk footer/edit-bar clipping are a source-inspection candidate whose behaviour was not reproduced; they are not current confirmed defects. | web/css/responsive.css, web/kiosk.html; linked feature has 0 fresh-pass records; register row §4.7 line 302; inherited from SW-FINDINGS-01 §6; linked features: F-UI-033 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-34** | L | Kiosk ignores the theme presets (always Tron Classic) | Inherited accepted disposition: the kiosk ignoring the theme presets is a source-inspection candidate whose behaviour was not reproduced. | web/kiosk.html; linked feature has 0 fresh-pass records; register row §4.7 line 303; inherited from SW-FINDINGS-01 §6; linked features: F-KIO-013 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-35** | M | axe: `aria-required-parent` on desktop tabs, unlabeled tab-pin checkboxes, `aria-hidden-focus` in closed drawers, unnamed tooltip, kiosk `color-contrast` ×22, zoom disabled | Inherited accepted disposition: the listed axe findings (aria-required-parent on desktop tabs, unlabeled tab-pin checkboxes, aria-hidden-focus in closed drawers, unnamed tooltip, kiosk color-contrast x22, zoom disabled) are a source-inspection candidate whose behaviour was not reproduced in this inventory. | web/index.html, web/kiosk.html; linked features carry 0 fresh-pass records; register row §4.7 line 304; inherited from SW-FINDINGS-01 §6; linked features: F-UI-029, F-KIO-014 | inherited triage as source-presence only; axe was not run here | **reproduce** |
| **UI-36** | L | Passcode prompt is a native `window.prompt()` (unstyled, can't be captured) | Inherited accepted disposition: the native window.prompt() passcode prompt is a source-inspection candidate whose behaviour was not reproduced. | web/js/components/settings-drawer.js, web/js/components/dashboard-manager.js; linked feature carries 3 fresh-pass and 6 stale records; register row §4.7 line 305; inherited from SW-FINDINGS-01 §6; linked features: F-UI-014; fresh-pass example docs/validation/evidence/runtime-r8b/F-DOM-005/2026-10-19-V3-1baac3de-profiles.recall_needs_passcode-browser.json @ 1baac3dec660 (browser V3); stale records: 6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-38** | M | Kiosk output-status footer grows sideways with long names and runs off the right edge (iPhone: columns 3–4 and 7–8 hidden; Tab A11: OUT 8 hidden) | Inherited accepted disposition: the kiosk output-status footer growing sideways with long names is a source-inspection candidate whose behaviour was not reproduced. | web/kiosk.html routing/presets long-names states; register row §4.7 line 306; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-39** | M | iPhone kiosk: header title and "Edit Layout" button wrap to two lines; the edit-mode "DEFAULT TAB" strip runs to the edge with no padding | Inherited accepted disposition: the iPhone kiosk header/Edit-Layout wrapping and the edit-mode DEFAULT TAB strip is a source-inspection candidate whose behaviour was not reproduced. | web/kiosk.html edit-mode/profiles/toast states; register row §4.7 line 307; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-40** | L | iPhone kiosk profile wizard: "Keep Unchanged" dropdowns clipped | Inherited accepted disposition: the clipped iPhone kiosk profile-wizard 'Keep Unchanged' dropdowns are a source-inspection candidate whose behaviour was not reproduced. | web/kiosk.html profile-wizard/step-2; register row §4.7 line 308; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-41** | M | iPhone matrix grid: input row labels clipped on the left, output headers truncated, last column flush to the edge (related to UI-33) | Inherited accepted disposition: the clipped iPhone matrix-grid labels/truncation (related to UI-33) is a source-inspection candidate whose behaviour was not reproduced. | web matrix/grid/* iPhone states; register row §4.7 line 309; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UI-42** | L | Tab A11 kiosk routing modal uses the full 800 px height with almost no margin (will clip if the confirmed viewport is shorter) | Inherited accepted disposition: the Tab A11 kiosk routing modal using the full 800 px height is a source-inspection candidate whose behaviour was not reproduced. | web/kiosk.html routing-modal/step-1; register row §4.7 line 310; inherited from SW-FINDINGS-01 §6 | inherited triage as source-presence only; behaviour not exercised | **reproduce** |
| **UC-10** | M | Media player mixes routing and TV CEC; first toggle turns the TV off (still open: the strict xfail compared against the source table's power off, index 2; with the display table the first toggle sends display power off, index 1, which that assertion missed, so it XPASSed without a fix. The test now checks for display power off) | The register's text cell and phase cell disagree. The phase cell records the first-toggle bug as fixed in WP-B2 with display power tracked per output; the text cell records that the strict xfail compared against the source table's power-off index 2 and XPASSed without a fix. The routing/CEC split remains DI-9 entity-model work. | tests/uc/test_commands.py:290 test_media_player_first_toggle_does_not_turn_the_tv_off; tests/validation/scenarios/remote.py:215 remote.media_player_toggle; linked features carry 5 fresh-pass and 10 stale records; register row §4.9 line 363; inherited from SW-FINDINGS-01 §5; linked features: F-UC-008, F-UC-009; fresh-pass example docs/validation/evidence/runtime-r8b/F-UC-008/2026-10-19-V3-1baac3de-remote.select_source-uc.json @ 1baac3dec660 (uc V3); stale records: 10 | re-verified at this base for test/scenario presence; presence is not fresh behavioural proof and the two register cells were not reconciled behaviourally | **partial** |
| **UC-11** | M | mDNS publishes `0.0.0.0`, never unregisters (root of retry loop + duplicate events); env var names wrong in docs/plan | Inherited accepted disposition with a surviving element: the image no longer sets UC_INTEGRATION_INTERFACE=0.0.0.0 and the env names were corrected in DOCKER.md, but unregister-on-shutdown remains Phase 4 work. | register row §4.9 line 364; linked features carry 0 fresh-pass records; inherited from SW-FINDINGS-01 §6; linked features: F-UC-001, F-OPS-004 | inherited triage; the surviving element is source presence only and was not re-verified here | **partial** |
| **UC-12** | L | Non-standard remote command names, no button mapping, text/emoji UI tiles | Inherited accepted disposition: non-standard remote command names, missing button mapping and text/emoji UI tiles are agreed DI-9 Phase-4 work, not a newly reproduced defect. | register row §4.9 line 365; linked features carry 5 fresh-pass and 10 stale records; inherited from SW-FINDINGS-01 §6; linked features: F-UC-005, F-UC-006; fresh-pass example docs/validation/evidence/runtime-r8b/F-UC-004/2026-10-19-V3-1baac3de-remote.preset_names_from_web_app-uc.json @ 1baac3dec660 (uc V3); stale records: 10 | inherited triage under the owner-set 2026-09-25 DI-9 direction; the approved-ID compatibility constraint is preserved | **partial** |
| **UC-13** | L | Text sensors instead of binary; duplicate sensors | Inherited accepted disposition: text sensors instead of binary sensors and duplicate sensors are agreed DI-9 Phase-4 work, not a newly reproduced defect. | register row §4.9 line 366; linked features carry 0 fresh-pass records; inherited from SW-FINDINGS-01 §6; linked features: F-UC-011, F-UC-012 | inherited triage under the owner-set 2026-09-25 DI-9 direction | **partial** |
| **UC-18** | H | Modular path non-functional against the real API (envelope, allconnect, switch-all, next/previous, WS client); mocked tests hide it | The original assertion is that the modular path is non-functional against the real API (envelope, allconnect, switch-all, next/previous, WS client) and that mocked tests hide it. At this base the modular path still exists at src/integrations/unfolded_circle/ and is still unreferenced by run.py, so the D4 'rewrite api_client.py as HubClientHttp and delete adapter.py' work has not landed. This row is NOT a newly reproduced defect and NOT a current confirmed product failure; it is an unfinished-architecture record. | src/integrations/unfolded_circle/{__init__.py,api_client.py,entities.py} (api_client.py 5285 bytes); run.py has 0 'integrations' references; register row §4.9 line 371; D4 checkbox docs/REMEDIATION_PLAN.md:650; linked features: 0 (the row caps no feature); inherited from SW-FINDINGS-01 §6 (label R) | re-verified at this base for path existence and unreferenced status; no mocked-test coverage was re-executed and no real-API call was made | **partial** |
| **UC-28** | M | A preset or port renamed in the web app updates the entity definitions the driver offers (names, the matrix remote's pages), but the Integration API has no event to change an entity the user already added on the Remote (`entity_change` carries attributes only; ucapi 0.7.0 does not send `entity_available`); the Remote shows the new name only if it re-reads the definitions. Source lists (attributes) do update live (found in WP-B3) | A preset or port renamed in the web app updates the entity definitions but the Integration API has no event to change an entity the user already added; the Remote shows the new name only if it re-reads the definitions. The register's own next step is 'verify on a real Remote (V4)' and then a DI-9 decision. | register row §4.9 line 381; linked features carry 3 fresh-pass and 6 stale records; inherited from SW-FINDINGS-01 §6 (label PHY); linked features: F-UC-004, F-UC-016; fresh-pass example docs/validation/evidence/runtime-r8b/F-UC-004/2026-10-19-V3-1baac3de-remote.preset_button-uc.json @ 1baac3dec660 (uc V3); stale records: 6 | inherited triage; attribute-level live update is simulator/client level, the physical Remote behaviour is unproven | **hardware** |
| **HIL-03** | M | Telnet differs from the assumptions the hub's parser and the simulator were built on: the banner starts with IAC negotiation, every command is echoed before its answer, and `status` is a 111-line dump headed "get the unit all status:". The hub's parsing must be proven against the real captures | The Telnet dialect difference (IAC negotiation banner, echoed commands, 111-line status dump) is proven against the real captures for reads; set-command acknowledgements still need the write capture. | src/telnet_client.py, src/_telnet_proto.py, tools/simulator/telnet_commands.py; tests/test_telnet_real_captures.py; linked feature has 0 fresh-pass and 4 stale records; register row §4.11 line 411; inherited from SW-FINDINGS-01 §6 (label R+HW); linked features: F-MTX-026; stale records: 4 | re-verified at this base for the capture-test presence; the write-capture half is unproven here | **hardware** |
| **HIL-09** | C | ✅ Fixed and proven on hardware 2026-09-25 (WP-A4 part 2, `write` run with read-back). Every output/input setting command the hub sends is unknown to this firmware: `set output stream/hdcp/hdr/scaler/arc/mute`, `set input edid`, `copy edid`, `set output exa*` get **no answer** and change nothing; `set lcd on time` with `time` is rejected. The device's own web interface uses different commands and `[port, value]` payloads (`tx hdcp`, `tx stream`, `set output audio mute`, `set arc`, `set hdr conversion`, `set video scaler`, `set edid`, `"lcd on time"` …). Output settings, EDID, external audio and LCD have never worked on this hardware | The register row's own cells are contradictory: the description cell begins 'Fixed and proven on hardware 2026-09-25' while the Phase cell says 'open until the capture tool's write run proves them on hardware'. The web-interface command family IS in source at this base (tx stream, tx hdcp, set hdr conversion, set video scaler, set arc, set output audio mute, set edid, lcd on time, set ext-audio) and part of the obsolete family also remains (copy edid x2, copy_edid_from_output x2, edid_copy_from_output x6); the only 'set output stream' occurrence is inside a comment at src/orei_matrix.py:2550. Source presence cannot decide which commands the firmware answers. This row caps 12 features at V1 and its twelve caps are preserved, not removed. | src/orei_matrix.py:2550 (the only 'set output stream' occurrence in src/, inside a comment), :2575/:2583 (tx stream), :2588/:2599 (tx hdcp), :2604/:2616 (set hdr conversion), :2621/:2634 (set video scaler), :2642/:2650 (set arc), :2655/:2663 (set output audio mute), :2852/:2865 (set edid), :2771/:2774/:2782 (lcd on time), :2916/:2924/:2929 (set ext-audio), :2809/:2872 (comments recording that there is no `copy edid`); across src/ the obsolete literals `set output hdcp\|hdr\|scaler\|arc\|mute`, `set input edid` and `set output exa` occur 0 times, while `copy_edid_from_output` occurs 2 times and `edid_copy_from_output` 6 times; tools/hil/README.md (capture-tool write run with read-back); linked features F-MTX-007..F-MTX-020 (12) carry 1 fresh-pass and 174 stale records; register row §4.11 line 413; inherited from SW-FINDINGS-01 §5 (label R+HW); linked features: F-MTX-007, F-MTX-008, F-MTX-009, F-MTX-010, F-MTX-011, F-MTX-012, F-MTX-013, F-MTX-014, F-MTX-015, F-MTX-016, F-MTX-017, F-MTX-020; fresh-pass example docs/validation/evidence/ev02-original-api/F-MTX-007/2026-10-19-V2-1baac3de-outputs.audio_mute-api.json @ 1baac3dec660 (api V2); stale records: 174 | re-verified at this base for the command families; the register's 'Fixed and proven' wording is NOT hardware proof and the twelve V1 caps stand | **hardware** |
| **HIL-14** | L | Reads answered without a login from the capture PC, and sessions stayed alive over 300 s idle; whether a login is needed at all is unconfirmed | Whether a login is needed at all is still unconfirmed: the capture PC read without a login and sessions stayed alive over 300 s idle. | src/orei_matrix.py login/session handling; probes tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/probe/{http_no_session,session_idle_expiry}.json exist (source presence); register row §4.11 line 418; inherited from SW-FINDINGS-01 §6 (label PHY) | inherited triage; fixture presence is not a fresh observation | **hardware** |
| **VAL-14** | M | Already-disconnected routing requests omitted documented failure events | Already-disconnected routing requests omitted the documented failure events. The source correction is integrated at this base: the correction commit 3788353e, its independent review 0bd3d76f and the fresh source 310d8b65 are all ancestors of a07cf94, and src/rest_api/control.py contains switch_failed and switch_all_failed. The row's own disposition keeps it open: 'formal closeout awaits final assembly review and combined CI/publication. No V3 target promotion or historical failure waiver.' | src/rest_api/control.py (switch_failed x4, switch_all_failed x2); commits 3788353e, 0bd3d76f, 310d8b65 - all ancestors of a07cf94; docs/production/software-waves/SW-API-CLIENT-02-C1/FINDING.md; original failed CI bytes preserved under docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci; linked features F-API-033, F-API-034, F-REL-009 | re-verified at this base: integrated correction plus an independent review are ancestors; the combined CI/publication closeout has not happened, so this is not a closure | **partial** |
| **VAL-15** | M | Validation request artifacts and action descriptions do not redact X-Admin-PIN | Validation request artifacts and action descriptions do not redact X-Admin-PIN. The fix exists only in the retained, unintegrated privacy chain: privacy C1 (11f305b1) and C3 (2d02004d) are NOT ancestors of this base, and privacy C2 (615d3c84) is not even present as an object in this checkout's object database although both refs still point at it. | tools/validate/evidence.py at this base (132 lines): _SECRET_KEYS is defined at line 113, _SECRET_QUERY at line 117 and redact() at line 123; the string 'x-admin-pin' occurs 0 times in that file, so the anchored dictionary-key mechanism does not match the header name while _SECRET_QUERY is the separate query-parameter string redaction; tools/validate/model.py Response.describe; docs/production/software-waves/SW-SEC-DATA-02-C1/FINDING.md; linked feature F-SEC-014; no owner credential leak was observed - the reproduction used synthetic markers only | re-verified at this base for the unredacted header-key mechanism and the chain ancestry; the historical synthetic-marker reproduction is NOT a current reproduction | **partial** |

### 4.3 Material-delta rows — the detail the table compresses

For these seventeen rows the register text itself is stale or self-contradictory, so the exact original wording and the exact observed state are given here in full. The other 44 rows are inherited dispositions whose register text is byte-identical to the accepted triage base.

#### SEC-14 — owner

| Field | Value |
| --- | --- |
| Original assertion | Vendor firmware, `XP3.exe`, Control4/RTI drivers, and copyrighted manual committed (public) since the first commit; LICENSE is a stub |
| Register location cell | `docs/BK-808 */`, `LICENSE` |
| Register phase/close cell | 0 (D3) |
| Surviving condition at `a07cf94` | The register's element 'LICENSE is a stub' is obsolete at this base: LICENSE is the full Mozilla Public License 2.0. The vendor-firmware/manual element was purged from the tracked tree; the remaining owner action (GitHub-Support cache purge of public history) is unchanged. No legal conclusion is drawn here. |
| Current source / client / image / proof reference | LICENSE (16726 bytes, contains 'Mozilla Public License', contains no 'stub'); no tracked .exe/.pdf and no docs/BK-808* payload at this base (only tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/http/*.json HTTP capture fixtures); register row §4.3 line 200; inherited from SW-FINDINGS-01 §5 |
| Actual assertion strength | re-verified at this base for the licence clause and the tracked-tree absence; the public-history purge verification is inherited and was not re-run (no exhaustive history or secret-scan authority); no credentials, raw validation, image or archive payload read |
| Recommendation | **owner** |

#### SEC-15 — resolved

| Field | Value |
| --- | --- |
| Original assertion | gitleaks configured but never run; CI actions tag-pinned; base image not digest-pinned |
| Register location cell | `.github/`, `Dockerfile` |
| Register phase/close cell | 6 |
| Surviving condition at `a07cf94` | Both register clauses are obsolete at this base: gitleaks is configured and runs in CI, all 42 `uses:` entries are SHA-pinned (0 tag-pinned), and the external base image is digest-pinned. |
| Current source / client / image / proof reference | .github/workflows/ci.yml: all 42 `uses:` values match a 40-hex SHA; Dockerfile:1 `FROM python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1` (other FROM lines are internal stages); register row §4.3 line 201; inherited from SW-FINDINGS-01 §5 |
| Actual assertion strength | re-verified at this base by reading the workflow and Dockerfile; source declaration only, no fresh CI run is claimed here |
| Recommendation | **resolved** |

#### DEP-05 — resolved

| Field | Value |
| --- | --- |
| Original assertion | CI: no `pull_request` trigger; ruff only on `src/`; mypy non-blocking; no hassfest/HACS validation; no gitleaks; QEMU set up but no multi-arch platforms |
| Register location cell | `.github/workflows/docker-publish.yml` |
| Register phase/close cell | 0 |
| Surviving condition at `a07cf94` | The register's cited workflow file no longer exists (only ci.yml is tracked) and four of its five clauses are obsolete: ci.yml has pull_request/push/workflow_dispatch triggers, hassfest, hacs and gitleaks jobs, and the ruff step iterates six separate candidate paths rather than src/ only. The mypy 'non-blocking' clause is not reproducible from the declared job: the four continue-on-error occurrences (lines 450, 454, 459, 527) are not on the typecheck mypy step. |
| Current source / client / image / proof reference | .github/workflows/ci.yml (only tracked workflow); triggers at the top of the file; job names lint, typecheck, test, uc, ha-test, hassfest, hacs, hygiene, gitleaks, docker-build, ui, ui-comment, validation, validation-ha, publish; ruff loop at ci.yml:51-60; register row §4.5 line 232; inherited from SW-FINDINGS-01 §5 |
| Actual assertion strength | re-verified at this base by reading the workflow; source declaration only - no fresh CI result and no multi-arch build claim |
| Recommendation | **resolved** |

#### UI-06 — reproduce

| Field | Value |
| --- | --- |
| Original assertion | Keyboard shortcuts broken (`scenes` tab id, `window.settingsPanel` never set) |
| Register location cell | `keyboard-shortcuts.js:34,42` |
| Register phase/close cell | 5 |
| Surviving condition at `a07cf94` | Both elements of the condition still hold in source at this base: shortcut '4' still targets `[data-tab="scenes"]` (web/js/components/keyboard-shortcuts.js:34) and the application exposes no such top-level tab (web/index.html data-tab values are dashboard, matrix, inputs, outputs, profiles plus drawer-local general/hardware/interface), and shortcut 's' still tests `window.settingsPanel` (keyboard-shortcuts.js:42-43) while no file under web/ assigns `window.settingsPanel =` (0 matches). |
| Current source / client / image / proof reference | web/js/components/keyboard-shortcuts.js:34,42,43; web/index.html data-tab inventory; linked feature has 0 fresh-pass records; register row §4.7 line 275; also re-confirmed independently as CR-03 in docs/audits/COMPREHENSIVE_PROJECT_REVIEW_20261104.md |
| Actual assertion strength | re-verified at this base by reading the handler and the DOM identifiers; no browser behaviour was executed - this is a source-confirmed wiring defect, not a full browser acceptance |
| Recommendation | **reproduce** |

#### UI-09 — reproduce

| Field | Value |
| --- | --- |
| Original assertion | ~2,800 lines of dead JS: `quick-actions-drawer.js`, `floatable.js`, `presets-panel.js`, `system-shortcuts-panel.js`, `about-dialog.js`, `setup-wizard.js`, `empty-state.js`, `context-menu.js` (mostly), `settings-panel.js` + hidden modal |
| Register location cell | `web/js/` |
| Register phase/close cell | 5 |
| Surviving condition at `a07cf94` | The register's nine named dead-JS files are all present at this base, so the register text is not a file-absence claim; 'dead' is a behaviour claim that was not reproduced. The historical ~2,800-line figure was not re-measured here. |
| Current source / client / image / proof reference | web/js/components/{quick-actions-drawer,presets-panel,system-shortcuts-panel,about-dialog,setup-wizard,empty-state,context-menu,settings-panel}.js and web/js/utils/floatable.js; linked feature has 0 fresh-pass records; register row §4.7 line 278; inherited from SW-FINDINGS-01 §5 |
| Actual assertion strength | re-verified at this base for file presence; file presence is not evidence of deadness and no dead-code behaviour was exercised |
| Recommendation | **reproduce** |

#### UI-13 — partial

| Field | Value |
| --- | --- |
| Original assertion | No module system: ~50 ordered `<script>` tags, `window.*` globals |
| Register location cell | `index.html:660-715` |
| Register phase/close cell | 5 |
| Surviving condition at `a07cf94` | The '~50 ordered <script> tags' figure is approximate: there are exactly 53 <script tags and 0 type="module" tags in web/index.html at this base. |
| Current source / client / image / proof reference | web/index.html (53 <script, 0 module); register row §4.7 line 282; inherited from SW-FINDINGS-01 §5 |
| Actual assertion strength | re-verified at this base by counting tags; the absence of a module system is a source fact, the architectural consequence is not re-derived here |
| Recommendation | **partial** |

#### UI-16 — partial

| Field | Value |
| --- | --- |
| Original assertion | `tron-background.js` redraws every frame with heavy `shadowBlur`; no reduced-motion check |
| Register location cell | `tron-background.js:978-1104` |
| Register phase/close cell | 5 / WP-E2 part (`wp-e2-tokens-css-a11y`): the loop is capped at 30 fps (`this.maxFps = 30`, `this.frameInterval = 1000 / 30`); frames that arrive early skip the draw but still schedule the next one, and the first frame renders immediately so visual snapshots stay deterministic. `prefers-reduced-motion: reduce` paints one static frame and never starts the loop (`isPausedForReducedMotion`). Every `shadowBlur` now goes through `setShadowBlur()`, which caps it at 4 px on low-power devices (`navigator.hardwareConcurrency` / `deviceMemory`, overridable with `setLowPowerMode()`) and leaves a capable device's 20/15/10/8 px glows untouched. Still open: render only while the cycles move, and lazy-load the editors. Proof: `tests/test_ui_tokens_a11y_perf.py` drives the class frame by frame in a stubbed DOM (60 Hz input draws ~31 times a second, reduced motion draws exactly once and schedules nothing, low power caps the blur at 4 px, a capable device keeps every original glow) |
| Surviving condition at `a07cf94` | The register text's 'no reduced-motion check' clause is obsolete at this base: web/js/tron-background.js contains 2 prefers-reduced-motion references, this.maxFps = 30, and setShadowBlur() with a 4 px low-power cap. The Phase column's WP-E2 claims are source-confirmed. The two residual items named in the Phase cell (render only while the cycles move; lazy-load the editors) were not verified here. |
| Current source / client / image / proof reference | web/js/tron-background.js (39882 bytes; maxFps at :56-57, isPausedForReducedMotion and setShadowBlur present); register row §4.7 line 286; inherited from SW-FINDINGS-01 §5 |
| Actual assertion strength | re-verified at this base for the reduced-motion/fps/blur-cap clauses; the two residual items remain unverified - not a closure |
| Recommendation | **partial** |

#### UC-10 — partial

| Field | Value |
| --- | --- |
| Original assertion | Media player mixes routing and TV CEC; first toggle turns the TV off (still open: the strict xfail compared against the source table's power off, index 2; with the display table the first toggle sends display power off, index 1, which that assertion missed, so it XPASSed without a fix. The test now checks for display power off) |
| Register location cell | 4 (DI-9) (the first-toggle bug is fixed in WP-B2: display power is tracked per output and shared with `remote.output_N_cec`, and a toggle from UNKNOWN powers on; `tests/uc/test_commands.py::test_media_player_first_toggle_does_not_turn_the_tv_off`, scenario `remote.media_player_toggle`. The routing/CEC split stays with the DI-9 entity model) |
| Register phase/close cell | 4 (DI-9) (the first-toggle bug is fixed in WP-B2: display power is tracked per output and shared with `remote.output_N_cec`, and a toggle from UNKNOWN powers on; `tests/uc/test_commands.py::test_media_player_first_toggle_does_not_turn_the_tv_off`, scenario `remote.media_player_toggle`. The routing/CEC split stays with the DI-9 entity model) |
| Surviving condition at `a07cf94` | The register's text cell and phase cell disagree. The phase cell records the first-toggle bug as fixed in WP-B2 with display power tracked per output; the text cell records that the strict xfail compared against the source table's power-off index 2 and XPASSed without a fix. The routing/CEC split remains DI-9 entity-model work. |
| Current source / client / image / proof reference | tests/uc/test_commands.py:290 test_media_player_first_toggle_does_not_turn_the_tv_off; tests/validation/scenarios/remote.py:215 remote.media_player_toggle; linked features carry 5 fresh-pass and 10 stale records; register row §4.9 line 363; inherited from SW-FINDINGS-01 §5 |
| Actual assertion strength | re-verified at this base for test/scenario presence; presence is not fresh behavioural proof and the two register cells were not reconciled behaviourally |
| Recommendation | **partial** |

#### UC-18 — partial

| Field | Value |
| --- | --- |
| Original assertion | Modular path non-functional against the real API (envelope, allconnect, switch-all, next/previous, WS client); mocked tests hide it |
| Register location cell | 4 |
| Register phase/close cell | 4 |
| Surviving condition at `a07cf94` | The original assertion is that the modular path is non-functional against the real API (envelope, allconnect, switch-all, next/previous, WS client) and that mocked tests hide it. At this base the modular path still exists at src/integrations/unfolded_circle/ and is still unreferenced by run.py, so the D4 'rewrite api_client.py as HubClientHttp and delete adapter.py' work has not landed. This row is NOT a newly reproduced defect and NOT a current confirmed product failure; it is an unfinished-architecture record. |
| Current source / client / image / proof reference | src/integrations/unfolded_circle/{__init__.py,api_client.py,entities.py} (api_client.py 5285 bytes); run.py has 0 'integrations' references; register row §4.9 line 371; D4 checkbox docs/REMEDIATION_PLAN.md:650; linked features: 0 (the row caps no feature); inherited from SW-FINDINGS-01 §6 (label R) |
| Actual assertion strength | re-verified at this base for path existence and unreferenced status; no mocked-test coverage was re-executed and no real-API call was made |
| Recommendation | **partial** |

#### BE-22 — reproduce

| Field | Value |
| --- | --- |
| Original assertion | Entity creation duplicated 3×, `cec_sender` closure 2× |
| Register location cell | `driver.py:516-590,1553-1598,1929-2002` |
| Register phase/close cell | 4 |
| Surviving condition at `a07cf94` | Both original elements of the condition (entity creation duplicated 3x; cec_sender closure 2x) remain unverified: the cited driver.py ranges 516-590 and 1553-1598 contain no entity-creation or cec_sender code, and cec_sender appears once as an import and once as a single top-level async definition. |
| Current source / client / image / proof reference | src/driver.py (103001 bytes at this base) cec_sender at lines 79 (import), 642 (def), 643 (docstring); no `window`/entity-factory equivalent reproduces the accepted 'single factory' wording, and a name absence is not an architectural conclusion |
| Actual assertion strength | re-verified at this base; inherited `R` label is explicitly not inherited (neither R nor P) |
| Recommendation | **reproduce** |

#### BE-26 — partial

| Field | Value |
| --- | --- |
| Original assertion | Hard-coded default host `192.168.0.100`; ~62 `range(1, 9)` / `[0]*8` |
| Register location cell | many |
| Register phase/close cell | 4 |
| Surviving condition at `a07cf94` | The hard-coded default host and the hard-coded 1..8 range are still present in source; only the register's numeric figures are wrong. |
| Current source / client / image / proof reference | src/hub/cli.py:54 `DEFAULT_MATRIX_HOST = "192.168.0.100"`; `range(1, 9)` occurs 68 times across 18 files under src/ and 13 times across 5 files under src/hub/; the literal `[0] * 8` occurs once (src/orei_matrix.py:1616); linked feature has 0 fresh-pass and 1 stale record |
| Actual assertion strength | re-verified at this base by counting; the register's '~62 range(1, 9) / [0]*8' and the accepted '35x in src' figures are both unverified/approximate |
| Recommendation | **partial** |

#### API-19 — resolved

| Field | Value |
| --- | --- |
| Original assertion | Three divergent "apply profile" paths (recall handler, scene executor, shortcut executor) |
| Register location cell | `profiles.py`, `scene_execution.py`, `system_shortcuts.py` |
| Register phase/close cell | 4 |
| Surviving condition at `a07cf94` | Inherited accepted disposition: the three divergent 'apply profile' paths were resolved in source (run_rest_action is present twice in src/rest_api/control.py at this base); register text has not been reconciled. |
| Current source / client / image / proof reference | src/rest_api/control.py (run_rest_action x2) and src/rest_api/profiles.py (run_rest_action x2); linked feature carries 6 fresh-pass and 17 stale records; inherited from SW-FINDINGS-01 §5 |
| Actual assertion strength | re-verified at this base that the cited source is present; unchanged bytes support source presence only and renew no acceptance |
| Recommendation | **resolved** |

#### API-25 — reproduce

| Field | Value |
| --- | --- |
| Original assertion | Profile CEC targets have two formats: `config.CecConfig` documents (and its tests use) `"input:3"`, the resolver, CEC macros and the web UI use `"input_3"`, and the hub validates neither; the e2e fixture profile uses the colon form, which the CEC dialog shows as "Output NaN". Found in WP-E1 |
| Register location cell | `config.py:CecConfig`, `cec_resolver.py`, `cec_macros.py`, `scene-cec-modal.js`, `rest_api/profiles.py:_validate_cec_config` |
| Register phase/close cell | 4 / WP-E1 read side: the CEC dialog and the CEC tray parse both forms (chips read "Output 1 · TV"; they read "Output NaN"). Storage and validation still open. Proof: tests/e2e/flows.spec.ts API-25 (read side) |
| Surviving condition at `a07cf94` | The original condition has two elements: two CEC target formats in use, and 'the hub validates neither'. Element 1 still holds in the inspected scope; element 2 holds only partially, because _validate_cec_config checks known fields, string arrays and the auto_resolved boolean but not target syntax in that function. |
| Current source / client / image / proof reference | src/rest_api/profiles.py:192 `_validate_cec_config`, called at :516; `input_` x4 and `input:` x0 in that file; the colon form appears in src/config.py and src/rest_api/static.py; register row §4.2 line 171 |
| Actual assertion strength | re-verified at this base; the accepted `R` label does not meet the register's stated condition, so this stays a scoped source-inspection lead and not a resolution |
| Recommendation | **reproduce** |

#### HIL-09 — hardware

| Field | Value |
| --- | --- |
| Original assertion | ✅ Fixed and proven on hardware 2026-09-25 (WP-A4 part 2, `write` run with read-back). Every output/input setting command the hub sends is unknown to this firmware: `set output stream/hdcp/hdr/scaler/arc/mute`, `set input edid`, `copy edid`, `set output exa*` get **no answer** and change nothing; `set lcd on time` with `time` is rejected. The device's own web interface uses different commands and `[port, value]` payloads (`tx hdcp`, `tx stream`, `set output audio mute`, `set arc`, `set hdr conversion`, `set video scaler`, `set edid`, `"lcd on time"` …). Output settings, EDID, external audio and LCD have never worked on this hardware |
| Register location cell | `orei_matrix.py` output/input/ext-audio/LCD setters, `docs/OREI_API_COMMANDS.md`, simulator |
| Register phase/close cell | 1 / WP-A4 part 2 (critical): the hub sends the device web interface's commands (`tx stream`, `tx hdcp`, `set hdr conversion`, `set video scaler`, `set arc`, `set output audio mute`, `set edid`, `set lcd on time` with `"lcd on time"`, `set ext-audio *`, `ext-audio switch`, `reboot`); open until the capture tool's write run proves them on hardware (`tools/hil/README.md`) |
| Surviving condition at `a07cf94` | The register row's own cells are contradictory: the description cell begins 'Fixed and proven on hardware 2026-09-25' while the Phase cell says 'open until the capture tool's write run proves them on hardware'. The web-interface command family IS in source at this base (tx stream, tx hdcp, set hdr conversion, set video scaler, set arc, set output audio mute, set edid, lcd on time, set ext-audio) and part of the obsolete family also remains (copy edid x2, copy_edid_from_output x2, edid_copy_from_output x6); the only 'set output stream' occurrence is inside a comment at src/orei_matrix.py:2550. Source presence cannot decide which commands the firmware answers. This row caps 12 features at V1 and its twelve caps are preserved, not removed. |
| Current source / client / image / proof reference | src/orei_matrix.py:2550 (the only 'set output stream' occurrence in src/, inside a comment), :2575/:2583 (tx stream), :2588/:2599 (tx hdcp), :2604/:2616 (set hdr conversion), :2621/:2634 (set video scaler), :2642/:2650 (set arc), :2655/:2663 (set output audio mute), :2852/:2865 (set edid), :2771/:2774/:2782 (lcd on time), :2916/:2924/:2929 (set ext-audio), :2809/:2872 (comments recording that there is no `copy edid`); across src/ the obsolete literals `set output hdcp\|hdr\|scaler\|arc\|mute`, `set input edid` and `set output exa` occur 0 times, while `copy_edid_from_output` occurs 2 times and `edid_copy_from_output` 6 times; tools/hil/README.md (capture-tool write run with read-back); linked features F-MTX-007..F-MTX-020 (12) carry 1 fresh-pass and 174 stale records; register row §4.11 line 413; inherited from SW-FINDINGS-01 §5 (label R+HW) |
| Actual assertion strength | re-verified at this base for the command families; the register's 'Fixed and proven' wording is NOT hardware proof and the twelve V1 caps stand |
| Recommendation | **hardware** |

#### TST-03 — reproduce

| Field | Value |
| --- | --- |
| Original assertion | No tests: `/api/v2/scenes*`, `/api/integrations`, `/api/settings`, `_task_supervisor`, UC setup handler, poller, WS broadcast/state push, `api_client`/`entities` |
| Register location cell | `tests/` |
| Register phase/close cell | 1-2 |
| Surviving condition at `a07cf94` | The register's 'no tests' list is substantially obsolete at this base: the named surfaces now appear in the test tree (api/v2/scenes 151 occurrences, /api/integrations 91, /api/settings 40, _task_supervisor 7). Occurrence counts are not behavioural proof, so the claim 'these surfaces have no tests' is stale while 'these surfaces have adequate assertions' is not established here. |
| Current source / client / image / proof reference | tests/ tree; linked features carry 2 fresh-pass and 48 stale records; register row §4.6 line 248 |
| Actual assertion strength | re-verified at this base by counting occurrences; counts are identity/coverage hints, not semantic coverage - no assertion strength was reviewed per surface |
| Recommendation | **reproduce** |

#### TST-04 — reproduce

| Field | Value |
| --- | --- |
| Original assertion | No JS tests of any kind |
| Register location cell | `web/` |
| Register phase/close cell | 0 / 5 |
| Surviving condition at `a07cf94` | The register's 'No JS tests of any kind' is obsolete in its literal form: the repository carries Playwright end-to-end specifications (tests/e2e/*.spec.ts, playwright.config.ts). There are still no JavaScript unit-test files under tests/ outside tests/e2e (0 .js/.mjs/.ts files). |
| Current source / client / image / proof reference | tests/e2e/{smoke,flows,c4-flows,kiosk-security,security-auth}.spec.ts + playwright.config.ts; 0 JS/TS unit-test files outside tests/e2e; register row §4.6 line 249 |
| Actual assertion strength | re-verified at this base by file inventory; the presence of e2e specs is not proof that the named product behaviours are asserted |
| Recommendation | **reproduce** |

#### API-07 — owner

| Field | Value |
| --- | --- |
| Original assertion | LCD timeout mode map in shortcuts contradicts device mapping ("Always on" sets 60 s) |
| Register location cell | `system_shortcuts.py:22-34` vs `orei_matrix.py:1972` |
| Register phase/close cell | 2 (HIL) / WP-A4 part 2: shortcut map uses the device codes (0 off, 1 always, 2/3/4 = 15/30/60 s; read back as `get system status.mode`, 3 = 30 s captured); the old `{"time": N}` payload is rejected, the hub sends `{"lcd on time": N}` (proven with HIL-09). The shortcut label "LCD: 10s" (sets 15 s) needs a UI-approved rename. WP-C1: renamed "LCD: 15s" (owner-approved; key `lcd_timeout_10s` kept for pins/Flic; a stored label equal to the old default is migrated on load), proven by scenario `shortcuts.lcd_15s`; close once the owner approves the visual diff of the affected catalog entries |
| Surviving condition at `a07cf94` | The shortcut map uses the device codes (0 off, 1 always, 2/3/4 = 15/30/60 s); the old {"time": N} payload is rejected and the hub sends {"lcd on time": N}. The label was renamed 'LCD: 15s' in WP-C1 and proven by scenario shortcuts.lcd_15s. The row's own close condition is an explicit owner approval of the affected catalogue visual diff. |
| Current source / client / image / proof reference | src/orei_matrix.py:2755-2780 (LCD_TIMEOUT_MODES = dict(DEVICE_LCD_MODES); set_lcd_timeout sends the value under the key "lcd on time"), src/rest_api/audio.py:365-400 (handle_lcd_timeout_modes / handle_set_lcd_timeout); the register's own location anchors (system_shortcuts.py:22-34 vs orei_matrix.py:1972) are historical and carry no LCD map at this base; linked features carry 12 fresh-pass and 35 stale records; register row docs/REMEDIATION_PLAN.md §4.2 line 153 |
| Actual assertion strength | re-verified at this base for the register condition; the owner-approval element is an owner action, not a source defect |
| Recommendation | **owner** |

### 4.4 Records that must be preserved as they stand

These are not findings to close or re-open; they are current-state facts that the earlier prose could be read as contradicting. Each is recorded with its actual provenance.

| Record | Current state at `a07cf94` |
| --- | --- |
| **RV-API034 bounded source review** | **Complete and bounded-PASS, not pending.** The Opus 5.5 source review of `caaa4faabe9ede1e3aed37d2269efd4a4d691e04` (review base `938ae30339790c361abdda6fdd01b11a4e498518`) is recorded at report commit `12eeef938857bfd740854ccbaad34f9bc1b6ce36` with a bounded `PASS` verdict over a named scope only. The reviewed source is **not** integrated into this base (`caaa4faa` is not an ancestor), and `full_RV_completed` is `false`. |
| **RV-API034 report evaluation** | **Complete, accepted for report quality only.** The secondary evaluation of the review report is accepted at commit `c3fcace6260e31d6c176f9feb6ab0dfd6ead849e` (`EVALUATION.md`, 18095 canonical bytes, SHA-256 `9d3825744f43985efa65dd373778d1036891d8cd8696daca05dc70adfa0e67f4`). Its own scope limit: *no evaluator source/security/privacy acceptance*. It is **not** an ancestor of this base; the record of it is, in `EXECUTION_GATE_STATUS.json`. |
| **M-1 / F-SEC-007 freshness** | **Still open and separate.** At exact `caaa`, the C2 edits stale all 16 `F-SEC-007` V3 records, leaving four fresh V2 records, while the registry records `F-SEC-007` at `current: V3`. The actual global gate observed `V2 < recorded V3` and exited 1. That numeric mismatch is **unresolved**; an exit 1 with V2 below a recorded V3 does **not** by itself establish a level-freshness defect, and the recorded FSEC007 diagnosis/refresh remains owed in its own parallel scope. No unchanged failed gate was retried here. |
| **RV-WS040** | **A separate retained-source review package, still open.** The corrective plan (`docs/planning/COMPREHENSIVE_REMEDIATION_20261104.md:13`) lists `RV-PRIVACY-CHAIN`, `RV-WS040` and the remaining `RV-API034` report evaluation as three distinct items. `RV-WS040` is not discharged by the WS component work, by the RV-API034 review or by this inventory. |
| **Accepted UNWIRED WS component** | **Integrated, reviewed, and still unwired.** `e54228c0e3a9451f39b27caeef6aa77e1e1fa59a` ("feat(rest): integrate independently reviewed WS request-work component") added `src/rest_api/ws_request_work.py` (519 lines) and `tests/test_ws_request_work.py` (1502 lines); it **is** an ancestor of this base. The module is referenced by **no** other file under `src/`, `run.py` or `run_server.py` — it is accepted, unwired, and does not by itself discharge CR-01. It is also the **only** product-source delta between the accepted triage base `3602a4e` and this base. |
| **Privacy chain C1–C4** | **Unaccepted.** C1 (`11f305b16c4c95e27682d13df4b02c8de33354d7`) and C3 (`2d02004d3108953a302e1a49aab9a5f24e944136`) exist as objects but are **not** ancestors of this base; C2 (`615d3c8403b237dd117c803269c7b9b58895f9217`) is **not present in the local object database** at all (§1.2). The chain therefore remains delivered-but-unintegrated and unaccepted. |
| **Privacy qualification** | **Terminal FAIL for both attempted families; no automatic retake.** The Opus 5.5 privacy assessment is recorded `FAIL; mandatory six-axis competence not earned`; the MiniMax privacy review domain is recorded `FAIL/NOT_QUALIFIED; one first candidate / one judge exhausted; no automatic retry / extra judge` (axes: provenance PASS, dataflow_invariants FAIL, counterexamples PASS, behaviour_and_tools FAIL, calibration FAIL, review_quality FAIL). `automatic_retakes` is `false`. The lost original bytes and the failed-run outputs stay as recorded; nothing was reconstructed. |
| **WS first authorship** | **NOT_GRANTED / WSR03** — unchanged. The Opus 5.5 WS component is recorded as *bounded correction candidate*, not as granted first authorship, and the acceptance chain for it is separate from this inventory. |

## 5. All 268 canonical feature contracts

One row per canonical registry entry. Columns:

* **Target** — the registry's `target`.
* **Recorded** — the registry's `current` (the recorded baseline).
* **Effective** — the project's computed level: the highest level with **fresh passing** evidence, else the recorded baseline, capped at V1 while an open critical/high finding is linked. This is the number the project's own gate and ledger use.
* **Cap** — the open critical/high finding that caps the feature, if any.
* **Fresh** — `fresh` / `stale` / `—` (no committed record of any kind).
* **Proof binding** — the committed evidence record(s) that establish the effective level, with their path and evidence commit, or the explicit absence of one.
* **Gap (Eff<Tgt)** — the project's below-target test.
* **Declared (Rec≠Tgt)** — the registry inequality, which is **not** the below-target test.
* **Pkg** — the mapped package from the 30-package crosswalk.

### 5.1 Matrix control (31 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-MTX-001 | Route one input to one output | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-008/2026-10-19-V3-1baac3de-remote.select_source-uc.json` @ `1baac3dec660` (uc V3, remote.select_source) | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-002 | Route one input to every output | V4 | V3 | V3 | — | stale | no fresh passing record; 6 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-003 | Recall a matrix preset (1-8) | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-004/2026-10-19-V3-1baac3de-remote.preset_button-uc.json` @ `1baac3dec660` (uc V3, remote.preset_button) | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-004 | Save the current routing to a matrix preset | V4 | V1 | V1 | — | stale | no fresh passing record; 27 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-005 | Name presets in the web app (names shown by the API, UI, kiosk) | V4 | V0 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-MTX-005/2026-10-19-V3-1baac3de-presets.rename-browser.json` @ `1baac3dec660` (browser V3, presets.rename) +1 more | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-006 | Matrix power on / standby | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-010/2026-10-19-V3-1baac3de-remote.power_switch_off-uc.json` @ `1baac3dec660` (uc V3, remote.power_switch_off) | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-007 | Mute / unmute the audio of an output | V4 | V1 | V1 | HIL-09 | fresh | `docs/validation/evidence/ev02-original-api/F-MTX-007/2026-10-19-V2-1baac3de-outputs.audio_mute-api.json` @ `1baac3dec660` (api V2, outputs.audio_mute) | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-008 | Enable / disable an output's video stream | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 5 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-009 | Set an output's HDCP mode | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 11 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-010 | Set an output's HDR mode | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 9 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-011 | Set an output's scaler mode (incl. audio-only) | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 11 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-012 | Enable / disable ARC on an output | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 5 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-013 | Set an input's EDID | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 10 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-014 | Copy EDID from a connected display | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 11 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-015 | External audio: matrix mode | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 9 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-016 | External audio: enable per output | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 20 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-017 | External audio: source per output | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 71 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-018 | Front-panel beep on / off | V4 | V1 | V1 | — | stale | no fresh passing record; 3 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-019 | Front-panel lock | V4 | V1 | V1 | — | stale | no fresh passing record; 3 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-020 | Front-panel LCD timeout | V4 | V1 | V1 | HIL-09 | stale | no fresh passing record; 8 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-021 | Reboot the matrix | V4 | V1 | V1 | — | stale | no fresh passing record; 8 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-022 | Rename inputs (names stored on the matrix) | V4 | V1 | V1 | — | stale | no fresh passing record; 6 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-023 | Rename outputs (names stored on the matrix) | V4 | V1 | V1 | — | stale | no fresh passing record; 6 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-024 | Read the current routing and names | V4 | V2 | V2 | — | stale | no fresh passing record; 4 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-025 | Show which inputs have an active signal | V4 | V1 | V1 | — | stale | no fresh passing record; 16 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-026 | Show which cables are plugged in (Telnet link status) | V4 | V1 | V1 | — | stale | no fresh passing record; 4 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-027 | Show which outputs have a display connected | V4 | V1 | V1 | — | stale | no fresh passing record; 16 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-028 | Show device info (model, firmware, network) | V4 | V1 | V1 | — | stale | no fresh passing record; 5 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-029 | Cycle an output to the next / previous input | V4 | V1 | V1 | — | stale | no fresh passing record; 138 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-030 | Read a preset's stored routing | V4 | V1 | V1 | — | stale | no fresh passing record; 35 stale record(s), commits `1baac3dec660`…`f4f417bfed08` | **yes** | yes | SW-PROTOCOL-PREP |
| F-MTX-031 | Notice changes made outside the hub (front panel, cable plugged, source on/off) | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.display_unplugged-browser.json` @ `1baac3dec660` (browser V3, live.display_unplugged) +3 more | **yes** | yes | SW-PROTOCOL-PREP |

### 5.2 CEC control (11 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-CEC-001 | Power a source on / off over CEC | V4 | V1 | V1 | — | stale | no fresh passing record; 17 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-002 | Navigate a source's menus over CEC (up/down/left/right/select/menu/back) | V4 | V1 | V1 | — | stale | no fresh passing record; 56 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-003 | Control playback on a source over CEC | V4 | V1 | V1 | — | stale | no fresh passing record; 56 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-004 | Source volume / mute over CEC | V4 | V1 | V1 | — | stale | no fresh passing record; 24 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-005 | Turn a display (TV) on / off over CEC | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-007/2026-10-19-V3-1baac3de-remote.output_cec_power_on-uc.json` @ `1baac3dec660` (uc V3, remote.output_cec_power_on) +1 more | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-006 | Display / soundbar volume and mute over CEC | V4 | V1 | V1 | — | stale | no fresh passing record; 25 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-007 | Enable CEC on the target port automatically before a command | V4 | V1 | V1 | — | stale | no fresh passing record; 417 stale record(s), commits `62adf645a020`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-008 | Enable / disable CEC per port | V4 | V1 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-CEC-008/2026-10-19-V2-1baac3de-cec_controls.input_1_enable_0-api.json` @ `1baac3dec660` (api V2, cec_controls.input_1_enable_0) +39 more | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-009 | Read which ports have CEC enabled | V4 | V1 | V1 | — | stale | no fresh passing record; 4 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-010 | Send CEC over Telnet (OREI_USE_TELNET_CEC) | V4 | V1 | V1 | — | stale | no fresh passing record; 208 stale record(s), commits `62adf645a020`…`a538a8ef4c52` | **yes** | yes | SW-PROTOCOL-PREP |
| F-CEC-011 | List CEC commands and per-port capabilities (incl. audio-only outputs) | V4 | V1 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-CEC-011/2026-10-19-V2-1baac3de-cec_caps.all_pattern_0-api.json` @ `1baac3dec660` (api V2, cec_caps.all_pattern_0) +87 more | **yes** | yes | SW-PROTOCOL-PREP |

### 5.3 REST/WebSocket contract (42 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-API-001 | GET /api/health, /api/openapi.json, /api/docs (liveness, matrix connection, runtime metrics, integration lifecycle, OpenAPI 3.1 & Swagger UI) | V3 | V2 | V2 | — | — | **no committed record of any kind** | **yes** | yes | SW-API-CLIENT |
| F-API-002 | API info and root (GET /, /api, /api/info) | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/software-waves/SW-API-READ-01/F-API-002/2026-10-20-V2-0dd2c25e-contracts.api_info-api.json` @ `0dd2c25ea866` (api V2, contracts.api_info) +4 more | no | no | SW-API-READ |
| F-API-003 | GET /api/status | V3 | V2 | V2 | — | — | **no committed record of any kind** | **yes** | yes | SW-API-CLIENT |
| F-API-004 | Detailed status (GET /api/status/full\|inputs\|outputs\|cables\|edid\|ext-audio\|system\|device\|cec) | V3 | V1 | V1 | — | stale | no fresh passing record; 6 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-API-CLIENT |
| F-API-005 | POST /api/switch (one output or all) | V3 | V2 | V2 | — | stale | no fresh passing record; 6 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-API-CLIENT |
| F-API-006 | POST /api/output/{output}/source and input cycling | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-API-CLIENT |
| F-API-007 | POST /api/preset/{preset} (recall) | V3 | V2 | V2 | — | stale | no fresh passing record; 4 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-API-CLIENT |
| F-API-008 | POST /api/preset/{preset}/save | V2 | V1 | V1 | — | stale | no fresh passing record; 49 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-API-WRITE |
| F-API-009 | POST /api/power/on\|off | V3 | V1 | V1 | — | stale | no fresh passing record; 2 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-API-CLIENT |
| F-API-010 | Output setting routes (mute, enable, hdcp, hdr, scaler, arc) | V2 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-API-WRITE |
| F-API-011 | EDID routes | V2 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-API-WRITE |
| F-API-012 | External audio routes | V2 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-API-WRITE |
| F-API-013 | System setting routes (beep, panel lock, LCD, reboot) | V2 | V1 | V1 | — | stale | no fresh passing record; 8 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-API-WRITE |
| F-API-014 | System info and storage routes | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-API-014/2026-10-19-V2-1baac3de-contracts.storage-api.json` @ `1baac3dec660` (api V2, contracts.storage) +1 more | no | no | SW-API-READ |
| F-API-015 | CEC command routes | V3 | V1 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-CEC-005/2026-10-19-V2-1baac3de-cec.output_power_on-api.json` @ `1baac3dec660` (api V2, cec.output_power_on) | **yes** | yes | SW-API-CLIENT |
| F-API-016 | CEC catalogue, capability and enable routes | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-API-016/2026-10-19-V2-1baac3de-contracts.cec_input_catalog-api.json` @ `1baac3dec660` (api V2, contracts.cec_input_catalog) +131 more | no | no | SW-API-READ |
| F-API-017 | Device settings routes (icons, display names, preset names, favourite/dashboard presets) | V2 | V1 | V1 | — | stale | no fresh passing record; 9 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-API-WRITE |
| F-API-018 | Name routes (POST /api/input\|output/{n}/name) | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/ev02-input-name/F-API-018/2026-10-20-V2-bb4d3fdc-writes.input_name-api.json` @ `bb4d3fdc972e` (api V2, writes.input_name) +3 more | no | no | SW-API-WRITE |
| F-API-019 | Profile routes | V2 | V1 | V1 | — | stale | no fresh passing record; 108 stale record(s), commits `0b9cbe878608`…`7dbc4dc70c70` | **yes** | yes | SW-API-WRITE |
| F-API-020 | Scene v1 alias routes (/api/scene*, /api/scenes) | V2 | V1 | V2 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-002/2026-10-19-V2-1baac3de-profile_state.alias_recall-api.json` @ `1baac3dec660` (api V2, profile_state.alias_recall) | no | yes | SW-API-WRITE |
| F-API-021 | Scene v2 routes (/api/v2/scenes*) | V2 | V2 | V2 | — | stale | no fresh passing record; 44 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | no | no | SW-API-WRITE |
| F-API-022 | Response envelope and input validation (4xx before anything reaches the matrix) | V2 | V1 | V1 | — | stale | no fresh passing record; 1 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-API-WRITE |
| F-API-023 | Macro routes | V2 | V1 | V1 | — | stale | no fresh passing record; 72 stale record(s), commits `1aafbbf4ec1d`…`7dbc4dc70c70` | **yes** | yes | SW-API-WRITE |
| F-API-024 | Shortcut routes (/api/system-shortcuts* and the /api/shortcuts* aliases) | V2 | V1 | V1 | — | stale | no fresh passing record; 11 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-API-WRITE |
| F-API-025 | Dashboard layout routes | V2 | V1 | V1 | — | stale | no fresh passing record; 2 stale record(s), commits `b3aced1ba250`…`b3aced1ba250` | **yes** | yes | SW-API-WRITE |
| F-API-026 | Themes and UI preference routes | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-API-026/2026-10-19-V2-1baac3de-contracts.themes-api.json` @ `1baac3dec660` (api V2, contracts.themes) +4 more | no | no | SW-API-READ |
| F-API-027 | Settings routes (matrix host, test connection) | V2 | V1 | V1 | — | stale | no fresh passing record; 2 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-API-WRITE |
| F-API-028 | Flic integration routes | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-API-028/2026-10-19-V2-1baac3de-contracts.flic_buttons-api.json` @ `1baac3dec660` (api V2, contracts.flic_buttons) +1 more | no | no | SW-API-READ |
| F-API-029 | Web UI, kiosk and static asset routes | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-API-CLIENT |
| F-API-030 | Rate limiting (60 requests / 10 s per client) | V2 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-API-WRITE |
| F-API-031 | CORS headers | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/software-waves/W03-CLOSEOUT-20261028/combined/cors/F-API-031/2026-10-26-V2-310d8b65-sw_api_read_04.configured_allowed-api.json` @ `310d8b65a9fc` (api V2, sw_api_read_04.configured_allowed) +25 more | no | no | SW-API-READ |
| F-API-032 | WebSocket /ws: welcome, status snapshot, get_status, matrix link, errors | V2 | V2 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-REL-009/2026-10-19-V3-1baac3de-live.matrix_offline-browser.json` @ `1baac3dec660` (browser V3, live.matrix_offline) | no (above target) | no | SW-API-READ |
| F-API-033 | WS event routing_change (one per changed output, whoever routed) / switch_failed | V3 | V2 | V2 | — | fresh | `docs/validation/evidence/software-waves/W03-CLOSEOUT-20261028/combined/offline/F-REL-009/2026-10-26-V2-310d8b65-failures.unreachable_switch-api.json` @ `310d8b65a9fc` (api V2, failures.unreachable_switch) | **yes** | yes | SW-API-CLIENT |
| F-API-034 | Route to all: routing_change per output that changed / switch_all_failed | V3 | V2 | V2 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-API-CLIENT |
| F-API-035 | WS event preset_recall / preset_recall_failed | V3 | V2 | V2 | — | stale | no fresh passing record; 4 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-API-CLIENT |
| F-API-036 | WS event audio_mute | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-MTX-007/2026-10-19-V2-1baac3de-outputs.audio_mute-api.json` @ `1baac3dec660` (api V2, outputs.audio_mute) +1 more | no | no | SW-API-WRITE |
| F-API-037 | WS events device_settings / device_settings_full | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/runtime-r8b/F-MTX-005/2026-10-19-V2-1baac3de-presets.rename-api.json` @ `1baac3dec660` (api V2, presets.rename) | no | no | SW-API-WRITE |
| F-API-038 | WS event cec_command | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-CEC-005/2026-10-19-V2-1baac3de-cec.output_power_on-api.json` @ `1baac3dec660` (api V2, cec.output_power_on) | no | no | SW-API-WRITE |
| F-API-039 | WS status snapshot (after connect, after a first reading, get_status) | V2 | V2 | V2 | — | — | **no committed record of any kind** | no | no | SW-API-READ |
| F-API-040 | WS live matrix events from the hub's own poller (routing, power, signal, display, cable, mute, names) | V2 | V2 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.display_unplugged-browser.json` @ `1baac3dec660` (browser V3, live.display_unplugged) +3 more | no (above target) | no | SW-API-READ |
| F-API-041 | WS event scene_execution_error | V2 | V2 | V2 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-011/2026-10-19-V2-1baac3de-scenes.partial_failure-api.json` @ `1baac3dec660` (api V2, scenes.partial_failure) | no | no | SW-API-WRITE |
| F-API-042 | WS heartbeat (ping / pong) | V2 | V2 | V2 | — | — | **no committed record of any kind** | no | no | SW-API-READ |

### 5.4 Domain features (36 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-DOM-001 | Create, edit and delete profiles | V3 | V1 | V1 | — | stale | no fresh passing record; 50 stale record(s), commits `0b9cbe878608`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-PROFILE |
| F-DOM-002 | Recall a profile: its routing is applied | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-002/2026-10-19-V3-1baac3de-profiles.recall_disabled_output-browser.json` @ `1baac3dec660` (browser V3, profiles.recall_disabled_output) +5 more | **yes** | yes | SW-DOM-HIL-PREP |
| F-DOM-003 | Recall a profile: its output settings (mute, HDR, HDCP, enable) are applied | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-002/2026-10-19-V3-1baac3de-profiles.recall_disabled_output-browser.json` @ `1baac3dec660` (browser V3, profiles.recall_disabled_output) +6 more | **yes** | yes | SW-DOM-HIL-PREP |
| F-DOM-004 | Recall a profile: its power-on macro runs | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-004/2026-10-19-V3-1baac3de-profiles.recall_power_macro-browser.json` @ `1baac3dec660` (browser V3, profiles.recall_power_macro) +1 more | **yes** | yes | SW-DOM-HIL-PREP |
| F-DOM-005 | Protect a profile with a passcode (per-item PIN) | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-005/2026-10-19-V3-1baac3de-profiles.recall_needs_passcode-browser.json` @ `1baac3dec660` (browser V3, profiles.recall_needs_passcode) +7 more | no | yes | SW-DOM-PROFILE |
| F-DOM-006 | Favourite, pin, reorder profiles and show them on the dashboard | V3 | V1 | V1 | — | stale | no fresh passing record; 20 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-PROFILE |
| F-DOM-007 | Per-profile CEC targets (nav/playback/volume/power) and auto-resolve | V3 | V1 | V1 | — | stale | no fresh passing record; 83 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-PROFILE |
| F-DOM-008 | Profile execution log | V3 | V0 | V0 | — | stale | no fresh passing record; 6 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-PROFILE |
| F-DOM-009 | Save the current routing as a new profile | V3 | V1 | V1 | — | stale | no fresh passing record; 14 stale record(s), commits `7dbc4dc70c70`…`ed4cb0fb7876` | **yes** | yes | SW-DOM-PROFILE |
| F-DOM-010 | Create, edit and delete scenes (sequences of steps) | V3 | V2 | V2 | — | stale | no fresh passing record; 46 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-SCENE |
| F-DOM-011 | Run a scene: profile steps | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-011/2026-10-19-V3-1baac3de-scenes.disabled_output_state-browser.json` @ `1baac3dec660` (browser V3, scenes.disabled_output_state) +9 more | **yes** | yes | SW-DOM-HIL-PREP |
| F-DOM-012 | Run a scene: macro steps | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-011/2026-10-19-V3-1baac3de-scenes.run_profile_macro_preset-browser.json` @ `1baac3dec660` (browser V3, scenes.run_profile_macro_preset) +5 more | **yes** | yes | SW-DOM-HIL-PREP |
| F-DOM-013 | Run a scene: wait and shortcut steps | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-013/2026-10-19-V3-1baac3de-scenes.wait_between_actions-browser.json` @ `1baac3dec660` (browser V3, scenes.wait_between_actions) +3 more | no | no | SW-DOM-SCENE |
| F-DOM-014 | Scene overrides (per-run changes to a profile step) | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-011/2026-10-19-V3-1baac3de-scenes.run_profile_macro_preset-browser.json` @ `1baac3dec660` (browser V3, scenes.run_profile_macro_preset) +5 more | no | no | SW-DOM-SCENE |
| F-DOM-015 | Protect a scene with a passcode | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-011/2026-10-19-V3-1baac3de-scenes.run_protected-browser.json` @ `1baac3dec660` (browser V3, scenes.run_protected) +1 more | no | yes | SW-DOM-SCENE |
| F-DOM-016 | Validate a scene and detect conflicting steps | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-016/2026-10-19-V3-1baac3de-scenes.conflicts_visible-browser.json` @ `1baac3dec660` (browser V3, scenes.conflicts_visible) +2 more | no | no | SW-DOM-SCENE |
| F-DOM-017 | Scene execution history | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-011/2026-10-19-V3-1baac3de-scenes.partial_failure-browser.json` @ `1baac3dec660` (browser V3, scenes.partial_failure) +1 more | no | no | SW-DOM-SCENE |
| F-DOM-018 | Legacy 'scenes' (v1) as aliases of profiles | V2 | V1 | V1 | — | stale | no fresh passing record; 2 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-PROFILE |
| F-DOM-019 | Create, edit, delete and validate CEC macros | V3 | V1 | V1 | — | stale | no fresh passing record; 63 stale record(s), commits `1aafbbf4ec1d`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-MACRO |
| F-DOM-020 | Run a CEC macro (steps, targets, delays) | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-012/2026-10-19-V3-1baac3de-scenes.macro_continues_after_refusal-browser.json` @ `1baac3dec660` (browser V3, scenes.macro_continues_after_refusal) +7 more | **yes** | yes | SW-DOM-HIL-PREP |
| F-DOM-021 | Test / dry-run a macro | V3 | V1 | V1 | — | stale | no fresh passing record; 2 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-MACRO |
| F-DOM-022 | Favourite macros and show them on the dashboard | V3 | V1 | V1 | — | stale | no fresh passing record; 7 stale record(s), commits `7dbc4dc70c70`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-MACRO |
| F-DOM-023 | Built-in shortcuts: route all to an output, one-to-one routing | V3 | V2 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-023/2026-10-19-V3-1baac3de-shortcuts.route_one_to_one-browser.json` @ `1baac3dec660` (browser V3, shortcuts.route_one_to_one) +1 more | no | yes | SW-DOM-SHORTCUT |
| F-DOM-024 | Built-in shortcut: power everything off | V3 | V2 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-024/2026-10-19-V3-1baac3de-shortcuts.power_off_all-browser.json` @ `1baac3dec660` (browser V3, shortcuts.power_off_all) +1 more | no | yes | SW-DOM-SHORTCUT |
| F-DOM-025 | Built-in shortcuts: mute / unmute all outputs | V3 | V2 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-025/2026-10-19-V3-1baac3de-shortcuts.mute_all-browser.json` @ `1baac3dec660` (browser V3, shortcuts.mute_all) +5 more | no | yes | SW-DOM-SHORTCUT |
| F-DOM-026 | Built-in shortcuts: recall preset 1-8 | V3 | V2 | V2 | — | stale | no fresh passing record; 7 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-DOM-SHORTCUT |
| F-DOM-027 | Built-in shortcuts: beep, panel lock, reboot | V3 | V2 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-027/2026-10-19-V3-1baac3de-shortcuts.beep_off-browser.json` @ `1baac3dec660` (browser V3, shortcuts.beep_off) +13 more | no | yes | SW-DOM-SHORTCUT |
| F-DOM-028 | Built-in shortcuts: LCD timeout | V3 | V2 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-028/2026-10-19-V3-1baac3de-shortcuts.lcd_15s-browser.json` @ `1baac3dec660` (browser V3, shortcuts.lcd_15s) +11 more | no | yes | SW-DOM-SHORTCUT |
| F-DOM-029 | Create, rename, reorder and delete user shortcuts | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-DOM-SHORTCUT |
| F-DOM-030 | Favourite shortcuts and show them on the dashboard | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-DOM-SHORTCUT |
| F-DOM-031 | Dashboard layout (add, remove, reorder cards) | V3 | V1 | V1 | — | stale | no fresh passing record; 2 stale record(s), commits `b3aced1ba250`…`b3aced1ba250` | **yes** | yes | SW-DOM-PRESENT |
| F-DOM-032 | Input/output icons, colours and display names (device settings) | V3 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-DOM-PRESENT |
| F-DOM-033 | Favourite presets and choose which presets the dashboard shows | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-DOM-PRESENT |
| F-DOM-034 | Save a custom routing mapping into a preset | V3 | V1 | V1 | — | stale | no fresh passing record; 25 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-DOM-PRESENT |
| F-DOM-035 | Theme presets and custom themes | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-DOM-PRESENT |
| F-DOM-036 | UI preferences stored on the hub | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-DOM-PRESENT |

### 5.5 Web UI (36 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-UI-001 | Open the web UI; the header shows the matrix connection | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-UI-CONTROL |
| F-UI-002 | Route by clicking a cell in the matrix grid | V3 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | no | no | SW-UI-CONTROL |
| F-UI-003 | Route from the matrix card view (routing sheet) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-CONTROL |
| F-UI-004 | Route one input to every output from the Route To All drawer | V3 | V1 | V1 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-UI-CONTROL |
| F-UI-005 | Recall a preset from the Presets drawer | V3 | V1 | V1 | — | stale | no fresh passing record; 4 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-UI-CONTROL |
| F-UI-006 | Rename a preset in the Presets drawer | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-MTX-005/2026-10-19-V3-1baac3de-presets.rename-browser.json` @ `1baac3dec660` (browser V3, presets.rename) | no | yes | SW-UI-CONTROL |
| F-UI-007 | Overwrite a preset / save a custom mapping from the Presets drawer | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-CONTROL |
| F-UI-008 | Run profiles, scenes, presets, shortcuts and macros from dashboard cards | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-011/2026-10-19-V3-1baac3de-scenes.run_protected-browser.json` @ `1baac3dec660` (browser V3, scenes.run_protected) | no | no | SW-UI-MANAGE |
| F-UI-009 | Customise the dashboard (card picker, pin, reorder) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-MANAGE |
| F-UI-010 | Inputs tab: signal/cable status and input settings (name, icon, EDID) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-CONTROL |
| F-UI-011 | Outputs tab: display status and output settings (HDCP, HDR, scaler, ARC, mute) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-CONTROL |
| F-UI-012 | Profiles tab and profile manager | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-002/2026-10-19-V3-1baac3de-profiles.recall_routing-browser.json` @ `1baac3dec660` (browser V3, profiles.recall_routing) | no | no | SW-UI-MANAGE |
| F-UI-013 | Create and edit a profile in the profile editor | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-MANAGE |
| F-UI-014 | Run a passcode-protected profile (passcode prompt) | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-005/2026-10-19-V3-1baac3de-profiles.recall_needs_passcode-browser.json` @ `1baac3dec660` (browser V3, profiles.recall_needs_passcode) +2 more | no | no | SW-UI-MANAGE |
| F-UI-015 | Build a scene in the scene editor | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-UI-MANAGE |
| F-UI-016 | Build a CEC macro in the macro editor | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-MANAGE |
| F-UI-017 | CEC remote on output/input tiles and the CEC tray | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-CONTROL |
| F-UI-018 | Theme presets, customisation and card opacity | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-019 | General settings: matrix host and connection test | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-020 | Hardware settings: beep, panel lock, LCD, reboot | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-021 | Interface settings | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-022 | Shortcuts drawer: run, rename, reorder | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-MANAGE |
| F-UI-023 | Integrations drawer (Flic request builder, HA YAML, Remote 3 info) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-MANAGE |
| F-UI-024 | Live updates when another client or the matrix changes something | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.display_unplugged-browser.json` @ `1baac3dec660` (browser V3, live.display_unplugged) +3 more | no | no | SW-UI-CONTROL |
| F-UI-025 | Reconnect and resync after the WebSocket drops | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-UI-CONTROL |
| F-UI-026 | Show an error state when the matrix is unreachable | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-UI-CONTROL |
| F-UI-027 | Toasts and confirmation dialogs | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-DOM-011/2026-10-19-V3-1baac3de-scenes.partial_failure-browser.json` @ `1baac3dec660` (browser V3, scenes.partial_failure) | no | no | SW-UI-CONTROL |
| F-UI-028 | Keyboard shortcuts | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-029 | Accessibility (keyboard, focus, ARIA, contrast, zoom) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-030 | Debug panel | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-031 | About dialog | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-UI-PRESENT |
| F-UI-032 | Animated Tron background (opt-in) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-033 | Tablet and phone layouts | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-PRESENT |
| F-UI-034 | Personalise tabs in the Control Deck (pin, reorder) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-MANAGE |
| F-UI-035 | Copy an API endpoint for automation (API button / modal) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-MANAGE |
| F-UI-036 | First-run setup wizard (matrix connection) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UI-MANAGE |

### 5.6 Kiosk (14 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-KIO-001 | Open the kiosk; it shows the matrix connection | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-KIOSK-STATE |
| F-KIO-002 | Route a source to one display with the routing wizard | V3 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | no | no | SW-KIOSK-CONTROL |
| F-KIO-003 | Route a source to every display from the kiosk | V3 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | no | no | SW-KIOSK-CONTROL |
| F-KIO-004 | Input and output status tiles | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-KIOSK-STATE |
| F-KIO-005 | Recall a preset from the kiosk | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-KIOSK-CONTROL |
| F-KIO-006 | Configure which presets the kiosk shows (edit mode) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-KIOSK-CONTROL |
| F-KIO-007 | Run shortcuts from the kiosk and map them to slots | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-KIOSK-CONTROL |
| F-KIO-008 | Run profiles from the kiosk; create one with the profile wizard | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-KIO-008/2026-10-19-V3-1baac3de-kiosk.profile_with_passcode-browser.json` @ `1baac3dec660` (browser V3, kiosk.profile_with_passcode) +1 more | no | yes | SW-KIOSK-CONTROL |
| F-KIO-009 | CEC remote in the kiosk | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-KIOSK-CONTROL |
| F-KIO-010 | Kiosk live updates | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.front_panel_route-browser.json` @ `1baac3dec660` (browser V3, live.front_panel_route) +1 more | no | no | SW-KIOSK-STATE |
| F-KIO-011 | Kiosk disconnected state | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-REL-009/2026-10-19-V3-1baac3de-live.matrix_offline-browser.json` @ `1baac3dec660` (browser V3, live.matrix_offline) | no | no | SW-KIOSK-STATE |
| F-KIO-012 | Kiosk layout and pins persist | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-KIOSK-STATE |
| F-KIO-013 | Kiosk follows the selected theme | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-KIOSK-STATE |
| F-KIO-014 | Kiosk touch accessibility (targets, ARIA, contrast) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-KIOSK-STATE |

### 5.7 Remote 3 integration (17 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-UC-001 | Discover the integration and register the driver (mDNS, driver URL) | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |
| F-UC-002 | Set up the integration on the Remote | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |
| F-UC-003 | Reconfigure the integration (new matrix address) | V4 | V3 | V3 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |
| F-UC-004 | Preset buttons on the Remote | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-004/2026-10-19-V3-1baac3de-remote.preset_button-uc.json` @ `1baac3dec660` (uc V3, remote.preset_button) +1 more | **yes** | yes | SW-UC-PREP |
| F-UC-005 | Matrix remote entity with a preset page | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-004/2026-10-19-V3-1baac3de-remote.preset_names_from_web_app-uc.json` @ `1baac3dec660` (uc V3, remote.preset_names_from_web_app) +1 more | **yes** | yes | SW-UC-PREP |
| F-UC-006 | Per-input CEC remotes (source power, navigation, playback) | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-006/2026-10-19-V3-1baac3de-remote.input_cec_command-uc.json` @ `1baac3dec660` (uc V3, remote.input_cec_command) +2 more | **yes** | yes | SW-UC-PREP |
| F-UC-007 | Per-output CEC remotes (TV power, volume) | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-007/2026-10-19-V3-1baac3de-remote.cec_bad_sequence-uc.json` @ `1baac3dec660` (uc V3, remote.cec_bad_sequence) +4 more | **yes** | yes | SW-UC-PREP |
| F-UC-008 | Choose an output's source from the Remote (media player source list) | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-008/2026-10-19-V3-1baac3de-remote.select_source-uc.json` @ `1baac3dec660` (uc V3, remote.select_source) +2 more | **yes** | yes | SW-UC-PREP |
| F-UC-009 | TV power / volume / mute from the output media player | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-009/2026-10-19-V3-1baac3de-remote.media_player_toggle-uc.json` @ `1baac3dec660` (uc V3, remote.media_player_toggle) +1 more | **yes** | yes | SW-UC-PREP |
| F-UC-010 | Matrix power switch on the Remote | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-010/2026-10-19-V3-1baac3de-remote.power_switch_follows_front_panel-uc.json` @ `1baac3dec660` (uc V3, remote.power_switch_follows_front_panel) +1 more | **yes** | yes | SW-UC-PREP |
| F-UC-011 | Input signal and cable sensors | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |
| F-UC-012 | Output connected, cable and source sensors | V4 | V3 | V3 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |
| F-UC-013 | Entities go unavailable while the matrix is unreachable | V4 | V3 | V3 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |
| F-UC-014 | Remote standby and wake | V4 | V3 | V3 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |
| F-UC-015 | Only changed attributes are sent to the Remote | V4 | V3 | V3 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |
| F-UC-016 | Renamed inputs/outputs show up on the Remote | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-UC-016/2026-10-19-V3-1baac3de-remote.input_rename_live-uc.json` @ `1baac3dec660` (uc V3, remote.input_rename_live) | **yes** | yes | SW-UC-PREP |
| F-UC-017 | Restore the configuration at startup (also with the matrix offline) | V4 | V3 | V3 | — | — | **no committed record of any kind** | **yes** | yes | SW-UC-PREP |

### 5.8 Home Assistant component (18 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-HA-001 | Add the hub in Home Assistant (config flow) | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-002 | Choose each output's source (select entities) | V4 | V3 | V3 | — | stale | no fresh passing record; 6 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-003 | Matrix power switch | V4 | V3 | V3 | — | stale | no fresh passing record; 6 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-004 | Output audio mute switches | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-005 | Output stream enable switches | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-006 | Preset buttons | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-007 | Reboot button | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-008 | Input signal binary sensors | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-009 | Output connected binary sensors | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-010 | Service hdmi_matrix.recall_preset | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-011 | Service hdmi_matrix.switch_input | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-012 | Service hdmi_matrix.send_cec_command | V4 | V3 | V3 | — | stale | no fresh passing record; 9 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-013 | Poll the hub; entities go unavailable when it is unreachable | V4 | V3 | V3 | — | stale | no fresh passing record; 15 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-014 | Install through HACS (custom repository) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-HA-PREP |
| F-HA-015 | Device and entity naming in Home Assistant | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-016 | Change the hub address of a configured matrix (reconfigure flow) | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-017 | Polling interval option (options flow) | V4 | V3 | V3 | — | stale | no fresh passing record; 3 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |
| F-HA-018 | Services target one matrix (config entry or device) | V4 | V3 | V3 | — | stale | no fresh passing record; 6 stale record(s), commits `1baac3dec660`…`7dbc4dc70c70` | **yes** | yes | SW-HA-PREP |

### 5.9 Flic (10 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-FLIC-001 | Button click recalls a preset | V3 | V1 | V1 | — | stale | no fresh passing record; 2 stale record(s), commits `1baac3dec660`…`4adbc136a4c1` | **yes** | yes | SW-FLIC |
| F-FLIC-002 | Button hold powers the matrix off / on | V3 | V1 | V1 | — | stale | no fresh passing record; 4 stale record(s), commits `1baac3dec660`…`4adbc136a4c1` | **yes** | yes | SW-FLIC |
| F-FLIC-003 | Button powers a source on over CEC | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-FLIC-003/2026-10-19-V3-1baac3de-flic.source_power-flic.json` @ `1baac3dec660` (flic V3, flic.source_power) | no | yes | SW-FLIC |
| F-FLIC-004 | Flic Twist cycles an output through its inputs | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-FLIC-004/2026-10-19-V3-1baac3de-flic.cycle_next-flic.json` @ `1baac3dec660` (flic V3, flic.cycle_next) +2 more | no | yes | SW-FLIC |
| F-FLIC-005 | Flic Twist controls TV volume and mute over CEC | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-FLIC-005/2026-10-19-V3-1baac3de-flic.cec_output_navigation_refused-flic.json` @ `1baac3dec660` (flic V3, flic.cec_output_navigation_refused) +1 more | no | yes | SW-FLIC |
| F-FLIC-006 | Button recalls a profile or runs a macro | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-FLIC-006/2026-10-19-V3-1baac3de-flic.manual_macro-flic.json` @ `1baac3dec660` (flic V3, flic.manual_macro) +4 more | no | yes | SW-FLIC |
| F-FLIC-007 | Register Flic buttons with the hub (button registry) | V3 | V0 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-FLIC-007/2026-10-19-V3-1baac3de-flic.register-flic.json` @ `1baac3dec660` (flic V3, flic.register) | no | yes | SW-FLIC |
| F-FLIC-008 | Button switches every output to input N (POST /api/switch with JSON input) | V3 | V0 | V0 | — | stale | no fresh passing record; 2 stale record(s), commits `1baac3dec660`…`4adbc136a4c1` | **yes** | yes | SW-FLIC |
| F-FLIC-009 | Flic Hub SDK JavaScript module templates | V3 | V0 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-FLIC-004/2026-10-19-V3-1baac3de-flic.sdk_twist_next-flic.json` @ `1baac3dec660` (flic V3, flic.sdk_twist_next) +2 more | no | yes | SW-FLIC |
| F-FLIC-010 | Generate Flic request URLs in the web UI | V3 | V1 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-FLIC-003/2026-10-19-V3-1baac3de-flic.source_power-flic.json` @ `1baac3dec660` (flic V3, flic.source_power) +5 more | no | yes | SW-FLIC |

### 5.10 Deployment, configuration, persistence (20 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-OPS-001 | Run the hub from the Docker image | V4 | V3 | V3 | — | stale | no fresh passing record; 2 stale record(s), commits `b30436afd26e`…`b30436afd26e` | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-002 | Run the hub without the Remote integration (UC_ENABLED=false, the default) | V4 | V3 | V3 | — | stale | no fresh passing record; 1 stale record(s), commits `b30436afd26e`…`b30436afd26e` | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-003 | docker compose quick start | V4 | V3 | V3 | — | stale | no fresh passing record; 1 stale record(s), commits `b30436afd26e`…`b30436afd26e` | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-004 | Remote 3 discovery works from Docker | V4 | V2 | V2 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-005 | Container health check and auto-restart | V4 | V3 | V3 | — | stale | no fresh passing record; 2 stale record(s), commits `b30436afd26e`…`b30436afd26e` | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-006 | Point the hub at the matrix (MATRIX_HOST / MATRIX_PORT) | V4 | V3 | V3 | — | stale | no fresh passing record; 1 stale record(s), commits `b30436afd26e`…`b30436afd26e` | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-007 | Choose the API port (API_PORT) | V4 | V2 | V2 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-008 | Matrix credentials (OREI_USER / OREI_PASSWORD) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-009 | Verify the matrix TLS certificate (OREI_VERIFY_SSL) | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-010 | Log level (LOG_LEVEL) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-011 | Enable/disable integrations (UC_ENABLED) | V4 | V3 | V3 | — | stale | no fresh passing record; 2 stale record(s), commits `b30436afd26e`…`b30436afd26e` | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-012 | Background polling (POLLING_ENABLED / POLLING_INTERVAL) | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-013 | Telnet options (OREI_TELNET_PORT, OREI_USE_TELNET_CEC) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-014 | Cache and retry tuning (OREI_STATUS_CACHE_TTL, OREI_CEC_CACHE_TTL, OREI_*RETR*) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-015 | Hub data persists across restarts (DATA_DIR) | V4 | V3 | V3 | — | stale | no fresh passing record; 2 stale record(s), commits `b30436afd26e`…`b30436afd26e` | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-016 | Writes are atomic and safe under concurrency | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-017 | Migrate legacy data files (scenes -> profiles) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-018 | Only one hub instance runs (process lock) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-019 | One consistent version everywhere | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-OPS-020 | Multi-arch images (amd64 + arm64) | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |

### 5.11 Security controls (15 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-SEC-001 | Optional admin / control PIN gate | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-AUTH |
| F-SEC-002 | Cross-site request protection (CORS, Origin, Content-Type, Host allow-list) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-AUTH |
| F-SEC-003 | Matrix host changes cannot leak the matrix password (SSRF guard) | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-AUTH |
| F-SEC-004 | Profile/scene passcodes are stored as PBKDF2 hashes | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-DATA |
| F-SEC-005 | Passcode hashes are never sent to clients | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-DATA |
| F-SEC-006 | Changing or removing a PIN needs the current PIN | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-AUTH |
| F-SEC-007 | Wrong-PIN attempts are limited and do not stall the hub | V3 | V3 | V3 | — | fresh | `docs/validation/evidence/software-waves/W03-CLOSEOUT-20261028/combined/auth/F-SEC-007/2026-10-26-V3-310d8b65-sw_sec_auth_01.profile_allowed-browser.json` @ `310d8b65a9fc` (browser V3, sw_sec_auth_01.profile_allowed) +15 more | no | no | SW-SEC-AUTH |
| F-SEC-008 | Rate limiting per client | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-AUTH |
| F-SEC-009 | Proxy headers trusted only from configured proxies | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-AUTH |
| F-SEC-010 | Static files cannot escape the web root | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-DATA |
| F-SEC-011 | Error responses do not leak internals | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-DATA |
| F-SEC-012 | User-provided names are escaped in the UI (no XSS) | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-SEC-DATA |
| F-SEC-013 | TLS certificate verification / pinning for the matrix | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-DATA |
| F-SEC-014 | No credentials in logs | V3 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-SEC-DATA |
| F-SEC-015 | Remote 3 integration port requires authentication | V3 | V3 | V3 | — | — | **no committed record of any kind** | no | no | SW-SEC-AUTH |

### 5.12 Reliability (18 features)

| ID | Feature | Target | Recorded | Effective | Cap | Fresh | Proof binding | Gap (Eff<Tgt) | Declared (Rec≠Tgt) | Pkg |
| --- | --- | --- | --- | --- | --- | --- | --- | :---: | :---: | --- |
| F-REL-001 | Reconnect automatically after a matrix outage | V4 | V0 | V0 | — | stale | no fresh passing record; 8 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-002 | Report the connection state truthfully on errors and timeouts | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-003 | Detect a wrong matrix password | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-004 | Log in again when the matrix session expires | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-005 | Recover after the matrix reboots or is power-cycled | V4 | V0 | V0 | — | stale | no fresh passing record; 8 stale record(s), commits `1baac3dec660`…`d6baf3ca2574` | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-006 | Detect a dropped Telnet connection and reconnect | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-007 | Shut down and disconnect cleanly | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-008 | A command the matrix rejects is reported as failed | V4 | V0 | V2 | — | fresh | `docs/validation/evidence/ev02-original-api/F-REL-008/2026-10-19-V2-1baac3de-outputs.audio_mute_rejected-api.json` @ `1baac3dec660` (api V2, outputs.audio_mute_rejected) | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-009 | Matrix unreachable: commands fail visibly and no state is made up | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-REL-009/2026-10-19-V3-1baac3de-live.matrix_offline-browser.json` @ `1baac3dec660` (browser V3, live.matrix_offline) +1 more | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-010 | Status stays fresh (caches expire, one refresh at a time) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-011 | API calls are not blocked while the hub reconnects | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-012 | Background polling keeps state live without a Remote connected | V4 | V3 | V3 | — | fresh | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.front_panel_route-browser.json` @ `1baac3dec660` (browser V3, live.front_panel_route) | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-013 | The event loop never stalls (loop-lag metric) | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-014 | A slow WebSocket client cannot stall commands | V4 | V2 | V2 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-015 | Tolerate slow and malformed matrix responses | V4 | V1 | V1 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-016 | Standby does not start reconnect storms or duplicate pollers | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-017 | No leaked sessions, sockets or tasks after reconfiguration | V4 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-RUNTIME-PREP |
| F-REL-018 | 72-hour soak with flat memory, tasks and sockets | V5 | V0 | V0 | — | — | **no committed record of any kind** | **yes** | yes | SW-SOAK-PREP |

## 6. All 65 mapped units — author/reviewer/judge rematch

### 6.1 What is actually qualified right now

The adopted packet's per-unit reservations are **historical labels**. The repository's own current qualification state at this base is:

| Route | Current recorded state | Scope of the grant |
| --- | --- | --- |
| Anthropic `claude-opus-5-5` | `SCOPED_PASS` (one replacement attempt) | **Only** "bounded Python validation-runner/model offline simulator API refusal preparation and relevant compatibility guards". `generic_core_qualification: NOT_GRANTED`; `automatic_reservation_unlock: false`; `fresh_task_match_required: true`. Evaluated source `caaa4faa`, review base `938ae303`, evaluator report `1d49014b`, independent judge `gpt-6-astra/high` report `dda63d66`. The two earlier attempts remain **FAIL** with `qualified_domains: []`. |
| OpenAI `gpt-6.1-sol` / `gpt-6-astra` | No separate competence record in the current gate JSON | Historical reviews remain valid **within their recorded scope**. Sol and Astra are the **same underlying family** (OpenAI GPT): a Sol review of Astra's work, or an Astra review of Sol's work, is **not** a different-family review. |
| MiniMax `MiniMax-M3` | No competence-assessment record; assigned as the inventory/prose author | The adopted packet requires that the **coordinator, from a non-MiniMax family**, independently checks every MiniMax-specific attempt/contribution fact, and that a MiniMax fidelity review **cannot certify MiniMax's own eligibility**. |
| Gemini / Antigravity | **Unverified** — no confirmed native routing, helper behaviour, qualification or supported capacity |
| DeepSeek | **Unavailable** — owner reports exhausted credit; no dispatch, no fallback |

### 6.2 Rematch of the 65 units

`A→R` is the packet's `current_author_reservation → current_reviewer_reservation`. **Rematch** is this report's reading against the current qualification state, not a grant.

| # | Unit | Pkg | Phase | A→R | Rematch | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | SW-AUDIT-01 | SW-AUDIT | P0 | M3 → Sol | **inventory-ready** | prose/metadata only, no source, no tests, no tooling, no feature/competence gate; M3→Sol is a genuine cross-family pair for a prose deliverable, and the packet itself names SW-AUDIT-01 / SW-FINDINGS-01 / SW-REPO-01 / SW-DOCS-01 as the `independent_inventory_routes`. Canonical registry/ledger/summary edits stay with the coordinator. |
| 02 | SW-FINDINGS-01 | SW-FINDINGS | P0 | M3 → Sol | **inventory-ready** | prose/metadata only, no source, no tests, no tooling, no feature/competence gate; M3→Sol is a genuine cross-family pair for a prose deliverable, and the packet itself names SW-AUDIT-01 / SW-FINDINGS-01 / SW-REPO-01 / SW-DOCS-01 as the `independent_inventory_routes`. Canonical registry/ledger/summary edits stay with the coordinator. |
| 03 | SW-HARNESS-01 | SW-HARNESS | P0 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 04 | SW-API-READ-01 | SW-API-READ | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 05 | SW-API-READ-02 | SW-API-READ | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 06 | SW-API-READ-03 | SW-API-READ | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 07 | SW-API-READ-04 | SW-API-READ | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 08 | SW-SEC-AUTH-01 | SW-SEC-AUTH | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 09 | SW-SEC-AUTH-02 | SW-SEC-AUTH | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 10 | SW-SEC-AUTH-03 | SW-SEC-AUTH | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 11 | SW-API-WRITE-01 | SW-API-WRITE | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 12 | SW-API-WRITE-02 | SW-API-WRITE | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 13 | SW-API-WRITE-03 | SW-API-WRITE | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 14 | SW-API-WRITE-04 | SW-API-WRITE | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 15 | SW-SEC-DATA-01 | SW-SEC-DATA | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 16 | SW-SEC-DATA-02 | SW-SEC-DATA | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 17 | SW-API-CLIENT-01 | SW-API-CLIENT | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 18 | SW-API-CLIENT-02 | SW-API-CLIENT | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 19 | SW-DOM-PROFILE-01 | SW-DOM-PROFILE | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 20 | SW-DOM-PROFILE-02 | SW-DOM-PROFILE | P1 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 21 | SW-DOM-SCENE-01 | SW-DOM-SCENE | P2 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 22 | SW-DOM-MACRO-01 | SW-DOM-MACRO | P2 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 23 | SW-DOM-SHORTCUT-01 | SW-DOM-SHORTCUT | P2 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 24 | SW-DOM-SHORTCUT-02 | SW-DOM-SHORTCUT | P2 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 25 | SW-DOM-PRESENT-01 | SW-DOM-PRESENT | P2 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 26 | SW-UI-CONTROL-01 | SW-UI-CONTROL | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 27 | SW-UI-CONTROL-02 | SW-UI-CONTROL | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 28 | SW-UI-CONTROL-03 | SW-UI-CONTROL | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 29 | SW-UI-MANAGE-01 | SW-UI-MANAGE | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 30 | SW-UI-MANAGE-02 | SW-UI-MANAGE | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 31 | SW-UI-PRESENT-01 | SW-UI-PRESENT | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 32 | SW-UI-PRESENT-02 | SW-UI-PRESENT | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 33 | SW-KIOSK-CONTROL-01 | SW-KIOSK-CONTROL | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 34 | SW-KIOSK-CONTROL-02 | SW-KIOSK-CONTROL | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 35 | SW-KIOSK-STATE-01 | SW-KIOSK-STATE | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 36 | SW-KIOSK-STATE-02 | SW-KIOSK-STATE | P2 | Sol → Opus after Q-UI-A and exact kiosk/UI domain fit | **needs unused first assessment** + qualification + capacity | the reserved reviewer is "Opus after Q-UI-A and exact kiosk/UI domain fit". Q-UI-A is **not launched, not assigned a Task and not qualified**; Opus 5.5's scoped PASS does **not** cover UI/kiosk. The reserved `Q-UI-M3` alternative is likewise only a named reservation. This unit therefore also needs the FC-PROVENANCE unused-attempt/contribution/role audit before any assessment, and a fresh pool observation at dispatch. |
| 37 | SW-FLIC-01 | SW-FLIC | P2 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 38 | SW-FLIC-02 | SW-FLIC | P2 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 39 | SW-PROTOCOL-PREP-01 | SW-PROTOCOL-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 40 | SW-PROTOCOL-PREP-02 | SW-PROTOCOL-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 41 | SW-PROTOCOL-PREP-03 | SW-PROTOCOL-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 42 | SW-PROTOCOL-PREP-04 | SW-PROTOCOL-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 43 | SW-PROTOCOL-PREP-05 | SW-PROTOCOL-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 44 | SW-PROTOCOL-PREP-06 | SW-PROTOCOL-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 45 | SW-PROTOCOL-PREP-07 | SW-PROTOCOL-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 46 | SW-RUNTIME-PREP-01 | SW-RUNTIME-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 47 | SW-RUNTIME-PREP-02 | SW-RUNTIME-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 48 | SW-RUNTIME-PREP-03 | SW-RUNTIME-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 49 | SW-RUNTIME-PREP-04 | SW-RUNTIME-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 50 | SW-RUNTIME-PREP-05 | SW-RUNTIME-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 51 | SW-RUNTIME-PREP-06 | SW-RUNTIME-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 52 | SW-RUNTIME-PREP-07 | SW-RUNTIME-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 53 | SW-UC-PREP-01 | SW-UC-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 54 | SW-UC-PREP-02 | SW-UC-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 55 | SW-UC-PREP-03 | SW-UC-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 56 | SW-HA-PREP-01 | SW-HA-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 57 | SW-HA-PREP-02 | SW-HA-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 58 | SW-HA-PREP-03 | SW-HA-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 59 | SW-DOM-HIL-PREP-01 | SW-DOM-HIL-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 60 | SW-SOAK-PREP-01 | SW-SOAK-PREP | P3 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 61 | SW-REPO-01 | SW-REPO | P4 | M3 → Sol | **inventory-ready** | prose/metadata only, no source, no tests, no tooling, no feature/competence gate; M3→Sol is a genuine cross-family pair for a prose deliverable, and the packet itself names SW-AUDIT-01 / SW-FINDINGS-01 / SW-REPO-01 / SW-DOCS-01 as the `independent_inventory_routes`. Canonical registry/ledger/summary edits stay with the coordinator. |
| 62 | SW-DOCS-01 | SW-DOCS | P4 | M3 → Sol | **inventory-ready** | prose/metadata only, no source, no tests, no tooling, no feature/competence gate; M3→Sol is a genuine cross-family pair for a prose deliverable, and the packet itself names SW-AUDIT-01 / SW-FINDINGS-01 / SW-REPO-01 / SW-DOCS-01 as the `independent_inventory_routes`. Canonical registry/ledger/summary edits stay with the coordinator. |
| 63 | SW-VERSION-01 | SW-VERSION | P4 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 64 | SW-BUILD-01 | SW-BUILD | P4 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |
| 65 | SW-SOFTWARE-GATE-01 | SW-SOFTWARE-GATE | P5 | Sol → M3 after exact relevant domain PASS; no automatic broad source entitlement | **qualification** + provenance + capacity | the reserved reviewer is "M3 after exact relevant domain PASS; no automatic broad source entitlement". MiniMax has **no** recorded domain PASS for this scope, so the reviewer reservation is unmet; the Opus 5.5 scoped PASS does not cover these domains either. The unit additionally depends on `QUAL-ANTHROPIC-CORE-01` in its frozen dependency list and on FC-PROVENANCE for the author's actual attempt/contribution/role record, and on a fresh pool observation at dispatch. |

### 6.3 What the rematch does and does not say

* **4 units are inventory-ready now**: `SW-AUDIT-01`, `SW-FINDINGS-01`, `SW-REPO-01`, `SW-DOCS-01`. All four are `domain: inventory`, `owner_gate: false`, no feature IDs and no source. They are the only units whose deliverable is prose/registry metadata rather than implementation, which is precisely why they need no new competence assessment.
* **11 units are blocked on an unused first assessment** (`Q-UI-A`, `Q-UI-M3`) plus qualification and capacity.
* **50 units are blocked on qualification, provenance and capacity.** Their reviewer reservation names M3 *after an exact relevant domain PASS* that does not exist in any record at this base.
* **No unit of the 65 carries `owner_gate: true`.** The seven human-owner gates are separate entries in `docs/planning/software-waves/EXECUTION_PINS.json` and are **not** among the 65 mapped units. Owner conditions do attach to *findings* though — API-07 (catalogue visual diff), SEC-14 (GitHub-Support cache purge), UC-11/UC-12/UC-13 (the DI-9 direction), UC-28 and HIL-14 (physical), and the privacy budget request — and those remain open.
* **Dependency state is inherited, not re-derived.** Every non-inventory unit's frozen dependency list still names `QUAL-ANTHROPIC-CORE-01` and/or other units that have not completed. Dependency satisfaction is a coordinator fact; this report does not assert it.
* **Historical Claude/Astra labels are not current eligibility.** The accepted historical reviews keep their recorded scope and attribution; they do not confer eligibility for these units now, and a same-family pair (Sol ↔ Astra) can never discharge the different-family gate.
* **Capacity is a dispatch-time condition for every row**, not a property of the unit. No quota observation was taken by this package and none is claimed.

## 7. Stale current gate / summary prose — proposed coordinator updates

These are **proposed** edits for the coordinator to apply after qualified different-family review of this report. The coordinator owns the canonical files; this package changed none of them. Historical records are **not** to be rewritten — only dated current summaries are to be corrected, with the superseded text retained and labelled.

| # | File and field | Current text (verbatim) | Why it is stale at `a07cf94` | Proposed update |
| --- | --- | --- | --- | --- |
| 1 | `docs/planning/software-waves/EXECUTION_GATE_STATUS.json` → `remediation_authority.state` | *"wave1 active: NEW bounded WS component authorship assessment and planned API-review evaluation"* | The WS component is **integrated** (`e54228c0`, an ancestor of this base) and the API-review evaluation is **complete and accepted for report quality only** (`c3fcace6`, `EVALUATION.md`). The field describes a wave-1 state that has moved on. | Replace with a dated statement of the current state, e.g. *"wave1 component integrated and reviewed (unwired); API-review evaluation accepted (report quality only); source admission, wiring, privacy chain and candidate proof still held"* — and keep the old string in a dated `historical_*` field rather than deleting it. |
| 2 | `docs/planning/software-waves/EXECUTION_GATE_STATUS.json` → `owner_decision_pending` | *"Bounded privacy reassessment budget proposal requires explicit owner approval; current exhausted attempts remain terminal/no automatic retake. Separate physical/visual/final release gates remain."* | This is **substantively correct** and must not be weakened: the extra privacy attempt is still owner-pending and both exhausted attempts are terminal. The staleness flagged by the audit is only that it sits next to a *completed* qualification elsewhere in the same file, which can read as if the qualification itself were pending. | Keep the text; add a sibling field naming **which** decision is pending (the privacy budget proposal only) so it cannot be read as covering the completed Opus 5.5 scoped qualification. Do not ask the owner again for an approval that is already recorded. |
| 3 | `docs/planning/software-waves/EXECUTION_READINESS.md` → the 85-entry reservations table (from the earlier execution-pinning plan) | Rows such as `SW-RUNTIME-PREP-01 \| P3 \| astra / claude` and the reviewer column `claude` throughout | The **adopted** functional-completion packet `933166c3…` re-staffs the 65 units to `Sol` as author and `M3 (after an exact relevant domain PASS)` as reviewer, with `Opus after Q-UI-A` for the 11 UI/kiosk units. The readiness table therefore shows a **different reservation set** from the governing packet. | Add a dated note above the table stating that the table records the *execution-pinning* plan's reservations and that the adopted `functional-completion-20261104` packet supersedes the staffing column; keep the older table intact as history. |
| 4 | `docs/agent-process/REPO_CONFIG.json` → `readiness.current_values` | `below_target: 203`, `stale: 57`, `source: "Last accepted wave02 ledger; wave03 qualification/evidence not yet applied."` | The value is **accurate for its stated snapshot** but is being read in circulation as the current count, alongside 210 and 228. `stale: 57` is a different population again (a stale-evidence count at the wave02 ledger, not the 96 stale-only features at this base). | Keep the values and the `source` note (they are honest history), and add an explicit `superseded_by` / `current_measurement` pointer naming the current base and its rule so 203/57 cannot be quoted without their date and definition. |
| 5 | `docs/validation/LEDGER.md` (generated) | *"Commit `28fce729`"* and the summary block | The committed ledger is **current in its totals** (210 / 96 / 70 fresh-passing / 0 fresh-failing / 12 capped reproduce exactly at this base) but its header commit is older than HEAD. | Do **not** hand-edit the generated ledger. If a refreshed ledger is wanted, the coordinator regenerates it serially with the canonical command; this package did not and must not. |
| 6 | `docs/REMEDIATION_PLAN.md` §4 register text (many rows) | e.g. SEC-14 *"LICENSE is a stub"*; SEC-15 *"CI actions tag-pinned"*, *"base image not digest-pinned"*; DEP-05 *"no `pull_request` trigger"*, *"ruff only on `src/`"*, *"no hassfest/HACS validation"*, *"no gitleaks"*, and its cited workflow path; UI-16 *"no reduced-motion check"*; BE-26 *"~62 `range(1, 9)` / `[0]*8`"*; TST-03 *"No tests: …"*; TST-04 *"No JS tests of any kind"*; API-07's location anchors; several UI line anchors | Each clause is contradicted by the current source, as recorded in §4.2/§4.3. These are **register-text** inaccuracies, not new defects and not closures. | Text-only reconciliation of the affected cells, keeping every original assertion visible and dated. Per the pending-YAML header, a closed row is renamed into the register and its `features.yaml` / scenario `finding=` links updated. This package proposes that; it does not apply it. |
| 7 | `docs/REMEDIATION_PLAN.md` §4 HIL-09 row | Description cell begins *"✅ Fixed and proven on hardware 2026-09-25 …"* while the phase cell says *"open until the capture tool's write run proves them on hardware"* | The two cells contradict each other, and the first is **not** a hardware proof. The row is the sole cap for 12 features. | Text reconciliation so the row stops asserting a hardware proof it does not have, **keeping the row open and keeping all twelve caps** until the capture-tool write run with read-back exists. |

## 8. New source-backed residual findings (not duplicate implementation)

These are **source-backed residuals** that no existing parser-open row states in current form. Each is reported as a finding lead with the smallest possible follow-up scope and the exact acceptance that would discharge it. **No implementation is proposed or made here**, and none of these is a duplicate of an existing corrective package.

| # | Residual | Source evidence at `a07cf94` | Smallest follow-up scope | Exact acceptance | Independent review needed |
| --- | --- | --- | --- | --- | --- |
| R-01 | The **228** peer numerator is not reproducible from the registry it claims to summarise, while its adjacent counts are. | `docs/validation/features.yaml` is byte-identical between `9b783d72` and `a07cf94`; an independent parse yields 227 rows with `current != target` and 227 with `current < target`, 0 above target; the peer's 268/50/33 counts reproduce exactly. | A read-only arithmetic re-derivation by the MiniMax fidelity reviewer, plus a coordinator note recording the verified numerator. | The published numerator for `current != target`, its denominator (268), its date and its definition, with the verified 227/268 stated. | Not a new implementation — a factual cross-family check by the M3 fidelity reviewer and the coordinator. |
| R-02 | The retained **privacy C2 commit object is absent** from the local object database while both refs still point at it. | `refs/heads/ryan-haver/wp-sec-data-02-c2` and `refs/remotes/origin/ryan-haver/wp-sec-data-02-c2` → `615d3c8403b237dd117c803269c7b9b58895f9217`; `git cat-file -t` → *Not a valid object name*; the repository is not a partial clone. | A coordinator-side object restore from the existing remote ref, then a content verification of C2. **No worker may fetch, prune or rewrite history.** | The C2 commit object resolves and its tree matches the recorded C1→C3 chain, with the fetch receipt recorded. | No — object restoration and verification is coordinator work, not a new deliverable. |
| R-03 | The register's **line anchors** for at least six findings no longer point at the content they name. | `system_shortcuts.py:22-34` / `orei_matrix.py:1972` (API-07); `web/js/app.js:74-78` and `dashboard-manager.js:71,1102,1126` (UI-08); `hardware-drawer.js:145-178` and `web/index.html:352-598` (UI-05); `cec-tray.js:1468-1580` (UI-12); `api-copy.js:13` (UI-18); `overlay-manager.js:35-46` (UI-15); `scene-editor.js:263-278` (UI-19); `config.py:221,486` (API-12); `utils.py:388-395` (API-18); `driver.py:60` (DEP-07). | Text-only re-anchoring of the register's location cells to current lines, with the original anchors retained as dated history. | Every re-anchored cell names a file and line that exist at the stated base and carry the named content. | Text-only change to a register cell — not a new implementation deliverable. |
| R-04 | The register's **TST-03/TST-04 'no tests' claims** are stale in their literal form but are being used as if they were coverage gaps. | `tests/` contains 151 occurrences of `api/v2/scenes`, 91 of `/api/integrations`, 40 of `/api/settings`, 7 of `_task_supervisor`; `tests/e2e/` carries six Playwright `.spec.ts` files; there are **0** JavaScript unit-test files outside `tests/e2e`. | A bounded per-surface assertion inventory under `SW-AUDIT-01` (already an inventory unit) to decide, per named surface, whether the assertion is adequate — **not** new test authorship. | For each named surface: the test file, the test name, the asserted behaviour and the client/level it actually proves, or an explicit *missing assertion* decision. | Prose inventory; the independent reviewer checks the inventory's claims against the test source. |
| R-05 | The **accepted UNWIRED WS component** is integrated and reviewed but not wired, so CR-01's bounded admission/cleanup behaviour is not in the product path. | `e54228c0` added `src/rest_api/ws_request_work.py` (519 lines) and `tests/test_ws_request_work.py` (1502 lines); the module is imported by **no** file under `src/`, `run.py` or `run_server.py`. | The **existing** WS wiring package — `FC-WS-WIRE` in the adopted packet — which is a separate source package with its own author/reviewer/lease requirements. This report only records that the component is unwired. | The adopted `FC-WS-WIRE` acceptance at the exact wiring commit, including bounded outstanding work, a defined overload response, connection/application-owned cleanup, preservation of the status schema and fresh-read semantics, and proof that another client's service survives a burst. | Yes — qualified different-family exact-commit source review (the packet's `FC-WS-WIRE` row). |

**Deliberately not reported as new findings.** CR-01 (unbounded per-frame WebSocket task creation), CR-02 (HA setup does not establish that a supplied key can control a locked hub), CR-03 (keyboard shortcuts), CR-04 (credential redaction), CR-06 (API-C2 invalidates the F-SEC-007 V3 proof), CR-07 (CI proof names a synthetic PR merge), CR-10 (declared minimum versions exceed the demonstrated matrix) and CR-11…CR-14 are **already recorded** in `docs/audits/COMPREHENSIVE_PROJECT_REVIEW_20261104.md` with their own dispositions; repeating them here would duplicate an existing record rather than add truth. Where this report touches them it does so only to carry their recorded status forward (R-05, M-1, CI attribution).

## 9. Owner questions — only where a controlling rule requires one

| # | Question | Controlling rule | Why it is still required |
| --- | --- | --- | --- |
| O-1 | Authorise (or decline) one additional prepared controlled privacy assessment attempt and its single fresh judge. | `docs/production/remediation-20261104/recovery-execution/PRIVACY_REASSESSMENT_BUDGET_REQUEST.json` is recorded `OWNER_APPROVAL_REQUIRED / proposal only, no worker or attempt launched`; the repository's standing protocol says an exhausted/failed attempt budget needs explicit owner authority and that elapsed time infers no approval. | The Opus 5.5 attempt is a **terminal FAIL** and the MiniMax attempt is a **terminal FAIL** with its one candidate and one judge consumed; `automatic_retakes` is `false`. The chain cannot advance on this package. This question is **carried forward unchanged** — it is not re-asked, and nothing in this report is waiting on the answer to proceed. |
| O-2 | Approve the visual diff of the affected catalogue entries for the LCD shortcut rename (API-07's own recorded close condition). | The register row's exact close condition: *"close once the owner approves the visual diff of the affected catalog entries"*. The repository's owner visual-approval rule applies to changed rendering. | The WP-C1 rename to "LCD: 15s" is recorded as owner-approved with the legacy key retained, but the row's own close condition is recorded separately and is **not** discharged by this inventory. |
| O-3 | Owner action: GitHub-Support cache purge of the public history for SEC-14. | SEC-14's recorded owner condition (vendor-blob history purge); the public-history purge verification was **inherited**, not re-run here, and this package has no exhaustive public-history or secret-scan authority. | The tracked tree no longer carries the vendor payloads and LICENSE is the full MPL 2.0, but the *public-history* element is an owner/support action. |

**No other owner question is required by this package.** Kiosk zoom is a technical design choice within existing scope; only a *changed* rendering needs a visual decision. Software viewport probes may run; actual-device confirmation is a separate gate. The compatibility floor, the physical HIL windows, the continuous 72-hour soak, the field week, the final version/artifact matching and release authority all stay open and untouched by this inventory.

## 10. Acceptance, non-acceptance and what remains

### 10.1 What this package does

* Publishes the recomputed parser-open set (**61**, with its **59 + 2** composition and severity distribution) and a per-ID original assertion, surviving condition, current source/client/image/proof reference, assertion strength and recommendation for **every** one of them.
* Publishes the full **268**-feature contract table with recorded, target, effective, owner-capped level, freshness, proof binding and package binding.
* Publishes the full **65**-unit author/reviewer/judge rematch against the actually recorded qualification state.
* Reconciles **228 / 210 / 203 / 227** with explicit definitions, numerators, denominators, dates, the ordered level ladder, the twelve caps and the two over-achievements.
* Names the stale current-summary prose and proposes precise coordinator updates without applying any of them.
* Reports five source-backed residuals with the smallest follow-up scope and exact acceptance, without implementing anything.

### 10.2 What this package does not do

* It closes **no** finding and proposes **no** mass closure.
* It promotes **no** feature level and changes **no** registry, ledger, register or pending row.
* It generates **no** ledger and calls **no** gate.
* It admits **no** evidence and relabels **no** PR merge or green CI as closure.
* It awards **no** competence, dispatches **no** worker and launches **no** assessment.
* It removes **none** of HIL-09's twelve caps, and it does not call UC-18 or the LICENSE-stub prose a current reproduced defect.
* It grants **no** owner, hardware, visual, soak, field, version, artifact or release approval.
* It does not publish, push, merge, tag, release or clean up anything.

### 10.3 What remains open

| Gate | State |
| --- | --- |
| Qualified different-family review of **this** report | **Required and not done.** The reserved reviewer route is OpenAI `gpt-6.1-sol/high`. This report is not self-accepted. |
| Coordinator application of the proposed canonical edits | **Not done** — §7 proposals only. |
| RV-API034 source admission and the M-1 F-SEC-007 freshness diagnosis | Open (separate scope). |
| RV-WS040 retained-source review | Open (separate scope). |
| Privacy chain C1–C4 qualified review, privacy admission and register reconciliation | Open; the chain is unintegrated and C2's object is locally missing. |
| WS component wiring (`FC-WS-WIRE`) | Open; the component is integrated and unwired. |
| Owner privacy-budget request | Pending owner answer; carried forward unchanged. |
| Physical HIL-B/C/E, continuous 72-hour soak, field week, final version/artifact matching, release | Open. |

## 11. Verification method for this report (declared before the run)

This package is **pure prose and new metadata**. The applicable check is the repository's own documentation check set, run **once**, after this file's final prose bytes, from this checkout.

* Interpreter: `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -B` (absolute path, `-B` to disable bytecode).
* The **five existing documentation modules**: `tests/test_core_documentation.py`, `tests/test_client_guides_docs.py`, `tests/test_openapi_and_config_docs.py`, `tests/test_security_docs.py`, `tests/test_license_and_protocol_docs.py`.
* Plugin suppression as instructed: `-p no:tests.route_inventory -p no:cacheprovider` (the route-inventory plugin would overwrite the shared coverage report; this package makes **no** route-coverage claim).
* Environment: the child **inherits the Windows environment** and then receives a fresh owned overlay — `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`, `HIDDEN_TEMP`, `--basetemp` and `--junitxml` all under `C:/t/remediation-functional/fc-truth/**`; `PYTEST_ADDOPTS`, `PYTEST_PLUGINS` and `PYTHONPATH` dropped; `PYTHONDONTWRITEBYTECODE=1`; `PYTHONNOUSERSITE=1`.
* Captured: direct argv, working directory, UTC start/end, the child's own exit code, full stdout and stderr streams, the JUnit file, the **in-run** module/import origins measured inside the pytest process, and the owned-root ordinary and hidden file inventory before and after.
* **Before the commit**: strict UTF-8 decode of this file, a local-target/anchor link check, `git -c core.whitespace=cr-at-eol diff --check`, and an exact staged-scope check that only this new report is staged. The commit uses the authorised **invocation-only empty `core.hooksPath`** exception for a pure-prose commit; **no** repository or global hook configuration is changed and **no** source-hook or full-suite success is claimed.

**What the run does and does not prove.** The documentation modules exercise the *checkout's* documentation and some local REST code. They do **not** prove that this new Markdown file was parsed by any test (none of the five modules globs `docs/` or any Markdown file), and they do **not** prove a feature level, a source qualification, a model qualification or a canonical route check. The actual measured outcome is recorded in §12, which was appended **after** the run; the bytes of §12 itself were not exercised by the run and were only scope/UTF-8/whitespace checked.

## 12. Post-run verification record (appended after the single run)

**This section was written after the one documentation run.** Its own bytes were **not** exercised by that run; they were checked for scope, UTF-8 validity and whitespace only (§12.4). Nothing here retroactively extends the run's coverage to these paragraphs.

### 12.1 Invocation actually used

| Item | Value |
| --- | --- |
| Interpreter | `C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe` with `-B` |
| Python | 3.12.10 |
| Working directory | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-truth` |
| Checkout under test | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-truth` |
| Run id | `fc-truth-20261104T190000Z` |
| UTC start | `2026-11-04T19:26:59.902704+00:00` |
| UTC end | `2026-11-04T19:27:03.679941+00:00` |
| Wall time inside the entry script | 3.782 s |
| Direct child exit code | **0** |

Direct argv handed to `pytest.main` (13 elements):

```
tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -q -p no:tests.route_inventory -p no:cacheprovider --basetemp=C:/t/remediation-functional/fc-truth/fc-truth-20261104T190000Z/temp/pytest-tmp --junitxml=C:/t/remediation-functional/fc-truth/fc-truth-20261104T190000Z/out/junit.xml
```

The repository's own `pyproject.toml` `addopts` are prepended by pytest **in place**, so the argument list observed inside the process after the run begins with the repository's default marker filter. That filter is the repository default, not an addition by this run, and nothing was deselected (the JUnit records 489 tests).

Environment: the child **inherited the Windows environment** and then received this fresh owned overlay; `PYTEST_ADDOPTS`, `PYTEST_PLUGINS` and `PYTHONPATH` were dropped.

| Variable | Value |
| --- | --- |
| `MATRIX_DATA_DIR` | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\temp\matrix_data_dir` |
| `UC_CONFIG_HOME` | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\temp\uc_config_home` |
| `TEMP` | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\temp\temp` |
| `TMP` | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\temp\tmp` |
| `TMPDIR` | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\temp\tmpdir` |
| `HIDDEN_TEMP` | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\temp\hidden_temp` |
| `PYTHONDONTWRITEBYTECODE` | `1` |
| `PYTHONNOUSERSITE` | `1` |
| `PYTEST_ADDOPTS` | *dropped* |
| `PYTEST_PLUGINS` | *dropped* |
| `PYTHONPATH` | *dropped* |

### 12.2 Measured outcome

| Measure | Value |
| --- | --- |
| pytest summary | **489 passed**, 0 failed, 0 errors, 0 skipped, 0 xfailed, 0 deselected (`489 passed in 3.34s`) |
| Direct child exit code | **0** |
| stdout | 596 bytes on disk / 588 characters (CRLF written by the text stream), SHA-256 `2dcb5860e064bc3380e2a30716ec0094a1cecbdc82372a23dbcb74945b00ba18` |
| stderr | **0 bytes** (empty), SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (the SHA-256 of the empty string) |
| JUnit | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\out\junit.xml` — 63691 bytes, SHA-256 `63ae82718745bfdfb9762f8289105bfb96ff4897fef7b467da109bd39b3638e6` |
| JUnit counters | tests **489**, failures **0**, errors **0**, skipped **0** |
| Entry receipt | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\out\docs_result.json` — 87313 bytes, SHA-256 `08f970c723edbeccc026fc7c3770d3b4a97ae35c56322a789d8177bfde8e5ed0` |
| Owned-root inventory | 36 files / 3473181 bytes before → 145 files / 3737360 bytes after |

The full streams, the JUnit file, the in-run import capture and both owned-root inventories (ordinary **and** hidden files, with per-file SHA-256) are preserved under the owned roots:

| Artefact | Path |
| --- | --- |
| stdout | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\out\stdout.txt` |
| stderr | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\out\stderr.txt` |
| JUnit | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\out\junit.xml` |
| Entry receipt (argv, cwd, env, UTC, exit, imports) | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\out\docs_result.json` |
| Run summary | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\out\run_summary.json` |
| Pre-run owned inventory | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-truth\build\remediation-functional-20261104\fc-truth\owned_inventory_pre-run.json` |
| Post-run owned inventory | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-truth\build\remediation-functional-20261104\fc-truth\owned_inventory_post-run.json` |
| pytest basetemp | `C:\t\remediation-functional\fc-truth\fc-truth-20261104T190000Z\temp\pytest-tmp` |

### 12.3 In-run module and import origins

Measured **inside** the pytest process after `pytest.main` returned (the same snapshot is taken at interpreter exit):

| Module | Origin |
| --- | --- |
| `tests.conftest` | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-truth\tests\conftest.py` |
| `hub` | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-truth\src\hub\__init__.py` |
| `hub.openapi` | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-truth\src\hub\openapi.py` |
| `pytest` | `C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Lib\site-packages\pytest\__init__.py` |

| Observation | Value |
| --- | --- |
| Product imports under `src.rest_api` / `tools.validate` observed | **0** |

So this run exercised the **documentation modules of this checkout** (`tests.conftest`, `hub` and `hub.openapi` resolved inside this worktree) together with `pytest` from the root virtual environment. It did **not** import `src/rest_api/*` or `tools/validate/*`. It is therefore a documentation-module prose check of *this* checkout — **not** a product-behaviour result, **not** a feature-level result, **not** a model-qualification result and **not** a canonical route check (the route-inventory plugin was deliberately disabled, so no route-coverage number is claimed).

### 12.4 Post-append scope, encoding and whitespace checks

After appending this section and §13, the following were checked on the **final** bytes of this file: strict UTF-8 decode; every relative Markdown link target in the file resolves to an existing path in this checkout; `git -c core.whitespace=cr-at-eol diff --check` reports no whitespace error; and the staged scope contains **only** this new report. These checks cover the appended bytes for scope/encoding/whitespace only — they do **not** re-run the documentation modules and do **not** claim that any test parsed this file. None of the five documentation modules globs `docs/` or any Markdown file, so no new-Markdown-parsing claim is made.

### 12.5 What the run deliberately did not do

* No second run, no retry, no softened assertion, no skipped test counted as a pass, no unchanged failed check re-run.
* No ledger generation, no `tools.validate check`, no canonical gate, no evidence import, no source hook, no campaign, no browser, no container, no device.
* No global or repository configuration change of any kind; no second scratchpad; no shared system `TEMP` inventory was taken.

### 12.6 Post-run prose correction (declared, not covered by the run)

After the single run, **one** path citation was corrected: §9 O-1 now names `docs/production/remediation-20261104/recovery-execution/PRIVACY_REASSESSMENT_BUDGET_REQUEST.json`, which is where that file actually lives at this base; the earlier string omitted the `recovery-execution/` segment. This is a **citation-string correction only** — it changes no question, no owner condition, no disposition and no count. The corrected bytes were checked for scope, UTF-8 validity and whitespace only, exactly like the appended sections. **The run did not cover them, and this report makes no claim that it did.**

## 13. Storage receipt

This package's disposable output is confined to two owned roots. No other location on the host was written by this task, and no other agent's output, cache, workspace, evidence archive, baseline or protected resource was read, moved or removed.

| Root | Role | Files | Approx. bytes | Disposition |
| --- | --- | ---: | ---: | --- |
| `build/remediation-functional-20261104/fc-truth/**` | owned, git-ignored | 38 | 3484439 | **retained** — the private metadata-only extraction helpers, the authored disposition table, the in-run receipt copies and the owned-root inventories are the audit trail for this report and are retained for the reviewer |
| `C:/t/remediation-functional/fc-truth/fc-truth-20261104T190000Z/**` | owned, fresh per invocation | 107 | 252921 | **retained** — stdout/stderr/JUnit/entry receipt are the raw proof of the one run; the pytest basetemp contents are **disposable** and may be removed by the coordinator |

| Item | Value |
| --- | --- |
| Bytes created by this task (owned roots, measured) | 3737360 (pre-run {inv_pre['grand_total_bytes']} → post-run {inv_post['grand_total_bytes']}) |
| Bytes retained and why | the owned roots above, as the review trail and the raw run proof |
| Quarantined | none — this package performed no deletion and has no deletion authority |
| Actually removed | **nothing**. No file, directory, worktree, branch, ref, cache or archive was deleted, truncated or rewritten by this task. |
| Output left outside the owned roots | **none**, except the single intended tracked deliverable `docs/production/functional-completion-20261104/FC-TRUTH/INVENTORY.md` |
| Expiry / review date | the owned roots are retained until the coordinator settles this task and reviews this report; the disposable pytest basetemp may be removed at that point |
| Diagnostic budget | far below the 100 MiB default per-task diagnostic budget |

The size and SHA-256 of this report, its commit and its parent are recorded in this task's separate completion receipt rather than here, so that this file does not contain a self-referential hash.

