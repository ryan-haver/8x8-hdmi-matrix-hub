# FC-TRUTH — covered correction notes (original-author factual correction)

**Package:** `FC-TRUTH` · **Phase:** `functional-completion-20261104` · **Author route:** MiniMax M3
(`minimax-coding-plan/MiniMax-M3`, variant `thinking`) via OpenCode 2 · **Reserved reviewer route:** OpenAI
`gpt-6.1-sol` / `high` (`Sol`, OpenAI family) — **the same reserved reviewer, at the exact corrected commit.**

**What this file is.** The itemised correction record for `INVENTORY.md`, produced under the package's one factual
correction reserve after the independent Sol review of the exact author commit `99e72bd9ac9c592afde5fd3b110f8b56e7c3d5d4`
returned **REQUIRE_CHANGES**. It states, finding by finding, what the review found, what was changed, where the change
lives, what was **not** changed, and what remains unread or unproven.

**What this file is not.** It is not a second report, not a source acceptance, not a competence decision, and not a
qualification. It closes no finding, promotes no level, admits no evidence, changes no canonical registry, ledger,
register or pending row, and grants no owner, hardware, visual, soak, field, version, artifact or release approval.

**Custody.** The original author completion, its report bytes, the original evidence/native/full-bundle custody and
the reviewer's registered payload `02df1ad6c37b48a1b82a80dbf261e2e1` are **preserved unchanged**. The original
failed command and its captured bytes (the mistyped C2 object query) are **preserved as the historical record of the
error**; the corrected observations below are **supplemental** measurements recorded separately. Nothing in the
original `99e72bd9…` history was rewritten, and no fetch, prune, reset, rebase, cherry-pick or import occurred.

---

## 1. Review findings, one by one

### R1 — Medium: a mistyped SHA was presented as lost history

**Reviewer's finding.** The inventory presented `615d3c8403b237dd117c803269c7b9b58895f9217` as a privacy-C2 commit
object that was *absent* from the local object database, and built an availability blocker and a coordinator
fetch/restore task on it.

**Independent observations re-measured by this correction (in this checkout, at `99e72bd9…`):**

| Operation | Actual result |
| --- | --- |
| `git rev-parse 615d3c84` | exit 0 → `615d3c8403b237dd117c8032697c9b58895f9217` |
| `git cat-file -t 615d3c8403b237dd117c8032697c9b58895f9217` | exit 0 → `commit` |
| `git cat-file -t 615d3c8403b237dd117c803269c7b9b58895f9217` | exit 128 → *Not a valid object name* |
| `git show-ref` (local **and** origin `ryan-haver/wp-sec-data-02-c2`) | both point at the **valid** SHA `…2697c9b…` |
| `git merge-base --is-ancestor <valid C2> a07cf942…` | exit 1 — non-ancestor, **without** an object error |
| `git merge-base --is-ancestor <valid C2> 2d02004d…` (C3) | exit 0 — C2 **is** an ancestor of C3 |
| `remote.origin.promisor` / `extensions.partialclone` | both unset — not a partial clone |

**Corrections made.**

1. §1.2 ancestry table — the privacy-C2 row now names the **valid** full SHA and its actual relation (not an
   ancestor of this base; an ancestor of C3; the object is present).
2. §1.2 — the "object is not present" bullet is **replaced**. The absence claim, the partial-clone reasoning and the
   coordinator restore task are withdrawn. The bullet now distinguishes the **transcription error in the identifier
   under test** from the **integration** fact that the chain is not integrated here, and it states explicitly that
   **no fetch, prune or history repair is required or proposed**.
3. §4.2 VAL-15 — the privacy-chain sentence no longer claims C2 is absent; it states that C2 is present, is an
   ancestor of C3 and is not an ancestor of this base.
4. §4.4 privacy chain C1–C4 — rewritten: all of C1–C3 exist as objects, none is an ancestor of this base, C2 is an
   ancestor of C3, so the chain is intact and merely unintegrated.
5. §8 residual **R-02 is retracted in place**, with the reason, the corrected measurements, and an explicit statement
   that **no** object restore, fetch, prune or history repair is required. The withdrawn claim stays visible and
   labelled as withdrawn.
6. §10.3 — the privacy-chain gate row no longer says "C2's object is locally missing".

**What was deliberately not done.** No fetch, no prune, no history repair, no rewrite of the original failed command
or its captured bytes, no change to the original `99e72bd9…` history, and no change to the separately recorded lost
original evidence or the pending privacy budget. The chain remains **unintegrated and unaccepted** — that is an
independent fact and it is unchanged.

### R2 — Medium: five inherited leads were labelled resolved

**Reviewer's finding.** API-16, API-18, API-21, UI-05 and UI-08 were reported as `resolved`, although both the
accepted SW-FINDINGS-01 triage and its accepted execution delta classify all five as `S` — *source-inspection
candidate, behaviour not reproduced*. There was no relevant product-source change.

**Surviving source re-read at this base (all five confirmed present):**

| Row | Source actually read | Classification restored |
| --- | --- | --- |
| API-16 | `sys.path.insert` in nine request handlers — `src/rest_api/audio.py:45,82,105,371,394`, `src/rest_api/outputs.py:263,293,316`, `src/rest_api/cec.py:314` | `S` → **reproduce** |
| API-18 | `src/config.py:258` `class SceneManager` with its legacy scenes reader (`load()` at :277) | `S` → **reproduce** |
| API-21 | `src/rest_api/scenes_v2.py:212` `async def _json_response` plus its awaited call sites, beside the shared **sync** helper at `src/rest_api/utils.py:336` | `S` → **reproduce** |
| UI-05 | `web/js/components/hardware-drawer.js:145-168` forwards the drawer controls to the legacy elements and dispatches `new Event("change")` on them | `S` → **reproduce** |
| UI-08 | `web/js/utils/dashboard-manager.js:1113-1140` reads/writes the dashboard configuration in `localStorage`; `web/kiosk.html:2856-2883` loads, migrates and defaults the local shortcut/profile pin arrays in `localStorage` | `S` → **reproduce** |

**Corrections made.**

1. §4.2 — all five rows rewritten: the surviving condition is stated from the source, the inherited `S` label is
   restored and cited to the accepted triage, the recommendation becomes **reproduce**, and the strength cell says
   explicitly that only the **source condition** was re-verified and that the behaviour was **not** exercised.
2. §4.1 strength-label paragraph — now states that a positive "re-verified" cell does **not** mean the behaviour was
   reproduced, the evidence re-run, or the inherited disposition re-qualified.
3. §2.3 — the five rows move from the inherited population to the positive re-read population, and the resulting
   counts are stated explicitly (see §2 below).
4. §7 — a **new proposal 8** records that these five rows must **stay open** as source-inspection leads and must
   **not** be routed to register-text reconciliation; the register text is not stale and source presence proves
   neither active runtime use nor closure.
5. §8 R-03 — **UI-05 is withdrawn from the anchor residual.** The register's own 145-178 range **does** carry the
   synthetic-change mechanism; the earlier statement in the report that it carried only unrelated comments was wrong.
   The residual's remaining anchor cases and their corrected live anchors are listed.
6. §10.1/§10.2 — the completion claims are narrowed: the package does **not** claim a completed semantic re-read of
   every historical assertion, client campaign, image layer or UI behaviour.

**What was deliberately not done.** No duplicate implementation, no runtime reproduction campaign, no browser or device
session, no new test or tooling, and no promotion of any level to fill the gap. The correct follow-up remains the
bounded reproduction the `S` class already calls for.

### R3 — Medium: the 268-row ledger index omitted the required semantic map

**Reviewer's finding.** The report indexed ledger metadata but did not map the registry `claim`, interfaces, recorded
`basis`, actual source/assertions and residual acceptance per feature. In particular the 102 rows labelled "no
committed record" never identified the named tests or historical assertions their baseline rests on, so a
mechanically correct level could be mistaken for complete contract coverage. No incorrect ledger level was alleged.

**Correction delivered — a new §5A, covering all 268 rows.**

For **every** canonical feature the map now carries, in one place:

* the registry **claim** and **interfaces** (verbatim);
* the registry **recorded basis** (verbatim);
* the **named source/assertion scope actually read at this base** — `file::function` with its line range and the
  assertion statements inside it, or the named test module, class or package. The assertion bodies were **read**, not
  counted; a file name, scenario id, link, hash count or occurrence total is never used as a substitute for an
  assertion;
* what that observable assertion **does** establish and what it **does not**;
* the evidence **attribution** — the committed record's own path, evidence commit, level, client, scenario, target,
  image digest and `covers` set (with the common-core delta) — or an explicit **unknown** where no committed record
  exists;
* the **level, cap, ancestry and freshness** state, including which cited commits are ancestors of the base and which
  are not;
* the **exact residual acceptance**.

§5A also publishes the legends it uses: **52 named assertion scopes** with their establishes / does-not-establish
text, the named **module, class and package** scopes (the class scopes are read from the tree, with line range,
docstring, test-method list and assertion counts), and the per-feature rows themselves.

**The five examples the review named are covered explicitly**, with a per-feature distinction recorded in the row:

* **F-API-001** — the basis names three distinct assertions (health/runtime read, integration-lifecycle mapping,
  real OpenAPI response assertions), not one.
* **F-API-039** — the basis names `tests/sim/test_sim_ws_contract.py::test_welcome_carries_the_protocol_and_the_matrix_link_then_a_snapshot`
  at line 281 and `::test_get_status_answers_a_status_snapshot` at line 295; both were read.
* **F-API-032** — its fresh V3 record is `live.matrix_offline` (link loss, REST refusal, recovery, UI/kiosk
  connection state); it does **not** by itself cover every welcome/`get_status` requirement in the title.
* **F-UI-015** — the recorded V3 rests on the scene-editor save flow; the registry itself retains prompt-based step
  editing under UI-19, so the baseline is **not** complete editor acceptance.
* **F-FLIC-005** — the first selected V3 proof `flic.cec_output_navigation_refused` is a **negative** record (HTTP
  400, no write, no mutation); the positive volume proof is the separate `flic.display_volume` record. The physical
  Flic Hub, the SDK version and the physical button set are **unknown** in that record.

**Honest limits of §5A, stated in the section itself.** No product test, scenario, browser session, container, device,
simulator campaign or HIL session was executed for any row. The assertion bodies were read for the 52 named test
functions and the named modules/classes/packages the registry bases cite; where a basis names a module or class the
scope is recorded at that granularity and no per-assertion claim is made beyond it. Where a basis names no test at all,
the row says so explicitly: **125** of the 268 rows have no named test in their recorded basis — for **45** of them no
committed evidence record exists either, so the assertion scope is recorded as **unknown**, and for the other **80**
the only available observable assertion is the committed record's own recorded `checks`, which the row reproduces and
labels as such. None of those 125 rows is presented as having had its semantics read. The `covers` set of a record is
the record's **own** claim, reproduced and not re-derived. Every committed
record cited records `target: sim`: **no committed evidence record in this tree was produced against physical
hardware**, so no row in §5A carries a physical claim.

**What was deliberately not done.** No new tests, tooling or fixtures; no retained deliverable other than the two
report files; no campaign, promotion or evidence import to fill prose; no level, cap or finding changed; and no
claim of full scope derived from generated rows — the section says exactly what was and was not inspected, and rows
that could not be inspected are marked **unknown** rather than counted as covered.

### R4 — Low: the documentation-import conclusion contradicted the original snapshot

**Reviewer's finding.** The report stated that the documentation run "did **not** import `src/rest_api/*`", on the
strength of a filtered zero. The retained original `docs_result.json` actually holds **25** `rest_api`/`rest_api.*`
entries, all resolving to the author's own checkout, because the receipt's filter used `src.`/`tools.validate`
prefixes while the project's canonical import name is `rest_api`. The serialised `imports_atexit` was empty and was
not proof of a completed second snapshot.

**Corrections made.**

1. §12.3 — the original conclusion is **withdrawn** and replaced by a corrected reading taken from the **same
   original snapshot**: the 25 `rest_api`/`rest_api.*` entries and their origin paths are listed, the
   `src.`-prefix filter is explained, `tools.validate` is correctly reported as 0, and `imports_atexit` is reported
   as empty with the explicit statement that it is **not** proof of a completed second snapshot.
2. §12.3 — the scope statement is rewritten: the run **did** import the canonical `rest_api` package from this
   checkout, and it remains a documentation-module prose check — **not** a product-behaviour result, **not** a
   feature-level result, **not** a model-qualification result and **not** a canonical route check.
3. §12.6 — the correction is listed as a **post-run prose correction**, explicitly not covered by the run.

**What was deliberately not done.** No rerun of the unchanged documentation check, and no relabelling of the old
evidence identity. The original `docs_result.json` (87313 bytes, SHA-256
`08f970c723edbeccc026fc7c3770d3b4a97ae35c56322a789d8177bfde8e5ed0`) is **preserved unchanged**; the corrected
reading is a **derived supplement** computed from it.

---

## 2. Consequential non-blocking overclaims that were also corrected

| # | Overclaim in the reviewed report | Correction | Where |
| --- | --- | --- | --- |
| P1 | §6.3's four units are *"inventory-ready now"* | *Inventory-ready* now means **bounded inventory task fit subject to the normal gates** — not a readiness grant, not a qualification, and not a claim that dependencies are satisfied. **SW-REPO-01 requires accepted findings intake** (the SW-FINDINGS-01 triage and its accepted execution delta, accepted **as triage only, with limits**); **SW-DOCS-01 retains numerous accepted/integrated/published package and unit dependencies**, and its full completion/dispatch readiness was **not established**. | §6.2 rows 01, 02, 61, 62; §6.3 |
| P2 | §6.1 said MiniMax had *"No competence-assessment record"* | Replaced by **"no relevant PASS for the proposed source role"**. The MiniMax records that exist are the terminal privacy **FAIL** (`FAIL/NOT_QUALIFIED; one first candidate / one judge exhausted; no automatic retry / extra judge`) and the terminal Opus 5.5 privacy **FAIL**; both are preserved and visible in §4.4, and neither is renewed, waived or retaken. | §6.1 |
| P3 | §2.3's *47*, the receipt's *14*, §4.3's *17 / 44* and the table's *27* strength cells were used loosely | Six populations (P1–P6) are now **defined with their own criterion and per-ID membership**: P1 = 47 inherited no-material-delta rows; P2 = 14 = the complement of P1 (the accepted triage's 12 material-delta rows plus `VAL-14`/`VAL-15`); P3 = 17 expanded in §4.3; P4 = 44 = the complement of P3; P5 = the positive "re-verified" strength cells — **29** in the corrected report, 24 on the reviewed commit; P6 = the "inherited triage" cells — **32** in the corrected report, 37 on the reviewed commit. A naive string search for "re-verified" returns **27** on the reviewed commit because three inherited cells contain the phrase only to say the element was **not** re-verified. | §2.3; §4.1 |
| P4 | §4.3 said *"The other 44 rows are inherited dispositions"* | Corrected: the other 44 are the **42** P1 rows not expanded there, **plus** `VAL-14` and `VAL-15`, which no accepted triage covered. Five rows that *are* inherited no-delta rows (UI-06, UC-18, TST-03, TST-04, API-07) are expanded anyway, because the accepted triage had flagged their register text as material to their own close conditions. | §4.3 |
| P5 | §3.5 defined a stale record as *"evidence that existed and whose covered paths changed afterwards"* | Corrected to the project's actual semantics: `FeatureRow.stale` holds **every** record whose freshness is not `fresh`, which includes records whose commit is **not an ancestor** of HEAD (`gitinfo.freshness` returns `unknown`). At this base exactly **one** non-ancestor evidence commit appears among the stale records — `d6668000167b259a4a285541fc1bb58fa30ac6f2`, on `F-UI-024`, `F-REL-008` and `F-REL-009`. | §3.5 |
| P6 | The report gave 210 below target without the inequality sensitivity control | The **effective-inequality control is 212**, not 210: reading the same effective levels with `!=` instead of the ordered `<` wrongly adds the two above-target rows (`F-API-032`, `F-API-040`). Both the raw pair (227 ordered below / 227 unequal, 0 above) and the effective pair (210 ordered below / 212 unequal) are now stated with their rules. The **historical 203 / 57** wave02 pair is retained unchanged, with its date, its definition and its `source` note. | §3.1, §3.2 |
| P7 | §7 proposal 6 could have turned literal test-file occurrence counts into assertion adequacy | Proposal 6 now requires a **per-row, per-clause** correction and states that the TST-03 counts (151 / 91 / 40 / 7) are **identity counts, not assertion adequacy**; the reconciled text must say the adequacy is **not established**, exactly as the registry basis says. §8 R-04 carries the same rule. | §7 proposal 6; §8 R-04 |
| P8 | §13 claimed *"No other location on the host was written … and no other agent's output … was read"* | Withdrawn and replaced by a **scoped** statement: every byte this package wrote lies inside the two owned roots, which it inventoried before and after; it did **not** run a host-wide write audit; it **did** read other agents' historical evidence records and the retained review/custody payloads **read-only**, and wrote to, moved or removed none of them. | §13 |
| P9 | The original completion receipt recorded `scoped_model_config_present_in_this_worktree: false` and a `git_config_sha256` equal to the empty-string hash | Corrected: **`opencode.json` exists** in this worktree — **1628 bytes**, SHA-256 `62e6f5ab100bffe9aa802a380f3860612ba1aedf5e760ae443d5040984b18096` — and the hashed `.git/config` path **does not exist** because `.git` is a **pointer file**; hashing a non-existent path yields the empty-string SHA-256 and proves **nothing** about the common or global configuration (the real `core.hooksPath` is in the common directory). The original receipt bytes are **not** rewritten. | §13.1 |
| P10 | §13 carried unrendered template placeholders (`{inv_pre['grand_total_bytes']}`) | Replaced with the measured values: pre-run **3473181 bytes / 36 files** → post-run **3737360 bytes / 145 files**. | §13 |
| P11 | The report did not state explicitly that no owner question was re-asked and no closed decision reopened | §9 now states that O-1 is carried forward unchanged rather than re-asked, that O-2 and O-3 restate their rows' own recorded conditions, that this report issues **no** new owner question, and that the **closed original Tron owner decisions stay closed**. | §9 |

---

## 3. What was re-verified and what was not

**Re-verified in this correction, by direct read or by the project's own unchanged code at this base:**

* The privacy-C2 object identity and both ancestry relations (§1, above).
* The surviving source of all five `S` rows: the nine `sys.path.insert` call sites, `src/config.py:258`'s legacy
  `SceneManager`, `src/rest_api/scenes_v2.py:212` beside `src/rest_api/utils.py:336`, the synthetic-change forwarding
  at `web/js/components/hardware-drawer.js:145-168`, and the two `localStorage` stores at
  `web/js/utils/dashboard-manager.js:1113-1140` and `web/kiosk.html:2856-2883`.
* Every ledger figure in §3 and §5, recomputed with the project's own `registry.load_features()`,
  `registry.load_findings()` and `ledger.compute()` over `default_roots()` at this base: 268 features; 61 parser-open
  findings; raw 227 below / 227 unequal / 0 above; effective 210 ordered below and 212 by inequality; 58 at or above
  (56 equal + 2 above); 16 at-or-above without a fresh passing record; 198 without any fresh passing record
  (96 stale-only + 102 no record); 70 fresh passing and 0 fresh failing; 12 V1 caps, all from HIL-09; effective levels
  V0 18, V1 122, V2 32, V3 96, V4 0, V5 0; and all 30 package aggregates.
* The **52 named test functions** and the named test modules, classes and packages that the registry bases cite —
  their assertion statements, class line ranges, docstrings, test-method lists and assertion counts were read.
* The committed evidence records' own `checks`, `environment`, `covers` and `commit` fields.
* The original documentation run's `docs_result.json`, `junit.xml`, `stdout.txt`, `stderr.txt` and the two owned-root
  inventories, read from the preserved original roots.

**Not done, and not claimed:**

* No product test, scenario, browser session, container, device, simulator campaign or HIL session was executed.
* No runtime defect was reproduced, and no historical feature assertion, client campaign, image layer or UI behaviour
  was semantically re-read end-to-end.
* No finding was closed, no level promoted, no ledger generated, no gate called, no evidence admitted, no canonical
  record changed, no competence awarded, no worker or assessment dispatched, no HIL-09 cap removed, no owner/hardware/
  visual/soak/field/version/artifact/release gate approved, and no push, merge, tag, publication or cleanup performed.
* No source, test, tool, contract, root manifest, lockfile, registry, ledger, baseline, private runtime data or other
  workspace was modified. The only tracked edits are this file and `INVENTORY.md`.

---

## 4. Verification of this correction

### 4.1 The correction's own documentation check (attributed to the correction, not to the original run)

The applicable check is the repository's own **documentation** check set, run **once**, after this file's and
`INVENTORY.md`'s final prose bytes, from this checkout. **This run is attributed to the correction and is a separate
event from the original package's run; it does not replace, re-date or re-identify the original run's evidence, and
the original run's conclusion is corrected from its own preserved snapshot (§1 R4).**

| Item | Value |
| --- | --- |
| Run id | `fc-truth-correction-20261104T201500Z` |
| Interpreter | `C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe` with `-B` |
| Python | 3.12.10 |
| Working directory | `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-truth` |
| UTC start / end | `2026-11-04T21:21:18.749578+00:00` → `2026-11-04T21:21:22.832315+00:00` |
| Direct child exit code | **0** |
| pytest summary | **489 passed**, 0 failed, 0 errors, 0 skipped (`489 passed in 3.49s`) |
| stdout | 588 bytes, SHA-256 `b4e1f8cefa58734397a7c2c487e0b4ef1e6b4af91fdf76ffd054e4bc24890534` |
| stderr | **0 bytes**, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (the SHA-256 of the empty string) |
| JUnit | 63691 bytes, SHA-256 `5ef20e1cd51fd5c710b3301113cadbba74b7fa222e10e01c8421836022a8a281` — tests **489**, failures **0**, errors **0**, skipped **0** |
| Environment | the child **inherited the Windows environment**, then received a fresh owned overlay; `PYTEST_ADDOPTS`, `PYTEST_PLUGINS` and `PYTHONPATH` were dropped; `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`, `TMPDIR`, `HIDDEN_TEMP`, `--basetemp` and `--junitxml` all point inside this correction's registered payload |
| Direct argv | `tests/test_core_documentation.py tests/test_client_guides_docs.py tests/test_openapi_and_config_docs.py tests/test_security_docs.py tests/test_license_and_protocol_docs.py -q -p no:tests.route_inventory -p no:cacheprovider --basetemp=<payload>/docs-run/temp/pytest-tmp --junitxml=<payload>/docs-run/junit.xml` |
| In-run module origins | `tests.conftest`, `tests.test_*_docs`, `hub`, `hub.openapi`, `hub.env`, `hub.integrations`, `hub.persistence`, `hub.runtime`, `hub.runtime_paths` and `pytest` all resolved inside this checkout / the root venv |

**One incidental corroboration of R4, recorded because it was observed, not because it was sought.** This correction's
own in-run snapshot contains **25** `rest_api`/`rest_api.*` modules resolving to this checkout and **0**
`tools.validate` modules — the same shape as the original snapshot. That confirms the R4 diagnosis of the original
receipt's `src.`-prefix filter independently of the original bytes. It does **not** change the original run's
recorded exit code, pass count or JUnit counters, which stand exactly as originally measured, and it establishes
nothing about product behaviour: the five documentation modules do not prove that this Markdown was parsed by any
test, that any route is covered, that any feature level changed, or that any source or model is qualified.

### 4.2 Scope, encoding and whitespace checks

Before the commit: strict UTF-8 decode, a local-target/anchor link check, `git -c core.whitespace=cr-at-eol diff
--check`, and an exact staged-scope check. The commit uses the authorised **invocation-only empty `core.hooksPath`**
exception for this pure-prose change; **no** repository or global hook configuration is changed and **no** source-hook
or full-suite success is claimed.

### 4.3 Storage

This correction's disposable output — scratch scripts, intermediate digests, the generated §5A fragment and the run
artefacts above — is confined to its own registered agent-storage payload
(`…/artifacts/8cf626a93e994201a7f90405627e24b9/payload`). Its byte accounting, retention decision and review date are
in that payload's completion receipt. The original package's two owned roots, its report bytes, its completion
receipt and the reviewer's registered payload are **read-only** for this correction and are **unchanged**.

**The reserved independent different-family reviewer (`Sol`, OpenAI family) must review the exact corrected commit
before any coordinator action.** This correction is **not** self-accepted.
