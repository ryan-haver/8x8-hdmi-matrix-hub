# Runtime-completion execution record

Started 2026-10-18 on `wp-runtime-completion`, from Phase 6/7 tip
`6debe5a9d1ce3b5993bbd1f6c16d14550d11141b`. This branch depends on the
unmerged Phase 5/6/7 release work; it is not a final release tag.

The [development plan](NEXT_DEVELOPMENT_PHASES.md) and
[accepted contract](RUNTIME_CONTRACT.md) define the work. No Claude/Anthropic
worker, helper, automatic fallback or default tab is authorized.

## Accepted work

- **R0, Astra high through Codex:** contract commit `0125ad2`, merged as
  `70de5d9`. Coordinator checked the sole-file scope, local links and all six
  implementation briefs. The worker also checked 77 existing paths, 21 declared
  new paths and unique test ownership. Its terminal was released and its Orca
  worktree removed/pruned. This is design evidence, not a runtime test result.
- **R1, Sol 6.1 high through Codex:** implementation `a6da11c`, merged as
  `952a14a`. Coordinator independently ran 205 focused tests successfully;
  one unchanged real-startup test remains pending R2's production migration
  barrier. This accepts the shared runtime foundation, not complete startup
  or UC/image behavior. Its terminal was released and worktree removed/pruned.
- **R6, Flash 3.8 high plus focused Sol 6.1 high correction:** final candidate
  `d7866fa`, merged as `809f934`. Coordinator independently ran 74 tests with
  one explicit integrated disabled-route test pending. Review checked actual
  generator/startup capture, callback multiplicity, failure results and evidence
  redaction. Terminals were released and its worktree removed/pruned. Shipped
  image and physical Flic Hub/SDK/buttons remain separate acceptance gates.

## First implementation wave

All four worktrees start from accepted contract merge `70de5d9`.

| Track / worktree | Selected model and harness | Current evidence |
| --- | --- | --- |
| R1 `wp-runtime-core-composition` | Sol 6.1 high / Codex | Foundation accepted/merged; actual startup awaits peer integration |
| R2 `wp-runtime-persistence-wiring` | MiniMax M3 / OpenCode | Native configuration and active Build session identify M3; implementation underway |
| R3 `wp-runtime-uc-adapter` | Argon high / Antigravity | Effective launch plus Gemini 4 Argon/high session header observed; implementation underway |
| R6 `wp-validation-flic-replay` | Flash 3.8 high / Antigravity; focused Sol follow-up | Accepted/merged `809f934`; 74 tests passed, one integrated disabled-route gate pending; worktree removed |

Launch observations alone are not acceptance evidence. R4/R5
remain dependent on accepted R1/R2/R3 integration; the final campaign precedes
R7 documentation and a fresh R8 review.

## Preflight and explicit ownership updates

Repository setup scripts are empty; setup was explicitly skipped. The global
default agent is Pi, overridden by each explicit worker agent. No global
account/model settings were changed.

For R2, ignored worktree-local configuration restricts providers to the
MiniMax coding plan, pins native agents plus 14 plugin roles/eight categories
to M3, denies nested agents, and disables plugin runtime/model fallback.
Native model discovery, agent permissions/model inspection and plugin schema
validation passed before dispatch. Orca's OpenCode TUI model-override preflight
still refused `--model` before creating a dispatch; state inspection confirmed
the Task remained ready. The successful launch inherits the verified local
configuration; its null launch-model receipt is not described as explicit
override support. The actual session header identifies M3. Access at launch
does not guarantee remaining quota.

The coordinator explicitly transfers one additional source seam to **R6**:
`web/js/components/integrations-drawer.js`, only the all-output request inside
`updateFlicOutput`. The current generated `POST /api/input/{n}` has no route.
R6 must capture the failure, change it to existing `POST /api/switch` with
the JSON input body/content type, and prove exact generated-request/SDK replay.
This narrowly overrides R0's no-UI boundary; other UI behavior/styles,
credential handling and baselines remain outside this transfer. No new REST
route is required. Any actual visual difference remains subject to review.

R2 also has an explicit acceptance clarification: preserve unknown private
storage fields without expanding public API/snapshot bodies or exposing
credentials/PIN hashes. Test disk roundtrips and public projections separately.
Filename-only persistence expectation updates are permitted in
`tests/test_hub_persistence_openapi_env.py`, `tests/test_scene_manager.py`,
`tests/test_profiles_scenes_pins.py` and
`tests/test_security_v3_hardening_scenarios.py`; hashing/security assertions
remain intact and dedicated legacy plaintext-PIN import coverage is required.
Two on-disk filename expectations in `tests/sim/test_sim_scenes_v2.py` are also
transferred; its API/value assertions remain intact.

Coordinator reproduced pre-merge R2 blockers with synthetic data: version-zero
preparation continued after backup failure, and a real profile save/PIN rehash
dropped unknown fields plus the schema marker. These are acceptance failures
under correction, not changes accepted into this branch. R3 is correcting a
setup/address signature mismatch against the real R1 types; its private UC
metadata must not change the shared runtime interface.

R6 candidate `465c10d` is not accepted. Its original tests passed, but review
found a copied generator rather than proof against the actual UI generator,
incomplete refusal/partial-result checks and unsafe error evidence. Follow-up
Task `task_2c07e3bae5ba` reuses its proven Flash terminal under Dispatch
`ctx_5c50aeae95ca`. A narrow JS bridge in `tools/validate/clients/` is also
authorized. R7 waits for this follow-up's acceptance, exact-template replay,
auth/redaction checks and the later integrated campaign. That follow-up settled
at `119cfac`; coordinator independently ran 44 tests successfully, but review
still found copied startup registration, silently truncated callback requests
and incomplete response/error redaction. Its Flash terminal was released.
Fresh **Sol 6.1 high / Codex** completed focused Task `task_04743d5e528d`, Dispatch
`ctx_f0288cfc3a99`, in the same worktree. Accepted final result is recorded above.
Its automatic broad pre-commit hook reached 3,209 passes before local missing
`@eslint/js` ESM resolution failed; owned lint/syntax checks passed. This is not
recorded as a successful full-suite run. The commit used an invocation-only
hook bypass, with no dependency/global configuration change.

Shared evidence commit `f116d61` redacts manual-auth/PIN values from persisted
action descriptions, including nested hashes and query keys, without changing
transport parameters. Nineteen model tests and 23 evidence/ledger tests passed.

## Evidence and release gates

Accepted worker reports must include the commit, actual files, targeted tests,
parallel seams still mocked and runtime/image evidence still pending. The
coordinator validates before merging and promptly removes accepted worktrees.
Shared registry/ledger/schema/scenario changes stay coordinator-owned.

The old candidate [validation report](../validation/VALIDATION_REPORT.md)
remains tied to its recorded commits. Runtime changes need fresh integrated
image/client evidence. The three Tron baselines still need owner approval;
hardware/CEC/client observations, 72-hour soak and field sign-off remain open.
