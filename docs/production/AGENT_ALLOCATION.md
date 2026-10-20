# Agent allocation and execution ledger

This reusable ledger implements the [standing protocol](../ORCHESTRATION_PROTOCOL.md).
Read [AGENTS.md](../../AGENTS.md), the [master plan](../planning/UNIFIED_MASTER_PLAN.md)
and [model inventory](../planning/MODEL_AND_AGENT_INVENTORY.md) first. Append
dated observations and decisions; do not replace historical outcomes. Use
sanitized receipt references, not credentials or full private settings.

## Recording task: 2026-10-19

**Scope:** persist instructions only. No development phase, worktree creation,
author/reviewer dispatch, model probe, quota-consuming qualification or technical
approval is authorized by this task. Coordinator-only prose edits; documentation
checks do not establish new runtime or model qualification.

### Project binding snapshot

Observed 2026-10-19 during instruction recording; recheck before execution.

| Binding | Observation and scope |
| --- | --- |
| Project / remote | `ryan-haver/8x8-hdmi-matrix-hub`; `origin` = `https://github.com/ryan-haver/8x8-hdmi-matrix-hub.git` |
| Coordinator/root | `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration`; sole Git-registered worktree; protected |
| Integration branch | `wp-runtime-completion`, initial local/remote head `6dafb00963d7576cebcaae47c00c06eb77a4ad08`; this instruction commit advances that branch |
| PR stack | [#38](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/pull/38) draft/open -> `wp-g1-g2-release-and-docs`; [#37](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/pull/37) draft/open -> `main`; [#36](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/pull/36) open -> `main` |
| Remote base heads | #37 `6debe5a9d1ce3b5993bbd1f6c16d14550d11141b`; #36 `c5387d6769600c8a5b8cca217227606edfc47bc0`; remote main `25233bbd90a51ddb7f34d0bb541e90c7b4505c80` (local main is stale) |
| Applicable existing Run | `run_37205f6095b3`, objective runtime R0-R8, no Anthropic, preserve release gates; reuse when applicable, no reset/new Run |
| Historical Run | `run_cd8e6542c879` covers Phase 6/7; retain history, do not confuse with current runtime Run |
| Orca / runtime | Read-only discovery: 1.4.230, runtime `ba9443bb-3d71-459a-8dff-4b535678d276`; historical `5973f7e6-...` receipts are not current live handles |
| Repository ID | `2d494566-13c3-4624-b834-7e0bc340801b`; scope Orca inventories to it |
| Coordinator handle | Existing Run records `term_b8d29307-e8ad-4244-b1bb-0fda04063015`; historical binding, live handle requires revalidation after restart |
| Worker accounting | Run-scoped list: 38 released, two retained compatibility rows with null owned resources; not two newly active workers |
| Unresolved workspace | Orca lists an existing `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-runtime-persistence-wiring`, branch `ryan-haver/wp-runtime-persistence-wiring`; Git root list does not register it. Preserve; filesystem/ownership/liveness discrepancy unresolved. No cleanup attempted. |
| Host capacity | Local Windows execution observed; saved SSH targets are disconnected, not verified capacity. Current collaboration interface has four slots including coordinator; Orca engine limit unknown. Conservative project ceiling: four total / at most three workers, further constrained by actual host/provider/nesting limits. |
| Protected resources | Root/coordinator, unresolved workspace, unrelated projects/worktrees, `main`, integration/release branches, tags, all private runtime data/config/backups, historical evidence and odd untracked encoded hook-directory artifact |
| Handoff | Host-local `C:/Users/ryanh/.antigravity-configs/handoff_active.md` is append-only supplemental context; portable entry points are this ledger and [execution record](../planning/RUNTIME_EXECUTION.md) |

Evidence from read-only Git refs/PR metadata, Orca status/Run/worker/worktree/host
inventories, installed skills and command help is retained locally as
`.git/instruction-*`. These host-local receipts are not portable public evidence.
No Run mutation or worker launch was performed for this recording task.
No existing repository `AGENTS.md` was found by the initial hidden-file search;
the new root file adds an entry point without replacing prior agent instructions.

### Model assessment baseline

This table assesses **historical project observations**, not a new live catalog
refresh or usage measurement. Refresh every allowed route before a development
wave. Exact example IDs below must be rediscovered; provider selection and
underlying family identity are separate facts.

| Candidate / historical selectable route | Observed project evidence | Current eligibility / unresolved checks |
| --- | --- | --- |
| Sol 6.1: `codex`, `gpt-6.1-sol`, high | Accepted core, persistence, lifecycle and deployment corrections | Task-fit author candidate; current catalog/access/quota/start must be rechecked |
| Astra: `codex`, `gpt-6-astra`, high | Substantive concurrency failures and accepted source/image/evidence reviews | Qualified historical review scopes only; same family as Sol, cannot cross-family review Sol |
| Older Sol: `gpt-5.6-sol` | Historical Codex catalog presence, no new task execution demonstrated here | Compatibility candidate, not task-qualified or capacity-verified |
| Luna: `codex`, `gpt-6-luna`, medium | Accepted bounded guide/index updates; last R7B 49 coordinator documentation checks | Inventory/docs candidate; code/review competence must be separately qualified |
| Argon: `antigravity`, `gemini-4-argon`, high | Accepted UC work; requested/effective alias recorded, backend self-report conflicted | Route history retained; underlying family/backend certainty unresolved for cross-family gate |
| Flash: `antigravity`, `gemini-3.8-flash-high` | Accepted bounded Flic/HA-validation corrections | Refresh adapter/provider/family/tool proof and quotas; no automatic reviewer qualification |
| MiniMax M3: `minimax-coding-plan/MiniMax-M3` | Some accepted bounded docs; persistence track needed Sol takeover; quota exhaustion retained | Limited task-fit candidate; no current verified quota |
| MiniMax M3.1 Flash Preview: `minimax-coding-plan/MiniMax-M3.1-Flash-Preview` | Catalog/configured; earlier requested M3.1 actually executed M3 | No verified M3.1 project execution; do not relabel M3 receipts |
| DeepSeek Pro: `deepseek/deepseek-v4-pro` | Historical OpenCode catalog; no accepted exact execution established | Architecture/concurrency review hypothesis only; access/launch/review qualification unknown |
| DeepSeek Flash: `deepseek/deepseek-flash` | Historical catalog; helper `deepseek-reasoner` was a mismatched alias | Bounded audit hypothesis only; reconcile exact route, helper routing and qualification |
| Claude/Anthropic | Historical Phase 6/7 work remains attributed | **Policy-excluded** in all new author/review/helper/fallback roles; do not probe/dispatch |

Orca 1.4.230 `worker-start --help` now advertises OpenCode overrides only in
existing worktrees with host CLI/model verification; effort unsupported. This
is **launch capability documentation**, not proof that M3.1 or DeepSeek executed.
The older blanket override rejection in launch notes remains historical.

### Quota observation and dispatch hold

| UTC observation | Provider / account-pool scope | Remaining / windows / reset | Commitments / decision |
| --- | --- | --- | --- |
| Not measured in instruction-only task | Codex/OpenAI, pools not enumerated | **Unknown**; no supported usage report captured | Existing cross-project demand unknown; hold future dispatch pending verified headroom |
| Not measured in instruction-only task | Antigravity/Google, pools not enumerated | **Unknown**; historical credit footer is not a measurement now | Refresh supported usage reporting and family proof before eligibility |
| Not measured in instruction-only task | MiniMax/OpenCode route, pool unknown | **Unknown**; prior exhaustion retained as negative history | Hold; fallback also needs its own verified headroom |
| Not measured in instruction-only task | DeepSeek/OpenCode route, pool unknown | **Unknown**; catalog does not prove access or credits | Hold; selection/access/tool/review qualification also outstanding |

No row above is verified headroom. Model/account listing is not quota reporting.
No launch is required to complete this documentation task.

### Instruction-maintenance record

| State | Record |
| --- | --- |
| Authorized / planned | Owner requested durable repository instructions and entry-point updates only |
| Launched | **None**; no author/reviewer sessions or worktrees created |
| Review | Coordinator policy/consistency inspection only; no independent implementation review or fresh qualification claimed |
| Changes | New root AGENTS, complete protocol, reusable ledger; additive links/clarifications in existing coordination, inventory, contribution and handoff entry points |
| Verification | Existing core/client documentation suites: **359 passed, 1.67 s**, exit 0; nine affected docs: **131 local links, five anchors**, zero failures; `git diff --check` exit 0; actual commands below |
| Integration / publication | Scoped Conventional Commit on `wp-runtime-completion`, then normal push to origin; resolve the containing commit in Git history. Exact completed push/head-equality status is recorded outside its own commit in `build/instruction-recording/publication.json` and the appended host handoff; this row alone does not assert remote success |
| Cleanup | Not applicable: no workers created; unrelated/unresolved resources preserved |

Actual documentation verification (Python 3.12 project venv on Windows):

```powershell
.venv/Scripts/python.exe -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py -p no:tests.route_inventory -q --junitxml=build/instruction-recording/documentation-tests.xml
.venv/Scripts/python.exe -X utf8 .git/check_instruction_docs.py
git diff --check
```

The disposable local checker validates relative Markdown files/anchors and
whitespace across the nine owned files; its result is retained in
`build/instruction-recording/documentation-check.json`. It is not shipped tooling
or a model-authored implementation package. The route-inventory writer is disabled
for this partial documentation run; complete-route evidence is not regenerated.
The scoped commit uses invocation-only `git -c core.hooksPath= commit` to avoid
the broad runtime hook during instruction maintenance. Persistent hook settings,
runtime/tests, registry/ledger, immutable evidence and visual baselines are not
changed. Final staged whitespace/path checks follow before commit.

### Readiness carried forward, not requalified

Historical clean source `1baac3de`: 4,041 local core passes/four platform skips,
177/177 REST routes, 100 dedicated Remote tests, 1,506 source client outcomes,
193 image outcomes and accepted combined evidence gate. Final documentation-head
[CI39239356448](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/39239356448)
at `6dafb009`: every non-UI required job passed; UI 1,098 passed, 33 skipped,
three existing Tron paused-frame failures; gallery 62 passed. Those are
historical results, not checks run by this instruction task.

Open vectors: owner visual approval; HIL-B/C/E physical devices, owner HA/LAN
and firmware; continuous 72-hour soak and week field sign-off; feature targets
below required evidence levels; prospective cross-family review for new
implementation; final canonical version/matching rebuilt artifacts and gated
PR/release sequence. Preserve the unchanged red conditional disconnect probe.
Neither a same-family historical review nor a gallery capture closes these gates.

## Release-readiness planning package (2026-10-19)

The owner's subsequent **proceed** authorizes the proposed evidence-gap inventory
and release-validation checklist. Scope is coordinator-owned planning/prose and
read-only evidence analysis. No implementation wave, model probe, worker/worktree,
hardware action, soak collector, baseline approval, merge to main or tag is started.

| Field | Observation / disposition |
| --- | --- |
| Base / publication target | Initial local/origin `wp-runtime-completion` = `621288b11580f348d24481a2973622a4f1f1855a`; publish scoped planning docs through draft PR #38 |
| Existing Run / runtime | Read-only recheck confirms `run_37205f6095b3`, Orca 1.4.230/runtime `ba9443bb-3d71-459a-8dff-4b535678d276`; no Run reset or mutation |
| Protected / capacity | Root and unresolved persistence workspace preserved; 38 released/two null-resource retained rows; standing four-total ceiling remains conservative, not measured Orca capacity |
| Staffing / quota | No dispatch. Provider quotas remain unknown; no model catalog or runtime qualification is asserted by this planning work. Any future EV package needs fresh exact routing, headroom and qualified cross-family implementation review. Anthropic excluded. |
| Read-only evidence computation | Existing registry/findings/scenario/ledger policy, committed evidence only, at exact base SHA. All 268 features mapped once: 89 software-target gaps, 120 hardware-target gaps, one field-target gap, 58 numerically at target. |
| Software follow-up partition | 14 target-level mapped, 29 with scenarios but no mapped target-level client, 46 without discoverable scenarios. Scenario mappings use `features_for(client)`; declared mappings are not passes or verified driver support. |
| Overlays / limits | 68 stale features; 12 HIL-09 caps; three numerically at-target stale rows and 15 at-target rows without fresh passing records. Overlays overlap; no targets lowered or levels promoted. No fresh runtime/schema/hardware qualification. |
| Artifacts | `build/release-readiness/evidence-gap-snapshot.json` preserves initial analysis; `evidence-gap-snapshot-refined.json` narrows per-client attribution. Local audit/render helpers live under `.git/`, not shipped tooling. Command/check/publication receipts remain alongside snapshots. |
| Deliverables | `docs/validation/RELEASE_EVIDENCE_GAPS.md`, `RELEASE_VALIDATION_CHECKLIST.md`, discovery links in docs/validation indexes and current plans, this ledger entry and append-only host handoff |
| Documentation verification | **359 existing documentation tests passed, 1.48 s**, exit 0; seven owned docs: **122 local links/four anchors** pass; all **268 rows** match the pre-existing ledger and read-only computation; all **six protected input hashes** unchanged; whitespace passes. The initial disposable checker misread bold at-target levels; that diagnostic is preserved and formatting-aware comparison passes without changing product evidence. |
| Integration / publication | Scoped Conventional Commit then normal origin push. Resolve the containing commit from history; exact post-push remote equality is recorded in `build/release-readiness/publication.json` and the host handoff, outside its own commit. |

Proposed EV-01 through EV-05 scopes are **planned only**, with no Task/Dispatch,
observed start, implementation-review verdict, integration or qualification
claimed. EV-01 first distinguishes reusable original proof from required reruns,
missing assertions and actual behavior findings; the other packages depend on
that disposition. Historical software passes and final-head CI observations stay
attached to their recorded commits. Release acceptance remains open.

Verification uses the existing Python 3.12 project venv:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py -p no:tests.route_inventory -q --junitxml=build/release-readiness/documentation-tests.xml
.venv/Scripts/python.exe -X utf8 .git/check_release_readiness_docs.py
git diff --check
```

The local checker/audit helpers are disposable planning aids, not shipped
implementation tooling. Exact commands and exit receipts are retained in
`build/release-readiness/verification.json`; partial documentation checks disable
the shared route-inventory writer. The commit uses the documented invocation-only
empty `core.hooksPath` exception to avoid broad runtime tests during prose
maintenance; persistent hook settings remain unchanged. No fresh runtime/model/
hardware qualification is inferred from these checks.

## EV-01 reconciliation execution (2026-10-20 UTC)

Owner authorized remaining release-readiness coordination, starting with EV-01.
This entry records **in-progress coordinator evidence reconciliation**, not a
new implementation campaign. No author/reviewer/worktree has been launched.

| Field | Observation / decision |
| --- | --- |
| Initial base / remote | `wp-runtime-completion` at `95f64920220fd5269007272ed8f3cbe04604db7e`; origin URL revalidated; exact remote and PR receipts under `build/ev01-20261020/` |
| Existing Run | `run_37205f6095b3` present; no reset/replacement. Initial `run-current` is null in this invoking session; old coordinator handle is historical, not claimed live. |
| Runtime / host | Orca 1.4.230, runtime `7974a428-1f2a-4689-96bc-69590e2df7d0`; local Windows host Zelu. Saved SSH hosts are disconnected. |
| Worker accounting | Run-scoped complete inventory: 38 released, two retained compatibility entries; no new dispatch. Four-total project ceiling remains conservative, further subject to verified host/provider limits. |
| Ownership | Coordinator owns read-only reconciliation, a new EV-01 report and scoped integration records. Product, tests, registry, generated ledger, immutable evidence and visual baselines remain protected. |
| Protected resources | Root/private data, unrelated encoded hook artifact and unresolved `wp-runtime-persistence-wiring` workspace preserved; no cleanup attempted. |
| Staffing / quota | Catalog/capability/usage discovery in progress. No verified quota headroom yet; affected worker creation and dispatch held. No Anthropic or non-Orca substitute. |
| Acceptance | Per-feature source-linked disposition for the union of 14 target-mapped software gaps, 26 stale software gaps and 15 at-target rows without fresh proof; inspect original assertions, client mapping, covers, source/environment/image identities. No automatic level promotion. |
| Receipts | New `build/ev01-20261020/` destinations only. Initial capture saved all subprocess receipts but console rendering hit Windows cp1252 on terminal preview; receipt bytes were retained. Subsequent output uses UTF-8. |

EV-02/03 implementation dispatch and EV-04/05 owner execution remain dependent
on actual disposition, verified staffing capacity and their separate gates.

### EV-01 observed execution and staffing gate

Read-only discovery and reconciliation completed on 2026-10-20 UTC; no model
inference probe or worker launch was used. Supported app-server model/usage
reads are account queries, not an implementation/reviewer dispatch. Current
Codex CLI is 0.163.0 and OpenCode is 2.0.32. Exact catalog/usage responses and
command receipts are local in `build/ev01-20261020/`.

| Candidate / exact route | Current observation | Fit / capacity decision |
| --- | --- | --- |
| Sol 6.1 / `codex:gpt-6.1-sol` | Live `model/list`, high supported; historical qualified systems work | Core implementation candidate. Current invoking pool has measured usage below; future worker's actual account binding/commitments still need verification. No dispatch. |
| Astra / `codex:gpt-6-astra` | Live catalog, high supported | Difficult composition candidate; same family as Sol, cannot close its cross-family review gate. No dispatch. |
| Older Sol / `codex:gpt-5.6-sol`, `gpt-6-sol` | Both in live catalog; high supported | Compatibility routes, not newly task-qualified. Same pool/family limits. |
| Luna / `codex:gpt-6-luna` | Live catalog; medium supported | Suitable bounded inventory/documentation candidate; coordinator completed EV-01 directly, so no worker needed. Not a cross-family implementation reviewer. |
| Argon / historical `antigravity:gemini-4-argon` | OpenCode currently lists `opencode/gemini-4-argon`; native Antigravity selection/backend/access and pool quota not verified | Historical native alias is not current cross-family identity proof. Hold; do not substitute the OpenCode route. |
| Flash / historical `antigravity:gemini-3.8-flash-high` | OpenCode lists `opencode/gemini-3.8-flash`; native high alias/access/quota not verified | Bounded QA hypothesis only; different selectable route is not an authorized silent substitute. Hold. |
| MiniMax / `minimax-coding-plan/MiniMax-M3` | Current supported `opencode models` lists it; primary configuration selects it | Historical exhaustion and bounded-task limits retained. Remaining credits/windows unknown; hold. |
| M3.1 / `minimax-coding-plan/MiniMax-M3.1-Flash` | Current catalog uses this ID; helper configuration still names `MiniMax-M3.1-Flash-Preview` | Exact variant mismatch; effective helper selection and quota unverified. Hold, no relabeling. |
| DeepSeek Pro / `deepseek/deepseek-v4-pro` | Current catalog presence | Review-domain competence, access and balance unverified. Hold. |
| DeepSeek Flash / `deepseek/deepseek-flash` | Current catalog presence; helper config still uses `deepseek/deepseek-reasoner` | Helper/catalog mismatch and unverified capacity/review competence. Hold. |
| Anthropic | Policy-excluded in every new role, including nested/default/plugin routes | No launch or probe. OpenCode plugin-supplied defaults remain unverified and ineligible. |

Quota observation: `account/rateLimits/read` at **2026-10-20T02:56:41Z**
(exact response timestamp in `codex-quota.json`) reports ordinary usage allowed,
34% used / **66% remaining** in the current managed Codex account's **10,080-minute
weekly window**, reset **2026-10-25T20:07:49Z**; no secondary window was supplied.
Additional credit balance is zero, no reset credits available, and no spend
control reached. This is included weekly capacity, not a claim of prepaid credits.
The account is shared with this coordinator; unobserved cross-project demand
and the pool Orca would select for a new worker are not quantified. Do not
transfer this observation to a different/default worker account. No inference
probe or account/global preference change was performed. OpenCode statistics
help describes usage history, not remaining provider balance; MiniMax/DeepSeek
headroom remains unknown. Google quota and backend-family proof remain unknown.

Host/launch observation: only local Windows execution verified; saved SSH
targets disconnected. Repo setup/archive scripts are empty, setup policy runs
by default with start-immediately. Current `worker-start --help` supports named
Codex model/effort and OpenCode selection in an existing worktree only, without
effort. No setup/default-tab or opaque plugin route was executed. The project
ceiling remains four total, subject to verified pool/host limits; no numeric
Orca engine capacity is asserted. Unknown alternate-family capacity means no
suitable verified implementation-review fallback has been established.

### EV-01 result, verification and publication

| State | Evidence / decision |
| --- | --- |
| Run binding | Supported `run-use` rebound the existing Run to live coordinator `term_259c5526-02c2-44a8-b469-bf171aa435a0`, generation 2. Prior handle was historical; no Run reset/replacement or worker mutation. |
| Completed | [Per-feature reconciliation](../validation/EV01_EVIDENCE_RECONCILIATION.md): 42-feature union, seven primary preservation cases and 35 missing mapping/assertion cases; no primary rerun solely for unchanged runtime inputs, no newly reproduced product defect. |
| Original records | 2,728 schema-valid, per-client-mapping-consistent records: 907 passing source `1baac3de`, 907 passing candidate-CI and 914 old committed (906 pass/eight fail). All 907 selected source records have fresh covers. Original bytes/hashes retained; 146 source records for seven preservation cases copied and verified to a new local archive. No ledger import. |
| Candidate CI | Run 39305698510 completed for head `95f64920`. Record SHA `66a82c32885baf0893cbd06e57715251e14fd4d0` has parents #37 head and `95f64920`; its tree equals candidate tree `472c02738fa78f7928d2039e98b56f5b0471e42b`. All twelve non-UI required checks pass; actual UI JSON 1,098 expected/33 skipped/three Tron failures/zero flaky, 59 smoke/flow expected results; review capture 62 passes. No visual approval. |
| Reviewed | Coordinator source/assertion/provenance inspection and existing documentation checks; no independent model reviewer dispatched and no implementation-review acceptance claimed. New implementation review remains held for a qualified different family with verified capacity. |
| Integrated / qualified | Coordinator-owned documentation/evidence-index package only. Product/tests/fixtures/tooling/registry/generated ledger/baselines unchanged; no runtime, feature-target, HIL, soak or final release qualification. |
| Verification | 359 existing documentation tests passed (1.89 s), route-inventory plugin disabled; seven owned files, 94 local links/two anchors, 42-feature/2,728-record correspondence and all six protected input hashes pass; whitespace passes. The shared root route report was observed only after these tests; no pre-test hash is claimed. |
| Publication | Normal scoped commit/push to `origin/wp-runtime-completion`; exact post-push local/remote equality receipt is `build/ev01-20261020/publication.json`, outside its own commit. This row is not a claim that the push already happened. |
| Lifecycle / cleanup | No new Task/Dispatch, worker, worktree or task branch; no cleanup. Existing retained entries and unresolved persistence workspace preserved. |

EV-02/03 are now **scoped by evidence**, not launched or qualified. Existing
proof can be preserved without inventing a new runtime pass; missing client
assertions require implementation and qualified cross-family review. The
specific staffing hold is unverified alternate-family account capacity,
effective routing and domain-review qualification, plus exact future worker
account binding. Owner visual/physical/72-hour/week/final-artifact gates remain.

Actual verification uses the project Python 3.12 venv:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py -p no:tests.route_inventory -q --junitxml=build/ev01-20261020/documentation-tests.xml
.venv/Scripts/python.exe -X utf8 .git/ev01_verify.py
git diff --check
```

Disposable `.git/ev01_*` audit/check helpers are coordinator analysis aids, not
shipped implementation tooling. The portable JSON is derived reconciliation
metadata; original evidence bytes were not reformatted. Its compact encoding
keeps it below the repository's 2 MiB artifact limit. The scoped documentation/
evidence-index commit uses invocation-only `git -c core.hooksPath= commit`
to avoid the broad runtime hook for a package with no product/test/tool changes.
Persistent hook settings are unchanged; no full-suite/hook success is claimed.
Post-commit hygiene and exact publication checks are recorded in local receipts.

## Reusable phase or wave entry

Copy this section for each authorized wave. Use `unknown`, `held` or `not
applicable` with a reason rather than empty success-looking fields. Reference
full receipts outside private account material; append corrections and failures.

### Identity, authorization and constraints

| Field | Value to record |
| --- | --- |
| Wave / UTC / authorized scope | Owner request; technical gate authorization distinct from standing policy |
| Run / current coordinator / host | Existing Run, validated live handle/runtime, repo ID; no invented replacement |
| Integration / remote | Actual branch/full SHA, upstream/URL, PR dependency chain, last verified remote equality |
| Protected inventory | Root/unrelated/retained/unresolved workspaces, private data, refs and evidence |
| Capacity | Interface/runtime/host/nesting/provider limits, all existing commitments, effective ceiling |
| Catalog / capability refresh | Time/source/cache age per host, exact IDs, adapter selection/effort/helper support |

### Candidate assessment and quota gate

One row per allowed candidate and route, including rejected alternatives.

| Candidate / family / exact route | Catalog / access / launch support | Author qualification / reviewer qualification | Quota receipt, UTC, pool, remaining, windows/reset, commitments | Selection or hold / fallback rationale |
| --- | --- | --- | --- | --- |
| Unassessed | Unknown / unknown / unknown | Unknown / unknown | Unknown; not verified headroom | Held until suitable route and verified capacity |

### Assignment and execution receipts

| Task / dependency / state | Base SHA / actual branch / host / worktree | Exclusive writable / prohibited / coordinator-owned paths | Requested vs effective model/effort; family proof | Quota gate / launch receipt / observed start / Dispatch | Acceptance and artifacts |
| --- | --- | --- | --- | --- | --- |
| Planned; not launched | Record exact bindings | Record disjoint boundaries | Do not silently inherit/substitute | Unknown quota holds dispatch; start request is not observed start | Behavioral checks, environments, output destinations |

Record mid-task quota changes, limit responses, questions, lifecycle/liveness
evidence, failed attempts and any retry-of chain. No ambiguous duplicate writer.

### Independent review and correction

| Package / exact author SHA | Author family | Reviewer exact model/family and domain qualification | Review SHA / methods / findings | Author correction / material integration change / re-review SHA | Gate disposition |
| --- | --- | --- | --- | --- | --- |
| Not reviewed | Unknown | Different underlying family required, checked quota | Actual source/assertions/behavior, negatives preserved | Authors fix; reviewers report | Held until qualified independent acceptance |

### Integration, combined verification and preservation

| Package / base-boundary audit | Worker-worktree checks / reviewed SHA | Sequential integration SHA / re-review | Combined commands, environment, exits, skips/limits | Full bundle verification, hashes, recovery proof / tracked-untracked-ignored patches / complete transcripts | Task remote ref equality / preservation gaps |
| --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Historical passes are not fresh results | Save outside cleanup target; protect private data | Hold destructive cleanup if incomplete/unpublished |

### Settlement, cleanup and synchronization

| Task / Dispatch / outcome | Reuse / explicit retention / release receipt before ack | Full preservation and integration proof | Exact Orca removal / local branch deletion or hold | Integration commit / push / exact remote-local SHA / time | Qualification scope / remaining gates |
| --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Never broadly prune or force | Verify before next execution wave; receipt outside its own commit | Planned/completed/reviewed/integrated/qualified/published stay distinct |

Close the wave with unresolved findings, unknown capacity/identity, retained
resources, remote synchronization and next authorized action. Do not erase a
failed assignment when its fallback succeeds.
