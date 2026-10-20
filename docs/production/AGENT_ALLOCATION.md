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

## Owner visual approval and provider rediscovery (2026-10-20 UTC)

Owner explicitly approved the three existing Tron paused-frame differences
(desktop, kiosk-tab-a11 and kiosk-iphone16promax) and deferred arranging physical
validation. This is specific visual-update authority; hardware/field actions
remain pending. The owner also directed the coordinator to inspect provider
quota through Orca rather than delegate that discovery back to the owner.

Initial binding: integration/origin `bbeaae4a70752b65c131fe87f226b77c5f0e4187`,
same Orca 1.4.230/runtime `7974a428-1f2a-4689-96bc-69590e2df7d0`, existing Run
`run_37205f6095b3`, 38 released/two retained compatibility entries; no new worker.
Root/private data, historical evidence, unrelated encoded hook artifact and
unresolved persistence workspace remain protected. No release/tag/main merge.

Coordinator testing uses a fresh tracked-source export under
`build/visual-approved-20261020/source`, with hydrated baseline copies and
separate preserved before images. No private/untracked root data is copied.
Docker Desktop was initially stopped and was started using its supported
detached command; the existing pinned Playwright image matches CI digest
`sha256:eff16c30e6f3f4af0a03fa4b706120d5e9b0891c344a27d64559aff5900a4a27`.
Only the three approved captures are regenerated in that isolated export;
root baselines remain untouched pending verification. Separate baseline-only
approval commit and actual visual checks are required before claiming closure.

Provider discovery is in progress through Orca's native Usage UI. Preliminary
status/menu observation exposes Antigravity's **Gemini Models · Weekly Limit
Remaining 77%**, MiniMax **70% / 3d 4h**, and Codex **36% / 5d 16h**. The latter
two displays need used-versus-remaining and window/account details; these
rounded footer values alone are not yet recorded as verified launch capacity.
No excluded-provider action was invoked. The CLI has no advertised general
quota command; native UI access is being used. Current routing, access,
commitments and reviewer qualification must still pass before dispatch.

### Verified follow-up observations

The footer is in **Used** display mode. Its rounded Gemini 77% used means
approximately 23% remaining (held, below 30%); MiniMax 70% used means about 30%
remaining (held near the floor; limiting reset about 3d 3h). Codex later showed
37% used, about 63% remaining, limiting reset about 5d 16h. These are shared
pools; unrelated project commitments are visible but not fully quantified.
No Antigravity account switching is supported on this Windows host. No excluded
provider was invoked. The preliminary label above is retained as observed,
not interpreted as 77% available.

Authenticated, non-inference DeepSeek API reads at **2026-10-20T03:34:17Z**
reported `is_available: true`, **USD 33.45** available/top-up balance, grant zero.
The configured OpenCode system-default account is shared; API keys were kept
in memory and never exported. The current authenticated catalog confirms
`deepseek-v4-pro` (DeepSeek-V4-Pro) and `deepseek-flash` (DeepSeek-V4.1-Flash).
Credit expiry/reset and aggregate other-project commitments are not reported.
Reserve USD 5 for a bounded review/correction cycle; this is an allocation
estimate, not a provider-enforced spending cap. Rate limits remain unreported.
Receipts: local `build/provider-preflight-20261020/deepseek-{balance,models}.json`.

OpenCode 2.0.32 has unqualified global helper plugins/defaults. A disposable
project-local routing configuration was checked without inference: provider
policy denies all except DeepSeek, external helper plugins and MCP are denied,
subagents are denied, and primary/title/summary/compaction models are pinned to
DeepSeek Pro. `opencode models --standalone` exposes exactly the two confirmed
DeepSeek IDs; `debug agents` confirms the pinned models. Global preferences
were not changed. The exact managed review worktree must repeat these checks;
effective launch selection and substantive review qualification remain pending.

The baseline-only commit is `10f788f692881edf329d247de17c5679e1dba2eb`.
[Approval record](../validation/TRON_OWNER_APPROVAL_20261020.md) and portable
manifest preserve hashes and the separate three-pass normal comparison.
Root baselines were copied only after that comparison passed. Full affected CI
at the published head remains pending; no failed historical run was rewritten.
Invocation-only hook bypass was used for this baseline-only commit; persistent
hook settings were unchanged and no full hook pass is claimed.

Next bounded EV-02 package is **planned, not launched**: F-API-018 input rename
scenario and behavioral assertions, Sol 6.1 high author; DeepSeek Pro independent
review at the exact author commit. Author may edit only
`tests/validation/scenarios/writes.py` and its assigned new report/artifact paths.
Registry/ledger, root manifests, shared runner/contracts and product routes
remain coordinator-owned. No physical device actions. Acceptance must include
independent simulator readback, exact command and no unrelated mutation, with
meaningful negative coverage and actual scenario execution. No feature target
is promoted until mapping, evidence and independent review are accepted.

The subsequent supported Codex `model/list` and `account/rateLimits/read`
refresh confirms Sol 6.1, Astra, older Sol and Luna routes in the invoking
managed pool. At the timestamp in local
`build/provider-preflight-20261020/codex-quota.json`, weekly use is 38%, **62%
remaining**, reset **2026-10-25T20:07:49Z**, ordinary usage allowed, no additional
credits. Sol 6.1 high is selected for the bounded scenario package based on
prior backend/test work; Astra's concurrency strengths are unnecessary here;
older Sol and Luna supply no cross-family review. Gemini Argon/Flash are held
for low shared quota and uncertain alias routing; MiniMax M3/M3.1 are held near
the quota floor. DeepSeek Pro is the reserved review candidate; Flash is an
available same-family alternative, not an independent review of Pro work.

Coordinator documentation checks for the approval package: 440 passed in
7.04 seconds with `-p no:tests.route_inventory`; `git diff --check` passed.
The root runtime route report is not regenerated by these supplemental tests.
No implementation package or review has yet been delivered.

### EV-02 first dispatch checkpoint

Visual/coordination publication verified local and remote equality at
`3979d6020165bcf31f0f44f21de6bb5b3648dc1e` before placement. Current-head CI
is run `39365581349`, initially pending behind the prior UI run.

An agent-free review worktree was created at that full base through Orca:
`wp-ev02-name-review`, actual branch `ryan-haver/wp-ev02-name-review`, instance
`a1c35c93-ba14-4b97-97ed-da157695cf20`. Its local untracked `opencode.json`
repeats the restricted routing; managed-worktree model listing confirms exactly
DeepSeek Flash/Pro and debug agents confirms the pinned internal models.
An initial relative copy failed and a non-inference model listing consequently
reported plugin activation unavailable; corrected absolute copy and checks
passed. No inference or model substitution occurred during those probes.

Author Task `task_9341adb87ed9`, Dispatch `ctx_f12cb2321b79`, actual branch
`ryan-haver/wp-ev02-input-name`, full base above, dedicated worktree
`wp-ev02-input-name`. Start receipt requests/effectively selects Sol 6.1 high,
but reports **outcome_unknown / turn_start_unobserved** after input acceptance.
Handle `term_54b9e257-f74f-4cb9-bef6-dceb0b551071`; resource
`wtr_8a3c67ec5a66`. This is not observed task execution, failure or completion.
No duplicate writer is dispatched. Installed recovery reference was read;
inspect the exact worker and preserve authority/resources while liveness is
unverifiable. Receipt is local `build/ev02-name-coordination/author-start.json`.
Reviewer is provisioned only, not dispatched. Project budget remains at most
four agents including coordinator; no other new project worker is active.

Recovery inspection showed the exact original `[Pasted Content 7540 chars]`
still in the author composer. An Enter-only send submitted that existing draft;
the screen then displayed the live preamble/task and **Working** state. No text
was resent, no new Task/Dispatch was created and no resources were abandoned.
The attempted combination of Enter-only with `--wait-submit` was rejected before
mutation because observation requires text; a subsequent supported Enter-only
send wrote one byte. Receipts are preserved beside the original start receipt.
The author was asked to verify its own account-pool headroom before edits and
hold if different/unknown. Review remains dependent on the exact author commit.

Author own-environment capacity confirmed at **03:45:10Z**, managed pool suffix
`4ed0`, weekly 62% remaining/reset 2026-10-25T20:07:49Z, ordinary usage allowed.
Provider transcript and fresh agent status now positively show Sol 6.1 working.
DeepSeek balance/catalog refresh at **03:45:46Z** still reports USD 33.45 and
the same two exact models; local receipt subdirectory `review-refresh`.

The original author brief erroneously permitted an implementation hook bypass.
Coordinator withdrew that sentence before any observed author commit and
required the normal hook. To resolve the expected symmetric-mapping test
failure without transferring shared ownership, coordinator changed only the
F-API-018 `scenarios` list **inside the task worktree** to include the three new
IDs. The author leaves that file unstaged and commits only assigned paths;
coordinator will commit the mapping after author settlement. Review must inspect
the final combined task-branch SHA/diff, and clean-candidate evidence is required.
No root registry change or target promotion has been made at this checkpoint.

Subsequent receipt establishes that author commit
`0a7d71b2e509b558263bc164a384f157195d96e9` used the original brief's erroneous
hook exception **before the correction was read**. Preserve that attribution;
do not rewrite history or call it a normal-hook commit. Author is correcting
the report and running the complete normal hook before delivery. Coordinator's
first mapping patch also introduced excess YAML indentation; it was corrected
immediately and independently parsed successfully. No malformed mapping was
committed. These mistakes do not establish an implementation or review pass.

The initial health `version: 2.10.0` is the existing REST `API_VERSION`, not a
different installed hub: author verified `run.py` loads the exact worktree's
source modules and `hub.__version__ == 1.0.0rc1`. Keep API/application versions
distinct. Prior documentation-head CI `39362841065` was ultimately cancelled,
not a completed current-head visual result.

### Review adapter checkpoint

Review worktree was fast-forwarded to exact author code commit `0a7d71b2` for
preliminary source/assertion review while the author's full hook runs. Final
mapping/report delta remains a required follow-up, not an accepted review yet.
Explicit OpenCode model override failed preflight with `capability_unsupported`:
"This OpenCode TUI cannot verify launch-time model selection." Request
`4db09db2-6a00-418a-ba95-9e761efd4b85`; request-show is absent and Run-scoped
fleet remains 41 entries with only the one new author Dispatch. No review
Task/Dispatch/terminal was created by this refused placement.

Use the error's supported configuration route next: omit the unsupported CLI
override while the worktree-local configuration explicitly pins primary and
internal models to `deepseek/deepseek-v4-pro`, denies other providers and helper
routes, and exposes only the two authenticated DeepSeek models. This is a
recorded selection-mechanism change, not model substitution. No effort override
is supported. Effective provider/model and real tools must still be observed
before any reviewer qualification or gate closure. Preserve the refused receipt
at `build/ev02-name-coordination/review-start.json`.

Configured-route supervised review start succeeded: Task `task_515977753dd0`,
Dispatch `ctx_15fe6f7a06be`, handle
`term_3ccdd3e2-b8e8-40b6-b203-c29896ce7a4e`, resource `wtr_5899b6ccbb63`.
The control-plane launch reports model/effort null because the configuration
route is used; do not relabel that receipt as an explicit model override.
The actual terminal positively displays **Build · DeepSeek V4 Pro DeepSeek**
and substantive task reasoning, and fresh Orca status reports working/live.
Together with local pinned configuration, restricted catalog and authenticated
provider model IDs this establishes the selected DeepSeek route; actual review
competence and accepted findings remain pending. Saved exact terminal screen
and observation receipts under `build/ev02-name-coordination/`.

### Preliminary review delivery and settlement

DeepSeek's supported session export independently confirms model
`deepseek/deepseek-v4-pro`, variant `default`, in actual assistant messages.
Complete private JSON export is preserved locally; sanitized exports redact
tool input/output and therefore are not the complete transcript. Substantive
source/runner/simulator inspection, 59 pytest passes, Ruff and three V2 outcomes
with 24 passing checks support bounded API-scenario review competence. No
blocking code findings; three informational scope observations are preserved.
Review commit `37216b6b7d700a93d21db7fa993c11ffe453373f` is **preliminary only**.
Final registry mapping, normal-hook result and exact combined SHA remain held.

Coordinator found a prose envelope typo in the review (top-level `error: null`
was printed inside `data`) and requested correction before completion. It was
not processed: the reviewer's final inbox check truncated output to 40 lines
and omitted that queued follow-up. Preserve this coordination/report defect;
the code assertions and actual passing records have the correct envelope.
Correct the report and inspect the entire delivered inbox during final review;
do not silently edit a reviewer's report under coordinator attribution.

Full-history review bundle was verified; task ref was published and exact
remote/local SHA equality confirmed at `37216b6b`. Before acknowledging delivery
`delivery_30eabc095115`, coordinator attempted supported `worker-release`.
Orca returned **retained / user_takeover / processAction none / archive null**.
This is a safety retention, not a released terminal or an explicit owner request
to retain it. Preserve this session/worktree and do not force-close or remove
it. Receipt `build/ev02-name-coordination/review-release.json`; no cleanup
authority is inferred. Complete provider export and bundle already exist;
remaining artifacts/settings must also be preserved before any later removal.

Review workspace preservation now copies all 4,285 files (268,789,227 bytes),
excluding only `.git` (preserved by verified full-history bundle); every copied
file hash matches its source. Complete provider JSON, tracked/untracked/ignored
artifacts and local routing settings are retained outside the managed worktree.
Snapshot is not removal authority: Orca's user-owned resource remains preserved.

Author normal hook **failed** after 3,816 passes, 22 skips, 35 deselections:
`TestJavaScriptLinting.test_npm_run_lint_js_passes` could not resolve `@eslint/js`
from the task checkout. Shared `NODE_PATH` does not resolve that ESM import.
Route inventory still measured **177/177**. Preserve original log/JUnit; this
partial run is not a full-suite pass. Coordinator proved local `node_modules`
absent and installed the unchanged lock with
`npm ci --ignore-scripts --no-audit --no-fund` (190 packages, exit 0, 3 seconds).
No manifests, lockfiles or tests changed. Author must confirm the failed node
and rerun the normal hook with a new destination before acceptance. This is
environment setup diagnosis, not a fabricated product finding or waived test.

At **04:03:49Z**, authenticated DeepSeek balance is USD **31.32** and the same
Pro/Flash catalog remains available. Other shared-account activity accounts for
unattributed consumption beyond this session's observed USD 0.20; do not assign
all balance movement to this project. USD 5 remains reserved for the bounded
review cycle. No account/settings/model changes were made.

The exact settled DeepSeek session is positively done/live and its task branch
is clean at `37216b6b`; no unexpected user edits were found. A supported
same-terminal `worker-start` accepted the immediate report-only correction:
Task `task_850114b80411`, Dispatch `ctx_42a2e7a0a189`, same exact handle/process,
same worktree/model configuration. This is explicit reuse under fresh authority,
not force-release or deletion of the retained resource. It owns only the review
prose and assigned build artifacts; original preliminary verdict stays held for
final mapped-SHA review. Entire delivered inbox must be inspected without the
prior 40-line truncation. Original retention receipt/history remains unchanged.

Report-only correction delivered at
`c384dff856752fc5724834974cb703ba34c7af06`: only `NAME_REVIEW.md`, transparent
correction note, top-level envelope fixed and dependency claim qualified.
Coordinator audited the diff and published/verified the exact task ref; a new
verified full-history bundle and complete private provider export preserve this
checkpoint. No runtime tests were repeated merely for prose. Before acknowledging
`delivery_40dff201f8f2`, coordinator explicitly reused the same proven session
for a ready, independent EV-02 API-preservation audit under new authority.

New Task `task_c339a58870e0`, Dispatch `ctx_0f509ee13c00`, full base `c384dff8`
(full SHA above), same exact host/worktree/terminal/DeepSeek route. Exclusive
new report `docs/production/ev02/API_PRESERVATION_REVIEW.md` plus
`build/ev02-api-preservation/**`; all product/tests/registry/settings and old
reports prohibited. Audit six EV-01 preservation dispositions F-API-014/016/026/
028/036/038, original source `1baac3de`, actual assertions/client mappings/covers/
environment and attribution. Coordinator copied 144 original source records
hash-exact to a fresh `originals-utf8` directory. The earlier partial copy failed
on Windows default text decoding and remains preserved; it is not used. No
original evidence bytes changed. This is independent original-proof review,
not another runtime run, image pass, import, feature promotion or final input-name
mapped-SHA acceptance. Quota/catalog observation remains the verified 04:03:49Z
DeepSeek snapshot; project agents remain coordinator plus Sol and reused DeepSeek.

Published visual head `3979d602` now has all **13 required CI checks passing**
in run `39365581349`; the additional UI review comment passed and GHCR publication
was skipped for the PR. Actual CI merge `53a4359f7bbd034acf8ae80fc102ec4fb0c0b297`
has verified parents `6debe5a9...` and `3979d602...`, with exact head/merge tree
equality `aae201211708b31185229f10d1fd2ef199e4b74d`. Full UI: **1,101 passes,
33 skips**, including all three approved paused-frame cases. Gallery has three
changed images for that entry, zero unapproved snapshot paths. Complete logs and
gallery preserved in new local CI directory; portable
`docs/validation/runs/tron-approved-20261020/ci.json` indexes results/hashes.
This closes the specific owner visual/update verification at that source tree,
not the newer unintegrated API package or final version/artifact release gates.

Independent API-preservation audit delivered at
`700a7d7e3eadc89748f0718ba43a462c2e96afcc`, new report only. Coordinator audited
the source-linked six-feature dispositions and actual structural checks:
**144/144** byte hashes match both copied index and EV-01 original hashes;
144 schema-valid, 144 actual API client mappings match, all V2/pass at original
`1baac3de`, all image digests null. Declared product/scenario/tool inputs for
these old assertions match published integration `3979d602`; new input-name
scenarios are separately reviewed and not attributed to the old source.
The six original V2 scopes are eligible for coordinator evidence preservation;
no import/level reflection has yet occurred. In particular the shared
`cec.output_power_on` record does not qualify the broader F-API-015 feature.
Do not infer whole-feature qualification from a numerical ledger maximum.

Audit task ref published with exact remote/local equality at `700a7d7e`; full
Git bundle verified and complete private provider export preserved. New audit
artifact snapshot contains 293 files / 9,705,768 bytes, all hash-matched,
including the failed partial copy and successful originals. Supported release
before acknowledgment returned **retained / external_terminal / processAction
none / archive null** because this Task reused an existing terminal. Preserve
the exact session/worktree; do not manually close or remove it. This differs
from the earlier user_takeover retention. Delivery `delivery_c304d925ba50` was
acknowledged after that recorded disposition. Final input-name review still held.

Author delivered final `d8e4e1eff6e394144b7a0d007f500579108c2c88`: only assigned
`writes.py` (+40) and `NAME_AUTHOR.md` (+204), full base/path audit accepted.
Normal configured hook passed repository Ruff and **4,041 core tests**, four
skips, 35 deselections, four warnings, **177/177 routes** in 1,121.68 seconds.
Skips are POSIX permission enforcement/unlink race, HA dependencies and Windows
symlink privilege. Original bypass and failed JS dependency attempt are retained.
Verified full-history author bundle and exact published task ref at this SHA;
complete positively identified provider transcript copied before and after
release. Source logs/JUnit/patches/routes and metadata are being preserved outside
the worktree. Supported `worker-release` **released/closed_agent_terminal**, with
provider transcript **captured**, before acknowledging `delivery_4af52810cb1d`.

Coordinator now owns the settled task worktree's pending mapping and evidence
integration. The mapping-only documentation commit introduces no behavior;
the full normal hook just tested these exact scenario/mapping bytes together.
Generate the ledger to a new diagnostic output and run registry checks serially,
then use the documentation-only invocation hook exception for that mapping
metadata. Do not claim a second full-hook run or use the exception for new test
implementation. A clean exact mapped-SHA four-scenario campaign and final
different-family review remain required before integration/target acceptance.

Author artifact preservation completed: **42,043 files / 138,318,662 bytes**,
all copied file hashes matched. The preliminary full ledger diagnostic was
slower than expected; coordinator proposed consolidating the scan after import
and attempted to stop only its positively identified read-only PID. The PID
guard refused because that process had already completed; **no termination or
cancellation occurred**. The completed output is preserved, and subsequent
serial registry checks passed **17/17 in 2.65 seconds**. Mapping-only commit
`bb4d3fdc972e7f556f29c6ed468accd4ff3b88b5` contains exactly the one-line
coordinator scenario-list change. The required final canonical ledger generation
after evidence import and its serial checks remain pending. Clean mapped-candidate
F-API-018 campaign is now running in a fresh destination; no existing run reused.

Clean mapped source `bb4d3fdc` passed four API name-route outcomes and **31**
checks, zero failures/skips/abort, `dirty: false`. The candidate preserves 144
old original records plus these four records, all with unchanged bytes/source/
timestamp/client/digest fields. Root `.gitattributes` gains three narrowly scoped
`-text` rules for these new evidence/metadata directories; no old bytes are
renormalized. Initial default whitespace checking flags the intentional CRLF
bytes; a preserved reproduction log and invocation-only CRLF-aware check retain
other default whitespace rules. **148/148 staged Git blob hashes match** source.
No persistent Git configuration changed.

Canonical ledger generated first, then **103 registry/schema/ledger/hygiene
tests passed**, two Docker cases deselected (35.34 s), then the formal evidence
gate passed with **zero known failures linked to open findings**. Post-commit
repository hygiene passed. Numerical ledger: 268 features, **205 below target**,
**57 stale rows**. Proposed current-level reflections affect only F-API-014/016/
018/026/028; fresh original proof is also attached for at-target F-API-036/038.
All other feature fields/targets/findings remain unchanged. F-API-015 remains
unqualified for its V3 target; shared API V2 evidence is not V3 client proof.

Candidate preparation includes original independent review history (report-only
merge `3539b190`) and is committed at
`e5ebb376230d1dc6bbb62e07f38b7d4cf8221b32`. Source implementation is unchanged
from independently reviewed `0a7d71b2`. Metadata/evidence/byte-preservation commit
used the scoped invocation hook exception after the full source implementation
hook and affected metadata checks; no new full-hook success is claimed for it.
Task ref `ryan-haver/wp-ev02-input-name` published with exact remote equality;
new full-history candidate bundle verified. **Not yet integrated or finally
qualified.** Final independent review must inspect this exact combined commit.

Final-review quota/catalog refresh **04:48:05Z**: shared DeepSeek account USD
**28.54** available, Pro/Flash IDs unchanged; USD 5 bounded-cycle allocation
remains sufficient, reset/rate limits unreported. Runtime/host/version and blank
setup hooks re-observed unchanged. New agent-free final-review worktree is being
provisioned at full candidate SHA, with the same explicitly pinned DeepSeek-only
configuration route before any agent is started. Project ceiling remains four;
coordinator, old settled retained DeepSeek and new reviewer would total three.

Final-review worktree instance `f512cb8e-a2e3-4bc2-bfac-95e9d4d5e94f`, branch
`ryan-haver/wp-ev02-final-review`, verified full base `e5ebb376...`. Local model
catalog and configuration rechecked: only DeepSeek Pro/Flash selectable, internal
primary/title/summary/compaction models explicitly Pro. A cold first agent-list
read returned empty; a repeat after activation returned the expected pinned
built-in agents. Ancestor `.opencode` directory has no agent/plugin definitions;
all MCP and subagent use is denied, three unqualified global helper plugins are
disabled, and only Orca status hooks remain as external plugins. Global routing
preferences were not changed.

Genuine final review started: Task `task_2f3700b530a4`, Dispatch
`ctx_294f9d071a03`, exact terminal `term_fc3c9481-da5b-425b-99bc-dda198ff526e`.
Configured-route receipt has model/effort null (unsupported CLI override), not a
claimed explicit override. Scope is actual combined candidate/source/assertions,
all record hashes/client mappings and metadata boundaries, actual committed-head
freshness/gate, 4-scenario runtime rerun and final independent verdict. Only new
`FINAL_API_REVIEW.md` and assigned build artifacts writable. No product fixes,
registry edits, evidence rewriting, hardware or publication by reviewer. All
prior deliveries are settled with recorded release/reuse decisions; no duplicate
writer. Integration remains held for this verdict.

## Reusable phase or wave entry

### EV-02 final settlement and integration checkpoint — 2026-10-20 UTC

Final independent DeepSeek Pro Task `task_2f3700b530a4` / Dispatch
`ctx_294f9d071a03` succeeded at 05:08:34Z. The coordinator inspected the exact
candidate `e5ebb376230d1dc6bbb62e07f38b7d4cf8221b32` and report-only tip
`e5eb9831780742598a605da5adfb17d905377955`; only the assigned new review report
was added after the candidate. Accepted methods: all 148 record hashes/schema/
per-client mappings, actual source/assertions and refusal effects, seven-feature
registry boundary audit, four-scenario/31-check exact-candidate replay,
122 scoped tests/two Docker deselections, independent canonical-ledger
recomputation and formal gate with zero failures. Three informational scope
limitations remain; no blocker or product defect was reported. Sol author and
DeepSeek reviewer are different underlying families. Actual pinned Pro session
`ses_ea85ac1aeffeevCjxBIKtUkXhL` export is complete and private.

The same reviewer independently audited the three approved Tron fixtures: only
three PNG LFS pointers change at `10f788f6`; their hashes equal the original
failed CI actuals, and prior pointers equal the original CI expected frames.
No assertion/threshold changes. Clarification of review prose: the coordinator
did run the approved snapshot update, then proved byte identity with original
captures; identical hashes do not establish that no regeneration command ran.
The structural acceptance and owner's visual decision remain distinct.
Baseline CI 39365581349 passed all 13 required checks at `3979d602`, with
identical-tree merge proof and 1,101 UI passes/33 skips. Portable receipts and
original-frame identity are now recorded; historical failed artifacts remain.

Published final-review task ref exactly equals `e5eb9831`; source task ref
exactly equals `e5ebb376`. Verified complete-history bundles and recovery bare
checkouts resolve each submitted SHA and pass `git fsck --full`. Private full
author workspace archive: 51,680 files/two fixture-junction links, 478,349,150
source bytes, SHA-256
`151051d1aee274830a68ed6c407bbeb413cc7f01d5191b92641242e1be5fb713`.
Private final-review workspace archive: 5,845 files/no links, 276,583,288 bytes,
SHA-256 `04b947547b8ad766efa0b0a54c91ceca64b84af94d211070f853eb0702d3b1c3`.
Every archive entry hash/link target was verified; junctions were not traversed.
Full provider transcripts, earlier audit artifacts and patches/status are
preserved outside cleanup targets under `build/ev02-name-coordination`.
[Portable integration receipt](../validation/runs/ev02-api-evidence/integration.json)
records preservation hashes and exact scope without publishing private exports.

Final reviewer release returned `released/closed_agent_terminal`, captured
terminal archive, before acknowledging delivery `delivery_86d617ad5888`.
Fleet reclaimable list is empty: 40 released/five retained historical Task rows;
the three newly retained rows share one older external review terminal, and
the other two are the prior null-resource compatibility rows. These are not
five active assignments. The older terminal remains protected by Orca's
external/user-takeover release guard; no manual close. No worker is active.

Coordinator rebound root branch/remote at `3979d602`, then sequentially
fast-forwarded accepted source/evidence candidate and final report tip. No
source or evidence integration edits were made; all 148 root Git-blob and
working-tree hashes match the reviewed manifest. Seven API V2 dispositions
are accepted; five current levels advance. Canonical ledger remains 268 total,
205 below target/57 stale. Original source/image attribution is preserved.
Wider EV-02/security, EV-03 and owner physical/72-hour/week/final-artifact gates
remain open; PR #38 remains draft. No new wave starts before verified push.

Post-integration Ruff passes and mypy reports no issues in 91 source files;
full-tree hygiene reports zero errors/warnings. Initial documentation-check
invocation produced 550 setup errors because its parent temporary directory did
not yet exist; all failed output is preserved. The JUnit writer created that
parent afterward, so a guarded setup-create attempt then declined an existing
directory. Retry uses a distinct empty temporary destination; no populated
evidence or private runtime data is overwritten. Actual retry result and
publication receipt follow separately. Coordinator record changes use the
invocation-only documentation/archive hook exception; no new full-hook pass
is claimed for record-only commits. Current integration CI must be observed
at its own published head, not inherited from `3979d602`.

Exact Orca worktree removal was requested only after verified full preservation,
published task refs and accepted integration ancestry. Receipts initially said
`removed/removing`; subsequent observation reveals incomplete cleanup: author
directory residuals and exact stale Git metadata, and final-review `EBUSY`
directory lock. Local task branches are held until removal and unused-workspace
proof are complete. No raw managed-worktree deletion, broad prune, branch force
deletion, unrelated process stop or protected-workspace change was used. The
unresolved persistence workspace and unrelated encoded hook artifact remain
untouched. Cleanup is **held**, not completed, despite initial request receipts.

Documentation/hygiene retry completed: **550 passed, two Docker cases
deselected**, 104.13 seconds, exit 0; output and JUnit remain in the isolated
integration build paths. Ruff and mypy passed as recorded above. No applicable
test failure remains locally. The complete post-wave CI pipeline will run at
the published integration-record head; its status is not yet a pass.

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


## Software wave build-out and distributed execution — 2026-10-20 UTC

Owner requested all nonhardware work in phases/waves and explicitly instructed
that development must continue by balancing available, task-relevant providers.
Capacity is an assignment-routing constraint, not a project-wide stop; ready
independent packages are pulled forward. No Claude/Anthropic, anonymous fallback,
unsupported quota claim or same-family implementation-review substitution.

Baseline root/origin `wp-runtime-completion` exactly
`97e617c2276c7b1e015bb4a9419cb9820deafdee`; prior CI 39374096223 passed all
13 required checks. Reobserved Orca **1.4.232**, runtime
`113f2af8-5169-408a-9b81-00bd6316d35c`; current coordinator terminal show positively
confirms `term_259c5526-02c2-44a8-b469-bf171aa435a0` in this runtime. Existing
Run `run_37205f6095b3` reused, no reset/new Run. Local Zelu Windows host available;
saved SSH hosts disconnected. Repo hooks remain blank, setup may be skipped.
Historical fleet 40 released/five retained Task rows; three retained rows share
one older external/user-owned review process whose restored status is
`unverifiable/missing_status`. Reserve one concurrency slot for it; do not infer
exit, duplicate or close it. Effective budget: coordinator + reserved old
process + at most two new workers, below project ceiling four.

Live supported Codex model/list and account/rateLimits/read at **16:35:44Z**:
ordinary use allowed, **97% weekly remaining** (10,080-minute window), reset
2026-10-27T06:33:16+00:00; shared current managed launch pool, no extra credits/secondary
window reported. Sol 6.1 high selected for bounded API implementation; Astra
reserved for actual concurrency composition work, Luna for bounded inventories,
older Sol only explicit qualified fallback, not cross-family review. Authenticated
DeepSeek balance/models at **16:35:44Z**: **USD 18.78 available**, Pro/Flash owned
by DeepSeek; pool shared with other projects, reset/rate limits and external
commitments unreported. Reserve USD 5 for bounded audit/review/corrections;
monitor balance rather than attributing all account consumption to this project.
OpenCode 2.0.32; previous Pro family/tool competence demonstrated on API/evidence
review. Pro configured-route pinning must be verified anew before its launch.
Gemini/Argon/Flash and MiniMax M3/M3.1 remain conditional until current access,
route and capacity observations; their old quota observations do not hold the
ready Codex/DeepSeek assignments. No fixed diversity roster. Receipts private
under `build/software-wave-planning-20261020`.

Plan data allocates 268 features once: 147 software targets (84 below/63 numeric
at-target), 120 physical-preparation rows and one field-preparation row; 59
parser-open findings have owners. These are dated inventories, not new defects
or target acceptance. Thirty packages/63 bounded units planned; exact runtime
Task/Dispatch/base/lease/status recorded only on genuine dispatch. Existing API
request/assertion support is sufficient for the first root/API-info unit, so its
scoped intake/harness check is no-change; global inventory completion is not a
blanket implementation barrier.

First author assignment is preparing: **SW-API-READ-01 / F-API-002**, Sol 6.1
high, exact base `97e617c2...`; exclusive new
`tests/validation/scenarios/sw_api_read_01.py`, optional
`tests/validation/test_sw_api_read_01.py`, new
`docs/production/software-waves/SW-API-READ-01/AUTHOR.md` and its build subtree.
Prohibited: product/shared runner/client/schema, registry/ledger, root manifests/
locks, old evidence/baselines and private root data. Preserve adequate existing
api_info proof; add actual GET / and GET /api contract assertions using source
inspection and simulator-backed runtime. Observe response contract, unchanged
device/no-command and independent checks; run actual scenarios and normal hook.
Qualified different-family DeepSeek review reserved before integration.
Coordinator continues plan/registry/integration ownership; no fictitious Task
or unobserved launch is claimed by this entry.

### Initial distributed dispatch receipts

**SW-API-READ-01 launched:** Task `task_3853c93e69ef`, Dispatch
`ctx_41f75bc23079`, terminal `term_f176e63d-c1df-4f09-9916-11aa9b530699`,
worktree `wp-sw-api-root`, actual branch `ryan-haver/wp-sw-api-root`, full base
`97e617c2276c7b1e015bb4a9419cb9820deafdee`. Requested/effective
`codex:gpt-6.1-sol` high match; prompt turn start observed; later transcript
positively shows actual source inspection/working. Author confirms own managed
pool matches the current supported 97% observation. Owner's capacity-balanced
policy supplied in the self-contained spec; no global inventory wait.

The author promptly identified symmetric registry links required by the normal
hook and continued scoped implementation/checks. Coordinator applied/staged
exactly F-API-002.scenarios adding `contracts.api_root` and
`contracts.api_root_alias`, explicitly allowing only this coordinator-authored
metadata delta in the same normal implementation commit (messages
`msg_b22c51987e53`, reply `msg_00c30e575432`). General registry ownership was not
transferred. An initial semantic comparison used Windows text decoding and
reported spurious Unicode claim differences; explicit UTF-8 Git-byte decoding
then confirmed only the scenario-list field changed, matching the one-line
staged diff. No level/evidence/finding changed. Actual author report: Ruff and
81 relevant tests pass, three diagnostic API outcomes; the diagnostic source
looked clean because new scenarios were untracked and is **not accepted proof**.
Normal full implementation hook and later clean committed-head campaign are
running/pending; no review/integration/qualification claimed yet.

**SW-FINDINGS-01 launched concurrently:** Task `task_e1bec78af179`, Dispatch
`ctx_07bca220949e`, terminal `term_9a074b85-0f88-4b87-995e-bd9e432feb6b`,
worktree `wp-sw-findings`, actual branch `ryan-haver/wp-sw-findings`, same full
base. Scope is read-only source/evidence reconciliation of all 59 parser-open
findings, exclusive new report/artifact paths. No product/test/registry changes.
Independent audit competence from prior API/evidence work; no legal/aesthetic
or hardware conclusions inferred. Native OpenCode 2.0.32 current model list
contains only DeepSeek Pro/Flash under local pins; seven built-in agents listed.
The supported config-source read and local pin were inspected without publishing
credentials; its raw private output may contain inherited MCP environment data
and must stay private. Global MiniMax/default settings were unchanged; local
policies deny non-DeepSeek providers, MCP/subagents and unqualified plugins.
CLI configured-route model/effort fields are null, turn-start observation is
unsupported, not claimed observed from receipt alone. Actual TUI then shows
working Pro; supported native export of session
`ses_ea5d0cd26ffeoHj0iNOGlj7zKj` independently confirms
`{id: deepseek-v4-pro, providerID: deepseek, variant: default}` and real tool
activity. Checkpoint export cost USD 0.194, not total account consumption.
Full completion export still required before settlement.

Two new active workers plus coordinator and one conservative retained-process
reservation use the four-agent project ceiling. No extra author/reviewer is
launched until a slot is settled/released; this is resource packing, not a
provider-capacity pause. DeepSeek audit can settle before it or another qualified
different-family route reviews the Sol implementation. Original Run, protected
persistence workspace, older external review resources, rejected empty-folder
cleanup and unrelated encoded hook artifact remain preserved. No cleanup retry
or unrelated process stop was attempted. The complete planned allocation lives
in [the software wave plan](../planning/SOFTWARE_RELEASE_WAVES.md); only the two
real initial units are marked launched, all others planned.

### Finding audit settlement, calibration and continued work

Original DeepSeek audit completed at `8f23ae8976a4056f7dd7793ad3733c730594f42d`
with all 59 rows covered. Coordinator review rejects its unqualified wording
that static code/file presence reproduced 27 current defects: no tests ran in
that audit. Required correction distinguishes source-inspection candidates from
observed reproductions and removes any invented visual/DI-9 approval gates.
Original report remains preserved; no finding/level/cap is closed from it.

Attempted exact-terminal fresh-authority reuse was refused preflight with
`agent_unconfigured`, request `26459b4f-8791-45d3-ba58-bc6dff8b8732`. Request-show
reported absent; fleet/worker/terminal inspection confirmed the original Task
settled and owned terminal live, with no replacement Task/Dispatch created.
No ambiguous duplicate writer or terminal-close workaround. Full native session
export and complete verified bundle were preserved, then accepted original
Dispatch `ctx_07bca220949e` released (`closed_agent_terminal`, archive captured)
before acknowledgment `delivery_3fb99400b0b6`.

Supported DeepSeek balance/catalog refresh **16:50:18Z**: USD **17.95** available,
Pro/Flash unchanged, reset/rate limits/external pool commitments unreported.
Fresh same-worktree Pro configured-route correction Task `task_185e93ca5a0c`,
Dispatch `ctx_6cee9d4ae624`, terminal
`term_dc89e1f3-bafd-4db2-b49b-7fcaefb79657`, full base `8f23ae89...`, was launched
after the old process release. Only its author report and new correction build
subtree writable; actual source/tests/register remain unchanged. Native status
positively reports working; no source or evidence acceptance claimed. Sol's
implementation hook continues independently (last observed 69%). Capacity
remains coordinator + one reserved old external process + two new workers.

Planning publication `53e4b6710e9835ced03b7c614e2ee00f70649f2f` exactly matched
origin. 473 existing documentation tests, complete allocation/DAG/exclusive-path/
source-input/Markdown checks, whitespace and full-tree hygiene passed. Only
planning/protocol/static data were committed with the documented invocation-only
documentation hook exception; no new implementation hook pass was asserted.
A subsequent portability correction changes snapshot hashes to exact baseline
Git-blob bytes and forward-slash paths, separating Windows checkout CRLF from
portable identities; it is queued with this wave's integration records.

### Native usage observation and balanced third-provider assignment

Orca native footer in **Used** mode was visually read about **16:56Z** on
2026-10-20: Codex 4% used / **96% remaining**, approximate reset 6d13h;
Gemini 81% used / **19% remaining**, reset 3d5h; MiniMax 72% used /
**28% remaining**, reset 2d14h. Exact credits, per-window throughput and other
project commitments are not exposed. The private screenshot remains private;
sanitized receipt is `build/software-wave-planning-20261020/native-provider-usage-sanitized.json`.
The eligible below-30 MiniMax bounded allocation has a verified Codex fallback
with its own checked headroom. No silent model substitution is authorized.

DeepSeek report correction completed at
`b008297b1a3c988789e92c2cb4c32f3396bcd07f`; zero runtime defects reproduced,
all 59 rows retained for triage, no register/feature qualification changed.
Both complete native sessions and verified full Git bundles preserved. Correction
Dispatch `ctx_6cee9d4ae624` released through Orca with terminal archive captured
before acknowledging `delivery_c6a841e2cbf0`. Coordinator still requires exact
row-level validation before any closure: report summary has residual shorthand
inconsistencies (BE-22 classified R in table but partial in prose; external-gate
counts in section 7), so neither counts nor broad historical test totals are
accepted as final closure evidence. This is useful scoped intake, not qualification.

**SW-REPO-01 launched on MiniMax M3:** Task `task_39d9d5951f53`, Dispatch
`ctx_789b450d0a6e`, terminal `term_e9cd5c16-37dc-4151-ab76-ad622239a0c8`,
worktree `wp-sw-repo-audit`, branch `ryan-haver/wp-sw-repo-audit`, exact full
base `53e4b6710e9835ced03b7c614e2ee00f70649f2f`. Source inventory of SEC-14,
SEC-15 and DEP-05 only, exclusive new report/build subtree, target under 15
minutes, no source/tests/tooling or feature/register closure. Completed upstream
triage copied privately; independent package verification is still required.
Local supported catalog exposes precisely MiniMax-M3 and MiniMax-M3.1-Flash;
primary/small/build/title/summary/compaction pinned **MiniMax-M3**, other providers,
MCP/subagents denied and unqualified plugins disabled. Default variant explicit.

An explicit launch-time `--model` was refused `capability_unsupported` before
agent creation, request `cb434abf-d8de-4b23-a14e-f608e6b9802f`. Installed recovery
read; request-show absent plus fleet and exact terminal listing positively showed
no new Task/agent, only plain PowerShell. Supported configured-route start then
succeeded: receipt model/effort null and turn-start unsupported are not positive
native-model proof; full native session identity must still be checked. No global
preference or silent M3.1 change. Coordinator + old external-process reservation
+ Sol author + M3 inventory remain at the four-agent ceiling.

Fleet now labels Sol's existing active terminal `user_owned/user_takeover` while
its genuine Dispatch remains working/live. Preserve that ownership; do not force
close/reclaim it after completion or infer capacity from historical retained rows.

Native session `ses_ea5b9e54affecYCZNEwGlFiyLZ` export positively confirms
MiniMax provider `minimax-coding-plan`, model `MiniMax-M3`, actual variant
**thinking** (the configured model's resolved default). This is explicitly
recorded rather than silently relabelled as the literal variant `default`;
coordinator follow-up `msg_96656284ef84` supplied the actual identity.

Sol's normal implementation hook completed: **4,041 passed, 4 skipped,
35 deselected, 177/177 REST routes (100%)**, Ruff passed, 1,321.26 seconds.
Source commit `afe344a0` includes only its new scenario/report and the explicitly
coordinator-authored one-line scenario mapping. The separate committed-head
campaign and complete author delivery remain pending. No feature level is yet
advanced and no independent review/integration is claimed.

Corrected finding report branch was normally published and exact remote/local
`b008297b1a3c988789e92c2cb4c32f3396bcd07f` equality verified. Coordinator
accepts it **as triage only with explicit residual limits**, recorded in
`docs/production/software-waves/SW-FINDINGS-01/COORDINATOR_RECONCILIATION.md`.
Sequential prose-only merge adds both preserved report commits; no register
closure or qualification. 473 existing documentation tests, whitespace and
changed Markdown targets checked. Invocation-only documentation hook exception
used for these prose/static-plan records, not for Sol's implementation.


### First implementation delivery and ongoing independent review preparation

SW-API-READ-01 completed at `0dd2c25ea866fd56fbe6046e03f0172499b70080`,
implementation `afe344a0e6a17392ccda90bab140284dd512267e`. Exact base diff:
new 76-line scenario, new 209-line report, coordinator's one-line F-API-002
scenario mapping; no product change. Normal hook passed 4,041/4/35 and 177/177
routes; 81 relevant tests; clean final API/source simulator campaign has three
passes and 20 checks, empty state differences, null image digests. Initial
untracked diagnostic remains excluded. Supported same-pool author observation
about 17:09Z: **95% remaining**; no model-capacity stop.

Complete native Codex transcript (1,741,792 bytes, hash recorded privately) and
original source records preserved. Orca settlement action `worker-release`
returned **retained/user_takeover**, processAction none; no terminal close or
worktree reuse. This explicit ownership decision precedes acknowledgment
`delivery_de635c0d28b8`. Coordinator uses a separate `wp-sw-api-acceptance`
worktree at exact submitted SHA for evidence/registry/ledger assembly; author's
user-owned worktree stays untouched. Three records copied byte-exact; only
F-API-002 current/basis/evidence proposed, no target/interfaces/finding change.
Ledger generation is running alone; registry tests wait until it completes.
No qualification or integration yet; exact combined candidate needs DeepSeek review.

MiniMax source inventory completed at `73a9621c0874e12c17f8ff525f44ce4c85f41a27`
in about four minutes. Full native transcript and verified full bundle preserved,
Dispatch `ctx_789b450d0a6e` released/archived before `delivery_d8edba9685ae`
acknowledgment. Coordinator review requires prose corrections before acceptance:
prior CI receipts exist with their original source scope; redacted gitleaks
matches are candidates, not proven harmless or permission for a broad 64-hex
allowlist; unreachable tree paths do not prove dangling-blob content/provenance.
Extra read-only unreachable inspection is not deletion authority.
Fresh same-worktree correction Task `task_f3691c08b309`, Dispatch
`ctx_7bbd908b29c9`, terminal `term_097d554a-6d03-448b-bf78-8b1a1e53a50c`, exact
base `73a9621c0874e12c17f8ff525f44ce4c85f41a27`, same pinned M3/thinking route.
Only report/correction build output writable, no repeat scans or config changes;
within original bounded 15-minute allocation with verified 95% Codex fallback.

Supported DeepSeek authenticated balance/catalog refresh **17:13:03Z**: USD
**16.56** available, current Pro/Flash unchanged, windows/reset/other commitments
unreported. Reserve USD 3 for exact API combined independent review/corrections.
This qualified different-family route remains available while M3 corrects prose.


Prepared combined API candidate **3622dc9a82893981feddc2e84ae7784eca3cdede**
was normally published on `ryan-haver/wp-sw-api-acceptance`; author
`ryan-haver/wp-sw-api-root` published at `0dd2c25e...`; both exact tips verified.
Canonical ledger generation completed before registry/schema checks (33 pass).
A coordinator basetemp-parent setup error caused 33 setup errors before test
bodies, corrected by creating a short new isolated parent; original failure
retained and no source fix implied. Numerical proposed count 204 below/57 stale.

**Independent combined review launched:** Task `task_b62e4cdfe32e`, Dispatch
`ctx_0334309854fd`, terminal `term_de20da3a-5639-4b3b-b82f-45b7b09e309a`,
worktree/branch `wp-sw-api-review` / `ryan-haver/wp-sw-api-review`, exact base
`3622dc9a82893981feddc2e84ae7784eca3cdede`. DeepSeek Pro/default configured
route with local provider/internal model pins; supported native export session
`ses_ea5ae7f03ffeBeIq9I4AsiPF21` positively confirms actual model/variant.
Different family from OpenAI author/coordinator; prior DeepSeek accepted
API/evidence review demonstrates relevant competence. New REVIEW.md and private
`build/swapi-review/**` only writable; no code/metadata fixes by reviewer.
Required independent 81+33 checks, three clean simulator outcomes, immutable
hash/mapping/scope audit and actual formal gate result. No ledger regeneration
concurrent with registry tests. Review is genuinely launched, not yet accepted.

Current M3 correction native session `ses_ea5b1d88fffel0fH1b79YDx36y` also
positively confirms M3/thinking. Both active tasks fit coordinator + old process
reservation + two new workers; completed Sol user-owned terminal remains idle
and preserved. Full author native transcript and verified complete bundle retained;
full workspace archive is in progress without deleting or rewriting anything.


M3 report correction completed at **b4736c2b6aedd6b033984e624783bd79ed2bb7c8**,
prose-only, original commit preserved. Full native correction export confirms
M3/thinking; Dispatch `ctx_7bbd908b29c9` released/terminal archived before ack
`delivery_4e664d6ad00d`. Corrected task ref published and exact remote SHA
verified. OpenAI coordinator independent prose review accepts calibrated source
inventory with explicit limits in `SW-REPO-01/COORDINATOR_REVIEW.md`. No broad
secret-scan suppression, source correction, finding closure or release proof
inferred. Sequential prose merge; actual Markdown targets and whitespace pass;
invocation-only documentation hook exception, no full-suite claim.

Finding workspace complete private archive verified all 4,288 file entries,
272,566,411 bytes, SHA-256 recorded. Full bundles/transcripts/status/patch,
published ref and integrated ancestry verified before exact Orca worktree rm.
Receipt reports removal accepted/in progress; filesystem/Git/Orca final-state
verification remains required, so cleanup completion is not yet asserted.
Protected old user/external workspaces, denied empty-folder removal and odd
untracked hook artifact remain untouched.


### Accepted first API unit: review, sequential integration and publication gate

DeepSeek exact candidate review **accepted API/source-simulator V2 only, no
findings**, report tip `6385499f7f1c7dc754599a37508d14171c4ef5c7`. Independently
81 focused + 33 registry/schema tests passed, three clean 3622dc9a scenario
outcomes / 20 checks. **Actual formal gate PASS**, zero known failures/drops,
exit 0, 191.9 seconds; the older two-drop hypothesis was not current evidence.
An initial native 120-second check timeout is preserved in the complete provider
transcript; later actual process/exit/result was checked, no timeout treated as
an exit or a gate failure. No extra ledger generation. Both original/imported
source SHA and all 3 hashes/covers/client mappings audited, null image digests.

Complete native reviewer export positively confirms Pro/default. Exact settled
Dispatch `ctx_0334309854fd` released/terminal archived before acknowledging
`delivery_2a64617a7773`. Review task branch published and exact 6385499f remote
SHA verified. Full bundles and workspace archives preserve original failures,
tracked/untracked/ignored files, transcripts and private receipts before removal.

Normal sequential Git merge **0812dfbc00418a18220a2492c83ddc052e450166**
integrates the accepted source/candidate/review with no conflicts or material
source change. The reviewed source, full registry, ledger, attributes and three
original evidence blobs are byte-identical in integration. Normal source hook
passed on author implementation; no hook override was supplied to the Git merge.
Local combined verification: **515 documentation/registry/schema/ledger tests
pass**, repository Ruff pass, mypy pass (91 source files). New API change-range
redacted gitleaks scan: 3 commits, ~201KB, exit0/no leaks; separate from the M3
full-history exit1 candidate-match inventory. No new suppression/config change.
Canonical numerical ledger now **204 below / 57 stale**; software-below snapshot
83. Other features are not freshly qualified by these numbers.

The final publication-head full applicable CI pipeline is required and remains
pending at this pre-publication checkpoint. Do not reuse old 97e617c2 CI as new
head proof. Task refs stay published; exact root/origin equality and current-head
CI receipts will be captured privately without a self-hash commit loop.

GitHub read-only check of PR38 target wp-g1-g2-release-and-docs protection
returned explicit HTTP404 `Branch not protected`; repository rulesets returned
empty. The project's 13-check acceptance requirement is still enforced by this
workflow; it is not falsely described as an observed GitHub branch-protection
setting. PR38 remains draft and targets the same branch; no settings changed.

Quota-window clarification after re-inspecting the original native footer:
MiniMax shows Used72%/remaining28% and reset2d14h, but does not explicitly label
its period weekly. Any initial private task-spec weekly qualifier is corrected:
MiniMax period is unreported, remaining/reset observation unchanged. Gemini
explicitly says wk; Codex weekly is independently confirmed by its account API.
Bounded M3 allocation kept the verified Codex fallback; no credits invented.

Orca exact finding and M3 worktree removals have now removed Git registrations
and proven completed local task branches; published remote refs remain. Empty
filesystem residual directories are still present, preserved without raw-delete
retry. Their full verified archives/status/patch/history/transcripts are retained.
The old protected/denied cleanup targets and author user-owned worktree remain
untouched. No extra active worker assignment remains from this initial wave.


## Software wave 02 preflight and prior-head qualification — 2026-10-20

Owner explicitly authorized proceeding. Revalidated integration/root/origin
`2b10e000587d4279b0cad5583ff1038732c70415`, same PR38 draft/target and Run
`run_37205f6095b3`, Orca **1.4.232**, runtime
`113f2af8-5169-408a-9b81-00bd6316d35c`. Coordinator terminal handle remains
`term_259c5526-02c2-44a8-b469-bf171aa435a0`; actual process incarnation differs
and is retained in the fresh receipt. Local Windows Zelu only; all saved SSH
hosts disconnected. Initial `orca agent list` unsupported, so no capability
claim came from it; current launch help/catalog and native host receipts used.
OpenCode is now **2.1.1**, not the historical 2.0.32; current catalog and local
pins must be checked again before execution. Do not replay old model overrides.

Fleet fresh snapshot: **45 released / 6 retained, no active assignments**.
Retained rows include null compatibility entries, older external/user resources
and the completed user-owned Sol author; they are not six new active workers.
Conservative project ceiling remains four including coordinator. Reserve one
slot for the older external process whose state is still not proven exited;
maximum two new workers. Preserve all prior protected persistence/empty-folder/
user-owned workspaces, root private runtime, unrelated encoded hook artifact and
historical failures. No deletion or orchestration reset is authorized here.

### Exact CI closure for the first API unit

[CI39467476091](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/39467476091)
completed successfully at published head `2b10e000...`: all 13 required jobs and
UI review comment success; GHCR publish skipped on PR. Actual source
`564346beb0d955970333b22dba6c5f719d079a4a`, tree
`27325b4554875c096e68c1e852615a33601e91ff`, equals that head's tree. Core
4,023 passed/22 skipped/35 deselected, 177/177 routes; source API/browser/UC
1,416/54/18, actual HA19; Remote100, HA component101, deployment29/2 skips,
UI1,101/33 skips. All **1,507 source records** schema/source/per-client mappings
validated with zero errors, original merge SHA and null image digests retained.
They are not imported as later-candidate or image/client qualification.
F-API-002/API source-simulator V2 now has independent review, integrated proof
and combined CI acceptance; other targets/physical/field/final release remain.

Full raw job logs and all seven original artifact payloads are preserved under
`build/software-wave-02-20261020/ci-39467476091/`; hashes and attributed results
in `docs/validation/runs/software-waves/SW-API-READ-01/ci-39467476091.json`.
Initial all-artifact gh download exited1 after two outputs; those partial files
and the failure record remain. Direct original downloads all passed. Two
Docker-build payloads are opaque non-ZIP bytes, retained without pretending they
are ZIPs; the other five artifacts were safely extracted into a fresh destination.
No populated historical capture helper was rerun or original bytes overwritten.

### Current model/host/pool observations and allocation

Supported Codex app-server observation **20:59:33Z**: ordinary usage allowed,
**25% used / 75% remaining**, 10,080-minute weekly window, reset
2026-10-27T06:33:16Z, no secondary pool or reset credits. Exact current catalogs
contain Sol6.1, Astra, older Sol5.6/6 and Luna with their selectable efforts.
Sol6.1 high remains the implementation choice for bounded security behavior;
Astra is available for demonstrated concurrency/composition difficulty, not
added speculatively. Older Sol/Luna remain same-family alternatives; Luna fits
inventory but MiniMax is selected for the bounded preservation task below.

Supported authenticated DeepSeek balance/catalog observation **20:59:33Z**:
USD **3.79 available**, Pro/Flash IDs unchanged; rate limits/reset/external
commitments unreported. This shared pool has materially declined since the
previous wave. Reserve **USD1.50** for a bounded exact-commit security review
and corrections, based on prior comparable Pro API review execution; refresh
before review launch and monitor limits. Do not spend this reserve on generic
inventory. Pro remains qualified for API/security invariants; Flash remains a
conditional bounded-audit route, not automatically a qualified implementation
reviewer. No claim of unlimited headroom or new credits.

Native Orca Used-mode observation about **21:02Z**: Codex25% agrees with the
supported API; MiniMax75% used / **25% remaining**, reset about2d10h, period not
reported. This below30 bounded M3 preservation/report assignment has verified
**Sol6.1 high / 75%** fallback with its own account check; no silent substitution,
no extra author duplicated on an ambiguous process. The Gemini footer displays
87% in Used mode while its compact label says Remaining; this semantic
inconsistency and backend alias routing remain unresolved, so no verified Gemini
headroom/family launch is asserted. Argon/Flash remain task-conditional candidates;
their uncertainty does not hold the eligible Sol/M3 assignments. M3 and M3.1-Flash
both appear in current catalogs; **M3/thinking** is selected for the source
inventory role with prior accepted comparable work. M3.1 is not silently used.
All primary/internal/helper models and plugins need local route containment.
Claude/Anthropic excluded everywhere, including any nested default or fallback.

### Bounded wave packing (planned, not launched by this entry)

Two original six-feature units split before dispatch: allocation now **30
packages / 65 units**, retaining all268 unique primary feature owners. Original
63-unit publication remains historical. SW-SEC-AUTH-01 now owns **F-SEC-007**
only (wrong PIN/lockout, actual UI and independent no-effect/responsiveness
assertions through existing browser intents). Other five auth features move to
SW-SEC-AUTH-03. Sol owns only its new scenario/optional test/report/build paths;
no shared client/runner/schema/product write by default. If existing observations
are insufficient, request a minimal exact lease or report the gap without fake V3.

SW-API-READ-02 now owns accepted **F-API-014/016/026/028** preservation only;
CORS/WebSocket F-API-031/032 move to SW-API-READ-04 for explicit capability
intake. M3 report/readonly source/evidence verification has exclusive new report/
build paths, no speculative tests or qualification promotion. Coordinator owns
registry/evidence import/ledger and integration. Each unit gets a full newly
published base, genuine Orca Task/Dispatch and real acceptance; scoped existing
client inspection provides a no-change harness gate, not a global inventory wait.
New implementation still needs qualified different-family review. Model capacity
routes useful work; it does not pause the project.


### Genuine wave 02 starts after exact prior publication

Scoped CI/preflight records published at **51275723846e4b126ccdc48c71d1727cabca4dbc**;
exact origin equality verified before worktree/author dispatch. 473 existing
instruction/documentation tests, 65-unit/268-unique-owner/exclusive-path/link
checks and whitespace passed. Commit is prose/static allocation/evidence receipt
only; documented invocation-only documentation hook exception, no runtime claim.
No worker was launched for that coordinator-only record commit itself.

**SW-SEC-AUTH-01/F-SEC-007 Sol author:** Task `task_eb4ab88caa5b`, Dispatch
`ctx_5c634ce3cf0f`, terminal `term_704585c8-7ce8-4e60-a147-d13c285f1d25`,
worktree `wp-sw-auth-lockout`, actual branch `ryan-haver/wp-sw-auth-lockout`,
exact base51275723. Requested/effective **gpt-6.1-sol/high** match, prompt turn
start observed. Exclusive new sw_sec_auth_01 scenario/optional test, author report
and own build subtree; existing shared/browser/client/product paths read-only.
Actual browser wrong-PIN/refusal/control/lockout proof and existing during-held-
PBKDF2 responsiveness tests are required; API-only response checks do not earn V3.
Coordinator alone stages mapping after exact scenario IDs; source normal hook,
clean committed campaigns and qualified DeepSeek different-family review required.
No level/evidence import or finding closure yet.

**SW-API-READ-02 M3 preservation author:** Task `task_a75ae30df852`, Dispatch
`ctx_de4764241ae7`, terminal `term_db88836b-5d55-4a57-9397-b4d65bcb4d39`,
worktree `wp-sw-api-preservation`, actual branch `ryan-haver/wp-sw-api-preservation`,
same exact full base51275723. Existing-worktree configured route explicitly pins
M3 primary/small/internal models, denies other providers/MCP/subagents and
unqualified plugins; supported current local model list is only M3/M3.1-Flash,
with M3.1 unauthorized. OpenCode2.1.1 `debug agents` returns empty, not the old
seven-agent listing; no inherited agent-inventory claim. Initial model-list read
ran in root and showed the global catalog; corrected exact-worktree read proved
local containment before launch. Catalog exclusion listings are not model use.
Launch receipt configured-route model/effort null and turn-start unsupported;
native effective identity still needs independent export verification. Exact new
AUTHOR/report build subtree only writable, read-only original proof/covers audit
of F-API-014/016/026/028; no new tests/fixtures/tooling or broader qualification.

Two new workers + coordinator + older external-process reservation occupy the
conservative four-agent ceiling. No extra reviewer/helper dispatch until a worker
is settled/released. Original Run reused; no global config/default edits, new
orchestration reset or ambiguous writer duplication. All ownership/lifecycle
updates remain separate from completion/review/integration/qualification.


### Observed models and minimal serial capability lease

M3 native session `ses_ea4d904d6ffe07R7fPLq6zMJcw` export independently confirms
provider minimax-coding-plan, model MiniMax-M3, actual **thinking** variant.
No M3.1 substitution. Sol's own supported account check at21:10:48Z confirms
same pool,26%used/74%remaining with same window/reset/ordinaryusageallowed.
Both genuine Tasks show working heartbeats, not merely launch requests.

Sol intake found two concrete lockout-evidence gaps: runner setup aborts on
expected wrong-PIN403 attempts and ClientState exact toast equality cannot
express varying retry seconds. Coordinator reply to `msg_eaab70d5172d` grants
an exclusive serial lease **only** `tools/validate/clients/browser.py` and
`tools/validate/clients/browser_driver.mjs` to Task `task_eb4ab88caa5b`, alongside
its owned new scenario/test/report. Author should use a bounded actual-UI burst
flow and stable visible-lockout/refusal/Retry-After observation, preserve old
intent/observer defaults and include meaningful negative/allowed controls.
Runner/model/schema/registry/product remain prohibited; no broad framework or
expected-status setup bypass. New lease must be covered in exact-candidate
cross-family implementation review. M3 inventory remains read-only and disjoint.

Because API-root scenarios declare broad tools/validate covers, any browser-
bridge change makes that original source proof stale under the actual policy.
Coordinator will rerun those three existing API cases against the actual clean
candidate and preserve new SHA/bytes before combined review, without replacing
old records or relabelling their original source. Wider applicable client CI
is required after accepted integration. Scope is implementation of a measured
capability gap, not an owner gate or a project-wide capacity hold.


### Wave 02 preservation accepted; security source hook active

SW-API-READ-02 original Task task_a75ae30df852 completed80735439. Coordinator
independently checked all141 original records/1,079 checks and actual source/
client/assertion mappings. Original prose incorrectly called six linked findings
open; original native transcript and full verified bundle were preserved, original
Dispatch ctx_de4764241ae7 released before acknowledgment. Fresh bounded correction
Task task_c7b627a988f6 / ctx_7fa9d2abc3ff, same worktree at full80735439 base,
committed56466c16e838a936c0278b84f824b2601553a110 without amend. Exact writable
AUTHOR.md/private own build only, same verified MiniMax-M3 thinking route and
same allocation/fallback. Correction confirms five already closed plus TST-03
open; observations informational, no cleanup/fixture/cover-change request.
Coordinator OpenAI-family factual review accepts corrected prose and preservation
of141 original1baac3de API V2 records; no new runtime, image, V3 or level claim.
Full corrected native export84messages verifies M3/thinking, full bundle verified;
ctx_7fa9d2abc3ff released21:24Z before delivery acknowledgment. Worktree retained
pending full workspace backup and accepted integration; no deletion yet.

Sol task_eb4ab88caa5b remains the only new active author, with older external
process reservation preserved. Exact authorized FSEC007 mapping staged by
coordinator (eight new IDs, two existing preserved); normal implementation hook
now executing strict route coverage and SW_SEC_AUTH_BROWSER_TESTS=1 in isolated
hook-01. Focused actual Chromium2/2 passed after retained assertion-calibration
failures; these are test-oracle corrections, not a reproduced product defect.
Ruff full CI paths and mypy91 pass reported; source commit/clean campaign and
qualified DeepSeek different-family review remain pending. Browser1.63.0 /
Chromium153.0.8010.12 observed. Ordinary core skip for opt-in Chromium test is
explicit; actual formal browser scenarios have no fake dependency pass.

Covers inspection confirms four preservation features do not cover changed
browser adapter paths; original API proof remains scoped to1baac3de. F-API-002
covers tools/validate and requires three fresh cases at actual clean auth candidate.
No next wave begins before current integration records/push/equality are complete.
