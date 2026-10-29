# SW-API-READ-03-C1: device-side output-name event proof

Implemented `sw_api_read_03_c1.output_name_change` for F-API-040, API/sim V2
only, with real managed simulator/hub regression controls. Independent qualified
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
and absent pytest basetemp. Raw logs, exit codes, JUnit/JSON, exact command/env
receipts and every produced temp file are copied outside pytest retention and
SHA256-verified against still-existing originals before another invocation.
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
- Normal configured source hook with strict full routes and clean committed-source campaign:
  pending at this source checkpoint; final outcomes will be appended after runs.

Registry question `msg_f82d03cb5b47`, answered in `msg_fe753eca38d2`, completed
the blocking handshake. The coordinator alone edited and staged the exact
`sw_api_read_03_c1.output_name_change -> F-API-040` scenario link in this child.
This is composite authorship: the author wrote the runner/scenario/test/report;
the coordinator contributed the registry mapping. The author did not edit or
stage the registry. Coordinator-observed registry SHA256 changed from
`a8c6d592bbded20af6d2b8d587c5ce81a48bf98931b0372727e09a261b0cdc8e` to
`df2f1662c94306f1e107734c0c7190ab95b21d7350ccf13e1299bebd4c7196af`.
No current/target/basis/evidence/finding/ledger changes are authorized.
No source commit or clean campaign is yet claimed in this checkpoint.

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
