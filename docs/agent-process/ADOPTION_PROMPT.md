# Prompt for the receiving agent

Replace `PROCESS_KIT_PATH` below with the local directory containing this file,
or the directory where you extracted the supplied ZIP. Run the receiving agent
inside its target repository; its current workspace is the target. Give it access
to the whole kit, not just this prompt.

```text
Adopt the reusable phased-development process from PROCESS_KIT_PATH into this
repository so future agents follow one consistent process.

Read the kit's README.md, PROTOCOL.md, ORCA.md, SKILL.md and the relevant templates.
Inspect this repository's existing AGENTS.md/instructions, current development
plan, live handoff, latest validation evidence and Git state. The current workspace
is the receiving repository; the kit's source repository is not your execution
target. Treat kit source/provenance IDs as historical references only.

Copy/reconcile the complete kit into docs/agent-process/, preserving relative
paths. Preserve existing files, user changes, stricter compatible rules and the
current project architecture/language. Do not overwrite an existing process
directory or AGENTS.md wholesale. Reconcile genuine instruction conflicts and
ask only when current user authority does not resolve an action that needs it.

Create docs/agent-process/REPO_CONFIG.json from its template using this repo's
actual root, integration branch and remote, documented protected resources,
existing Orca Run/coordinator bindings where discoverable, environments, shared
ownership, validation commands, model/provider restrictions and release gates.
Keep unknowns explicit. Reuse an existing target Run; if none exists, leave it
unset during adoption. Never reset a Run or import the supplying repo's Run,
Task IDs, branches, quota snapshots, production flags or model qualifications.

Append/reconcile templates/AGENTS.fragment.md into root AGENTS.md, fixing links
if this repo requires a different destination. Initialize an honest current
handoff, model catalog and capacity/allocation records at the configured paths.
Document missing observations as unknown/not_run/not_started, without invented
PASSes, participant contributions, worker activity or acceptance.

Make the following standing process explicit:
1. Program direction covers phase order, goals, dependencies, priorities and
   assumption-based timeline ranges. Every phase gets fresh three-provider,
   three-round planning: independent assessment, peer challenge and explicit
   decisions on one hashed final phase plan and staffing allocation.
2. Every phase evaluates the models for its actual tasks and isolated worktrees,
   including exact routes/supported effort, demonstrated task fit, alternatives,
   current capacity, independent reviewers and accepted fallback combinations.
   Refresh the assessment before each wave; no permanent model entitlement.
3. The active coordinator tracks quota/reset windows and demand throughout the
   phase at a recorded cadence/checkpoints, reserves review/correction capacity
   and adjusts new assignments to suitable available providers. Below 30% or
   unknown quota is not a global stop. Preserve provisional debate coverage
   honestly and keep unrelated ready work moving.
4. Model handovers preserve exact source/dirty files, findings and authorship.
   Prove the previous writer settled or exited under supported recovery before
   transferring ownership. Never launch two writers or silently swap models.
5. Use real Orca-supervised Tasks/Dispatches in separate worktrees, at most three
   workers plus coordinator, no nesting. Load target-installed version-matched
   Orca skills before operations; verify actual effective model and turn evidence.
6. New implementation/test/tooling packages need qualified independent review
   from a different underlying model family. Authors fix; reviewers report.
   Preserve failed evidence and actual authorship; no automatic qualification
   retries, retrospective relabeling or waived technical/environment gates.
7. Integrate accepted packages sequentially, verify combined behavior, release
   settled workers promptly, preserve full relevant artifacts and verified bundles,
   publish/verify task branches, use Orca-managed cleanup, then push/verify the
   integration head before the next execution wave. Preserve protected resources.
8. Update the ledger, current handoff and actual readiness state after each wave.
   Templates, planning agreement and lifecycle success are not production proof.

The kit's supplied owner profile excludes Anthropic models through every route;
honor this unless this repository's current user instruction explicitly changes
it. Discover permitted exact models through supported local catalogs; do not copy
stale selections or import source-project pass/fail qualifications. No credentials,
account changes, new spend or global skill installation is authorized by adoption.

This request authorizes process adoption and supported read-only discovery.
It does not start a development phase/debate, workers/worktrees, persistent quota
monitor, product changes or deployment. Do not claim background automation exists.
Preserve any separately authorized ongoing work and its actual state.

Validate JSON, links, policy consistency and this repo's applicable documentation
checks. Commit/push only under this repo/session's existing authority; otherwise
leave a concrete reviewable change and identify the precise missing authority.
Finish with changed files, observed target bindings, unresolved unknowns/conflicts,
checks, publication status and what future agents must read first.
```
