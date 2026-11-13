# Fable handoff: audit remediation, 2026-11-13

Author: Claude Fable 5.2 (`claude-fable-5-2`), the original author of the commits below, same native conversation `f47fc739-3bb5-4a71-abcb-d1896c8e1fab`. Task `task_8221ac785b94`, dispatch `ctx_44dc5f1e0cc4`, Run `run_37205f6095b3`. Effort (high) and permission mode (bypass) are as the session and cutover record state them; I cannot measure them from inside.

This is an author's handoff. It is not a review, a qualification, a visual approval or a landing acceptance. Nothing is pushed or merged.

## Source

- Audited base: `wp-runtime-completion` @ `680e93b88b711369e452cdbe415415ef23ab99ed`.
- Branch `ryan-haver/audit-remediation-fable52` @ `f2a122f955def578960303bc15242fed00d01be3`, tree clean before this file. 30 files, +2037/-160.
- Input review: `C:/Users/ryanh/.gemini/antigravity-cli/brain/71673a56-d8dc-4f2c-8db6-e2afcfb4a828/codebase_review.md` (Gemini-authored; host-local).

| Commit | Scope |
| --- | --- |
| `730c0c2888386bef150d0fffee0ebd5ce9c57996` | H4, M4 |
| `3eb459197c19b3a346e02b7fc173ce0f4ead8095` | H3 |
| `38dad33c1b9801e378e71fba7c96762ecf55e25b` | H1 backend, M3 |
| `2a24a518f958996d54bcdd58c98c78221af9aaac` | H2 |
| `f2a122f955def578960303bc15242fed00d01be3` | M1, M2, L1 |

## Findings

| ID | Class | Reference and reason |
| --- | --- | --- |
| H1 UI lockout | confirmed; deferred | `settings.py` password rule is deliberate (`SECURITY.md` "Matrix host SSRF guard", `tests/test_security_ssrf_tls.py`). The forms send no password. Owner-held. |
| H1 runtime false "updated" | confirmed (new); completed | `38dad33c`: 400 before `runtime.reconfigure`; `applied` in the answer. |
| H1 DNS rebinding | confirmed; completed with an open risk | `38dad33c` `_connect_host`. See "Settings host". |
| H1 JSON 500, port 23 | confirmed; completed | `38dad33c`. `SetupWizard.connectionSetup` has no caller; left alone. |
| H2 | confirmed; completed | `2a24a518` (CR-02). |
| H3 | confirmed; completed, acceptance open | `3eb45919` (CR-01). |
| H4 500s, PIN race, caps | confirmed; completed | `730c0c28`. |
| H4 `?key=` | refuted as a defect; accepted design | `docs/REMEDIATION_PLAN.md` section 6 Phase 3, `docs/FLIC_SETUP.md` 2b. Unchanged. |
| H5 | confirmed; deferred | Fix exists unlanded on `remediation/privacy-c4` @ `a8fdbaa3`. No edit here. |
| M1 | confirmed (latent, no caller); completed | `f2a122f9`. |
| M2 | confirmed; completed | `f2a122f9` (CR-03). `unified-settings-drawer.js` stays unloaded. |
| M3 | confirmed; completed | `38dad33c`. |
| M4 | confirmed; completed | `730c0c28`. |
| M5 pyee floor | confirmed; deferred | Installed `pyee 14.0.0` requires Python >=3.12. Coordinator-owned paths. |
| M5 Dockerfile | refuted | `requirements-uc.txt` is `-r requirements.txt` (hashed), so pip enforces hashes. `run_server.py` is a documented alias. |
| L1 | confirmed; completed | `f2a122f9`. |
| L2 | confirmed; deferred | `.github/workflows/ci.yml` is coordinator-owned. Both lints exit 0 on this branch. |
| L3, L4 | accepted; no action | Debt and owner gates. |

## Unresolved choices

Items marked **contract** change an external behaviour and should not be settled by silence.

**WebSocket bounds (`3eb45919`)**
- Limit of 8 reads per hub is a constant, not configuration. Alternative: an environment setting.
- A `get_status` sent during the client's own read is coalesced, so its `status` can predate the frame. Alternative: answer `error`. **contract** (`docs/api/WEBSOCKET.md` now documents coalescing).
- The process-wide `_ws_clients` set (the `MAX_WS_CLIENTS` cap) is still global. H3's third bullet is only partly addressed.
- **Process conflict to resolve, not a design choice:** repository records hold CR-01 wiring ("no wiring grant", original component authorship `NOT_GRANTED`, `docs/agent-process/state/HANDOFF.md`). The owner handoff directed remediation of H3, and I wired it. The coordinator must decide whether this commit stands as a candidate for review or is set aside.

**Settings host (`38dad33c`)**
- Pinning stores and shows the IP, not the name. A matrix whose address changes must be saved again. **contract**
- **Open risk, unverified:** with a custom CA or fingerprint policy (`_matrix_tls_policy`), connecting by IP may fail hostname verification where the name worked. Not tested. Preferred alternative if this matters: keep the name and pin resolution in the connector (aiohttp resolver plus the Telnet connect), which is a larger change in `src/orei_matrix.py` and `src/telnet_client.py`.
- An unconfigured hub now answers 400 without a password. Before, it answered 200 and changed nothing.
- New response field `applied`; unknown scene 404 (was 400) on three scene routes. **contract**. Whether `docs/validation/features.yaml` or the ledger must change is the coordinator's call; I did not touch them. `src/hub/openapi.py` has no entry naming these fields.

**Home Assistant (`2a24a518`)**
- A hub answering 404 on `/api/auth/status` is treated as having no locks.
- Options flow writes the key to `entry.data`; "reloads once" is my reading, not asserted by a test.
- Unknown: whether `async_update_reload_and_abort(data=, options=)` exists at the declared floor HA 2025.1.0. Tested on 2026.2.3 only.

**UI (`f2a122f9`)**
- `s` opens the General drawer. Alternative: load and use `unified-settings-drawer.js`.
- Two visible text changes shipped without captures: the help overlay line "Switch to Profiles view" and the Power Cycle error toast. No markup, style or baseline change. Under the owner's UI rule these still need the owner's look.

**H1 password input (owner-held visual)**: (a) add a password field to `#settings-modal` and the General drawer, my preference; (b) defer to a UI package; (c) relax the server rule, which I advise against. The backend credential requirement stays in every option I support.

**H5 redaction**: (a) leave to `privacy-c4`, my preference, since two other unlanded chains touch the same files; (b) small fix here; (c) merge `privacy-c4` here, which would bypass its own held privacy review.

**M5**: (a) `requires-python = ">=3.12"`, my preference: one metadata line, one classifier, `CONTRIBUTING.md:44`, and the `environment_requirements` line in `REPO_CONFIG.json`; (b) constrain `pyee<14` and regenerate hashed locks, with no 3.11 CI to prove it; (c) no change.

## Evidence

All runs are mine, on this Windows host, Python 3.12.10, isolated `MATRIX_DATA_DIR`/`UC_CONFIG_HOME`.

| Check | Result |
| --- | --- |
| First complete core run (pre-commit content) | 4235 passed, 2 failed, 24 skipped. Failures: `npm run lint:js` without `node_modules`; `tests/validation/test_sw_api_read_04.py` middleware order. Both corrected before any commit; the second by keeping `cors_middleware` innermost, with that test file unchanged. |
| Pre-commit hook, each of 5 commits | 4255 passed, 0 failed, 6 skipped, 35 deselected; routes 177/177. |
| Negative controls | New tests fail on unfixed `src` (output capped, no exact count), HA component (12 failed, 105 passed), web scripts (7 failed, 1 passed). |
| `tests/ha` | 117 passed, Linux container, Python 3.13.15, HA 2026.2.3. |
| Ruff, Mypy (92 files), ESLint, Stylelint | clean |

Gaps, stated plainly:
- The hook tests the working tree, which held all changes every time. Intermediate commits were not tested in isolation.
- `tests/ha` ran before the commits on identical content, not at `f2a122f9`. It cannot run on Windows.
- Not run: `tests/uc`, Docker-marked image tests (including the two that post to `matrix-host`), any browser, `tools.validate`, hardware.
- The 6 skips were not examined one by one.
- No independent review exists. No validation level is claimed.

## Proposed grants and tests

| Work | Writable paths | Tests |
| --- | --- | --- |
| H1 option (a) | `web/index.html`, `web/js/components/settings-panel.js`, `web/js/components/general-drawer.js` | Extend `tests/test_ui_classic_api_and_shortcuts.py`; Playwright before/after captures of both forms |
| Settings-host resolver alternative | `src/rest_api/settings.py`, `src/orei_matrix.py`, `src/telnet_client.py`, `tests/test_settings_matrix_host.py`, `tests/test_security_ssrf_tls.py` | TLS custom-CA case by name and by IP |
| M5 option (a) | `pyproject.toml`, `CONTRIBUTING.md` (coordinator lease) | `tests/test_packaging_version_sync.py` |
| HA floor | none, or `tests/ha` only | Run `tests/ha` on HA 2025.1.0 |
| H5 | none on this branch | n/a |

## Caps and rules

- Credentials: tests use synthetic PINs and keys only. No environment value, credential or owner data was printed or stored. New code logs no PIN, key or password.
- No push, no merge, no force, no hook-setting change. Landing needs a read-only audit from a non-Anthropic family at the exact SHA, then the owner or spoke gate.
- A consensus vote on the choices above decides design only. It is not visual approval, not qualification and not landing acceptance. Visual before/after approval of any form change, and of the two text changes above, is the owner's alone.
- Contract items and the CR-01 grant conflict need an explicit decision. Ordinary tradeoffs can go to the two-round debate.

## Left on disk (original task, not cleaned under this dispatch)

Tagged `C:/tmp/unfoldedcircle-orei-hdmi-matrix-integration/audit-remediation-fable52/` (logs, patches, pytest temp, Mypy cache); in the worktree, ignored `node_modules/` (about 70 MB), `route-coverage.json`, `.ruff_cache/`, `src/rest_api/__pycache__/`; exited container `ha-audit-fable52`; patch scripts in the session scratchpad. All are rebuildable and should go when the original task closes.
