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
final action execute an independently protected peer. Other flows are unchanged.
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
