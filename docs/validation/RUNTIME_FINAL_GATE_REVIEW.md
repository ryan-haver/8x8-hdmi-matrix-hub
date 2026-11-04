# R8E final evidence attribution review

**Accept the completed functional software evidence for the supported runtime
candidate. Final v1.0.0 publication remains gated.** No material attribution,
record-preservation or evidence-link defect remains in the audited scope.
This is an independent assessment of completed evidence, not a new product test
campaign, visual approval, or physical/field certification.

Reviewed 2026-10-19 UTC. The [runtime report](RUNTIME_VALIDATION_REPORT.md),
[R8D restoration review](RUNTIME_REVIEW_RESTORATION.md),
[archive manifest](runs/runtime-r8b/manifest.json),
[milestone journal](runs/runtime-r8b/milestone-records.json), registry/ledger,
[field runbook](RUNTIME_FIELD_GATE_RUNBOOK.md), validation plan and current
planning records support this disposition. Supplemental originals were read
from `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/runtime-completion/`.
Owner private runtime configuration/data/environment values were not inspected.

## Audited revisions and independence

- Fresh Orca child: `wp-runtime-final-evidence-audit`, based on actual
  `wp-runtime-completion`, initial clean HEAD
  `443c2da36e8e6dee5a432982a28e0020234f855d`.
- Tested clean source/image revision:
  `1baac3dec660f41345869c126cfca94d6731c5a0`.
- Completed archive checkpoint:
  `fe0e7f0705f376aaa9f8c27d6e50a2b78a3df9fe`.
- Accepted Luna documentation commit
  `603ce18781b7855de11bfd5b1c9d0035d9810a67`, merged as
  `dd8a8a7d46622402f0cb1f6357ddc9a96853d3f8`, and coordinator clarification
  `e4cdda231a7eb24ebfb9a4f284238e016c707e17` were inspected through actual Git
  blobs/diffs before signoff. The review child was not merged or reset.

`orca orchestration worker-show --dispatch ctx_83edfd87ff1f --json` records
requested **and** effective provider/agent `codex`, model `gpt-6-astra`, effort
`high`. `orca worktree current --json` confirms the child, parent, base and HEAD.
These receipts are Orca control-plane evidence, not independent backend
attestation. No nested/helper/fallback agents or Anthropic models were used.
No applicable `AGENTS.md` was found in the checkout or its ancestors.

The accepted documentation delta changes only `README.md`, `ROADMAP.md`,
`docs/README.md` and `RUNTIME_VALIDATION_INDEX.md`. It correctly updates the
candidate/archive/CI attribution and retains remaining gates; `e4cdda23`
explicitly labels the ROADMAP proof table as historical and points to the
authoritative current ledger. All **135 local path links** checked in those
four final files resolve at that Git tree; external URLs and anchors were not
network-validated. These prose changes preserve the audited source/image inputs.
README is also package-description input; this does not claim a newly built
wheel has byte-identical metadata. Later documentation-head CI remains a
separate observation, not the `1baac3de` CI result below.

## Preservation and scope checks

Independent SHA-256 comparison used binary `git cat-file --batch` output,
parsing Git's byte lengths without text decoding or newline normalization.
All **439/439** expected blobs match both the archive checkpoint and the review
base: **213 original + 193 new image records + 32 archive files + one conditional
probe**. The original 213 also match their pre-consolidation source checkpoint.
All 193 imported records match their full original image-client records byte
for byte. Scoped `-text` attributes preserve raw evidence representations.

All **259 captured ROOT source/build hashes** match their accepted capture.
Canonical Git content is identical across the R8D reviewed source `619baccc`,
tested source `1baac3de`, and this review base. The six recorded root/review
checkout differences are independently verified LF/CRLF variants of identical
canonical content, consistent with the preserved rejected strict-byte audit.
The final **257-input image parity** record matches actual ROOT build bytes
for both images; it is not compared against this child's converted checkout.
The four later documentation paths do not alter these hash sets.

History remains qualified: `92d463b0` omitted the ignored complete-core log;
`fe0e7f0` added its original bytes before the successful 439-blob checkpoint.
The initial default whitespace rejection of raw CRLF is not a test failure or
a successful earlier archive audit; CRLF-aware checking passed without rewriting
evidence. Earlier normalization/setup failures and unsuccessful runtime campaigns
remain recorded. Initial CI log downloads failed due to terminal escape handling;
retained raw retry files supply the successful capture, not the empty first files.

The archived original complete-core log matches its root original at SHA-256
`5796baa6d854d6098c3077ee1294e61fb378da06f3076a8482ae5384eea5a958`.
Its strict **177/177** route result and independent CI are authoritative.
The supplemental external-image diagnostic's non-strict zero is uninstrumented;
it overwrote the shared JSON, whose original full form was not separately retained.
No replacement was synthesized. This is neither failed complete coverage nor
proof of universal image route coverage.

## Accepted functional evidence

Both images have canonical product version **1.0.0rc1**, built from clean
`1baac3dec660f41345869c126cfca94d6731c5a0`:

| Architecture | Immutable image ID |
| --- | --- |
| amd64 | `sha256:558c2677c65995598d7b06a2f1726c2a254ae1afac74b1f34060f336bac0fd8e` |
| arm64 | `sha256:c7d017fbcbf61e47b64aeab12cab0d153fe92b9ca74ecf0823b32cb551e14c93` |

API contract version `2.10.0` in client evidence is distinct from product
version `1.0.0rc1`. Local image IDs do not imply registry publication or Git tags.

| Evidence at tested source | Independently reconciled result and limit |
| --- | --- |
| Local core log/XML | **4,041 passed, 4 skipped, 35 deselected**, 177/177 routes; includes installed entry checks, excludes dedicated HA/UC suites |
| Dedicated Remote XML | **100 passed**, no skips; SDK/simulator |
| amd64 deployment XML | **26 passed, 3 skipped**; normal command, health, SDK/discovery/volume/context |
| Required normal-image regressions | **4 passed**, no skips/failures/errors; UC off/on restarts and immediate/deadline rollback |
| Source clients | **1,506 passed**: API 1,411, browser 54, Remote 18, Flic 23 |
| Actual source HA containers | **19 each** on 2026.9.3 and 2025.1.4; the latter proves a version line, not exact 2025.1.0 |
| amd64 image clients | **193 passed**: API 79, browser 54, Remote 18, HA 19, Flic 23 |
| Source browser flows | **59 expected**, zero unexpected/flaky/skipped |
| Image Swagger | **4 cases**: enabled 177 / disabled 175 operations, online/CDN-blocked, no page errors or saved synthetic PIN |
| arm64/QEMU | Offline normal startup, canonical metadata, health and graceful SIGTERM only |

All **1,737 original client outcomes** across eight roots have matching clean
run attribution, passing records and valid evidence schemas. Their archived
summaries equal the original summaries byte for byte. Every original outcome
is represented in the composite with its `original_run_commit`; original
summaries remain authoritative. The image includes all **114 declared non-API
simulator scenario/client pairs** and all **25 preset-read API cases**. Its
79 API cases are representative; they do not repeat all 1,411 source API cases.

All **42 `n/a` assertions** in the 193 imported image records match unchanged
declared client exclusions and the milestone journal. They were not promoted
to passes. All 268 feature baselines are unchanged; no imported record claims
V4/V5. The current ledger still has **210 features below target**, and the
formal regression gate does not erase those target gaps.

The original `r8b-formal-gate-command.json` records actual exit **0** for
`python -m tools.validate check --run-summary
build/runtime-completion/after-r8b/combined-campaign-summary.json
--expect-clients api,browser,uc,ha,flic`, with nine explicit `--evidence`
arguments: all eight roots in the [gate context](runs/runtime-r8b/formal-gate-context.json)
plus deployment. The original [gate output](runs/runtime-r8b/formal-gate.txt)
matches its captured hash and reports zero linked known failures in scope.
Ledger generation precedes the retained **26 passing registry checks** (3.32 s).

These are software observations: Flic uses Node SDK stubs and actual HTTP replay;
Remote uses scripted SDK/socket clients; HA uses disposable real containers.
They do not certify physical Flic/Remote, owner HA/LAN or matrix/CEC effects.
Source-only evidence does not establish shipped-image/V3 conditions. Swagger
catalog rendering does not execute every disabled-configuration handler.

## Restoration boundary, CI and release disposition

R8D's supported acceptance is correctly retained at its own source/image:
12 mandatory cases, 102 scoped regressions and two supported boundary controls
pass. The original conditional probe is byte-identical to the committed manual
reproduction (SHA-256
`defca6b53cd9f03e2c00cd26eb00d6c733e6e68fd93294ab455e59debb077df4`).
Its retained rerun remains **one failure, one passing control, one deselection**,
exit 1, with no skip/xfail or changed oracle. Replacing public disconnect to throw
before the real Orei body prevents its synchronous intentional-close fence and
allows an existing supervisor to continue while commands remain fenced. No
natural supported in-body bypass was demonstrated; actual in-body listener-error
and late successful-close controls pass. This preserves the coordinator's explicit
unimplemented arbitrary-client extension limit without claiming universal
quiescence or reopening supported acceptance on the same conditional evidence.

Cleanup's five-second bound plus a separately bounded settling phase of at most
five seconds is not one global ten-second transaction/shutdown deadline.
Post-discovery **16-file plus three-presence** integrity checks are only relative
to that checkpoint, not proof of original pre-test integrity.

Retained raw CI logs and final metadata for run **39228762775**, at `1baac3de`,
confirm all **12 non-UI required jobs pass**. CI core is **4,023 passed,
22 skipped, 35 deselected, 177/177 routes, 690.90 s**; actual HA is **19 passed**.
Main UI is **1,098 passed, 33 skipped, three Tron paused-frame failures,
25.3 minutes**. The review gallery is **62 passed, 3.4 minutes**. Both UI
artifacts are retained, and `unapproved.txt` names the same desktop,
kiosk-tab-a11 and kiosk-iphone16promax frames. A gallery capture is not baseline
approval; overall CI remains failed on UI. No owner approval is recorded.

This review closes the final independent evidence assessment for the audited
software candidate and accepted documentation delta. Release still requires:

1. Owner visual decisions and applicable final PR/CI checks, followed by the
   gated PR #36/#37 merge/tag sequence in the master plan.
2. Owner HIL-B/C/E, physical matrix/CEC/Remote/Flic and owner HA/LAN evidence;
   unavailable hardware remains explicitly unvalidated.
3. Continuous 72-hour resource soak, the owner's week of daily use/signoff,
   and accepted feature evidence reaching required targets.
4. Canonical final `1.0.0` metadata, matching rebuilt artifacts and affected
   evidence before the final tag. The tested RC images cannot serve as final
   version artifacts by relabeling them.

## Independent audit commands and retained outputs

All audit writes are confined to this new report and local `build/r8e/`.
The existing interpreter was used without installation:

```powershell
& C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -B build/r8e/audit.py
& C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -B build/r8e/supplement.py
& C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -B build/r8e/docs_join.py
git diff --check -- docs/validation/RUNTIME_FINAL_GATE_REVIEW.md
```

The three scripts pass; they perform byte/schema/count/provenance/link checks,
not pytest/Docker/HA/browser execution. `audit.json`, `supplement.json`,
`docs-join.json`, `accepted-docs.diff`, identity/worktree receipts and command
results are retained under `build/r8e/` for coordinator copying before cleanup.
The supplemental audit also retains the exact original campaign command arrays;
they are historical commands read from the archive, not rerun here.
Only this report is committed with the authorized per-command empty
`core.hooksPath`. The completion message supplies its exact commit SHA.
No production/test/registry/ledger/baseline edits, physical actions, new Git
release tags, push, merge or publication were performed by this review.
