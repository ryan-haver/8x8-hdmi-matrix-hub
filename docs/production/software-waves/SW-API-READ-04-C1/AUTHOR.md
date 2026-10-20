# SW-API-READ-04-C1 author record

Task `task_f21b82527590`, Dispatch `ctx_a3ed1a9562f1`, existing Run
`run_37205f6095b3`; terminal `term_a8811282-4acf-4cfe-8b50-0c1449511b3c`.
Base: `411c66429df3b813072e736c41c3a8aa83043a70`.
Branch: `ryan-haver/wp-sw-api-header-proof`; dedicated Windows Orca worktree.
Authorized model: Codex `gpt-6.1-sol` / high, no delegation, helpers or fallback.
Orca worker projection independently reports provider codex / model gpt-6.1-sol;
that control-plane receipt alone does not attest the native backend or effort.
Coordinator preserves the full native transcript and model proof separately.

## Implementation and boundaries

`ApiClient.request` retains its signature and three-item return. Each completed
exchange records case-normalized actual response header names and public values.
An explicit allowlist admits CORS, public security policy, content type and retry
values. Every other observed name remains present with `***` and is also listed
in `response_headers_redacted`; cookies, authorization, tokens, keys and unknown
headers never contribute raw values. Repeated values use aiohttp's complete
`getall` list joined with comma-space, so equality cannot silently select one.

`Response.headers` checks exact values using case-insensitive names;
`absent_headers` checks observed absence. Both fail without final API exchange
capture and redaction metadata, including for unsupported clients. Masked values
cannot prove equality, including equality to `***`, but disprove absence.
Descriptions and header diagnostics print names only. Existing status checks
still apply to browser clients; body subset matching remains API-only. Observer,
base client, event contracts, evidence writer and schema are unchanged.

The only new recorded environment key is explicit nonsensitive
`CORS_ALLOWED_ORIGINS`. Each new scenario supplies it, including the empty
default. No arbitrary environment values or PINs are added to evidence.

## Scenarios and coordinator mapping

All 13 IDs below have `clients=(api,)`, `targets=(sim,)`,
`features=(F-API-031,)`, no client features and no declared device writes:

- `sw_api_read_04.default_no_origin`
- `sw_api_read_04.default_same_origin`
- `sw_api_read_04.default_denied_origin`
- `sw_api_read_04.default_preflight`
- `sw_api_read_04.default_no_origin_preflight`
- `sw_api_read_04.default_denied_mutation`
- `sw_api_read_04.configured_allowed`
- `sw_api_read_04.configured_denied`
- `sw_api_read_04.configured_allowed_preflight`
- `sw_api_read_04.configured_denied_preflight`
- `sw_api_read_04.wildcard_origin`
- `sw_api_read_04.wildcard_no_origin`
- `sw_api_read_04.wildcard_preflight`

Exact covers are `COVERS` in the scenario module: shared `HUB_CORE`, actual
`src/rest_api/security.py` and `src/rest_api/core.py`, four leased tooling files,
the new scenario/test, and fixture data. The initial mapping message mistakenly
named nonexistent health.py; corrected to actual core.py before any commit.
Coordinator discovered the real IDs and authored/staged only
`F-API-031.scenarios` in `docs/validation/features.yaml`; message
`msg_57c5757a9e6d` explicitly authorizes including that staged delta. The author
does not edit the registry. Current level, basis, evidence and finding fields
stay as before; no evidence import, ledger generation or finding closure.

## Actual contract and limits

Source inspection found the app-wide chain rate limit → security → CORS.
All registered application routes inherit that chain; there are no subapps.
The focused audit enumerates actual registered method/path pairs without a
hardcoded count and exercises real OPTIONS on API read/write, UI, WS and unknown
paths. It proves common middleware application, not each handler/error branch.
The full normal hook independently measures actual complete route coverage.

CORS supplies methods `GET, POST, PUT, DELETE, OPTIONS`, allowed request headers
`Content-Type, X-API-Key, X-Admin-PIN`, max-age `86400`, and `Vary: Origin`.
Configured origins and same origin echo; a denied origin receives no allow-origin.
Explicit wildcard supplies `*`, including when Origin is absent. OPTIONS is an
actual preflight with method/header request fields and does not call the write
handler. A denied cross-origin mutation is rejected by the earlier security guard
with 403 before CORS. Scenarios assert headers together with unchanged device
state, no device writes and no protocol warnings; HTTP 200 alone proves nothing.

No CSP/frame/nosniff/referrer emitters exist in this source; that is an observation,
not an invented defect or newly promised feature. Coordinator confirmed this
scope in `msg_0e6639a83b09`. No real CORS defect was reproduced.
Parent SW-API-READ-04 retains ownership; F-API-032 is deferred. Runner preaction
WebSocket sync/schema checking does not qualify that feature. No browser V3,
image, hardware, release, physical HIL, soak or field approval is claimed.

## Verification checkpoint before source commit

Artifacts are exclusively under `build/software-waves/SW-API-READ-04-C1/`.
Root interpreter is `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`;
process-local `PYTHONPATH` points to this worktree's src then root, with own CWD.
Runtime campaigns use fresh isolated temp/data/config/output paths and loopback
simulator ports, never owner hardware or private runtime data.

- Initial focused pytest: exit 1, 21 passed / 1 failed / 14.51s. The failure was
  a test setup omitting required HubProcess arguments, corrected in owned test.
  Original log and temp evidence retained in `focused.log` and `focused-tmp`.
- Corrected focused command: `python -m pytest tests/validation/test_sw_api_read_04.py tests/validation/test_model.py tests/validation/test_runner_environment.py -q -p no:tests.route_inventory --basetemp=build/software-waves/SW-API-READ-04-C1/focused2-tmp`:
  exit 0, 45 passed / 35.51s; `focused2.log`. Includes real aiohttp response
  capture, wrong value, unexpected presence, case handling, absent observation,
  masked sensitive presence/equality, non-API clients and browser status controls.
- Actual real-runner negative scenarios produce two FAIL/regression evidence
  records, despite 200 statuses, beside one positive PASS; schema validation passes.
  These intentionally red observations remain diagnostic evidence under focused temp.
- `python -m mypy src`: exit 0, 91 source files, `mypy.log`.
- Scoped Ruff: initial import-spacing error corrected with scoped Ruff fix;
  subsequent exact six-file check passes.
- Uncommitted diagnostic campaign runs all 13 scenarios against actual run.py
  and simulator; output stays under `diagnostic`. Untracked sources may be missed
  by existing dirty detection: these diagnostics are not accepted clean proof.

The source commit must run the normal configured, unmodified full Ruff/core hook
with strict actual route inventory. Clean committed-source campaign, schema and
source/dirty/environment/null-image audits follow that commit. Final SHAs,
command receipts, counts and limits will be appended in a report-only follow-up.
Independent qualified DeepSeek Pro/default review at the exact submitted commit
remains mandatory; integration, publication and combined reruns belong to the
coordinator. Tool changes stale 14 auth and two of three root API records; the
coordinator will rerun all 14 plus all three at the combined candidate, retaining
old evidence and four unaffected preservation-feature attributions.
