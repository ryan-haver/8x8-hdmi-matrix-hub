# EV-01 evidence reconciliation

Status: **coordinator evidence inspection at candidate `95f64920`; no feature
promotion or new implementation**. Observed 2026-10-20 UTC. This is the executed
follow-up to the [gap inventory](RELEASE_EVIDENCE_GAPS.md), not another general
plan. The [allocation ledger](../production/AGENT_ALLOCATION.md) records staffing
and publication. Owner visual, physical and field gates remain open.

## Candidate attribution

The inspected integration commit is
`95f64920220fd5269007272ed8f3cbe04604db7e`, initially equal to
`origin/wp-runtime-completion`. PR #38 remains draft against
`wp-g1-g2-release-and-docs`; #37 and #36 still target `main`.

[CI 39305698510](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/39305698510)
completed for that PR head. Its actual checked-out source in scenario records is
synthetic merge `66a82c32885baf0893cbd06e57715251e14fd4d0`, whose parents are
`6debe5a9d1ce3b5993bbd1f6c16d14550d11141b` and the integration commit above.
The GitHub Git-commit response and local `git rev-parse 95f64920^{tree}` both
identify tree `472c02738fa78f7928d2039e98b56f5b0471e42b`.
This exact tree equivalence justifies inspecting the CI behavior for this
candidate. Keep the original merge SHA in the records. It is not an ancestor
of the integration branch; the current ledger's ancestry rule cannot treat
those records as fresh merely because their tree matches.

All twelve non-UI required jobs passed. Actual Playwright results are 1,098
expected, 33 skipped, three unexpected, zero flaky; all three failures are
`special/tron-background/paused-frame` at desktop, kiosk-tab-a11 and
kiosk-iphone16promax. The subsequent review capture passed 62 tests; that
capture is not owner approval. Original reports, screenshots and logs were
downloaded into a new `build/ev01-20261020/ci-artifacts/` destination.

The [complete source campaign](runs/runtime-r8b/source-campaigns.json) remains
attached to `1baac3dec660f41345869c126cfca94d6731c5a0`.
The [manifest](runs/runtime-r8b/manifest.json) identifies the original amd64
image `sha256:558c2677c65995598d7b06a2f1726c2a254ae1afac74b1f34060f336bac0fd8e`
and arm64 image
`sha256:c7d017fbcbf61e47b64aeab12cab0d153fe92b9ca74ecf0823b32cb551e14c93`.
The latter's smoke run is not a physical arm64 qualification. Source scenarios
have no hub image digest; do not attach an image digest from another campaign.
Image-client proof is the separately recorded 193-outcome subset, not the full
source API run. The 42 declared client exclusions remain non-applicable.
None of the 193 passing image outcomes attributes any of the 42 features
selected here. Their source/CI records must not inherit those image passes.
The older committed records' four non-null hub digests stay attached to their
own historical sources; they are not either accepted `1baac3de` image above.

The committed difference from `1baac3de` to the inspected head consists of
documentation, registry/ledger and evidence consolidation, including README
long-description prose. Runtime source, web assets, dependencies, simulator,
scenario definitions and validation clients are unchanged. This supports
preserving the original *scoped* behavior proof; it does not claim identical
new wheel metadata or qualification of a future final-version rebuild.

## Method and disposition rules

The requested sets overlap: 14 target-mapped software gaps plus 26 stale
software gaps plus 15 at-target rows without fresh records select **42 distinct
features**. Every selected feature appears once below. Inspection uses
`Scenario.features_for(client)`, registry interfaces, actual scenario actions
and assertions, record checks, original source/environment/image identities,
`covers` and the committed path difference. The
[portable reconciliation index](runs/ev01-20261020/reconciliation.json) records
all 42 dispositions, original record paths/hashes, provenance counts and selected
direct-test outcomes. The detailed inventory is retained locally under
`build/ev01-20261020/`.

All 2,728 inspected records pass the existing JSON schema and match their
declared per-client feature mapping. They comprise 907 passing original-source
records, 907 passing candidate-CI records and 914 committed historical records
(906 pass, eight fail). All 907 original-source records have fresh `covers` at
the inspected candidate. The old failed records remain unchanged. The 146
original source records supporting the seven primary preservation dispositions
were copied byte-for-byte to a new local `preserved-originals/` directory and
their SHA-256 hashes verified. No copy was imported into the feature ledger.

Disposition numbers follow the owner's requested categories:

1. Preserve valid original evidence **within the stated assertion scope**.
2. Rerun against the actual candidate where inputs/identity or adequate original
   results cannot be established.
3. Supply missing client/feature mapping or behavioral assertions before target
   closure. Existing partial passes remain valid at their original level.
4. Reproduce an implementation defect, record a finding, correct and independently
   review it. Evidence absence alone does not establish this category.

The primary dispositions below distinguish preservable scoped proof from missing
proof. Every row may preserve its valid partial original results.
No new supported product failure was reproduced in this read-only task. A
rerun of the same API scenarios cannot produce their missing V3 client mapping
or add the unasserted routes. After material candidate changes, repeat the
affected checks using the exact new source and artifact identities.

## Target-mapped software gaps: fourteen

All fourteen mapped targets are V2. `S` below means the original `1baac3de`
source campaign; `C` means the candidate-equivalent CI tree described above.
Neither label changes the SHA inside an evidence record.

| Feature | Disposition | Inspected assertion scope and required action |
| --- | --- | --- |
| F-API-002 | 3 | `contracts.api_info` asserts canonical version and driver identity at `/api/info`; it does not exercise `GET /` or `GET /api`. Preserve S/C info proof; connect actual root/API assertions before closing the grouped feature. |
| F-API-014 | 1 | `contracts.system_info` asserts the runtime API version; `contracts.storage` reads actual disposable storage/config existence, with unchanged-device/no-command checks. Preserve S/C V2 for these two registered reads; no private deployment storage claim. |
| F-API-016 | 1 | `cec_caps.*` checks literal catalog tables, per-port/all capability values and invalid/unavailable reads; `cec_controls.*_enable_*` checks exact flag arrays, independent device readback and unchanged other ports, including refusal. Preserve S/C V2; physical CEC effects remain V4 work. |
| F-API-017 | 3 | `contracts.*settings` and `writes.*settings` read saved names and bulk/preset changes back. Favorite/dashboard preset GET/PUT/toggle interfaces and icon behavior are not established by those nine mapped scenarios. Reconcile existing simulator tests before adding assertions. |
| F-API-018 | 3 | `writes.output_name` verifies output 8's hub name, device name and exact command. The input-name route is not covered by that one mapping. Preserve output proof and attribute an actual input rename/readback case. |
| F-API-019 | 3 | `profile_crud.*`, `profile_state.*` and `writes.profile_*` check CRUD, metadata, assignments and rejection/readback. Recall and execution-log behavior exists elsewhere but is not attributed to this API feature by those scenario/client pairs. Reconcile all registered interfaces before target closure. |
| F-API-022 | 3 | `failures.bad_input` verifies input 9 returns 400, sends no command and leaves the device unchanged. It does not establish the envelope and validation claim for all routes. Preserve this negative control; map representative success/error/auth/body failures without claiming exhaustive behavior from route coverage. |
| F-API-023 | 3 | `domain_manage.macro_*` verifies saved CRUD, boundaries, favorites/dashboard and dry-run no-effect behavior. Actual execution is exercised under domain features; map its real API assertions to this grouped API claim and verify collection coverage. |
| F-API-024 | 3 | Contracts/writes check alias reads, creation, updates, toggles, ordering, execution with device effect and refusal to delete a built-in. Successful user deletion and the complete canonical/alias surface need explicit attribution; the scenario itself points to separate simulator tests. |
| F-API-025 | 3 | `dashboard.widget_cards_dropped` checks migration/order; `widget_card_refused` checks a rejected widget leaves saved items unchanged. Positive add/remove/reorder/layout-write effects are outside these two scenarios. |
| F-API-026 | 1 | `contracts.themes`, `contracts.ui_preferences`, `writes.themes`, `writes.themes_reset`, `writes.ui_preferences` cover the five registered interfaces with saved-value readback and unchanged-device checks. Preserve S/C V2; this is not browser preference rendering proof. |
| F-API-027 | 3 | `contracts.settings` and `writes.connection_test` check connected status/test-connection. Matrix-host mutation, credentials and denied changes are absent from this pair. Reconcile existing security/runtime reconfiguration tests, including no-PIN/admin/admin+control conditions. |
| F-API-028 | 1 | The two registered interfaces are read buttons and register buttons. `contracts.flic_buttons` checks fixture contents; `writes.flic_register` verifies a renamed button through a separate GET. Preserve S/C V2 registration/read proof; no physical-button claim. |
| F-DOM-018 | 1 | `domain_manage.legacy_list` compares canonical/legacy list state; `legacy_recall` checks actual routing and command effects through the deprecated alias. Preserve S/C V2 for the two registered alias interfaces. Restart compatibility is outside this proof and retains its existing finding scope. |

Assertion sources: [read contracts](../../tests/validation/scenarios/contracts.py),
[API identity](../../tests/validation/scenarios/api_documentation.py),
[saved writes](../../tests/validation/scenarios/writes.py),
[CEC capabilities](../../tests/validation/scenarios/cec_capabilities.py),
[CEC controls](../../tests/validation/scenarios/cec_controls.py),
[profile CRUD](../../tests/validation/scenarios/profile_crud.py),
[profile state](../../tests/validation/scenarios/profile_state.py),
[domain management](../../tests/validation/scenarios/domain_management.py),
[dashboard](../../tests/validation/scenarios/dashboard.py) and
[failure checks](../../tests/validation/scenarios/failures.py).

## Additional stale software gaps: thirteen

These rows are the stale software set after removing the thirteen rows already
included above. F-API-002 is the target-mapped row without stale committed proof.
All rows below have primary disposition **3**: the preserved S/C API proof is
V2, while the required target is V3. The client mappings must be inspected and
extended through actual client assertions; adding a feature label alone is not
sufficient. API success is never relabeled as V3 client proof.

| Feature | Preserved behavior and missing target proof |
| --- | --- |
| F-API-004 | CEC status raw/formatted arrays and cable-state reads, including failed CEC read, have API assertions. Remaining detailed-status routes and target-level client use need attribution. |
| F-API-009 | `power.standby/wake` checks device power, one command and hub readback. F-API-009 is attributed to API only; other clients' matrix-power feature proof does not automatically prove this API feature at V3. |
| F-API-015 | Literal HTTP/Telnet CEC frames, all ports/table entries, enablement and refusal cases establish V2. Preserve that scope; real-client command selection/effect and API-feature attribution remain missing. |
| F-DOM-001 | `profile_crud.*` reads create/edit/delete results back and checks rejected writes preserve data. Browser CRUD effects are not asserted by this API inventory. |
| F-DOM-006 | Favorite/dashboard/pin/order changes are read back through API. Actual rendered cards and ordering need client effect proof; layout reconciliation is explicitly excluded by the scenario module. |
| F-DOM-007 | `profile_state.*` checks stored CEC targets and resolver output over API. Map actual client editing/selection and observed target use; a resolver response alone is not that proof. |
| F-DOM-008 | Execution history asserts success/error/order, scene metadata and real command effects. A real client's history presentation/use remains unproven by those API pairs. |
| F-DOM-009 | Capture scenarios compare routing/output settings across seeded patterns. The actual save-current-state client flow and resulting saved profile need target-level attribution. |
| F-DOM-010 | Scene CRUD, mixed steps, overrides, boundaries and refusal/readback are tested over API. Browser scene creation alone does not prove full client edit/delete/step behavior. |
| F-DOM-019 | Macro CRUD/validation checks full saved steps, limits and rejected changes. Browser editing and persisted client-visible results need proof; restart/storage-failure coverage stays separate. |
| F-DOM-021 | Dry-run asserts 25-step command coverage, duration, unchanged saved steps/device and no CEC transmission; missing IDs return 404. Actual client dry-run behavior is still unmapped. |
| F-DOM-022 | Favorite/dashboard toggles in both directions, missing IDs and sorted favorites have independent API readback. Rendered client collections/layout need proof. |
| F-DOM-031 | Stored-layout migration and invalid widget rejection preserve order. Positive user add/remove/reorder and client rendering remain outside these scenarios. |

## At-target rows without fresh committed records: fifteen

Numerical baselines are retained. Direct tests can supply useful original proof
without being discoverable scenario records. Their real assertions determine
scope; converting them into accepted feature evidence is still work.

| Feature | Disposition | Inspected original proof and remaining limit |
| --- | --- | --- |
| F-API-021 | 3 | `domain_manage.scene_*` checks scene CRUD/steps/overrides and readback. Execute/validate/history are asserted in `scenes.py` under other feature IDs; reconcile those exact API mappings. A V2 baseline does not make the grouped claim fully fresh. |
| F-API-029 | 3 | Real `/ui` and `/kiosk` smoke tests load assets and reject page errors. Map the complete static/asset route scope and actual client evidence; successful page load does not prove every static/path-denial interface. |
| F-API-036 | 1 | `outputs.audio_mute` verifies the WS event payload plus device/hub mute; `audio_mute_rejected` verifies unchanged state and no success event. Preserve S/C V2 API event proof. HIL-09 still caps the separate hardware feature; this row does not close that finding. |
| F-API-038 | 1 | `cec.output_power_on` checks the exact display command frame, WS payload and unchanged device settings. Preserve S/C V2 event proof, without claiming the TV powered on. |
| F-API-039 | 3 | Simulator WS tests check welcome protocol/link, initial routing/names and `get_status` snapshots. Preserve the direct test basis; no discoverable scenario currently attributes this feature. |
| F-API-042 | 3 | Simulator WS tests check both ping message forms, no error events and protocol ping frames. Preserve that basis; feature-attributed scenario records are absent. The shortened heartbeat control is not an elapsed production-duration soak. |
| F-UI-001 | 3 | Real-browser smoke checks open WS, connected header, actual model and 64 cells. The reconnecting-header flow additionally manipulates app state for one color control. Preserve the actual scope and attach a valid feature/client evidence path. |
| F-UI-015 | 3 | The scene-editor flow types a name and asserts POST 201/name, then deletes through API. It does not independently read the saved scene/steps back through the UI. Preserve creation-response proof; add meaningful editor/save/readback coverage. |
| F-UI-025 | 3 | Smoke deliberately drops/refuses WS, changes simulator routing while disconnected, then checks a new connection and updated active cell. This is substantive real-browser resync proof; connect its exact results to this feature without inventing an existing scenario mapping. |
| F-UI-026 | 3 | Browser flow intercepts `/api/status` with 503 and checks the unreachable message/no fabricated grid; initial-loading case holds the response. Preserve client rendering proof; this controlled response is not a real matrix outage. Reconcile actual live-failure evidence separately. |
| F-UI-031 | 3 | About flow calls `window.AboutDialog.show()` directly and checks connection/model text. Source search finds no shipped call to `AboutDialog.show`. It proves dialog rendering, not user reachability. Preserve the known baseline limitation; establish the intended user trigger and a real interaction oracle before closure. |
| F-KIO-001 | 3 | Real kiosk smoke checks an open WS, connected dot and eight output tiles, with no page errors. Preserve that result and supply feature-attributed current proof; physical kiosk acceptance is separate. |
| F-KIO-004 | 3 | Kiosk flow checks no API 404s and seeded signal/no-signal classes. A separate flow changes simulator output 3 and checks its displayed input via WS without polling. Combine those actual assertions with required tile fields and feature attribution; screenshots alone do not cover all tile semantics. |
| F-SEC-012 | 3 | SEC-07/08 browser flows assert quote escaping, zero injected handlers/images in main UI and kiosk using intercepted hostile payloads. Preserve this client security basis; map explicit feature evidence and maintain its rendered-surface scope. |
| F-SEC-015 | 3 | Real shared-runtime process plus `UcRemoteSim` checks missing/wrong/type-invalid token denial before matrix login, valid setup/reconfigure and token-free logs. This is real scripted-client proof, distinct from mocked `tests/uc/test_setup.py`; connect its result to accepted feature evidence. No physical Remote claim. |

Direct assertion sources: [browser smoke](../../tests/e2e/smoke.spec.ts),
[browser flows](../../tests/e2e/flows.spec.ts),
[WS simulator contracts](../../tests/sim/test_sim_ws_contract.py),
[UC authentication process test](../../tests/test_security_v3_hardening_scenarios.py),
[mute events](../../tests/validation/scenarios/outputs.py),
[CEC events](../../tests/validation/scenarios/cec.py) and
[scene execution/validation](../../tests/validation/scenarios/scenes.py).
Original source test outcomes are in [core XML](runs/runtime-r8b/final-source-rerun.xml)
and [flow results](runs/runtime-r8b/source-flows-results.json); the downloaded CI
Playwright JSON is tied to the identical candidate tree above.

## Concrete follow-up boundaries

EV-02 first preserves reviewed original V2 records for F-API-014/016/026/028
and the event proof for F-API-036/038, keeping original SHA/digest/environment
bytes. It then reconciles grouped API route/assertion gaps identified above
against existing simulator/security tests. Registry mapping, evidence import
and ledger generation remain coordinator-owned. No import or level change has
been performed here. New tests or tooling require qualified cross-family review.

EV-03 preserves F-DOM-018's alias proof and the substantive browser/kiosk
results, then scopes real-client CRUD/editor/history/layout assertions from
the listed omissions. A test that reads response status alone cannot be
upgraded by changing its feature tags. About-dialog reachability is a specific
source/acceptance question; this report has not fabricated a runtime failure.

EV-04 retains all physical protocol/client gaps and HIL-09 caps; the source
and CI records supply software prerequisites only. EV-05 still requires the
owner's continuous 72-hour measurements and week-of-use sign-off. No hardware
action, collector or owner observation was started or inferred.

The execution outcome is reconciliation, with **seven primary preservation
dispositions and 35 mapping/assertion dispositions**. No primary rerun is
required solely because the candidate's later changes are documentation and
evidence consolidation; any affected implementation or final artifact change
must refresh its proof. Zero newly reproduced implementation defects means
no new product finding was opened; it does not certify the unasserted behavior.
The inventory's 210 below-target rows and all release gates remain unchanged.
