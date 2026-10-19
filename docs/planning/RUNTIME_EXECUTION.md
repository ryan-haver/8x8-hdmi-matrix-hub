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
- **R1P, Sol 6.1 high through Codex:** `3010128`, merged as `324a4b0`.
  Coordinator independently ran 103 tests, with two installed-start skips and
  one unchanged real source-start deselection, all tied to missing R2. Real
  wheel installation/resource/console dispatch and clearly labeled factory
  doubles passed. Actual runtime/UC/image startup remains pending. Its terminal
  was released and worktree removed/pruned.
- **R3 plus R3B, Argon implementation / Sol 6.1 high transaction correction:**
  final `3c523df`, merged as `ccc9483`. Coordinator independently ran 151
  targeted tests, including 17 actual-runtime/SDK transaction tests with a
  labeled R2 barrier shim and transport doubles. Setup/save rollback, queued
  events, single-writer counts, live renames and SDK cleanup passed. Its
  terminal was released and worktree removed/pruned. Actual normal-entry,
  installed UC and shipped-image behavior still await R2 and the later tracks.
- **R2, MiniMax M3 checkpoint / fresh Sol 6.1 high completion:** final
  `168fc03`, merged as `59a2e8e`. Coordinator independently ran 666 persistence,
  security, scene, source and installed-entry tests with one platform skip,
  plus 68 configuration tests; mypy passed all 90 source files and focused
  Ruff passed. Review checked original-byte failure preservation, private
  projections, real edit/save/restart and legacy imports. The worker was
  released and worktree removed/pruned. Full image/client and R4/R5 behavior
  remain separate gates; these focused results are not a full product campaign.
- **R4 plus R4A, Sol 6.1 high through Codex:** final `d461daa`, integrated
  with coordinator test fixes as `9730bf5` and merged as `6ae0227`.
  Coordinator independently ran 432 action, PIN, cancellation, simulator,
  foundation and UC transaction tests with one HA dependency skip; mypy passed
  all 90 source files. Review checked exact public projections, cycle readback,
  shared authorization, cancellation restoration and HTTP unified-scene parity.
  Both Dispatches settled, the terminal was released and worktree removed/pruned.
  UC dispatcher adoption remains R3C-owned; full image/client proof is pending.

## First implementation wave

All four worktrees start from accepted contract merge `70de5d9`.

| Track / worktree | Selected model and harness | Current evidence |
| --- | --- | --- |
| R1 `wp-runtime-core-composition` | Sol 6.1 high / Codex | Foundation accepted/merged; actual startup awaits peer integration |
| R2 `wp-runtime-persistence-wiring` | MiniMax M3 / OpenCode checkpoint; fresh Sol 6.1 high finish | Accepted/merged `59a2e8e`; 734 independent passes, one platform skip; worktree removed |
| R3 `wp-runtime-uc-adapter` | Argon high / Antigravity; Sol transaction follow-up | Accepted/merged `ccc9483`; 151 coordinator tests passed; worktree removed |
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
dropped unknown fields plus the schema marker. These were pre-acceptance
failures, subsequently corrected and validated in R2. R3's setup/address
signature mismatch was corrected without changing the shared runtime interface.

R2's M3 attempt subsequently settled with a failed full-scope checkpoint at
`cf7ea7c`; its terminal was released. The coordinator merged accepted parent
`99e9d56` into that clean child as `5ec374e`, preserving the checkpoint. Fresh
**Sol 6.1 high / Codex** took retry Dispatch `ctx_cde87530b675` on the same
Task `task_02e6418f9110`. Requested/effective launch preferences matched.
The finish brief requires real edit/save/restart preservation, fail-closed
backups and malformed/future files, safe legacy scene reconciliation, Flic
metadata preparation, and unchanged source/installed startup tests. This was
subsequently accepted as recorded above. Final ownership transfers also covered
five exact obsolete migration/layout expectations, one malformed Flic fixture
sentinel, the shared simulator's canonical scene-copy filename, and replacing a
probabilistic PIN substring check with hash-format/verification assertions.
Unsafe-input tests retain exact-byte preservation; public security assertions
were retained. R5 must use the accepted `load_versioned_json`,
`flat_map_records('flic_buttons.json', payload)` and `save_versioned_json` seam,
projecting only the known button fields to public callers.

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

Shared campaign commit `6e06bf0` registers 23 Flic scenarios and the client's
four specialized intents, and prevents replay/transport errors from passing an
unchanged-device check. Combined registry/model/evidence/runner checks: 61
passed. The recorded Flic levels are retained pending a fresh runtime campaign.

## Installed entrypoint scope extension (R1P)

Source review found the packaged `orei-matrix-driver` console command still
targets `driver:main`, bypassing the accepted shared runtime and migration
barrier. Installed runtime path/metadata resolution also assumes a checkout.
This is a shipped-path gap, not a completed packaging test result.

Explicit Task `task_7cc233ade54f`, Dispatch `ctx_1346bbff7935`, assigns
**Sol 6.1 high / Codex** to `wp-runtime-installed-entry`, based on `6e06bf0`.
Effective launch and an active turn were observed. Ownership is restricted to
packaged bootstrap/console metadata, root compatibility wrappers, narrow default
path/driver-metadata seams and packaging tests. It also receives the known
signal-handler type-annotation correction; R4 no longer owns that run.py change.
R2/R3/R4/R5 files stay separate. R7 and the final source/wheel/image campaign
wait for R1P acceptance as well as the original implementation tracks.

R1P is now accepted as recorded above. Installed use requires explicit writable
`DATA_DIR` (or `MATRIX_DATA_DIR`); source/Docker defaults remain unchanged. This
decision and the actual startup tests must be reflected in the final guides.

## UC transaction follow-up (R3B)

R3's candidate starts real SDK sockets and retains the published 74 entities,
but isolated/legacy tests do not prove the active runtime transaction. Review
found an extra setup-complete save after `runtime.reconfigure(persist=True)`;
the worker also found a names-event writer during candidate connection. These
must not bypass rollback or leak candidate names into stored configuration.

After releasing the Argon terminal, the coordinator merged accepted parent
`4e4c288` into its clean candidate worktree as `c31bac6` for the follow-up.
Task `task_c958f21e544b`, Dispatch `ctx_6fcfc385f0a8`, assigns fresh **Sol 6.1
high / Codex** to the setup/persistence transaction and bounded UC cleanup.
It owns only the reconfigure persistence spans in runtime composition, UC
setup/bridge/migration code, dedicated tests, and (if needed) the UC arguments
of `runtime.integrations.bind_integrations`. Loader/flag work remains R5-owned.
R4/R5 wait for accepted R2 and R3B. No duplicate persistence editor is launched
before the current R2 worker settles and is released.

R3 model evidence is recorded precisely: Orca effective preferences and the
native session header identified Argon high; its completion self-report named
Gemini 3.1 Pro. The discrepancy does not establish the backend model identity.

After combining R1P/R3B, full `mypy src/` found one dataclass-class narrowing
error in the entity normalizer. Coordinator excluded classes from `asdict`;
45 typed-UC regressions passed, owned Ruff passed, and mypy passed all 89
source files. Shared harness metadata now records the actual `hub.cli` entry,
Flic/HA flags and active runtime/UC paths for evidence freshness; 38 focused
registry/model/error-pipeline checks passed. Full source-client runs remain
pending the real persistence integration.

Deployment evidence now covers the shipped source, assets, runtime entrypoints
and license files, rather than only legacy driver paths. Sixteen evidence-schema
tests and focused Ruff checks passed. Old deployment records remain historical;
these metadata changes do not imply a fresh image run.

## Remaining integration corrections

- **R3C, Argon high / Antigravity:** actual installed-console validation found
  an unconfigured UC bridge starts with zero entities, then its initial event
  incorrectly exposes the full 74-entity catalog. The bounded bridge correction
  also owns only UC next/previous dispatch adoption of R4's atomic wrap/clamp
  cycle seam. No golden or empty-before-setup assertion is relaxed.
- **R5B, fresh Sol 6.1 high / Codex:** Flash candidate `7b78785` independently
  passed 157 tests, but coordinator review reproduced metadata counted as a
  Flic button, a disabled direct factory importing Flic, and a canceled stop
  losing its unfinished cleanup owner. The Flash worker was released; its
  candidate remains unmerged. Sol owns safety completion and exact approved
  fixture corrections, including retained failed-cleanup health and retry.
- **R1C, Sol 6.1 high / Codex:** new real simulator cycle/readback tests exposed
  an unclosed HTTP session. Diagnostic allocation tracing found a shielded
  output-status fetch initiating a connection during teardown. This track owns
  only matrix transport read draining plus dedicated tests; intentional shutdown
  must settle outstanding reads across cache generations before disposal.

Coordinator removed obsolete R2 module substitutions from the shared R1 test
builder, retaining a spy around actual preparation. Thirty-nine composition,
shutdown and UC transaction checks plus nine state-bridge checks passed; the
explicit UC subprocess double remains labeled as such. The HTTP contract fixture
now models the existing unified scene route; 47 framework tests passed.

Registered device-settings and scene reads now test private extension retention
through actual edits/reloads while keeping credentials and hashes out of public
responses. Registry and ledger are synchronized. OpenAPI describes cycle query
parameters and scene v2's existing omitted fields, 201 creation and 207 partial
execution without changing runtime wire bodies: 122 API/config tests and 17
registry checks passed. Cycle readback checks pass, while their transport cleanup
warning remains explicitly open for R1C. New deployment discovery proof is ready
but has not yet run against the final image.

## Evidence and release gates

Accepted worker reports must include the commit, actual files, targeted tests,
parallel seams still mocked and runtime/image evidence still pending. The
coordinator validates before merging and promptly removes accepted worktrees.
Shared registry/ledger/schema/scenario changes stay coordinator-owned.

The old candidate [validation report](../validation/VALIDATION_REPORT.md)
remains tied to its recorded commits. Runtime changes need fresh integrated
image/client evidence. The three Tron baselines still need owner approval;
hardware/CEC/client observations, 72-hour soak and field sign-off remain open.
