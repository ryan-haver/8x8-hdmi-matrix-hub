# SW-SEC-AUTH-01 author record

Scope is **F-SEC-007 only**: wrong PIN refusal, per-item lockout and hub
responsiveness. Base is `51275723846e4b126ccdc48c71d1727cabca4dbc`, task branch
`ryan-haver/wp-sw-auth-lockout`, local Windows host Zelu, Orca 1.4.232.
Run `run_37205f6095b3`, Task `task_eb4ab88caa5b`, Dispatch `ctx_5c634ce3cf0f`,
worker `term_704585c8-7ce8-4e60-a147-d13c285f1d25`; requested author model
Codex `gpt-6.1-sol`, high, OpenAI GPT family. No helper, fallback or delegation
was launched. Different-family exact-commit review remains coordinator-owned.

Own supported `account/rateLimits/read` observation at 2026-10-20T21:10:48Z
reported ordinary usage allowed, **74% remaining**, 10,080-minute weekly window,
reset 2026-10-27T06:33:16Z, no secondary pool, credits or reset credits. This is
the assigned managed pool, with one percentage point more usage than the 20:59Z
dispatch observation; the change was reported through Orca. Receipt:
`build/software-waves/SW-SEC-AUTH-01/quota-start.json`.

## Authority and changes

Original ownership is the new scenario, optional new focused test, this report,
and `build/software-waves/SW-SEC-AUTH-01/**`. Coordinator's explicit serial lease
in the reply to the worker's capability question additionally authorizes exactly
`tools/validate/clients/browser.py` and `tools/validate/clients/browser_driver.mjs`.
It forbids runner/model/schema/product changes. The lease resolves two observed
constraints: runner setup aborts on deliberate 403 responses, and exact toast
equality cannot check variable retry seconds. No generic setup bypass was added.

The bounded optional `pin_lockout` parameter on existing `profile_recall` and
`scene_run` intents makes five actual UI activations/executions, answers each
real prompt, requires 403 `invalid_passcode` and visible `Invalid passcode`, then
clicks the locked item again. It records the real 429/body/header and visible
lockout message, screenshots, dialogs and page requests. Stable `pin.*` client
observations expose five attempts, visible lockout, and a positive integer
`Retry-After` matching the response body. An optional different target makes the
final action execute an independently protected peer. Default flow semantics
are preserved, including the restored native duration-prompt fallback below.
There is no request-context or page-fetch substitute for GUI execution.

Eight IDs are new, all attributed exclusively to F-SEC-007 with empty
`client_features`: `sw_sec_auth_01.profile_wrong_pin`, `profile_allowed`,
`profile_locked`, `profile_per_item`, `scene_wrong_pin`, `scene_allowed`,
`scene_locked`, `scene_per_item` (each uses the `sw_sec_auth_01.` prefix).
Wrong-PIN/allowed cases support API and browser; locked/per-item cases support
browser only. Refusals require no simulator command, unchanged device state,
protected metadata and unchanged saved action definition. Positive controls
require changed independent routing and the exact video-switch command; peer
controls require exactly one video-switch command across the whole sequence.
Locked fixtures are discarded by the existing disposable-hub restart instead
of unauthenticated cleanup. Other fixtures use authenticated cleanup.

Coordinator message `msg_ebd6603b5b4e` at 21:16:36Z explicitly authorizes including
its staged eight-line F-SEC-007 scenario mapping in the normal-hook source
commit. The author inspected this exact staged diff: no other feature, level,
evidence, interface, finding or target field changes. The author did not edit
the registry, generate a ledger, import evidence, change baselines or touch
product source.

## Verification and calibration

Environment: Python 3.12.10 using the existing locked development virtualenv,
Node 24.20.0; local pinned Playwright Chromium. `npm ci --ignore-scripts
--no-audit --no-fund`, `npx playwright install chromium`, and `pip check` passed.
All configuration and temporary files use the new build subtree; no owner LAN,
hardware, root private data or deployment was used. Raw logs and screenshots
remain in that subtree; screenshots are observations without visual approval.

Focused run 01 passed **16 tests** in 30.78 seconds. It covers existing
`TestLockout`, `TestPbkdf2OffTheEventLoop`, both parameterizations of the strong
held-PBKDF2 responsiveness test and clocked lockout/reset/expiry test, plus two
new real Chromium cases. Those new cases compare exact saved profiles/scenes
bytes and independent simulator state/logs across five GUI wrong PINs, locked
clicks and correct-PIN refusal, then execute a protected peer through the GUI.
They reject an unbounded attempt count. The subsequent added oracle control
also requires the bridge to stop when its supposed wrong PIN succeeds.

The existing rendezvous test holds the verifier in a worker while health
answers, checks pending verification, worker-thread identity and current/max
loop lag below 100 ms. Existing tests check 429/Retry-After, correct-PIN lockout,
per-item isolation, increasing penalties, expiry and success reset. No new
duplicate timing test or after-only health claim was introduced.

Diagnostic run 01 is retained in `diagnostic-01/` with its log. Its new untracked
scenario source is not represented by clean base metadata: **all records from
that run are diagnostic only**, regardless of runner level/dirty labels. It
first caught an author expectation error: profile readback normalizes outputs
with `enabled: true` and `audio_mute: false`. This is an oracle correction,
not a presumed product defect. The original scene peer fixture intentionally
routes twice through two configured steps; the new peer control now explicitly
configures one profile step so its exact-one-command assertion is meaningful.
Diagnostic run 01 finished with seven passes and seven oracle failures; its
original records, screenshots and log remain intact. Initial Ruff also caught an imported fixture
name collision; the import was corrected. Full normal-hook source commit and
clean committed-source campaign results are recorded below when complete.

Focused run 02 retained one failed oracle/19 passes: JSON serialization omits
an undefined success error-code field; the calibration now checks its absent
or null value explicitly. Early focused diagnostics used default per-intent
screenshot names for successive actions, so their `after` screenshot could be
replaced by the next action. The final test assigns separate locked, peer,
guard and calibration artifact directories. These early diagnostics are not
accepted clean-campaign evidence.

Focused run 03 passed both final real Chromium tests, including the corrected
allowed-PIN calibration, in 71.60 seconds. Full-tree CI-path Ruff passed;
`python -m mypy src/` passed for all 91 source files. `node --check` passed.
The browser tests are explicitly opt-in via `SW_SEC_AUTH_BROWSER_TESTS=1` so
ordinary core-only CI has an honest dependency skip; opt-in is enabled for the
author's focused runs and normal full hook. The runner browser scenarios have
no conditional pass for missing browser dependencies.

## Limits and outstanding gates

This packet is source API/browser proof with **null image digests**. Runner V3
labels identify the browser client; they do not establish shipped-image V3
qualification, visual approval, hardware, soak or field acceptance. Global
admin/control authentication configurations belong to other auth units and
are not newly qualified here. Frozen images, historical `1ba`/CI `564` evidence,
registry levels and finding closure are not promoted. Existing direct/simulator
tests complement actual UI proof; different-family review and coordinator
acceptance/integration remain required. No push, merge, tag or cleanup is owned
by this worker.

## R1 compatibility correction and preserved first source

The first source commit is `f4ffa8d15aea519934e25a8b248992ebb074fe86`. Its
normal configured hook passed full CI-path Ruff and **4,043 tests, four skips,
35 deselections**, with strict **177/177 routes (100%)** in 1,145.97 seconds.
Original hook log and route bytes are retained as `source-commit-hook-01.log`
and `route-coverage-hook-01.json` under the build subtree. This first commit is
not the submitted final source.

Coordinator identified SW-SEC-AUTH-01-R1 during that frozen hook: the new wrapper
reset `promptValue` to the action's passcode even for a no-probe scene wait edit,
overriding its original seconds choice. The correction moves that reset inside
the actual PIN-probe branch, preserving original no-probe prompt semantics.
The source/index were not changed during the first hook. A fresh complete normal
hook is required for the corrected source; the first pass cannot cover it.

Calibration: the actual pre-fix `scenes.wait_edit` browser scenario **passed**,
including independent saved 0.5-second readback and no device writes. The current
UI uses the duration sheet, with no native dialog. R1 is therefore a native-prompt
fallback compatibility issue found by source inspection, not a demonstrated
current UI failure. The coordinator explicitly narrowed its earlier finding
and directed reuse of the existing wait scenario after correction. No prompt
was manufactured and no duplicate test was added. The passing pre-fix diagnostic
remains in `r1-before-01/` with its own log; it is not clean acceptance evidence.

## Final corrected source and clean results

Submitted implementation source: **`2ae46e6c8bb9c2133371c3d93509277235e5e40e`**.
This is the corrected commit after R1, based on the first source commit above;
the assigned comparison base remains **`51275723846e4b126ccdc48c71d1727cabca4dbc`**.
The later report-only commit changes this file alone; evidence keeps its original
implementation SHA. Orca's `worker-observed.json` records requested **and
effective** `codex / gpt-6.1-sol / high`. No different-family acceptance is
claimed from author checks or the coordinator's preliminary source study.

Fresh normal configured hook 02 passed CI-path Ruff, **4,043 tests / four skips /
35 deselections / four warnings**, and strict **177/177 actual routes (100%)**
in **1,352.90 seconds**. Both real Chromium tests were enabled. The hook's four
skips are reported as skips, not passes; its quiet output does not enumerate
their reasons. HA and scripted-Remote suites are excluded by the normal hook
and are not newly qualified here. Original outputs are `logs/source-commit-hook-02.log`
and `route-coverage-hook-02.json`; the prior full pass remains separately retained.
Mypy passed all 91 configured source files; this does not claim test-module
mypy coverage outside the configured scope.

Clean committed-source campaigns both passed with empty dirty-file lists:

| Campaign | Actual results | Checks | Artifacts |
| --- | --- | --- | --- |
| F-SEC-007 | **14/14**, six API and eight browser | **108 pass, six expected client-specific n/a, zero fail** | `clean-01/` |
| Existing `scenes.wait_edit` control | **1/1 browser** | **four pass** | `clean-wait-01/` |

The six n/a checks are explicit client scoping: browser-only toast assertions
do not apply to API, and API JSON-body subsets do not apply to browser. The
actual runner checks captured browser response status; no API-only body check
is used as proof of browser status. All eight new scenarios ran through actual
GUI intents in Chromium **153.0.8010.12**, pinned Playwright **1.63.0**, Python
**3.12.10**, Windows 11, and the real `run.py` shared-runtime entry with a local
matrix simulator. Image digests remain **null**. This is source/client proof,
not image qualification or a change to F-SEC-007's registry `current: V1`.

Clean records prove five actual GUI 403 `invalid_passcode` attempts, subsequent
429 `passcode_locked`, a positive integer `Retry-After` matching the body, actual
page request provenance, and independent protected peer execution. Every refused
record's independent simulator state and command log remain unchanged; every
allowed control changes routing from its pre-action value. The focused Chromium
tests additionally require exact saved profile/scene bytes to remain unchanged
across refusal and a correct-PIN API request to the locked item. Existing full-hook
tests supply per-item reset/expiry/escalation and the during-held-PBKDF2 no-stall
proof. The historical API scenarios' after-only health read is not timing proof.

`campaign-audit-02.json` verifies all **15 records and 33 PNGs**, JSON schemas,
exact source/dirty attribution, per-client feature ownership, covers, null image
digests, captured page requests, refusal/control effects and immutable SHA-256
hashes. The original audit and log remain: it wrongly expected success
`gate: pass`, while the actual runner contract is `result: pass, gate: ok`.
The corrected audit rechecked unchanged raw record/screenshot hashes and has
zero errors. No evidence bytes were normalized or imported.

Manual image inspection confirmed readable final wrong-PIN and profile/scene
lockout error toasts, plus the wait editor's saved-result feedback. Immediate
intermediate `locked.png` frames can precede toast paint; those frames are
observations, not a claim that every intermediate PNG contains readable text.
The final locked `after.png` frames show the errors. Screenshots grant no visual
baseline approval.

The actual formal command passed with exit zero and **zero known failures**:

```text
python -m tools.validate check --evidence build/software-waves/SW-SEC-AUTH-01/clean-01/evidence --run-summary build/software-waves/SW-SEC-AUTH-01/clean-01/run-summary.json --expect-clients api,browser
```

The gate also scans existing committed evidence and took longer than the scoped
record audit; its original output is `logs/clean-gate.log`. No ledger generation
ran. The coordinator separately refreshed three existing F-API-002 cases at
the same clean source in its own ignored subtree, then explicitly released the
tracked-file freeze before this report write. Those records are coordinator
deliverables and are not counted as worker-authored F-SEC-007 results.

Reproduction commands (all output directories were new; partial pytest disabled
`tests.route_inventory`):

```text
SW_SEC_AUTH_BROWSER_TESTS=1 python -m pytest -p no:tests.route_inventory tests/test_profiles_scenes_pins.py::TestLockout tests/test_profiles_scenes_pins.py::TestPbkdf2OffTheEventLoop tests/test_security_v3_hardening_scenarios.py::test_wrong_pin_keeps_health_responsive_during_pbkdf2 tests/test_security_v3_hardening_scenarios.py::test_wrong_pin_lockout_is_per_item_and_expires tests/validation/test_sw_sec_auth_01.py --basetemp=build/software-waves/SW-SEC-AUTH-01/focused-01 -q --tb=short
SW_SEC_AUTH_BROWSER_TESTS=1 python -m pytest -p no:tests.route_inventory tests/validation/test_sw_sec_auth_01.py --basetemp=build/software-waves/SW-SEC-AUTH-01/focused-03 -q --tb=short
python -m tools.validate run --feature F-SEC-007 --client api --client browser --out build/software-waves/SW-SEC-AUTH-01/clean-01
python -m tools.validate run --scenario scenes.wait_edit --client browser --out build/software-waves/SW-SEC-AUTH-01/clean-wait-01
```

These examples use shell-appropriate environment assignment; Windows execution
set the variables in PowerShell. Both normal Git commits inherited
`SW_SEC_AUTH_BROWSER_TESTS=1`, `ROUTE_COVERAGE_STRICT=1`, isolated
`MATRIX_DATA_DIR`/`UC_CONFIG_HOME`, and separate `PYTEST_ADDOPTS=--basetemp=.../hook-01`
or `hook-02`. `TEMP`/`TMP` used the task-owned new `tmp` parent. No manifests,
locks, hook configuration or global preferences changed.

The full assigned-base diff has exactly six paths: this report, the two new
scenario/test files, the two explicitly leased browser files, and only the
coordinator-authored eight-line registry mapping. No product, runner, DSL/model,
schema, baseline, finding, evidence or ledger source changed. The existing
registry interface list names profile recall only; any scene execute interface
metadata update belongs to coordinator assembly. Different-family exact-candidate
review, evidence import, registry/ledger qualification, integration, publication
and release gates remain coordinator/owner responsibilities.

Final shared-pool observation (`quota-finish.json`): ordinary usage still
allowed, **66% remaining**, same weekly window/reset and no secondary pool.
The 74% to 66% change is shared-pool usage, not an attribution to this worker.
Raw native output includes an initial environment discovery with transient Orca
hook/launch capability values: preserve that transcript privately and sanitize
external excerpts. No such values are committed in this report or source.

The report-only follow-up uses the task-authorized invocation-only
`git -c core.hooksPath= commit` exception after the corrected source's full normal
hook, clean campaigns, audit and formal gate. Its checks are scoped whitespace,
path/diff and artifact-hash checks; it is not another full-hook pass. Final
submission SHA and full base diff are recorded in the separate build receipt,
avoiding a self-referential report hash. No push, merge, tag, ledger import,
finding closure, worker settlement or destructive cleanup was performed here.
