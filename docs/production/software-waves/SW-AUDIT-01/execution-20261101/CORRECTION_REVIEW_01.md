# SW-AUDIT-01 independent correction re-review 01

**Verdict: require_changes.** The corrected inventory reproduces its structural
counts and improves several historical dispositions, but still contains factual
contradictions and unsupported next actions. This is ordinary independent
metadata review, not a core qualification retake, source acceptance or product
acceptance. Parent-unit closure is **not supported**.

```json
{
  "reviewed_author_commit": "981e7e4a48bce07e4dce24443d386b3e0643601a",
  "original_review_commit": "4c2d18b8cdd3f49523e9014e498bbfd7d55601ac",
  "overall_verdict": "require_changes",
  "R1_R6_dispositions": {
    "R1": "require_changes: obsolete undispatched claim survives in method 3.6",
    "R2": "accept: retained API-V2 full-boundary review precedes new implementation",
    "R3": "accept: candidate-specific failed global gate remains unresolved",
    "R4": "require_changes: incorrect runnable subset and non-WS row actions",
    "R5": "require_changes: client and attribution gaps lost; stale error claim survives",
    "R6": "require_changes: hashes and phase split corrected, counting contradiction remains"
  },
  "verified_feature_rows": 268,
  "not_feature_qualification": true,
  "parent_unit_closure_supported": false
}
```

## Authority and exact representation

Task `task_2e497661d2af`, Dispatch `ctx_4ec26c6917ca`, worker
`term_cfcfc101-0c4c-45cd-b6c1-b244f75b5772`, coordinator
`term_6ed8131e-3ab3-4693-8094-56cc10acd412`, existing Run
`run_37205f6095b3`. Dispatch selects native OpenAI `gpt-6-astra/high`, a different
family from the MiniMax author; this report makes no additional backend
attestation. No helpers, nested workers or route substitution were used.
Live Orca status returned version 1.4.246 and runtime
`e8ce3460-a9d4-4897-8e4f-10a8e3cdc400`.

Actual isolated checkout is
`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-exec-sw-audit-01-rereview01`,
branch `ryan-haver/wp-exec-sw-audit-01-rereview01`. Initial clean HEAD equals the
reviewed commit, with exact parent `13fe2ae8d423d8e43065b08a8767109e011c61c0`.
The original REVIEW was read directly from its immutable Git commit, not from
an old working report. The only tracked output is this new report; allocation
ledger maintenance and acceptance remain coordinator-owned.

[AUTHOR.md](AUTHOR.md) was reviewed from the exact committed blob:
**195324 bytes**, SHA-256
`f2870b27b3ad12a4f9e0a9d332acfab80a7d2fa23ef128e6fce193cd5d3223c2`.
Its working representation is **196430 bytes**, SHA-256
`07c5836d89bc7d38538d329250be1e3a36a466f90fb56138ca0b76738d993875`,
with **1106 CRLF sequences**. Independently replacing only CRLF with LF exactly
reproduces the Git blob. The delivery's working-file identity was mislabeled as
a Git-blob identity: this is an explicit representation erratum, not substantive
content drift. The incorrect old identity validation is **not** called passed.

## Independently reproduced structure

One-off inspection parsed unescaped Markdown pipes and joined all 268 unique
IDs against the canonical ledger, registry, feature contracts, manifest and
final pins. All unit/phase/target mappings, scenario ID sets, declared clients
through `features_for(client)`, full `covers` source-reference sets and displayed
first references agree with the corrected records. Source references are
declarations, not fresh runtime evidence. No file existence, execution or
qualification is inferred from a `covers` entry.

Canonical arithmetic reproduces **268 features / 210 below / 96 stale**;
**147 software targets = 58 at + 89 below**, **120 V4 + 1 V5**. Primary owners
are 57 units; phase feature counts are P1=64, P2=83, P3=121. Numeric level,
recorded baseline and freshness agree; the 12 capped rows lose the displayed
asterisk despite the table legend, as noted under R6.

The actual primary-label census is **39 PRESERVE, 41 RERUN-FRESH,
47 MISSING-CLIENT, 32 MISSING-ASSERT, 7 DECLARATIVE-GAP,
68 COVERAGE-UNRESOLVED, 33 PHYS-OWNER-GATE, 1 RETAINED-CHAIN-OPEN**.
All eight transition groups in section 4.3 reproduce, totaling **77 changed
rows**. This verifies arithmetic, not semantic acceptance of those labels.

Static discovery returns **1507 scenarios**. All **100** scenario-less rows
reproduce the author's bounded registry-text classification: **72** have the
non-declarative-basis label and **28** match its no-effect phrase rule.
The 72 remain uninspected proof, and the 28 are statements in registry basis,
not independent runtime observations. There are **25** WS-contract rows and
**243** non-WS rows; full assertion adequacy for the latter remains unknown.

For all 25 WS rows, independent object inspection used actual `WsEvent` and
`NoWsEvent` types, exact `event`, positive/negative polarity, expectation
`clients`, declared scenario clients and `features_for(client)`. The extracted
typed states and bound scenario/client sets reproduce after deduplicating
repeated tuples. Non-event entries `/ws`, `all broadcasts` and client command
`ping` do not become event proof. The problems below occur when those facts
are converted into primary labels and acceptance actions.

All **121** owner-target rows retain an owner disposition and action:
**33** primary owner rows plus **88** software-action suffix rows. They remain
distinct from the **89** below-target software rows. No software completion
follows from numeric level, fresh metadata, or this census.

## R1 — partially corrected, still require changes

Sections 0, 4, 5, 6 and the F-SEC-014 row correctly retain historical VAL-15
reproduction and direct qualified retained-chain review. Final pins under
`SW-SEC-DATA-02.corrective_child_dispositions.current_residual` explicitly say
C1/C2/C3 are **delivered, unreviewed/unintegrated**, with submitted heads
`11f305b16c4c95e27682d13df4b02c8de33354d7`,
`615d3c8403b237dd117c8032697c9b58895f9217`,
`2d02004d3108953a302e1a49aab9a5f24e944136`.

However **section 3, item 6 (lines 174-179)** still defines a reproduced defect
as open with no dispatched replacement, then explicitly identifies VAL-15 on
F-SEC-014 as that case. Correct this surviving present-tense assertion to match
the retained-chain disposition. Preserve historical reproduction, the open
finding and qualified review/admission/integration gates; do not claim a fresh
reproduction or close VAL-15.

## R2 and R3 — corrections accepted within factual scope

The F-API-034 row and unit crosswalk now prefer full `938ae303` through
`386872316cb60130b06dd704557ae6ca1a92b5c8`,
`ee3f2e7f034a9ace64553e942f328dff921a1e04`, and
`caaa4faabe9ede1e3aed37d2269efd4a4d691e04` review/integration under RV-API034.
Direct inspection of the retained scenario confirms F-API-034-only API binding,
HTTP503, exact `switch_all_failed`, negative success/failure controls, no command
and unchanged state. That is a retained **API V2** candidate, not V3 evidence
and not F-MTX-002 attribution. No new source acceptance follows here.

The retained C2 AUTHOR at `caaa4faa`, read as a Git blob, explicitly records
the actual global gate at `ee3f2e7f`: **exit1, F-SEC-007 V2 below recorded V3**,
partial/unmet source acceptance and failed worker outcome. Corrected section 6
row 5 preserves this distinct unresolved failure and does not derive onset,
causality or supersession from canonical V3/fresh metadata. The older W03
history remains scoped history; EV-API034-SECURITY-REFRESH is still owed.

## R4 — unresolved intake improved, runnable slice and actions wrong

The blanket new-scenario prescription has been removed from row actions.
The existing F-SEC-008/009 rate-limit and trusted-proxy controls are substantive
as the original review stated; targeted source inspection confirms their
status/state and rightmost-untrusted-address assertions without executing them.
Keeping uninspected basis as unresolved is appropriate.

**Section 8, SW-API-CLIENT-01** nevertheless misstates both membership and
runnability. Its six rows are **F-API-001/003/004/005/006/007**, not a set
containing F-API-029. Four have API declarations: 001, 004, 005 and **007**
(`presets.recall`); only 003 and 006 lack declarations. F-API-029 belongs to
SW-API-READ-03 and has a live declaration. The proposed browser run is not
an existing client-bound subset: `contracts.api_docs`, `contracts.health` and
`cec_controls.status_off` declare only API; `routing.switch_one` declares a
browser client but binds that client to F-MTX-001/F-UI-002, not F-API-005.
Likewise `presets.recall` binds browser to F-MTX-003/F-UI-005, not F-API-007.
Name the actual API runnable subset and retain unresolved V3 intake instead of
describing a currently runnable browser proof for these API features.

**All 28 no-effect-basis rows** incorrectly receive action text about
"exact contract WS event(s) this feature" and a missing non-declarative WS
control although their WS column says **no ws contract entry**. Exact affected
IDs: F-KIO-005/006/007/009/012/013 and
F-UI-003/007/009/010/011/013/016/017/018/019/020/021/022/023/028/029/030/032/033/034/035/036.
Use the actual basis limitation and bounded intake action; do not fabricate a
WS contract or turn a registry phrase into independently established absence.

## R5 — typed extraction improves, semantic conversion still fails

- **F-SEC-001:** recognizing `/ws` as a non-event does not remove its V3 client
  requirement. Target remains V3 and live bindings are API-only. Yet the primary
  label becomes RERUN-FRESH and the sole action is an API run. The private
  corrected record also retains `software_gap: missing assertion` while
  `corrected_gap` says RERUN-FRESH. Recompute the remaining client/semantic scope
  after excluding the false event; preserve the real-client gap or explicitly
  unresolved intake. An API freshness run cannot establish V3.
- **F-MTX-001 and F-REL-012:** WS subfields correctly say `switch_failed` and
  `signal_change` are bound elsewhere, and section 6.1 calls these attribution
  gaps, but the primary labels/actions say owner-only and "no SW-AUDIT-01
  action; preserve accepted evidence." **F-CEC-006** similarly lists
  `cec_command` elsewhere while its action addresses client/freshness only.
  Give these attribution gaps an explicit inspection/reuse disposition, or
  supply concrete evidence rejecting them. Numeric freshness cannot erase the
  report's own named gap; no automatic demotion or new implementation is required.
- **Section 6, blocker row 3 (line 349)** still says F-API-032 `error` is
  asserted only under other feature IDs. That directly contradicts the corrected
  typed result: exact `error` is absent from declarative WsEvent objects;
  `scene_execution_error` is different. Remove the surviving substring claim.
- **Section 6.1's counting scope:** four named effects occupy **eight** rows in
  its current table: API-034/MTX-002, API-035/MTX-003, API-037/DOM-032,
  API-040/MTX-024. The earlier review's seven-row subset excluded scenario-less
  DOM-032; this expanded table includes it. State seven for the narrower subset
  or eight for the displayed complete mapping, rather than copying the old
  count into the expanded scope. The four exact names remain absent from typed
  declarative expectations at this commit; retained candidates stay separate.

Non-declarative call-site matches locate candidate controls; they do not by
themselves establish matching polarity, client, full feature coverage or target
adequacy. The report's bounded-negative caveat should govern its stronger
"demonstrated gap" language as well. No source fix is prescribed by this review.

## R6 — identities and phases accepted, residual counting/display fixes

All **22** fully identified author artifacts in sections 12.1/12.2 match their
retained byte counts and SHA-256 values. This includes corrected final
`assemble_report.py` (3973 bytes,
`6fd9c35abb7b02e0e556a1f58e613b14865352b8cfaf7591b25f068aa51f74c2`)
and `report_tail.md` (23798 bytes,
`cdd4ddd9302845d8b6c27a8072c21a8ee47a1938a7902e0f94b1d12d60538675`).
Earlier digests are now correctly labeled historical checkpoints. Original
author artifacts were read only; no archives or raw validation records were
opened. This verifies the named retained identities, not every unlisted
historical file against an unavailable earlier full-tree snapshot.

Four P4 units plus the P5 SW-SOFTWARE-GATE-01 are correctly separated. However
**section 4.2 (line 284)** still says `89 + 32 = 121` owner rows immediately
after distinguishing 89 software-below rows from 88 owner suffixes. The owner
decomposition is **88 + 33 = 121**. Correct the mixed-axis sentence.

The table legend and section 5 say capped rows display `V1*`, but all 12
F-MTX-007/008/009/010/011/012/013/014/015/016/017/020 show bare V1.
Private records retain `capped: true` and owner finding-closure actions remain;
restore the promised display annotation or make its absence explicit. This is
not an uncapping or finding closure.

## Checks, retained evidence and limits

The only test run used root `.venv/Scripts/python.exe`, own checkout plus `src`
PYTHONPATH, UTF-8, bytecode off, fresh created data/config/temp parents under
`C:/t/exec-sw-audit-01/nov02-rereview01`, and explicit forward-slash basetemp:

```text
python -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -p no:tests.route_inventory -p no:cacheprovider -q --basetemp=C:/t/exec-sw-audit-01/nov02-rereview01/pytest-temp --junitxml=C:/t/exec-sw-audit-01/nov02-rereview01/docs.junit.xml
```

Direct subprocess result: **exit0, 489 passed in 3.06s**, no rerun. Full original
stdout, stderr, command/returncode JSON and JUnit/temp bytes are retained.
Private review namespace is
`build/software-waves/SW-AUDIT-01/execution-20261101/reviewer/re-review-01/`.
It contains independent metadata, mappings, typed bindings, basis classification,
artifact identities and report-check receipts, not product tooling.

The first metadata probe failed on a nonexistent expectations import; corrected
inspection uses `tools.validate.model`. Earlier probe outputs and script versions
are retained, including formatting/duplicate-tuple diagnostics. The final 12
display mismatches are the real missing cap markers described above. A guessed
retained C2 report path failed before discovery of the actual committed path;
neither failed probe is represented as passed qualification.

Report-only final checks cover strict UTF-8, fenced JSON, newline/trailing
whitespace, local link, exact staged scope and CR-aware Git whitespace. The
dispatch-authorized invocation-only empty hooks path applies only to committing
this prose report; no source-hook or combined-pipeline success is claimed.

The original reviewer core qualification attempt 1 remains **FAIL with no
domain**; this delivery neither overrides it nor authorizes a retake. No source,
test, registry, scenario, manifest, finding, baseline or evidence was changed;
no service, campaign, ledger generation, evidence import, Docker, hardware or
release action ran. Physical HIL/CEC, 72-hour soak, week field sign-off and final
artifact/version gates remain open. Coordinator owns correction routing,
settlement, preservation, publication and acceptance; no push, merge, cleanup or
self-release is performed here.

Retained check identities (SHA-256):

- `docs.stdout.txt`: `ec4f935a36f5bfd9790e37f72b23df9c6f22f1fcb328ac4bee2ba84f0af7459b`
- `docs.stderr.txt`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `docs.exit.json`: `8a331e70d456cf708ef85977646d3f7062e3f433748f60395049906334160448`
- `docs.junit.xml`: `9a7138cdbe6704d89288c0d2b8dc0d491ce6627de8336f70130ff28c56216db4`
- `metadata.json`: `e1f140c80d71d7506b28548e026a6bcddad42566490901f19d6b1d54f44c0f2c`
- `typed_ws.json`: `d586d0e19c1d64edb583d22054f77d782c2b5aff9a30353d6e0eaf5cd7d6b12f`
- `author-identities.json`: `f69a365f2accd9304256e1fde21f0e22919ac78bcc8547f11a422a10e6ad5ca3`
