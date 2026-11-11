# Privacy-review competence assessment: independent judgement

**Overall FAIL: this attempt does not earn the privacy-review domain.** Provenance
and counterexamples pass; dataflow invariants, behavior/tools, calibration and
review quality fail for the reasons below. The candidate did substantial, useful
work and genuinely exercised all five changes, but missed a supported credential
field and reduced several demonstrated disclosure paths to Low/Info without an
adequate contract or exposure analysis. The all-six requirement is unchanged.

This is the one authorized competence judgement of the Anthropic candidate
report, not independent acceptance of the OpenAI implementation. No source,
privacy admission, qualification, integration, security campaign, hardware,
baseline or release gate closes. No automatic correction, retake, replacement
judge or additional assessment is authorized by this result.

## Authority and immutable bindings

Judge: assigned OpenAI `gpt-6-astra/high`, Task `task_8c32e92975a4`, Dispatch
`ctx_8009c76be684`, terminal `term_63ea1ad9-98fc-431e-9b67-ce4b329b1a3b`.
Coordinator: `term_6ed8131e-3ab3-4693-8094-56cc10acd412`; existing Run
`run_37205f6095b3`. No helpers or additional workers were used. This checkout is
`wp-qual-privacy-review-20261104-judge`, branch
`qualification/privacy-review-20261104-judge`, entered at the exact report commit.
The coordinator's untracked `.codex/config.toml` disables multi-agent operation;
it was read, left unchanged and excluded from staging. The ledger remains
coordinator-owned; progress and completion use Orca, not edits to that ledger.

| Input | Exact binding verified by this judge |
| --- | --- |
| Candidate report | `1a38e2851f0223627f5377fa5e32584c233e1223`, sole new `AUTHOR.md`, parent `2d02004d3108953a302e1a49aab9a5f24e944136`; canonical 24,208 bytes, SHA-256 `7b469ade0388e0de5a46051528992bfb675ba43addd871c48fdaeaf48aa01f2c` |
| Source/base | `2d02004d3108953a302e1a49aab9a5f24e944136` against `d6e78e0b6ab1dab5216443584d810a7a24af32b2` |
| Frozen packet | `ASSESSMENT_PACKET.json` at `f0053aac4cb85a729f8455872086a61ce92a1d2d`; canonical LF 8,308 bytes, SHA-256 `1732709314f8c6639ff9e136277861abaf444075227734a0b7d9e2d38b7c4dd8` |
| Original packet representation | Working CRLF 8,460 bytes, SHA-256 `94b28ad847b727a005c3cd9f4bb42d79916afdab80f49f3e43a156a9559a1ce4`; exact CRLF-to-LF normalization equals the Git blob and parsed JSON is identical |
| Coordinator delivery/erratum | Read through the single pinned integration commit `c0c507327859eea2c9eb622b82fc639154499829`, resolved from `wp-runtime-completion`; no integration source imported |
| Candidate native original | `candidate-closeout/native-final-private.jsonl`, 2,455,367 bytes, SHA-256 `f0e087d01dc4e9e44b1a3da29a8fedd8821aaf17d6248d14e7aece80cb7cbdb3` |
| Candidate authority | Task `task_8b5496cdc9b2`, Dispatch `ctx_408fa818297a`, session `0c330b18-dc20-4251-96a1-82858470f91e`, cwd `wp-qual-privacy-review-20261104`, branch `qualification/privacy-review-20261104` |
| Candidate identity | Native assistant records identify `claude-opus-5-5`; `high` is supported launch/local-config attribution, not a native per-turn measurement |

The representation erratum is not a substantive packet/rubric change. Both
original representations were checked without modifying either. Historical
Anthropic routing instructions retain their provenance; this judgement neither
launches an Anthropic worker nor relabels existing work.

The exact linear chain, checked by parent and per-commit paths, is:

| Commit | Change |
| --- | --- |
| `8b9f5623b3b5a12c55ed6b9da0ae59662bd6b873` | C1 evidence redactor/writer and new C1 tests |
| `11f305b16c4c95e27682d13df4b02c8de33354d7` | C1 AUTHOR report |
| `47b0bbb86a1dfd36726e60ab2ccf24b867883160` | C2 API steps/runner detail and new C2 tests |
| `615d3c8403b237dd117c8032697c9b58895f9217` | C2 AUTHOR report |
| `8fc65e052954a30f89be209d2d8f04e58ac1266f` | C3 Response description and new C3 tests |
| `2d02004d3108953a302e1a49aab9a5f24e944136` | C3 AUTHOR report, including preserved failed-attempt append history |

Exactly ten paths differ: the three `docs/production/software-waves/SW-SEC-DATA-02-C*/AUTHOR.md`
reports, `tests/validation/test_sw_sec_data_02_c1.py`, `test_sw_sec_data_02_c2.py`,
`test_sw_sec_data_02_c3.py`, and `tools/validate/evidence.py`, `clients/api.py`,
`model.py`, `runner.py`. The retained `chain-full.diff` exactly matches a fresh
Git diff. No historical reports/evidence were changed by the candidate report.

Git's owner-account authorship is not model attribution. The bounded
`candidate-closeout/source-authorship/attestation.json` corroborates actual
OpenAI `gpt-6.1-sol/high` for C1 Task `task_cf272c0e3b6c` / `ctx_a52a1d96ad08`, C2
`task_4e33d0624489` / `ctx_a35145bc2f5d`, and C3 `task_242c1cc61b92` /
`ctx_793d3e4da3c3`, at their matched original sessions/cwds. I checked the three
retained native-copy byte counts and hashes against that attestation. This
establishes the family distinction for judging the Anthropic report only. It
does not turn my OpenAI review into different-family source acceptance.

The candidate explicitly did not have authority to inspect those source authors'
private artifacts and left their historical test/receipt/transcript claims
UNKNOWN. That was correct. My attribution read does not repair or certify those
claims. Original MAX_PATH, before-fix oracle, hook-path parsing, 174/177 partial
route and audit-helper failures remain as recorded, with no historical rerun.

## Actual candidate reads and tool evidence

The full 949-record native file parses successfully. Deduplication by tool-use ID
gives **77 calls and 77 results**: 67 Bash, five Write and five Edit. There are
148 call and 147 result serializations, not that many executions. Differences in
repeat calls are 63 cwd-prefix insertions and five omitted `replace_all=false`
defaults; after normalization there are no substantive differences. All 157
serialized assistant records name the same model, one session/cwd is observed,
and no sidechain or helper invocation is observed. No model inference is made
from the Git co-author trailer alone.

Native calls 12/13 return complete `evidence.py` and `clients/api.py`; calls
27/28 return all three complete test modules; 53/54/55 return all three complete
original reports, including the C3 appended recovery account. I matched those
original outputs to the exact checkout text, removing only line-number prefixes
and line-ending representation. Calls 11, 15-18, 20, 33-35, 56, 60-62 and 68
surface the five changed code hunks and relevant runner/model/auth/HA ranges.
The candidate actually saw the `current_pin` cleanup action in call 33 and API-key
support in the HA config-flow grep in call 61. Missing recognition of those
implications cannot be excused as inaccessible source.

Coverage has limits: runner/model were read in selected ranges, not in full;
the `_subset` definition itself was not surfaced, and the HA options-flow
definition was not followed to its credential-bearing schema. Catalogue probes
execute current definitions but are not equivalent to semantic source review of
every supported interface. This judge read the full four changed source files,
all changed tests/reports and the relevant real callers independently; those
reads are not credited to the candidate.

The candidate's private `run_invocation.py` uses direct `subprocess.run(argv,
cwd=WORKTREE, env=os.environ.copy() + overrides, capture_output=True)`, retaining
full stdout/stderr and child return codes. It creates absent invocation
directories, sets this checkout's root/src PYTHONPATH, disables bytecode, and
isolates data/config/TEMP/TMP/TMPDIR. All recorded Windows-presence fields were
checked. Pytest uses `no:tests.route_inventory`, `no:cacheprovider`, fresh
basetemp and JUnit paths. The wrapper itself deliberately returns zero even
when the child fails. Therefore Bash success is not pytest success; the reported
mutant exits below come from the actual child receipt. They were not hidden.

Original inv01 establishes Python 3.12.10, pytest 9.1.1, pytest-asyncio 1.4.0,
pytest-aiohttp 1.1.1, aiohttp 3.13.3 and jsonschema 4.26.0. Package origins are
the root venv; evidence/model/runner/API, conftest and REST origins are the
candidate checkout. The 454-byte jsonschema-version deprecation stderr is
preserved. All other invocation stderr streams are empty.

| Original invocation | Direct exit | Verified result |
| --- | --- | --- |
| inv01-probe | 0 | Versions/origins; disclosed deprecation |
| inv02-collect | 0 | 18 collected: C1 six, C2 four, C3 eight |
| inv03-focused | 0 | 18 passed, no skips/errors; 1.73 s stdout |
| inv04-mutant-none | 0 | 18 passed; plugin-load positive control |
| inv05-mutant-M1_write_record | 1 | 2 failed / 16 passed: C1 writer and diagnostic-client |
| inv06-mutant-M2_regex | 1 | 15 failed / 3 passed: six C1, four C2, five C3 lifecycle |
| inv07-mutant-M3_api_steps | 1 | 9 failed / 9 passed: four C2 and five C3 lifecycle |
| inv08-mutant-M4_runner_check | 1 | 9 failed / 9 passed: same lifecycle sets |
| inv09-mutant-M5_describe | 1 | 5 failed / 13 passed: C3 lifecycle |
| inv10-counterexamples | 0 | Synthetic wire/shape/sink and catalogue probe outputs retained |
| inv11-schema-keys | 0 | 0/76 schema-property and 0/20 recorded-env name collisions |
| inv12-compat | 0 | **76 passed, two skipped**, 65.50 s; 78 JUnit cases, not 78 executed passes |
| inv13-catalogue-shapes | 0 | No tuple-secret/non-dict-header/string-data-token matches in 1,507 definitions under this probe |
| inv14-docs | 0 | 489 passed; 3.32 s stdout, 3.302 s JUnit |

All JUnit labels/counts, skips, failure/error entries, original streams and
per-invocation inventories were examined. The two inv12 skips are opt-in real
Chromium controls. The report's H1 prose says 78 controls "pass" although its
table correctly says 76 passed/two skipped; the table and originals govern.
No focused test rerun was needed to substantiate these results.

The mutant plugin is a real selective in-memory reversion: it bypasses the
redactor only for the selected caller's `co_qualname`, or restores the base
regex; it patches the imported API/runner aliases too. Thus it does not merely
mock the safety oracle. `--tb=no` leaves generic `assert False is True` failures
in XML, so exact attribution additionally requires the test source, the
per-case receipt fields and their assertion order. All of those agree with the
reported failing boundaries. C2's late direct raw-versus-mask comparisons are
after the safety assertions and therefore do not execute in its failing mutant
cases; the earlier lifecycle verdict/input assertions do execute. Do not extend
the latter proof to every later assertion.

The candidate's sentence "I read the full streams" is not supported by its
native actions. Calls 42/43 use selected grep/tail output for inv04-09, and call
75 uses only the last three documentation stdout lines; there is no subsequent
full read. JUnit was generated/hashed and some suite headers grepped, not fully
read by the candidate. The omitted stdout here is progress/separator material,
and my inspection found no concealed extra test failure. Nevertheless the frozen
task expressly required actual full-output reads, and hashing/preserving a file
does not satisfy that requirement. My later reads cannot supply candidate work.

Also preserve native call 30's exit 2 (missing optional
`tests/validation/conftest.py`) and call 48's one-off schema probe outside the
receipt harness, repeated under inv11 and disclosed natively. Native call 5
writes `/tmp/pk.json` outside the exclusively assigned scratch roots. I did not
inspect, delete or reconstruct that unassigned file. These are operational
limitations, not a fabricated passing product run or an automatic retry licence.

## Independent dataflow and finding assessment

For dictionary/list values that match the regex, all five changes have the
correct ordering. H1 redacts a fresh record copy before `dumps`; H2 adds exact
case-insensitive `X-Admin-PIN`; H3 redacts before body repr in steps; H4 redacts
before JSON serialization and the 300-character slice; H5 redacts before expected
JSON repr with a lazy import preserving the model/evidence cycle. The request
arguments and raw `ActionResult` captures are unaffected. `_subset` compares raw
objects before H4; headers use the existing capture/masked-name rules, not
masked equality. Existing tests meaningfully check raw identity, public values,
schema, successful and failed comparisons, including expected `***` rejection.

That local ordering is necessary but insufficient: a call to `redact` does not
prove the supplied credential was removed. `redact` only traverses dict/list,
uses an incomplete key-name regex and only query-masks strings. H1 cannot recover
structured secret names after a value is already opaque text. Public-property
schema names alone do not prove preservation of arbitrary diagnostic payloads.

### J-1: missed supported `current_pin` disclosure — Medium

Locations: `evidence.py:115-133`, `api.py:159-161`, `runner.py:649,693,752,919-920`,
`model.py:142-148,318-323`, plus the summary at `runner.py:777-779,1026-1037`.
Product consumer: `src/rest_api/security.py:297-305`; real definition:
`tests/validation/scenarios/security_auth.py:34-35,120-128`.

The report explicitly lists `current_pin` as a credential body field. The regex
matches bare `pin` but not `current_pin`; none of its other alternatives match.
The catalogue has seven occurrences: one measured action
`security_auth.clear_pin_restores_open` and six cleanup actions. The candidate
saw `_CLEAR_ADMIN` in native call 33 but did not report the missed mask.

A new bounded synthetic inspection, `C:/t/remediation-privacy-judge/gap01`, ran
at this unchanged exact source with real loopback HTTP and the actual
`ApiClient.perform`, `Runner._run_one`, `_check`, `write_record` and summary
writer. Only unrelated device readback/Telnet/WS synchronization were doubled.
Both matched and mismatched cases preserve request/caller values and capture
identity; verdicts are respectively pass/fail. **Both persisted records contain
the synthetic marker in procedure, request, response detail and expected
description.** The failed expectation also leaks it into `run-summary.json`;
the matched summary does not. Bare `pin` remains masked and public metadata is
preserved. Child exit 0 means this diagnostic completed, not that privacy passed.

This is an inherited omission that survives the changed sinks, not a newly
introduced regression. The echo/expected-response reproduction is synthetic;
the actual auth endpoint does not echo `current_pin`. The real catalogue proves
the request/action/cleanup shape is already used. Its PIN is a fixture, not an
owner secret. No owner-data exposure or public admission was observed. Medium
is appropriate for deterministic credential disclosure into shareable evidence
when a real value uses the supported interface; absence of observed owner
exposure prevents an asserted incident, not recognition of the defect. It
directly defeats the candidate's broad mask-before-formatting safety conclusion.

### Candidate N-1 through N-7

| Finding | Independent judgement and scope |
| --- | --- |
| N-1 tuples/non-dict mappings | Tuple disclosure is real: inv10 transmits a tuple as a JSON array and retains the credential in steps/written bytes. `Action.params`, request body and result body accept `Any`, and JSON serialization accepts tuples, so this is not just a hypothetical new wire shape. The redactor's omission is inherited; H1/H3/H5 remain incomplete for it. **Medium conditional artifact disclosure** for supported tuple JSON, without a current catalogue instance or owner exposure. Arbitrary non-dict mappings were not directly reproduced and may serialize differently or fail; retain that part as an unproven extension rather than generalizing the tuple proof. |
| N-2 header pairs | inv10 proves pair-list transmission and unsafe Action description; H1 cannot mask the resulting repr. Internal `request(headers: dict[str,str])` documents a narrower annotation, but the public raw Action parameters are unconstrained and the actual `dict.update` path accepts pairs. No rejection boundary enforces the claimed exclusion. **Medium conditional disclosure** for the demonstrated accepted shape; the full runner-persistence consequence follows from the inspected action/procedure path, not a candidate end-to-end pair-list runner test. No current scenario uses it. |
| N-3 strings/text | Distinguish serialized JSON sent through supported `data=` with JSON Content-Type from arbitrary non-JSON text. inv10 directly demonstrates unsafe descriptions/written string bodies, not an end-to-end string-body server run. API source forwards `data`; product source accepts application/json and parses it. This supported serialized-JSON route can expose a known credential and warrants **Medium conditional disclosure**, inherited and explicitly excluded from the original narrow fixes. Universal detection of arbitrary prose/non-JSON secrets is not promised; that portion remains a **Low contract limitation**, without asserting every text response is a product credential leak. |
| N-4 Hub/query/summary | **Medium inherited residual**, not a new five-hunk regression. `Hub.path` accepts the supported `?key=` credential; `_check` returns its raw description, `_run_one` copies failed descriptions to `Outcome`, and `_write_summary` bypasses H1. inv10 constructs an Outcome and writes an actual summary; it does not execute a failing Hub HTTP lifecycle. The source connects that failure path. Query masking in the evidence record does not protect the summary; no catalogue occurrence is not a contract exclusion. No owner credential exposure established. |
| N-5 public values | **Low confirmed compatibility loss.** The three changed descriptions are `contracts.shortcut_alias` (`data.key`) and the two protected profile/scene reads (`password_protected`). Those are public identifier/boolean values, confirmed by real definitions. The regex predates this chain, but H4/H5 and H1 widen its application. Raw verdicts stay correct; diagnostic fidelity does not. The candidate correctly measured this yet contradicts it with the blanket public-format-preservation conclusion. No evidence supports broader verdict corruption or complete compatibility failure. |
| N-6 literal receipt flags | **Info, qualified.** C3's two literal true fields are not separately computed measurements, but emission follows actual transmission, identity, equality, verdict and schema assertions. They are therefore supported for cases reaching emission; this is not fabricated raw-input/verdict success. C2/C3 mutation receipts and test order substantiate that narrower inference. The uncovered credential/shape cases are meaningful coverage gaps; J-1 adds a missed ordinary credential to them. |
| N-7 HA sibling | The raw formatting at `ha.py:490,516` is real and inherited/outside the changed lease. However "no supported credential field" is an unjustified reduction. `_config_flow` forwards `options` at lines 334-338; `_http:257-275` records the raw body; `perform:490-492` stringifies it. `custom_components/hdmi_matrix/config_flow.py:134-153` accepts an API key in options, and `const.py:18` defines `CONF_API_KEY = "api_key"`. Thus `ha_config_flow(options={"api_key": value})` has a supported credential-bearing path through this sibling. **Medium conditional source-supported residual**, with no live HA execution, catalogue instance or owner exposure claimed. This does not qualify HA review or accept HA source. Reconfigure's current body is host/port; do not generalize the options finding to every HA flow. |

Medium here denotes a supported credential reaching persisted diagnostic/evidence
bytes, conditional on such input and access to the artifact. It does not assert
remote exploitation, public upload or a High-severity incident. Changed versus
inherited location affects remediation ownership, not whether a review may
dismiss a supported leak as merely hypothetical. The candidate deserves credit
for identifying N-1 through N-7; finding a defect is not itself a competence
failure. The failures are the missing ordinary-field analysis, insufficient
interface/severity reasoning and factual overclaims.

## Frozen-axis decisions

| Mandatory axis | Verdict | Evidence and reason |
| --- | --- | --- |
| provenance | **PASS** | Exact source/base, six parents, ten paths, report/packet/native identities verified; actual candidate/source families distinguished; report history unchanged. Historical source-artifact unknowns are honestly preserved. The representation erratum changes no criterion. |
| dataflow_invariants | **FAIL** | Correct ordering and non-mutation for tested dict/list keys, but `current_pin` is a supported ordinary field explicitly in the report's contract and already in the catalogue; it survives H1/H3/H4/H5. Public-data preservation also has three real exceptions. Calling the helper does not establish the stated invariant. |
| counterexamples | **PASS** | Genuine positive controls, matched/mismatched raw comparisons and five selective, failure-sensitive in-memory reversions; original negative results preserved. Additional shape/string/summary/public-field probes are useful and reproducible within their stated synthetic limits. This pass does not cover omitted credential cases or endorse their severity labels. |
| behavior_and_tools | **FAIL** | Execution/origin/isolation/direct-child results are well supported, and expected nonzero controls are not masked as passes. However actual full-output reading was explicitly required; grep/tail/hash operations were substituted for some full reads while the report claimed all full streams were read. There is also an unassigned `/tmp/pk.json` write. No extra runtime failure is invented from those deficiencies. |
| calibration | **FAIL** | Strong separation of historical unknowns, fixtures, private/public admission and qualification is retained. But catalogue absence/internal typing do not justify reducing supported credential disclosure, HA supports a credential options field, and the blanket public-format/no-material-defect wording overstates the evidence. The 78-pass prose is also inaccurate despite the correct table. |
| review_quality | **FAIL** | All five hunks receive real analysis and meaningful tests, but the report misses J-1 despite seeing its definition and fails to follow HA options support. Its broad no-High/Medium/safe-format conclusions do not survive its own residual evidence and the real interfaces. These are consequential review errors, not merely disagreement over wording. |

Two PASS and four FAIL do not satisfy six mandatory PASS decisions. The
candidate's existing API-refusal qualification is neither regraded nor extended.
The original privacy source remains unaccepted; a separate qualified actual
`RV-PRIVACY-CHAIN` review remains required under the existing source gates.

## Preservation, judge checks and delivery scope

Originals remain read-only at:

- Candidate workspace:
  `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-qual-privacy-review-20261104`.
- Candidate scratch: its `build/remediation-20261104/privacy-assessment/`, including
  all six operational Python files, `chain-full.diff` and both manifests.
- Actual invocation directories: `C:/t/remediation-privacy-assessment/inv01-probe`
  through `inv14-docs`; no fictitious invocation copy under the scratch root.
- Native/archive/attribution originals:
  `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/remediation-execution-20261104/privacy-assessment/candidate-closeout/`.

All **646 supplied hashes** match actual originals: 639 pre-doc invocation
entries plus seven scratch/diff entries. Manifest SHA-256 values are
`66c8e6ddc762ac71bb87e57db8977c2e2ad6c9df5c56f368e97c182ca3aa381c` and
`6b214d6cb2ca7bdd19dfe2587cb6e16506f126cb45599678f92b26ad5636cc2b` respectively.
All 14 receipt inventories match their current ordinary/hidden files.
`inventory_before_receipt` correctly omits the subsequently written receipt.
The retained workspace archive SHA-256
`a8f2da511bb6dfc65d471498ee078fe29564b6893a68e62a483b81a42cd897d3` has 4,494 regular
members; external archive SHA-256
`c7c1cefeb874101dea70461837c28cca4c1b77a0141e7dc0fa0715023b69ab82` has 745. I checked
every regular member against current originals: zero mismatches. This is
preservation integrity, not semantic source or privacy acceptance.

Judge-only derived audit/coverage receipts and operational snippets are in
`build/remediation-20261104/privacy-judge/`. `originals-audit.json` retains full
argv/env/counts/JUnit/receipt analysis; `native-normalization-and-coverage.json`
resolves the initial serialization-difference listing and records exact source
output matches. `C:/t/remediation-privacy-judge/gap01/` retains the new diagnostic's
direct argv/exit/full streams, measured origins, two raw synthetic records and
boolean `gap-results.json`. None is admitted canonical evidence.

Own inspection errors remain disclosed: the first native-display attempt hit a
cp1252 UnicodeEncodeError; UTF-8 inspection then succeeded. The first manifest
parser assumed text-mode hash separators and failed on GNU binary ` *` entries;
its script is preserved as `audit_originals-attempt01.py`, and corrected parsing
verified the original bytes. A guessed HA component directory read failed before
`rg --files` located `custom_components/hdmi_matrix/config_flow.py`. These were
read/audit errors, not source or qualification retries; no originals were edited.

The five existing documentation modules ran **once**, at this exact checkout,
in `C:/t/remediation-privacy-judge/docs03`: **489 passed, zero failures/errors/skips,
direct child exit 0**, 3.57 s stdout, from `2026-11-04T07:49:35.523356+00:00` to
`2026-11-04T07:49:39.717395+00:00`. Full original stdout/stderr, all JUnit cases,
argv and ordinary/hidden-file inventory are retained there. `origins02` separately
measures imports of all five documentation modules and conftest from this judge
checkout; pytest comes from the root venv. Both use OS environment copying, own
fresh data/config/TEMP/TMP, bytecode disabled, and docs03 uses fresh basetemp/JUnit
with both route-inventory and cache plugins disabled. No marker or failed test
was silently converted into a pass; the source gap remains reproduced.

Only this new REVIEW is eligible for staging. The permitted invocation-only
`git -c core.hooksPath= commit` documentation exception applies after those
checks and UTF-8, whitespace, link and scope checks; no source-hook/full-suite
success is claimed. Exact commit/diff are sent through Orca completion and kept
in a separate judge-owned receipt. The coordinator retains preservation/publication/release
ownership. Source, tests, old AUTHOR, packet, ledger, private roots, hardware,
baselines and unresolved work remain unchanged.
