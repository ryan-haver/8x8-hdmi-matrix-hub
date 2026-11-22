# Orca runtime adapter

Read this when adopting runtime bindings or executing the portable protocol.
It is a discovery and safety guide, not a copy of a particular Orca CLI release.

## Load the installed instructions

Use the target environment's available `orca-cli` and `orchestration` skill
discovery stubs to resolve the correct executable. Follow `ORCA_CLI_COMMAND` or
development/runtime-specific selection as those installed stubs direct. Bare
`orca` can name a screen reader on Linux outside Orca; do not guess an executable.
Do not install or upgrade software merely to adopt documentation.

With the resolved executable, obtain the version-matched guides through its
supported `skills get orca-cli` and `skills get orchestration` commands, preferably
JSON. Load conditional references before the associated placement, expanded
coordination, messaging or recovery operations. If guides are unavailable, use
installed help for read-only discovery and report execution capability unknown.
Do not fabricate commands, silently switch runtimes or substitute another framework.

## Verify local authority before dispatch

Inspect runtime status, repo/worktree identity, current coordinator binding and
the target's existing Run. Bind that Run through the documented `run-use` route;
do not reset it. Enumerate all `worker-list --include-remote` pages scoped to the
Run and inspect the coordinator inbox before placement. Preserve retained and
protected resources. Adoption itself creates no Run, Task, Dispatch or worktree.

When the target has no Run, leave its config unset during adoption. An authorized
execution coordinator can create a new Run only after confirming none is already
applicable. A source kit's provenance commit is not a runtime identity.

## Actual supervised placement

Use the installed supervised worker-start procedure with exact task scope, base,
worktree and requested model. A bare `agent launch` does not create supervised
Task/Dispatch authority. Record actual effective identity and turn evidence; input
acceptance alone does not prove a model ran.

Fresh-launch model support and effort support are agent/host/version dependent.
Inspect installed help and advertised capability. Some OpenCode routes require
an existing worktree and do not support effort flags. Do not generalize that
historical limitation to all future releases or bypass a current refusal.
Do not repeat an unchanged failed launch or silently omit a requested model.

One coordinator consumes the Run inbox. Validate each completion against its
active Dispatch, decide its resource ownership immediately, then acknowledge
processed deliveries. Questions, heartbeats, timeout and PTY liveness are not
completion. The fleet verdict and execution-host evidence govern recovery;
unknown/unverifiable is never promoted to exited.

## Quota and handovers

Discover supported account/usage reporting through installed help. For hosts
where `account list --json` exposes usage, select only sanitized pool/window
fields; never publish raw account/credential data. Observe provider timestamps
and unsupported fields. It may return cached usage and need not expose a plan's
absolute allowance, per-model limit or mapping to the intended worker route.

Dynamic placement uses an accepted fallback and a fresh supervised invocation.
There is no assumed atomic live-model swap. Preserve a checkpoint and settle or
recover the previous writer before replacement. Use the installed recovery guide
for the proven state, with idempotent retry identities where supported. Do not
replace an ambiguous launch with a fresh request or duplicate an uncertain writer.

This adapter does not implement continuous telemetry or a background scheduler.

## Preservation and removal

Release/reuse/retain settled workers according to the installed lifecycle rules.
Preserve full relevant artifacts, available native transcripts and verified Git
bundles, then publish and verify exact task branch heads. Only then use the
installed Orca managed-worktree removal command. An uncertain removal requires
supported inspection/recovery, not raw deletion, broad pruning or shared-process
termination. Preserve protected worktrees and all existing user changes.

## Missing Orca capability

Complete useful repository inspection and process adoption without pretending
workers ran. Record the unavailable capability and leave affected execution
unstarted. The receiving user can authorize a separately documented adapter for
another orchestrator, but that is not Orca authority and must never be reported
as the requested Orca process. Do not stall unrelated authorized local work.
