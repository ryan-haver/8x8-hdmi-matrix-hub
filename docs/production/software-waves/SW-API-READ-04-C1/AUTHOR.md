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

## Final author verification

Checked source: **`7b07e1cb7e7eb29a38b55d3b050703149f1b797c`**, parent exactly
`411c66429df3b813072e736c41c3a8aa83043a70`. The final submitted tip adds only
this report update; its full SHA is recorded outside its own commit in
`build/software-waves/SW-API-READ-04-C1/submission.json` and the worker delivery.
Coordinator independently confirmed native **gpt-6.1-sol/high** in
`msg_9fa8c3ba36f0`; no helpers, delegation, other models or fallback were used.

The source commit changed exactly these eight tracked paths:

- `tools/validate/clients/api.py`
- `tools/validate/model.py`
- `tools/validate/runner.py`
- `tools/validate/stack.py`
- `tests/validation/scenarios/sw_api_read_04.py`
- `tests/validation/test_sw_api_read_04.py`
- `docs/validation/features.yaml` (coordinator-authored F-API-031 scenario list only)
- `docs/production/software-waves/SW-API-READ-04-C1/AUTHOR.md`

All product source, other scenarios/tests, evidence schemas/writer, registry
levels/basis/evidence/findings, ledger, manifests, locks and baselines remain
unchanged. Additional environment-only lease authorized own ignored
`node_modules/**`; artifacts remain in the assigned build subtree.

### Normal source hook, including retained failures

Actual command array for all three attempts was
`[git, commit, -m, "feat(validation): prove CORS headers from actual API exchanges"]`.
Configured hook remained
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.githooks/pre-commit`,
SHA-256 `e69e64194ca07a606718b5fea748f44a06ddf767b6f6756cef578b8565f544bc`.
No source, test or hook workaround was applied between attempts.

- First attempt: exit 1, Ruff passed; 2,142 passed / 2 skipped / 35 deselected,
  one fixture error, 314.14s. Temporary Git object write reproduced exit 128,
  `Filename too long`, in a 215-character repository path under own nested temp.
  Failed partial route report **109/177** and raw log remain in `source-hook/`.
- Second attempt used a fresh short OS temp: exit 1, Ruff passed; 3,816 passed /
  22 skipped / 35 deselected, one failure, 883.99s. Strict routes reached
  **177/177**, but JavaScript lint failed ESM resolution of `@eslint/js` because
  own worktree had no local dependencies. This remains a failed full run in
  `source-hook2/`; its route coverage alone does not make the run pass.
- Coordinator authorized an exact environment-only dependency lease through
  the blocking ask reply and `msg_acbcdaf86fd7`. Actual
  `npm ci --offline --ignore-scripts --no-audit --no-fund` exited 0, installed
  190 packages in 4s from cache. No network fallback, root dependency mutation,
  manifest or lock edit. Actual `npm run lint:js` exited 0; the previously failing
  focused pytest passed 1/1 in 6.99s with the partial route writer disabled.
  Logs are in `node-setup/`.
- Third attempt: exit **0**, normal full Ruff passed; **4,063 passed / 6 skipped /
  35 deselected / 4 warnings**, pytest 1,119.11s; actual strict route coverage
  **177/177**. Commit succeeded at the checked source SHA. Full log, command
  start/end, interpreter, configured hook, environment correction and route
  report are in `source-hook3/`. Source/test bytes were unchanged across attempts.

### Clean committed-source campaign and failed global freshness gate

Actual run command and subsequent check command arrays, start/end times and
exits are preserved in `clean/commands.json`; raw output is `clean/command-0.log`
and `clean/command-1.log`. The run exited **0**, all **13 API V2 scenarios passed**.
All **65 checks passed**: 52 declared checks plus 13 automatic observer-schema
checks. Those observer checks do not qualify F-API-032.

`clean/audit.json` verifies every original record against the schema, exact
scenario/client/features/covers, full source SHA, `dirty=false`, empty dirty
files, actual run.py entry, simulator source fingerprint, explicit per-case
CORS config (including empty default), null image digest, empty state diff and
no mutated device command. It retains SHA-256 hashes of all 13 original record
bytes and actual public header observations. Evidence is exclusively under
`clean/campaign/evidence/F-API-031/`; nothing was imported or relabelled.

The subsequent **global formal check exited 1** with the sole reported reason:
`F-SEC-007 dropped below its recorded level: level V2 < recorded V3`.
The shared tooling changes stale the existing auth V3 evidence, exactly the
freshness dependency identified in the dispatch. Coordinator owns the reserved
**14 auth plus all 3 root API reruns against the actual combined candidate**.
This failed global gate is retained. The earlier uncommitted diagnostic gate
passed at the base HEAD and is not substituted for this source result. No old
passes are attached to changed source and no registry level or gate is weakened.

### Additional boundary observation and preservation

A synthetic-only readonly calibration of existing request redaction found that
`X-API-Key`, `Authorization` and `Cookie` values are masked, while literal
`X-Admin-PIN` survives `evidence.redact` and `Action.describe`. Receipt
`request-redaction-observation.json` stores booleans only, without credentials or
environment data; reported to coordinator as `msg_0b207923dadd`. This is an
existing writer/procedure boundary outside the lease. New CORS scenarios send
no credentials, and new response header values are masked at API capture.
No finding was registered or closed and the readonly writer was not changed.

Retained external test roots, which a worktree-only archive will not include:

- `C:/Users/ryanh/AppData/Local/Temp/c1-hook-v90b4ka3`: inventory **20,006 files /
  65,452,341 bytes**, `source-hook2/external-temp-inventory.json`.
- `C:/Users/ryanh/AppData/Local/Temp/c1-hook3-erf6axvs`: inventory **21,207 files /
  70,080,576 bytes**, `source-hook3/external-temp-inventory.json`.

Inventories hash each regular file and record symlinks without following them;
coordinator must include relevant external bytes in private preservation. An
initial third-inventory wrapper prefix assertion failed before output and was
corrected; receipt remains `source-hook3/inventory-first-attempt.json`. No
source or evidence was changed by that artifact-script correction.

The follow-up commits only this report, after whitespace and scope checks,
using the explicitly permitted invocation-only documentation hook exception.
It claims no new full-hook run. Source, scenario, test and mapping bytes remain
identical to the normal-hook source commit and clean campaign.

Author scope is complete. Qualified exact-tip different-family DeepSeek
Pro/default review, global freshness reruns, integration, evidence acceptance,
publication and worker preservation/settlement remain coordinator steps. The
global gate is currently failed; no browser/image/WS/hardware/release approval
is claimed.
