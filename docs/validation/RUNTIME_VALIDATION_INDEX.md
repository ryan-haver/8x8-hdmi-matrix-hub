# Runtime validation index

This index summarizes the final integrated software campaign and keeps its source revision, evidence archive, and remaining release gates distinct. The report and archived records retain run-level scopes, timestamps, artifact roots, and hashes; historical runs are not attributed to a single final SHA.

## Candidate and archive

| Item | Revision or result |
| --- | --- |
| Tested runtime and image source | [`1baac3dec660f41345869c126cfca94d6731c5a0`](runs/runtime-r8b/manifest.json), clean tracked checkout, product version `1.0.0rc1` |
| Evidence archive checkpoint | [`fe0e7f0705f376aaa9f8c27d6e50a2b78a3df9fe`](RUNTIME_VALIDATION_REPORT.md); preserves original evidence bytes and history |
| Integrated formal evidence gate | Passed, exit 0, zero known failures linked to open findings; [context](runs/runtime-r8b/formal-gate-context.json) records consolidation scope |
| Registry and ledger checks | 26 passed within the 4,041-pass complete local core run; 26 formal registry checks passed in 3.32 seconds |
| Feature and client ledger | [Existing ledger](LEDGER.md), retaining feature-level targets and provenance |
| Full campaign report | [Runtime validation report](RUNTIME_VALIDATION_REPORT.md) |

The source/image campaign ran on `1baac3de`. Archive checkpoint `fe0e7f0` records its evidence consolidation; it is not a new campaign run. Earlier candidates and failures remain attached to their original revisions. The binary Git-blob audit matched 439/439 audited files (213 previous + 193 image records + 32 archive files + one conditional probe), including CRLF bytes. This does not mean every report-text byte is hash-indexed or that all historical runs share one SHA. All 259 captured source/build inputs remained unchanged.

## Software evidence

| Scope | Result | Evidence |
| --- | --- | --- |
| Complete core including installed-package entry checks | 4,041 passed, 4 platform skips, 35 deselected; excludes HA component and dedicated UC suites | [Manifest](runs/runtime-r8b/manifest.json); [complete core log](runs/runtime-r8b/final-source-rerun.log) |
| Dedicated scripted Remote | 100 passed, no skips; SDK and simulator, no physical Remote claim | [Manifest](runs/runtime-r8b/manifest.json) |
| Built amd64 deployment | 26 passed, 3 expected skips; normal image command, health, SDK/discovery/volume/context checks | [Manifest](runs/runtime-r8b/manifest.json) |
| Source API/browser/UC/Flic | API 1,411; browser 54; UC 18; Flic 23 passed | [Source campaigns](runs/runtime-r8b/source-campaigns.json) |
| Source Home Assistant containers | 19 passed on 2026.9.3 and 19 on 2025.1.4; supported line, not the exact 2025.1.0 floor | [Current](runs/runtime-r8b/source-ha-current.json), [minimum line](runs/runtime-r8b/source-ha-minimum-line.json) |
| amd64 image client campaigns | API 79, browser 54, Flic 23, HA 19, UC 18; 193 passing outcomes | [Campaigns](runs/runtime-r8b/image-campaigns-cached.json), [milestones](runs/runtime-r8b/milestone-records.json) |
| Source UI flows | 59 passed; zero unexpected, flaky, or skipped | [Flow outcomes](runs/runtime-r8b/source-flows-results.json) |
| REST route coverage | 177/177 in the actual complete-core run | [Complete core log](runs/runtime-r8b/final-source-rerun.log); independent CI core log |
| Swagger rendering/catalog | 177 operations with Flic enabled; 175 disabled; online and CDN blocked, no page errors or saved PIN | [Enabled](runs/runtime-r8b/swagger-flic-true.json), [disabled](runs/runtime-r8b/swagger-flic-false.json), [image summary](runs/runtime-r8b/final-swagger-image.json) |
| Application images | amd64 `sha256:558c2677c65995598d7b06a2f1726c2a254ae1afac74b1f34060f336bac0fd8e`; arm64 `sha256:c7d017fbcbf61e47b64aeab12cab0d153fe92b9ca74ecf0823b32cb551e14c93` | [Manifest](runs/runtime-r8b/manifest.json) |
| Shipped input parity | Both architectures match all 257 tracked shipped input bytes | [Manifest](runs/runtime-r8b/manifest.json) |
| arm64/QEMU smoke | Offline startup, canonical metadata, Docker health, graceful SIGTERM; no device-action claim | [Manifest](runs/runtime-r8b/manifest.json) |

The 42 predeclared client exclusions remain `n/a`, not passes. Swagger results establish catalog rendering, not every disabled-configuration handler. The supplemental external-image route diagnostic is non-strict, uninstrumented, and returned zero; it is not product route coverage. The original complete-core JSON was not separately retained, so the archived complete-core log and independent CI result are the route evidence; no JSON was reconstructed.

The source HA runs use disposable containers, not the owner's deployment. Flic replay uses a Node SDK stub and simulator-backed hub; scripted UC tests use the SDK and simulator. Neither establishes physical device behavior. Source/private-config integrity was checked only after discovery: 16 metadata and 3 presence values matched, which is not pre-original proof. The report preserves R8D's conditional replacement-disconnect reproduction: failure before the real supported fence remains outside the supported guarantee, while the actual in-body control passes. No universal arbitrary-client quiescence claim is made.

The formal gate checks evidence relationships and registry/ledger consistency; it does not elevate software evidence to hardware or field acceptance. Earlier failed campaigns and the earlier `4adbc13` archive remain historical failures/results and were not rewritten.

## CI and remaining gates

CI at [`1baac3de`](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/39228762775) passed all 12 non-UI required jobs. CI core passed 4,023, skipped 22, deselected 35, and covered 177/177 routes; actual HA passed 19 scenarios. Main UI had 1,098 passes, 33 skips, and three existing Tron paused-frame visual failures; the gallery had 62 passes. The owner has not approved those visuals. The independent R8D review accepts the supported Orei fixes: 12 required source/image cases, 102 regressions, and two supported controls pass. Final documentation-head CI remains subsequent to this commit.

Physical matrix and CEC behavior, physical Remote and Flic operation, owner HA/LAN, HIL-B/C/E, the 72-hour resource soak, and week-of-daily-use field sign-off remain external gates. No v0.5, v1 RC, or final tags have been created. Final `1.0.0` metadata and matching rebuilt artifacts are required before release. See the [field runbook](RUNTIME_FIELD_GATE_RUNBOOK.md), [validation plan](VALIDATION_PLAN.md), and [complete report](RUNTIME_VALIDATION_REPORT.md).
