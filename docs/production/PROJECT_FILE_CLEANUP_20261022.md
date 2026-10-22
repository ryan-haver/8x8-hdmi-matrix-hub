# Project file cleanup and Windows residual recovery

Observed 2026-10-22T02:11:23.692632+00:00. User authorized cleanup of unneeded old project Orca/OpenCode
files and failed-delete worktrees. This sweep is scoped to this HDMI project.
No phase, worker, paid model call, deployment or release was started.

## Completed Windows residual cleanup

`wp-sw-api-preservation` is now absent from disk and Orca. The empty folder was
previously locked; Orca is now 1.4.237, runtime
`90aa9fd9-dfbc-4dfe-8061-8be9154242db`. Same existing Run
`run_37205f6095b3`, coordinator handle `term_259c5526-02c2-44a8-b469-bf171aa435a0`,
generation 2. Refreshed installed guides/live inventory. No Orca terminal remained
in this folder; Handle returned no matching handle. No process/handle was killed
or forcibly closed. Under the new runtime, exact non-recursive removal succeeded.

The exact `orca worktree rm` receipt again instructed deletion of this leftover
non-Git folder. Verified exact absolute path/parent, empty directory and no root
reparse point first, then followed that recovery. Earlier complete archive/bundle,
published-ref and integrated-ancestor checks remain in
`build/worktree-cleanup-20261021/eligible-old-workspaces.json`.

Orca entries **9 -> 8**; Git registrations remain **7**. The five prior cleanup
residuals are now all gone; this does not include the separately unresolved
persistence workspace below.

## Obsolete files removed from active locations, reversibly

Moved **20 exact directories / 1,288,098,644 bytes (about 1.20 GiB)** into:
`build/project-file-cleanup-20261022/quarantine/`.
The relocation map is `reversible-relocation-plan-complete.json` in its parent directory.
This is quarantine, not permanent deletion or reclaimed disk space.

| Category | Count | Recovery proof |
| --- | --- | --- |
| Old CORS test temp directories `c1-hook-v90b4ka3`, `c1-hook3-erf6axvs` | 2 | Every current regular file and junction target matched the existing complete tar manifests; archive SHA-256 verified. Junctions were moved without following or deleting their targets. |
| Older EV-02 copied recovery workspace | 1 | 167 paths differed from its later final-review archive, so a separate complete gzip tar was created; all 4,285 file hashes verified before moving. No historical version was discarded. |
| Obsolete project OpenCode snapshot caches | 14 | Exact `core.worktree` mapping tied each cache to this project. Five matched the completed cleanup workspaces; nine additional original worktree folders are absent. Complete gzip archives preserve all objects, refs, index/config and exact file hashes. No extra author settlement/qualification is inferred for these historical cache copies. Active snapshot directory count 19 -> 5. |
| Standalone completed bundle-recovery clones `build/w3r/h`, `o`, `r` | 3 | Exact heads/source equivalence, full verified bundles, no extra unreachable Git objects, no ignored artifacts; all four untracked generated hook files plus local Git metadata preserved in verified extras archives. These were coordinator recovery copies, not Orca task worktrees. |

Eighteen relevant full native OpenCode session exports were preserved and hashed.
Original sessions, child histories and databases remain intact; no session deletion,
DB surgery or history rewriting. Shared OpenCode service remains running for its
existing users. Shared package/model caches, credentials/configuration and other
projects were not modified.

Full cache/native/recovery archives remain private/ignored in
`build/project-file-cleanup-20261022/`. The source task full bundles, original
workspace archives, immutable evidence, failed attempts and visual baselines are
retained. OpenCode cache manifests record snapshot-cache scope, not new source
qualification. The prior short recovery-checkout proof remains historical;
`verified-recovery-clones.json` records their new location and recovery inputs.

## Automatic approval limitation

Automatic approval review rejected the attempted permanent recursive deletion
batch with only **"blocked by policy"**. The batch never ran. Switched to exact,
validated, reversible `Move-Item` operations with unoccupied project-specific
destinations; no permanent recursive deletion was retried. Files and backups
therefore remain on disk. Quarantine can be restored using the exact recorded
source/destination mapping after ensuring the original source is unoccupied.
Permanent disposal is unperformed; no disk-space saving is claimed.

## Retained resources and precise prerequisites

- `wp-runtime-persistence-wiring`: current folder is empty/no Git marker; matched
  two historical settled/released Dispatches. Source
  `168fc0322ca452cd30a7273062e778ca8193c332` is integrated, but fresh remote lookup
  found its named task branch absent and original full-preservation attribution
  remains unresolved. Preserve it; do not infer historical compliance or recreate
  publication/cleanup authority from an empty directory.
- Four recent wave03 task worktrees remain: header author/reviewer and offline
  controller author/reviewer. Independent source reviews and local merges exist,
  but combined verification and remaining full-workspace preservation still gate
  their removal. No source/qualification gate waived to clean disk.
- Old user-owned `wp-sw-api-root`, external `wp-ev02-name-review`, root/private
  runtime/config/backups, unrelated encoded hook artifact and other projects stay
  protected. New runtime missing-status observations do not prove those agents
  exited. No broad service restart, process kill, handle close, Git prune/clean,
  force push or remote branch deletion.

Current canonical feature levels and source/evidence attribution are unchanged.
Source c993 remains locally merged, pending combined campaign/evidence/review/
pipeline work; adoption 6b74 and previous cleanup 040ab are local documentation.
This record is also local: pushing descendants would publish that pending source.
Existing publication authority is sufficient once technical gates are met; no
new execution wave or publication is performed by this cleanup.

## Validation and receipts

Full post-move path/hash/head reconciliation is retained in
`verified-quarantine-post-state.json`; exact archives/manifests, bundle/fsck logs,
native exports, source/destination mapping and Orca removal/current inventories
are in the same private cleanup directory. Initial read-only diagnostics included
an unsupported OpenCode API operation, legacy/live session-store mismatch and a
native-export shim lookup correction; they triggered no model work or deletion.
No credentials/account files were read as cleanup input or published.

Final documentation suite: 489 passed in 3.32 seconds, isolated data/config and
partial route writer disabled. All 20 local Markdown targets and CR-aware whitespace
checks passed. All 20 post-move trees and 18 native-export hashes verified. Local
record-commit receipt is retained alongside those receipts. Documentation-only invocation hook
exception applies to this scoped record; no source hook/full CI/HIL pass claimed.
