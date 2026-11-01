# F-SEC-007 evidence-level gate — bounded metadata/input diagnosis

**Original diagnosis (authored and preserved).** Task `task_f441e3251dbd` ·
Dispatch `ctx_341e35be5290` · Run `run_37205f6095b3` · branch
`ryan-haver/wp-api-read-03-c1` · frozen entry
`7294af5e39a5225d61f5b1b9961bf6976d9bc904`; committed as
`d9273a0385f6534b7c8e75b6fd8b5fafce14cb29`.

**This revision (bounded metadata correction).** Task `task_3dabf0d8d5be` ·
Dispatch `ctx_dd26ee86926f` · Run `run_37205f6095b3` · branch
`ryan-haver/wp-api-read-03-c1` · correction base
`d9273a0385f6534b7c8e75b6fd8b5fafce14cb29`. The original report bytes at
`d9273a03` are preserved unchanged outside this worktree; only this tracked
file was edited. The correction scope, the coordinator-established findings it
applies and the receipt index are in §9.1, §10.1 and §11.

**Scope.** A bounded, read-only metadata/input audit of the failed F-SEC-007
evidence-level gate. This is **not** a source/security review, **not** a new
phase, **not** a CLI gate rerun, **not** a qualification, **not** an original
log, **not** a ledger generation, and **not** an admission of raw evidence. No
implementation, test or tooling was committed. Only this report is new; all
diagnostic computation is a read-only library calculation whose output is kept
in the ignored private tree
`build/software-waves/SW-API-READ-03-C1/diagnosis-20261031/`.

**Scope of this revision.** A **metadata-only correction** of the report above
after an independent coordinator fact-check. It stays **metadata only**: it is
still **not** a source/security review, still **not** a behavioural or security
verdict, and it commits **no** implementation, test or tooling. **No fresh
validation run happened** in this revision — no scenario was executed, no
browser was driven, no gate was re-run. The original diagnostics, the original
global gate and the original campaign were **not** re-run and **not**
modified. This revision adds no feature, parent-unit, F-API-040, VAL-15,
global-review, admission or release closure, and it changes none of the
source, client or level limitations recorded below.

## 1. Answer in brief

The gate failure is **established by comparison, not inferred**:

* **Established cause.** Commit `5331d547` modified `tools/validate/runner.py`.
  All 24 committed `sw_sec_auth_01.*` records declare `tools/validate/runner.py`
  inside their `covers`, so the ledger's freshness rule marks every one of them
  stale. The only F-SEC-007 records that stay fresh are the four
  `security_hardening.*` API V2 records, whose `covers` do not include the
  tooling. Because the ledger sets a feature's level to the highest level among
  *fresh passing* records, the surviving fresh set is V2 only and the row falls
  below its recorded V3 baseline → `(b) F-SEC-007 dropped below its recorded
  level: level V2 < recorded V3`.
* **How many records actually changed state.** The frozen base already carried
  **12 stale** F-SEC-007 records (§6 table); `5331d547` makes **12 records
  newly stale**. **All 24** `sw_sec_auth_01.*` records are stale afterwards,
  but **12 of them were already stale before `5331d547`** — so the 24 stale
  records after the commit are **not** 24 fresh→stale transitions. Exactly 12
  records transition fresh→stale, and those 12 are precisely the ones whose
  only cover match is `tools/validate/runner.py`.
* **What this audit does *not* establish.** This is a **metadata and
  bookkeeping** audit, not an executed behavioural or security verdict.
  `fresh_fail = 0` is read from the `result` fields of the **existing**
  records, not from a newly executed run, and the `5331d547` runner change is
  **not entered** by the action intents of these scenarios (§6) — a
  code-reading result, not a re-execution. No broad no-regression claim and no
  global security approval are made here.
* **Not a rules defect, and not input/mapping selection.** The rule behaved as
  written; the committed `covers` are over-broad relative to what a
  validation-tooling eligibility exception can affect, but that is a
  **cover-granularity** observation, not a rule defect. **No implementation
  defect in the freshness rules is established by this audit.**
* **Consequently:** *fresh browser proof is required, and it has **not** been
  executed.* No implementation correction is called for by this audit, and this
  report closes no feature, parent unit, F-API-040, VAL-15, global review,
  admission or release gate. §8 gives the exact execution envelope.

## 2. The failed gate, exactly as it ran (original, preserved)

| Item | Value |
| --- | --- |
| Command | `python -m tools.validate check --evidence build/software-waves/SW-API-READ-03-C1/campaign-02/run/evidence --run-summary build/software-waves/SW-API-READ-03-C1/campaign-02/run/run-summary.json --expect-clients api` |
| Exit | `1` |
| Sole stderr | `validation gate FAILED:` / `  (b) F-SEC-007 dropped below its recorded level: level V2 < recorded V3` |
| Original bytes | `build/software-waves/SW-API-READ-03-C1/gate-01/{check.log,exit.txt,command.json,process-checkpoint.json}` and the hash-verified `gate-01-copy/` |
| Source commit | `5331d5471a9d319c134e6798645d6ba8cf8466fc` (clean tree, recorded in the run summary) |
| Registry/findings | `docs/validation/features.yaml` and `docs/validation/findings_pending.yaml` at `5331d547` |

The exit-1 result and its single message are preserved unchanged. Nothing in
this audit re-ran that gate.

## 3. Exact input attribution

* **Evidence roots** — `tools/validate/ledger.py:251-252`
  (`default_roots` = committed evidence **plus** any `--evidence` directory),
  consumed by `tools/validate/__main__.py:85-95` (`_rows`) and
  `tools/validate/evidence.py:92-120` (`iter_records`, which accepts a record
  only when `schema_version == 1` and `scenario` is present).
  For the failed gate the roots were exactly:
  1. `docs/validation/evidence` (committed tree), and
  2. `build/software-waves/SW-API-READ-03-C1/campaign-02/run/evidence`.
* **Record population** — 2 132 evidence records in those roots; **28** of them
  carry `F-SEC-007` in their `features` list. **0** come from the campaign-02
  root: the campaign record is `F-API-040` only
  (`2026-10-29-V2-5331d547-sw_api_read_03_c1.output_name_change-api.json`,
  file SHA256 `7591de8ce9e152fceb18af12668b9593f6afbba7af2996a4adb4a7c1a089e3b2`).
  The campaign-02 run summary contains exactly one outcome —
  `sw_api_read_03_c1.output_name_change` / `api` / `V2` / `pass` / gate `ok`,
  9 passing checks — whose own `features` list is `["F-API-040"]`, which
  independently corroborates the `F-API-040` attribution below. The gate
  consumes that summary only through
  `tools/validate/ledger.py:119-133` (`gate`), i.e. for the `(a)` "scenario
  failed without a linked open finding" rule and the `--expect-clients api`
  rule at `tools/validate/__main__.py:108-125`.
* **Registry row** — `docs/validation/features.yaml`, `F-SEC-007`
  (line 7771 onward): `target: V3`, `current: V3`, `findings: [SEC-06]`,
  10 declared scenarios, 28 registry-cited evidence paths. The `current: V3`
  value is **unchanged** by `5331d547`; that commit's only registry edit is a
  **single** line — `docs/validation/features.yaml:4934` — and that line
  belongs to the **`F-API-040`** block, not to `F-MTX-031`. The `F-API-040`
  block opens with `- id: F-API-040` at line 4917 and closes before
  `- id: F-API-041` at line 4935; the edit adds
  `sw_api_read_03_c1.output_name_change` to **`F-API-040`'s** `scenarios`
  list. `F-MTX-031`'s own `scenarios` list is **not** touched by `5331d547`:
  it still reads `[live.front_panel_route, live.input_signal,
  live.display_unplugged, live.rename_elsewhere, ha.front_panel_route]`.
  `F-MTX-031` appears only inside **evidence filenames** listed in the
  `F-API-040` block (`docs/validation/evidence/F-MTX-031/...`), which is where
  the earlier attribution went wrong. **F-SEC-007's row is untouched by
  `5331d547`.**
* **F-SEC-007 is not capped** by an open blocking finding
  (`SEC-06` is not open critical/high), so the recorded V3 baseline is the
  value the row must meet.

## 4. Declared scenarios, clients and levels

From the live scenario modules (`tools/validate/scenarios.py` discovery), each
of the ten scenarios declared for F-SEC-007 maps to `F-SEC-007` for **each
client it declares**, and none declares a different feature set — the mapping
is not the cause. The `clients` column below is the **declared** client set,
not a universal one: **two** scenarios declare `api` only, **four** declare
both `api` and `browser`, and **four** declare `browser` only.

| Scenario | clients | targets | level(api) | level(browser) | `covers` count | covers `tools/validate/runner.py` |
| --- | --- | --- | --- | --- | ---: | --- |
| `security_hardening.profile_wrong_pin` | api | sim | V2 | – | 32 | no |
| `security_hardening.scene_wrong_pin` | api | sim | V2 | – | 32 | no |
| `sw_sec_auth_01.profile_allowed` | api, browser | sim | V2 | V3 | 48 | **yes** |
| `sw_sec_auth_01.profile_wrong_pin` | api, browser | sim | V2 | V3 | 48 | **yes** |
| `sw_sec_auth_01.scene_allowed` | api, browser | sim | V2 | V3 | 48 | **yes** |
| `sw_sec_auth_01.scene_wrong_pin` | api, browser | sim | V2 | V3 | 48 | **yes** |
| `sw_sec_auth_01.profile_locked` | browser | sim | – | V3 | 48 | **yes** |
| `sw_sec_auth_01.profile_per_item` | browser | sim | – | V3 | 48 | **yes** |
| `sw_sec_auth_01.scene_locked` | browser | sim | – | V3 | 48 | **yes** |
| `sw_sec_auth_01.scene_per_item` | browser | sim | – | V3 | 48 | **yes** |

Levels follow `tools/validate/model.py:63-68` (`level_for`: sim + a real client
— `browser`, `ha`, `uc`, `flic`, `model.py:60` — is V3; sim + `api` is V2),
applied per client at `tools/validate/runner.py:584`.

Two distinct cover sets exist among the 28 records:

| Cover set | Records | Scenarios | Levels / clients |
| --- | ---: | --- | --- |
| 32 paths | 4 | `security_hardening.profile_wrong_pin`, `security_hardening.scene_wrong_pin` | V2 api ×4 |
| 48 paths | 24 | the eight `sw_sec_auth_01.*` scenarios | V2 api ×8, V3 browser ×16 |

The 28 records are two evidence waves — `2ae46e6c` and `310d8b65` — each
contributing 2 `security_hardening.*` API V2 records, 4 `sw_sec_auth_01.*` API
V2 records and 8 `sw_sec_auth_01.*` browser V3 records. The 48-path set is
therefore **8 API V2 + 16 browser V3 = 24 records**, and the 32-path set is
**4 records**; no other mix occurs.

The 48-path set is `tests/validation/scenarios/sw_sec_auth_01.py:35-41`
(`COVERS`), which includes `tools/validate/clients/browser.py`,
`tools/validate/clients/browser_driver.mjs`, `tools/validate/clients/api.py`,
`tools/validate/model.py`, **`tools/validate/runner.py`**, the scenario and its
test module, the web assets and `tests/e2e/fixtures/data`. The 32-path set
(`tests/validation/scenarios/security_hardening.py:50`) declares only
`src/...` runtime paths plus the scenario module — **no validation tooling**.
`covers` is a required scenario field (`tools/validate/model.py:454`,
`480-481`) and is copied verbatim into each record
(`tools/validate/runner.py:780`).

## 5. The gate's actual rules, with references

* **Freshness** — `tools/validate/ledger.py:33-45`:
  a record is *stale* when any path in its `covers` changed in a commit after
  the record's own commit (or when the record recorded dirty files);
  *fresh* otherwise; *unknown* when the commit is not an ancestor of HEAD.
  The changed-path set is `git diff --name-only <record-sha>..HEAD`
  (`tools/validate/gitinfo.py:64-79`), and a cover entry matches a changed
  path by exact path, directory prefix or glob
  (`tools/validate/gitinfo.py:81-94`).
* **Level** — `tools/validate/ledger.py:86-113` (`compute`): the row starts at
  the registry's `current`; **if any fresh passing record exists, the level
  becomes the maximum level among fresh passing records** (then capped at V1 by
  an open critical/high finding). So a feature whose fresh set shrinks can fall
  *below* its recorded baseline even when nothing failed.
* **Drop rule** — `tools/validate/ledger.py:73-83` (`dropped`): any row with
  `level < recorded` is a drop.
* **Gate** — `tools/validate/ledger.py:119-133` (`gate`): `(a)` a run-summary
  outcome with gate `regression` and no linked open finding; `(b)` every
  dropped row. `--expect-clients` adds a third check at
  `tools/validate/__main__.py:108-125`.

## 6. Comparison across the three reference commits

Every number below is reproduced by the repository's **own**
`tools.validate.ledger.compute` / `gate` code, using the gate's exact input
roots. The frozen-base row was produced by evaluating the same library against
an isolated temporary repository whose HEAD is `938ae303` (the frozen base),
so it is a real library evaluation and not a re-implementation.

| HEAD | fresh pass | fresh fail | stale | proven | row level | recorded | gate errors for F-SEC-007 |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| `938ae303` (frozen base) | 16 (8 api V2 + 8 browser V3) | 0 | 12 | **V3** | **V3** | V3 | none |
| `5331d547` (gate-time source) | 4 (all api V2) | 0 | 24 | **V2** | **V2** | V3 | `(b) … level V2 < recorded V3` |
| `7294af5` (current entry) | 4 (all api V2) | 0 | 24 | **V2** | **V2** | V3 | `(b) … level V2 < recorded V3` |

The gate-time row was obtained with the real library at the checkout HEAD,
which is `7294af5`; `7294af5` differs from `5331d547` only in
`docs/production/software-waves/SW-API-READ-03-C1/AUTHOR.md`, which is in no
F-SEC-007 cover set, so the `5331d547` and `7294af5` rows are identical by
construction (the changed-path sets confirm this).

**The delta between frozen base and gate-time source is exactly five paths**
(`git diff --name-only 938ae303..5331d547`):

```
docs/production/software-waves/SW-API-READ-03-C1/AUTHOR.md   (no cover match)
docs/validation/features.yaml                                (no cover match)
tests/validation/scenarios/sw_api_read_03_c1.py              (no cover match)
tests/validation/test_sw_api_read_03_c1.py                   (no cover match)
tools/validate/runner.py                                     (cover match — 48-path set)
```

Exactly **one** changed path is inside any F-SEC-007 cover set:
`tools/validate/runner.py`, matching the 48-path set only. The 32-path
`security_hardening` set matches nothing.

Because the 48-path set is the cover set of **24** records, all **24** of them
are stale after `5331d547`. But only **12** of those records make a
fresh→stale transition at that commit; the other **12** were **already stale**
at the frozen base `938ae303` (the `12 stale` column of the table above). The
single changed path therefore leaves the 4 V2 API `security_hardening.*`
records fresh and drops **12** fresh records — which is precisely the observed
level change from V3 to V2.

The two groups are exact and disjoint:

* **Newly stale at `5331d547` (12 records)** — the `310d8b65` wave: 4 API V2
  (`profile_allowed`, `profile_wrong_pin`, `scene_allowed`, `scene_wrong_pin`)
  and 8 browser V3 (`profile_*` and `scene_*` × `allowed`, `wrong_pin`,
  `locked`, `per_item`). Their **only** matching changed path is
  `tools/validate/runner.py`.
* **Already stale at `938ae303` (12 records)** — the older `2ae46e6c` wave,
  with the same scenario/client shape. Their matching changed paths are
  `tools/validate/clients/api.py`, `tools/validate/model.py` **and**
  `tools/validate/runner.py`, all changed after `2ae46e6c` and before the
  frozen base. The `runner.py` change of `5331d547` is therefore **not** what
  made these 12 stale, and they are **not** part of the fresh→stale transition
  caused by `5331d547`.

**Why the changed branch is not entered by these scenarios.**
`5331d547` touched exactly one hunk in `tools/validate/runner.py`, inside
`Runner._refusal` (`tools/validate/runner.py:532-544`):

```python
if sc.action.intent in RUNNER_INTENTS:
    if not client.observes:
        applicable = [e for e in sc.expect if e.clients is None or client.name in e.clients]
        api_ws_observation = (
            self.o.target == "sim" and client.name == "api" and sc.action.intent == "device_change"
            and any(isinstance(e, WsEvent) for e in applicable)
            and not any(isinstance(e, ClientState) for e in applicable)
        )
        if not api_ws_observation:
            return f"client '{client.name}' cannot observe a '{sc.action.intent}'"
```

`RUNNER_INTENTS` is `frozenset({"device_change"})`
(`tools/validate/model.py:199`). Every F-SEC-007 scenario's action intent is
something else — `profile_recall` / `scene_run`
(`tests/validation/scenarios/sw_sec_auth_01.py:63`, `85`, `107`) or `request`
(`tests/validation/scenarios/security_hardening.py:31`) — and the new escape
path additionally requires the intent to be literally `device_change`. The
changed branch is therefore **not entered** by any of the ten F-SEC-007
scenarios, so the pre-change and post-change `_refusal` logic is identical for
all of them. This is a **code-reading** result: it is not a re-execution, it is
not a behavioural verdict, and it says nothing about whether the browser
behaviour still passes today.

## 7. What was ruled out, and what remains unknown

Ruled out by the comparisons above:

* **Changed covers (as a cause).** The recorded `covers` are byte-identical
  across the two source commits; the *declared* covers are also unchanged since
  `f4ffa8d1`. The covers did not change — a *covered path* changed.
* **Input selection.** The same 28 records were present at the frozen base and
  at the gate-time source; the campaign-02 root contributed 0 F-SEC-007
  records at either head.
* **Mapping.** Each of the ten declared scenarios maps to `F-SEC-007` for
  **each client it declares** — two `api`-only, four shared `api`/`browser`,
  four `browser`-only — and no record's `features` list disagrees with its
  scenario's `features_for(client)`.
* **Summary scope.** The run summary has a single `pass`/`ok` outcome with
  `gate: "ok"`, so gate rule `(a)` cannot fire; the run was not aborted.
* **A failing scenario or a weakened expectation.** `fresh_fail = 0` at every
  compared head — but that number is read from the `result` field of the
  **existing** records, so it is a bookkeeping reading and **not** a newly
  executed behavioural verdict. No level, target, expectation or assertion was
  changed by `5331d547`.
* **A registry change.** `F-SEC-007`'s `current: V3` / `target: V3` are
  untouched by `5331d547`; the commit's single registry line belongs to
  `F-API-040` (§3), and this report makes **no** statement about F-API-040's
  own correctness.

Remaining unknowns (explicitly **not** resolved by this audit):

* **Whether the `5331d547` runner change would alter any *other* feature's
  evidence freshness.** Only F-SEC-007 was in scope; the 48-path cover set is
  shared with any scenario that declares `tools/validate/runner.py`, so other
  features may have been affected in the same way. This audit makes no claim
  about them.
* **Whether the browser proof still holds today in substance.** This audit
  establishes that the *ledger bookkeeping* dropped, and that the changed
  `Runner._refusal` branch is not entered by these scenarios' action intents.
  It does **not** re-execute the browser flow and it issues **no** behavioural
  or security verdict. Whether the browser behaviour still passes today is
  **explicitly unknown**; that requires the fresh browser run in §8. No
  broad no-regression claim and no global security approval are made here.
* **Cover granularity as a design question.** The 48-path cover set marks
  evidence stale for any change to the validation runner itself, even when
  the change cannot affect the scenario. Narrowing that cover set (or
  separating "tooling" from "behaviour" covers) would be a *tooling change
  with its own review requirement* and is **out of scope here**; §8 does not
  depend on it.

## 8. Proposed minimal next action (not executed)

**Fresh browser proof is required and has not been executed. No implementation
defect is established by this audit, and no implementation correction is
called for by it.**

* **What to run.** The **existing** eight `sw_sec_auth_01.*` scenarios that
  declare the `browser` client, on the `sim` target — that is the only set
  that can carry F-SEC-007 at V3:
  `sw_sec_auth_01.profile_allowed`, `sw_sec_auth_01.profile_locked`,
  `sw_sec_auth_01.profile_per_item`, `sw_sec_auth_01.profile_wrong_pin`,
  `sw_sec_auth_01.scene_allowed`, `sw_sec_auth_01.scene_locked`,
  `sw_sec_auth_01.scene_per_item`, `sw_sec_auth_01.scene_wrong_pin`.
  **No new scenario, test or tooling is proposed**; these eight already
  exist in `tests/validation/scenarios/sw_sec_auth_01.py`. A browser run at V3
  (`tools/validate/model.py:60,63-68`) is sufficient: the row level is the
  maximum level among fresh passing records
  (`tools/validate/ledger.py:105-107`), so restoring a fresh V3 record set
  restores the V3 baseline. The four still-fresh `security_hardening.*` API V2
  records keep the API side represented; the stale `sw_sec_auth_01` API V2
  records are not level-bearing and do not need to be re-run to clear the gate.
* **Raw outputs stay private.** The fresh run writes to a **private**
  (git-ignored) output directory, and its raw outputs — screenshots, logs,
  artifacts and the evidence records it produces — are **not** imported into
  the canonical tree `docs/validation/evidence/`. **No `--record`** is to be
  used, and **no** canonical evidence, registry (`docs/validation/features.yaml`,
  `docs/validation/findings_pending.yaml`) or ledger
  (`docs/validation/LEDGER.md`) edit is authorised by this step.
* **Source to run it against.** A clean tree at `7294af5e39a5225d61f5b1b9961bf6976d9bc904`
  (or a later commit), with **no further change to `tools/validate/runner.py`
  or to any of the 48 covered paths after the run's recorded source commit** —
  otherwise the new records are stale again by the same rule
  (`tools/validate/ledger.py:33-45`). No change to
  `tests/validation/scenarios/sw_sec_auth_01.py` is needed: that module has
  not changed since `f4ffa8d1`.
* **Command (execution envelope).**
  `python -m tools.validate run --target sim --client browser --scenario sw_sec_auth_01.profile_allowed --scenario sw_sec_auth_01.profile_locked --scenario sw_sec_auth_01.profile_per_item --scenario sw_sec_auth_01.profile_wrong_pin --scenario sw_sec_auth_01.scene_allowed --scenario sw_sec_auth_01.scene_locked --scenario sw_sec_auth_01.scene_per_item --scenario sw_sec_auth_01.scene_wrong_pin --out <fresh run dir>`
  with real Chromium available for the browser client, a clean source tree, and
  isolated data/config as in §9. `<fresh run dir>` is a **private** directory.
* **Parser support for the acceptance shape (confirmed, not assumed).**
  `tools.validate check` declares `--evidence` with `action="append"`
  (`tools/validate/__main__.py:159`), so the flag is **repeatable**; the
  roots handed to the ledger are `default_roots([...])` =
  `[docs/validation/evidence (committed), *each --evidence]`
  (`tools/validate/ledger.py:251-252`, `tools/validate/__main__.py:85-95`).
  `--run-summary` takes a **single** file (`tools/validate/__main__.py:160`)
  and `--expect-clients` a comma-separated client list
  (`tools/validate/__main__.py:165`). The two
  command shapes below are therefore exactly what the parser accepts; they
  were checked against the parser, not inferred.
* **Acceptance — two unchanged gate-logic checks over the combined evidence
  roots.** After the fresh browser run exists, run the **unchanged**
  `tools.validate check` gate logic **twice** over the **same** two evidence
  roots — the **original** WS campaign-02 evidence root **and** the **fresh**
  browser evidence root — keeping the two original run summaries separate and
  unmodified:
  * **(a) original WS campaign evidence, original WS run summary:**
    `python -m tools.validate check --evidence build/software-waves/SW-API-READ-03-C1/campaign-02/run/evidence --evidence <fresh run dir>/evidence --run-summary build/software-waves/SW-API-READ-03-C1/campaign-02/run/run-summary.json --expect-clients api`
  * **(b) fresh browser evidence, fresh browser run summary:**
    `python -m tools.validate check --evidence build/software-waves/SW-API-READ-03-C1/campaign-02/run/evidence --evidence <fresh run dir>/evidence --run-summary <fresh run dir>/run-summary.json --expect-clients browser`

  Each check keeps its **own original** run summary and its **own**
  `--expect-clients` value: (a) gates the original WS campaign outcome with
  `--expect-clients api`, (b) gates the fresh browser outcome with
  `--expect-clients browser`. `--expect-clients` matches the client that the
  respective summary actually ran; a mismatched value would itself raise
  "client '<c>' ran no scenario". The two summaries are **never merged**:
  **no mixed summary may be synthesised**, **no record may be rewritten**, and
  the historical WS summary stays byte-identical to the one that produced the
  original exit `1`.
* **This is a NEW evidence-input set, not a rerun of the historical failed
  qualification.** The historical failure was the single-root check of §2
  (campaign-02 evidence only, at `5331d547`). The two checks above run
  **after** the fresh browser execution, over a **two-root** evidence set
  (committed evidence + original WS campaign evidence + fresh browser
  evidence) and with **two separate original summaries**. The historical
  failed qualification is therefore **not** re-run unchanged, and its
  recorded exit `1` (§2) is neither overwritten nor retracted.
* **Acceptance does not depend on canonical import.** Because source review
  and privacy admission are **held**, the acceptance above deliberately runs
  against the **private** fresh evidence root and the **private** fresh run
  summary. It does **not** require, and does **not** assume, that any record
  is imported into `docs/validation/evidence/`, committed to the canonical
  tree, or registered in `docs/validation/features.yaml`. Any later import,
  registry edit or ledger regeneration is a **separate, coordinator-owned**
  step that this report does **not** request, authorise or perform.
* **What must not happen.** Do not lower `F-SEC-007`'s `current`/`target`,
  do not weaken a level, target or expectation, do not edit `covers` to dodge
  staleness, do not hand-edit an evidence record, do not use `--record`, do
  not import canonical evidence, do not edit the registry or the ledger, do
  not re-label or re-admit the existing stale records, and do not synthesise
  or merge a run summary. This report closes no feature, parent unit or
  release gate, and admits no raw evidence.

## 9. Verification performed for this report

### 9.0 Original diagnosis pass (preserved, not re-run)

All commands used the root interpreter
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
this checkout's `src` and root on `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONIOENCODING=utf-8`, an isolated `data`/`config` directory, and a NEW
empty `TEMP`/`TMP` parent per invocation under the coordinator-allocated
`C:/t/fsec007-20261031-a/`. No pytest plugin or route/cache plugin was used
for the diagnostic calculations.

* The five existing documentation modules were run with the same interpreter
  and isolation: `tests/test_core_documentation.py`,
  `tests/test_client_guides_docs.py`, `tests/test_openapi_and_config_docs.py`,
  `tests/test_security_docs.py`, `tests/test_license_and_protocol_docs.py`
  (route inventory and cache providers disabled, forward-slash `--basetemp` and
  `--junitxml` paths). Result: **489 passed in 3.74 s, exit 0**. Raw output,
  JUnit XML and the exit code were written outside pytest retention and
  hash-verified:
  `pytest.log` SHA256 `272ad050bce58d5169db6b232698198cb75c2119f802bee665956604d89631af`,
  `junit.xml` SHA256 `a9adfc429abbd875ca1d0fd0fce6f04638ebdec9e8ab84aafefa18c6796d11ef`,
  `exit.txt` SHA256 `5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9`
  (all under `build/software-waves/SW-API-READ-03-C1/diagnosis-20261031/receipts/docs-20261031/`).
* CR-aware whitespace, UTF-8 and scope checks on this report passed.
* The inherited tracked source, the registry, the findings register, the
  committed evidence tree and the original gate bytes are **unchanged**; as of
  the original commit `d9273a03` the only tracked addition was this file.

This pass was **not re-run** by the correction below. Its receipts are
**immutable** and remain at
`build/software-waves/SW-API-READ-03-C1/diagnosis-20261031/`.

### 9.1 This correction pass (Task `task_3dabf0d8d5be` / Dispatch `ctx_dd26ee86926f`)

The correction re-verifies only the metadata that the corrected statements
rest on, and re-runs the five documentation modules. It ran **no** validation
scenario, drove **no** browser and re-ran **no** gate.

* **Isolation.** Every invocation used the root interpreter
  `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
  this checkout's root and `src` on `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`,
  `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`, an isolated
  `DATA_DIR`/`MATRIX_DATA_DIR`/`UC_CONFIG_HOME`, and a **NEW, EMPTY** short
  `TEMP`/`TMP` parent per invocation under the coordinator-allocated
  `C:/t/fsec007-20261031-a/correction-docs-01-parent/`. The route-inventory
  and cache plugins were disabled with `-p no:route -p no:cacheprovider`, and
  forward-slash `--basetemp` / `--junitxml` paths were used.
* **Bounded metadata verification** (`scripts/fsec007_correction_verify.py`,
  `scripts/fsec007_stale_reason.py`; whitelisted metadata only). It used the
  repository's own `tools.validate.evidence`, `tools.validate.gitinfo`,
  `tools.validate.scenarios` and `tools.validate.registry` code. It confirms:
  2 132 evidence records in the two roots, **28** of them carrying `F-SEC-007`,
  **0** from the campaign-02 root; the freshness table of §6 at
  `938ae303` (**16 fresh pass / 0 fresh fail / 12 stale / proven V3**),
  `5331d547`, `7294af5e` and `d9273a03` (**4 / 0 / 24 / V2**); exactly **12**
  records transitioning fresh→stale at `5331d547` (the `310d8b65` wave, whose
  only cover match is `tools/validate/runner.py`) against **12** already stale
  at `938ae303` (the `2ae46e6c` wave, matching
  `tools/validate/clients/api.py`, `tools/validate/model.py` and
  `tools/validate/runner.py`); the cover-set composition **32 paths → 4
  records** and **48 paths → 24 records (V2 api ×8, V3 browser ×16)**; the
  registry change ownership (**one** changed line,
  `docs/validation/features.yaml:4934`, owned by **`F-API-040`**, with
  `F-MTX-031`'s `scenarios` list unchanged and `F-MTX-031` appearing only in
  evidence filenames); the declared scenario/client mapping (**2** `api`-only,
  **4** shared `api`/`browser`, **4** `browser`-only; every declared action
  intent `request`, `profile_recall` or `scene_run`, none `device_change`); and
  the parser support for the §8 acceptance shape (**`--evidence` is
  `action="append"`, so it is repeatable**, and `default_roots` is
  `[committed evidence, *each --evidence]`).
* **The five existing documentation modules** were re-run with the isolation
  above: `tests/test_core_documentation.py`,
  `tests/test_client_guides_docs.py`, `tests/test_openapi_and_config_docs.py`,
  `tests/test_security_docs.py`, `tests/test_license_and_protocol_docs.py`.
  Result: **489 passed in 3.18 s, exit 0** — the same module count and the
  same pass count as §9.0. The raw output, JUnit XML and exit code were copied
  out of pytest retention and hash-verified immediately, before any further
  invocation:
  `pytest.log` SHA256 `e02b4a30e77e8f0c44766122f629b3ba6fa24ea7ceee2fa0862c516cca4e098c`,
  `junit.xml` SHA256 `2f83649423e43dac449b9c7bee33b6ef9c64fbfec0bc34141e884c33f9d65c37`,
  `exit.txt` SHA256 `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354`
  (under `build/software-waves/SW-API-READ-03-C1/diagnosis-correction-01/receipts/docs-01/`).
* **Scope.** `git diff --name-only HEAD` lists exactly one path — this report —
  and `git diff --name-only HEAD` restricted to every other tracked path is
  **empty**: the source, tests, scenario modules, runner, client, model,
  schema, registry, findings register, ledger and the committed evidence tree
  are **byte-unchanged**. The private `diagnosis-20261031/` receipts are
  **byte-unchanged**: the three hashes quoted in §9.0 still match the files on
  disk exactly. The original report bytes at `d9273a03` are preserved in Git
  and were not rewritten in place.
* **CR-aware whitespace and encoding.** This report is UTF-8 without BOM, LF
  line endings only, with no trailing whitespace, no tab characters and no
  whitespace errors reported by `git diff --check`.

## 10. Receipt index (private, git-ignored)

`build/software-waves/SW-API-READ-03-C1/diagnosis-20261031/`

| Path | Content |
| --- | --- |
| `scripts/fsec007_meta_audit.py` | git/library metadata audit: per-record whitelisted metadata + freshness simulation at the three reference heads |
| `scripts/fsec007_gate_repro.py` | reproduction of the gate rule through the repository's own `ledger.compute`/`ledger.gate` at the checkout HEAD |
| `scripts/fsec007_frozen_base_repro.py` | the same real library evaluated at the frozen base in an isolated temporary repository |
| `scripts/fsec007_mapping_and_cover_delta.py` | declared scenario/client/level mapping and the per-cover-set changed-path delta |
| `receipts/*.json` | the corresponding outputs (whitelisted metadata only) |

These are operational receipts, not shipped tools. The original native
transcript of the prior writer was not read or copied; only the original gate
bytes already in `build/.../gate-01/` were used, and they were not modified.

### 10.1 Correction-pass receipts (private, git-ignored)

`build/software-waves/SW-API-READ-03-C1/diagnosis-correction-01/` — **new**
tree for this correction only. It does **not** modify or replace the
`diagnosis-20261031/` tree above, which stays byte-identical.

| Path | Content |
| --- | --- |
| `scripts/run_iso.ps1` | the bounded isolated-invocation helper (root venv, own root/src `PYTHONPATH`, isolated data/config, UTF-8, bytecode off, NEW empty short `TEMP`/`TMP` per invocation) |
| `scripts/fsec007_correction_verify.py` | the bounded metadata re-verification of §9.1 (record population, freshness at the four reference heads, fresh→stale transition split, cover-set composition, registry change ownership, declared scenario/client mapping, `--evidence` repeatability) |
| `scripts/fsec007_stale_reason.py` | per-record matching changed paths at a given head (the evidence for the 12/12 split) |
| `receipts/verify-02/fsec007_correction_verify.json` | the metadata re-verification output (whitelisted metadata only) |
| `receipts/verify-03/stale_reason_938ae303.json` | per-record staleness at the frozen base |
| `receipts/verify-04/stale_reason_5331d547.json` | per-record staleness at the gate-time source |
| `receipts/docs-01/{pytest.log,junit.xml,exit.txt}` | the five documentation modules' raw output, JUnit XML and exit code, hashed before any further invocation |

These are operational receipts, not shipped tools, and they are not tracked.
No prior raw native transcript, environment store or credential store was read
in this correction pass.

## 11. Correction provenance (this revision)

This revision is a **bounded, metadata-only correction** of the report above,
authored under **Task `task_3dabf0d8d5be`** and **Dispatch
`ctx_dd26ee86926f`** in **Run `run_37205f6095b3`**, on branch
`ryan-haver/wp-api-read-03-c1`, from correction base
`d9273a0385f6534b7c8e75b6fd8b5fafce14cb29`. The original report's bytes at
`d9273a03` are **preserved unmodified**; the original authorship line, the
original frozen-entry provenance (`7294af5e…`), the original diagnostics, the
original global gate and the original campaign are **unchanged and were not
re-run**. The corrections were requested by an **independent coordinator
fact-check** and are limited to five findings, each re-verified against the
repository's own code before being written here: the `5331d547` registry
scenario-link change belongs to **`F-API-040`**, not to `F-MTX-031` (§3); the
fresh→stale transition at `5331d547` is **12** records, with **12** already
stale at the frozen base and all **24** `sw_sec_auth_01.*` records stale
afterwards, while the **28 total / 4 fresh V2 / 24 stale** table is unchanged
(§1, §4, §6); each scenario maps to `F-SEC-007` only for **each client it
declares** — two `api`-only, four shared `api`/`browser`, four `browser`-only
(§4, §7); the behavioural statements are **bounded** to what was actually
established, so that a metadata audit and `fresh_fail = 0` are **not** a newly
executed behavioural or security verdict, the changed branch is merely **not
entered** by the listed intents, and whether the browser behaviour still passes
today stays **explicitly unknown** (§1, §6, §7); and the §8 acceptance no
longer depends on canonical import while source review and privacy admission
are held — it now proposes the **existing** eight real-browser scenarios with
raw outputs **private**, followed by **two unchanged gate-logic checks** over
the **original WS campaign evidence and the fresh browser evidence**, each with
its own original, unmixed run summary and its own `--expect-clients` value,
as a **NEW evidence-input set after fresh execution** rather than a rerun of
the historical failed qualification, with no `--record`, no canonical
evidence/registry/ledger edit and no import authorised (§8). This revision
claims **no** fresh run, closes **no** feature, parent unit, F-API-040,
VAL-15, global-review, admission or release gate, and retains the actual
prior exit `1` of §2 together with every source, client and level limitation
recorded above.
