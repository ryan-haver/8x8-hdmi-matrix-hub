# RV-API034 secondary review-quality and factual evaluation

**Verdict: accept, for the report-quality pin only.** The independent Anthropic
review at `12eeef938857bfd740854ccbaad34f9bc1b6ce36` substantively supports its
bounded runner/model/refusal conclusion. Its M-1 integration hold is correct.
Two minor reporting qualifications below do not require a report correction
before settling this pin. This evaluation does not accept or integrate the
OpenAI source, replace its different-family source review, clear security or
privacy gates, or qualify another domain.

## Authority and exact inputs

Evaluation date: 2026-11-04 UTC (2026-11-03 local). Assigned evaluator: OpenAI
`gpt-6-astra/high`, genuine Orca worker, Task `task_dca414868333`, Dispatch
`ctx_8017ffe0975e`, terminal `term_cdcad379-f52e-4f93-8f80-e0f3877c61a2`, existing
Run `run_37205f6095b3`. No helpers, subagents, nested workers or new model calls.
The dispatch supplies the prior competence and narrow evaluation authority;
this report does not manufacture fresh qualification or backend attestation.

The sole tracked write is this new document. The checkout entered at exact
`12eeef938857bfd740854ccbaad34f9bc1b6ce36`, branch
`execution/wp-exec-rv-api034-review-evaluation`. Its parent is exactly
`caaa4faabe9ede1e3aed37d2269efd4a4d691e04`. The coordinator-supplied untracked
`.codex/config.toml` disables multi-agent operation and remains unmodified and
unstaged (31 bytes, SHA-256
`92207a5a69cbc0f711534664a43e3d397433bab8fbd2290226a32d5e664202f4`).
Ledger, source, tests, registry, original REVIEW and qualification histories
remain coordinator-owned/read-only under the explicit dispatch restriction.

Independently verified input bytes:

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| Canonical `12ee:docs/production/software-waves/RV-API034/execution-20261101/REVIEW.md` | 23,218 | `145c899d9196ad672f2db014d5c7d8d8337835ca46e26973f64e15a7d18e5e17` |
| Original `native-final-after-release-private.jsonl` | 2,051,668 | `850a994c71acc1d4f845024a322ca67b1706679b01ccd506237b3f5df2a08888` |
| Local CRLF checkout of REVIEW | 23,505 | `8eb5e43cf867aeebe649fa5a0ca7f78e8282e8f3befda173e2639c790ae829c6` |

The local report differs from the canonical blob only by CRLF conversion;
neither copy was rewritten. The native original was read directly from
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/api034-source-review-20261103/`.
Reviewer artifacts were read directly from the retained
`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-exec-rv-api034-review/`
and original `C:/t/exec-rv-api034/` invocation directories. The retained reviewer
checkout still resolves to exact `12ee`.

For disposition context only, I read the coordinator record at pinned
`ce03d9f0df7c4667584f93240cdc0b380fb85ecd`. It is not the semantic evidence for
this judgement or a new source base. No live remote/publication verification,
archive-wide certification, qualification retake or global gate was performed.

## Native provenance and actual inspection coverage

The complete native file contains 678 JSONL entries, one session
`ad131db1-c207-495f-ac80-371efd971b04`, and the exact original reviewer cwd.
Its task preamble identifies Task `task_43fbf6bb49a2`, Dispatch
`ctx_4e0e187682b0` and terminal `term_de68c145-2d0c-400e-84dc-fbda8d79a0fc`.
All 125 assistant entries identify `claude-opus-5-5` and have
`isSidechain=false`; they represent 56 distinct message IDs, not 125 independent
model calls. High effort is the requested launch attribution, not a native
per-turn effort measurement. Live read-only Orca worker-show also matches this
Task/Dispatch/workspace and reports succeeded/settled, exited/released.

Deduplication by tool-use ID yields 62 actual calls and 62 matched results:
44 PowerShell, five Read, five Grep, four Write, three Edit, one Skill. Repeated
serialized calls/results are not retries. There are no helper/Agent/Task/team,
MCP, plugin-tool or nested-worker calls. The scripts are local inspection and
receipt operations, not hidden model delegates. Their bodies and invocations
were inspected; only the original report and assigned private scratch paths
were written. Native line references below refer to the original JSONL file.

The source window is the exact linear chain
`938ae30339790c361abdda6fdd01b11a4e498518` →
`386872316cb60130b06dd704557ae6ca1a92b5c8` →
`060769b724e7a546b8df22eac82f3b288d9bbbe8` →
`ee3f2e7f034a9ace64553e942f328dff921a1e04` →
`caaa4faabe9ede1e3aed37d2269efd4a4d691e04`.
Parent checks and numstat independently confirm nine paths, +1,053/-4.
Both report-only commits are byte-prefix appends. The original C1 AUTHOR prefix
is exactly 11,878 bytes, SHA-256
`c25692409f8d4f7ae38a21695571821475b1ec097de995517b266c2b59c4e9ff`.
Its earlier DeepSeek attribution remains historical; the four-commit window
is recorded as OpenAI Sol source with the explicitly composite coordinator
registry contribution. Git owner metadata alone does not prove model authorship.

| Actual review evidence | Native call/result lines | Evaluation |
| --- | --- | --- |
| Full model/runner/registry/scenario diff | 123/124 | All changed implementation hunks and the single scenario link are present. |
| Runner lifecycle, preparation, caller, refusal and verdict | 143/145 | Full source lines 290–809, including all of `_run_one`; independently compared with the exact candidate, zero mismatches. |
| Stack environment/start/restart/stop and SimStack | 163/165 | Full lines 40–487, zero source-line mismatches. |
| Handler, health projection and TLS policy | 193/194; 212/213 | Actual route-all handler, typed health projection, connection state/reconnect and TLS settings read. |
| Expectation implementation and model guards | 227/229; 239/240; 246/247 | `_check` 850–1024 and `_subset`, relevant expectation declarations, full Scenario fields/guard inspected. |
| Both new test modules | 294/296; 298/300 | Complete C1 220 and C2 224 source lines, plus terminal empty lines; zero source-line mismatches. Meaningful assertions inspected, not counts alone. |
| C1 append and C2 intake/author | 320/327; 339/340; 346/353 | Complete changed documentation, retained failed outcomes and limitations read. |
| API request and registry/CLI selection | 365/366; 279/286; 272/273 | Relevant helper request, scenario-existence references and CLI selection present. |
| Freshness implementation/ancestry/prefix | 542/543; 549/550; 563/564; 570/571 | Direct static inspection and append/whitespace checks support lineage and M-1. |

I independently read the report in full, changed source and assertions, and
these actual native results. All changed hunks are covered. This does not
assert that every unchanged dependency was read in full; see E-L1 below.

## Original controls, completeness and factual checks

The original six labels under
`build/software-waves/RV-API034/execution-20261101/author/` each contain direct
child argv, cwd, selected environment, start/end, return code and full separate
stdout/stderr. I recomputed all 12 stream hashes and every one of the 278
manifest-file hashes against both original temp files and preserved copies:
zero missing/mismatching files. That total is 1 collected-JUnit file, 174 focused
files and 103 documentation files. It is not a claim that every unrelated
workspace/archive file was audited.

| Original label | Direct outcome independently checked |
| --- | --- |
| `probe-01` | Exit 0; CPython 3.12.10, pytest 9.1.1, aiohttp 3.13.3, jsonschema 4.26.0; runner/model/stack/scenario/REST/matrix origins in the reviewer worktree. |
| `collect-01` | Exit 0, 54 collected: C1 13 and C2 41. Collect-only JUnit has zero executed tests, not 54 passes. |
| `focused-01` | Exit 0, 54 passed in 55.63 s; actual JUnit 54 tests, zero failures/errors/skips and matching testcase inventory. |
| `inspect-registry-01` | Exit 0; 1,508 scenarios, exactly one disconnected; F-API-034 alone links it, only `scenarios` differs, current V2/target V3 unchanged. |
| `inspect-fsec007-01` | Exit 0; read-only record/covers analysis, independently recomputed across all five source pins below. |
| `docs-01` | Exit 0, 489 passed in 2.92 s; actual JUnit 489/0 failures/0 errors/0 skips, full streams preserved. |

The original wrapper inherits `os.environ.copy()` and supplies worktree root/src
PYTHONPATH, disabled bytecode, UTF-8, unique temp/data/config/basetemp/JUnit paths,
and disabled route/cache plugins. Its `-I` is wrapper-only. It always returns 0
after recording a completed child; therefore the wrapper/shell exit alone is
not proof of a passing child. Here the actual child returncode fields, streams,
JUnit and observed records agree. The wrapper prints only the last 3,000 stdout
characters to the native display; full stdout exists on disk and was checked.

The assertion arithmetic is substantive: four refused inputs each exercise
five wrong expectations (20), six invalid offline inputs each disprove the
valid-input event expectation (6), and a real successful connected route
disproves four no-effect expectations (4): **30 counterfactual failures**.
The C2 41 cases are 11 declaration, three runtime scope, 21 strict health,
one transport, two default/external, one managed lifecycle and two wrong
managed-precondition cases. They exercise actual checker behavior, real HTTP/WS
and simulator readback, rather than accepting a fabricated result dictionary.

Both original managed and external refusal records carry exact `caaa`, clean
tracked source, eight passing checks, HTTP 503, one input-6 failure event, equal
state and no routing write/success event. The two negative managed records are
actually BLOCKED/regression, with no request and no action step; their tests
pass by requiring those outcomes. The report's statement of no failed/blocked
control outcomes means the test/inspection invocations, not the absence of
intentional blocked scenario records.

The mixed lifecycle receipt has one simulator and four hub launcher generations,
all exit 1, with the third hub alone recording TLS verification enabled.
Original logs show certificate verification failures and backoff for hub 3,
and real connected states before and after. The complete raw WS record confirms
`connected.data.matrix.state == "backoff"`; its pre-action `get_status` failure
and error event are preserved, not hidden or counted as successful sync.
No graceful-exit-0 or unobserved descendant-process claim follows.

## Findings calibration

**M-1 is correct and remains integration-blocking.** Static Git-blob analysis
used actual `gitinfo.matches`, each record's dirty paths and ancestry at every
pin, without running a gate, ledger generator or security campaign. All 28
listed F-SEC-007 records are passing, ancestral and have no covered dirty paths.

| Evidence group | Count | At 938 / 386 / 060 | At ee3 / caaa |
| --- | ---: | --- | --- |
| `2ae46e6c` sw_sec_auth V3 browser | 8 | Stale | Stale |
| `310d8b65` sw_sec_auth V3 browser | 8 | Fresh | Stale |
| `2ae46e6c` sw_sec_auth V2 API | 4 | Stale | Stale |
| `310d8b65` sw_sec_auth V2 API | 4 | Fresh | Stale |
| security_hardening wrong-PIN V2 (two per commit) | 4 | Fresh | Fresh |

The first 12 already-stale records each have three covered changes at the
base. Both edited shared paths match all 24 sw_sec_auth records; only `ee3`
touches those paths in this window. Thus the fresh maximum changes from V3
to V2 at `ee3`, matching the historical line in C2 AUTHOR:
`(b) F-SEC-007 dropped below its recorded level: level V2 < recorded V3`.
The static derivation corroborates that reported gate failure; it is not a new
global execution or certification of the original author's private gate receipt.
This is evidence freshness, not an established product-security regression.
No gate waiver, level reduction, security competence extension or acceptance
of a future refresh follows.

| Original observation | Independent judgement |
| --- | --- |
| L-1, runner 477–485 | Accurate point-in-time limitation. The new health observation is strict but does not establish cause or duration. The registered TLS environment, real backoff logs and failure-sensitive oracles support the present scenario. No false PASS is demonstrated; this is not a proof that arbitrary future disconnected scenarios cannot race. The prior attempt01 account remains historical, not recreated evidence. |
| L-2, registry 4844/4848 | Confirmed: `basis` still says no scenario while `scenarios` links it. Keeping levels unchanged is appropriate. Prose repair belongs to the coordinator under later authority. |
| L-3, C1 test 141–143 and scenario 12–14 | Confirmed obsolete healthy-Telnet/shared-runner comments after C2; no runtime impact. |
| I-1 | Source-derived fail-closed prediction is sound: external settings are operator-owned and a connected health snapshot rejects before action. No original direct external-connected test is claimed or found. |
| I-2 | Confirmed empty `hub_reads` for preparation and absent CA/fingerprint in RECORDED_ENV. Logs and explicit scenario settings provide additional private evidence; this does not repair record-alone completeness or artifact privacy. |
| I-3 | `_run_client` filters nonmember clients before `_refusal`; direct calls exercise that arm. Hardware is excluded and its skip text changes. No hardware execution is implied. |

The no-blocking-runner/model-defect judgement is reasonable **within the stated
scope**: appended default field preserves construction, enum/scope guards reject
unsafe declarations, runtime guards precede helper reads, strict booleans reject
look-alikes, transport errors propagate, ordinary Telnet preparation and hardware
branch remain unchanged, and the managed sequence restores normal settings.
The existing `_start_system` call precedes the `run()` try/finally; the observed
successful-start lifecycle is not a blanket startup-failure cleanup proof.
No new defect in that unchanged path is inferred here.

## Remaining report-quality qualifications

- **E-L1 Low, REVIEW lines 52–61: supporting-read wording is broader than the
  native proof.** All changed hunks and critical callers/assertions were read,
  but the native does not show full definition reads of `WsObserver`,
  `SimDevice`, `make_client` or `discover`; it shows their call sites/imports,
  execution and relevant discovery output. The simulator `video switch` source
  was located by a matching-line search, not a complete handler read. Interpret
  that table as traced usage, not exhaustive dependency-body inspection. A later
  author clarification could say so. This is nonblocking because those helpers
  are unchanged, the consequential runner/checker bodies were actually read,
  and the real positive/negative controls exercise the relevant behavior.
- **E-I1 Informational, REVIEW control/completeness section and native line
  449:** the probe emitted a jsonschema version-access deprecation warning;
  PowerShell's default JSON depth abbreviated nested WS data and emitted its
  explicit depth warning. Neither is a failed test or lost raw evidence. The
  raw JSON retains the nested backoff state and was independently read here.
  The report could mention these display/probe warnings for completeness;
  its zero-failed-invocation claim is not contradicted.

These qualifications do not establish a blocking factual error, missing changed
hunk, fabricated pass, hidden retry or unsupported gate clearance. The original
author, not this evaluator, would make any later correction under fresh authority.

## Evaluation checks, retained evidence and remaining gates

No focused runtime controls were rerun: the originals substantiate the claims,
and no contradiction requiring a narrow rerun was found. Own read-only audit
artifacts are retained under `build/remediation-20261104/api-evaluation/`, notably
`native-read-coverage.json`, `original-evidence-checks.json`,
`original-evidence-inventory.json`, `original-focused-records.json` and
`static-freshness.json`. They are private operational analysis, not shipped
tooling, canonical evidence or a new implementation deliverable.

Two disposable coverage-audit attempts exited 1 with IndexError while handling
native doubled-backslash paths and the extra terminal empty line in Read output.
Both errors remain in the evaluator transcript; `ancillary-error.txt` records
them. Correcting only audit parsing produced zero source-line mismatches. No
source, test, original evidence or gate was changed or retried by that correction.

Final prose verification runs the five existing modules
`tests/test_core_documentation.py`, `tests/test_client_guides_docs.py`,
`tests/test_openapi_and_config_docs.py`, `tests/test_security_docs.py` and
`tests/test_license_and_protocol_docs.py`, with
`-p no:tests.route_inventory -p no:cacheprovider`, isolated OS-inherited
temp/data/config and unique basetemp/JUnit under
`C:/t/remediation-api-evaluation/docs-01/`. Direct argv, import origins,
selected safe environment, complete streams, direct exit and JUnit are retained
in this evaluator's `docs-01/`; their actual final results accompany worker_done.
The report-only commit uses the explicitly authorized invocation-only scoped-doc
hook exception after those checks, strict UTF-8 and staged path/whitespace checks.
No implementation hook is bypassed and no full-suite success is claimed.

Acceptance of this evaluation can settle this report-quality pin only. Original
C1 lost bytes remain lost; fresh controls do not reconstruct them. Both author
FAILED/partial outcomes, the failed global FSEC007 gate and its security/V3
refresh obligation remain intact. Source integration/acceptance, VAL-14/VAL-15,
private artifact admission/publication, parent scope, images, physical HIL/LAN,
72-hour soak, week field and final release/owner gates remain separate and open
where previously open. No visual baseline or owner approval was changed.
Coordinator owns disposition, preservation, publication and worker release;
all original reviewer files and this worker's evidence remain retained.
