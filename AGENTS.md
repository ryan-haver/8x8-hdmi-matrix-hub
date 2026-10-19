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
- **No Claude/Anthropic**, including reviewers, helpers, defaults and fallbacks.
  The historical six-model roster is retired. Audit nested routing too.
- Before each execution wave, rediscover the integration branch, remote, Orca
  Run, execution hosts, catalogs, launch capabilities, protected resources and
  concurrency. Reuse the applicable Run; never reset or replace it to evade state.
  The dated bindings in the ledger are observations, not permanent launch args.
- Check provider/account-pool quotas before creating phase worktrees or
  dispatching authors/reviewers. Unknown quota is not verified headroom. Below
  30%, near exhaustion or insufficient capacity requires a suitable verified
  fallback with checked headroom; otherwise hold the affected dispatch.
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
- Commit scoped integration records, push the integration branch and verify
  exact remote/local head equality before another execution wave. Follow the
  [publication and verification rules](docs/ORCHESTRATION_PROTOCOL.md#verification-and-publication).
- Distinguish planned, launched, completed, reviewed, integrated, qualified and
  published. Software passes do not approve Tron snapshots, physical HIL,
  72-hour soak, week field sign-off or final version/artifact release gates.

Current handoff discovery starts in the ledger and the
[execution record](docs/planning/RUNTIME_EXECUTION.md). Host-local handoffs are
supplemental; never assume their absolute paths exist on another host.
