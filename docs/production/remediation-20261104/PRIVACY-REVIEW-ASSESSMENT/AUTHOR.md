# Privacy-review competence assessment: candidate author report

This is **one candidate report** for the first task-domain privacy-review competence
assessment (`RV-PRIVACY-CHAIN` gate). It is not a qualified source review, source
acceptance, integration, new authorship or a retry of an earlier qualification. No
competence is claimed here. A qualified outcome needs a future independent
different-family judge (reserved: OpenAI `gpt-6-astra/high`) passing all six axes,
judged against this exact report, its native evidence and the original proof. The existing
Opus 5.5 scope (API-refusal runner/model review) is not extended by this report.

## 1. Identity, authority and inputs

| Item | Value |
| --- | --- |
| Native candidate | Anthropic `claude-opus-5-5` (Claude Code CLI); effort `high` per dispatch. I cannot measure the effort setting myself, so it is the dispatch's assignment, not a self-attestation |
| Orca Task / Dispatch | `task_8b5496cdc9b2` / `ctx_408fa818297a`; worker `term_17f4f3f2-085d-411d-901f-3f1350ade4c7`; coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`; Run `run_37205f6095b3` (from packet) |
| Workspace | `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-qual-privacy-review-20261104`, branch `qualification/privacy-review-20261104`, clean at entry |
| Helpers | None. No subagents, teams, plugins, MCP or nested workers. Only shell and file-write tools were used |
| Integration ref (resolved once) | `origin/wp-runtime-completion` = `f0053aac4cb85a729f8455872086a61ce92a1d2d`. `git ls-remote` matched the local ref. Task, packet, AGENTS and protocol were read from this commit via `git show`; nothing was imported into the checkout |
| Packet hash | Frozen SHA-256 `94b28ad847b727a005c3cd9f4bb42d79916afdab80f49f3e43a156a9559a1ce4` **matches the CRLF working-tree form** of `ASSESSMENT_PACKET.json`. The LF Git blob bytes hash to `1732709314f8c6639ff9e136277861abaf444075227734a0b7d9e2d38b7c4dd8`. The content is the same; only the line endings differ. `TASK.md` blob SHA-256 `25eb4a8e98fa2886ab3df632a95694010e5ac852628a058036ecbb64c3d9b23c` |
| Routing authority | `AGENTS.md` and `docs/ORCHESTRATION_PROTOCOL.md` at `f0053aac` record the owner's 2026-11-01 direction allowing Anthropic. That supersedes the older exclusion still present in this checkout's `AGENTS.md`. Routing was not changed |

## 2. Exact source, lineage and authorship

Base `d6e78e0b6ab1dab5216443584d810a7a24af32b2`, candidate
`2d02004d3108953a302e1a49aab9a5f24e944136`. The chain is linear: every parent was
checked with `git rev-parse <c>^`. It changes exactly the packet's 10 paths
(959 insertions, 5 deletions).

| Commit | Subject | Paths (shortstat) |
| --- | --- | --- |
| `8b9f5623` | redact credential headers before evidence persistence | `tools/validate/evidence.py`, `tests/validation/test_sw_sec_data_02_c1.py` (+143/-2) |
| `11f305b1` | record bounded credential redaction delivery | `SW-SEC-DATA-02-C1/AUTHOR.md` (+154) |
| `47b0bbb8` | mask structured bodies before diagnostic formatting | `tools/validate/clients/api.py`, `tools/validate/runner.py`, `test_sw_sec_data_02_c2.py` (+136/-2) |
| `615d3c84` | record C2 body-formatting verification | `SW-SEC-DATA-02-C2/AUTHOR.md` (+160) |
| `8fc65e05` | redact expected JSON before response description formatting | `tools/validate/model.py`, `test_sw_sec_data_02_c3.py` (+168/-1) |
| `2d02004d` | record C3 author proof and preserved attempts | `SW-SEC-DATA-02-C3/AUTHOR.md` (+198) |

**Authorship.** Git author and committer on all six commits is the owner account
(Ryan Haver). The actual model author, as stated in each original report, is OpenAI
`gpt-6.1-sol/high`. C1 labels it "Codex `gpt-6.1-sol/high`"; C2 and C3 label it
"OpenAI `gpt-6.1-sol/high`". Tasks/Dispatches: C1 `task_cf272c0e3b6c`/`ctx_a52a1d96ad08`,
C2 `task_4e33d0624489`/`ctx_a35145bc2f5d`, C3 `task_242c1cc61b92`/`ctx_793d3e4da3c3`.
I did not attest these identities independently; they are the reports' own claims.
This report does not relabel that authorship or the existing C3 pre-review fixes.

**Original failure and partial outcomes, kept as recorded.** C1's first normal hook
exited 1 (Windows MAX_PATH hygiene fixture). C1's deep-fixture reproduction exited
128. The C1 tip's negative oracle still exposed the body-step and Response-detail
boundaries. C2's before-fix oracle exited 1 (four failures). C3's before-fix oracle
exited 1 (five failures). C3's first source hook exited 1 (`PYTEST_ADDOPTS`
backslash parsing, 174/177 routes). C3's audit-helper attempt 01 failed. All three
reports say UNREVIEWED / UNINTEGRATED / UNQUALIFIED. The candidate is **not** an
ancestor of `f0053aac`: at that ref the 10 paths still hold base content.

**Claims I verified from Git:**

- Per-commit path sets and shortstats match each report.
- C1's residual line references are exact at `11f305b1`: `clients/api.py:158`
  formats raw `{body}` and `runner.py:919` formats raw `json.dumps(result.body)`.
- C2's residual matches `615d3c84` `model.py:319`, which formats raw `{self.json}`.
- `Action.describe` already redacted lazily at base, as C1 says.
- The tracked `.githooks/pre-commit` SHA-256 is `e69e6419…f544bc`, as all reports
  say.
- The chain changes no evidence, ledger, feature registry or scenario files.

**UNKNOWN (not verified, not reconstructed, not waived).** This covers every
historical run count, duration, exit, JUnit, byte receipt, preservation hash and
transcript claim stored in the old worktrees' private
`build/software-waves/SW-SEC-DATA-02-C*/` trees or native transcripts. This dispatch
gave no bounded authority to open other workspaces' private artifacts, and I did not
access them. My fresh runs at the tip cannot certify those historical bytes, and
they are not a privacy admission of them.

## 3. Domain contract used for judgement

The credential carriers the product actually accepts come from the product source,
not from a generic secret list:

- Header `X-Admin-PIN` (`src/rest_api/security.py:255`).
- Header `X-API-Key` or query `?key=` (`security.py:210`).
- Header `X-Passcode` (`src/rest_api/scenes_v2.py:134`, used by profiles too).
- Session and remembered-device cookies, sent in the `Cookie` request header and
  set with `Set-Cookie` (`security.py:228/234`).
- Body fields `pin`, `current_pin`, `passcode`, `current_passcode`.
- A created API key returned as response `{"key": ...}` (`security.py:341`).

`Authorization` is not a hub REST credential but is masked anyway. The redactor is
a **key-name contract** for structured data plus a query-parameter rule for
strings. It is not universal secret detection, so a gap is judged against this
contract. Synthetic markers in tests and probes are not owner credentials, and the
PIN, passcode and key values committed in scenarios are test fixtures. Broad
product logging and privacy are outside this domain.

## 4. Per-hunk dataflow, invariants and compatibility

The invariant checked at every changed boundary: **structured data is masked into a
new copy before interpolation, `repr`, `json.dumps` or truncation.** In addition,
on-wire requests, raw `ActionResult` values and comparison inputs stay original and
unmutated. `redact()` (`tools/validate/evidence.py:125-133`) builds new dicts and
lists and recurses into them. It masks the value of any key matching `_SECRET_KEYS`
(case-insensitive) and applies only `_SECRET_QUERY` to strings. Other types pass
through unchanged.

**H1, `evidence.py:59-65` `write_record` → `dumps(redact(record))`.**

- Dataflow: `Runner._run_one` builds `record` (`runner.py:734-775`), with
  `procedure`, `checks`, `observations.*` (including `client_diagnostics`,
  `state_*`, `ws_events`, `notes`) and `blocked_reason`. Before H1 only
  `requests`, `hub_reads` and `device_log` (`runner.py:752-758`) and the
  client-error check detail string (`:667`) were redacted at capture.
- Effect: H1 adds a whole-record structured mask at the persistence sink, and query
  masking for every string in it, including `?key=` inside procedure step text.
  Path naming still uses the unredacted metadata. `record` is not mutated (C1
  asserts `record == original`).
- Compatibility: none of the 76 evidence-schema property names and none of the 20
  `RECORDED_ENV` keys match `_SECRET_KEYS` (inv11), so record shape and ledger
  fields are untouched. `ledger.py` and `registry.py` do not consume `state_*` or
  `ws_events`. The 78 existing schema, model, runner, ledger, API-read and
  auth-scenario controls pass (inv12).
- Finding: correct for the contract. It does not reach `run-summary.json` (N-4)
  and does not recurse tuples (N-1).

**H2, `evidence.py:115-118` adds the anchored `x-admin-pin` name.**

- Dataflow: one regex consumed by every `redact` call site, including the
  pre-existing `Action.describe` (`model.py:142-148`). Before H2, an
  `X-Admin-PIN` header in action params was persisted unmasked in the procedure
  through `describe`.
- Effect: every casing is masked through nested dicts and lists, and similarly
  named public headers are preserved: `X-Admin-PIN-Policy`, `X-Correlation-ID`,
  `Origin`, `Vary`, `X-Forwarded-For`, `Content-Type` (inv10 and C1 tests).
  `X-API-Key`, `X-Passcode`, `Cookie` and `Authorization` in all tested casings
  were already masked. Underscore or compact spellings and `Proxy-Authorization`
  are not masked, and none of them is a header the product reads.
- Finding: correct and minimal. No real scenario passes `X-Admin-PIN` as an
  action header (0 of 1,507 scenarios), so this fixes a latent leak rather than an
  observed one.

**H3, `clients/api.py:10,159-161` steps use `redact(body)`.**

- Dataflow: `rest_call` returns the body, which goes to `ApiClient.request`
  (`json=body` on the wire, unchanged) and to `result.steps`. From there it
  becomes the procedure (`runner.py:657`) and the persisted record.
- Before H3 the step text was `str(dict)` of the raw body. H1's string pass does
  not mask dict reprs, so fixture credentials persisted in procedure bytes at
  base and at the C1 tip. Measured on the real catalogue: 93 of 977 API step
  bodies change. The masked keys are `pin`, `passcode`, `current_passcode`,
  `password` and `remove_passcode`.
- Compatibility: the other 884 step texts are byte-identical, because the `repr`
  of a dict without secret keys is unchanged. The importing module did not
  already import `evidence`, and no cycle exists (`model` lazy-imports).
- Residual: the `path` part of the step keeps raw `?key=` in memory until
  `write_record` masks it (inv10 confirms both states). `data=` string bodies are
  not formatted into steps, so they don't leak here.

**H4, `runner.py:919-920` Response detail uses `json.dumps(redact(result.body))[:300]`.**

- Order: mask, then serialize, then truncate, so truncation cannot expose part of
  a secret.
- Raw comparisons are kept. `_subset(exp.json, result.body)` (`runner.py:895`) and
  the header checks run on the raw body before H4. In C2, a raw expected
  credential passes and an expected `"***"` fails. In C3, `masked-mismatch` fails.
  Masking therefore cannot be used to fake equality.
- Finding: correct. Other detail builders in `_check` are unchanged: `Hub`
  `json.dumps(shown)` (`:946`), `ClientState`/`Device` `repr`s and command
  payloads. None of them carries a supported credential in the current catalogue.
  They are out-of-lease residuals, not defects of H4.

**H5, `model.py:318-323` `Response.describe` formats `redact(self.json)` (lazy import).**

- Dataflow: the description flows into `check.description` in the persisted
  record, and into `Outcome.failed_checks` in `run-summary.json`.
- The lazy import keeps the `evidence` → `model.Level` cycle intact. The status
  and header-name formatting are unchanged; header values were already
  names-only.
- Compatibility: 1,389 of 1,392 real `Response(json=…)` descriptions are
  unchanged. The three that change lose only **public** values:
  `contracts.shortcut_alias` (`data.key`), and
  `security_hardening.profile_read_protected` and `scene_read_protected`
  (`password_protected`). See N-5.

**Tests.**

- C1, 6 cases: casing parametrization, nested and list headers, the anchored
  public control, query masking, non-mutation, and a real loopback `_run_one` in
  API and diagnostic-client variants. `expect=()` deliberately avoids the
  Response boundary.
- C2, 4 cases: mapping and root-list bodies, matched and mismatched public checks,
  on-wire method/path/headers/body equality, object identity of raw captures,
  schema validity, masked `Set-Cookie`, and direct raw-versus-masked comparison
  controls.
- C3, 8 cases: five lifecycle variants (matched, top/nested/list mismatch,
  masked-mismatch) with identity checks on the expected JSON, plus three
  public-format compatibility cases.
- Assertions use booleans, so failure output does not echo markers. No test
  sanitizes its own inputs.
- Gaps (N-6): `X-Passcode`, tuples, string bodies, `?key=` through runner steps,
  and over-masking negatives are not exercised.

**Reports.** The three AUTHOR reports describe scope, residuals and holds honestly.
Each one names the next boundary rather than claiming VAL-15 is closed, and they do
not sanitize the failures. I found no overclaim in the Git-checkable statements.
Their run receipts are UNKNOWN (section 2).

## 5. Native tool evidence (exact checkout `2d02004d`)

Every invocation ran through a private stdlib harness (`run_invocation.py`). The
harness runs the argv directly with no shell, cwd = this worktree, and
`env = os.environ.copy()` (147 keys after overrides; `SYSTEMROOT`, `WINDIR`, `COMSPEC`,
`PATH`, `PATHEXT`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA` present). It then sets:

- `PYTHONPATH=<worktree>;<worktree>/src`
- `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`
- a new per-invocation `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, and `TEMP`/`TMP`/`TMPDIR`

Each invocation gets a new absent directory under
`C:/t/remediation-privacy-assessment/<inv>/` (the harness refuses existing ones, so
nothing is silently retried). It records full stdout and stderr, the JUnit file, a
receipt with argv, start/end UTC, exit code and selected env, and a SHA-256
inventory of every ordinary and hidden file. Python is
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
`-B`. Pytest is always given `-p no:tests.route_inventory -p no:cacheprovider` and
`--basetemp={inv}/basetemp`.

**Versions and origins (inv01).**

- Interpreter: Python 3.12.10 (MSC v.1943, 64-bit).
- Packages: pytest 9.1.1, pytest-asyncio 1.4.0, pytest-aiohttp 1.1.1, aiohttp
  3.13.3, jsonschema 4.26.0; all from the root `.venv` site-packages.
- `tools.validate.evidence`, `model`, `runner`, `clients.api`, `tests.conftest` and
  `rest_api` all import from **this worktree**, not from the root editable install.

| Inv | Purpose | Exit | Result | Key SHA-256 (prefix) |
| --- | --- | --- | --- | --- |
| inv01-probe | versions/origins | 0 | as above | stdout `da01b53e5c4465a7` |
| inv02-collect | `--collect-only` C1+C2+C3 | 0 | **18 collected**, matching my independent count of 3+1+2 / 2×2 / 5+3 | stdout `ec505229ef7499e6` |
| inv03-focused | C1+C2+C3 `-v -rA --junitxml` | 0 | **18 passed**, 0 failed/errors/skips, 1.73 s | JUnit `7005c998142da249`, stdout `bcc1263f4ec61ce3` |
| inv04…09 | counterfactual reversion (section 6) | 0,1,1,1,1,1 | see section 6 | receipts in manifest |
| inv10-counterexamples | synthetic probes + catalogue compatibility | 0 | section 7; 0 marker hits in stdout | stdout `993d06966a17c88c` |
| inv11-schema-keys | schema/env key collision probe | 0 | 0/76, 0/20 | stdout `7b2ac80607052531` |
| inv12-compat | existing `test_model`, `test_evidence_schema`, `test_runner`, `test_runner_environment`, `test_sw_api_read_04`, `test_sw_sec_auth_01`, `test_flic_runner_errors`, `test_ledger` | 0 | **76 passed, 2 skipped** (opt-in real Chromium), 65.5 s | JUnit `867cb9cd251fbad9` |
| inv13-catalogue-shapes | tuple, header-pair and string-data shapes in 1,507 real scenarios | 0 | none found | stdout `fef81059b2e8186b` |

All stderr streams were empty except inv01, whose 454 bytes are a jsonschema
`__version__` deprecation warning from my probe. I read the full streams. The final
documentation check is inv14 (section 10).

## 6. Counterexamples: failure sensitivity of the existing tests

`privacy_mutants.py` is a private pytest plugin, loaded with `-p` and selected by
`PRIVACY_MUTANT`. It reverts **one** hunk at a time, in memory: `redact` becomes
the identity only when the caller frame's `co_qualname` is that hunk's function, or
the base regex is restored. No source byte changes. Raw receipts are the tests' own
boolean `byte-receipt.json` files.

| Mutant (reverted hunk) | Exit | Failed / 18 | Receipt booleans in the failing cases |
| --- | --- | --- | --- |
| none (plugin-load control) | 0 | 0 | all true |
| M1 H1 `write_record` | 1 | 2 (C1 writer; C1 diagnostic-client) | — (C1 asserts directly) |
| M2 H2 regex | 1 | 15 (all 6 C1, all 4 C2, 5 C3 lifecycle) | record/procedure/checks/description all false |
| M3 H3 api steps | 1 | 9 (all C2, all C3 lifecycle) | procedure false, record false, checks true |
| M4 H4 runner detail | 1 | 9 (all C2, all C3 lifecycle) | checks false, record false, procedure true |
| M5 H5 describe | 1 | 5 (C3 lifecycle; 3 public-format cases still pass) | description/checks/record false, procedure true |

M2 leaves 3 cases passing: the 3 C3 public-format cases. Every hunk is therefore
covered by at least one assertion that targets it. The counterfactual reproduces
the C3 report's before-fix shape (5 failed, 3 passed, procedure safe), and M3/M4
are consistent with C2's "all three false" when both are reverted together. I did
not run that combined mutant, and this is an in-memory reversion at the tip, not
their historical bytes. C3 public-format cases passing under M5 show that the
masked and raw description formats are identical for public data. In every
mutant, raw verdicts stayed correct, so a masked value never served as an
equality oracle.

## 7. Synthetic counterexample and compatibility probe results (inv10, inv13)

| Probe | Result |
| --- | --- |
| Supported header names, nested 3 deep, 11 spellings/casings | all masked |
| Query `key`, `api_key`, `api-key`, `token`, `passcode`, `password`, `pin` | all masked |
| Public header controls (6) | all preserved |
| Tuple-nested `{"pin":…}` through `redact`, `write_record` bytes, `Action.describe`, API steps | **not masked**; aiohttp transmits the tuple as a JSON array |
| Header list of pairs `[("X-Admin-PIN", …)]` | transmitted on the wire; `Action.describe` **not masked** |
| JSON-in-string `data=` body; plain-text `pin=…` response | **not masked** in describe or record (strings get query masking only) |
| Raw `?key=` in an API step | raw in memory; masked after `write_record` |
| `Hub(path="…?key=…").describe()` | raw in memory, masked in the record; **raw in `run-summary.json`** |
| Public-looking keys | `password_protected`, `requires_scene_passcode`, `passcode_locked`, `passcode_required`, `remove_passcode`, `passthrough`, `bypass`, `token_count`, `key` masked; `admin_pin_set`, `control_pin_set`, `pin_set`, `session_level` preserved |
| Real catalogue: tuples, non-dict headers or string `data` with secret keys | 0 / 0 / 0 |

## 8. Findings

There is **no High or Medium defect in the five changed hunks.** Each hunk masks
before stringification at its boundary. Each keeps on-wire values and raw
comparisons, avoids mutating callers, and keeps public-data formatting compatible.

- **N-1 (Low; contract limit at H1/H2/H3/H5).** `redact` does not recurse tuples or
  non-dict mappings. A supported credential key inside a tuple is transmitted and
  then persisted raw: `evidence.py:127-133`, reached through `Action.describe`,
  steps and `write_record`. Reproduce with
  `act("request", method="POST", path="/x", json=({"pin": M},))` (inv10). No
  real scenario uses this shape (inv13).
- **N-2 (Low; outside the typed contract).** `headers` given as a list of pairs
  works on the wire (`api.py:121` `dict.update`), but `Action.describe` persists
  the values. The typed contract is `dict[str, str]`, and every real scenario uses
  dicts.
- **N-3 (Low; disclosed by the authors).** JSON-in-string `data=` bodies and
  non-JSON response text are only query-masked (`evidence.py:131-132`;
  `api.py:129,133`). The one real `data=` scenario carries public data.
- **N-4 (Low; unchanged sink).** `Runner._write_summary` (`runner.py:1026-1037`)
  writes `Outcome.failed_checks` descriptions and `reason` through plain
  `json.dumps`, so H1's query masking does not apply there. `Hub.describe`
  (`model.py:343-350`) is not redacted. This is synthetic-only in the current
  catalogue, because no `Hub` path carries `?key=`.
- **N-5 (Low; public-data compatibility).** The unanchored
  `pass(word|code)?|secret|token|api[_-]?key` and the anchored `key` over-mask
  public fields: 3 real `Response` descriptions (H5), the matching body
  diagnostics (H4), and procedure, state and ws_events masking widened by H1.
  Verdicts are unaffected. The cost is loss of evidence fidelity, in the
  privacy-safe direction. The regex shape predates the chain, but the chain
  widened where it applies.
- **N-6 (Info; test quality).** C3 writes `"raw_inputs_unchanged": True` and
  `"raw_verdict_correct": True` as **literals** (`test_sw_sec_data_02_c3.py:137`).
  As receipt fields they overstate what was measured; the separate assertions at
  `:106-121` are what enforce it. The tests do not cover `X-Passcode`,
  `X-API-Key` or `Cookie` through runner steps or details, tuples, string bodies,
  or over-masking negatives.
- **N-7 (Info; sibling boundary).** `clients/ha.py:490,516` formats raw
  `r['body']` into steps, the same pattern H3 fixed for `api`. Current HA bodies
  are host, port and options with no supported credential field. This is out of
  lease and not exercised.

## 9. Calibration and limits

- **Separations.** Source defects (none High/Medium; N-1…N-5 Low) are separate
  from test-quality notes (N-6), sibling residuals (N-7), unverified historical
  claims (section 2 UNKNOWN), evidence admission (none), review competence (not
  claimed) and integration (none).
- **What the evidence covers.** The probes use synthetic markers only. I read no
  owner credentials, private roots or other workspaces. I made no physical, LAN,
  release, baseline, ledger-generation or global-gate run.
- **Uncertainty.** The over-masking measurement covers scenario definitions only,
  not live device-state or ws_event payloads. The catalogue probes rely on
  `tools.validate.scenarios.discover()` at this tip. The counterfactuals are
  in-memory reversions and are not the authors' original bytes.

## 10. Evidence locations (private vs tracked)

- **Tracked.** Only this file:
  `docs/production/remediation-20261104/PRIVACY-REVIEW-ASSESSMENT/AUTHOR.md`.
- **Private, ignored scratch** (`build/remediation-20261104/privacy-assessment/`):
  - `chain-full.diff` (SHA-256 `f195b329…12f5fd`)
  - `tools/` (harness, probes, mutant plugin), hashed in `scratch-tools-sha256.txt`
    (`6b214d6c…74cc2b`)
  - `invocations-sha256.txt` (`66c8e6dd…a381c`), 639 file hashes over inv01–inv13
- **Original invocation directories:** `C:/t/remediation-privacy-assessment/inv01-probe`
  … `inv13-catalogue-shapes`, plus `inv14-docs` for the final documentation check.
  The inv14 receipt is reported through Orca `worker_done`, outside this commit,
  so this file doesn't hash itself.
- **Handling.** These are left in place for coordinator preservation. Basetemps
  hold only synthetic-marker records and boolean receipts. None of it is public or
  admitted evidence.

The commit adds only this file. It uses the documented invocation-only
`git -c core.hooksPath= commit` scoped-documentation exception after the five
documentation modules and the UTF-8, CR-aware whitespace and scope checks. There
are no source, test, tooling, report-history, registry or ledger changes, and no
claim that a source hook or the full suite passed. No push, publication or
qualification is claimed.
