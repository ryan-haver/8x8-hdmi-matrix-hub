# Comprehensive project review — 2026-11-04

Reviewed integration: `wp-runtime-completion` at **`ac1dc745ebf552b4d762fc33bc25382052b0e9d6`**. This is a coordinator-authored project assessment and corrective proposal requested by the owner. It is not independent source acceptance, a new three-provider phase decision, or authority to launch implementation, change baselines, touch hardware or release. The accepted P0–P5/OWNER program remains intact.

The implementation has a strong passing software baseline. The project is **not yet qualified for the planned release**: two newly identified source/validation gaps, reconfirmed existing defects, three pending integration chains, evidence admission/freshness, compatibility boundaries and real-device/field gates remain. No honest completion percentage follows from test counts or the number of reserved worktrees.

The [corrective plan](../planning/COMPREHENSIVE_REMEDIATION_20261104.md), [machine-readable actions and complete package crosswalk](../planning/comprehensive-review-20261104/REMEDIATION_PLAN.json), and [268-feature baseline](../planning/comprehensive-review-20261104/REVIEW_BASELINE.json) contain acceptance, dependencies and scope. CR identifiers below are audit-local observations, not silently registered new VAL findings.

## What was examined

- Live integration Git state, six retained source worktrees, their ancestry, current handoff/allocation, master/runtime/remediation plans, validation policy and the immutable accepted execution packet.
- Runtime composition, reconnect/reconfigure/cleanup and persistence boundaries; REST access controls, request validation and WebSocket dispatch; shared validation model/runner/evidence code; Flic registration/replay; HA transport/config flow/coordinator; Remote bridge/transport; UI shortcut initialization and viewport configuration.
- Existing test/CI structure, package/version/build metadata, HACS configuration, dependency locks, lint baselines, release/HIL/field runbooks and current qualification/routing restrictions.
- Existing committed evidence using `ledger.compute`, **without** calling the global gate, regenerating the ledger or importing evidence. The previously failed candidate gate was not retried.
- Current GitHub CI jobs and original validation/HA/deployment/UI artifacts. Four ZIP archives were preserved privately, their CRCs checked and their SHA-256 values matched against GitHub's published artifact digests.

This was a broad source and evidence assessment with focused executable counterexamples, not a claim to have inspected every line or rerun every environment. Local execution used Windows/Python 3.12.10 and Node 26.13.0. No local full HA framework, new image campaign, physical hardware, owner network, soak or visual-baseline update was run. Existing CI results are separately attributed below. Current dependency-advisory access returned HTTP 403; this review makes no clean-CVE claim. Two private audit-helper startup errors were corrected before their probes ran; their original scripts remain preserved. They were not project-test failures.

## Verification and current evidence

| Check | Observed result | Practical limit |
| --- | --- | --- |
| Local core suite | **4,082 passed, 6 skipped, 35 deselected**, exit 0; four deprecation warnings | `tests/ha` and `tests/uc` excluded; hardware/Docker deselected; current integration, not pending branches |
| Local scripted Remote suite | **100 passed**, exit 0 | Scripted Integration API client, not a physical Remote |
| Ruff | Pass | Static lint |
| Mypy | Pass, **91 source files** | Current configured type-check scope |
| `pip check` | Pass | Installed dependency consistency, not advisory/security qualification |
| ESLint | Pass | **15 existing suppressions in 11 files** remain |
| Stylelint | Pass against **521-finding baseline** | Not zero CSS debt; baseline unchanged |
| Repository hygiene, all tracked files | **0 errors, 0 warnings** | Does not prove external cache purge or historical licensing closure |
| GitHub CI [41756761049](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/41756761049) | Current head: **14 successful jobs; release publication correctly skipped** | Includes tests, HA, HACS/hassfest, Docker/deployment, UI, validation and gitleaks; job success is not every feature's final acceptance |
| Original CI validation artifacts | **1,513 passing API/browser/scripted-Remote outcomes; 19 passing HA outcomes; 4 passing deployment records** | Original source is the PR merge commit; no canonical import/admission performed |

The local test route-inventory plugin was disabled to preserve the existing root coverage report. This review therefore makes **no fresh local 100% route-coverage claim**. The combined-candidate pipeline must retain that gate. Full direct stdout/stderr, command/isolation receipts, JUnit and temporary originals are under private `build/comprehensive-review-20261104` and `C:/t/comprehensive-review-20261104`.

### The numerical ledger is not the implementation backlog

Read-only calculation over **2,131 committed records** (2,110 passing and 21 historical failing records) at the reviewed head gives:

| Measure | Count |
| --- | ---: |
| Features | 268 |
| Below target under the existing effective-level policy | **210** |
| Software-target features below V2/V3 | **89 of 147** |
| Hardware-target features below V4 | **120** |
| Field-target feature below V5 | **1** |
| Without any fresh passing committed record | **198** |
| Stale-only features | **96** |
| Features capped by an open critical/high finding | **12** |
| Numerically at target | 58 |
| Numerically at target but without a fresh passing record | **16** |
| Finding register | 265 total; **61 parser-open**, 204 closed |

The 61 open records comprise one critical, two high, 31 medium and 27 low **recorded severities**. Some descriptions are historical or resolved in source, others await evidence or owner action. These are not 61 freshly reproduced bugs. Likewise, 210 below-target features do not mean 210 missing implementations. Effective levels can fall back to recorded baselines when fresh proof is absent; raw CI proof and client-specific assertions need separate admission.

| Area | Features | Below target | Without fresh passing committed proof |
| --- | ---: | ---: | ---: |
| Matrix | 31 | 31 | 25 |
| CEC | 11 | 11 | 8 |
| REST/WebSocket | 42 | 24 | 26 |
| Domain workflows | 36 | 25 | 19 |
| Web UI | 36 | 24 | 30 |
| Kiosk | 14 | 7 | 11 |
| Remote | 17 | 17 | 9 |
| Home Assistant | 18 | 18 | 18 |
| Flic | 10 | 3 | 3 |
| Operations/deployment | 20 | 20 | 20 |
| Security | 15 | 12 | 14 |
| Reliability | 18 | 18 | 15 |

These counts supersede earlier dated snapshots **for this reviewed head and committed-evidence method only**. They do not rewrite historical outcomes or accept private/CI records automatically.

## Findings and required dispositions

### CR-01 — WebSocket status requests create unbounded pending work

**P1; newly confirmed source gap; Medium.** [websocket.py](../../src/rest_api/websocket.py) creates a task for every `get_status` frame at lines 104–109. `_replies` is a global retention set; it is not an admission limit. Socket cleanup at lines 85–88 removes the client but does not own/cancel these reply tasks. HTTP request limits, outgoing queues and the maximum number of WebSocket connections do not cap incoming per-frame task creation.

A bounded in-process probe executed the **actual** dispatch/reply functions with a synthetic blocked refresh: **1,000 frames created 1,000 pending tasks**, all of which were explicitly cancelled and drained afterward. This proves the missing admission bound, not a measured production outage or memory threshold. Runtime refresh may serialize work; serialization still leaves queued tasks allocated.

Require bounded/coalesced per-client work, a defined overload response and connection/application-owned cleanup. Tests must hold refresh pending, burst requests, disconnect/shut down, verify bounded outstanding work and preserve another client's service. Preserve the existing status schema and fresh-read semantics. Map to existing `SW-API-READ-02/03` and security-control acceptance, with one coordinator-owned shared-path lease.

### CR-02 — HA setup does not establish that a supplied key can control a locked hub

**P1; new source/coverage gap; Medium.** [config_flow.py](../../custom_components/hdmi_matrix/config_flow.py) probes public health, then tolerates a device-read `HubError` to support an offline matrix. It never checks the supplied key's capability. Public reads therefore cannot establish authentication.

The actual [HA transport](../../custom_components/hdmi_matrix/api.py), against the actual local REST app with a synthetic control PIN, accepted health using an invalid key; `/api/auth/status` reported `control_pin_set=true` and `session_level=none`; the control write returned **401** before any matrix action. Only the transport's timeout constant was supplied through a dependency shim; the HA framework/config-flow itself was **not** executed locally. The source branch through `_probe` is clear, but a full real-HA flow regression must establish the final framework behavior.

Use the existing **nonmutating** auth-status endpoint and its actual bare-JSON contract; do not test credentials by switching hardware. Add real-HA wrong/missing/revoked/valid-key setup, options/reconfigure and recovery cases. Preserve unlocked-hub and offline-matrix setup. This belongs in `SW-HA-PREP-01/03`.

### CR-03 — advertised keyboard shortcuts miss the live controllers/views

**P2; reconfirmed existing UI-06, not a duplicate new bug.** [keyboard-shortcuts.js](../../web/js/components/keyboard-shortcuts.js) targets `window.settingsPanel`, while [app.js](../../web/js/app.js) initializes `window.app.components.settingsPanel`. Shortcut `4` targets `data-tab="scenes"`, but [index.html](../../web/index.html) uses `profiles`.

A minimal Node VM ran the actual shortcut handlers against the actual HTML tab identifiers: settings callback count **0**, scenes click absent, Matrix navigation positive control successful. This is a bounded handler/initialization reproduction, not full browser acceptance. Repair wiring and add real browser keyboard/focus/edit-field tests. Keep approved identifiers and compatibility constraints.

### CR-04 — credential redaction remains broken in the integration source

**P0 execution order; existing VAL-15 Medium tooling defect.** The actual [evidence redactor](../../tools/validate/evidence.py) preserves a nested synthetic `X-Admin-PIN` while masking `X-API-Key` and `Authorization`. Public header values remain intact. No actual owner credential disclosure was observed.

The fix already exists in the retained privacy chain; review and integrate it rather than commission a duplicate fix. Its full nested-header/action/procedure/response/artifact boundaries need qualified different-family review and privacy admission. Preserve all historical raw originals privately. Resolve this before claiming newly captured credential-bearing evidence is safe to admit. See [original finding](../production/software-waves/SW-SEC-DATA-02-C1/FINDING.md).

### CR-05 — six retained source worktrees contain three integration chains

**P0 integration work.** All six pending source trees were clean at inspection. Git ancestry proves API-client C1 is contained in C2, and privacy C1 is contained in C2 and then C3. The API-read/WS chain is separate. They are **three chains**, not six independent missing implementations:

| Chain | Final retained source | Outstanding boundary |
| --- | --- | --- |
| API-client refusal C1/C2 | `caaa4faabe9ede1e3aed37d2269efd4a4d691e04` | Bounded source review PASS; secondary report evaluation, security freshness and combined acceptance remain |
| API-read/WS | `1fbfee112cc503ffa273c19dc565092d01fe2d6b` | Exact full-chain independent review/evidence disposition |
| Privacy C1/C2/C3 | `2d02004d3108953a302e1a49aab9a5f24e944136` | Qualified privacy/tool review and admission |

Shared `runner.py`, `model.py`, evidence and API-client changes require serial coordinator composition. Do not blindly merge all six trees, duplicate writers or transfer one chain's proof to another. Preserve actual OpenAI/current and earlier DeepSeek authorship. The [API review disposition](../production/software-waves/RV-API034/execution-20261101/SOURCE_REVIEW_DISPOSITION_20261103.json) remains a partial acceptance boundary.

### CR-06 — API-C2 changes invalidate the existing security V3 proof

**P0 integration gate; existing M-1, not a demonstrated product-security regression.** At exact `caaa`, C2's covered runner/model edits stale **all 16 F-SEC-007 V3 records**, leaving four fresh V2 records. The [independent review](../production/software-waves/RV-API034/execution-20261101/REVIEW.md) statically establishes onset and preserves the historical failed gate.

Freeze all relevant shared-tool/source edits first; then execute separately scoped new eight-browser-scenario security proof and required API controls at the correct candidate. Preserve separate and combined summaries, obtain qualified security review and privacy admission. No unchanged failed-gate rerun, target downgrade, borrowed nonancestor WS proof or reconstruction of lost bytes resolves this.

### CR-07 — current CI proof names a synthetic PR merge, not the integration commit

**P0 evidence admission; confirmed, despite green CI.** The current run's reported PR head is `ac1dc745`, but all **1,536 inspected validation/HA/deployment records** name **`c9dac37abccbe66cfed383379c44cf6061cbc787`**, GitHub's synthetic merge. Its parents include `ac1dc745`; it is not an ancestor of that branch head.

The fetched Git objects prove the two full file trees are **identical** (`2bf33c502f0a6a2b4e106608c7d4574426ca5877`). This is strong source-equivalence evidence and preserves the value of the CI run. It does **not** satisfy the current ledger's ancestry rule. Relabeling the record commit would falsify provenance. These passing archives also do not test the unintegrated `caaa` candidate.

Keep PR-merge CI as integration testing. For canonical acceptance, run new proof at an explicitly selected accepted candidate ref with valid ancestry and source/image/client attribution, or adopt an exact tested candidate only through the existing accepted integration process. This addresses `EV-CI-ATTRIBUTION`/combined proof; it is not permission to weaken freshness or manufacture missing historical originals. Inspect assertion completeness before deciding how many apparent gaps actually need new tests or code.

### CR-08 — finding and current-status records require reconciliation

**P1 metadata correctness.** The parser-open register includes UC-18's historical nonfunctional-path description, SEC-14's obsolete "LICENSE is a stub" clause, and HIL-09 text that says fixed/proven while its formal cap remains. Accepted triage already distinguishes resolved-source, partial, reproduction-needed, hardware and owner conditions.

`EXECUTION_READINESS.md` leads with a scoped Opus 5.5 update but retains older current-tense "no qualified domain"/next-qualification instructions. The mutable gate JSON also retains an obsolete top-level `owner_decision_pending` statement alongside the later completed qualification. Preserve history, but make current status unambiguous. Do not ask for already recorded approval again.

Reconcile each exact finding's surviving conditions with accepted source/image/client evidence. Do not close the 12 HIL-09 caps from parser text or code presence. Do not spend another implementation round fixing already accepted code solely because a row still reads open.

### CR-09 — UI/kiosk accessibility and mobile acceptance remain incomplete

**P2; mixed confirmed settings and unverified residual hypotheses.** Both app/kiosk viewport declarations suppress user zoom; the kiosk also sets a maximum scale. This is source-confirmed configuration, not a claim about every browser's enforcement. The older accessibility/overflow/persistence findings still need actual supported-device reproduction.

Qualify keyboard/focus/modal behavior, zoom, contrast, long names, phone/tablet routing views, kiosk persistence and recovery through real browser actions plus request/device effects. CSS's 521 baseline findings and ESLint's 15 suppressions are debt, not 536 newly reproduced product failures. Existing three Tron approvals remain valid; only new changed visuals need new owner decisions. Avoid turning broad CSS/module/dead-code refactors into automatic MVP prerequisites.

### CR-10 — declared minimum versions exceed the demonstrated test matrix

**P1 compatibility proof, not a proven incompatibility.** [hacs.json](../../hacs.json) declares HA **2025.1.0**. Historical testing at **2025.1.4** does not establish that exact floor; the ordinary HA test environment uses a separate Python 3.13/plugin pin. Core CI/local checks use Python 3.12 while `pyproject.toml` declares **Python >=3.11**.

Test the exact supported floors, or reconcile the claims through an explicit compatibility decision. Cover HACS custom-repository install/upgrade, setup, auth, options/reconfigure and unload/reload. HACS validation passing is useful packaging evidence, not proof of the owner's deployment or default-catalog listing. Default-catalog publication is not invented as an MVP requirement.

### CR-11 — software integration exists; physical acceptance does not

**Release gate.** Flic SDK templates/generated-JS replay, the HA custom component/HACS packaging, and the Remote bridge/scripted tests exist. The current 100-test Remote run and 19 CI HA outcomes reinforce that distinction.

Remaining software/client work includes candidate-correct Flic auth/failure/registry/request/effect admission, real HA installation and recovery, and the required client-specific feature contracts. Physical button/radio/SDK behavior, physical Remote control, owner HA/LAN discovery, matrix firmware protocol effects and attached-device CEC effects need the actual environment. Follow HIL-B/C/E, backup/read-only-first, agreed disruptive actions and explicit restoration. None can be closed by another mock or screenshot.

### CR-12 — final release artifacts, support, licensing and advisory closure remain

**Release gate.** Hub, driver and HA metadata currently agree on `1.0.0rc1`; no version mismatch was found. Current hygiene/gitleaks/CI passes are positive observations. They do not authorize a final version, tag, main merge or artifact publication, prove external cache purge, or establish dependency advisory status.

Finish the exact remaining SEC-14/cache-purge owner condition without a new history rewrite; reconcile stale licensing claims. Obtain an appropriate current dependency-advisory assessment: the attempted GitHub read was unavailable (403), not evidence of a vulnerability or a clean audit. Bind authorized matching versions, shipped licenses/assets/dependencies, amd64/arm64 artifacts and immutable image digests to the accepted candidate, then independently audit the full software pipeline. Later metadata/source changes need their applicable evidence refresh.

### CR-13 — the soak and field week are actual outstanding measurement windows

**Release gate.** [The field runbook](../validation/RUNTIME_FIELD_GATE_RUNBOOK.md) contains an existing sampling recipe. Its presence is not proof of a working uninterrupted collector or a completed run. F-REL-018 remains below V5.

Qualify collection/continuity/restart handling first. On the accepted deployment digest, preserve 72 continuous hours of CPU, memory, PID/task, loop-lag, availability and restart data, plus a documented owner week and sign-off. Windows may overlap only with approved conditions and stable candidate identity. Do not combine interrupted intervals or transfer acceptance automatically after material changes. No collector was started by this review.

### CR-14 — reviewer coverage and protected resources constrain execution

**P1 staffing; P3 cleanup.** Opus 5.5 is qualified only for the named runner/model/refusal domain, not blanket privacy/security/UI/HA review. OpenAI, Anthropic and MiniMax are not interchangeable pool/competence labels; DeepSeek is unavailable and Gemini remains unverified. Verify capacity and qualified author/reviewer/correction coverage before each actual dispatch. Capacity observations are dated, not a funding promise.

Retain the two old unverifiable workspaces and stale persistence folder until installed Orca recovery proves their state. The completed 33-tree cleanup should not be repeated. Keep root/private data, published task refs, original evidence, full archives and uncertain writers protected. Ordinary covered corrections do not need ceremonial planning repeats; material outcome/contract/strategy/family changes still require the prospective three-provider process.

## Recommended outcome

First make current truth and staffing reviewable, finish privacy/source reviews and repair the reproduced bounded defects. Then serially compose a stable candidate and run/admit candidate-specific proof, rather than repeatedly invalidating security evidence between shared-tool edits. Complete the remaining mapped software/client contracts and exact-version/build matrix before scheduling one stable physical/field candidate.

The [execution plan](../planning/COMPREHENSIVE_REMEDIATION_20261104.md) cross-references **all 30 existing packages / 65 units / 268 feature IDs** and distinguishes software RC readiness from HIL/field/final-release acceptance. It preserves existing phase ownership and does not launch another worktree or worker.
