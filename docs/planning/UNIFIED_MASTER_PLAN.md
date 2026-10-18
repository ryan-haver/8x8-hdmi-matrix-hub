# Unified master plan

This is the current coordination entry point. The earlier execution record is
in [the phased roadmap](../../orca-phased-roadmap.md). Finding IDs and acceptance
criteria come from [the remediation plan](../REMEDIATION_PLAN.md) and
[the validation plan](../validation/VALIDATION_PLAN.md).

## Release sequence

1. Phases 0–4 are merged into `main`; `v0.4.0` points to `25233bb`.
2. Phase 5 is on [PR #36](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/pull/36).
   Commit `1aab559` corrects browser assertions for stacked overlays and limits
   the PIN latency test to its verification window. Local validation passed:
   Ruff, 2,793 Python tests, 175/175 REST routes, and 59 browser smoke/flow tests.
   CI run `39080173082`: 1,093 UI tests passed, 33 skipped, eight snapshots failed.
   Five modal differences were the corrected deployment port; their fixture now
   asserts the live origin before normalizing capture text. Three Tron snapshots
   retain small temporal changes from the 30-fps cap and await owner approval
   in `build/phase5-visual-review/index.html`. No baselines were changed.
   Merge only after all applicable CI checks pass, then tag `v0.5.0` on the merge
   commit and merge `main` into the release integration branch.
3. Integrate Phases 6–7 on `wp-g1-g2-release-and-docs`, validate the combined
   result, open its PR to `main`, and merge after CI passes. Synchronize package
   versions with the release bump script before tagging `v1.0.0-rc1`.
4. Run Phase 8 against the candidate and publish the validation report. Tag
   `v1.0.0` only when the final gates below have evidence.

## Phases 6–7 ownership

| Track | Requested model | Scope | State |
| --- | --- | --- | --- |
| `wp-g1-packaging-version-locks` | Sol 6.1 high | Packaging, canonical version, atomic bump script, hashed locks | Merged `14477d5`, worktree removed. Coordinator added RC version/notice coverage: 22 packaging tests passed, including coexistence with an editable install. |
| `wp-g1-ci-multiarch-hygiene` | Opus 5.5 high | Docker context, Git guard, pinned build dependencies, Dependabot, multiarch | Merged `de6693f`, worktree removed; coordinator reran 61 non-Docker tests. Worker also proved amd64/arm64 publication in a disposable local registry and arm64 health under QEMU. |
| `wp-g2-openapi-swagger-config-docs` | Argon high | OpenAPI/Swagger routes, API/config reference, registry and ledger | Merged `5366eff`, worktree removed; 172 coordinator tests passed, followed by corrected response/auth metadata and three passing read-only scenarios. |
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
The final suite must retain 100% route coverage. The RC image `sha256:5c9f50df...` passed 26 deployment/context tests (two expected skips); its 17 dependency license inventories were verified inside the image.

## Final validation gates and discovered gaps

- **Runtime wiring:** the Phase 4 `MatrixService`, `ActionRunner`, and
  `IntegrationLoader` classes exist and have tests, but the shipped `run.py`
  still constructs `OreiMatrix` and `RestApiServer` directly or delegates to
  `src/driver.py` for UC. Documentation must distinguish the framework from
  actual runtime behavior. Runtime consolidation is not proven complete.
- **Simulator and clients:** regenerate fresh API/browser/scripted-Remote and
  Home Assistant evidence on the release candidate; record failures and any
  features below their targets without relabeling them as passes.
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
