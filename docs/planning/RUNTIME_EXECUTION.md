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

## Integrated corrections and combined validation

- **R3C, Argon high / Antigravity:** accepted in `709232b` after 67 combined
  checks. The bridge preserves an empty catalog before setup and restores the
  configured 74 entities. Fourteen real installed-wheel checks passed, including
  setup/control/restart outside the checkout. Four concurrent dispatcher/REST
  simulator checks passed for shared wrap/clamp cycles. SDK 0.7 does not advertise
  optional select entities; these direct dispatcher calls are not Remote
  WebSocket cycling proof. Existing real Remote source-selection proof remains.
- **R5B, fresh Sol 6.1 high / Codex:** accepted in `3e21e6f` after 219 independent
  checks. Corrected metadata counted as buttons, disabled imports and lost
  cleanup owners; retained failed owners support explicit retry. Actual separate
  Zeroconf instances resolve and withdraw the established service type.
- **R1C, Sol 6.1 high / Codex:** accepted in `89b4928` after 177 independent
  checks. Owned reads across cache generations drain before transport disposal.
  Ten registered REST cycle/readback tests passed again without the earlier
  session leak warnings. Explicit reconnect remains supported after shutdown.

The first combined source run at `3e21e6f` passed 3,733 tests with four skips,
29 deselections and 177/177 routes, but **47 tests failed**. This is not a green
release gate. Corrections have separate ownership:

- **R2C, Sol 6.1 high:** accepted in `8fc4570`. Both synthetic-source worktree
  and actual root reruns passed 428 checks with one platform skip. Managed
  catalogs import only from explicitly selected installations; unsafe existing
  targets are refused before imports, preserving original bytes. Legacy test
  fixtures now use disposable source directories. The root rerun left local
  runtime files unchanged against the post-discovery hash checkpoint.
- **R4B, Argon high:** candidate `5daa554` passed 395 worker checks with one skip
  but was not accepted. Review rejected live-client method interception and a
  special `BaseException` bypass. The committed candidate is preserved in the
  same child worktree for **R4C, fresh Sol 6.1 high**, which owns explicit service
  exception propagation and safe public action errors. Ordinary refusals, partial
  results, cancellation and the sole client owner must remain intact. This was
  coordinator code review; no automatic approval rejection occurred.
- **R6B, Flash 3.8 high:** accepted in `30fd047`. Seventy-two independent R6
  checks and an additional command-filter guard passed; root JavaScript lint
  passed. Coordinator tightened maintenance filtering to known commands and
  ensured failed readiness runs inside fixture cleanup.
- **R1D, fresh Sol 6.1 high:** accepted in `42893e5` after 95 independent
  capture/readiness/source-UC checks. Capture uses fresh, serialized reads
  instead of cached facade state; failed reads preserve storage. UC production
  bind rollback was already correct. Harness checks now require this child's
  completed bind and prove exclusive listener conflicts; explicit ports do not
  silently move. Final combined source/image/client gates remain pending R4C.

R7 Luna is preparing guides against accepted behavior while the last correction
runs. Its final evidence index and completion are blocked on a separate
coordinator campaign-evidence handoff. Fresh Astra R8 review remains after that
acceptance. Dedicated HA component tests passed 101 checks in the pinned Python
3.13 test container; these are unit checks, not HA deployment or physical proof.

Coordinator refreshed only the additive health JSON contract fixture and added
registered Flic privacy/disabled-route reads. The obsolete direct-construction
documentation assertion will follow the packaged composition documentation in
R7. No visual baseline changed.

A new amd64 image built from the combined UC correction passed 27 deployment
checks with two expected skips (Linux-host networking and a UC-only disabled-mode
check), including separate-container discovery, advertised API access and goodbye
after normal SIGTERM. Its image ID and source provenance are in
`build/runtime-completion/image-amd64-build.log` and `deploy-amd64.log`; these
checks do not cover the still-pending corrective commits or physical LAN clients.

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
registry checks passed. Cycle readback and transport cleanup checks now pass.
Final image/client campaigns and configuration-specific registry/ledger checks
must follow the current corrective tracks before R7 and independent R8 review.

## Integrated correction and campaign checkpoint, 2026-10-19

The held R4B candidate above is historical. Its explicit R4C correction and later
R1E preset-cache correction are integrated; the rejected interception approach
was not accepted. The accepted clean `59aae63` local run passed 3,941 core tests,
four documented skips and 31 deselections, covering 177/177 REST routes. Its
dedicated actual-SDK UC suite passed 100 tests. The complete source campaign
passed API 1,411, browser 54, scripted Remote 18 and Flic 23 outcomes. Earlier
failed source summaries remain preserved, including the preset-read failures
that led to R1E; they are not counted as accepted passes.

Both normal-command images were built from `59aae63`. Their recorded IDs are
amd64 `sha256:a91722edff1a44baf29e66b0332a99adb805b1591749846539525b7a039cfc2e`
and arm64 `sha256:dba8ac3587e5ccdd69580c0498612142fa568c517b419d6a7e53ea86cb40f2bb`.
Both matched all 257 tracked shipped inputs. The amd64 deployment run passed
26 tests with three expected platform/configuration skips; arm64/QEMU passed
normal startup, offline API/health and SIGTERM checks. These results do not cover
the pending R3E UI correction or physical device actions.

- **R5C, Sol 6.1 high:** `4f57245`, merged as `9b512f5`, fixes Linux deployment
  test assumptions. Docker selects the isolated subnet before the harness makes
  it explicit; an independent Zeroconf observer checks actual SDK discovery
  instead of an obsolete log string. Linux passed 27 deployment tests with two
  expected configuration skips. Coordinator verification passed four with one
  Linux-only skip; the new GitHub Docker job also passes. The worker was released
  and its child removed/pruned.
- **R6C, Flash 3.8 high:** `b4d0915`, merged as `a7eedf6`, classifies structured HA
  application errors without bypassing unexpected transport failures or normal
  response checks. Fourteen independent focused checks passed. Corrected actual
  HA source campaigns at clean `a7eedf6` passed 19/19 on HA 2026.9.3 and 19/19
  on 2025.1.4. The latter checks the supported 2025.1 version line, not the exact
  2025.1.0 floor. Original 17-pass/two-failure records remain intact. The worker
  was released and its child removed/pruned.
- **R3E, requested Argon high alias:** `ccb4a08`, merged as `4dd7ca5`.
  Startup/manual refresh now preserve newer WS routes across delayed and
  overlapping REST reads, with later REST fallback. Independent checks passed
  16 tests with one optional host dependency skip; final reconnect smoke 1/1
  and smoke 5/5 passed. Later clean-candidate flows passed all 59. The worker was
  released and its child removed/pruned. Backend identity behind the alias
  remains unverified as documented in the model inventory. A fresh Sol review used real
  runtime/SIM payloads and actual application JavaScript to demonstrate newer WS
  routing being overwritten by a delayed startup REST response. Exact event-order
  attribution to the first failing CI run remains unproven. The bounded
  `app.js` and new-regression change leaves existing E2E oracles and visual
  baselines intact. The read-only review is
  complete, its artifacts copied, and its worker released and child removed.
- **R1F, Sol 6.1 high:** `007a02d`, merged as `aa27b4d`, expires CEC enable
  decisions on explicit protocol/facade/WS synchronization. Ordinary cache
  behavior is preserved. Exact-commit independent checks passed 27 tests; two
  additional registered simulator cases fail before and pass after the fix.
  The full clean image campaign now passes the unchanged Flic source-power
  oracle that previously failed at `55d4fe0`. The worker was released, evidence
  copied and its child immediately removed/pruned.
- **R7, Luna medium:** guide preparation accepted at `5608407` after 375
  independent documentation checks. The final report/evidence reply is now
  delivered for final indexing. **R8, fresh Astra high**, has
  not launched and remains after those gates.

Draft [PR #38](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/pull/38) targets
the Phase 6/7 branch. At `4adbc13`, CI finished 12/13 required jobs passing;
only the same three Tron screenshots fail (1,098 UI passes, 33 skips; follow-up
gallery 62 passes). CI core passed 3,948 tests with 22 skips, 31 deselections and
177/177 routes; actual HA passed. The complete local core separately passed
3,966 tests with four skips, dedicated UC 100, source clients 1,506 and source
HA 19 per pinned version. All 193 image client outcomes, both architecture
builds, deployment/arm64/parity checks, 59 flows and four Swagger checks pass.
The formal combined gate passed; 26 registry/ledger checks and all 213 archived
Git-blob hashes pass. An initial importer client-scope overconstraint and Git
line-ending normalization were corrected without changing original results;
rejected intermediate checks remain retained. See the
[runtime report](../validation/RUNTIME_VALIDATION_REPORT.md) and actual
`build/runtime-completion/after-r1f/` artifacts. Older runs under `after-r1e/`
and `after-r6c/` retain their original scope; the independent
R3E report is `build/runtime-completion/r3e-review-evidence/REPORT.txt`.

## Evidence and release gates

Accepted worker reports must include the commit, actual files, targeted tests,
parallel seams still mocked and runtime/image evidence still pending. The
coordinator validates before merging and promptly removes accepted worktrees.
Shared registry/ledger/schema/scenario changes stay coordinator-owned.

The old candidate [validation report](../validation/VALIDATION_REPORT.md)
remains tied to its recorded commits. Runtime changes need fresh integrated
image/client evidence. The three Tron baselines still need owner approval;
hardware/CEC/client observations, 72-hour soak and field sign-off remain open.
