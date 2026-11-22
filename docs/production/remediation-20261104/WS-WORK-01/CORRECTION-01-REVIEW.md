# WS-WORK-01 correction 01: independent component review

Date: 2026-11-04. Reviewed source: `24c5170458200209836228646fdfc8784a967ad1`.

| Decision | Result |
| --- | --- |
| Exact corrected component correctness, adopted D2/D3 | **PASS**, within the limits below |
| Original first-authorship qualification | **NOT_GRANTED / HOLD**; no new competence grant |
| WSR-03 original exclusive-path violation | **Historical FAIL**, unchanged |
| Existing handler / WS-WIRING / CR-01 closure | **HELD**; handler remains unbounded and unwired |
| New API lease, integration, canonical evidence or release | **Not granted or performed** |

The correction removes the demonstrated false-drain and lifecycle-mutation defects.
This is a review of the whole component, not approval based only on its patch or
passing counters. Two low-severity observations remain below; neither demonstrates
a failure of the adopted corrected runtime contract. Product acceptance is not
made conditional on rewriting historical failed evidence.

## Authority, subject and boundaries

Task `task_dbebfdfebb1c`, Dispatch `ctx_ecdde4971dc6`, worker
`term_d39b805d-109c-4a84-ab15-41e55f26a439`, existing Run `run_37205f6095b3`.
Live Orca worker authority matched this dedicated review tree and exact base.
Reviewer assignment: OpenAI `gpt-6-astra/high`, a different underlying family
from the Anthropic correction author. Assignment is not an independent attestation
of this review backend. I used the installed orchestration skill, no helper,
subagent, second model, nested worker, global configuration or account change.

At entry I resolved `wp-runtime-completion` once to
`f693b7848c5b973f0c207ae53b8b7dfffc8b5758`, then used that immutable snapshot.
The complete relevant final packet, consensus/decisions and Wave B subject packet
were read; raw Git blob SHA256 values were independently checked:

- `FINAL_PACKET.json`: `f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e`.
- `WAVE_B_SUBJECT_PACKET.json`: `7a6256111da21e71aee2f3ad315a646f7e3b6e088c45a3d4ee18dcf222c66763`.

The adopted three-family/three-round decision, including D2/D3 and D6's held
target provenance, governs prospectively. The whole component was compared from
`460a190575e905f8350c454e63c4d570c8b560fa`; the correction was compared from
`15c069bdeb3a9ace37bf68033812ff72659bfbd1` through the exact reviewed commit.
The earlier review at `1cc442207d54b0ad1c5887f6c4e9d5d17b7c8b19` remains historical.

Only this new report is tracked. All authored probes, runners, derived reads,
receipt indexes and commit messages are under this tree's ignored
`build/remediation-recovery-20261104/ws-r01/` or
`C:/t/remediation-recovery/ws-r01/`. Source, tests, original reports, coordinator
`.codex/`, root manifests, registry, ledgers, other worktrees and source publication
were not changed. The coordinator owns allocation and integration records.

## Semantic review and runtime reasoning

I read all 506 current component lines, the original implementation and complete
correction diff, all 1,502 current focused-test lines, original AUTHOR, original
REVIEW, CORRECTION-01, the original reviewer probe and its raw gap-probe outputs.
The original 887-line test prefix is byte-identical after Git LF normalization:
44 original cases remain unchanged; 615 appended lines add 29 collected cases.
Hashes establish provenance, not a substitute for those reads.

Caller review covered complete `websocket.py` and `events.py`, the app creation
and cleanup lifecycle and REST server wrapper, and runtime composition shutdown.
The unrelated full REST route table and entire runtime implementation were not
read line by line. `_handle_command` still starts `ws_get_status` without this
component; `_replies` remains module-global and unbounded. Event client writer
queues are a separate mechanism. The app and runtime do not install this owner
controller. Existing `_reply_status` exception logging also prevents a broad
application privacy claim; this review imported no separate privacy code.

Admission reserves owner/application capacity before invoking the factory and
before an eager task's first step. Nested admission therefore cannot evade either
limit. Rejections do not invoke the factory or create a coroutine. A factory
failure and a task-creation refusal release the reservation; an unsubmitted
coroutine is closed. Registration replaces the reservation with the real task,
and a scope closed during admission cancels the newly registered task. Strong
references remain until completion processing. Exact-task release and result
retrieval prevent a stale callback from removing a successor or losing a task
exception. Done-but-unreleased tasks still occupy admission capacity, but are
correctly excluded from unfinished-work drain counts.

D2 has two fields, with different meanings. `requested` counts attached live
tasks for which this invocation requests cancellation, including an attached
calling task. `remaining` recounts all unfinished attached tasks plus all
in-progress reservations in the relevant scope; a reservation is not a cancelled
task. Consequently `remaining > requested` is valid. Reservation counts are
arbitrary bounded integers, not a one-reservation theorem. Owner drains use only
that owner's reservations/tasks; application drains use the controller's totals.
Zero timeout returns immediately. A reservation or self dependency may return
conservatively immediately; otherwise one bounded `asyncio.wait` is followed by
a fresh recount. Cancelled waiters propagate cancellation without dropping work
or reopening admission. Resistant tasks stay held until they really finish.

D3 checks bound-loop ownership before lifecycle mutations, including cancellation
requests, for both synchronous and asynchronous entry points. Missing or foreign
running loops raise without changing fences or cancellation counts. Before first
admission, lifecycle fences work synchronously and never bind a loop. The first
admission attempt still binds, even if rejected, as explicitly tested. This does
not confer thread safety or allow recovery of a controller from a closed loop.

## Findings and dispositions

| Finding | Severity and evidence | Disposition |
| --- | --- | --- |
| WSR-01, false drained result while admission is reserved | Original Medium/blocking. All four owner/application factory/eager-body shapes return truthful `(0, 1)` now; independently selected multiple-reservation controls return owner `(0, 2)` and application `(0, 4)` before any body exists. Old source and reservation-omission mutant fail these same liveness oracles. | **Corrected at exact subject**; historical failure retained. |
| WSR-02, lifecycle cross-loop contract discrepancy | Original Low. All four lifecycle APIs refuse wrong-loop and no-loop calls before state or cancellation changes; unbound lifecycle closes without binding. Independent guard-removal mutant fails only these eight refusal checks. | **Corrected under D3**; original narrower behavior remains historical. |
| WSR-03, original scratch scripts and commit message outside lease | Original Low, actual write-boundary failure, proven by prior native indices 22/23, 59/60 and 83. | **Historical FAIL**, neither waived nor rewritten; correction does not grant first-authorship competence. |
| WSR-04, original `-X dev` debug claim | Original Low evidence-description error. Installed pytest-asyncio explicitly uses configured debug, default false; interpreter development mode alone is insufficient. | Original claim remains invalid. New explicit debug configuration, loop assertion and JUnit properties establish the new debug runs only. |
| C01-R01, overly broad no-progress rationale | **Low, documentation/calibration**. Module lines 59-64, related `_drain` comment and correction report mechanism prose imply all work cannot progress until any reentrant cleanup returns. An independently spawned eager cleaner can suspend, allowing the factory to continue, admission to attach and a sibling to finish before that cleaner returns. Own `progress_control` demonstrates those gates without changing product cleanup. | **Open, nonblocking for corrected runtime**. Describe immediate return as the conservative adopted policy, rather than a universal impossibility theorem. Any source wording change returns to the original author only under a fresh coordinator gate; reviewer made no fix. |
| C01-R02, scope of write-compliance attestation | **Low, operational evidence limitation**. Current direct authored files stay within the assigned tracked/ignored leases. Tool/harness outputs include caches, route output, bytecode and harness artifacts outside the two ignored roots, as disclosed below. | **Explicitly bounded**: authored-path audit passes; a literal all-host-write exact-root PASS is not asserted. No new authored out-of-lease scratch was found in this correction. |

No additional blocking source defect was found. Ordinary task factories that
refuse creation were covered; arbitrary factories that secretly spawn detached
tasks and then throw, exotic Task method overrides, synchronously blocking user
code, and eager `SystemExit`/`KeyboardInterrupt` are not qualified by these tests.

## Independent execution and failure-sensitive controls

Every Python invocation used the existing absolute
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
with explicit `-B`, inherited Windows OS environment, and fresh own data/config,
TEMP/TMP/TMPDIR roots. Pytest runs additionally have fresh basetemp and JUnit.
`PYTHONPATH`/external pytest options were cleared, not redirected to substitute
source. The focused import-origin test and the independent probe's measured
module path/hash identify this checkout. Probe variants are explicitly labelled
in-memory exploratory code, never production changes or source-hook acceptance.
No product server, private credentials, LAN or hardware was needed.

The runner saves exact argv/cwd, safe environment, UTC times, direct child exit,
complete stdout/stderr and their hashes. Original hidden and ordinary temporary
files are retained. Standalone audit/probe invocations have JSON observations,
not fabricated pytest JUnit. Own original roots and results:

| Root under `C:/t/remediation-recovery/ws-r01/` | Direct result |
| --- | --- |
| `01-focused-debug` | **0**, all 73 focused cases pass, no skip; `--asyncio-debug`, RuntimeWarning/ResourceWarning treated as errors; route/cache plugins disabled. |
| `02-provenance-audit` | **0**, subject/packet hashes, unchanged original test prefix, native inventory and all 31 author receipt stream hashes verified. |
| `03-independent-current` | **0**, 113 checks, zero failed. Explicit `asyncio.run(debug=True)` and actual loop debug assertion. |
| `04-independent-baseline` | **1**, same 113 checks, 28 failed: 16 original-shape truths, two multiple-reservation truths, two self-cleanup results and eight loop-mutation refusal checks. |
| `05-independent-omit-reserved` | **1**, 18 failures limited to 16 original-shape and two multiple-reservation truths; guard/self controls remain passing. |
| `06-independent-loop-noop` | **1**, eight failures limited to missing/foreign-loop mutation refusal; drain controls remain passing. |
| `07-evidence-views` | **0**, native input variants, full report-write equality, author output views, own compact observations and hook skips/routes inspected. |

The four original shapes were independently crossed with cooperative/resistant
work and timeout 0/0.002. Factory entry, cleaner return, factory return, eager
body start, cancellation and release are observed with test-owned gates and actual
Task liveness. During the factory-cleaner window the admitted Task does not exist;
an `all_tasks` snapshot alone would miss it. The nested control holds four
reservations across owners A/B/A/B, then checks real attachment, locality and
termination. Other controls cover attached self cleanup, waiter cancellation at
both scopes, factory exceptions, task-factory refusal/coroutine closure, other-owner
progress despite resistant work, and prebinding/no-loop/foreign-loop boundaries.
Existing unchanged cases additionally cover stale completion callbacks, rejection
without calling factories, eager completion/failure and ordinary cancellation.

All controls release and await their own tasks in `finally`, restore the task
factory, flush callbacks and close their own loops. Even negative variants finish
teardown before the final deliberate failed oracle; their exit 1 is an intended
behavioral detection, not a crash, timeout or unresolved task. The home-loop
cross-loop control cancels and awaits its task on its home loop. The final main
loop inventory has no owned tasks remaining; factory-window proof uses gates in
addition to that inventory.

Own operational errors are not product passes: the first PowerShell runner call
had an ambiguous `-p` parameter before Python launched; an initial private-root
lookup and later mistyped derived-view/report paths failed read-only. These remain
in the transcript; no test receipt was overwritten or claimed for those failures.
Large tool previews sometimes clipped; relevant source/test/report reads were
reissued in bounded chunks. Raw author streams were also inspected through views
that factor only exactly repeated lines, leaving every original byte intact.

## Independent verification of retained author evidence

The read-only correction tree is sibling `wp-remediation-ws-work-c01`; the earlier
review tree is sibling `wp-remediation-ws-work-01-review`. Complete correction
originals remain at `C:/t/remediation-recovery/ws-c01/` and its owned build root.
The actual coordinator closeout root is
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/remediation-execution-20261104/recovery-source-waveA/ws-c01-closeout/`.
I read its full native command inputs and relevant results, native tool inventory,
receipt verification and publication/release evidence. The supplied source worker
is positively released and its task ref published; this review does not repeat
that lifecycle action or perform cleanup.

The normal source commit hook original `31-commit-hook-strict` has direct exit 0,
start `2026-11-04T11:10:10.221872+00:00`, end
`2026-11-04T11:24:34.547748+00:00`, and 864.326 seconds elapsed. Its normal
configured hook ran Ruff and full core without a hook override, with strict route
inventory enabled: **4,155 passed, six skipped, 35 deselected, four warnings;
177/177 routes, 100%**. I checked the actual command/environment, source bytes,
JUnit, complete streams and route JSON rather than relying on report prose.
The authorized retained full-core evidence is used instead of a redundant
fourteen-minute rerun. That core run is not an asyncio-debug run.

Six skips are POSIX permissions, POSIX unlink race, unavailable HA dependencies,
Windows symlink privilege, and two opt-in Chromium profile/scene checks. Warnings
are two started-app mutation deprecations and two aiohttp bare-handler warnings.
These exclusions are not passes. Original `30-final-regress-ws-events-server-runtime`
has 320 passes and exit 0; its **104/177 partial** route inventory cannot replace
strict hook inventory. Final 24/25 focused runs each pass 73, with 25 JUnit loop
properties True/False respectively. Final 26 Ruff, 27 mypy source (92 files),
28 strict new-file mypy and 29 controlled original probe all exit 0.

Author baseline run 06 fails 24 new regressions while all 44 original cases and
five additional cases pass. Selective mutants 07-18 each exit 1, with respectively
20/3/2/1/2/1/2/2/2/2/3/3 failures. Their actual substitutions and assertions address
reservation omission/short-circuit, self dependency, owner scope, synchronous and
asynchronous lifecycle guards, unbound binding/fences, missing loop and done-task
counting. They fail for those intended reasons, not collection/import errors.
Only six unused new-test type-ignore comments differ between that mutation stage
and final tests. Independent controls above separately confirm key truth and
guard sensitivity; mutation counts alone are not a correctness proof.

All failed originals remain: author 02 copied old probe aborted after its old
foreign-loop teardown assumption hung (direct exit 4294967295; empty stdout,
60-byte stderr); later controls add explicit home-loop teardown, not a source
workaround. Author 04 has one genuine test-oracle setup failure (application
limit 2 allowed the purportedly forbidden bystander), 72 passes and property
warnings; corrected setup uses limit 1 and direct user properties. Author 21
fails six unused ignores, then 22 passes after their removal. Native discovery
10 has a Windows `/c/...` FileNotFoundError; native 64 has a failed process-
substitution diff read, followed by the real prefix check. Shell wrapper success
does not erase these child failures. Old WSR-03, old debug-false claims, lost raw
streams, aborted runs and missing-Node hook failures remain historical; no lost
evidence was reconstructed as an original.

## Native route and write audit

`native-final-private.jsonl`: 2,693,249 bytes, SHA256
`98be82696b0ccd8c0d8e6fdf99deb596526b279ca18e051cff457db17ae2bdaf`.
All 889 rows were parsed: 169 model fields identify `claude-opus-5-5`, no
sidechain. Deduplication by tool-use ID yields 84 calls and 84 results: Skill 1,
Bash 64, Read 1, Edit 12, Write 3, PowerShell 2, ToolSearch 1. The ToolSearch
selected Monitor but no Monitor/helper invocation followed. The three observed
cwd values are the author tree and its owned entry/mutant directories. High
effort is launch/config evidence; native per-turn effort is not exposed.

All authored write commands, shell redirections/heredocs, edits, report and
commit-message creation were inspected, not just the final Git diff. Native
duplicate input forms consist of three inserted author-cwd prefixes and twelve
omitted `replace_all:false` fields; they do not conceal another writer. The native
report Write equals the complete final report read here. The correction's direct
source/test writes and report stay in its tracked lease; script, control, mutant,
note, receipt and commit-message writes stay in its assigned ignored roots.

This is not an all-host filesystem audit. Disclosed automatic outputs include
`.mypy_cache/`, `.ruff_cache/`, worktree `route-coverage.json` and
`src/rest_api/__pycache__/ws_request_work.cpython-312.pyc`, plus a harness background
output, cwd markers and persisted read preview under its profile/temp roots.
The unchanged original isolated-import test invokes `python -I`, which ignores
the bytecode environment variable; my own unchanged 73-case run likewise creates
that ignored bytecode in this review tree despite parent `-B`. No source/test was
altered to suppress it. Thus authored scratch compliance is supported, while
literal confinement of every automatic write to two ignored roots is not.
Neither old scratch violations nor current ancillary outputs are silently erased.

Some ancillary historical policy/listing outputs are clipped in native previews;
I do not attest a full historical standing-protocol read by the author or every
line of the coordinator's large ledger/handoff. Required component/test/report
content was available and read independently. No host-wide census, complete
archive extraction, private data audit or backend effort attestation was performed.

## Provenance, final documentation check and retention

Git LF blob SHA256 values at the reviewed source:

| Artifact | SHA256 |
| --- | --- |
| Component | `2352c7d66e281599659bfbdb81c14dab12455f64be6a04fcd2260dc09075e266` |
| Focused tests | `69ac419d6513888831239816e5a7c2dd20e6a5654bafe7d506e3719fdb619776` |
| Original AUTHOR | `028d80071084a988f47e07272785a8ec72940a8302808c907f1b57beea8c24fc` |
| CORRECTION-01 | `16d4f3d4e81b8d6cef2fecd345d1bba330ec6024c3322e697a9299f956ac90f6` |
| Strict hook manifest | `53e938f49fcbaa3385731ba71e366c4602afedbaf9358b2ae80774b5e0532691` |
| Strict hook JUnit | `de94dd96499501ce4f9b0fa4c18df1640a0bc6e154677201b8ec8dc6b08ad779` |
| Strict hook stdout | `041882a41ca9d15ddb55a87ad7ca3c89c907fe35823a62ff5240d35323a4415e` |
| Strict hook stderr | `fdd664923fbf9bdb6fbf2abfced057f6ebea8f796e704ca378bd604eab00c552` |
| Strict hook route JSON | `6f4d570ee7d899010ee1c982086130bebb882bb3323c1581e6573161ed38194a` |

Own `audit-summary.json`, `author-receipts-audit.json`, complete derived native
reads, `probe.py`, compact observations and original per-invocation manifests
remain under the declared roots. The final supplemental documentation run uses
exactly `tests/test_core_documentation.py`, `tests/test_client_guides_docs.py`,
`tests/test_openapi_and_config_docs.py`, `tests/test_security_docs.py` and
`tests/test_license_and_protocol_docs.py`, with
`-p no:tests.route_inventory -p no:cacheprovider` and fresh basetemp/JUnit.
The single run `08-final-docs` returned **0: 489 passed**, no failures or skips,
at `2026-11-04T12:08:42.212202+00:00` through
`2026-11-04T12:08:45.587867+00:00`. Full stdout/stderr, JUnit, safe environment
and direct exit are retained there. It does not overwrite or substitute for
the strict source-hook route evidence.

This report alone is committed using the expressly authorized invocation-only
`git -c core.hooksPath= commit` prose exception. That is a documentation check,
not a normal source/core hook pass for this report commit. Exact report commit,
parent, report SHA256, one-file diff and final receipt inventory are supplied in
the owned completion record and Orca delivery; no push or cleanup is performed.

Verification is Windows CPython 3.12 only. No Python 3.11, real HA, physical HIL,
UI/Tron baseline, LAN, 72-hour soak, week field sign-off, release artifact or
canonical feature evidence promotion follows. Default limits/timeouts and
integration behavior still require the separately gated wiring package.
