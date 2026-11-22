# Portable Orca phase development process

Version 1.0.0. This kit gives agents one reusable process for preparing phases,
assigning models to isolated worktrees, monitoring quota, reviewing implementation
and closing each wave with preserved work and a verified push.

The [protocol](PROTOCOL.md) contains the operating rules. The
[Orca adapter](ORCA.md) explains how to obtain current CLI instructions without
embedding a stale command manual. The [adoption prompt](ADOPTION_PROMPT.md) tells
a receiving agent how to install the process into its own repository. The
[optional skill entry point](SKILL.md) supports agents that load skills.

## Adopt into another repository

1. Give the receiving agent this whole directory or the release ZIP and the
   adoption prompt. The kit must be readable on that agent's machine. For another
   machine, transfer the ZIP; a path on the original machine is insufficient.
2. Have the agent inspect its current instructions, Git state, project plans,
   toolchain, review policy and Orca runtime before changing its process.
3. Copy the entire kit directory into `docs/agent-process/` in the target repo.
   Keep relative paths intact. If that directory already exists, compare and
   reconcile it; do not overwrite it wholesale. Preserve existing user changes.
4. Fill `docs/agent-process/REPO_CONFIG.json` from
   [REPO_CONFIG.template.json](templates/REPO_CONFIG.template.json), using observed
   target facts. Keep the template unchanged. Null values remain explicit unknowns;
   they cannot stand in for required execution evidence.
5. Append or reconcile [AGENTS.fragment.md](templates/AGENTS.fragment.md) into the
   target's root `AGENTS.md`. Its paths assume the destination above. Adapt paths
   if an existing documented destination is more appropriate. Do not replace the
   target's existing instructions or silently weaken its controls.
6. Initialize a factual current handoff, allocation/capacity ledger and model
   catalog at the configured paths. Use the templates as record shapes. Record
   `not_started`, `unknown` or `not_run` where appropriate; do not manufacture
   completed work to fill a template.
7. Validate local links, JSON, exact repo bindings, protected resources and the
   existing project verification command that applies to documentation changes.
   Commit/push only within the target user's established publication authority.
   Report adoption, remaining unknowns and the next authorized action.

The optional `SKILL.md` is readable directly. Installing it into an agent's skill
directory is separate and only necessary if the user requests installation. It
must retain the supporting files and does not replace the installed Orca skills.

## Files and records

| File | Purpose |
|---|---|
| `PROTOCOL.md` | Common phase/wave, review, capacity and closeout rules |
| `ORCA.md` | Runtime discovery and supervised lifecycle constraints |
| `ADOPTION_PROMPT.md` | Prompt to give the receiving agent |
| `templates/AGENTS.fragment.md` | Durable root instruction entry point |
| `templates/REPO_CONFIG.template.json` | Target bindings, policies, paths and verification commands |
| `templates/PHASE_PLAN.template.md` | Outcomes, dependencies, three-round debate and staffing decisions |
| `templates/WAVE.template.json` | Exact task/worktree/author/reviewer/fallback allocation |
| `templates/MODEL_CATALOG.template.json` | Discovered selections, actual route/competence evidence and limits |
| `templates/CAPACITY_EVENT.template.json` | Dated usage observations and routing decisions |
| `templates/CONSENSUS.template.json` | Actual panel contributions and same-packet final decisions |
| `templates/REVIEW.template.md` | Independent source/assertion review and author-owned corrections |
| `templates/HANDOFF.template.md` | Current state, unresolved work, resources and next action |
| `templates/CLOSEOUT.template.json` | Checks, lifecycle, archives, publication and closure evidence |
| `MANIFEST.json` | Version, source provenance and SHA-256 of each other kit file |

Use one capacity event object per JSONL line if maintaining a JSONL ledger. Keep
templates marked as templates; remove that marker only from instantiated records
whose actual facts have been filled. Do not pre-create future Task IDs or PASSes.

## Common defaults and local decisions

The owner defaults are three independent model families across three planning
rounds, at most three workers plus coordinator, no nesting, task-specific model
selection, qualified different-family implementation review, quota-aware routing
and verified closeout before the next wave. Below 30% capacity is a sizing signal,
not a ban. Missing quota or a third debate provider does not stop unrelated ready
work; record uncertainty/provisional coverage and keep technical gates intact.

The supplied owner profile excludes Anthropic models through every route. This
is a visible owner preference, not an Orca limitation. Reconcile any different
current target-user instruction explicitly; do not silently add or remove a ban.
Discover exact model IDs and supported effort locally. Model preferences are
candidates, not permanent assignments or qualifications.

Choose target-specific integration branch/remote, protected worktrees, existing
Run, environments, language/toolchain, validation commands, shared ownership and
release gates. Preserve the target stack; Rust commands and architecture are not
part of this portable process. Do not copy source-project phase IDs, Run/Task IDs,
branches, account quotas, production flags, reviewer failures or qualifications.
Prior model evidence may inform an assessment only with its original scope and
provenance; it is not target-project acceptance.

Reuse a target's existing Run. If it has none, adoption leaves the Run unset.
Only an authorized execution coordinator may create one after local discovery.
Never reset another repo's Run or use one belonging to the supplying repository.

## Scope and verification

Adopting this kit authorizes process documentation and local read-only discovery,
not product development, a phase debate, background services, paid changes,
deployment or messages outside authorized agent coordination. Existing task
authorization remains valid; do not add recurring permission questions.

Every later phase still needs its own actual preparation and execution records.
The quota-monitoring policy runs through an active coordinator. A persistent
automatic monitor/scheduler is not included and must not be reported as running.

For transfer integrity, verify each non-manifest member against `MANIFEST.json`.
The manifest does not hash itself and is an integrity aid, not a signature or a
source-review approval. The ZIP's sibling `.sha256` file hashes the archive.

Keep distributed core files intact where possible and put target bindings and
local deviations in `REPO_CONFIG.json` and an adoption report. If core files need
adaptation, record the originating version/manifest and the changes; do not claim
the old hashes verify modified bytes. For later kit versions, compare changes and
reconcile them with local policy. Never overwrite populated configuration, model
evidence, phase records or existing user instructions with fresh templates.
