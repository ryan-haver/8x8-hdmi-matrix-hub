# Repository storage retention

Owner decision 24 (2026-11-11), "Purge now, keep hashes," and installed Orca
`SPOKE.md` section 5c supersede decision 23's 14/30/90-day waits, monthly archive
rebuild and older indefinite evidence or recorded-path promises. Closed work
keeps manifests, receipts and checksums. It keeps no evidence archive. This
applies to the primary checkout, owned repo workspaces, owned storage and
Git-internal artifact folders. It authorizes no product phase or release.

| Class | Disposition |
| --- | --- |
| Source, Git history, branches, committed docs and records | Keep always; no history pruning |
| Credentials, `.env`, user data, media and assets | Keep; owner decides |
| Actual named dependency of an open task, gate or unlanded branch | Keep while open and needed |
| Rebuildable outputs, caches, venvs and scratch | Purge at task end; keep a verified in-use unattended dependency |
| Pinned build bytes | Keep original SHA256 in manifest; purge closed bytes now |
| Shipped release binary named in a release record | Keep one year |
| Closed test output, transcripts, QA packets, loose evidence and logs | Keep original-path/size/SHA256 manifest and receipts; purge bytes now |
| Existing closed evidence zip/tar/zst | Keep member manifests and receipts; purge archive now |
| Recovery/worktree archives and Git bundles | Purge once every commit survives on an actual local or remote branch |
| Agent-storage tool payloads | Close finished payloads as disposable through the tool; seven-day quarantine is compliant. Never raw-purge or globally sweep |

Closed means done, cancelled, superseded, or an accepted or abandoned containing
phase. If no task, gate, receipt or commit gives a close date and no open task,
gate or unlanded branch references the item, use its newest internal file mtime.
Missing dates create no hold. Copying or reviewing bytes creates no new keep.

Only owner-set longer keeps survive decision 24. Record an actual reason and
an `until` date, at most one year; only the owner renews it. Coordinator-created
retention dates for closed evidence end now. Source/data protection and actual
open dependencies remain guards; a generic historic reference creates no
indefinite dependency. `C:/scripts/#OLD` is owner-protected: never touch it.

Before removal verify ownership, untracked/ignored status, closure, branch
custody, source/data protection and absence of live or unattended consumers.
Inventory archive members before purging their container. Preserve actual
uncommitted source or user assets separately if discovered; keep the affected
container until preservation succeeds. A Git LFS pointer alone is insufficient
proof of asset bytes: verify the retained LFS object or actual source file.

Use one consolidated repo plan, one cross-family read-only plan review and one
guarded execution pass. Immediately recheck exact paths, parent reparse points,
tracked-file exclusions, size, SHA256 and exclusive-open access; stop on changed,
locked or unknown state. Read back every result. Managed workspaces use Orca's
lifecycle command and retain branches under current owner direction. Never
force, broadly prune Git resources or interrupt shared services. Do not touch
another agent's active output or the storage tool's quarantine.

If automatic approval review blocks a verified deletion, do not retry or route
through another shell. Send the hub exact paths, bytes and proof; read back its
result. Current plan, member manifests and application receipts are under the
primary checkout's `build/purge-now-20261111/`. The committed rollout record is
[PURGE_NOW.json](storage-cleanup-20261110/PURGE_NOW.json). Frozen earlier records
retain their historical facts; current manifests record intentional deletion
and never promise that every recorded path still has bytes.
