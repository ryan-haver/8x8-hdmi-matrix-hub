# Orca dispatch, review and correction templates

Read [the wave plan](../SOFTWARE_RELEASE_WAVES.md),
[package briefs](PACKAGES.md), [manifest](manifest.json) and
[standing protocol](../../ORCHESTRATION_PROTOCOL.md). Templates are prose, not
an executable launcher. A coordinator fills and validates every field against
current runtime state. Existing owner authorization persists; routine routing
and reversible implementation do not require another permission question.

## Preflight and ready queue

1. Rebind actual branch/full SHA/remote, runtime/coordinator handle, existing
   Run, repository/host, catalog/launch capabilities and protected inventory.
2. Read supported provider/account-pool usage; record observation/window/reset,
   available quota/credits and author/review/fix commitments. Inspect helpers,
   plugins, defaults, setup hooks and exact family. Rebalance constrained routes
   immediately; pull other ready units forward. Never call invented quota APIs.
3. Compute slots conservatively, including retained/unverifiable processes.
   Choose an eligible author and different-family reviewer. Current quota on one
   provider is not transferable to another account or model family.
4. Resolve only real prerequisites for this bounded unit. A scoped no-change
   support audit can satisfy the harness gate while unrelated inventory runs.
   Record the gate proof; never simply delete a dependency to start early.
5. Pin full base SHA and exact exclusive new/leased paths. Publish integration
   records and verify prior-wave remote equality. Create the dedicated worktree
   through Orca after route checks, then use genuine `worker-start` authority.

For OpenCode, rediscover supported existing-worktree model selection on the
actual host. If using the configured route, pin every internal model and deny
excluded/opaque helpers/providers before inference. Record that CLI model/effort
may be null and prove actual native execution. The earlier 1.4.230 refusal is
historical, not blanket proof that 1.4.232 supports or refuses the override.
Do not change shared global settings or use bare launch as Task authority.

New scenario links must be symmetric for the normal implementation hook. When a
unit adds scenario IDs, the coordinator can apply/audit/stage only that feature's
registry-link delta in the worker worktree and explicitly permit its inclusion
in the normal implementation commit. The worker does not edit the registry.
Coordinate index operations to avoid racing the author. This permits a clean
committed-head campaign with correct mappings; do not accept diagnostic records
that incorrectly look clean while new scenario files are still untracked.

## Author envelope

Fill every bracket; unset fields hold only this assignment while other eligible
work continues.

```text
Objective: [package/unit], exact primary feature IDs and interfaces from manifest.
Current authorization: nonhardware development; no new baseline approval or release.
Run: [rediscovered existing Run]. Actual Task/Dispatch: live injected preamble only.
Host/worktree/actual branch: [returned Orca identities]. Full base: [40-char SHA].
Dependencies: [accepted integration/gate SHAs, or scoped no-change proof].
Route: [exact provider/model/variant/effort/harness; no silent default/substitution].
Capacity: [UTC observation, account pool, remaining, window/reset, commitments].
Review: [qualified DIFFERENT underlying family, checked capacity and reserved fixes].
Exclusive writes: [unit paths plus any explicit minimal serial lease].
Read-only/prohibited: product/shared paths absent a lease, registry/ledger, root
manifests/locks, private data, historical evidence/failures, visual baselines,
unrelated resources, main/tags/release publication.
Read first: AGENTS/protocol, actual package brief, feature claim/basis/interfaces,
existing scenarios/client drivers, original evidence and applicable findings.
Change: [preserve/rerun/map/assert/correct; do not assume a defect from absent proof].
Invariants/counterexamples: [independent effects/readback; negative/cancel/no-leak
or no-command/no-unrelated-mutation where relevant; source/client limits].
Acceptance: [exact existing commands, isolated new outputs, actual record/check
inspection, per-client Scenario.features_for, covers/source/environment/digests].
Implementation uses normal hooks. No --record or canonical ledger mutation by
workers. For partial pytest disable tests.route_inventory; do not overwrite the
full-route report. Do not run ledger generation beside registry checks.
New shared/product need: report a reproducible finding/lease request; do not expand.
Delivery: full base/submitted SHA, diff/path audit, commands/exits/counts/skips,
failures and artifacts, evidence attribution, open limits; no push/merge/cleanup.
Check full inbox at checkpoints and immediately before one live-authority
worker_done; then idle. Coordinator preserves/publishes and decides release/reuse
before acknowledgment. Report capacity changes so work can be redistributed.
```

## Independent review envelope

```text
Review [unit] at exact author SHA [40 chars], against assigned base [40 chars].
Author underlying family [family]; reviewer [different family, exact verified
route/model/variant/effort], domain/tool qualification [actual evidence].
Fresh supported quota/host/route observation [UTC, units/reset/commitments].
Use a separate exact-author-commit worktree. Inspect source, assertions, diff,
per-client feature attribution, covers, refusal/cancel cases and actual outcomes.
Run [bounded independent existing checks/campaign] with isolated fresh output;
inspect record/check/state/command/image identities, not exit0 alone.
Only new [unit REVIEW.md and reviewer artifact subtree] writable. Reviewers
report; authors fix. New reviewer tooling/tests are implementation too and cannot
review themselves. No product/schema/fixture/baseline/registry/evidence edits.
Report exact reviewed SHA, effective family proof, invariants/counterexamples,
findings/severity and acceptance/hold scope with actual evidence and limits.
No API-to-V3, source-to-image, numerical-level-to-release or human-gate promotion.
Read full inbox before one worker_done, then idle; no push/merge/cleanup.
```

## Corrective child and integration gate

For each reproduced defect, record `FIX-<finding>-<attempt>` with a new genuine
Task/Dispatch, exact changed base, observable failed control, exclusive source/
test lease and required independent review. Reuse a proven settled worker only
through fresh authority; otherwise release it promptly. Do not duplicate a writer
on timeout or ambiguous liveness. Reviewers cannot apply their own proposed fix.

Coordinator acceptance records: author boundary audit; worker verification;
different-family exact-commit review; material-fix re-review; sequential merge;
applicable combined verification; preserved original evidence and actual target
scope; verified full bundle/recovery/transcripts/artifacts; published task ref;
settlement decision before ack; exact eligible cleanup or honest hold; integration
commit/push/full remote equality. A completed Task is not an accepted gate.

Only then can a dependent logical package consume that integration SHA. Bind
logical dependencies to actual Run Task IDs without inventing them. If a review
or owner gate is pending, continue independent ready units on qualified capacity;
do not integrate unreviewed implementation or manufacture gate acceptance.
