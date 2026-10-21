# Worktree cleanup checkpoint

Observed 2026-10-21T02:40:43.872819+00:00. User authorized cleanup of eligible worktrees. No worker,
phase, service, source correction or evidence qualification was started.

## Removed and verified

The following completed workspaces had already lost their Git registrations and
local branches but retained empty folders/Orca entries after prior Windows EBUSY
failures:

- `wp-ev02-final-review`
- `wp-sw-findings`
- `wp-sw-repo-audit`
- `wp-sw-auth-review`

Before recovery, verified exact published task heads, integration ancestry,
full Git bundles and complete archive SHA-256 hashes against existing manifests.
All corresponding supervised workers were released, no Orca terminals remained,
and each exact directory was empty. Prior complete entry verification/native
transcripts and accepted combined-check receipts remain preserved privately.

Called exact `orca worktree rm` selectors. Orca returned: "is no longer a Git
worktree" and "Delete the folder yourself to finish removing this workspace."
Followed that supported recovery by resolving each exact literal directory,
checking its parent, emptiness and absence of reparse points, then removing it
without recursion. No force flags, raw Git removal, process termination, closed
handles, broad pruning or remote branch deletion. Verified directories and Orca
entries absent afterward; their local task refs were already absent.

Orca workspace count **13 -> 9**. Git registered checkouts remain **7**; these
four were residual entries, not four additional registered Git checkouts.

## Retained with exact reasons

| Resource | Reason |
| --- | --- |
| `wp-sw-api-preservation` | Published/integrated/preserved and empty, but exact non-recursive removal still fails because another process holds it. Orca terminals empty; existing Handle utility found no matching handle. No owner/process exit inferred, no kill/forced retry. |
| `wp-sw-api-header-proof`, `wp-sw-api-header-review` | Wave03 source accepted/merged locally, but combined verification remains pending; reviewer whole-workspace preservation also pending. |
| `wp-sw-api-offline-events`, `wp-sw-api-offline-review` | Same pending combined verification; controller/reviewer whole-workspace preservation pending. |
| `wp-sw-api-root`, `wp-ev02-name-review` | Existing user-owned/external resources remain protected. |
| `wp-runtime-persistence-wiring` | Unresolved Orca/filesystem/Git ownership discrepancy remains protected, even though the directory is empty. |
| Root checkout | Coordinator/integration, private runtime data, baselines, historical evidence, unrelated encoded hook-directory artifact and all other user changes preserved. |

All 60 Run rows checked on one complete page: **54 released, six retained**;
no new active workers. Coordinator inbox peek empty. Historical retained rows are
not new assignments. No changes to canonical levels or release gates.

The next cleanup opportunity is the locked preservation residual after its actual
lock clears, or wave03 worktrees after complete preservation and combined checks.
No need to repeat completed planning or request publication authority. Current
integration descendants remain unpublished while pending combined-source gates
are unmet; cleanup does not waive them or push those ancestors.

## Receipts and checks

Private original observations, supported removal receipts, verified archive/bundle
proof and post-state are in `build/worktree-cleanup-20261021/`, notably
`eligible-old-workspaces.json`, `residual-recovery-post-proof.json` and
`final-cleanup-report.json`. First inventory helper hit a null historical resource
field; corrected read-only enumeration retained, no destructive action preceded
completed eligibility checks. Managed removal of the already absent auth-review
selector returned selector_not_found, then the complete listing verified absence.

Documentation checks: 489 passed in 5.35 seconds with isolated data/config and
partial route writer disabled. All 18 local Markdown targets and CR-aware
whitespace checks passed. Local record-commit results are retained in that same
private directory. Scoped documentation-only invocation hook exception
is used after actual checks; no full source/CI/HIL success is claimed here.
