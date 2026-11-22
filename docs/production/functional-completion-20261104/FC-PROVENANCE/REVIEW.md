# FC-PROVENANCE: independent different-family factual review

2026-11-04. Reviewer: MiniMax (`opencode2/minimax-coding-plan/MiniMax-M3`, thinking),
underlying family **MiniMax**. Author under review: OpenAI Codex `gpt-6-astra/high`
(Astra). This is a genuine different-family review of an Astra-authored factual
inventory.

**Verdict: PASS** for the factual inventory at exact commit
`4c5c8120a27e41c8666998a6d0faeb6c758cc57b` (parent
`a07cf94211486150fa8222c5aad43ecb9f938bf3`), with one LOW-severity,
non-blocking wording finding (F-1) and three non-blocking refinements (R-1..R-3).
A negative verdict would have been an equally valid successful delivery; none is
required here.

**This review clears no gate.** It is a fidelity review of one prose report. It
awards no model qualification, no domain competence, no judge fit, no source
acceptance, no feature or capability closure, and no release. Q-UI-A, Q-LC-M3
and Q-HA-M3 remain **HELD**; Q-UI-M3 remains **HELD / CONFLICTED AS SCOPED**;
the D6 whole-target hold at `12ad507eb3c0b24bd896b3bf1757d03980d19696` is
unchanged; the original WS `NOT_GRANTED`/WSR-03 disposition, the terminal
Opus and MiniMax privacy FAILs, the C1-C4 privacy chain, and the exhausted
privacy-budget proposal remain exactly as recorded. No owner gate, hardware,
visual, soak, field or artifact gate is waived by this document.

## Reviewer conflict disclosure and the limit of this review

MiniMax is a **subject** of facts in the audited report. The report's
MiniMax-specific assertions include the affirmative MiniMax M3.1 keyboard and
assertion contribution, the Q-UI-M3 same-family conflict, the M3 persistence-to-Sol
handover, the M3 privacy-candidate attempt and its HA diagnostic probes, and the
M3 family/role-unused questions for Q-LC-M3 and Q-HA-M3.

Accordingly:

- I wrote **fidelity checks only**. Where the report asserts something about
  MiniMax, I verified the assertion against the original native/task/Git/source
  records and reported whether the assertion is accurate. I did not decide
  whether MiniMax is eligible for anything.
- I **cannot and do not** self-certify any M3 eligibility, M3 source
  independence for a prospective target, M3 domain-review competence, M3
  judge fit, or M3 product-HA/UI assessment standing. My PASS on an M3-specific
  *fact* is not a clearance of the row that fact feeds.
- The **coordinator, from a non-MiniMax family, must still independently verify
  every M3-specific source/attempt fact** before clearing any M3 entry gate,
  exactly as the adopted notes require. This review does not discharge that.
- Astra appears in the report as a proposed judge for Q-UI-A, Q-LC-M3 and
  Q-HA-M3. I verified that the report **refuses to award Astra** any
  product-HA or real-key/browser-effect judge competence, and that its
  statements about Astra's own record are factually accurate. I award Astra
  nothing. A non-OpenAI factual crosscheck of Astra-specific claims is
  mandatory and this document does not substitute for it.
- I did not read, and will not be influenced by, any other reviewer's future
  decision on this commit.

## Exact inputs under review

| Item | Value | Independent check performed |
| --- | --- | --- |
| Dedicated worktree | `wp-fc26-fc-provenance-review` | directory of this checkout |
| Branch | `review/wp-fc26-fc-provenance-review` | `git rev-parse --abbrev-ref HEAD` |
| HEAD | `4c5c8120a27e41c8666998a6d0faeb6c758cc57b` | `git rev-parse HEAD` |
| Parent | `a07cf94211486150fa8222c5aad43ecb9f938bf3` | `git cat-file -p` |
| Commit scope | one added file, `docs/production/functional-completion-20261104/FC-PROVENANCE/AUDIT.md` (483 lines) | `git diff --stat <parent> HEAD` |
| Report canonical Git LF SHA-256 | `38938a02a275981a93ed359768cfdb1c506e73310869e2c259f54ecfd5128d8e` | recomputed from the checkout and from the author's retained original; **matches** |
| Author retained original | `.../provenance-closeout/report-original.md`, 46829 bytes, same Git LF SHA-256 | recomputed; **matches** |
| Adopted packet | `FINAL_PACKET.json`, 616751 bytes, `933166c3925e38e748bb4b78e15bb488c90e43bb12807b2f02ffd65b7ea6f2f4` | recomputed; **matches** |
| Embedded plan text | `90f8459b050577acb4fd6b55e195288380a1586780dd3eba05accf2159da00bb` | packet field + `FINAL_PLAN.md`; **matches** |
| `CONSENSUS.json` | `75df990e1254d3add958701a08203c84fcbfb6a6640399bb41342eea6565b4ba` | recomputed; **matches** |
| `ADOPTION_NOTES.md` | `c28265cd3e9d71b0ad75cd7448b834c663aac7abfe5df12a207625b804e9e747` | recomputed; **matches** |
| Fixed product P | `9b783d723c81cc56ec86810b789fa31be41e75cc` | exists; ancestor of the reviewed parent |
| Scoped model config | `92207a5a69cbc0f711534664a43e3d397433bab8fbd2290226a32d5e664202f4` | recomputed from the author's retained `.codex/config.toml`; **matches** |

The commit was verified once. No checkout, reset, rebase, cherry-pick, import or
moving-ref follow was performed at any point in this review.

## Independent verification actually performed

Everything below was re-derived from primary records (original native exports,
original task/dispatch records, Git objects at exact commits, the retained
author evidence manifest, the read-only historical roots, and the author's own
completion receipt). Hash and census checks are reported as **identity**, never
as semantic coverage.

### 1. Attempt, outcome and budget history

- The two retained `worker-list` pages were re-read directly. Page 1 holds 100
  rows with `hasMore=true`, page 2 holds 68 rows with `hasMore=false`, `total`
  168, `scope.run = run_37205f6095b3`. The report's "168 rows, page two had
  `hasMore=false`" is **accurate**.
- Every Task/Dispatch/terminal identifier the report names was located in the
  projection, including the author's own `task_a7ee911f3245` /
  `ctx_d6197cc497ff` / `term_cf0879a0-7eb9-4b52-a0b0-a6afc8fc755f`, whose
  projection binds `provider = {id: codex, model: gpt-6-astra}` on the
  `wp-fc26-fc-provenance` worktree. The report's "the live Run projection
  independently binds this Task/Dispatch/tree to `gpt-6-astra`" is **accurate**.
- The M3 persistence handover was re-derived from the projection rows:
  `task_02e6418f9110` carries dispatch `ctx_1d5825e1f726` with
  `dispatchStatus=failed`, `workerState=failed`, and dispatch
  `ctx_cde87530b675` with `dispatchStatus=completed`, `workerState=succeeded`.
  The report's "failed MiniMax Dispatch ... followed by completed continuation"
  is **accurate**. `docs/planning/RUNTIME_EXECUTION.md` independently records
  the M3 attempt settling at `cf7ea7ca` and the fresh Sol 6.1 high continuation
  taking `ctx_cde87530b675` on the same Task.
- The interrupted/continued judge pair was confirmed: `task_3a3a04200302` with
  `ctx_f7db39e6c800` (failed/stopped) and `ctx_5db4e4b62a69` (completed/succeeded),
  matching the report's "one Task ... not two independent judges".
- `task_ae949bd12fff` / `ctx_2caca18359bf` exists and is bound to the
  `wp-fc26-fc-truth` worktree (see R-2).
- Across all 168 rows there is **no** UI-review, full-lifecycle-review or
  product-HA-review assessment worktree: the workspace list contains no such
  candidate/judge tree. This supports the report's bounded negative statement
  that Q-UI-A, Q-LC-M3, Q-HA-M3 and Q-UI-M3 have "no matching launched
  candidate or judge located in the returned Run pages". That statement is
  correctly bounded and is **not** inflated into an all-time absence proof.
- Every report/judgment commit named in the attempts table resolves to a real
  commit whose subject matches the described work, including `97c47be3`
  (candidate evaluation), `5b70c916` (judge), `78eea151` (manual attempt 02
  report), `7548b5b7` (manual attempt 02 judge), `1d49014b` (Opus 5.5 candidate
  evaluation), `dda63d66` (Opus 5.5 judge), `1cc44220` (WS hold), `ed697083`
  and `9817554e` (corrected-component reviews), `1a38e285` / `e8ce3966` (Opus
  privacy candidate/judge), `f3a783b4` / `1b2b7c5f` (MiniMax privacy
  candidate/judge), and the C1-C4 chain `8b9f5623`, `47b0bbb8`, `8fc65e05`,
  `01ca5572`, `53853257`.
- The C1-C4 chain is **not** an ancestor of P (each of the five commits returns
  a non-ancestor result), confirming the report's statement that P "does not
  contain the unaccepted C1-C4 chain".
- `docs/production/remediation-20261104/recovery-execution/D6_PROVENANCE_HOLD.json`
  was read directly: status `HELD / NOT_DISPATCHABLE_AS_SCOPED`, target
  `12ad507eb3c0b24bd896b3bf1757d03980d19696`, `candidate_attempts_launched: 0`,
  `wiring_leases_granted: 0`. The report's D6 row is **accurate**.
- `PRIVACY_REASSESSMENT_BUDGET_REQUEST.json` was read directly: status
  `OWNER_APPROVAL_REQUIRED / proposal only, no worker or attempt launched`,
  proposing exactly one Opus candidate and one Astra judge. The report's
  "still owner-only and unapproved" is **accurate**.
- The qualification-replacement packet's `R3_decision_rule` states
  "exactly three remaining genuine contributions, total 9 including prior 6",
  confirming the report's "nine planning contributions" and its refusal to
  imply extra authorised attempts.

### 2. Native identities and hashes

The report's native-identity table was checked against
`native-identity-checks.json` and, independently, against the retained native
files themselves:

| Native capture | Report claim | Result |
| --- | --- | --- |
| OpenAI Sol C1 | `01a184b2-fc3e-7d60-a462-e29adf1e26a3` / `7adba7a3baae3b7369bf8d52c661b74be67e4f5d9f8f745cac62399f3a026f10` | matches |
| OpenAI Sol C2 | `01a1856e-d431-7221-896e-76233290217e` / `8fe7981661981e22615ba398ab249bbdf33f2021de22a7e41d834e33bcec2e6a` | matches |
| OpenAI Sol C3 | `01a1859e-84ec-7800-8a93-bcb6b40918f9` / `cc5fa61c2d96a112fe5baedc470b3884efb62ecc03570766bef970c742d3a81e` | matches |
| OpenAI Sol C4 | `01a1a62d-5b7d-7282-b691-753a3c38d963` / `3e728f1c9c3d8aaa220e909ddd226f3346e24e1a0948cce281452c2d38f8cdd6` | matches |
| Anthropic original WS author | `2a593a53-f899-407f-a59d-862cd4c8e524` / `62c345ef6af80abe7eb302d868722f90b8895da359fd7bd8c1bad9b5e37a22e6`, 2484777 bytes | matches |
| Anthropic corrected WS author | `48219381-d4ac-4e1a-8cb1-97ddf25364aa` / `98be82696b0ccd8c0d8e6fdf99deb596526b279ca18e051cff457db17ae2bdaf`, 2693249 bytes | matches |
| Opus privacy candidate | `0c330b18-dc20-4251-96a1-82858470f91e` / `f0e087d01dc4e9e44b1a3da29a8fedd8821aaf17d6248d14e7aece80cb7cbdb3`, 2455367 bytes | matches |
| Original WS judge | `01a1a59a-f00e-7853-ae5a-9033ade1c9c1` / `39578c766c54881a1dd4faaf87aae0f3ac7471cabfc7fbba6b722934d6490366` | matches |
| Corrected WS judge | 3080155 bytes / `81eed9e9ede860a7b07645fd7244ea6ea36f6c2fa3cc06a65f884f5586523706` | matches at `recovery-waveB/ws-r01-closeout/native-final-private.jsonl` |
| Opus privacy judge | `01a1a57b-e9d1-7cc3-94ca-2408e2dfac3a` / `956d73d4dd58e1ced7e4762031fe101709fa3316ea055ea70eed251ed65736e0` | matches |
| MiniMax privacy judge | `01a1a67f-592d-7202-b8dc-3e9ffce10f86` / `32427d325377cc258c5604b3160cfd8c0a87230eff33877793af7f84fd159c2b` | matches |
| MiniMax privacy candidate | `ses_e5998016fffe3emviWZx9eKO2h` / `c19d45451cc7eeb4a9041a64ef6457783f58137a7563c8476e68029912827741`, 1642596 bytes | matches; native `info` confirms `MiniMax-M3` / `minimax-coding-plan` / `thinking` |
| Opus 5.5 candidate | `f2d52957-9554-4636-917b-b83780388faa` / `76a5ef49087827f0874bcd8bfdf41586bceb8302e8d08bbedeb7406fc3b533aa`, 2182789 bytes | matches |
| Opus 5.5 Astra judge | `01a1a2d7-348e-75a1-8ff2-cca40f80df34` / `6d0ddf7d31f89fc6003bd4bd5d23388e4ac51d8c89b27cfdfd7309c996f76672`, 1875545 bytes | matches |

The three older API-domain native identities (Opus 4.7 attempt 1 at 1331454
bytes / `136362b6...`, Opus 4.7 manual attempt 2 at 1294061 bytes /
`1538b981...`, and the attempt-2 Astra judge at 1088133 bytes /
`b7e23d43...`) are **not** present in the read-only historical build roots on
this host. Each hash and byte count is independently corroborated by canonical
in-repository records (`QUALIFICATION_DELIVERY.json`,
`QUALIFICATION_MANUAL02_DELIVERY.json`, `QUALIFICATION_MANUAL02_JUDGEMENT_DELIVERY.json`,
`EXECUTION_GATE_STATUS.json`, `HANDOFF.md`, `RUNTIME_EXECUTION.md`). The report
explicitly attributes these to the judgments/dispositions rather than claiming a
fresh read. That attribution is **honest and correctly bounded**.

### 3. The affirmative MiniMax UI conflict (the load-bearing claim)

This is the most consequential assertion in the report, so it was re-derived
from the retained native export rather than accepted from the report.

- The retained `pwa-native-private.json` is 4727230 bytes with SHA-256
  `b7ed172099117b435a92b2951e46f2b178ff5ab2913cb4e4f6701c588a8316f3`
  (**matches** the report), session `ses_eb4819a68ffecboVIwnlsfrd53`
  (**matches**), located in the `wp-e2-pwa-icons-shortcuts` worktree
  (**matches** "bound to the PWA/icons/shortcuts worktree").
- The export has 229 messages; exactly **216** carry a model object, and all
  216 are identical: `{"id": "MiniMax-M3.1-Flash-Preview", "providerID":
  "minimax-coding-plan", "variant": "default"}`. The report's "All 216 messages
  with an actual model object identify ... M3.1-Flash-Preview, variant default"
  is **exact**.
- M3.1 and M3 are both under provider `minimax-coding-plan`; the report's "This
  is M3.1, not M3; both are MiniMax for independence" is **correct**, and no
  harness or variant relabeling is applied.
- The flattened native tool list was re-derived and the claimed indices were
  checked one by one. Entries **39** and **40** are `edit` calls on
  `web/js/components/keyboard-shortcuts.js` whose returned patches add
  `window.overlayStack?.closeTop();` and `window.overlayManager?.closeActive();`
  (the two Escape closers) and the `isTypingTarget` helper respectively;
  **128** is the `write` that creates `tests/test_ui_pwa_icons_shortcuts.py`;
  **137** is the `edit` that rewrites the guard-order assertions; **180** and
  **183** repeat the relevant edits against the earlier file content; and
  **181** has `state.status = "error"` with "Could not find oldString ..." and
  empty output, i.e. an actual failed replacement that is not counted as a
  success. Every one of these entries is carried by a message whose model is
  `MiniMax-M3.1-Flash-Preview`. All reported indices and descriptions are
  **exact**.
- The reported `executed=false` serialization field is real and co-occurs with
  `state.status = "completed"` on the same tool entries. The report's
  disclosure that the raw `executed` field "does not negate completed tool
  status, returned patch, timestamps and matching Git content" is **accurate
  and appropriately hedged**.
- The Git range `94051739ef6e7c1e754dd3264e9d943cb78060cf..9dabcf900051b81990b707d2096da5235ba83913`
  exists and resolves to the single commit "feat(ui): add PWA manifest, icon
  provenance, dynamic api-copy origin, and shortcut input guard (WP-E2 Track 6)".
  Its `web/js/components/keyboard-shortcuts.js` diff contains exactly the two
  Escape closers, the `isTypingTarget` helper, the `target.blur()` call and the
  guard rewrite, and adds the 336-line `tests/test_ui_pwa_icons_shortcuts.py`.
  The native returned patches and the Git diff **agree**.
- Those additions are still present at P: `keyboard-shortcuts.js` at
  `9b783d72` carries the four-closer Escape handler, `isTypingTarget`, the
  `target.blur()` behaviour and the `data-tab="scenes"` click. The keyboard
  guards at P are source-string assertions only
  (`assert guard in shortcuts`, an ordering comparison of `isTypingTarget`
  against `shortcuts.get(id)`, and a parametrized `closer` over
  `overlayStack?.closeTop()`, `overlayManager?.closeActive()` and
  `ContextMenu?.closeAll()`). They therefore do not demonstrate exactly-topmost
  browser behaviour. The report's whole Q-UI-M3 conflict characterisation is
  **verified against the original records** and the HOLD/CONFLICTED disposition
  for that row is correctly held.

**Conclusion on this claim:** the report's Q-UI-M3 conflict finding is
affirmatively established by native evidence, not by trailer absence, and the
report says so explicitly. I concur with the *fact*. I do not and cannot
certify any MiniMax eligibility outcome from it.

### 4. MiniMax persistence handover

- The retained `persistence-native-private.json` is 1797948 bytes with SHA-256
  `9f4c04c264d71403745054790fbfa4b648466b7a192f24852c7467f924b1467c`
  (**matches**), session `ses_eaf0a28a9ffeXuV7XGB2F0ytHO` (**matches**).
- The export has 271 messages; exactly **267** carry a model object and all 267
  are `MiniMax-M3` / `minimax-coding-plan` / `thinking` (**exact**).
- Native tool entry **59** is a `write` with `state.status = "completed"` and
  the returned "Created file successfully: src/hub/persistence/startup.py"
  (**matches** the report's claim).
- Git lineage was re-derived: `cf7ea7ca65f212c3dd30dc40a8f61fa2949414e8` has
  parent `70de5d94ad851585a518100f5c6a4c4afae9161a`; `cf7ea7ca` is an ancestor
  of `168fc032`, which is an ancestor of merge
  `59a2e8eaa4677defbc998a116375d715c1d5945c` (**matches**).
- At P, `src/hub/runtime/composition.py` imports
  `hub.persistence.startup.prepare_runtime_storage` and calls it inside
  `build_runtime` at lines 640-658 (**matches**). `startup.py` at P still
  carries the `PersistencePaths` and `PreparedPersistence` dataclasses
  introduced at `cf7ea7ca`, and the file shows large later divergence
  (282 insertions / 652 deletions between `cf7ea7ca` and P), consistent with
  "later substantial Sol corrections are also visible".
- The report's restraint — that it did **not** establish a per-hunk native
  mapping for the whole handed-over package, did not label the package
  all-OpenAI, and did not declare MiniMax contribution-free — is **correct and
  matches the evidence**.

### 5. Historical Anthropic WS/runtime/HA contributions

The five historical native child files were hashed directly in the Claude
profile tree, and the parent transcript was hashed directly:

| Native child | Report SHA-256 | Result |
| --- | --- | --- |
| `agent-a992bfdfcc75664de` | `0c0dc8b2ac0c2d5ad7665b7badf36219f3cf55e809ab14d9478195a74b6113a1` | matches (6313748 bytes) |
| `agent-aec2fb3cf98fc0c89` | `6762d3d1bb58c81dcada8aebe0beda28ef83217da653a4733974021f8f13fd14` | matches (2042224 bytes) |
| `agent-a9a94a39d74b48479` | `829f5f50ac1a56b137df875fc2bc4fb33297947899a8fc2c4ecd304c3cf51925` | matches (3713607 bytes) |
| `agent-aa108be869fb0a569` | `88c415bff69caf3a8517ae58055f21b60c8c0f904c2ab4e93d6bb5365286f8eb` | matches (1880473 bytes) |
| `agent-a2b493849a07414d3` | `6ca764602d60faf852275974d00c8a65849cc4c82e181598d8a53ee15ff26e24` | matches (33292796 bytes) |
| parent `5737f4ac-eccf-432c-83bc-2593fb3ea078` | `fc7967bab7c23e94bf0ffec4c5fddf8c77b932b503342c137d6d6b964c69a60f` | matches (23417884 bytes) |

The two strongest equality claims were re-derived from the native Write
payloads rather than from the report:

- Native Opus 5.5 `Write` at JSONL line 503 for `src/rest_api/websocket.py`
  has an LF-normalised SHA-256 of
  `358fc6575ec926af2a5198e0bfeed4ff1342a4dd3b8761b9c3b09b804ddb0b87`, which is
  **byte-for-byte the same value** as the Git-LF SHA-256 of
  `src/rest_api/websocket.py` at commit `323af8e4`. The report's "exactly
  equals" claim is **verified**, not asserted.
- Native Opus 5.5 `Write` at JSONL line 235 for `src/rest_api/runtime.py` has
  an LF-normalised SHA-256 of
  `28e40e075f6fae0ebfde62dd2d742b62ee62da35f0d76e08e6736b89e98dec43`, which is
  **byte-for-byte the same value** as the Git-LF SHA-256 of
  `src/rest_api/runtime.py` at commit `bc3b9353`. The adjacent native `Edit`
  calls at lines 239/242 on `src/rest_api/app.py` do contain
  `install_runtime_monitor`, confirming "Adjacent native edits add app
  runtime-monitor installation".
- Native Opus 5.5 `Write` at JSONL line 312 creates
  `custom_components/hdmi_matrix/config_flow.py` with LF SHA-256
  `517650b3e161739972b4ebe452fd87af670517a89cc65fcc640403d53615744b`, which is
  **different** from the Git-LF SHA-256 of the final
  `0f7372d8df31af2242eebe55947619c32fa91dd8` blob
  (`073f2d7f3140fc90847a4b55a0883d159f3a680f2190c8f10dc226b8c6b0db63`). The
  final blob adds `format_mac`, a `_MAC` pattern and `is_mac`, and adjusts
  `_probe`/identity handling. The report's "NOT byte-identical to final ...
  the inspected difference adds MAC detection and adjusts probe/identity
  handling" is **accurate**.
- `agent-aa108be869fb0a569` does contain `tools/gen_contract_fixtures.py`
  (fixture generator) and `tests/ha/test_config_flow.py` writes;
  `agent-a2b493849a07414d3` does contain `tests/e2e/flows.spec.ts` (browser
  flow assertions) and `tests/sim/test_sim_status_broadcast.py` writes. Both
  described characterisations are **accurate**, and the report correctly
  refuses to treat them as final-integration lineage proof.

### 6. Historical unknowns

- `47fc33cecb94e0def6c10c8e51b4799735a8008e` = "Initial commit: 8x8 HDMI Matrix
  Hub"; `896856096e29677ec197ce4939350fcb4d33ed41` = "Add two-level API access
  and browser request guards" with parent
  `3821fff6f143858732beb2006f22362445d21ed0`; and
  `725ef268388a45ba72ce249f08a2120ede73f744` = "feat(rest-api): wire all Phase
  7 routes in create_rest_app" all resolve as the report describes. The
  report's **unresolved** attribution for these, its statement that "Sisyphus
  is not a model family", and its refusal to infer non-Anthropic or non-MiniMax
  authorship from the earlier no-Anthropic routing era or from missing trailers
  are **correct and appropriately held as bounded unknowns**.

### 7. Source and behavioural statements at fixed product P

Every consequential source statement in the report was re-read at
`9b783d72`. All are **accurate**:

- `_handle_command` allocates each `get_status` reply into the module-global
  `_replies: set[asyncio.Task[None]]`, and the websocket `finally` block removes
  only `ws_clients.discard(ws)` and `await stream.remove_client(ws)` — the
  socket does not drain `_replies`. Accurate.
- `EventStream.refresh` awaits `self.runtime.refresh(force_refresh=True)` when a
  runtime is present and otherwise falls through to the compatibility
  `poll_once`/`_poll_lock` path. Accurate.
- `RestApiServer.stop` awaits `self.app["event_stream"].stop()` before
  `self.runner.cleanup()`. Accurate.
- The accepted component `src/rest_api/ws_request_work.py` is **unwired** at P:
  no product module imports it, and
  `tests/test_ws_request_work.py::test_the_existing_websocket_module_does_not_use_the_component_yet`
  explicitly asserts `"ws_request_work" not in source` and
  `"_replies.add(task)" in source`. The report's "the test explicitly asserts
  it is not installed in the handler yet" is **exact**.
- The component `_drain` counts in-progress admissions via `reserved()` and
  reports truthful `remaining` work. Accurate.
- HA `_probe` uses `async_get_clientsession(self.hass)` (the shared session);
  the options flow calls `async_create_entry(data=user_input)` directly; and
  setup selects `self.config_entry.options.get(CONF_API_KEY, ...data.get(...))`,
  i.e. options key before data key. All three **accurate**.
- `tests/ha/test_config_flow.py` asserts that transmitted requests carry
  `X-API-Key`; it contains no invalid-key-rejection-on-a-locked-real-hub case.
  The report's "assert transmitted `X-API-Key` but do not demonstrate rejection
  of an invalid key on a locked real hub" is **accurate**.
- `keyboard-shortcuts.js` calls the legacy `window.settingsPanel.toggle()`,
  selects `[data-tab="scenes"]`, registers the literal `'?'` while the
  `parseKey`/`keyToId` lookup is Shift-aware, and invokes four Escape closers
  (`overlayStack.closeTop`, `overlayManager.closeActive`, `ContextMenu.closeAll`,
  `hideHelp`). `unified-settings-drawer.js` maps the `general` section to
  `globalKey: 'generalDrawer'`. All **accurate**.
- The report's claimed read windows line up with the real file at P:
  `_drain` 218, `WorkOwner` 248, `try_start` 283 (window 181-350); the unwired
  guard at 871 and the import-resolution test at 864 (window 841-955);
  `EventStream.stop` 260, `refresh` 313, `poll_once` 321 (window 221-375);
  `create_rest_app` 238 (window 221-360). Accurate.

### 8. Negative controls and original receipts

- `C:/t/remediation-privacy-judge/gap01/gap-results.json` was read directly: it
  records `current_pin_masked: false`, `pin_positive_control_masked: true`,
  and in both the `matched` and `mismatched` cases `wire_body_unchanged: true`
  and `raw_body_capture_identity: true`. The report's characterisation is
  **exact**.
- `C:/t/remediation-recovery/priv-m3-judge/j03-writer-negative/receipt.json`
  records `direct_child_exit: 1`. The report's "writer-negative original exits 1"
  is **exact**.
- `C:/t/remediation-ws-review/02-gap-probes/` exists with `manifest.json`,
  `stdout.txt` and `stderr.txt` at the paths the report names.
- The report explicitly states it did not execute those probes itself and that
  the controls are evidence of report reasoning, not a new privacy gate run.
  That separation is **correct** and is the difference between a negative
  control and a new assessment.

### 9. Published R1/R2 judge inputs

All six canonical Git-LF hashes in the report's judge-input manifest were
recomputed and **match exactly**: R1 OpenAI `57a634bc...`, R1 Anthropic
`efe8219c...`, R1 MiniMax `42bd1888...`, R2 OpenAI `d63a3e51...`, R2 Anthropic
`5c8615b0...`, R2 MiniMax `a881fd04...`. The report's framing — "an input
manifest, not a claim that this audit reread all six in full", "Known findings
alone cannot earn PASS; discovering a novel bug is not required" — is the
correct protocol and matches the adopted notes.

### 10. Staffing rows and held-gate precision

The packet's `staffing` array was parsed and contains exactly **ten** rows,
matching the report's ten-row table one for one (FC-TRUTH, FC-PROVENANCE,
Q-UI-A, Q-LC-M3, Q-HA-M3, FC-UI-KEYS, FC-HA-AUTH, FC-WS-WIRE, FC-SUPPORT-RUN,
FC-UI-REPRO), with the same author/reviewer pairs, bases, entry gates and
acceptance text. The packet's `routes` confirm the family bindings the report
relies on: Sol and Astra are OpenAI, Opus is Anthropic, M3 is MiniMax
(`minimax-coding-plan/MiniMax-M3`, variant `thinking`).

Each held row's stated missing proof is stated as a **missing proof**, not as a
finding of incompetence, and each is consistent with the underlying records:

- Q-UI-A HELD — no prior formal Opus UI-review assessment located (consistent
  with the 168-row projection and with the historical UI contributors the
  report lists); Astra UI judge fit not established.
- Q-LC-M3 HELD — no prior formal full-lifecycle review assessment located;
  M3 persistence/native contributions must be reconciled; D6 not discharged.
- Q-HA-M3 HELD — the prior M3 HA work was a **privacy diagnostic probe**, not a
  product-HA review PASS; exact HA/security/fixture independence and unused
  role unproved.
- Q-UI-M3 HELD / CONFLICTED AS SCOPED — the affirmative M3.1 contribution
  verified in section 3.

The report's precision on the gates is good: it does not convert a missing
proof into a competence verdict, does not narrow a target to manufacture
independence, does not relabel a harness variant as a new family, and does not
treat the known R1/R2 findings as assessment credit.

## Findings

| ID | Severity | Source | Evidence | Impact | Actual necessary correction |
| --- | --- | --- | --- | --- | --- |
| F-1 | LOW | `AUDIT.md` line 255-256: "No Task/Dispatch pair was established for this older PWA session; `task_supervisor` is a tool name, not an invented Task ID." | In `pwa-native-private.json`, `task_supervisor` occurs exactly once, and only as a substring of the repository filename `test_task_supervisor.py` inside a directory listing produced by a `bash`/`shell` call. The session's actual tool names are `bash`, `edit`, `grep`, `read`, `shell`, `write`; there is no `task_supervisor` tool. The native contains **no** `task_*` or `ctx_*` identifier at all, and the 68-row session list contains no `task_supervisor` row. | The operative assertion in the same sentence — that no Task/Dispatch pair was established and that `task_supervisor` is **not** an invented Task ID — is **correct and independently confirmed**. Only the descriptive aside misidentifies what the string is. No attribution, attempt, outcome, gate, hold, correction reserve, budget or conclusion changes. | Reword the aside to state that `task_supervisor` is a repository **test-file name** (`tests/test_task_supervisor.py`) seen in a directory listing and is likewise not a Task ID. One sentence; no other change. |

F-1 is below the threshold for `REQUIRE_CHANGES` on this report because it is a
non-decision-affecting descriptive aside inside an anti-fabrication disclosure
whose protective conclusion is correct, and because the reserved correction
budget is for a material correction. The coordinator may still fold the one-line
wording fix into any future prose revision of that file without consuming the
reserved author-fix/rereview cycle; this review does not require it.

### Non-blocking refinements (optional, no correction reserve consumed)

- **R-1.** The report's Q-UI-M3 conflict paragraph would be easier to audit if
  it named the exact Git range whose diff it compared against the native
  patches. The range is in fact stated (`94051739... .. 9dabcf90...`) and is
  correct; no change is needed.
- **R-2.** The sentence "The current independent inventory Task is
  `task_ae949bd12fff/ctx_2caca18359bf`" is accurate but easy to misread as the
  FC-PROVENANCE reviewer. That Task is bound to the **FC-TRUTH** worktree
  (`wp-fc26-fc-truth`). Naming the row explicitly would remove the ambiguity.
  This review's own Task/Dispatch is `task_64e1d8cb5db6` / `ctx_f509f51a7c49`
  and is not referenced by the audited report, which is correct — the report
  was written before this review was dispatched.
- **R-3.** The report's attempts table gives a source window for the API-domain
  rows but not for every row. Adding the window to the remaining rows would
  make each row independently checkable without cross-referencing the packet.
  Not required; the current references resolve.

## Covered and unread limits of this review

**Semantically read in full by this reviewer:** the audited `AUDIT.md`
(483 lines); `FINAL_PACKET.json` (parsed; staffing, routes, rubric, assessment
rule, frozen inputs, six-axis rubric); `CONSENSUS.json`; `ADOPTION_NOTES.md`;
`FINAL_PLAN.md` hash; `D6_PROVENANCE_HOLD.json`;
`PRIVACY_REASSESSMENT_BUDGET_REQUEST.json`; the retained author's
`author-completion-original.json` and `retained-author-evidence-manifest-private.json`;
the retained PWA and persistence native exports at the level of message model
objects, tool entries, per-entry status/error/target and returned patch content;
the retained `workers-page1/2-private.json` projection rows and the retained
`native-identity-checks.json`; the derived historical native child selections
for the five Anthropic children and the parent session; the retained
`gap-results.json`, the `j03-writer-negative` receipt and the
`02-gap-probes` directory; and, at P, `src/rest_api/websocket.py`,
`src/rest_api/events.py`, `src/rest_api/app.py`,
`src/rest_api/ws_request_work.py`, `tests/test_ws_request_work.py`,
`custom_components/hdmi_matrix/config_flow.py`,
`tests/ha/test_config_flow.py`, `web/js/components/keyboard-shortcuts.js`,
`web/js/components/unified-settings-drawer.js` and
`tests/test_ui_pwa_icons_shortcuts.py`.

**Verified by identity/hash only, and therefore credited as identity only:** the
Opus 4.7 and Opus 5.5 API-domain native byte counts and digests (corroborated
by canonical in-repository records, not by a local original on this host); the
C1-C4 native originals in the root-private `privacy-assessment/` and
`recovery-source-waveA/` trees, whose digests were matched against the
author's derived identity table rather than re-read semantically; the R1/R2
report digests; the author's own once-only docs run (its JUnit digest
`5c50585e1300d8101e97f3615719cf96557823945ca753ed0148e7b071dfb499` was
independently recomputed from the retained `junit.xml`, and its 489/0/0/0
summary and exit 0 were confirmed, but I did not re-run the author's run and
did not re-read its 489 test bodies).

**Not read by this reviewer:** the full original Opus and MiniMax privacy
judgement reports beyond their cited receipts; the full C1-C4 source chain
beyond the changed hunks the report cites; every historical archive member and
every old child process; whole historical native sessions other than the five
Anthropic children and the one parent transcript; all six published R1/R2
reports in full; every WS assertion, the full runtime, all HA fixtures and
security branches, and every UI caller/overlay test. None of these were
credited to the report by this review, and the report does not claim them.

**Explicitly not done:** I did not read or anticipate any other reviewer's
decision on this commit; I did not read other workers' inboxes or consume any
Orca resource; I did not launch a helper, subagent, model, candidate, judge or
assessment; I did not touch credential stores, provider configuration or
account state; I did not contact DeepSeek; I did not modify any source, test,
contract, registry, ledger, manifest, lockfile, baseline or the author report.

## Checks performed by this review

The five existing documentation modules were run **ONCE** in this review
checkout with the absolute root-venv interpreter and `-B`:

```
C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -B -m pytest \
  tests/test_core_documentation.py tests/test_client_guides_docs.py \
  tests/test_openapi_and_config_docs.py tests/test_security_docs.py \
  tests/test_license_and_protocol_docs.py \
  -p no:tests.route_inventory -p no:cacheprovider -p fc_review_observer \
  --basetemp <owned payload>/basetemp --junitxml <owned payload>/junit.xml -q --tb=short
```

The Windows environment was inherited and then overlaid with **fresh owned**
data/config/TEMP/TMP/TMPDIR/basetemp/JUnit paths, all inside this task's
registered agent-storage payload
(`C:\Users\ryanh\.local\state\agent-storage\artifacts\7568c4290b8f486695b9acf4104ea817\payload`).

The once-only run's actual result: direct exit **0**, stdout
`489 passed in 3.28s`, stderr empty, JUnit **489** tests with **0** failures,
**0** errors, **0** skips and no non-passing case. Per-module case counts taken
from that run's own JUnit classnames are `tests.test_client_guides_docs` 310,
`tests.test_license_and_protocol_docs` 76, `tests.test_core_documentation` 49,
`tests.test_security_docs` 38 and `tests.test_openapi_and_config_docs` 16,
which confirms all five modules executed rather than being silently skipped.

An owned observer plugin ran inside that invocation. Its `collection_finish`
and `session_finish` phases both wrote to the same owned path, so the surviving
observer payload is the `session_finish` one: it holds **43** in-run project-module
origins, and every one of them resolves inside this review checkout (none
points outside it). The collected test-module origin list was overwritten in
place by that same run, so test-module origin is instead derived from the
run's own JUnit classnames together with the recorded cwd and argv. **No
module was re-executed** to recover it.

The authoritative receipt — direct argv, cwd, UTC window, environment policy
and safe-environment record, direct exit code, full stdout and stderr bytes
with digests, the JUnit summary with any non-passing cases, the observer
payload, and an ordinary/hidden inventory limited to this task's own run root —
is written to
`C:\Users\ryanh\.local\state\agent-storage\artifacts\7568c4290b8f486695b9acf4104ea817\payload\runs\docs-review-01\receipt.json`.
No global TEMP crawl was performed and no host-wide write or storage claim is
made. The route-inventory and cache-provider plugins were disabled; no
canonical ledger generation, route coverage check, core source hook or
qualification campaign was run, and no unchanged failed test was retried.

These modules exercise this checkout's product and project documentation. They
do **not** prove that this Markdown was parsed, and they establish no feature,
source, model, route or qualification outcome. None of the five modules reads
this file, so the once-only run's coverage claim is unaffected by the single
post-run prose amendment made above to describe the observer output precisely;
the post-run strict checks were re-run afterwards and cover the final bytes
delivered in this commit.

Strict UTF-8 decoding, local-target link resolution, CR-aware whitespace
(`git -c core.whitespace=cr-at-eol diff --check`) and exclusive staged-scope
checks were run against this file and the resulting commit scope, which contains
**only** the new `docs/production/functional-completion-20261104/FC-PROVENANCE/REVIEW.md`.
No repository configuration was changed; the checkout's existing
`core.hooksPath` was left untouched, so no invocation-only empty-hook exception
was needed. No source hook was run or claimed.

## Storage, custody and limits of this review's own output

This review used registered agent-storage payload
`7568c4290b8f486695b9acf4104ea817` under
`C:\Users\ryanh\.local\state\agent-storage\artifacts\7568c4290b8f486695b9acf4104ea817\payload`.
All new temporary scripts, receipts, private copies, test temporaries and logs
were written there. No workspace, toolchain, build tree, dependency tree or
whole project was copied into the payload. The author's original roots, the
read-only historical roots, the retained native originals, the author's worktree
and the coordinator's registered closeout payload were treated as read-only and
were neither moved, deleted nor pruned. No Orca workspace or branch cleanup and
no cache deletion was performed or attempted. The final storage receipt with
byte counts, retention reason, review date, quarantine state, actually-removed
bytes and outputs left outside the payload is delivered with this review's
completion receipt; the payload is retained rather than completed, because it
holds the required review evidence.

## Disposition

**PASS** for the factual inventory at
`4c5c8120a27e41c8666998a6d0faeb6c758cc57b`. The report's attempt/outcome
inventory, native identity table, source-contribution findings, MiniMax M3.1 UI
conflict, MiniMax persistence handover, historical-unknown holds, ten staffing
rows, negative-control records, R1/R2 judge-input manifest and held-gate
dispositions are **factually accurate as written**, within the read limits the
report itself declares.

The single LOW-severity wording finding (F-1) and refinements R-1..R-3 are
recorded for the coordinator's discretion; none consumes the reserved
one-author-fix/one-rereview budget, and no correction, retake, extra judge or
new attempt is recommended or authorised here.

The coordinator — from a non-MiniMax family — must still independently verify
every MiniMax-specific source and attempt fact before clearing any MiniMax
entry gate, and a non-OpenAI crosscheck of every Astra-specific claim remains
required. All four prospective gates stay HELD, D6 stays unchanged, and no
feature, capability, model, competence, source, budget, hardware, visual, soak,
field or release gate is advanced by this document.
