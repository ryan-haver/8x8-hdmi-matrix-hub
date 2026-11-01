# F-SEC-007 evidence-level gate — bounded metadata/input diagnosis

Task `task_f441e3251dbd` · Dispatch `ctx_341e35be5290` · Run `run_37205f6095b3` ·
branch `ryan-haver/wp-api-read-03-c1` · frozen entry `7294af5e39a5225d61f5b1b9961bf6976d9bc904`.

**Scope.** A bounded, read-only metadata/input audit of the failed F-SEC-007
evidence-level gate. This is **not** a source/security review, **not** a new
phase, **not** a CLI gate rerun, **not** a qualification, **not** an original
log, **not** a ledger generation, and **not** an admission of raw evidence. No
implementation, test or tooling was committed. Only this report is new; all
diagnostic computation is a read-only library calculation whose output is kept
in the ignored private tree
`build/software-waves/SW-API-READ-03-C1/diagnosis-20261031/`.

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
* **Not a behavioural regression.** No F-SEC-007 scenario failed at any
  compared head (`fresh_fail = 0`), and the `5331d547` runner change is
  unreachable for these scenarios (see §6). No level, target, expectation or
  assertion was weakened anywhere.
* **Not a rules defect, and not input/mapping selection.** The rule behaved as
  written; the committed `covers` are over-broad relative to what a
  validation-tooling eligibility exception can affect, but that is a
  **cover-granularity** observation, not a rule defect.
* **Consequently:** *fresh browser proof is required; an implementation
  correction is **not** required.* §8 gives the exact execution envelope.

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
  9 passing checks — which the gate consumes only through
  `tools/validate/ledger.py:119-133` (`gate`), i.e. for the `(a)` "scenario
  failed without a linked open finding" rule and the `--expect-clients api`
  rule at `tools/validate/__main__.py:108-125`.
* **Registry row** — `docs/validation/features.yaml`, `F-SEC-007`
  (line 7771 onward): `target: V3`, `current: V3`, `findings: [SEC-06]`,
  10 declared scenarios, 28 registry-cited evidence paths. The `current: V3`
  value is **unchanged** by `5331d547`; that commit's only registry edit was
  to `F-MTX-031`'s `scenarios` list (add `sw_api_read_03_c1.output_name_change`).
* **F-SEC-007 is not capped** by an open blocking finding
  (`SEC-06` is not open critical/high), so the recorded V3 baseline is the
  value the row must meet.

## 4. Declared scenarios, clients and levels

From the live scenario modules (`tools/validate/scenarios.py` discovery), all
ten scenarios declared for F-SEC-007 map to `F-SEC-007` for both clients, and
none declares a different feature set — the mapping is not the cause.

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
| 32 paths | 4 | `security_hardening.profile_wrong_pin`, `security_hardening.scene_wrong_pin` | V2 api |
| 48 paths | 24 | the eight `sw_sec_auth_01.*` scenarios | V2 api ×12, V3 browser ×12 |

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
`security_hardening` set matches nothing. That single path flips 24 records
from fresh to stale and leaves the 4 V2 API records fresh — which is precisely
the observed level change from V3 to V2.

**Why the runner change cannot have changed F-SEC-007 behaviour.**
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
path additionally requires the intent to be literally `device_change`. For all
ten F-SEC-007 scenarios the pre-change and post-change `_refusal` logic is
identical, so the change is **unreachable** for this feature.

## 7. What was ruled out, and what remains unknown

Ruled out by the comparisons above:

* **Changed covers (as a cause).** The recorded `covers` are byte-identical
  across the two source commits; the *declared* covers are also unchanged since
  `f4ffa8d1`. The covers did not change — a *covered path* changed.
* **Input selection.** The same 28 records were present at the frozen base and
  at the gate-time source; the campaign-02 root contributed 0 F-SEC-007
  records at either head.
* **Mapping.** All ten declared scenarios map to `F-SEC-007` for both clients
  and no record's `features` list disagrees with its scenario's
  `features_for(client)`.
* **Summary scope.** The run summary has a single `pass`/`ok` outcome with
  `gate: "ok"`, so gate rule `(a)` cannot fire; the run was not aborted.
* **A failing scenario or a weakened expectation.** `fresh_fail = 0` at every
  compared head; no level, target, expectation or assertion was changed by
  `5331d547`.
* **A registry change.** `F-SEC-007`'s `current: V3` / `target: V3` are
  untouched by `5331d547`.

Remaining unknowns (explicitly **not** resolved by this audit):

* **Whether the `5331d547` runner change would alter any *other* feature's
  evidence freshness.** Only F-SEC-007 was in scope; the 48-path cover set is
  shared with any scenario that declares `tools/validate/runner.py`, so other
  features may have been affected in the same way. This audit makes no claim
  about them.
* **Whether the browser proof still holds today in substance.** This audit
  establishes that the *ledger bookkeeping* dropped, and that the runner change
  is unreachable for these scenarios. It does **not** re-execute the browser
  flow; that requires the fresh browser run in §8.
* **Cover granularity as a design question.** The 48-path cover set marks
  evidence stale for any change to the validation runner itself, even when
  the change cannot affect the scenario. Narrowing that cover set (or
  separating "tooling" from "behaviour" covers) would be a *tooling change
  with its own review requirement* and is **out of scope here**; §8 does not
  depend on it.

## 8. Proposed minimal next action (not executed)

**Fresh browser proof is required. No implementation correction is required.**

* **What to run.** The eight `sw_sec_auth_01.*` scenarios that declare the
  `browser` client, on the `sim` target — that is the only set that can carry
  F-SEC-007 at V3:
  `sw_sec_auth_01.profile_allowed`, `sw_sec_auth_01.profile_locked`,
  `sw_sec_auth_01.profile_per_item`, `sw_sec_auth_01.profile_wrong_pin`,
  `sw_sec_auth_01.scene_allowed`, `sw_sec_auth_01.scene_locked`,
  `sw_sec_auth_01.scene_per_item`, `sw_sec_auth_01.scene_wrong_pin`.
  A browser run at V3 (`tools/validate/model.py:60,63-68`) is sufficient: the
  row level is the maximum level among fresh passing records
  (`tools/validate/ledger.py:105-107`), so restoring a fresh V3 record set
  restores the V3 baseline. The four still-fresh `security_hardening.*` API V2
  records keep the API side represented; the stale `sw_sec_auth_01` API V2
  records are not level-bearing and do not need to be re-run to clear the gate.
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
  isolated data/config as in §9.
* **Acceptance command for the refresh itself.**
  `python -m tools.validate check --evidence <fresh run dir>/evidence --run-summary <fresh run dir>/run-summary.json --expect-clients browser`
  → expected exit `0` and `[validate] gate OK`. (The `--expect-clients browser`
  value matches the client actually run; `--expect-clients api` would itself
  raise "client 'api' ran no scenario".)
* **Acceptance command for the original failure.** After the coordinator has
  imported and committed the accepted records, re-run the original gate shape
  unchanged:
  `python -m tools.validate check --evidence build/software-waves/SW-API-READ-03-C1/campaign-02/run/evidence --run-summary build/software-waves/SW-API-READ-03-C1/campaign-02/run/run-summary.json --expect-clients api`
  → expected exit `0`.
* **What must not happen.** Do not lower `F-SEC-007`'s `current`/`target`,
  do not weaken a level, target or expectation, do not edit `covers` to dodge
  staleness, do not hand-edit an evidence record, and do not re-label or
  re-admit the existing stale records. This report closes no feature, parent
  unit or release gate, and admits no raw evidence.

## 9. Verification performed for this report

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
* The inherited tracked source, the original report, the registry, the
  findings register, the committed evidence tree and the original gate bytes
  are **unchanged**; the only tracked addition is this file.

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
