# QUAL-ANTHROPIC-CORE-01 replacement evaluation: Opus 5.5

This is the candidate evaluation report for the single authorized Opus 5.5
replacement attempt. It is **not** a qualification verdict. The candidate does
not pass itself on any axis. An independent OpenAI judge decides all six rubric
axes, and the coordinator records the final bounded disposition. Nothing here
accepts source code, RV-API034, findings, privacy, HA, hardware, Tron, HIL,
72-hour soak, week field, version or artifact release, or unlocks the 78 review
reservations.

**Outcome in short.** I reviewed the full four-commit, nine-path window. The
three existing invocations (collection, focused and documentation) were run
exactly as the frozen packet prescribes, with direct return codes recorded. The
focused run collected and passed 54 of 54 cases. It produced four F-API-034
records, two of them deliberately blocked controls. I report one **Low**
finding (F1) and three informational notes. I found no product-source defect,
and the window changes no product source.

## 1. Authority, identity and inputs

- Task `task_5b5162506677`, Dispatch `ctx_5e62800cd2dc`. Existing Run
  `run_37205f6095b3`, coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`
  (generation 5). Worker terminal `term_61fbb9cb-1270-4002-b497-b6c9e244b5e2`.
- Route: Anthropic, native model ID `claude-opus-5-5`. High effort comes from
  the dispatch and local configuration. Native per-turn effort is not
  observable inside the session. No helpers, subagents, teams, MCP, plugins,
  model swaps or fallbacks were used. The coordinator captures and hashes the
  native transcript.
- Root `AGENTS.md` direction of 2026-11-01 permits Anthropic candidates. The
  `AGENTS.md` at caaa (Claude exclusion) is older checkout text and does not
  override it.
- Worktree `wp-exec-qual-opus55-20261103`, branch
  `execution/qual-opus55-20261103`. Entry was clean at exact HEAD
  `caaa4faabe9ede1e3aed37d2269efd4a4d691e04`. Inbox was empty at startup,
  after the checks and before the commit.
- Inputs were read through pinned-ref `git show`; nothing was copied into the
  sample checkout. All hashes match:

| Input | Ref | Bytes | SHA-256 |
| --- | --- | --- | --- |
| `FINAL_PACKET.json` | `f8d90f22` | 79,378 | `dfd433557c35fb974d346ba869addbaef2fe1e621dbe8e30c77760936f718b74` |
| `QUALIFICATION_RUBRIC.json` | `f8d90f22` | 3,384 | `66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672` |
| shared-root `CONSENSUS.json` (read in place) | n/a | 8,182 | `d599b857a014e7d1fbb731893b527b93ea2ccb99bc3ef08dfbf03b08f6808306` |
| attempt-1 evaluator / judge | `97c47be3` / `5b70c916` | 25,102 / 17,488 | `cb7ccfc3…` / `edf0cc17…` (match packet) |
| attempt-2 evaluator / judge | `78eea151` / `7548b5b7` | 16,677 / 18,514 | `4dfbfc8a…` / `23f0676c…` (match packet) |

I read every section of the final packet: the authority, all six R1/R2 reports,
dispositions D1–D9, the sample manifest, the rubric, both prior dispositions,
staffing, the commands and capture rules, capacity and recovery. `CONSENSUS.json`
records 9 of 9 contributions, three explicit `accept` votes on the same packet
hash, and no unresolved blockers. I also read both prior judge reports in full.
Their findings were: attempt 1 J1–J4 (deleted original, unproven exits,
causal FSEC007 exclusion, miscounts) and attempt 2 J1–J3 (`060769` excluded,
ignored sidecar called published, file/record populations misstated). I read
no private planning reasoning or traces.

## 2. Fixed sample, lineage and authorship

`git log 938ae303..caaa4faa` gives exactly
`938ae303 → 38687231 → 060769b7 → ee3f2e7f → caaa4faa`. All four commits are
in scope. The rubric's `source_commits` (`38687231`, `ee3f2e7f`) is shorthand
for the two implementation commits; it does not exclude the report-only commits
`060769b7` and `caaa4faa`. The full diff touches nine files, with 1,053
insertions and 4 deletions. All nine blobs at caaa equal the packet manifest
(`c72db0cc`, `5f3f408c`, `1286fca5`, `ff61632f`, `ea3fe000`, `a7bddfcd`,
`c654a189`, `30f9c0ad`, `95df14bb`).

Authorship (as recorded; I do not relabel it):

- **DeepSeek, before the window.** The `deepseek-v4-pro` product-handler fix
  (`64e10a16`, `3788353e`) and its report, C1 AUTHOR lines 1–179 (blame
  `4baef574`). All three commits are verified ancestors of `938ae303`.
- **OpenAI `gpt-6.1-sol/high`, inside the window.**
  - The C1 declarative follow-up in `38687231`: scenario, test and C1 AUTHOR
    lines 180–280. Authority is task `task_c0d26e9e563e` and dispatch
    `ctx_0f27082dc4eb` (C1 AUTHOR:184–190).
  - The report-only partial disposition in `060769b7` (C1 AUTHOR lines 281–391).
  - C2 in `ee3f2e7f`: model, runner, scenario update, C2 test, INTAKE and
    C2 AUTHOR lines 1–116. Authority is `task_14b35f83dc26` (C2 AUTHOR:5–8).
  - The report-only C2 closeout in `caaa4faa` (C2 AUTHOR lines 117–219).
- **Coordinator.** The one-line F-API-034 `scenarios` append in `features.yaml`
  inside `38687231` (C1 AUTHOR:212–223, "composite authorship").
- **Git committer.** "Ryan Haver" on every commit. The committer account is not
  the model author.

There is zero diff in the window for `src/`, `tools/validate/stack.py`,
`tools/validate/clients/` and canonical evidence. That was checked with a
`git diff 938ae303 caaa4faa -- <paths>` line count of 0.

## 3. Coverage matrix (nine paths × four commits)

Proof legend:

- **S** = per-commit `git show <sha> -- <path>` full diff read.
- **R** = full Read-tool read of the caaa checkout file.
- **B** = `git blame --line-porcelain` line-origin census at caaa.
- **X** = exercised by my focused invocation.

All reads happened in this session; the native tool transcript holds them.

| Path | Commits that change it | Inspected revisions and proof | Key reasoning | Finding |
| --- | --- | --- | --- | --- |
| `docs/production/software-waves/SW-API-CLIENT-02-C1/AUTHOR.md` | 38687231 (+101), 060769b7 (+111) | caaa R (lines 1–391); B: 4baef574×179, 38687231×101, 060769b7×111; stat for both commits | Append-only. Lost managed originals stay lost (225–241, 346–353). FAILED/partial outcome kept. "30 live counterfactual checks" (325) recomputes to 4×5+6×1+4 = 30. | I1 (basis wording) |
| `docs/production/software-waves/SW-API-CLIENT-02-C2/AUTHOR.md` | ee3f2e7f (+116), caaa4faa (+103) | caaa R (1–219); B: ee3f2e7f×116, caaa4faa×103 | Attempt01 race is recorded (57–63). FSEC007 gate failed once with no retry (174–196). Acceptance PARTIAL/UNMET (198). | F1 context |
| `docs/production/software-waves/SW-API-CLIENT-02-C2/INTAKE.md` | ee3f2e7f (+105) | caaa R (1–105); B: ee3f2e7f×105 | `wait_ready` deliberately waits only for the listener (11–13). Lease constraints match the code (82–89). Attempt01 observation (96–101). | F1 context |
| `docs/validation/features.yaml` | 38687231 (1 line) | S 38687231; caaa F-API-034 entry read (lines 4836–4848) | Only the scenario ID is appended. `current: V2`, `target: V3`, evidence, findings and basis are unchanged. | I1 |
| `tests/validation/scenarios/sw_api_client_02_c1.py` | 38687231 (new), ee3f2e7f (+8/−7) | S both; caaa R (1–35) | Adds `matrix_connection="disconnected"` (12), keeps the TLS `hub_env` (16), adds C2 to `covers` (30), rewrites notes (31–33). Identity, action and expectations unchanged. | none |
| `tests/validation/test_sw_api_client_02_c1.py` | 38687231 (new; blob unchanged afterwards) | S 38687231 (full file); X 13 cases | Assertions at 70–95, 100–113, 116–135, 188–211, 214–220. | none |
| `tests/validation/test_sw_api_client_02_c2.py` | ee3f2e7f (new) | caaa R (1–224); X 41 cases | Assertions at 24–43, 46–90, 93–116, 119–224. | I2, I3 |
| `tools/validate/model.py` | ee3f2e7f (+12) | S ee3f2e7f; caaa R (1–30, 400–511) | Appended field with default; enum and scope validation at 475–482; `Literal` imported (16). | none |
| `tools/validate/runner.py` | ee3f2e7f (+24/−4) | S ee3f2e7f; caaa R (380–709); callers `_run_client` 511–550 and `_run_one` 596–709 | See section 4. | F1, I2 |

Supporting context I also read (unchanged in the window):

- `tools/validate/stack.py` 223–260, 307–332, 442–488
- `tools/validate/clients/api.py` 96–140
- `src/rest_api/core.py` 200–255
- `tests/conftest.py` 20–47, 151–160

A repo-wide grep found no `asdict`/`fields` serialization of `Scenario`.

## 4. Invariants

1. **Appended field compatibility.**
   - `matrix_connection: Literal["ready","disconnected"] = "ready"` is the last
     field (model.py:472). The recorded preflight reports
     `scenario_last_field: matrix_connection`.
   - Positional construction, defaults and every existing scenario are
     unchanged, and `discover()` equality still holds (C2 test:189).
   - Nothing serializes `Scenario` fields, so record and ledger shapes do not
     change.
2. **Declarative guard** (model.py:475–482).
   - Invalid enum values (including `None`) are rejected.
   - `disconnected` requires all of: `targets == ("sim",)`,
     `clients == ("api",)`, `kind == "failure"`, and no writes, setup, cleanup
     or faults.
   - Because it runs in `__post_init__`, `dataclasses.replace` re-validates
     (C2 test:31–33).
3. **Direct runtime guards.**
   - `_refusal` refuses a disconnected scenario on a non-sim target or a
     non-api client before any run (runner.py:553–554). This only changes the
     skip reason text; such scenarios were already skipped through `targets`.
   - `_prepare_sim_matrix` repeats the whole scope check before any HTTP
     (runner.py:472–476). The test proves ordering by calling it with an
     unstarted `ApiClient`, whose `request` would assert (C2 test:42–43;
     api.py:106).
4. **Strict health envelope** (runner.py:477–484).
   - One immediate `GET /api/health`.
   - It requires all of: `status == 200`, a dict body, `success is True`, dict
     `data`, dict `matrix`, `configured is True`, `connected is False`.
     Identity comparisons reject `1`, `"true"`, `0`, `"false"` and `None`.
   - Transport errors propagate from `ApiClient.request`, which has no catch
     around `session.request` (api.py:123). `_run_one` then turns them into a
     blocked outcome (runner.py:704–705).
   - The server always emits real booleans (`core.py:223–224`). The client-side
     strictness is defense in depth.
5. **Scope is the simulator only.** Only the `SimDevice` branch calls the
   helper (runner.py:620–625). The hardware branch is the same text as before
   (626–631, unchanged context in the `ee3f2e7f` diff).
6. **Existing Telnet and external delegation.**
   - `ready` calls the unchanged `_wait_hub_telnet` (451–465). An operator's
     hub (`--hub-url`) is still not waited for (457–458).
   - `if self.stack` on 471 is equivalent to the old `is not None`, because
     `SimStack` defines no `__bool__` or `__len__` (stack.py:442–488).
   - External hubs keep their operator settings: `_scenario_environment_changes`
     returns False when there is no stack (runner.py:429–431). The C1 external
     helper therefore applies `hub_env` itself.
   - Behavior change, intended: an external disconnected scenario now gets a
     real health observation where it previously skipped preparation. My
     external record's procedure shows
     `observe /api/health: … connected=false`.
7. **Writes, setup, cleanup and faults** are excluded by both guards. The
   managed refusal record asserts no `video switch` and no `mutated` log entry,
   and equal state before and after (C2 test:178–179).
8. **Actual side effects (not absolute).**
   - Every simulator scenario is reset before preparation (runner.py:621).
     That includes both blocked controls: their procedures list only
     "reset the simulator to the seed state".
   - Scenario-environment changes restart the managed hub (539–542, 435–440).
     The mixed lifecycle receipt shows 1 simulator and 4 hub launcher handles.
   - Hub data directories and simulator TLS material went to my isolated
     `TEMP`.
   - I make no claim that nothing else on the host changed.
9. **No evidence or schema weakening.** Records validate against the existing
   schema (C1 test:201, C2 test:167). The procedure adds only status and
   booleans. The registry change is append-only, with levels unchanged.

## 5. Counterexamples: assertions vs observed execution

**Observed now** (my focused run at caaa, 54 of 54 passed):

- **C1, disconnected valid inputs** (1, 4, 8, `" 6 "`). Each asserts:
  - exact 503 status and body;
  - int-normalized `switch_all_failed` with `type(...) is int`;
  - unchanged state and the WS contract;
  - five deliberately wrong expectations that must each evaluate `fail`:
    200, success=true, wrong input, `routing_change`, and
    `NoWsEvent(switch_all_failed)` (70–95).
- **C1, six malformed bodies** (range, bool, float, missing, string, extra
  field). Each asserts 503 with no event, no command and no state change, and
  that the registered valid-input oracle fails (100–113).
- **C1, connected control.** A real route to output 1 makes four no-effect
  oracles fail. Connected invalid input returns 400 (116–135).
- **C1, external source runner.** Owned `SimulatorProcess` and `HubProcess`,
  TLS verification true, initial health `connected False`. Result: one
  schema-valid V2 record with all checks passing (188–211).
- **C2, declarations (11).** `skip`, `None`, sim+hardware, hardware, browser,
  api+uc, happy, writes, setup, cleanup, faults (24–33).
- **C2, runtime guards (3).** hardware/api, sim/browser, sim/uc (36–43).
- **C2, strict envelope (21).** 7 literal bodies, 4 `success` values,
  9 `matrix` shapes and HTTP 503. Each also asserts exactly one health call
  (46–77).
- **C2, transport failure (1).** A closed server raises `OSError` (80–90).
- **C2, default delegation (2).** A runner-started hub polls
  `/api/status/cables`; an external hub makes no call; no hub start in either
  case (93–116).
- **C2, managed mixed lifecycle (1).** Real `contracts.cables` (healthy) →
  C1 (disconnected) → `routing.switch_one` (healthy), all `pass/ok`. The
  refusal record has 8 checks: 7 expectations plus `ws_contract_check`
  (runner.py:696–697). Hub env is `OREI_VERIFY_SSL=true` only for C1 (187–202).
- **C2, wrong actual preconditions (2).** Each blocks before the action with
  zero requests (205–224):
  - `ready` with TLS env gives the Telnet timeout;
  - `disconnected` with an empty env, after priming the connection with
    cables, gives "HTTP 200 health".

**Static analysis only:** the before/after diff reasoning in section 4 and the
`SimStack` truthiness equivalence.

**Historical only:** C1's lost managed BLOCKED originals, C2's `focused-01`
(52 passed, 1 failed), C2's managed campaign and the FSEC007 gate. These are
cited from the reports and are not re-observed.

## 6. Behavior and tools: invocations

All runs used the cwd `…/wp-exec-qual-opus55-20261103` at caaa. The tool was
the shared-root venv
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
with Python 3.12.10 and pytest 9.1.1. That interpreter is a tool, not the
sample.

Each invocation used a direct `subprocess.run(argv, cwd, env, stdin=DEVNULL,
capture_output=True)` and recorded `returncode` itself. Nothing was piped
through `tee`/`tail`. The recorder is a one-off private ignored file:
`build/qualification-route-20261103/candidate-opus55/driver/invoke_once.py`,
SHA-256 `4831d299207a927b256283235b1c1679ed351cb934e9796de3619d6a3d4363c8`.

The argv lists equal the packet's `collection_argv` and `focused_argv`, with
these concrete values:

- basetemp: `C:/t/qr-route-20261103/candidate-opus55/<inv>/pytest-temp`, which
  did not exist before the run;
- JUnit: `build/qualification-route-20261103/candidate-opus55/focused-01/focused.junit.xml`;
- `-B` set, no `-I`, both plugins disabled.

Environment:

- `os.environ.copy()`. All of `SYSTEMDRIVE`, `SYSTEMROOT`, `USERPROFILE`,
  `WINDIR`, `COMSPEC`, `PATHEXT`, `PATH`, `PROGRAMDATA`, `APPDATA` and
  `LOCALAPPDATA` were present, checked case-insensitively.
- Overrides, replaced case-insensitively: `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`,
  `MATRIX_CONFIG_DIR` (own data/config), `TEMP`/`TMP` (own native-temp),
  `PYTHONPATH=<checkout>;<checkout>/src`, `PYTHONUTF8=1`,
  `PYTHONIOENCODING=utf-8` and `PYTHONDONTWRITEBYTECODE=1`.
- The only behavior-relevant inherited name was `PYTHONUSERBASE` (value not
  recorded). It has no effect here: the venv has
  `include-system-site-packages = false` and `site.ENABLE_USER_SITE` is False.

Measured effective configuration (preflight, same environment construction):

- `sys.flags`: `dont_write_bytecode=1`, `utf8_mode=1`, `isolated=0`,
  `ignore_environment=0`.
- `sys.path` begins with the checkout and then its `src`.
- `orei_matrix`, `rest_api`, `tools.validate.{model,runner,stack,clients.api}`
  and the C1 scenario module all resolve inside this checkout.
- Every record I produced has source `caaa4faa…` with `dirty: false` and
  `dirty_files: []`.

| Invocation | UTC start → end | Direct rc | Result (from full output / JUnit) | stdout SHA-256 | manifest SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `preflight-01` (packet preflight, `-B -c`) | 19:04:04.627 → 19:04:05.218 | 0 | versions/paths above | `f9891f02…6556` | `926274ca52cb7b730af252c0f7ed7a1e53c356e2f63d7dd59c6c830b7dbc4aad` |
| `collect-01` | 19:04:12.512 → 19:04:13.356 | 0 | **54 collected**, 0 deselected/errors | `5a6865f2…388c` | `011d08c9023baf3e2b17a2e743589002673123204f0089ca5a2e0f3fd6fd0e1e` |
| `focused-01` | 19:04:19.702 → 19:05:15.140 | 0 | `54 passed in 54.87s`; JUnit: tests 54, failures 0, errors 0, skipped 0, time 54.869 | `6f03aa271fee91f561bfdc8f062dc6b1ed5fc9396f39f6c831d025bb2ba974a1` | `53daecd5d00a9ab5ad2d4203245a08611fc438c0e7f403260c29855491930e44` |

- All three stderr files are empty (SHA-256 `e3b0c442…b855`).
- Focused JUnit: 8,433 bytes, SHA-256
  `e2d60dcb54fdb881a18c8ad4779d87b2cccee3f26f5e54e75ae1e57286a0c112`.
- Per-function counts derived from the JUnit: C1 is 4+6+1+1+1 = **13**; C2 is
  11+3+21+1+2+1+2 = **41**. The packet's static D5 expectation of 54 was met,
  not forced.
- Collection created no temp files.
- The focused temp parent holds **173 regular files**, 450,837 bytes, no links:
  35 in native-temp (5 simulator-TLS directories and hub data) and 138 in
  pytest-temp. A hash-verified copy was taken before the next invocation.

Population produced by `focused-01`: **7 evidence records**.

- **F-API-034: 4 records.**
  - 2 are `pass/ok/V2`, each with 8 checks and 1 request: the managed mixed
    lifecycle `69c6a67c…` and the external runner `b27f3267…`.
  - 2 are **blocked/regression**, each with 0 checks and 0 requests: the Telnet
    timeout `61fd0e7b…` and the HTTP-200-health refusal `365189fe…`.
  - The blocked controls are intended negatives. They count toward the
    denominator and are not failures of the run.
- **Other features: 3 records.** `contracts.cables` ×2 and
  `routing.switch_one` ×1, all `pass/ok`.

Process facts:

- Managed receipts list launcher handles with `poll()` codes:
  - mixed lifecycle `552ebb2b…`: simulator plus 4 hubs, all code 1;
  - wrong-ready `d6c4af5d…`: simulator plus 2 hubs, code 1;
  - wrong-disconnected `560833f4…`: simulator plus 2 hubs, code 1.
- External receipt `9cc04404…`: hub 1 and simulator 1, initial health
  `configured True, connected False, telnet_connected False`.
- At 19:06:02Z, `Get-Process` found none of the 13 recorded PIDs. That is a
  bounded observation: PIDs can be reused, and the recorded handles are
  WindowsApps redirector launchers whose interpreter descendants I did not
  observe.
- Code 1 is the number returned under the existing stop helper. It says
  nothing about why a process stopped, and the descendant census remains
  **unknown**.

Checkout effects: `git status --ignored` shows only my ignored build tree, plus
`.claude/settings.local.json`. That file is dated 18:59:02Z, before my first
invocation (19:04:04Z); I did not write it and its origin is not established by
me.

## 7. Findings

**F1 — Low (validation robustness; no product defect; no false pass in the
registered scenario).**

*Claim.* The disconnected precondition is a single point-in-time observation.
It does not establish that the matrix stays disconnected, or that the
disconnection is caused by the declared TLS settings.

*Evidence:*

- `runner.py:477–485` makes one read, which C2 test:75 asserts exactly.
- `HubProcess.wait_ready` deliberately returns before matrix connectivity
  (`stack.py:307–312`, INTAKE:11–13). A freshly (re)started hub can therefore
  report `connected False` briefly.
- C2 AUTHOR:57–63 and INTAKE:96–101 record that this happened in C2
  `focused-01`: preparation saw disconnected, then routing succeeded.
- The negative control at C2 test:212–214 avoids that window by priming with
  `contracts.cables`. That control therefore proves rejection of an
  already-connected hub, not of a misdeclared scenario that runs first after a
  start or restart.

*Consequence.*

- For `sw_api_client_02_c1.switch_all_failed` there is no false pass. With
  `OREI_VERIFY_SSL=true` against the self-signed simulator the link cannot
  come up, and every action-time oracle (503, event, no command, equal state)
  must still pass.
- A future `disconnected` scenario whose disconnection is not durable could
  produce nondeterministic results instead of a clean preparation block. The
  scenario notes (line 31, "under the declared TLS settings") claim more than
  the guard verifies.

*Reproduction.* Not executed: it would need a new or mutated scenario, which is
outside this lease. Statically: declare `matrix_connection="disconnected"`
with no `hub_env` as the first scenario of a managed run. Preparation then
reads startup health once, and the outcome depends on connection timing, as
C2 `focused-01` recorded.

*Direction (not implemented).* Document the point-in-time semantics in the
model docstring, or require a second observation after a bounded settle, before
more disconnected-profile scenarios are added.

**I1 — informational (registry text).** The F-API-034 `basis` still says
"switch_all_failed: V1 … no scenario yet", but `scenarios` now lists
`sw_api_client_02_c1.switch_all_failed`. C1 AUTHOR:218–219 says the basis was
deliberately left unchanged, and no evidence was admitted, so `current: V2`
remains honest. The registry is coordinator-owned. Nothing was changed.

**I2 — informational (coverage).** The scenario-field half of the runtime guard
(runner.py:473–474) cannot be reached through normal construction, because
`__post_init__` already rejects those values. No test executes it; the direct
tests use the valid `SCENARIO` and exercise only the target/client half. This
is defense in depth, not a defect.

**I3 — informational (assertion strength).** C2 test:202 asserts
`len(runner.children) >= 4`. The actual count was 5 (1 simulator + 4 hubs),
which agrees with C2 AUTHOR:75–76. A lower bound would not detect an extra,
unexpected hub restart.

Apart from F1, I found no violations of the invariants in section 4 within the
inspected boundary.

## 8. Calibration

- **FSEC007.** The required global CLI gate failed once (C2 AUTHOR:174–196:
  `F-SEC-007 … level V2 < recorded V3`, exit 1).
  - That is a global evidence-level/freshness gate failure. It does **not**
    demonstrate a product defect, and it does not prove the absence of one.
  - Its onset is unknown.
  - I did not rerun or waive it, and I made no scoped substitute.
- **Lost C1 originals.** These remain **lost** (C1 AUTHOR:225–241, 346–353).
  My focused run is a new, separate observation at caaa. It does not
  reconstruct those originals and is not an original PASS.
- **Prior attempts.** Both Opus 4.7 FAIL dispositions are unchanged. This
  report does not repair either of them.
- **Scope of what I ran.** No V3, image, browser, HA, hardware, LAN, Docker,
  CI, ledger generation, global gate or campaign.
- **Unknowns stay unknown.** Termination cause, descendant census and process
  state outside my receipts are not established. Code 1 is a returned number,
  nothing more.

## 9. Publication labels and limits

- **Tracked at commit:** only this `AUTHOR.md`, in one report-only commit whose
  parent is exactly caaa. Source is untouched.
  - Until that commit, HEAD is caaa and only this report is dirty.
  - Code was unchanged throughout, but the tree as a whole was not clean.
- **Not published:** this report is not task-ref-published until the
  coordinator pushes and verifies remote/local equality.
- **Ignored/private, not shipped or published:**
  - `build/qualification-route-20261103/candidate-opus55/`, holding the
    recorder, the `preflight-01`, `collect-01`, `focused-01` and `docs-01`
    manifests, streams, JUnit and hash-verified temp copies;
  - the original temp parents under `C:/t/qr-route-20261103/candidate-opus55/`.
- **Documentation invocation.** The single final five-module invocation runs
  after this report is finalized, under `docs-01`. Its result appears only in
  the delivery receipt, never in this file.
- **Commit hooks.** The commit uses the invocation-only
  `git -c core.hooksPath=` prose exception. That is not a source-hook or
  full-CI result.
- **Timing.** The target was 15 minutes and is not a cutoff. The worker session
  began at about 18:59Z; that is inferred from a pre-existing checkout file
  timestamp, and the exact start is unknown. The inputs and source were
  reviewed by 19:04Z, the focused run finished at 19:05:15Z, and the report was
  written from about 19:08Z. The total elapsed time and the exact overrun are
  in the delivery receipt.
- **Errors during the session.** One ad-hoc read-only inspection query failed
  on a Windows path separator and was corrected. No test invocation was
  repeated.

```json
{
  "pin": "QUAL-ANTHROPIC-CORE-01",
  "attempt": "replacement-opus55-20261103",
  "candidate_model": "claude-opus-5-5",
  "effort": "high as dispatched; native per-turn effort not observable",
  "candidate_family": "Anthropic",
  "review_base": "938ae30339790c361abdda6fdd01b11a4e498518",
  "candidate_source": "caaa4faabe9ede1e3aed37d2269efd4a4d691e04",
  "commits_reviewed": ["386872316cb60130b06dd704557ae6ca1a92b5c8", "060769b724e7a546b8df22eac82f3b288d9bbbe8", "ee3f2e7f034a9ace64553e942f328dff921a1e04", "caaa4faabe9ede1e3aed37d2269efd4a4d691e04"],
  "paths_reviewed": 9,
  "rubric_sha256": "66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672",
  "final_packet_sha256": "dfd433557c35fb974d346ba869addbaef2fe1e621dbe8e30c77760936f718b74",
  "invocations": {
    "collect": {"returncode": 0, "collected": 54},
    "focused": {"returncode": 0, "junit_tests": 54, "passed": 54, "failures": 0, "errors": 0, "skipped": 0},
    "docs": "single final run after this report; result in delivery receipt only"
  },
  "f_api_034_records": {"total": 4, "pass_ok": 2, "blocked_regression_controls": 2},
  "all_feature_records": 7,
  "findings": [{"id": "F1", "severity": "low"}, {"id": "I1", "severity": "info"}, {"id": "I2", "severity": "info"}, {"id": "I3", "severity": "info"}],
  "product_source_defect_found": false,
  "self_qualification_verdict": null,
  "source_or_release_acceptance": false,
  "unknown": ["termination cause", "descendant census", "exact session start"]
}
```
