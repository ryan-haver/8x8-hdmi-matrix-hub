# Proposed final plan for Round 2 decisions

Version 1, 2026-11-13. **PROPOSED, NOT CONSENSUS, NO IMPLEMENTATION GO.**
Authority: owner workflow `msg_b052a16e725b`, candidate trial clarification
`msg_13f63a372426`, CR-01 hold confirmation `msg_950ea1f660ca`, and Fable capacity
hold `msg_1cb08e28729c`. Existing Run `run_37205f6095b3`, workflow
`task_c94bdfc187f6`. Exact source is `f2a122f955def578960303bc15242fed00d01be3`,
tree `3384886fc4e624175046536bfd13e998923d5933`, base `680e93b8`.

Three genuine independent R1 opinions were captured, hashed and lifecycle-settled
before exchange: [Sol](R1_SOL.md), [Opus](R1_OPUS.md), [Argon](R1_ARGON.md).
[ROUND1_REPORTS.json](ROUND1_REPORTS.json) pins original bytes and authorship.
These reports are planning input. Neither a clean planning verdict nor two votes
establishes source acceptance. R2 must explicitly accept or challenge **this exact
plan hash**, identify per-decision agreement and retain unresolved disagreement.
No third round is invented. Irreconcilable/material choices go to the hub.

## Reconciliation and proposed decisions

### D1 — CR-01 authority and existing source: HELD

All three seats recommend preserving `3eb45919` as unaccepted candidate history.
The hub independently confirms `D6_PROVENANCE_HOLD.json` still says
`HELD / NOT_DISPATCHABLE_AS_SCOPED`, `wiring_leases_granted: 0`; no existing
authority supersedes it. Preserve NOT_GRANTED/WSR03 and actual Anthropic authorship.
No new WS lease, wiring, intake, qualification attempt, target narrowing, attribution
relabel, retake, acceptance or landing follows from this plan. The hub is taking
the existing wired-candidate-versus-later-exclusion disposition to the owner.
Both options preserve this branch/history. Do not choose one before that decision.
Independent covered TLS/HA/UI/floor planning can continue.

### D2 — WS technical direction: CONDITIONAL DESIGN ONLY, NO AVAILABLE GRANT

Sol/Argon reject silent stale coalescing and want app-isolated membership/broadcast;
Opus accepts coalescing and defers global isolation. Proposed reconciliation:
preserve caller-visible freshness and recovery in the accepted
`functional-completion-20261104/ADOPTION_NOTES.md:7`. An overlapping request must
receive an existing, documented bounded busy/error response or a proven fresh
post-request result; it cannot silently rely on an older in-flight snapshot.
Prefer bounded busy/error, with no unbounded trailing-task queue or new protocol
envelope. Resolve membership, cap and broadcast ownership per app; any deliberate
additional process budget must be explicit, not incidental module-global state.
The accepted prospective application-read cap is **4**, distinct from client cap32;
candidate constant8 is not silently accepted or made configurable above that cap.
Drain/cancellation must report resistant remaining work honestly and fence late
replies. These are proposed tests/directions only until D1 and qualification gates
resolve. Do not rerun failed qualification exercises under another label.

### D3 — H1 host identity, TLS and rebinding: PROPOSED ORDINARY CORRECTION

All three reject name-to-IP replacement as final behavior. Preserve the configured,
persisted and displayed hostname and existing URL/SNI identity, including verified
TLS (`OREI_VERIFY_SSL=true` and custom CA), while validating the actual destination
on each HTTP/Telnet connection and reconnect. Prefer a validating resolver/connector
and a validated Telnet connect boundary; cover literal IP paths too. Reject unsafe
or mixed address sets without a second unchecked resolution; do not disable
verification, weaken fingerprints, allow public/link-local/loopback destinations
or bypass same-host reconnect/port updates. Preserve the backend fresh-credential
requirement. No real matrix, credential or LAN probe is authorized.

This preserves the original hostname contract instead of adopting the candidate's
new IP-display/save behavior. Opus calls the saved/displayed choice a coordinator/
owner contract decision: R2 must explicitly determine whether preserving the base
contract is an ordinary corrective choice within owner scope, or cite the material
decision that still needs escalation. Do not infer agreement from the preferred
implementation alone. A hostname/IP/custom-CA/fingerprint/rebinding/reconnect test
matrix using synthetic loopback fixtures is required before acceptance.

### D4 — REST result and scene semantics: CONDITIONAL CONTRACT RECORDS

Keep rollback HTTP200 with honest `applied:false`, preserving the existing tested
rollback behavior; callers must not report or persist success on an unapplied
change. Explicitly document and test `applied`, unknown-scene404 and HTTP matrix
default port443, keeping HTTP/Telnet port roles distinct. Coordinator owns registry,
OpenAPI, simulator/read assertions and serial ledger changes. These records cannot
be omitted merely because old route tests pass. Maintain 100% of actual registered
routes; 177/177 is an earlier candidate observation, not a permanent denominator.
Do not promote canonical evidence/feature levels from this work.

### D5 — H2 HA: PROPOSED FAIL-CLOSED COMPATIBILITY CORRECTION

All agree the floor API accepts data/options, but that does not establish floor
behavior. Sol rejects unconditional404=>unlocked and malformed200 objects; Opus/
Argon accept404 for assumed pre-lock compatibility. Proposed reconciliation:
fail closed on missing/malformed auth capability unless a documented, positively
identified supported legacy version/capability proves the safe fallback. Health200
alone does not prove that a missing auth route means unlocked. If reviewers can
establish that compatibility contract with exact evidence, identify it explicitly;
otherwise use cannot_connect/invalid-response handling and document compatibility.
Do not broaden/remodel the auth protocol. Add exact-one-reload assertions for
options and reconfigure, migration precedence/key clearing, and missing/wrong/
revoked-key and malformed-auth controls. Run the HA suite on actual2025.1.0 and
the already tested2026.2.3 with compatible interpreters/dependencies in isolated
containers; no support-floor success is claimed before actual execution.

### D6 — H1 password fields and existing visible UI changes: CAPTURE/REVIEW GATED

All three prefer masked password input in both current settings surfaces, using
existing General-drawer forwarding; keep the unloaded unified drawer unloaded.
Send only when required for host/port changes, clear secret UI state after save/
close, never persist/log it, and handle `applied:false` honestly. No backend
credential relaxation or automatic native-menu answer is permitted.

The exact rule is `docs/REMEDIATION_PLAN.md` section5.3: capture affected catalog
entries **before and after every UI change**, present the before/after review for
owner sign-off **before a PR is opened**, use the pinned Linux Playwright renderer,
and keep baseline approval owner-only. Proposed sequence: obtain verified before
captures first; only then implement the agreed isolated forms/behavior; capture
after/error/keyboard/responsive states and both existing text changes; prepare a
concrete review page; hold PR/landing/baseline updates for explicit owner approval.
No look-and-feel redesign, baseline update or Phase5 expansion is authorized.
Sol's stronger phrase "owner visual prerequisite before form edits" must be
reconciled against the exact rule or a stricter cited current owner decision;
do not add a routine permission step without its actual source.

### D7 — H5 privacy: DEFER, NO IMPLEMENTATION LEASE

All agree H5 is real and the held `privacy-c4` lane must not be copied/cherry-picked,
renamed, retried or integrated here. Overlap means other unlanded privacy chains
share validation paths; it does not mean these five Fable commits touch those
paths. Coordinator may map exact existing refs/provenance read-only. Respect the
owner-only extra-attempt budget and all-six-axes privacy standard. Do not launch
the proposed assessment or full-chain review without its actual prerequisites.
Keep source acceptance of that chain held; no new privacy opinion is counted here.

### D8 — M5 Python floor, L2 lint and device limits: SEPARATE COORDINATOR WORK

All prefer honest>=3.12 metadata/docs/classifier to an unproved3.11 claim; a3.11
alternative needs an actual complete hashed re-lock and install/core CI. No lock
edit is proposed. Coordinator retains exclusive root-manifest/config/CI ownership.
Sol/Argon propose enforcing existing UI lint; Opus defers it. Proposed direction:
make lints genuinely blocking with a deliberate failing-lint check, without
baseline/suppression broadening or unrelated CI changes. This is a separately
leased coordinator package with its own author-family attribution, qualification,
independent exact-SHA review and normal gate; it grants Fable no root-file writes.
Defer if those independent acceptance prerequisites are unavailable.

Opus additionally identifies MAX_DEVICES silent eviction and locked-peer eviction.
Do not silently declare those harmless or expand implementation. Record their
exact contract/risk for owner/coordinator disposition; no new limit change is
granted in this bounded ordinary-fix package. Preserve intended Flic `?key=` auth,
the documented run_server alias, and hashed-lock include behavior. L3/L4 receive
no architecture, storage or release expansion.

## Exact proposed grants and validation

These grants become available only after actual R2 agreement, all named entry
conditions, coordinator serial lease and a fresh Fable admission decision. No
second writer may edit a shared path. Shared contracts, manifests/locks, canonical
registries/evidence, integration and qualification decisions stay coordinator-owned.

| Package | Proposed exclusive writable files | Entry and meaningful validation |
| --- | --- | --- |
| Fable H1 transport | `src/rest_api/settings.py`; `src/orei_matrix.py`; `src/telnet_client.py`; `SECURITY.md`; `tests/test_settings_matrix_host.py`; `tests/test_security_ssrf_tls.py` | D3 agreement; explicit serial transport lease; synthetic name/IP/CA/verify-true/fingerprint/bad-address/reconnect cases; do not alter credentials or runtime data |
| Fable H2 HA | `custom_components/hdmi_matrix/api.py`; `custom_components/hdmi_matrix/config_flow.py`; `custom_components/hdmi_matrix/__init__.py`; `tests/ha/test_api.py`; `tests/ha/test_config_flow.py`; `tests/ha/test_init.py`; `docs/HOME_ASSISTANT.md` | D5 agreement; capability/shape/fallback, migration/key clearing and exactly-one-reload controls; actual declared-floor/current HA suites |
| Fable UI/captures | `web/index.html`; `web/js/components/settings-panel.js`; `web/js/components/general-drawer.js`; `tests/test_ui_classic_api_and_shortcuts.py`; `tests/e2e/flows.spec.ts`; `tests/e2e/visual/catalog.ts`; new owned review-artifact subtree | D6 exact visual sequence; before capture before code; no CSS/tokens/look-and-feel/baseline edits; before/after owner sign-off before PR/landing |
| Coordinator REST records | `src/hub/openapi.py`; `docs/validation/features.yaml`; `tests/sim/test_sim_rest_reads.py`; `tests/validation/scenarios/contracts.py`; `tests/validation/scenarios/scenes.py`; generated `docs/validation/LEDGER.md` only through supported generator | D4 explicit contract disposition, own disjoint serial package and independent review; actual route100%; ledger generation never concurrent with registry/full hooks |
| Coordinator M5/L2 | `pyproject.toml`; `CONTRIBUTING.md`; `docs/agent-process/REPO_CONFIG.json`; `.github/workflows/ci.yml`; `tests/test_packaging_version_sync.py` | D8 separate lease/independent-family review;3.12 clean install/core compatibility; honest failing-lint proof; no lock/suppression changes |
| CR-01 / H5 | **None** | D1/D2 and D7 holds remain; proposed future tests are not implementation, review or attempt authorization |

Combined validation after corrections must use exact committed source, clean
working-tree equivalence and isolated synthetic data/config. Run the applicable
normal hook/core suite, Ruff/Mypy, both UI lints, separate UC/HA, pinned browser/
visual flows, simulator REST contract/scenario checks and deployment-image tests
where authorized. Record actual pass/fail/error/skip/deselection counts, images,
versions and source attribution. Inspect skips. Negative controls must fail for
the actual wrong-key, rollback, TLS/address, malformed-response and lifecycle
conditions; do not manufacture missing originals or repeat failed qualification
attempts. No physical HIL,72-hour soak, week field or final artifact release GO.

## Staffing, independence and admission

Original owner-pinned Fable5.2/high remains the remediation author. **New Fable
admission is held** while its dedicated pool is below30% (observed27%); both it
and the general Claude pool must be actually healthy at the next admission.
A reset time is not proof, and no polling, new account, credits or substitute
author is authorized. Planning/spec preparation continues independently.

Final acceptance is fresh, read-only, qualified at the exact corrected SHA and
independent of **every actual implementation author family**. Opus/Fable are one
Anthropic family; Sol/Astra/Luna one OpenAI family. Planning prose is not relabeled
as code authorship, and mechanical integration does not erase actual authors.
If OpenAI coordinator implementation and Anthropic implementation share a final
candidate, a Sol-only whole-head review is insufficient: an eligible qualified
third family must cover it, or the affected intake remains held. Separate package
reviews do not waive the required final-head independence. Establish reviewer
qualification/capacity before implementation admission; planning participation
does not itself qualify a source reviewer. No automatic extra assessment/retake.

At most three active workers plus coordinator, no helpers/nesting. R2 uses three
fresh explicitly pinned native Tasks, sequenced with at most two active seats,
verified actual model/account/high/full-access/healthy pool before assessment GO.
No follow-up send may assume a completed worker preserves its original model.
The incidental Carbon diagnostic Task remains **failed**, is not an Argon opinion,
and did not edit the genuine completed Argon report. Its output is excluded from
consensus; native lifecycle/source provenance is recorded in TRACKING.json.

After actual R2 decisions, publish an honest consensus/disagreement record with
per-item status and exact grants. Eligible ordinary work proceeds without another
routine permission request once actual admission prerequisites pass. Human-only
choices and normal exact-SHA landing/publication gates remain held. Author fixes;
reviewers report. No push/merge/source approval is granted by this proposed plan.
