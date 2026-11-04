# SW-AUDIT-01 independent factual review

**Verdict: require_changes.** The 268-row structural inventory is reproducible,
but several current-state claims and prescribed actions are materially wrong.
MiniMax should correct the report; this review neither fixes its implementation
nor accepts source, evidence, privacy admission, feature qualification or parent
completion.

```json
{
  "reviewed_report_commit": "13fe2ae8d423d8e43065b08a8767109e011c61c0",
  "overall_verdict": "require_changes",
  "verified_feature_rows": 268,
  "material_findings": ["R1", "R2", "R3", "R4", "R5", "R6"],
  "not_feature_qualification": true
}
```

## Authority and exact input

- Live Task `task_b6f6a269c364`, Dispatch `ctx_e3e2bd49b348`, worker
  `term_f03d6072-9ef6-4455-a67b-037dd083eac3`, coordinator
  `term_6ed8131e-3ab3-4693-8094-56cc10acd412`, existing Run `run_37205f6095b3`.
- Selected route supplied by dispatch: native OpenAI `gpt-6-astra/high`;
  MiniMax authored the report, so the assigned reviewer family differs.
  No helper, nested worker, substitute route or external message channel used.
- Actual checkout:
  `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-exec-sw-audit-01-review`;
  actual branch `ryan-haver/wp-exec-sw-audit-01-review` (not an invented
  `execution/...` branch). Initially clean HEAD exactly
  `13fe2ae8d423d8e43065b08a8767109e011c61c0`, parent
  `b4a2c6e93918028e080fdc5ed3d7abedb3f14a9e`.
- [AUTHOR.md](AUTHOR.md) Git blob: **143808 bytes**, SHA-256
  `ee1aac572cf9b269568fcb5ac7791bf3b150d49968123f0399cb9d1fc52f17ef`.
  Working bytes equal that blob after CRLF-to-LF conversion; no substantive drift.
- Accepted plan `52ed758e711891ee57be0bbadb87c688333049733e697a52829cf0ba87d7b15e`;
  final pins and feature contracts are the prospective allocation authority.
  Dated manifest delivery states are not current authority.
- Only new tracked output is this review. Allocation-ledger updates remain
  coordinator-owned under the exclusive dispatch; this delivery supplies its
  review transition without editing that shared ledger.

## Verified structure and counting axes

Independent parsing split unescaped Markdown pipes and handled capped-level
suffixes. All 268 IDs occur once and match ledger, registry, contracts and
manifest. All primary unit/package associations and feature membership in final
pins match, as do per-row phase, target, displayed level/recorded/freshness,
live scenario IDs, clients obtained through `features_for(client)`, and complete
`covers` lists in the retained inventory. The displayed first source reference
agrees with those lists. One inherited reference does not currently exist:
`F-API-026` includes `tests/e2e/fixtures/data/themes.json`; this is a declaration
reference, not proof of a present file or tested effect.

The canonical arithmetic reproduces: **268 / 210 below / 96 stale**;
**147 software targets = 58 at + 89 below**, **120 V4 + 1 V5**. Primary units:
57 of 65; phase feature counts P1=64, P2=83, P3=121. Static discovery found
1507 scenarios, 100 feature IDs without a live declarative scenario, and 243
contracts without a WebSocket entry.

The table's primary-label census reproduces exactly:
40 PRESERVE / 40 RERUN-FRESH / 106 MISSING-ASSERT / 48 MISSING-CLIENT /
33 PHYS-OWNER-GATE / 1 REPRODUCED-DEFECT. This verifies **arithmetic and the
author's classifier output, not the truth of every semantic label**. R1, R4
and R5 require reconsidering labels/actions without changing canonical levels.

All **121** V4/V5 rows retain an owner gate in both disposition and action:
33 primary owner rows plus **88** software-action rows with owner suffixes.
Thus precedence does not erase owner authority; section 4.1's **89** suffix
rows is an arithmetic error. The 89 below-target software rows are a different
axis. Physical, CEC, 72-hour soak, week-of-use and final-release gates remain.

## Material corrections required

### R1 — retained privacy correction is not undispatched

AUTHOR sections 3.6, 4.1, 5, 6 row 4 and table row **F-SEC-014** describe no
dispatched corrective replacement; the row prescribes dispatching one. Final
pins, `SW-SEC-DATA-02.corrective_child_dispositions`, explicitly mark the old
`reproduced_finding_no_dispatch` state as dated and give current residual:
**C1/C2/C3 delivered, unreviewed/unintegrated**. Submitted heads are
`11f305b16c4c95e27682d13df4b02c8de33354d7`,
`615d3c8403b237dd117c8032697c9b58895f9217`, and
`2d02004d3108953a302e1a49aab9a5f24e944136`; functional heads are separately
recorded there.

Replace the next action with qualified retained-chain review under
`RV-PRIVACY-CHAIN`, then required corrections, admission and integration under
the accepted pins. Preserve historical VAL-15 reproduction and current open
registration, but distinguish both from a fresh reproduction at this base.
The scratch classifier sets `defect = VAL-15` from finding membership; it does
not establish an actual reproduction or absence of a replacement. An open
register row alone cannot justify the current `REPRODUCED-DEFECT` rationale.
Do not close VAL-15 or approve privacy from this correction.

### R2 — F-API-034 already has a retained assertion candidate

The absence at the integration base is real, but sections 6 row 2, 8 and the
F-API-034 action incorrectly prescribe new assertion implementation. At retained
`caaa4faabe9ede1e3aed37d2269efd4a4d691e04`,
`tests/validation/scenarios/sw_api_client_02_c1.py` binds F-API-034 to API and
contains `WsEvent("switch_all_failed", {"input": 6})`, HTTP503, no success
event, no command and unchanged-device controls. Source `386872316cb60130b06dd704557ae6ca1a92b5c8`
introduces the assertion; `ee3f2e7f034a9ace64553e942f328dff921a1e04` supplies
the later managed preparation correction. These commits are not ancestors of
the report HEAD (`merge-base --is-ancestor` exit1); `938ae303` is (exit0).

Prefer exact full-boundary review through `RV-API034` and accepted integration,
then assess remaining client/feature gaps. This is API V2, not V3 acceptance.
F-MTX-002 is not claimed by that retained scenario: inspect feature attribution
separately rather than implying the candidate already covers the matrix row.

### R3 — do not transfer a historical gate supersession to the current candidate

Section 6 row 5 and section 9 borrow W03-CLOSE-INVENTORY's older-source
supersession wording for the API-C2 candidate. The canonical F-SEC-007
V3/V3/fresh row is accurate, and the older W03 report remains valid within its
own stated scope. However the retained C2 AUTHOR at `caaa4faa` explicitly records
the actual global command at `ee3f2e7f`: **exit1, F-SEC-007 level V2 < recorded
V3**, source acceptance partial/unmet, worker outcome failed. It explicitly
does not diagnose historical onset or a new security regression.

State that candidate-specific failure and retain
`EV-API034-SECURITY-REFRESH` as unresolved. Do not call this particular gate
superseded/stale merely because canonical metadata is fresh, nor establish
usable ancestry from that metadata. No new runtime campaign or raw private
evidence inspection was performed here.

### R4 — scenario absence does not mandate new scenario implementation

The 99 scenario-less rows classified MISSING-ASSERT (100 total minus F-SEC-014)
receive blanket `author a declarative scenario` actions. This conflicts with
section 10.8's unit-level judgement caveat and exceeds what this method proves.
Examples **F-SEC-008/009** have actual non-declarative controls in
`tests/test_security_v3_hardening_scenarios.py:359` and `:386`: rate limits,
read/write separation, health exemption, unchanged simulator state and trusted
proxy/rightmost-untrusted IP assertions. These are substantive expectations,
not mere references or emitters; no conclusion about full target acceptance is
needed to disprove a blanket assertion-absence rule.

Change affected actions to inspect/reuse existing basis and controls, then name
the actual remaining assertion/client/freshness gap. Retain uncertainty for the
243 non-WS contracts. Some rows truly lack effective proof (e.g. F-KIO-012's
basis says screenshot only), but that cannot be inferred for every row solely
from declarative-registry absence. Section 8's SW-API-CLIENT-01 suggestion
`no new assertion needed` also cannot represent all six rows while two have
no declarative scenario; name the exact runnable subset and client binding.

### R5 — text containment is not a WebSocket predicate

The scratch method searches `Expectation.describe()` with substring inclusion,
without checking expectation type, exact event identity, polarity or applicable
client. This causes concrete false attribution:

- **F-SEC-001 `/ws`**: both global matches are `Response` expectations in
  `contracts.api_root` / `api_root_alias`, checking an endpoint-description
  document. They do not assert WebSocket access/PIN behavior. Correct section
  6.1 and this row's `ws asserted under other feature: /ws` claim.
- **F-API-032 `error`**: the sole WsEvent containing that string is
  `scene_execution_error`; it is not exact `error`. Likewise `connected` can
  occur inside `disconnected`, and `status` in unrelated HTTP descriptions.
  The typed bound expectations found for this row assert `matrix_connection`.
  Correct the `error` elsewhere-asserted claim and inspect startup/runner or
  other existing controls before claiming either coverage or absence.

Independent object inspection found 192 WsEvent and 5 NoWsEvent objects.
The four exact names `switch_all_failed`, `preset_recall_failed`,
`device_settings_full`, `output_name_change` are absent from expectation objects
at this base; thus the **seven feature-row** gaps in section 6.1 survive that
bounded check. Its heading must say **four unique named effects across seven
rows**, not five effects. Reassess all 25 WS-contract rows using exact predicates,
`features_for(client)` and expectation client restrictions, with non-event
contract entries treated semantically. Do not mechanically convert this review
into new scenario requirements or feature demotion.

### R6 — final reference metadata and rollups need exact corrections

Section 12.1's claimed final scratch hashes do not match two retained files:

| File | Report claims | Observed retained bytes / SHA-256 |
| --- | --- | --- |
| `author/assemble_report.py` | 3887 bytes, `edb84c4d...` | 3973 / `6fd9c35abb7b02e0e556a1f58e613b14865352b8cfaf7591b25f068aa51f74c2` |
| `author/report_tail.md` | 23002 bytes, `1c8363aa...` | 23798 / `cdd4ddd9302845d8b6c27a8072c21a8ee47a1938a7902e0f94b1d12d60538675` |

Label an earlier checkpoint explicitly if those older digests are intended;
otherwise update final identities. Inventory, rendered table, builder and other
listed scratch digests match. Section 8 also calls five entries P4; final pins
assign **four P4** and **SW-SOFTWARE-GATE-01 to P5**. Fix this and the 89-to-88
suffix count without changing the correct per-feature phase mappings.

## Preserved references, ready slices and limitations

Accepted-slice working-byte hashes match the report's prefixes for coordinator
review, freshness delta, CI review, Flic review and W03 close inventory. Separate
Git-blob hashes are retained privately; CRLF differences are not substantive
drift. The 56 CI records, four Flic records, privacy HOLD, source ancestry
limits and preservation gaps remain distinct from feature counts. No original
record, screenshot, archive payload or private credential evidence was opened.

Independently executable work within existing authority is the **report-only
correction** above. Retained API and privacy source-review slices can proceed
under their existing pins when reviewer qualification, dependencies and capacity
are satisfied; this review launches none. Existing accepted-source freshness
reruns remain candidate work, subject to exact accepted head/client/dependency
checks. No parent completion, new MVP scope or owner-gate approval follows.

Optional readability improvement: separate observed canonical state, declared
coverage, retained delivery and next acceptance action into explicit columns.
That presentation choice is optional; R1-R6 factual corrections are required.

## Checks and retained artifacts

Only the five authorized documentation modules ran with root `.venv` Python,
own checkout plus `src` PYTHONPATH, UTF-8/bytecode-off and isolated data/config.
Fresh parent `C:/t/exec-sw-audit-01/nov02-review01` was created before invocation:

```text
python -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -p no:tests.route_inventory -p no:cacheprovider -q --basetemp=C:/t/exec-sw-audit-01/nov02-review01/pytest-temp --junitxml=C:/t/exec-sw-audit-01/nov02-review01/docs.junit.xml
```

Result **exit0, 489 passed in 3.37s**, no rerun. Original stdout, stderr, JUnit,
return-code file and temporary files retained. SHA-256:

- `docs.stdout.txt`: `9021193ead506b437862c6802d219b0d45447a2c6d74d1433842aca350d7d452`
- `docs.junit.xml`: `7495ac9b283040cae598a37221681f3f1a7c85fe9f0de1a2ffc915980e654813`
- `docs.exit.txt`: `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354`
- Empty `docs.stderr.txt`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The retained author's documentation stdout independently says 489 passed in
3.03s, 588 bytes, SHA-256
`0940f4b85335432eddc206cb41ec7d12561b03e54a0b21132c34a4731fc46dee`.
No separate author JUnit/return-code receipt was present at that inspected temp
location; its exit0 remains the author's recorded claim, not reconstructed proof.

Own ignored `build/software-waves/SW-AUDIT-01/execution-20261101/reviewer/`
contains one-off `inspect.py`, `inspection.json` and `effects.json`; these are
inspection aids, not product tooling. The first script launch failed because
its name shadowed Python `inspect`; running it via `runpy` from the checkout
resolved that without deleting it. Earlier bounded probes encountered a default
Windows decoding error, guessed nonexistent paths and an incorrect `event_type`
attribute (actual field `event`); those failures are not passing checks or
runtime failures. Corrected observations above use explicit UTF-8 and actual
paths/fields. No source tests, generators, campaign, services, Docker, hardware,
package installation or evidence import ran.

Final checks cover this report's UTF-8, newline/trailing whitespace, local link,
JSON verdict, exact staged scope and CR-aware Git whitespace. Commit uses the
dispatch-authorized invocation-only `git -c core.hooksPath= commit` for this
single prose file; no full source-hook success is claimed. Coordinator owns
publication, preservation and author correction routing; no push, merge, tag,
cleanup or self-release is performed.
