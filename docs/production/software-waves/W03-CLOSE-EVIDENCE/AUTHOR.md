# W03-CLOSE-EVIDENCE author record

## Outcome and authority

Fresh combined-source evidence collection **PASS** on exact clean source
`310d8b65a9fce3c9069523d4ac5ce21157e75c9f`: **31/31 outcomes**, **200 passing
checks**, **six expected client-specific n/a checks**, **32 screenshots**, no
failed, blocked or skipped scenario. The global formal check also passed,
with zero known failures. This report alone is committed after execution.

- Task `task_4a90a94be3a3`, Dispatch `ctx_aa530b51696d`, existing Run
  `run_37205f6095b3`; own terminal `term_f36b71e4-d506-4021-b50e-3440f8406b18`.
- Live coordinator: `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`. Owner authorized
  the resumed accepted wave03 closeout on 2026-10-26. No new phase debate,
  historical approval, launch, helper, fallback or nested worker was inferred.
- Dedicated worktree:
  `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-w03-close-evidence`;
  branch `ryan-haver/wp-w03-close-evidence`; actual initial HEAD and merge-base
  both equal the immutable source above; initial porcelain status empty.
- Requested **and effective** Orca control-plane selection: **Codex
  gpt-6.1-sol / high**, as recorded by this live Dispatch's `worker-show.json`.
  The receipt proves selection and observed live worker identity, not independent
  native backend attestation. No unsupported model variant, other family,
  Anthropic, MCP helper or delegation was used by this worker.
- Coordinator-supplied capacity at 2026-10-26T22:22Z: managed Codex current pool
  96% weekly remaining, reset 2026-11-02T06:13:28Z; shared external commitments
  unreported. Coordinator owns refresh and independent review. Work completed
  within the dispatched 40-minute budget; no new spend or routing was initiated.
- Exclusive tracked write: this new report. All runtime proof preceded this
  write, with `dirty: false`, `dirty_files: []` in every original record and
  empty whole-worktree porcelain status at command starts and final audit.
  Allocation ledger and canonical integration records remain coordinator-owned.

## Provenance and environment

The accepted original CORS source remains attributed to Sol 6.1/high at
`7b07e1cb7e7eb29a38b55d3b050703149f1b797c`, independently reviewed by DeepSeek
Pro/default. The accepted offline correction remains attributed to DeepSeek
Pro/default at `3788353ef2ef92cf52cf266f3e356dd6840d00da`, independently reviewed
by Sol 6.1/high at candidate `4baef5743b0e970328a979f181d701361f58da70`.
Read the original [CORS author](../SW-API-READ-04-C1/AUTHOR.md),
[CORS review](../SW-API-READ-04-C1/REVIEW.md),
[offline author](../SW-API-CLIENT-02-C1/AUTHOR.md) and
[offline review](../SW-API-CLIENT-02-C1/REVIEW.md) for their actual scope.
These new executions retain their own combined source/client attribution;
no original evidence bytes, author identity, timestamp or image digest changed.

All private artifacts are under this worktree's new ignored
`build/phase-resume-20261026/evidence/` (abbreviated `E` below). Python:
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
3.12.10, Windows 11. Process-local `PYTHONPATH` was **this worktree's src, then
this worktree**, never root source. Node v24.22.1, npm 11.19.1, locked Playwright
1.63.0, actual Chromium 153.0.8010.12. Local
`npm ci --offline --ignore-scripts --no-audit --no-fund` exited 0, installed
190 packages; manifests, lockfiles and global configuration were untouched.
Existing installed Chromium was used; no browser download was needed.

`MATRIX_DATA_DIR=E/runtime-data`, `UC_CONFIG_HOME=E/uc-config` were fresh isolated
locations; focused pytest jobs had separate offline/docs data and config paths.
`TEMP` and `TMP` pointed to the new, previously absent, preserved task directory
`C:/Temp/hdmi-w03-evidence-20261026`. The runner starts its existing simulator
and real `run.py -> hub.cli shared runtime (UC_ENABLED=false)` on disposable
loopback ports, copies fixture data into isolated hub data, and controls only
that simulator. Simulator fingerprint: `23f7439ea94f5fcc`, seed
`tools/simulator/states/default.json`. No existing owner simulator, LAN device,
hardware, private root data or other worktree was changed. Every image digest
is null; API/CORS proof remains V2 and actual browser proof V3.

Initial `run --help` discovery preceded `PYTHONDONTWRITEBYTECODE=1` and left
incidental ignored bytecode caches at `tools/__pycache__`,
`tools/validate/__pycache__` and `tools/validate/clients/__pycache__`.
They were disclosed to the coordinator, inventoried and preserved; no tracked
source changed. Later Python executions disabled bytecode writes. No cleanup
or global setting change was used to conceal this incidental scope deviation.

## Count reconciliation and behavioral inspection

| Campaign | Outcomes | Client/level | Passing checks | Expected n/a |
| --- | --- | --- | --- | --- |
| Auth F-SEC-007 | 14/14 | 6 API V2 + 8 real Chromium V3 | 108 | 6 |
| Root/info API | 3/3 | API V2 | 20 | 0 |
| CORS | 13/13 | API V2 | 65 | 0 |
| Unreachable switch | 1/1 | API V2 | 7 | 0 |
| Total | 31/31 | 23 API + 8 Chromium | 200 | 6 |

The eight `sw_sec_auth_01` IDs produce **12**, not 14, outcomes: four wrong/allowed
IDs run in API and browser (eight), and four locked/per-item IDs run in browser
(four). Existing registry-mapped `security_hardening.profile_wrong_pin` and
`security_hardening.scene_wrong_pin` add the remaining two API outcomes.
Coordinator confirmed this original F-SEC-007 selection through the blocking
question. No new scenario or duplicated result was invented to reach 14.
The three root reads are `contracts.api_info`, `contracts.api_root`, and
`contracts.api_root_alias`; all 13 `sw_api_read_04` IDs are API-only.
Thus the expected **14 + 3 + 13 + 1 = 31** exactly matches observed outcomes.
The 18 existing offline pytest controls below are separate tests, not additional
scenario records or browser qualification. Six n/a checks reflect API-only
JSON body or browser-only toast expectations, not skipped scenarios.

`campaign-audit.json` inspects the original serialized records against the JSON
schema and actual scenario/client/features/covers, rather than trusting process
exit. It verifies full source SHA/cleanliness, null image digests, explicit CORS
configuration, captured response header/redaction metadata, page-origin request
provenance, actual GUI click procedures, simulator state effects and screenshot
existence/PNG signatures. Every record and all 32 PNGs have SHA-256 hashes.
`command-state-audit.json` independently inspects raw device logs: all refusals,
reads and unreachable routing have **no mutating command**; each of six allowed
auth controls has exactly one `video switch`, with routing from 2 to 6 (profile
peer to 7), plus the pre-existing enabled/audio-setting commands. No other
state change occurred. Both audits have zero errors.

All eight browser outcomes used the shipped UI in real Chromium: Profiles tab
Activate or dashboard/settings Scenes Execute, actual prompt handling, real
page HTTP requests and visible success/error feedback. Four lockout/per-item
cases each capture five actual 403 invalid_passcode clicks, a 429 passcode_locked
probe and positive Retry-After equal to the body; the two peer controls still
execute independently. Screenshots comprise four ordinary after frames and
four sequences of five wrong-PIN, one locked and one after frame: 32 total.
Manual image inspection confirmed readable profile/scene Invalid passcode and
final timed-lockout error messages. Intermediate screenshots are observations,
not approval of every frame or a visual baseline. The historical after-only
health controls do not newly prove during-PBKDF2 latency, reset or expiry.

The unchanged `failures.unreachable_switch` fault-in-command scenario observed
**HTTP 500**, body `Failed to switch routing`, `switch_failed` with input 3/output
1, unchanged simulator state and no successful mutation. The attempted video
switch is logged with `fault: drop_http`. Its subsequent `/api/status` read is
503 with success false; health reports matrix.connected false. Seven checks pass,
including seven WebSocket messages schema-checked. This is distinct from a
request submitted when the matrix is **already offline**.

The existing `tests/sim/test_sim_offline_switch_events.py` supplied that latter
boundary: **18 passed in 5.66 s**, exit 0, no skips, partial route inventory
writer disabled. Actual aiohttp/simulator tests cover already-disconnected
single/all/alternate routes with 503 and failure events, malformed/invalid
no-event refusals, unconfigured valid/invalid routes, unavailable oversized-body
503 versus connected opaque 500, connected positive routing, and inside-command
failure. These tests use actual app fixtures and simulator; no new probe/tool,
scenario, fixture, source hack or standalone already-offline scenario was added.

## Exact commands, raw output and per-record counts

`E/<campaign>-receipt.json` preserves exact argv, CWD, source/dirty state,
start/end UTC, process environment and exit; `E/<campaign>.log` is raw output.
Each destination was absent before execution. Original run summaries are
`E/{auth,api-root,cors,offline}/run-summary.json`, original records/screenshots
under each campaign's `evidence/`, and original hub/simulator logs in `logs/`.
The original auth AUTHOR's feature selector was expanded to its actual ten
registry-mapped IDs; the exact executed arguments follow, with all four exits 0.

### auth

```text
C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe -m tools.validate run --target sim --client api --client browser --scenario security_hardening.profile_wrong_pin --scenario security_hardening.scene_wrong_pin --scenario sw_sec_auth_01.profile_wrong_pin --scenario sw_sec_auth_01.profile_allowed --scenario sw_sec_auth_01.profile_locked --scenario sw_sec_auth_01.profile_per_item --scenario sw_sec_auth_01.scene_wrong_pin --scenario sw_sec_auth_01.scene_allowed --scenario sw_sec_auth_01.scene_locked --scenario sw_sec_auth_01.scene_per_item --out build\phase-resume-20261026\evidence\auth
```

UTC 2026-10-26T22:25:51.407921+00:00 to 2026-10-26T22:27:11.162644+00:00; exit 0.

### api-root

```text
C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe -m tools.validate run --target sim --client api --scenario contracts.api_info --scenario contracts.api_root --scenario contracts.api_root_alias --out build\phase-resume-20261026\evidence\api-root
```

UTC 2026-10-26T22:27:11.164689+00:00 to 2026-10-26T22:27:14.973339+00:00; exit 0.

### cors

```text
C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe -m tools.validate run --target sim --client api --scenario sw_api_read_04.default_no_origin --scenario sw_api_read_04.default_same_origin --scenario sw_api_read_04.default_denied_origin --scenario sw_api_read_04.default_preflight --scenario sw_api_read_04.default_no_origin_preflight --scenario sw_api_read_04.default_denied_mutation --scenario sw_api_read_04.configured_allowed --scenario sw_api_read_04.configured_denied --scenario sw_api_read_04.configured_allowed_preflight --scenario sw_api_read_04.configured_denied_preflight --scenario sw_api_read_04.wildcard_origin --scenario sw_api_read_04.wildcard_no_origin --scenario sw_api_read_04.wildcard_preflight --out build\phase-resume-20261026\evidence\cors
```

UTC 2026-10-26T22:27:14.974345+00:00 to 2026-10-26T22:27:22.921470+00:00; exit 0.

### offline

```text
C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe -m tools.validate run --target sim --client api --scenario failures.unreachable_switch --out build\phase-resume-20261026\evidence\offline
```

UTC 2026-10-26T22:27:22.923522+00:00 to 2026-10-26T22:27:27.591717+00:00; exit 0.

| Scenario | Client | HTTP | Passing checks | n/a |
| --- | --- | --- | --- | --- |
| `security_hardening.profile_wrong_pin` | api | 403 | 5 | 0 |
| `security_hardening.scene_wrong_pin` | api | 403 | 5 | 0 |
| `sw_sec_auth_01.profile_allowed` | api | 200 | 8 | 0 |
| `sw_sec_auth_01.profile_wrong_pin` | api | 403 | 7 | 1 |
| `sw_sec_auth_01.scene_allowed` | api | 200 | 8 | 0 |
| `sw_sec_auth_01.scene_wrong_pin` | api | 403 | 7 | 1 |
| `sw_sec_auth_01.profile_allowed` | browser | 200 | 7 | 1 |
| `sw_sec_auth_01.profile_locked` | browser | 429 | 9 | 0 |
| `sw_sec_auth_01.profile_per_item` | browser | 200 | 11 | 0 |
| `sw_sec_auth_01.profile_wrong_pin` | browser | 403 | 7 | 1 |
| `sw_sec_auth_01.scene_allowed` | browser | 200 | 7 | 1 |
| `sw_sec_auth_01.scene_locked` | browser | 429 | 9 | 0 |
| `sw_sec_auth_01.scene_per_item` | browser | 200 | 11 | 0 |
| `sw_sec_auth_01.scene_wrong_pin` | browser | 403 | 7 | 1 |
| `contracts.api_info` | api | 200 | 4 | 0 |
| `contracts.api_root` | api | 200 | 8 | 0 |
| `contracts.api_root_alias` | api | 200 | 8 | 0 |
| `sw_api_read_04.configured_allowed` | api | 200 | 5 | 0 |
| `sw_api_read_04.configured_allowed_preflight` | api | 200 | 5 | 0 |
| `sw_api_read_04.configured_denied` | api | 200 | 5 | 0 |
| `sw_api_read_04.configured_denied_preflight` | api | 200 | 5 | 0 |
| `sw_api_read_04.default_denied_mutation` | api | 403 | 5 | 0 |
| `sw_api_read_04.default_denied_origin` | api | 200 | 5 | 0 |
| `sw_api_read_04.default_no_origin` | api | 200 | 5 | 0 |
| `sw_api_read_04.default_no_origin_preflight` | api | 200 | 5 | 0 |
| `sw_api_read_04.default_preflight` | api | 200 | 5 | 0 |
| `sw_api_read_04.default_same_origin` | api | 200 | 5 | 0 |
| `sw_api_read_04.wildcard_no_origin` | api | 200 | 5 | 0 |
| `sw_api_read_04.wildcard_origin` | api | 200 | 5 | 0 |
| `sw_api_read_04.wildcard_preflight` | api | 200 | 5 | 0 |
| `failures.unreachable_switch` | api | 500 | 7 | 0 |

## Formal and documentation checks

The formal command used all four fresh evidence roots and the actual auth
summary for expected API/browser participation; the audit separately verified
all four original summaries and all 31 outcomes. It also scans committed evidence
and registry recorded-level consistency. No canonical import or ledger writer ran.

```text
C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe -m tools.validate check --evidence build\phase-resume-20261026\evidence\auth\evidence --evidence build\phase-resume-20261026\evidence\api-root\evidence --evidence build\phase-resume-20261026\evidence\cors\evidence --evidence build\phase-resume-20261026\evidence\offline\evidence --run-summary build\phase-resume-20261026\evidence\auth\run-summary.json --expect-clients api,browser
```

UTC 2026-10-26T22:27:39.653317+00:00 to 2026-10-26T22:31:43.859571+00:00; **exit 0**,
`[validate] gate OK (0 known failure(s) linked to open findings)`.

There was no failing qualification attempt or behavioral retry in this task.
Original prior failed source runs and evidence remain unchanged. Read-only
Windows rg wildcard discovery errors and a rejected informational Orca send
(`--type message`, unsupported, no enqueue) are disclosed in
`discovery-attempt-notes.txt` and the native transcript; corrected supported
read/status commands did not alter runtime behavior.

The following existing checks both exited 0; full command arrays and raw logs
are in the corresponding receipt/log pairs:

```text
C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe -m pytest tests/sim/test_sim_offline_switch_events.py -p no:tests.route_inventory -p no:cacheprovider --basetemp=C:/Temp/hdmi-w03-evidence-20261026/offline-pytest -q --tb=short
```

UTC 2026-10-26T22:27:21.214443+00:00 to 2026-10-26T22:27:27.956219+00:00; exit 0.

```text
C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -q -p no:tests.route_inventory -p no:cacheprovider --basetemp=C:/Temp/hdmi-w03-evidence-20261026/docs-pytest
```

UTC 2026-10-26T22:30:54.108702+00:00 to 2026-10-26T22:30:59.891764+00:00; exit 0.

Documentation suite: **489 passed in 4.85 s**, no skips, isolated data/config,
mock matrix, no cache provider and partial route inventory disabled. It ran on
clean source before this report was written. This report subsequently receives
local link/path, CR-aware whitespace, exact staged-path and source-identity
checks. The one prose-only commit uses the explicitly authorized invocation-only
`git -c core.hooksPath= commit` exception after those checks. No normal source
hook/full combined pipeline is claimed or bypassed for implementation.

## Preservation and remaining coordinator work

Preserve the full ignored `E` tree, local `node_modules`, incidental caches,
external task temp directory and native transcript. `external-and-cache-inventory.json`
is the earlier 916-file/1,841,381-byte external-temp checkpoint before docs tests,
plus the three cache inventories; final preservation inventory captures later
files separately. Neither destination is overwritten or removed. Submitted SHA
and final path audit are recorded in `submission.json` outside the commit it
identifies and in the required worker delivery.

No tracked source/test/scenario/fixture/config/registry/ledger/manifest/lock/
guide/evidence/baseline changes occurred. No evidence import, level promotion,
source correction, new implementation/test tool, ledger generation, push, merge,
tag, worktree cleanup, hardware/LAN/device write, image build, HIL, soak, field
or final-release action occurred. Only this new prose report is committed.
Existing source/client attribution and original acceptance remain intact.

Canonical import, finding/registry reconciliation, serial ledger and registry
checks, independent evidence/assembly acceptance, full applicable combined
pipeline, integration publication and exact remote equality remain coordinator
steps. Root's later bookkeeping commit is docs-only and is not substituted for
this campaign's source SHA. The worker neither self-releases nor removes any
resources; coordinator preserves full artifacts/native/bundle and settles the
owned worktree. No source or campaign blocker remains in this bounded task.
