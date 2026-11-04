# functional-completion-20261104 — Round 3 same-packet final decision (MiniMax)

**Verdict: ACCEPT** — for exactly `933166c3925e38e748bb4b78e15bb488c90e43bb12807b2f02ffd65b7ea6f2f4`.

**Route:** `opencode2` / `minimax-coding-plan/MiniMax-M3` / thinking inherited / CLI effort
override unsupported. **Family:** MiniMax. Task `task_e486754b791b`, Dispatch
`ctx_1cd734915060`, worker terminal `term_a51fe753-e0d3-4708-a429-e112a83d364c`,
coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`.

This is **one** R3 decision on **one** hashed complete plan/staffing packet. It is
not source implementation, not a qualification attempt, not a retake, not an extra
judge, not a budget request, not an owner approval, not a source/evidence/hardware
acceptance and not a primary review. I accept the *conditional programme*: every
source, evidence, owner, visual, physical, soak, field and release gate stays open
exactly as recorded, and no gate is waived by this vote.

---

## 0. Exact bindings and digests (recomputed by me from raw Git blob bytes)

| Object | Exact value | My verification |
| --- | --- | --- |
| `wp-runtime-completion` | **resolved once at entry** → `13859c334238ea0353c9c7b844771cb3dfb8bdee` | local `refs/heads/wp-runtime-completion` == `refs/remotes/origin/wp-runtime-completion` == the integration worktree HEAD at entry. **Not re-resolved afterwards.** |
| Packet | `docs/agent-process/phases/functional-completion-20261104/FINAL_PACKET.json` at that SHA | blob `812004961079d68e24194052d2141fbc64945f17`, 616 751 bytes |
| Packet canonical Git-LF SHA-256 | `933166c3925e38e748bb4b78e15bb488c90e43bb12807b2f02ffd65b7ea6f2f4` | **MATCH** (recomputed over the raw blob bytes) |
| `complete_final_plan_text_sha256` | `90f8459b050577acb4fd6b55e195288380a1586780dd3eba05accf2159da00bb` | **MATCH** — UTF-8 of the decoded string, 13 195 bytes, LF only, trailing newline present |
| `FINAL_PLAN.md` at the same SHA | blob `4a99566aee4c76f5dbba1de2a8db3745fb08dd91`, 13 195 bytes | SHA-256 `90f8459b…da00bb` — **byte-identical** to `complete_final_plan_text` |
| Own base (report parent) | `e6f8df9a9c6e0f347d35b9230f30c01c3fdded4c`, parent `32f911a576de0251b06e77a46a39681c7d7dc679` | `planning/remediation-recovery-r1-minimax`, worktree clean at entry, local head == `origin` head |
| Product source baseline | `9b783d723c81cc56ec86810b789fa31be41e75cc` | ancestor of the resolved head; every source statement below is read at this SHA |
| Accepted (unwired) WS component | `e54228c0e3a9451f39b27caeef6aa77e1e1fa59a` | ancestor of `9b783d72`; `src/rest_api/ws_request_work.py` blob is `145845f493627c98bdf37bc7a6028798b014dd7c` **at both** — byte-identical, unchanged since acceptance |

**Extraction honesty.** My first attempt to hash the packet used a PowerShell `>`
redirection, which merged/converted the byte stream and produced a *wrong* digest
(`0a15324f…`). I discarded that method and re-extracted every blob byte-exactly via
`git cat-file blob` into a `Process` stdout stream, and the digest became the
expected `933166c…`. The failed method is recorded rather than hidden.

### All three complete R2 originals — re-read in full at the packet's exact commit/path/hash

| Report | Family | Head | Parent | Sole report path | SHA-256 (my recomputation) |
| --- | --- | --- | --- | --- | --- |
| `openai.md` | OpenAI | `ddd04f78d7da37ee1d0ae0d84cefdf5745684228` | `7baf8262976772ed3de6eac7a19d5fafc7b5a1b8` | `…/round2/openai.md` | `d63a3e51805ef057b965054ffe51bb7b4098b7314ac51aa7e369bf18696f383e` — **MATCH** (48 551 bytes) |
| `anthropic.md` | Anthropic | `5ab8653dc1d0f7bf3807e500945b76b888061779` | `4ae498baa200cf17f90430f6961c8f1fecd2b8d1` | `…/round2/anthropic.md` | `5c8615b0d5deb6bc23298b52c33dd4d0fab4e2a17213066e78ba56f0ff53d046` — **MATCH** (45 150 bytes) |
| `minimax.md` (mine) | MiniMax | `e6f8df9a9c6e0f347d35b9230f30c01c3fdded4c` | `32f911a576de0251b06e77a46a39681c7d7dc679` | `…/round2/minimax.md` | `a881fd045d30519676a7dc0cc0047a059a60693b57e81fa353e5dda9570c5b67` — **MATCH** (65 851 bytes) |

Each of the three commits contains **exactly one** `round2/` path (its own report) —
I verified the tree, so no report was silently merged or rewritten. All three were
read end to end in this round (OpenAI 168 lines, Anthropic 310 lines, MiniMax 765
lines), not sampled. My own R2 is the parent of this report; R1 inputs and the
recovery history are untouched.

**Moving-ref discipline and peer-decision isolation.** After resolving the
integration once at entry I did **not** re-resolve it. A later read-only
publication-integrity check (`git ls-remote`) showed the remote integration ref had
advanced to `764c2bef…`; I did **not** read that commit's content and did not follow
it. I did verify one thing about it, because it bears on whether my vote is on
current bytes: the `FINAL_PACKET.json` blob at `764c2bef…` is **identical**
(`812004961079d68e24194052d2141fbc64945f17`) to the blob at `13859c33…`, so the
packet I judged is the packet in force. During a repository-wide
`git log --all --oneline` inventory I incidentally saw the **subject lines** of the
peers' R3 branch tips; I opened no peer R3 report and took **no** decision input from
those lines. I did not and do not know the peers' R3 verdicts; this document is my
decision alone and claims nothing about theirs.

---

## 1. What I read this round, and what that limits

Read **semantically, in bounded chunks, at `9b783d72…`** unless stated:

- **WS:** `src/rest_api/websocket.py` (all 124 lines); `src/rest_api/ws_request_work.py`
  (the 519-line component — module docstring, `RejectReason`, `DrainReport`,
  `WorkOwner.try_start/close/aclose`, `WsRequestWork.open_owner/begin_shutdown/
  shutdown`, the *Wiring (proposed)* section); `src/rest_api/events.py` (client
  registry, `remove_client`, `send`, `publish`, `_send`/`_drop`, `refresh`,
  `poll_once`, `QUEUE_LIMIT = 256`); `src/rest_api/app.py` (`create_rest_app`,
  `RestApiServer.start/stop`); `src/hub/runtime/composition.py` (`operation`,
  `command`, `protocol`, `refresh`, `stop`/`_stop`); `src/rest_api/security.py`
  (`api_key_valid`, `access_level`, `session_level`, `remembered`,
  `security_middleware`, `auth_status`).
- **HA:** `custom_components/hdmi_matrix/{api,config_flow,__init__,coordinator}.py`.
- **UI:** `web/js/components/{keyboard-shortcuts,unified-settings-drawer,
  settings-drawer,settings-panel,side-nav-drawer}.js`; `web/js/app.js` (tab
  rendering, `components.settingsPanel`); `web/js/core/ws.js` (requestStatus).
- **Contracts/metadata:** `docs/api/WEBSOCKET.md` (message table, the `error`
  reply row, the REST-status table); `docs/api/websocket.schema.json` (presence);
  `docs/validation/features.yaml` (parsed in full).
- **Callers:** `tools/validate/runner.py::sync`.
- **Records (at `9b783d72…`):**
  `docs/production/remediation-20261104/recovery-execution/{D6_PROVENANCE_HOLD,
  PRIVACY_REASSESSMENT_BUDGET_REQUEST}.json`; the WS component intake record and
  the WS-C01 delivery record; the `QUAL-ANTHROPIC-CORE-01` coordinator dispositions
  (Opus 4.7 FAIL, manual attempt 2 FAIL, Opus 5.5 bounded PASS with its
  `not_granted` list).
- **Policy and phase records** (these are *not* product source; they were read at
  the resolved integration SHA `13859c33…`, because the phase packet tree and the
  updated policy/ledger state do not exist at the product baseline): root
  `AGENTS.md`, `docs/ORCHESTRATION_PROTOCOL.md` (model discovery, quota preflight,
  ownership, independent review/qualification, worker lifecycle),
  `docs/agent-process/PROTOCOL.md`, `docs/agent-process/REPO_CONFIG.json` (both the
  adopted-copy and the integration copy), `docs/production/AGENT_ALLOCATION.md`
  (tail at my own base `e6f8df9a…`), the R2/R3 preflight and dispatch records, and
  `docs/agent-process/phases/functional-completion-20261104/tasks/R3_minimax.md`
  (my own spec).
- **Primary source:** upstream Home Assistant `2025.1.0` `pyproject.toml`, fetched
  read-only, for the Python floor (§3.6).

**Named limits — honest, not cosmetic.** I did **not** read
`tests/test_ws_request_work.py` bodies, the ~1 500-line focused WS test corpus, the
full 4 647-line allocation ledger, every one of the 61 parser-open register rows,
`tools/validate/evidence.py`'s `redact` implementation, the whole
`REMEDIATION_PLAN.json` feature-contract file, or every per-feature acceptance
record under `FEATURE_CONTRACTS.json`. I did **not** execute product code, a
project test, a runtime/canonical campaign, ledger generation or a source hook; the
only execution is the single scoped documentation run in §8. **Hashes are identity,
not comprehension** — every conclusion below rests on the reads named here.

---

## 2. Route, native visibility and worker discipline

The coordinator assigned `opencode2` with model `minimax-coding-plan/MiniMax-M3`,
effort "unsupported; thinking inherited". That is what the harness reports; it is
**not** a backend attestation of model identity, of the underlying family, or of the
effort actually applied. `native_final` bytes for this dispatch are the
coordinator's to collect; I make **no** independent family-identity claim, and my
vote does not rest on one.

I used no helper, subagent, team, alternate model, plugin, MCP server or nested
worker. No default scratch directory, no fixed overwrite, no global configuration
change, no account, no spend, no credential. **DeepSeek was not dispatched and no
credit was bought.** Source, tests, prior reports, scoped model configuration, root
and private runtime data, visual baselines and coordinator-owned paths were read
only. The untracked `.codex/config.toml` remains unstaged.

**Owned roots (the only places I wrote):** the new tracked report
`docs/agent-process/phases/functional-completion-20261104/round3/minimax.md`; ignored
`build/remediation-functional-20261104/minimax-r3/**` (`.gitignore:7 build/`); and
fresh `C:/t/remediation-functional/minimax-r3/**`.

---

## 3. Material decisions — evidence-backed assessment

### 3.1 WS response policy (packet Decision 4): ACCEPT

I checked the policy against the source rather than against the peer preference, and
the packet's hybrid is the only one of the three candidate policies that satisfies
every documented invariant at once.

Source facts I re-verified:

- `src/rest_api/websocket.py:29,107-109` — the current handler creates one
  `ws_get_status` task **per frame** into a **module-global** `_replies` set; the
  component is imported nowhere in `src/` (grep at `9b783d72`: only
  `ws_request_work.py` itself matches). The component is genuinely accepted and
  genuinely unwired.
- `docs/api/WEBSOCKET.md:26` promises `status` **"after a fresh read of the matrix
  (status caches bypassed)"**, and `:88` reserves the `error` event for exactly
  three triggers: invalid JSON, unknown command, or `get_status` when the hub cannot
  read the matrix. A busy rejection is therefore a **new documented trigger**, and
  reusing `"Matrix status not available"` would misreport admission as a matrix read
  failure. Decision 4's "distinct documented busy error" plus "documented in the
  coordinator-owned contract in the same reviewed candidate" is therefore
  **required**, not optional — and the packet correctly keeps `docs/api/**` out of
  the author lease and inside the coordinator's contract lease.
- `tools/validate/runner.py:253-275` — `sync()` takes `answers[0] == "status"`, the
  **first** `status`/`error` after its mark. A busy `error` becomes a false scenario
  precondition failure. Decision 5's "callers' double-send and timed-out-sync
  recovery are part of acceptance; application-busy errors must not be misreported as
  matrix-read failures" is the correct mitigation, and "any bounded caller recovery
  needed gets an exact serial lease and complete qualified review, never hidden
  retry loops" is the correct prohibition.
- `src/hub/runtime/composition.py:224-272` — `command()`, `protocol()` and
  `refresh()` all take the **same** `self.transaction` lock inside `operation()`, and
  `events.py:313-319` routes a `get_status` through `runtime.refresh(force_refresh=True)`.
  A forced-read burst therefore **delays user commands**; it is not merely task
  accumulation. Decision 4's "a queued command must not be overtaken by this owner's
  later trailing read", the "fair command" control, and the "two-second simulator
  progress deadline **AFTER** the held read is released" (correctly labelled a
  software test threshold, not a physical latency claim) are the right controls.
- `src/rest_api/events.py:43,193-198` — `QUEUE_LIMIT = 256` with a drop-on-full
  path, so "the existing bounded send queue" for the busy error is real.
- `src/rest_api/ws_request_work.py` (component docstring) — the accepted public
  surface is `try_start(factory) -> Task | RejectReason` with
  `RejectReason.{OWNER_BUSY, APPLICATION_BUSY, OWNER_CLOSED, SHUTTING_DOWN}`;
  a rejected request **starts nothing** (the factory is not called); `owner_limit`
  defaults to 1; `application_limit` is required and has no default; and the
  component's own *"Wiring (proposed)"* section records that whether an `OWNER_BUSY`
  rejection should instead be coalesced with the in-flight read **"is a wiring
  decision with a freshness consequence"**.

On that basis the packet's synthesis — **per-connection one admitted read plus one
Boolean trailing-demand flag, no cross-owner sharing of an already-started read, no
global reply-task set, plus a bounded application-level busy error at the
admission ceiling** — is the only policy that keeps all of: freshness (a request may
only be satisfied by a read that started after it), the client-visible error
surface (a rare, distinct, documented busy error instead of a per-request failure),
the `runner.sync()` first-answer semantics, and a **hard bound** on concurrent
forced reads. The rejected alternatives each break one of those: pure rejection
breaks `sync()` and turns a normal read into a client-visible error; per-application
shared single-flight (Anthropic's R1 form) can answer a later request with a read
that started before it, violating `WEBSOCKET.md:26`; and "no bound at all" is the
status quo defect.

Two sub-points I want on the record, because they are where a reviewer will push:

1. **The two-read assertion is correctly scoped.** Decision 4 says it applies *only*
   to "a finite burst held behind one pending read, not to an arbitrary long
   stream", and that "at least one scheduling opportunity follows each completed
   read". That is the right limit: with `owner_limit = 1` a single connection under
   sustained demand performs **successive** fresh reads, so a naive "≤2 reads per
   burst" assertion would be wrong. The plan states the correct assertion.
2. **The application limit of 4 is a coordinator design decision, and I record that
   it is one.** With `MAX_WS_CLIENTS = 32` (default) and `application_limit = 4`,
   a 32-connection burst admits 4 reads and returns 28 busy errors. The packet
   makes the number **frozen and testable** (the `FC-WS-WIRE` acceptance lists
   `application4` explicitly), it keeps the busy error distinct and documented, and
   the browser's `get_status`-on-`*_failed` behaviour plus the "no visible error
   handler" fact means a busy error can drop a refresh that the push channel would
   otherwise have delivered anyway. I accept the number as an explicit, testable
   choice with a named reviewer control, and I note it as the single most
   contestable constant in the plan (§6).

### 3.2 WS lifecycle (packet Decision 5): ACCEPT

Verified entry points and their actual order:

- `src/rest_api/app.py:598-617` — `RestApiServer.stop()` awaits
  `self.app["event_stream"].stop()` **inside** the `try`, and only in the `finally`
  calls `self.runner.cleanup()`. aiohttp's cleanup contexts therefore run **after**
  the event stream is already stopped. A `cleanup_ctx` alone cannot establish the
  fence ordering; the fence must run inside `stop()` **before**
  `event_stream.stop()`, with the drain after. Decision 5's requirement to fence
  "direct app cleanup, **direct RestApiServer.stop**, runtime stop, startup rollback
  and repeated stop" is exactly the set of real entry points, and
  `FC-WS-WIRE` naming `RestApiServer.stop` in the coordinator lease is correct.
- `src/rest_api/app.py:594` — the start-failure path calls `await self.stop()`, so
  startup rollback is a real path; `stop()` returns early when not running, so
  repeated stop is a real path.
- `src/hub/runtime/composition.py:423-443` — runtime stop sets `_stopping`, cancels
  `_operations`, then stops the API server and closes the client.
- The component's own `DrainReport` semantics — `remaining` counts **all**
  unfinished admitted work (attached tasks plus in-progress admissions),
  `requested` counts only what this call asked to cancel, a resistant task is never
  relabelled drained, and a cleanup called from inside its own scope returns at once
  — match Decision 5's "cooperative work reaches remaining=0, resistant work remains
  truthfully tracked/reported". Decision 5's "modify the existing unwired guard
  explicitly; retain all other accepted component tests" is right: the guard at
  `tests/test_ws_request_work.py` (~line 871/872, docstring *"this candidate is not
  wired in; /ws still has its original unbounded path"*) is a **historical boundary
  assertion** that a wiring package must deliberately replace, not a test that
  silently continues to pass.

### 3.3 HA cookie / effective-key / manual-recovery / legacy-fault split (Decision 6): ACCEPT

- **Bare JSON is real.** `src/rest_api/security.py:267-269` — `auth_status` returns
  `web.json_response({...})` with **no** `success`/`data` envelope, while
  `custom_components/hdmi_matrix/api.py:67-71` requires `body.get("success") is True`.
  A dedicated strict reader is therefore genuinely required, and the packet's
  "retaining the existing envelope parser" is the correct minimal change.
- **Cookie contamination is real.** `security.py:217-223` — `access_level` returns
  `"control"` if a session **or a remembered device** **or** a valid API key, and
  `api.py:41,59` sends the request through **HA's shared** `aiohttp` session.
  `security.py:269` publishes that *effective* level under the misleading field name
  `session_level`. A stray control cookie would make a **wrong** key look valid.
  Decision 6's "without ambient session/remembered cookies" and its
  "cookie contamination controls" and "real generated bare fixtures" are required
  for the wrong/missing/revoked matrix to mean anything.
- **Effective-key precedence is real, including the empty-options trap.**
  `custom_components/hdmi_matrix/__init__.py:30` reads
  `entry.options.get(CONF_API_KEY, entry.data.get(CONF_API_KEY))` — **options win**;
  `config_flow.py:113-116` (reconfigure) writes `data_updates` — **data only**;
  `config_flow.py:132-136` (options) stores the key with **no probe at all**; and
  `api.py:54` (`if self.api_key:`) sends **no** `X-API-Key` header for an empty
  string. So an empty options key silently shadows a valid data key and the hub is
  contacted with no credential. Decision 6's "omitted preserves, explicit empty
  removes, reconfigure updates/removes stale options overrides, reload actually uses
  the validated header" and its "Preserve polling options/unique identity/duplicate
  and wrong-device handling" cover exactly these paths.
- **The unlocked-with-invalid-key case is decidable from source, not an owner
  choice.** `security.py:209-215` — `api_key_valid` checks stored key hashes and
  the `API_KEY`/`CONTROL_API_KEY` environment variables **regardless of lock
  state**; `security.py:258-259` — the control 401 is raised only when a control PIN
  is set. So on an unlocked hub a supplied key that still yields effective level
  `none` is **demonstrably invalid**. Decision 6's "an explicitly supplied invalid
  key is rejected when capability can determine that, including unlocked hubs" is
  source-backed, not a policy preference. "Unlocked/no-key and an offline matrix
  remain supported" is also source-correct: `security.py` gates control on
  `pin_set("control")`, and `_probe`/`config_flow.py:70-73` already tolerate a
  missing device/MAC.
- **Manual recovery vs automatic reauth.** `custom_components/hdmi_matrix/` has no
  `async_step_reauth` and no `ConfigEntryAuthFailed`; `coordinator.py:100-118`
  raises `UpdateFailed` and polls public GETs only, so a revoked key is invisible
  until a write 401s. Decision 6's "automatic reauth from arbitrary write401 is
  outside this minimal repair; retain manual correctable recovery" and "a later
  positively classified setup auth/reauth extension requires its own scoped
  acceptance" are the correct boundaries — an admin-only action may correctly
  refuse a valid control key, so a blanket 401→reauth rule would be wrong.
- **Legacy fault split.** `security.py` has had `/api/auth/status` since `v0.1.0`
  (per the peer history in the R2 reports). Decision 6's "unsupported auth-status
  404 is explicitly capability-unknown legacy compatibility, with a tested logged
  branch; timeout/malformed/5xx never becomes an authenticated PASS" and "do not
  silently revise a support claim" are the right dispositions, and they keep a 404
  from being laundered into a PASS.

### 3.4 UI: actual General controller, Profiles, `shift+?`, and scope (Decision 7): ACCEPT

- **`s` is a silent no-op today.** `web/js/components/keyboard-shortcuts.js:41-45`
  calls `window.settingsPanel.toggle()`; `window.settingsPanel` is **never
  assigned** anywhere in `web/` (only `app.js:141` assigns
  `this.components.settingsPanel = new SettingsPanel()`, and
  `settings-panel.js:638` assigns the **class** `window.SettingsPanel`). The
  legacy panel exposes `open()`/`close()` but no `toggle()`. Decision 7's "do not
  invoke the legacy SettingsPanel" is therefore correct, and the real controller is
  `window.unifiedSettings` (`unified-settings-drawer.js:362`), whose
  `open(section = 'general')` defaults to the visible **General** section
  (`sections` starts with `'general'`, `general` has `drawerId: 'general-drawer'`,
  `globalKey: 'generalDrawer'`). Decision 7's "opens the existing visible General
  settings controller (unifiedSettings General)" is source-correct, and "confirm
  visible controls before editing" is the right ordering.
- **`4` currently targets a tab that does not exist.**
  `keyboard-shortcuts.js:33-35` clicks `[data-tab="scenes"]`; the tab specs at
  `side-nav-drawer.js` are exactly `dashboard | matrix | inputs | outputs |
  profiles`. `profiles` is the correct target, matching the original CR-03
  acceptance wording "existing Profiles/Scenes view". Decision 7's "4 selects actual
  visible Profiles/Scenes navigation" is right.
- **`shift+?` really never fires.** `keyboard-shortcuts.js:53-55` registers the id
  `"?"`; `handleKeydown` (`:147-173`) builds the id from `e.key.toLowerCase()` plus
  active modifiers, so on any layout where `?` requires Shift the lookup id is
  `shift+?` and the lookup **misses**. Decision 7's "shifted ? opens help under a
  declared keyboard layout" is correct, and the "declared keyboard layout" phrase is
  the honest way to state it.
- **Escape is bounded, not broken.** The registered handler closes
  `overlayStack?.closeTop()`, `overlayManager?.closeActive()`, `ContextMenu.closeAll()`
  and the help. The plan is right to require "exactly-topmost Escape behavior" to be
  **tested** rather than to assert that every Escape path is broken — and right to
  keep "broad overlay/a11y changes in CR09 unless a minimal CR03 assertion proves a
  necessary overlap".
- **Scope control is right.** `FC-UI-KEYS` leases only
  `web/js/components/keyboard-shortcuts.js`, one new e2e spec and a bounded guard
  hunk; `app.js`/`unified-settings-drawer.js` are reached through a named call
  site; "no baseline edits or visual approval inferred from passing tests" matches
  the repository's owner-visual-approval rule.

### 3.5 Truth inventory, counts and domain acceptance (Decision 8 + `FC-TRUTH`): ACCEPT

I parsed `docs/validation/features.yaml` at `9b783d72` in full: **268 unique feature
ids**, 50 of them `F-UI-*`/`F-KIO-*`, and **33** `F-UI/F-KIO` rows at
`current: V1` against `target: V3`. I also counted **228** rows with
`current != target`.

That gives **three different aggregate below-target figures in circulation** — the
packet's frozen per-package `below_target` values (sum 223), the dated
`REPO_CONFIG.json` readiness snapshot (203), and my own per-feature parse of the
current registry (228). This is exactly the disagreement Decision 8 refuses to paper
over: *"Reconcile the disputed UI/KIO counts from the registry rather than selecting
a report number."* That instruction is correct, and my three figures are the
evidence that it is needed. I record them as **my measurement at `9b783d72`**,
not as acceptance of any count, and not as a defect in the packet (the packet
labels all of it dated history and requires re-derivation).

The packet also correctly keeps **HIL-09's twelve caps**, refuses to call UC-18 or
the old LICENSE-stub prose current reproduced defects, separates "software viewport
probes may run now" from "actual-device confirmation is a separate gate", and treats
kiosk zoom as a technical design choice whose **changed rendering** still needs
owner visual approval. `FC-TRUTH` is scoped `prose_inventory` with new report paths
only and coordinator-applied canonical edits — no source, no registry edit by a
worker.

### 3.6 Support floors and the upstream Python floor (Decision 9): ACCEPT — primary source verified

I fetched the upstream Home Assistant `2025.1.0` `pyproject.toml` read-only and
recomputed its SHA-256: **`36e5fd29a9ab17bc881569a513f969622732c7a1439c5f39927368f764469889`** —
**identical** to the packet's `support_primary_evidence.sha256`, and the file
contains exactly `requires-python = ">=3.12.0"`.

So the packet's Decision 9 is primary-source correct and **my own R2 §4.5 claim that
"HA 2025.1 requires Python 3.13" was wrong**. The packet's
`M3_remaining_overclaims` entry rejects that claim by name; I accept that rejection
and retract my statement. Two consequences follow and the packet states both:
HA `2025.1.0` must not be attempted on Python 3.11, and the **hub package's own
`requires-python >= 3.11` claim** is a separate axis proved in its own environment.
Decision 9 also keeps the exact floor (`2025.1.0`, not `2025.1.4`), separates
HACS custom-repository install/upgrade from default-listing admission, and keeps
"a post-run import probe is not in-run proof". The packet correctly separates
**proof** from a **claim change**: proving the declared floor is routine; changing
it is an owner compatibility decision.

### 3.7 Composition before fresh canonical proof (Decision 10): ACCEPT

This is the decision that removes the circularity the R2 reports identified. The
retained `RV-API034` bounded source review and report-quality evaluation are
already complete (with `M-1` still held as a **candidate-freshness** condition);
`RV-WS040` stays a distinct retained chain; the shared runner/model/client/evidence
code is frozen **before** any candidate-bound security/canonical campaign; full
privacy-chain acceptance stays held and "source staging is not canonical admission";
and original PR-merge CI records are never relabelled as branch ancestry. That is
the right ordering, and it is consistent with `CR-06`/`CR-07`'s own acceptance text
and with the CI record binding in the packet's frozen record (identical tree, non-
ancestor record commit — *no* relabel/import, no policy waiver).

### 3.8 Provenance, D6 and the rejected narrowing (Decisions 1–3): ACCEPT

- **Decision 1** keeps the WS first-authorship `NOT_GRANTED`/`WSR03` and the
  terminal Opus/M3 privacy FAILs unchanged, rejects immediate Opus-authored handler
  wiring, and holds D6 at its complete existing target. Verified: the adopted
  `D6_PROVENANCE_HOLD.json` says `HELD / NOT_DISPATCHABLE_AS_SCOPED`,
  `candidate_attempts_launched: 0`, `wiring_leases_granted: 0`, and its disposition
  says **"No target narrowing, authorship relabel, retake or changed family
  allocation at dispatch."**
- **The coordinator rejects my own R2 narrowing proposal, and I accept that
  rejection.** In R2 §3.3 I proposed `src/hub/runtime/composition.py` +
  `adapters.py` as a trailer-free D6 review-role target. The packet's
  `peer_dispositions.D6` rejects it: *"REJECT MiniMax narrowed composition/adapters
  target as discharging existing whole D6 or granting Anthropic review of own
  component… Full M3 lifecycle candidate conditional audit selected instead."* On
  the record that rejection is **correct**, for three reasons: (i) D6's own
  disposition forbids target narrowing at dispatch; (ii) trailer absence is an
  indicator, not provenance — which I myself wrote in R2 §3.3 (*"trailer absence is
  not proof… corroboration is still required and is not optional"*), so my own
  proposal could not have discharged D6 without a native audit anyway; and (iii) the
  packet's replacement is **strictly stronger in scope** — a *full mixed target*
  (`websocket`/component/`events`/`app`/runtime/`adapters`/callers/assertions at
  `9b783d72`) rather than a trailer-free subset — and its `acceptance` states
  explicitly that it **"does NOT discharge D6 by narrowing"**. The packet also
  preserves my substantive content as a possible *"separate scoped runtime analysis
  only with no wiring grant; NOT launched/reserved here"*, i.e. it keeps the finding
  without granting a wiring lease. That is a fair disposition of a peer proposal I
  made, and I record the disagreement's end state rather than defending it.
- **Decision 2** adopts prospective first assessments for WS, HA and UI, each
  gated on an actual family/domain/role attempt audit, an exact target/native
  contribution/conflict audit, a useful competence match and a **qualified
  independent judge** match, with Astra as the *proposed* report-quality judge whose
  existing async/report judgments **do not automatically grant HA/UI judging
  competence**, and with an unproved judge or target holding that row. That is
  exactly the "do not qualify roles from brand" requirement, and it matches the
  standing protocol's rule that accepted implementation work or a catalog
  description alone does not qualify review.
- **Decision 3** prefers M3 over Anthropic for the complete WS and HA review
  because the consequential targets carry actual Anthropic contributions or
  unresolved historical indicators, keeps Anthropic UI conditional on affirmative
  non-self-authorship, requires an exact new-diff review to carry disclosed old
  context without certifying the historical subsystem, and — importantly —
  separates *published planning findings* from *implementation authorship*:
  *"Published planning findings are not implementation authorship and do not by
  themselves disqualify a useful first review assessment."* I checked this against
  the D6 wording (*"conflict indicators, not a replacement for actual native
  source-family attribution"*) and it is the same distinction: a planning report is
  not a source contribution. This is also the correct answer to the self-interest
  problem in Anthropic's own R2 (*"I am Anthropic, so proposing an Opus assessment
  is self-interested. The selection should be made by R3"*) — the packet makes the
  selection with a stated reason and keeps the conditional gate.
- **Decision 3's "Unknown source family is recorded and resolved, never treated as
  clean"** matters here, and the packet gets it right where the R2 reports
  disagreed: my R2 §4.3 counted **three** distinct co-author labels in the history
  (`Anthropic`, `OpenAI Codex`, and `Sisyphus` with two different addresses), so a
  trailer is neither proof of family nor its absence proof of provenance.

### 3.9 Staffing, first-attempt gates and judge fit: ACCEPT

| Row | Candidate | Judge | My assessment of domain fit |
| --- | --- | --- | --- |
| `FC-TRUTH` | M3 (inventory) | Sol | M3's earned scope is planning/prose/bounded inventories; the deliverable is prose + a new report path, no source. Cross-family review exists. ✓ |
| `FC-PROVENANCE` | Astra (audit) | M3 (fidelity) | Correctly the enabling row: it is the mechanism that records each proposed author/reviewer/judge's actual attempts, target contributions, exclusions and unknowns. Scope is `prose_metadata_audit`, no code acceptance. ✓ (see §6.1 for one refinement I recommend) |
| `Q-UI-A` | Opus (first UI review) | Astra | Domain-scoped "genuine FIRST Opus UI-review role unused, complete exact target independent, **Astra UI/report-judgment taskfit established; else HOLD**". Nothing is qualified by brand. ✓ |
| `Q-LC-M3` | M3 (first lifecycle review) | Astra | "no target source/test/probe authorship, full mixed target audit"; the failed M3 *privacy* attempt does not transfer to a different role/domain, and M3's earned scope is inventory-only, so this must be earned. ✓ |
| `Q-HA-M3` | M3 (first product-HA review) | Astra | "distinct from failed diagnostic privacy"; the HA target's Anthropic indicators bar an Opus whole-flow certification instead. ✓ |
| `FC-UI-KEYS` | Sol | Opus (after Q-UI-A) | Different family from the author; the reviewer is gated on the assessment PASS *and* exact kiosk/UI domain fit. ✓ |
| `FC-HA-AUTH` | Sol | M3 (after Q-HA-M3) | Product-HA source review; coordinator serial fixture-generation lease named. ✓ |
| `FC-WS-WIRE` | Sol | M3 (after Q-LC-M3) | Explicitly requires "complete composed target independent source-review" and a coordinator contract lease. ✓ |
| `FC-SUPPORT-RUN` | Sol | M3 (fidelity only) | Scope `evidence_generation_pending_domain_acceptance`; "no target promotion". ✓ |
| `FC-UI-REPRO` | Sol | M3 (fidelity only) | Same; "Actual feature acceptance requires qualified UI reviewer". ✓ |

The `assessment_rule` is right in every clause I checked: all six axes PASS, one
candidate and one independent qualified judge at the exact report commit, **no
assessment correction / retake / extra judge**, target and role judged exactly as
frozen after the source/attempt audit, no material scope change under the same
attempt, a negative verdict is a delivered successful judgment (not a failed
launch), qualification does not accept source, and every primary changed commit
needs a separate exact independent qualified review. Product corrections after a
qualified source review keep their own one-fix/one-rereview reserve — which
corrects my own R2 §5.2, where I had written an assessment correction reserve that
contradicted my own earlier statement and the adopted rule. ✓

### 3.10 All 65 unit reservations, capacity and correction rules: ACCEPT

I verified the embedded allocation against the packet's own coverage: **30 packages,
65 units, 268 feature ids, 85 existing execution pins, 0 new canonical findings**;
my independent sums of the embedded package rows (65 units / 268 features) agree.
Every one of the 65 rows carries a current author reservation, a current reviewer
reservation **with an explicit domain gate**, a readiness statement, a
`source_review_if_new` rule (*"qualified different-family exactcommit REQUIRED,
including tests/tooling/fixtures; no source through inventory"*), and its frozen
original scope/acceptance/dependency/lease/verification/temporary-data block. The
reviewer reservations read `M3 after exact relevant domain PASS; no automatic broad
source entitlement` (or `Opus after Q-UI-A and exact kiosk/UI domain fit`) — that is
**not** a blanket family promotion, and it is exactly what the AGENTS.md rule
requires. Two of the three reviewer routes are themselves conditional on an
assessment PASS, so the 65-unit backlog cannot silently acquire a reviewer.

Capacity is honestly dated (codex 22 % used / 78 % remaining, claude 26 % / 74 %,
minimax 37 % / 63 %, all with reset windows; `codex` session window not reported),
the ceiling is `max 2 current + coordinator + protected external = 4`, no nesting,
and every row says to re-check the intended pool before creation/start while
reserving review and correction capacity. The first wave (`FC-TRUTH` author M3 +
`FC-PROVENANCE` author Astra, reviews staged) fits the ceiling exactly. Google is
unverified, Antigravity's family is unresolved, DeepSeek is unavailable; no new
accounts, login or spend. ✓

### 3.11 The 14 issues, 30 packages and 65 units all remain in scope

All fourteen `CR-01…CR-14` records are embedded with their real priority,
classification, evidence pointers, existing execution pins, acceptance text, owner
and `dispatch_state: "not_launched"`. `CR-04`/`CR-05`/`CR-06`/`CR-07` remain held or
sequenced; `CR-11`/`CR-13`/final release remain owner gates. Nothing is closed,
promoted or relabelled. The `historical_status_warning` and
`complete_65_unit_allocation_and_acceptance` boundary ("Repeated historical
route/launch/qualification metadata stays in this immutable original; it is not
current readiness") are honest.

---

## 4. Critical disposition of the coordinator's `peer_dispositions`

I checked each entry rather than accepting it, including the four that correct my
own R2 positions:

| Packet entry | My position |
| --- | --- |
| `consensus_already_reconciled` | Correctly worded: the three R2 reports *did* converge on rejecting immediate Opus WS authorship, retracting first-assessment owner-funding and one-domain-unlock, preserving the privacy budget and separating inventory — but the convergence was **not** a consensus on the whole plan. The packet does not treat it as one. ✓ |
| `WS_policy` | Correctly records a **coordinator decision** with a hybrid and states *"Reports preference/disagreement preserved, not majority vote."* My R2 preference (wiring-level trailing) is the same hybrid's core; OpenAI's busy-rejection preference is the admission-ceiling half; Anthropic's trailing preference is honoured. A reasoned decision with a recorded dissent — not a vote. ✓ |
| `D6` | Correct, and it rejects **my own** R2 narrowing with reasons (§3.8). ✓ |
| `HA_conflicts` | Correct: a separate M3 product-HA domain with a full attempt/native audit; historical Anthropic indicators bar an automatic Opus whole-flow certification; no source-family proof from trailer absence. ✓ |
| `UI_source_and_budget` | Correct: conditional Opus UI first review with native audit and Astra judge task-fit; prior planning findings neither author code nor disqualify a useful assessment; no owner permission ritual for a truly first domain or routine environment work. ✓ |
| `M3_remaining_overclaims` | Every one of the five rejections is correct, and **four of them reject my own R2 positions** (assessment correction reserve; lifecycle PASS unlocking HA/UI; the narrowed-D6 full-wiring review; the 3.13 Python claim) plus the separate-probe/in-run-import overclaim and the same-family source acceptance by relabelling a run-report author. I accept all five. ✓ |
| `privacy` | Correct: owner-pending extra attempt budget only; full-chain mixed-source context/provenance mandatory **even if approved**; original FAILs and lost bytes remain; no narrower privacy grant. ✓ |

---

## 5. Material issues considered and **not** raised

I looked for blockers and did not manufacture one. Specifically, I considered and
rejected the following as **not** material:

- **The absence of a privacy "readiness" in the first wave.** The privacy chain
  stays held by design; the first wave is inventory/provenance work, which the
  adopted `owner_questions` explicitly places inside existing authority
  (*"None for the next covered product corrections, first genuinely new-domain/
  family assessments or read-only discovery"*). This is the AGENTS.md rule too:
  capacity is a routing constraint, not a project-wide stop, and unrelated ready
  work keeps moving. ✓
- **A hard-coded `application_limit = 4`.** Contestable, but frozen, testable, and
  paired with a documented distinct busy error and a named reviewer control. §6.2.
- **The narrowness of the first wave.** Two rows, both prose-only, no source. That
  is the correct risk posture immediately after a three-provider planning cycle, and
  the packet explicitly says "Do not dispatch the whole backlog from one quota
  observation." ✓
- **The absence of a `Q-UI-M3` staffing row.** The fallback is carried in every
  row's `fallback` field and in the plan's execution order, and it is gated on an
  unused-attempt/contribution/judge audit with "no failed-family reset". Adequate
  as a rule; I recommend it also become a named reserved row so that it cannot be
  lost (§6.3).
- **`FC-SUPPORT-RUN`/`FC-UI-REPRO` being "evidence only".** Correct and required:
  the plan separates evidence generation from domain/feature/support acceptance, and
  only a qualified reviewer can accept the domain. ✓
- **The three aggregate below-target counts differing.** That is the very
  discrepancy Decision 8 orders reconciled from the registry. Not a defect. ✓

---

## 6. Residual weaknesses I recommend fixing (none of them blocks adoption)

These are **improvements**, not changes of substance; none is a gate waiver and
none contradicts a packet field.

1. **The `FC-PROVENANCE` fidelity reviewer is MiniMax, and MiniMax is itself a
   proposed candidate in that audit.** `staffing[FC-PROVENANCE]` =
   Astra (author) → M3 (reviewer, "M3 fidelity review only"), while the audit
   subject includes M3 as a proposed candidate/judge (Q-LC-M3, Q-HA-M3) and M3 as
   a proposed reviewer (FC-HA-AUTH, FC-WS-WIRE, FC-SUPPORT-RUN, FC-UI-REPRO).
   A MiniMax fidelity review of statements *about MiniMax's own* attempt history is
   self-referential. It does not grant competence (the substance is the
   coordinator's call, and the underlying records are native/transcript records the
   coordinator owns), and the audit's own `acceptance` requires affirmative
   native/source evidence with unknowns recorded rather than self-assertion. I
   recommend that the **M3-specific claims** in that audit be signed off by a
   non-MiniMax family, or that the coordinator record that it performed that
   verification itself, before any MiniMax-sourced assessment entry gate is
   cleared. *Specific packet field: `staffing[FC-PROVENANCE].reviewer_or_judge` and
   `.acceptance`.*
2. **`application_limit = 4` should carry its rationale in the plan, not only its
   number.** Decision 4 states the number and the acceptance ("application4"), but
   not the bound's derivation against `MAX_WS_CLIENTS = 32` and the shared
   transaction lock. I recommend one sentence recording the intended relationship
   (client bound vs read bound vs command-latency bound) so a reviewer does not have
   to re-derive it. *Specific packet field: `complete_final_plan_text` Decision 4,
   and `staffing[FC-WS-WIRE].acceptance`.*
3. **Promote the `Q-UI-M3` alternative to a named reserved row.** It is currently
   only prose in a shared `fallback` string. A named row would make the
   alternative-audit path (unused attempt, contribution audit, judge fit, frozen
   target) auditable in the same way as the primary rows. *Specific packet field:
   `staffing` (add a conditional row) / `peer_dispositions.UI_source_and_budget`.*
4. **The truth inventory should record the registry's own `current`/`target`
   semantics as the reconciliation key.** My parse of `features.yaml` yielded 228
   per-feature `current != target` rows while the frozen per-package
   `below_target` values sum to 223 and the dated readiness snapshot says 203.
   `FC-TRUTH` should publish the *definition* it uses (per-feature level gap vs
   package-level aggregate vs "no fresh passing committed record") so the three
   numbers stop circulating as contradictions. *Specific packet field:
   `staffing[FC-TRUTH].acceptance`.*

---

## 7. Remaining real blockers and owner questions — **not** waived by this vote

**Blocking the *programme*, not this decision:**

- The privacy chain's **full-chain acceptance stays held**. The terminal Opus and
  M3 privacy FAILs, the lost original bytes and the old managed-failure outputs
  stay exactly as recorded. `PRIVACY_REASSESSMENT_BUDGET_REQUEST.json` remains
  `OWNER_APPROVAL_REQUIRED / proposal only, no worker or attempt launched`; **no
  approval is inferred from this vote, from any wake, or from elapsed time.**
- **D6 stays held at its complete existing target**; no narrower slice discharges
  it, and `Q-LC-M3` does not discharge it either.
- WS first-authorship remains `NOT_GRANTED` / `WSR03`; the corrected component
  acceptance grants no new authorship competence.
- No source, test, fixture or tooling deliverable may enter through the
  inventory lane; the API034/WS040 retained chains stay distinct; `M-1` candidate
  freshness stays held.
- Tron/visual owner approval, physical HIL, the uninterrupted 72-hour soak, the
  field week, and final version/`main`/tag/artifact release remain owner gates.
  Software passes and CI's 14 green jobs close none of them.

**The owner questions that actually exist (unchanged by this vote):**

1. **Immediate, already prepared:** the existing exhausted-budget request — exactly
   one additional `claude-opus-5-5/high` privacy-review candidate and one
   `gpt-6-astra/high` judge of the unchanged six axes, on existing accounts, no
   automatic retry. Approval alone would authorise an *attempt*; it would not clear
   provenance, qualification or source acceptance. **Still pending. Not approved
   here.**
2. **Later, at their own gates:** an evidenced compatibility-claim change (only if
   the CR-10 proof fails); approval of newly changed visuals/baselines; actual
   devices, topology, disruptive-action and restore scope, and viewport
   measurements; the continuous 72-hour window and field-week conditions/sign-off;
   and final version/`main`/tag/artifact publication.

**The one immediate owner item that is *not* a question:** the packet's Decision 9
places HA `2025.1.0` (which requires Python ≥ 3.12.0, primary-source verified) and
the hub package's independent Python 3.11 proof inside existing authority, so no
owner answer is needed to *run* those proofs; only a demonstrated incompatibility
would turn a claim change into an owner decision.

---

## 8. The scoped prose check — run **once**, and what it is not

*(Protocol fixed before the run. The measured outcome — argv, cwd, inherited
environment, fresh overlay, UTC start/end, direct exit code, full stdout/stderr,
JUnit counts and SHA-256, skip list, failures, and the ordinary/hidden original
inventories — is recorded in the separate owned completion receipt, because a
report cannot contain its own post-run results.)*

**Byte coverage, stated precisely.** The single invocation below ran against this
report's bytes at SHA-256 `27aaeed9b6c258da0af33cab7dded70d400c69d642b99de6bdaa3e243a2554c1`.
The committed bytes differ from that **only** in §8, and only by the paragraphs
there that record the run's own measured outcome, the in-run import origins, the
`addopts` detail and this byte-coverage note — prose *about* the run, added after
it. Because none of the five documentation modules reads any Markdown file
(verified separately below), those paragraphs cannot change the outcome of the
check, and I did **not** re-run the five modules. The owned completion receipt
records **both** digests and the exact diff. The cheap structural checks (strict
UTF-8, local targets, CR-aware whitespace, staged scope) were re-run against the
final bytes.

**Purpose:** show that this new Markdown file and the five existing documentation
modules run cleanly **in my own historical checkout**
(`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-remediation-recovery-r1-minimax`).
It is explicitly **not** product-baseline verification, **not** source
qualification, **not** a route-coverage pass, **not** an evidence admission and
**not** a product test.

**Command (exactly the five named modules, with the two plugins the repository's
documentation-check convention disables):**

```
C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -B \
  C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-remediation-recovery-r1-minimax/build/remediation-functional-20261104/minimax-r3/docs_entry.py
```
where the owned entry script calls `pytest.main` with exactly

```
tests/test_core_documentation.py tests/test_client_guides_docs.py \
tests/test_openapi_and_config_docs.py tests/test_security_docs.py \
tests/test_license_and_protocol_docs.py -q \
-p no:tests.route_inventory -p no:cacheprovider \
--basetemp=C:/t/remediation-functional/minimax-r3/prose/temp/pytest-tmp \
--junitxml=C:/t/remediation-functional/minimax-r3/prose/out/junit.xml
```

The interpreter is the absolute path above with `-B`; the working directory is my
own historical checkout; the exit code is the child's own direct exit code.

**Isolation:** the child inherits the Windows environment and then gets a fresh
overlay — `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`,
`HIDDEN_TEMP`, `--basetemp` and `--junitxml` all under a new owned root
`C:/t/remediation-functional/minimax-r3/prose/`; `PYTEST_ADDOPTS`, `PYTEST_PLUGINS`
and `PYTHONPATH` dropped; `PYTHONDONTWRITEBYTECODE=1`; `PYTHONNOUSERSITE=1`;
bytecode additionally disabled by the explicit `-B`.

**Runs: one.** No retry, no softened assertion, no skipped test counted as a pass,
no unchanged failed-check re-run, no bypass, no ledger generation, no source hook,
no canonical campaign. All artefacts stay inside the owned roots. The ordinary and
hidden pre-run inventory is taken for the **owned roots only** — I make no claim
about writes anywhere else on the host, and no inventory of the shared system
`TEMP` was taken.

**Measured outcome of that one run:** **489 passed**, 0 failures, 0 errors,
**0 skipped**, 3.35 s, direct child exit code **0**, stdout 588 bytes
(`489 passed in 3.35s`), **stderr empty** (0 bytes), JUnit
`tests=489 failures=0 errors=0 skipped=0`, JUnit SHA-256
`8d043b02d981f7fde0f4a33a16526d0dc56819c0823aec36efc00e1f97340c84`, stdout
SHA-256 `e585ecc08ecf32487c1c37a05ee9a77ca4f335fd1926aa0648e1d8e963e95c17`,
stderr SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
(the SHA-256 of the empty string). UTC `2026-11-04T18:47:01Z` → `18:47:04Z`,
interpreter Python 3.12.10 from the root virtual environment, owned-root file
count 42 before → 154 after. The full streams, the JUnit file, the in-run origin
captures and both inventories are in the owned receipt.

**Honest limits on what this proves — measured, not assumed.** The in-run import
capture (collection-finish, session-finish, atexit and post-run, all four
consistent) shows this run imported **`tests.conftest`**, **`hub`** and
**`hub.openapi`** from **this historical checkout**, plus `pytest` and `aiohttp`
from the venv. It did **not** import `src/rest_api/*` or `tools/validate/*`. So this
is a **documentation-module prose check of this historical checkout**, *not* a check
of the product baseline `9b783d72`, *not* a product-behaviour result, and **not**
proof that this new Markdown file was parsed by any test — I verified separately
that none of the five modules globs `docs/` or any Markdown file at all. No
new-Markdown-parsing claim is made. Any import-origin measurement is in-run where
practical and separately labelled where it is a separate probe.

**One honest recording detail about "the argv".** The argv I supplied to
`pytest.main` was the 13-element list in the command block above (recorded in the
owned `env.json` before the run). The repository's own `pyproject.toml` sets
`addopts = "-m 'not hardware and not docker'"`, and pytest prepends that
configured `addopts` to the argument list **in place**, so the list captured after
the run inside the process shows 15 elements beginning with `-m`. That marker
filter is the repository's default (it deselects hardware/docker-marked tests);
it is not something I added, and nothing was deselected here — the JUnit records
489 tests, 0 failures, 0 errors, 0 skipped.

**Before the commit:** strict UTF-8 decoding, local-target link check,
`git -c core.whitespace=cr-at-eol diff --check`, and an exact staged-scope check
that only the new report is staged. The commit is a pure-prose commit using the
authorised **invocation-only empty `core.hooksPath`** exception; there is no global
configuration change and no source-hook result is claimed.

---

## 9. Scope and what this vote is not

This is one R3 planning decision on one hashed complete plan/staffing packet. It
**qualifies no route**, **authorises no launch**, **expands no attempt budget**,
**closes no finding**, **admits no evidence**, **changes no source**, **grants no
lease**, **approves no release** and **discharges no hold**. It does not accept the
privacy chain, D6, the WS authorship question, the HA or UI domains, any retained
source chain, any candidate evidence, any compatibility claim, or any physical,
visual, soak, field or artifact gate. It does not approve a new support-floor
claim, a kiosk-zoom rendering change, or a compatibility revision.

The coordinator records the **three actual** R3 decisions before adoption; my vote
is one of them and I make no claim about the other two. This report does not
rewrite R1, R2, the final packet, the ledger, the registry or any prior report.

**No push, no cleanup, no release, no next worker** is part of this delivery. The
coordinator owns preservation, publication, settlement and release of this worker.
