# SW-SEC-AUTH-01 independent review (initial source + final acceptance)

## Identity and scope

- **Reviewer:** deepseek/deepseek-v4-pro (DeepSeek family; native variant default/`none`, no effort override passed). Different model family from the source author (`gpt-6.1-sol`/high, OpenAI family), satisfying the cross-family review requirement.
- **Reviewed commit:** `f4ffa8d15aea519934e25a8b248992ebb074fe86` (`f4ffa8d1`), branch `ryan-haver/wp-sw-auth-review`.
- **Base:** `51275723846e4b126ccdc48c71d1727cabca4dbc`.
- **Run:** `run_37205f6095b3`. This is the **initial** source, not the final acceptance candidate.
- **Exact diff boundary** (author-owned, per `git diff 51275723..f4ffa8d1`, 6 files, +420/−3):
  - `tests/validation/scenarios/sw_sec_auth_01.py` (new, 129 lines)
  - `tests/validation/test_sw_sec_auth_01.py` (new, 115 lines)
  - `tools/validate/clients/browser.py` (+5/−0)
  - `tools/validate/clients/browser_driver.mjs` (+46/−3)
  - `docs/validation/features.yaml` (+8, coordinator-staged F-SEC-007 scenario IDs)
  - `docs/production/software-waves/SW-SEC-AUTH-01/AUTHOR.md` (new, author record)
  - Product/routes/schema/runner/root packaging/lockfiles are unchanged, as required.

## Independent verification performed

All run with the root venv interpreter
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
process-local `PYTHONPATH=src;.`, Node v24.20.0, playwright chromium revision 1243
(present in the local cache; `npm ci --ignore-scripts --no-audit --no-fund` resolved
190 packages in 4s). Route-inventory plugin disabled (`-p no:tests.route_inventory`).

| Check | Command (abridged) | Result |
| --- | --- | --- |
| Scenario DSL import + mapping | `python -c "...import sw_sec_auth_01 SCENARIOS..."` | 8 scenarios; IDs exactly match the 8 F-SEC-007 additions; `level_for` api=V2, browser=V3 |
| PBKDF2 held-verifier rendezvous + thread identity + loop lag (<100 ms) | `pytest ...::test_wrong_pin_keeps_health_responsive_during_pbkdf2` | passed (profile+scene) |
| Per-item lockout / correct-PIN cannot bypass / expiry reset | `pytest ...::test_wrong_pin_lockout_is_per_item_and_expires` | passed (profile+scene) |
| Scenario discovery (no duplicate ids) | `pytest ...::test_discovery_loads_security_hardening_without_duplicate_ids` | passed |
| **Opt-in real-Chromium UI lockout** (profile + scene) | `SW_SEC_AUTH_BROWSER_TESTS=1 pytest tests/validation/test_sw_sec_auth_01.py` | **2 passed in 36.25s** |
| Ruff (changed Python files) | `ruff check tests/validation/scenarios/sw_sec_auth_01.py tests/validation/test_sw_sec_auth_01.py tools/validate/clients/browser.py` | All checks passed |
| Node syntax | `node --check tools/validate/clients/browser_driver.mjs` | OK |
| mypy (changed Python files) | `mypy ...sw_sec_auth_01.py ...test_sw_sec_auth_01.py ...browser.py` | 2 errors (see Finding 2) |

The **5 API complements passed in 3.07s**; the **2 real-Chromium cases passed in 36.25s**.
Independent execution at the exact initial SHA reproduced the core claims through a real
browser: five real GUI wrong-PIN attempts (each HTTP 403 `invalid_passcode` with a visible
"Invalid passcode" toast; `dialogs == 5`), a locked click returning HTTP 429
`passcode_locked` with a visible "Too many wrong passcodes" message and a positive
`Retry-After` matching the body, no device write / unchanged saved JSON bytes after
refusal, correct-PIN refusal on the same locked item (429), and an independent protected
peer executing with the exact device effect. The unbounded-attempt guard (`attempts=6`)
and the negative allowed-oracle (correct PIN supplied as `wrong_passcode`) both reject as
designed. No HTTP or `page.evaluate` bypass: the probe drives `flow()` real UI clicks only.

## Findings / review disposition

1. **R1 — known, already corrected by the author (not a current UI failure).**
   `browser_driver.mjs` initializes `let promptValue = ... scene_wait_edit ? seconds : passcode`
   and then unconditionally resets `promptValue = msg.params?.passcode` before the measured
   action, overriding `scene_wait_edit`'s seconds fallback even with no probe. Confirmed in
   the frozen source and in the author's `r1-correction.patch`, which moves that reset inside
   the probe branch. The existing `scenes.wait_edit` scenario still passes pre-fix (the current
   UI uses the duration sheet, not a native prompt), so this is a native-prompt compatibility
   issue, not a reproduced UI failure. Correct handling; do not re-open as red.

2. **Minor (Low) — type errors in new test-scenario module (outside configured mypy scope).**
   `mypy` reports two `assignment` errors in `tests/validation/scenarios/sw_sec_auth_01.py:70-71`:
   `setup`/`cleanup` are inferred as `tuple[Any]` and widened by `setup += (...)` / `cleanup = (...)`.
   The configured CI/hook runs `mypy src/` only (`.github/workflows/ci.yml:86`), so this does not
   fail the configured hook and is not in shipped code. Not a security defect; noted for the author
   (annotate as `tuple[Any, ...]` if the type-checker is ever extended over `tests/`).

3. **Informational — malformed-PIN guard is defensive, not directly exercised.**
   `browser_driver.mjs` rejects a non-`/^\d{4,8}$/` `wrong_passcode` at the gate, but no
   scenario/test feeds an actually malformed PIN (e.g. `"abc"`). The `attempts=6` bound and the
   correct-PIN oracle are tested; the regex path is not. Defense-in-depth only; no defect.

4. **Informational — features.yaml F-SEC-007 `interfaces` lists only the profile-recall route.**
   The coordinator-staged mapping adds the eight scenario IDs but leaves `interfaces`
   (`POST /api/profile/{profile_id}/recall`) without the scene-execute route, even though
   `sw_sec_auth_01.scene_*` scenarios exercise `/api/v2/scenes/{scene_id}/execute`. This is
   pre-existing coordinator-owned metadata (unchanged by this commit), not a code defect.

No red/failure is fabricated. The source does not relabel API (V2) proof as V3: `locked` and
`per_item` scenarios are browser-only (V3); `wrong_pin`/`allowed` are api+browser (V2/V3).
AUTHOR.md correctly scopes this as source API/browser proof with null image digests and does
not claim deployed-image/HIL/soak/field/final-release qualification.

**Evidence freshness (corrected):** `tools/validate/gitinfo.matches` applies
directory-prefix semantics — a `covers` entry `tools/validate` matches
`tools/validate/clients/browser.py` and `browser_driver.mjs`. Two of the three F-API-002
records (`contracts.api_root`, `contracts.api_root_alias`, both at `0dd2c25e`) cover the
`tools/validate` directory, so the two pre-existing files touched by this commit (the serial
lease) **do stale those two records**. The third (`contracts.api_info`) covers only `src/`,
`run.py`, `docs/api` and `driver.json` and is not directly staled. Coordinator will rerun the
affected F-API-002 cases at the final clean source and preserve the old records; the four
preservation features do not cover these adapters, so their original `1ba` evidence remains
valid. The broad `tools/validate/*` entries in the new scenario's own `COVERS` only bound
*future* staleness of this new evidence.

## Disposition

Initial source `f4ffa8d1` is sound for its declared scope; the security invariants are
independently reproduced at the exact commit. Findings 2–4 are non-blocking. This review is
**not** final acceptance: it covers the initial source only, and the corrected source plus the
coordinator's final report/evidence assembly must be re-reviewed at the exact final SHA.

---

# Final acceptance review (`94b76fe1`)

## Identity and scope

- **Reviewer:** deepseek/deepseek-v4-pro (same native family/variant as the initial source
  review above; a different model family from the source author `gpt-6.1-sol`/high).
- **Reviewed candidate:** `94b76fe1c1232f43c0df2cd84c6378cee77f14ee` (`94b76fe1`), branch
  `ryan-haver/wp-sw-auth-review`, fast-forwarded from `141bffb2` under explicit coordinator
  authorization (`git merge --ff-only`).
- **Tested source:** `2ae46e6c8bb9c2133371c3d93509277235e5e40e` (byte-identical in the candidate).
- **Submitted author tip:** `141bffb225c8c2a5cd25f614bccf5d0ab32ec0e1`; **first source:**
  `f4ffa8d15aea519934e25a8b248992ebb074fe86`; **original base:**
  `51275723846e4b126ccdc48c71d1727cabca4dbc`.
- **Run / dispatch:** `run_37205f6095b3` / `ctx_aa7cf1ed5aab`.

## R1 correction (the only material source change)

The one-line R1 fix in `tools/validate/clients/browser_driver.mjs` moves
`promptValue = msg.params?.passcode` inside the `if (probe)` branch (immediately after
`await shot('locked')`), so a no-probe `scene_wait_edit` keeps its original `seconds`
native-prompt fallback instead of being reset to the action passcode. Verified in the
committed tree at `94b76fe1`: the reset is no longer unconditional. Semantics are correct;
this is a native-prompt compatibility fix, not a current-UI regression.

## Source-unchanged proof

`git diff 2ae46e6c..94b76fe1` touches only `AUTHOR.md` (prose),
`COORDINATOR_PREPARATION.md`, `LEDGER.md`, `features.yaml`, the 17 evidence JSON records,
the 32 PNG screenshots and the 3 run-summary JSONs. No path under `src/`, `tests/`, or
`tools/validate/` differs between the tested source `2ae46e6c` and the candidate `94b76fe1`,
so the corrected-normal-hook result (4,043 passed / 4 skipped / 35 deselected / 177/177
routes in 1,352.90 s) covers exactly the source committed here.

## Evidence, metadata, registry and ledger

- 17/17 evidence JSON records match their manifest `sha256`; manifest `source_sha`
  `2ae46e6c`, null image digests; 32 PNG screenshots valid/non-empty (LFS OIDs/sizes
  coordinator-verified).
- Manifest: `auth_clients` api=6 / browser=8; `auth_checks` 108 pass / 6 client-scoped n/a /
  0 fail; `api_root_checks` 20; corrected normal hook 4043/4/35/177/177.
- `features.yaml` F-SEC-007: `current` V1→V3; `interfaces` now includes
  `POST /api/v2/scenes/{scene_id}/execute` (resolves initial Finding 4) alongside the
  profile-recall route; 14 evidence records added.
- `features.yaml` F-API-002: `basis`/`evidence` refreshed with the three clean `2ae46e6c`
  API cases; original `0dd2c25e` records retained.
- `LEDGER.md`: F-SEC-007 now V3 fresh with evidence; F-API-002 refreshed; ledger generated
  serially, then registry/schema 33 PASS (6.15 s) and the assembled formal gate 0 known
  failures.

## Bounded replay at the final SHA

- `node --check tools/validate/clients/browser_driver.mjs` → exit 0 (Node v24.20.0).
- Scenario DSL import: 8 scenarios, IDs exactly the 8 F-SEC-007 additions; `level_for`
  api=V2, browser=V3 (no V2→V3 relabel); feature set `{F-SEC-007}`.

## Disposition

Final candidate `94b76fe1c1232f43c0df2cd84c6378cee77f14ee` is **accepted** for its declared
scope (F-SEC-007 API V2 / browser V3 source-simulator proof plus the three F-API-002 API V2
refresh records, all null image digests). Initial findings 2–4 remain non-blocking; Finding 4
is now resolved by the added scene-execute interface. This is not image/HIL/soak/field/
final-release qualification, which remain separate gates.
