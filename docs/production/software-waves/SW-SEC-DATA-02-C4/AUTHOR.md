# SW-SEC-DATA-02-C4 original-author correction

The leased diagnostic paths now mask the supported structured credential carriers
before formatting or truncation, preserve specified public fields through explicit
display context, and suppress opaque error text. This is an **unaccepted source
delivery**: qualified different-family privacy review, integration, evidence
admission and all release gates remain HELD. Original Opus failure, unqualified M3
status, C1–C3 reports and all earlier failure/lost-byte records are unchanged.

This report is frozen before its normal source commit hook. The actual resulting
commit/parent, hook exit, full-core/JUnit/strict-route originals and final inventory
are recorded separately in the owned `build/remediation-recovery-20261104/priv-c4/`
completion artifact and Orca worker_done. Nothing in this report predicts a hook PASS.

## Authority, provenance and boundaries

- Exact base/parent: `2d02004d3108953a302e1a49aab9a5f24e944136`.
- Original chain begins at `d6e78e0b6ab1dab5216443584d810a7a24af32b2`:
  C1 source `8b9f5623b3b5a12c55ed6b9da0ae59662bd6b873`, report
  `11f305b16c4c95e27682d13df4b02c8de33354d7`; C2 source
  `47b0bbb86a1dfd36726e60ab2ccf24b867883160`, report
  `615d3c8403b237dd117c8032697c9b58895f9217`; C3 source
  `8fc65e052954a30f89be209d2d8f04e58ac1266f`, report at this base.
- Entry-pinned integration observation:
  `ff27f7a8b157b9255acab5f76db931d2970a52e0`. The complete FINAL_PACKET v1
  canonical LF SHA256 independently computed as
  `f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e`.
  Actual CONSENSUS records three ACCEPT votes on that digest. D4/D5/D7 hold
  privacy acceptance and separate candidate/judge/actual-source-review roles.
- Task `task_25a4c3572682`, Dispatch `ctx_5ca1ba3f03ac`, worker
  `term_29f8e8c7-b972-4c89-84dd-d0ee7a7bfe00`, coordinator
  `term_6ed8131e-3ab3-4693-8094-56cc10acd412`; existing Run `run_37205f6095b3`.
- Branch `remediation/privacy-c4`, worktree
  `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-sec-data-02-c4`.
  Native preamble assigns OpenAI Codex `gpt-6.1-sol/high`, original source family.
  No model switch, helper, worker, plugin or external message channel was used.
  Backend/native provenance capture and independent headroom attestations remain
  coordinator records; this author does not manufacture them from self-report.

Exactly seven tracked paths are delivered: the five leased Python files,
new `tests/validation/test_sw_sec_data_02_c4.py`, and this new report. In
`evidence.py` changes are limited to redaction/helpers and the writer boundary;
in `api.py`, perform diagnostics only; in `model.py`, Action/Response/Hub display
methods; in `runner.py`, diagnostic context, descriptions, check detail,
procedure/error/Outcome/record/summary sinks; in `ha.py`, `_http` error display
and `perform` diagnostic copies only. No transport, comparator, status/error-kind
classification, required argument, root manifest/lock, registry, ledger, product
HA config-flow, baseline or original evidence/report edit is included.

## Supported contract and invariants

Structural masking covers dict/list/tuple traversal, tuple/list header pairs,
and serialized JSON objects/arrays in data/body diagnostics. Credential names
include current_pin, pin/pin_hash and underscore/hyphen PIN fields, pass/passcode/
password/current_passcode/manual_passcode, secret/token/API-key variants, bare
key, Authorization/Proxy-Authorization and Cookie/Set-Cookie. Exact header names
include X-Admin-PIN, X-Passcode, X-API-Key, API-Key, X-Auth-Token and X-Access-Token.
The product cookies are orei_session and orei_device_token. Query names are
percent-decoded for classification; values and public query parameters are
copied without parsing/re-encoding the wire URL. Credential header matching is
exact and case insensitive: X-Admin-PIN-Policy stays public in every casing.

Public shortcut keys are limited to the inspected built-in identifiers and the
matching `/api/system-shortcuts/<key>` or `/api/shortcuts/<key>` diagnostic route,
or the shortcut_run Action context. Unknown/created credential `key` values stay
masked. Boolean password_protected is retained only for the inspected profile/
scene routes and named fields. Wrong types, integer PINs, bool/None credentials
and unrelated routes receive no broad exemption. No global value registry or
short-PIN substitution alters coincident public ports, IDs or timing values.

Only known exchange collections explicitly enable exchange context. A response
body containing method/path/status cannot grant itself public-field exceptions.
Response.describe accepts an optional default-compatible path context; the runner
derives it from the existing action mapping. Hub descriptions mask both query
carriers and sensitive equals/not_equals values. Actual and expected comparisons
continue to use original objects; display copies precede repr/JSON/slicing.

ApiClient raw requests, response bodies and references remain original. HA raw
HTTP/config-flow records and options references also remain original. HA perform
rebuilds config-flow/reconfigure/service display steps from structured captures;
error_kind/status/verdict classification is unchanged. Opaque HTTP/error bodies
are suppressed, retaining method/path/status or exception-class metadata as
available, rather than claiming query-only redaction can parse arbitrary prose.
Writer and summary add independent copy boundaries; caller records and Outcome
objects are not mutated by persistence.

## Actual controls and execution

41 new C4 cases include real loopback ApiClient.perform/Runner._run_one/_check/
write_record/_write_summary; action/setup/cleanup; actual and expected credential
matches, different raw values and expected `***` mismatches; string and integer
PINs sharing public port 1; tuples, pair headers and serialized JSON; Hub query,
equals/not_equals and public/negative context controls; blocked setup/prepare/
action, transport and cleanup exceptions; opaque response truncation; unavailable
client stdout; and HA options/default/error paths. Each new HTTP fixture explicitly
closes its test clients/servers with bounded guards, and sessions/awaited operations
also have bounded teardown. Existing C1–C3 tests/markers remain unchanged.

The actual product auth endpoint creates a fresh API key at loopback, raw identity
and equality are checked, display mask equality fails, persisted bytes exclude the
generated value, and the key is deleted from that disposable test instance.
Synthetic credential markers are used elsewhere; no owner credentials/LAN/hardware.
The complete generated record/summary bytes and retained captured stdout/stderr/log
streams are scanned, with public-value assertions. Original failed/mutant payloads
remain private synthetic artifacts. JUnit test names may contain synthetic parameter
values; no claim is made that all intentionally failing artifacts are marker-free.

Python is the existing absolute root venv executable, version 3.12.10; aiohttp
3.13.3, pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0. Each authored launcher copies the
Windows OS environment, uses explicit Python `-B`, its own src/root PYTHONPATH,
and new data/config/TEMP/TMP/TMPDIR/basetemp/JUnit directories. Measured imports
in child output resolve tools/product/tests to this checkout, not root editable
source. The unchanged normal hook uses its configured pytest console entry point
with inherited PYTHONDONTWRITEBYTECODE; its command itself is not relabelled `-B`.

| Invocation label / scope | Actual direct result before this report |
| --- | --- |
| focused-01, initial C4 module | Exit 1; 29 passed/one overly broad integer-description assertion failed. |
| focused-02, C1–C4 | Exit 1; 49 passed/one incomplete fixture lacked hub.mode. |
| focused-03, corrected C1–C4 | Exit 0; 51 passed, 15.25s. |
| focused-04, additional HA HTTP controls | Exit 0; 35 C4 passed, 13.47s. |
| focused-frozen, explicit exchange-context correction plus schema/model | Exit 0; 88 passed, 17.15s. |
| focused-frozen-02, additional actual integer-PIN wire controls | Exit 0; 94 passed, 17.95s. |
| focused-frozen-03, explicit bounded HTTP fixture teardown | Exit 0; 94 passed, 18.08s. |
| regression-final, tests/validation | Exit 0; 265 passed/two opt-in Chromium skips, 205.92s; began before the final explicit-exchange-context tightening. |
| runner-frozen, actual runner/client-state/Flic/HA error regressions after that tightening | Exit 0; 18 passed, 77.74s. |
| lint-01/lint-final/lint-frozen, CI Ruff paths | Exit 0 each; src tests custom_components tools run.py run_server.py. |
| mypy-final/mypy-frozen, CI src/ scope | Exit 0 each; 91 files. This does not claim separate strict typing of all tools. |
| freeze-audit | Exit 1; author wrapper attempted module audit instead of owned script path, ImportError retained. |
| freeze-audit-02 | Exit 0; corrected run_path, C1–C3 source/report equivalence, versions/imports and source hashes recorded. |

All focused pytest runs use `-q --tb=short -p no:tests.route_inventory
-p no:cacheprovider`, plus unique explicit basetemp/JUnit and `-ra`.
The exact argv/environment/start/end/exit and stream/JUnit hashes are in each
label's receipt.json. No global validation gate or ledger-generation command ran.

15 selective **in-memory** source reversions each exited 1 for the intended byte
or public-value oracle: field (3 failed), tuple (3), header pairs (3), serialized
display copy (6), Hub expectation (1), actual Response detail (6), HA steps (1),
blocked Outcome error (1), summary (6), wrong-type public exemption (2 failed/
7 passed), API steps (6), expected Response description (4 failed/2 passed),
writer boundary (3), HA HTTP error text (2), and HA named defaults (1).
These are counterfactual sensitivity checks, not failed competence attempts or
historical source retries. Full originals, exact selectors and source hashes
remain in mutant-*/; the checkout source was never modified by the loader.
The first ten precede the final exception-idempotence/context refinements; final
normal source verification separately covers the delivered candidate.

Discovery errors are also retained in the native transcript: guessed obsolete
consumer paths, a non-Force junction lookup, unsupported check --from, and an
ACK using a message rather than delivery ID. Corrected native Get-Item -Force
confirmed the preprovisioned junction; subsequent full check had no delivery.
Large initial read output was truncated and consequential sources/criteria were
then read in bounded chunks; those previews are not represented as full reads.

## Original artifacts and calibrated limits

Own build root (absolute prefix is the worktree above):
`build/remediation-recovery-20261104/priv-c4/`. It retains run.ps1, run_check.py,
the pre-audit-fix runner, mutate.py, audit.py, plan-verification.json, freeze.json,
all labelled stdout.log/stderr.log/receipt.json and mutant driver logs. Original
native temp, including hidden members, is retained at
`C:/t/remediation-recovery/priv-c4/<label>-<unique>/`; each receipt names the exact
full path and JUnit hash. Final no-follow inventory/completion receipts will bind
all surviving original members by path/size/SHA256 without replacing originals.

The coordinator-provisioned node_modules junction targets root existing locked
dependencies READ_ONLY. Coordinator reported exact package/lock working/Git-byte
equivalence and direct npm lint success. No install/download/dependency-target
write, private runtime edit, push, cleanup or worker release is performed here.
The normal strict hook necessarily generates this checkout's ignored
route-coverage.json; its original and owned copy are retained as automatic output.
No separate tool-returned output-preview file path was exposed; native transcript
and any coordinator preview exports remain preservation responsibilities.

HA product config_flow.py uses named API-key defaults in user/reconfigure/options
schemas. The harness tests the serialized `{name: api_key, default: ...}` shape
over loopback, including raw returned defaults and HTTP errors. Actual HA schema
serialization is **unproved here**: homeassistant is unavailable in this Python
environment; no real HA/form run, product credential-flow CR02 correction,
incident claim or live-HA acceptance is inferred. ClientState's actual observer
can read entry fields/attributes; runner check/precondition displays now mask named
sensitive keys. Standalone ClientState.describe and unrelated clients/log capture
are outside the model-method lease; no universal diagnostic/privacy claim follows.

Arbitrary Mapping/custom sequence objects, userinfo URLs, unknown prose carrying
credentials under public names, screenshot bytes, all product logging and custom
shortcut identifiers have no blanket acceptance from these tests. Suppression
intentionally trades opaque error-body detail for safe display while retaining
public protocol metadata. Hardware, full supported HA/UC/image/client campaigns,
physical HIL, 72-hour soak, week field sign-off and final release remain separate.
No REST routes changed; there is no registry/route-count accommodation. Qualified
privacy assessment/judge, separate actual full-chain review and report-quality
evaluation, sequential coordinator integration and combined acceptance remain due.
