# SW-REPO-01 — repository/security/release-engineering source inventory (author report)

**Task:** `task_39d9d5951f53` · **Dispatch:** `ctx_789b450d0a6e`
**Full base SHA:** `53e4b6710e9835ced03b7c614e2ee00f70649f2f` (worktree `ryan-haver/wp-sw-repo-audit`, `wp-sw-repo-audit`)
**Effective provider/model:** `minimax-coding-plan/MiniMax-M3`, actual variant **thinking**
(default M3 config resolving to the thinking variant; confirmed by the coordinator's native
session export — not relabelled as a literal `default`). No Anthropic, no other provider, no
helper/subagent/MCP/plugin, no fallback.
**Input report consumed:** `build/software-waves/SW-REPO-01/upstream-finding-audit.md`
(source commit `b008297b1a3c988789e92c2cb4c32f3396bcd07f`, parent `97e617c2`) — treated as
source-inspection triage, **not** as proof of closure.

## 0. Correction provenance

Original submission landed at `73a9621c0874e12c17f8ff525f44ce4c85f41a27` and remains the
authored commit of record. **No amend.** This file is a bounded prose correction under fresh
Task `task_f3691c08b309` / Dispatch `ctx_7bbd908b29c9`, same `minimax-coding-plan/MiniMax-M3`
thinking-native route, same exact base, same single-file scope
(`docs/production/software-waves/SW-REPO-01/AUTHOR.md`).

The coordinator's external review of `73a9621` flagged four wording problems; this revision
calibrates them in place without re-running any scan, network fetch, history scan, secret
read or config edit:

1. The §4 "no CI run receipt in the repository at all" claim overstated the absence — the
   repository already carries a *prior* published CI receipt at the source base, attributed
   exactly rather than relabelled as a new candidate pass. Fresh exact-candidate CI and
   branch-protection inspection still belong to the coordinator evidence step and were not
   performed here.
2. The §4 / row-8 "No credential-shaped material was found … all classified false positive"
   wording made a global no-credential conclusion from a redacted gitleaks report and
   path/key context alone, and the matching "next correction" item instructed broad 64-hex
   suppression. Both are replaced with *candidate* digest/test-literal status that requires
   exact-match coordinator verification before any suppression, and the broad allowlist
   instruction is removed. No secret value was read into the report or printed.
3. The §3 "188 dangling blobs … not purge residue" sentence drew a provenance/vendoring
   conclusion over byte contents the task did not inspect. The unreachable-blob read-only
   scan is honestly noted as beyond the work spec's tracked-ref-inventory scope; only the
   tree-path observation under the 84 unreachable *commits* is reported, with no
   blob-provenance or vendor-content claim.
4. The row-8 "all classified false positive (§5)" cell is relabelled as *candidate*
   classification aligned with §5; no finding is closed and no feature level is set.

No source/test/tooling/registry/ledger/evidence/push/merge/tag/cleanup or actual config edit
is performed in this correction. Local edits and a focused doc-only invocation hook
exception (`git -c core.hooksPath= commit`) are used; persistent hook settings are unchanged
and no full-hook pass is claimed. Diff is confined to `AUTHOR.md`. Original commit
`73a9621` is preserved as the source-of-truth authored commit; subsequent settlement must
attribute any acceptance/closure to the corrected prose commit, not to `73a9621`.

## 1. Scope and authority

Read-only bounded inventory of **SEC-14**, **SEC-15** and **DEP-05** against the exact source,
CI and tracked history at the base. Writable: this file and `build/software-waves/SW-REPO-01/**`.
No product/test/tooling/fixture/manifest/lock/registry/ledger/finding/plan/baseline/evidence
edit. No finding closed, no feature level set, no evidence record written, no push, merge,
tag, cleanup, network owner device, or history rewrite. No legal conclusion is drawn and no
new owner gate is invented.

## 2. Method actually executed

| # | Check | Result |
| --- | --- | --- |
| 1 | `git rev-list --objects --all`, per-pattern path scan | 17 604 objects; **0** hits for `*.exe`, `*.c4z`, `*.har`, `*.bin`, `XP3`, `Control4`, `User_Manual`, `firmware`, word-bounded `RTI`, `BK-808 Firmware|RTI|Control4`, `BK-808_User_Manual` |
| 2 | Remaining `BK-808` paths in history | 129 paths, all under `tests/fixtures/device` — the project's own golden captures |
| 3 | `git fsck --unreachable --dangling` | 498 lines; 84 unreachable commits, 188 unreachable blobs; newest 2026-10-19T22:32:56-06:00 |
| 4 | `git ls-tree -r` over all 84 unreachable commits | **0** purged-vendor paths |
| 5 | CI pin scan of `.github/workflows/ci.yml` | 14 distinct `uses:` refs, **0** without a 40-hex SHA |
| 6 | `Dockerfile` `FROM` scan | 1 external base, `Dockerfile:24` digest-pinned |
| 7 | `python -m tools.check_repo_hygiene --all` | `0 error(s), 0 warning(s) in every file in HEAD`, exit 0 |
| 8 | `gitleaks git .` 8.30.1, `.gitleaks.toml`, `--redact`, report into `build/…` | exit 1; **36** `generic-api-key` findings, all redacted, all *candidate* false-positive under file/line/key classification in §5; no finding closed here and no feature level set |

Raw output: `build/software-waves/SW-REPO-01/scan-output.txt`,
`build/software-waves/SW-REPO-01/gitleaks-history.json` (redacted; values never printed).

Object counts drift between runs (17 578 → 17 604) because `refs/codex/turn-diffs/checkpoints/*`
is rewritten by the IDE while the scan runs; the per-pattern zero counts are stable.

## 3. SEC-14 (H) — vendor firmware/drivers/manual in public history; stub LICENSE

**Exact current condition.** No purged vendor blob or path is reachable from any local or
remote-tracking ref (`refs/heads/*`, `refs/remotes/*`) at the base: 0 hits across all ten
patterns (§2 #1). The only `BK-808` paths are the project's own fixtures. 84 unreachable
commits exist in the local object store; their `git ls-tree -r` output contains 0 purged
paths (§2 #4). 188 dangling blobs also exist and were *not* byte-inspected by any check
above: the extra read-only `git fsck --unreachable --dangling` plus tree walk beyond the
tracked-ref-inventory call in §2 #1 is honestly noted as beyond the work spec's
tracked-ref-inventory scope, not as evidence about blob provenance or vendor content.
No deletion authority follows from that extra read-only scan, and this report draws no
conclusion about what the 188 dangling blobs contain.

`LICENSE` is the full **MPL-2.0** text: 293 lines, ending with Exhibit A (Source Code Form
License Notice) and Exhibit B. Not a stub. `docs/vendor/README.md` documents the removal, the
ten former paths with SHA-256 checksums, the firmware versions, and the contributor rule that
CI rejects `*.bin`, `*.exe`, `*.c4z`, `*.har`.

**Existing proof.** Checks 1–4 (history scan, executed here) and check 7 (the project's own
binary/size guard, executed here, clean). The ban is enforced in CI by the `hygiene` job
(`ci.yml:232–258`, `python -m tools.check_repo_hygiene --base "$BASE_SHA"`).

**Missing proof / owner action.** A local tracked-ref scan is **not** the GitHub-cache purge.
`docs/REMEDIATION_PLAN.md:546` carries the unclosed owner checkbox: *"Ask GitHub Support to
purge cached views/refs of the removed blobs"*. That remains owner-only and is unchanged by
this report. No evidence of the request, acknowledgement or completion exists in the repository,
and no legal conclusion about redistribution rights is drawn here.

**Concrete next correction / verification and acceptance.** Executable software work: none
outstanding for SEC-14 in the tracked repository. Residual: the owner action in
`REMEDIATION_PLAN.md:546`. Observable acceptance for the repository half is the two executed
checks above (history scan clean, `check_repo_hygiene --all` 0/0) re-run at the coordinator's
integration commit; the owner half closes only when the coordinator records the owner's
confirmation, which is not a software acceptance and not asserted here.

**Text-drift note (register, coordinator-owned).** `docs/vendor/README.md:3` dates the
removal 2026-09-24; `REMEDIATION_PLAN.md:545` records the force-push as 2026-09-25
(`469c013`). Documentation reconciliation, not a code defect.

## 4. SEC-15 (L) — gitleaks never run; actions tag-pinned; base image not digest-pinned

**Exact current condition.** All three limbs are contradicted by source at this base.
Actions: 14 distinct `uses:` references in the only workflow file (`.github/workflows/` holds
`ci.yml` alone), **every one** pinned to a 40-hex SHA with a `# vX.Y.Z` comment
(e.g. `ci.yml:40`, `ci.yml:214`, `ci.yml:226`, `ci.yml:277`). Base image:
`Dockerfile:24 FROM python:3.12-slim@sha256:a6e34c5…d11b1`; the remaining three `FROM` lines
are internal stage references. Gitleaks: config `.gitleaks.toml` (`useDefault = true`, path
allowlist), fingerprint allowlist `.gitleaksignore:3` (one known doc false positive), and a
`gitleaks` CI job (`ci.yml:260–281`) wired to `.gitleaks.toml` with `GITLEAKS_ENABLE_COMMENTS:
'false'`. `.github/dependabot.yml` schedules monthly github-actions, docker and pip updates
against those pins.

**Existing proof — and its exact limit.** This is *static pin and job presence*. A job that
exists in a workflow is not a run that passed. **No remote CI run for the exact candidate
base (`53e4b671…`) was fetched or inspected in this task**, so SEC-15's original "never run"
claim for the candidate is neither confirmed nor refuted here.

The repository does carry a *prior* published CI receipt at the source base `97e617c2`
(parent of `53e4b671`, recorded as the existing main-line review base in the local
coordination handoff), preserved in
[`docs/validation/runs/ev02-api-evidence/integration.json`](../../../validation/runs/ev02-api-evidence/integration.json)
and recorded with that exact scope in
[`docs/production/AGENT_ALLOCATION.md`](../../AGENT_ALLOCATION.md) §"Software wave
build-out" (CI run `39374096223`, "all 13 required checks" at base `97e617c2…`, UI included).
That historical receipt attests the *source* tree only; it is not relabelled as a fresh
candidate pass and does not substitute for fresh exact-candidate CI/protection inspection,
which remains the coordinator evidence step below.

What *was* executed: a **local** full-history `gitleaks git .` scan (8.30.1, committed config,
`--redact`). It exited 1 with 36 `generic-api-key` findings across 4 files and 4 commits
dated 2026-10-17 → 2026-10-19. Classification, from file/line/key inspection only, with no
value ever printed:

- 35 findings are 64-hex **SHA-256 digests** used as JSON object keys in input-parity evidence
  (`docs/validation/runs/runtime/final-image-input-parity.json`,
  `…/runtime-r8b/final-image-input-parity.json`,
  `…/runtime-r8b/accepted-independent-review.json`) — e.g. the key is a source path such as
  `src/hub/openapi.py` or `src/password.py`, the value the digest.
- 1 finding is `tests/test_security_v3_hardening_scenarios.py:492`,
  `@pytest.mark.parametrize("style", [...])` — a short literal in a test parameter list.

No credential-shaped material was *asserted* found. Each match remains a **candidate**
digest/test-literal false positive under the same path/line/key classification; a
final determination requires exact-match coordinator verification against the original Git
blob (for a SHA-256 key: confirm the value equals the expected hash of the named source
path; for the test parameter: confirm the value equals the expected literal in the test
list) **without printing secret-shaped values**. No broad 64-hex allowlist or
"suppress-all-digests" rule is asserted here; only narrowly justified fingerprints (path
+ expected SHA-256, or test name + expected literal) belong in `.gitleaksignore` after the
coordinator's exact-match check, and meaningful negative coverage against non-digest,
non-literal credential shapes is preserved.

**Missing proof / owner action.** The proof SEC-15 still lacks is a **CI run receipt** for a
commit that exercises the `gitleaks`, `hygiene`, `hassfest`, `hacs`, `docker-build` and
`publish` job graph, plus the remote branch-protection required-check list. Branch protection
is a remote repository setting and is **not observable from this clone**. There is no owner
decision pending here — this is an evidence-availability gap, not a new gate.

**Concrete next correction / verification and acceptance.** Two distinct items:
1. *Executable software work (future author, coordinator-owned files, future dispatch):*
   the committed `.gitleaks.toml` has no `generic-api-key` discriminator for 64-hex digests
   used as JSON object keys, so a *full-history* gitleaks run exits non-zero on clean input.
   **Do not introduce a broad 64-hex allowlist or any "suppress all digests" rule.** If
   suppression is required, the future author records each match as a *narrowly justified*
   fingerprint (path + expected SHA-256, or test name + expected literal) and proposes it
   **after** a coordinator-confirmed exact-match check against the original Git blob or
   expected literal — without printing secret-shaped values — for inclusion in
   `.gitleaksignore`. Observable acceptance: `gitleaks git .` exits 0 on a clean tree with
   no broad-digit allowlist and only coordinator-verified fingerprints suppressed, and
   meaningful non-digest, non-literal credential shapes still match. Whether this is
   *needed* depends on CI's scan range (`gitleaks-action` scans the PR/push range, not full
   history) — unverified here, so it is filed as a *friction risk, not a red CI*. **No
   actual config change is authorized by this report.**
2. *Coordinator evidence step:* retrieve and attach one CI run receipt at the candidate commit.
   Acceptance for SEC-15 = pinned-source inspection **plus** that receipt, **plus** the
   coordinator's register text reconciliation for `REMEDIATION_PLAN.md:201`. No remote run,
   protection setting or licence/legal conclusion is asserted by this report.

## 5. DEP-05 (M) — CI triggers, lint scope, mypy, hassfest/HACS, gitleaks, multi-arch

**Exact current condition**, clause by clause against `.github/workflows/ci.yml`:

| DEP-05 clause | Current source | Verdict |
| --- | --- | --- |
| "no `pull_request` trigger" | `ci.yml:9–16` `on: pull_request:` + `push:` main/`v*` + `workflow_dispatch:` | contradicted |
| "ruff only on `src/`" | `ci.yml:54–60` builds the path list `src tests custom_components tools run.py run_server.py` (existing ones only) | contradicted |
| "mypy non-blocking" | `ci.yml:85–86` `mypy src/`, no `continue-on-error`; `publish` `needs: typecheck` (`ci.yml:699`) | contradicted in source; branch-protection required status unverified |
| "no hassfest/HACS validation" | `hassfest` `ci.yml:199–214`, `hacs` `ci.yml:216–230`, both blocking since WP-D1 | contradicted |
| "no gitleaks" | `gitleaks` `ci.yml:260–281` | contradicted (see §4 limit) |
| "QEMU set up but no multi-arch platforms" | `docker-build` builds `linux/arm64` under QEMU (`ci.yml:342–355`); `publish` builds `linux/amd64,linux/arm64` (`ci.yml:773`) and verifies both manifests + version label (`ci.yml:785–803`) | contradicted |

The separate HA test job (`ci.yml:160–197`) exists and is **live**: `tests/ha/` and
`requirements-test-ha.txt` are both present, so the `present` guard does not skip it.
`publish` (`ci.yml:692–713`) requires 13 of the 14 jobs (all but the PR-only `ui-comment`) and
is additionally gated on `github.event_name != 'pull_request'` and ref `main`/`refs/tags/v*`.

**Register drift (coordinator-owned).** DEP-05's Location column still names
`.github/workflows/docker-publish.yml`, which does not exist; publishing now lives inside
`ci.yml`. The Phase-0 checkbox at `REMEDIATION_PLAN.md:549` is marked `[x]` while the row at
`:232` still has no resolution text, so the parser keeps it open. Reconciling that text is
register work, not code work.

**Missing proof / owner action.** Same limit as SEC-15: no CI run receipt was fetched or
inspected at the exact candidate base (`53e4b671…`), and no branch-protection required-check
list was inspected. The *prior* published source-base CI receipt at `97e617c2` (run
`39374096223`, all 13 required checks) recorded under §4 is not a candidate-base or
branch-protection claim. `permissions: {}` at `ci.yml:24` with per-job grants,
`persist-credentials: false` on every `actions/checkout`, and `concurrency` cancelling only
superseded PR runs are source-visible least-privilege controls; none of them is execution proof.

**Concrete next correction / verification and acceptance.** No further code change is
indicated by source inspection. Acceptance = one attached CI run receipt at the candidate
commit in which `gitleaks`, `hassfest`, `hacs`, `hygiene`, `typecheck` and the arm64
`docker-build` all report success on the PR event, plus coordinator reconciliation of
`REMEDIATION_PLAN.md:232`. Not asserted here.

## 6. Honest gaps, limits and non-claims

- **Executed here:** tracked-history vendor scan, unreachable-object tree scan, CI pin scan,
  Dockerfile pin scan, `tools.check_repo_hygiene --all`, one local full-history `gitleaks git .`.
- **Not executed / not available:** any GitHub Actions run, branch-protection or required-check
  inspection, `hassfest`/`hacs` execution, Docker or QEMU build, Playwright visual jobs,
  ruff, mypy, pytest, `tools.validate`, any push/tag/release, any GitHub Support request.
  Static presence of a pinned action, a digest pin or a CI job is **not** a passed remote
  security scan and is labelled as such wherever it appears above.
- **SEC-14 wording discipline:** "0 purged vendor paths reachable from a ref" is a statement
  about this clone's refs at this base. It says nothing about GitHub's cached views, forks,
  or any server-side copy, and it is not a legal conclusion. The §3 tree-path observation
  is limited to the `git ls-tree -r` output of the 84 unreachable *commits*; the 188 dangling
  blobs were *not* byte-inspected and no conclusion is drawn about their provenance, vendor
  content or "not-purge-residue" status. The extra read-only `git fsck --unreachable
  --dangling` plus tree walk beyond the work-spec tracked-ref inventory is honestly noted as
  beyond scope; no deletion authority follows from it.
- **SEC-15 wording discipline:** the local gitleaks run is a *local full-history* scan, which
  is broader than the `gitleaks-action` PR-range scan CI performs. Its 36 findings are
  *candidate* digest/test-literal false positives from file, line and key inspection; no
  matched value was read into this report or printed, no finding is closed, no feature level
  is set, and any future suppression must follow the exact-match coordinator-verification
  path in §4 (no broad 64-hex allowlist, only narrowly justified fingerprints after the
  original Git blob or expected literal is checked). The remote-CI limit refers specifically
  to the *exact candidate* base (`53e4b671…`); the repository does carry a prior published
  source-base CI receipt at `97e617c2` (run `39374096223`, all 13 required checks) preserved
  in `docs/validation/runs/ev02-api-evidence/integration.json` and recorded with that exact
  scope in `docs/production/AGENT_ALLOCATION.md`. That historical receipt attests the source
  tree and is not relabelled as a fresh candidate pass.
- **Registry observation, not a finding:** `refs/heads/main` is 28 commits ahead of
  `refs/remotes/origin/main`, the base `53e4b671` is reachable only from
  `refs/remotes/origin/wp-runtime-completion`, and seven local branches are unpushed
  (including `ryan-haver/wp-sw-repo-audit`). Publication is the coordinator's decision; nothing
  was pushed, merged or cleaned up from this worktree.
- This is the **author** report. It is not an independent review and makes no self-claim of
  one; a different-underlying-model-family review at the exact submitted commit is still
  required before any acceptance.

## 7. Publication

Author-only prose. Report commit recorded in the completion message (`worker_done`). No push,
merge, tag, cleanup, register edit, ledger regeneration or finding closure.