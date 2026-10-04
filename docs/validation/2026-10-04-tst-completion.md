# Test tooling completion: TST-14 and TST-19

## Approved baselines (TST-14)

The owner approved the 21 remaining drifted baselines and the test-tooling
merge on 2026-10-04. Commit `2a757c7` refreshes exactly those 21 PNGs in
`mcr.microsoft.com/playwright:v1.63.0-noble` and empties `STALE_BASELINES`.
Their IHDR dimensions match the desktop and Tab A11 projects; all 21 have
zero pixel differences from the approved candidate captures at 0.05.
The contact sheet was inspected. The catalog changed only in line endings
and was restored. The separate visual commit contains the PNGs and the
emptied exception list.

No shipped `src/` or `web/` file changes. The earlier failing-first proof for
TST-10/11/13/15/16/17 remains in [the original report](2026-10-03-tst-10-11.md).

## Scenario environment and readiness (TST-19)

The full CI scenario command exposed three setup problems on unchanged
`main` (`14f5e49`), also present on the test-tooling branch:

- HTTP-only CEC checks and opt-in Telnet CEC checks ran in the same default
  HTTP configuration. All 206 Telnet checks failed their transport expectations.
- `contracts.cables` could act before the Telnet handshake finished and receive
  503, although a subsequent read succeeded.
- `profile_state.capture_output_read_failure` injected an HTTP read fault after
  the runner warmed the hub cache. The measured action used the cached value,
  saved successfully, and never reached the injected fault.

Before the fix, both new end-to-end tests in
`tests/validation/test_runner_environment.py` failed (14.76 s). A separate run
on unchanged main reproduced all three failed scenario types.

Commits `62adf64` and `bb029d4` fix the runner-managed simulator setup:

- Scenarios can declare `hub_env`; the Telnet CEC family opts in explicitly.
  The runner restarts the hub and client when settings change, and restores
  the HTTP defaults afterward.
- Fault scenarios use `OREI_STATUS_CACHE_TTL=0`, so read faults reach the
  measured device read. Happy paths retain the normal three-second cache,
  including the preset catalog's one-read-per-slot checks. An added preset
  check failed when caching was disabled globally and passed after this
  override was narrowed; all four environment tests then passed (32.48 s).
- The runner waits up to 10 seconds for Telnet before setup and fault injection.
  Failure to become ready produces blocked evidence rather than an assumed pass.
- External hubs and hardware retain the operator's settings. Two additional
  tests verify the runner does not restart or reconfigure them.

After the fix, both end-to-end tests passed (14.44 s), including HTTP → Telnet
→ HTTP, successive interrupted power replies, cable readiness, and rejected
output reads. All four new tests passed in the full commit hook.

Only the 206 Telnet records made stale by the scenario definition were
re-recorded, against committed `62adf64`: all passed at V2. No hardware was
contacted and no V4 claim is made.

The approved pruner removed the 206 superseded records and 612 registry
references, after verifying all deletion targets stayed in the evidence
directory. Its before/after ledger comparison found zero differences.

## Final local validation

The full pinned visual suite passed: **1,098 passed, 33 skipped, 0 failed**
(36.2 minutes), including smoke, flows, every viewport, and status colours.
No baseline changed during that comparison run.

Other local checks: Ruff, `mypy src`, ESLint; Stylelint at baseline 539;
full pytest **1,707 passed, 2 skipped, 26 deselected**; scripted Remote
**97 passed, 1 existing UC-02 xfail**; HA unit tests in `python:3.13`
**99 passed**; hassfest **0 invalid integrations**; real HA-container
scenarios **19 passed**; Docker build and deployment **24 passed, 2 skipped**.

Final API/browser/Remote scenario verification, gates, and secret scan are
recorded on the test-tooling PR. Proof levels remain unchanged: 268 features,
92 at V3, 65 at V2, no V4, and zero stale evidence.

HACS cannot run locally. Deployment has the documented skips for Linux host
networking on Docker Desktop and the disabled-integration case.
