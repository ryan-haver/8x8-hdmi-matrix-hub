# SW-API-READ-04-C1 independent review

Reviewer: DeepSeek `deepseek/deepseek-v4-pro` / default (different underlying
family from the Sol 6.1 / high author). Report-only; authors fix, reviewers report.

## Reviewed object

| Field | Value |
| --- | --- |
| Candidate tip | `cb87427bd2646fc686e1cff02692a4240dcf51c1` |
| Functional source | `7b07e1cb7e7eb29a38b55d3b050703149f1b797c` (parent `411c6642`) |
| Base | `411c66429df3b813072e736c41c3a8aa83043a70` |
| Candidate delta | `cb87427b` adds only the `AUTHOR.md` report update (116 lines) on top of `7b07e1cb` |
| Review worktree | `ryan-haver/wp-sw-api-header-review`, clean, exact head |
| Run / route | `run_37205f6095b3`, configured pinned DeepSeek Pro route (no Anthropic/helpers/MCP/subagents) |

## Scope and boundary audit

`git diff --name-status 411c6642..cb87427b` shows exactly eight paths, no more:

- `tools/validate/clients/api.py` (+17) — response-header capture + public allowlist + masking
- `tools/validate/model.py` (+14/-4) — `Response.headers` / `Response.absent_headers`
- `tools/validate/runner.py` (+25) — fail-closed header equality/absence assertion
- `tools/validate/stack.py` (+2/-1) — `CORS_ALLOWED_ORIGINS` added to `RECORDED_ENV`
- `tests/validation/scenarios/sw_api_read_04.py` (+67, new) — 13 F-API-031 scenarios
- `tests/validation/test_sw_api_read_04.py` (+184, new) — HTTP/privacy/negative controls
- `docs/validation/features.yaml` (1 line) — coordinator-authored F-API-031 scenario list only
- `docs/production/software-waves/SW-API-READ-04-C1/AUTHOR.md` (+237) — author report

`src/rest_api/app.py`, `src/rest_api/security.py`, evidence schema/writer,
root manifests, lockfiles and baselines are **unchanged**. The CORS middleware
(`cors_middleware` in `app.py`) and `allowed_origin`/`security_middleware` are
pre-existing product behavior; this package proves it, it does not implement it.

## Findings

No blocking or product findings. The following are informational observations,
recorded for completeness; none prevents acceptance of the named source scope.

| # | Severity | Observation | Source / counterexample |
| --- | --- | --- | --- |
| 1 | Info | The deny-mutation 403 carries no CORS headers because `cors_middleware` never
reaches its header step when an outer middleware raises. This holds for *either*
middleware ordering, so that single assertion alone does not prove ordering. | `runner.py` header step is post-handler; `security_middleware` raises `HTTPForbidden` before calling `handler`. I independently confirmed the actual order (see below), so the author's "security before CORS" claim is accurate, not merely asserted. |
| 2 | Info | Non-CORS response headers (`content-length`, `date`, `server`) are masked to `***` because they are absent from `PUBLIC_RESPONSE_HEADERS`. Harmless and conservative; it means those values can never be asserted. | `clients/api.py` allowlist; observed in campaign records. |
| 3 | Info | `test_global_middleware_topology_and_representative_preflight` reads the private `app._subapps`. Test-internal coupling to aiohttp internals; acceptable, not product code. | `test_sw_api_read_04.py`. |
| 4 | Info | The public allowlist admits CSP/X-Frame-Options/HSTS/referrer/permissions headers for capture, but no scenario asserts them. No invented CSP/frame/nosniff requirement is introduced (F-API-031 is CORS only). | `clients/api.py` vs `sw_api_read_04.py`. |

## What I verified (source-level)

- **Case-insensitive names, exact values.** `runner.py` builds
  `actual = {name.lower(): value ...}` and compares `actual.get(name.lower()) != value`,
  and `redacted = {name.lower() ...}`. Names fold, values are exact.
- **Fail-closed boundaries.** The header step fails when `client.name != "api"`,
  when `exchange.get("status") != result.status` (final-exchange/status-mismatch),
  or when `response_headers`/`response_headers_redacted` are not a dict/list
  (missing capture). An earlier request cannot fill the gap: only
  `result.requests[-1]` is consulted.
- **Masked presence disproves absence, never proves equality.** A masked header
  stays in `actual` (value `***`) so `absent_headers` fails, and its name stays in
  `redacted` so `headers` equality fails — including equality to `***`.
- **Masking happens at capture, before redact/artifacts.** `clients/api.py` writes
  `***` for every non-allowlisted name and records it in
  `response_headers_redacted`; `evidence.redact` is a second, key-based layer.
- **Return signature preserved.** `ApiClient.request` still returns
  `(status, parsed, record)`; `Response.json` subset matching remains gated on
  `client.name == "api"`; browser status semantics unchanged.
- **Env recording bounded.** The only `RECORDED_ENV` change is
  `CORS_ALLOWED_ORIGINS`; no arbitrary/secret env export. `ADMIN_PIN` is absent
  from `recorded_env()` (verified by the test).
- **Middleware topology.** Empirically confirmed `[rate_limit, security, cors]`
  list order and aiohttp's reversed wrapping: request order is
  rate_limit → security → cors → handler, so a denied cross-origin mutation is
  rejected by the earlier guard with 403 before CORS adds headers.
- **Covers.** `COVERS = HUB_CORE + security.py + core.py + 4 leased tooling files
  + new scenario/test + fixture data`. `HUB_CORE` already includes
  `src/rest_api/app.py` (the CORS middleware), so app-level CORS changes would
  stale this evidence. `core.py` covers the one handler actually invoked
  (`handle_health`); `control.py` is not needed because OPTIONS and denied
  mutation never reach `handle_switch`.

## What I ran (own source, isolated short temp)

| Command (exit) | Result |
| --- | --- |
| `python -m pytest tests/validation/test_sw_api_read_04.py -q -p no:tests.route_inventory --basetemp=<short temp>` (0) | **22 passed** in 15.56 s — real aiohttp exchange oracles (case/absent/redacted), missing-observation fail-closed (5 mutations), sensitive-value non-persistence, non-API clients, browser status/API-only body, config recording, global middleware topology + representative OPTIONS, real-runner negative FAIL evidence. |
| `python -m tools.validate run --target sim --client api --feature F-API-031 --out build/software-waves/SW-API-READ-04-C1-review/campaign` (0) | **13/13 PASS**, V2, `dirty=false`, commit `cb87427b`. |
| Record inspection (script `inspect_records.py`) | Per-record: `state_diff=[]` (no device writes), correct allow-origin per case, `CORS_ALLOWED_ORIGINS` recorded, `image_digest=null`, `screenshots=[]`. |
| Middleware probe (`mwprobe.py`) | Confirmed list/wrap order and a real denied POST `/api/switch` → **403 with empty CORS/Vary headers**. |

### Observed per-scenario allow-origin (independent campaign)

| Scenario | status | allow-origin | env |
| --- | --- | --- | --- |
| default_no_origin / default_denied_origin | 200 | absent | '' |
| default_same_origin | 200 | `http://hub.local` (echo) | '' |
| default_preflight / default_no_origin_preflight | 200 | absent | '' |
| default_denied_mutation | **403** | absent (all CORS headers absent) | '' |
| configured_allowed / configured_allowed_preflight | 200 | `https://allowed.example` | `https://allowed.example` |
| configured_denied / configured_denied_preflight | 200 | absent | `https://allowed.example` |
| wildcard_origin / wildcard_no_origin / wildcard_preflight | 200 | `*` | `*` |

All 13 records show no device-state mutation and no write command; the WS
observer-schema check is automatic and does not qualify F-API-032.

## Acceptance disposition

**ACCEPT** the named source implementation (`7b07e1cb`, unchanged in candidate
`cb87427b`) for F-API-031 CORS header proof at **API/simulator V2 only**, with
the explicit boundary below. No findings require author correction.

**Boundary (explicit, not conditional approval).** The global formal check exits
1 solely because the four changed tooling paths (`api.py`, `model.py`,
`runner.py`, `stack.py`) stale the existing F-SEC-007 browser V3 evidence
(V2 < recorded V3), exactly the known freshness dependency. This is a required
evidence refresh owned by the coordinator (14 auth + all 3 root API reruns at the
actual combined candidate), not a waiver and not a source defect. I do **not**
preapprove future records, and I do not claim release qualification. F-API-032
remains deferred; this is not browser V3, image, HIL, soak, field, or final
release proof. No CSP/frame/nosniff requirement is invented.

## Commands and receipts

- Interpreter: `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe` (Python 3.12.10).
- `PYTHONPATH` (process-local): `<review worktree>/src;<review worktree>`.
- Focused log and campaign evidence are under
  `build/software-waves/SW-API-READ-04-C1-review/` (new, review-owned).
