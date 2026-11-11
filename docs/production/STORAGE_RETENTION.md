# Repository storage retention

Owner decision 23 (2026-11-10), installed Orca governance `SPOKE.md` section
5c, supersedes indefinite evidence retention and promises to keep bytes at
recorded paths. This applies to the primary checkout, repo workspaces, owned
shared storage and Git-internal artifact folders. Git objects, refs, reflogs,
branches, committed docs and actual source remain protected; this policy does
not authorize Git history pruning. Credentials, `.env`, user data/media/assets
are never purged by agents. Do not infer artifact ownership from size or age.

| Class | Disposition |
| --- | --- |
| Source, history, branches, committed records | Keep always |
| Credentials and user data/assets | Keep; owner decides |
| Actual dependency of an open task/gate/unlanded branch | Keep while needed and open |
| Rebuildable output, caches, venvs, tool scratch | Purge at task end; retain a real in-use unattended dependency |
| Pinned build bytes | Keep original SHA-256 in manifest; purge bytes 14 days after close |
| Shipped release binary | Keep one year |
| Closed-work evidence | Loose 14 days, then one compressed archive with original-path/hash manifest; purge archive at 90 days, retain manifest/receipts |
| Recovery/worktree archive | Purge 30 days after landing/abandonment if commits survive on a branch or bundle |
| Logs | Purge after 14 days |

Closed means done, cancelled, superseded or an accepted/abandoned containing
phase. Use original task/phase closure, never a new copy/archive/review date.
Record native completion timestamps where available; label conservative phase
closure bounds explicitly. Bulletin 2026-11-10s supplies the fallback: if no task, gate, receipt or commit
gives a close date and no open task/gate/unlanded branch references the item,
use the newest original file modification time inside it. Missing close dates
do not create owner-review holds or keep entries. Actual unique source and user
data remain protected; a file extension alone does not prove safe disposal.

Longer keeps require `{"keep":{"reason":"...","until":"YYYY-MM-DD"}}`,
at most one year. Only the owner renews them. Keep existing promises as dated
history; prospective artifact custody follows this policy. Expired keep metadata
does not authorize deleting unresolved source, credentials or user assets.

The hub's clarification (`msg_d2a88a442999`) leaves the verified 20 GB aggregate
unchanged now. Its new per-member manifest carries original path, SHA-256,
class, closure basis and due date. Rebuild at most monthly on its original
first-due schedule, removing due eligible members together. Expired log/pinned
build members may ride until that batch. Purge the entire container when all
members are due; preserve its manifests and receipts. Source/open/data guards
still apply. This does not start an automation or a product phase.

Before any purge, verify ownership, untracked/ignored status, no protected
source/data, no unattended consumer and no live writer. Use Restart Manager or
a fresh exclusive-open check, compare current size/SHA-256 and verify lossless
compression before deleting a loose original. Stop on changed/locked/unknown
state. Read back every result. Managed workspaces use Orca lifecycle commands;
keep branches under the current owner direction. Never force, broadly prune
Git resources or interrupt shared services. If automatic approval review blocks
a verified deletion, send exact paths/sizes/evidence to the hub and read back
its result; do not retry through another shell.

Before a monthly drop, gate phase bounds on the newest original item/root
mtime, prove surviving commits/refs or a verified full bundle for every recovery
member, and recheck due members against surviving source refs and unique user
data/credential content. Scan text payloads as well as JSON. Require fresh
unattended-consumer and exclusive-open checks. Missing proof keeps the member;
a due timestamp alone authorizes no source or data loss.

Current rollout pins and post-review application receipt location are in
[RETENTION_POLICY.json](storage-cleanup-20261110/RETENTION_POLICY.json). Frozen
older evidence paths resolve through the retained manifests, including the
original owner-22 manifest and the new physical-prune crosswalk. A manifest
records intentional purge as well as retained members; it never promises that
all recorded paths still have bytes.
