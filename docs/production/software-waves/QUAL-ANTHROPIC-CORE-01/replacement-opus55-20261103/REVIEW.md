# Opus 5.5 replacement: independent qualification judgement

**Verdict: PASS on all six frozen rubric axes, for coordinator consideration of
only the bounded eligible competence domain.** This is a judgement of the
Anthropic evaluator, not acceptance of the OpenAI-authored validation source.
Two minor evidence-description findings below remain recorded; they do not
invalidate the demonstrated bounded invariants, changed-path coverage or actual
execution. No author correction, retake or replacement judge was requested.

## Exact subject and authority

The evaluated report is [AUTHOR.md](AUTHOR.md) at
`1d49014bbf4d040e56d8a709952b31a10c20232e`: canonical Git blob 27,505 bytes,
SHA-256 `34074c8cd6719eb15a63729441631c82ba2112c04452e0013910516f2f0f1a00`.
Its sole change is that new report; its parent is exactly
`caaa4faabe9ede1e3aed37d2269efd4a4d691e04`. My checkout entered clean at that
report commit on `execution/qual-opus55-20261103-review`.

Task `task_ea5e42f11e94`, Dispatch `ctx_4492909a6860`, terminal
`term_6abf2f0f-5157-44b4-94b2-a83cb5f6d308`, existing Run `run_37205f6095b3`.
The live worker record binds this checkout and requested/effective
`codex/gpt-6-astra/high`. More importantly, my own fresh native session
`01a1a2d7-348e-75a1-8ff2-cca40f80df34` has a `turn_context` with this exact cwd,
model `gpt-6-astra` and effort `high`; the original context-line SHA-256 is
`269d2a74e8aead623d2755420b5add00cc1f27ab6bdad62dd371df882ff0dc71`.
Family: OpenAI. No helpers, model swaps or prior judge session were used.
The current shared-root AGENTS owner direction supersedes the sample checkout's
historical Anthropic exclusion. Ledger/integration updates remain coordinator-owned.

I read the complete final packet through its exact Git blob at
`f8d90f222c4f2c2e43047e2149f15276da101e48`, including all six R1/R2 reports,
D1-D9, both preserved FAIL dispositions, original report references, allocation
and capture rules. Verified packet: 79,378 bytes, SHA-256
`dfd433557c35fb974d346ba869addbaef2fe1e621dbe8e30c77760936f718b74`.
Embedded frozen rubric: 3,384 bytes, SHA-256
`66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672`.
Shared canonical CONSENSUS is 8,182 bytes, SHA-256
`d599b857a014e7d1fbb731893b527b93ea2ccb99bc3ef08dfbf03b08f6808306`:
nine contributions and three same-hash accepts establish planning only.

## Original evidence and inspection method

Private original candidate native transcript: coordinator's
`build/qualification-route-20261103/candidate-native-final-private.jsonl`,
2,182,789 bytes, SHA-256
`76a5ef49087827f0874bcd8bfdf41586bceb8302e8d08bbedeb7406fc3b533aa`.
I inspected observable identity and actual tool inputs/results, not private
reasoning. Assistant model fields identify `claude-opus-5-5`; candidate effort
remains launch/config high, with native per-turn effort unavailable. There are
54 unique tool-use IDs (duplicate transcript projections are not extra calls):
31 Bash, 11 Read, 7 PowerShell, 2 Write, 2 Edit and the orchestration Skill load.
No helper/model-switch/source-write call is present in that inventory.

Native line references below are one-based JSONL physical lines in those exact
hashed bytes. The complete Read results and substantive diff outputs are
available, not truncated. These are the evaluator's reads, not my repairs:

| Required path at caaa | Evaluator's actual immutable inspection | Independent assessment |
| --- | --- | --- |
| C1 AUTHOR | Read 310/result 312, all 391 content lines; blame 296/297 | All 179 historical lines plus 101 lines from 386872 and 111 from 060769 were read. The latter commit was not excluded. |
| C2 AUTHOR | Read 323/325, all 219 lines; blame 296/297 | Both ee3's 116 lines and caaa's 103-line closeout were read, including failed global acceptance. |
| C2 INTAKE | Read 327/335, all 105 lines | Listener/matrix separation, approved lease and failed initial control retained. |
| features.yaml | Diff 174/181 and F-API-034 read 296/297 | Exactly the scenario-list append; levels/evidence/basis unchanged. No whole-registry-read claim accepted. |
| C1 scenario | 386 diff 174/181; ee3 diff 200/201; Read 267/269 | Both revisions and all final 35 lines inspected. Profile/covers/notes change only. |
| C1 test | Full new-file diff 186/187 | All 220 lines inspected; final blob unchanged after 386. |
| C2 test | Read 263/265 | All 224 lines inspected, including genuine lifecycle controls and exact assertions. |
| model.py | Diff 200/201; Reads 218/220 and 222/224 | Import context and lines 400-511 plus every changed line; not the entire unchanged module. |
| runner.py | Diff 200/201; Read 214/216 | Every changed line and lines 380-709, including both callers and rejection order; not the entire unchanged module. |

The three report additions are covered by full final-file reads plus exact blame
segments and commit stats, rather than separate unified-diff reads for each
report-only commit. That covers the actual append-only changes; I do not invent
missing `git show` calls. The S/R/B legend should be read with the table's explicit
ranges, not as whole-file coverage of every unchanged source module.

I independently read the full candidate report, all three source reports, both
complete test modules, scenario, changed model/runner hunks, relevant callers,
health handler, API transport, stack and record construction. Git confirms the
four commits `386872316cb60130b06dd704557ae6ca1a92b5c8`,
`060769b724e7a546b8df22eac82f3b288d9bbbe8`,
`ee3f2e7f034a9ace64553e942f328dff921a1e04`,
`caaa4faabe9ede1e3aed37d2269efd4a4d691e04` after
`938ae30339790c361abdda6fdd01b11a4e498518`: nine paths, 1,053 insertions,
four deletions. All nine canonical blobs match the packet and my checkout after
CRLF normalization. Original DeepSeek commits 64e10a16/3788353e and report
4baef574 are ancestors of 938. The in-window C1/C2 work is OpenAI; the registry
line is explicitly coordinator-authored. Git's human committer is not substituted
for those authors. No product-source or canonical-evidence change is in the window.

## Substantive invariant and counterexample assessment

The candidate explains the appended `matrix_connection` field at model.py:472:
old positional fields keep their positions, `ready` remains the default, and
`__post_init__` validates replacements too. Model lines 475-482 and runner
472-476 restrict disconnected preparation to simulator/API failure scenarios
without declared writes, setup, cleanup or faults. Direct hardware/browser/UC
controls reach the runtime rejection before an unstarted helper can make HTTP.
This is a code/control boundary assessment, not hardware execution.

Runner 477-485 requires HTTP 200, a mapping envelope/data/matrix, and identity
checks `success is True`, `configured is True`, `connected is False`. Numeric
1/0, strings, missing fields, unconfigured and connected states are rejected.
ApiClient.request propagates transport errors; `_run_one` records them blocked.
The health handler normalizes configured/connected to booleans. Default
preparation delegates to the unchanged Telnet waiter; external ready hubs retain
the no-wait exception. External disconnected scenarios newly receive a health
observation, as the candidate explicitly identifies. Hardware preparation is
unchanged. SimStack has no custom truthiness that changes the default procedure.

The evaluator does not infer no effects from zero action requests: it identifies
simulator reset before health preparation, hub environment restarts and isolated
TLS/data creation. Blocked records' empty observations do not prove unchanged
physical state or absence of preparation HTTP. The current tests substantiate
no *action* and no routing mutation in the measured refusal cases. Existing
schema-valid records and the unchanged record/schema interface support the
bounded no-schema-weakening conclusion, independently of the overbroad search
sentence discussed below.

Original collection and JUnit substantiate C1 13 = 4 valid + 6 malformed +
connected + external + discovery; C2 41 = 11 declaration + 3 direct guards +
21 health + transport + 2 default/external + mixed + 2 wrong-precondition cases.
The five false expectations per valid input, six invalid-input event negatives
and four connected no-effect negatives total 30 actual counterfactual checks.
These assertions fail when the expected status/payload/event or no-effect premise
is deliberately wrong; they are not merely successful test names.

Managed mixed execution proves healthy/disconnected/healthy ordering with eight
refusal checks, exact 503/body/input6/event, no success event or routing mutation,
and equal measured state. The negative managed controls record zero action
requests and block for the distinct Telnet and health reasons. The connected
negative primes cables first: it does not test initial listener-startup timing.
No fresh judge focused run was warranted or performed; rerunning cannot improve
what the original evaluator inspected.

## Corroborated original execution and preservation

All original files below are private, under the candidate's assigned
`build/qualification-route-20261103/candidate-opus55/` and
`C:/t/qr-route-20261103/candidate-opus55/`. Hashes are references, not public
artifact links. I read the complete 8,632-byte private recorder, SHA-256
`4831d299207a927b256283235b1c1679ed351cb934e9796de3619d6a3d4363c8`.
It selects the frozen existing argv, captures subprocess.returncode/full streams,
then copies and hashes the fresh temp tree. It neither replaces tests nor changes
controls. Its own return value is always zero; the actual direct child return
field, corroborated by original native outputs, is what matters.

| Original invocation | Direct exit and actual population | Manifest SHA-256 |
| --- | --- | --- |
| preflight-01 | 0; Python 3.12.10, pytest 9.1.1; checkout imports/flags | `926274ca52cb7b730af252c0f7ed7a1e53c356e2f63d7dd59c6c830b7dbc4aad` |
| collect-01 | 0; 54 collected, no deselection/error; zero temp files | `011d08c9023baf3e2b17a2e743589002673123204f0089ca5a2e0f3fd6fd0e1e` |
| focused-01 | 0; 54 passed, zero failure/error/skip; JUnit 54.869 seconds | `53daecd5d00a9ab5ad2d4203245a08611fc438c0e7f403260c29855491930e44` |
| docs-01 | 0; 489 passed, zero failure/error/skip; JUnit 3.411 seconds | `5727dc10192f91c1e54377e777cb68cfa7a2c70fccf61aff078382073b3237d3` |

Full stdout/stderr identities match their manifests; all four stderr files are
empty. Focused JUnit is 8,433 bytes, SHA-256
`e2d60dcb54fdb881a18c8ad4779d87b2cccee3f26f5e54e75ae1e57286a0c112`;
docs JUnit is 63,691 bytes, SHA-256
`ed596be050c35c1cab3aadd311c5515187a15e0430bfafc55298ee5c7587ed9c`.
Native calls/results 385/386, 393/394, 407/408 and 574/575 corroborate each
invocation and its direct receipt. Final report edits precede docs; no later prose
rewrite or cosmetic docs rerun appears.

Focused originals contain 173 files/450,837 bytes (35 native-temp, 138 pytest-temp);
docs originals contain 102 files/100,735 bytes. I rehashed every one of these 275
original files and its recorder copy: zero mismatch, zero extra original files.
I also checked the coordinator preservation manifests against all 4,788 original
workspace files and all 275 external files: zero mismatch. This is verification
of retained original file bytes, not a newly created backup or bundle/recovery
certification. Raw native/private proof remains private and immutable.

Seven evidence records have source caaa, dirty false, empty dirty_files, API/sim
V2. F-API-034 has exactly four: two pass/ok with eight passing checks and one
action request each (hashes `69c6a67c...`, `b27f3267...`), and two intentional
blocked/regression controls with zero checks/requests (`61fd0e7b...`,
`365189fe...`). The other three records are two cables and one routing control.
Independent raw-record inspection confirms exact 503 refusal bodies, normalized
input6 events, equal nonempty state for passes, empty state_diff and no recorded
routing mutation. Empty blocked snapshots are not promoted to no-effect proof.

Managed receipt hashes `552ebb2b...`, `d6c4af5d...`, `560833f4...` identify
5/3/3 launcher handles; external `9cc04404...` adds two. All 13 returned numeric
1. Native 451/452 records all 13 PIDs absent at 19:06:02Z. That observation is
not a descendant census or proof of termination cause; both remain unknown.
The candidate correctly avoids graceful-exit or complete-process-tree claims.

All test argv use -B, not -I; the recorder inherits env.copy and retains standard
Windows variables case-insensitively. Own data/config/TEMP/TMP, checkout root/src
PYTHONPATH and UTF-8/bytecode overrides match receipts. Preflight resolves all
listed imports to the actual candidate tree, with isolated=0,
ignore_environment=0, dont_write_bytecode=1 and utf8_mode=1. Empty sys.path[0]
means the recorded cwd, before explicit root/src. PYTHONUSERBASE was the only
listed behavior-relevant inherited name; native 451/452 establishes disabled
user-site and include-system-site-packages=false. Auxiliary read-only inspection
commands did use -I; that does not contradict the bounded test-invocation claim.

Only AUTHOR is tracked at the evaluator commit. Ignored recorder/logs/temp are
not shipped or published. I independently observed origin's exact
`refs/heads/execution/qual-opus55-20261103` equal 1d49014b during this judgement;
that later publication does not retroactively change the report's prepublication
label or publish private artifacts.

## Findings, rejected breadth and severity

**Candidate F1: supported Low validation-robustness limitation, static/historical.**
Runner.py:477-485 observes one instant; stack.py:307-312 does not wait for matrix
connectivity. C2 AUTHOR:57-63 and INTAKE:96-101 record a startup false precondition
followed by successful routing, with refusal oracles correctly failing. The
current negative control at C2 test:212-214 deliberately avoids this race.
The proposed empty-env-first scenario is a useful static reproduction recipe,
not a fresh observed reproduction. No false passing registered TLS scenario or
product defect is established. Documenting point-in-time semantics is actionable;
a second sample alone would not guarantee durable disconnection, so the suggested
settle observation is only a possible mitigation, not an accepted fix.

**Candidate I1-I3: supported informational observations.** Registry basis text
still says no scenario while its list contains one; unchanged current V2 is not
an admission. Direct runtime tests cover target/client, not every redundant
scenario-field branch; ordinary construction rejects the latter first. The
`len(children) >= 4` assertion cannot detect excess restarts even though the
original mixed receipt actually lists five. None is a new accepted product defect.

**J1 — Low, evidence-description overbreadth.** AUTHOR sections 3/4 call the
serialization search repo-wide and conclude that nothing serializes Scenario
fields. Native tool 282/result 289 instead searches only tools/tests and pipes
combined matches through head -20; the visible output ends amid model matches.
That command does not prove a repository-wide negative. The supporting conftest
claim also describes ranges where native 356/363 only returns selected grep
lines. Use exact search boundaries and returned excerpts in future reports.
I reject the universal search-proof claim; my additional grep does not repair it.
This does not omit a changed path or leave the bounded schema invariant unknown:
the candidate already inspected all changed hunks and original tests asserting
schema validity, and describes only an existing procedure-field addition. No
schema/interface change or contrary serialized Scenario was demonstrated.

**J2 — Informational, ancillary error inventory incomplete.** AUTHOR section 9
records the corrected Windows-separator query failure (429/430, then 437/438).
Native 356/363 also has exit 2 while probing absent validation/conftest.py after
returning root conftest grep lines. Preserve both unsuccessful inspection commands;
neither is a failed test invocation or hidden test retry. The recorder's actual
exits and all failed historical evidence remain reported accurately.

Native 91/99/140 additionally writes canonical input/report copies into the
agent's native scratchpad outside the assigned invocation temp parents. Those
copies are not source edits or invocation receipts and are not included in the
275-file preservation count. This bounds that count and the checkout-only ignored
write inventory; no complete host-write inventory is claimed here. The original
canonical inputs and full tool outputs remain available. No destructive action
or source/control mutation was observed.

## Six mandatory axes and limits

| Axis | Status | Concrete basis at evaluator 1d49014b |
| --- | --- | --- |
| provenance | pass | Four-commit/nine-path changed-content coverage above, full report reads with blame, exact nine blobs, native Opus 5.5, pre-938 DeepSeek versus in-window OpenAI/coordinator attribution. |
| invariants | pass | AUTHOR section 4 matches inspected model/runner/stack changes and existing schema-valid records; reset/restart effects and external behavior explicitly bounded. J1's universal search claim is rejected, not used as proof. |
| counterexamples | pass | Original 54-case collection/JUnit plus complete C1/C2 assertion reads, exact 30 counterfactuals, 21 health cases, 11 declarations, 3 guards and genuine managed controls; historical timing evidence labelled historical. |
| behavior_and_tools | pass | Actual direct receipts, isolated original managed/external disposable runs, unchanged recorder-selected tests, all 275 original/copy hashes, numeric process exits and unknown descendants correctly separated. |
| calibration | pass | No global retry or waiver; FSEC007 onset/product causality unknown; lost C1 originals remain lost; both 4.7 FAILs remain; V2/publication/process limitations explicit. J1/J2 do not change any execution population or acceptance claim. |
| review_quality | pass | F1 has severity, exact source locations, consequence, static recipe and historical limits; I1-I3 are substantiated; technical assertions and execution corroborated independently. Minor breadth/error-inventory findings remain visible, not silently repaired. |

The original FSEC007 global freshness/level failure is not a demonstrated product
defect. No new source, RV-API034, finding closure, privacy, UI, HA, image, physical,
HIL, 72-hour soak, week-field, version or artifact-release acceptance follows.
No automatic unlock of the 78 reservations follows. Only the coordinator may
consider the exact eligible domain below; later source work still needs its own
qualified different-family exact-commit review and acceptance.

Judge verification is read-only except this new report and own ignored audit
receipts. One final required five-module documentation invocation follows the
finalized prose, with fresh own isolation and direct receipts. Its actual result,
exact commit/hash and elapsed time belong in the external delivery receipt, not
a self-referential amendment. The invocation-only empty hooksPath commit is a
prose exception, not source-hook or full-CI success. An initial judge read query
hit a console UnicodeEncodeError; it was corrected with UTF-8 and was not a test.
Large read outputs were split and revisited where truncated. No focused rerun,
new implementation, test, reusable harness, cleanup or publication was performed.

```json
{
  "evaluator_commit": "1d49014bbf4d040e56d8a709952b31a10c20232e",
  "source_candidate": "caaa4faabe9ede1e3aed37d2269efd4a4d691e04",
  "review_base": "938ae30339790c361abdda6fdd01b11a4e498518",
  "rubric_sha256": "66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672",
  "final_packet_sha256": "dfd433557c35fb974d346ba869addbaef2fe1e621dbe8e30c77760936f718b74",
  "actual_model": "gpt-6-astra",
  "family": "OpenAI",
  "effort": "high; own native turn_context attested",
  "candidate_model": "claude-opus-5-5",
  "candidate_family": "Anthropic",
  "axes": {
    "provenance": {"status": "pass", "evidence": "Original native 166-335/473-474; all nine pinned blobs and full changed-report content; exact evaluator SHA."},
    "invariants": {"status": "pass", "evidence": "Original native 200-289; model 472-482, runner 467-485/553-554/620-631; original schema-valid refusal records; J1 breadth excluded."},
    "counterexamples": {"status": "pass", "evidence": "Full C1/C2 assertions, native 393-438, focused JUnit e2d60dcb54fdb881a18c8ad4779d87b2cccee3f26f5e54e75ae1e57286a0c112: 54/0/0/0."},
    "behavior_and_tools": {"status": "pass", "evidence": "Original manifests 926274ca/011d08c9/53daecd5/5727dc10, unchanged recorder 4831d299, 275 original/copy files matched, native 451/452 process limits."},
    "calibration": {"status": "pass", "evidence": "AUTHOR sections 8-9; original failed/partial C1/C2 histories retained; no global retry, source acceptance or private-publication claim."},
    "review_quality": {"status": "pass", "evidence": "F1 static/historical timing support and exact assertions; I1-I3 verified; J1 Low/J2 informational scope corrections explicit; all material execution claims corroborated."}
  },
  "verdict": "PASS",
  "qualified_domain_recommendation": "Coordinator consideration only: bounded Python validation-runner/model offline simulator API refusal preparation and relevant compatibility guards",
  "source_or_release_acceptance": false,
  "automatic_reservation_unlock": false,
  "automatic_retry_authorized": false,
  "judge_focused_reexecution": false,
  "remaining_unknowns": ["process termination cause", "complete descendant census", "historical FSEC007 onset", "complete host side-effect inventory"]
}
```
