# PRIV-M3-ASSESSMENT: first MiniMax privacy-review domain candidate report

This is an **independent, first new-family (MiniMax `minimax-coding-plan/MiniMax-M3`,
configured thinking) review-domain candidate** over the complete corrected
SW-SEC-DATA-02 privacy chain. It is **not** source acceptance, **not** privacy
qualification, **not** evidence admission and **not** a release gate. It grants
nothing to itself: the six frozen axes are judged afterwards by ONE independent
`gpt-6-astra/high` judge, and only an actual qualified PASS could ever open the
separate full-chain source review and the report-quality evaluation.

The delivered chain's own contract, the original author reports and the earlier
failed Opus assessment/judgement are treated as **attributed supplied inputs**.
Everything below was produced by my own reads and my own probes; no conclusion
is copied from a supplied source, and no novel-defect quota was applied.

## 1. Authority, bindings and provenance

| Item | Value actually verified in this run |
| --- | --- |
| Exact base / HEAD | `5385325722a39e6dd766352489f828f5e54b56d5` (measured `git rev-parse HEAD`, `p08-origins`) |
| Branch / worktree | `qualification/recovery-privacy-m3` in `wp-recovery-privacy-m3-assess` |
| Chain base | `d6e78e0b6ab1dab5216443584d810a7a24af32b2` |
| Chain commits (8) | `8b9f5623`, `11f305b1`, `47b0bbb8`, `615d3c84`, `8fc65e05`, `2d02004d`, `01ca5572`, `53853257` — set-equal to the frozen packet's list (`p12-provenance`); the packet lists them chronologically, `git log` lists them reversed, so the first comparison reported "not equal" for ordering only |
| Changed paths (13) | Exactly the packet's 13 paths; **every** path's blob SHA-256 matches the packet's `git_blob_sha256` (`p12-provenance`, `all_paths_match=true`) |
| Subject packet | `.../recovery-execution/WAVE_B_SUBJECT_PACKET.json`, SHA-256 `7a6256111da21e71aee2f3ad315a646f7e3b6e088c45a3d4ee18dcf222c66763` — matches the required digest exactly |
| Adopted plan digest | `f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e` (as recorded in the packet) |
| Git authorship | All 8 commits are authored `Ryan Haver <13879652+ryan-haver@users.noreply.github.com>`; Git identity is **not** model attribution. The source family is the coordinator's attested OpenAI `gpt-6.1-sol/high` (private receipts `source-waveA/privacy-c4-closeout` and the earlier source-authorship attestation, which I did not read or re-attest) |
| My own route | Task `task_eef2d2e8f289`, Dispatch `ctx_b6947db9e4fd`, worker `term_30f38e9d-a5b4-413a-bd90-af611e5e7abe`, coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`; actual model `minimax-coding-plan/MiniMax-M3` with inherited thinking (CLI effort override unsupported); no helper, subagent, nested worker, plugin, MCP server, DeepSeek or fallback of any kind was used |
| Integration branch | Resolved **once** at entry: `wp-runtime-completion` local == `origin` == `8cc0ebc5d843c1c2ab9b9a0a9d1c6c922c176513`. The reviewed tip is **not** an ancestor of it and it is **not** an ancestor of the tip; merge-base is the chain base `d6e78e0b`. The privacy chain is therefore **not yet integrated**, and integration remains coordinator-owned. I touched no integration, root, manifest, lock, registry or ledger path |
| Source/registry/ledger | Unchanged by me. No canonical ledger, validation gate, registry or evidence generation was run |

Historical failures are preserved and were not re-run or relabelled: the failed
Opus candidate assessment `1a38e285` and its judgement `e8ce3966` were read as
attributed inputs (report and review text), the C1/C2/C3/C4 author reports and
their preserved attempt histories were read in full, and the C4 self-audit
decision `WAVE_A_C4_SELF_AUDIT_DECISION.json` was read as the lease record.

## 2. What I actually read

Full semantic reads (not hashes, not summaries):

- `tools/validate/evidence.py` (252 lines), `tools/validate/model.py` (508),
  `tools/validate/runner.py` (1059), `tools/validate/clients/api.py` (170),
  `tools/validate/clients/base.py` (117), `tools/validate/clients/ha.py` (547).
- `tests/validation/test_sw_sec_data_02_c1.py` (121), `..._c2.py` (114),
  `..._c3.py` (143), `..._c4.py` (643) — the full C4 module in two chunks.
- The four author reports `docs/production/software-waves/SW-SEC-DATA-02-C{1..4}/AUTHOR.md`
  (154/160/198/283 lines).
- The complete chain diff `d6e78e0b..53853257` for all 13 paths, file by file.
- Product callers and contracts that define the real carriers and the real
  public values: `src/rest_api/security.py` (auth manager, middleware, PIN and
  API-key endpoints), `src/rest_api/profiles.py` (passcode carriers, the PIN
  change rule, `_supplied_pin`, `_check_profile_pin`), `src/rest_api/scenes_v2.py`,
  `src/rest_api/system_shortcuts.py` (built-in shortcut registry, `to_dict`,
  catalog routes), `src/rest_api/app.py` (route registration),
  `src/rest_api/utils.py` (manager wiring), `src/system_shortcuts.py`
  (`_default_shortcuts`), `src/config.py` (`ProfileManager`),
  `tests/validation/scenarios/contracts.py` (the real catalog expectations),
  `tests/validation/scenarios/security_auth.py`, `sw_api_read_04.py`,
  `profile_crud.py`, `kiosk.py`, `profiles.py` (the real catalogue carriers),
  `tools/validate/clients/browser.py` + `browser_driver.mjs` (the browser
  client's unredacted `client_diagnostics`), `tools/validate/clients/uc.py`,
  `tools/validate/clients/flic.py` (its own pre-existing `redact_body`).
- The five documentation modules' subjects (by running them, §7).

## 3. Method (independent, not a replay of the author suite)

All Python used the absolute existing interpreter
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(3.12.10) with explicit `-B`. Every invocation ran through one owned harness
(`build/remediation-recovery-20261104/priv-m3-assess/run_invocation.py`) that
copies the Windows OS environment and then overlays **fresh, own** `MATRIX_DATA_DIR`,
`UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`, `PYTEST_DEBUG_TEMPROOT`, a fresh
`--basetemp` and a fresh `--junitxml`, records the exact argv, cwd, overlay,
start/end times, the **direct child exit** and the full stdout/stderr bytes and
SHA-256, and inventories the invocation directory (ordinary and hidden members).
Measured imports resolve `tools.validate.*`, `rest_api.*`, `system_shortcuts`
and `config` to **this checkout** (`p08-origins`), with pytest 9.1.1,
aiohttp 3.13.3, jsonschema 4.26.0, pytest-asyncio 1.4.0, pytest-aiohttp 1.1.1.

My probes (all ignored, under my owned roots only):

| Probe | What it does |
| --- | --- |
| `probe_carriers.py` / `probe_carriers2.py` | Carrier/public-value enumeration; both the leaf usage (`field_path` names the leaf) and the whole-body usage |
| `probe_live2.py`, `probe_live3.py`, `probe_live4.py` | Live **product** round trips: the real `create_rest_app`, the real `ApiClient`, the real `Runner._run_one`/`_check`/`write_record`/`_write_summary`, the real catalogue scenario |
| `probe_changed_scope.py` | Base (`d6e78e0b`) versus delivered redactor over 347 real product field names |
| `probe_sensitivity.py` | Seven **in-memory** reversions of the delivered redactor/writer (no source file edited) to prove my own oracles are failure-sensitive |
| `probe_raw_vs_persisted.py` | Captures the record the runner hands the writer and compares it field-by-field with the persisted bytes |
| `probe_blocked.py` | The blocked/setup/summary reason path |
| `probe_ha_harness.py` | The added HA diagnostic lease (`_http` error display, `perform` display copies, named defaults, options identity) |
| `probe_provenance.py`, `probe_origins.py` | Provenance and import/tool measurement |

Every product server, aiohttp session and probe process was closed or awaited in
a `finally` block; the disposable product instance's generated API key was
deleted (`DELETE /api/auth/api-keys/<id>` → 200) and its profile deleted.

## 4. Enumerated carriers, sinks and callers

**Real credential carriers (from the product's own code), all masked by the
delivered redactor, verified live:** body `current_pin`, `pin`,
`current_passcode`, `passcode`, `passcode_hash`, `api_key`; header `X-Admin-PIN`,
`X-API-Key`, `X-Passcode`; query `key`; cookies `orei_session`,
`orei_device_token`; plus `Authorization`, `Proxy-Authorization`, `Cookie`,
`Set-Cookie`, `X-Auth-Token`, `X-Access-Token`, `API-Key` and the catalogue's
`passcode` action parameter. `p01b-carriers`: every credential field/header/query
name is masked; **no** public header or public query name is swallowed, and
`X-Admin-PIN-Policy` survives in three casings.

**Transport shapes (all accepted unchanged on the wire):** JSON object bodies,
JSON arrays, tuples, header-pair collections (`(("X-Passcode", v), (...))`) and
serialized JSON in `data=`. `p02b`/`p06d` show the wire body/headers byte-identical
to the caller's objects while the persisted record shows only `***`.

**Sinks traced (source line → observed behaviour):** `Action.describe`
(`model.py:142-149`), `Response.describe` (`model.py:313-330`), `Hub.describe`
(`model.py:344-356`), `ClientState` display (`runner.py:98-101`, `runner.py:649-657`,
`runner.py:992`), `Runner._check` Response/Hub details (`runner.py:940-941`,
`runner.py:965-966`), `ApiClient.perform` steps (`api.py:159-165`),
`HomeAssistantClient._http` error (`ha.py:274`) and `perform` display copies
(`ha.py:491-509`), procedure entries (`runner.py:635`, `667`, `713`), the record
(`runner.py:753-794`), the writer (`evidence.py:60-72`) and the summary
(`runner.py:1047-1059`).

**Live product results (all with real product responses):**

| Case | Real endpoint | Raw verdict | Persisted bytes |
| --- | --- | --- | --- |
| A | `POST /api/auth/pin` with `current_pin` in the body and `X-Admin-PIN` in the headers | HTTP 200 | no credential marker in the record/summary; the public `X-Admin-PIN-Policy` value survives; `admin_pin_set`/`control_pin_set` masked (F-1) |
| B | `POST /api/auth/api-keys` (genuine product-generated 43-char key) | HTTP 201 | the generated key is **absent** from the record and the summary bytes; the key was deleted afterwards (200) |
| C | the **real** `contracts.shortcut_favorites` catalogue scenario against the real product | **pass** (all six checks) | the public catalog key `route_all_to_output` and the public boolean `favorite: true` survive |
| D | `GET /api/auth/status?key=<control api key>` — the product answered `session_level: "control"`, so the query carrier is a *real accepted* credential | HTTP 200 | the query value is `***` in the path, body and procedure |
| E | `GET /api/health` with `X-Admin-PIN` + `X-Admin-PIN-Policy` | HTTP 200 | credential header masked, public header value preserved |
| G/H | `PUT /api/profile/<id>` with `current_passcode` + `X-Passcode`: a **wrong** current passcode (real 403 `invalid_passcode`) and the **correct** one (200) | pass / pass | no credential marker in either; raw bodies keep the original values |
| J | live matched / mismatched / expected-`***` verdict trio on `password_protected` | pass / fail / fail | the raw comparison inputs are untouched; the descriptions and bytes are masked |

## 5. Findings

### F-1 — Low — changed scope — three public product fields are newly masked

The delivered credential-name rule (`evidence.py:122`,
`pass(word|code)?|secret|token|api[_-]?key|(?:^|[_-])pin(?:$|[_-])`) matches
`admin_pin_set`, `control_pin_set` and `pin_order` — **public** fields of the
product's own API contract (the two booleans in `/api/auth/status` and
`/api/auth/pin`; the pinned-order integer in every profile response). The base
commit `d6e78e0b` did **not** mask them: `p05-changed-scope` compares the base
and delivered redactors over 347 real product field names and reports exactly
three newly masked names, all public.

Live evidence: `p02b` case A persisted `"admin_pin_set": "***"` and
`"control_pin_set": "***"` in both the response capture and the check detail;
`p04` case K shows `pin_order` as the **only** masked field among the twelve
public profile fields. Reproduction: `redact({"pin_order": 0})` → `"***"`.

Impact: diagnostic/evidence fidelity only — a public boolean/int loses its value
in every persisted record. No disclosure, no wrong verdict, no raw mutation.
Severity **Low**; it is a *regression introduced by this chain* (C1's rule), not
an inherited defect. A narrow, route/field/type-bounded exception (the shape the
chain already uses for `password_protected`) would restore it without any blanket
bool exemption.

### F-2 — Info — changed scope — structured error objects are suppressed wholesale

`evidence.py:220` replaces the value of any `error`/`blocked_reason`/`aborted`
key with `display_error(...)`, which for a non-exception value yields
`<error text suppressed>`. Live evidence (`p04` case H): the product's real
rejection body `{"error": "invalid_passcode", "profile_id": "m3probe"}` is
persisted as `{"error": "<error text suppressed>", "profile_id": "m3probe"}` — the
public error code is lost while the public id survives. `p10-blocked` shows the
same for a blocked setup step: the in-memory `Outcome.reason` keeps
`"setup step ... failed: HTTP 400"`, but the persisted `blocked_reason` and the
summary reason are both `<error text suppressed>`. The public HTTP status still
survives in the `procedure` list and the check description, so the loss is
partial. Deliberate and safe-sided; recorded as a fidelity cost, not a defect.

### F-3 — Info — latent robustness, **not reachable** in the delivered configuration

`evidence.py:66-71` assumes that `redact(record)["observations"]` is still a
mapping and then assigns into it. Under the "mask everything" reversion the
writer raises `TypeError: 'str' object does not support item assignment` at
`evidence.py:70` and the whole scenario aborts after all other work (`p06g`,
five recorded crashes). With the delivered rule this is **not reachable**:
`observations` is not a credential name, so the key is never masked. No defect
is claimed against the delivered code; the finding is that the writer has no
guard, so a future name rule that matched `observations` would fail late and
loudly. Disclosed exactly as the task requires: the crash was produced by an
in-memory reversion, not by the delivered source.

### F-4 — Info — scope, not a defect: sinks that are deliberately not redacted

`observations.state_before`, `state_after`, `state_diff`, `ws_events`,
`client_diagnostics` (non-API clients), `operator`, `restore` and the
`checks[].detail` of the device-side expectations are persisted **raw**
(`runner.py:770-789`). `p07-raw-vs-persisted` shows which sinks still carry
byte-identical raw text in the written file: the record metadata, the response
status and the empty device/operator collections; every credential-bearing sink
is already masked before the writer. These sinks carry device/hub state and
client diagnostics, not credentials. `device_log` is redacted explicitly
(`runner.py:777`). The browser client's `client_diagnostics`
(`browser.py:116-123`: page errors, console errors, toasts, dialogs, `pin_probe`)
is unredacted; I read the driver (`browser_driver.mjs:515-565`) and the probe
records only HTTP statuses and error **codes**, never the passcode value, but
the browser client was **not run** here (opt-in Playwright, out of the C1–C4
lease).

### F-5 — Info — scope: standalone model description methods remain raw

`ClientState.describe`, `Device.describe`, `CommandSent.describe` and
`WsEvent.describe` interpolate their values directly (`model.py:405-407`,
`233-237`, `265`, `419`). The runner does not use them for the persisted
description: `_description` (`runner.py:90-102`) routes `Response` and
`ClientState` through masked copies, and `runner.py:992`/`runner.py:649-657`
mask the ClientState values before they are shown. The standalone methods are
outside the model-method lease the C4 report declares, so no defect is claimed;
the gap is recorded so a future caller of the raw methods is not surprised.

### F-6 — Info — calibration of the safety parser

The delivered parser covers dict/list/tuple, header pairs, serialized JSON and
query parameters. Arbitrary prose, arbitrary `Mapping`/custom sequence
objects, userinfo URLs, screenshot bytes and all product logging are outside
its supported boundary (the source says so: `evidence.py:196-203`). Opaque
error prose is **suppressed** rather than parsed, which is the safe direction
but loses public error codes (F-2). Browser/screenshot capture is out of
proved scope. These are calibrated limits, not findings.

## 6. Failure-sensitive controls (my own oracles proven sensitive)

Each reversion is an **in-memory** patch of the delivered module attributes; no
source file was edited. Child exits are the real ones (`p06c`, `p06d`, `p06g`).

| Mode | Reversion | Observed effect | Exit |
| --- | --- | --- | --- |
| baseline | none | no credential marker; every public value preserved | 0 |
| no-mask | `_secret_name` → always False | the markers appear in the record **and** the writer output | 0 |
| mask-all | `_secret_name` → True, `_public_field` → False | all public values lost **and** the writer crashes (F-3) | 0 |
| no-public-exception | `_public_field` → False | the public shortcut key and the public boolean are lost | 0 |
| no-error-suppression | `display_error` → identity (evidence **and** the runner's import-time alias) | the exception prose leaks into the persisted `blocked_reason` | 0 |
| no-query-mask | `_query_copy` → identity | the query carrier leaks into the record | 0 |
| no-writer-boundary | base writer in `evidence` **and** `runner` | the raw caller record is persisted with the credential | 0 |

The `no-error-suppression` mode first showed *no* leak: the runner binds
`display_error` at import time, so patching the evidence module alone does not
reach the sink. That is recorded as a methodological correction, not a result.

## 7. Actual commands, exits and read coverage

| Invocation | Scope | Direct child exit | Observed |
| --- | --- | --- | --- |
| `p12-provenance` | packet digest, 13 path blob digests, chain, integration | 0 | packet digest matches; 13/13 path digests match; integration resolved once |
| `p01b-carriers` | carrier matrix, public registry vs the product, 168 catalog cases, 120 `password_protected` cases | 0 | no unmasked credential carrier; no swallowed public carrier; the public shortcut registry **equals** the product's 23 built-in keys exactly |
| `p02b-live` | live product: current_pin + header, genuine API key, real catalogue scenario, query carrier, public header | 0 | table in §4 |
| `p03b-live-profile` | live product profile passcode carriers | 0 | body and header carriers masked; wrong-type and wrong-value controls |
| `p04-live-verdicts` | live rejection pair + verdict trio + public-field census | 0 | §4, F-1 |
| `p05-changed-scope` | base vs delivered over 347 product field names | 0 | exactly three newly masked public fields (F-1); no newly unmasked field |
| `p06c`/`p06d`/`p06g` | seven in-memory reversions | 0 | §6 |
| `p07-raw-vs-persisted` | raw record vs persisted bytes | 0 | only public/device-state sinks stay byte-identical |
| `p08-origins` | import origins and tool versions | 0 | every module resolved inside this checkout; tree clean |
| `p09-c1c4-tests` | `test_sw_sec_data_02_c{1..4}` + `test_evidence_schema` + `test_model` + `test_registry` + `test_runner` (`-q -p no:tests.route_inventory -p no:cacheprovider --tb=short -ra`, own basetemp and JUnit) | 0 | **136 passed in 50.28 s** |
| `p10-blocked` | blocked/setup/summary reason | 0 | F-2 |
| `p11-ha-harness` | the added HA lease | 0 | options body identity preserved; `api_key` masked, `scan_interval` kept; named default masked; opaque HTTP error suppressed |
| `p13-docs` | the five documentation modules, `-p no:tests.route_inventory -p no:cacheprovider`, own basetemp/JUnit | 0 | **489 passed in 2.73 s** |

`p09` and `p13` are *targeted slices* for review coverage, not a repeated full
core/canonical campaign; no canonical route/gate/ledger generation was run, and
the supplemental documentation run does not overwrite any strict route evidence.

**Read coverage of the invocation outputs:** `p01-carriers` (3,512 lines),
`p01b-carriers` (3,025 lines), `p02b-live` (650), `p04-live-verdicts` (340),
`p06d-*` (6 files) and `p06g-mask-all` (70) were read **in full**;
`p02-live`, `p03-live-profile`, `p03b-live-profile`, `p05`, `p07`, `p08`, `p09`,
`p10`, `p11`, `p12`, `p13` were read in full or in their complete material
sections with the remainder inspected through the extracted JSON fields. The
superseded probe iterations `p01`, `p02`, `p03`, `p06`, `p06b`, `p06c`, `p06e`,
`p06f` are retained with their original streams; their defects were **probe-side**
(a mis-used `field_path` in `p01`, a wrong expectation table in `p06`, a module
alias not patched in the first `no-error-suppression` attempt, and `None`-handling
gaps) and were corrected, not hidden. `p01`'s catalog section is superseded by
`p01b`'s correct leaf/body usage; its carrier sections stand.

## 8. Frozen-axis evidence and my honest recommendation

The axes judge **this review**, not the source; the source acceptance is
separate and remains with the coordinator and the qualified review.

| Axis | My recommendation | Evidence |
| --- | --- | --- |
| provenance | **PASS** | packet digest, all 13 path blob digests, the 8-commit chain, base, integration resolution (once) and authorship attribution verified; the added `ha.py` scope is bound explicitly; historical failures preserved and not re-run |
| dataflow_invariants | **PASS (with F-1 recorded)** | every real carrier enumerated and masked live; raw/wire/comparison inputs proven unmutated by identity checks; the public catalog and `password_protected` contexts proven preserved live and by 168+120 cases; opaque error text suppressed before truncation; the writer and summary are independent boundaries proven load-bearing by reversal. **This PASS is a statement about the completeness of this review, not a claim that the source is defect-free: F-1 is a real, changed-scope, live-demonstrated public-value defect inside the preservation half of this axis** |
| counterexamples | **PASS** | seven failure-sensitive in-memory reversions with real child exits; live positive and negative controls (wrong current passcode → real 403, correct → 200; genuine generated key; real query carrier; raw matched/mismatched/expected-`***` trio); supplied prior findings were re-derived independently, not copied |
| behavior_and_tools | **PASS** | full reads of every changed source file, test module and author report; measured imports from this checkout; exact argv/cwd/environment/time/direct-exit/streams for every invocation; fresh own data/config/TEMP/TMP/basetemp/JUnit per invocation; no global gate, ledger or canonical evidence generated |
| calibration | **PASS** | changed vs inherited separated with a base-vs-delivered comparison over 347 real field names; supported/conditional/unproved shapes distinguished; synthetic fixtures are not called owner data; the HA **harness** is never called product HA; no live-HA, HIL, soak, field or release claim |
| review_quality | **PASS** | the full C1–C4 window analysed including the error/blocked/setup/cleanup/summary and HA paths, the sensitive/compatibility and wrong-type controls, with two severity-calibrated findings that are *not* the supplied ones, and the F-3 non-reachability stated explicitly |

**Overall recommendation: PASS on all six axes, as a candidate review
recommendation only.** I record the dependency honestly rather than
pre-empting the judge: if the independent Astra judge holds that F-1 — a
changed-scope, live-demonstrated regression of three public product fields — is
material to the dataflow axis, the correct result for that axis is HOLD and the
overall result is HOLD, because FAIL/HOLD is terminal for this attempt. This
report neither grants that judgement nor assumes it.

## 9. What this report does not establish

- No source acceptance, no privacy qualification, no evidence admission, no
  canonical/ledger/gate outcome, no release, no owner incident.
- **Product Home Assistant is unproved.** No Home Assistant is installed in this
  environment; I exercised the *harness* (`clients/ha.py`) only. HA form
  serialization by the product, the product's credential flow, any real-client
  acceptance and any live-HA behaviour remain unproved and unclaimed.
- The browser, UC and Flic clients were not run. The Flic client's own
  pre-existing `redact_body` was read, not exercised.
- Physical HIL, 72-hour soak, week field sign-off, visual baselines and the
  final release artefacts are separate gates and are untouched.
- The author's retained 4,164-test hook result, 4 skips, 35 deselections,
  4 warnings, 177/177 routes and 42 receipt sets were **not** re-run and are
  not evidence of acceptance; I inferred nothing from them.
- The earlier Opus candidate assessment/judgement and the C4 catalog self-audit
  are supplied inputs; their conclusions are not credited to me and are not
  re-argued as discovery.
- The C1–C3 sources/reports and the C4 first commit are immutable and
  unchanged; nothing in this report edits or supersedes them.

## 10. Preserved originals and owned artifacts

Own build root (ignored): `build/remediation-recovery-20261104/priv-m3-assess/`
— the harness, the ten probe scripts, the produced records and their scans.
Own native temp root: `C:/t/remediation-recovery/priv-m3-assess/` — one
directory per invocation with `stdout.txt`, `stderr.txt`, `receipt.json`
(argv/cwd/environment overlay/times/direct exit/stream digests) and
`inventory.json` (ordinary and hidden members), plus the two JUnit files
(`p09-tests-results.xml`, `p13-docs-results.xml`).

Nothing was pushed, cleaned, released or merged; no worker was created; no
other workspace, root file, private runtime data, historical evidence or
coordinator-owned configuration was modified. The `opencode.json` in this
checkout was left untouched and untracked.

## 11. Left for the coordinator and the judge

1. The ONE independent Astra judge over this exact report.
2. A separate, actual qualified full-chain source review — which is where F-1
   (and any other finding the judge endorses) would be disposed of, including
   the decision whether a bounded public-field exception or an explicit scope
   statement is the right correction.
3. A separate report-quality evaluation.
4. Coordinator-owned integration of the privacy chain into `wp-runtime-completion`
   (still at `8cc0ebc5`, unchanged by me), evidence admission and every release
   gate — all still held.
