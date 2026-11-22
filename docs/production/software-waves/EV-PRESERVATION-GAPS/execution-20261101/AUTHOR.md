# EV-PRESERVATION-GAPS — bounded disposition of two historical preservation gaps

| Field | Value |
| --- | --- |
| Task / Dispatch | `task_9456469c267b` / `ctx_f2864b9be31e` |
| Run | `run_37205f6095b3` (existing Run; not reset or replaced) |
| Worker terminal | `term_5c3e6c60-992b-4c1a-ad7b-739388adcab3` |
| Coordinator terminal | `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| Runtime / Orca | `e8ce3460-a9d4-4897-8e4f-10a8e3cdc400` / 1.4.246 |
| Worktree | `wp-exec-ev-preservation-gaps` (dedicated, Windows Orca) |
| Branch | `execution/wp-exec-ev-preservation-gaps` |
| Exact base (injected, verified) | `f2dc1dbf683d8f96200d1517b0786e3441105b36` |
| Required ancestor floor | `e2161484459da65aee14433136a14963507b499c` (verified ancestor of the base) |
| Author route | native MiniMax-M3 via OpenCode 2 (project-pinned model; no CLI model/effort override) |
| Date of this record | 2026-11-02 local (−07:00) / 2026-11-03 UTC |
| Delivery class | bounded inventory/prose documentation only — no implementation, test or tool |

---

## 1. Scope, and what this report is not

This report dispositions **exactly two** known historical preservation gaps, both
named in the accepted pins for this unit:

1. the **lost original API-C1 managed-failure artifacts**, and
2. the **overwritten original SW-AUDIT freshness scratch extracts**.

Nothing else is dispositioned. In particular this report **does not**:

* reconstruct, re-create, approximate or substitute any missing historical byte;
* call preservation acceptance **passed**, or accept any original evidence or
  function proof for either gap;
* re-open, re-score or re-audit the accepted triage, the accepted controller /
  header workspaces, or the accepted evidence;
* re-run any managed failure, qualification, validation campaign, ledger or gate
  generation, source/core/client/image/physical test, recovery probe or cleanup;
* close a product or security finding, promote a level, or approve a
  source / privacy / owner / release gate;
* grant, imply or canonicalize a waiver. The author cannot accept this report;
  an **independent OpenAI-family factual review at the exact report commit** is
  required, and the coordinator owns the canonical ledger, registry, integration
  and every cleanup decision.

**Accepted negative-gap disposition versus accepted original evidence/function
proof.** What follows is a *negative* disposition: two losses are recorded as
losses, with the surviving material separated from the material the accepted
records disposition as irrecoverable and from what remains unverifiable. It is **not** an acceptance of the two
histories, of the artifacts they produced, or of the behaviour they exercised.
The two must never be read as one: "the gap is disposed" never means "the
original evidence was accepted" and never means "the original function was
proved".

**No new runtime, campaign, qualification or recovered-original evidence was
produced, in this correction round or the original attempt.** No managed
failure, validation campaign, gate, ledger generation, registry check,
source/core/client/image/physical test, recovery probe of the lost material,
cleanup, push, merge or release ran, and no historical original was recovered,
reconstructed or substituted. Two kinds of **new inspection metadata** were
created and are described in §7–§8 and §9: bounded **read-only** hash /
existence / Git-provenance inspection artifacts (byte-extraction receipts, an
existence-and-identity probe and a Git provenance proof), and
**documentation-check** artifacts (the five existing documentation modules'
own receipts plus the report-only UTF-8/CR-aware/reference checks). The **only
test invocation** in each recorded round was the five existing documentation
modules (§7.1, §9.3); the metadata commands were read-only inspection, not
tests.

---

## 2. Two-row summary

| # | Gap | Event, actor, Task/Dispatch, source/report | Accepted recorded failure and limit | Surviving originals (demonstrably retained) | Irrecoverable | Unverifiable / unknown | Acceptance and cleanup consequence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **G1** | **Lost original API-C1 managed-failure artifacts** | SW-API-CLIENT-02-C1 declarative-assertion follow-up (F-API-034 only). OpenAI `gpt-6.1-sol/high` author, Task `task_c0d26e9e563e`, Dispatch `ctx_0f27082dc4eb`, Run `run_37205f6095b3`, worker terminal `term_0b99c857-414e-4891-ae63-768327f92812`. Worktree `wp-api-client-02-c1`, branch `ryan-haver/wp-api-client-02-c1`, frozen base `938ae30339790c361abdda6fdd01b11a4e498518`. Source `386872316cb60130b06dd704557ae6ca1a92b5c8`; report `060769b724e7a546b8df22eac82f3b288d9bbbe8` (report-only, one path). | First focused invocation exited **1** with 12 passed / 1 failed: the managed source runner BLOCKED because it requires a healthy Telnet link before any simulator scenario. The raw failed record/hub logs were created under `C:/t/f034-20261029-a/pytest-of-ryanh/pytest-0/test_registered_scenario_with_0/`, and pytest's automatic retention removed that directory **before** the author's preservation copy; the copy failed. Accepted limit: *"Acceptance is partial/UNMET, and the required worker outcome is FAILED."* | `focused-first.log` (1 497 B, SHA-256 `744800b8…a580`); `preservation-status.json` (1 496 B, SHA-256 `93abb25c…2d27`, the authored status receipt); `focused-external.log`; `source-commit-hook.log`; `precommit-ownership-audit.json`; the clean external campaign record (18 179 B, SHA-256 `11849d40…0492`, equal to the hash the accepted report records); the report's 11 878-byte historical DeepSeek prefix (SHA-256 `c2569240…c4e9ff`) byte-identical inside the new report; Git objects for source and report; the published task ref and its verified full Git bundle. | The **original managed BLOCKED raw JSON/hub logs** at the path above. Verified absent now: that directory, its `pytest-0` parent, the `pytest-of-ryanh` parent and the whole `C:/t/f034-20261029-a` root. The accepted records disposition these originals as a lost, unrecoverable preservation failure; the bounded inspection performed here did **not** recover them, and that disposition is the accepted record's rather than a newly proven global fact. The present absence of this one temp root is **not** an exhaustive backup search and does **not** prove recovery is universally impossible; copies held elsewhere remain **unverified**. Narrow and still valid: no later run can recreate the original historical bytes. | The original bytes, byte length and SHA-256 of those lost logs are recorded nowhere accepted and are **not invented here**. The raw JSON that showed the actual Telnet blocked reason is gone. Per the original C1 report, `focused-first.log` retains the **count, assertion and BLOCKED outcome**, while the **native tool transcript** records the actual Telnet blocked reason observed from that original JSON; the reason is carried here as an **accepted reported observation**, not as a detail independently found in the log, and no raw payload was read. | Preservation acceptance stays **UNMET / partial**; the failed outcome is not converted to passed. Cleanup of the owned worktree/temp stays **HELD**. Default managed-runner / all-scenario CI compatibility, qualified review, privacy admission and integration stay **HELD**. The chain `38687231 → 060769b7 → ee3f2e7f → caaa4faa` stays unreviewed and unintegrated. |
| **G2** | **Overwritten original SW-AUDIT freshness scratch extracts** | SW-AUDIT-01 freshness-delta child (committed-ledger comparison). Native MiniMax-M3 / thinking author, Task `task_02c22e77963a`, Dispatch `ctx_e973d4be3c60`, Run `run_37205f6095b3`, worker terminal `term_ba1c0350-0193-49cb-80d3-019fdcfd3dda`, coordinator terminal `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`. Worktree `wp-audit-freshness-delta`, branch `ryan-haver/wp-audit-freshness-delta`, base `d6e78e0b6ab1dab5216443584d810a7a24af32b2`; report `11b09676f78acd76bd1ac47d11a8d8817e8d0624` (one path). Independent factual check: OpenAI coordinator, accepted at `490a879bd346773cca64fac861eaaab29e703628`. | Attempt 1 ran `git show <rev>:docs/validation/LEDGER.md > file` through a shell redirection: exit 0, but every non-ASCII character was mangled (U+2014/U+00B7 → U+FFFD) and the parse found 0 feature rows. The mangled first-pass files were then **replaced** by byte-exact `git cat-file` extracts. Accepted limit (coordinator review): *"The author reports overwriting its first mangled scratch extracts. Their original generated bytes are not preserved or reconstructed as originals. … This is a diagnostic preservation gap, not lost project source or evidence. Retain this worktree and task ref; no destructive cleanup is approved here."* | The **ledger content itself was never lost**: the two committed blobs exist and are byte-exact — `28fce729…:docs/validation/LEDGER.md` (blob `fa0da83c…129a`, 74 831 B, SHA-256 `41d81dae…aecce`, 0 CR, 0 U+FFFD) and `d6e78e0b…:docs/validation/LEDGER.md` (blob `281a7647…4d98`, 74 447 B, SHA-256 `b8078e4d…5cf7`, 0 CR, 0 U+FFFD), matching the report's §1 values exactly. The **replacement** scratch extracts survive and are byte-identical to those blobs (`ledger_old.md`, `ledger_new.md`). The analysis scripts survive (`parse_ledger.py`, `attribute_delta.py`). The report and the coordinator acceptance are in the tree. | The **original generated bytes of the first-pass mangled scratch extracts** (the two files that existed on disk before the byte-exact replacement). Never committed, never hashed in any accepted record, overwritten. The accepted coordinator review dispositions these originals as not preserved and not reconstructed; the bounded inspection performed here did **not** recover them, and no hash is invented. That disposition is the accepted record's rather than a newly proven global fact: no backup or archive search was performed, copies held elsewhere remain **unverified**, and no later run can recreate the original historical bytes. | The first-pass files' exact byte length, content and SHA-256 are recorded nowhere accepted and are **not invented here**. Whether the mangled files were ever copied elsewhere before replacement is not established by any accepted record and is not asserted. | The accepted freshness-mapping acceptance is **unaffected** — it accepted the report's mapping, not a code review or a runtime qualification. The gap is **diagnostic only**: no canonical ledger, record, finding, manifest, source or baseline byte is affected and no feature level moves. The worktree and task ref must be **retained**; no destructive cleanup is approved by this report. |

---

## 3. Gap G1 — lost original API-C1 managed-failure artifacts

### 3.1 Event and provenance

The accepted source of this history is the **append-only author report** at
`060769b724e7a546b8df22eac82f3b288d9bbbe8`, path
`docs/production/software-waves/SW-API-CLIENT-02-C1/AUTHOR.md`, section *"Preserved
initial preparation failure"* and the closing *"Final source verification and
partial disposition — 2026-10-29"* / *"Current invocation and exit inventory"*
sections.

* Author: OpenAI `gpt-6.1-sol/high`; Task `task_c0d26e9e563e`; Dispatch
  `ctx_0f27082dc4eb`; Run `run_37205f6095b3`; worker terminal
  `term_0b99c857-414e-4891-ae63-768327f92812`
  (`docs/production/AGENT_ALLOCATION.md`, worker table).
* Worktree `wp-api-client-02-c1`; branch `ryan-haver/wp-api-client-02-c1`;
  frozen published base `938ae30339790c361abdda6fdd01b11a4e498518`.
* Source commit `386872316cb60130b06dd704557ae6ca1a92b5c8` ("test(validation):
  assert unavailable route-all refusal"), parent exactly `938ae303`. Verified
  scope: four paths — the append-only report, `docs/validation/features.yaml`
  (the coordinator-staged one-line F-API-034 scenario link; **composite
  authorship**, recorded by the author), and the two new modules
  `tests/validation/scenarios/sw_api_client_02_c1.py` and
  `tests/validation/test_sw_api_client_02_c1.py`.
* Report commit `060769b724e7a546b8df22eac82f3b288d9bbbe8` ("docs(validation):
  record route-all partial acceptance"), parent exactly `38687231`, **one path**
  only (`docs/production/software-waves/SW-API-CLIENT-02-C1/AUTHOR.md`).
* Append-only provenance verified byte-exactly: the first **11 878** bytes of the
  report at `060769b7` are byte-identical to the blob at `938ae303`, SHA-256
  `c25692409f8d4f7ae38a21695571821475b1ec097de995517b266c2b59c4e9ff` — the
  value the report itself claims. The historical DeepSeek authorship of the
  original 11 878-byte report is therefore intact and unrelabelled.
* The independent review blob at the same path is **unchanged**
  (`85c18d2443c758fe78964c6c2098b1317eb41036`, review commit `0bd3d76f`). That
  review covers the **DeepSeek** F-API-033 chain only. The 2026-10-29 OpenAI
  addendum at `060769b7` has **no independent review of its own**.

### 3.2 The accepted recorded failure

The accepted report records the first focused invocation

```text
python -m pytest tests/validation/test_sw_api_client_02_c1.py -q -p no:tests.route_inventory -p no:cacheprovider
```

as exited **1** with **12 passed, 1 failed** and the outcome **BLOCKED**: the
managed source runner requires a healthy Telnet link before starting any
simulator scenario, and requiring certificate verification against the
disposable simulator's self-signed TLS certificate correctly keeps the matrix
client disconnected. The accepted report states this is *"not a shared-runner
edit or product defect"*.

The loss itself, in the accepted report's own words: *"The original raw failed
record/hub logs were created under
`C:/t/f034-20261029-a/pytest-of-ryanh/pytest-0/test_registered_scenario_with_0/`,
but subsequent pytest automatic retention removed that temporary directory before
the author's preservation copy. This is a preservation failure: the raw JSON/hub
logs are unavailable, not preserved."* and *"no reconstructed raw record or
qualification retry substitutes for it."*

The accepted outcome is stated by the author and confirmed by the coordinator's
ledger (`docs/production/AGENT_ALLOCATION.md`, *"API author partial failure
settled/preserved — 2026-10-29T03:02Z"*; `docs/planning/RUNTIME_EXECUTION.md`,
*"API failed-run preservation gap recorded — 2026-10-29T02:31Z"*;
`docs/agent-process/state/HANDOFF.md`, *"API original failure artifacts missing;
acceptance remains failed — 2026-10-29T02:31Z"*):

* *"Acceptance is partial/UNMET, and the required worker outcome is FAILED."*
* *"These do NOT recover original managed BLOCKED raw JSON/hub logs; preservation
  acceptance UNMET and default managed/all-scenario CI compatibility, qualified
  review, privacy/admission and cleanup remain HELD."*
* *"These current snapshots do not claim to contain lost original attempts."*

### 3.3 What is demonstrably retained

All entries below were located and identified by this report at the base
`f2dc1dbf` (existence, byte size and SHA-256 only; no private payload was
opened).

| Surviving artifact | Path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Initial failed focused log (12 passed / 1 failed, exit 1) | `wp-api-client-02-c1/build/software-waves/SW-API-CLIENT-02-C1/focused-first.log` | 1 497 | `744800b8b92c5b24a17f5cc0c69181fad183403126075f4d9530ac073afea580` |
| Authored preservation status receipt (lost paths, surviving references, observed copy error) | `…/SW-API-CLIENT-02-C1/preservation-status.json` | 1 496 | `93abb25cac13b6e97fc9256a3dacc3fc4dba98a610155d26b478c4c4a6c72d27` |
| Externally approved focused log (13 passed) | `…/SW-API-CLIENT-02-C1/focused-external.log` | 102 | `9218943cc5a2fe9b427327dbd3ca580a95340e9503a201fdce985e179213368d` |
| Normal configured source-commit hook output | `…/SW-API-CLIENT-02-C1/source-commit-hook.log` | 6 590 | `bf3c8c9d7db9280a74457ad3cdd10620d12008bbf042c4584d4ee173f2d6cbee` |
| Pre-commit path/semantic/prefix audit (five hash-verified preserved files) | `…/SW-API-CLIENT-02-C1/precommit-ownership-audit.json` | 1 227 | `80f9318ca96726f6a5be440de321f35c067c8ee90901d35de9890e05230ff6b1` |
| Clean committed-source external campaign record | `…/SW-API-CLIENT-02-C1/campaign-clean-01/evidence/F-API-034/2026-10-29-V2-38687231-sw_api_client_02_c1.switch_all_failed-api.json` | 18 179 | `11849d40b89ad90b2a554577e26df9ac62f154d67c55f2b5ecaa935a218e0492` |

The campaign record's SHA-256 is **identical** to the value recorded in the
accepted author report and independently re-checked by the coordinator
(`AGENT_ALLOCATION.md`, *"…external record hash
`11849d40b89ad90b2a554577e26df9ac62f154d67c55f2b5ecaa935a218e0492`; 49 surviving
manifest member sizes/hashes match"*). The external campaign is a **separate,
later** invocation under explicit coordinator approval
(`msg_2ec594fdfa50` answering question `msg_ce80f092d9d9`); it is retained
evidence of its own and is **not** a recovery of the original managed failure.

Git-retained references, verified at the base:

* source commit `386872316cb60130b06dd704557ae6ca1a92b5c8` — present;
* report commit `060769b724e7a546b8df22eac82f3b288d9bbbe8` — present, one path;
* the report's 11 878-byte historical prefix, SHA-256 `c2569240…c4e9ff` —
  present byte-identically inside the new report;
* the unchanged independent review blob `85c18d24…41036` — present at the base
  and at `060769b7`;
* the coordinator's recorded **publication** of the exact task ref `060769b7`
  and a **verified complete full Git bundle** (`AGENT_ALLOCATION.md`,
  2026-10-29T03:02Z). The bundle's own bytes are coordinator-owned private
  preservation; this report did not open or re-hash them and makes no claim
  about their contents.
* the coordinator's recorded **current** workspace archive
  (`c11da5cf5bff13d80e76e1577eb8341357053ccab509dcffd77918c39a712a4c`) and
  **current** temp-tree archive
  (`4cd174b1971a956b78a983ea450496751d819cb48a039c05c37f21c6b5451d24`). These
  are snapshots of the *later* workspace and temp state. The ledger states
  explicitly that they *"do not claim to contain lost original attempts"*, and
  this report adopts that limit unchanged.

### 3.4 What the accepted records disposition as irrecoverable

The original managed **BLOCKED** raw JSON/hub logs under
`C:/t/f034-20261029-a/pytest-of-ryanh/pytest-0/test_registered_scenario_with_0/`.
Verified at the base: that directory, its `pytest-0` parent, the
`pytest-of-ryanh` parent and the whole `C:/t/f034-20261029-a` root are all
**absent** on this host.

The disposition and its exact limit:

* The accepted records (the C1 author report at `060769b7` and the coordinator
  ledger entries cited in §3.2) disposition these originals as a
  **lost, unrecoverable** preservation failure. That disposition is carried
  here as **accepted recorded history**, attributed to those records.
* The bounded inspection performed for this report **did not recover** the
  original logs. No substitute, reconstruction or recovered hash is offered in
  their place.
* The scope of that inspection is **narrow**: the present absence of one temp
  root. It is **not** an exhaustive backup or archive search, and it does
  **not** establish that recovery is universally impossible. Whether a copy of
  those bytes exists anywhere else remains **unverified** and is left open.
* What does hold, and is unaffected by that limit: **no later run can recreate
  the original historical bytes.** A later invocation at a different state is a
  different artifact, not the original.
* This report does not reconstruct them, does not label any later artifact as
  them, and does not offer the retained current snapshots as their substitute.
* A missing path is **not** treated here as proof of worker exit, of any
  additional artifact loss beyond the recorded paths, or of when the removal
  happened. Only the recorded paths' present absence is asserted.

### 3.5 What remains unverifiable, and is left unknown

* The original bytes, byte length and SHA-256 of the lost logs: recorded
  nowhere accepted, **not invented here**.
* The raw JSON that showed the actual Telnet blocked reason is gone. The
  original C1 report at `060769b7` states the split this report preserves
  exactly: *"The failed pytest log retains the count, assertion and BLOCKED
  outcome; the native tool transcript records the actual Telnet blocked reason
  observed from that original JSON."* So `focused-first.log` retains the
  **count, assertion and BLOCKED outcome**, while the **native tool
  transcript** records the actual Telnet blocked reason observed from the
  original JSON. The reason is carried here as an **accepted reported
  observation** from that transcript, **not** as a detailed reason
  independently found in the log. This report identified the retained log by
  existence, size and SHA-256 only; no raw payload was read, and no raw
  payload read is requested.
* The precise mechanism of the removal beyond the author's recorded statement
  (pytest automatic retention) is not independently established by this report.

### 3.6 Acceptance and cleanup consequences

* The unit's preservation acceptance stays **UNMET / partial**; the required
  worker outcome remains **FAILED**. This report does not convert it to a pass.
* Cleanup of the owned worktree and temp stays **HELD**; no cleanup, release,
  worktree removal or branch deletion is performed or authorized here. All
  cleanup decisions are coordinator-owned.
* Default managed-runner / all-scenario CI compatibility, qualified
  different-family review, VAL-15 privacy admission and integration/qualification
  stay **HELD**.
* The OpenAI chain remains unreviewed and unintegrated. Verified at the base:
  `38687231`, `060769b7`, `ee3f2e7f` and `caaa4faa` are **none of them
  ancestors** of `f2dc1dbf`.
* The accepted pins already carry the limit in
  `SW-API-CLIENT-02.corrective_child_dispositions[0].current_residual.remaining`:
  *"full unreviewed OpenAI chain from `938ae303`; new branch-correct proof and
  parent remaining target/client contracts; **original lost managed-failure bytes
  remain irrecoverable**"*, with `pins: [RV-API034, EV-API034-SECURITY-REFRESH,
  EV-PRESERVATION-GAPS, EV-COMBINED-P1]`, and
  `state_is_dated_snapshot_not_current_authority: true`. The same entry keeps the
  actual authorship split intact: the DeepSeek-authored F-API-033 source
  `3788353e` / report `4baef574` with OpenAI review `0bd3d76f`, and the later
  OpenAI addendum `38687231`/`060769b7` plus `ee3f2e7f`/`caaa4faa` as *"separate
  append-only provenance"*. **This report changes no attribution and does not
  canonicalize a waiver.**
* The later managed follow-up C2 (`task_14b35f83dc26`, Dispatch
  `ctx_d658a8d62647`, base `060769b7`, source `ee3f2e7f`, report `caaa4faa`) is a
  **separate** unit with its own partial/UNMET outcome. Its accepted author
  record states the boundary this report adopts verbatim: *"This separately
  named diagnostic does not recreate the historical lost C1 original or repair
  its permanently failed/partial preservation status"* and *"The old C1
  lost-original preservation failure remains independently immutable."* C2's own
  failure (the required global CLI gate exiting 1 on
  `F-SEC-007 dropped below its recorded level: level V2 < recorded V3`) is
  **not** dispositioned here.

---

## 4. Gap G2 — overwritten original SW-AUDIT freshness scratch extracts

### 4.1 Event and provenance

The accepted sources are the freshness-delta report
`docs/production/software-waves/SW-AUDIT-01/FRESHNESS_DELTA.md` at
`11b09676f78acd76bd1ac47d11a8d8817e8d0624` (§9, attempt 1) and the coordinator's
factual review `docs/production/software-waves/SW-AUDIT-01/COORDINATOR_REVIEW.md`
at `490a879bd346773cca64fac861eaaab29e703628`.

* Author: native MiniMax-M3 / thinking; Task `task_02c22e77963a`; Dispatch
  `ctx_e973d4be3c60`; Run `run_37205f6095b3`; worker terminal
  `term_ba1c0350-0193-49cb-80d3-019fdcfd3dda`; coordinator terminal
  `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`.
* Worktree `wp-audit-freshness-delta`; branch `ryan-haver/wp-audit-freshness-delta`;
  exact base `d6e78e0b6ab1dab5216443584d810a7a24af32b2`; report written
  2026-10-28T23:36Z.
* Report commit `11b09676f78acd76bd1ac47d11a8d8817e8d0624`, parent exactly
  `d6e78e0b`, **one path** only. Verified an ancestor of the base `f2dc1dbf`.
* The independent factual check is the **OpenAI coordinator**; it accepted the
  report's *mapping* at report `11b09676` — *"not a code review, runtime
  qualification, feature promotion or parent-unit closure"*.

### 4.2 The accepted recorded failure and limit

`FRESHNESS_DELTA.md` §9, attempt 1:

> `git show <rev>:docs/validation/LEDGER.md > file` via the shell — exit 0, but
> the redirection mangled every non-ASCII character (U+2014/U+00B7 became
> U+FFFD); the parse then found 0 feature rows — *Superseded by
> `extract_ledgers.py` (`git cat-file blob`, byte-exact). **The mangled
> first-pass files were replaced**; the byte-exact SHA-256 values in §1 are from
> the `git cat-file` blobs.*

The coordinator's accepted review carries this as one of two nonblocking limits:

> *The author reports overwriting its first mangled scratch extracts. Their
> original generated bytes are not preserved or reconstructed as originals.
> Native transcript, reported failed symptoms and present workspace are
> retained. **This is a diagnostic preservation gap, not lost project source or
> evidence. Retain this worktree and task ref; no destructive cleanup is
> approved here.***

### 4.3 What is demonstrably retained

The important distinction is between **the ledger content** (never lost) and
**the first-pass mangled scratch files** (the lost originals). Verified at the
base:

| Retained item | Identity | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Committed old ledger blob | `28fce729ca4ea08bfc2f19805b36e13ae8c184f2:docs/validation/LEDGER.md`, Git blob OID `fa0da83c5b2351e48c40b00f5884f5e25b1c129a` | 74 831 | `41d81dae99566b01c15b4ada2eeff67ec2c87065a312b16a8c8bd4f8071aecce` |
| Committed new ledger blob | `d6e78e0b6ab1dab5216443584d810a7a24af32b2:docs/validation/LEDGER.md`, Git blob OID `281a7647b41e816529d8b7d953df7705a3084d98` | 74 447 | `b8078e4d45be717c88f7f138c34a60d45a3ad118e1051e30f5da8a8c88c25cf7` |
| Surviving replacement scratch extract | `wp-audit-freshness-delta/build/software-waves/SW-AUDIT-01-freshness-delta/ledger_old.md` | 74 831 | `41d81dae…aecce` — **byte-identical to the committed old blob** |
| Surviving replacement scratch extract | `…/SW-AUDIT-01-freshness-delta/ledger_new.md` | 74 447 | `b8078e4d…5cf7` — **byte-identical to the committed new blob** |
| Surviving analysis script | `…/SW-AUDIT-01-freshness-delta/parse_ledger.py` | 4 328 | `8a750ffcdee8f39cdc091d75558e2a4b818e4a455ea01026fd6b3bae0e5a371a` |
| Surviving analysis script | `…/SW-AUDIT-01-freshness-delta/attribute_delta.py` | 6 989 | `2c8e08df8079f4e266555897fdaaa3c2996a2180745459f7c78e0be4388f1661` |

Both committed ledger blobs are **0 CR bytes and 0 U+FFFD**, and both byte
counts and SHA-256 values match the report's §1 table exactly. The surviving
scratch extracts are therefore the **replacements**, not the originals — proved
by their byte-identity with the committed blobs, which the mangled first pass
could not have had.

Also retained: the report `11b09676` and its coordinator acceptance
`490a879b` (both in the tree at the base), the native tool transcript and the
reported failed symptoms (per the accepted coordinator review), and the present
workspace.

### 4.4 What the accepted records disposition as irrecoverable

The **original generated bytes of the two first-pass mangled scratch extracts**
— the files that existed on disk before the byte-exact replacement. They were
never committed, never hashed in any accepted record, and were overwritten.

* The accepted coordinator review (`490a879b`, quoted in §4.2)
  dispositions these originals as **not preserved and not reconstructed**, and
  classifies the event as a diagnostic preservation gap. That disposition is
  carried here as **accepted recorded history**, attributed to that review.
* The bounded inspection performed for this report **did not recover** the
  first-pass bytes. This report does not reconstruct them and invents no hash
  for them.
* The scope of that inspection is **narrow**: it establishes that the retained
  scratch files are the byte-exact **replacements**, not the originals. It is
  **not** an exhaustive backup or archive search, and it does **not** establish
  that recovery is universally impossible. Whether the mangled files were ever
  copied elsewhere before replacement remains **unverified** and is left open.
* What does hold, and is unaffected by that limit: **no later run can recreate
  the original historical bytes.**
* The ledger **content** they were meant to hold is fully recoverable from the
  committed blobs, but that is a different thing: it does not restore the
  first-pass artifact of the failure. The gap is that the failure's own
  diagnostic bytes are gone, not that the ledger was lost.

### 4.5 What remains unverifiable, and is left unknown

* The first-pass files' exact byte length, content and SHA-256: recorded
  nowhere accepted, **not invented here**.
* Whether the mangled files were ever copied elsewhere before replacement: not
  established by any accepted record, and not asserted here.
* The count of mangled code points is not re-derived here; the accepted report's
  qualitative description (every non-ASCII character mangled to U+FFFD, parse
  finding 0 rows) is carried as the **reported** symptom.

### 4.6 Acceptance and cleanup consequences

* The accepted freshness-mapping acceptance is **unaffected**. It accepted the
  report's mapping and its arithmetic against committed bytes, with the
  preservation limit attached; this report does not widen or narrow it.
* The gap is **diagnostic only**. No canonical ledger, record, finding,
  manifest, source byte, baseline or feature level is affected, and no
  feature, target or finding disposition moves.
* The worktree `wp-audit-freshness-delta` and its task ref must be **retained**;
  no destructive cleanup is approved by this report. All cleanup decisions
  remain coordinator-owned.
* The report's other nonblocking limit (the `git diff --name-only` exit-code
  erratum) is **not** a preservation gap and is **not** dispositioned here; it
  is noted only so it is not confused with the gap above.

---

## 5. What this report explicitly does not claim

* It does not claim that either gap's **preservation acceptance passed**. Both
  remain recorded failures: G1 partial/UNMET with a FAILED outcome, G2 a
  diagnostic preservation gap accepted as a nonblocking limit.
* It does not claim that any **original evidence or function proof** was
  accepted, and it does not accept the C1 external campaign, the C1/C2 managed
  campaigns or the freshness-delta mapping as original proof of the lost
  material.
* It does not claim that a **later successful run** recovered anything. The C1
  external campaign, the C2 managed campaign and the byte-exact freshness
  extracts are separate later artifacts with their own attribution; none of
  them restores the lost originals or establishes the original source/exit
  identity of the failed managed invocation.
* It does not close **VAL-14** or **VAL-15**, promote any level, admit any
  evidence, or approve any source / privacy / owner / CI / image / physical
  HIL / 72-hour soak / week field / version or release gate.
* It does not claim that the lost originals are provably unrecoverable
  **globally**, and it does not claim that an exhaustive backup or archive
  search was performed. The unrecoverable-original disposition is the
  **accepted records'** recorded history; the bounded inspection here did not
  recover the originals and leaves copies held elsewhere **unverified**. It
  does claim the narrow, valid fact that **no later run can recreate the
  original historical bytes**.
* It does not grant the author any authority to accept this report. An
  **Independent OpenAI-family factual review at the exact report commit** is
  required, and the author cannot self-accept or canonicalize a waiver.
* It does not change any source, test, tool, schema, scenario, registry,
  findings, evidence, baseline, root manifest, lockfile, runtime or credential
  setting. **No existing original or failure was modified, re-scored, re-dated,
  relabelled or byte-altered.**

---

## 6. Checks actually run (original attempt)

Interpreter: the root virtualenv
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(Python 3.12.10), own checkout root + `src` on `PYTHONPATH`, `PYTHONUTF8=1`,
bytecode disabled. Each invocation got a **freshly created** temp parent under
`C:/t/exec-ev-preservation-gaps/nov02-attempt01/`, isolated `MATRIX_DATA_DIR` /
`UC_CONFIG_HOME`, and an explicit **forward-slash** `--basetemp` and
`--junitxml`. Each invocation was captured as a direct subprocess with its own
return code, full stdout, full stderr and JUnit; the artifacts and the temp
bytes were hashed **immediately, before any further invocation**.

See §7 for the recorded exit codes, byte counts and SHA-256 values.

Report-only checks (UTF-8 strict decode, CR-aware whitespace, final newline,
cited repository-relative path existence, markdown link targets, required
section tokens, and single-path tracked scope) were run against this file.

No campaign, ledger generation, registry check, source/core/client/image test,
cleanup, push, merge, tag or release ran. The bounded **read-only**
hash/existence/Git-provenance metadata commands and the report-only checks
described above are inspection metadata, not runtime, campaign, qualification
or recovered-original evidence; no recovery action against the lost material
ran.

---

## 7. Recorded results

### 7.1 Existing documentation modules (the only test invocation of the original attempt)

Interpreter: root virtualenv
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(Python 3.12.10). Own checkout root + `src` on `PYTHONPATH`, `PYTHONUTF8=1`,
`PYTHONDONTWRITEBYTECODE=1`, isolated `MATRIX_DATA_DIR` / `UC_CONFIG_HOME`,
`TEMP`/`TMP` inside the fresh parent, explicit **forward-slash** `--basetemp`
and `--junitxml`, and the two required plugin suppressions.

```text
python -B -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -p no:tests.route_inventory -p no:cacheprovider -q --tb=short --basetemp=C:/t/exec-ev-preservation-gaps/nov02-attempt01/docs-modules/pytest-temp --junitxml=C:/t/exec-ev-preservation-gaps/nov02-attempt01/docs-modules/docs.junit.xml
```

| Item | Value |
| --- | --- |
| Direct subprocess return code | **0** (captured from the process, not inferred from a pipeline) |
| Result line | `489 passed in 2.76s` |
| Wall clock | 2026-11-03T02:50:56.956164Z → 2026-11-03T02:51:00.231600Z |
| stdout | 588 bytes, SHA-256 `828cb20b6b7987830a903e0d2eb7e703211a7f1e65c6258d849978321ec6a679` |
| stderr | 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| JUnit XML | 63 691 bytes, SHA-256 `56fdd8f3adb447396106df0d5303844b7b3a788c619e7159418d960033442b01` |
| Fresh temp parent after the run | 103 files / 164 426 bytes, each file hashed immediately after the invocation and before any later one |
| Route / cache plugins | `no:tests.route_inventory`, `no:cacheprovider` (full route proof not overwritten) |

Receipt: `build/software-waves/EV-PRESERVATION-GAPS/execution-20261101/author/checks/docs-modules.receipt.json`
(return code, argv, env-relevant paths, stdout/stderr/JUnit hashes and the
per-file temp-parent hash list).

### 7.2 Report-only checks

A private, read-only report checker (`author/report_checks.py`) ran against
this file. It checks, and it reported:

| Check | Result |
| --- | --- |
| UTF-8 strict decode | **pass** (0 U+FFFD replacement characters) |
| CR-aware whitespace | **pass** (0 CR bytes, 0 trailing-whitespace lines, 0 tabs, single final LF) |
| Non-ASCII inventory | only `§`, `–`, `—`, `…`, `→` — no mojibake, no unlabelled CRLF mixing |
| Cited base-tree paths resolve | **pass** — 12/12 present (C1 author + review, freshness delta, coordinator review, SW-AUDIT-01 execution report, W03 close inventory, QUAL review, allocation ledger, runtime execution, handoff, final pins, canonical ledger) |
| Cited historical paths resolve at their named revision | **pass** — 3/3 (`sw_api_client_02_c1.py` and `test_sw_api_client_02_c1.py` at `38687231`; the C1 author report at `060769b7`) |
| Markdown link targets | **pass** — 0 broken |
| Required provenance tokens | **pass** — every Task, Dispatch, Run, base, commit, artifact hash and review-family token present |
| Tracked scope | **pass** — no tracked file modified; exactly one new tracked path (`docs/production/software-waves/EV-PRESERVATION-GAPS/execution-20261101/AUTHOR.md`) |
| Private build tree ignored | **pass** — `.gitignore:7:build/` |
| Base / branch at check time | `f2dc1dbf683d8f96200d1517b0786e3441105b36` on `execution/wp-exec-ev-preservation-gaps` |

The report's own blob hash cannot be embedded in the file it describes; it is
recorded by the commit object and in the private receipt. The §7.1 hashes come
from the invocation recorded there, and the only byte difference between the
file state that invocation last saw and the committed file lies within §7
itself; §7.2 ran on the final bytes.

### 7.3 What was deliberately not run

No managed failure, qualification retake, validation campaign, ledger or gate
generation, registry check, source/core/client/image/physical test, recovery
probe, archive extraction or rewrite, file removal or move, branch or ref
deletion, reset, prune, service, dependency install, Docker, hardware, external
deployment, version, tag or release. No cleanup was performed or authorized.
No push, merge or self-release.

The read-only existence/hash/Git-provenance inspection metadata of §8 is
not part of that excluded list: it started no runtime service, campaign or
qualification, ran no recovery action against the lost material, and produced
no recovered-original evidence.

---

## 8. Artifacts and limits

**Private, ignored** (own tree only, `build/software-waves/EV-PRESERVATION-GAPS/execution-20261101/author/`):
byte-exact extraction receipts of the historical blobs read
(`refs/`, `refs-receipt.json`), the bounded existence/identity probe
(`probe_survival.py`, `survival-probe.json`), the Git provenance proof
(`git_proof.py`, `git-proof.json`), and the invocation receipts. These are
**new inspection metadata** created for this report, **not** restored
historical evidence and **not** recovered originals. They are inspection aids
for this report only; **no new reusable tool or fixture is shipped** and
nothing here is imported into the canonical tree.

**Uncertainties left open** (stated, not speculated):

* The original bytes, lengths and hashes of the G1 lost logs and the G2
  first-pass mangled extracts are unknown and were not invented.
* The absolute paths quoted for other hosts' workspaces and temp roots are
  supplemental; existence was verified for the paths this report names, and
  their absence is asserted only for the recorded lost paths.
* Whether a copy of the G1 lost logs or of the G2 first-pass mangled extracts
  exists anywhere else was **not searched for** and remains **unverified**. The
  unrecoverable-original disposition is the accepted records' recorded
  history, not a newly proven global filesystem fact.
* No raw private record, log, screenshot, archive payload or credential was
  opened. The retained private artifacts above were identified by existence,
  size and SHA-256 only.

**Explicitly out of this unit's scope** (named so no reader assumes full
coverage, and **not** dispositioned here):

* The **third** instance of the same class recorded by the SW-AUDIT-01
  execution author's own §11 note (*"This author's first scratch extraction
  overwrote its own earlier mangled output … The original generated bytes of
  that first pass were not preserved"*, at
  `docs/production/software-waves/SW-AUDIT-01/execution-20261101/AUTHOR.md`).
  That report's correction (`981e7e4a`) and its independent re-review are
  **pending** at the base and the corrected author report is **not** an
  ancestor of the base; its row 7 is the origin of this unit's pin naming, not
  an accepted source of truth for these two gaps.
* The **W03-CLOSE-INVENTORY** gaps G1–G4 (absent whole-workspace archives for
  the controller author, the header reviewer and the controller reviewer, and
  the missing recovery-checkout proof row). These are a **different**
  preservation-gap set and are outside this unit's pinned scope. Nothing in
  this report re-hashes, re-scores or re-audits that inventory.
* The **failed Anthropic core qualification** (`QUAL-ANTHROPIC-CORE-01`): a
  separate matter with **attempt 1 FAILED**, **no domain granted** and **no
  automatic retry**. The owner's explicit retake choice is **pending**; this
  correction round performs no retake and grants no source authority. Its own
  findings do not repair, widen or reclassify either gap here, and it grants no
  source acceptance.
* The **current global inventory** for SW-AUDIT-01, whose correction re-review
  still reads **`require_changes`** as recorded by the independent review at
  `abd339eda`. No global acceptance is inferred, claimed or re-audited here,
  and it is not treated here as an accepted proof source. It is a **separate**
  global scope owned by another worker; this correction round neither edits
  nor takes it over.

---

## 9. Correction round (this commit)

### 9.1 Round identity, scope, and what this round does not change

This is a **prose-only correction** of this report, made after the independent
factual review at the exact commit `ed78321e51156f229507e654f0cf3faae100b935`
returned **`require_changes`** with three required corrections (R1, R2, R3). It
is **not** a new source phase, not a failed-qualification retry and not a
re-audit.

| Item | Value |
| --- | --- |
| Correction Task / Dispatch | `task_e1d5c3589200` / `ctx_f56a5a99bfee` |
| Run | `run_37205f6095b3` (existing Run; not reset or replaced) |
| Worker terminal | `term_b6996ca4-3c88-4471-8c4d-1ccbb18f3eed` |
| Coordinator terminal | `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| Runtime / Orca | `e8ce3460-a9d4-4897-8e4f-10a8e3cdc400` / 1.4.246 |
| Worktree / branch | `wp-exec-ev-preservation-gaps` / `execution/wp-exec-ev-preservation-gaps` |
| Corrected base (exact, verified) | `ed78321e51156f229507e654f0cf3faae100b935` |
| Corrected base's parent | `f2dc1dbf683d8f96200d1517b0786e3441105b36` |
| Author route | native MiniMax-M3 via OpenCode 2 (project-pinned model; no CLI model/effort override) |
| Date of this record | 2026-11-02 local (-07:00) / 2026-11-03 UTC |
| Delivery class | report prose only - one tracked path, no implementation, test or tool |

Reviewed identities (immutable history, not restated as new artifacts): the
independent review blob at
`docs/production/software-waves/EV-PRESERVATION-GAPS/execution-20261101/REVIEW.md`
is commit `abd339eda108e4d74f1a147b2f445299814e9cf9`, 10 496 bytes, SHA-256
`b0720257b8e0104f7cab5ed5c3a72bd39e01c4cadc56bc35f9e8dc9149a233f6`; the
reviewed author blob was 36 331 bytes, SHA-256
`ca72b8fff2c1adc60a03b77d6932febc450171716a074c1b9c8b163b0bce76ab`. The
original author and the independent OpenAI-family reviewer (native
`gpt-6-astra/high`) were **settled and released**; their originals, natives,
workspace and temp archives are preserved and their exact task refs are
published. No duplicate writer was created.

This round **changed no** source, test, tool, fixture, scenario, schema,
registry, ledger, finding, manifest, lockfile, evidence, baseline, runtime or
credential setting, and performed **no** campaign, gate, ledger generation,
registry check, source/core/client/image/physical test, recovery probe,
cleanup, push, merge, tag, release, archive opening or broad filesystem
search. The **only test invocation** was the same five existing documentation
modules; the only other executions were read-only report-only checks
(§9.3). Every historical artifact, private artifact and historical
identity quoted in §1 to §8 is **byte-identical and unchanged**; this round
only edits prose and adds new, separately identified correction artifacts.

§1 to §8 record the **original attempt**. Their check-time rows
(for example the tracked-scope and base rows in §7.2) describe that
attempt's state and are superseded for the current commit by §9.3.

### 9.2 Responses to the required corrections

**R1 - qualify the universal recovery assertions.** Applied.

* The **summary G1 row** now attributes the loss and the irrecoverable-original
  disposition to the **accepted records**, states that the bounded inspection
  did **not** recover the originals, and states explicitly that the present
  absence of one temp root is **not** an exhaustive backup search and does
  **not** prove recovery is universally impossible, so copies held elsewhere
  remain **unverified**.
* The **summary G2 row** carries the same qualification, attributing the
  disposition to the accepted coordinator review and recording that no backup
  or archive search was performed.
* §3.4 and §4.4 are retitled and rewritten to state the disposition as the
  accepted records' recorded history, to state that the bounded inspection did
  not recover the originals, and to leave copies elsewhere unverified.
* The **closing characterization** and a new bullet in §5 carry the same
  limit, and a new bullet in §8 records that no copy search was performed.
* The **valid narrow fact is retained**: no later run can recreate the original
  historical bytes.
* **Not done, deliberately**: no broader search, no archive opening, no
  substitute originals and no recovered hashes. The accepted record's own
  irrecoverable-original *disposition* is preserved as recorded history; the
  report simply no longer asserts it as a newly proven global filesystem fact.

**R2 - distinguish new inspection metadata from historical evidence.** Applied.

* §1 no longer says *"No new evidence was created"* and no longer says *"The
  only invocations were"*. It now states precisely that **no new runtime,
  campaign, qualification or recovered-original evidence was produced**, and
  that **new bounded read-only hash / existence / Git-provenance inspection
  metadata** and **documentation-check artifacts** were created. *"Only"* is
  now scoped to the **test invocation**.
* §6 and §7.3 now distinguish the read-only inspection metadata from the
  excluded runtime work.
* §8 now labels the private inspection artifacts as **new inspection
  metadata**, explicitly **not** restored historical evidence and **not**
  recovered originals.
* This is a **reporting correction only**. It does **not** assert that any
  prohibited runtime diagnostic ran; the inspected records establish no such
  execution, and none ran in this round either.

**R3 - preserve the original count/outcome versus reason-attribution split.**
Applied.

* The **summary G1 row** and §3.5 now follow the original C1 report at
  `060769b724e7a546b8df22eac82f3b288d9bbbe8` exactly: `focused-first.log`
  retains the **count, assertion and BLOCKED outcome**, while the **native
  tool transcript** records the actual Telnet blocked reason observed from the
  original JSON.
* The reason is carried as an **accepted reported observation**, explicitly
  **not** as a detailed reason independently found in the log. The report
  states that the retained log was identified by existence, size and SHA-256
  only, and that **no raw payload was read and no raw payload read is
  requested**.
* §3.2 now attributes the recorded outcome to the accepted report.

### 9.3 Correction-round checks and new artifact identities

This round ran **exactly one test invocation** and otherwise only read-only
report checks. Environment: root virtualenv
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(Python 3.12.10), own checkout root + `src` on `PYTHONPATH` (forward slashes),
`PYTHONUTF8=1`, bytecode disabled, a **freshly created** isolated
`MATRIX_DATA_DIR` / `UC_CONFIG_HOME` / `TEMP` / `TMP` under
`C:/t/exec-ev-preservation-gaps/nov02-correction01/`, and explicit
**forward-slash** `--basetemp` and `--junitxml`.

#### 9.3.1 The one test invocation of this round

```text
python -B -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -p no:tests.route_inventory -p no:cacheprovider -q --tb=short --basetemp=C:/t/exec-ev-preservation-gaps/nov02-correction01/docs-modules/pytest-temp --junitxml=C:/t/exec-ev-preservation-gaps/nov02-correction01/docs-modules/docs.junit.xml
```

| Item | Value |
| --- | --- |
| Direct subprocess return code | **0** (captured from the process, not inferred from a pipeline) |
| Result line | `489 passed in 2.93s` |
| Wall clock | 2026-11-03T03:17:42.517087Z → 2026-11-03T03:17:45.964583Z |
| stdout | 588 bytes, SHA-256 `ac717f1dfb578463ba5e5428228853124a61c3f4135e31163138446950b99a63` |
| stderr | 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| JUnit XML | 63 691 bytes, SHA-256 `f3dc919fd1f7cd4b3f26c74eda716c993cfbc3da8869f88e4c2a89a96fba0f85` |
| Fresh temp parent after the run | 103 files / 164 426 bytes, each file hashed immediately after the invocation and before any later one |
| Capture order | return code, full stdout, full stderr, JUnit and every temp file captured and hashed immediately after the invocation returned, before any further invocation |
| Deletion | **none** - no captured original, receipt, artifact or temp file was removed |

Receipt: `build/software-waves/EV-PRESERVATION-GAPS/execution-20261101/author/correction-01/checks/docs-modules.receipt.json`.

#### 9.3.2 Report-only checks

A private, read-only correction checker
(`author/correction-01/correction_report_checks.py`) ran against this file. It
checks, and it reported:

| Check | Result |
| --- | --- |
| UTF-8 strict decode | **pass** (0 U+FFFD replacement characters) |
| CR-aware whitespace | **pass** (0 CR bytes, 0 trailing-whitespace lines, 0 tabs, single final LF) |
| Non-ASCII inventory | only `§`, `–`, `—`, `…`, `→`, `−` — unchanged from the reviewed file, no mojibake, no unlabelled CRLF mixing |
| Fenced JSON and round-receipt JSON parse | **pass** |
| Cited base-tree paths resolve | **pass** — 12/12 present |
| Cited historical paths resolve at their named revision | **pass** — 4/4 (the two C1 source paths at `38687231`, the C1 author report at `060769b7`, and this unit's independent review at `abd339eda`) |
| Markdown link targets | **pass** — 0 broken |
| Required provenance tokens | **pass** — every Task, Dispatch, Run, base, commit, artifact hash and review-family token present, including the correction-round tokens |
| R1 content assertions | **pass** — the superseded universal wording is absent from the body, and the qualification reaches both summary rows, sections 3.4 and 4.4, section 5 and section 8 |
| R2 content assertions | **pass** — the superseded absolute wording is absent from the body, and the precise scope wording is present |
| R3 content assertions | **pass** — the superseded reason attribution is absent from the body, and the original count/outcome versus reason split is present in both the summary G1 row and section 3.5 |
| Tracked scope | **pass** — exactly one modified tracked path (`docs/production/software-waves/EV-PRESERVATION-GAPS/execution-20261101/AUTHOR.md`), no untracked paths |
| Private build tree ignored | **pass** — `.gitignore:7:build/` |
| Base / branch at check time | `ed78321e51156f229507e654f0cf3faae100b935` on `execution/wp-exec-ev-preservation-gaps` |

The report's own committed blob identity cannot be embedded in the file it
describes; it is recorded by the commit object and reported separately to the
coordinator. The §9.3.1 hashes come from the invocation recorded there, and
the only byte difference between the file state that invocation last saw and
the committed file lies within §9.3 itself; §9.3.2 ran on the final
bytes.

#### 9.3.3 New correction artifact identities

These are **new, round-local inspection metadata**. They are **distinct from**
every immutable historical identity quoted in §3.3, §4.3 and §9.1,
and they do not restate or replace the original author's or the reviewer's
artifacts.

| New artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `author/correction-01/checks/correction-responses.json` | 10 764 | `e5a91daf3bea255cf8fa9b715191ba26459d393c9fb1bb0a024046ed6f7cc18f` |
| `author/correction-01/checks/docs-modules.receipt.json` | 23 554 | `72b19bde0a25aea7ec2274403b1752d4c2fd9f18f85c4c355657738f2670b49e` |

Root: `build/software-waves/EV-PRESERVATION-GAPS/execution-20261101/author/correction-01/`
(private, ignored, this worktree only). Temp root:
`C:/t/exec-ev-preservation-gaps/nov02-correction01/` (private, this host only).
Both are **new inspection metadata** for this round: not restored historical
evidence, not recovered originals, and not part of the canonical tree.

### 9.4 Remaining limits after this correction

* The **two-gap scope** is unchanged: G1 remains **FAILED / partial / UNMET**
  with managed/all-scenario CI compatibility, qualified different-family
  review, VAL-15 privacy admission, integration and cleanup **HELD**; G2
  remains a **diagnostic-only** gap, with the accepted historical
  freshness-mapping acceptance and its recorded limits and retention
  requirement unchanged.
* No **original preservation PASS**, **function proof**, **source
  qualification**, **feature promotion** or **gate closure** is claimed,
  implied or granted by this correction.
* The **current global inventory** remains `require_changes` and is outside
  this unit's scope; it is neither edited nor re-audited here.
* **Core qualification** attempt 1 remains **FAILED with no domain** and the
  owner's explicit retake choice remains **pending**. This round performs no
  retake and grants no source authority.
* The **physical HIL, 72-hour soak, week field sign-off, version and final
  release gates** remain **owner-open**.
* **New and distinct from the immutable historical identities**: the
  correction-round artifacts of §9.3 are new inspection metadata for
  this round only. They are **not** restatements of, and do not replace, the
  original author's or the reviewer's historical artifact identities.
* A **qualified OpenAI-family re-review at the exact corrected commit**
  remains mandatory. There is **no self-acceptance** here; the coordinator
  owns settlement, preservation, publication and the different-family
  exact-commit re-review.

---

*Report-only disposition of two known historical preservation gaps. It records
what is retained, what the accepted records disposition as irrecoverable, and
what is unknown. The unrecoverable-original disposition is **accepted recorded
history**: the bounded inspection here did not recover the originals, did not
search exhaustively for copies, and leaves copies held elsewhere
**unverified**; the narrow fact that no later run can recreate the original
historical bytes stands. It is **not** a preservation acceptance, **not** an
original evidence or function proof, and **not** a source, privacy, owner or
release approval. Independent OpenAI-family factual review at the exact report
commit is required; the coordinator owns the canonical ledger, registry,
integration and all cleanup decisions.*
