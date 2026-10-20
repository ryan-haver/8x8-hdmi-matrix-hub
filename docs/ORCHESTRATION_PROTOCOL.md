# Standing Orca coordination and staffing protocol

## Authority and scope

This is the operating protocol for autonomous coordination of **authorized**
work on `ryan-haver/8x8-hdmi-matrix-hub`. It is discoverable from
[AGENTS.md](../AGENTS.md). Maintain the
[allocation ledger](production/AGENT_ALLOCATION.md) before and throughout work.
Installing this protocol does not start a phase or authorize worker launches,
hardware actions, visual approval, deployment, merge to main or release tags.
The instruction-recording task of 2026-10-19 explicitly prohibits launches.

Owner instructions and exclusions take precedence over example rosters, model
catalogs and skill examples. **Claude/Anthropic is excluded from all new roles**:
authors, reviewers, helpers, category routing, retries and automatic fallbacks.
An opaque alias is ineligible until its provider/family and routing are known.
Do not rewrite historical Claude work or historical failures to match policy.

Technical and acceptance authorities remain:

- [Unified master plan](planning/UNIFIED_MASTER_PLAN.md) and
  [runtime-completion plan](planning/NEXT_DEVELOPMENT_PHASES.md).
- [Remediation plan](REMEDIATION_PLAN.md), particularly section 5.3 visual
  capture/owner approval, and [security policy](../SECURITY.md).
- [Validation policy](validation/README.md),
  [validation plan](validation/VALIDATION_PLAN.md),
  [feature registry](validation/features.yaml), and
  [runtime evidence index](validation/RUNTIME_VALIDATION_INDEX.md).
- [Contributing](../CONTRIBUTING.md), [.github/workflows/ci.yml](../.github/workflows/ci.yml)
  and [.githooks/pre-commit](../.githooks/pre-commit).

This protocol supersedes older launch recipes and cleanup ordering for future
coordination. It does not change technical contracts, feature evidence levels,
release gates or the identity/qualification of historical work. Record a real
policy conflict and hold the dependent action rather than assuming approval.

## Rebind the project before work

1. Read all applicable `AGENTS.md` files, current plans, allocation entries and
   handoff updates. Record the user-authorized scope and explicit exclusions.
2. Inspect `git status --short`, `git branch --show-current`, `git remote -v`,
   `git worktree list --porcelain`, branch upstreams and remote refs. Record the
   integration branch and full SHA, remote URL, PR base chain and protected refs.
   Do not checkout/reset another branch merely because an old prompt names it.
3. Resolve the Orca executable once using the installed `orca-cli` skill. Read
   its version-matched `skills get orca-cli` and `skills get orchestration`
   guides. Use that executable throughout; check command help before unsupported
   flags. A changed runtime requires re-observation of handles, not invented IDs.
4. Inspect `orca status --json`, `orca orchestration run-current --json`,
   `orca orchestration run-list --json`, scoped `run-show`, and
   `worker-list --run <actual-run> --include-remote --json` (follow pagination).
   Reuse the applicable existing Run; use `run-use` only as supported and needed
   for the actual coordinator. Never run orchestration reset, create a replacement
   Run to escape failures, or reuse copied Task/Dispatch authority.
5. Compare Orca workspaces with Git worktrees and filesystem presence, scoped
   to this repository ID. Preserve discrepancies as unresolved, even if old
   reports say all workers were removed. Global listings include other projects;
   those resources are outside this project's cleanup authority.
6. Record execution host, capabilities, connected/unknown status, setup hooks,
   default tabs, nested depth and existing workload. Inspect remote capability
   on the actual execution host; local help does not prove remote support.
   No remote fallback or provisioning is implied by a saved host name.
7. Record the applicable coordinator/worker concurrency budget. This recording
   session exposes four collaboration slots including the coordinator; that is
   **not** a measured Orca worker limit. Until a phase records a tighter verified
   host/provider budget, use a conservative project ceiling of four active
   agents total (coordinator plus at most three workers, reviewers included).
   Use the minimum of that ceiling, runtime/nesting limits, host capacity and
   verified provider capacity; do not assume six historical lanes may run at once.

Use explicit working directories for every command. The current dated branch,
Run, runtime, root and unresolved workspace are in the ledger; revalidate them
before execution. `wp-*` task labels and observed `ryan-haver/wp-*` Git branches
are distinct: record Orca's returned actual branch rather than constructing it.
The older `fix/phase-N-*` convention remains historical context.

## Model discovery and assessment

Before **each development phase or fan-out wave**, refresh supported catalogs
and execution-host capabilities. Use current host/harness help, supported model
listing or non-secret catalog APIs/caches; record command, host, version, UTC
time and cache age. Do not install/login/change global preferences or spend
credits on probes merely to expand the roster. Unknown capabilities remain
unknown. Audit setup agents, plugin categories, helpers and fallback chains.

Explicitly assess each allowed candidate below. These are initial role
hypotheses, not performance, speed, price or qualification guarantees. The
[model inventory](planning/MODEL_AND_AGENT_INVENTORY.md) retains project results
and historical IDs; it is not a live capacity report.

| Candidate | Initial task fit | Required task-specific evidence |
| --- | --- | --- |
| Codex Sol (`gpt-6.1-sol`) | Core systems, backend, protocols, shared APIs, integration | Correct behavioral tests, lifecycle/compatibility reasoning, exact tool execution |
| Codex Astra (`gpt-6-astra`) | Difficult concurrency, native/platform behavior, composition | Cancellation/ownership/failure analysis, real platform scope, substantive review findings |
| Codex `gpt-5.6-sol` | Candidate compatibility route for scoped systems work | Explicit current catalog/access/launch support and representative accepted work; no inherited Sol 6.1 qualification |
| Codex Luna, where available | Bounded inventories, documentation and evidence indexing | Scope discipline, source-linked factual checks; no automatic architecture/code-review qualification |
| Antigravity Argon | Complex UI, broad design analysis, security/protocol review | Actual task competence plus confirmed provider/family routing; alias alone is insufficient |
| Antigravity Flash | Bounded QA, codecs, tooling and link checks | Meaningful assertions, reproducible checks and declared limits |
| MiniMax M3 | Bounded algorithms, runbooks, fixtures, adapters | Verified model selection, sufficient quota, accepted comparable work |
| MiniMax M3.1 Flash variants | Bounded implementation, tests and mocks | Exact variant and effective launch proof; M3 is not M3.1 evidence |
| DeepSeek Pro variants | Architecture/concurrency review | Exact ID/access, tool execution, demonstrated review of invariants/failure paths |
| DeepSeek Flash variants | Bounded invariant, lock-graph and tooling audits | Accurate source-linked findings and tested audit scope |
| Claude/Anthropic | Excluded by owner policy | Mark policy-excluded; listing or account presence does not authorize use |

Discover exact selectable provider/model/variant IDs and supported effort on
the execution host. Example names are search candidates, not portable commands.
Distinguish and record separately:

1. **Catalog presence** (including its freshness).
2. **Account access/entitlement** for that route and pool.
3. **Supported launch selection** in this host/harness/placement.
4. **Observed execution**: requested versus effective provider/model/effort,
   observed start, tools, host and authoritative Task/Dispatch receipt.
5. **Task qualification**, separately for authoring and reviewing that domain.

The present Orca 1.4.230 help supports OpenCode model selection only in an
**existing worktree**, with verified host CLI/model availability; effort is
unsupported. Earlier project launches rejected overrides, and a nominal M3.1
assignment actually ran M3. Neither fact may be silently generalized to a new
host/version. If this route is needed in authorized work, first pass quota and
placement preflight, provision isolation without an automatic agent, then use
the verified supervised existing-worktree route. Never silently launch defaults
or change shared/global provider preferences to make selection appear supported.

Record alternatives and selection rationale against task risk, dependencies,
observed project performance and available headroom. A model-diversity quota,
brand name or assumed speed/cost is not a reason to dispatch. An unsupported
effort, fallback variant or routing difference is a recorded discrepancy, not
an implicit substitution. A receipt proves control-plane selection; self-report
alone does not attest an underlying backend. Unproven family identity cannot
satisfy the cross-family review gate.

## Quota and rate-limit preflight

Owner clarification (2026-10-20): **capacity constrains routing, not continued
development**. Balance ready tasks across available, task-qualified providers.
If a preferred route is low, unavailable or cannot report usage, immediately
evaluate supported alternative pools/routes and pull independent ready work
forward. Queue only the affected assignment or acceptance gate when no suitable
route is available; do not stop the project or wait for a fixed model roster.
Unknown quota remains an unknown observation, not proof of exhaustion or
verified headroom. Record each routing choice and keep the different-family
review and concurrency requirements. A blocked reviewer need not block authors
on independent work, but unreviewed implementation cannot be integrated or
qualified. No Anthropic/Claude or opaque fallback is permitted.

Before **creating phase worktrees or dispatching any author or reviewer**, use
supported provider usage reporting on the intended host/account pool. Record:

- UTC observation and source/reporting capability, provider, redacted account
  or pool reference, model scope and whether the pool is shared.
- Remaining percentage or credits, units/denominator, limiting windows, reset
  times with timezone, reported rate limits and any stale/unavailable fields.
- Existing commitments across this and other work, likely author/review/fix
  capacity and a bounded task-size estimate with its uncertainty.
- Dispatch decision and checked fallback: exact provider/model/effort, task
  suitability, its own observation/headroom and reason for switching.

Below **30% remaining**, near credit exhaustion, or insufficient capacity for
the task **requires a suitable verified fallback with independently checked
headroom**. Enough percentage alone does not prove enough capacity. Unknown,
unavailable or stale quota is explicitly **unknown**, never verified headroom;
hold affected creation/dispatch if no suitable verified fallback exists.
Reserve capacity for independent review and material corrections, not just the
initial author. Refresh if the pool changes, a window resets, a long interval
passes or another commitment makes the observation unreliable.

Discover the reporting interface from supported host/provider help or account
UI/API; do not invent an `orca quota`/`usage` command. Account listing,
authentication and model catalogs do not measure quota. Never dump credentials,
tokens or full private settings into receipts. Record sanitized observations;
keep any necessary raw account material private and outside Git/public artifacts.

Monitor explicit limit responses and usage observations at natural checkpoints.
A credit footer, quiet transcript or lost contact is not proof of worker exit.
Before replacing a stalled writer, preserve its Git/dirty state, reports and
lifecycle receipt, prove settlement or fence it through the supported recovery
procedure, and prove no surviving writer can edit the replacement's paths.
If liveness remains ambiguous, hold replacement dispatch. No excluded fallback.

## Ownership and supervised workers

Use genuine Orca-supervised autonomous sessions in dedicated worktrees for new
implementation and review packages. Do not impersonate workers under fictional
model names, use shell scripts as purported model work, or substitute native
non-Orca subagents for requested Orca provenance.

`orca orchestration worker-start` is the normal supervised route. Bare
`agent launch` or `worktree create --agent` does not establish Task/Dispatch
authority. Read the installed placement/coordinator-loop reference before any
new placement. It is valid to create an agent-free worktree first when required
by a verified adapter; the ensuing worker still needs `worker-start` authority.
Do not run example launches while merely recording this protocol.

Every assignment must pin:

- Authorized objective, parent/dependencies, actual integration/base full SHA
  and actual task branch/worktree/host. Verify the returned base matches it.
- Exact exclusive writable paths, prohibited paths and ownership expiry.
  Parallel tasks must not overlap writers; reviewers are read-only on product
  paths and may write only their assigned new report/artifact paths.
- Shared contracts, API shapes, root packaging/CI manifests, dependency
  lockfiles, validation registry/ledger, integration records and final merges
  remain coordinator-owned. A necessary change is proposed to that owner;
  transfer a specific path explicitly and serially if implementation is assigned.
- Behavioral invariants, compatibility boundaries, acceptance commands and
  environments, evidence destination, time/resource limits and failure cases.
- Requested model/effort, qualification and quota decision, alternatives and
  independent reviewer family/eligibility (or a recorded held review gate).
- Expected completion report: full commit, base diff/path audit, commands and
  exits, failures/skips/limitations, artifacts and unresolved questions.

Use only live injected authority for worker lifecycle messages. Record Task ID,
Dispatch ID, selected/effective launch receipt, host and observed start; a
terminal title or copied old preamble is insufficient. A launch request is not
an observed start or completion. Follow hooks/default-tab policy without starting
an excluded side-effect agent. Do not duplicate launch after an uncertain receipt.

## Independent review and qualification

Every **new implementation deliverable**, including fixtures, tests and tooling,
requires a qualified independent reviewer from a **different underlying model
family** before gate closure. A separate session is necessary but insufficient:
Sol, Astra, older Sol and Luna are all the OpenAI GPT family; Argon and Flash
are the Gemini family; M3 and M3.1 are MiniMax; DeepSeek Pro and Flash are one
DeepSeek family. Different harnesses/providers do not change an underlying
family. Reject opaque/unverified family identity as cross-family proof.

Qualify reviewer competence for the actual domain: source/assertion inspection,
invariants, realistic counterexamples, execution/tool competence and calibrated
findings. Accepted implementation work or a catalog description alone does not
qualify review. Preserve failed qualification attempts and negative findings;
if no suitable reviewer has verified access/headroom, hold gate closure.

Review the exact author commit, its assigned base diff, actual source,
assertions and observed behavior. A green summary is not a source review.
Record reviewed SHA, family evidence, scope, methods, findings/severity and
disposition. Reviewers **report; authors fix**. Review tests/tooling introduced
by reviewers as implementation too, with separate independent coverage.
Re-review material fixes and material integration/conflict-resolution changes
at their final commits. Coordinator acceptance cannot silently waive findings.

This rule is prospective. Earlier Sol/Astra independent reviews remain valid
historical evidence within their recorded scope, but are **same-family**, not
new cross-family qualification. Do not retroactively claim an open vector closed
or launch a retroactive review as part of instruction maintenance. Pure prose
maintenance uses applicable documentation checks and policy inspection; it does
not establish fresh runtime or model qualification.

## Worker lifecycle and recovery

Use Run-scoped `check`, `worker-list`, `worker-show` and `worker-read`. Follow
pagination and returned `projection.nextAction` arguments. `worker-show` PTY
liveness is not agent liveness. Treat `live`, `unverifiable` and `exited` as
distinct. Timeouts, empty waits, null status and unchanged tails are checkpoints.
After repeated empty waits, enumerate rather than blindly waiting or relaunching.
Keep progress reporting responsive; bound individual waits to 60 seconds here.

For every delivered batch, handle questions and escalations, verify each
`worker_done` against the expected active Dispatch, and accept its real success
or failure outcome. Decide immediate reuse, user-requested explicit retention
or release **before acknowledgment**. Release settled owned resources promptly;
read archived output afterward. Orca release archives terminal output, but does
not replace the complete artifact/Git preservation checks below. Acknowledge
only processed deliveries and handle any next delivery returned by the ack.

Load the installed `recovery-and-cleanup` reference for failed starts, stale
handles, retries, unknown outcomes or uncertain release. Inspect `failedStage`,
`residualResources`, request identity and the receipt's exact recovery action.
Retry a known failed/stopped Task using its `--retry-of` with explicit placement;
do not invent another Task/Run to defeat a circuit breaker. Preserve ambiguous
state rather than duplicate a writer. Never substitute terminal close for
uncertain `worker-release`. Re-list handles after restart; do not dual-send to
the old and replacement handle. Retained compatibility rows with no owned
resource are historical metadata, not permission to delete files.

## Verification and publication

Audit **every** worker result against its assigned full base SHA, including
added/deleted/renamed files, tests, untracked files and relevant ignored output.
Reject edits outside ownership; do not hide them by resetting the checkout.
Verify acceptance in the worker worktree at the exact submitted commit and
confirm independent review before integrating accepted packages sequentially
onto the rebound integration branch. Re-review material integration changes.

Run the complete **applicable combined** pipeline after a development wave.
Derive exact commands/dependencies from current CI and validation policy; this
reference list is not a claim that any command ran in instruction maintenance:

| Scope | Project verification |
| --- | --- |
| Python changes | CI Ruff paths (`src tests custom_components tools run.py run_server.py` as present), `python -m mypy src/`, core `python -m pytest tests/ --ignore=tests/ha --ignore=tests/uc --tb=short` |
| Core REST inventory | Complete core run with `ROUTE_COVERAGE_STRICT=1`; all registered routes must be covered, not a fixed historical route count |
| UC behavior | Dedicated `python -m pytest tests/uc` with recorded environment |
| HA | Dedicated `tests/ha` on its supported Python/dependencies plus actual HA client campaign where applicable; an auto-skip is not HA acceptance |
| REST changes | Update `docs/validation/features.yaml`, add coverage in `tests/sim/test_sim_rest_reads.py`, run `python -m tools.validate ledger`, then registry checks serially |
| Browser/UI | Pinned Playwright container, smoke/flow and applicable visual projects; no baseline approval by an agent |
| Clients/evidence | Supported `tools.validate run` clients and attributed summaries, ledger/schema/freshness checks and `tools.validate check`; preserve declared non-applicable cases as such |
| Packaging/deployment | Version sync/installed entry tests, hygiene guard, applicable amd64/arm64 builds, deployment checks, image input/digest proof |
| Instruction-only docs | Applicable existing documentation tests, local Markdown targets/anchors, whitespace and policy consistency; no new runtime qualification claim |

Keep ledger generation and registry checks sequential. Partial documentation or
external-container tests do not measure complete REST coverage; disable the
`tests.route_inventory` plugin for these supplemental runs to avoid overwriting
the shared report, and preserve existing complete-run evidence. Protect runtime
data before any suite: use isolated temporary configuration/data, not private
root data. Do not infer pre-run integrity from a post-discovery checkpoint.

Record actual command arrays, environment/tool versions, tested/source SHA,
image digests/platforms, start/end, exit codes, passes/failures/errors/skips,
limitations and raw sanitized logs. Never flatten source/image/client scopes or
turn old passing results into fresh verification. Keep rejected runs and failed
oracles, including the existing conditional disconnect reproduction.

For instruction-only commits, perform scoped documentation checks. The default
pre-commit hook runs broad Python tests; this repository has previously used
`git -c core.hooksPath= commit ...` for such scoped maintenance. If using that
invocation-only exception, record why and the checks actually run. Do not change
global/repository hook settings, claim hook/full-suite success or use this
exception for implementation. Use Conventional Commit messages and stage exact
owned files, never blanket-add unrelated state.

Push scoped integration commits to the actual integration branch through the
existing PR chain. Normal documentation publication does not authorize merging
to main, baseline changes or release tags. If origin advanced, reconcile without
force, inspect/recheck affected changes and preserve ownership. Record commit,
remote and push receipt; compare `git rev-parse HEAD` to the exact
`git ls-remote <remote> refs/heads/<integration>` SHA. Do not start the next
execution wave until integration records are committed/pushed and equality is
verified. Keep the post-push receipt outside the commit it identifies; link it
from the ledger/handoff rather than creating an endless self-hash commit cycle.

## Preservation and exact cleanup

Before **any destructive local cleanup**, require all of the following:

1. Settled authority and accepted integration/review outcome; no surviving
   writer, protected resource or unresolved ownership. Failure is preserved too.
2. Outside the worker path, a **full Git bundle** containing the complete
   reachable task/base history and all task refs needed for recovery, without
   revision-range truncation. Run `git bundle verify`, inspect bundled heads,
   record SHA-256 and prove a recovery checkout can resolve the submitted SHA.
   A patch or remote branch alone is not this backup.
3. Inventory and preserve tracked working files, staged/unstaged/binary patches,
   untracked files, relevant ignored `build/` logs/reports/fixtures, complete
   transcripts and authoritative sanitized lifecycle/execution receipts. Verify
   copied-file hashes, completeness and destination outside the deletion target.
   A bounded tail is not a complete transcript; record clipping/export gaps and
   hold destructive cleanup if required preservation is incomplete.
4. Keep private runtime data, credentials and raw sensitive backups private;
   preserve them safely without putting them into Git, task branches, public
   bundles or artifact links. Public task history must remain sanitized and
   must not reintroduce vendor binaries, HARs or purged history.
5. Publish the exact task branch to the intended remote and verify its remote
   full SHA equals the submitted local SHA **before removal/deletion**. If
   publication is blocked or unsafe, retain the local resource and record the
   blocker; do not declare cleanup complete.
6. Prove integration with ancestry or a documented inspected equivalent commit
   mapping (for an intentional squash/cherry-pick), and record the integration
   SHA, review and combined verification. Retain the remote task ref by default.
7. Remove only the exact completed Orca-managed worktree with supported
   `orca worktree rm --worktree <exact-selector> --json`. Do not call raw Git
   removal for managed worktrees. Reconcile Git metadata only for that completed
   target, after checking other entries; no broad prune/clean operations.
8. Delete only its exact completed **local task branch** after proving it is
   unprotected, preserved, published, integrated and unused by every workspace.
   Prefer safe `git branch -d <exact-branch>`; a refusal means inspect/hold, not
   `-D`. Never force-push or delete protected/unrelated branches or resources.

Preservation failure overrides the preference for immediate worktree removal;
settled terminal release remains prompt where supported. Record release,
archive, publication, worktree removal, branch deletion and any held step as
separate states. Never claim old cleanup retrospectively met new bundle or
remote-publication requirements without evidence.

## Protected evidence and honest readiness

Protect the coordinator/root worktree, `main`, integration/release branches,
published tags, unresolved workspaces, unrelated edits and other projects.
Preserve ignored private `data/`, `config/`, configuration/backups and root
runtime JSON; never use `git clean`, recursive computed deletion or broad
resource pruning. The odd untracked encoded hook-directory artifact observed
in this checkout remains unrelated and protected. On Windows, resolve any
authorized deletion target to an absolute path inside the exact intended
workspace using one shell and literal paths before acting.

Do not normalize immutable evidence bytes. Respect the scoped `-text`
[attributes](../.gitattributes) for archived records/logs and preserve old failed
runs. Do not rerun historical checkpoint/render/publication helpers over populated
destinations. Keep current state separate from historical reports.

The 2026-10-19 software candidate has accepted source/image evidence; final CI
at `6dafb009` still fails three Tron paused frames. This dated result is not a
permanent CI waiver. Owner visual approval, HIL-B/C/E physical matrix/CEC/Remote/
Flic and owner HA/LAN/firmware evidence, HIL-D continuous 72-hour metrics and a
week of daily use/sign-off remain open. The registry has feature targets still
below qualification; no V4/V5 may be invented. arm64/QEMU smoke is not physical
arm64 qualification; the tested HA minimum line is not an exact-version-floor
test. Preserve the conditional alternate-disconnect limit and its red probe.

Follow actual PR dependencies: #36 targets main; #37 targets main; #38 targets
#37's integration branch. The RC must contain **both** Phase 6/7 and tested
runtime work before tagging main. Final `1.0.0` needs canonical version metadata,
matching rebuilt artifacts and affected evidence, not relabeled RC images.
No standing instruction approves the visual differences or closes field gates.

Maintain distinct states in the allocation ledger: **planned**, **held**,
**launched**, **observed-start**, **completed**, **reviewed**, **integrated**,
**qualified** (named scope only), **published**, **released**, **preserved** and
**cleaned**. Update outcomes, blockers and unknowns at each transition; never
overwrite negative findings. Finish a wave with actual evidence, remote equality
and explicit remaining gates, not a claim that every catalog model is ready.
