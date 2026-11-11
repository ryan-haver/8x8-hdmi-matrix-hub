# EV-PRESERVATION-GAPS independent factual review

Verdict: **require_changes** at exact author commit
`ed78321e51156f229507e654f0cf3faae100b935`, parent
`f2dc1dbf683d8f96200d1517b0786e3441105b36`.
The two recorded losses and their negative acceptance consequences are supported;
three prose corrections are required before accepting this disposition report.

```json
{
  "reviewed_author_commit": "ed78321e51156f229507e654f0cf3faae100b935",
  "overall_verdict": "require_changes",
  "two_gap_dispositions": {
    "G1": "Recorded lost original managed-failure artifacts; FAILED/partial/UNMET remains; require calibrated recovery claims and precise symptom attribution",
    "G2": "Recorded overwritten first-pass scratch bytes; diagnostic preservation gap, historical mapping acceptance unchanged; require calibrated recovery claims"
  },
  "original_preservation_pass": false,
  "source_or_feature_qualification": false
}
```

Reviewer: OpenAI native gpt-6-astra/high, as dispatched; independent of MiniMax
report authorship, metadata-review scope only. Task `task_eea6f443f108`, Dispatch
`ctx_70e7d15a49fc`, terminal `term_2f911550-1cc0-47dc-8f12-f770a4eaed3a`,
Run `run_37205f6095b3`; coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`.
No helper or substituted provider was used. The prior Sol capacity incident is
unchanged history. The coordinator owns allocation-ledger updates and settlement;
this exclusive review lease authorizes no ledger write.

## Required corrections

**R1: qualify universal recovery assertions (material).** In [AUTHOR.md](AUTHOR.md),
summary G1 (line 63) says "Permanently unrecoverable; no later run, snapshot,
archive or diagnostic restores them"; section 3.4 says "The bytes are gone";
section 4.4 (line 328) says "Their bytes cannot be recovered". Current absence of
`C:/t/f034-20261029-a` and identity checks on surviving replacements establish
neither an exhaustive backup search nor impossibility of another historical
copy. Section 4.5 explicitly leaves such copying unknown, contradicting the
unqualified section 4.4 assertion. The accepted pins' irrecoverable-original
*disposition* remains valid as recorded history; it is not a newly proven global
filesystem fact. Attribute the loss/unrecoverable disposition to the accepted
records, state that originals were not recovered in the bounded inspection, and
explicitly leave copies elsewhere unverified. Apply this qualification consistently
to both summary rows, sections 3.4/4.4 and the closing characterization. Retain
the valid statement that later execution cannot recreate an original artifact;
do not run a broader search or create replacements to satisfy this correction.

**R2: distinguish new inspection metadata from historical evidence (material).**
Section 1 lines 53-55 says "No new evidence was created" and "The only invocations"
were documentation modules/report checks, while sections 7-8 describe new hash,
existence, Git provenance and invocation receipts, including `probe_survival.py`
and `git_proof.py`. Replace the absolute statement with: no new runtime,
campaign, qualification or recovered-original evidence was produced; this report
created bounded inspection metadata and documentation-check artifacts. Scope
"only" to the test invocation, and explicitly include the read-only metadata
checks. This is a reporting correction, not a finding that prohibited runtime
diagnostics ran; no such execution is established by the inspected records.

**R3: preserve the original distinction between count/outcome and reason
attribution.** Summary G1 and section 3.5 attribute the actual Telnet blocking
reason to `focused-first.log` as well as the native transcript. At
`060769b724e7a546b8df22eac82f3b288d9bbbe8`, the C1 author report's "Preserved
initial preparation failure" section instead says the failed pytest log retains
the count, assertion and BLOCKED outcome, while the native tool transcript records
the actual Telnet reason observed from the original JSON. Correct both places to
that precise split and label the reason an accepted reported observation. This
review hashed the log without reading its payload; it does not establish that
the log contains the detailed reason. No raw payload read is requested.

## Evidence checked and supported dispositions

The author commit adds exactly one path, `AUTHOR.md`, with no source changes.
Its actual Git blob is **36,331 bytes**, SHA-256
`ca72b8fff2c1adc60a03b77d6932febc450171716a074c1b9c8b163b0bce76ab`;
parent and hash match the dispatch. The shared root task was read at
`docs/production/software-waves/MVP-EXECUTION-20261102/PRESERVATION_GAPS_TASK.txt`
(the initial root-level lookup did not exist; no authority inferred from that).
Standing protocol, configured handoff and relevant allocation/runtime entries
were inspected read-only.

G1: read the historical C1 prose at `060769b7`, including failure, final partial
disposition and invocation inventory, plus allocation entries for
`task_c0d26e9e563e` / `ctx_0f27082dc4eb` and the 2026-10-29T03:02Z settlement.
These support OpenAI Sol/high authorship, source `38687231`, report `060769b7`,
12 passed/1 failed/exit 1 and FAILED/partial/UNMET. Git metadata confirms the
source's four paths and parent `938ae303`, the report-only child, and non-ancestry
of `38687231`, `060769b7`, `ee3f2e7f`, `caaa4faa` to `f2dc1dbf`.
The 11,878-byte DeepSeek historical prefix is byte-identical, SHA-256
`c25692409f8d4f7ae38a21695571821475b1ec097de995517b266c2b59c4e9ff`.
The old review blob `85c18d2443c758fe78964c6c2098b1317eb41036` is unchanged
between C1 report and base; it does not become review of the OpenAI addendum.

Bounded byte hashing, without payload display/interpretation, independently
matches all six section 3.3 identities: `focused-first.log` 1,497 bytes;
`preservation-status.json` 1,496; `focused-external.log` 102;
`source-commit-hook.log` 6,590; `precommit-ownership-audit.json` 1,227; and
`campaign-clean-01/evidence/F-API-034/2026-10-29-V2-38687231-sw_api_client_02_c1.switch_all_failed-api.json`
18,179. Every full SHA-256 matches the author's table; the campaign hash is
`11849d40b89ad90b2a554577e26df9ac62f154d67c55f2b5ecaa935a218e0492`.
The current missing temp root was observed; no exhaustive backup search occurred.
The allocation record supports historical task publication, verified full bundle,
49 checked members and later workspace/temp archive hashes, expressly without
claiming they contain lost attempts. Those archives/bundles were not opened or
reverified here; publication is historical attribution, not a fresh remote check.
Managed/all-scenario compatibility, qualified review, privacy admission,
integration and cleanup remain held under the accepted limits.

G2: read `FRESHNESS_DELTA.md` at
`11b09676f78acd76bd1ac47d11a8d8817e8d0624` and `COORDINATOR_REVIEW.md` at
`490a879bd346773cca64fac861eaaab29e703628`; checked allocation attribution for
`task_02c22e77963a` / `ctx_e973d4be3c60`, MiniMax-M3/thinking and independent
OpenAI coordinator factual review. Git metadata confirms the one-path report's
parent `d6e78e0b` and ancestry of both report/acceptance to the base. Attempt 1's
reported mangling/zero rows and overwritten originals remain reported history.
The old/new ledger blobs independently match 74,831/74,447 bytes, zero CR and
zero replacement characters, OIDs `fa0da83c5b2351e48c40b00f5884f5e25b1c129a` /
`281a7647b41e816529d8b7d953df7705a3084d98`, SHA-256
`41d81dae99566b01c15b4ada2eeff67ec2c87065a312b16a8c8bd4f8071aecce` /
`b8078e4d45be717c88f7f138c34a60d45a3ad118e1051e30f5da8a8c88c25cf7`.
The retained `ledger_old.md`/`ledger_new.md` match those identities;
`parse_ledger.py` (4,328 bytes) and `attribute_delta.py` (6,989 bytes) match the
full hashes in section 4.3. No analysis script was executed. Original scratch
lengths/hashes remain unknown; diagnostic preservation failure does not imply
lost project source/evidence. Historical freshness mapping stays accepted with
its recorded limits and retention requirement. It is separate from current global
inventory: `CORRECTION_REVIEW_01.md` in the retained rereview checkout explicitly
still says `require_changes`; no global acceptance is inferred or re-audited.

The author's documentation receipt was read as metadata. Its stdout/stderr/JUnit
sizes and hashes match retained bytes, and all 103 listed temp files match their
listed hashes and total 164,426 bytes. Receipt return code is 0, reported 489
passes; this verifies current retention and receipt consistency, not independently
the historical process exit. Full native transcripts and archive payloads were
not inspected. No sensitive payload, credential, screenshot or raw validation
record was opened for interpretation. Only hashes were calculated for the named
retained raw artifacts. No runtime/source qualification, feature promotion,
finding closure, cleanup permission or owner gate is granted. Core qualification
1 FAIL/no domain and pending explicit owner retake decision remain unchanged.

## Reviewer verification

Private inspection receipts are under
`build/software-waves/EV-PRESERVATION-GAPS/execution-20261101/reviewer/`:
`identity.json`, `author-check-identity.json`, and the documentation/check receipts.
These are new review metadata, not restored historical evidence. Reviewer checks used root .venv Python, own root/src PYTHONPATH, UTF-8 and
bytecode disabled, fresh data/config/temp and forward-slash basetemp under
`C:/t/exec-ev-preservation-gaps/nov02-review01/`. Only the five assigned existing
documentation modules ran, with route-inventory and cache plugins disabled.
Direct subprocess exit **0**, **489 passed in 2.80s**; full stdout/stderr, JUnit
and all 103 temp files were retained and hashed immediately before any further
invocation. No historical diagnostic, campaign, registry or ledger was rerun.


Reviewer stdout: 588 bytes, SHA-256 `a30d4fa77d4ec382a252c142c1ffeceed86837b17d4f64539b3a2ed77a5c96fc`.
JUnit: 63691 bytes, SHA-256 `5d32c521cdd4cdd067a324ed13be2359aae1ffa77235cab70c23ad7d9b8f7da2`.
UTF-8 strict decode, fenced JSON parse, local Markdown target, LF/final newline,
CR-aware whitespace and exact report-only scope checks passed. The prose commit
uses the authorized invocation-only empty hooksPath; this is not a source-hook
pass. Actual committed report identity is delivered separately to avoid a
self-referential hash. Author corrections and exact-commit re-review remain;
coordinator settlement/publication/canonical acceptance are separate.
