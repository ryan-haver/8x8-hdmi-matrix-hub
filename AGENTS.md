# Repository instructions for agents

Read the [standing orchestration protocol](docs/ORCHESTRATION_PROTOCOL.md) and
maintain the [agent allocation ledger](docs/production/AGENT_ALLOCATION.md).
Technical scope and release acceptance remain in the
[master plan](docs/planning/UNIFIED_MASTER_PLAN.md),
[runtime plan](docs/planning/NEXT_DEVELOPMENT_PHASES.md),
[remediation plan](docs/REMEDIATION_PLAN.md),
[validation policy](docs/validation/README.md) and [contributing guide](CONTRIBUTING.md).

- Standing instructions govern authorized work; they do not authorize starting
  a development phase, launching workers, changing visual baselines or releasing.
  For instruction-only maintenance, edit and check documentation only.
- **Current owner routing direction (2026-11-01):** Anthropic, Gemini,
  OpenAI Codex and MiniMax via OpenCode 2 are allowed candidates. This supersedes
  the earlier Claude/Anthropic exclusion for future work. DeepSeek is unavailable
  because the owner reports exhausted credit; do not dispatch it or buy credit.
  Preserve historical routing/reviews unchanged. Verify exact route, family,
  qualification and quota; audit nested routing and disable unassigned helpers.
- Before each execution wave, rediscover the integration branch, remote, Orca
  Run, execution hosts, catalogs, launch capabilities, protected resources and
  concurrency. Reuse the applicable Run; never reset or replace it to evade state.
  The dated bindings in the ledger are observations, not permanent launch args.
- Check provider/account-pool quotas before creating phase worktrees or
  dispatching authors/reviewers. Unknown quota is not verified headroom. Below
  30%, near exhaustion or insufficient capacity requires a suitable verified
  fallback with checked headroom; otherwise hold the affected dispatch.
- Capacity is a routing constraint, not a project-wide stop. Per the owner's
  2026-10-20 direction, redistribute ready work across available, task-qualified
  providers and continue independent packages when one route is constrained.
  Preserve cross-family review, honest quota observations and the concurrency
  ceiling; never wait for a preferred provider while a suitable route is ready.
- Use real Orca `orchestration worker-start` sessions in dedicated worktrees.
  Record Task/Dispatch authority, exact base, exclusive paths and acceptance.
  Keep shared APIs/contracts, root manifests, lockfiles and integration under
  coordinator ownership. Never silently substitute models or duplicate writers.
- Every new implementation package, including tests, fixtures and tooling,
  needs qualified independent review from a **different underlying model family**
  at the exact commit. Sol/Astra/Luna are one family. Historical reviews keep
  their original attribution; they do not establish this new review requirement.
- Audit boundaries, verify acceptance, review, integrate sequentially and run
  the applicable combined pipeline. For REST changes update
  `docs/validation/features.yaml`, `tests/sim/test_sim_rest_reads.py` and run
  `python -m tools.validate ledger`; retain 100% route coverage. Do not run
  ledger generation concurrently with registry checks.
- Settle workers through Orca; decide reuse/explicit retention/release before
  acknowledging deliveries. Preserve verified full Git bundles, artifacts,
  relevant ignored files, patches, transcripts and sanitized receipts before
  removal. Publish and verify task refs before destructive local cleanup.
  Remove exact owned worktrees through Orca; delete only proven completed local
  task branches. Never force-push or broadly prune resources.
- Preserve root/private runtime data, unrelated edits, historical failed runs,
  evidence bytes, baselines and unresolved workspaces. A stale handle or missing
  status is not proof of exit. Follow the installed Orca recovery guide.
- **Temporary storage (owner decision 21, 2026-11-10):** never create `C:/t`
  or another new drive-root folder. Use a registered agent-storage payload or
  `%TEMP%`; when a short path is necessary, use
  `C:/tmp/unfoldedcircle-orei-hdmi-matrix-integration/<task-id>/` and create its
  `.owner.json` first. Follow the [temporary-output rules](docs/ORCHESTRATION_PROTOCOL.md#temporary-output-and-short-paths)
  for ownership, evidence preservation and task-end removal. Include them in
  every worker spec. Historical task packets keep their original paths as
  records; those paths never authorize a new invocation.
- **Build output placement (owner decision 22):** build outputs and caches go
  in the worktree or its tagged `C:/tmp` task folder. Never put them in `%TEMP%`,
  Claude/OpenCode temp folders or tool scratch. At session end review ignored
  and untracked paths of at least 50 MB against code and unattended consumers;
  preserve credentials, user data and required evidence. See the current
  [archive disposition and manifest location](docs/production/storage-cleanup-20261110/DATA_REVIEW.json)
  before looking up historical `build/` evidence.
- **Retention (owner decision 23):** apply installed Orca SPOKE section 5c and
  [this repo retention policy](docs/production/STORAGE_RETENTION.md). Its bounded
  deadlines override indefinite evidence retention and recorded-path promises.
  Preserve actual source/history/branches, credentials and user data; preserve
  bytes an open task/gate/unlanded branch actually needs. Keep permanent manifests
  and receipts when eligible closed-work bytes expire. Never reset a deadline
  when copying, compressing or reviewing an artifact.
- Commit scoped integration records, push the integration branch and verify
  exact remote/local head equality before another execution wave. Follow the
  [publication and verification rules](docs/ORCHESTRATION_PROTOCOL.md#verification-and-publication).
- Distinguish planned, launched, completed, reviewed, integrated, qualified and
  published. Software passes do not approve Tron snapshots, physical HIL,
  72-hour soak, week field sign-off or final version/artifact release gates.

Current handoff discovery starts in the ledger and the
[execution record](docs/planning/RUNTIME_EXECUTION.md). Host-local handoffs are
supplemental; never assume their absolute paths exist on another host.

## Phased development and model coordination

Follow [the adopted process](docs/agent-process/PROTOCOL.md) and this repository's
[bindings and local policy](docs/agent-process/REPO_CONFIG.json). Current user
instructions and existing stricter compatible repository rules govern; the
[adoption report](docs/agent-process/ADOPTION_REPORT.md) records local overrides. Read the
configured current handoff and latest baseline before taking over coordination.

- Reuse this repo's existing Orca Run; load installed version-matched Orca skills,
  inspect live Git/binding, every worker-list page and inbox before dispatch.
  Never import another repo's Run, protected resources or qualification state.
- Prepare program direction and each phase with three genuine model providers
  across three rounds: independent assessment, peer challenge, then explicit
  decisions on one hashed final plan and staffing allocation. Incomplete provider
  coverage remains provisional; keep unrelated technically ready work moving.
- Reevaluate task/model/worktree matches every phase and before each wave.
  Record exact selections/supported effort, evidence, alternatives, independent
  reviewer, capacity/demand and accepted fallback author/reviewer combinations.
- Monitor quota/reset windows throughout active coordination. Below 30% or
  unknown reporting is not a project-wide stop. Preserve this repo's stricter
  verified-fallback requirement before affected creation/dispatch; reroute suitable
  ready work and reserve qualified review/correction capacity. No new spend,
  accounts or credentials are authorized by this rule.
- Handovers preserve source, dirty files, findings and actual authorship. Prove
  prior-writer settlement/recovery before replacement; never duplicate an active
  or uncertain writer. Apply existing material-change/fallback review rules.
- Use genuine Orca-supervised workers in isolated worktrees, at most three plus
  coordinator, no nesting. Pin bases, dependencies, exclusive paths and acceptance.
  Coordinator alone owns shared contracts/APIs, root manifests/locks and integration.
- Every new implementation, test or tooling deliverable needs qualified
  independent different-family review. Authors fix; reviewers report. No self-
  review, authorship relabeling or automatic failed-qualification retries.
- Integrate accepted packages sequentially and verify combined behavior. Release
  settled workers immediately; preserve artifacts/transcripts/verified bundles,
  verify task-branch publication, then use Orca-managed worktree cleanup. Delete
  only exact proven completed local task branches; preserve remote/protected work.
- Push and independently verify the configured integration head before the next
  execution wave. Record actual outcomes, unresolved blockers and honest readiness.
  Process adoption does not launch phases, workers or a background quota service.

Apply the new planning cycle prospectively to future phases/material plan changes.
Keep historical and in-flight decisions with their actual provenance; adoption
does not manufacture a completed debate or reopen recorded owner approval.
