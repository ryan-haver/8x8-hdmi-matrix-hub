# Software wave package briefs

Status: **execution in progress**. SW-API-READ-01 is qualified/published at API V2 after CI39467476091. Finding/repository inventories are integrated as scoped triage, without finding closure. The manifest/ledger record current per-unit states; dated earlier launch summaries are historical.

Every unit is capped at six primary features. This bounds assignment size, not duration or quota cost. If assertions/changes still exceed a bounded author/review/fix cycle, split the unit before dispatch with new exclusive files and update the manifest/ledger; never duplicate a live writer. Preserve adequate existing tests/evidence instead of implementing six new tests by default.

## SW-AUDIT: Feature and client assertion inventory

Wave W00; kind `audit`; role `inventory`; dependencies: intake/preflight only.

Reconcile every manifest feature with actual source, Scenario.features_for(client), assertions, covers, original records and current-head CI. Preserve the seven accepted EV-02 API dispositions. Produce per-feature preserve/rerun/missing-assertion/actual-defect decisions; no code edits or level changes.

**Observable acceptance:** 268 source-linked dispositions; all 147 software targets have a behavioral acceptance owner, and all 121 V4/V5 targets have software-preparation owners plus explicit external gates. Client capability gaps are enumerated before harness changes.

**Primary features:** Cross-cutting; no separate feature ownership.

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-AUDIT-01 | Cross-cutting scope above | Report/artifact paths only; source/root edits require the coordinator |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-FINDINGS: Finding and release-contract reconciliation

Wave W00; kind `audit`; role `evidence`; dependencies: intake/preflight only.

Audit every parser-open finding against the current source and original resolution/review evidence. Historical prose is not a new reproduction. Route genuine defects to exact-path corrective children and stale register rows to coordinator-owned evidence review. Check public-history/licensing and supported-runtime guarantees separately.

**Observable acceptance:** Every parser-open finding has source/proof, disposition, owner, closure condition and any external authority dependency. No historical failure, HIL cap or alternate-client disconnect limit is erased.

**Primary features:** Cross-cutting; no separate feature ownership.

**Parser-open findings to reconcile:** TST-03

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-FINDINGS-01 | Cross-cutting scope above | Report/artifact paths only; source/root edits require the coordinator |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-HARNESS: Minimal real-client assertion support

Wave W01; kind `shared_support`; role `core`; dependencies: SW-AUDIT, SW-FINDINGS.

From SW-AUDIT, identify the smallest missing client actions/observations for the next ready packages. Prefer existing intents and existing tests. Any model/runner/schema/client bridge edit requires a coordinator-issued exact-file lease and serial implementation; do not build a generic plugin framework speculatively.

**Observable acceptance:** Each new intent drives an actual supported client, observes an independent state/effect and has a meaningful refusal/counterexample. API requests through a browser context alone do not earn V3. Per-client feature mapping, schema compatibility and runner isolation pass. If no changes are needed, record an inspected no-change gate.

**Primary features:** Cross-cutting; no separate feature ownership.

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-HARNESS-01 | Cross-cutting scope above | `tests/validation/scenarios/sw_harness_01.py`<br>`tests/validation/test_sw_harness_01.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-API-READ: API foundations, configuration and WebSocket state

Wave W02; kind `software`; role `core`; dependencies: SW-HARNESS.

Exercise the complete registered read/status/root/configuration surfaces, event snapshots, poller changes and heartbeat with simulator-backed hub state. Preserve accepted original CEC/system/theme/Flic reads and their source identities. Reconcile direct WS tests into feature-attributed proof instead of relabelling unit passes.

**Observable acceptance:** Each interface has response/state assertions, applicable no-command checks and malformed/unavailable cases. WS connect/get_status/ping/pong and poller-driven snapshots have independent observations; short heartbeat tests are not a soak.

**Primary features:** F-API-002, F-API-014, F-API-016, F-API-026, F-API-028, F-API-031, F-API-032, F-API-039, F-API-040, F-API-042

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-API-READ-01 | F-API-002 | `tests/validation/scenarios/sw_api_read_01.py`<br>`tests/validation/test_sw_api_read_01.py` |
| SW-API-READ-02 | F-API-014, F-API-016, F-API-026, F-API-028 | `tests/validation/scenarios/sw_api_read_02.py`<br>`tests/validation/test_sw_api_read_02.py` |
| SW-API-READ-03 | F-API-039, F-API-040, F-API-042 | `tests/validation/scenarios/sw_api_read_03.py`<br>`tests/validation/test_sw_api_read_03.py` |
| SW-API-READ-04 | F-API-031, F-API-032 | `tests/validation/scenarios/sw_api_read_04.py`<br>`tests/validation/test_sw_api_read_04.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-SEC-AUTH: Authentication, request guards and client access

Wave W02; kind `software`; role `core`; dependencies: SW-HARNESS.

Cover admin/control PINs, current-PIN changes, rate limits, proxy trust, origins/host/content type, SSRF and Remote integration authentication. Use real clients for V3 claims. Coordinate auth fixtures; never touch private root configuration or use the owner deployment.

**Observable acceptance:** No-PIN/admin-PIN/admin-plus-control-PIN matrix with allowed and denied effects, token/API-key privileges, no device command or saved-state mutation on refusal, lock/reset cleanup and secret-free logs. A 200 or an API-only pass is insufficient V3 proof.

**Primary features:** F-SEC-001, F-SEC-002, F-SEC-003, F-SEC-006, F-SEC-007, F-SEC-008, F-SEC-009, F-SEC-015

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-SEC-AUTH-01 | F-SEC-007 | `tests/validation/scenarios/sw_sec_auth_01.py`<br>`tests/validation/test_sw_sec_auth_01.py` |
| SW-SEC-AUTH-02 | F-SEC-009, F-SEC-015 | `tests/validation/scenarios/sw_sec_auth_02.py`<br>`tests/validation/test_sw_sec_auth_02.py` |
| SW-SEC-AUTH-03 | F-SEC-001, F-SEC-002, F-SEC-003, F-SEC-006, F-SEC-008 | `tests/validation/scenarios/sw_sec_auth_03.py`<br>`tests/validation/test_sw_sec_auth_03.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-API-WRITE: API writes, grouped resources and event contracts

Wave W03; kind `software`; role `core`; dependencies: SW-API-READ, SW-SEC-AUTH.

Complete grouped device settings, profile/legacy/v2-scene/macro/shortcut/layout/settings routes, response envelopes, mutation events and refused writes. Connect existing domain assertions where adequate. Preserve input-name V2 evidence; inspect complete registered interface groups before accepting a feature.

**Observable acceptance:** Saved-value GET/readback, exact simulator command/payload/count where applicable, unrelated-state invariants and refusal/no-success-event checks. Cover successful user-shortcut deletion, preset favorite/dashboard operations, scene execution/history and safe matrix-host auth cases. Required REST route coverage stays 100%.

**Primary features:** F-API-008, F-API-010, F-API-011, F-API-012, F-API-013, F-API-017, F-API-018, F-API-019, F-API-020, F-API-021, F-API-022, F-API-023, F-API-024, F-API-025, F-API-027, F-API-030, F-API-036, F-API-037, F-API-038, F-API-041

**Parser-open findings to reconcile:** API-16, API-21

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-API-WRITE-01 | F-API-008, F-API-010, F-API-011, F-API-012, F-API-013, F-API-017 | `tests/validation/scenarios/sw_api_write_01.py`<br>`tests/validation/test_sw_api_write_01.py` |
| SW-API-WRITE-02 | F-API-018, F-API-019, F-API-020, F-API-021, F-API-022, F-API-023 | `tests/validation/scenarios/sw_api_write_02.py`<br>`tests/validation/test_sw_api_write_02.py` |
| SW-API-WRITE-03 | F-API-024, F-API-025, F-API-027, F-API-030, F-API-036, F-API-037 | `tests/validation/scenarios/sw_api_write_03.py`<br>`tests/validation/test_sw_api_write_03.py` |
| SW-API-WRITE-04 | F-API-038, F-API-041 | `tests/validation/scenarios/sw_api_write_04.py`<br>`tests/validation/test_sw_api_write_04.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-SEC-DATA: Stored secrets, browser escaping, TLS and opaque errors

Wave W03; kind `software`; role `core`; dependencies: SW-SEC-AUTH.

Inspect actual PBKDF2 storage and absent hash/credential fields, XSS rendering in main UI/kiosk, static traversal, error correlation/redaction, TLS verification/pinning using isolated local endpoints, and logs. Existing security tests are starting evidence, not automatic V3 records.

**Observable acceptance:** Client-visible rendering and independent storage/network observations; hostile names, malformed requests, wrong trust/certificate and path cases. Prove deny/no-leak effects in all applicable auth configurations. Never disable verification to pass a test.

**Primary features:** F-SEC-004, F-SEC-005, F-SEC-010, F-SEC-011, F-SEC-012, F-SEC-013, F-SEC-014

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-SEC-DATA-01 | F-SEC-004, F-SEC-005, F-SEC-010, F-SEC-011, F-SEC-012, F-SEC-013 | `tests/validation/scenarios/sw_sec_data_01.py`<br>`tests/validation/test_sw_sec_data_01.py` |
| SW-SEC-DATA-02 | F-SEC-014 | `tests/validation/scenarios/sw_sec_data_02.py`<br>`tests/validation/test_sw_sec_data_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-API-CLIENT: Real-client routing, power, CEC and API presentation

Wave W04; kind `software`; role `core`; dependencies: SW-API-WRITE, SW-HARNESS.

Attribute actual client requests/events plus device effects for V3 API claims: health/docs/status/static delivery, routing/source cycling/presets/power/CEC and success/failure broadcasts. Use client-specific mapping after proving the API feature itself, rather than borrowing a matrix/UI feature label.

**Observable acceptance:** Real-client action/presentation plus observed request/event and independent simulator effect. Correlate one/all routing and rejected operations without duplicate events; API V2 alone and screenshot-only claims do not satisfy V3.

**Primary features:** F-API-001, F-API-003, F-API-004, F-API-005, F-API-006, F-API-007, F-API-009, F-API-015, F-API-029, F-API-033, F-API-034, F-API-035

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-API-CLIENT-01 | F-API-001, F-API-003, F-API-004, F-API-005, F-API-006, F-API-007 | `tests/validation/scenarios/sw_api_client_01.py`<br>`tests/validation/test_sw_api_client_01.py` |
| SW-API-CLIENT-02 | F-API-009, F-API-015, F-API-029, F-API-033, F-API-034, F-API-035 | `tests/validation/scenarios/sw_api_client_02.py`<br>`tests/validation/test_sw_api_client_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-DOM-PROFILE: Profile management, capture, PINs and legacy aliases

Wave W04; kind `software`; role `core`; dependencies: SW-API-WRITE, SW-SEC-AUTH.

Drive create/edit/delete, favorites/pins/order, CEC target selection, execution history and save-current-state through the real UI/client. Reconcile legacy v1 profile aliases independently at their V2 target. Reuse original adequate legacy evidence where justified.

**Observable acceptance:** Persisted client-visible results plus independent API/storage/device observations; cancel/wrong-PIN/missing-item/invalid target failures leave unrelated state unchanged. Legacy and v2 data coexist without destructive migration.

**Primary features:** F-DOM-001, F-DOM-005, F-DOM-006, F-DOM-007, F-DOM-008, F-DOM-009, F-DOM-018

**Parser-open findings to reconcile:** API-18, API-19, API-25, UI-36

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-DOM-PROFILE-01 | F-DOM-001, F-DOM-005, F-DOM-006, F-DOM-007, F-DOM-008, F-DOM-009 | `tests/validation/scenarios/sw_dom_profile_01.py`<br>`tests/validation/test_sw_dom_profile_01.py` |
| SW-DOM-PROFILE-02 | F-DOM-018 | `tests/validation/scenarios/sw_dom_profile_02.py`<br>`tests/validation/test_sw_dom_profile_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-DOM-SCENE: Scene editing, validation, overrides and history

Wave W05; kind `software`; role `core`; dependencies: SW-DOM-PROFILE, SW-SEC-DATA.

Real-client scene CRUD, mixed wait/shortcut steps, overrides, conflict validation, protected changes and execution history. Preserve previously accepted supported cancellation and partial-execution semantics.

**Observable acceptance:** Client editing and persisted results, expected ordered simulator effects/history and realistic missing/invalid/cancel cases. No arbitrary alternate-client quiescence guarantee is invented.

**Primary features:** F-DOM-010, F-DOM-013, F-DOM-014, F-DOM-015, F-DOM-016, F-DOM-017

**Parser-open findings to reconcile:** UI-19

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-DOM-SCENE-01 | F-DOM-010, F-DOM-013, F-DOM-014, F-DOM-015, F-DOM-016, F-DOM-017 | `tests/validation/scenarios/sw_dom_scene_01.py`<br>`tests/validation/test_sw_dom_scene_01.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-DOM-MACRO: Macro editing, validation and dry-run

Wave W05; kind `software`; role `core`; dependencies: SW-API-WRITE, SW-SEC-AUTH.

Real-client macro CRUD, target selection/limits, favorites/dashboard placement and dry-run. Use an independent command oracle; dry-run must not transmit CEC or alter stored steps/device state.

**Observable acceptance:** Client-visible persisted steps/targets and refusal behavior; dry-run command plan/duration and zero transmission verified separately from actual execution.

**Primary features:** F-DOM-019, F-DOM-021, F-DOM-022

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-DOM-MACRO-01 | F-DOM-019, F-DOM-021, F-DOM-022 | `tests/validation/scenarios/sw_dom_macro_01.py`<br>`tests/validation/test_sw_dom_macro_01.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-DOM-SHORTCUT: Built-in and user shortcut behavior

Wave W06; kind `software`; role `core`; dependencies: SW-API-WRITE, SW-DOM-MACRO.

Drive built-in routing/power/mute/preset/hardware-setting shortcuts and user shortcut rename/reorder/delete/favorites through the real client against a simulator. Validate LCD/scaler tables against preserved protocol evidence, without claiming physical effects.

**Observable acceptance:** Exact simulated device effects, persisted ordering and correct failure/confirmation/cancel behavior. Reboot remains simulator-only here; no physical or disruptive owner action.

**Primary features:** F-DOM-023, F-DOM-024, F-DOM-025, F-DOM-026, F-DOM-027, F-DOM-028, F-DOM-029, F-DOM-030

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-DOM-SHORTCUT-01 | F-DOM-023, F-DOM-024, F-DOM-025, F-DOM-026, F-DOM-027, F-DOM-028 | `tests/validation/scenarios/sw_dom_shortcut_01.py`<br>`tests/validation/test_sw_dom_shortcut_01.py` |
| SW-DOM-SHORTCUT-02 | F-DOM-029, F-DOM-030 | `tests/validation/scenarios/sw_dom_shortcut_02.py`<br>`tests/validation/test_sw_dom_shortcut_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-DOM-PRESENT: Dashboard, device metadata, presets and preferences

Wave W06; kind `software`; role `core`; dependencies: SW-DOM-PROFILE, SW-DOM-MACRO, SW-DOM-SHORTCUT.

Prove dashboard add/remove/reorder and deletion reconciliation, icons/colors/display names, favorite/dashboard presets, custom routing preset save, themes and hub-stored UI preferences through the real client.

**Observable acceptance:** Reload/restart readback, independent saved state and rendered card/order/name effects, plus refusal/cancel/storage-failure cases where relevant. No dual-store migration or orphan-card regression.

**Primary features:** F-DOM-031, F-DOM-032, F-DOM-033, F-DOM-034, F-DOM-035, F-DOM-036

**Parser-open findings to reconcile:** API-20, UI-08

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-DOM-PRESENT-01 | F-DOM-031, F-DOM-032, F-DOM-033, F-DOM-034, F-DOM-035, F-DOM-036 | `tests/validation/scenarios/sw_dom_present_01.py`<br>`tests/validation/test_sw_dom_present_01.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-UI-CONTROL: Main UI control, status and recovery

Wave W07; kind `software`; role `ui`; dependencies: SW-API-CLIENT.

Exercise grid/card/all-output routing, preset recall/rename/save, input/output settings, CEC controls, live updates, reconnect and disconnected/error presentation using shipped UI against real hub plus simulator.

**Observable acceptance:** Visible client outcome and independent effects, interleaved/late REST versus WS controls, truthful unavailable state, denied/cancel behavior and no duplicate actions. No intercepted fake response stands in for real hub behavior except explicitly bounded hostile-payload tests.

**Primary features:** F-UI-001, F-UI-002, F-UI-003, F-UI-004, F-UI-005, F-UI-006, F-UI-007, F-UI-010, F-UI-011, F-UI-017, F-UI-024, F-UI-025, F-UI-026, F-UI-027

**Parser-open findings to reconcile:** UI-12

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-UI-CONTROL-01 | F-UI-001, F-UI-002, F-UI-003, F-UI-004, F-UI-005, F-UI-006 | `tests/validation/scenarios/sw_ui_control_01.py`<br>`tests/validation/test_sw_ui_control_01.py` |
| SW-UI-CONTROL-02 | F-UI-007, F-UI-010, F-UI-011, F-UI-017, F-UI-024, F-UI-025 | `tests/validation/scenarios/sw_ui_control_02.py`<br>`tests/validation/test_sw_ui_control_02.py` |
| SW-UI-CONTROL-03 | F-UI-026, F-UI-027 | `tests/validation/scenarios/sw_ui_control_03.py`<br>`tests/validation/test_sw_ui_control_03.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-UI-MANAGE: Main UI editors, drawers and onboarding

Wave W07; kind `software`; role `ui`; dependencies: SW-DOM-SCENE, SW-DOM-MACRO, SW-DOM-SHORTCUT.

Verify dashboard management, profile/scene/macro editors, protected actions, shortcuts/integrations, tab personalization, automation endpoint copy and first-run setup. Prefer real-client existing flow tests and add only missing assertions/mappings.

**Observable acceptance:** Client persistence/effects and focus/cancel/error paths; live-origin endpoint copying; valid/invalid onboarding and auth states; served assets have no page errors. Product fixes require exact-file corrective leases.

**Primary features:** F-UI-008, F-UI-009, F-UI-012, F-UI-013, F-UI-014, F-UI-015, F-UI-016, F-UI-022, F-UI-023, F-UI-034, F-UI-035, F-UI-036

**Parser-open findings to reconcile:** UI-05, UI-14, UI-15, UI-18, UI-20

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-UI-MANAGE-01 | F-UI-008, F-UI-009, F-UI-012, F-UI-013, F-UI-014, F-UI-015 | `tests/validation/scenarios/sw_ui_manage_01.py`<br>`tests/validation/test_sw_ui_manage_01.py` |
| SW-UI-MANAGE-02 | F-UI-016, F-UI-022, F-UI-023, F-UI-034, F-UI-035, F-UI-036 | `tests/validation/scenarios/sw_ui_manage_02.py`<br>`tests/validation/test_sw_ui_manage_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-UI-PRESENT: Presentation, accessibility, settings and visual regression

Wave W08; kind `software`; role `ui`; dependencies: SW-DOM-PRESENT, SW-SEC-DATA.

Themes/interface/general/hardware-settings presentation, keyboard/focus/ARIA/zoom, debug/about, reduced motion/Tron and phone/tablet layouts. Reconcile parser-open UI findings to current source; retain the three accepted Tron snapshots unchanged.

**Observable acceptance:** Meaningful keyboard/focus/contrast/responsive assertions plus functional client effects. Pinned visual comparisons; new differences remain owner-pending, never auto-approved or silently normalized.

**Primary features:** F-UI-018, F-UI-019, F-UI-020, F-UI-021, F-UI-028, F-UI-029, F-UI-030, F-UI-031, F-UI-032, F-UI-033

**Parser-open findings to reconcile:** TST-04, UI-06, UI-07, UI-09, UI-10, UI-13, UI-16, UI-21, UI-33, UI-35, UI-41

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-UI-PRESENT-01 | F-UI-018, F-UI-019, F-UI-020, F-UI-021, F-UI-028, F-UI-029 | `tests/validation/scenarios/sw_ui_present_01.py`<br>`tests/validation/test_sw_ui_present_01.py` |
| SW-UI-PRESENT-02 | F-UI-030, F-UI-031, F-UI-032, F-UI-033 | `tests/validation/scenarios/sw_ui_present_02.py`<br>`tests/validation/test_sw_ui_present_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-KIOSK-CONTROL: Kiosk routing, presets, shortcuts, profiles and CEC

Wave W08; kind `software`; role `ui`; dependencies: SW-DOM-PROFILE, SW-DOM-SHORTCUT, SW-API-CLIENT.

Touch/client flows for routing, preset configuration, shortcut slots, profile wizard and CEC, including authorized and refused operations against a simulator-backed hub.

**Observable acceptance:** Client-observed effects and persisted configuration, modal/dropdown bounds, touch and cancel/refusal behavior; no physical display/CEC claim.

**Primary features:** F-KIO-002, F-KIO-003, F-KIO-005, F-KIO-006, F-KIO-007, F-KIO-008, F-KIO-009

**Parser-open findings to reconcile:** UI-40, UI-42

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-KIOSK-CONTROL-01 | F-KIO-002, F-KIO-003, F-KIO-005, F-KIO-006, F-KIO-007, F-KIO-008 | `tests/validation/scenarios/sw_kiosk_control_01.py`<br>`tests/validation/test_sw_kiosk_control_01.py` |
| SW-KIOSK-CONTROL-02 | F-KIO-009 | `tests/validation/scenarios/sw_kiosk_control_02.py`<br>`tests/validation/test_sw_kiosk_control_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-KIOSK-STATE: Kiosk state, themes, layout persistence and accessibility

Wave W09; kind `software`; role `ui`; dependencies: SW-KIOSK-CONTROL, SW-DOM-PRESENT.

Connection/status tiles, live updates/disconnect, persisted layout/pins and selected themes, long names and touch accessibility. Inspect separate kiosk code paths instead of inheriting main-UI passes.

**Observable acceptance:** Reload/restart and cross-client updates verified independently, truthful unavailable state, nonclipped phone/tablet layouts, ARIA/touch/contrast checks. New snapshots require separate owner decision.

**Primary features:** F-KIO-001, F-KIO-004, F-KIO-010, F-KIO-011, F-KIO-012, F-KIO-013, F-KIO-014

**Parser-open findings to reconcile:** UI-11, UI-34, UI-38, UI-39

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-KIOSK-STATE-01 | F-KIO-001, F-KIO-004, F-KIO-010, F-KIO-011, F-KIO-012, F-KIO-013 | `tests/validation/scenarios/sw_kiosk_state_01.py`<br>`tests/validation/test_sw_kiosk_state_01.py` |
| SW-KIOSK-STATE-02 | F-KIO-014 | `tests/validation/scenarios/sw_kiosk_state_02.py`<br>`tests/validation/test_sw_kiosk_state_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-FLIC: Flic replay, generated requests and auth regression

Wave W09; kind `software`; role `bounded`; dependencies: SW-API-WRITE, SW-SEC-AUTH.

Requalify all ten Flic software targets with the existing SDK stub/replay and generated-request flow; include preset/power/CEC/twist/profile/macro/registration/template operations and control-PIN allowed/denied behavior.

**Observable acceptance:** Inspect actual generated request and independent simulator effects, correct client feature mapping, reconnect/error/cancel where supported. SDK-stub replay is explicit; physical buttons/Twist remain external.

**Primary features:** F-FLIC-001, F-FLIC-002, F-FLIC-003, F-FLIC-004, F-FLIC-005, F-FLIC-006, F-FLIC-007, F-FLIC-008, F-FLIC-009, F-FLIC-010

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-FLIC-01 | F-FLIC-001, F-FLIC-002, F-FLIC-003, F-FLIC-004, F-FLIC-005, F-FLIC-006 | `tests/validation/scenarios/sw_flic_01.py`<br>`tests/validation/test_sw_flic_01.py` |
| SW-FLIC-02 | F-FLIC-007, F-FLIC-008, F-FLIC-009, F-FLIC-010 | `tests/validation/scenarios/sw_flic_02.py`<br>`tests/validation/test_sw_flic_02.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-PROTOCOL-PREP: Protocol and matrix software prerequisites

Wave W10; kind `physical_preparation`; role `core`; dependencies: SW-AUDIT, SW-FINDINGS.

Audit all matrix/CEC features against immutable real captures, simulator behavior and existing command/readback tests; replay malformed/slow/refused commands. Prepare exact missing capture/restore/operator questions for HIL-03/09/14; preserve caps.

**Observable acceptance:** Per-feature V2/V3 prerequisite disposition, source-linked command table/replay assertions and reversible hardware handoff instructions. No matrix connection, new physical observation or V4 promotion.

**Primary features:** F-MTX-001, F-MTX-002, F-MTX-003, F-MTX-004, F-MTX-005, F-MTX-006, F-MTX-007, F-MTX-008, F-MTX-009, F-MTX-010, F-MTX-011, F-MTX-012, F-MTX-013, F-MTX-014, F-MTX-015, F-MTX-016, F-MTX-017, F-MTX-018, F-MTX-019, F-MTX-020, F-MTX-021, F-MTX-022, F-MTX-023, F-MTX-024, F-MTX-025, F-MTX-026, F-MTX-027, F-MTX-028, F-MTX-029, F-MTX-030, F-MTX-031, F-CEC-001, F-CEC-002, F-CEC-003, F-CEC-004, F-CEC-005, F-CEC-006, F-CEC-007, F-CEC-008, F-CEC-009, F-CEC-010, F-CEC-011

**Parser-open findings to reconcile:** BE-14, BE-15, BE-25, API-07, HIL-03, HIL-09, HIL-14

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-PROTOCOL-PREP-01 | F-MTX-001, F-MTX-002, F-MTX-003, F-MTX-004, F-MTX-005, F-MTX-006 | `tests/validation/scenarios/sw_protocol_prep_01.py`<br>`tests/validation/test_sw_protocol_prep_01.py` |
| SW-PROTOCOL-PREP-02 | F-MTX-007, F-MTX-008, F-MTX-009, F-MTX-010, F-MTX-011, F-MTX-012 | `tests/validation/scenarios/sw_protocol_prep_02.py`<br>`tests/validation/test_sw_protocol_prep_02.py` |
| SW-PROTOCOL-PREP-03 | F-MTX-013, F-MTX-014, F-MTX-015, F-MTX-016, F-MTX-017, F-MTX-018 | `tests/validation/scenarios/sw_protocol_prep_03.py`<br>`tests/validation/test_sw_protocol_prep_03.py` |
| SW-PROTOCOL-PREP-04 | F-MTX-019, F-MTX-020, F-MTX-021, F-MTX-022, F-MTX-023, F-MTX-024 | `tests/validation/scenarios/sw_protocol_prep_04.py`<br>`tests/validation/test_sw_protocol_prep_04.py` |
| SW-PROTOCOL-PREP-05 | F-MTX-025, F-MTX-026, F-MTX-027, F-MTX-028, F-MTX-029, F-MTX-030 | `tests/validation/scenarios/sw_protocol_prep_05.py`<br>`tests/validation/test_sw_protocol_prep_05.py` |
| SW-PROTOCOL-PREP-06 | F-MTX-031, F-CEC-001, F-CEC-002, F-CEC-003, F-CEC-004, F-CEC-005 | `tests/validation/scenarios/sw_protocol_prep_06.py`<br>`tests/validation/test_sw_protocol_prep_06.py` |
| SW-PROTOCOL-PREP-07 | F-CEC-006, F-CEC-007, F-CEC-008, F-CEC-009, F-CEC-010, F-CEC-011 | `tests/validation/scenarios/sw_protocol_prep_07.py`<br>`tests/validation/test_sw_protocol_prep_07.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-RUNTIME-PREP: Runtime, persistence, deployment and reliability prerequisites

Wave W10; kind `physical_preparation`; role `runtime`; dependencies: SW-AUDIT, SW-FINDINGS.

Reconcile all ops and reliability software paths: lifecycle/reconnect/polling/ownership, auth/session expiry, concurrent writes/migration/process lock, caches/backpressure, event-loop/metrics/configuration and supported error/cancel guarantees. Use source plus disposable containers/simulator faults.

**Observable acceptance:** Actual startup/rollback/restore and bounded cancellation invariants, installed/normal-image entry parity, no leaked resources, isolated configuration and retained historical failed alternate-client probe. V4/V5 and owner host remain unqualified.

**Primary features:** F-OPS-001, F-OPS-002, F-OPS-003, F-OPS-004, F-OPS-005, F-OPS-006, F-OPS-007, F-OPS-008, F-OPS-009, F-OPS-010, F-OPS-011, F-OPS-012, F-OPS-013, F-OPS-014, F-OPS-015, F-OPS-016, F-OPS-017, F-OPS-018, F-OPS-019, F-OPS-020, F-REL-001, F-REL-002, F-REL-003, F-REL-004, F-REL-005, F-REL-006, F-REL-007, F-REL-008, F-REL-009, F-REL-010, F-REL-011, F-REL-012, F-REL-013, F-REL-014, F-REL-015, F-REL-016, F-REL-017

**Parser-open findings to reconcile:** BE-16, BE-23, BE-24, BE-26, BE-33, API-12, PER-04, DEP-07

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-RUNTIME-PREP-01 | F-OPS-001, F-OPS-002, F-OPS-003, F-OPS-004, F-OPS-005, F-OPS-006 | `tests/validation/scenarios/sw_runtime_prep_01.py`<br>`tests/validation/test_sw_runtime_prep_01.py` |
| SW-RUNTIME-PREP-02 | F-OPS-007, F-OPS-008, F-OPS-009, F-OPS-010, F-OPS-011, F-OPS-012 | `tests/validation/scenarios/sw_runtime_prep_02.py`<br>`tests/validation/test_sw_runtime_prep_02.py` |
| SW-RUNTIME-PREP-03 | F-OPS-013, F-OPS-014, F-OPS-015, F-OPS-016, F-OPS-017, F-OPS-018 | `tests/validation/scenarios/sw_runtime_prep_03.py`<br>`tests/validation/test_sw_runtime_prep_03.py` |
| SW-RUNTIME-PREP-04 | F-OPS-019, F-OPS-020, F-REL-001, F-REL-002, F-REL-003, F-REL-004 | `tests/validation/scenarios/sw_runtime_prep_04.py`<br>`tests/validation/test_sw_runtime_prep_04.py` |
| SW-RUNTIME-PREP-05 | F-REL-005, F-REL-006, F-REL-007, F-REL-008, F-REL-009, F-REL-010 | `tests/validation/scenarios/sw_runtime_prep_05.py`<br>`tests/validation/test_sw_runtime_prep_05.py` |
| SW-RUNTIME-PREP-06 | F-REL-011, F-REL-012, F-REL-013, F-REL-014, F-REL-015, F-REL-016 | `tests/validation/scenarios/sw_runtime_prep_06.py`<br>`tests/validation/test_sw_runtime_prep_06.py` |
| SW-RUNTIME-PREP-07 | F-REL-017 | `tests/validation/scenarios/sw_runtime_prep_07.py`<br>`tests/validation/test_sw_runtime_prep_07.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-UC-PREP: Remote software and SDK prerequisites

Wave W11; kind `physical_preparation`; role `runtime`; dependencies: SW-RUNTIME-PREP, SW-PROTOCOL-PREP, SW-SEC-AUTH.

Scripted Remote discovery/setup/reconfigure, entities/events/renames/auth, standby/wake and offline recovery. Reconcile UC findings against SDK contracts and accepted runtime limits. Prepare owner steps for actual Remote rediscovery/firmware constraints.

**Observable acceptance:** Real SDK/scripted-client effects, unavailable state, no duplicate pollers/actions and token-free logs; SDK lacks an entity-definition update event, so document supported owner reload behavior rather than inventing it. No physical Remote V4 proof.

**Primary features:** F-UC-001, F-UC-002, F-UC-003, F-UC-004, F-UC-005, F-UC-006, F-UC-007, F-UC-008, F-UC-009, F-UC-010, F-UC-011, F-UC-012, F-UC-013, F-UC-014, F-UC-015, F-UC-016, F-UC-017

**Parser-open findings to reconcile:** BE-20, BE-22, UC-10, UC-11, UC-12, UC-13, UC-18, UC-28

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-UC-PREP-01 | F-UC-001, F-UC-002, F-UC-003, F-UC-004, F-UC-005, F-UC-006 | `tests/validation/scenarios/sw_uc_prep_01.py`<br>`tests/validation/test_sw_uc_prep_01.py` |
| SW-UC-PREP-02 | F-UC-007, F-UC-008, F-UC-009, F-UC-010, F-UC-011, F-UC-012 | `tests/validation/scenarios/sw_uc_prep_02.py`<br>`tests/validation/test_sw_uc_prep_02.py` |
| SW-UC-PREP-03 | F-UC-013, F-UC-014, F-UC-015, F-UC-016, F-UC-017 | `tests/validation/scenarios/sw_uc_prep_03.py`<br>`tests/validation/test_sw_uc_prep_03.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-HA-PREP: Home Assistant software and packaging prerequisites

Wave W11; kind `physical_preparation`; role `bounded`; dependencies: SW-RUNTIME-PREP, SW-PROTOCOL-PREP, SW-SEC-AUTH.

Disposable real HA container config/reconfigure/options, entities/services targeting, auth and offline behavior; hassfest/HACS and supported-version/install floors. Reconcile any nominal minimum-floor gap explicitly; owner HA/LAN untouched.

**Observable acceptance:** Actual HA client behavior and component tests in recorded supported environments, correct config-entry targeting and no secret disclosure. Installer/mDNS/LAN and owner deployment checks remain external where not reproducible in isolation.

**Primary features:** F-HA-001, F-HA-002, F-HA-003, F-HA-004, F-HA-005, F-HA-006, F-HA-007, F-HA-008, F-HA-009, F-HA-010, F-HA-011, F-HA-012, F-HA-013, F-HA-014, F-HA-015, F-HA-016, F-HA-017, F-HA-018

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-HA-PREP-01 | F-HA-001, F-HA-002, F-HA-003, F-HA-004, F-HA-005, F-HA-006 | `tests/validation/scenarios/sw_ha_prep_01.py`<br>`tests/validation/test_sw_ha_prep_01.py` |
| SW-HA-PREP-02 | F-HA-007, F-HA-008, F-HA-009, F-HA-010, F-HA-011, F-HA-012 | `tests/validation/scenarios/sw_ha_prep_02.py`<br>`tests/validation/test_sw_ha_prep_02.py` |
| SW-HA-PREP-03 | F-HA-013, F-HA-014, F-HA-015, F-HA-016, F-HA-017, F-HA-018 | `tests/validation/scenarios/sw_ha_prep_03.py`<br>`tests/validation/test_sw_ha_prep_03.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-DOM-HIL-PREP: Physical domain execution prerequisites

Wave W12; kind `physical_preparation`; role `core`; dependencies: SW-DOM-SCENE, SW-DOM-MACRO, SW-PROTOCOL-PREP.

Consolidate software proof for six hardware-target profile/scene/macro effects and the precise owner observation/restore sequence, including failures, partial execution and overrides.

**Observable acceptance:** Simulator-backed independent effects and per-feature handoff ready; actual attached-device effects and V4 acceptance remain deferred.

**Primary features:** F-DOM-002, F-DOM-003, F-DOM-004, F-DOM-011, F-DOM-012, F-DOM-020

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-DOM-HIL-PREP-01 | F-DOM-002, F-DOM-003, F-DOM-004, F-DOM-011, F-DOM-012, F-DOM-020 | `tests/validation/scenarios/sw_dom_hil_prep_01.py`<br>`tests/validation/test_sw_dom_hil_prep_01.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-SOAK-PREP: Metrics and field validation readiness

Wave W12; kind `field_preparation`; role `bounded`; dependencies: SW-RUNTIME-PREP.

Audit the existing field collector/runbook before proposing tooling. Test collection/analysis only on isolated disposable data, including missing samples/restarts and resource trends. Prepare operator instructions for the exact later candidate.

**Observable acceptance:** Schema/time/resource fields and gap/restart interpretation checked; no dummy/synthetic dataset becomes accepted soak evidence. Continuous deployment-host 72 hours and week daily use/sign-off remain deferred.

**Primary features:** F-REL-018

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-SOAK-PREP-01 | F-REL-018 | `tests/validation/scenarios/sw_soak_prep_01.py`<br>`tests/validation/test_sw_soak_prep_01.py` |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-REPO: Repository, security and release engineering reconciliation

Wave W13; kind `release_preparation`; role `evidence`; dependencies: SW-FINDINGS.

Reconcile SEC-14/15 and DEP-05 against actual public repository/history, license/support tables, secret scan, pinned CI/container actions and supply-chain/build gates. Do not restore purged vendor data, rewrite history, force-push or infer licensing authority.

**Observable acceptance:** Every repository finding has retained proof and honest disposition; current full-tree/change hygiene and secret-scan checks pass. Any remaining external licensing/history authority question is an explicit release hold.

**Primary features:** Cross-cutting; no separate feature ownership.

**Parser-open findings to reconcile:** SEC-14, SEC-15, DEP-05

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-REPO-01 | Cross-cutting scope above | Report/artifact paths only; source/root edits require the coordinator |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-DOCS: User guides, claims and operator handoff

Wave W13; kind `release_preparation`; role `inventory`; dependencies: SW-UC-PREP, SW-HA-PREP, SW-DOM-HIL-PREP, SW-SOAK-PREP, SW-KIOSK-STATE, SW-FLIC, SW-UI-PRESENT.

Reconcile README/client/deployment/troubleshooting/support docs with accepted software, exact flags/ports/auth and evidence. Label unsupported claims. Prepare hardware/soak handoff documents without recording execution.

**Observable acceptance:** Runnable documented commands and local Markdown targets, actual source/configuration alignment, physical support claims only where accepted, final evidence and external-gate inventory complete.

**Primary features:** Cross-cutting; no separate feature ownership.

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-DOCS-01 | Cross-cutting scope above | Report/artifact paths only; source/root edits require the coordinator |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-VERSION: Coordinator-owned final candidate metadata assembly

Wave W14; kind `candidate_assembly`; role `coordinator`; dependencies: SW-API-READ, SW-SEC-AUTH, SW-API-WRITE, SW-SEC-DATA, SW-API-CLIENT, SW-DOM-PROFILE, SW-DOM-SCENE, SW-DOM-MACRO, SW-DOM-SHORTCUT, SW-DOM-PRESENT, SW-UI-CONTROL, SW-UI-MANAGE, SW-UI-PRESENT, SW-KIOSK-CONTROL, SW-KIOSK-STATE, SW-FLIC, SW-PROTOCOL-PREP, SW-RUNTIME-PREP, SW-UC-PREP, SW-HA-PREP, SW-DOM-HIL-PREP, SW-SOAK-PREP, SW-REPO, SW-DOCS.

Prepare the canonical 1.0.0 metadata diff with existing version tooling in a coordinator-owned assembly worktree after software packages and repository/doc reconciliation. Apply shared/root metadata only through the coordinator; review the exact commit independently before use.

**Observable acceptance:** Canonical/package/driver/component/docs/OCI versions agree, metadata verification and installed-entry checks pass, no final tag/main merge/publication. Metadata preparation creates a candidate, not release acceptance; affected software evidence must be refreshed.

**Primary features:** Cross-cutting; no separate feature ownership.

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-VERSION-01 | Cross-cutting scope above | Report/artifact paths only; source/root edits require the coordinator |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-BUILD: Matching rebuilt application artifacts

Wave W14; kind `candidate_assembly`; role `core`; dependencies: SW-VERSION.

Build fresh amd64/arm64 artifacts from the reviewed final-metadata source, record immutable digests/platforms and source/input parity, and exercise actual normal image commands. RC images are never relabelled as final.

**Observable acceptance:** Rebuilt bytes and canonical versions agree; amd64 deployment and arm64/QEMU startup/health/SIGTERM plus installed/source entry checks pass with their real limits recorded. No final release/image tag publication or hardware claim.

**Primary features:** Cross-cutting; no separate feature ownership.

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-BUILD-01 | Cross-cutting scope above | Report/artifact paths only; source/root edits require the coordinator |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.

## SW-SOFTWARE-GATE: Combined software campaign and independent acceptance

Wave W15; kind `final_acceptance`; role `evidence`; dependencies: SW-BUILD, SW-REPO, SW-DOCS.

Coordinator runs the complete applicable source/client/UI/UC/HA/Flic/image/packaging pipeline on the frozen candidate and serial registry/ledger/formal gate. Independent different-family reviewer audits actual outputs, assertions and source/image relationships; finish all corrective re-reviews.

**Observable acceptance:** All 147 software-target features have fresh accepted target proof, all 120 V4 and one V5 features have explicit software-prerequisite dispositions, all nonhardware blockers settled or explicitly held, current-head CI green and exact push equality verified. Hardware caps and owner gates remain visible; release/main/tag actions stay deferred.

**Primary features:** Cross-cutting; no separate feature ownership.

**Parser-open findings to reconcile:** None assigned; new reproduced defects still need a finding.

| Dispatch unit | Exact primary features | Default new writable test files |
| --- | --- | --- |
| SW-SOFTWARE-GATE-01 | Cross-cutting scope above | Report/artifact paths only; source/root edits require the coordinator |

Author prose: `docs/production/software-waves/<unit>/AUTHOR.md`; reviewer prose: `docs/production/software-waves/<unit>/REVIEW.md`. Independent review has a separate worktree at the exact submitted commit and no product-write permission. Existing source, browser/SDK bridge, schemas, common fixtures and guides are read-only until a specific serial lease is recorded. Root manifests, lockfiles, registry/ledger and integration remain coordinator-owned.
