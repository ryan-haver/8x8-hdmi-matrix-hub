# SW-AUDIT-01 — global remaining-acceptance inventory (author report)

**Report-only.** One new tracked file. No source, test, tool, fixture, scenario,
schema, registry, ledger, evidence, baseline, manifest, lockfile or runtime
change was made. This report **completes the disposition mapping of all 268
registry features**; it does **not** qualify a feature, does not accept
evidence, does not close a finding, does not admit private artefacts, does not
set a new MVP scope, and does not claim a completion percentage.

| Authority | Value |
| --- | --- |
| Task / Dispatch | `task_45eb6e2ea9fc` / `ctx_a0c78df4a3b9` |
| Run | `run_37205f6095b3` (existing Run; not reset or replaced) |
| Worker terminal | `term_9e6b3a2a-6c65-4634-9817-e6e1eeedd88c` |
| Coordinator terminal | `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| Worktree | `wp-exec-sw-audit-01` (Orca-managed), branch `execution/wp-exec-sw-audit-01` |
| Assigned base (injected) | `b4a2c6e93918028e080fdc5ed3d7abedb3f14a9e` |
| **Verified full HEAD at start** | `b4a2c6e93918028e080fdc5ed3d7abedb3f14a9e` — **equal** to the injected spec base (checked before any write; `git rev-parse HEAD`, exit 0) |
| Working tree at start | clean (`git status --short` empty) |
| Accepted packet (authority, immutable) | `52ed758e711891ee57be0bbadb87c688333049733e697a52829cf0ba87d7b15e` = `docs/agent-process/phases/execution-pinning-20261101/FINAL_PACKET.json`, verified by SHA-256 over raw bytes |
| Frozen rubric | `66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672` = `docs/production/software-waves/MVP-EXECUTION-20261102/QUALIFICATION_RUBRIC.json`. Verified at the shared **root** path `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/docs/production/software-waves/MVP-EXECUTION-20261102/QUALIFICATION_RUBRIC.json` (read-only, 3 384 B, SHA-256 = `66f37090…`). This worktree's checkout of the same file is 3 426 B with 42 CRLF sequences and hashes to `66f37090…` after LF normalisation — i.e. the same content under Windows line-ending conversion. Referenced only; not modified. |
| Route | native `minimax-coding-plan` / `MiniMax-M3` (thinking), OpenCode 2; no helper, no subagent, no plugin, no fallback, no route substitution |
| Exclusive tracked write | `docs/production/software-waves/SW-AUDIT-01/execution-20261101/AUTHOR.md` (this file) |
| Private scratch | `build/software-waves/SW-AUDIT-01/execution-20261101/author/**` (git-ignored, `.gitignore:7 build/`) |
| One-off scratch | `C:/t/exec-sw-audit-01/nov02-attempt01/**` (fresh per invocation) |

---

## 1. What this report is, and what it is not

This is the **global inventory** that the parent `SW-AUDIT-01` unit scope
defines ("Reconcile every manifest feature with actual source,
`Scenario.features_for(client)`, assertions, `covers`, original records and
current-head CI … Produce per-feature preserve/rerun/missing-assertion/
actual-defect decisions; no code edits or level changes",
`FINAL_EXECUTION_PINS.json` → `SW-AUDIT-01`). It answers, for each of the 268
registry features: which bounded unit owns it, what client/effect assertion
coverage exists in the **current** source, what the canonical proof disposition
is, which source/scenario/evidence references back it, and the single next
exact acceptance action.

It is **not**:

* a source review, a privacy review, a code-correctness opinion, or a
  qualification of any feature, unit, package or candidate;
* a re-run of any scenario, validation campaign, formal gate or ledger
  generation (`python -m tools.validate ledger` was **not** run);
* an admission of the private CI, Flic or privacy artefact sets;
* a new MVP scope, a level promotion or demotion, a target change, a finding
  closure, or an obligation deletion;
* a claim that any P2/P3/P4/P5 acceptance test has already run.

Historical accepted results are **reused and cited, not redone**. The earlier
audit slices named in the dispatch — the coordinator's factual review of the
freshness delta ([COORDINATOR_REVIEW.md](../COORDINATOR_REVIEW.md)),
the accepted freshness delta itself
([FRESHNESS_DELTA.md](../FRESHNESS_DELTA.md)), the CI evidence review
([CI_EVIDENCE_REVIEW.md](../CI_EVIDENCE_REVIEW.md)), the Flic evidence review
([FLIC_EVIDENCE_REVIEW.md](../FLIC_EVIDENCE_REVIEW.md)) and the W03 close
inventory
([W03-CLOSE-INVENTORY/AUTHOR.md](../../W03-CLOSE-INVENTORY/AUTHOR.md)) — are
the authority for the parts they already accepted; this report re-derives only
what they did not (the global mapping, and the live-source assertion coverage
of the rows they did not cover).

---

## 2. Exact inputs (read-only; byte identities)

All inputs are repository files at the verified base `b4a2c6e`. SHA-256 over
raw working-tree bytes; Git blob identity is used where line-ending
normalisation matters.

| Input | Bytes | SHA-256 (working-tree bytes) | Role |
| --- | ---: | --- | --- |
| `docs/validation/LEDGER.md` | 74 823 | `c03538c14f0081e4ed3950f53b74eb3225b4b9e37e05e6b00e48a4670306a3b6` | canonical 268-row ledger (Git blob `281a7647b41e816529d8b7d953df7705a3084d98`, identical at `e2161484459da65aee14433136a14963507b499c` and at the base) |
| `docs/validation/features.yaml` | 537 605 | `a8c6d592bbded20af6d2b8d587c5ce81a48bf98931b0372727e09a261b0cdc8e` | feature registry: target, recorded level, basis, evidence, findings, declared scenarios |
| `docs/validation/findings_pending.yaml` | 2 095 | `54726f451b03e8023a2965779285d57421eee5235c365fbf5e5ca46c61a83779` | open provisional findings (`VAL-14`, `VAL-15`) |
| `docs/planning/software-waves/manifest.json` | 1 240 981 | `bd02be4552323f6545ce799ec6ae91847e608ad0080e8c3411e0e033d2e5568c` | **historical (2026-10-20) planning snapshot** — used only for package/unit ownership and declared client mappings, never for current readiness |
| `docs/agent-process/phases/execution-pinning-20261101/FEATURE_CONTRACTS.json` | 363 108 | `ec5ec2378bf79510966d3e4d8498923e1b60ce28008852ea8b85ce8864f4bb76` | per-feature contract: target, interfaces, required observations, scenario snapshot |
| `docs/agent-process/phases/execution-pinning-20261101/FINAL_EXECUTION_PINS.json` | 982 942 | `e68f1ff2843676e24d8a9f6757edf78e90bc5bf167c0c53ae591b552a9615b1d` | 85 execution pins: phase, unit, dependencies, base rule |
| `docs/planning/software-waves/EXECUTION_READINESS.md` | 17 204 | `c4c6230f3ade60cd7cda3af30ee2c43a9ef79cacf841b4b8ad0820319e674aea` | 85-entry phase/route/base table |
| `tests/validation/scenarios/**` (39 modules) | — | imported at the base | live declarative assertions: `Scenario.features_for(client)`, `expect`, `covers`, `clients` |

The manifest's own counts (`software_below_target: 84`,
`software_numerically_at_target: 63`, `below_target_total: 205`,
`stale_snapshot: 57`) are the **historical** snapshot and are **not** used as
current readiness; the canonical current numbers in §4 come from the committed
ledger.

---

## 3. Method

1. **Ledger parse.** All 268 feature rows were parsed from
   `docs/validation/LEDGER.md` at the base, splitting on **unescaped** pipes
   only (regex `(?<!\\)\|`) so that the three titles containing escaped pipes
   (`F-API-004`, `F-API-009`, `F-API-018`) survive intact, and stripping the
   capped-level suffix (`V1 (capped)`) while recording the cap separately.
   Em-dash cells were read as "none" (`freshness` `—`, `open findings` `—`).
2. **Live assertion extraction.** The scenario registry was imported from the
   **current base** (`tools.validate.scenarios.discover()` → **1 507
   scenarios**) and, for every scenario and every declared client, the feature
   set was taken from `Scenario.features_for(client)`, the expectations were
   rendered with `Expectation.describe()`, and the `covers` path groups were
   read. This is static declaration inspection only: no scenario was executed,
   no service was started, no record was written.
3. **Contract effect coverage.** For each feature, the WebSocket effect names
   in `FEATURE_CONTRACTS.json` were searched in the expectation descriptions
   of the scenarios that declare that feature (**bound**), in the descriptions
   of the whole corpus (**anywhere**), and the two were distinguished:
   * `asserted-bound` — the effect is asserted by a scenario that declares the
     feature;
   * `asserted-elsewhere` — the effect is asserted in the corpus, but only
     under a different feature id (an attribution gap, not a missing
     assertion);
   * `not-asserted-anywhere` — **no expectation in the corpus asserts the
     effect** (a genuine missing assertion);
   * `no-scenario` — the feature has a WebSocket contract but no scenario
     declares it;
   * `no-ws-effect` — the contract declares no WebSocket effect (the effect
     is a device/storage/rendered-state effect that this method cannot check
     mechanically — see §10).
4. **Client coverage.** The clients that can prove a level were taken from
   `tools/validate/model.py`: `api` proves **V2**, `browser`/`ha`/`uc`/`flic`
   prove **V3** (`REAL_CLIENTS`, `level_for`). A feature whose target needs
   V3 but whose live coverage is `api`-only therefore has a **missing
   client**, not merely stale evidence.
5. **Ownership.** The owning bounded unit and its phase come from the
   manifest (`primary_package`, `dispatch_unit`) cross-read against
   `FINAL_EXECUTION_PINS.json` (phase, base rule, dependencies). The manifest
   is used **only** for ownership; a `planned` flag is never read as missing
   code, and an accepted historical scope is never reopened.
6. **Findings.** Open provisional findings are read from
   `findings_pending.yaml` and the registry's per-feature `findings` list. A
   finding is called a *reproduced defect* here only when it is open **and**
   its corrective package has no dispatched replacement (that is `VAL-15` on
   `F-SEC-014`). `VAL-14` is open as a register row but its source correction
   is already merged and independently reviewed (`0bd3d76f`), so it is not
   re-reported as an unfixed defect.
7. **Cross-check against the accepted slice.** The 54 rows the accepted
   freshness delta changed (39 `fresh → stale`, 15 other) were re-parsed from
   the accepted report and compared row by row with this inventory (§9).

**Reproduction.** All analysis scripts are in the private ignored subtree
`build/software-waves/SW-AUDIT-01/execution-20261101/author/`
(`build_inventory.py`, `render_table.py`, `crosscheck_accepted.py`,
`probe_details.py`, `hash_all.py`); the machine-readable result is
`author/inventory.json` (all 268 rows with every derived field) and the
rendered table is `author/table268.md`. Nothing in that subtree is tracked.

---

## 4. Canonical counts — reproduced exactly

Every number below was recomputed from committed bytes at the base and
**matches the canonical current snapshot exactly**.

| Measure | Recomputed here | Canonical |
| --- | ---: | ---: |
| Registry / ledger features | **268** | 268 |
| Below target (numerically) | **210** | 210 |
| At target (numerically) | **58** | 58 |
| Stale evidence rows | **96** | 96 |
| Fresh evidence rows | **70** | 70 |
| No evidence record | **102** | 102 |
| Capped at V1 by an open critical/high finding | **12** | 12 |
| **Software targets** (contract target ≤ V3) | **147** | 147 |
| — numerically **at** target | **58** | 58 |
| — numerically **below** target | **89** | 89 |
| **Physical** targets (V4) | **120** | 120 |
| **Field** targets (V5) | **1** | 1 |

Features are counted separately from CI records (56 CI records at a
non-ancestral source) and from task/entry counts (85 execution entries).
`58 + 89 = 147`; `147 + 120 + 1 = 268`; `89 + 121 = 210`; `58 + 210 = 268`.

The 121 physical/field-target rows are all numerically below target by
construction (their targets are V4/V5 and the software ceiling is V3); the
"physical owner gate" / "field owner gate" dispositions therefore describe
the *binding* gate for the rows whose software side is already satisfied, and
the software gap is named explicitly for the rest.

### 4.1 Disposition census

Canonical disposition, all 268 rows:

| Disposition | Rows | Meaning |
| --- | ---: | --- |
| `PRESERVE` | **40** | Fresh passing evidence at/above the software ceiling; nothing to redo |
| `RERUN-FRESH` | **40** | The existing scenario/client proves the feature but the evidence is stale or absent; re-run it at the current source |
| `MISSING-ASSERT` | **106** | No live scenario declares the feature (99) or the contract's WebSocket effect is asserted nowhere in the corpus (7) |
| `MISSING-CLIENT` | **48** | The target needs a real client (V3) but live coverage is `api`-only (V2), or a declared client is not covered live |
| `PHYS-OWNER-GATE` | **33** | Software side satisfied; the binding gate is physical HIL measurement (12 of them are the `HIL-09(C)`-capped rows) |
| `REPRODUCED-DEFECT` | **1** | `F-SEC-014` / `VAL-15`: an open reproduced defect whose corrective package has no dispatched replacement |

The single V5 field-target row (`F-REL-018`) is counted inside
`MISSING-ASSERT` and is labelled `+FIELD` in the table below, because its
software gap must be closed before the owner field gate.

Rows whose software gap must be closed **before** the physical/field gate are
labelled `… +PHYS` / `… +FIELD` in the table below (89 rows) and their first
action is the software action, not the owner action.

### 4.2 Same dispositions split by target class

| Target class | Rows | `PRESERVE` | `RERUN-FRESH` | `MISSING-ASSERT` | `MISSING-CLIENT` | owner gate | defect |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Software targets (≤ V3) | 147 | 40 | 20 | 60 | 26 | 0 | 1 |
| Physical (V4) / field (V5) | 121 | 0 | 20 (+PHYS) | 45 (+PHYS) + 1 (+FIELD) | 22 (+PHYS) | 33 | 0 |
| **Total** | **268** | **40** | **40** | **106** | **48** | **33** | **1** |

Within the 89 below-target software targets: 46 missing assertion, 26 missing
client, 16 rerun freshness, 1 reproduced defect. Within the 58 at-target
software targets: 40 preserve, 14 missing assertion and 4 rerun freshness.
Of those 14 missing-assertion rows, 12 have **no evidence record at all** (the
at-target number comes from the recorded baseline, not from fresh proof) and 2
have fresh evidence but an unasserted contract effect (`F-API-037`,
`F-API-040`).

---

## 5. Disposition vocabulary and the rules behind it

The vocabulary is the one fixed by the dispatch:

| Disposition | Rule applied (all inputs from §2) |
| --- | --- |
| `PRESERVE` | evidence freshness `fresh` **and** ledger level ≥ software ceiling **and** no unasserted contract effect **and** no open reproduced defect |
| `RERUN-FRESH` | freshness `stale` or `none`, a live scenario/client covers the feature, and no unasserted contract effect and no missing client |
| `MISSING-ASSERT` | no live scenario declares the feature, **or** the contract's WebSocket effect is asserted nowhere in the live corpus |
| `MISSING-CLIENT` | the contract target needs V3 but live coverage is `api`-only, or a manifest-declared client is not covered live |
| `REPRODUCED-DEFECT` | an open reproduced finding with no dispatched corrective replacement (`VAL-15`) |
| `PHYS-OWNER-GATE` / `FIELD-OWNER-GATE` | V4/V5 target whose software side is satisfied; the binding gate is owner measurement/sign-off |

Precedence, in order: reproduced defect → capped-by-open-critical-finding →
missing assertion → missing client → freshness → at-target. The `+PHYS` /
`+FIELD` suffix records that the physical/field owner gate still follows the
software action. The *next exact acceptance action* column is the composed
list of the outstanding steps, in order, and names the owning unit and phase.

The 12 rows shown as `V1*` in the ledger (`F-MTX-007` … `F-MTX-020`) are
capped by the open critical finding `HIL-09(C)`; the cap is a
**finding-closure gate**, not an evidence shortfall, so those rows are
`PHYS-OWNER-GATE` with "close the open critical finding by physical
measurement" as their action.

---

## 6. Top actual blockers (P1), crosswalked

These are the clear P1 blockers named in the dispatch, crosswalked against the
inventory. **None of them was executed, re-run or dispositioned by this
report**; the pins' own dispatch state at the base is `not_launched`.

| # | Blocker | Pin (P1) | Base rule | Inventory rows it governs | What this inventory adds | What stays open |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Retained API candidate: full boundary `938ae303` → `386872316` → `ee3f2e7f` → report `caaa4faa` | `QUAL-ANTHROPIC-CORE-01` | `caaa4faabe9ede1e3aed37d2269efd4a4d691e04` | the 64 P1-owned feature rows (§8) | the inventory states, per row, the exact assertion each P1 unit still owes, so the candidate evaluation can be judged against named rows rather than prose | independent Anthropic evaluation + OpenAI judgement + coordinator pass/hold/fail |
| 2 | `RV-API034` — review of the unreviewed OpenAI F-API-034 chain | `RV-API034` | `caaa4faa…` | `F-API-034` (V3, `SW-API-CLIENT-02`) | **independent confirmation at the current base**: no expectation in the live 1 507-scenario corpus asserts `switch_all_failed` (0 hits), while the source *does* emit it (`src/rest_api/control.py:129,153`) — so the gap is the declarative assertion, not the emitter | source/artifact review; the assertion is new work for `SW-API-CLIENT-02` |
| 3 | `RV-WS040` — WS source `5331d547` vs `938ae303` at submitted `1fbfee11` | `RV-WS040` | `1fbfee112cc503ffa273c19dc565092d01fe2d6b` | WS-contract rows (`F-API-032`, `F-API-040`, `F-REL-012`) and the browser-V3 rows the accepted freshness delta lists as needing refresh (`F-KIO-002/003`, `F-UI-002/004/005`) | `F-API-040`'s contract effect `output_name_change` is emitted by the source (`src/rest_api/events.py:465`) but is asserted **nowhere** in the corpus; `F-API-032`'s `error` effect is asserted only under other feature ids. This report does **not** assert which feature rows the `1fbfee11` browser records cover — that attribution belongs to `RV-WS040` / `EV-CI-ATTRIBUTION` | the pin's own source/artefact review; candidate freshness of the browser V3 records |
| 4 | `RV-PRIVACY-CHAIN` — full retained VAL-15 C1/C2/C3 chain (`11f305b1` / `615d3c84` / `2d02004d`) | `RV-PRIVACY-CHAIN` | `2d02004d3108953a302e1a49aab9a5f24e944136` | **`F-SEC-014`** — the only row whose disposition is `REPRODUCED-DEFECT` | the inventory states the row's exact state at the base: target V3, level V1, **no evidence record**, no live scenario declares it, and the defect is open in `findings_pending.yaml` with `SW-SEC-DATA-02-C1` undispatched | qualified different-family privacy/code review; no admission, no closure |
| 5 | `FSEC007` candidate-specific freshness disposition | `EV-API034-SECURITY-REFRESH` | `caaa4faa…` | `F-SEC-007` | on the **canonical** ledger `F-SEC-007` is `V3/V3/fresh` at target with 10 live scenarios across `api`+`browser` → `PRESERVE`. The historical "F-SEC-007 dropped below its recorded level: level V2 < recorded V3" gate is a **stale historical gate at an older source**, not the current row. The *candidate-specific* freshness question (new actual browser proof on the API-C2 branch, never borrowed non-ancestor WS proof) is owned by this pin and is **not** answered here | the candidate-specific disposition; no borrow of non-ancestor proof |
| 6 | Privacy / Flic / CI admission | `EV-PRIVACY-ADMISSION`, `EV-FLIC-ADMISSION`, `EV-CI-ATTRIBUTION` | accepted-integration-after-dependencies | `F-FLIC-001/002/008` (Flic V3 rows), `F-API-034` + `F-SEC-014` (privacy), the 56 CI records | the inventory keeps **actual fresh accepted evidence distinct from inherited private unreviewed evidence**: the Flic rows are `RERUN-FRESH`/preserve on the canonical ledger while the private Flic attempt stays on privacy + artifact-admission HOLD (8 unmasked fixture-password fields, unchanged bytes), and the 56 CI records at the non-ancestral source `bdcf06dc` are **not** ordinary fresh evidence (4 Flic units absent because the CI command never requested the `flic` client) | admission decisions and privacy clearance are coordinator-owned and remain open |
| 7 | Irrecoverable old-original preservation gaps | `EV-PRESERVATION-GAPS` | accepted-integration-after-dependencies | — (evidence-level, not feature-level) | preserved unchanged from the accepted slices: lost original API-C1 managed-failure artefacts and the overwritten original freshness scratch extracts; whole-workspace archives absent for the controller author, the header reviewer and the controller reviewer, and one missing recovery-checkout proof | coordinator disposition of the losses; no reconstruction is claimed |

### 6.1 The five WebSocket effects that no declarative assertion covers

Discovered by static inspection of the live corpus at the base (not a
reproduction of any defect):

| Feature | Contract WebSocket effect | Emitter at the base | Asserted anywhere in the corpus? |
| --- | --- | --- | --- |
| `F-API-034` (V3, `SW-API-CLIENT-02`) | `switch_all_failed` | `src/rest_api/control.py:129,153` | **no** (corroborates the accepted `FRESHNESS_DELTA` §6 gap) |
| `F-MTX-002` (V4, `SW-PROTOCOL-PREP-01`) | `switch_all_failed` | same emitter | **no** (same gap under the matrix feature id) |
| `F-API-035` (V3, `SW-API-CLIENT-02`) | `preset_recall_failed` | `src/rest_api/control.py:78` | **no** |
| `F-MTX-003` (V4, `SW-PROTOCOL-PREP-01`) | `preset_recall_failed` | same emitter | **no** |
| `F-API-037` (V2, `SW-API-WRITE-03`) | `device_settings_full` | `src/rest_api/device_settings.py:622` | **no** |
| `F-API-040` (V3, `SW-API-READ-03`) | `output_name_change` | `src/rest_api/events.py:465` | **no** |
| `F-MTX-024` (V4, `SW-PROTOCOL-PREP-04`) | `output_name_change` | same emitter | **no** |

Four further features have a WebSocket contract and **no scenario at all**:
`F-API-039` (`status`), `F-API-042` (`ping`/`pong`), `F-DOM-032`
(`device_settings`, `device_settings_full`), `F-REL-014` (`all broadcasts`).

Five features have their WebSocket effect asserted only under a **different**
feature id (attribution gap, not a missing assertion): `F-API-032`
(`error`), `F-MTX-001` (`switch_failed`), `F-CEC-006` (`cec_command`),
`F-REL-012` (`signal_change`), `F-SEC-001` (`/ws`).

This is a **declarative-assertion inventory gap**, not a reproduced functional
defect: in every case above the emitter exists in the current source.

---

## 7. The 268-row disposition table

Reading the columns: `Tgt` is the contract target; `Lvl/Rec/Ev` is the ledger
level (with `*` = capped), recorded baseline and evidence freshness; `Unit
(phase)` is the owning bounded unit and its execution phase; `Coverage` is the
live clients and scenarios found in the current source; `Effect assertion` is
the contract's WebSocket-effect coverage; `Source ref` is the first `covers`
path group of the covering scenarios (the full set is in `author/inventory.json`);
`Disposition` is the canonical proof disposition; the last column is the next
exact acceptance action.

| ID | Feature | Tgt | Lvl/Rec/Ev | Unit (phase) | Coverage: clients / scenarios | Effect assertion | Source ref | Disposition | Next exact acceptance action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F-API-001 | GET /api/health, /api/openapi.json, /api/docs (liveness, matrix connection, runtime metrics, integration lifecycle, OpenAPI 3.1 & Swagger UI) | V3 | V2/V2/none | SW-API-CLIENT-01 (P1) | api / contracts.api_docs, contracts.health (+1) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT | first run of contracts.openapi_spec/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-01, P1] |
| F-API-002 | API info and root (GET /, /api, /api/info) | V2 | V2/V2/fresh | SW-API-READ-01 (P1) | api / contracts.api_info, contracts.api_root (+1) | no-ws effect | `docs/API_REFERENCE.md (+32)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-READ-01, P1] |
| F-API-003 | GET /api/status | V3 | V2/V2/none | SW-API-CLIENT-01 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-API-CLIENT-01, P1] |
| F-API-004 | Detailed status (GET /api/status/full\|inputs\|outputs\|cables\|edid\|ext-audio\|system\|device\|cec) | V3 | V1/V1/stale | SW-API-CLIENT-01 (P1) | api / cec_controls.status_mixed, cec_controls.status_off (+4) | no-ws effect | `docs/api/websocket.schema.json (+20)` | MISSING-CLIENT | re-run cec_controls.status_off/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-01, P1] |
| F-API-005 | POST /api/switch (one output or all) | V3 | V2/V2/stale | SW-API-CLIENT-01 (P1) | api / routing.route_all, routing.switch_one | no-ws effect | `docs/api/websocket.schema.json (+26)` | MISSING-CLIENT | re-run routing.switch_one/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-01, P1] |
| F-API-006 | POST /api/output/{output}/source and input cycling | V3 | V1/V1/none | SW-API-CLIENT-01 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-API-CLIENT-01, P1] |
| F-API-007 | POST /api/preset/{preset} (recall) | V3 | V2/V2/stale | SW-API-CLIENT-01 (P1) | api / presets.recall | no-ws effect | `docs/api/websocket.schema.json (+24)` | MISSING-CLIENT | re-run presets.recall/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-01, P1] |
| F-API-008 | POST /api/preset/{preset}/save | V2 | V1/V1/stale | SW-API-WRITE-01 (P1) | api / preset_read.saved_current_1, preset_read.saved_current_2 (+15) | no-ws effect | `docs/api/websocket.schema.json (+20)` | RERUN-FRESH | re-run preset_read.saved_current_1/api at current source to refresh [unit=SW-API-WRITE-01, P1] |
| F-API-009 | POST /api/power/on\|off | V3 | V1/V1/stale | SW-API-CLIENT-02 (P1) | api / power.standby, power.wake | no-ws effect | `docs/api/websocket.schema.json (+17)` | MISSING-CLIENT | re-run power.standby/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-02, P1] |
| F-API-010 | Output setting routes (mute, enable, hdcp, hdr, scaler, arc) | V2 | V1/V1/none | SW-API-WRITE-01 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-API-WRITE-01, P1] |
| F-API-011 | EDID routes | V2 | V1/V1/none | SW-API-WRITE-01 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-API-WRITE-01, P1] |
| F-API-012 | External audio routes | V2 | V1/V1/none | SW-API-WRITE-01 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-API-WRITE-01, P1] |
| F-API-013 | System setting routes (beep, panel lock, LCD, reboot) | V2 | V1/V1/stale | SW-API-WRITE-01 (P1) | api,browser / reboot.direct, reboot.enabled_shortcut (+1) | no-ws effect | `docs/api/websocket.schema.json (+27)` | RERUN-FRESH | re-run reboot.direct/api at current source to refresh [unit=SW-API-WRITE-01, P1] |
| F-API-014 | System info and storage routes | V2 | V2/V2/fresh | SW-API-READ-02 (P1) | api / contracts.storage, contracts.system_info | no-ws effect | `docs/api/websocket.schema.json (+17)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-READ-02, P1] |
| F-API-015 | CEC command routes | V3 | V2/V1/fresh | SW-API-CLIENT-02 (P1) | api / cec.input_power_on, cec.output_power_on (+436) | no-ws effect | `docs/api/websocket.schema.json (+21)` | MISSING-CLIENT | add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-02, P1] |
| F-API-016 | CEC catalogue, capability and enable routes | V2 | V2/V2/fresh | SW-API-READ-02 (P1) | api / cec_caps.all_pattern_0, cec_caps.all_pattern_1 (+130) | no-ws effect | `docs/api/websocket.schema.json (+21)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-READ-02, P1] |
| F-API-017 | Device settings routes (icons, display names, preset names, favourite/dashboard presets) | V2 | V1/V1/stale | SW-API-WRITE-01 (P1) | api / contracts.device_settings, contracts.input_settings (+7) | no-ws effect | `docs/api/websocket.schema.json (+19)` | RERUN-FRESH | re-run contracts.device_settings/api at current source to refresh [unit=SW-API-WRITE-01, P1] |
| F-API-018 | Name routes (POST /api/input\|output/{n}/name) | V2 | V2/V2/fresh | SW-API-WRITE-02 (P1) | api / writes.input_name, writes.input_name_blank (+2) | no-ws effect | `docs/api/websocket.schema.json (+20)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-WRITE-02, P1] |
| F-API-019 | Profile routes | V2 | V1/V1/stale | SW-API-WRITE-02 (P1) | api / profile_crud.clear_assignments, profile_crud.create_assignments (+104) | no-ws effect | `docs/api/websocket.schema.json (+31)` | RERUN-FRESH | re-run profile_crud.create_defaults/api at current source to refresh [unit=SW-API-WRITE-02, P1] |
| F-API-020 | Scene v1 alias routes (/api/scene*, /api/scenes) | V2 | V2/V1/fresh | SW-API-WRITE-02 (P1) | api / domain_manage.legacy_list, domain_manage.legacy_recall (+66) | no-ws effect | `docs/api/websocket.schema.json (+31)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-WRITE-02, P1] |
| F-API-021 | Scene v2 routes (/api/v2/scenes*) | V2 | V2/V2/stale | SW-API-WRITE-02 (P1) | api / domain_manage.scene_a_list, domain_manage.scene_b_create_reject_body_type (+42) | no-ws effect | `docs/api/websocket.schema.json (+26)` | RERUN-FRESH | re-run domain_manage.scene_a_list/api at current source to refresh [unit=SW-API-WRITE-02, P1] |
| F-API-022 | Response envelope and input validation (4xx before anything reaches the matrix) | V2 | V1/V1/stale | SW-API-WRITE-02 (P1) | api / failures.bad_input | no-ws effect | `docs/api/websocket.schema.json (+16)` | RERUN-FRESH | re-run failures.bad_input/api at current source to refresh [unit=SW-API-WRITE-02, P1] |
| F-API-023 | Macro routes | V2 | V1/V1/stale | SW-API-WRITE-02 (P1) | api / domain_manage.macro_all_commands, domain_manage.macro_create (+69) | no-ws effect | `docs/api/websocket.schema.json (+26)` | RERUN-FRESH | re-run domain_manage.macro_create/api at current source to refresh [unit=SW-API-WRITE-02, P1] |
| F-API-024 | Shortcut routes (/api/system-shortcuts* and the /api/shortcuts* aliases) | V2 | V1/V1/stale | SW-API-WRITE-03 (P1) | api / contracts.shortcut_alias, contracts.shortcut_dashboard (+9) | no-ws effect | `docs/api/websocket.schema.json (+19)` | RERUN-FRESH | re-run contracts.shortcut_favorites/api at current source to refresh [unit=SW-API-WRITE-03, P1] |
| F-API-025 | Dashboard layout routes | V2 | V1/V1/stale | SW-API-WRITE-03 (P1) | api / dashboard.widget_card_refused, dashboard.widget_cards_dropped | no-ws effect | `docs/api/websocket.schema.json (+18)` | RERUN-FRESH | re-run dashboard.widget_cards_dropped/api at current source to refresh [unit=SW-API-WRITE-03, P1] |
| F-API-026 | Themes and UI preference routes | V2 | V2/V2/fresh | SW-API-READ-02 (P1) | api / contracts.themes, contracts.ui_preferences (+3) | no-ws effect | `docs/api/websocket.schema.json (+21)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-READ-02, P1] |
| F-API-027 | Settings routes (matrix host, test connection) | V2 | V1/V1/stale | SW-API-WRITE-03 (P1) | api / contracts.settings, writes.connection_test | no-ws effect | `docs/api/websocket.schema.json (+17)` | RERUN-FRESH | re-run contracts.settings/api at current source to refresh [unit=SW-API-WRITE-03, P1] |
| F-API-028 | Flic integration routes | V2 | V2/V2/fresh | SW-API-READ-02 (P1) | api / contracts.flic_buttons, writes.flic_register | no-ws effect | `docs/api/websocket.schema.json (+19)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-READ-02, P1] |
| F-API-029 | Web UI, kiosk and static asset routes | V3 | V3/V3/none | SW-API-CLIENT-02 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-API-CLIENT-02, P1] |
| F-API-030 | Rate limiting (60 requests / 10 s per client) | V2 | V1/V1/none | SW-API-WRITE-03 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-API-WRITE-03, P1] |
| F-API-031 | CORS headers | V2 | V2/V2/fresh | SW-API-READ-04 (P1) | api / sw_api_read_04.configured_allowed, sw_api_read_04.configured_allowed_preflight (+11) | no-ws effect | `docs/api/websocket.schema.json (+24)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-READ-04, P1] |
| F-API-032 | WebSocket /ws: welcome, status snapshot, get_status, matrix link, errors | V2 | V3/V2/fresh | SW-API-READ-04 (P1) | api,browser / live.matrix_offline, reboot.direct (+2) | ws asserted under other feature: error | `docs/api/websocket.schema.json (+29)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-READ-04, P1] |
| F-API-033 | WS event routing_change (one per changed output, whoever routed) / switch_failed | V3 | V2/V2/fresh | SW-API-CLIENT-02 (P1) | api / failures.unreachable_switch, routing.switch_one | ws asserted (bound) | `docs/api/websocket.schema.json (+23)` | MISSING-CLIENT | add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-02, P1] |
| F-API-034 | Route to all: routing_change per output that changed / switch_all_failed | V3 | V2/V2/stale | SW-API-CLIENT-02 (P1) | api / routing.route_all | **NOWHERE: switch_all_failed** | `docs/api/websocket.schema.json (+25)` | MISSING-ASSERT | re-run routing.route_all/api at current source to refresh; author a declarative scenario asserting switch_all_failed + different-family review; add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-02, P1] |
| F-API-035 | WS event preset_recall / preset_recall_failed | V3 | V2/V2/stale | SW-API-CLIENT-02 (P1) | api / presets.recall | **NOWHERE: preset_recall_failed** | `docs/api/websocket.schema.json (+24)` | MISSING-ASSERT | re-run presets.recall/api at current source to refresh; author a declarative scenario asserting preset_recall_failed + different-family review; add/execute a real-client end-to-end assertion [unit=SW-API-CLIENT-02, P1] |
| F-API-036 | WS event audio_mute | V2 | V2/V2/fresh | SW-API-WRITE-03 (P1) | api / outputs.audio_mute, outputs.audio_mute_rejected | ws asserted (bound) | `docs/api/websocket.schema.json (+16)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-WRITE-03, P1] |
| F-API-037 | WS events device_settings / device_settings_full | V2 | V2/V2/fresh | SW-API-WRITE-03 (P1) | api / presets.rename | **NOWHERE: device_settings_full** | `docs/api/websocket.schema.json (+25)` | MISSING-ASSERT | author a declarative scenario asserting device_settings_full + different-family review [unit=SW-API-WRITE-03, P1] |
| F-API-038 | WS event cec_command | V2 | V2/V2/fresh | SW-API-WRITE-04 (P1) | api / cec.output_power_on | ws asserted (bound) | `docs/api/websocket.schema.json (+17)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-WRITE-04, P1] |
| F-API-039 | WS status snapshot (after connect, after a first reading, get_status) | V2 | V2/V2/none | SW-API-READ-03 (P1) | none / - | no scenario; ws: status | `-` | MISSING-ASSERT | author a declarative scenario asserting status + different-family review; run it to produce the first evidence record [unit=SW-API-READ-03, P1] |
| F-API-040 | WS live matrix events from the hub's own poller (routing, power, signal, display, cable, mute, names) | V2 | V3/V2/fresh | SW-API-READ-03 (P1) | api,browser / live.display_unplugged, live.front_panel_route (+3) | **NOWHERE: output_name_change** | `docs/api/websocket.schema.json (+25)` | MISSING-ASSERT | author a declarative scenario asserting output_name_change + different-family review [unit=SW-API-READ-03, P1] |
| F-API-041 | WS event scene_execution_error | V2 | V2/V2/fresh | SW-API-WRITE-04 (P1) | api / scenes.partial_failure | ws asserted (bound) | `docs/api/websocket.schema.json (+34)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-API-WRITE-04, P1] |
| F-API-042 | WS heartbeat (ping / pong) | V2 | V2/V2/none | SW-API-READ-03 (P1) | none / - | no scenario; ws: ping,pong | `-` | MISSING-ASSERT | author a declarative scenario asserting ping, pong + different-family review; run it to produce the first evidence record [unit=SW-API-READ-03, P1] |
| F-CEC-001 | Power a source on / off over CEC | V4 | V1/V1/stale | SW-PROTOCOL-PREP-06 (P3) | api / cec.input_power_on, cec_controls.input_1_power_off (+15) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | re-run cec.input_power_on/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-06, P3] |
| F-CEC-002 | Navigate a source's menus over CEC (up/down/left/right/select/menu/back) | V4 | V1/V1/stale | SW-PROTOCOL-PREP-06 (P3) | api / cec_controls.input_1_back, cec_controls.input_1_down (+54) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | re-run cec_controls.input_1_up/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-06, P3] |
| F-CEC-003 | Control playback on a source over CEC | V4 | V1/V1/stale | SW-PROTOCOL-PREP-06 (P3) | api / cec_controls.input_1_fast_forward, cec_controls.input_1_next (+54) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | re-run cec_controls.input_1_previous/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-06, P3] |
| F-CEC-004 | Source volume / mute over CEC | V4 | V1/V1/stale | SW-PROTOCOL-PREP-06 (P3) | api / cec_controls.input_1_mute, cec_controls.input_1_volume_down (+22) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | re-run cec_controls.input_1_mute/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-06, P3] |
| F-CEC-005 | Turn a display (TV) on / off over CEC | V4 | V3/V3/fresh | SW-PROTOCOL-PREP-06 (P3) | api,ha,uc / cec.output_power_on, cec_controls.output_1_power_off (+17) | ws asserted (bound) | `custom_components/hdmi_matrix (+28)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-06, P3] |
| F-CEC-006 | Display / soundbar volume and mute over CEC | V4 | V1/V1/stale | SW-PROTOCOL-PREP-07 (P3) | api / cec.output_volume_up, cec_controls.output_1_mute (+23) | ws asserted under other feature: cec_command | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | re-run cec.output_volume_up/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-07, P3] |
| F-CEC-007 | Enable CEC on the target port automatically before a command | V4 | V1/V1/stale | SW-PROTOCOL-PREP-07 (P3) | api / cec.input_power_on, cec_controls.input_1_already_enabled (+415) | no-ws effect | `docs/api/websocket.schema.json (+21)` | MISSING-CLIENT +PHYS | re-run cec.input_power_on/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-07, P3] |
| F-CEC-008 | Enable / disable CEC per port | V4 | V2/V1/fresh | SW-PROTOCOL-PREP-07 (P3) | api / cec_controls.input_1_enable_0, cec_controls.input_1_enable_1 (+38) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-07, P3] |
| F-CEC-009 | Read which ports have CEC enabled | V4 | V1/V1/stale | SW-PROTOCOL-PREP-07 (P3) | api / cec_controls.status_mixed, cec_controls.status_off (+2) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | re-run cec_controls.status_off/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-07, P3] |
| F-CEC-010 | Send CEC over Telnet (OREI_USE_TELNET_CEC) | V4 | V1/V1/stale | SW-PROTOCOL-PREP-07 (P3) | api / cec_telnet.input_1_back, cec_telnet.input_1_down (+204) | no-ws effect | `docs/api/websocket.schema.json (+20)` | MISSING-CLIENT +PHYS | re-run cec_telnet.input_1_power_on/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-07, P3] |
| F-CEC-011 | List CEC commands and per-port capabilities (incl. audio-only outputs) | V4 | V2/V1/fresh | SW-PROTOCOL-PREP-07 (P3) | api / cec_caps.all_pattern_0, cec_caps.all_pattern_1 (+86) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-07, P3] |
| F-DOM-001 | Create, edit and delete profiles | V3 | V1/V1/stale | SW-DOM-PROFILE-01 (P1) | api / profile_crud.clear_assignments, profile_crud.create_assignments (+46) | no-ws effect | `docs/api/websocket.schema.json (+31)` | MISSING-CLIENT | re-run profile_crud.create_defaults/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-PROFILE-01, P1] |
| F-DOM-002 | Recall a profile: its routing is applied | V4 | V3/V3/fresh | SW-DOM-HIL-PREP-01 (P3) | api,browser / profile_state.alias_recall, profiles.recall_disabled_output (+2) | no-ws effect | `docs/api/websocket.schema.json (+41)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-DOM-HIL-PREP-01, P3] |
| F-DOM-003 | Recall a profile: its output settings (mute, HDR, HDCP, enable) are applied | V4 | V3/V3/fresh | SW-DOM-HIL-PREP-01 (P3) | api,browser / profiles.recall_disabled_output, profiles.recall_leaves_unset_scaler_arc (+2) | no-ws effect | `docs/api/websocket.schema.json (+30)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-DOM-HIL-PREP-01, P3] |
| F-DOM-004 | Recall a profile: its power-on macro runs | V4 | V3/V3/fresh | SW-DOM-HIL-PREP-01 (P3) | api,browser / profiles.recall_power_macro | no-ws effect | `docs/api/websocket.schema.json (+19)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-DOM-HIL-PREP-01, P3] |
| F-DOM-005 | Protect a profile with a passcode (per-item PIN) | V3 | V3/V1/fresh | SW-DOM-PROFILE-01 (P1) | api,browser / kiosk.profile_with_passcode, kiosk.profile_wrong_passcode (+3) | no-ws effect | `docs/api/websocket.schema.json (+32)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-PROFILE-01, P1] |
| F-DOM-006 | Favourite, pin, reorder profiles and show them on the dashboard | V3 | V1/V1/stale | SW-DOM-PROFILE-01 (P1) | api / profile_crud.dashboard_missing_field, profile_crud.dashboard_post_false (+18) | no-ws effect | `docs/api/websocket.schema.json (+21)` | MISSING-CLIENT | re-run profile_crud.favorite_post_false/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-PROFILE-01, P1] |
| F-DOM-007 | Per-profile CEC targets (nav/playback/volume/power) and auto-resolve | V3 | V1/V1/stale | SW-DOM-PROFILE-01 (P1) | api / profile_state.cec_profile_get_default, profile_state.cec_profile_get_missing (+81) | no-ws effect | `docs/api/websocket.schema.json (+30)` | MISSING-CLIENT | re-run profile_state.cec_profile_post_manual/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-PROFILE-01, P1] |
| F-DOM-008 | Profile execution log | V3 | V0/V0/stale | SW-DOM-PROFILE-01 (P1) | api / profile_state.history_empty, profile_state.history_failure (+4) | no-ws effect | `docs/api/websocket.schema.json (+30)` | MISSING-CLIENT | re-run profile_state.history_empty/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-PROFILE-01, P1] |
| F-DOM-009 | Save the current routing as a new profile | V3 | V1/V1/stale | SW-DOM-PROFILE-01 (P1) | api / profile_state.capture_defaults, profile_state.capture_output_read_failure (+10) | no-ws effect | `docs/api/websocket.schema.json (+30)` | MISSING-CLIENT | re-run profile_state.capture_pattern_0/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-PROFILE-01, P1] |
| F-DOM-010 | Create, edit and delete scenes (sequences of steps) | V3 | V2/V2/stale | SW-DOM-SCENE-01 (P2) | api / domain_manage.scene_a_list, domain_manage.scene_b_create_reject_body_type (+44) | no-ws effect | `docs/api/websocket.schema.json (+26)` | MISSING-CLIENT | re-run domain_manage.scene_a_list/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-SCENE-01, P2] |
| F-DOM-011 | Run a scene: profile steps | V4 | V3/V3/fresh | SW-DOM-HIL-PREP-01 (P3) | api,browser / scenes.disabled_output_state, scenes.partial_failure (+4) | ws asserted (bound) | `docs/api/websocket.schema.json (+35)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-DOM-HIL-PREP-01, P3] |
| F-DOM-012 | Run a scene: macro steps | V4 | V3/V3/fresh | SW-DOM-HIL-PREP-01 (P3) | api,browser / scenes.macro_continues_after_refusal, scenes.run_profile_macro_preset (+2) | no-ws effect | `docs/api/websocket.schema.json (+34)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-DOM-HIL-PREP-01, P3] |
| F-DOM-013 | Run a scene: wait and shortcut steps | V3 | V3/V3/fresh | SW-DOM-SCENE-01 (P2) | api,browser / scenes.wait_between_actions, scenes.wait_edit | no-ws effect | `docs/api/websocket.schema.json (+35)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SCENE-01, P2] |
| F-DOM-014 | Scene overrides (per-run changes to a profile step) | V3 | V3/V3/fresh | SW-DOM-SCENE-01 (P2) | api,browser / scenes.enabled_override, scenes.override_leaves_scaler_arc (+2) | no-ws effect | `docs/api/websocket.schema.json (+34)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SCENE-01, P2] |
| F-DOM-015 | Protect a scene with a passcode | V3 | V3/V1/fresh | SW-DOM-SCENE-01 (P2) | api,browser / scenes.run_needs_passcode, scenes.run_protected | no-ws effect | `docs/api/websocket.schema.json (+35)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SCENE-01, P2] |
| F-DOM-016 | Validate a scene and detect conflicting steps | V3 | V3/V3/fresh | SW-DOM-SCENE-01 (P2) | api,browser / scenes.conflicts_scaler_arc, scenes.conflicts_visible | no-ws effect | `docs/api/websocket.schema.json (+35)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SCENE-01, P2] |
| F-DOM-017 | Scene execution history | V3 | V3/V3/fresh | SW-DOM-SCENE-01 (P2) | api,browser / scenes.partial_failure | no-ws effect | `docs/api/websocket.schema.json (+34)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SCENE-01, P2] |
| F-DOM-018 | Legacy 'scenes' (v1) as aliases of profiles | V2 | V1/V1/stale | SW-DOM-PROFILE-02 (P1) | api / domain_manage.legacy_list, domain_manage.legacy_recall | no-ws effect | `docs/api/websocket.schema.json (+31)` | RERUN-FRESH | re-run domain_manage.legacy_list/api at current source to refresh [unit=SW-DOM-PROFILE-02, P1] |
| F-DOM-019 | Create, edit, delete and validate CEC macros | V3 | V1/V1/stale | SW-DOM-MACRO-01 (P2) | api / domain_manage.macro_all_commands, domain_manage.macro_create (+60) | no-ws effect | `docs/api/websocket.schema.json (+26)` | MISSING-CLIENT | re-run domain_manage.macro_create/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-MACRO-01, P2] |
| F-DOM-020 | Run a CEC macro (steps, targets, delays) | V4 | V3/V3/fresh | SW-DOM-HIL-PREP-01 (P3) | api,browser / macros.run_rejected, macros.run_volume_up (+2) | no-ws effect | `docs/api/websocket.schema.json (+37)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-DOM-HIL-PREP-01, P3] |
| F-DOM-021 | Test / dry-run a macro | V3 | V1/V1/stale | SW-DOM-MACRO-01 (P2) | api / domain_manage.macro_dry_run, domain_manage.macro_dry_run_missing | no-ws effect | `docs/api/websocket.schema.json (+26)` | MISSING-CLIENT | re-run domain_manage.macro_dry_run/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-MACRO-01, P2] |
| F-DOM-022 | Favourite macros and show them on the dashboard | V3 | V1/V1/stale | SW-DOM-MACRO-01 (P2) | api / domain_manage.macro_dashboard_false, domain_manage.macro_dashboard_missing (+5) | no-ws effect | `docs/api/websocket.schema.json (+26)` | MISSING-CLIENT | re-run domain_manage.macro_favorite_true/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-MACRO-01, P2] |
| F-DOM-023 | Built-in shortcuts: route all to an output, one-to-one routing | V3 | V3/V2/fresh | SW-DOM-SHORTCUT-01 (P2) | api,browser / shortcuts.route_input_to_output, shortcuts.route_one_to_one (+1) | no-ws effect | `docs/api/websocket.schema.json (+25)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SHORTCUT-01, P2] |
| F-DOM-024 | Built-in shortcut: power everything off | V3 | V3/V2/fresh | SW-DOM-SHORTCUT-01 (P2) | api,browser / shortcuts.power_off_all | no-ws effect | `docs/api/websocket.schema.json (+25)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SHORTCUT-01, P2] |
| F-DOM-025 | Built-in shortcuts: mute / unmute all outputs | V3 | V3/V2/fresh | SW-DOM-SHORTCUT-01 (P2) | api,browser / shortcuts.mute_all, shortcuts.mute_rejected (+1) | no-ws effect | `docs/api/websocket.schema.json (+25)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SHORTCUT-01, P2] |
| F-DOM-026 | Built-in shortcuts: recall preset 1-8 | V3 | V2/V2/stale | SW-DOM-SHORTCUT-01 (P2) | api,browser / shortcuts.preset_recall | no-ws effect | `docs/api/websocket.schema.json (+26)` | RERUN-FRESH | re-run shortcuts.preset_recall/api at current source to refresh [unit=SW-DOM-SHORTCUT-01, P2] |
| F-DOM-027 | Built-in shortcuts: beep, panel lock, reboot | V3 | V3/V2/fresh | SW-DOM-SHORTCUT-01 (P2) | api,browser / reboot.enabled_shortcut, reboot.legacy_shortcut (+7) | no-ws effect | `docs/api/websocket.schema.json (+29)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SHORTCUT-01, P2] |
| F-DOM-028 | Built-in shortcuts: LCD timeout | V3 | V3/V2/fresh | SW-DOM-SHORTCUT-01 (P2) | api,browser / shortcuts.lcd_15s, shortcuts.lcd_30s (+4) | no-ws effect | `docs/api/websocket.schema.json (+25)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-DOM-SHORTCUT-01, P2] |
| F-DOM-029 | Create, rename, reorder and delete user shortcuts | V3 | V1/V1/none | SW-DOM-SHORTCUT-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-DOM-SHORTCUT-02, P2] |
| F-DOM-030 | Favourite shortcuts and show them on the dashboard | V3 | V1/V1/none | SW-DOM-SHORTCUT-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-DOM-SHORTCUT-02, P2] |
| F-DOM-031 | Dashboard layout (add, remove, reorder cards) | V3 | V1/V1/stale | SW-DOM-PRESENT-01 (P2) | api / dashboard.widget_card_refused, dashboard.widget_cards_dropped | no-ws effect | `docs/api/websocket.schema.json (+18)` | MISSING-CLIENT | re-run dashboard.widget_cards_dropped/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-PRESENT-01, P2] |
| F-DOM-032 | Input/output icons, colours and display names (device settings) | V3 | V0/V0/none | SW-DOM-PRESENT-01 (P2) | none / - | no scenario; ws: device_settings,device_settings_full | `-` | MISSING-ASSERT | author a declarative scenario asserting device_settings, device_settings_full + different-family review; run it to produce the first evidence record [unit=SW-DOM-PRESENT-01, P2] |
| F-DOM-033 | Favourite presets and choose which presets the dashboard shows | V3 | V1/V1/none | SW-DOM-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-DOM-PRESENT-01, P2] |
| F-DOM-034 | Save a custom routing mapping into a preset | V3 | V1/V1/stale | SW-DOM-PRESENT-01 (P2) | api / preset_read.saved_partial_1, preset_read.saved_partial_2 (+7) | no-ws effect | `docs/api/websocket.schema.json (+20)` | MISSING-CLIENT | re-run preset_read.saved_partial_1/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-DOM-PRESENT-01, P2] |
| F-DOM-035 | Theme presets and custom themes | V3 | V1/V1/none | SW-DOM-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-DOM-PRESENT-01, P2] |
| F-DOM-036 | UI preferences stored on the hub | V3 | V1/V1/none | SW-DOM-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-DOM-PRESENT-01, P2] |
| F-FLIC-001 | Button click recalls a preset | V3 | V1/V1/stale | SW-FLIC-01 (P2) | flic / flic.preset | no-ws effect | `docs/api/websocket.schema.json (+27)` | RERUN-FRESH | re-run flic.preset/flic at current source to refresh [unit=SW-FLIC-01, P2] |
| F-FLIC-002 | Button hold powers the matrix off / on | V3 | V1/V1/stale | SW-FLIC-01 (P2) | flic / flic.power_off, flic.power_on | no-ws effect | `docs/api/websocket.schema.json (+20)` | RERUN-FRESH | re-run flic.power_off/flic at current source to refresh [unit=SW-FLIC-01, P2] |
| F-FLIC-003 | Button powers a source on over CEC | V3 | V3/V1/fresh | SW-FLIC-01 (P2) | flic / flic.source_power | no-ws effect | `docs/api/websocket.schema.json (+20)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-FLIC-01, P2] |
| F-FLIC-004 | Flic Twist cycles an output through its inputs | V3 | V3/V1/fresh | SW-FLIC-01 (P2) | flic / flic.cycle_next, flic.sdk_twist_next (+1) | no-ws effect | `run.py (+6)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-FLIC-01, P2] |
| F-FLIC-005 | Flic Twist controls TV volume and mute over CEC | V3 | V3/V1/fresh | SW-FLIC-01 (P2) | flic / flic.cec_output_navigation_refused, flic.display_volume | no-ws effect | `docs/api/websocket.schema.json (+20)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-FLIC-01, P2] |
| F-FLIC-006 | Button recalls a profile or runs a macro | V3 | V3/V1/fresh | SW-FLIC-01 (P2) | flic / flic.manual_macro, flic.manual_macro_refused (+3) | no-ws effect | `docs/api/websocket.schema.json (+37)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-FLIC-01, P2] |
| F-FLIC-007 | Register Flic buttons with the hub (button registry) | V3 | V3/V0/fresh | SW-FLIC-02 (P2) | flic / flic.register | no-ws effect | `run.py (+8)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-FLIC-02, P2] |
| F-FLIC-008 | Button switches every output to input N (POST /api/switch with JSON input) | V3 | V0/V0/stale | SW-FLIC-02 (P2) | flic / flic.all_outputs | no-ws effect | `docs/api/websocket.schema.json (+28)` | RERUN-FRESH | re-run flic.all_outputs/flic at current source to refresh [unit=SW-FLIC-02, P2] |
| F-FLIC-009 | Flic Hub SDK JavaScript module templates | V3 | V3/V0/fresh | SW-FLIC-02 (P2) | flic / flic.sdk_double, flic.sdk_duo_left (+7) | no-ws effect | `docs/api/websocket.schema.json (+26)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-FLIC-02, P2] |
| F-FLIC-010 | Generate Flic request URLs in the web UI | V3 | V3/V1/fresh | SW-FLIC-02 (P2) | flic / flic.all_outputs, flic.cec_output_navigation_refused (+14) | no-ws effect | `docs/api/websocket.schema.json (+43)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-FLIC-02, P2] |
| F-HA-001 | Add the hub in Home Assistant (config flow) | V4 | V3/V3/stale | SW-HA-PREP-01 (P3) | ha / ha.config_flow | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.config_flow/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-01, P3] |
| F-HA-002 | Choose each output's source (select entities) | V4 | V3/V3/stale | SW-HA-PREP-01 (P3) | ha / ha.front_panel_route, ha.select_source | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.select_source/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-01, P3] |
| F-HA-003 | Matrix power switch | V4 | V3/V3/stale | SW-HA-PREP-01 (P3) | ha / ha.power_off, ha.power_on | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.power_off/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-01, P3] |
| F-HA-004 | Output audio mute switches | V4 | V3/V3/stale | SW-HA-PREP-01 (P3) | ha / ha.mute_switch | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.mute_switch/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-01, P3] |
| F-HA-005 | Output stream enable switches | V4 | V3/V3/stale | SW-HA-PREP-01 (P3) | ha / ha.stream_switch | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.stream_switch/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-01, P3] |
| F-HA-006 | Preset buttons | V4 | V3/V3/stale | SW-HA-PREP-01 (P3) | ha / ha.preset_button | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.preset_button/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-01, P3] |
| F-HA-007 | Reboot button | V4 | V3/V3/stale | SW-HA-PREP-02 (P3) | ha / ha.reboot_button | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.reboot_button/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-02, P3] |
| F-HA-008 | Input signal binary sensors | V4 | V3/V3/stale | SW-HA-PREP-02 (P3) | ha / ha.input_signal | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.input_signal/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-02, P3] |
| F-HA-009 | Output connected binary sensors | V4 | V3/V3/stale | SW-HA-PREP-02 (P3) | ha / ha.display_unplugged | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.display_unplugged/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-02, P3] |
| F-HA-010 | Service hdmi_matrix.recall_preset | V4 | V3/V3/stale | SW-HA-PREP-02 (P3) | ha / ha.service_recall_preset | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.service_recall_preset/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-02, P3] |
| F-HA-011 | Service hdmi_matrix.switch_input | V4 | V3/V3/stale | SW-HA-PREP-02 (P3) | ha / ha.service_switch_input | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.service_switch_input/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-02, P3] |
| F-HA-012 | Service hdmi_matrix.send_cec_command | V4 | V3/V3/stale | SW-HA-PREP-02 (P3) | ha / ha.service_cec_display, ha.service_cec_invalid (+1) | no-ws effect | `custom_components/hdmi_matrix (+22)` | RERUN-FRESH +PHYS | re-run ha.service_cec_display/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-02, P3] |
| F-HA-013 | Poll the hub; entities go unavailable when it is unreachable | V4 | V3/V3/stale | SW-HA-PREP-03 (P3) | ha / ha.display_unplugged, ha.front_panel_route (+3) | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.input_signal/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-03, P3] |
| F-HA-014 | Install through HACS (custom repository) | V4 | V1/V1/none | SW-HA-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-03, P3] |
| F-HA-015 | Device and entity naming in Home Assistant | V4 | V3/V3/stale | SW-HA-PREP-03 (P3) | ha / ha.config_flow | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.config_flow/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-03, P3] |
| F-HA-016 | Change the hub address of a configured matrix (reconfigure flow) | V4 | V3/V3/stale | SW-HA-PREP-03 (P3) | ha / ha.reconfigure | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.reconfigure/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-03, P3] |
| F-HA-017 | Polling interval option (options flow) | V4 | V3/V3/stale | SW-HA-PREP-03 (P3) | ha / ha.config_flow | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.config_flow/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-03, P3] |
| F-HA-018 | Services target one matrix (config entry or device) | V4 | V3/V3/stale | SW-HA-PREP-03 (P3) | ha / ha.service_recall_preset, ha.service_switch_input | no-ws effect | `custom_components/hdmi_matrix (+20)` | RERUN-FRESH +PHYS | re-run ha.service_recall_preset/ha at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-HA-PREP-03, P3] |
| F-KIO-001 | Open the kiosk; it shows the matrix connection | V3 | V3/V3/none | SW-KIOSK-STATE-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-STATE-01, P2] |
| F-KIO-002 | Route a source to one display with the routing wizard | V3 | V3/V3/stale | SW-KIOSK-CONTROL-01 (P2) | browser / kiosk.route_one_muted | no-ws effect | `docs/api/websocket.schema.json (+19)` | RERUN-FRESH | re-run kiosk.route_one_muted/browser at current source to refresh [unit=SW-KIOSK-CONTROL-01, P2] |
| F-KIO-003 | Route a source to every display from the kiosk | V3 | V3/V3/stale | SW-KIOSK-CONTROL-01 (P2) | browser / kiosk.route_all_apply | no-ws effect | `docs/api/websocket.schema.json (+19)` | RERUN-FRESH | re-run kiosk.route_all_apply/browser at current source to refresh [unit=SW-KIOSK-CONTROL-01, P2] |
| F-KIO-004 | Input and output status tiles | V3 | V3/V3/none | SW-KIOSK-STATE-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-STATE-01, P2] |
| F-KIO-005 | Recall a preset from the kiosk | V3 | V1/V1/none | SW-KIOSK-CONTROL-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-CONTROL-01, P2] |
| F-KIO-006 | Configure which presets the kiosk shows (edit mode) | V3 | V1/V1/none | SW-KIOSK-CONTROL-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-CONTROL-01, P2] |
| F-KIO-007 | Run shortcuts from the kiosk and map them to slots | V3 | V1/V1/none | SW-KIOSK-CONTROL-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-CONTROL-01, P2] |
| F-KIO-008 | Run profiles from the kiosk; create one with the profile wizard | V3 | V3/V1/fresh | SW-KIOSK-CONTROL-01 (P2) | browser / kiosk.profile_with_passcode, kiosk.profile_wrong_passcode | no-ws effect | `docs/api/websocket.schema.json (+21)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-KIOSK-CONTROL-01, P2] |
| F-KIO-009 | CEC remote in the kiosk | V3 | V1/V1/none | SW-KIOSK-CONTROL-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-CONTROL-02, P2] |
| F-KIO-010 | Kiosk live updates | V3 | V3/V3/fresh | SW-KIOSK-STATE-01 (P2) | browser / live.front_panel_route, live.input_signal | no-ws effect | `docs/api/websocket.schema.json (+23)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-KIOSK-STATE-01, P2] |
| F-KIO-011 | Kiosk disconnected state | V3 | V3/V3/fresh | SW-KIOSK-STATE-01 (P2) | browser / live.matrix_offline | no-ws effect | `docs/api/websocket.schema.json (+22)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-KIOSK-STATE-01, P2] |
| F-KIO-012 | Kiosk layout and pins persist | V3 | V1/V1/none | SW-KIOSK-STATE-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-STATE-01, P2] |
| F-KIO-013 | Kiosk follows the selected theme | V3 | V1/V1/none | SW-KIOSK-STATE-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-STATE-01, P2] |
| F-KIO-014 | Kiosk touch accessibility (targets, ARIA, contrast) | V3 | V1/V1/none | SW-KIOSK-STATE-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-KIOSK-STATE-02, P2] |
| F-MTX-001 | Route one input to one output | V4 | V3/V3/fresh | SW-PROTOCOL-PREP-01 (P3) | api,browser,ha,uc / ha.select_source, remote.select_source (+1) | ws asserted under other feature: switch_failed | `custom_components/hdmi_matrix (+30)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-01, P3] |
| F-MTX-002 | Route one input to every output | V4 | V3/V3/stale | SW-PROTOCOL-PREP-01 (P3) | api,browser / routing.route_all | **NOWHERE: switch_all_failed** | `docs/api/websocket.schema.json (+25)` | MISSING-ASSERT +PHYS | re-run routing.route_all/api at current source to refresh; author a declarative scenario asserting switch_all_failed + different-family review; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-01, P3] |
| F-MTX-003 | Recall a matrix preset (1-8) | V4 | V3/V3/fresh | SW-PROTOCOL-PREP-01 (P3) | api,browser,ha,uc / ha.preset_button, presets.recall (+1) | **NOWHERE: preset_recall_failed** | `custom_components/hdmi_matrix (+32)` | MISSING-ASSERT +PHYS | author a declarative scenario asserting preset_recall_failed + different-family review; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-01, P3] |
| F-MTX-004 | Save the current routing to a matrix preset | V4 | V1/V1/stale | SW-PROTOCOL-PREP-01 (P3) | api / matrix.preset_invalid_slot, matrix.preset_refused (+9) | no-ws effect | `docs/api/websocket.schema.json (+21)` | MISSING-CLIENT +PHYS | re-run matrix.save_current_preset/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-01, P3] |
| F-MTX-005 | Name presets in the web app (names shown by the API, UI, kiosk) | V4 | V3/V0/fresh | SW-PROTOCOL-PREP-01 (P3) | api,browser / presets.rename | ws asserted (bound) | `docs/api/websocket.schema.json (+25)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-01, P3] |
| F-MTX-006 | Matrix power on / standby | V4 | V3/V3/fresh | SW-PROTOCOL-PREP-01 (P3) | api,ha,uc / ha.power_off, ha.power_on (+3) | no-ws effect | `custom_components/hdmi_matrix (+24)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-01, P3] |
| F-MTX-007 | Mute / unmute the audio of an output | V4 | V1*/V1/fresh | SW-PROTOCOL-PREP-02 (P3) | api,ha / ha.mute_switch, outputs.audio_mute | ws asserted (bound) | `custom_components/hdmi_matrix (+20)` | PHYS-OWNER-GATE | close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-02, P3] |
| F-MTX-008 | Enable / disable an output's video stream | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-02 (P3) | api / settings.enable_0, settings.enable_1 (+3) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run settings.enable_0/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-02, P3] |
| F-MTX-009 | Set an output's HDCP mode | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-02 (P3) | api / settings.hdcp_1, settings.hdcp_2 (+9) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run settings.hdcp_1/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-02, P3] |
| F-MTX-010 | Set an output's HDR mode | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-02 (P3) | api / settings.hdr_1, settings.hdr_2 (+7) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run settings.hdr_1/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-02, P3] |
| F-MTX-011 | Set an output's scaler mode (incl. audio-only) | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-02 (P3) | api / settings.scaler_1, settings.scaler_2 (+9) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run settings.scaler_1/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding BE-15 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-02, P3] |
| F-MTX-012 | Enable / disable ARC on an output | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-02 (P3) | api / settings.arc_0, settings.arc_1 (+3) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run settings.arc_0/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-02, P3] |
| F-MTX-013 | Set an input's EDID | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-03 (P3) | api / settings.edid_input_0, settings.edid_input_9 (+8) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run settings.edid_mode_1/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-03, P3] |
| F-MTX-014 | Copy EDID from a connected display | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-03 (P3) | api / settings.edid_copy_invalid_0, settings.edid_copy_invalid_9 (+9) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run settings.edid_copy_output_1/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding BE-25 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-03, P3] |
| F-MTX-015 | External audio: matrix mode | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-03 (P3) | api / audio.mode_0, audio.mode_1 (+7) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run audio.mode_catalog/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-03, P3] |
| F-MTX-016 | External audio: enable per output | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-03 (P3) | api / audio.enable_1_0, audio.enable_1_1 (+18) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run audio.enable_1_0/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-03, P3] |
| F-MTX-017 | External audio: source per output | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-03 (P3) | api / audio.source_1_1, audio.source_1_2 (+69) | no-ws effect | `docs/api/websocket.schema.json (+18)` | PHYS-OWNER-GATE | re-run audio.source_1_1/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding HIL-09 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-03, P3] |
| F-MTX-018 | Front-panel beep on / off | V4 | V1/V1/stale | SW-PROTOCOL-PREP-03 (P3) | api / matrix.beep_off, matrix.beep_on (+1) | no-ws effect | `docs/api/websocket.schema.json (+17)` | MISSING-CLIENT +PHYS | re-run matrix.beep_off/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-03, P3] |
| F-MTX-019 | Front-panel lock | V4 | V1/V1/stale | SW-PROTOCOL-PREP-04 (P3) | api / matrix.panel_lock_off, matrix.panel_lock_on (+1) | no-ws effect | `docs/api/websocket.schema.json (+17)` | MISSING-CLIENT +PHYS | re-run matrix.panel_lock_off/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-04, P3] |
| F-MTX-020 | Front-panel LCD timeout | V4 | V1*/V1/stale | SW-PROTOCOL-PREP-04 (P3) | api / matrix.lcd_invalid_mode, matrix.lcd_missing_mode (+6) | no-ws effect | `docs/api/websocket.schema.json (+17)` | PHYS-OWNER-GATE | re-run matrix.lcd_mode_0/api at current source to refresh; add/execute a real-client end-to-end assertion; close open critical/high finding API-07 by physical measurement (owner); then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-04, P3] |
| F-MTX-021 | Reboot the matrix | V4 | V1/V1/stale | SW-PROTOCOL-PREP-04 (P3) | api,browser / reboot.direct, reboot.enabled_shortcut (+1) | no-ws effect | `docs/api/websocket.schema.json (+27)` | RERUN-FRESH +PHYS | re-run reboot.direct/api at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-04, P3] |
| F-MTX-022 | Rename inputs (names stored on the matrix) | V4 | V1/V1/stale | SW-PROTOCOL-PREP-04 (P3) | api / matrix.input_blank_name, matrix.input_invalid_port (+4) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | re-run matrix.input_name/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-04, P3] |
| F-MTX-023 | Rename outputs (names stored on the matrix) | V4 | V1/V1/stale | SW-PROTOCOL-PREP-04 (P3) | api / matrix.output_blank_name, matrix.output_invalid_port (+4) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT +PHYS | re-run matrix.output_name/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-04, P3] |
| F-MTX-024 | Read the current routing and names | V4 | V2/V2/stale | SW-PROTOCOL-PREP-04 (P3) | api / status.routing_all_1, status.routing_all_8 (+2) | **NOWHERE: output_name_change** | `docs/api/websocket.schema.json (+20)` | MISSING-ASSERT +PHYS | re-run status.routing_mixed/api at current source to refresh; author a declarative scenario asserting output_name_change + different-family review; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-04, P3] |
| F-MTX-025 | Show which inputs have an active signal | V4 | V1/V1/stale | SW-PROTOCOL-PREP-05 (P3) | api / status.signal_1_0, status.signal_1_1 (+14) | no-ws effect | `docs/api/websocket.schema.json (+20)` | MISSING-CLIENT +PHYS | re-run status.signal_1_0/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-05, P3] |
| F-MTX-026 | Show which cables are plugged in (Telnet link status) | V4 | V1/V1/stale | SW-PROTOCOL-PREP-05 (P3) | api / status.cables_all, status.cables_alternating (+2) | no-ws effect | `docs/api/websocket.schema.json (+20)` | MISSING-CLIENT +PHYS | re-run status.cables_none/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-05, P3] |
| F-MTX-027 | Show which outputs have a display connected | V4 | V1/V1/stale | SW-PROTOCOL-PREP-05 (P3) | api / status.display_1_0, status.display_1_1 (+14) | no-ws effect | `docs/api/websocket.schema.json (+20)` | MISSING-CLIENT +PHYS | re-run status.display_1_0/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-05, P3] |
| F-MTX-028 | Show device info (model, firmware, network) | V4 | V1/V1/stale | SW-PROTOCOL-PREP-05 (P3) | api / status.device_dhcp_0, status.device_dhcp_1 (+3) | no-ws effect | `docs/api/websocket.schema.json (+22)` | MISSING-CLIENT +PHYS | re-run status.device_dhcp_0/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-05, P3] |
| F-MTX-029 | Cycle an output to the next / previous input | V4 | V1/V1/stale | SW-PROTOCOL-PREP-05 (P3) | api / status.cycle_next_1_1, status.cycle_next_1_2 (+136) | no-ws effect | `docs/api/websocket.schema.json (+18)` | MISSING-CLIENT +PHYS | re-run status.cycle_next_1_1/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-05, P3] |
| F-MTX-030 | Read a preset's stored routing | V4 | V1/V1/stale | SW-PROTOCOL-PREP-05 (P3) | api / preset_read.catalog_matches_device, preset_read.device_slot_1 (+7) | no-ws effect | `docs/api/websocket.schema.json (+20)` | MISSING-CLIENT +PHYS | re-run preset_read.device_slot_1/api at current source to refresh; add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-05, P3] |
| F-MTX-031 | Notice changes made outside the hub (front panel, cable plugged, source on/off) | V4 | V3/V3/fresh | SW-PROTOCOL-PREP-06 (P3) | browser,ha / ha.front_panel_route, live.display_unplugged (+3) | ws asserted (bound) | `custom_components/hdmi_matrix (+27)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-PROTOCOL-PREP-06, P3] |
| F-OPS-001 | Run the hub from the Docker image | V4 | V3/V3/stale | SW-RUNTIME-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-01, P3] |
| F-OPS-002 | Run the hub without the Remote integration (UC_ENABLED=false, the default) | V4 | V3/V3/stale | SW-RUNTIME-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-01, P3] |
| F-OPS-003 | docker compose quick start | V4 | V3/V3/stale | SW-RUNTIME-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-01, P3] |
| F-OPS-004 | Remote 3 discovery works from Docker | V4 | V2/V2/none | SW-RUNTIME-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-01, P3] |
| F-OPS-005 | Container health check and auto-restart | V4 | V3/V3/stale | SW-RUNTIME-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-01, P3] |
| F-OPS-006 | Point the hub at the matrix (MATRIX_HOST / MATRIX_PORT) | V4 | V3/V3/stale | SW-RUNTIME-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-01, P3] |
| F-OPS-007 | Choose the API port (API_PORT) | V4 | V2/V2/none | SW-RUNTIME-PREP-02 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-02, P3] |
| F-OPS-008 | Matrix credentials (OREI_USER / OREI_PASSWORD) | V4 | V1/V1/none | SW-RUNTIME-PREP-02 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-02, P3] |
| F-OPS-009 | Verify the matrix TLS certificate (OREI_VERIFY_SSL) | V4 | V0/V0/none | SW-RUNTIME-PREP-02 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-02, P3] |
| F-OPS-010 | Log level (LOG_LEVEL) | V4 | V1/V1/none | SW-RUNTIME-PREP-02 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-02, P3] |
| F-OPS-011 | Enable/disable integrations (UC_ENABLED) | V4 | V3/V3/stale | SW-RUNTIME-PREP-02 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-02, P3] |
| F-OPS-012 | Background polling (POLLING_ENABLED / POLLING_INTERVAL) | V4 | V0/V0/none | SW-RUNTIME-PREP-02 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-02, P3] |
| F-OPS-013 | Telnet options (OREI_TELNET_PORT, OREI_USE_TELNET_CEC) | V4 | V1/V1/none | SW-RUNTIME-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-03, P3] |
| F-OPS-014 | Cache and retry tuning (OREI_STATUS_CACHE_TTL, OREI_CEC_CACHE_TTL, OREI_*RETR*) | V4 | V1/V1/none | SW-RUNTIME-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-03, P3] |
| F-OPS-015 | Hub data persists across restarts (DATA_DIR) | V4 | V3/V3/stale | SW-RUNTIME-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-03, P3] |
| F-OPS-016 | Writes are atomic and safe under concurrency | V4 | V1/V1/none | SW-RUNTIME-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-03, P3] |
| F-OPS-017 | Migrate legacy data files (scenes -> profiles) | V4 | V1/V1/none | SW-RUNTIME-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-03, P3] |
| F-OPS-018 | Only one hub instance runs (process lock) | V4 | V1/V1/none | SW-RUNTIME-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-03, P3] |
| F-OPS-019 | One consistent version everywhere | V4 | V1/V1/none | SW-RUNTIME-PREP-04 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-04, P3] |
| F-OPS-020 | Multi-arch images (amd64 + arm64) | V4 | V0/V0/none | SW-RUNTIME-PREP-04 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-04, P3] |
| F-REL-001 | Reconnect automatically after a matrix outage | V4 | V0/V0/stale | SW-RUNTIME-PREP-04 (P3) | api,browser / reboot.direct, reboot.enabled_shortcut (+1) | no-ws effect | `docs/api/websocket.schema.json (+27)` | RERUN-FRESH +PHYS | re-run reboot.direct/api at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-04, P3] |
| F-REL-002 | Report the connection state truthfully on errors and timeouts | V4 | V0/V0/none | SW-RUNTIME-PREP-04 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-04, P3] |
| F-REL-003 | Detect a wrong matrix password | V4 | V0/V0/none | SW-RUNTIME-PREP-04 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-04, P3] |
| F-REL-004 | Log in again when the matrix session expires | V4 | V0/V0/none | SW-RUNTIME-PREP-04 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-04, P3] |
| F-REL-005 | Recover after the matrix reboots or is power-cycled | V4 | V0/V0/stale | SW-RUNTIME-PREP-05 (P3) | api,browser / reboot.direct, reboot.enabled_shortcut (+1) | no-ws effect | `docs/api/websocket.schema.json (+27)` | RERUN-FRESH +PHYS | re-run reboot.direct/api at current source to refresh; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-05, P3] |
| F-REL-006 | Detect a dropped Telnet connection and reconnect | V4 | V0/V0/none | SW-RUNTIME-PREP-05 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-05, P3] |
| F-REL-007 | Shut down and disconnect cleanly | V4 | V0/V0/none | SW-RUNTIME-PREP-05 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-05, P3] |
| F-REL-008 | A command the matrix rejects is reported as failed | V4 | V2/V0/fresh | SW-RUNTIME-PREP-05 (P3) | api / outputs.audio_mute_rejected | no-ws effect | `docs/api/websocket.schema.json (+16)` | MISSING-CLIENT +PHYS | add/execute a real-client end-to-end assertion; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-05, P3] |
| F-REL-009 | Matrix unreachable: commands fail visibly and no state is made up | V4 | V3/V3/fresh | SW-RUNTIME-PREP-05 (P3) | api,browser,ha / failures.unreachable_switch, ha.matrix_offline (+1) | no-ws effect | `custom_components/hdmi_matrix (+26)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-05, P3] |
| F-REL-010 | Status stays fresh (caches expire, one refresh at a time) | V4 | V1/V1/none | SW-RUNTIME-PREP-05 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-05, P3] |
| F-REL-011 | API calls are not blocked while the hub reconnects | V4 | V0/V0/none | SW-RUNTIME-PREP-06 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-06, P3] |
| F-REL-012 | Background polling keeps state live without a Remote connected | V4 | V3/V3/fresh | SW-RUNTIME-PREP-06 (P3) | browser / live.front_panel_route | ws asserted under other feature: signal_change | `docs/api/websocket.schema.json (+23)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-06, P3] |
| F-REL-013 | The event loop never stalls (loop-lag metric) | V4 | V1/V1/none | SW-RUNTIME-PREP-06 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-06, P3] |
| F-REL-014 | A slow WebSocket client cannot stall commands | V4 | V2/V2/none | SW-RUNTIME-PREP-06 (P3) | none / - | no scenario; ws: all broadcasts | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting all broadcasts + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-06, P3] |
| F-REL-015 | Tolerate slow and malformed matrix responses | V4 | V1/V1/none | SW-RUNTIME-PREP-06 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-06, P3] |
| F-REL-016 | Standby does not start reconnect storms or duplicate pollers | V4 | V0/V0/none | SW-RUNTIME-PREP-06 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-06, P3] |
| F-REL-017 | No leaked sessions, sockets or tasks after reconfiguration | V4 | V0/V0/none | SW-RUNTIME-PREP-07 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-RUNTIME-PREP-07, P3] |
| F-REL-018 | 72-hour soak with flat memory, tasks and sockets | V5 | V0/V0/none | SW-SOAK-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +FIELD | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner week-of-use field sign-off (OWNER-FIELD-WEEK) [unit=SW-SOAK-PREP-01, P3] |
| F-SEC-001 | Optional admin / control PIN gate | V3 | V1/V1/none | SW-SEC-AUTH-03 (P1) | api / security_auth.admin_pin_blocks_admin_route, security_auth.api_key_not_admin (+10) | ws asserted under other feature: /ws | `docs/api/websocket.schema.json (+20)` | MISSING-CLIENT | first run of security_auth.status_open/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-SEC-AUTH-03, P1] |
| F-SEC-002 | Cross-site request protection (CORS, Origin, Content-Type, Host allow-list) | V3 | V1/V1/none | SW-SEC-AUTH-03 (P1) | api / security_auth.cross_site_allowed_origin, security_auth.cross_site_bad_host (+3) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT | first run of security_auth.cross_site_bad_host/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-SEC-AUTH-03, P1] |
| F-SEC-003 | Matrix host changes cannot leak the matrix password (SSRF guard) | V3 | V1/V1/none | SW-SEC-AUTH-03 (P1) | api / security_auth.matrix_host_admin_pin, security_auth.matrix_host_link_local (+4) | no-ws effect | `docs/api/websocket.schema.json (+19)` | MISSING-CLIENT | first run of security_auth.matrix_host_password_required/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-SEC-AUTH-03, P1] |
| F-SEC-004 | Profile/scene passcodes are stored as PBKDF2 hashes | V3 | V1/V1/none | SW-SEC-DATA-01 (P1) | api / security_hardening.profile_read_protected, security_hardening.scene_read_protected | no-ws effect | `docs/api/websocket.schema.json (+28)` | MISSING-CLIENT | first run of security_hardening.profile_read_protected/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-SEC-DATA-01, P1] |
| F-SEC-005 | Passcode hashes are never sent to clients | V3 | V1/V1/none | SW-SEC-DATA-01 (P1) | api / security_hardening.profile_read_protected, security_hardening.scene_read_protected | no-ws effect | `docs/api/websocket.schema.json (+28)` | MISSING-CLIENT | first run of security_hardening.profile_read_protected/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-SEC-DATA-01, P1] |
| F-SEC-006 | Changing or removing a PIN needs the current PIN | V3 | V1/V1/none | SW-SEC-AUTH-03 (P1) | api / security_hardening.profile_change_requires_pin, security_hardening.profile_change_with_pin (+9) | no-ws effect | `docs/api/websocket.schema.json (+28)` | MISSING-CLIENT | first run of security_hardening.profile_change_requires_pin/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-SEC-AUTH-03, P1] |
| F-SEC-007 | Wrong-PIN attempts are limited and do not stall the hub | V3 | V3/V3/fresh | SW-SEC-AUTH-01 (P1) | api,browser / security_hardening.profile_wrong_pin, security_hardening.scene_wrong_pin (+8) | no-ws effect | `docs/api/websocket.schema.json (+47)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-SEC-AUTH-01, P1] |
| F-SEC-008 | Rate limiting per client | V3 | V1/V1/none | SW-SEC-AUTH-03 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-SEC-AUTH-03, P1] |
| F-SEC-009 | Proxy headers trusted only from configured proxies | V3 | V1/V1/none | SW-SEC-AUTH-02 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-SEC-AUTH-02, P1] |
| F-SEC-010 | Static files cannot escape the web root | V3 | V1/V1/none | SW-SEC-DATA-01 (P1) | api / security_hardening.static_traversal_backslash, security_hardening.static_traversal_slash | no-ws effect | `docs/api/websocket.schema.json (+16)` | MISSING-CLIENT | first run of security_hardening.static_traversal_backslash/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-SEC-DATA-01, P1] |
| F-SEC-011 | Error responses do not leak internals | V3 | V1/V1/none | SW-SEC-DATA-01 (P1) | api / security_hardening.invalid_schema, security_hardening.non_object_json | no-ws effect | `docs/api/websocket.schema.json (+28)` | MISSING-CLIENT | first run of security_hardening.non_object_json/api at current source to refresh; add/execute a real-client end-to-end assertion [unit=SW-SEC-DATA-01, P1] |
| F-SEC-012 | User-provided names are escaped in the UI (no XSS) | V3 | V3/V3/none | SW-SEC-DATA-01 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-SEC-DATA-01, P1] |
| F-SEC-013 | TLS certificate verification / pinning for the matrix | V3 | V1/V1/none | SW-SEC-DATA-01 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-SEC-DATA-01, P1] |
| F-SEC-014 | No credentials in logs | V3 | V1/V1/none | SW-SEC-DATA-02 (P1) | none / - | no-ws effect | `-` | REPRODUCED-DEFECT | dispatch corrective package for VAL-15; no auto-close; author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-SEC-DATA-02, P1] |
| F-SEC-015 | Remote 3 integration port requires authentication | V3 | V3/V3/none | SW-SEC-AUTH-02 (P1) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-SEC-AUTH-02, P1] |
| F-UC-001 | Discover the integration and register the driver (mDNS, driver URL) | V4 | V0/V0/none | SW-UC-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-01, P3] |
| F-UC-002 | Set up the integration on the Remote | V4 | V1/V1/none | SW-UC-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-01, P3] |
| F-UC-003 | Reconfigure the integration (new matrix address) | V4 | V3/V3/none | SW-UC-PREP-01 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-01, P3] |
| F-UC-004 | Preset buttons on the Remote | V4 | V3/V3/fresh | SW-UC-PREP-01 (P3) | uc / remote.preset_button, remote.preset_names_from_web_app | no-ws effect | `docs/api/websocket.schema.json (+21)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-01, P3] |
| F-UC-005 | Matrix remote entity with a preset page | V4 | V3/V3/fresh | SW-UC-PREP-01 (P3) | uc / remote.matrix_preset_command, remote.preset_names_from_web_app | no-ws effect | `docs/api/websocket.schema.json (+21)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-01, P3] |
| F-UC-006 | Per-input CEC remotes (source power, navigation, playback) | V4 | V3/V3/fresh | SW-UC-PREP-01 (P3) | uc / remote.input_cec_command, remote.input_cec_off (+1) | no-ws effect | `docs/api/websocket.schema.json (+21)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-01, P3] |
| F-UC-007 | Per-output CEC remotes (TV power, volume) | V4 | V3/V3/fresh | SW-UC-PREP-02 (P3) | uc / remote.cec_bad_sequence, remote.output_cec_on (+3) | no-ws effect | `docs/api/websocket.schema.json (+21)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-02, P3] |
| F-UC-008 | Choose an output's source from the Remote (media player source list) | V4 | V3/V3/fresh | SW-UC-PREP-02 (P3) | uc / remote.input_rename_live, remote.select_source (+1) | no-ws effect | `docs/api/websocket.schema.json (+20)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-02, P3] |
| F-UC-009 | TV power / volume / mute from the output media player | V4 | V3/V3/fresh | SW-UC-PREP-02 (P3) | uc / remote.media_player_toggle, remote.media_player_volume | no-ws effect | `docs/api/websocket.schema.json (+21)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-02, P3] |
| F-UC-010 | Matrix power switch on the Remote | V4 | V3/V3/fresh | SW-UC-PREP-02 (P3) | uc / remote.power_switch_follows_front_panel, remote.power_switch_off | no-ws effect | `docs/api/websocket.schema.json (+19)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-02, P3] |
| F-UC-011 | Input signal and cable sensors | V4 | V1/V1/none | SW-UC-PREP-02 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-02, P3] |
| F-UC-012 | Output connected, cable and source sensors | V4 | V3/V3/none | SW-UC-PREP-02 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-02, P3] |
| F-UC-013 | Entities go unavailable while the matrix is unreachable | V4 | V3/V3/none | SW-UC-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-03, P3] |
| F-UC-014 | Remote standby and wake | V4 | V3/V3/none | SW-UC-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-03, P3] |
| F-UC-015 | Only changed attributes are sent to the Remote | V4 | V3/V3/none | SW-UC-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-03, P3] |
| F-UC-016 | Renamed inputs/outputs show up on the Remote | V4 | V3/V3/fresh | SW-UC-PREP-03 (P3) | uc / remote.input_rename_live | no-ws effect | `docs/api/websocket.schema.json (+20)` | PHYS-OWNER-GATE | no SW-AUDIT-01 action; preserve accepted evidence; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-03, P3] |
| F-UC-017 | Restore the configuration at startup (also with the matrix offline) | V4 | V3/V3/none | SW-UC-PREP-03 (P3) | none / - | no-ws effect | `-` | MISSING-ASSERT +PHYS | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record; then owner HIL measurement on the physical device (OWNER-HIL-*) [unit=SW-UC-PREP-03, P3] |
| F-UI-001 | Open the web UI; the header shows the matrix connection | V3 | V3/V3/none | SW-UI-CONTROL-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-CONTROL-01, P2] |
| F-UI-002 | Route by clicking a cell in the matrix grid | V3 | V3/V3/stale | SW-UI-CONTROL-01 (P2) | browser / routing.switch_one | no-ws effect | `docs/api/websocket.schema.json (+23)` | RERUN-FRESH | re-run routing.switch_one/browser at current source to refresh [unit=SW-UI-CONTROL-01, P2] |
| F-UI-003 | Route from the matrix card view (routing sheet) | V3 | V1/V1/none | SW-UI-CONTROL-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-CONTROL-01, P2] |
| F-UI-004 | Route one input to every output from the Route To All drawer | V3 | V1/V1/stale | SW-UI-CONTROL-01 (P2) | browser / routing.route_all | no-ws effect | `docs/api/websocket.schema.json (+25)` | RERUN-FRESH | re-run routing.route_all/browser at current source to refresh [unit=SW-UI-CONTROL-01, P2] |
| F-UI-005 | Recall a preset from the Presets drawer | V3 | V1/V1/stale | SW-UI-CONTROL-01 (P2) | browser / presets.recall | no-ws effect | `docs/api/websocket.schema.json (+24)` | RERUN-FRESH | re-run presets.recall/browser at current source to refresh [unit=SW-UI-CONTROL-01, P2] |
| F-UI-006 | Rename a preset in the Presets drawer | V3 | V3/V1/fresh | SW-UI-CONTROL-01 (P2) | browser / presets.rename | no-ws effect | `docs/api/websocket.schema.json (+25)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-UI-CONTROL-01, P2] |
| F-UI-007 | Overwrite a preset / save a custom mapping from the Presets drawer | V3 | V1/V1/none | SW-UI-CONTROL-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-CONTROL-02, P2] |
| F-UI-008 | Run profiles, scenes, presets, shortcuts and macros from dashboard cards | V3 | V3/V3/fresh | SW-UI-MANAGE-01 (P2) | browser / scenes.run_protected | no-ws effect | `docs/api/websocket.schema.json (+35)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-UI-MANAGE-01, P2] |
| F-UI-009 | Customise the dashboard (card picker, pin, reorder) | V3 | V1/V1/none | SW-UI-MANAGE-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-01, P2] |
| F-UI-010 | Inputs tab: signal/cable status and input settings (name, icon, EDID) | V3 | V1/V1/none | SW-UI-CONTROL-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-CONTROL-02, P2] |
| F-UI-011 | Outputs tab: display status and output settings (HDCP, HDR, scaler, ARC, mute) | V3 | V1/V1/none | SW-UI-CONTROL-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-CONTROL-02, P2] |
| F-UI-012 | Profiles tab and profile manager | V3 | V3/V3/fresh | SW-UI-MANAGE-01 (P2) | browser / profiles.recall_routing | no-ws effect | `docs/api/websocket.schema.json (+30)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-UI-MANAGE-01, P2] |
| F-UI-013 | Create and edit a profile in the profile editor | V3 | V1/V1/none | SW-UI-MANAGE-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-01, P2] |
| F-UI-014 | Run a passcode-protected profile (passcode prompt) | V3 | V3/V3/fresh | SW-UI-MANAGE-01 (P2) | browser / profiles.recall_needs_passcode, profiles.recall_with_passcode (+1) | no-ws effect | `docs/api/websocket.schema.json (+31)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-UI-MANAGE-01, P2] |
| F-UI-015 | Build a scene in the scene editor | V3 | V3/V3/none | SW-UI-MANAGE-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-01, P2] |
| F-UI-016 | Build a CEC macro in the macro editor | V3 | V1/V1/none | SW-UI-MANAGE-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-02, P2] |
| F-UI-017 | CEC remote on output/input tiles and the CEC tray | V3 | V1/V1/none | SW-UI-CONTROL-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-CONTROL-02, P2] |
| F-UI-018 | Theme presets, customisation and card opacity | V3 | V1/V1/none | SW-UI-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-01, P2] |
| F-UI-019 | General settings: matrix host and connection test | V3 | V1/V1/none | SW-UI-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-01, P2] |
| F-UI-020 | Hardware settings: beep, panel lock, LCD, reboot | V3 | V1/V1/none | SW-UI-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-01, P2] |
| F-UI-021 | Interface settings | V3 | V1/V1/none | SW-UI-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-01, P2] |
| F-UI-022 | Shortcuts drawer: run, rename, reorder | V3 | V1/V1/none | SW-UI-MANAGE-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-02, P2] |
| F-UI-023 | Integrations drawer (Flic request builder, HA YAML, Remote 3 info) | V3 | V1/V1/none | SW-UI-MANAGE-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-02, P2] |
| F-UI-024 | Live updates when another client or the matrix changes something | V3 | V3/V3/fresh | SW-UI-CONTROL-02 (P2) | browser / live.display_unplugged, live.front_panel_route (+3) | no-ws effect | `docs/api/websocket.schema.json (+24)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-UI-CONTROL-02, P2] |
| F-UI-025 | Reconnect and resync after the WebSocket drops | V3 | V3/V3/none | SW-UI-CONTROL-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-CONTROL-02, P2] |
| F-UI-026 | Show an error state when the matrix is unreachable | V3 | V3/V3/none | SW-UI-CONTROL-03 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-CONTROL-03, P2] |
| F-UI-027 | Toasts and confirmation dialogs | V3 | V3/V3/fresh | SW-UI-CONTROL-03 (P2) | browser / scenes.partial_failure | no-ws effect | `docs/api/websocket.schema.json (+34)` | PRESERVE | no SW-AUDIT-01 action; preserve accepted evidence [unit=SW-UI-CONTROL-03, P2] |
| F-UI-028 | Keyboard shortcuts | V3 | V1/V1/none | SW-UI-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-01, P2] |
| F-UI-029 | Accessibility (keyboard, focus, ARIA, contrast, zoom) | V3 | V1/V1/none | SW-UI-PRESENT-01 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-01, P2] |
| F-UI-030 | Debug panel | V3 | V1/V1/none | SW-UI-PRESENT-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-02, P2] |
| F-UI-031 | About dialog | V3 | V3/V3/none | SW-UI-PRESENT-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-02, P2] |
| F-UI-032 | Animated Tron background (opt-in) | V3 | V1/V1/none | SW-UI-PRESENT-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-02, P2] |
| F-UI-033 | Tablet and phone layouts | V3 | V1/V1/none | SW-UI-PRESENT-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-PRESENT-02, P2] |
| F-UI-034 | Personalise tabs in the Control Deck (pin, reorder) | V3 | V1/V1/none | SW-UI-MANAGE-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-02, P2] |
| F-UI-035 | Copy an API endpoint for automation (API button / modal) | V3 | V1/V1/none | SW-UI-MANAGE-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-02, P2] |
| F-UI-036 | First-run setup wizard (matrix connection) | V3 | V1/V1/none | SW-UI-MANAGE-02 (P2) | none / - | no-ws effect | `-` | MISSING-ASSERT | author a declarative scenario asserting this feature + different-family review; run it to produce the first evidence record [unit=SW-UI-MANAGE-02, P2] |

---

## 8. Per-unit crosswalk (no test is claimed to have run)

The 268 rows are owned by **57 of the 65 mapped dispatch units**. The eight
units that own no feature row by design are `SW-AUDIT-01`,
`SW-FINDINGS-01`, `SW-HARNESS-01` (all P0) and `SW-REPO-01`, `SW-DOCS-01`,
`SW-VERSION-01`, `SW-BUILD-01`, `SW-SOFTWARE-GATE-01` (P4/P5) — they are
cross-cutting or gate the whole set rather than owning a feature.
Rows per execution phase: **P1 = 64**, **P2 = 83**, **P3 = 121**, **P4 = 0**,
**P5 = 0**, **OWNER = 0**. The five P4 entries (`SW-REPO-01`, `SW-DOCS-01`,
`SW-VERSION-01`, `SW-BUILD-01`, `SW-SOFTWARE-GATE-01`) and the seven OWNER
gates carry **no feature rows**; they gate the 268 rows as a set (claims,
docs, version, build, combined pipeline; physical HIL/CEC, 72-hour soak,
week-of-use and final release). No P2/P3/P4/P5 acceptance test is claimed to
have run by this report.

| Unit (phase) | Rows | Disposition mix | Smallest next independently executable slice |
| --- | ---: | --- | --- |
| `SW-API-CLIENT-01` (P1) | 6 | 4 MISSING-CLIENT, 2 MISSING-ASSERT | one real-client (browser) execution of the existing API scenarios — no new assertion needed |
| `SW-API-CLIENT-02` (P1) | 6 | 3 MISSING-CLIENT, 3 MISSING-ASSERT | `F-API-034` `switch_all_failed` declarative scenario + connected control (new assertion, different-family review) |
| `SW-API-WRITE-01` (P1) | 6 | 3 RERUN-FRESH, 3 MISSING-ASSERT | re-run the 3 stale `preset_read.*` units |
| `SW-API-WRITE-02` (P1) | 6 | 2 PRESERVE, 4 RERUN-FRESH | re-run the 4 stale units |
| `SW-API-WRITE-03` (P1) | 6 | 3 RERUN-FRESH, 2 MISSING-ASSERT, 1 PRESERVE | re-run 3 stale units; `F-API-037` `device_settings_full` assertion |
| `SW-API-WRITE-04` (P1) | 2 | 2 PRESERVE | none |
| `SW-API-READ-01` (P1) | 1 | 1 PRESERVE | none |
| `SW-API-READ-02` (P1) | 4 | 4 PRESERVE | none |
| `SW-API-READ-03` (P1) | 3 | 3 MISSING-ASSERT | `F-API-039`/`F-API-042`/`F-API-040` WS assertions |
| `SW-API-READ-04` (P1) | 2 | 2 PRESERVE | none (CORS V2 already accepted) |
| `SW-SEC-AUTH-01` (P1) | 1 | 1 PRESERVE | none (F-SEC-007 is at target and fresh on the canonical ledger) |
| `SW-SEC-AUTH-02` (P1) | 2 | 2 MISSING-ASSERT | `F-SEC-008`/`F-SEC-009` declarative scenarios |
| `SW-SEC-AUTH-03` (P1) | 5 | 4 MISSING-CLIENT, 1 MISSING-ASSERT | real-client proof for the profile rows |
| `SW-SEC-DATA-01` (P1) | 6 | 4 MISSING-CLIENT, 2 MISSING-ASSERT | real-client proof + `F-SEC-012`/`F-SEC-013` scenarios |
| `SW-SEC-DATA-02` (P1) | 1 | 1 REPRODUCED-DEFECT | **`F-SEC-014` / VAL-15** — depends on `RV-PRIVACY-CHAIN`; no dispatch here |
| `SW-DOM-PROFILE-01` (P1) | 6 | 5 MISSING-CLIENT, 1 PRESERVE | real-client execution of the existing profile scenarios |
| `SW-DOM-PROFILE-02` (P1) | 1 | 1 RERUN-FRESH | re-run the stale unit |
| `SW-DOM-SCENE-01` (P2) | 6 | 5 PRESERVE, 1 MISSING-CLIENT | one real-client execution |
| `SW-DOM-MACRO-01` (P2) | 3 | 3 MISSING-CLIENT | real-client execution |
| `SW-DOM-SHORTCUT-01` (P2) | 6 | 5 PRESERVE, 1 RERUN-FRESH | re-run the stale unit |
| `SW-DOM-SHORTCUT-02` (P2) | 2 | 2 MISSING-ASSERT | declarative scenarios |
| `SW-DOM-PRESENT-01` (P2) | 6 | 4 MISSING-ASSERT, 2 MISSING-CLIENT | `F-DOM-032` device-settings scenario + real-client execution |
| `SW-UI-CONTROL-01` (P2) | 6 | 3 RERUN-FRESH, 2 MISSING-ASSERT, 1 PRESERVE | re-run 3 stale browser units |
| `SW-UI-CONTROL-02` (P2) | 6 | 5 MISSING-ASSERT, 1 PRESERVE | declarative UI scenarios |
| `SW-UI-CONTROL-03` (P2) | 2 | 1 MISSING-ASSERT, 1 PRESERVE | one declarative scenario |
| `SW-UI-MANAGE-01` (P2) | 6 | 3 PRESERVE, 3 MISSING-ASSERT | declarative UI scenarios |
| `SW-UI-MANAGE-02` (P2) | 6 | 6 MISSING-ASSERT | declarative UI scenarios |
| `SW-UI-PRESENT-01` (P2) | 6 | 6 MISSING-ASSERT | declarative UI scenarios |
| `SW-UI-PRESENT-02` (P2) | 4 | 4 MISSING-ASSERT | declarative UI scenarios |
| `SW-KIOSK-CONTROL-01` (P2) | 6 | 3 MISSING-ASSERT, 2 RERUN-FRESH, 1 PRESERVE | re-run 2 stale kiosk units + scenarios |
| `SW-KIOSK-CONTROL-02` (P2) | 1 | 1 MISSING-ASSERT | one declarative scenario |
| `SW-KIOSK-STATE-01` (P2) | 6 | 4 MISSING-ASSERT, 2 PRESERVE | declarative kiosk scenarios |
| `SW-KIOSK-STATE-02` (P2) | 1 | 1 MISSING-ASSERT | one declarative scenario |
| `SW-FLIC-01` (P2) | 6 | 4 PRESERVE, 2 RERUN-FRESH | re-run 2 stale Flic units (admission HOLD unchanged) |
| `SW-FLIC-02` (P2) | 4 | 3 PRESERVE, 1 RERUN-FRESH | re-run 1 stale Flic unit (admission HOLD unchanged) |
| `SW-PROTOCOL-PREP-01` (P3) | 6 | 3 PHYS-OWNER-GATE, 2 MISSING-ASSERT, 1 MISSING-CLIENT | `F-MTX-002` `switch_all_failed` assertion; then owner HIL |
| `SW-PROTOCOL-PREP-02` (P3) | 6 | 6 PHYS-OWNER-GATE | the 6 `HIL-09(C)`-capped rows: physical measurement |
| `SW-PROTOCOL-PREP-03` (P3) | 6 | 5 PHYS-OWNER-GATE, 1 MISSING-CLIENT | physical measurement; one real-client execution |
| `SW-PROTOCOL-PREP-04` (P3) | 6 | 3 MISSING-CLIENT, 1 each PHYS-OWNER-GATE/RERUN/MISSING-ASSERT | `F-MTX-024` `output_name_change` assertion; real-client execution |
| `SW-PROTOCOL-PREP-05` (P3) | 6 | 6 MISSING-CLIENT | real-client execution |
| `SW-PROTOCOL-PREP-06` (P3) | 6 | 4 MISSING-CLIENT, 2 PHYS-OWNER-GATE | real-client execution; then owner HIL |
| `SW-PROTOCOL-PREP-07` (P3) | 6 | 6 MISSING-CLIENT | real-client execution |
| `SW-RUNTIME-PREP-01..07` (P3) | 37 | 32 MISSING-ASSERT(+PHYS), 2 PHYS-OWNER-GATE, 2 RERUN-FRESH(+PHYS), 1 MISSING-CLIENT(+PHYS) | declarative reliability scenarios; `F-REL-014` "slow client cannot stall commands" has a WS contract and no scenario |
| `SW-UC-PREP-01..03` (P3) | 17 | 9 MISSING-ASSERT(+PHYS), 8 PHYS-OWNER-GATE | declarative Remote-3 scenarios; then owner HIL |
| `SW-HA-PREP-01..03` (P3) | 18 | 17 RERUN-FRESH(+PHYS), 1 MISSING-ASSERT(+PHYS) | re-run the 17 stale HA units (the accepted re-run set of the freshness delta) |
| `SW-DOM-HIL-PREP-01` (P3) | 6 | 6 PHYS-OWNER-GATE | owner HIL measurement |
| `SW-SOAK-PREP-01` (P3) | 1 | 1 MISSING-ASSERT(+FIELD) | `F-REL-018` soak scenario, then owner 72-hour soak and field week |

**Accepted-intake dependencies for the smallest executable slices.** Every slice
above is *independently executable* only after the intake it depends on has
been accepted:

* the **re-run** slices need the current source to be the accepted integration
  head and the scenario/client to exist unchanged — no new assertion, but a
  different-family review of the produced record is still required before it is
  canonical evidence;
* the **new-assertion** slices (`F-API-034`, `F-API-035`, `F-API-037`,
  `F-API-040`, `F-MTX-002`, `F-MTX-003`, `F-MTX-024`, `F-DOM-032`,
  `F-API-039`, `F-API-042`, `F-REL-014`) are new implementation deliverables
  and need a qualified **different-underlying-family** review at the exact
  commit before integration;
* the **real-client** slices need a client that the CI command actually
  requests — the accepted CI inventory shows the CI run only requested
  `api,browser,uc` and `ha`, which is why the 4 Flic units are absent from it;
* the **admission** slices (`F-FLIC-*`, the 56 CI records, the privacy
  artefacts) depend on `EV-PRIVACY-ADMISSION`, `EV-FLIC-ADMISSION` and
  `EV-CI-ATTRIBUTION`, which are themselves gated on the P1 review pins;
* the **owner** slices depend on nothing in software and cannot be executed by
  an agent.

---

## 9. Reuse of the accepted earlier slices, and where they agree

| Accepted slice | What it already established | How this report uses it |
| --- | --- | --- |
| [COORDINATOR_REVIEW.md](../COORDINATOR_REVIEW.md) | accepts the freshness delta's mapping at report `11b09676`, with two stated limits: the `git diff --name-only` exit-code statement is an erratum, and the author overwrote its first mangled scratch extracts (originals not preserved) | the limits are carried forward unchanged in §11; nothing in this report re-scans raw evidence, so the diagnostic preservation gap is not widened |
| [FRESHNESS_DELTA.md](../FRESHNESS_DELTA.md) | 268 rows in both ledgers, 54 changed rows, 39 `fresh → stale`, `F-API-031` newly fresh, below-target 203→210, stale 57→96, the 38-row/60-unit/55-scenario re-run set, the `F-API-034` `switch_all_failed` assertion gap, and the owner package/unit of every changed row | the 39 stale rows were re-parsed from the accepted tables and compared with this inventory: **all 39 are stale in the canonical ledger at the base**, and the accepted `rerun` / `assertion-gap` labels are carried into the table's actions. The accepted 15-row "preserve" set is **not** copied as a global disposition: those labels describe the *ledger-row delta* (the row's displayed evidence set changed), while this report's disposition describes the *whole acceptance state* of the row, which is strictly more information. Where the two differ the difference is stated in the row's reason column, not hidden |
| [CI_EVIDENCE_REVIEW.md](../CI_EVIDENCE_REVIEW.md) | 56 CI records at the non-ancestral source `bdcf06dc` are stale/unknown under the ledger rule; 4 Flic units absent because the CI command never requested the `flic` client; `F-API-034`'s gap confirmed across 1 480 scenarios; screenshots structurally verified, not visually approved | the CI records are **not** counted as features and are not treated as fresh evidence; the absence of Flic units in CI is used in §8 to state the intake dependency for the real-client slices |
| [FLIC_EVIDENCE_REVIEW.md](../FLIC_EVIDENCE_REVIEW.md) | 4 Flic V3 records at `865ec9c6` are genuine `client=flic` artefacts with 26 checks (25 pass, 1 n/a); 8 unchanged unmasked fixture-password fields; privacy and artefact-admission HOLD preserved | the Flic rows keep their canonical-ledger state; the privacy HOLD is carried unchanged into §6 row 6 and §10 |
| [W03-CLOSE-INVENTORY/AUTHOR.md](../../W03-CLOSE-INVENTORY/AUTHOR.md) | 88 records inventoried (57 original API V2 + 31 fresh), preservation gaps G1–G7, VAL-14/VAL-15 register state, the `F-SEC-007` historical gate explanation | the G1–G4 preservation gaps and the `F-SEC-007` stale-historical-gate explanation are carried into §6 rows 5 and 7; nothing was re-hashed or re-scored |

**Crosswalk result.** Of the 39 rows the accepted freshness delta classified as
`rerun` (plus the one `assertion-gap` row), this inventory independently finds
**all 39 stale** in the canonical ledger at the base, and **all 39** of those
rows carry the accepted re-run step in their next acceptance action. 32 of the
39 get the same software-axis label; the other 7 differ only because the
accepted label is the *ledger-delta* disposition ("the evidence is stale,
re-run it") while this report's label is the stricter *whole-state*
disposition ("the row is stale **and** its V3 target still needs a real-client
proof" — `F-API-005`, `F-API-007`, `F-DOM-034`, `F-MTX-004`, `F-MTX-030`; or
"its contract effect is asserted nowhere" — `F-API-035`, `F-MTX-002`). For the
15 rows the accepted slice marks `preserve` for the delta, 11 get the same
label and 4 differ, each for a stated reason: `F-API-033` (V3 target, `api`-only
live coverage), `F-MTX-003` (`preset_recall_failed` asserted nowhere),
`F-MTX-007` (capped at V1 by the open critical `HIL-09(C)`), `F-SEC-014` (open
reproduced finding `VAL-15`). None of these differences reopens an accepted
scope: the delta disposition describes what changed in the ledger row, this
report describes what the row still owes.

---

## 10. Explicit unknowns and unresolved intake

These are **unknown**, not verified. They are listed so that no reader infers
coverage that was not established.

1. **Non-WebSocket effect coverage is not mechanically checkable here.** 243
   of the 268 contracts declare no WebSocket effect; for those, the contract's
   "independent device/storage/rendered effect" is asserted by non-declarative
   means in the registry `basis`. This report states *that* such a proof is
   cited and *which* scenarios exist, but it does **not** verify the
   correctness of the cited non-declarative proofs. That remains source-review
   work, not inventory work.
2. **Effect assertions asserted under a different feature id** (5 rows, §6.1)
   are recorded as attribution gaps. Whether the covering scenario should also
   claim those feature ids is an ownership decision for the owning unit and
   the coordinator; this report does not change any feature mapping.
3. **Freshness is evaluated only against the canonical ledger's generation
   `HEAD` (`28fce729`)**, as committed. Whether the 96 stale rows will pass at
   the current source is **not known**; staleness establishes neither a defect
   nor a pass.
4. **The manifest is dated planning data** (`observed_utc` 2026-10-20,
   `baseline_sha 97e617c2`, `stale_snapshot 57`). It was used only for
   package/unit ownership and declared client mappings. A manifest `planned`
   flag was never read as missing code, and no accepted historical scope was
   reopened.
5. **Candidate-specific freshness is not answered.** The inventory describes
   the canonical ledger state at the base only. `F-SEC-007` is `PRESERVE` on
   the canonical ledger; whether the candidate `caaa4faa` needs a new browser
   proof is the `EV-API034-SECURITY-REFRESH` question and is not answered here.
6. **The 56 CI records and the 4 Flic records are not ordinary fresh
   evidence.** Their non-ancestral source identity and the privacy HOLD are
   unchanged; no admission is implied.
7. **No private evidence bytes were read.** No raw record, archive or
   screenshot was opened; the raw-evidence scans of the accepted slices were
   reused, not repeated. The 8 unmasked fixture-password fields are reported
   only as a **count** carried over from the accepted Flic review.
8. **The 100 features with no live declarative scenario** are baseline-only
   features whose proof rests on non-declarative tests cited in the registry
   `basis`. Whether each of those needs a declarative scenario is a unit-level
   judgement; the inventory states the absence and the owning unit, and does
   not assert that the underlying behaviour is unproven.
9. **No physical, HIL, CEC, outage, 72-hour soak, week-of-use, visual or
   release gate was executed, inspected for fact, or dispositioned.**

---

## 11. Limits, failures and preservation notes of this attempt

* **Method limits.** The inventory is a *classification over committed bytes
  plus live declarative declarations*. It is not a code review and it does not
  reproduce any behaviour. No scenario, campaign, formal gate or ledger
  generation was run. No source byte was modified.
* **Diagnostic preservation.** This author's first scratch extraction
  overwrote its own earlier mangled output before being replaced by a
  byte-exact version. The original generated bytes of that first pass were
  **not** preserved and are not reconstructed as originals. This is the same
  class of diagnostic preservation gap the accepted coordinator review already
  recorded for the freshness-delta author, and it is stated here rather than
  papered over. No project source, evidence byte, historical record or
  baseline was touched; all inputs are read-only and byte-identical to the
  base (§2). Every scratch artefact of this attempt is retained under
  `build/software-waves/SW-AUDIT-01/execution-20261101/author/**` and
  `C:/t/exec-sw-audit-01/nov02-attempt01/**`; nothing was deleted.
* **Superseded first parses.** Two early parser attempts produced wrong
  results and were replaced, not hidden: (a) the first ledger parse used the
  raw `|` split and dropped the three escaped-pipe titles (`F-API-004`,
  `F-API-009`, `F-API-018`); (b) the first `FEATURE_CONTRACTS`/manifest probe
  assumed `features.yaml` was a mapping and raised `TypeError: list indices
  must be integers`. The corrected parser (`(?<!\\)\|` split, list-safe
  registry access) produced the numbers in §4. Both failures are recorded in
  the private scratch tree; the failed outputs were preserved, not deleted.
* **No credentials, raw evidence payloads or environment values were printed**
  in this report or in any scratch artefact.
* **No hook was bypassed silently.** The configured `core.hooksPath`
  pre-commit hook runs `ruff` and the fast `pytest tests/` suite; this
  dispatch authorises no test campaign, so the commit uses the documented
  **invocation-only** exception `git -c core.hooksPath= commit`, which changes
  no hook configuration. The checks actually performed are the UTF-8/CR/scope
  audit in §12 and the five documentation modules.

---

## 12. Commands, checks, exits and artefact hashes

Interpreter: `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(Python 3.12.10). `PYTHONPATH` = this checkout's root **and** `src`;
`PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`.
Every invocation used a **fresh** `C:/t/exec-sw-audit-01/nov02-attempt01/**`
subdirectory with an isolated `MATRIX_DATA_DIR` and `UC_CONFIG_HOME`.

| # | Invocation | Exit | Result |
| ---: | --- | ---: | --- |
| 1 | `git rev-parse HEAD` | 0 | `b4a2c6e93918028e080fdc5ed3d7abedb3f14a9e` — equal to the injected spec base |
| 2 | `git status --short` (before any write) | 0 | empty |
| 3 | `git branch --show-current` | 0 | `execution/wp-exec-sw-audit-01` |
| 4 | `git rev-parse e2161484…:docs/validation/LEDGER.md HEAD:docs/validation/LEDGER.md` | 0 | both `281a7647b41e816529d8b7d953df7705a3084d98` — the canonical ledger is unchanged between the packet floor and this base |
| 5 | SHA-256 over the 38 packet files | 0 | `FINAL_PACKET.json` = `52ed758e…` (the accepted packet, verified); all declared member hashes reproduced |
| 5b | SHA-256 of the shared frozen rubric (root path, read-only) and of this worktree's checkout | 0 | root 3 384 B = `66f37090…`; worktree 3 426 B (42 CRLF) = `66f37090…` after LF normalisation — same content |
| 6 | `author/probe_structure.py` | 0 | manifest/pin structure census (30 packages, 65 units, 268 features, 85 pins) |
| 7 | `author/probe_registry.py` (first attempt) | **1** | `TypeError: list indices must be integers` — `features.yaml` is a list, not a mapping; corrected in attempt 02, output preserved |
| 8 | `author/probe_registry.py` (corrected) | 0 | 268 registry rows; 1 507 scenarios discovered; expectation `describe()` reachable |
| 9 | `author/hash_inputs.py` (first attempt) | **1** | wrong repo-root parent index → `FileNotFoundError` on `FINAL_PACKET.json`; corrected, first output preserved |
| 10 | `author/hash_inputs.py` (corrected) | 0 | accepted packet `52ed758e…` located and verified |
| 11 | `author/build_inventory.py` | 0 | 268 rows; §4 counts reproduced exactly; `inventory.json` written |
| 12 | `author/render_table.py` | 0 | 268-row table + breakdowns; `table268.md` written |
| 13 | `author/crosscheck_accepted.py` | 0 | 39/39 accepted-stale rows confirmed stale at the base; 1 accepted assertion-gap independently confirmed; axis differences listed in §9 |
| 14 | `author/probe_details.py` | 0 | 100 scenario-less features; 7 unasserted effects; 5 else-bound effects; 12 capped rows |
| 15 | `python -m pytest tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -p no:tests.route_inventory -p no:cacheprovider -q` | **0** | **489 passed in 3.03 s** (the five core/client-guide/openapi-config/security/license-protocol documentation modules; no other test was run and no route proof was overwritten) |
| 16 | `git grep -n "switch_all_failed\|preset_recall_failed\|device_settings_full\|output_name_change" -- src web` | 0 | emitters exist in `src/rest_api/control.py:78,129,153`, `src/rest_api/device_settings.py:622`, `src/rest_api/events.py:465` |
| 17 | `author/hash_all.py` | 0 | input and artefact SHA-256 values in §2 and below |
| 18 | report UTF-8 decode, CR-byte scan, trailing-whitespace scan, final-newline check, local-link resolution, tracked-scope screen | 0 | see §12.1 |
| 19 | `python -m tools.validate ledger` | **not run** | deliberately not run: no canonical regeneration in this report |
| 20 | full test / core / CI / image suite, validation campaigns, hardware, Docker, owner deployment | **not run** | out of scope for this dispatch |

### 12.1 Own private artefacts (ignored; retained, not deleted)

| SHA-256 | Bytes | Artefact |
| --- | ---: | --- |
| `51d6cb040a2cce097c2a45a3de9963e1e183c5e7f43d2e93ab00c05cbc392bb4` | 815 510 | `author/inventory.json` — all 268 rows, every derived field |
| `6115b03cacee49b4635a23f093ee7c14c52d5301ca30523434f204ba9caca71c` | 97 224 | `author/table268.md` — the rendered 268-row table |
| `48c97471dc3df9addea4cd5bf0ac64b975cfcb23a31c233a7c17d4b97a15683e` | 14 667 | `author/build_inventory.py` — the inventory builder |
| `3d7dca06134c86255f4fe9b85e6d7715354763017e2281be6379f6bab66c6067` | 4 587 | `author/render_table.py` — table renderer + breakdowns |
| `ee57e101ac0782d0ee8b187e21a8264c74e6560c7df7f52ea84cde5cb9703e52` | 3 853 | `author/crosscheck_accepted.py` — accepted-slice cross-check |
| `edb84c4daae5cc52711286e1b3361ae26feebf344ede1cf1a52382d6cd5267cc` | 3 887 | `author/assemble_report.py` — report assembly + scope/UTF-8 audit |
| `6633dc5edb0a27ee7d7d2fce62eba1e8d0449dd582ed13beb11e58ca61857570` | 2 188 | `author/probe_details.py` |
| `ef394b3659631051940c4d89dd034f8f2a900a2eb120d39d03c31e0083387b7a` | 1 782 | `author/hash_all.py` |
| `d5eb4e1742fbd8dfe95d51ab2b3434b7ab87bf8f73c486dfa83d44945cf4cd75` | 1 731 | `author/probe_registry.py` |
| `7bb9797a850ae93243231898ef4f3ba0ecff88d79d319eefafed82a4abddb363` | 1 862 | `author/probe_structure.py` |
| `2fcbdad82c11ee7122a05fdff6b5d9648dbfc8b6db9630e37ae83cb7995e80b2` | 1 691 | `author/hash_inputs.py` |
| `a409111334e0b9ed27affb04d85a1dc2ffe7eb3eb2903a077b8cd8149aef16a4` | 23 056 | `author/report_head.md` — report prose, part 1 |
| `1c8363aa3112ab6ed2b292d543e118b00da8e96bb7b0fab3c3f902d0cd0c7921` | 23 002 | `author/report_tail.md` — report prose, part 2 |
| `c03538c1…` / `a8c6d592…` / `ec5ec237…` / `e68f1ff2…` / `bd02be45…` / `52ed758e…` / `3106f55b…` / `a4b48170…` / `bf19589d…` / `989971d0…` / `20ad93f0…` | — | input hashes of §2 and the accepted slices (§9) |

The tracked report itself is exactly one new file:
`docs/production/software-waves/SW-AUDIT-01/execution-20261101/AUTHOR.md`.
Its byte length, Git blob SHA-256 and commit id are stated in the delivery
message, not here: a document cannot carry its own digest or commit id without
changing them.

---

## 13. Non-claims that remain open after this report

* **Full global inventory acceptance is pending independent exact-report
  factual review** (an OpenAI reviewer checks the exact report commit and the
  remaining disposition). This report is the author's submission, not its
  acceptance.
* No feature is qualified; no level is promoted, demoted or capped; no target
  is changed; no finding is closed; no obligation is deleted; no MVP scope is
  set or narrowed; no completion percentage is claimed.
* The three Tron paused-frame owner approvals closed on 2026-10-20 stay closed
  and are not reopened, extended or treated as released.
* Physical measurement, physical CEC, the 72-hour soak, a week of use, final
  matching versions/artifacts and release authority remain owner gates.
* The `SW-AUDIT-01` **parent unit** is not closed by this report: the
  dispositions are mapped, but the P1 review/admission/integration chain, the
  new assertions named in §6.1 and §8, and the owner gates still have to be
  executed and independently reviewed.

*Report-only child of `SW-AUDIT-01`. The 268 feature dispositions are mapped;
no feature, unit, package, candidate or artefact is qualified or accepted by
this document.*
