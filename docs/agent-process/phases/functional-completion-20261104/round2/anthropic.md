# functional-completion-20261104: Round 2 all-peer challenge (Anthropic)

**Status: one R2 contribution only.** It is not a final plan, a vote, a consensus, a qualification, a source or feature acceptance, a lease, a dispatch, or any owner approval. Product source, tests, registry, ledger, manifests, baselines and release state are unchanged. All three R2 originals are still to be preserved. After that, the coordinator writes one complete hashed final plan and allocation, and then three explicit R3 decisions are made on it.

## 0. Provenance and inputs

| Item | Value |
| --- | --- |
| Task / Dispatch | `task_a78ba6ed9dc1` / `ctx_0736448ea192`. Coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`. |
| Route | Assigned `claude` / `claude-opus-5-5` / `high`. The session reports `claude-opus-5-5`. The scoped ignored `.claude/settings.local.json` (SHA-256 `53d75479…bdfd`, unchanged since R1) sets `effortLevel: high` and denies Agent/Task/Team/SendMessage/MCP. This is a self-report, not backend attestation. I cannot see per-turn native effort. No helpers, subagents, plugins, MCP or other models were used. |
| Own base | Branch `planning/remediation-recovery-r1-anthropic`, entry HEAD `4ae498baa200cf17f90430f6961c8f1fecd2b8d1` (my R1), clean. No checkout, reset, rebase or import. The product code in this checkout is **older** than the baseline; I neither executed it nor cite it as product evidence. |
| Integration, resolved once at entry | `wp-runtime-completion` = `eaa05cee01b8ab448e3694fe1d80dc96a3054f44` (local ref = `origin` tracking ref, no fetch). Resolved between 17:29:01Z (packet creation) and 17:30:48Z (creation of my owned roots). **Deviation, disclosed:** a later diagnostic `rev-parse` at 17:40:53Z showed the branch had moved to `f4cb7d31…`. I did not read anything at that ref, follow it, or use it. Every packet read below is bound to `eaa05cee`. |
| R2 packet | `docs/agent-process/phases/functional-completion-20261104/ROUND2_PACKET.json` at `eaa05cee`, canonical Git LF SHA-256 `c37fc7200e6d6384e2b536132090c3affb2b0e98a08b95fc9e94ef8129b0e6fb`: **verified**. It does not exist at `9b783d72`, because it was introduced after the product baseline. |
| Original input packet | `INPUT_PACKET.json` at `eaa05cee`: `cb6a9871fdf8a4adfb181ab1fbf3abafb6c265323c27b543ebd62f9c68857dc4`, **verified**. That equals my R1 read at `afe24d4d`. |
| R1 reports (raw Git blobs, each read in full) | OpenAI `7baf8262…` (parent `ff57e990…`) `57a634bc…9777`. Anthropic `4ae498ba…` (parent `50976503…`) `efe8219c…65c1`. MiniMax `32f911a5…` (parent `d9b575cc…`) `42bd1888…df653`. **All three match the packet**, and each is byte-identical to its copy at `eaa05cee`. |
| Product source | Fixed `9b783d723c81cc56ec86810b789fa31be41e75cc`, read with `git show`/`git grep`/`git blame`/`git log`. Released tags `v0.1.0` and `v0.3.0` were read only for the auth-endpoint history. |
| Peer independence | No peer R2 report was read or searched for. A `C:/t/remediation-functional/openai-r2` directory exists on this host, and I did not open it. |
| Private evidence | `build/remediation-functional-20261104/anthropic-r2/**` (ignored) holds raw read copies. `C:/t/remediation-functional/anthropic-r2/**` holds the prose-check run. The completion receipt is separate, because this report cannot contain its own commit. |

## 1. What I actually read, and the limits

**Semantic reads at `9b783d72` (bounded chunks, not hash checks):**

- **WS:**
  - `src/rest_api/websocket.py` (all).
  - `ws_request_work.py` lines 1–140 (contract, lifecycle and "Wiring (proposed)").
  - `events.py` `remove_client`/`send`/`_send` (171–200), `stop` (260–272), `refresh`/`poll_once` (313–335) and `install_event_stream` (567–581).
  - `app.py` `create_rest_app` (238–268) and `RestApiServer.start/stop` (565–617).
  - `hub/runtime/composition.py` `operation`/`command`/`refresh` (224–273) and `stop`/`_stop` (423–465).
  - `docs/api/WEBSOCKET.md` lines 26, 43, 88 and 112.
  - Callers: `tools/validate/runner.py::sync` (253–275), `web/js/core/ws.js::requestStatus`, and `web/js/app.js` 520–533.
  - Test locations that send `get_status` (`tests/sim/test_sim_ws_contract.py:299`, `tests/test_rest_api.py:898`) and the guard at `tests/test_ws_request_work.py:871`.
- **WS records:**
  - `WS_COMPONENT_INTAKE_RESULT.json` (head).
  - `WS-WORK-01/REVIEW_DELIVERY.json` (verdicts, findings WSR-01..04).
  - `D6_PROVENANCE_HOLD.json`.
  - From `remediation-recovery-20261104/FINAL_PACKET.json`: `authority`, `owner_questions`, `async_review_assessment`, `remaining_gates` and `adoption`.
  - From `REPO_CONFIG.json`: `model_policy` and `current_recovery_allocation_20261104`.
  - `PRIVACY_REASSESSMENT_BUDGET_REQUEST.json`.
- **HA:**
  - `config_flow.py` reconfigure/options (95–149).
  - `__init__.py` setup (20–60).
  - `security.py` `api_key_valid`/`access_level`/`security_middleware` (209–262).
  - `/api/auth/status` history (`git log -S`, presence at `v0.1.0`/`v0.3.0`), `hacs.json` and `manifest.json`.
  - `git blame` of `config_flow.py:54-73,129-136` and `__init__.py:26-31`.
- **UI:**
  - `keyboard-shortcuts.js` defaults, `register`/`parseKey`/`keyToId` and `handleKeydown` (22–173).
  - `app.js` tab rendering (275–345).
  - `unified-settings-drawer.js` header and `open()` (1–40, 190–225).
  - `side-nav-drawer.js` Settings buttons (250–300).
  - The globals that are assigned (`settingsDrawer`, `sideNavDrawer`, `unifiedSettings`).
  - The `index.html` `#settings-modal`.
  - The `visual/catalog.ts` shortcut note (1161–1169).
  - `git blame` of `keyboard-shortcuts.js:22-65`.
- **Trailers:** `Co-Authored-By` counts on all 14 CR-01/02/03 target paths, with dated commit lists.
- **Historical checks:** the five docs test modules in *my* checkout were checked by `grep` for globbing of `docs/agent-process` or Markdown. There is none.

**Not read (limits):**

- `ws_request_work.py` past line 140 and the component test bodies.
- `TransactionLock` (I still make no FIFO claim).
- HA 2025.1.0 or any HA library source. None is installed locally. Every HA API statement below is labelled *memory*.
- `EXECUTION_PINS.json` (I rely on R1 and peer quotes).
- `AGENT_ALLOCATION.md` (4,928 lines). I searched it only with targeted regexes, and found no prior UI-, HA- or lifecycle-review-domain attempt by any family. That is a search result, not a full audit.
- API034/WS040 disposition bodies.
- The native transcripts behind any trailer.

## 2. Bottom line: what changed since my R1

1. **I withdraw my R1 FC-WS staffing (Opus authors the wiring, Astra reviews).** The adopted `FINAL_PACKET.remaining_gates.wiring` requires a "real qualified author". Opus's WS authorship is `bounded_first_authorship: NOT_GRANTED` (`REVIEW_DELIVERY.json`), and `current_recovery_allocation_20261104` says "original author competence stays HOLD". The WS-C01 precedent was an *original-author correction of its own component*. It is not authorship of new handler/app lifecycle code. OpenAI and MiniMax were right.
2. **Anthropic is also conflicted as the CR-01 *reviewer*, independent of D6.** The wiring acceptance necessarily certifies two things: correct use of the Anthropic-authored component `ws_request_work.py`, and the handler/app lifecycle carrying Anthropic trailers (`websocket.py` `c39ee8d5`/`323af8e4`/`dbf5349e`). Even a discharged D6 would not make an Anthropic review of Sol's wiring independent. So D6 stays HELD and gives CR-01 little value.
3. **By my own R1 rule, Anthropic cannot be the CR-02 reviewer.**
   - `git blame` puts 17 of the 20 `_probe` lines and the options-flow structure in `0f7372d8` ("rework the HA component", Anthropic trailer).
   - The key-handling lines come from `89685609` (Oct 17, no trailer, no-Anthropic Run era).
   - CR-02's acceptance (options/reconfigure/reload effective-key behaviour) certifies the whole flow. I withdraw R1 §4's "allowed with disclosure" for CR-02.
4. **The budget dispute is settled by controlling text.** `FINAL_PACKET.owner_questions` says "None for the next covered product corrections, **first genuinely new-domain/family assessments** or read-only discovery." Owner-only applies to an *exhausted*-attempt expansion. So MiniMax's O-1 ("owner must fund a first non-privacy assessment") is rejected. My own R1 O-3/O-4/O-5 (image downloads and public advisory reads as owner gates) are withdrawn: authority is "remediate all findings… no new accounts/spend/credentials".
5. **The CR-01 response policy remains a genuine R3 choice.** Trailing coalescing needs **no component byte change**, so MiniMax's premise is wrong. My R1 per-application "single-flight shared by every waiting owner" *did* risk answering with a read that started before the request, so I retract that part.
6. **Lawful pairs I can support now:**
   - **CR-03:** Sol author, with Opus as reviewer only after a genuinely first Opus UI-behaviour review assessment judged by Astra.
   - **CR-01 and CR-02:** Sol author, with MiniMax M3 as reviewer only after *separate* first M3 lifecycle-review and HA-review assessments, each judged by Astra.
   - Each PASS unlocks only its own bounded domain.

## 3. Challenge topics, with dispositions

Dispositions: **A** = accept, **C** = challenge, **M** = modify. "Self" = my own R1.

### T1. CR-01 response policy

| Proposal | Disp. | Evidence and reasoning |
| --- | --- | --- |
| MiniMax: "coalescing… means changing `ws_request_work.py`, which invalidates the two accepted reviews" | **C** | The component only admits and owns tasks. The factory is wiring code: `owner.try_start(lambda: …)` (docstring lines 116–126). Trailing coalescing lives entirely in `websocket.py`. On `OWNER_BUSY`, set one per-connection flag. The admitted coroutine performs a read, sends `status`, and if the flag is set clears it and performs **one** more read that *starts after* the flagged request. `owner_limit=1` holds, nothing is queued, and component blob `145845f4` is unchanged. Accepted component blobs and reviews remain exact historical facts. |
| MiniMax: coalescing = "answered with the *same* snapshot when the in-flight read completes" | **C** | That describes sharing a read that started before the request. It violates `WEBSOCKET.md:26` ("after a fresh read"), and I did not propose it per owner. |
| OpenAI: prefer busy rejection "over silently satisfying later requests with an older refresh" | **M** | The objection is correct against sharing an in-flight read, and it does apply to my R1 *per-application* sharing, which I retract (§2.5). It does not apply to per-owner trailing. |
| OpenAI/MiniMax: rejection with the existing `error` payload keeps the schema, "zero contract change" | **C** | Schema equality is not behaviour equality. `WEBSOCKET.md:88` restricts `error` to invalid JSON, an unknown command, or "`get_status` when the hub cannot read the matrix". A busy rejection that reuses `"Matrix status not available"` would misreport a read failure. A distinct message needs a coordinator-owned contract edit in the same candidate. |
| Self: "coalesce, do not reject" as *the* policy | **M** | Downgraded to one option. Neither policy is adopted in advance. |

**Facts that the decision must use:**

- **Callers.**
  - `runner.sync` sends one request and takes the first `status`/`error` after its mark (runner 266–274). If an earlier sync timed out (15 s) while its read was still in flight, then under rejection the next sync can get a busy `error` and report a false precondition failure. Under trailing it gets a `status`.
  - The web UI re-requests on each `*_failed` event (`app.js:528-533`), so two quick failures produce two frames. The UI has no visible `error` handler, so a rejection is harmless to display but drops the refresh. Trailing gives a post-request read.
- **Backpressure.** A per-frame `error` is no worse than today's per-frame `pong`. Each reply goes to a bounded per-client queue, and a slow reader is disconnected (`events.py:193-198`). Trailing sends at most one extra `status` per in-flight read.
- **Command latency.** Forced refreshes run inside `operation()` → `async with self.transaction` (composition 225–239, 265–272), the same guard as `command()`/`protocol()`. With `owner_limit=1` and `MAX_WS_CLIENTS=32` (`websocket.py:70`), an `application_limit ≥ 32` means application rejection never fires. Commands could then wait behind up to 32 queued reads, plus one trailing read per owner. A smaller limit forces rejections, which need the contract edit. R3 must choose `application_limit` against a measured command-latency bound.
- **Shutdown order.**
  - Runtime path: `_stop` first sets `_stopping`, then cancels runtime `_operations` (in-flight refreshes), *then* `server.stop()`, then closes the matrix client (composition 425–443). So underlying runtime resources do not vanish under in-flight reads there.
  - `RestApiServer.stop` calls `event_stream.stop()` *before* `runner.cleanup()` (`app.py:603-609`). A component `cleanup_ctx` would therefore fence admission only after sockets are being closed. The runtime-less `driver.py` path has no runtime fence.
  - Accept OpenAI that "appending a cleanup context does not prove order". Modify my R1 lease: it must include the `RestApiServer.stop` hunk, so that `begin_shutdown()` runs first.

**Policy-neutral acceptance (in addition to the packet):**

- Under a pending refresh, a 1,000-frame burst on one socket yields ≤2 forced reads under trailing, or ≤1 admitted plus N rejections under rejection.
- Every `status` sent comes from a read whose start is after the triggering request. This is an ordering assertion, not a count.
- A route command issued mid-burst completes within the bound R3 states.
- `runner.sync` after a timed-out sync, and the double-send after a UI `*_failed` event.
- `admitted==0` after the fence, for both the runtime and runtime-less stop paths. Cooperative work drains (`remaining==0`). Resistant work is reported, not hidden.
- Two app instances do not share state. Ping still makes progress. The `_replies` global is removed.
- The guard `tests/test_ws_request_work.py:871` is inverted with its rationale recorded.
- **Negative controls:** a deliberately non-fenced variant and an intentionally stale-sharing variant must fail these tests.

### T2. CR-01 staffing

| Proposal | Disp. | Evidence and reasoning |
| --- | --- | --- |
| Self: Opus authors, Astra reviews | **withdrawn** | See §2.1. A corrected component review does not grant original first-authorship. That stays `NOT_GRANTED`/HOLD, and WSR-03 (Low; scripts and a commit message outside the lease) stays a historical finding. |
| OpenAI: Sol author; a genuinely first **M3 async-lifecycle review** assessment with an Astra judge, after an attempt-history and contribution audit | **A** | REPO_CONFIG gives Sol "Core implementation". The absence of MiniMax trailers on `websocket.py`/`app.py`/`events.py` is an indicator only, so native task records must confirm that M3 contributed no target code. M3's privacy FAIL is a different domain and role, so this assessment is not a retake. |
| MiniMax: route A (an Anthropic non-privacy domain via Gate Q) also unlocks CR-01 review | **C** | That conflicts per §2.2: the target and the component are Anthropic-shaped. |
| MiniMax: "running one first is enough to open CR-01/CR-02/CR-03" | **C** | The packet and the adopted scope are domain-bound: "Qualified scope must match later actual Sol wiring diff before primary review" (`async_review_assessment.review_quality`). |

**Proposed assessment (planning only, launch after R3):**

- **Q-LC-M3.** One candidate, `opencode2`/`minimax-coding-plan/MiniMax-M3` (thinking inherited, no effort flag), reviewing an existing lifecycle target. Suitable targets are D6's `12ad507e` WS/app/runtime surface or an equivalent one the coordinator selects. The target must have no MiniMax authorship and no prior M3 findings on it (M3's R1 analysed `websocket.py` at a summary level, so the coordinator must judge that contamination).
- **Judge.** One fresh Astra/high judge on the unchanged six axes of `FINAL_PACKET.async_review_assessment`, with all six required to PASS.
- **Outcome.** A FAIL is terminal for MiniMax lifecycle review. Then CR-01 stays HELD, because no other family is available (Gemini is unverified and DeepSeek is unavailable).

### T3. CR-02 HA behaviour

| Item | Disp. | Evidence and position |
| --- | --- | --- |
| Bare-JSON `auth_status` reader with the strict envelope preserved (all three) | **A** | `security.py:267-269` returns a bare dict, while `api.py` `_request` requires `success:true`. Add a dedicated method that keeps the timeout, header and non-2xx handling and rejects a non-dict body. `_request` stays unchanged. |
| Decision table: a locked hub with level `none` gives a correctable error; unlocked/no-key works; offline-matrix works; no mutating probes (all three) | **A** | Control is gated only when a control PIN is set (`security.py:258-259`). Keys resolve through `access_level` → `api_key_valid`, including the env keys (209–223). HA never calls unlock, login or remember, so no hub session or device cookie can mask the key signal (MiniMax's point, accepted in this form; HA's shared cookie-jar behaviour is unverified). |
| Unlocked hub plus an *unknown* supplied key: reject (self) vs accept (MiniMax) | **unresolved, R3** | Both satisfy the packet. Rejecting prevents a silent break if the hub is later locked. Accepting matches "present key cannot be validated as required". This is not owner-only. |
| Options-flow bypass and effective-key precedence (self and OpenAI) | **A+M** | `__init__.py:30` uses `entry.options.get(CONF_API_KEY, entry.data…)`. An options value of `""` (kept after a key is cleared, `config_flow.py:134-136`) or an old key therefore **shadows** a later reconfigured `data` key, which reconfigure alone writes (113–116). Concrete negative control: options key revoked or `""` → reconfigure a new valid key → reload → assert that the actual `X-API-Key` on hub requests equals the new key. Empty-key removal must still remove the key. |
| Self: mandatory `async_step_reauth` plus a 401 → reauth trigger | **M** | CR-02 says "recovery", not reauth. Minimum recovery is a correctable error with retry in user/reconfigure/options. A bounded setup-time auth failure on a locked hub with an invalid key, which starts HA's reauth, is *recommended*. Starting reauth from write 401s is an **optional extension** for R3. Whether HA 2025.1.0 has `_get_reauth_entry`/`_get_reconfigure_entry`/`async_update_reload_and_abort(data_updates=…)` is *memory only*. The code already calls the last two (102, 116), so FC-SUP must verify them at 2025.1.0. |
| Self: auth-status 404 → keep today's behaviour | **M** | This is source-backed only for hubs like `v0.1.0` (2026-09-25), which have neither the endpoint nor key enforcement (`git grep` of X-API-Key/control_pin in `src/rest_api`: none). `v0.3.0`+ serve the same bare shape. The 404 branch must be explicit, logged and tested. It must not apply to malformed or 5xx responses, which are "cannot verify", not "accepted". |
| MiniMax: the `MockHub` route and two existing assertions must change deliberately | **A** | The probed-path list assertion is updated. The key-on-every-call invariant is kept. |
| Fixtures (self, TST-02) | **A** | The `auth_status` contract fixture must be **generated by `tools/gen_contract_fixtures.py`** under a coordinator serial lease, and the API shape must not change. |
| Real HA (all) | **A** | Real-`hass` tests, plus a disposable HA container against a simulator-backed, control-PIN-locked hub. `tools/validate/clients/ha.py` is a privacy-chain path, so any edit to it needs a separate coordinator serial lease. Prefer running from ignored roots. |

**Staffing.** Sol is the author, as the REPO_CONFIG core-implementation author. The defective key lines are from `89685609`, whose native author is unverified. The reviewer is **M3, only after a genuinely first Q-HA-M3 HA-config-flow review assessment** judged by Astra, on an HA target the candidate has not already reported on (for example coordinator/services/entities rather than the CR-02 flow M3 analysed in R1). I challenge OpenAI and MiniMax on "Opus after an HA assessment": Opus would be judging behaviour of Anthropic-shaped flow code (§2.3). I also reject an Opus original-author correction plus Sol review. Sol has no HA-review qualification, and the only non-OpenAI judge for Sol is Opus, which is conflicted on every HA target in this repo.

### T4. CR-03 UI behaviour

| Item | Disp. | Evidence |
| --- | --- | --- |
| `s`: target `sideNavDrawer.open()` (self) / `settingsDrawer.open()` (MiniMax) / the established controller (OpenAI) | **M** | The visible Settings entry is the side-nav section with General/Hardware/Interface buttons, each toggling its own drawer (`side-nav-drawer.js:256-282`). The documented programmatic entry is `window.unifiedSettings.open(section)` (`unified-settings-drawer.js:190-225`, DI-7/UI-05/UI-14, default `general`, hash `#settings/<section>`). `settingsDrawer` handles only profiles/scenes/system. `#settings-modal`/`SettingsPanel` (`index.html:355`, `app.js:141`) is legacy, and its `#settings-btn` is absent. Recommended hypothesis: `s` → `unifiedSettings.open('general')`, which opens the same drawer as the visible General button. The author confirms this in a browser *before* editing. |
| `4`: `profiles`, not `scenes` (all) | **A** | Top-level tabs come from `getTabSpecs()`. `data-tab="scenes"` exists only in the settings drawer (`settings-drawer.js:67`) and the card picker (`dashboard-card-picker.js:44`). |
| `?` "is fine" (MiniMax) | **C** | `register('?')` → id `?` (`parseKey`/`keyToId` 89–111). `handleKeydown` builds `shift+?` whenever `shiftKey` is true (158–166), so `?` never matches on layouts where it is shifted. The catalog note at `catalog.ts:1168` records the same thing. A real keyboard test under a declared layout is required (OpenAI's point, accepted). |
| Self: "`.click()` on a hidden tab may navigate to a user-hidden tab" | **withdrawn/M** | An unpinned tab renders **no** button (`app.js:317`), so the shortcut silently does nothing. The pinned button is rendered twice, in mobile and desktop containers (334–339), so `querySelector` may click a copy hidden by CSS, which still works. R3 or the author decides whether an unpinned tab stays unreachable, and tests cover both pinned and unpinned states. |
| Scope split | **A** (OpenAI) | The minimal UI-06 correction is `keyboard-shortcuts.js` plus one new spec. Help-overlay dialog semantics, focus trap and `overlayStack` registration go to CR-09 unless the CR-03 test proves Escape/topmost is broken. |

**Exact Playwright interactions** (real `page.keyboard`, pinned browser container, existing baselines untouched):

- Assert the visible effect and URL/hash for `s`, `4`, `1`, `?` (after setting a layout), `shift+s` (negative) and `ctrl+s` (negative, with the browser default not prevented).
- Keys typed into an input (text), button-type input, textarea, select and a contenteditable must be suppressed, except Escape, which blurs the field.
- Escape closes the topmost overlay only, and focus returns to the opener.
- Run with personalised unpinned `profiles`, and with the default prefs.
- No page errors.

A reproduction report is not a qualified source review. Screenshot equality grants no owner approval.

**Staffing.** Sol is the author. The reviewer is Opus **only after Q-UI-A**: a genuinely first Opus UI-behaviour *review* assessment judged by Astra under a frozen rubric adapted from the six D6 axes.

- **Target.** It must have no Anthropic or unknown-family trailers, native non-Anthropic provenance, and no prior Anthropic findings on it. That excludes `keyboard-shortcuts.js`, because I authored the CR-03 findings in R1. `unified-settings-drawer.js`/overlay-manager (`a5b65724`, no trailer, WP-E2 during the no-Anthropic Run) is a candidate *subject to the coordinator's native audit*. `side-nav-drawer.js`/`index.html` carry `Sisyphus` trailers, an unresolved helper whose family is unknown.
- **Remaining indicator on the primary review.** `keyboard-shortcuts.js` has no Anthropic trailer, but 39 of its 44 default lines are from the initial commit `47fc33ce`, whose provenance is unknown. The coordinator records that limit. CR-03 acceptance does not certify `settings-drawer.js` (Anthropic UI-49/UI-55 visual commits).
- **Fallback.** If Q-UI-A FAILs, a separate first M3 UI-review assessment is lawful, because it is a different family and not a retake.
- **Disclosure.** I am Anthropic, so proposing an Opus assessment is self-interested. The selection should be made by R3, not by me.

### T5. Authorship and independence indicators

| Proposal | Disp. | Position |
| --- | --- | --- |
| Self: the prospective "exact change + acceptance coverage" rule | **M (kept, applied strictly)** | A historical indicator **blocks** a reviewer whenever the review's acceptance claim certifies behaviour of lines or components the reviewer's family authored. Applied consistently, it blocks Anthropic on CR-01 and CR-02, D6 as scoped, and the privacy whole chain. It leaves CR-03 open with disclosed limits. It is not a narrowing: it *widens* my R1's blocks. |
| Trailers are indicators, not backend proof (all) | **A, with new evidence** | They fail in both directions: `ws_request_work.py` is recorded as Anthropic-authored (intake "Original actual Anthropic authorship retained") yet its only commit `e54228c0` has **no** trailer. `Sisyphus` trailers name no family. Native Task/Dispatch/transcript records decide. Where they are missing, the target is held, not assumed clean. |
| Privacy whole chain vs a new bounded diff (packet) | **A** | The extra Opus privacy assessment would judge redaction behaviour across `runner.py`/`model.py`/`clients/*`, which carry 11/10/6/1 Anthropic-trailer commits before `d6e78e0b` (R1 §4). That is a whole-target certification, so the D6-class provenance gate must be applied *before* any launch, even if the owner approves the budget. This is a gate on the coordinator, not a reason to change the owner's choice. |
| OpenAI: prior OpenAI chain authorship / unchanged surrounding code | **A** | Sol is the recorded author of the privacy C1–C4 chain, so OpenAI cannot be its independent reviewer. `89685609` (the CR-02 key lines) has no trailer and dates from the no-Anthropic Run era, but its native author is **unverified**. Because Sol is the proposed author and M3 the reviewer, the outcome is the same either way. The unchanged surrounding code keeps its own attribution. |

**Unresolved evidence:** the native authorship of `47fc33ce` (the initial commit), of `89685609`, and of all `Sisyphus` commits. D6 target independence remains **unestablished**, and the target stays HELD.

### T6. Authority and attempt budget

- **Rejected (MiniMax):** "a first non-privacy assessment always requires owner funding". The controlling text is quoted in §2.4. Genuinely first new-domain or new-family assessments proceed after adoption of the plan, using existing accounts and no new spend.
- **Owner-only (all agree):** the *pending exhausted* privacy-attempt expansion. It is still unapproved. Broad "continue" or "remediate" instructions and wakes are **not** that approval (`PRIVACY_REASSESSMENT_BUDGET_REQUEST.json.current_state`).
- **Scope does not reset.** A new model, target, task ID or elapsed time does not reset a failed scope: Opus privacy review, M3 privacy review, Opus 4.7 core review and Opus WS first-authorship all stay as recorded. The ledger line 604 shows that the owner already approved one Anthropic core-review *replacement* after two FAILs. That approval does not extend to anything else.
- **Each first assessment is checked before launch** against an attempt-history audit for that same family, domain and role. If the audit finds any prior attempt, the assessment becomes owner-only, and the coordinator prepares the bounded choice at that point.

### T7. CR-08/09/10, the independent lane

| Proposal | Disp. | Position |
| --- | --- | --- |
| CR-08 truth reconciliation by M3, reviewed by Sol (self, OpenAI) or by Astra (MiniMax) | **A (Sol)** | The pinned `SW-FINDINGS-01`/`SW-AUDIT-01` pair is m3→sol. Astra is the same family and an acceptable fallback reviewer. The output is a dated per-row disposition table under its own report path. The coordinator alone edits the register, summary and ledger. HIL-09's 12 caps stay. UC-18 and the LICENSE-stub text are historical. Add the stale `EXECUTION_GATE_STATUS.remediation_authority.state` (R1). |
| MiniMax N-2/N-3: M3 performs browser reproduction and runs Python 3.11 | **C** | M3's earned scope is "bounded evidence inventories only". Executing environments and interpreting browser behaviour is evidence *generation*. M3 may inventory: the 33 V1 UI/KIO rows (MiniMax's count, to be reconciled with the plan's 31), the declared floors, and the run receipts' fidelity (argv, exit, digest, JUnit consistency). |
| Self R1: FC-SUP Astra→Opus and FC-A11Y-R Sol→Opus as READY | **M** | The HA component and `web/js` carry Anthropic indicators, so an Opus review of support or UI behaviour evidence hits the T5 rule. New shape: **evidence runs only**. Sol authors them, with scripts and outputs in ignored or owned roots and no tracked tests. M3 does a fidelity inventory. **No** support or feature acceptance and no claim promotion follow until a qualified domain reviewer exists. Any tracked test, fixture, CI, lock or manifest becomes a separate reviewed package under coordinator leases. |
| Initial test of a claimed floor vs a policy change (OpenAI) | **A** | Testing the declared HA 2025.1.0 floor and `requires-python >=3.11` as they stand is routine. Only a *revision* of a claim after demonstrated incompatibility is an owner compatibility decision. MiniMax O-4 ("confirm the intended floor first") is rejected as a precondition. |
| HA 2025.1 needs Python 3.13 (MiniMax) | **C (unverified)** | My memory is that HA 2025.1 still accepted 3.12 and dropped it later. Both of us are unverified. It does not change the plan, because the `homeassistant/home-assistant:2025.1.0` image brings its own Python. The Python 3.11 claim concerns the hub package, which runs in a digest-pinned `python:3.11-slim`. Record immutable image digests. |
| Kiosk viewports (MiniMax O-3) | **M** | Software probes run on the provisional sizes now. Only the owner's devices can *confirm* a viewport. That confirmation is needed to promote kiosk-viewport claims, not to start work. |

### T8. All of CR-01–14, the 30 packages and 65 units, retained work

- **All retained:** every CR-01–14 item, the 30 packages and 65 units with their dependencies (OpenAI's table is accepted as the reservation list). Planning creates no leases.
- **API034:** bounded review and evaluation are complete (`c3fcace6`). The M-1 candidate-freshness hold stays.
- **WS040:** the retained chain (`938ae303…1fbfee11`, per OpenAI R1) is **distinct** from the new component. Its browser/domain review is held.
- **Privacy:** the full-chain acceptance is held. The terminal Opus and M3 FAILs, the lost original bytes and the preserved M3-judge F1 (Low, C4 masking of public fields) all stay as recorded.
- **Serial composition:** the coordinator integrates accepted chains and FC packages one at a time, with the combined checks after each. Then it **freezes** the shared tool code (`runner.py`/`model.py`/`clients/*`/`evidence.py`) *before* the single candidate-bound F-SEC-007/canonical campaign. Without privacy admission there is no frozen candidate, and I still do not recommend a staged candidate without privacy.
- **REST routes:** no FC package adds a REST route. If one does, it updates `features.yaml` and `tests/sim/test_sim_rest_reads.py`, followed by serial `python -m tools.validate ledger` with 100% routes. Ledger generation never runs alongside registry checks.
- **CI:** CI14 green closes nothing listed here.

### T9. Evidence and report precision

- **Self-correction, R1 §10.** It said the import origins were "measured". The receipt says that was a **separate post-run probe** (`COMPLETION.json`: "via separate post-run probe"), not an in-run measurement. Not that run, my grep, or any other check proves that a new Markdown file was parsed. The historical docs tests do not glob `docs/agent-process` at all. For R2 I measure imports **in-run** (an `atexit`/`finally` dump of `sys.modules` inside the pytest process) and label any extra probe as separate.
- **MiniMax §9.2** says the run "means the one new prose file… imports and parses cleanly" and "no product behaviour was exercised". **C:** its own measured imports include `hub` and `tools.validate.*`. I found no evidence that those tests read the report (bounded to my checkout). Its "system TEMP digests changed by *other* processes" is plausible, but one temp inventory cannot prove who wrote.
- **OpenAI.** The in-run import capture is accepted. Its report embeds the results of a run made before the final bytes, so the check did not cover the final file. Minor, but noted.
- **MiniMax packet-wording observation** (packet absent at `9b783d72`, introduced at `afe24d4d` with an identical hash). **A:** this is an ambiguity in wording, not changed or missing content. My R1 read it at `afe24d4d`. This R2 binds the R2 packet to `eaa05cee` unambiguously (§0). No prior report is regenerated.

## 4. My own R1 claims, reconsidered

| R1 claim | Now |
| --- | --- |
| FC-WS Opus author / Astra reviewer "respects D6" | Withdrawn (§2.1). |
| An Anthropic review of Sol's CR-02 diff is allowed with disclosure | Withdrawn (§2.3). |
| CR-01 "coalesce, do not reject", plus per-application shared single-flight | Modified to an R3 option. The cross-owner sharing is retracted. |
| WS `app.py` lease = the `create_rest_app` cleanup_ctx hunk | Widened to include `RestApiServer.stop` ordering. |
| `s` → `sideNavDrawer.open()`; a hidden-tab click navigates | Modified (T4). Corrected: unpinned tabs have no button. |
| Mandatory reauth; 404 keeps today's behaviour | Modified (T3). |
| FC-SUP and FC-A11Y-R READY with an Opus reviewer | Modified to evidence-only runs with no acceptance (T7). |
| O-2 (kiosk zoom), O-3/O-4 (image downloads), O-5 (OSV/npm advisory) as owner gates | Withdrawn as owner-only. Kiosk zoom is a design decision for R3/coordinator, and visual approval is needed only if rendering changes. Advisory queries send only the names and versions of public packages, under existing authority. The coordinator confirms nothing private is sent. |
| Retained | The CR-01/02/03 source defects; CR-08 M3→Sol; the privacy hold and owner budget; the trailer disclosure for the privacy proposal; serial composition; capacity being dated. |

## 5. Recommended packages and staffing (for the R3 plan; nothing launches from here)

**Common rules for every row:**

- **Base.** Resolve `wp-runtime-completion` once, at worktree creation, to a full SHA. It must contain `9b783d72` and, for FC-WS, `e54228c0`. Record it in the Task and never follow a moving ref.
- **Worktrees.** Created through Orca `worker-start` only.
- **Coordinator-owned paths.** The coordinator owns contracts and APIs, root manifests and locks, `features.yaml`/`LEDGER.md`/`findings_pending.yaml`, allocation and state, fixtures generation and integration.
- **Review.** Exact-commit review by a different family. Reviewers report; authors fix.
- **Reserve.** Each package reserves 1 author correction plus 1 exact changed-commit re-review. Assessments reserve nothing: one candidate and one judge, and a FAIL is terminal.
- **Evidence.** Raw argv/cwd/safe-env/UTC/direct exits/stdout/stderr/JUnit/imports and the immutable image digests. Unique output roots, no overwrite, no retry of an unchanged failed check, no baseline edits.
- **Routes.** Sol = `codex`/`gpt-6.1-sol`/`high` (OpenAI). Astra = `codex`/`gpt-6-astra`/`high` (OpenAI). Opus = `claude`/`claude-opus-5-5`/`high` (Anthropic). M3 = `opencode2`/`minimax-coding-plan/MiniMax-M3`, thinking inherited, no effort flag (MiniMax).

| ID (worktree reservation) | CR | Author | Reviewer / judge | Exclusive lexical lease | Depends | Acceptance and negative controls | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **FC-TRUTH** (`wp-fc-truth`) | 08, 14, 09/10 inventory | M3 | Sol (fallback Astra) | New report under `docs/production/remediation-20261104/FC-TRUTH/` plus ignored roots. Proposed patches only for coordinator paths. | R3 adoption | Per row: assertion, condition, proof, disposition. 65-unit route rematch against the actual qualifications. The 33/31 UI/KIO reconciliation. Floor declarations. Negative control: no row closed without a proof reference. | **Technically ready after R3**, subject to quota. |
| **FC-SUP-RUN** (`wp-fc-support-run`) | 10 evidence | Sol | M3 fidelity inventory only. **No acceptance.** | Owned/ignored run roots and report. No `pyproject`/`requirements*`/CI/`hacs.json`/`clients/ha.py`. | R3 | HA 2025.1.0 and current HA by digest. HACS custom-repository install/upgrade, setup/auth/reconfigure/options/unload/reload. Verify the HA APIs used in `config_flow.py`. Core suite on `python:3.11-slim`. Failures preserved, not "fixed" in place. | **Ready after R3** as evidence only. Claim acceptance HELD until Q-HA-M3 PASS. |
| **FC-UI-REPRO** (`wp-fc-a11y-repro`) | 09 evidence | Sol | M3 fidelity inventory only | Owned roots. No `web/`, no snapshots. | R3 | Phone/tablet/kiosk (provisional) zoom, focus, modal semantics, contrast, offline/recovery, persistence. Action/request/state controls. | Ready after R3, evidence only. No feature promotion. |
| **Q-UI-A** (`wp-qual-ui-review-opus`) | gate for 03 | Opus (candidate) | Astra judge | New assessment report plus ignored/temp roots | R3, plus native-provenance audit of the target | Six frozen axes, all PASS required. Attempt-history audit shows none prior. | **Held → ready after R3 and audit.** |
| **Q-LC-M3** (`wp-qual-lifecycle-review-m3`) | gate for 01 | M3 (candidate) | Astra judge | Same | R3, plus M3-contribution audit | `async_review_assessment` axes, unchanged | Held → ready after R3 and audit. |
| **Q-HA-M3** (`wp-qual-ha-review-m3`) | gate for 02/10 | M3 (candidate) | Astra judge | Same | R3, plus audit. A target M3 has not reported on. | Adapted six axes | Held → ready after R3 and audit. |
| **FC-UI-KEYS** (`wp-fc-ui-keys`, review tree separate) | 03 | Sol | Opus (after Q-UI-A PASS) | `web/js/components/keyboard-shortcuts.js`; new `tests/e2e/functional-keyboard-shortcuts.spec.ts`; report. `app.js`/`unified-settings-drawer.js` only through a named-function coordinator lease. | Q-UI-A PASS | T4 interactions, with `?` under a declared layout and pinned/unpinned states. Negative control: today's code fails `s`/`4`/`?`. Baselines unchanged. | **HELD on Q-UI-A.** Fallback: M3 UI review (first, separate) if Q-UI-A FAILs. |
| **FC-HA-AUTH** (`wp-fc-ha-auth`) | 02 | Sol | M3 (after Q-HA-M3 PASS) | `custom_components/hdmi_matrix/{api.py (new reader only), config_flow.py, __init__.py:26-31 + update listener, strings.json, translations/en.json}`, `tests/ha/{helpers.py, test_config_flow.py, test_api.py}`, a new auth test. **Serial coordinator:** generated `auth_status` fixtures. | Q-HA-M3 PASS. FC-SUP-RUN API check preferred. | T3 table, plus the precedence negative control (stale options key) and the 404/5xx/malformed split. No write during the probe. | **HELD on Q-HA-M3.** No other lawful reviewer (Opus conflicted, Gemini unverified). |
| **FC-WS-WIRE** (`wp-fc-ws-wire`) | 01 | Sol | M3 (after Q-LC-M3 PASS) | `src/rest_api/websocket.py`; `app.py` `create_rest_app` controller hunk **and** `RestApiServer.stop` (coordinator lifecycle-contract lease, serial); the guard at `tests/test_ws_request_work.py:871` only; new `tests/test_ws_get_status_wiring.py`; `docs/api/WEBSOCKET.md` only if rejection is chosen (coordinator contract lease). `ws_request_work.py`, `events.py` and `security.py` are prohibited. | Q-LC-M3 PASS, plus the R3 policy choice | T1 acceptance. Negative controls: non-fenced and stale-sharing variants fail. Applicable REST/WS pipeline, routes 100%. | **HELD on Q-LC-M3 and the policy choice.** |
| PRIVACY C1–C4 | 04/05 | Sol (corrections, if any) | none qualified | review-only | owner budget, then the provenance gate | Unchanged six axes | **HELD (owner).** |
| CR-05/06/07/11/12/13 | — | per plan | per plan | coordinator | freeze/owner | per packet | Future. |

**Sequence.** Each step requires a fresh quota check of the intended pool and a positively released prior slot. At most 2 current workers plus the coordinator and the protected external slot (4 in total), with no nesting.

1. FC-TRUTH (M3) together with Q-UI-A (Opus).
2. Q-UI-A judge (Astra) together with FC-SUP-RUN (Sol).
3. FC-TRUTH review (Sol) together with Q-LC-M3 (M3).
4. Q-LC-M3 judge (Astra) together with FC-UI-KEYS (Sol), if Q-UI-A passed.
5. FC-UI-KEYS review (Opus) together with Q-HA-M3 (M3).
6. Then FC-HA-AUTH and FC-WS-WIRE, as their gates allow.

I default to writing source only *after* its reviewer passes, so that no unreviewable candidates are left stranded. R3 may choose otherwise, knowingly.

**Capacity** (dated packet preflight at 17:26:36Z; I made no new probe):

| Route | Weekly used | Remaining | Notes |
| --- | ---: | ---: | --- |
| Codex | 19% | 81% | |
| Claude | 26% | 74% | Session 3%; weekly reset Fri 05:00 |
| MiniMax | 35% | 65% | |

Demand is concentrated on **Astra** (3 judges), **M3** (1 author, 3 candidates, up to 2 reviews) and **Sol** (5 authors, 1 review). Each needs its correction reserve counted before it starts. Other-host demand is unknown. Gemini (OAuth disabled) and Antigravity (~20%, unresolved family) are not verified fallbacks. DeepSeek is never used.

## 6. Unresolved material disagreements (for R3)

1. **CR-01 policy.** Trailing coalescing (my preference: it keeps freshness and needs no contract edit) vs busy rejection (OpenAI/MiniMax: one response per request, with a contract edit).
2. **The CR-01 reviewer route.** M3 lifecycle review (OpenAI, now me) vs an Anthropic Gate-Q route (MiniMax). I hold that Anthropic is conflicted.
3. **The CR-02 reviewer family.** Opus after an HA assessment (OpenAI, MiniMax) vs M3 after an HA assessment (me, because of the HA authorship indicators).
4. **Unlock scope.** One PASS opens everything (MiniMax) vs each PASS unlocks its own domain (packet, OpenAI, me).
5. **Owner funding of first assessments.** MiniMax yes; the controlling text no.
6. **Unlocked hub plus an unknown key:** reject vs accept. Reauth extent.
7. **The CR-03 `s` target.** Needs browser confirmation; not material to staffing.

## 7. Owner-only choices, only where a controlling rule requires them

1. **Privacy budget (pending).** Approve or decline the exact `PRIVACY_REASSESSMENT_BUDGET_REQUEST.json` proposal (one Opus candidate, one Astra judge). Facts to weigh: the Anthropic trailer indicators on the privacy-chain tool paths (§T5), and the rule that the coordinator applies the provenance gate before any launch. Declining keeps privacy HELD while everything in §5 except PRIVACY continues. I record my R1 preference to decline, or to have a different family, without forcing it. Enabling Gemini requires the owner's own login or settings action. It is an optional lever, not a requirement.
2. **Conditional:** a compatibility-claim revision, but only if FC-SUP-RUN demonstrates incompatibility with HA 2025.1.0 or Python 3.11.
3. **Conditional:** approval of newly changed rendering (CR-03 help overlay, CR-09 fixes). Kiosk real-device viewport readings, but only to promote kiosk-viewport claims.
4. Physical HIL, the 72-hour soak and the field week. Then the final version, `main` merge, tag and artifact release.

No hardware, credentials, new accounts or spend are needed for anything in §5.

## 8. Prose check and delivery limits

The five existing docs modules run **once**, after this file's final bytes, from my **historical checkout**. The interpreter is `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -B`. The run inherits the Windows environment, then fresh owned data/config/TEMP/TMP/TMPDIR/basetemp/JUnit, with `-p no:tests.route_inventory -p no:cacheprovider`. Imports are captured inside the pytest process.

This is a historical prose check only. It is not product or source qualification. It does not prove that this Markdown was parsed, and some modules exercise old local product code. The argv, cwd, safe-env, times, exit, stdout/stderr, JUnit and imports are in the separate completion receipt, under `build/remediation-functional-20261104/anthropic-r2/` and `C:/t/remediation-functional/anthropic-r2/`.

The commit adds only this file, using the authorized invocation-only empty `core.hooksPath` exception for pure prose. No hook configuration changes and no source-hook result is claimed. There is no push, cleanup or release.
