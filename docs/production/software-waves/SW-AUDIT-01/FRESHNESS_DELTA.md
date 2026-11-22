# SW-AUDIT-01 — ledger freshness delta: what changed between the two committed ledgers and why

**Child scope:** explain the regenerated feature ledger. This document does **not**
complete the global 268-feature inventory, does not qualify any feature, does not
promote or demote any level, and does not close any finding. Primary feature
owners are unchanged by this child.

| Field | Value |
| --- | --- |
| Task / Dispatch | `task_02c22e77963a` / `ctx_e973d4be3c60` |
| Run | `run_37205f6095b3` (existing Run; not reset or replaced) |
| Worker terminal | `term_ba1c0350-0193-49cb-80d3-019fdcfd3dda` |
| Coordinator terminal | `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662` |
| Worktree | `wp-audit-freshness-delta` (dedicated, Windows Orca) |
| Branch | `ryan-haver/wp-audit-freshness-delta` |
| Exact base | `d6e78e0b6ab1dab5216443584d810a7a24af32b2` |
| Report written (UTC) | `2026-10-28T23:36Z` |
| Report-only | yes — one new file; no source, test, registry, ledger, record, manifest, lock or runtime change |

---

## 1. Exact inputs (byte sources, read-only)

Two committed `docs/validation/LEDGER.md` blobs are the only ledger inputs. Nothing
was regenerated, imported, re-targeted or rewritten.

| Ledger | Blob commit | Bytes | SHA-256 of blob | Generation `HEAD` in its header |
| --- | --- | ---: | --- | --- |
| old | `28fce729ca4ea08bfc2f19805b36e13ae8c184f2` | 74 831 | `41d81dae99566b01c15b4ada2eeff67ec2c87065a312b16a8c8bd4f8071aecce` | `141bffb2` |
| new | `d6e78e0b6ab1dab5216443584d810a7a24af32b2` | 74 447 | `b8078e4d45be717c88f7f138c34a60d45a3ad118e1051e30f5da8a8c88c25cf7` | `28fce729` |

Both blobs are clean UTF-8. `tools/validate/ledger.py` at `d6e78e0b` emits U+2014
(em dash) for an empty table cell and U+00B7 (middle dot) as the link separator, so
the committed files are intact; the earlier mojibake seen in a terminal was a
PowerShell redirection artefact, not a repository defect (§8, attempt 1).

### 1.1 The record set each ledger was generated from

`tools/validate/ledger.py` reads the **working tree**
(`docs/validation/evidence`), not git. The record set that produced a committed
`LEDGER.md` is therefore the evidence tree of the commit that *carries* that
`LEDGER.md`, while freshness is evaluated against the `HEAD` recorded in the
ledger header. Using one record set for both ledgers is wrong and does not
reproduce the committed numbers.

| Ledger | `LEDGER.md` carried by | Evidence tree (record set) | Records | Features with records |
| --- | --- | --- | ---: | ---: |
| old | `94b76fe1` (parent `141bffb2`) | `94b76fe1` | 2 087 | 165 |
| new | `78ce3448` (parent `28fce729`) | `78ce3448` | 2 131 | 166 |

`94b76fe1` and `78ce3448` are the last commits that touched `docs/validation/LEDGER.md`
at `28fce729` and `d6e78e0b` respectively (`git log -1 <rev> -- docs/validation/LEDGER.md`).

---

## 2. Method and method verification

1. Extracted both ledger blobs byte-exactly with `git cat-file blob` (no shell
   redirection) and parsed all **268 feature rows** from each.
2. Diffed the parsed rows per feature across the columns that can change:
   `level`, `recorded`, `target`, `freshness`, `capped`, `open_findings`, and the
   displayed evidence links. **54 of 268 rows changed; the other 214 are identical
   in every compared column.**
3. Re-implemented `tools/validate/ledger.py`'s `freshness()` and `compute()` logic
   read-only — including the rule that the **record's own `covers` list** is
   authoritative (not the live scenario registry), that `dirty_files` force stale,
   that a commit which is not an ancestor yields `unknown`, and that `matches()`
   treats a cover entry as a path prefix or an `fnmatch` glob.
4. Replayed it over both record sets at both generation `HEAD`s and compared the
   result to the two committed ledgers row by row.

**Method verification result: 0 freshness mismatches across all 268 rows of both
ledgers, and stale counts reproduced exactly as 57 (old) and 96 (new).**
This is a verification of the *parser and the attribution arithmetic* against
committed bytes. It is **not** a canonical ledger regeneration: no ledger command
was run, nothing was written to `docs/validation/`, and the committed
`docs/validation/LEDGER.md` at `d6e78e0b` is untouched.

### 2.1 The freshness window

Freshness is evaluated between a record's source commit and the ledger's
generation `HEAD`. The window that separates the two ledgers is therefore
`141bffb2..28fce729` — 31 commits, **111 changed paths**:

| Class | Paths |
| --- | --- |
| Non-`docs/` (11) | `.gitattributes`, `AGENTS.md`, `src/rest_api/control.py`, `tests/sim/test_sim_offline_switch_events.py`, `tests/sim/test_sim_rest_reads.py`, `tests/validation/scenarios/sw_api_read_04.py`, `tests/validation/test_sw_api_read_04.py`, `tools/validate/clients/api.py`, `tools/validate/model.py`, `tools/validate/runner.py`, `tools/validate/stack.py` |
| `docs/` (100) | documentation and planning files only |

`tests/validation/scenarios/_paths.py` did **not** change in the window, so every
scenario's `covers` definition is identical at both ends; only the newly added
`tests/validation/scenarios/sw_api_read_04.py` differs.

---

## 3. Totals, reconciled honestly

Recomputed from the parsed rows and identical to the committed summary rows.

| Measure | old (`141bffb2`) | new (`28fce729`) | Delta |
| --- | ---: | ---: | ---: |
| Features | 268 | 268 | 0 |
| Below target | 203 | 210 | **+7** |
| Stale evidence | 57 | 96 | **+39** |
| Fresh evidence | 108 | 70 | −38 |
| No evidence record | 103 | 102 | −1 |
| Level changes | — | — | **15** |
| Target changes | — | — | **0** |
| Capped at V1 by an open critical/high finding | 12 | 12 | 0 (same set) |

### 3.1 The +7 and the +39 are the same 39 rows

* **Stale +39** is exactly the **39 rows that moved `fresh → stale`**. No row moved
  `stale → fresh`, `stale → none` or `none → stale`.
* **Below target +7** = **8 rows newly below target** − **1 row no longer below
  target**:
  * newly below target (8): `F-API-008`, `F-API-013`, `F-DOM-026`, `F-FLIC-001`,
    `F-FLIC-002`, `F-FLIC-008`, `F-UI-004`, `F-UI-005`;
  * no longer below target (1): `F-API-031` (V1 → V2 against a V2 target).
* **Fresh −38** = −39 (the flips) + 1 (`F-API-031` gained a fresh record).
* **No-record −1** = `F-API-031` (had no record, now has 26).
* **Level changes 15** = 14 level drops caused by staleness (the level falls back to
  the registry's recorded baseline when no fresh passing evidence remains) + the
  `F-API-031` recorded-level change V1 → V2.
* **Target changes 0.** No target was lowered, and no evidence was retired.

---

## 4. Cause classification — four distinct things, not one

The 54 changed rows fall into four mechanically distinct causes. They must not be
read as one "39-feature regression".

### Class A — already-merged source freshness effect (39 rows)

`src/rest_api/control.py` changed twice inside the window:

| Commit | Date | Subject |
| --- | --- | --- |
| `64e10a16` | 2026-10-20 | `fix(rest): emit switch_failed/switch_all_failed for unavailable routes` |
| `3788353e` | 2026-10-20 | `fix(rest): keep 503 for oversized bodies on unavailable routes` |

`src/rest_api/control.py` is in the `covers` list of the `CONTROL` path group, so
every record whose scenario covers `CONTROL` is stale once those commits land.
All 39 flipped rows have exactly this cause — the covered-path change is
`src/rest_api/control.py` in every one of them, and no other covered path
changed for any of them.

**This is not a reproduced functional defect.** `64e10a16`/`3788353e` are the
*correction* of the one genuine defect in this window (VAL-14, §4.4), already
independently reviewed at `0bd3d76f` and recorded in
`docs/production/software-waves/SW-API-CLIENT-02-C1/`. The ledger is behaving
correctly: evidence captured before the corrected source is now, by the registry's
own freshness rule, no longer fresh. Absence and staleness establish no new bug.
The historical failed CI record under
`docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci` is untouched
and was not imported as accepted feature evidence.

The rows that lost a proven level did so by falling back to the recorded baseline
(`F-API-008` V2→V1, `F-API-013` V3→V1, `F-DOM-026` V3→V2, `F-DOM-034` V2→V1,
`F-FLIC-001` V3→V1, `F-FLIC-002` V3→V1, `F-FLIC-008` V3→V0, `F-MTX-004` V2→V1,
`F-MTX-021` V3→V1, `F-MTX-030` V2→V1, `F-REL-001` V3→V0, `F-REL-005` V3→V0,
`F-UI-004` V3→V1, `F-UI-005` V3→V1). This is the registry's recorded baseline
speaking, not a level reduction applied by this child.

### Class B — newly accepted CORS V2 (1 row: `F-API-031`)

`F-API-031` ("CORS headers") had **no evidence record at all** in the old ledger
(freshness `—`, recorded V1, level V1, below its V2 target). In the new ledger it
is **fresh at V2**, recorded V2, level V2, at target.

Cause: 26 accepted records were added under
`docs/validation/evidence/software-waves/W03-CLOSEOUT-20261028/` (13
`original-cors` at source `7b07e1cb`, 13 `combined/cors` at source `310d8b65`),
and the registry `current` was raised V1 → V2 with the matching `basis` and
`evidence` list. This is the **accepted CORS V2** qualification from package
`SW-API-READ-04` / unit `SW-API-READ-04-C1`, independently reviewed at `29c217ae`.
It is an accepted qualification, not a defect and not a promotion by this child.

### Class C — named auth / root refresh (2 rows: `F-SEC-007`, `F-API-002`)

* `F-SEC-007` ("Wrong-PIN attempts are limited and do not stall the hub"): recorded
  V1 → V3 with a full V3 basis and evidence list, plus 14 fresh `combined/auth`
  records at `310d8b65` (6 API V2 + 8 browser V3). Owner `SW-SEC-AUTH` /
  `SW-SEC-AUTH-01` (`docs/production/software-waves/SW-SEC-AUTH-01/`). Its own row
  is unchanged in level and freshness; only the displayed evidence set changed.
* `F-API-002` ("API info and root"): 2 of its 4 fresh-at-old-head records
  (`contracts.api_root`, `contracts.api_root_alias` at source `2ae46e6c`, the
  `SW-SEC-AUTH-01-api-refresh` set) went stale, because the CORS package's leased
  tooling covers changed — `tools/validate/clients/api.py`, `tools/validate/model.py`,
  `tools/validate/runner.py`, `tools/validate/stack.py` at `7b07e1cb`, and
  `tests/sim/test_sim_rest_reads.py` at `64e10a16`. Its level **stays V2** and it
  stays **fresh**, because the three `combined/api-root` records at `310d8b65`
  (which postdate the tooling change) still prove it. The stale pair is retained
  with its original source attribution, as the registry intends.

This is a tooling-covers effect of an accepted refresh, not a defect and not a
source relabel.

### Class D — the one actual reproduced functional defect (already corrected)

**VAL-14** ("Already-disconnected routing requests omitted documented failure
events", severity M, location `src/rest_api/control.py`) was raised by
`SW-API-CLIENT-02-C1`, reproduced with a real offline probe, corrected in source
at `64e10a16`/`3788353e`, independently reviewed at `0bd3d76f`, and registered in
the registry at `78ce3448`. It is now linked to `F-API-033`, `F-API-034` and
`F-REL-009`.

* **VAL-14 is severity M, so it does not cap any level** (only open critical/high
  findings cap at V1). The capped set is unchanged: the same 12 features, all
  capped by `HIL-09(C)`, before and after. The new links changed no level.
* `F-API-033` and `F-REL-009` keep a fresh `failures.unreachable_switch` record at
  `310d8b65`, which postdates the correction.
* `F-API-034` is the row where the correction's **all-output** boundary is not yet
  proven by any scenario — see §6.

**VAL-15** ("Validation request artifacts and action descriptions do not redact
X-Admin-PIN", severity M, location `tools/validate/evidence.py` and
`tools/validate/model.py`) was linked to `F-SEC-014` at `78ce3448`. `F-SEC-014` has
no evidence record on either side (freshness `—` before and after); only its
finding link changed. VAL-15's own corrective package `SW-SEC-DATA-02-C1` is
separately owned and, per `docs/validation/findings_pending.yaml`, remains
undispatched. That is not a delta item.

### Class E — displayed-evidence-set-only changes (9 rows)

`F-API-032`, `F-CEC-005`, `F-FLIC-009`, `F-FLIC-010`, `F-MTX-001`, `F-MTX-003`,
`F-MTX-006`, `F-MTX-007`, `F-MTX-031` changed **only** in the evidence column.
Their level, recorded baseline, target, freshness and findings are unchanged.
Their previously-fresh `1baac3de` records are now stale (Class A), so the ledger
now displays a different — still stale — record. The rows keep a fresh record, so
their disposition is unchanged. `F-MTX-007` remains `V1 (capped)` by `HIL-09(C)` in
both ledgers.

---

## 5. Changed-feature table

### 5.1 Table A — the 39 rows that moved `fresh → stale` (Class A)

All 39 share one cause: `src/rest_api/control.py` @ `64e10a16`, `3788353e`.

| Feature | Old → New (level / freshness) | Cause (covered path @ commit) | Original fresh record (sha client level scenario) | Owner package / unit | Disposition |
| --- | --- | --- | --- | --- | --- |
| `F-API-005` | V2 → V2 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `routing.switch_one`; `1baac3de` api V2 `routing.route_all` | SW-API-CLIENT / SW-API-CLIENT-01 | rerun |
| `F-API-007` | V2 → V2 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `presets.recall` | SW-API-CLIENT / SW-API-CLIENT-01 | rerun |
| `F-API-008` | **V2** → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `preset_read.saved_partial_1..8`; `1baac3de` api V2 `preset_read.saved_current_1..8` | SW-API-WRITE / SW-API-WRITE-01 | rerun |
| `F-API-013` | **V3** → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `reboot.enabled_shortcut`; `1baac3de` browser V3 `reboot.enabled_shortcut` | SW-API-WRITE / SW-API-WRITE-01 | rerun |
| `F-API-034` | V2 → V2 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `routing.route_all` | SW-API-CLIENT / SW-API-CLIENT-02 | **assertion-gap** (§6) |
| `F-API-035` | V2 → V2 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `presets.recall` | SW-API-CLIENT / SW-API-CLIENT-02 | rerun |
| `F-DOM-026` | **V3** → V2 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `shortcuts.preset_recall`; `1baac3de` browser V3 `shortcuts.preset_recall` | SW-DOM-SHORTCUT / SW-DOM-SHORTCUT-01 | rerun |
| `F-DOM-034` | V2 → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `preset_read.saved_partial_1..8`; `1baac3de` api V2 `preset_read.saved_current_1..8` | SW-DOM-PRESENT / SW-DOM-PRESENT-01 | rerun |
| `F-FLIC-001` | **V3** → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` flic V3 `flic.preset` | SW-FLIC / SW-FLIC-01 | rerun |
| `F-FLIC-002` | **V3** → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` flic V3 `flic.power_off`; `1baac3de` flic V3 `flic.power_on` | SW-FLIC / SW-FLIC-01 | rerun |
| `F-FLIC-008` | **V3** → V0 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` flic V3 `flic.all_outputs` | SW-FLIC / SW-FLIC-02 | rerun |
| `F-HA-001` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.config_flow` | SW-HA-PREP / SW-HA-PREP-01 | rerun |
| `F-HA-002` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.front_panel_route`; `1baac3de` ha V3 `ha.select_source` | SW-HA-PREP / SW-HA-PREP-01 | rerun |
| `F-HA-003` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.power_off`; `1baac3de` ha V3 `ha.power_on` | SW-HA-PREP / SW-HA-PREP-01 | rerun |
| `F-HA-004` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.mute_switch` | SW-HA-PREP / SW-HA-PREP-01 | rerun |
| `F-HA-005` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.stream_switch` | SW-HA-PREP / SW-HA-PREP-01 | rerun |
| `F-HA-006` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.preset_button` | SW-HA-PREP / SW-HA-PREP-01 | rerun |
| `F-HA-007` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.reboot_button` | SW-HA-PREP / SW-HA-PREP-02 | rerun |
| `F-HA-008` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.input_signal` | SW-HA-PREP / SW-HA-PREP-02 | rerun |
| `F-HA-009` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.display_unplugged` | SW-HA-PREP / SW-HA-PREP-02 | rerun |
| `F-HA-010` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.service_recall_preset` | SW-HA-PREP / SW-HA-PREP-02 | rerun |
| `F-HA-011` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.service_switch_input` | SW-HA-PREP / SW-HA-PREP-02 | rerun |
| `F-HA-012` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.service_cec_display`; `1baac3de` ha V3 `ha.service_cec_invalid`; `1baac3de` ha V3 `ha.service_cec_source` | SW-HA-PREP / SW-HA-PREP-02 | rerun |
| `F-HA-013` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.front_panel_route`; `ha.input_signal`; `ha.display_unplugged`; `ha.matrix_offline`; `ha.matrix_unreachable` | SW-HA-PREP / SW-HA-PREP-03 | rerun |
| `F-HA-015` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.config_flow` | SW-HA-PREP / SW-HA-PREP-03 | rerun |
| `F-HA-016` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.reconfigure` | SW-HA-PREP / SW-HA-PREP-03 | rerun |
| `F-HA-017` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.config_flow` | SW-HA-PREP / SW-HA-PREP-03 | rerun |
| `F-HA-018` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` ha V3 `ha.service_recall_preset`; `1baac3de` ha V3 `ha.service_switch_input` | SW-HA-PREP / SW-HA-PREP-03 | rerun |
| `F-KIO-002` | **V3** → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` browser V3 `kiosk.route_one_muted` | SW-KIOSK-CONTROL / SW-KIOSK-CONTROL-01 | rerun |
| `F-KIO-003` | **V3** → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` browser V3 `kiosk.route_all_apply` | SW-KIOSK-CONTROL / SW-KIOSK-CONTROL-01 | rerun |
| `F-MTX-002` | V3 → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `routing.route_all`; `1baac3de` browser V3 `routing.route_all` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-01 | rerun |
| `F-MTX-004` | V2 → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `preset_read.saved_current_1..8` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-01 | rerun |
| `F-MTX-021` | V3 → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `reboot.enabled_shortcut`; `1baac3de` browser V3 `reboot.enabled_shortcut` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-04 | rerun |
| `F-MTX-030` | V2 → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `preset_read.catalog_matches_device`; `1baac3de` api V2 `preset_read.device_slot_1..8` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-05 | rerun |
| `F-REL-001` | V3 → V0 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `reboot.enabled_shortcut`; `1baac3de` browser V3 `reboot.enabled_shortcut` | SW-RUNTIME-PREP / SW-RUNTIME-PREP-04 | rerun |
| `F-REL-005` | V3 → V0 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` api V2 `reboot.enabled_shortcut`; `1baac3de` browser V3 `reboot.enabled_shortcut` | SW-RUNTIME-PREP / SW-RUNTIME-PREP-05 | rerun |
| `F-UI-002` | **V3** → V3 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` browser V3 `routing.switch_one` | SW-UI-CONTROL / SW-UI-CONTROL-01 | rerun |
| `F-UI-004` | **V3** → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` browser V3 `routing.route_all` | SW-UI-CONTROL / SW-UI-CONTROL-01 | rerun |
| `F-UI-005` | **V3** → V1 / fresh → stale | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | `1baac3de` browser V3 `presets.recall` | SW-UI-CONTROL / SW-UI-CONTROL-01 | rerun |

`V3 → V3` and `**V3** → V3` rows kept their level because their recorded baseline
already equals the level they had proven; only the freshness label moved.

### 5.2 Table B — the 15 rows that changed for another reason

| Feature | What changed | Old → New | Cause | Owner package / unit | Disposition |
| --- | --- | --- | --- | --- | --- |
| `F-API-002` | displayed evidence set only | level V2 → V2; freshness fresh → fresh | covered paths `tools/validate/{clients/api.py,model.py,runner.py,stack.py}` @ `7b07e1cb`; `tests/sim/test_sim_rest_reads.py` @ `64e10a16` (2 of 4 fresh-at-old-head records went stale; 3 `combined/api-root` records at `310d8b65` keep it fresh) | SW-API-READ / SW-API-READ-01 | preserve |
| `F-API-031` | freshness + level + recorded + evidence links | level V1 → **V2**; recorded V1 → V2; freshness — → fresh | 26 accepted CORS V2 records (13 `original-cors` @ `7b07e1cb`, 13 `combined/cors` @ `310d8b65`) + registry `current` V1 → V2 at `78ce3448`; no changed covered path | SW-API-READ / SW-API-READ-04 | preserve |
| `F-API-032` | displayed evidence set only | level V3 → V3; freshness fresh → fresh | `src/rest_api/control.py` @ `64e10a16`, `3788353e` (one fresh record remains) | SW-API-READ / SW-API-READ-04 | preserve |
| `F-API-033` | finding link + displayed evidence set | level V2 → V2; freshness fresh → fresh; open findings — → `VAL-14(M)` | `src/rest_api/control.py` @ `64e10a16`, `3788353e`; fresh `failures.unreachable_switch` record at `310d8b65` | SW-API-CLIENT / SW-API-CLIENT-02 | preserve |
| `F-CEC-005` | displayed evidence set only | level V3 → V3; freshness fresh → fresh; findings `BE-14(M)` unchanged | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-06 | preserve |
| `F-FLIC-009` | displayed evidence set only | level V3 → V3; freshness fresh → fresh | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | SW-FLIC / SW-FLIC-02 | preserve |
| `F-FLIC-010` | displayed evidence set only | level V3 → V3; freshness fresh → fresh | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | SW-FLIC / SW-FLIC-02 | preserve |
| `F-MTX-001` | displayed evidence set only | level V3 → V3; freshness fresh → fresh | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-01 | preserve |
| `F-MTX-003` | displayed evidence set only | level V3 → V3; freshness fresh → fresh | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-01 | preserve |
| `F-MTX-006` | displayed evidence set only | level V3 → V3; freshness fresh → fresh | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-01 | preserve |
| `F-MTX-007` | displayed evidence set only | level `V1 (capped)` → `V1 (capped)`; freshness fresh → fresh; findings `HIL-09(C)` unchanged | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-02 | preserve |
| `F-MTX-031` | displayed evidence set only | level V3 → V3; freshness fresh → fresh | `src/rest_api/control.py` @ `64e10a16`, `3788353e` | SW-PROTOCOL-PREP / SW-PROTOCOL-PREP-06 | preserve |
| `F-REL-009` | finding link + displayed evidence set | level V3 → V3; freshness fresh → fresh; open findings — → `VAL-14(M)` | `src/rest_api/control.py` @ `64e10a16`, `3788353e`; fresh `failures.unreachable_switch` record at `310d8b65` | SW-RUNTIME-PREP / SW-RUNTIME-PREP-05 | preserve |
| `F-SEC-007` | displayed evidence set only | level V3 → V3; freshness fresh → fresh | covered paths `tools/validate/{clients/api.py,model.py,runner.py}` @ `7b07e1cb`; 14 fresh `combined/auth` records at `310d8b65` keep it fresh | SW-SEC-AUTH / SW-SEC-AUTH-01 | preserve |
| `F-SEC-014` | finding link only | level V1 → V1; freshness — → —; open findings — → `VAL-15(M)` | no changed covered path; registry link only | SW-SEC-DATA / SW-SEC-DATA-02 | preserve |

### 5.3 Owner roll-up

| Owner package | Dispatch unit | Changed rows | `fresh → stale` | Other change |
| --- | --- | ---: | ---: | ---: |
| SW-HA-PREP | SW-HA-PREP-01 | 6 | 6 | 0 |
| SW-HA-PREP | SW-HA-PREP-02 | 6 | 6 | 0 |
| SW-HA-PREP | SW-HA-PREP-03 | 5 | 5 | 0 |
| SW-PROTOCOL-PREP | SW-PROTOCOL-PREP-01 | 5 | 2 | 3 |
| SW-API-CLIENT | SW-API-CLIENT-02 | 3 | 2 | 1 |
| SW-FLIC | SW-FLIC-02 | 3 | 1 | 2 |
| SW-UI-CONTROL | SW-UI-CONTROL-01 | 3 | 3 | 0 |
| SW-API-CLIENT | SW-API-CLIENT-01 | 2 | 2 | 0 |
| SW-API-READ | SW-API-READ-04 | 2 | 0 | 2 |
| SW-API-WRITE | SW-API-WRITE-01 | 2 | 2 | 0 |
| SW-FLIC | SW-FLIC-01 | 2 | 2 | 0 |
| SW-KIOSK-CONTROL | SW-KIOSK-CONTROL-01 | 2 | 2 | 0 |
| SW-PROTOCOL-PREP | SW-PROTOCOL-PREP-06 | 2 | 0 | 2 |
| SW-RUNTIME-PREP | SW-RUNTIME-PREP-05 | 2 | 1 | 1 |
| SW-API-READ | SW-API-READ-01 | 1 | 0 | 1 |
| SW-DOM-PRESENT | SW-DOM-PRESENT-01 | 1 | 1 | 0 |
| SW-DOM-SHORTCUT | SW-DOM-SHORTCUT-01 | 1 | 1 | 0 |
| SW-PROTOCOL-PREP | SW-PROTOCOL-PREP-02 | 1 | 0 | 1 |
| SW-PROTOCOL-PREP | SW-PROTOCOL-PREP-04 | 1 | 1 | 0 |
| SW-PROTOCOL-PREP | SW-PROTOCOL-PREP-05 | 1 | 1 | 0 |
| SW-RUNTIME-PREP | SW-RUNTIME-PREP-04 | 1 | 1 | 0 |
| SW-SEC-AUTH | SW-SEC-AUTH-01 | 1 | 0 | 1 |
| SW-SEC-DATA | SW-SEC-DATA-02 | 1 | 0 | 1 |
| **Total** | | **54** | **39** | **15** |

---

## 6. The one assertion gap: `F-API-034` / `switch_all_failed`

`F-API-034` ("Route to all: `routing_change` per output that changed /
`switch_all_failed`", target V3) is the only row where a plain re-run cannot
restore the target.

* The corrected source **does** emit `switch_all_failed` for a valid route-to-all
  against a disconnected matrix (`src/rest_api/control.py` @ `64e10a16`).
* **No declarative scenario asserts it.** `git grep switch_all_failed` over
  `tests/validation/scenarios/` at `d6e78e0b` returns **no match**; the only
  failure-event assertion is `WsEvent("switch_failed", {"input": 3})` in
  `failures.unreachable_switch` (`tests/validation/scenarios/failures.py:25`),
  which is registered for `F-API-033` and `F-REL-009`, not for `F-API-034`.
* The registry itself records the gap in `F-API-034`'s own `basis`:
  *"switch_all_failed: V1 (sent by the handler on a refused write; no scenario
  yet)."*
* The behaviour is covered only by a **source-level simulator regression test**,
  `tests/sim/test_sim_offline_switch_events.py::test_offline_route_all_emits_switch_all_failed`
  (plus 9 sibling offline/503 tests). A source test is not a scenario and produces
  no evidence record, so it cannot raise the ledger row.

**Bounded next verification for `F-API-034`:** a declarative scenario asserting the
`switch_all_failed` event (with the `{"input": N}` payload, `503` response, no
device mutation and no routing write) on the already-disconnected all-output
path, plus a connected positive control, executed against the current source to
produce a fresh evidence record. That is a new assertion and therefore belongs to
the owning unit `SW-API-CLIENT-02` / package `SW-API-CLIENT`, not to this
report-only child. Until it exists, `F-API-034` stays at V2 and its V3 target is
unproven.

---

## 7. Archive-count reconciliation (not lost source bytes)

The evidence archive grew by 44 records between the two ledgers. This is **not** a
discrepancy and **not** a loss of source bytes:

| Measure | Value |
| --- | ---: |
| Records at `94b76fe1` | 2 087 |
| Records at `78ce3448` | 2 131 |
| Present in both | 2 087 |
| **Payload of the 2 087 common records** | **byte-identical JSON** (2 087 / 2 087) |
| **Removed** | **0** |
| Added | 44 |

The 44 added records are exactly the accepted W03 import:

| Directory | Count | Source SHA | Client / level | Features |
| --- | ---: | --- | --- | --- |
| `software-waves/W03-CLOSEOUT-20261028/original-cors/` | 13 | `7b07e1cb` | api V2 pass | `F-API-031` (13) |
| `software-waves/W03-CLOSEOUT-20261028/combined/cors/` | 13 | `310d8b65` | api V2 pass | `F-API-031` (13) |
| `software-waves/W03-CLOSEOUT-20261028/combined/api-root/` | 3 | `310d8b65` | api V2 pass | `F-API-002` (3) |
| `software-waves/W03-CLOSEOUT-20261028/combined/auth/` | 14 | `310d8b65` | api V2 (6) + browser V3 (8) pass | `F-SEC-007` (14) |
| `software-waves/W03-CLOSEOUT-20261028/combined/offline/` | 1 | `310d8b65` | api V2 pass | `F-REL-009`, `F-API-033` (1 each) |

Nothing was deleted, relabelled or re-dated. The historical failed CI record for
VAL-14 remains under `docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci`
and is **not** among the imported records. The 32 PNG artifacts and the 44 JSON
records are the 76 files the independent W03 review `29c217ae` checked byte for
byte against the read-only originals; this child did not re-verify that byte
identity (see §8 limits) and makes no new claim about it.

---

## 8. Dispositions and bounded next verification

| Disposition | Rows | What it means | Bounded next verification |
| --- | ---: | --- | --- |
| **rerun** | 38 | The row's evidence is stale solely because `src/rest_api/control.py` changed after the record. The row is not defective; it is out of date. | Re-run the same scenario + client at the current source to produce a fresh record. The exact evidence units are the `scenario / client / level / sha` triples in Table A. No new scenario, assertion, registry edit or target change is needed for these rows. |
| **assertion-gap** | 1 (`F-API-034`) | The row cannot reach its V3 target by re-running; the required assertion does not exist. | One declarative scenario asserting `switch_all_failed` (payload, 503, no mutation, no routing write) on the disconnected all-output path plus a connected control — owned by `SW-API-CLIENT-02`, needs the normal different-family review of any new scenario or test. |
| **preserve** | 15 | The row's disposition is unchanged or is an accepted qualification already independently reviewed. Nothing to redo for the delta. | None for the delta. `F-API-031`'s CORS V2 acceptance is already independently reviewed at `29c217ae`; `F-SEC-007`'s auth/root refresh is owned by `SW-SEC-AUTH-01`; `F-SEC-014`'s `VAL-15` corrective package `SW-SEC-DATA-02-C1` is separately owned and undispatched. |
| **needs-investigation** | 0 | — | — |

**No cause is unknown.** For every one of the 54 changed rows the covered-path
change, the commits that made it and the owning package/unit were identified from
committed bytes. Where a row's *owner* is a planning allocation rather than a
committed package, that is stated as such (`SW-PROTOCOL-PREP` and
`SW-RUNTIME-PREP` rows are `physical_preparation_only` scope in the manifest; their
software-preparation owner is unchanged by this child).

### 8.1 The minimal re-run set

The 38 `rerun` rows need **60 distinct `(scenario, client, level)` evidence units**
re-run, drawn from **55 distinct scenarios** — far fewer than 38 feature runs,
because several records serve several features. Every one of them comes from the
single `1baac3de` runtime campaign (`evidence/runtime-r8b/…`); the two `2ae46e6c`
records that also went stale (`contracts.api_root`, `contracts.api_root_alias`)
belong to `F-API-002`, a `preserve` row, and are listed in Table B instead.

| Scenario / client / level | Features served |
| --- | ---: |
| `reboot.enabled_shortcut` api V2 | 4 (`F-API-013`, `F-MTX-021`, `F-REL-001`, `F-REL-005`) |
| `reboot.enabled_shortcut` browser V3 | 4 (same four) |
| `ha.config_flow` ha V3 | 3 (`F-HA-001`, `F-HA-015`, `F-HA-017`) |
| `routing.route_all` api V2 | 3 (`F-API-005`, `F-API-034`, `F-MTX-002`) |
| `preset_read.saved_current_1..8` api V2 | 2 each (`F-API-008`, `F-MTX-004`) |
| `preset_read.saved_partial_1..8` api V2 | 2 each (`F-API-008`, `F-DOM-034`) |
| `ha.display_unplugged`, `ha.front_panel_route`, `ha.input_signal` ha V3 | 2 each (each with `F-HA-013`) |
| `ha.service_recall_preset`, `ha.service_switch_input` ha V3 | 2 each (each with `F-HA-018`) |
| `presets.recall` api V2 | 2 (`F-API-007`, `F-API-035`) |
| `routing.route_all` browser V3 | 2 (`F-MTX-002`, `F-UI-004`) |
| the remaining 33 units | 1 each |

The 55 scenarios break down as 25 `preset_read.*` (31 `preset_read`/`routing`/
`presets` units in total, since `routing.route_all`, `routing.switch_one` and
`presets.recall` each run for two clients), 19 `ha.*`, 4 `flic.*`, 2 `kiosk.*`,
1 `shortcuts.preset_recall` and 1 `reboot.enabled_shortcut`. Client mix: `api`,
`browser`, `flic`, `ha`.

### 8.2 What this child did **not** do

* No ledger generation, no `python -m tools.validate ledger`, no registry edit, no
  record import, no file removal, no push, no merge, no tag, no service launch.
* No feature promotion, no target reduction, no evidence retirement, no baseline
  promotion, no finding close, no source relabel, no fabricated timestamp. The
  `F-API-031` V1 → V2 change and the `VAL-14`/`VAL-15` links are pre-existing
  accepted registry edits at `78ce3448`, reported here, not made here.
* No new test, scenario, fixture or production tooling.
* No completion of the global 268-feature inventory: 214 rows are unchanged
  between the two ledgers, and their qualification state is unchanged and
  unreviewed by this child. **This report does not mean parent `SW-AUDIT-01` is
  complete.**

---

## 9. Limits, failed attempts and unknowns

**Method limits.**

* The freshness reproduction is a *verification* of the parser and the attribution
  arithmetic against committed bytes, not a canonical regeneration. No ledger
  command was run and no canonical artifact was written.
* Only the 268 ledger rows and the records behind them were examined. The 214
  unchanged rows were diffed, not re-qualified.
* `git diff --name-only <sha>..<head>` was used for staleness, exactly as
  `tools/validate/gitinfo.changed_since` does; a record whose source commit is not
  an ancestor yields `unknown`, and no row in either ledger depends on an
  `unknown` freshness value.

**Unknowns, stated as unknown.**

* The byte identity of the 44 imported W03 records against the read-only
  originals was **not** re-verified here; that verification belongs to the
  independent review `29c217ae` and its manifest. This child verified only that
  the 2 087 common records are payload-identical across the two trees and that 44
  records were added and none removed.
* The manifest's per-feature `ledger_snapshot` is **dated planning data**
  (`observed_utc` 2026-10-20, `baseline_sha` 97e617c2) and matches the *old*
  ledger, not the current one. It was used only for the package/unit ownership
  mapping; it is not treated as current qualification.
* Whether the 39 stale rows' *new* evidence will pass at the current source is
  **not** known. Staleness says only that the evidence predates the change; it
  establishes no defect and no pass. The re-run in §8.1 is what would settle it.
* `F-API-031`'s CORS V2 acceptance, `F-SEC-007`'s auth/root refresh and
  VAL-14's source correction are reported as **accepted** on the strength of the
  committed independent reviews (`29c217ae`, `SW-SEC-AUTH-01/REVIEW.md`,
  `SW-API-CLIENT-02-C1/REVIEW.md`). This child did not re-run their checks.

**Failed / limited diagnostic attempts (preserved separately in
`build/software-waves/SW-AUDIT-01-freshness-delta/`).**

| # | Attempt | Outcome | Handling |
| ---: | --- | --- | --- |
| 1 | `git show <rev>:docs/validation/LEDGER.md > file` via the shell | exit 0, but the redirection mangled every non-ASCII character (U+2014/U+00B7 became U+FFFD); the parse then found 0 feature rows | Superseded by `extract_ledgers.py` (`git cat-file blob`, byte-exact). The mangled first-pass files were replaced; the byte-exact SHA-256 values in §1 are from the `git cat-file` blobs. |
| 2 | `parse_ledger.py` area regex `[a-z0-9\-]+` | exit 0 but 0 rows parsed — area codes are uppercase (`F-MTX`) | Regex fixed to `[A-Za-z0-9\-]+`; re-run parsed 268/268. |
| 3 | `dump_covers.py` importing `tools.validate.scenarios` | exit 1, `ModuleNotFoundError: No module named 'tools'` (script directory on `sys.path`, repo root not) | `sys.path.insert(0, repo_root)` added; re-run exit 0, 1 507 scenarios. |
| 4 | `python -c "... | ..."` with a pipe inside the double-quoted argument | exit 1, PowerShell `ScriptBlock should only be specified as a value of the Command parameter` | Replaced by script files for all subsequent analysis. |
| 5 | First attribution pass used the **live scenario registry** for `covers` | 16 freshness mismatches (14 `F-OPS-*`, `F-API-031`, `F-API-033`) | The ledger uses the **record's own** `covers`; corrected, mismatches fell to 2, then to 0 after the record-set correction in §1.1. |
| 6 | Attribution using the `28fce729` record set for both ledgers | 2 mismatches (`F-API-031`, `F-API-033`) | Corrected to the distinct record sets (`94b76fe1` / `78ce3448`), per §1.1. This is exactly the trap the coordinator flagged; the counterfactual was **not** reported as the current ledger. |
| 7 | Background run of `attribute_delta.py` piped to `Select-Object -First 20` | the truncating pipe closed the upstream pipeline before Python flushed its block-buffered stdout: 0 bytes captured and the output file was never written | Re-run without the truncating pipe and with explicit flushing; completed with **0 freshness mismatches** and exact stale counts 57 / 96. |
| 8 | Cause grouping over *all* changed paths rather than window-changed paths | grouped 54 features into one over-broad cause set | Restricted to paths changed inside `141bffb2..28fce729`; the grouping became `src/rest_api/control.py` (50 rows), the CORS tooling covers (`F-API-002`, `F-SEC-007`) and two rows with no changed covered path (`F-API-031`, `F-SEC-014`). |

**Commands and exits actually observed** (abridged; all in the worktree, all
read-only):

| Command | Exit | Result |
| --- | ---: | --- |
| `git rev-parse HEAD` | 0 | `d6e78e0b6ab1dab5216443584d810a7a24af32b2` |
| `git status --porcelain=v1` | 0 | empty before writing this report |
| `git merge-base --is-ancestor 141bffb2 28fce729` | 0 | `141bffb2` is an ancestor of `28fce729` |
| `git log --oneline 141bffb2..28fce729` | 0 | 31 commits; window = 111 changed paths |
| `git diff --name-only 141bffb2..28fce729 -- src/rest_api/control.py` | 1 | file differs in the window (the expected non-zero for "differs") |
| `git cat-file blob <rev>:docs/validation/LEDGER.md` (×2) | 0 | byte-exact blobs; SHA-256 in §1 |
| `git ls-tree -r --name-only <rev> -- docs/validation/evidence` (×2) | 0 | 2 087 / 2 131 records after schema filtering |
| `git log -1 --format=... <rev> -- docs/validation/LEDGER.md` (×2) | 0 | `94b76fe1` / `78ce3448` carry the ledgers |
| `git grep -n switch_all_failed d6e78e0b -- .` | 0 | 38 hits (docs, manifest, source test, package records) — **0** hits in `tests/validation/scenarios/` |
| `git diff -U0 141bffb2..28fce729 -- docs/validation/features.yaml` | 0 | 5 hunks / 3 feature blocks (F-API-002, F-API-031, F-SEC-007) |
| `git diff -U0 28fce729..78ce3448 -- docs/validation/features.yaml` | 0 | 23 hunks / 18 feature blocks (F-API-031 `current` V1→V2, VAL-14/VAL-15 links, § encoding) |
| `python build/.../parse_ledger.py` | 0 | 268/268 rows parsed per ledger |
| `python build/.../classify_delta.py` | 0 | 54 changed rows; 39 fresh→stale; 15 level changes |
| `python build/.../reconcile.py` | 0 | 203→210 below (+7 = +8 −1); 57→96 stale (+39) |
| `python build/.../attribute_delta.py` | 0 | **0 freshness mismatches** vs both committed ledgers; stale 57 / 96 |
| `python build/.../final_attribution.py` | 0 | per-feature cause + owner + disposition for 54 rows |
| `python build/.../archive_delta.py` | 0 | +44 added, 0 removed, 2 087/2 087 payload-identical |
| `python -m tools.validate ledger` | **not run** | deliberately not run: no canonical regeneration in this child |
| full test / core / CI / image suite | **not run** | zero source, test, scenario, fixture or tooling bytes changed by this child |

**Local working artifacts** (all under the ignored `build/software-waves/SW-AUDIT-01-freshness-delta/`
directory; not part of the commit): `ledger_old.md`, `ledger_new.md` (byte-exact
ledger blobs), `parsed.json`, `delta.json`, `records_94b76fe1.json`,
`records_78ce3448.json`, `scenario_covers.json`, `attribution.json`,
`final_attribution.json`, `detail.txt`, `tables.md`, `reconcile.txt`, and the
analysis scripts. `records_*.json` are large (≈70 MB each) because evidence
records carry full observation payloads.

---

## 10. Attributed input and independence

* The completed generated-ledger comparison from the immutable independent W03
  review `29c217ae25856f91d79a85064eb7e38a6aa197a0` — 39 fresh→stale flips and
  `F-API-031` newly fresh — was used as **attributed input** and is consistent with
  this child's independent per-row arithmetic (39 / 1 / 15 level changes).
* This child did **not** repeat that review's interrupted optional four-world
  scans and did not re-run its checks. Its new value is the per-changed-feature
  mapping to the responsible existing package/unit and the bounded next
  verification.
* No Anthropic model, helper, nested agent, broker, MCP server, plugin or global
  provider setting was used or changed. No fallback model was needed.
* No handoff or source lease was granted by this child. Any source, scenario,
  shared-contract or registry correction (including the `F-API-034` assertion in
  §6) requires a separate dispatch and a qualified different-family review.

---

*Report-only child of `SW-AUDIT-01`. Primary feature owners unchanged. This report
explains a regenerated ledger; it does not complete the global 268-feature
inventory and does not qualify any feature.*
