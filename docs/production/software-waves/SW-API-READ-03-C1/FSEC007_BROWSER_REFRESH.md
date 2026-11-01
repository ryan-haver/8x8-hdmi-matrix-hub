# F-SEC-007 fresh browser execution

**Result:** eight existing browser scenarios passed; both new combined-input checks exited 0.

Task `task_017738dbb31b` / Dispatch `ctx_4e220d036b79` / Run `run_37205f6095b3`; Sol 6.1/high dispatched execution and sanitized reporting only.

Exact clean execution base: `659d3f4a65bd3eb463bf7e4f9a78857cf6b8acb2` on `ryan-haver/wp-api-read-03-c1`. All eight original records and the original run summary attribute this same SHA, with `dirty: false` and empty dirty-file lists. Source is unchanged from `5331d5471a9d319c134e6798645d6ba8cf8466fc`; the intervening tracked diff contains only the existing AUTHOR and diagnosis reports. No attribution to independent API-C2 is made.

Actual target/client/level: `sim` / `browser` / `V3` for all eight; every outcome is `pass`, gate `ok`, no abort or failed check. Original runner client metadata identifies `chromium 153.0.8010.12` and the Playwright driver for every record. Prerequisites observed: Node `v26.13.0`, pinned `@playwright/test 1.63.0`, installed Chromium executable present. Campaign finished at `2026-11-01T01:28:18.277Z` (UTC date Nov 1, local Oct 31); the authorized output directory keeps its Oct 31 name.

| Existing scenario (`sw_sec_auth_01.` prefix) | Outcome | Passing checks | N/A |
| --- | --- | ---: | ---: |
| `profile_allowed` | pass / ok | 7 | 1 |
| `profile_locked` | pass / ok | 9 | 0 |
| `profile_per_item` | pass / ok | 11 | 0 |
| `profile_wrong_pin` | pass / ok | 7 | 1 |
| `scene_allowed` | pass / ok | 7 | 1 |
| `scene_locked` | pass / ok | 9 | 0 |
| `scene_per_item` | pass / ok | 11 | 0 |
| `scene_wrong_pin` | pass / ok | 7 | 1 |

**Totals: 68 pass, four N/A, zero fail.** The four N/A checks are the existing response-body assertions for allowed/wrong-PIN flows, explicitly marked by the runner as not checked for the browser client: the unchanged scenario declaration limits those assertions to `clients=("api",)`. No expectation was edited. Real UI procedures, 32 screenshots, before/after independent simulator state and 332 command-log entries are present across the original records. The runner retained its existing managed disposable stack and cleanup behavior; per-record restore fields are null for this simulator campaign, so no hardware-restore claim is made.

Interpreter: `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`; own checkout and `src` on `PYTHONPATH`, bytecode disabled, UTF-8, isolated DATA_DIR/MATRIX_DATA_DIR/UC_CONFIG_HOME/TEMP/TMP. Every invocation used a new empty parent under `C:/t/fsec007-browser-20261031-a`. Raw logs, original summaries, records, screenshots and temporary files were copied and SHA-256 inventoried before the next invocation; the campaign run copy was independently hash-compared equal.

Campaign command shape (the interpreter above precedes it; the original receipt uses the absolute forward-slash output path):

```text
-m tools.validate run --target sim --client browser --scenario sw_sec_auth_01.profile_allowed --scenario sw_sec_auth_01.profile_locked --scenario sw_sec_auth_01.profile_per_item --scenario sw_sec_auth_01.profile_wrong_pin --scenario sw_sec_auth_01.scene_allowed --scenario sw_sec_auth_01.scene_locked --scenario sw_sec_auth_01.scene_per_item --scenario sw_sec_auth_01.scene_wrong_pin --out build/software-waves/SW-API-READ-03-C1/browser-refresh-20261031/campaign-01/run
```

Actual gate command shapes used two repeated evidence roots, with absolute forward-slash paths in the private command receipts. Let `OLD` be `build/software-waves/SW-API-READ-03-C1/campaign-02/run` and `NEW` be `build/software-waves/SW-API-READ-03-C1/browser-refresh-20261031/campaign-01/run`:

```text
-m tools.validate check --evidence OLD/evidence --evidence NEW/evidence --run-summary OLD/run-summary.json --expect-clients api
-m tools.validate check --evidence OLD/evidence --evidence NEW/evidence --run-summary NEW/run-summary.json --expect-clients browser
```

Both original, unmixed summaries were consumed unchanged. Both new gate logs report `gate OK (0 known failure(s) linked to open findings)`. The historical single-root `gate-01` exit 1 remains immutable; these are a new evidence-input set after fresh execution, with unchanged gate logic.

Private receipt root: `build/software-waves/SW-API-READ-03-C1/browser-refresh-20261031/`. Each invocation has `launch.json`, `exit.json`, `process.log`, `sha256.json` and immediate private copies. Receipt hashes:

| Invocation | Exit | process.log SHA-256 | exit.json SHA-256 |
| --- | ---: | --- | --- |
| `campaign-01` | 0 | `24e619d17c5ef746a28666f8b97489d74fcc8d126e630f7cc7847f9b9715c21f` | `d07a209497a15fe5494d039b881e99527e9759aff82ee2a1c9f6b9c10700edb5` |
| `gate-api` | 0 | `c18eb6f36ffcb821517c994f8f83f9f27c7481b5273bb7c8bbba1114a57b854d` | `020df039783be4cbc09ff756a4b87c85fb753dbfc083cff5a7ada3948ed67cee` |
| `gate-browser` | 0 | `c18eb6f36ffcb821517c994f8f83f9f27c7481b5273bb7c8bbba1114a57b854d` | `747cfa648ab22015dabcb68dd3dba4d67d86d1221005cec46759b1be43c0d137` |

Original input integrity: all 20 inventoried inputs (original campaign-02/gate-01 files, inherited diagnosis and root route diagnostic) match their pre-execution SHA-256 values. All four source/registry hashes in the original campaign launch metadata also match current bytes. `source-input-comparison.json` and per-invocation original-input comparisons retain the complete comparisons privately.

| Original or new summary / evidence | SHA-256 |
| --- | --- |
| Original WS summary | `2ed63939db118c7c390a780b291b90f5042ae58b3bc04573a90d3fee2325c600` |
| Original WS evidence | `7591de8ce9e152fceb18af12668b9593f6afbba7af2996a4adb4a7c1a089e3b2` |
| New browser original summary | `8320cc158a85759057a721469b65cd8308b770b8b2b511a5657b334451019bbe` |
| Original-input before manifest | `9c7073ebd34f49ce81354b3c0aace673162d6200463def027f1ea8d25e25d9be` |
| Inspection metadata | `e834d8ea63f4516265a309a152e8955be317f10cdf567f9d0bb58d61c7bae87b` |

Coordinator erratum retained: the preceding correction docs check actually used `no:route` and emitted root report-only 8/177 coverage; the archived strict hook-01 177/177 proof is separate. Neither original is restored, relabeled or deleted here.

**Holds:** raw records, summaries, logs and screenshots remain private pending privacy review/admission; synthetic fixture PIN/request data is not published. Qualified different-family source review remains held for unknown DeepSeek capacity; any M3 metadata inventory cannot substitute for it. Coordinator owns preservation, task-ref publication, independent audit, integration and canonical admission. No canonical record/import, registry, findings or ledger changes; no global feature-level qualification, F-API-040/parent-unit/VAL-15 closure, source-review approval, hardware, soak, field or release closure is claimed.

Report-only verification: the five existing documentation modules passed **489 tests, zero failures/errors/skips, exit 0**, with `-p no:tests.route_inventory -p no:cacheprovider`, fresh isolated data/config/TEMP/TMP and forward-slash basetemp/XML paths. Original log/XML/exit receipts were immediately copied and hash-compared. The root route diagnostic remained byte-identical. An invocation-only `git -c core.hooksPath= commit` exception is used for this documentation-only report; no normal source-hook or full-suite success is claimed.

Docs process log SHA-256: `c6f604a8170c232b274bc04e74dcb68db17b75b2b6d20c63f168ba7326282841`; JUnit XML: `9eb68a5bf8a6628027be877f5dbe776890f225e33406eea6fd203ce26b4e63c3`; exit receipt: `8730045edebf43df3c8803fd0084ddb7710c9ea348dbdffec709e9b228590b01`.
