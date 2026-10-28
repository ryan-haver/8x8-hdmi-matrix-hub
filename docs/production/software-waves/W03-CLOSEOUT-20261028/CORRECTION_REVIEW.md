# W03 F-01 encoding correction — focused re-review

**Reviewed final fix (exact):** `d6e78e0b6ab1dab5216443584d810a7a24af32b2` (parent `6228b273df5822b63b6d516121ab9a3f169f598e`) · **Original metadata candidate:** `78ce344800a9d1b3088bb8e886f65e2c8dfa0918` · **Original assigned base:** `28fce729ca4ea08bfc2f19805b36e13ae8c184f2`.
**Prior review (immutable, settled/released, not re-authored here):** `29c217ae25856f91d79a85064eb7e38a6aa197a0` → `docs/production/software-waves/W03-CLOSEOUT-20261028/REVIEW.md`, HOLD on F-01 only.
**Author of the fix:** coordinator/metadata author, OpenAI family. **Reviewer:** native `minimax-coding-plan` / `MiniMax-M3` / `thinking` through audited worktree-only opencode2 routing; CLI model/effort null (no override), no Anthropic, helper, plugin, MCP, subagent or fallback route, no new spending. Different underlying family from the author.
**Scope:** the 14-sequence metadata encoding correction only. **Report only** — no source, test, tooling, registry, ledger, finding, manifest, evidence or root byte was edited; the only file added by this review is this report.
**Worktree:** `.../w03-metadata-encoding-review`, branch `ryan-haver/w03-metadata-encoding-review`, HEAD `d6e78e0b`, clean at start. Scratch: own ignored `build/fanout-readiness-20261028/encoding-review/`.

This is a normal author-fix / re-review of one qualified, concrete finding. It is **not** an automatic failed-model-qualification retry, **not** a new development phase, and **not** a re-review of source code. The prior review's raw evidence comparisons (76/76 byte-identical originals, 44/44 schema-valid, 32/32 LFS, ledger attribution) remain attributed to `29c217ae`; they are not re-executed, relabelled or reclaimed here.

## 1. Commands actually run, with exits

Interpreter: existing root virtualenv `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe` (3.12.10), read-only. Process-local `PYTHONPATH` = this worktree root + `src`; isolated `MATRIX_DATA_DIR`/`UC_CONFIG_HOME` and pytest `--basetemp` under this reviewer's own ignored build dir. No root/private runtime data or config read or written.

| # | Command | Exit | Result |
| --- | --- | ---: | --- |
| 1 | `git diff --name-status 6228b273 d6e78e0b` | 0 | **1 path**: `M docs/validation/features.yaml` |
| 2 | `git cat-file blob` byte census + `bytes.replace(BAD, GOOD)` proof (§2) | 0 | 14 replacements; parent-with-substitution **==** fix byte-for-byte |
| 3 | `git diff 6228b273 d6e78e0b -- docs/validation/features.yaml` | 0 | 14 changed lines (3 header comments + 11 `claim:` rows) |
| 4 | YAML parse of base / original / fix `features.yaml`; per-feature field diff | 0 | 268 rows; **7** changed rows vs base, exactly the authorized set (§3) |
| 5 | `git ls-tree -r 78ce3448 -- docs/validation` vs `d6e78e0b` | 0 | 2611 entries each; **1** differing blob (§4) |
| 6 | `git diff --numstat 78ce3448 6228b273` | 0 | 4 new files under `docs/planning/`, 100 insertions / 0 deletions; no non-`docs/` path (§5) |
| 7 | `git show --no-patch d6e78e0b` | 0 | single commit, "restore section-sign encoding in feature claims" |
| 8 | `pytest tests/validation/test_registry.py tests/validation/test_evidence_schema.py tests/validation/test_ledger.py -q -p no:tests.route_inventory` | **0** | **42 passed** (8.20 s) |
| 9 | `python -m tools.validate check` | — | **deliberately not completed**: the large committed-evidence scan this bounded task excludes; abandoned at the 120 s tool limit, terminated, **not counted as a pass or a failure** |

No test was created or modified; no ledger was regenerated (§6). No background job of this reviewer survived: a post-run sweep for `python.exe` found no `tools.validate`/`pytest` process of mine, only the shared runtime's own MCP servers, which were not touched.

## 2. F-01 disposition — measured on the actual Git bytes

`BAD` = UTF8(U+00C2 U+00A7) = `C3 82 C2 A7` (4 bytes, double-encoded form); `GOOD` = UTF8(U+00A7) = `C2 A7` (2 bytes).

| Blob | bytes | `BAD` | `GOOD` | U+00C2 | U+FFFD |
| --- | ---: | ---: | ---: | ---: | ---: |
| base `28fce729` | 521 658 | 0 | 14 | 0 | 0 |
| original `78ce3448` | 529 478 | **14** | 14 | **14** | 0 |
| parent `6228b273` | 529 478 | **14** | 14 | **14** | 0 |
| **fix `d6e78e0b`** | 529 450 | **0** | 14 | **0** | 0 |

**Decisive test:** `parent_bytes.replace(BAD, GOOD) == fix_bytes` → **True**. The fix is therefore *exactly* the parent's bytes with **14** `BAD`→`GOOD` substitutions and **no other byte changed** (length delta 28 = 14 × 2 bytes). Line level: 8 156 lines both sides, **14** changed lines, each with exactly one `BAD` and one `GOOD` and equal after substitution — no line added, removed or reordered; LF endings throughout (0 CRLF), trailing newline present.

**The 14 repaired sites** are exactly those F-01 named: header comments `VALIDATION_PLAN.md §3`, `VALIDATION_PLAN §2`, `REMEDIATION_PLAN.md §4`, and the `claim:` values of `F-UC-008`, `F-UC-009`, `F-UC-011`, `F-UC-012`, `F-UC-013`, `F-UC-014`, `F-UC-016`, `F-REL-005`, `F-REL-009`, `F-REL-015`, `F-REL-018`. The fixed file's non-ASCII inventory is now **exactly** `{U+00A7 SECTION SIGN ×14}` — identical to the base, with **0** U+00C2 and **0** U+FFFD.

**F-01 is resolved on the exact bytes. Nothing else in the candidate changed.**

## 3. Registry comparison — final `d6e78e0b` vs original assigned base `28fce729`

268 features before and after; identical id set and order. **Exactly 7 rows** have any changed field, each matching the authorized field set exactly: `F-API-002` [`basis`,`evidence`] · `F-API-031` [`basis`,`current`,`evidence`] · `F-API-033` [`evidence`,`findings`] · `F-API-034` [`findings`] · `F-SEC-007` [`basis`,`evidence`] · `F-SEC-014` [`findings`] · `F-REL-009` [`evidence`,`findings`].

- `claim` changed on **0** rows vs base (11 rows vs the original candidate — precisely the F-01 set, now fully restored).
- `target` changed on **0** rows vs base.
- `current` changed on **1** row only: `F-API-031` **V1 → V2**, target V2. `F-SEC-007` stays V3 (target V3); `F-API-002` stays V2 (target V2); `F-API-033`/`F-API-034`/`F-REL-009` keep their targets and levels.
- Evidence deltas are additions only into the imported W03 namespace (`F-API-002` +3, `F-API-031` +26 = 13 original-CORS + 13 combined, `F-API-033` +1, `F-REL-009` +1, `F-SEC-007` +14); findings deltas are `VAL-14` on `F-API-033`/`F-API-034`/`F-REL-009` and `VAL-15` on `F-SEC-014`. No evidence path removed, no finding re-scored, no level lowered, no target lowered, no assertion weakening, no cap waiver, no owner gate or baseline change.

## 4. Canonical subtree — `78ce3448` vs `d6e78e0b` (all Git blobs)

`docs/validation` holds **2 611** entries in both trees with identical path sets. **1** blob differs. Identical blob SHA counts: evidence JSON 2 224/2 224 · evidence PNG 145/145 · W03-CLOSEOUT imported namespace 76/76 (44 JSON + 32 PNG) · import manifest 1/1 · `LEDGER.md` 1/1 · `findings_pending.yaml` 1/1 · `W03_EVIDENCE_ASSEMBLY.md` 1/1 · `evidence.schema.json` 1/1 · `features.yaml` 0/1 (**the repair**). All 32 W03 PNG blobs remain git-LFS pointers at `d6e78e0b` (0 non-pointers); all 44 W03 JSON records still parse as UTF-8 JSON at the fix (0 failures). The manifest, ledger, findings register, assembly packet, schema and every evidence byte are **identical** to the reviewed original.

## 5. Intervening commit `6228b273` — scope

`git diff --numstat 78ce3448 6228b273` → **4 files, 100 insertions, 0 deletions**, all new and all under `docs/planning/`: `software-waves/READY_QUEUE_20261028.md` and `software-waves/next-wave/{SW-API-READ-03-INTAKE,SW-AUDIT-01-FRESHNESS-DELTA,SW-SEC-DATA-02-C1}.txt`. **No** `src/`, `tools/`, `tests/`, `web/`, `custom_components/`, root-manifest or lockfile path changed; **no** non-`docs/` path changed at all; no existing file was modified or deleted. The commit is pure next-wave planning briefs with no metadata, evidence, ledger, findings or manifest content.

## 6. Why no ledger regeneration was required

`tools/validate/ledger.py` consumes the registry's `title` only; it never reads `claim` or `basis`. The repair changes **only** `claim` strings, so the committed `docs/validation/LEDGER.md` remains the correct output for the fixed registry and is byte-identical to the reviewed original. `tools/validate/registry.py` validates `claim` only as a non-empty string, so the restored text satisfies the same checks. Ledger generation and registry checks were never run concurrently; **no** ledger generation was run by this review.

## 7. Checks run at the fix — results

- `pytest tests/validation/test_registry.py tests/validation/test_evidence_schema.py tests/validation/test_ledger.py -q -p no:tests.route_inventory` → exit **0**, **42 passed**, 0 failed, 0 skipped (no test created or edited).
- Independent byte proof, YAML registry diff, `git ls-tree` subtree identity and `git diff --numstat` scope checks → exit **0**, results as tabulated above.

## 8. Honest limits

- **`python -m tools.validate check` was not completed.** It is the large committed-evidence scan this bounded task excludes; abandoned at the tool timeout and claimed as neither a pass nor a failure. The 42 metadata tests plus the byte/registry/blob proofs are the checks actually run.
- The **4 084-test core suite, 100 Remote tests, Ruff, mypy, route coverage, current-head CI, image and broader-client gates were not re-run.** The reviewed range contains zero source, test, tooling, UI, root-manifest or lockfile bytes, so those results retain their original attribution and date.
- The **31-outcome campaign was not re-executed** and the **original evidence trees were not re-scanned**; the imported bytes were verified identical to the reviewed original by Git blob SHA (76/76), and the byte-for-byte comparison against the read-only delivery roots stays attributed to `29c217ae`.
- The **underlying CORS / offline-routing source behaviour was not re-reviewed**; those blobs are unchanged and remain attributable to their prior independent reviews.
- This report is **not** a core or security source-review qualification, **not** an image/browser/UI/hardware/soak/field qualification, **not** a CI or publication pre-approval, and **not** a release approval.
- The three **Tron paused-frame owner approvals closed by the owner on 2026-10-20** are historical, unchanged, and not re-granted, extended or treated as release approval. Physical HIL, deployment-host 72-hour soak, week owner field use and final version/artifact release acceptance all remain **open**.
- The coordinator's ledger/production quota observations (Orca version, fleet census, provider usage) were **not** independently attested here; only the Git/Run references named in this report were checked.
- The integration branch has since advanced to `7a3e8d965da3b253dfc091e429b0bde2731acc2a` (merge of `d6e78e0b` with `29c217ae`). Verified: the `docs/validation` subtree at `7a3e8d96` is **byte-identical** to `d6e78e0b` (2 611 entries, 0 differing blobs), and the original `REVIEW.md` blob is preserved unchanged (`e460b26a2995d98438156ca1153440f059554292`). This review remains anchored at `d6e78e0b`.

## 9. Disposition

**ACCEPT — the F-01 correction at exact `d6e78e0b6ab1dab5216443584d810a7a24af32b2`.**

Independently proven from actual Git bytes: (1) the parent→fix diff is **exactly one path** (`docs/validation/features.yaml`) and **exactly 14** byte-sequence replacements UTF8(U+00C2 U+00A7) → UTF8(U+00A7) with **no other byte changed** (`parent.replace(BAD, GOOD) == fix`, byte-for-byte; 14 changed lines; 0 U+00C2 and 0 U+FFFD remaining); (2) parsed registry vs the original assigned base `28fce729` shows **7** changed rows with exactly the authorized fields, **0** claim changes, **0** target changes, and exactly one level advance `F-API-031` V1 → V2; (3) the `docs/validation` subtree vs the reviewed original `78ce3448` has **2 610 of 2 611** blobs identical — all evidence JSON, all evidence PNG (32 W03 PNGs still LFS pointers), import manifest, `LEDGER.md`, `findings_pending.yaml`, `W03_EVIDENCE_ASSEMBLY.md` and the schema — with only the repaired `features.yaml` differing; (4) the intervening `6228b273` is pure new planning briefs with no `src/`, `tools/`, `tests/`, UI, root-manifest or lockfile byte involved; (5) existing metadata tests re-run read-only: **42 passed**, exit **0**, no test created.

This is a normal author-fix / re-review disposition for the single qualified concrete finding F-01 raised at `78ce3448`. **Reviewers report; the coordinator authors.** All other acceptance elements recorded in `29c217ae` — original bytes, schema, source equivalence, ledger honesty, formal checks and all stated limits — keep their original attribution and are neither re-attributed nor re-verified here. This disposition is bounded to the W03 metadata correction at `d6e78e0b`; it is not a new core/security qualification, and it does not approve any CI, image, hardware, soak, field or release gate.

**Report-only commit** with a documented invocation-only `core.hooksPath=` exception (`git -c core.hooksPath= commit`), after the real checks in §1 and §7. The persistent hook configuration was **not** modified and no implementation hook was bypassed: the configured pre-commit hook runs `ruff` plus the full core pytest suite, and this commit's diff contains no source, test, tooling, registry, ledger, finding, manifest or evidence byte, while the task declines to re-run the 4 084-test core and 100-test Remote suites.
