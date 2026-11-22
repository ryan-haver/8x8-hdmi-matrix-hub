# Manual attempt 02 independent judgement

Overall verdict: **FAIL**. The evaluator demonstrated useful bounded source
reasoning and real managed controls, but did not demonstrate the mandatory full
review provenance and made material, contradicted claims about its evidence.
This is a completed evaluation-quality judgement, not source rejection or source
acceptance and not the coordinator's final competence disposition.

Judge authority: Task `task_c8b55f48fcff`, Dispatch `ctx_6f1b83d8f673`, terminal
`term_40ebc9e8-9038-43b7-904d-1fb4a78fa09f`, existing Run `run_37205f6095b3`.
Assigned native OpenAI `gpt-6-astra/high`; no helpers or model substitution.
The owner-authorized single retake and fresh judgement supersede the dated
checkout provider exclusion for this task only. I read the complete shared-root
`QUALIFICATION_MANUAL02_AUTHORIZATION.json`,
`QUALIFICATION_MANUAL02_JUDGE_PREFLIGHT.json` and frozen
`QUALIFICATION_RUBRIC.json` under
`docs/production/software-waves/MVP-EXECUTION-20261102/`.
The allocation ledger and lifecycle/publication remain coordinator-owned under
this report-only lease; this report supplies the actual judgement record.

```json
{
  "attempt": 2,
  "evaluator_report_commit": "78eea1519cd4b6c8ac626b28ee45281f43623198",
  "candidate_source": "caaa4faabe9ede1e3aed37d2269efd4a4d691e04",
  "review_base": "938ae30339790c361abdda6fdd01b11a4e498518",
  "rubric_sha256": "66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672",
  "per_axis_verdicts": {
    "provenance": "fail",
    "invariants": "pass",
    "counterexamples": "pass",
    "behavior_and_tools": "pass",
    "calibration": "fail",
    "review_quality": "fail"
  },
  "overall_verdict": "fail",
  "qualified_domain_if_any": null,
  "source_acceptance": false,
  "first_attempt_status_preserved": "FAIL",
  "further_retry_authorized": false
}
```

The reviewed [AUTHOR.md](AUTHOR.md) is exactly 16,677 canonical Git bytes,
SHA256 `4dfbfc8a77c6ad910dc34eac55b62611195fe601ee6996dc2818ded7de988942`;
the original evaluator working file matches byte-for-byte, including LF.
The report commit's parent is the candidate above and its sole change is this
AUTHOR.md. The rubric's bytes match its frozen SHA256 above.

## Exact boundary and provenance — FAIL

I inspected the complete nine-path base-to-candidate diff, all three complete
source reports (including the original DeepSeek record), current assertions and
relevant runner/stack context. Actual ancestry is:

```text
938ae30339790c361abdda6fdd01b11a4e498518
  -> 386872316cb60130b06dd704557ae6ca1a92b5c8
  -> 060769b724e7a546b8df22eac82f3b288d9bbbe8
  -> ee3f2e7f034a9ace64553e942f328dff921a1e04
  -> caaa4faabe9ede1e3aed37d2269efd4a4d691e04
  -> 78eea1519cd4b6c8ac626b28ee45281f43623198 (evaluation report only)
```

`38687231` adds the C1 scenario/tests, coordinator registry contribution and
101 report lines; `060769b7` adds another 111 C1 report lines, including the
failed/partial preservation disposition. `ee3f2e7f` adds the compatible model/
runner preparation, C2 tests/intake/report and inherited scenario update;
`caaa4faa` adds 103 C2 report lines retaining the global gate failure.
The nine paths comprise those three reports, registry, scenario, two tests,
model and runner. The historical DeepSeek product-handler work precedes this
window; these validation follow-ups are OpenAI work, with coordinator registry
ownership, as their records state. Git account identity does not replace actual
model authorship.

**J1, major evaluation defect:** AUTHOR lines 35–39 and JSON line 123 explicitly
say `060769` is outside and was not reviewed. It is an intervening ancestor
inside the required boundary, not the review base. This is not merely an
incorrect commit count. The complete preserved native session's actual tool
calls show a nine-path `git diff --stat`, reads of runner/model/scenario/two
tests, and a diff restricted to runner/model/registry. Its seven unique Read
calls comprise those five files plus authorization and rubric; no tool reads
any of the three changed source reports or a complete nine-path diff. The
capture contains 29 unique tool IDs (20 Bash, seven Read, two Write); duplicate
serialized appearances were deduplicated by tool ID. No private reasoning was
used. The submitted boundary claim is contradicted and the required complete
source/report inspection was not demonstrated. My subsequent inspection cannot
retroactively supply the evaluator's missing work.

The captured native file is 1,294,061 bytes, SHA256
`1538b9810b23f8ec7e5733b81c353e5864ca769523b63a42120a98f0ec21a8a5`.
Actual assistant model metadata identifies `claude-opus-4-7`, stronger evidence
than the report's model-id reminder. High effort is supported by the supplied
launch/local-configuration attestation; native per-turn effort is not exposed.
No Agent/Task/team/MCP tool is observed in that capture. This does not establish
an OS descendant census. Route identity passes this component but cannot cure
J1. Correct disposition requires acknowledging the four-commit boundary and
missing coverage, not silently replacing the frozen base.

## Invariants — PASS

The evaluator correctly explains the important bounded behavior, independently
corroborated in `tools/validate/model.py:472–482` and
`tools/validate/runner.py:467–485,553–554,620–631`:

- The new Scenario field is appended after `notes`, defaulting to `ready`, so
  prior positional fields and default behavior remain compatible. The inherited
  C1 scenario explicitly changes to `disconnected`; the report's claim that no
  existing scenario file was touched is too broad.
- Declaration and direct runtime guards require simulator-only, API-only failure
  shape without declared writes, setup, cleanup or faults. `_refusal` additionally
  rejects hardware/other clients before scenario execution.
- Health must be HTTP 200 with dictionary envelopes and identity-true success/
  configured and identity-false connected. Missing/loosely typed values and
  transport failures cannot stand in for observed disconnected health.
- Ready preparation delegates to the existing Telnet waiter; its external-hub
  exception remains. Hardware retains the prior waiter branch. External
  disconnected preparation now observes health, while operator settings remain
  untouched. No live hardware or external deployment was tested.
- The registry only appends the scenario under F-API-034, preserving
  `routing.route_all`, levels and evidence. Schema/client/stack/product REST
  sources do not change; no evidence/schema weakening is present in this diff.

The report's absolute “no mutating side effect is possible” (line 158) exceeds
these facts: `_run_one` still resets the simulator before preparation, and a
`writes` declaration is not a universal proof about an arbitrary action. The
specific refused action has real no-write/state assertions. I treat this as a
calibration limitation, not an invented product defect or a reason to fail the
otherwise demonstrated bounded invariant explanation.

## Counterexamples — PASS

I inspected the actual complete C1/C2 assertion files and the original JUnit
case names, rather than accepting the green summary alone. The 54 cases are:
C1 4 valid disconnected inputs, 6 malformed inputs, 1 connected positive,
1 external source-runner and 1 discovery test; C2 11 declaration negatives,
3 direct target/client guards, 21 strict envelope negatives, 1 transport
failure, 2 default/external controls, 1 managed mixed lifecycle and 2 wrong
managed-precondition controls.

C1 lines 66–124 assert exact refusal/body/int-normalized WS input and unchanged
state; five counterfactual expectations must fail. The connected real route
changes routing and defeats no-command/no-state-change/no-event oracles.
Malformed requests cannot satisfy the registered valid-input event oracle.
C2 lines 24–112 exercise declaration restrictions, direct refusal before helper
reads, malformed/missing/unconfigured/connected/non-boolean/non-200 health,
transport failure and actual Telnet/default delegation. C2 lines 159–224 check
schema-valid eight-check managed refusal, healthy/disconnected/healthy hub
restarts, and blocked preparations with no action step or recorded request.
The connected negative deliberately first establishes connectivity through
`contracts.cables`, avoiding the historical listener-readiness race.

AUTHOR's “12” declaration rows and “four” counterfactual expectations are
actually 11 and five; its enumerated counterfactual list itself contains five.
Those count slips do not erase meaningful executed controls and do not alone
fail this axis. No new focused subset or campaign was needed or run by me.
Execution is the evaluator's actual candidate run; historical before/after
claims remain static analysis or explicitly historical evidence.

## Behavior and tools — PASS, with bounded facts

Original parents are retained read-only at
`C:/t/exec-qual-anthropic-core-01/nov03-manual02/{val-01,docs-02}/`.
I verified complete stdout/stderr/JUnit bytes against their actual manifests,
commands, cwd, safe environment, versions, direct subprocess returns and times.
The capture driver uses `subprocess.run(..., capture_output=True)` and records
`proc.returncode`; its own final return of zero is not the test-return oracle.
Actual native commands show one test invocation for each parent, plus version
queries, not a second focused test attempt.

| Original invocation | Direct exit / JUnit | SHA256 stdout | SHA256 JUnit |
| --- | --- | --- | --- |
| val-01, 17:09:13.287700–17:10:08.489126 UTC | 0; 54 tests, zero errors/failures/skips; 54.517 s | `b363ba21eb23942113b79fb485146a008125eaf66049ffb67667953846c374c0` | `370161f3a686a0dac23dc8d36893fec06463ec8050d28809b05a84587f1ce7fb` |
| docs-02, 17:10:39.496216–17:10:43.325387 UTC | 0; 489 tests, zero errors/failures/skips; 3.145 s | `98c366a9aab7839b6b76cb567e38a7e13b291187938a6cdb40d738371779a474` | `383e59156d60b6152ca3dfbf41015e35625e79c0cf2aae3a13a69b454eb10fba` |

Both stderr files are empty, SHA256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
Manifest SHA256 values are respectively
`20085c6a7725e3be3cd50232fffc72254ca762f199550dcd7cf49c6282f66b1b` and
`5b45da6904ce4c4d390935340c95b3ef0f389f41d597e80457a46cff2c68812f`.

The real external-stack receipt records configured=true/connected=false and
both known handles exited with code 1. The three managed receipts record five,
three and three children, all with numeric exit 1. These are settled known
handles, not evidence of every descendant or of a particular termination cause.
The four F-API-034 records are two pass/ok records with eight checks and one
request each, and two blocked/regression records with zero checks/requests.
The mixed lifecycle also emits other-feature records. Actual assertions verify
refusal payload/event/state/log behavior; no credentials or raw payloads are
published here.

Distinct explicit basetemp/native-temp/data/config parents prevented the docs
run from reusing validation output. The immediate driver retained streams and
JUnit; a pre-docs sidecar hashed 70 JSON files in val-01/pytest-temp. It was not
a complete immediate hash inventory of ordinary/hidden/native-temp/log files.
The two completed coordinator preservation manifests attest later full capture:
4,652 workspace files/298,183,314 bytes and 283 external files/687,290 bytes.
I independently matched all 283 current external regular files to the completed
manifest with zero mismatches, and all 70 sidecar hashes to originals. No loss
of attempt02 originals is demonstrated. Later complete preservation is not
retroactive proof of an earlier full capture. This passes the rubric's retained
actual-execution/process-evidence requirement with these explicit limits.

Both pytest argv arrays include `-I`. It ignores Python environment settings,
including PYTHONPATH and PYTHONDONTWRITEBYTECODE; merely recording those values
does not prove they were effective for the pytest parent. Pytest's local test
imports and `tests/conftest.py:46–47` insert this checkout's src; the inspected
fixtures/receipts use the intended candidate. Application TEMP/TMP/data/config
settings remain applicable. Thus this is an invocation-explanation/bytecode
claim defect, not evidence that the 54 tests ran against a different source.

## Calibration — FAIL

**J2, major evaluation defect:** AUTHOR lines 110–111 and 181–183 call the
sidecar published/shipped beside the report; the exact commit tree contains
only AUTHOR.md. The actual `build/.../author/val-01-receipts.json` is ignored,
private supplementary metadata. Its 70 JSON entries are valid hashes but do
not describe a shipped artifact or complete evidence inventory. This matters
because a downstream reviewer is directed to unavailable proof and told it is
published, despite the evaluator's own captured `git check-ignore` confirming
otherwise. No privacy clearance or evidence admission follows its existence.

**J3, material evidence-scope error:** AUTHOR line 110 reports 177 and one file
under val-01/docs-02. Actual originals and the completed preservation manifest
contain 177 and **106** regular files. Validation comprises 138 pytest-temp,
35 native-temp and four top-level files; docs comprises 102 pytest-temp and
four top-level files. The report also claims six distinct F-API-034 records
(line 149); there are four, including two blocked controls, among seven total
feature records. This misstates the feature-record population and
inventory scope; the two blocked controls must remain distinguishable. The reported 764 KB is a filesystem `du` figure, not the
468,822 logical validation bytes; that size-unit ambiguity alone is minor.

Numeric code 1 plus the source stop helper does not independently establish
“Windows-signal termination” (lines 94,148). `tools/dev_stack.py:48–57` can see
an already exited process, terminate it, or kill after timeout; the receipts
record the exit number, not which branch caused it. The observed exits remain
useful. Similarly, the PYTHONPATH/bytecode and absolute no-side-effect claims
need the limitations stated above.

The report correctly preserves the first attempt FAIL, does not reconstruct
lost first-attempt bytes, retains the F-SEC-007 global gate failure without a
retry/waiver, and claims neither V3 nor source integration. I do not infer a
product defect's onset or absence from that historical gate. Those strengths
are credited. J2/J3 still materially misstate evidence availability/completeness;
this mandatory calibration axis therefore fails, rather than treating the
whole issue as harmless counting terminology.

## Review quality — FAIL

The no-finding rationale is substantive about defaults, guards, health and
non-vacuous controls. However the frozen axis also requires factual correctness
and comparison of claimed execution with originals across the declared scope.
J1 omits report-bearing provenance within that scope, while J2/J3 misdescribe
what the retained proof contains and where it is available. A technically
plausible code explanation and passing pytest summary cannot satisfy that
complete requirement. These are actionable findings against this evaluation
report: correct its coverage/status and evidence scope before relying on its
claims. They do not authorize another attempt or an automatic author rewrite.
No new candidate product-source defect is established by this judgement.

## Judge verification and disposition

Private judge audit: `build/software-waves/QUAL-ANTHROPIC-CORE-01/manual-attempt-02/reviewer/originals-audit.json`,
SHA256 `1456512d5d5f82f7a42fa1003286154545e23bc8f21a3f966ecd51379ab4b952`.
It contains sanitized hashes/counts and actual tool metadata without native
transcript payloads or reasoning. Existing originals were read-only. No source,
test, fixture, registry, schema, evidence, dependency, baseline, root manifest
or lockfile changes; no global gate, ledger generation, network/hardware/CI/
Docker/HA/campaign run, push, merge, cleanup or worker release.

The required single fresh five-module documentation invocation exited **0**:
**489 passed in 3.23 s**, zero JUnit failures/errors/skips. It used the root venv
Python with explicit `-B`, own checkout/root+src PYTHONPATH, UTF-8, isolated
created data/config/native-temp/pytest-temp directories, TEMP/TMP, both plugin
disables and explicit forward-slash basetemp/JUnit under
`C:/t/exec-qual-anthropic-core-01/nov03-manual02-judge/docs-01/`.
The five modules were core documentation, client guides, OpenAPI/config,
security and license/protocol. Full argv, safe environment, tool versions,
start/end and direct subprocess exit are in that parent's manifest:
SHA256 `367cbeecd5e8d49f738fdf72f8707cba1e3e68fc61c5b4379439d245404fa4bc`.
Stdout SHA256 `a153a7f288f6066e4203bbbdaab053bbbf3de549c2ac612b94ed8af17f5f4545`;
JUnit SHA256 `fdf42647ba8242d2a93bafab593e8e9895dcc6d30c3bfd206871f217f7b91e73`;
stderr is empty with the empty-file SHA256 above.
All 106 produced files/167,143 bytes, including hidden/temp files and originals,
were copied and hash-verified into own ignored `reviewer/docs-01-preserved/`
before another invocation. Preservation manifest
`reviewer/docs-01-preservation.json` SHA256:
`23ae80ee4cf5c1c3ac0706fe1e60bae3799da148b66cafe69f127516c4e4a707`.

Strict UTF-8/LF, fenced JSON schema/axis/decision consistency, existing local
reference, exact new-report scope and CR-aware whitespace checks passed.
The prose-only commit uses the authorized invocation-only empty hooksPath
exception; no repository/global hook setting changes. Documentation checks
establish hygiene, not semantic review quality, source-hook success or source
acceptance. Canonical Git bytes and working representation are separately
verified in the private delivery receipt, avoiding a self-referential hash.

No domain is qualified by this failed judgement. The only domain eligible had
all axes passed would have been bounded Python validation-runner/model offline
simulator API refusal preparation and relevant compatibility guards. Coordinator
alone records final disposition; no blanket authentication/privacy/UI/HA/image/
physical qualification or qualification of dependent packages follows. Original
three Tron approvals remain closed; source/privacy/HIL/72-hour soak/week field/
final version and artifact release gates remain unchanged. First attempt FAIL
is preserved independently and no further retry is authorized.
