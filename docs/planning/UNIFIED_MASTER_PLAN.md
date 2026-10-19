# Unified master plan

This is the current coordination entry point. The earlier execution record is
in [the phased roadmap](../../orca-phased-roadmap.md). Finding IDs and acceptance
criteria come from [the remediation plan](../REMEDIATION_PLAN.md) and
[the validation plan](../validation/VALIDATION_PLAN.md).

## Next development and model policy (2026-10-18)

The [runtime-completion plan](NEXT_DEVELOPMENT_PHASES.md) now defines R0–R8,
their worktrees, model assignments, dependencies, file ownership and acceptance
gates. The [model/agent inventory](MODEL_AND_AGENT_INVENTORY.md) distinguishes
project-proven routes, configured/catalog models and unverified access.

The owner excludes **all Claude/Anthropic models** from these next phases,
including reviews, helper agents and fallbacks. This supersedes the historical
mandatory six-model roster; it does not rewrite who completed earlier work.
Sol 6.1 high coordinates and implements core wiring, Argon owns UC integration,
Flash owns focused integration/client work, M3 owns persistence if quota and
effective-model checks pass, Luna handles bounded guides/evidence indexing,
and Astra handles contract design and independent review. M3.1/DeepSeek are
conditional alternatives, not assumed successful launches.

Runtime implementation and corrective tracks through R3E's UI ordering fix and
R1F's CEC enable-cache correction are merged and their worktrees removed. At clean
`4adbc13`, the full local core passed 3,966 tests with four skips and 177/177 routes;
dedicated Remote 100, source client outcomes 1,506, actual HA 19 per pinned version,
and image client outcomes 193 all passed. Both architectures built and matched
257 shipped files; deployment/arm64 checks, 59 browser flows, four Swagger cases
and the formal combined evidence gate passed. The current
[runtime report](../validation/RUNTIME_VALIDATION_REPORT.md) retains actual
commits/image IDs and prior failed runs. Historical Phase 6/7 results below remain
tied to their earlier candidate. R7 Luna's final guides/index are merged after
413 independent tests and 214 local links passed. Completed Astra R8 review
found two high availability defects in actual source and the normal image:
legacy-scene migration plus v2 creation breaks restart, and transient failed
reconfigure rollback abandons automatic reconnect. R2D/R1G corrections are now
merged, and the R8B follow-up passes all six original source/image cases. It
accepts the scene-restart fix within scope but reproduces reconnect loss when
rollback exceeds its cleanup deadline. R1H's deadline correction is merged;
fresh Astra R8C passes all eight known source/image cases on `dd184725` and its
new immutable image. R8C also reproduces a source-only failure when cancellation
or expiry interrupts candidate cleanup before original identity restoration.
Fresh Sol 6.1 high R1I owns complete bounded rollback restoration, including
early drain, late closure, shutdown and overlapping reconfiguration. Its initial
focused checks pass; final exact-commit acceptance and fresh Astra R8D review
remain pending. The candidate stays held pending that review and new complete
candidate evidence. Historical `4adbc13` CI passes 12/13 required jobs,
with only the three owner-pending Tron screenshots failing. No visual/hardware
approval or release tag is implied. The
[execution record](RUNTIME_EXECUTION.md) tracks effective model observations,
ownership clarifications and acceptance. Hardware and soak gates remain
owner-observed.

## Release sequence

1. Phases 0–4 are merged into `main`; `v0.4.0` points to `25233bb`.
2. Phase 5 is on [PR #36](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/pull/36).
   Commit `1aab559` corrects browser assertions for stacked overlays and limits
   the PIN latency test to its verification window. Local validation passed:
   Ruff, 2,793 Python tests, 175/175 REST routes, and 59 browser smoke/flow tests.
   CI run `39083178584`: 1,098 UI tests passed, 33 skipped, three snapshots failed.
   Five modal differences were the corrected deployment port; their fixture now
   asserts the live origin before normalizing capture text. Three Tron snapshots
   retain small temporal changes from the 30-fps cap and await owner approval
   in `build/phase5-visual-review/index.html`. No baselines were changed.
   Merge only after all applicable CI checks pass, then tag `v0.5.0` on the merge
   commit and merge `main` into the release integration branch.
3. All six Phase 6/7 tracks are integrated on `wp-g1-g2-release-and-docs`.
   [Draft PR #37](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/pull/37) is open.
   Commit `d04fcd5` passed 3,329 tests, four skips and 177/177 routes; `ec850d2`
   adds the validated Phase 5 capture fixtures. Harness-only `f55660e` passed 86
   validation tests plus requirements-only Linux discovery. Metadata is
   `1.0.0rc1`, mapped to Git tag `v1.0.0-rc1`. Merge/tag only after PR #36 and
   all applicable CI gates pass.
4. Run Phase 8 against the candidate and publish the validation report. Tag
   `v1.0.0` only when the final gates below have evidence.

## Phases 6–7 ownership

| Track | Requested model | Scope | State |
| --- | --- | --- | --- |
| `wp-g1-packaging-version-locks` | Sol 6.1 high | Packaging, canonical version, validated bump script with rollback, hashed locks | Merged `14477d5`, worktree removed. Coordinator added RC version/notice coverage: 22 packaging tests passed, including coexistence with an editable install. |
| `wp-g1-ci-multiarch-hygiene` | Opus 5.5 high | Docker context, Git guard, pinned build dependencies, Dependabot, multiarch | Merged `de6693f`, worktree removed; coordinator reran 61 non-Docker tests. Worker also proved amd64/arm64 publication in a disposable local registry and arm64 health under QEMU. |
| `wp-g2-openapi-swagger-config-docs` | Argon high | OpenAPI/Swagger routes, API/config reference, registry and ledger | Merged `5366eff`, worktree removed; 172 coordinator tests passed, followed by corrected response/auth metadata and four passing read-only contract scenarios. |
| `wp-g1-license-asset-audit` | Flash 3.8 high | Notices, original replacement device SVGs, protocol reference | Merged `f0a1641`, worktree removed. Coordinator expanded inventory to 17 locked packages, checked SVG rendering/reproduction and retained upstream notices. |
| `wp-g2-readme-architecture-changelog` | MiniMax M3 | README, architecture, integrations, changelog, roadmap, docs index | Merged review correction `1b65297`, worktree removed; 87 coordinator documentation/security tests passed. Coordinator refreshed RC/version text and archive links. |
| `wp-g2-client-guides-doc-archive` | MiniMax M3.1 | HA, Docker, Flic, UC, contributing guides | Merged `c4524ed`, worktree removed; coordinator tests: 310 passed after review corrections. Installed session reported M3 and exhausted its plan after committing. |

The coordinator owns documentation archive moves, compatibility links, this
plan, integration validation, PRs, tags, and cleanup. Workers edit only their
own worktrees and commit their changes. After each accepted completion: run
targeted tests, review, merge, release the settled worker, remove its Orca
worktree, and prune Git worktrees. Preserve unmerged work rather than deleting
it to make the worktree count look clean.

REST additions or changes require `docs/validation/features.yaml`, simulator
reads in `tests/sim/test_sim_rest_reads.py`, and `python -m tools.validate ledger`.
The final suite must retain 100% route coverage. The final amd64 RC image `sha256:e0ab773c...` passed 26 deployment/context tests (two expected skips); its 17 dependency license inventories were verified. The arm64 image built and passed canonical info/health checks under QEMU.

## Final validation gates and discovered gaps

- **Runtime wiring:** the Phase 6/7 candidate described below predates runtime
  consolidation. On `wp-runtime-completion`, the shared composition, installed
  console and UC bridge are now merged, but persistence, action parity and
  integration lifecycle acceptance remain. Fresh source, installed-package and
  image/client campaigns are required before claiming complete runtime behavior.
- **Simulator and clients:** candidate API/browser/scripted-Remote and Home
  Assistant runs passed as recorded below. Features below their target and the
  Flic replay placeholder remain visible; these runs do not close hardware gates.
- **Hardware:** owner-observed HIL-B regression, HIL-C fault injection, HIL-E
  real-client checks, firmware versions, and physical CEC observations remain
  required. Existing checked-in ledger evidence contains no V4/V5 records.
- **Reliability:** HIL-D requires the planned 72-hour soak and resource metrics.
  An automated simulator run is not a substitute for the field gate.
- **Report:** publish `docs/validation/VALIDATION_REPORT.md` with feature/client
  results, limitations, supported hardware, and the evidence behind each gate.

Phase 8 is called `WP-V3` in the checked-in remediation plan. The handoff's
`WP-F2` label refers to this final validation gate, not a separate implemented
work package. No final release tag should imply these unresolved gates passed.

## Candidate campaign results

The [candidate report](../validation/VALIDATION_REPORT.md) retains all 268 feature
rows and links the real summaries. Clean source commit `ec850d2`: API 1,411,
browser 54, scripted Remote 18, real HA container 19 passes. Clean harness commit
`f55660e`, through the built image: API 27 and browser 17 passes. The combined
regression gate passed with zero known/unexplained failures. The dedicated Flic
replay client is still a placeholder (one explicit skip), not V3 client proof.
The separate scripted-Remote pytest suite passed 100 tests.

All six worker worktrees and the coordinator's visual-repair worktree are removed;
only the main checkout remains. No `v0.5.0`, `v1.0.0-rc1`, or `v1.0.0` tag was
created during this coordination session. Phase 5 visual approval, runtime
framework consolidation and the owner-observed hardware/field gates remain open.
