# Functional completion 2026-11-04 — R1 independent assessment (MiniMax)

**Route:** `opencode2` / `minimax-coding-plan/MiniMax-M3` / thinking inherited / CLI effort
override unsupported. **Family:** MiniMax.

This is an **independent Round-1 planning assessment only**. It is not source
implementation, not a qualification attempt or retake, not an extra judge, not
a budget request, not hardware/visual/soak/release consent, and not a
reconciliation of peers. My recommendation is one of three independent R1
inputs; it is not a consensus, and R2 peer challenge plus one complete hashed
final plan and three explicit R3 same-hash decisions are all still future.

---

## 0. Bindings, provenance and what I am allowed to touch

| Item | Value |
| --- | --- |
| Task / Dispatch / terminal | `task_cfa1b9a6672f` / `ctx_363592a96ee8` / `term_d6d55d60-d1f4-4c95-a801-24ca384e5f5d` |
| Coordinator handle | `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| Orca Run (observed, reused) | `run_37205f6095b3`; runtime `2fec76fd-347f-432a-9d0d-6bc2e47cabc4` |
| Checkout | reused settled tree `…/wp-remediation-recovery-r1-minimax` |
| Branch / HEAD at entry | `planning/remediation-recovery-r1-minimax` / `d9b575cc438f8473d96f106db03629aaa608cde5` (my own R3 head) |
| Parent of HEAD | `6671c92789d0de0590609590aeebc73772c00069` |
| Working tree at entry | clean (`git status --porcelain` empty) |
| `wp-runtime-completion` | **resolved once, on entry** → `8bde6d47c3f249e627e89355ecd9f1a3116dc536` (local == `origin`, verified by `for-each-ref`; not re-resolved afterwards) |
| Immutable product baseline | `9b783d723c81cc56ec86810b789fa31be41e75cc` (ancestor of the resolved integration head) |
| New tracked write | **this file only**: `docs/agent-process/phases/functional-completion-20261104/round1/minimax.md` |
| Owned scratch (ignored) | `build/remediation-functional-20261104/minimax-r1/**` (`.gitignore:7` → `build/`) |
| Owned scratch (fresh) | `C:/t/remediation-functional/minimax-r1/**` |
| Helpers / subagents / nesting | none; no plugin/MCP routing; no other model; no accounts, spend, credentials or global config change |
| Source / tests / old reports / root manifests / locks / registry / ledger / integration / private data / baselines / other workspaces | read-only; untouched |

**Native model visibility, recorded honestly.** The route was selected by the
coordinator as `opencode2` with model `minimax-coding-plan/MiniMax-M3`, effort
"unsupported; thinking inherited" (`ROUND1_PREFLIGHT.json`
`selections.minimax`). That is what the harness reports; it is **not** a
backend attestation of identity, of the underlying model, or of the effort
actually applied. `native_final` bytes for this dispatch were not produced by
me and are the coordinator's to collect. I make no independent claim about
family identity beyond what the coordinator's route selection states.

**Peer reports not read.** The two peer R1 reports for this phase exist on
`planning/remediation-recovery-r1-openai` (`7baf8262`) and
`planning/remediation-recovery-r1-anthropic` (`4ae498ba`) — I observed those
commit subjects in a branch listing and did **not** open either file. Nothing
in this report is reconciled against them. My own R1/R2/R3 reports for the
*previous* phase (`remediation-recovery-20261104`) are mine and were re-read for
continuity.

---

## 1. Digest verification — including one honest discrepancy in the dispatch

All digests below were recomputed by me from **raw Git blob bytes** obtained
with `git cat-file blob`, not from text reconstructed through a shell
pipeline. (My first pass joined `git show` output with `\n` and produced one
spurious mismatch on a Markdown file; the raw-blob method is authoritative and
the spurious result is recorded here rather than discarded.)

### 1.1 The phase input packet

| Object | Expected | Mine | Match |
| --- | --- | --- | --- |
| `docs/agent-process/phases/functional-completion-20261104/INPUT_PACKET.json`, canonical Git-LF SHA-256 | `cb6a9871fdf8a4adfb181ab1fbf3abafb6c265323c27b543ebd62f9c68857dc4` | `cb6a9871fdf8a4adfb181ab1fbf3abafb6c265323c27b543ebd62f9c68857dc4` | **yes** |

**Discrepancy I must state plainly.** The dispatch says to read this packet
"in that immutable ref" `9b783d72…`. The file **does not exist at
`9b783d72`** — `git ls-tree -r 9b783d72` shows no
`functional-completion-20261104` path at all, and `git cat-file blob
9b783d72:…/INPUT_PACKET.json` fails. The packet was introduced at
`afe24d4d` ("docs(orchestration): prepare remaining functional completion
planning"), which is a **descendant** of `9b783d72`, and the same bytes are
present unchanged at `084a4722` and at the resolved integration head
`8bde6d47`. I verified the canonical Git-LF SHA-256 at all three: identical
and equal to the expected value. So the **content is unambiguous and verified**;
only the wording "in that immutable ref" is inaccurate — the correct binding
is *"the product baseline `9b783d72` for source, and the phase packet at the
resolved integration head `8bde6d47`"*. I proceed on that reading and record
it for the coordinator's final packet wording. I did not ask for a new
authority: the hash makes the intended content unique.

### 1.2 The packet's ten declared inputs, at `9b783d72`

Every entry was verified by raw-blob SHA-256 against the packet's
`git_blob_sha256` field.

| Input | Result |
| --- | --- |
| `docs/ORCHESTRATION_PROTOCOL.md` | MATCH (`72761a5b…`) |
| `docs/agent-process/PROTOCOL.md` | MATCH (`4aeb2351…`) |
| `docs/agent-process/REPO_CONFIG.json` | MATCH (`b131a232…`) |
| `docs/planning/COMPREHENSIVE_REMEDIATION_20261104.md` | MATCH (`af3ca3de…`) |
| `docs/planning/comprehensive-review-20261104/REMEDIATION_PLAN.json` | MATCH (`ffa81cc1…`) |
| `docs/planning/software-waves/EXECUTION_PINS.json` | MATCH (`e68f1ff2…`) |
| `docs/production/remediation-20261104/recovery-execution/WS_COMPONENT_INTAKE_RESULT.json` | MATCH (`c9a31283…`) |
| `docs/production/remediation-20261104/recovery-execution/PRIV_JUDGE_DELIVERY.json` | MATCH (`ffd10d85…`) |
| `docs/production/remediation-20261104/recovery-execution/D6_PROVENANCE_HOLD.json` | MATCH (`c576596e…`) |
| `docs/production/remediation-20261104/recovery-execution/PRIVACY_REASSESSMENT_BUDGET_REQUEST.json` | MATCH (`705b7d2c…`) |

All ten match. Nothing in the packet's input set is stale, edited or
reinterpreted.

---

## 2. What I actually read, and how — and what I did **not** read

A digest match proves identity, not comprehension. Below is the real reading
inventory.

### 2.1 Full reads (read as source, end to end)

| Object | Pin | Extent |
| --- | --- | --- |
| `docs/agent-process/phases/functional-completion-20261104/INPUT_PACKET.json` | `8bde6d47` | full (337 lines) |
| `docs/agent-process/phases/functional-completion-20261104/ROUND1_PREFLIGHT.json` | `8bde6d47` | full |
| `docs/ORCHESTRATION_PROTOCOL.md` | `9b783d72` | full text extracted; read (route/qualification, capacity, review, publication, verification sections) |
| `docs/agent-process/PROTOCOL.md` | `9b783d72` | full (245 lines) |
| `docs/agent-process/REPO_CONFIG.json` | `9b783d72` | full (263 lines) |
| `docs/planning/COMPREHENSIVE_REMEDIATION_20261104.md` | `9b783d72` | full (98 lines) |
| `docs/planning/comprehensive-review-20261104/REMEDIATION_PLAN.json` | `9b783d72` | structure + all 14 `issues`, all 8 `stages`, all 30 `packages`, all 65 `units` (author/review route reservations, dependencies, base rules), `coverage`, `boundaries`, `test_summary` |
| `docs/planning/software-waves/EXECUTION_PINS.json` | `9b783d72` | structure, `global_invariants`, `review_bottleneck`, `qualification_failure_policy`, the `QUAL-ANTHROPIC-CORE-01` pin in full |
| `docs/production/remediation-20261104/recovery-execution/{WS_COMPONENT_INTAKE_RESULT,PRIV_JUDGE_DELIVERY,D6_PROVENANCE_HOLD,PRIVACY_REASSESSMENT_BUDGET_REQUEST}.json` | `9b783d72` | full |
| `docs/production/software-waves/QUAL-ANTHROPIC-CORE-01/{execution-20261101,manual-attempt-02,replacement-opus55-20261103}/COORDINATOR_DISPOSITION.json` | `9b783d72` | full — **the decisive qualification records** |
| `src/rest_api/websocket.py` | `9b783d72` | full (124 lines) |
| `src/rest_api/ws_request_work.py` | `9b783d72` | lines 1–359 read in full (module docstring, `RejectReason`, `DrainReport`, `WorkOwner`, `WsRequestWork` construction/`try_start`/lifecycle) |
| `src/rest_api/security.py` | `9b783d72` | lines 1–324 (access levels, `route_level`, `api_key_valid`, `access_level`, `security_middleware`, `auth_status`) |
| `src/rest_api/app.py` | `9b783d72` | route assembly region + `create_rest_app` body |
| `src/rest_api/events.py` | `9b783d72` | `refresh`, `poll_once`, `add_client`/`send` region |
| `custom_components/hdmi_matrix/config_flow.py` | `9b783d72` | full (149 lines) |
| `custom_components/hdmi_matrix/api.py` | `9b783d72` | full (127 lines) |
| `custom_components/hdmi_matrix/strings.json` | `9b783d72` | full |
| `web/js/components/keyboard-shortcuts.js` | `9b783d72` | full (275 lines) |
| `web/js/app.js` | `9b783d72` | globals, tab handling, `loadInitialData` |
| `web/js/components/side-nav-drawer.js` | `9b783d72` | `getTabSpecs()` in full |
| `web/js/components/settings-drawer.js` | `9b783d72` | tab bar, `activeTab`, `renderScenesTab` |
| `web/js/components/settings-panel.js` | `9b783d72` | global export + keydown handler |
| `web/js/components/profile-editor.js` | `9b783d72` | global export |
| `tests/ha/test_config_flow.py` | `9b783d72` | full test list + the key-bearing and call-sequence assertions |
| `tests/ha/helpers.py` | `9b783d72` | full (`MockHub` route table, `set_response`, fixtures) |
| `tests/e2e/support/viewports.ts` | `9b783d72` | full |
| `docs/validation/findings_pending.yaml` | `9b783d72` | full |
| `docs/validation/features.yaml` | `9b783d72` | UI/KIO feature blocks parsed in full (50 features) |
| `docs/REMEDIATION_PLAN.md` | `9b783d72` | headings, findings-register structure, 160 id-bearing rows |
| `pyproject.toml`, `custom_components/hdmi_matrix/manifest.json`, `requirements-test-ha.txt`, `.github/workflows/ci.yml` | `9b783d72` | version/Python/HA-pin/CI-matrix regions |

### 2.2 Targeted / corroborating reads

`git grep` sweeps over `src/`, `web/`, `custom_components/`, `tests/`,
`docs/api/` at `9b783d72` for: `keydown`, `data-tab`, `data-view`,
`window.settingsPanel`, `window.profileEditor`, `window.app`,
`window.settingsDrawer`, `X-API-Key`, `api_key`, `auth/status`,
`ws_request_work`, `KeyboardShortcuts`, `loadInitialData`, `scenes`.

### 2.3 What I did **not** read, and what that limits

- **No peer R1 report for this phase** (§0). Consequently I make **no** claim
  about agreement or disagreement with peers, and no reconciliation claim.
- I did not read the full bodies of `src/rest_api/ws_request_work.py` past
  line 359 (the `WsRequestWork` internals `_admit`, `open_owner`,
  `begin_shutdown`, `shutdown`, counters). I verified the **public API surface**
  I rely on (`__all__`, `RejectReason`, `DrainReport`, `WorkOwner.try_start`,
  `close`, `aclose`, `WsRequestWork.__init__`) and the module's own wiring
  contract; I did not re-audit its internal admission arithmetic, which
  remains the subject of its two accepted different-family reviews.
- I did not read `tests/test_ws_request_work.py` bodies (I read only its
  module docstring header and its import surface via grep).
- I did not read `tools/validate/evidence.py` or `tools/validate/clients/ha.py`
  in this round (CR-04 subject); CR-04's status is taken from the packet, the
  `findings_pending.yaml` row VAL-15 and the previous phase's reviewed record,
  not from a fresh source audit.
- I did not read the 2066-line `docs/validation/LEDGER.md`, the full
  `docs/audits/COMPREHENSIVE_PROJECT_REVIEW_20261104.md`, the 61 open
  register rows individually, or any private/root runtime data.
- I did **not** execute any product code, project test, runtime campaign,
  ledger generation or source hook. The only execution is the scoped
  documentation-module run in §9.

---

## 3. Independent classification of CR-01…CR-14 at the product baseline

The packet's classifications are consistent with what I found; where I read
the source I say so with a line reference, and where I did not, I attribute.

### 3.1 CR-01 — Bound WebSocket `get_status` work and connection-owned cleanup — **CONFIRMED at source**

`src/rest_api/websocket.py` at `9b783d72`:

- line 29: `_replies: set[asyncio.Task[None]] = set()` — a **module-global**
  set of in-flight reply tasks.
- lines 106–109: every `get_status` TEXT frame runs
  `asyncio.get_running_loop().create_task(_reply_status(stream, ws), name="ws_get_status")`
  and adds it to `_replies`. **There is no per-connection bound and no
  per-application bound.** One frame → one task, always.
- lines 85–89 (the `finally` of `handle_websocket`): on disconnect the handler
  only discards the client from the registry and awaits
  `stream.remove_client(ws)`. **It does not cancel the `_reply_status` tasks
  that connection started.**
- `_replies.discard` is attached only as a *done* callback (line 109), so the
  set sheds a task only after it has already completed. The set is a lifetime
  reference, not an admission control.
- `_reply_status` (lines 114–124) awaits `stream.refresh()` — a real matrix
  read — and then calls `stream.send(ws, …)` on a socket that may already be
  closed.

So the resource-control gap is exactly as classified: **unbounded admission,
no connection-owned cancellation, work outliving its socket.** The
production denial-of-service magnitude is still unmeasured — I did not measure
it and I do not assert it.

**The remediation asset already exists and is unwired.** `src/rest_api/ws_request_work.py`
(blob `145845f4`, integrated at `e54228c0`, two different-family reviews
`ed697083` + `9817554e`) provides exactly this: `WsRequestWork(application_limit=…, owner_limit=1)`,
`open_owner()` → `WorkOwner.try_start(factory)` returning a task **or** a
`RejectReason` (`OWNER_BUSY`, `APPLICATION_BUSY`, `OWNER_CLOSED`,
`SHUTTING_DOWN`), `owner.close()/aclose(timeout)`, `work.begin_shutdown()/shutdown(timeout)`,
plus a truthful `DrainReport(requested, remaining)`.

I confirmed by grep over `src/` and `tests/` at `9b783d72` that **nothing
imports it** — the only references are inside the module itself and
`tests/test_ws_request_work.py`, whose own header says
`"""Tests for rest_api.ws_request_work (CR-01 candidate component, not yet wired)."""`.
Its module docstring states the same: *"Status: **internal component only**.
Nothing imports it yet … this module does not close CR-01 by itself."*

**The one genuine design decision CR-01 still owes.** The component
**rejects**, it does not **coalesce**. Its own docstring names the open
question: *"Whether an `OWNER_BUSY` rejection should instead be coalesced with
the in-flight read is a wiring decision with a freshness consequence."* The
CR-01 acceptance text says "bounded/**coalesced**". These are not the same
thing, and the difference has a cost that the plan does not currently price:

- **Reject-only wiring** = zero change to already-reviewed component bytes →
  the two accepted different-family reviews of `78295ecd` survive → cheaper.
  Cost: a client that asks twice quickly gets an `error` event instead of a
  second `status`.
- **Coalescing** = the second request must be answered with the *same*
  snapshot when the in-flight read completes. **The component does not
  implement that.** Delivering it means changing `ws_request_work.py`, which
  invalidates the two accepted reviews at `78295ecd` and forces a fresh
  different-family review of the changed component.

My recommendation is **reject-only wiring as the first delivery**, with the
policy written down (a rejection answers the existing `error` event
`{"message": <str>}`, keeping the public schema unchanged), and coalescing
treated as a **separate, later, explicitly-priced change** — because it is a
behaviour change to a reviewed component, not a wiring detail. That satisfies
"bounded" and "documented response policy" honestly; it does not silently
claim "coalesced".

**Acceptance detail that a wiring author must not miss.** `stream.refresh()`
is `runtime.refresh(force_refresh=True)` or `poll_once(force=True)`, and
`poll_once` takes `self._poll_lock`. A burst of frames therefore serialises
into N sequential matrix reads rather than N concurrent reads. The bound
still matters (N reads are queued behind one lock, each with a live task and
a live socket reference), but the honest description of the impact is
**read amplification and task accumulation**, not "N concurrent matrix reads".

### 3.2 CR-02 — Validate the Home Assistant API key during setup/reconfigure — **CONFIRMED at source, with the exact trap named**

`custom_components/hdmi_matrix/config_flow.py` at `9b783d72`:

- `_probe()` (lines 54–73) calls exactly two things: `client.health()`
  (`GET /api/health`) and `client.device()` (`GET /api/status/device`).
- `custom_components/hdmi_matrix/api.py` line 82 documents `/api/health` as
  *"answers while the hub runs, even if the matrix is offline"*, and
  `src/rest_api/security.py` lines 90–132 (`route_level`) return `None` for
  every `GET` — so **both probe reads are public and neither authenticates
  the key**.
- Consequence: **a wrong, revoked or mistyped key produces no error at all.**
  `async_step_user` stores it in the entry (`entry_data[CONF_API_KEY] = api_key`,
  line 87) and the integration then presents that bad key on every subsequent
  request. `async_step_reconfigure` (line 107) uses the same `_probe`, so it
  inherits the same hole; `HdmiMatrixOptionsFlow.async_step_init` (lines
  132–137) does **not probe at all** and stores whatever key it is given.

**The "actual bare-JSON contract" trap, confirmed.** The capability endpoint
exists: `src/rest_api/app.py:310` registers `GET /api/auth/status`, and
`src/rest_api/security.py:267–269` returns

```python
web.json_response({"admin_pin_set": …, "control_pin_set": …,
                   "session_level": security.access_level(request),
                   "device_remembered": security.remembered(request)})
```

— a **bare JSON object**. `HubClient._request` (`api.py` lines 51–71) requires
`body.get("success") is True`, so routing this endpoint through the shared
`_request` would raise `HubResponseError(path, 200, "HTTP 200")`. A new,
dedicated client method is required; the shared request contract must not be
bent.

**How the capability signal actually reads.** `SecurityManager.access_level`
(lines 217–223) returns `"admin"` for an admin session, `"control"` when a
control session **or** a remembered device **or** `api_key_valid(request)` is
true, else `"none"`. `api_key_valid` (lines 209–215) accepts the
`X-API-Key` header (or `?key=`) against stored key hashes **and** the
`API_KEY` / `CONTROL_API_KEY` environment variables. Home Assistant's shared
`aiohttp` session sends **no cookies**, so `session_level` and
`device_remembered` cannot mask the key signal. `route_level` returns `None`
for `/api/auth/status`, so the endpoint is not gated and answers with
`"none"` for a bad key rather than 401. **A valid key therefore yields
`session_level == "control"` and an invalid/missing key yields `"none"`.**

**The decision rule that satisfies CR-02 without breaking setup** (this is the
part the plan does not spell out, and it must be written down by the author):

- `control_pin_set == false` → the hub is **not control-locked** → an absent
  key is fine and a present key cannot be validated as *required*; setup must
  still succeed ("offline matrix and unlocked/no-key setup continue to work").
- `control_pin_set == true` and `session_level == "none"` → the hub **is**
  control-locked → a key is required, and a supplied key that yields `"none"`
  is **invalid** → a meaningful, correctable error.
- Matrix offline is fine: `/api/auth/status` is served by the security
  middleware, which does not need the matrix. `client.device()` failing while
  offline already degrades the unique id to `host:port` and that path must be
  preserved.
- The probe is a **non-mutating GET** — no disruptive action.

**Three concrete residuals the plan does not list.**

1. **The HA test harness cannot express the probe.** `tests/ha/helpers.py`
   `MockHub.register()` registers exactly five read routes (`/api/health`,
   `/api/status`, `/api/status/outputs`, `/api/status/inputs`,
   `/api/status/device`); `set_response()` only manipulates those. There is
   **no `/api/auth/status` route and no way to make it return a bare
   (non-`{success,…}`) body**. Extending `MockHub` is a prerequisite, not an
   afterthought.
2. **Two existing assertions will change and must change for the right
   reason.** `test_user_flow_success` asserts the exact probed path list
   `[ "/api/health", "/api/status/device" ]`; `test_user_flow_with_api_key`
   asserts `all(headers.get("X-API-Key") == "ha-key" …)` over **every**
   recorded call. A new probe request changes both. The key-bearing
   assertion is a *good* invariant and should be preserved by having the
   probe carry the header — but the call-list assertion must be updated
   deliberately, not weakened.
3. **The user-facing strings do not exist.** `custom_components/hdmi_matrix/strings.json`
   declares `config.step.user.data` with **only** `host` and `port` — there is
   **no `api_key` label** — and `config.error` contains only `cannot_connect`
   and `unknown` — there is **no `invalid_auth` (or equivalent) error
   string**. A CR-02 implementation that adds a meaningful correctable error
   must add the translatable strings (`strings.json` **and**
   `translations/en.json`), which is a second owned path and a second-family
   reviewable surface.

So CR-02 is bigger than "add a check": it is product client + config flow +
HA test harness + HA translation strings. That is one coherent package, but
it is not one file.

### 3.3 CR-03 — Repair settings/scenes keyboard shortcuts — **CONFIRMED at source, two distinct defects**

`web/js/components/keyboard-shortcuts.js` at `9b783d72` registers six
defaults (lines 22–65). Two of them target identifiers that **do not exist
in the application as advertised**:

1. **`'4'` → `document.querySelector('[data-tab="scenes"]')?.click()`**
   (lines 33–35). The application's top-level tabs are enumerated by
   `web/js/components/side-nav-drawer.js` `getTabSpecs()`: `dashboard`,
   `matrix`, `inputs`, `outputs`, `profiles` — and `web/index.html` carries
   exactly `data-tab="matrix|dashboard|inputs|outputs|profiles"` (lines 85,
   109, 129, 147, 165). **There is no top-level `scenes` tab.** The only
   `data-tab="scenes"` element is the *settings drawer* tab button
   (`web/js/components/settings-drawer.js:67`), which exists in the DOM only
   while that drawer is open. So with the drawer closed, `'4'` is a silent
   no-op (the `?.` swallows the null); with the drawer open it clicks the
   drawer's tab instead of navigating. **The advertised "Switch to Scenes
   view" shortcut does not work.**
2. **`'s'` → `if (window.settingsPanel) { window.settingsPanel.toggle(); }`**
   (lines 41–45). **`window.settingsPanel` is never assigned anywhere in
   `web/`.** `web/js/components/settings-panel.js:638` exports the *class*
   `window.SettingsPanel`; `web/js/app.js:141` creates the *instance* as
   `this.components.settingsPanel` (i.e. `window.app.components.settingsPanel`);
   and the live settings entry point used by the rest of the UI is
   `window.settingsDrawer` (`settings-drawer.js:446`, opened via
   `window.settingsDrawer.open(targetSection)` in
   `unified-settings-drawer.js:201–202`). The guard `if (window.settingsPanel)`
   is therefore always false and **`'s'` is a silent no-op.**

`'1'`, `'2'`, `'3'` (matrix/inputs/outputs) and `'r'`
(`window.app.loadInitialData()` — `app.js:673`, `window.app` set at
`app.js:867`) do resolve. `'n'` → `window.profileEditor?.openNew()`
(`profile-editor.js:818`) resolves. **`'?'` and `Escape` are fine.**

**Coverage gap.** `git grep -c "KeyboardShortcuts" -- tests/` returns **one
hit, in `tests/e2e/visual/catalog.ts`** — i.e. a visual catalogue reference,
not a behaviour test. **The keyboard-shortcut module has no behavioural test
at all.** CR-03's acceptance ("Browser negative/positive tests cover `s`, `4`,
Matrix navigation, editing-field suppression and Escape/focus behaviour") is
therefore green-field, not a regression fix.

The suppression logic itself (`isTypingTarget`, lines 125–142) is sound and
must be preserved: `<input>` except `button|submit|reset|image`, `<textarea>`,
`<select>`, and `contenteditable` all suppress, and `Escape` still blurs the
field and then runs the overlay-close handler.

### 3.4 CR-09 — UI/kiosk accessibility, mobile and persistence acceptance — **CONFIRMED as a coverage gap, with a number of my own**

I parsed `docs/validation/features.yaml` at `9b783d72`: **50 UI/KIO
features exist; 33 are below target** — 28 `F-UI-*` at `target: V3,
current: V1` and 5 `F-KIO-*` at `target: V3, current: V1`. (The plan's
package split totals 31 because it assigns some UI features to DOM packages;
the authoritative number is the generated ledger, which I did not re-derive.)
`V1` means "unit/mocked tests, or driver-level simulator tests, or screenshot
baselines" per the file's own header — i.e. **no browser-level effect proof**.

Two further facts from `tests/e2e/support/viewports.ts`:
- the two kiosk viewports are **explicitly PROVISIONAL** and unconfirmed
  against the owner's real devices (*"PROVISIONAL: the browser's CSS viewport
  is not confirmed … Confirm with whatismyviewport.com on the device"*);
- the owner already decided (2026-09-25) which two devices these are.

So CR-09's honest scope is: **reproduce and close a defined subset of 33
V1-level UI/KIO features, and resolve the two provisional kiosk viewports.**
It is *not* "fix the UI" — it is a promotion-by-proof exercise, and it must
not touch the immutable visual baselines except through the owner's
re-baseline path.

### 3.5 CR-10 — Prove the declared HA/HACS and Python support boundaries — **CONFIRMED as a coverage gap, and provable from the repository alone**

| Declared | Evidence at `9b783d72` |
| --- | --- |
| "Home Assistant **2025.1+**" (`docs/HOME_ASSISTANT.md:3` and `:628`) | `requirements-test-ha.txt` pins **one** version: `pytest-homeassistant-custom-component==0.13.316`, whose own comment says *"pins an exact Home Assistant release (0.13.316 -> homeassistant==2026.2.3)"*. CI runs the HA suite on **Python 3.13** only. **HA 2025.1.0 is never exercised.** |
| `requires-python = ">=3.11"`; ruff `target-version = ["py311","py312"]`; mypy `target-version = "py311"` (`pyproject.toml`) | CI's global `PYTHON_VERSION` is **`'3.12'`**; the HA job is **`'3.13'`**. **Python 3.11 is never exercised.** |

This is a **documentation-vs-coverage mismatch provable from the repository's
own pins** — no hardware, no owner device, no physical matrix needed. That
makes it the cheapest genuinely independent package in the whole programme.

One correction of scope that matters: **the two claims are independent
axes.** `requires-python >= 3.11` is a claim about the **hub package**
(`src/`); "HA 2025.1+" is a claim about the **custom component**, which runs
inside Home Assistant's own Python. HA 2025.1 requires Python 3.13, so
"prove Python 3.11" cannot mean "run the HA suite under 3.11". The Python
3.11 proof is about the hub's own package/tests; the HA 2025.1 proof is about
the component under that HA release.

Two real constraints for whoever does this:
- `requirements-test-ha.txt` is a **`requirements*.txt` file**, i.e. on the
  coordinator's `coordinator_only_paths` list in `REPO_CONFIG.json`. So the
  HA-version pinning change needs a **coordinator lexical serial lease**, not
  a worker-exclusive path. So does `.github/workflows/ci.yml` (a root
  manifest / CI definition). A worker may *prepare* the change and prove it
  locally, but the landing of a second pinned HA version is a coordinator
  act.
- A second HA version needs a second `pytest-homeassistant-custom-component`
  pin whose plugin version supports that HA release; the file's own comment
  warns that later plugin versions require Python ≥ 3.14, so the plugin
  version and the HA version must be chosen together.

### 3.6 CR-04…CR-08, CR-11…CR-14 — classification and what is *not* a defect

| ID | My independent reading |
| --- | --- |
| **CR-04** | `docs/validation/findings_pending.yaml` at the baseline still carries **VAL-15 open**, "Validation request artifacts and action descriptions do not redact `X-Admin-PIN`", location `tools/validate/evidence.py` and `tools/validate/model.py`, severity **M**, disposition "Corrective package SW-SEC-DATA-02-C1 remains undispatched". This is a **tooling** defect, not an observed credential disclosure, exactly as classified. I did not re-audit the redaction source this round. The C1/C2/C3 chain review and admission are held behind the **privacy** qualification, which is terminal-FAIL for both Opus and M3. |
| **CR-05** | Confirmed integration backlog. `docs/production/remediation-20261104/recovery-execution/PRIV_JUDGE_DELIVERY.json` `remaining` field lists the open items verbatim: *"WS-C01 runtime review PASS with C01-R01 wording OPEN, D6 target/wiring HELD, API034 M-1/WS040/combined/evidence/HA/visual/hardware/72h/week/finalartifact/version/release gates remain."* |
| **CR-06** | Confirmed evidence-freshness blocker (M-1), **downstream of CR-04/05/07**. It cannot start until the covered source is frozen. It is *not* a product-security regression and must not be described as one. |
| **CR-07** | Confirmed provenance gap. The packet's own CI scope line already concedes it: *"14success/1publishes-skipped; qualified local software pipeline only. PR checkout/artifact commit/tree/source/image/client binding not yet adjudicated for canonical feature evidence."* A green CI on a merge commit is integration testing, not candidate-bound proof. |
| **CR-08** | Confirmed metadata/decision-quality gap. I read `docs/REMEDIATION_PLAN.md` §4: 11 finding subsections, ~160 id-bearing rows across `UI-/HIL-/UC-/SEC-/VAL-/API-` families with mixed dispositions (e.g. a row reading *"done on `wp-e1-ui-fixes`"*). `findings_pending.yaml` holds only **2** open rows (VAL-14, VAL-15). The register is a **mixed historical decision log**, so the packet's caution that "61 parser-open records are not 61 verified current bugs" is, in my reading, correct. |
| **CR-11** | Known physical/environment gap. **Owner.** No source change needed; a source-code workaround for absent owner proof would be a defect. |
| **CR-12** | Known release obligations. The packet records "current version synchronization is healthy" — and I confirmed the manifest (`"version": "1.0.0rc1"`) and the CI version/image-label check exist. **Owner** for the final authorisation; the dependency-advisory audit is "unavailable" — another explicit environmental gap, not a finding to close by assertion. |
| **CR-13** | Unexecuted physical/field requirement. The packet is explicit that "No collector is started by this plan" — correct, and I do not propose starting one. **Owner.** |
| **CR-14** | **The decisive one — see §4.** |

### 3.7 What the green CI does and does not close

Run `41843691782`, head `9b783d72`, 14 success + 1 skipped ("Build and push to
GHCR"). I did not re-run or re-adjudicate it. It is consistent with everything
above: it says the *software pipeline* is green on that commit. It does **not**
close CR-01 (unwired, unbounded admission), CR-02 (no key validation), CR-03
(two dead shortcuts), CR-09 (33 V1 features), CR-10 (unexercised floors),
CR-04…CR-08 (evidence/provenance/admission), and it touches none of CR-11…CR-13
(owner gates). The packet's own sentence — *"Current CI green cannot
automatically close any of them"* — is correct and I adopt it.

---

## 4. The decisive programme finding: **there is currently no qualified author/reviewer pair for CR-01, CR-02 or CR-03**

This is the honest answer to "what input is needed", and it is a *negative*
finding I must state rather than paper over.

### 4.1 The reserved staffing cannot be executed as reserved

`docs/planning/comprehensive-review-20261104/REMEDIATION_PLAN.json` reserves
`review_route_reservation: "claude"` for **61 of the 65 units** (all but
`SW-AUDIT-01`, `SW-FINDINGS-01`, `SW-REPO-01`, `SW-DOCS-01`). Author
reservations are `m3` (4 units), `sol` (43), `astra` (17), `claude` (1:
`SW-HARNESS-01`).

But the *actual* Anthropic qualification at the baseline is narrow.
`docs/production/software-waves/QUAL-ANTHROPIC-CORE-01/replacement-opus55-20261103/COORDINATOR_DISPOSITION.json`
records **PASS** for `claude-opus-5-5` with:

- `scope`: *"bounded Python validation-runner/model offline simulator API
  refusal preparation and relevant compatibility guards"*;
- `role_limit`: *"bounded review/validation-preparation competence
  demonstrated; **no general implementation authorship or broad core-review
  entitlement**"*;
- `not_granted`, verbatim: *"general core review"*, *"implementation
  authorship qualification"*, *"authentication/privacy/UI/HA/image/physical
  domains"*, *"source/RV-API034/RV-WS040/RV-PRIVACY-CHAIN acceptance"*, …
- `fresh_task_match_required: true`, `automatic_reservation_unlock: false`.

The two earlier Opus 4.7 attempts (`execution-20261101`,
`manual-attempt-02`) are both **FAIL** with `qualified_domains: []` and
`further_retry_authorized: false`. The pin's own
`EXECUTION_PINS.json` `qualification_failure_policy` says: *"All currently
Claude-dependent source reviews hold after failed/declined/unknown
qualification; no automatic failed-qualification retry or same-family
substitution."*

**Therefore the `claude` reviewer reservation for CR-01/CR-02/CR-03 is not
currently established for UI, HA or core-runtime review scopes.** Reserving
`claude` in a plan is a dated reservation, and `EXECUTION_PINS.json` says so
itself: *"dated reservation; rediscover at actual dispatch."* Executing them
as written would be a qualification breach.

### 4.2 Each family's actual standing

| Family | What is actually established | Can it author CR-01/02/03? | Can it review CR-01/02/03? |
| --- | --- | --- | --- |
| **Anthropic** (`claude-opus-5-5`) | PASS, bounded: validation-runner / model offline simulator **API refusal preparation + compatibility guards**. Opus 4.7 attempts: FAIL. WS first-authorship **NOT_GRANTED**; privacy review **FAIL**. | **No** — no implementation-authorship qualification; privacy/WS authorship explicitly not granted. | **No** for UI/HA/core-runtime (explicitly `not_granted`). |
| **OpenAI** | `gpt-6.1-sol/high`: original author of the privacy chain **and** core author → **cannot review its own source**. `gpt-6-astra/high`: *"qualified async/diagnostic report judgment"* — a **report/evaluation** competence, plus a long record as the independent judge of qualification packets. | **Yes** (Sol is the recorded core/privacy author; the plan reserves `sol` for 43 units). | **Yes, for non-OpenAI-authored source** — i.e. for anything MiniMax or Anthropic authors. **No** for OpenAI-authored source (same family). |
| **MiniMax** (mine) | Accepted **planning / prose / bounded inventory** scope (REPO_CONFIG `preferred_models_with_scope_and_evidence`: *"Bounded evidence inventories only"*; the SW-API-READ-02 corrected report). Privacy-domain assessment **FAIL** (terminal, 2 PASS / 4 FAIL). | **No** earned implementation-authorship qualification. | **No** — no source-review entitlement. |
| **Google** | Gemini CLI: **OAuth disabled**, quota unavailable. Antigravity: live route in this Run, but the **"Gemini Models" weekly bucket reads 81% used (~19% remaining — below 30%)**, and the **underlying family/helper identity is unresolved** in local policy, so it is not a *verified* qualified fallback for the independence rule. | Not established. | Not established. |
| **DeepSeek** | Owner-reported exhausted credit. **Never dispatch, never buy credit.** | — | — |

### 4.3 The consequence

Today, a CR-01/CR-02/CR-03 delivery has **no route pair that is both
qualified for the domain and independent**. The only families with
*implementation* competence are OpenAI — and OpenAI cannot review OpenAI
source. That is a **structural** bottleneck, not a scheduling one, and no
amount of re-sequencing dissolves it.

Two legitimate ways out, both requiring a **prospective, genuine first
assessment** (never a retake, never a relabel):

- **(A) Qualify Anthropic for one bounded non-privacy domain** (UI or HA
  behaviour review, or existing-lifecycle runtime review) under the **same
  frozen rubric** `66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672`,
  judged by a different family (Astra). This is *not* a retake of either
  Opus 4.7 FAIL: it is a **new** domain on a **new** model, with the original
  FAILs preserved. This is also the natural home of the **D6** async-review
  strategy the packet says is still "unestablished" — a WS/runtime lifecycle
  *review* assessment is exactly the profile of a non-privacy bounded domain.
- **(B) Qualify MiniMax for one bounded *implementation* domain** — e.g. the
  CR-03 browser/UI correction — with an independent different-family judge.
  My own family's privacy FAIL is domain-specific and stays terminal for
  privacy; a **different** domain on a **different** subject is a legitimate
  first assessment, not a retry. **I must disclose the conflict**: I am the
  natural candidate for that assessment, so my proposal here is a
  *recommendation for the coordinator to allocate*, not a self-award; the
  selection must be made independently of my interest, exactly as my own
  previous R3 required of the coordinator when it selected my family for the
  privacy slot.

(A) and (B) are not mutually exclusive; running **one** first is enough to
open CR-01/CR-02/CR-03, because the reviewer's family is what matters and
either gives a reviewer outside the OpenAI family.

**Attempt budget is an owner-only decision.** The exhausted-budget precedent
is explicit in the adopted `FINAL_PACKET` `owner_questions`: *"An
exhausted-competence-attempt budget expansion remains owner-only if ever
chosen later; not requested or authorized here."* The **privacy** extra
assessment (one Opus candidate + one Astra judge) is already proposed to the
owner and **unapproved** (`PRIVACY_REASSESSMENT_BUDGET_REQUEST.json`). A
**non-privacy** extra assessment has **no proposal on record** — that is the
single most actionable input the owner can give, and §10 states it as an
exact owner-only decision.

---

## 5. Recommended programme shape — four streams, one gate

The packet's A0–A7 ladder (in `COMPREHENSIVE_REMEDIATION_20261104.md`) is
sound and I do not propose replacing it. I propose **splitting A2 into a
non-source track that can start immediately** and **making the qualification
dependency explicit**, because the current ladder lets a reader believe
CR-01/02/03 can start as soon as A1 finishes — they cannot, because the
reviewer does not exist.

```
              ┌───────────────────────────────────────────────┐
   GATE  Q ──►│ Q: ONE genuine first assessment in a bounded  │
 (owner-      │ non-privacy domain (route A or B, §4.3)      │
  funded)     │ → yields a different-family qualified reviewer│
              └───────────────┬───────────────────────────────┘
                              │
   ┌──────────────────────────┼────────────────────────────────────┐
   │                          │                                    │
TRACK N (no source change)  TRACK S (source change, held on Q)   TRACK E (evidence)
   CR-08 reconcile               CR-01 wiring                        CR-04 → CR-05 → CR-06
   CR-09 reproduce/inventory     CR-02 HA key                        CR-07 candidate proof
   CR-10 version/floor proof     CR-03 shortcuts
   CR-14 staffing/capacity      (one leased owner each)
   → runs NOW, in parallel      → runs when Q passes
```

**TRACK N is genuinely independent and can start today.** It needs no
different-family source review of *new implementation*, because it produces
**inventory, reproduction and prose**, not new product code — precisely the
`SW-AUDIT-01 / SW-FINDINGS-01 / SW-REPO-01 / SW-DOCS-01` routes that
`EXECUTION_PINS.json` names as
`qualification_failure_policy.independent_inventory_routes`. Those four
units already have `author_route_reservation: "m3"` and
`review_route_reservation: "sol"` — **and that pairing is genuinely
independent** (MiniMax → OpenAI), because the deliverable is prose/registry
metadata rather than product source. **This is the one staffing pair that is
executable today without any new qualification.** It is also the honest home
for CR-08, CR-09's reproduction phase, CR-10's environment proof and CR-14's
capacity ledger.

**TRACK S is held on Gate Q.** CR-01, CR-02 and CR-03 are all *source*
deliverables and therefore all need a qualified different-family exact-commit
review, which per §4 does not currently exist for these scopes.

**TRACK E is held on the privacy/chain qualification**, which is terminal-FAIL
for both Opus and M3 and whose extra budget is owner-pending. TRACK E cannot
be accelerated by planning; it can only be sequenced correctly and honestly
reported.

**Ordering inside TRACK S.** CR-01 should be first: it is the only one of
the three whose remediation component **already exists, is already
independently reviewed, and is already integrated** — it needs *wiring*, not
new design, and the wiring is a single leased owner on two files. CR-02 is
second (it has the most surface: product client + config flow + HA harness +
translations). CR-03 is third (smallest diff, green-field browser tests, but
new e2e infrastructure is the real cost).

**Parallelism.** CR-01, CR-02 and CR-03 have **disjoint** exclusive paths
(`src/rest_api/{app,websocket}.py` + `src/rest_api/tests` vs
`custom_components/hdmi_matrix/{api,config_flow}.py` + `strings.json` +
`translations/en.json` + `tests/ha/*` vs `web/js/components/*` + `tests/e2e/*`).
They can run as three parallel authors **only after** Gate Q, and only two at
a time under the concurrency ceiling. They **cannot** run in parallel with
the coordinator's serial integration of shared APIs/registry/locks.

---

## 6. Recommended phases (my proposal — for R2 challenge, not adopted)

| Phase | Contents | Entry gate | Exit condition |
| --- | --- | --- | --- |
| **F0** (N) | Current-truth reconciliation: CR-08 register disposition; CR-09 reproduction inventory of the 33 V1 features; CR-10 support-matrix inventory; CR-14 capacity/qualification ledger update | none beyond the adopted packet | One dated authoritative status; every row dispositioned; the 33 features split into *reproduce* / *already-proven* / *owner-device*; no finding closed without evidence |
| **F1** (E) | The **one** owner-funded bounded assessment (Q): a non-privacy domain on a route with a real first-attempt provenance; different-family judge; frozen rubric | owner authorisation of the attempt budget | An actual PASS/FAIL disposition with exact native/report/judge identities; a FAIL stays terminal for that attempt and does not block F0/F2 |
| **F2** (S-a) | CR-01 wiring: `src/rest_api/app.py` + `src/rest_api/websocket.py` (+ component only if coalescing is later approved) | F1 PASS **or** an already-qualified reviewer found | Bounded admission, connection-owned cancellation, shutdown drain; negative tests (pending refresh + burst + socket close + shutdown) prove the bound; ping/status schema and refresh semantics unchanged; exact-commit different-family review; applicable REST/WS registry + route-coverage pipeline |
| **F3** (S-b) | CR-02 HA key capability: `custom_components/hdmi_matrix/api.py` + `config_flow.py` + `strings.json` + `translations/en.json` + `tests/ha/helpers.py` + `tests/ha/test_config_flow.py` | F2 not required (disjoint), but needs one qualified reviewer | Wrong/missing/revoked key rejected with a correctable error **when the hub is control-locked**; valid key accepted; offline-matrix and unlocked/no-key setup still work; bare-JSON contract handled; no disruptive probe |
| **F4** (S-c) | CR-03 shortcuts: `web/js/components/keyboard-shortcuts.js` (+ controller wiring) + `tests/e2e/*` | F3 not required (disjoint) | `'s'` and `'4'` reach the **real** settings drawer / Profiles-Scenes view; browser positive+negative tests for `s`, `4`, matrix navigation, editing-field suppression, Escape/focus; existing approved identifiers and shortcuts preserved; **no visual baseline change** (new rendering ⇒ owner approval) |
| **F5** (E) | CR-04 → CR-05 → CR-06 → CR-07, strictly sequential, on a frozen source | F2+F3+F4 merged and frozen | Credential admission complete; three chains integrated one at a time; candidate-bound F-SEC-007 with valid ancestry; no relabelled PR-merge records |
| **F6** (O) | Software RC: version/manifests/artifacts, combined validation, independent output audit | F5 | Matching amd64/arm64 artifacts bound to digests; 100% routes; schema/ledger/gate green on the actual RC |
| **F7** (O) | CR-11 physical, CR-13 72 h + field week, CR-12 final release decision | F6 + owner presence | Owner sign-off; continuous measurements; explicit owner authorisation for main/tag/artifacts |

**F0 is the only phase that can start before the owner answers anything.**
That is the single most useful thing in this report for the "continue
remediating" instruction.

---

## 7. Task-level staffing, leases, acceptance, evidence and reserves

Notation: **A** = author route, **R** = reviewer route. `R` must be a
*different underlying family* from `A` (OpenAI = {Sol, Astra, older Sol,
Luna}; MiniMax = {M3, M3.1}). Route names are **proposals for R2 challenge**;
each needs a fresh preflight (exact model, effort, quota, helpers, native
identity) at dispatch.

### 7.1 TRACK N — dispatchable now

| Task | A | R | Families | Exclusive writable paths | Base | Dependencies | Acceptance | Evidence to produce | Correction reserve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **N-1 CR-08 current-truth reconciliation** | MiniMax M3 (mine) | OpenAI `gpt-6-astra/high` | MiniMax → OpenAI ✅ independent | new `docs/validation/findings_pending.yaml` rows? **No** — registry is coordinator-owned. Use **new** prose under `docs/production/remediation-20261104/recovery-execution/` + `docs/planning/` **and** a **new** report path; **read-only** on `docs/REMEDIATION_PLAN.md`, `docs/validation/features.yaml`, `docs/validation/LEDGER.md` | `8bde6d47` (resolved integration head) | none | Every one of the parser-open rows gets an exact disposition: resolved / partial / reproduce / hardware / owner, with the surviving condition and the accepted proof reference. **HIL-09 is not closed and its 12 caps are not removed.** UC-18 and the old LICENSE-stub text are **not** called current reproduced defects. One dated authoritative current summary added; superseded narrative labelled historical | The disposition table itself, with per-row source references | 1 author fix + 1 OpenAI re-review |
| **N-2 CR-09 reproduction inventory** | MiniMax M3 (mine) | OpenAI `gpt-6-astra/high` | MiniMax → OpenAI ✅ | **new** `tests/e2e/` inventory report + **new** prose; **no** change to `web/`, **no** change to `tests/e2e/visual/__snapshots__/**` (immutable baselines) | `8bde6d47` | N-1 (needs the reconciled register first) | All 33 V1 UI/KIO features enumerated with a reproduce plan; the 2 provisional kiosk viewports flagged as owner-device-dependent and **not** silently re-baselined | Per-feature reproduce status; a browser-inventory report | 1 fix + 1 re-review |
| **N-3 CR-10 support-matrix proof (hub package, Python 3.11)** | MiniMax M3 (mine) | OpenAI `gpt-6-astra/high` | MiniMax → OpenAI ✅ | **new** `build/remediation-functional-20261104/**` (ignored) + **new** prose; **no** change to `pyproject.toml`, `requirements*.txt` or `.github/workflows/**` (coordinator-owned) — propose a **prepared diff** for the coordinator instead | `8bde6d47` | none | The hub's own test suite is executed under **Python 3.11** in an isolated environment, with the exact command, interpreter version, exit code, JUnit and failure list. If 3.11 cannot be provisioned on this host, that is recorded as an explicit environmental limitation, **not** as a product failure and **not** as a pass | Interpreter provenance, full run receipt | 1 fix + 1 re-review |
| **N-4 CR-14 capacity/qualification ledger** | MiniMax M3 (mine) | OpenAI `gpt-6-astra/high` | MiniMax → OpenAI ✅ | **new** prose + a **proposed** update to `docs/production/AGENT_ALLOCATION.md` — which is **coordinator-owned**, so this task produces a *proposed* patch, not a landed edit | `8bde6d47` | none | Every one of the 65 units' `author/review_route_reservation` is re-matched against the **actual** current qualification state (the three `QUAL-ANTHROPIC-CORE-01` dispositions), and each row is marked executable / held / needs-first-assessment | The rematch table; an explicit list of units that cannot start without Gate Q | 1 fix + 1 re-review |

**Why N-1…N-4 can start now.** Their deliverable is **prose, inventory and
environment proof**, not product source. `EXECUTION_PINS.json` names exactly
these four routes (`SW-AUDIT-01`, `SW-FINDINGS-01`, `SW-REPO-01`, `SW-DOCS-01`)
as `independent_inventory_routes`, and reserves `m3` → `sol` for them. That
pairing is genuinely cross-family. **This is the only staffing combination in
the whole programme that is currently executable without a new qualification.**
It directly satisfies the packet's instruction to *"prioritize unrelated ready
software packages instead of waiting on preferred route/privacy"* and *"scope
independent HAcredential/UIshortcut andother covered softwarework instead of
waiting forallprivacy gates"* — with the honest caveat that CR-02 and CR-03
themselves need Gate Q, while their **scoping, reproduction and inventory**
work is in Track N.

### 7.2 TRACK S — held on Gate Q

| Task | A (proposed) | R (proposed) | Exclusive writable paths | Base | Dependencies | Acceptance | Evidence | Reserve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **S-1 CR-01 wiring** | OpenAI `gpt-6.1-sol/high` (recorded core author) | **Anthropic `claude-opus-5-5/high`** *only if* Gate Q grants a non-privacy runtime/UI review domain; otherwise **a newly qualified MiniMax reviewer** — but MiniMax has no review entitlement today, so this pairing is **conditional** | `src/rest_api/app.py`, `src/rest_api/websocket.py`, `src/rest_api/tests/**` (new). **Prohibited:** `src/rest_api/ws_request_work.py` unless a coalescing change is separately approved; `src/rest_api/security.py`; `docs/validation/features.yaml`; root manifests | exact integration head at dispatch; the component's reviewed blob `145845f4` must be **unchanged** | Gate Q; the accepted component at `145845f4` | (a) `WsRequestWork(application_limit=N, owner_limit=1)` created in `create_rest_app` under a `web.AppKey`, with a `cleanup_ctx` that awaits `shutdown(timeout)`; (b) `handle_websocket` opens one owner after `ws.prepare` and awaits `owner.aclose(timeout)` in its `finally`; (c) `_handle_command` uses `owner.try_start(...)` and answers a rejection with the existing `error` event; (d) negative tests hold a refresh pending, send a burst, close one socket, and shut down — admitted task count stays bounded, all owned tasks drain, another client still works; (e) ping/status schema and refresh semantics unchanged; (f) **documented response policy** for a rejection | The test file + exact-commit different-family review + applicable REST/WS registry and route-coverage pipeline (100% routes retained) | 1 author fix + 1 re-review; **no** component re-review needed if the component bytes are unchanged |
| **S-2 CR-02 HA key capability** | OpenAI `gpt-6.1-sol/high` | Anthropic `claude-opus-5-5/high` **conditional on Gate Q** (an HA-domain qualification), else the newly qualified reviewer from Gate Q | `custom_components/hdmi_matrix/api.py`, `config_flow.py`, `strings.json`, `translations/en.json`, `tests/ha/helpers.py`, `tests/ha/test_config_flow.py`. **Prohibited:** `src/rest_api/**` (the hub side needs no change — `/api/auth/status` already exists) | integration head at dispatch | Gate Q (HA-domain review) | (a) dedicated `HubClient` method for the **bare** `/api/auth/status` body (the shared `_request` envelope contract is not bent); (b) the control-lock rule of §3.2 implemented exactly; (c) wrong/missing/revoked key on a **control-locked** hub ⇒ a correctable error with a new `invalid_auth`-style string in `strings.json` **and** `translations/en.json`; (d) valid key accepted; (e) offline matrix and unlocked/no-key setup still create an entry; (f) `MockHub` gains an `/api/auth/status` route able to return a bare body; (g) the two existing assertions are updated **deliberately**, and the `X-API-Key`-on-every-call invariant is preserved | HA-suite JUnit under the pinned plugin; the exact probe call-sequence; a real-HA reproduction attempt is **recorded as pending** if it cannot be run here | 1 author fix + 1 re-review |
| **S-3 CR-03 shortcuts** | OpenAI `gpt-6.1-sol/high` | Anthropic `claude-opus-5-5/high` **conditional on Gate Q** (a UI-behaviour review domain) | `web/js/components/keyboard-shortcuts.js` (+ the minimal controller/drawer call sites), `tests/e2e/**` (new spec). **Prohibited:** `tests/e2e/visual/__snapshots__/**` and `web/css/**` (baselines and rendering) | integration head at dispatch | Gate Q (UI review domain) | (a) `'s'` opens the **real** settings entry point (`window.settingsDrawer.open(...)` / the app's own controller — whichever the current code actually owns), not a non-existent `window.settingsPanel`; (b) `'4'` reaches the real Profiles/Scenes view (today a drawer tab, not a nav tab) — the fix must use the **existing** identifier, not invent a new one; (c) browser positive **and** negative tests for `s`, `4`, matrix navigation, editing-field suppression and Escape/focus; (d) `isTypingTarget` suppression semantics unchanged; (e) existing approved UI/entity identifiers and existing shortcuts preserved; (f) **no** visual-baseline change — any changed rendering goes to the owner for approval | Playwright spec + JUnit + the visual job showing **unchanged** baselines | 1 author fix + 1 re-review |

### 7.3 Checked alternatives, and why they were rejected

| Alternative | Why rejected |
| --- | --- |
| **Author CR-01/02/03 with MiniMax, review with OpenAI** | M3 has **no earned implementation-authorship qualification**; this would be an unassessed first implementation with no owner-funded assessment behind it. `REPO_CONFIG` records the MiniMax scope as *"Bounded evidence inventories only"*. |
| **Author CR-01/02/03 with OpenAI, review with Anthropic** (the plan's literal reservation) | Anthropic's PASS is explicitly scoped to validation-runner/API-refusal preparation and **explicitly excludes** general core review, implementation authorship and the UI/HA/image domains. Executing the reservation as written would breach the qualification record. |
| **Author with OpenAI, review with Gemini/Antigravity** | Gemini CLI OAuth disabled; Antigravity's Gemini-models weekly bucket at **~19% remaining (below 30%)**, and its **underlying family/helper identity is unresolved**, so it is not a *verified* qualified fallback. Unknown identity is not independence. |
| **Author with DeepSeek** | Owner-reported exhausted credit. Never dispatch; never buy credit. |
| **Same-family review (Sol ↔ Astra)** | Prohibited: Sol, Astra, older Sol and Luna are one OpenAI family. |
| **Reuse the D6 async-review candidate for the CR-01 wiring review** | `D6_PROVENANCE_HOLD.json`: the frozen Anthropic lifecycle-review target's independence is **unestablished** (source-attribution conflict indicators on `websocket.py`/`app.py`), `candidate_attempts_launched: 0`, `wiring_leases_granted: 0`. The hold stands; I neither widen nor narrow it. |
| **Treat the green CI as CR-01/02/03 closure** | Disproved at source (§3). |
| **Close the WS/HA/UI work by relabelling the accepted reviews** | Prohibited by `mandatory_holds.independence` and by the protocol's "no authorship relabeling". |

### 7.4 The D6 provenance strategy I can support prospectively

The packet holds D6 because the frozen Anthropic lifecycle-review target's
independence is unestablished. The **correct** discharge is **not** Git
metadata: every file in `src/rest_api/` in this repository shares one
committer identity, so `git log` cannot distinguish families — it can only
*corroborate* (e.g. `src/rest_api/ws_request_work.py` is **absent** at the
D6 baseline `12ad507e`; `websocket.py` and `app.py` have no commits after
October 2026). A **genuinely new** strategy that I can propose prospectively,
without narrowing or relabelling anything:

> **Gate Q as a new-domain assessment on a target that is provably not
> Anthropic-authored.** Pick a *different* existing-lifecycle target than
> the frozen D6 one — for example the HA component boundary
> (`custom_components/hdmi_matrix/config_flow.py` + `api.py`) or the UI
> controller boundary (`web/js/components/keyboard-shortcuts.js` +
> `settings-drawer.js`) — and discharge the provenance gate from the
> **recorded attribution** (the task record, the peer reports, the allocation
> ledger), corroborated by commit-range inspection. A PASS then yields a
> reviewer competence for *that* domain, which is what CR-02/CR-03 need, and
> it does not touch the frozen D6 target, the D6 hold, or any failed history.

This is a **new domain with a new target and a new provenance record**, not a
narrowing of the failed D6 target and not a retake of the failed Opus
attempts.

---

## 8. Capacity, honestly, as observed now

Live read from the supported Orca usage interface (`orca account list --json`),
observed during this session, 2026-11-04:

| Route | Session | Weekly | Status for this programme |
| --- | --- | --- | --- |
| `codex` (OpenAI) | not exposed | **18% used / 82% remaining**, resets Tue 11:36 PM; 2 unused reset credits | ✅ above the 30% threshold |
| `claude` (Anthropic) | 2% used / 98% remaining | **26% used / 74% remaining**, resets Fri 5:00 AM | ✅ above the threshold |
| `minimax` (MiniMax) | 4% used / 96% remaining | **35% used / 65% remaining** | ✅ above the threshold |
| `gemini` (Gemini CLI) | — | — | ❌ *"Gemini CLI OAuth is disabled in settings"* |
| `antigravity` | 4% used | **"Gemini Models" bucket 81% used → ~19% remaining**; the "Claude and GPT models" bucket's semantics are labelled "Remaining" while the field is `usedPercent`, i.e. **unresolved** | ❌ below 30% **and** unresolved family/helper semantics → **not a verified fallback** |
| `opencode-go`, `kimi`, `grok`, `cursor`, `zcode` | — | — | ❌ not configured / not signed in |
| DeepSeek | — | — | ❌ exhausted credit; never dispatch |

**Honest limitations of this capacity picture.**

1. **Capacity is not the binding constraint — qualification is.** Every route
   that matters has ample headroom *right now*. The reason CR-01/02/03 cannot
   start is that no *qualified* reviewer exists for those scopes. Reporting
   "capacity is fine" and implying "so we can start" would be false.
2. **These readings are dated observations, not a reservation.** Per
   `REPO_CONFIG.json` the coordinator must re-check the intended pool
   immediately before every creation and every start, and at least every 15
   minutes during active coordination. The `ROUND1_PREFLIGHT` figures
   (codex 16%, claude 25%, minimax 34%) and mine (18/26/35) differ by a few
   points because time passed — that drift is normal and is exactly why the
   preflight rule exists.
3. **Unknown ≠ headroom.** I did not verify Antigravity's true underlying
   model identity, and I did not attempt any login, setting change, quota
   purchase or account creation.
4. **Concurrency.** This repo's ceiling is coordinator + at most 2 new workers
   + 1 protected external reservation = 4, no nesting. The Run's fleet also
   shows many live workers **in other repositories**; those are other repos'
   reservations and are not this repo's slots. I did not treat any other
   repo's run, protected resource or qualification state as usable here.
5. **I did not launch, dispatch or reserve anything.** All numbers above are
   observations for the coordinator's use.

---

## 9. The scoped prose check — run **once**

*(This section's results are written after the run and record it; they do not
change any recommendation above.)*

### 9.1 What was run, and what it is not

**Purpose:** prove that the single prose file I authored imports and parses in
my own checkout. **It is explicitly not** product-baseline verification, not
source qualification, not a route-coverage pass, not an evidence admission and
not a product test.

**Command** (exactly the five existing documentation modules named in the
dispatch, with the two plugins the repository's own documentation-check
convention disables):

```
C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe -B -m pytest \
  tests/test_core_documentation.py tests/test_client_guides_docs.py \
  tests/test_openapi_and_config_docs.py tests/test_security_docs.py \
  tests/test_license_and_protocol_docs.py -q \
  -p no:tests.route_inventory -p no:cacheprovider \
  --basetemp=<owned>/pytest-tmp --junitxml=<owned>/junit.xml
```

Working directory: my own checkout
`C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-remediation-recovery-r1-minimax`.
Interpreter: the root virtual environment's `python.exe`, **Python 3.12.10**.

**Isolation.** `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`
and `HIDDEN_TEMP` all point at fresh roots under
`C:/t/remediation-functional/minimax-r1/prose01/`; the child environment is
`os.environ.copy()` with `PYTEST_ADDOPTS`, `PYTEST_PLUGINS`, `PYTHONPATH`,
`MATRIX_DATA_DIR` and `UC_CONFIG_HOME` dropped; bytecode is disabled by `-B`
**and** `PYTHONDONTWRITEBYTECODE=1`; `PYTHONNOUSERSITE=1`.

**Import-origin probe.** A **separate** child process imports
`tests.conftest`, `tools.validate`, `tools.validate.evidence`,
`tools.validate.runner`, `tools.validate.model`, `tools.validate.clients.api`,
`tools.validate.clients.ha` and `hub` and reports `__file__`, so the origins
are **measured from this checkout**, not assumed.

### 9.2 Actual result — from the single run

| Field | Value |
| --- | --- |
| Interpreter | root venv `C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe`, Python **3.12.10** |
| Working directory | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-remediation-recovery-r1-minimax` (**my own checkout**) |
| Direct child exit code | **0** |
| pytest summary | **`489 passed` in 3.38 s** — 0 failed, 0 errors, 0 skipped, 0 xfailed, 0 deselected |
| stdout | 580 bytes, complete (seven progress lines plus the summary line) |
| stderr | **empty (0 bytes)** |
| Wall clock | 3.988 s, `2026-11-04T17:19:41Z` → `2026-11-04T17:19:45Z` |
| JUnit | 63 691 bytes; `tests="489" failures="0" errors="0" skipped="0"`; 0 `<failure`, 0 `<error`, 0 `<skipped>` elements; SHA-256 `b5780c4039b0831050a58e2bec8e8cc4306b8d85dcae9c47f4c3dfade46a3ede` |
| Runs | **one.** No retry, no softened assertion, no skipped test counted as a pass, no unchanged failed check re-run, no bypass |
| Import-origin probe | separate child, exit **0**, stderr 0 bytes, 0.512 s |
| Measured import origins | `tests.conftest`, `tools.validate`, `tools.validate.evidence`, `tools.validate.runner`, `tools.validate.model`, `tools.validate.clients.api`, `tools.validate.clients.ha` **and `hub`** all resolve to **this checkout** (`…\wp-remediation-recovery-r1-minimax\…`) — i.e. the run exercised *my* historical snapshot, **not** the product baseline `9b783d72` |
| Isolation | `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`, `HIDDEN_TEMP`, `--basetemp` and `--junitxml` all under `C:/t/remediation-functional/minimax-r1/prose01/`; child environment = `os.environ.copy()` with `PYTEST_ADDOPTS`, `PYTEST_PLUGINS`, `PYTHONPATH`, `MATRIX_DATA_DIR`, `UC_CONFIG_HOME` dropped; `PYTHONDONTWRITEBYTECODE=1`; `PYTHONNOUSERSITE=1`; bytecode off via explicit `-B`; route-inventory and cache providers disabled via `-p no:tests.route_inventory -p no:cacheprovider` |
| Original contents preserved | pre-run inventory retained in `original_temp_contents.json`: the owned root held **4 ordinary, 0 hidden** entries before the run; the inherited system `TEMP` and `TMP` listings were captured read-only (`d28874b2…`, `68d8d90e…`). After the run the owned root holds 1 079 ordinary and 22 hidden entries (the run's own artefacts). **Note honestly:** the inherited system `TEMP`/`TMP` listing digests also changed (`a8e3299d…`, `7b39a717…`) — that is concurrent activity by **other** processes on this host in a shared directory, not by this run, whose artefacts are all inside the owned root (`--basetemp`, `--junitxml` and every `TEMP`/`TMP` path). Nothing was overwritten, moved or deleted. |
| Errors preserved | none: both children exited 0 with empty stderr |

**What this result does and does not mean.** It means the one new prose file
this worker authored imports and parses cleanly in **my own historical
checkout**. It is **not** product-baseline verification, **not** source
qualification, **not** a route-coverage pass, **not** an evidence admission
and **not** a product test. The product source was not changed and no
product behaviour was exercised.

### 9.3 Receipts and preservation

All receipts live in my owned fresh root `C:/t/remediation-functional/minimax-r1/prose01/`
(`argv.json`, `result.json`, `exit_code.txt`, `prose.stdout.txt`,
`prose.stderr.txt`, `junit.xml`, `import_origins.stdout.txt`,
`import_origins.stderr.txt`, `original_temp_contents.json`,
`after_temp_contents.json`, `env.json`) plus the runner script
`C:/t/remediation-functional/minimax-r1/scripts/run_prose_check.py`. The
pre-run inventory of ordinary and hidden entries (owned roots **and** the
inherited system `TEMP`/`TMP`, read-only) and the post-run inventory are both
retained, so the pre-existing contents are preserved and demonstrably
unmodified. **Runs: one.** No unchanged failing check was repeated, no test
was bypassed, no assertion was softened, no skip was counted as a pass, and
no source was changed.

### 9.4 Commit

The single new file is committed with the authorised **invocation-only empty
`core.hooksPath`** exception (`git -c core.hooksPath=<empty owned dir>`
against an empty directory) — the pure-prose exception. The configured
repository `pre-commit` hook runs broad Ruff lint plus the fast unit-test
suite, which is out of scope for a prose-only change. **No source hook was
bypassed for any source change, and no hook result is claimed.** Real checks
on the new file were performed first: strict UTF-8 decode without BOM,
LF-only line endings, no trailing whitespace, no tab characters, no unresolved
Markdown link targets, and the file is the only change staged.

---

## 10. Exact owner-only decisions

These are the only things I cannot decide and the only things the owner must
supply. Each has a concrete, already-reviewable option.

### O-1 — **Fund (or decline) exactly one non-privacy competence assessment.** *(Highest value; this is what "continue remediating" is actually blocked on.)*

**Why it is owner-only.** The adopted `FINAL_PACKET` `owner_questions`
records: *"An exhausted-competence-attempt budget expansion remains owner-only
if ever chosen later; not requested or authorized here."* The privacy extra
assessment (one Opus candidate + one Astra judge) is **already proposed and
unapproved** (`PRIVACY_REASSESSMENT_BUDGET_REQUEST.json`, status
`OWNER_APPROVAL_REQUIRED`). A **non-privacy** assessment has **no proposal on
record**.

**Option A (recommended).** Authorise **exactly one** bounded
**non-privacy** first assessment — route A (§4.3): a new-domain assessment for
`claude-opus-5-5` in a single bounded domain (existing-lifecycle runtime
review, or UI/HA behaviour review), under the **unchanged** frozen rubric
`66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672`, judged by
**one** `gpt-6-astra/high` judge, on a **new** target whose non-Anthropic
provenance is discharged from the recorded attribution. No retake of either
Opus 4.7 FAIL, no rewrite of failed history, no second judge, no automatic
family substitution. Cost: **one** candidate assessment + **one** judge.
**Option B.** Option A but for **MiniMax M3** in a bounded *implementation*
domain (e.g. the CR-03 browser correction), judged by `gpt-6-astra/high` —
disclosed conflict: I am the natural candidate, so the selection must be made
independently of my interest.
**Option C.** Decline. Then CR-01/CR-02/CR-03 remain held for lack of a
qualified different-family reviewer, and only Track N (CR-08/09/10/14) and
Track E (behind privacy) progress. **This is a legitimate choice** — it is a
routing constraint, not a project-wide stop.

### O-2 — Decide the **privacy** extra assessment (already pending).

The proposal on record is one Opus candidate + one Astra judge under the
unchanged six privacy axes. It remains **unapproved**. The Opus-first privacy
qualification FAIL and the M3-first privacy qualification FAIL (judge
`1b2b7c5f`, 2 PASS / 4 FAIL) remain **terminal**; no retake, no budget
expansion and no alias escape may be inferred from this report, from elapsed
time, or from the broad "continue remediating" instruction.

### O-3 — Confirm the **two provisional kiosk viewports** (CR-09).

`tests/e2e/support/viewports.ts` states the two kiosk CSS viewports are
**PROVISIONAL** and unconfirmed against the real devices, and asks for a
`whatismyviewport.com` reading *in the kiosk browser mode actually used*.
Two confirmed readings unblock the CR-09 browser proof. Without them the
kiosk projects stay provisional and must not be silently re-baselined.

### O-4 — Confirm the **HA 2025.1.0 floor claim** (CR-10).

Two sub-questions, both owner decisions rather than test outcomes:
(a) is *"Home Assistant 2025.1+"* the intended supported floor (the docs say
it at `docs/HOME_ASSISTANT.md:3` and `:628`); and (b) is the **hub package**
floor `Python >= 3.11` (per `pyproject.toml`) intended to stay, or should it
be revised to the versions actually exercised (CI runs 3.12 and 3.13)? If the
intended floors are confirmed, the missing proof is a CI/environment gap that
software work can close; if a claim should change, that is an **approved
compatibility-policy decision** (the CR-10 acceptance explicitly allows
"explicitly revise the claimed floor through approved compatibility policy").

### O-5 — Owner presence and inputs for the release-side gates (CR-11, CR-12, CR-13).

The physical matrix/firmware and attached devices; Remote/Flic/HA availability;
deployment topology; backup/restore and disruptive-action scope; an agreed
continuous 72-hour soak and field-week window; the external cache-purge
condition; and the final main/tag/artifact authorisation. **No software work
substitutes for any of these**, and no source-code workaround for absent
owner proof is acceptable.

### O-6 — Confirm the **CR-01 response policy** (bounded design, owner-optional).

Reject-only vs coalescing. Reject-only preserves the already-reviewed
component bytes and their two accepted reviews; coalescing changes reviewed
source and needs a fresh different-family review of the component. My
recommendation is reject-only first (§3.1). This is a technical choice with
a freshness consequence; if the owner prefers coalescing, it should be said
explicitly so it is not smuggled in as a wiring detail.

---

## 11. Negative findings, limits and things I did not do

1. **No currently qualified author/reviewer pair exists for CR-01, CR-02 or
   CR-03** (§4). This is the central finding and it is negative.
2. **CR-01 is bounded but not "coalesced"** by the accepted component; the
   component rejects only, and a coalescing implementation changes reviewed
   source (§3.1).
3. **CR-02's `/api/auth/status` returns a bare JSON body** that the shared
   `HubClient._request` cannot parse, and the HA test harness has no route
   for it; the HA translation strings have **no** API-key label and **no**
   invalid-credential error (§3.2).
4. **CR-03's `'s'` and `'4'` shortcuts are both silent no-ops** against the
   current application, and the keyboard-shortcut module has **no**
   behavioural test at all (§3.3).
5. **CR-09's 33 below-target UI/KIO features** are at `V1` (unit/simulator/
   screenshot level); the two kiosk viewports are provisional (§3.4).
6. **CR-10's HA 2025.1 and Python 3.11 floors are documented but never
   exercised**; the claim is provable from the repository's own pins (§3.5).
7. **The CI green at `9b783d72` closes none of CR-01…CR-10** (§3.7).
8. **I did not re-audit the privacy redaction source (CR-04)**; its status is
   attributed, not re-derived.
9. **I did not read either peer R1 report for this phase**, did not reconcile,
   and make no agreement/disagreement claim (§0, §2.3).
10. **I did not read** the full `ws_request_work.py` internals past line 359,
    the `test_ws_request_work.py` bodies, `tools/validate/evidence.py`,
    `tools/validate/clients/ha.py`, `docs/validation/LEDGER.md`, or the
    61 open register rows individually.
11. **I executed no product code, no project test, no runtime campaign, no
    ledger generation and no source hook.** The only execution is §9.
12. **My checkout is an older snapshot** than the product baseline; the
    measured import origins in §9 therefore resolve to *this* checkout, and
    that result is a **prose check of my own file**, explicitly not product
    verification and not source qualification.
13. **I did not launch, dispatch, reserve or qualify anything**, and I created
    no account, spent nothing, changed no global configuration and messaged
    no one outside Orca.
14. **Native identity/effort is recorded as the coordinator's route
    selection**, not as a backend attestation (§0).
15. **The D6 hold, the privacy holds, the owner gates and all historical
    failures are untouched.** I neither widened nor narrowed any of them.

---

## 12. Scope of this report

Prose and reasoning only. This report qualifies no route, authorises no
launch, expands no attempt budget, closes no finding, admits no evidence,
changes no source, and approves no release. Tron/visual approval, physical
HIL, the 72-hour soak, the field week and the final version/artifact release
remain owner gates that software work does not touch. The coordinator owns the
ledger, the registry, the manifests, the locks, the integration, the
preservation, the publication and the settlement of this worker.

The recommendation above is **one independent R1 contribution of three**. It
becomes nothing on its own; R2 peer challenge, one complete versioned hashed
final plan and allocation, and three explicit R3 same-hash decisions are all
still required.
