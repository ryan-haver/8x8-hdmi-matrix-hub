# Round 1 independent assessment — Anthropic

- Author route: native Claude Code `claude-opus-4-7` effort `high` (planning only; no source/security review qualification claimed).
- Dispatch: task `task_7cd1706e862c`, context `ctx_369b591f37ba`, Run `run_37205f6095b3`, coordinator `term_15310037-f316-4fe8-9bbd-012f4e5ce38f` gen4.
- Worktree: `wp-pins-anthropic-20261101`. HEAD verified clean at `19ee8be994eb2d4630aead8a7eec8f6a22140224`.
- Planning floor (per packet): `e2161484459da65aee14433136a14963507b499c`.
- Scope: independent Round 1 assessment of the program direction and every prospective phase (P0 residual, P1 remainder, P2, P3, P4, P5) plus the 7 owner gates. No source, test, tooling, registry, ledger, or canonical pin edits. Peer Round 1 reports under this directory were deliberately not opened.
- Status: INDEPENDENT; **no consensus or final approval claimed**.

## Input integrity (material)

Content hashes of the frozen sibling files (via `git cat-file -p HEAD:<path>`, confirmed equal to on-disk UTF-8 bytes):

| File | Observed sha256 | Hash recorded in `DRAFT_PACKET.json.inputs` |
| --- | --- | --- |
| `DRAFT_EXECUTION_PINS.json` | `17bdf32dccde46a69973bb90b9d0c770480b4bf32367d0fb85c9a94e858cc2f5` | `73bddf6b396858618660d4aede9994e3da2aa817391d8308fae9980321c53604` |
| `PROGRAM.md` | `0e92683a1eeda28f655200324105da67269f94f0715fa5824a905c32c0d8791d` | `39de9d9e0fe2ed5a3c94a4acf64018a52a612579181677d92258ad6e27f96419` |
| `BASELINE.json` | `72d1aa31615cc4b2054fc5d9716703fb0ba5c81cd92b0d1418ceba2bac5dc5f9` | `e59faf7ed8790afa6ad1a4b2126e2d74a0b3593113965142128ad74bae88a563` |

All three recorded hashes diverge from the committed bytes. The three sibling files were introduced together in `19ee8be9` and the on-disk sha256 agrees with the git blob (no CRLF/BOM explanation). **Material requirement M-1**: before Round 3 the coordinator must regenerate `DRAFT_PACKET.inputs` from the frozen bytes or publish the exact hashing recipe used, so reviewers can reproduce it. Round 1 opinions should not be treated as attached to the current `DRAFT_PACKET.json` until reconciled.

## Program direction

The packet lands the owner's 2026-11-01 direction honestly: Anthropic/Gemini/Codex/MiniMax are allowed, DeepSeek is excluded with `dispatch_allowed: false` and no author/reviewer/fallback slot references it (verified across 84 rows). Gemini is held with `dispatch_allowed: false` and appears only as text in 60 fallback descriptors, never as a routed slot — correct posture given no verified Antigravity CLI. Every `base_pin` is `{kind: accepted_integration_after_dependencies, fixed_sha: null, requires_ancestor_floor: true}`: no future SHA is fabricated and no stale checkout is implied (matches invariant [5]). Three-family three-round schedule carries `status: not_yet_executed` and `coordinator_not_counted: true`. Historical attributions and the three closed Tron approvals are preserved by omission.

**M-2**: the `authority` line reads "entire mapped scope pinned for execution" while `capacity_commitment` and invariant [2] cap concurrency at coordinator + 2 workers + 1 external. Pinning is not funding; the authority sentence should state the matrix is a reservation, not a commitment to launch all 65 units.

## Overall staffing decision

Verified structural checks across 84 rows:

- Author × reviewer family: 0 same-family pairs. Distribution: `sol→claude` 62, `astra→claude` 11, `m3→sol` 7, `claude→sol` 4.
- Exclusive-writable paths: 0 collisions; 84 unique author worktree paths and 84 unique reviewer paths; no path reuse across rows or inside a row.
- `dispatch_state` is `not_launched` and `task_id`/`dispatch_id` are null on every row. No fabricated Orca IDs.

Concern: **Claude is reviewer on 73 of 84 rows (87%)**. QUAL-ANTHROPIC-CORE-01 appears in `dependencies` on only 3 rows (the Claude-authored RV-*), and on none of the 73 Claude-reviewed implementation units. The capacity_gate text names "task-qualified different-family reviewer" on 19 rows and generic 30% pool language on the other 65 — never the qualification artifact. **M-3**: either add `QUAL-ANTHROPIC-CORE-01` to `dependencies` of every row whose `reviewer_route == "claude"`, or tighten `capacity_gate` on those 73 rows to require it accepted before the wave fires. The invariant is otherwise honoured in prose, not at the scheduler.

**M-4**: Claude-as-reviewer is a single-point correction-capacity bottleneck. If QUAL-ANTHROPIC-CORE-01 is declined, 73 rows need rerouting and only Sol is a verified cross-family reviewer able to absorb them. The packet should document a Sol-reviewer fallback for a sampled subset or state explicitly that the program is held on the qualification result.

Staffing recommendation (independent): hold the matrix as **reservations**; dispatch only Wave 0–2 after M-1 and M-3 land. Reserve Sol correction capacity. Do not count Anthropic as verified source-review family in Round 2 until QUAL-ANTHROPIC-CORE-01 is accepted.

## P0 residual (3 rows, waves 0–1)

| id | author | reviewer | wave |
| --- | --- | --- | --- |
| SW-AUDIT-01 | m3 | sol | 0 |
| SW-FINDINGS-01 | m3 | sol | 0 |
| SW-HARNESS-01 | sol | claude | 1 |

Coverage matches PROGRAM.md P0 scope. m3 demand_class "bounded metadata/prose" matches audit/findings. SW-HARNESS-01 as the single wave-1 Sol unit cleanly fans out wave 2. Reviewer=claude on SW-HARNESS-01 is source review and inherits M-3.

**P0 material**: none beyond M-3. **Optional**: cross-link `canonical_below_target=210` and `canonical_stale=96` from BASELINE.json into SW-AUDIT-01 acceptance for arithmetic closure.

## P1 remainder (29 rows)

Coverage: 20 mapped units (API/sec/client/profile), the three RV-* re-reviews of retained candidates, 6 EV-* evidence followups, the P1 integration/evidence/publish trio, and QUAL-ANTHROPIC-CORE-01. Dependencies chain correctly: `RV-* → INTEGRATE-P1-CANDIDATES → EV-COMBINED-P1 → P1-PUBLISH-CHECKPOINT`. EV-API034-SECURITY-REFRESH names FSEC007 and prohibits non-ancestor WS proof reuse — matches the frozen SHAs in `BASELINE.current_review_candidates`.

**P1 material**:
- **M-5**: the 12 follow-up/review rows carry `review_independence: null`, `prohibited: null`, `demand_class: null`. For rows that produce new source or evidence (EV-API034-SECURITY-REFRESH, EV-PRIVACY-ADMISSION, EV-FLIC-ADMISSION, EV-COMBINED-P1, INTEGRATE-P1-CANDIDATES, QUAL-ANTHROPIC-CORE-01), populate these fields to match the 65 mapped units.
- **M-6**: clarify QUAL-ANTHROPIC-CORE-01 acceptance to distinguish evaluation (Claude performs frozen candidate task) from judgement (Sol evaluates against the rubric; coordinator holds disposition). Current wording reads as if the review itself were being qualified.

**P1 optional**: wave 2 has 7 rows all `sol→claude`; within the 2-worker ceiling that is ≥4 serial sub-waves. Note "suggested_wave" is a label, not a concurrent batch.

## P2 (18 rows)

All 18 are `sol→claude` across waves 4–9: scenes/macros/shortcuts/presets, UI control/manage/present, kiosk control/state, Flic. No cross-row conflicts. Waves 7, 8, 9 each exceed the active-worker ceiling (sub-batching implicit). **Material**: none above M-3. **Optional**: identify in acceptance which UI rows touch the owner-protected glass/Tron baselines so review preserves the "no new visual decision without owner" rule.

## P3 (22 rows)

Protocol/runtime/UC/HA preparation plus SW-DOM-HIL-PREP and SW-SOAK-PREP. Authors: sol 11, astra 10, m3 1 — all different-family under claude or sol review. **Wave 10 holds 14 of 22 rows**, the largest in the matrix. **O-1**: split wave 10 into 10a/10b/10c with explicit ordering or document that the wave number is a label. **O-2**: SW-DOM-HIL-PREP deps are SW-DOM-SCENE, SW-DOM-MACRO, SW-PROTOCOL-PREP; confirm SW-DOM-SHORTCUT is intentionally omitted (shortcuts share HIL surfaces).

## P4 (4 rows, waves 13–14)

- SW-REPO-01 (m3→sol, wave 13): deps only on SW-FINDINGS. Repository reconciliation that lands version metadata should transitively require everything merged. **M-7**: add explicit roll-up deps (as SW-VERSION-01 does) or document in `scope` that SW-REPO is reconciliation of ignored/dot-files only and does not gate on sources.
- SW-DOCS-01 (astra→claude, wave 13): deps cover P3 but **omit P1 writes (SW-API-WRITE, SW-SEC-DATA) and P2 UI base**. **M-8**: add missing package deps or document the intentional exclusion.
- SW-VERSION-01 (sol→claude, wave 14): 24-package roll-up. OK.
- SW-BUILD-01 (m3→sol, wave 14): deps SW-VERSION. OK.

## P5 (1 row, wave 15)

SW-SOFTWARE-GATE-01 (sol→claude). Through SW-BUILD→SW-VERSION the transitive closure covers P1–P3; through SW-REPO it only reaches SW-FINDINGS (M-7). Acceptance matches PROGRAM.md. **Material**: inherits M-7/M-8. **Optional**: enumerate the exact validation modules the gate will run.

## Owner gates (7 rows)

OWNER-HIL-B, OWNER-PHYSICAL-CEC, OWNER-HIL-C, OWNER-HIL-E, OWNER-SOAK-72H, OWNER-FIELD-WEEK, OWNER-FINAL-RELEASE — correct count and scope. All seven carry `author: sol, reviewer: claude`, which reads as a developer dispatch. These are owner-authority gates. **M-9**: null out `author_route`/`reviewer_route` and introduce `owner_witness`, or set `dispatch_allowed: false` with a scope note that the model fields are attestation witnesses, not dispatch targets. As stated, a scheduler could try to dispatch an owner gate.

## Row/field corrections (concrete)

| id | field | current | correction |
| --- | --- | --- | --- |
| 73 Claude-reviewed rows | `dependencies` or `capacity_gate` | no mention of QUAL-ANTHROPIC-CORE-01 | add dep or gate token (M-3) |
| 12 follow-up/review rows | `review_independence`, `prohibited`, `demand_class` | null | populate as per 65 mapped units (M-5) |
| QUAL-ANTHROPIC-CORE-01 | `acceptance` | ambiguous author/reviewer roles | clarify evaluate-vs-judge split (M-6) |
| SW-REPO-01 | `dependencies` | SW-FINDINGS only | add roll-up or scope note (M-7) |
| SW-DOCS-01 | `dependencies` | missing P1 writes & P2 UI | add or document (M-8) |
| 7 OWNER rows | `author_route`, `reviewer_route` | sol / claude | mark non-dispatch (M-9) |
| `DRAFT_PACKET.inputs` | three sha256s | diverge from committed bytes | regenerate or publish recipe (M-1) |
| `authority` | prose | "entire mapped scope pinned for execution" | add "reservation, not funding" (M-2) |

## Material requirements vs optional improvements

**Material (must land before Round 3 consensus):** M-1 packet-hash reconciliation, M-2 authority wording, M-3 qualification gate per row or capacity_gate, M-4 Claude-reviewer bottleneck fallback audit, M-5 null control fields on 12 follow-up/review rows, M-6 QUAL acceptance clarification, M-7 SW-REPO deps, M-8 SW-DOCS deps, M-9 OWNER rows marked non-dispatch.

**Optional improvements:** O-1 wave 10 sub-batching, O-2 SW-DOM-HIL-PREP dependency check, SW-AUDIT-01 arithmetic cross-link, P2 UI baseline sensitivity note, P5 pipeline enumeration.

## Statements I am not making

I do not claim consensus, final approval, or that Anthropic may author or source-review any package before QUAL-ANTHROPIC-CORE-01 is accepted. I did not read peer Round 1 reports. The private subtree `build/execution-pinning-20261101/anthropic/round1/` is reserved and will not hold private evidence bodies, credentials or original native transcripts.
