# Runtime validation index

This index is the entry point for fresh, integrated validation of the runtime
composition. It records only coordinator-supplied reports and artifact paths
for the exact tested commit. It is not a replacement for the feature-level
[ledger](LEDGER.md) or the owner's physical acceptance records.

## Candidate under review

| Field | Value |
| --- | --- |
| Integrated candidate commit | Pending coordinator campaign report |
| Full product suite | Pending |
| Dedicated UC, HA and Docker jobs | Pending |
| Browser suite | Pending |
| API, browser, scripted Remote, HA and Flic image campaigns | Pending |
| Route inventory coverage for enabled integrations | Pending exact configured inventory and result |
| Independent runtime review (R8) | Pending |

The campaign has not yet been supplied to this documentation work. These
pending entries make no pass-count, route-count or acceptance claim. Once the
coordinator provides the final report and fresh summaries, this table will link
the original artifacts and state each campaign's exact commit, command/result,
and limitations.

## Provenance rules

- A campaign result applies only to the exact code/image commit recorded in its
  report. Do not infer current-runtime behavior from a previous candidate.
- Existing `docs/validation/runs/rc1/` deployment, source, Swagger and client
  records remain evidence for their recorded RC1 commit. They are historical
  references and do not validate this runtime-completion candidate.
- Unit tests and simulator doubles prove only their exercised code path. A
  mocked SDK or replay client does not prove a physical Remote or Flic device.
- Private-container bridge/loopback discovery is not proof of physical LAN
  discovery or Home Assistant automatic setup.
- Hardware operation, owner-observed field behavior, outage/recovery and the
  72-hour soak remain pending until their respective owners provide evidence.

## Remaining owner gates

| Gate | Status | Evidence needed |
| --- | --- | --- |
| Physical matrix and CEC behavior (V4) | Pending | Operator-observed BK-808/TV checks with firmware and setup recorded. |
| Physical Remote and Flic behavior | Pending | Owner-run Remote 3 and button tests against the accepted runtime. |
| Field deployment and recovery | Pending | Owner-observed install, restart, outage and restoration records. |
| 72-hour reliability soak (V5) | Pending | Runbook metrics and post-soak report for the accepted candidate. |

See [the validation plan](VALIDATION_PLAN.md),
[hardware runbook](HIL_SESSION_2_RUNBOOK.md), and
[release report](VALIDATION_REPORT.md) for the project gates and prior
candidate evidence.
