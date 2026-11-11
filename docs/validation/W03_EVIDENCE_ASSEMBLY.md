# Wave03 evidence assembly

Prepared from integration `28fce729ca4ea08bfc2f19805b36e13ae8c184f2` on
2026-10-28. This is an exact-candidate metadata review packet; preparation is
not independent acceptance, integration publication or release qualification.

The [byte manifest](runs/software-waves/W03-CLOSEOUT-20261028/import-manifest.json)
lists 44 original JSON records and 32 original screenshots. Thirteen API-only
CORS records retain source `7b07e1cb7e7eb29a38b55d3b050703149f1b797c`; 31 combined
records retain clean source `310d8b65a9fce3c9069523d4ac5ce21157e75c9f`.
No record is reserialized, reattributed, retimestamped or changed to claim an
image digest. Screenshots remain observations; no visual baseline is changed.

| Set | Outcomes | Passing checks | Expected n/a | Scope |
| --- | ---: | ---: | ---: | --- |
| Original CORS | 13 | 65 | 0 | API/source-simulator V2 |
| Combined auth | 14 | 108 | 6 | Six API V2 and eight real Chromium V3 |
| Combined root/info | 3 | 20 | 0 | API/source-simulator V2 |
| Combined CORS | 13 | 65 | 0 | API/source-simulator V2 |
| Combined unreachable switch | 1 | 7 | 0 | API/source-simulator V2 |

The new records and their original per-feature artifact directories are under
`docs/validation/evidence/software-waves/W03-CLOSEOUT-20261028/`. All 76 copied
files match their source SHA-256 values. Existing evidence, original failures,
diagnostic campaigns, and original author/reviewer attribution remain unchanged.

Source implementation was independently accepted before this assembly:
[CORS review](../production/software-waves/SW-API-READ-04-C1/REVIEW.md) and
[offline routing review](../production/software-waves/SW-API-CLIENT-02-C1/REVIEW.md).
The [fresh execution report](../production/software-waves/W03-CLOSE-EVIDENCE/AUTHOR.md)
records the actual 31-outcome run and 18 existing offline regression tests.
The [corrected inventory](../production/software-waves/W03-CLOSE-INVENTORY/AUTHOR.md)
independently reconciles original records and the nine accepted functional blobs.
Neither inventory authorship nor this metadata packet confers general core or
security source-review qualification.

Only F-API-031 proposes a recorded-level advance, V1 to V2, on the accepted
13-case header assertion implementation and fresh combined proof. F-API-002
and F-SEC-007 receive evidence refreshes at unchanged V2/V3. The unreachable
record refreshes named F-API-033/F-REL-009 proof without completing V3 targets.
F-API-034 receives no new scenario or level claim.

VAL-14 is registered as medium/open: source correction is independently accepted,
while final assembly and combined CI/publication closure remain pending. The
ordinary unreachable scenario observes a failure inside the command (HTTP500);
the 18 focused existing regressions cover already-disconnected HTTP503/events,
all-output refusals, malformed input and connected controls. These boundaries
are not interchangeable. The original failed CI record remains a historical
regression; no assertion or finding link is changed to waive it.

VAL-15 is registered medium/open against validation request artifacts/action
descriptions, linked to F-SEC-014. Its synthetic reproduction does not establish
an owner credential leak or complete product-logging assessment. The corrective
child SW-SEC-DATA-02-C1 remains pending and no redaction fix is included here.

Ledger generation ran alone, then registry/schema/ledger checks passed 42 tests.
The regenerated ledger reports 268 features, 210 below target and 96 stale.
The previous committed report (203 below/57 stale) predates source changes whose
covered-path effects are now recomputed. These are evidence dispositions;
existing rows and stale records are preserved, with no fabricated refresh.

The accepted combined source also passed 4084 core tests/four skips/35
deselections with strict177/177 REST coverage, 100 dedicated Remote tests,
Ruff and mypy91files on 2026-10-26. Product, tooling, tests, client/UI code,
manifests and locks are unchanged by this assembly, so these results retain
their actual original attribution. Current-head CI, broader client/image
validation, exact final metadata review and integration publication remain
separate required gates. Physical HIL, deployment-host72hours, week owner use,
and final version/artifact release acceptance remain open.

Source worktrees, external temp data, private archives/quarantine and ignored
files remain preserved. This packet authorizes no cleanup and resolves no
unverified process exit or archival-count discrepancy. Before another execution
wave, satisfy preservation/cleanup policy and verify the published integration
head. No new phase debate or retrospective consensus is claimed.
