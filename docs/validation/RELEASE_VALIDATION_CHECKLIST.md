# Release validation checklist

Status: **planning package; release gates remain open**. Updated 2026-10-19.
This checklist organizes the [evidence-gap inventory](RELEASE_EVIDENCE_GAPS.md)
and existing acceptance rules. It records no new runtime, hardware or field
passes and does not authorize worker launches, device writes, snapshot approval,
deployment, merge to main or tags.

Executed follow-up: [EV-01 dispositions](EV01_EVIDENCE_RECONCILIATION.md) now
record original/candidate CI attribution and assertion gaps for the initial
42-feature union. No release gate is checked merely because reconciliation
completed; evidence import, target closure and implementation remain separate.

Use the [master plan](../planning/UNIFIED_MASTER_PLAN.md),
[validation policy](README.md), [validation plan](VALIDATION_PLAN.md),
[Orca protocol](../ORCHESTRATION_PROTOCOL.md) and
[allocation ledger](../production/AGENT_ALLOCATION.md) as authorities. Mark an
item complete only with the exact commit/digest, environment, timestamped result,
operator/reviewer and evidence reference. A checked planning task cannot stand
in for a passed release gate.

## 1. Freeze the candidate and classify the gaps

- [ ] Record the actual integration branch/full SHA, remote head, applicable
  Run and protected resources. Current integration is `wp-runtime-completion`;
  rebind it before execution rather than assuming an old handoff is current.
- [ ] Confirm PR dependencies: #36 -> main, #37 -> main, #38 -> #37's branch.
  Keep #38's runtime work in the candidate when #37 is merged. Do not tag a
  pre-runtime #37 tree as the tested runtime RC.
- [ ] Select an immutable candidate and exact amd64/arm64 image digests; record
  application/OCI version and input parity. Keep source-run, image-run and later
  documentation SHAs distinct. Local RC builds are not published release tags.
- [ ] Recompute the gap inventory from committed evidence at the selected SHA
  using the existing ledger logic. Preserve its input hashes, output and command
  receipt; do not edit `LEDGER.md` or promote registry levels to clear a checklist.
- [ ] Assign every below-target feature an accepted evidence task: software,
  hardware or field. Track stale evidence, missing scenarios and blocking finding
  caps as overlays, not extra features or proven implementation failures.
- [ ] For every actual behavior defect, record a finding with reproduction and
  acceptance criteria before assigning a corrective package. Evidence absence
  alone is not proof that the implementation is broken.

The original software campaign remains attached to `1baac3de` and its immutable
image digests in the [runtime evidence index](RUNTIME_VALIDATION_INDEX.md).
New changes need affected evidence at their actual commits. No historical pass
qualifies an untested source, image, platform or client.

## 2. Prepare only the required software follow-ups

- [ ] Refresh exact model catalogs, host/adapter capabilities, helper routing,
  domain qualification and provider/account-pool usage before any execution wave.
  Unknown quota holds the affected dispatch. Below 30%, near exhaustion or
  insufficient capacity requires a suitable fallback with its own verified
  headroom. No Claude/Anthropic in any author, review, helper or fallback role.
- [ ] Keep shared APIs, root manifests/locks, registry/ledger and integration
  coordinator-owned. For each necessary implementation package, pin exact base,
  disjoint writable paths, dependencies and behavioral acceptance in the ledger.
- [ ] Plan qualified review from a different underlying model family for each
  new implementation package, including tests, fixtures and tooling. Sol/Astra
  are the same family; a catalog alias or backend self-report is insufficient
  family proof. Historical reviews remain historical and are not relabeled.
- [ ] For software-target gaps, inspect the feature basis and actual assertions
  before adding tests. Prefer representative real-client behavior and negative
  cases over more assertions that mirror implementation. Re-run existing valid
  scenarios when the gap is freshness, not missing coverage.
- [ ] Verify feature/client attribution individually: 29 software gaps have
  scenarios whose current mapping cannot reach their required V3 level. A
  passing API run cannot substitute for that client proof. For security, retain
  negative tests with no PIN, admin PIN and admin plus control PIN.
- [ ] Close protocol/finding caps only with the required reproduction and
  accepted evidence. Preserve negative observations; a simulated 200 response
  does not establish physical write behavior.
- [ ] Validate each submitted worker commit in its own worktree, audit base/path
  boundaries, accept independent review, integrate sequentially and re-review
  material fixes or integration changes. Preserve/publish before exact cleanup
  and verify integration remote equality before the next wave.

This checklist does not preassign conditional MiniMax/DeepSeek routes or claim
available quota. The [inventory's proposed packages](RELEASE_EVIDENCE_GAPS.md#proposed-follow-up-packages)
are planning scopes, not launched workers.

## 3. Software regression and visual gates

- [ ] Observe all applicable CI jobs at the **exact submitted head**; record
  completed/pending/failed status, URL and actual results. A previous head's
  green jobs do not establish current-head success.
- [ ] Run the complete applicable combined verification after implementation:
  Ruff/Mypy, complete core with strict route inventory, dedicated UC and HA,
  supported image builds/deployment, browser flows and affected client campaigns.
  Use current CI commands, pinned environments and isolated temporary data.
- [ ] Preserve counts, exit codes, skips/errors, logs and limitations separately
  for source, installed entry, each image/platform and each client. Do not claim
  an image representative API subset covers the complete source API campaign.
- [ ] If a REST route changes, update `features.yaml` and simulator reads in
  `tests/sim/test_sim_rest_reads.py`; generate the ledger and then run registry
  checks serially. Require full route coverage of the actual mounted inventory.
- [ ] Keep partial documentation/external-container checks from overwriting the
  complete route diagnostic (`-p no:tests.route_inventory` for such supplements).
- [x] Obtain the owner's explicit decision on all three Tron paused-frame
  differences for desktop, kiosk-tab-a11 and kiosk-iphone16promax. Preserve the
  before/after artifacts. Follow remediation section 5.3; an automatically
  generated gallery is not approval and failed visual CI is not waived.
  [Owner approval and focused verification](TRON_OWNER_APPROVAL_20261020.md)
  record the 2026-10-20 decision; full affected CI remains a separate item.
- [ ] If approved visual changes are committed, use the required separate
  baseline approval commit and verify affected CI at the new head. If rejected,
  assign a scoped correction and repeat independent review/verification.

The documented conditional replacement-disconnect probe remains a known
extension limit; its red result is preserved. It is not silently made a skip,
weakened to green or treated as a newly discovered supported Orei failure.

## 4. Owner hardware session: HIL-B, HIL-C and HIL-E

Follow the [runtime field runbook](RUNTIME_FIELD_GATE_RUNBOOK.md),
[HIL session procedures](HIL_SESSION_2_RUNBOOK.md) and
[capture tool guide](../../tools/hil/README.md). The older HIL session document
contains historical version/main-branch, fixed-host and wiring assumptions;
rebind the accepted candidate, credentials, host and actual topology before
using its procedures. Do not execute its setup block literally for a new RC.

- [ ] Agree on the owner-present session, available hardware, permitted actions
  and disruptive/unrestorable operations separately. Record operator, matrix
  model, firmware, host architecture/network and attached source/display details.
- [ ] Back up the real deployment data and verify restoration. Capture starting
  routing, presets, names, audio/video settings and power state. Keep credentials
  and private configuration out of Git/public evidence.
- [ ] Perform read-only checks first. Authorize writes only for the agreed
  scenarios, with restoration/readback reports. Keep preset overwrite and other
  unrestorable operations under their separate gate.
- [ ] **HIL-B:** verify real routing, presets, matrix power, profile/core flows
  and affected settings at their required targets; restore the initial state.
- [ ] **Physical CEC:** observe actual source/TV/receiver effects for power,
  navigation, playback and volume/mute. Record devices/firmware and physical
  observations; command logs or matrix readback alone do not prove CEC effects.
- [ ] **HIL-C:** perform agreed real outage/recovery tests; verify availability,
  reconnect, last-known state and absence of duplicate actions. Preserve fault
  timings, restoration outcomes and any failures as findings.
- [ ] **HIL-E:** verify the physical Remote 3, owner's deployed HA, real browser/
  kiosk devices and available physical Flic hardware, including auth and denied
  actions. Report unavailable hardware explicitly; replay/container/scripted
  clients do not count as those physical-device results.
- [ ] Resolve the 12 feature caps associated with HIL-09 only after accepted
  real-device protocol evidence and the required finding disposition. Keep
  additional linked medium/low findings visible.

## 5. HIL-D: continuous soak and field acceptance

- [ ] Start the field runbook's metrics collection on the deployment host for
  the exact candidate digest, after agreeing on the monitoring window and safe
  operating conditions. This checklist has not started the collector.
- [ ] Preserve continuous 72-hour timestamped health/resource measurements:
  CPU, memory, PIDs/tasks, event-loop lag, availability, restart counts and
  collection gaps. Keep raw data plus analysis/plots; disclose every interruption.
- [ ] Confirm resources remain within accepted reliability limits and explain
  trends/restarts. A restarted collector is not an uninterrupted 72-hour pass.
- [ ] Complete a week of owner daily use with dated observations and explicit
  sign-off. Record which candidate was used and evaluate material changes during
  the window; do not transfer acceptance automatically to another image.
- [ ] Attach valid V5 evidence to the field-target features and maintain distinct
  V4 hardware, V3 software and unvalidated scopes.

## 6. Evidence closure and release publication

- [ ] Schema-validate new evidence and review feature/scenario/client/commit/
  digest attribution, freshness and linked findings. Preserve original failed
  records. Non-applicable client pairs stay non-applicable, not passing.
- [ ] After accepted evidence is recorded, regenerate the feature ledger once
  and then run registry/evidence gates without concurrent generation/checks.
- [ ] Confirm every feature reaches its required target with current accepted
  evidence; investigate stale and capped rows explicitly. The regression gate
  checks recorded baselines, **not** all final target levels.
- [ ] Publish the feature/client validation report, firmware/CEC observations,
  supported-hardware scope, soak analysis and owner sign-off. Keep unsupported
  hardware/versions clearly outside the claimed support scope.
- [ ] With applicable CI/review and visual gates satisfied, merge #36 and create
  `v0.5.0` according to the master plan; integrate main into the stacked work as
  needed. Integrate both #37 and #38 in a reviewed order that preserves the
  runtime candidate. Tag an RC only on the resulting tested main commit.
- [ ] Before final `v1.0.0`, synchronize canonical metadata to `1.0.0`, rebuild
  matching amd64/arm64 artifacts and verify version labels/digests, installed
  entry behavior and affected evidence. Do not relabel existing RC images.
- [ ] Refresh affected proof and owner acceptance when final artifacts change;
  record unchanged-input mappings where justified rather than assuming prior
  field proof automatically applies. Never move an existing release tag.
- [ ] Verify the exact integration/main remote head, release commit/tag and
  published image manifests. Record actual publication receipts and remaining
  limitations. Stop short of final publication while any required gate is open.

## Planning-package acceptance

- [x] Read the actual registry, findings rules and committed-evidence calculation.
- [x] Produce a complete, source-attributed gap inventory without changing levels.
- [x] Link hardware/soak procedures and keep approvals distinct from planning.
- [x] Record documentation/link/consistency checks in the allocation ledger.
  Exact scoped publication status is retained in the post-push receipt named
  there. This item concerns these documents only, not release readiness.
