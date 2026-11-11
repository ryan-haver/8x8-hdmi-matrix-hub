# SW-AUDIT-01 independent correction re-review 02

**Verdict: require_changes.** The substantive residual corrections mostly hold,
but the corrected submission adds a false census statement and leaves ambiguous
legacy metadata and overbroad unit-summary claims. Bounded inventory acceptance
is not yet supported. This is factual report review, not source acceptance,
feature qualification, a core qualification retake or product acceptance.

```json
{
  "reviewed_author_commit": "ac97e1f5886d591562597b5e81c3fa410adda2f8",
  "reviewed_author_parent": "981e7e4a48bce07e4dce24443d386b3e0643601a",
  "overall_verdict": "require_changes",
  "R1_R6_dispositions": {
    "R1": "accept: delivered retained privacy chain and historical-only VAL-15 reproduction",
    "R2": "preserve prior factual acceptance: retained API-V2 boundary before duplicate implementation",
    "R3": "preserve prior factual acceptance: actual parallel FSEC007 exit1 remains unresolved",
    "R4": "row corrections accepted; require correction of all-100 census prose",
    "R5": "typed/client/attribution corrections accepted; require explicit legacy-field provenance and bounded unit-summary wording",
    "R6": "accept: 88+33 owner decomposition and twelve cap markers; no level changes"
  },
  "F_API_029_erratum": {
    "accepted": true,
    "unit": "SW-API-CLIENT-02",
    "registry_scenarios": [],
    "live_declarative_bindings": [],
    "literal_declarative_source_match": false,
    "not_absence_of_nondeclarative_controls": true
  },
  "verified_feature_rows": 268,
  "not_feature_qualification": true,
  "bounded_inventory_acceptance_supported": false
}
```

## Authority and exact input

Task `task_afbc5357eb0e`, Dispatch `ctx_c0dcf402e9f3`, worker
`term_53731425-a7b1-4456-a4f3-c55220b7ccda`, coordinator
`term_6ed8131e-3ab3-4693-8094-56cc10acd412`, Run `run_37205f6095b3`.
The injected selection is native OpenAI `gpt-6-astra/high`, independent of the
MiniMax author. This report does not independently attest the backend or expand
qualification. No helpers, nesting or route substitution were used.

The isolated checkout began clean at the exact reviewed author commit and
parent above. The complete parent-to-author diff changes only [AUTHOR.md](AUTHOR.md),
374 insertions and 132 deletions. Its canonical Git blob is **223560 bytes**,
SHA-256 `f64b616548d1250331d2567963db2e1bc2dfbc327824a6b44c835814b0681758`.
The working file is separately verified identical, **223560 bytes**, the same
SHA-256, zero CR bytes. The complete diff was retained and inspected, including
row changes, crosswalks, method limits and the correction appendix.

The prior re-review was read from immutable commit
`d44ad2bca78dfe82c4b541e41f861c965cce2461`. The shared-root coordinator
`docs/production/software-waves/MVP-EXECUTION-20261102/REVIEW_INSTRUCTION_ERRATUM.json`
was read. Its correction is supported by the frozen manifest/pins, empty registry
scenario list, independently discovered scenario bindings and literal search of
the declarative scenario sources. F-API-029 belongs to SW-API-CLIENT-02; the old
SW-API-READ-03/live-declaration parenthetical was wrong. Rejecting it was correct
and changes no allocation. Historical review/spec bytes remain untouched.

## Required residual corrections

1. **Section 10 item 8 falsely says all 100 scenario-less rows are now
   COVERAGE-UNRESOLVED.** There are 100 rows in the 72/28 basis-class partition,
   but only **96** have that primary disposition. F-API-039 and F-API-042 remain
   DECLARATIVE-GAP, F-DOM-032 remains MISSING-ASSERT, and F-SEC-014 remains
   RETAINED-CHAIN-OPEN. The current table, private corrected rows and census
   agree with each other. Correct the prose to distinguish basis classification
   from primary disposition, including these four exceptions; do not relabel
   the rows merely to make the sentence true. Section 4.1's explanation should
   likewise distinguish the 100-row basis universe from the 96-row label subset.

2. **The new corrected metadata does not explicitly identify legacy fields as
   historical/superseded.** In `author/correction-02/correction02_rows.json`,
   F-SEC-001 still has `software_gap: missing assertion` and
   `disposition: missing assertion`, beside `corrected_gap: MISSING-CLIENT`.
   F-KIO-005 likewise retains those assertion labels beside
   `corrected_gap: COVERAGE-UNRESOLVED`; F-API-032 retains them beside
   `DECLARATIVE-GAP`. The tracked report contains no `software_gap` field
   explanation, and the new row objects provide no explicit provenance marker
   for that field. The corrected fields and displayed actions agree; the
   problem is an unlabeled contradictory secondary representation, not a demand
   to overwrite immutable originals. Explicitly document the legacy fields'
   provenance and non-authoritative status in the report/new correction
   metadata, and identify the authoritative corrected fields. Preserve the
   original and correction-01 files byte-for-byte.

3. **Section 8 overstates three unit-local gaps as inventory-wide singletons.**
   SW-API-WRITE-03 calls F-API-037 the inventory's only bounded-negative gap;
   SW-API-READ-03 says the same of F-API-040; SW-DOM-PRESENT-01 says it of
   F-DOM-032. These cannot all be the sole inventory-wide gap and conflict with
   the explicitly enumerated four rows, including F-MTX-024, in section 6.1
   and the section 8 intake explanation. Say the gap is local to that unit, or
   one of the four inventory rows. Retain the bounded textual-search caveat;
   no new assertion implementation or global re-audit is requested.

These are bounded report/metadata fixes for the author. The author's 33/33
self-check claim does not independently establish semantic consistency.

## Independently verified corrections and invariant structure

All **268** table IDs remain unique. Comparing the complete old/new tables
finds no changes to IDs, titles, targets, units/phases, client/scenario columns,
WS columns or displayed source references. Full private source-reference sets,
scenario IDs and actual `features_for(client)` mappings were independently
recomputed from **1507** discovered scenarios and agree for all 268 rows.
Manifest ownership, pin phase/feature membership, contract targets and ledger
levels/recorded values/freshness were also checked. Capped ledger text was
normalized as an annotation, not as a numerical change. Structural fields in
correction-01 and correction-02 private rows agree. No source, manifest, pin,
contract, registry, ledger or finding file changed in this commit.

Canonical arithmetic remains **268 / 210 below / 96 stale**;
**147 software targets = 58 at + 89 below**, **120 V4 + 1 V5**.
Current primary labels are **39 PRESERVE, 40 RERUN-FRESH, 48 MISSING-CLIENT,
4 MISSING-ASSERT, 7 DECLARATIVE-GAP, 96 COVERAGE-UNRESOLVED,
33 PHYS-OWNER-GATE, 1 RETAINED-CHAIN-OPEN**.

Independent comparison reproduces **77** original-to-correction-01 changes,
**29** correction-01-to-correction-02 changes, and **104** original-to-final
changes. The sets overlap at F-SEC-001, whose intermediate label is reversed:
**77 - 1 + 28 = 104**, not 77 + 29. The historical 77-row set and present 29-row
delta are valid different comparisons. All corrected dispositions and actions
in the 268-row table agree with the new private corrected fields.

**R1:** Section 3 item 6 now matches the pins' C1/C2/C3 delivered,
unreviewed/unintegrated state at submitted heads 11f305b1 / 615d3c84 / 2d02004d.
VAL-15 reproduction is historical only; the open finding and qualified full-chain
review/admission/integration gates remain. No new reproduction or closure follows.

**R2/R3:** The accepted factual corrections are preserved. F-API-034 still
prefers exact 938ae303-to-caaa4faa retained-chain review, including 38687231 and
ee3f2e7f, before duplicate implementation. It is API V2, not V3 or F-MTX-002
attribution. Section 6 row 5 retains the actual parallel-candidate global
exit1, F-SEC-007 V2 below recorded V3, without treating canonical fresh V3 as
supersession. Those prior accepted historical facts were not fully re-audited;
no new source acceptance or failure diagnosis is inferred.

**R4:** SW-API-CLIENT-01 membership is exactly 001/003/004/005/006/007.
The declared API subset is 001/004/005/007; 003 and 006 have no declarations.
`routing.switch_one` browser binds MTX-001/UI-002 and `presets.recall` browser
binds MTX-003/UI-005. API-docs, health and CEC-status declarations are API-only.
The V3/client intake remains unresolved. All **28** no-effect-basis rows have
empty WS contracts, corrected COVERAGE-UNRESOLVED labels and explicit bounded
inspect/reuse actions. No invented WS contract remains in those actions.

**R5:** SEC-001's real-client requirement is retained. MTX-001, REL-012 and
CEC-006 now carry explicit secondary attribution-inspection/reuse obligations,
including the possibility of a justified out-of-scope attribution decision;
numeric freshness does not discharge those obligations. The positive typed
corpus contains 13 message names; exact `error` is absent, while
`scene_execution_error` is a different name. F-API-032's bound event is
`matrix_connection`. Four named missing typed messages span the displayed
**eight** rows, distinct from the historical seven-row subset excluding
DOM-032. Text matches locate candidate controls, not adequate semantic proof;
the new caveats explicitly retain polarity, client, coverage and target limits.
The four bounded-negative rows are not proven runtime defects or proof that
all possible controls are absent.

**R6:** Owner rows independently total **88 suffix + 33 primary = 121**;
89 software-below rows are a separate axis. All twelve MTX-007 through MTX-017
plus MTX-020 display V1*. Levels, caps and findings remain unchanged.

## Identities, checks and limits

All **22** named original/correction-01 author artifacts match their listed
byte counts and SHA-256 values; the additional four correction-01 test-output
identities also match. All **15** named correction-02 artifacts match, giving
**41** matched identities total. This checks named retained files, not an
unavailable full pre-correction filesystem snapshot. No archive or raw private
validation payload was interpreted. Author bounds of seven/ten minutes were
exceeded historically; no author time-budget pass is inferred here.

The single authorized test invocation used the shared root `.venv` Python,
own checkout plus `src` PYTHONPATH, UTF-8, bytecode off, created isolated
data/config/temp parents and explicit forward-slash basetemp under
`C:/t/exec-sw-audit-01/nov02-rereview02/run02/`:

```text
python -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -p no:tests.route_inventory -p no:cacheprovider -q --basetemp=C:/t/exec-sw-audit-01/nov02-rereview02/run02/pytest-temp --junitxml=C:/t/exec-sw-audit-01/nov02-rereview02/run02/docs.junit.xml
```

Direct subprocess result: **exit0, 489 passed in 2.85s**. Full stdout, stderr,
command/returncode JSON and original JUnit/temp files were captured immediately
before another invocation. No documentation-test retry occurred. An initial
metadata probe named `inspect.py` shadowed the standard library and failed;
its script is retained, and the corrected probe excluded the scratch directory
from imports and used a fresh run02 parent. Initial guessed erratum/contract
paths failed before exact discovery. An unsupported `progress` message type
was rejected; the supported heartbeat succeeded. These are inspection/CLI
errors, not passed checks. A first ledger comparison flagged the textual
`(capped)` suffix; the annotation-aware check has zero mismatches.

Private reviewer evidence lives only in
`build/software-waves/SW-AUDIT-01/execution-20261101/reviewer/re-review-02/`
and the assigned scratch namespace. It includes the complete diff, independent
mapping/census/typed-object/identity receipts and one-off inspection scripts.
Final report checks cover strict UTF-8/LF, fenced JSON parsing, local references,
trailing whitespace, CR-aware Git whitespace and exact staged scope. The
invocation-only empty-hooks exception is solely for this new prose commit;
no source-hook or combined-pipeline success is claimed.

The only tracked output is this report. Ledger updates, acceptance, settlement,
preservation and publication belong to the coordinator. Core qualification
attempt1 remains FAIL/no domain; an owner retake decision is pending. Source
and owner gates remain held/open, including physical HIL, 72-hour soak, week
field sign-off and final version/artifact release. No services, campaigns,
probes of runtime behavior, ledger generation, push, merge, release, cleanup or
self-release occurred. No further historical re-audit is implied by this verdict.
