verdict=clean sha=f2a122f955def578960303bc15242fed00d01be3 scope=planning-only
decision=require_changes plan_sha256=f19a1d6850aa984e755f0ae83b75828a00a22670b51554d4602bdc9736214aa9

# R2 (Opus): decisions on the proposed plan

Seat: `claude-opus-5-5`, Anthropic family (same as Fable and the CR-01 author). Planning prose only, not review, qualification or authorship. Effort "high" is the launch setting; native introspection UNKNOWN. Static reading only: no tests, builds, Docker, hooks, probes or fetches. No other R2 read.

Verified: HEAD/tree `f2a122f9…`/`3384886f…`; every raw hash in `ROUND2_INPUTS.json` (`8a53d74d…`) matches, including the plan; my R1 is preserved (`6862c130…`).

"clean": no planning blocker for the eligible subsets. "require_changes": three non-material grant precisions (G1–G3); D1–D8 directions accepted. **One opinion, not consensus.**

## Positions I change from R1

- **WS coalescing: withdrawn.** Base `docs/api/WEBSOCKET.md:26` promises `status` "after a fresh read"; the candidate added coalescing and cap 8 in the same diff, so that is the contract change. My R1 argument ("refresh broadcasts found changes") fails for device-side changes after the in-flight read sampled: no later read, no event until the poller. `ADOPTION_NOTES.md:7` binds (freshness; "seeing any status is not sufficient"; read limit 4).
- **HA 404 ⇒ unlocked: withdrawn.** `/api/auth/status` first appears in `89685609` (in `v0.3.0`, not `v0.1.0`); `v0.1.0` had no locks. But `/api/health` cannot identify such a hub: `version`/`api_version` is `API_VERSION="2.10.0"` in both `v0.1.0` and HEAD (`src/rest_api/utils.py:86`, `core.py:244-245`). A wrong guess is not a bypass (the hub enforces locks), but setup succeeds with a key that later gets 401s, which is the H2 defect.
- **D3 is ordinary, not material.** Base `680e93b8` persisted and displayed the configured name; the IP substitution (`settings.py:_connect_host`) is the candidate's new contract. Restoring the base contract with connect-time validation is within owner remediation scope. Only IP-only operation would need escalation.

## Per-decision

**D1 — agree.** Keep `3eb45919` as unaccepted history; NOT_GRANTED/WSR03/D6 unchanged; the hub already carries the owner disposition.

**D2 — agree (design only, no grant).**
- **Freshness:** busy/error is the default. A single per-owner pending re-read, counted against the cap, is acceptable only if tests prove the answer was read after the request. No unbounded queue and no envelope change.
- **Caps:** application cap is 4, distinct from client cap 32. Constant 8 is rejected.
- **Ownership:** app-owned membership and broadcast (`utils.py:162,175`; module `get_event_stream()`) is a required part of H3, not optional.
- **Drain:** honest drain reporting plus fenced late replies.
- **Docs:** the `WEBSOCKET.md` text must be revised with any future correction.

**D3 — agree.**
- Keep the name for persistence, display, URL and SNI.
- Use a validating resolver on the aiohttp connector (`orei_matrix.py:717`) and resolve-validate-connect in `telnet_client.py:258`. This covers same-host port updates and reconnects.
- The CA plus verify-true matrix is required, because `_matrix_tls_policy` returns `True` under `OREI_VERIFY_SSL` (`orei_matrix.py:129-139`).

**D4 — agree, with G3.** HTTP 200 plus `applied:false`, unknown-scene 404 and default port 443 are coordinator records. `applied` already means a **list of strings** on scene apply (`docs/API_REFERENCE.md:604,758`). The matrix-host boolean `applied` must be typed separately in OpenAPI, the registry and the docs.

**D5 — agree (fail closed).**
- Missing or 404 auth capability, and a malformed 200 (no boolean `control_pin_set`, `api.py:130`), get no "unlocked" fallback.
- Supporting pre-v0.3.0 hubs is a compatibility-policy choice. That gate is still open per `ADOPTION_NOTES.md:13` and is not an ordinary default.
- Exactly-one-reload checks for options and reconfigure: reconfigure risks a double reload (`async_update_reload_and_abort` plus the `__init__.py:58` listener).
- Run on 2025.1.0 and 2026.2.3. See G1.

**D6 — agree. Reject Sol's "owner visual prerequisite before form edits"** as an uncited extra step.
- The exact rule (`REMEDIATION_PLAN.md` §5.3 step 4, last bullet) is: capture before and after every change, then present a review page for sign-off **before the PR is opened**. Baseline approval is owner-only (`visual:approve` in a separate commit; CODEOWNERS on `__snapshots__`).
- Both surfaces are catalogued (`drawer/general/*`, `modal/settings-legacy/*`, `catalog.ts:758,1105`), so before-captures are possible. New password/error states need new catalog entries. Their baselines go only into the owner-approved commit.
- Prerequisites: the pinned Linux Playwright container, and Docker being available (no CI budget). See G2.

**D7 — agree.** Map the read-only provenance. Sol's head mismatch (`53853257` vs `a8fdbaa3`) must be resolved first. No implementation lease.

**D8 — agree.**
- `>=3.12`, because `pyee==14.0.0` at `requirements.txt:641` needs it.
- L2: I drop my R1 deferral. Accept `continue-on-error` removal with a deliberate failing-lint proof, as a separate coordinator package. Note that the candidate already deleted entries from `eslint-suppressions.json`.
- MAX_DEVICES eviction is intentional and commented (`security.py:293-296`). Record it as documented behaviour. Locked-peer `_trim_failures` eviction goes to coordinator disposition. No grant either way.
- Root manifest and CI stay with the coordinator.

**Independence/admission — agree.**
- Final exact-SHA review must be independent of every implementing family. A head mixing Fable and OpenAI coordinator code needs a qualified third family (Google); planning does not qualify Argon, so that head stays held until it is.
- Fable admission waits for its pool ≥30%; no substitute author. My seat cannot review Anthropic source.

## Required grant changes (not material)

- **G1 (H2):** add `custom_components/hdmi_matrix/strings.json` and `translations/en.json` (candidate edits both); otherwise "hub too old/invalid response" falls into the misleading `cannot_connect` text.
- **G2 (UI):** name the "new owned review-artifact subtree" exactly, with a non-committed path or an explicit committed path. Assert in writing that there are no writes to `__snapshots__`, `tokens.css` or CSS.
- **G3 (coordinator REST):** add `docs/API_REFERENCE.md` for the matrix-host and scene-404 prose, and type `applied`.

## Consensus status

All three R1s already agreed on: rejecting name-to-IP replacement; keeping the credential guard and not relaxing the backend; masked password fields in both surfaces; deferring H5 without copying `privacy-c4`; M5 `>=3.12`; keeping CR-01 as an unaccepted candidate; coordinator ownership of contracts and CI.

Where I dissented in R1 (coalescing, cap, 404, global ownership, L2), I now side with the plan. R2 consensus on those still needs the unseen Sol and Argon R2 decisions on this hash. The CR-01/H5 human-only holds do not block the eligible H1, H2, UI, REST and M5/L2 subsets; owner and pool holds still apply. Nothing is irreconcilable here; no escalation beyond the existing CR-01 disposition. If G1–G3 change the hash, the revised plan needs fresh R2 decisions; this report does not approve it.

| D | Decision | Files (grant) | Tests / prerequisites |
| --- | --- | --- | --- |
| D1 | agree, hold | none | owner CR-01 disposition (hub) |
| D2 | agree, design only | none (future: websocket/ws_request_work/app/events/utils, WEBSOCKET.md) | busy-freshness, cap 4, two-app isolation, resistant drain/late reply; after D1 + qualification |
| D3 | agree | settings.py, orei_matrix.py, telnet_client.py, SECURITY.md, test_settings_matrix_host.py, test_security_ssrf_tls.py — **confirm** | name/IP/CA/verify-true/fingerprint/mixed/rebind/reconnect/same-host port, synthetic loopback |
| D4 | agree + G3 | openapi.py, features.yaml, sim reads, scenarios contracts/scenes, generated LEDGER, **+API_REFERENCE.md** | `applied` bool vs scene list, 404, 443, route 100%, serial ledger |
| D5 | agree + G1 | api.py, config_flow.py, __init__.py, tests/ha ×3, HOME_ASSISTANT.md, **+strings.json, +translations/en.json** | 404/malformed fail closed, one reload (options + reconfigure), migration/clearing, 2025.1.0 + 2026.2.3 |
| D6 | agree + G2 | index.html, settings-panel.js, general-drawer.js, UI test, flows.spec.ts, catalog.ts, **named** review path | §5.3 before → code → after → review page → owner sign-off before PR; pinned container |
| D7 | agree, defer | none | read-only chain mapping, owner budget |
| D8 | agree | pyproject, CONTRIBUTING, REPO_CONFIG, ci.yml, packaging test — **confirm** | 3.12 clean install/core; failing-lint proof; MAX_DEVICES recorded, no grant |
