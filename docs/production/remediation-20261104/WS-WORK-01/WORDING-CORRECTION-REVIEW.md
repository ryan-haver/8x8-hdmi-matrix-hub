# WS-WORK-01: reserved wording correction source re-review

Date: 2026-11-04. Reviewer assignment: native OpenAI `gpt-6-astra/high`.

| Decision | Result |
| --- | --- |
| Exact source wording at `78295ecdf8c47e330786e10eb8e00136c2025b7d` | **PASS**; C01-R01 corrected |
| Component runtime relative to `24c5170458200209836228646fdfc8784a967ad1` | **UNCHANGED, independently proved**; prior component PASS correlates to this subject |
| Direct authored-write scope | **PASS, bounded to observed native authored operations**; C01-R02 limits retained |
| Original first-authorship | **NOT_GRANTED / HOLD**, unchanged |
| WSR-03 | **Historical FAIL**, unchanged |
| Privacy competence, source intake, WS wiring, CR-01 closure, owner acceptance | **Not granted**; existing holds remain |

This uses the single reserved changed-commit product re-review, not another
qualification attempt, new phase, revised runtime contract or additional judge.
No automatic further correction round follows this report. A few evidence-prose
precision issues are recorded below; none overturns the source wording verdict.

## Authority and immutable inputs

Task `task_2baa71b16197`, Dispatch `ctx_0c1b1f2300b7`, worker
`term_5bb1ad09-cd60-4213-993a-75ce92f522f1`, Run `run_37205f6095b3`.
Live Orca worker-list matched this assignment, native Codex/Astra route and
`wp-remediation-ws-wording-review` tree. Branch `remediation/ws-wording-review`
started exactly at the subject, whose parent is the base above. The original
wording author is Anthropic `claude-opus-5-5`, a different underlying family.
Author high effort is launch/config evidence; native per-turn effort is unexposed.
This reviewer assignment is not independent backend attestation of itself.

At entry I resolved `wp-runtime-completion` once to
`4bbc26731be8942a7e29dbc712218623e063d5be`. That immutable ref supplied the
relevant adopted FINAL_PACKET decisions/allocation, consensus, latest ledger,
handoff/execution entries, delivery/preflight and this exact task specification.
The packet's raw Git SHA256 is
`f8fe93c8e673c2341b36ba93c2d0920bdd04af42c12b69daac12fae191ed103e`.
D1 permits this reserved product correction; D2 preserves all-unfinished-work
counting and conservative bounded cleanup; D3 preserves pre-mutation loop guards.
D6 and privacy/wiring qualification holds are not changed. The coordinator owns
ledger updates; this worker's explicit lease excludes those files.

Prior qualified whole-component review:
`ed69708325f9e10a2ae2784179303016acbd69d0`, reviewing exact base `24c51704`.
I read its report, the complete current 519-line module, the complete two-file
changed-commit diff and the new 158-line WORDING-CORRECTION report. I read the
retained reviewer's progress control and relevant original observations, the
old correction's erroneous mechanism sentence, and the focused tests' import,
debug and other-owner progress assertions. I do not claim a fresh line-by-line
review of all 1,502 unchanged test lines or the whole application caller graph;
those retain the prior exact-component review's scope and limits.

## C01-R01 semantic dispositions

| Wording location | Disposition and reasoning |
| --- | --- |
| Module docstring, Truthful drain | **Corrected.** It explicitly calls immediate non-drained return during a reservation the adopted conservative bounded policy, then explains that a separately spawned eager cleaner can suspend and permit factory/admission/sibling progress. |
| First `_drain` early-return comment | **Corrected.** It describes the reservation condition and policy without claiming universal inability to progress. Zero timeout and no pending attached task still return immediately under the unchanged branch. |
| Self-dependency paragraph/comment | **Correct.** An attached calling task cannot complete while its own cleanup invocation is still awaited. Other tasks may progress; that does not make the caller done or the entire scope drained. |
| Historical CORRECTION-01 mechanism step 1 | **Explicitly corrected in the new report.** The author quotes and attributes the old claim that admission cannot finish before cleanup returns, calls it overly broad, and supersedes its explanation. The old report is byte-identical and remains historical. |
| `aclose` / `shutdown` method docstrings | **Appropriately unchanged.** They describe immediate non-drained return, without the former universal no-progress rationale. |

The explanation is consistent with actual control flow. `_admit` is synchronous;
it reserves before calling the factory or starting an eager task step, registers
the task, then releases the reservation. A cleaner's eager first step can run
inside this stack, suspend, and return control to its creator without completing
the cleaner. A reservation is not an attached Task usable as the argument to
`asyncio.wait`; this is not a claim that the admitted Task can never exist yet
during an eager step. The revised word **attached** matters.

`_drain` still recounts reservations plus unfinished attached tasks of its scope,
including its own caller. `requested` still counts successful cancellation
requests on attached tasks; it does not count cancelled reservations. Owner scope
remains local. Reservations and self-dependency short-circuit conservatively;
ordinary eligible pending work uses one bounded wait and a fresh recount.
Timeout-zero/empty-pending fast paths remain in force; the prose's ordinary-wait
sentence is read in that context, not as a promise to await an empty collection.
Lifecycle loop checks still precede fence/cancellation mutation and never bind an
unbound controller. No D2/D3 implementation, interface or test changed.

## Independent proof and focused execution

Own artifacts are exclusively in this tree's ignored
`build/remediation-recovery-20261104/ws-wording-review/` and fresh invocation roots
`C:/t/remediation-recovery/ws-wording-review/`. `run.ps1` launches the existing
absolute `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
with `-B -I`, inherited Windows environment, then fresh data/config/TEMP/TMP/TMPDIR
roots. It clears inherited PYTHONPATH/PYTEST_ADDOPTS, records exact argv/cwd,
safe environment, UTC start/end, direct child exit and complete stdout/stderr,
and hashes/inventories ordinary and hidden files. Pytest additionally uses its
own fresh basetemp/JUnit; standalone scripts have JSON output, not invented JUnit.
Scripts insert this checkout's `src` explicitly and measure actual import origin.

| Own root | Result |
| --- | --- |
| `01-focused-debug` | Exit **0**, **73 passed**, no failure/error/skip; one run only |
| `02-audit` | Exit **0**, AST/tree identity, input hashes, complete native parse and debug-property counts |
| `03-progress` | Exit **0**, actual policy and scheduling counterexample both pass; actual loop debug true; no owned task left |
| `04-evidence` | Exit **1**, my audit script incorrectly expected route key `missing`; actual schema uses `uncovered`; original script/streams retained |
| `05-evidence-corrected` | Exit **1**, my comparison did not account for doubled CR line separators in the native numbered Read output; original script/streams retained |
| `06-evidence-final` | Exit **0**, corrected representation comparisons, all eight author manifests' captured artifacts verified, native write/edit replay equals actual retained files |

The focused invocation is `focused.py` under that interpreter; its printed pytest
argv selects `tests/test_ws_request_work.py -q --asyncio-debug`, disables
`tests.route_inventory` and `cacheprovider`, promotes RuntimeWarning,
ResourceWarning, pytest unraisable and thread warnings to errors, and names fresh
basetemp/JUnit. All **25** pairs of `asyncio_debug_configured=True` and
`asyncio_loop_debug=True` were independently parsed. The fixture compares actual
`loop.get_debug()` with configuration. The measured module is this review tree,
CPython **3.12.10**, raw working SHA256
`95fe2a40e281658e0af9bd003b299df99ce8b14d00f1c52368f13084306c9921`.

`audit.py` compares base Git blob, subject Git blob and actual working module ASTs,
removing **only** the module docstring statement and omitting location attributes.
Function/class docstrings remain included. All dumps have SHA256
`73ea0540fea5374108a705bac848f0c3ef619da70204c88e41d045eb0d10d5fa`.
In-memory negative controls changing a function docstring and an executable
integer constant both break equality. These are comparison controls, not product
mutations or substituted runtime acceptance. The complete diff has exactly the
three authorized prose hunks and the new report. All **4,728** other base tracked
entries have identical mode/type/blob identities, including every test. The
author's 03 and 09 raw snapshots also match all 4,728 current retained files.
Intentional module `__doc__` text and source line locations differ; the proof is
of executable behavior under the stated comparison, not byte-identical modules
or identical traceback line numbers.

`progress.py` uses the real imported controller with a sibling and a second
admission. The real owner cleanup returns `(requested=1, remaining=2)` before the
factory resumes. A separately labelled scheduling counterexample uses real
`owner.close()` followed by an ordinary bounded wait in an independent eager
cleaner: the factory resumes while that cleaner is unfinished, admission attaches,
and sibling and admitted bodies finish before the cleaner returns. This is a
counterexample to the old universal rationale, not a proposed replacement for
product cleanup. It uses observed event order, task completion and attachment,
not counters alone. Both paths restore the task factory and cancel/await owned
tasks in bounded `finally` blocks. No server, LAN, device or private data is used.
The retained old `progress_control` independently records the same possibility.

## Retained author evidence and failures

Author originals remain read-only in sibling `wp-remediation-ws-work-c01` under
`build/remediation-recovery-20261104/ws-wording/`, and
`C:/t/remediation-recovery/ws-wording/`. Coordinator originals are under
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/remediation-execution-20261104/recovery-ws-wording/closeout/`.
The author is positively released and its task ref published at the exact subject,
as recorded in actual lifecycle/publication receipts; I did not contact, restart,
release, publish or clean that worker.

I inspected the actual eight recorded invocations, proofs, original streams,
JUnit properties/skips and route data, verifying every manifest's captured hash
and size. Derived views preserve originals; the large failed filename list was
counted rather than represented as a semantic source read. Actual results:

- `02-prove-ast-hash`: exit **1**, CRLF/Git-LF comparison mistake; AST equality
  passed. **3,889 of 4,728** non-leased files mismatched that invalid comparison,
  not every file; the focused test's raw bytes already matched.
- `03-prove-ast-hash`: exit **0**, **intermediate wording only**, not final proof.
- `04-ruff-ci-paths`: exit **0**, CI lint paths, all checks passed.
- `05-mypy-src`: exit **0**, no issues in **92** source files.
- `06-focused-debug`: exit **0**, **73 passed**, 25 true debug-property pairs.
- `07-import-origin`: runner brace substitution raised `KeyError` **before the
  child launched**. Empty data/config/native-temp directories remain; no child
  exit or missing stream is invented.
- `08-import-origin`: exit **0**, actual author checkout and final CRLF hash.
- `09-prove-final`: exit **0**, final module AST and Git/raw snapshot checks pass.
- `10-commit-hook-strict`: direct git child exit **0**, normal configured source
  hook with no hooksPath override; Ruff plus **4,155 passed, six skipped,
  35 deselected, four warnings**, strict **177/177** actual routes.

The hook ran **2026-11-04T13:03:02.560337Z** through
**13:17:22.985287Z**, 860.425 seconds. Its full pytest output is in **stderr**,
while stdout records the actual two-path source commit. The route bytes were
identical before/after; native input 47 explicitly copies the post-hook file.
Fresh execution is supported by the actual hook output, invocation/environment
and JUnit, not by a changed route hash. Hook debug properties are **False**, so
this full core is not described as an asyncio-debug run. I did not repeat it.

The six skips are POSIX permissions, POSIX unlink-while-open race, unavailable HA
dependencies, Windows symlink privilege, and two opt-in Chromium profile/scene
checks. Four warnings are two started-app mutations and two aiohttp bare-handler
deprecations. Neither skips nor deselections are passes. The source hook excludes
HA and UC suites. No hardware, UI, soak or full-release claim follows.

An additional author failure is preserved in **native input/result 47**: its
completion script searched stdout alone for the pytest summary and raised
`IndexError`, exit 1, before writing completion.json. Input 48 reads both streams
and writes the actual completion record. This is a receipt-script correction,
not a second source hook or overwritten failed test run.

## Native authored-write audit and C01-R02 limits

The full native file is **1,523,472 bytes**, SHA256
`e3c2ee13124388f8713e415c3a19d3cab925e76346c727bfba7c29a0ba12ff0c`.
All **578 rows** parse. There are **49 unique tool calls and 49 matching results**:
Skill 1, PowerShell 2, Bash 29, Read 1, Edit 13, Write 3. All 96 model fields say
`claude-opus-5-5`; no sidechain/helper launch appears. The observed row cwd is the
author tree. There are 36 duplicate input variations: 23 author-cwd prefixes and
13 omitted `replace_all:false` fields; exact normalization reveals no other input
change. The complete native transcript is an input to the audit, not a claim to
host-wide operating-system surveillance or native per-turn effort evidence.

I read every distinct command/edit/write input, including heredocs, shell
redirections, staging, commit, post-hook copy and receipt construction. I inspected
corresponding results; full prior-report and numbered source outputs are verified
equal to the separately read exact blobs. Shell output excerpts remain excerpts;
no claim is made that the author read every historical policy/test line merely
because it hashed or listed those files. Native Write/Edit replay in memory
matches actual final module, report and scripts; it is explicitly a derived
comparison, never a reconstructed missing original. All direct authored source/
report edits stay in the two leased tracked paths. The entry snapshots, runner,
proof/import scripts, raw snapshots, diff, commit message, route copy and
completion receipt stay in the assigned ignored roots. No new out-of-lease
scratch file or source edit was found.

C01-R02 remains **bounded**, not erased: automatic cache/route/bytecode and harness
outputs can occur outside the two ignored roots. The native hook's background
output is under the session's AppData Temp profile; the hook also writes the
worktree's ignored route JSON. The unchanged isolated-import test launches
`python -I` without `-B`, so its bytecode can appear in the worktree despite the
parent's flags; my own 73-case run has that same inherited limitation. No product
test was changed to conceal it. I do not certify all-host write confinement.

**C01-WR01 (Low, evidence-description precision; nonblocking to source wording).**
The new report's phrase “every file mismatched” is inaccurate: the actual number
is 3,889/4,728 above. Its “all runs” isolation description is accurate for the
recorded check children, but cannot be expanded to every native Python command:
input 20 uses bare `python -c` for a read-only old-manifest preview, and inputs
30/40/47/48 also perform metadata reads/receipt construction outside the fresh
check runner. Full per-invocation isolation/receipts are therefore not established
for every metadata command. The post-hook input-47 failure also supplements the
two failures listed before that hook in the report. These observations are
recorded here without editing history, source fixes, another review round or a
broad process-compliance/first-authorship grant.

My own failed audit invocations 04/05 and exact scripts remain alongside the
successful 06. The first staged whitespace check flagged an extra blank line at
EOF; that report formatting issue was removed before commit. Initial large
terminal previews clipped; relevant semantic reads
were repeated in bounded chunks or compared to separately read exact content.
I did not semantically reread every historical ledger line, all archived temp
contents or every one of the 4,161 full-core JUnit testcase names; the complete
XML was parsed for counts/properties/skips, and original full hook streams read.
No missing historical original was reconstructed or relabelled.

## Hash bindings, documentation validation and delivery

Git LF SHA256 bindings (working CRLF hashes are deliberately separate):

| Artifact | SHA256 |
| --- | --- |
| Subject module | `3ae622fd21ca8b8c9472d0758df66bf7f674e5462ad251c8cb6417521d013449` |
| Base module | `2352c7d66e281599659bfbdb81c14dab12455f64be6a04fcd2260dc09075e266` |
| Unchanged focused tests | `69ac419d6513888831239816e5a7c2dd20e6a5654bafe7d506e3719fdb619776` |
| New author WORDING-CORRECTION | `5d3a1625d42aae4c24a30895680068703504c39a610cdb644cb1c730a963cb38` |
| Historical CORRECTION-01 | `16d4f3d4e81b8d6cef2fecd345d1bba330ec6024c3322e697a9299f956ac90f6` |
| Prior CORRECTION-01-REVIEW | `118159251a37ed65ba4afdf2c468eded9dff8bef45f8021f767b89f9354708ef` |
| New author hook stdout | `c3935815e760b6c7f1329fbf2403ff97dc2fb81201624b52ebe82b807a476aad` |
| New author hook stderr | `530d7a1938462ab29cecd99775f7020331e93bfdfde83232d1ac77fced96cfe0` |
| New author hook JUnit | `5c536a7f5297f7dbcfdef775d2faf19e5ad48539db3e3bf700bb5327d6262765` |
| Strict route post-hook copy | `6f4d570ee7d899010ee1c982086130bebb882bb3323c1581e6573161ed38194a` |

The final documentation check selects only `tests/test_core_documentation.py`,
`tests/test_client_guides_docs.py`, `tests/test_openapi_and_config_docs.py`,
`tests/test_security_docs.py` and `tests/test_license_and_protocol_docs.py`, with
`-p no:tests.route_inventory -p no:cacheprovider`, fresh basetemp/JUnit and the
same isolated runner. The single run `07-final-docs` returned **0: 489 passed**,
no failures/errors/skips, from 2026-11-04T13:32:08.0578315Z to 2026-11-04T13:32:11.4138931Z;
original full streams, JUnit and receipt remain in that root.
The existing strict route evidence is preserved and is not regenerated.

Only this new report is committed using the explicitly authorized invocation-only
`git -c core.hooksPath= commit` prose exception. This is not a source-hook pass
for the report commit. The completion record and Orca delivery supply the full
commit, parent, report blob SHA256 and exact one-path diff. Local coordinator
`.codex/config.toml` remains unchanged/untracked/unstaged. No push, cleanup,
release, subagent, helper, model switch, global setting or ledger generation was
performed. Coordinator preservation/publication/intake remain separate actions.

Windows CPython 3.12 is the measured platform. Existing first-authorship
NOT_GRANTED/HOLD, WSR-03 historical FAIL, old Opus and M3 privacy FAIL, held
D6/wiring, source intake and CR-01 closure are unchanged. No Python 3.11, HA/LAN,
physical HIL, visual baseline, 72-hour soak, week field sign-off, release artifact
or owner acceptance is granted by this bounded source wording PASS.
