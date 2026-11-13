# Original Fable remediation: two-round decision packet

Owner authority: hub message `msg_b052a16e725b`, 2026-11-13. Workflow
`task_c94bdfc187f6` in existing Run `run_37205f6095b3`. This packet prepares
two bounded rounds: independent R1, then exchanged peer reconciliation R2.
It starts no new implementation and grants no visual, qualification or landing approval.

## Frozen inputs and real authorship

- Integration/base: `680e93b88b711369e452cdbe415415ef23ab99ed`,
  `wp-runtime-completion`, local/live origin equality verified before preparation.
- Candidate source: `f2a122f955def578960303bc15242fed00d01be3`,
  branch `ryan-haver/audit-remediation-fable52`, five original Fable commits.
  Historical security head `730c0c2888386bef150d0fffee0ebd5ce9c57996` and its
  27 dirty paths were captured during account cutover; those edits subsequently
  became the remaining four commits. Current source is frozen, not independently accepted.
- [Fable's actual handoff](FABLE_HANDOFF.md): Task `task_8221ac785b94`,
  Dispatch `ctx_44dc5f1e0cc4`, original native conversation
  `f47fc739-3bb5-4a71-abcb-d1896c8e1fab`. Its exact original UTF-8 working bytes
  have SHA256 `ffece03c28aa388aaf4f9940e2549018e7e92efae19bcb263135b2a48f5db027`.
  This is a byte-identical copy, not coordinator-authored findings.
- The source author left only this new report uncommitted in its worktree.
  No report-only commit, tests, hooks, push or cleanup ran during the handoff.
- Original Gemini review is referenced by the handoff at its host-local path;
  reviewers may read it if present. Its absence must be reported, not reconstructed.
- Source/contracts/instructions are read from the candidate and their actual
  recorded commits. Current owner direction supersedes older routing instructions;
  historical privacy/qualification/visual holds remain actual holds.

## Questions to decide explicitly

Use `agree`, `reject`, `defer`, or `unresolved`, with exact source/contract citations,
alternatives, risk and the smallest useful acceptance check. Distinguish author
claims of completed fixes from independently verified behavior.

1. **CR-01 / WebSocket bounds.** Disposition of the already-authored wiring versus
   the recorded no-wiring grant and failed qualification. Can this source be
   retained as an unaccepted candidate under current owner scope, or must some
   part be set aside? Identify prerequisites; planning cannot manufacture qualification.
   Address the global client cap, per-client coalescing versus errors, stale status,
   shutdown/drain and app-instance isolation. Do not silently inherit a new contract.
2. **Settings host and TLS.** IP pinning versus a resolver/connection boundary
   preserving hostname verification; custom CA and fingerprint behavior, rebinding,
   reconnects and saved/displayed host semantics. Preserve the backend credential
   requirement. Decide `applied`, scene 404 changes and required REST registry/scenario
   updates separately from implementation convenience.
3. **HA.** API-key probe/envelopes and entry-data/options migration, one reload,
   404 behavior and the declared HA 2025.1.0 compatibility floor. The author's
   HA 2026.2.3 tests do not establish the earlier floor.
4. **UI and H1 password input.** General drawer versus unloaded settings layer,
   two uncaptured visible text changes, and password-entry options. Recommend
   an implementation and capture plan, but keep before/after owner approval held.
   No backend relaxation, automatic native-menu answer or visual-baseline change.
5. **H5 privacy/redaction.** Coordinate with unlanded `remediation/privacy-c4`
   and overlapping branches. Do not bypass a held privacy review by copying,
   cherry-picking or relabeling that implementation. Decide the smallest eligible
   next action and exact prerequisite evidence, including deferral when required.
6. **M5 Python floor and L2 lint.** >=3.12 metadata/documentation versus a real
   3.11 re-lock/CI proof; no false support claim. Root manifests, locks, CI,
   shared contracts, registry and integration remain coordinator-owned. Identify
   any necessary explicit coordinator action; this packet grants Fable none of them.
7. **Completed/refuted/deferred items and combined validation.** Explicitly
   disposition H1-H5/M1-M5/L1-L4 from the handoff. Preserve query-key auth and
   backend credentials unless a separately authorized material contract change
   is actually needed. Do not repeat completed audits. Identify exact combined
   checks, meaningful negative controls and outstanding UC/browser/HA/REST gaps.

## Rounds, outputs and barriers

R1 participants independently inspect identical packet bytes and exact candidate
source; do not read peers' R1 reports until all R1 results are captured. Write
only the assigned new report; no patches, source/test changes, new tests, model
helpers, services, hardware/LAN probes, secrets or credential/environment output.
Keep R1 to 1200 words plus one compact proposed file/test-grant table. Evidence
can include official primary documentation when a contract cannot be established
from source; browsing is read-only and citations must identify the actual source.

R2 receives all original R1 reports and a coordinator reconciliation. It challenges
and reconciles only material disagreements, then gives explicit per-item decisions
against one exact final-plan hash. Keep R2 to 1000 words plus decisions. No third
round is fabricated: irreconcilable/material choices go to the hub. Missing family
coverage is provisional, never consensus. No source acceptance is inferred from
planning agreement, peer-majority vote or a timeout.

Consensus must name agreed fixes, rejected/deferred items, unresolved disagreement,
exact exclusive file grants, tests, dependencies and human-only gates. Only after
actual agreement can owner-pinned Fable5.2/high remediate eligible ordinary work;
no routine permission request is added. Preserve all held prerequisites. A fresh
qualified different-family exact-SHA reviewer, independent of every implementation
author family, reports acceptance/blockers after corrections. Reviewers report;
authors fix. Normal exact-SHA landing/publication gates still apply.

## Custody and capacity

At most three active workers plus coordinator, no nesting. Initial R1 will be
sequenced conservatively with at most two new active assessors; Fable owner
conversation is retained idle for agreed remediation. Recheck exact route, native
identity, account consistency and pool capacity before every launch. Sol and
Argon are eligible technical read-only assessors in current routing; Opus5.5 is
recorded as a candidate. Hub `msg_13f63a372426` explicitly permits a bounded
manual Opus5.5/high planning trial (Why: trial), with native/new-account/high/
full-access/healthy-pool checks; no auto-routing, promotion or same-family source
acceptance is granted. Unknown quota is not headroom;
below30% needs a qualified verified fallback, or the affected dispatch stays held.
Fable author role is owner-pinned and cannot be silently substituted.

Actual staffing, Task/Dispatch IDs and observations are recorded in
[TRACKING.json](TRACKING.json). Original handoff helper `launch-check` returned
an honest agent-metadata mismatch for documented `--terminal` reuse (all requested
and effective launch fields null). Hub `msg_5287c57a95ce` confirms the installed
helper defect; exact live native Fable/account/high/bypass/same-UUID evidence
supports this continuation. The helper result is not called clean and no shared
tool was changed. Unanswered native questions remain held.
