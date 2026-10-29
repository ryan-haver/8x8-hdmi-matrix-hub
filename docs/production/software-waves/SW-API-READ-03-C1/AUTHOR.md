# SW-API-READ-03-C1: device-side output-name event proof

Implemented `sw_api_read_03_c1.output_name_change` for F-API-040, API/sim V2
only, with real managed simulator/hub regression controls. **Overall delivery:
FAILED acceptance** because the actual global validation gate exited 1 for
F-SEC-007 (V2 below recorded V3), despite the scoped event proof passing.
Its baseline/preexistence attribution is unverified. Independent qualified
different-family review, integration, qualification and artifact admission remain
HOLD; this report does not close the feature or parent unit.

## Authority and authorship

- Task `task_d72e772cd2f9`; Dispatch `ctx_07f9f4c85a04`;
  existing Run `run_37205f6095b3`.
- Worker `term_f014699e-0979-4e2c-8328-2890f4849dc8`;
  coordinator `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`.
- Author OpenAI `gpt-6.1-sol`, effort `high`, as assigned and observed in
  Orca requested/effective launch fields. No helper, nesting, fallback or reviewer.
- Exact frozen base `938ae30339790c361abdda6fdd01b11a4e498518`;
  branch `ryan-haver/wp-api-read-03-c1`, local Windows child checkout
  `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-api-read-03-c1`.

The original NEW-file-only scope encountered a real runner eligibility blocker.
`Runner._refusal` rejected `device_change` whenever `client.observes` was false;
`ApiClient` inherits that false default. A private in-memory diagnostic reproduced
`client 'api' cannot observe a 'device_change'`, exit 0, without starting services
or claiming event behavior. Original diagnostic source hashes and bytes remain
unchanged under `build/software-waves/SW-API-READ-03-C1/blocker-01/`, with an
independently hash-verified `blocker-01-copy/`. No default skipped scenario was
shipped to bypass that boundary.

Coordinator answer `msg_1f797d216755` to blocking question `msg_0f6783e51681`
then explicitly leased **only `tools/validate/runner.py::_refusal`** in addition
to the originally owned new scenario/test/report/build paths. The settled prior
runner writer and separate current `model.py` lease were confirmed by the
coordinator; this author did not touch the model or client contract. The new
exception requires target sim, API client, `device_change`, an applicable positive
`WsEvent`, and no applicable `ClientState`. NoWsEvent-only, device-state-only and
no-command-only checks do not enable it. Existing client/intent refusals and
hardware/target/write/unrestorable gates remain. `ApiClient.observes` stays false.
This separately authorized support change requires qualified final-commit
source review, which remains held for unknown DeepSeek headroom.
The private `support-01/after-refusal.json` confirms eligibility without enabling
`ApiClient.observes`, compares all six original source hashes and identifies only
the authorized runner change. The original blocker files remain unchanged.

## Behavior and failure controls

The scenario changes only simulator output index 0's name from `TV` to `Den TV`
through supported `device_change` state patching. The actual `/ws`
`output_name_change` expectation is first, before any hub GET readback. Managed
preparation initializes/synchronizes the hub before the action mark; the hub's
own poll observes the device-side mutation. This is not a hub rename POST or a
REST-triggered refresh claim. Disposable settings are `STATUS_POLL_INTERVAL=0.5`
and `OREI_STATUS_CACHE_TTL=0`, recorded by the existing runner.

The scenario also checks no routing event over three poll intervals, exact device
name, all other device state unchanged, no matrix write, no `set output name`
or `video switch` command, and only then REST readback. Existing JSON WS schema
validation checks every recorded message.

The new test module uses ordinary real `Runner.run` preparation and subprocesses:
one positive scenario, wrong name, wrong output, and an unchanged-name action.
Wrong-payload controls receive the actual correct event and fail their positive
checks. The unchanged action fails its required positive event while no-name-event,
no-routing-event, unchanged-state and no-write controls pass across multiple
poll windows; actual `get output status` reads establish live polling. A separate
unconnected real observer cannot satisfy a positive event check. Tests also
exercise the narrow eligibility and refusal boundaries, exact single event
payload, record/WS schemas and API/sim/V2 attribution. The existing
`test_client_state.py` is unchanged.

## Verification and preservation

All commands use root Python
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
this checkout's `src` and root `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1` and
`PYTHONIOENCODING=utf-8`. Each pytest/docs/hook invocation gets a NEW empty
parent under coordinator-allocated `C:/t/ws040-20261029-a`, isolated data/config
and absent pytest basetemp. Raw logs, exit codes, JSON, command/env receipts and
remaining produced temp files are copied outside pytest retention and
SHA256-verified against still-existing originals. The hook JUnit path exception
and recovery are described below; that XML was initially missed at its unexpected
path before the first campaign preflight, but its original bytes survived and
were verified before any later pytest invocation. Managed shutdown removes its
disposable hub data by design; no archive of that removed scratch data is claimed.
Actual observed state/log evidence and surviving raw outputs are retained.
No originals, failed attempts or evidence are reconstructed or overwritten.

- Initial documentation checks: 489 passed in 2.90 s, exit 0, five existing
  documentation modules; route inventory/cache disabled. Private `docs-01/`.
- Focused new module: 13 passed in 17.57 s, exit 0. Actual managed positive
  pass/ok V2 and three deliberately wrong/absent-event fail/regression V2
  outcomes were inspected. Private `focused-01/` preserves all four raw records,
  logs and temp files. These expected failing controls are not qualification
  retries or product findings.
- Scoped Ruff: passed for runner, new scenario and new test module.
- Configured mypy `src/`: exit 0, no issues in 91 source files; private `type-01/`.
- Relevant WS/live/model regressions: 60 passed in 46.70 s, exit 0, including
  the new module's strengthened actual quiet-window poll-count assertion and
  unchanged `test_client_state.py`; private `relevant-01/`, all temp copies
  hash-verified before another test invocation.
- New module plus registry/evidence-schema checks: 49 passed in 19.39 s,
  exit 0, including all three coordinator-requested eligibility controls;
  private `registry-01/`, raw temp copies hash-verified. No ledger generation.
- Normal configured source commit/hook: full Ruff passed; **4,098 passed,
  six skipped, 35 deselected**, four deprecation warnings, 874.24 s; exit 0.
  `ROUTE_COVERAGE_STRICT=1`: **177/177 routes, 100%, zero uncovered**, verified
  from the actual JSON report. Private `hook-01/` retains stdout, exit, command,
  copied temp files and verified hashes. The hook was never bypassed or retried.
  Skips: two POSIX-only cases, unavailable HA dependencies, unavailable symlink
  creation, and two opt-in Chromium bridge cases. Hardware/Docker are deselected
  by configured defaults; HA/UC directories are excluded by the normal core hook.
- Source commit **`5331d5471a9d319c134e6798645d6ba8cf8466fc`** contains the
  runner exception, new scenario/test/report and coordinator-staged registry link.
- Clean committed-source `campaign-02`: run exit 0, one API/sim **V2 pass/ok**,
  **nine checks passed**, zero failed/n/a checks. Both pre/post Git status are
  clean and recorded source is exactly `5331d5471a9d319c134e6798645d6ba8cf8466fc`.
  Actual validator PID 65624, command/environment/start/exit receipts and managed
  hub/simulator logs are in private `campaign-02/`; an immediate byte-verified
  copy is in `campaign-02-copy/`. Inspection validated record/WS schemas, all
  six actual JSON messages, exactly one post-action `{"output":1,"name":"Den TV"}`
  event, zero routing events/writes and only `outputs[0].name` changed. The
  positive WS check precedes hub REST readback. Private record SHA256:
  `7591de8ce9e152fceb18af12668b9593f6afbba7af2996a4adb4a7c1a089e3b2`.
- Actual global gate **exit 1** at the same clean source:
  `python -m tools.validate check --evidence build/software-waves/SW-API-READ-03-C1/campaign-02/run/evidence --run-summary build/software-waves/SW-API-READ-03-C1/campaign-02/run/run-summary.json --expect-clients api`.
  Inputs are the committed `docs/validation/evidence` tree plus that one campaign
  record and its one-outcome summary, with the registry/findings at source5331.
  Sole reported failure: `(b) F-SEC-007 dropped below its recorded level:
  level V2 < recorded V3`. Original `gate-01/check.log`, exit, command/process
  checkpoint and hash-verified `gate-01-copy/` remain private. No gate retry,
  scoped substitute pass, metadata change or baseline comparison was performed.
  Baseline/preexistence and causal attribution remain **unverified**.
- Final report-only documentation checks: 489 passed in 2.88 s, exit 0,
  fresh `docs-02` temp/basetemp, route inventory/cache disabled; original log,
  JUnit, command/exit and verified temp copies retained privately. UTF-8,
  CR-aware whitespace and sole-report follow-up scope checks passed. The
  report-only commit uses invocation-only `git -c core.hooksPath= commit`
  under the documented exception; persistent hook configuration is unchanged.
  No repeated full source-hook or runtime pass is inferred from this exception.

Coordinator answer `msg_62db40fc2e26` to question `msg_5045ae513e2a` directs
this failed delivery with explicit partial functional success and unmet actual
global-gate acceptance. It authorizes the documented report-only hook exception
after scoped checks; source acceptance, review, integration and admission stay held.

## Receipt-path failure and authorized recovery

The normal hook's `PYTEST_ADDOPTS` used a native backslash JUnit path. Pytest's
argument parsing stripped the backslashes and wrote one XML in an unexpected
untracked directory directly beneath this child root. The first post-hook XML
read failed, and `campaign-01`'s clean-checkout assertion then failed **before
starting the validation CLI, hub or simulator**. This is a real preflight failure,
not a scenario run or a failed scenario retry. Original tool error/preflight stderr
is retained in the private native transcript only; no standalone log is recreated.
The original campaign-01 launcher, empty temp/artifact paths and existing copy
manifests remain distinct and unchanged.

The surviving original JUnit XML is 549,050 bytes, SHA256
`bd1c3098b41194c3bafee934809eacd7375c904f0cb673de2c7f9d1544d4c930`.
It was copied and hash-verified in `hook-junit-original-copy/`. Coordinator
`msg_6af3554e3454` independently verified that exact sole file and authorized
only an exact preservation-first `Move-Item` of its generated directory into
NEW `hook-junit-relocated/`, after immediate absolute source/destination
containment, absence, no-reparse-point and file/hash checks. Relocated bytes
and the independent copy match; `hook-junit-relocation.json` retains the receipt.
No directory was deleted and no generic cleanup occurred. The coordinator then
authorized one fresh campaign-02 with forward-slash paths and full output capture;
it passed as described above. No hook rerun or source correction was needed.

Registry question `msg_f82d03cb5b47`, answered in `msg_fe753eca38d2`, completed
the blocking handshake. The coordinator alone edited and staged the exact
`sw_api_read_03_c1.output_name_change -> F-API-040` scenario link in this child.
This is composite authorship: the author wrote the runner/scenario/test/report;
the coordinator contributed the registry mapping. The author did not edit or
stage the registry. Coordinator-observed registry SHA256 changed from
`a8c6d592bbded20af6d2b8d587c5ce81a48bf98931b0372727e09a261b0cdc8e` to
`df2f1662c94306f1e107734c0c7190ab95b21d7350ccf13e1299bebd4c7196af`.
No current/target/basis/evidence/finding/ledger changes are authorized.
The report-only follow-up preserves the exact source/scenario/test/registry
blobs from source5331. Its final commit SHA is delivered through worker_done;
the source commit and original report checkpoint remain in Git history.
Private `final-receipt.json`, `external-temp-manifest.json` and
`artifact-manifest.json` record final heads/status, placement/junction metadata
and retained file hashes; native transcript/full bundle/task-ref preservation
and Orca settlement remain coordinator-owned, not claimed complete by this worker.

All `build/software-waves/SW-API-READ-03-C1/` raw artifacts are PRIVATE and
admission HOLD because simulator fixture state/logs may carry credentials under
VAL15. Initial broad ORCA environment discovery also inadvertently included
runtime launch/hook field values in the native tool transcript. Only that field
category is recorded here; no values were copied to tracked files or operational
receipts. The coordinator was notified and instructed preservation of unchanged
private originals. Subsequent discovery is restricted to named nonsecret fields;
no credential store was read, credentials changed or external messages sent.

No browser/V3, F-API-039/F-API-042, protocol connect/reply/heartbeat, physical/HIL,
visual, soak, field or release qualification is claimed. Prior API034 managed-
startup/lost-artifact gaps are outside this lease and remain unresolved. Product,
client/model/schema/shared fixture/manifests/locks/root-private data, canonical
evidence, ledger/findings and owner baselines remain unchanged. No publication,
merge, promotion, release or cleanup was performed. The coordinator owns final
preservation, task-ref publication and Orca settlement.
