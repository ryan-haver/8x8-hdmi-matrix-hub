# SW-AUDIT-01: independent review of the CI evidence intake inventory

**Disposition: ACCEPT** — the bounded inventory in
[CI_EVIDENCE_INTAKE.md](CI_EVIDENCE_INTAKE.md) is factually accurate at exact
candidate `9036ecffe2b5e18ccb6d636eba55edfbd0d6a80a`. Every quantity, mapping,
digest, ancestry fact and assertion-description claim in that report was
recomputed independently from the retained raw bytes and the exact candidate
source, and every one reproduced exactly.

This ACCEPT covers **inventory and metadata only**. It is not an admission
decision, not a feature qualification, not a canonical adoption, not a privacy
clearance, not a screenshot visual approval and not a closure of any finding.

| Authority | Observation |
| --- | --- |
| Task / Dispatch | `task_88451be35b50` / `ctx_3d5cba0330a2` |
| Run / worker / coordinator | `run_37205f6095b3` / `term_be107841-b2ac-45be-b772-58df5ed4af79` / `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662` |
| Host / reviewed candidate | Windows local; worktree `wp-ci-proof-review`, branch `ryan-haver/wp-ci-proof-review`, exact HEAD `9036ecffe2b5e18ccb6d636eba55edfbd0d6a80a` (verified at dispatch) |
| Reviewed artefact | [CI_EVIDENCE_INTAKE.md](CI_EVIDENCE_INTAKE.md) (author: OpenAI `gpt-6.1-sol` / high) |
| Reviewer model | native MiniMax-M3 / thinking — bounded inventory/metadata review only |
| Reviewer qualification | bounded inventory/metadata review. **No** source or privacy code-review qualification is claimed or inferred |
| Immutable input read | `…/wp-ci-proof-intake/build/software-waves/SW-AUDIT-01-ci-proof-intake/` (`attempt-01`, `analysis-01`, `input`, `final-01`) — read-only, unmodified |
| No substitution | no Anthropic, no helper, no nested worker, no fallback, no global configuration change, no `opencode.json` change |

## What this review did and did not do

The intake report's own numbers were **not** trusted. Every claim was
recomputed from two independent directions: the raw CI ZIP bytes plus the
coordinator input, and the exact candidate source tree read out of Git.

**Did:** recompute both archive digests and CRCs; re-derive the unit, feature,
matched/missing and check tallies from the raw records; re-derive each record's
source, dirty state, covers, features, client attribution, level and
screenshot references; re-derive every declarative expectation description from
the scenario definitions at the exact source commit and compare it against the
recorded checks; re-prove the ancestry non-membership and the tree equality;
re-read the retained CI run/job metadata and job logs; and re-derive the
report's own two tables and compare them cell by cell.

**Did not:** re-execute any scenario, re-run any test or validation campaign,
re-contact GitHub, regenerate the ledger, execute any artifact script, extract
any archive to disk, read or reproduce any secret-bearing value, run a source or
privacy code review, visually approve any screenshot, or decide admission.

## Independent method

| Step | How it was done |
| --- | --- |
| Raw archives | `hashlib.sha256` over the retained ZIP bytes; `zipfile.ZipFile.testzip()`; member-name safety screen (absolute, parent-traversal, drive/colon, backslash) |
| Records | Both ZIPs opened read-only; the `evidence/**.json` members parsed in memory; no member written to disk |
| Candidate source | `git archive --format=tar bdcf06dc… tools tests/validation docs/api` streamed read-only into this reviewer's own ignored build subtree, then the scenario packages imported there. No ref, index, worktree or hook was touched, and no repository module was executed from the live tree |
| Expectation ground truth | `tools.validate.model.Expectation.describe()` at `bdcf06dc…`, compared as exact strings against the recorded `checks[].description` |
| Covers screen | the repository's own `tools/validate/gitinfo.matches` rule (exact path, directory prefix, `fnmatch` glob) applied to each record's own covers |
| Git ancestry | `git cat-file`, `git merge-base --is-ancestor`, `git rev-parse …^{tree}`, `git diff --name-only`, `git log -1 --format=%H %T %P` via fixed argv |
| Report tables | the two markdown tables in the intake report parsed and compared cell by cell against the recomputed values |

## Verified results

### Archive integrity — both raw ZIPs, from retained bytes

| Artefact | Bytes (expected = actual) | Members | SHA-256 (recomputed) | Official metadata digest | `testzip()` | Unsafe names |
| --- | ---: | ---: | --- | --- | --- | ---: |
| `validation-evidence` (12853945294) | 30,334,482 | 1,743 | `54fbd594305ebecc9acdcdc25fd2524352d715129cf09448d4cc4cf1a1ca5774` | identical | `None` | 0 |
| `validation-ha-evidence` (12853275385) | 104,792 | 30 | `f30555eb92dcf9053bfa7f0e33047ec6b48dc75b4c63c19ca466416fa81b9825` | identical | `None` | 0 |

The retained official metadata (`attempt-01/artifact-*.json`) reports
`expired: false`, `expires_at: 2026-11-27`, `workflow_run.id: 40770556464` and
`workflow_run.head_sha: e16ec6af4d13c76c7024d42b605afec0c8ae9bf4` for both
artefacts, matching the intake report.

### Inventory counts — recomputed from the raw records

| Quantity | Report claim | Recomputed | Result |
| --- | ---: | ---: | --- |
| Requested scenario/client/level tuples | 60 | 60 (over 55 distinct scenarios) | match |
| Requested feature IDs | 38 | 38 unique | match |
| Matched records (exactly one record each) | 56 | 56, zero ambiguous | match |
| Missing units | 4 | 4, all four Flic V3 units | match |
| Passing checks | 470 | 470 | match |
| Nonapplicable checks | 2 | 2 | match |
| Failed checks | 0 | 0 | match |
| Total checks across the 56 records | 472 | 472 | match |
| `result` / `gate` / `blocked_reason` / `findings` | all `pass` / `ok` / none / zero | 56/56 each | match |
| Client split | 30 api, 7 browser, 19 ha | 30 / 7 / 19 | match |
| Level split | 30 V2, 26 V3 | 30 / 26 | match |
| Distinct cover sets | 11 | 11 | match |
| Records per archive | 1,513 (A) + 19 (H) | 1,513 + 19 | match |
| Whole-archive client census | A: 1,433 api, 62 browser, 18 uc; H: 19 ha | identical | match |
| Execution window | `2026-10-28T21:18:07.379Z` … `2026-10-28T21:27:22.981Z` | identical | match |

The two nonapplicable rows are exactly the intake report's U53 and U59
(`reboot.enabled_shortcut` / api and `shortcuts.preset_recall` / api), each
carrying the exact recorded reason `not checked for client 'api'`; their browser
counterparts (U54, U60) pass the same assertion. Both are genuine
client-scope exclusions, not waivers or suppressed failures.

### The four absent Flic units are explained by the CI command, not by a gap

Across **all 1,532** records in both archives the client census is
`api 1433 / browser 62 / uc 18 / ha 19` — there is **no** `flic` record at any
level. The retained job logs show why, independently of the report's prose:

| Job log | Line | Content |
| --- | ---: | --- |
| `attempt-03/job-123106264167.log` | 302–303 | `tools.validate run --client api --client browser --client uc --operator automation --out build/validation` |
| `attempt-03/job-123106264167.log` | 1873–1874 | `tools.validate check --expect-clients api,browser,uc --evidence build/validation/evidence …` |
| `attempt-03/job-123106264102.log` | 357–358 | `python -m tools.validate run --client ha --operator automation --out build/validation-ha` |
| `attempt-03/job-123106264102.log` | 439–440 | `python -m tools.validate check --expect-clients ha --evidence build/validation-ha/evidence …` |

No Flic client was ever requested, so no Flic unit could exist. This is a scope
property of the CI run, and it matches the intake report.

### Source attribution and dirty state — preserved, not relabelled

All **1,532** records in both archives declare `commit.sha =
bdcf06dc6723aad7da63ecfed3d3555ab0d02e55`, `commit.short = bdcf06dc`,
`commit.branch = HEAD`. Every one of the 56 matched records additionally has
`commit.dirty = false` and `commit.dirty_files = []`. No record was reassigned
to the published head `e16ec6af…` or to the frozen base `490a879b…`.

The retained job logs corroborate the checkout independently, at exactly the
line numbers the intake report cites:

| Job log | Line | Content |
| --- | ---: | --- |
| `attempt-03/job-123106264167.log` | 227 | `HEAD is now at bdcf06dc Merge e16ec6af4d13c76c7024d42b605afec0c8ae9bf4 into 6debe5a9d1ce3b5993bbd1f6c16d14550d11141b` |
| `attempt-03/job-123106264102.log` | 160 | `HEAD is now at bdcf06dc Merge e16ec6af4d13c76c7024d42b605afec0c8ae9bf4 into 6debe5a9d1ce3b5993bbd1f6c16d14550d11141b` |

`bdcf06dc…` is therefore the synthetic pull-request merge commit, exactly as the
report states. Its actual source SHA is preserved; nothing was relabelled.

### Ancestry: not an ancestor, despite tree equality — the central fact, re-proved

| Git fact | Exit / result | Reading |
| --- | --- | --- |
| `git cat-file -e bdcf06dc…^{commit}` | exit 0 | the source commit object exists |
| `git cat-file -t bdcf06dc…` | `commit` | it is a real commit, not a tree |
| `git merge-base --is-ancestor bdcf06dc… 490a879b…` | **exit 1** | **the actual source is NOT an ancestor of the frozen base** |
| `git merge-base --is-ancestor e16ec6af… 490a879b…` | exit 0 | the published head IS an ancestor of the frozen base |
| `git merge-base --is-ancestor bdcf06dc… 9036ecff…` | exit 1 | the actual source is also not an ancestor of this review's candidate |
| `git rev-parse bdcf06dc…^{tree}` | `7fa5c9d99731349b0705fa2ef7818d5eb5a11350` | — |
| `git rev-parse e16ec6af…^{tree}` | `7fa5c9d99731349b0705fa2ef7818d5eb5a11350` | **identical to the source tree** |
| `git rev-parse 490a879b…^{tree}` | `f70bcd4a51a68bd26dde80fab1e6070f10058b0f` | whole trees differ from both |
| `git log -1 --format=%H %T %P bdcf06dc…` | `bdcf06dc… 7fa5c9d9… 6debe5a9… e16ec6af…` | two parents: it is a merge commit whose second parent is the published head |
| `git diff --name-only bdcf06dc… 490a879b…` | 6 paths | `docs/agent-process/state/HANDOFF.md`, `docs/planning/RUNTIME_EXECUTION.md`, `docs/production/AGENT_ALLOCATION.md`, `docs/production/software-waves/SW-API-READ-03/INTAKE.md`, `docs/production/software-waves/SW-AUDIT-01/COORDINATOR_REVIEW.md`, `docs/production/software-waves/SW-AUDIT-01/FRESHNESS_DELTA.md` — all documentation, no runtime, source, test or client path |

Tree equality with the published head does **not** confer ancestry, and the
intake report does not claim it does. The report's framing — that these records
are blocked for freshness admission because their actual synthetic merge source
is not an ancestor of the frozen base — is correct as stated.

### The covered-path equivalence does not satisfy the ledger rule

Read from the exact candidate source (`tools/validate/gitinfo.py`,
`tools/validate/ledger.py` at `bdcf06dc…`):

- `gitinfo.changed_since(sha)` returns `None` when `git merge-base --is-ancestor
  sha HEAD` fails, i.e. when the commit is not in this history;
- `ledger.freshness()` then returns `"unknown"`, and `ledger.compute()` places
  any record whose freshness is not `"fresh"` into the row's `stale` collection.

So under current repository policy these 56 records compute as stale/unknown
regardless of the fact that their covers are disjoint from the six changed
paths. The intake report says exactly this, and it is correct.

### Assertion descriptions against the exact candidate source — 56/56

For every matched record, the scenario was resolved by id at `bdcf06dc…`, each
declarative expectation's `describe()` string was produced from the candidate
source, and that set was compared against the record's recorded
`checks[].description` values as exact strings.

| Check | Result |
| --- | --- |
| Units compared | 56 |
| Scenario found at the candidate source for every unit | 56 / 56 |
| Every declarative expectation description present in the record | **56 / 56**, zero missing |
| Record `features` == `Scenario.features_for(client)` at the candidate source | 56 / 56 |
| Requested feature IDs ⊆ the record's actual feature IDs | 56 / 56 |
| Record `covers` == the scenario's `covers`, exactly | 56 / 56 |
| Record `covers` ∩ the six source→base changed paths (repo `gitinfo.matches` rule) | **empty for all 56** |
| Record `level` == `level_for(target, client)` at the candidate source | 56 / 56 |
| Record `client` ∈ the scenario's declared `clients` | 56 / 56 |
| Record `target` | `sim` for all 56 |
| Only residual check descriptions not derived from a scenario expectation | the runner's own WebSocket-schema check (`every WebSocket message follows docs/api/websocket.schema.json`), its client-action check and its client precondition check |

The record feature sets are supersets of the 38 requested features: eleven
additional feature IDs (`F-API-032`, `F-API-033`, `F-API-034`, `F-CEC-005`,
`F-DOM-027`, `F-MTX-001`, `F-MTX-003`, `F-MTX-006`, `F-MTX-007`, `F-MTX-031`,
`F-REL-009`) appear on the records because a record carries the scenario's full
`features_for(client)` set. The intake report states this correctly ("Actual
features equal `Scenario.features_for(client)` in every matching record; the
38-row feature map below names the requested subset").

### Screenshots — structurally verified, not visually approved

The seven matched browser units (U24, U25, U52, U54, U56, U58, U60) each
reference exactly one PNG. Every referenced member is present in archive A, has
a valid PNG signature, measures **1440×900**, has **every chunk CRC valid**, and
matches the ZIP entry CRC. The intake report's `Shot` column is correct for all
60 rows with **zero** mismatches, and API/HA rows correctly show no screenshot.

Screenshot bytes were **not** visually inspected and no screenshot is approved
here.

### Client attribution

| Claim | Recomputed |
| --- | --- |
| Browser records use Playwright and `chromium 153.0.8010.12` | confirmed; one distinct browser environment across the seven matched records |
| Hub entry is `run.py -> hub.cli shared runtime (UC_ENABLED=false)` | confirmed for the matched records |
| Hub `image_digest` is `null` for all 56 | confirmed (these prove source-run simulator behaviour, not an executed release image) |
| HA client is a real `homeassistant/home-assistant:2026.9.3` container, component `custom_components/hdmi_matrix 1.0.0rc1`, client digest `homeassistant/home-assistant@sha256:d8922685169707fd91e8b9729902d975f06157d005e422874d201e0261dda196` | confirmed |
| That client digest is not a hub image digest and not exact HA minimum-version proof | correct as stated |

### The intake report's own tables — cell-by-cell

| Table | Rows | Mismatches |
| --- | ---: | ---: |
| Sixty proof units (scenario, client/level, archive/folder, state, P/N, Shot) | 60 | **0** |
| Disposition for the 38 freshness rows (matched/missing counts) | 38 | **0** |
| Disposition table `Target / recorded` vs frozen-base `docs/validation/features.yaml` (`target` / `current`) | 38 | **0** |

The report's unit ordering matches the coordinator input order exactly
(U01…U60), and the four Flic rows correctly show `— / —` for archive/folder,
`M` for state and `—` for P/N and Shot.

### F-API-034 remains a separate, real assertion gap

Across **1,480** scenarios at `bdcf06dc…`, **zero** expectations describe
`switch_all_failed`. `F-API-034` appears as a *client feature ID* on the
`routing.route_all` / api record, but a feature ID on a passing success record
does not establish the named all-output failure event. The intake report's
separate treatment of this gap is correct, and the gap is untouched by this
review.

## Findings

| # | Severity | Finding |
| --- | --- | --- |
| 1 | **None — accepted** | Every recomputed quantity, digest, mapping, ancestry fact and assertion-description comparison in [CI_EVIDENCE_INTAKE.md](CI_EVIDENCE_INTAKE.md) reproduced exactly at candidate `9036ecffe2b5e18ccb6d636eba55edfbd0d6a80a`. The bounded inventory is accepted as an accurate factual inventory. |
| 2 | Informational | The report's "Substantive recorded assertions" column is a human paraphrase, not a verbatim transcript of the recorded `checks[].description` values. The underlying declarative assertions are all present (verified 56/56); only the column's wording is summarised. Any downstream reader should rely on the records, not the paraphrase. |
| 3 | Informational | The report's phrase "exact record hashes" is accurate for the archives (both SHA-256 digests re-derived from raw bytes) but the retained official metadata JSON itself was not re-fetched from GitHub in this review; the correspondence between the retained bytes and GitHub's *current* artifact digest is only as strong as the retained metadata. The retained metadata is internally consistent with the bytes and with the coordinator input's own artifact listing. |
| 4 | Informational | This review cannot extend the freshness result: the 56 records remain non-ancestral, hence stale/unknown under `tools/validate/ledger.py`. The covered-path equivalence is real evidence for a coordinator-owned admission decision but is not itself an admission. No freshness waiver, source relabel, history manipulation or canonical adoption is proposed or implied here. |

No defect was found that requires the author to change anything. Nothing in this
review qualifies a feature, closes a finding, admits evidence, clears privacy,
approves a screenshot, or accepts `source11f`. The original Tron owner
approvals stay closed.

## Limits of this review

- **Bounded inventory/metadata review only.** No source or privacy code-review
  qualification is claimed or inferred; no implementation correctness opinion is
  offered on the hub, clients, scenarios or evidence tooling.
- Static inspection of real execution records and the exact candidate source.
  **No scenario, test or validation campaign was re-executed**, and the check
  predicates themselves were not independently re-evaluated beyond confirming
  that each declarative expectation is recorded and passing.
- **No** ledger generation, canonical validator run, manifest/lockfile change,
  push, merge, tag, cleanup, deployment or release was performed or is claimed.
- **No** network re-download of artefacts or metadata; **no** artifact script was
  executed; **no** archive member was written outside the reviewer's own
  ignored build subtree; **no** secret-bearing value was read or printed.
- **No** visual approval of any screenshot, **no** physical-Flic, physical-Remote
  or HIL attribution, **no** 72-hour soak, **no** week field sign-off, **no**
  final version/artifact release gate.
- **No** feature qualification or canonical adoption. The coordinator owns
  preservation, release, publication and any eventual canonical admission.
- The four Flic units, the F-API-034 negative-path assertion, the unintegrated
  redaction implementation and its own qualified review, the physical-HIL,
  field, 72-hour soak and final version/artifact release gates, and the
  `source11f` source/privacy qualification all remain open. The original three
  Tron owner approvals are closed and stay closed; this review does not reopen
  or extend them.

## Commands, checks and exits

| Invocation / check | Exit / result |
| --- | --- |
| `git rev-parse HEAD`, `git status --porcelain`, `git branch --show-current` | 0; HEAD exactly `9036ecffe2b5e18ccb6d636eba55edfbd0d6a80a`, branch `ryan-haver/wp-ci-proof-review`, working tree clean |
| `orca orchestration check --terminal … --json` (inbox) at three checkpoints | 0; `count: 0` each time, run `run_37205f6095b3`, dispatch `ctx_3d5cba0330a2` |
| `sha256`/`testzip()`/member-name screen over both retained ZIPs | 0; digests, member counts, `testzip() is None`, 0 unsafe names |
| Record parse of 1,532 `evidence/**.json` members from both ZIPs | 0; counts, tallies, attribution as tabulated above |
| `git archive --format=tar bdcf06dc… tools tests/validation docs/api` into the reviewer's own build subtree | 0; 142 members, 1,354,337 bytes; no ref, index or worktree touched |
| Import of the scenario packages and `tools.validate.model` from that export | 0; 8 primary + 24 further scenario modules imported (one further module, `api_documentation`, failed to import and is not needed for any reviewed unit), 1,480 scenarios loaded |
| `Expectation.describe()` vs recorded `checks[].description`, 56 records | 0 problems; 56/56 complete, 56/56 features, 56/56 covers, 56/56 zero cover/path intersection |
| `git cat-file`/`merge-base --is-ancestor`/`rev-parse …^{tree}`/`diff --name-only`/`log -1 --format=%H %T %P` via fixed argv | 0, except `merge-base --is-ancestor bdcf06dc… 490a879b…` = **1** (intentionally reported: not an ancestor) and the same against `9036ecff…` = 1 |
| Report table parse and cell-by-cell comparison (60 rows + 38 rows) | 0; zero mismatches in both tables |
| `features.yaml` at `490a879b…` parsed and compared for 38 feature rows | 0; 38/38 `target`/`current` identical |
| PNG signature/IHDR/chunk-CRC and ZIP-CRC check over the 7 matched browser screenshots | 0; 7/7 present, 1440×900, all chunk CRCs valid, all ZIP CRCs valid |
| Reviewer's first `scenario_crosscheck.py` attempt | **exit 1** — `TypeError: tuple expected at most 1 argument, got 3` from an unused `tuple(...)` call. Preserved verbatim at `build/software-waves/SW-AUDIT-01-ci-review/probe-01/attempt-01-failed.stderr.txt`; corrected in `attempt-02-run.txt` |
| Reviewer's first `report_crosscheck.py` attempt | **exit 1** — `AttributeError: 'NoneType' object has no attribute 'group'` from reading the wrong feature-table column index. Preserved verbatim at `…/probe-01/attempt-03-failed.stderr.txt`; corrected in `attempt-04-run.txt` |
| Reviewer's first screenshot path resolution | probe defect, not an artefact defect: record `observations.screenshots` paths are relative to the record's own archive folder, so the first pass resolved them against the wrong prefix and reported them absent. Preserved at `…/probe-01/attempt-03-run.txt`; corrected in `attempt-05-run.txt` with the `evidence/<Folder>/` prefix, after which 7/7 resolve |
| Report UTF-8, local-link and scope checks; CR-aware `git diff --check` | Run before this report's commit; final receipt retained privately under the reviewer's build subtree |

All reviewer diagnostics are confined to
`build/software-waves/SW-AUDIT-01-ci-review/` in this worktree. Every failed
attempt was preserved under its own numbered filename; no historical byte was
overwritten. The immutable intake artefacts, the source tree, tests, scenarios,
schemas, the registry, canonical records, findings, the ledger, manifests and
lockfiles are unchanged.

The only tracked deliverable of this review is this new report. The
repository's configured `core.hooksPath` (`…/.githooks`) installs a `pre-commit`
hook that runs `ruff check` plus the fast `pytest tests/` suite. This dispatch
authorises no test campaign, so the hook was deliberately **not** invoked; the
commit instead uses the documented **invocation-only** exception
`git -c core.hooksPath= commit`, which changes no hook configuration and leaves
the configured path untouched. The actual checks performed instead are the
UTF-8 decode, the local-link resolution, the scope screen and the CR-aware
`git diff --check` recorded above. No source-hook and no full-suite pass is
claimed. The coordinator owns independent report acceptance, preservation,
publication and worker release.
