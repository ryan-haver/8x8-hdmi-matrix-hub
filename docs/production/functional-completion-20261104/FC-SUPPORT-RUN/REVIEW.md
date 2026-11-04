# FC-SUPPORT-RUN: independent receipt-fidelity review

2026-11-04. Reviewer: MiniMax (`opencode2/minimax-coding-plan/MiniMax-M3`, thinking),
underlying family **MiniMax**. Author under review: OpenAI Codex `gpt-6.1-sol/high`
(Sol). This is a genuine different-family receipt-fidelity review of a
Sol-authored evidence report. The reviewer is not the author of any artifact
reviewed here.

**Verdict: PASS** for receipt fidelity at exact commit
`abb52542858845cf488a63b01f6ac619f3f38173` (parent
`436af63f44d2c4200c680909221343c9d6b976ae`), with three LOW-severity,
non-blocking findings (F-1..F-3) and four non-blocking refinements (R-1..R-4).
A negative verdict would have been an equally valid successful delivery; none is
required here.

**This review clears no gate.** It is a fidelity review of one prose report. It
awards no model qualification, no HA/packaging domain competence, no source
acceptance, no feature or capability closure, no support or compatibility
promotion, and no release. The report's own **PARTIAL** outcome, its **HOLD**
rows (HACS custom-repository install/upgrade; cookie-contamination/revocation/
malformed/legacy/5xx/recovery/guard-sensitivity controls), its **FAIL** rows
(missing/wrong key on locked hub; options validation; effective key after
reconfigure; checked-in lock installation), and its **HOLD: complete core
validation** are all unchanged and confirmed. Source, domain, owner privacy
budget, hardware, visual, 72-hour soak, field-week, main/tag and final artifact
gates remain exactly as recorded.

## Reviewer independence, scope and conflict disclosure

- The author is OpenAI; the reviewer is MiniMax. Different underlying family,
  as the adopted packet row requires for this M3 receipt-fidelity seat.
- I performed **fidelity checks only**. I checked what the report asserts
  against the original raw receipts, effect JSON, JUnit bytes, Docker/Orca
  records and the exact Git objects. I did not decide whether any HA/packaging
  behaviour is *correct*, whether the product defect the report describes is
  fixed, or whether any gate opens.
- MiniMax is not the subject of any FC-SUPPORT-RUN claim I am asked to clear.
  This review therefore certifies no MiniMax-specific fact, and no
  MiniMax-specific entry gate is discharged here.
- I did not read, and will not be influenced by, any other reviewer's decision
  on this commit.
- No helpers, subagents, alternate models, MCP servers, plugins, new accounts,
  credentials, spend or global configuration changes were used. No Orca
  lifecycle, branch, worktree, image or cache cleanup action was taken.

## Exact inputs under review

| Item | Value | Independent check performed |
| --- | --- | --- |
| Review worktree | `wp-fc26-fc-support-run-review` | directory of this checkout |
| Review branch | `review/wp-fc26-fc-support-run-review` | `git rev-parse --abbrev-ref HEAD` |
| Author commit | `abb52542858845cf488a63b01f6ac619f3f38173` | `git rev-parse HEAD` before my commit |
| Author parent | `436af63f44d2c4200c680909221343c9d6b976ae` | `git log -1 --format=%P` |
| Reviewed path | [REPORT.md](REPORT.md) (sole changed path, added) | `git diff-tree --no-commit-id --name-status -r` |
| Report Git-LF blob | SHA256 `1b84fa7b25d161463906a2c157858e040cfbcb1b899e18e4995be9569d3eb79b`, 22,020 bytes | `git show abb5254:<path>` piped to SHA256, byte-counted |
| Report worktree copy | SHA256 `e32392f5…f6a636`, 22,121 bytes, CRLF | read file bytes; LF-normalized content equals the blob exactly |
| Author registered payload | `…/artifacts/46e9b51573c14941955674ab0afe0cca/payload` (readonly) | 18,239 file entries, 17,327 regular files, 912 reparse points, 2 inaccessible entries |
| Coordinator custody payload | `…/artifacts/6e86d613d6c64ec2aa2f29c909260b6a/payload` (readonly) | `support-delivery.json`, bundle verify stdout, retained manifest |
| My registered payload | `…/artifacts/c2d66bc44d094e24930f538c5dd58db3/payload` | `agent_storage.py begin` result |
| Adopted packet | SHA256 `933166c3925e38e748bb4b78e15bb488c90e43bb12807b2f02ffd65b7ea6f2f4` | recomputed from [FINAL_PACKET.json](../../../agent-process/phases/functional-completion-20261104/FINAL_PACKET.json) in this checkout |
| Author row | FC-SUPPORT-RUN, author Sol `gpt-6.1-sol/high`, reviewer M3 | `FINAL_PACKET.json` staffing entry, cross-checked against [CONSENSUS.json](../../../agent-process/phases/functional-completion-20261104/CONSENSUS.json) and [ADOPTION_NOTES.md](../../../agent-process/phases/functional-completion-20261104/ADOPTION_NOTES.md) |

The report byte-identity note in `final-byte-checks.json` is **accurate and
material**: the committed blob is 22,020 LF bytes
(`1b84fa7b…9d3eb79b`) and the working copy is 22,121 CRLF bytes
(`e32392f5…f6a636`). I confirmed the LF-normalized bytes are identical, so the
distinct worktree hash is a checkout-encoding artifact, **not** a content
change. The report's own `initial_byte_identity_assertion` records that a
byte-identity assertion failed on CRLF versus Git LF with no prose change and no
commit attempted by the failed assertion — an honest disclosure.

## Method

I read the full report, then independently re-derived each consequential
outcome from original receipts rather than accepting the report's assertion:

- image and manifest resolution (`ha-*-manifest.stdout`, `ha-*-pull.json`,
  `ha-*-image.stdout`, `images-pinned.json`);
- in-runtime interpreter and distribution metadata (`ha-floor-python.stdout`,
  `ha-current-python.stdout`, `ha-floor-pypi.stdout`, `py311-identity.stdout`);
- every HA case effect (`ha-floor-live.json`, `ha-current-live.json`,
  `ha-*-resume.json`, `ha-*-resume-effects.json`, `ha-*-inrun-final.json`,
  `ha-*-config/.storage/core.config_entries`);
- the HACS archive, extracted tree and the genuine HACS code path
  (`hacs-2.0.5.zip`, `hacs-extracted-verified.json`, `hacs-code/config_flow.py`);
- the Python 3.11 install/lock/core-run chain (`py311-dev-lock.stderr`,
  `py311-install.*`, `py311-metadata-install.stdout`, `py311-pipcheck.stdout`,
  `py311-installed-runtime-origin-control.stdout`,
  `py311-installed2-runtime-inrun.json`, `py311-core-inrun.json`,
  `py311-core.xml`, `core-root/route-coverage.json`, `core-population.json`);
- the source-linked causal claims, read at the reviewed commit
  ([config_flow.py](../../../../custom_components/hdmi_matrix/config_flow.py),
  [api.py](../../../../custom_components/hdmi_matrix/api.py),
  [__init__.py](../../../../custom_components/hdmi_matrix/__init__.py),
  [security.py](../../../../src/rest_api/security.py));
- custody, containers, settlement and storage
  (`dispatch.stdout`, `ha-*-create.json`, `ha-*-inspect.stdout`,
  `ha-*-removed-proof.json`, `final-owned-containers.json`,
  `storage-receipt.json`, `logs/storage-retain.*`);
- the coordinator custody and the rejected-cleanup record
  (`support-delivery.json`, `bundle-verify.stdout`, `worker-release.stdout`,
  `rejected-cleanup.json`, `original-retained-manifest-private.json`).

I did not follow, read, repair or remove any test-created Linux symlink or
Windows reparse entry in the author payload, exactly as instructed.

## Verified outcomes

The following report claims were confirmed against original receipts and are
**faithful**:

- **Immutable runtime selection.** The three index digests
  (`7db850ef…`, `c6c1ca99…`, `db20d850…`), the three selected
  linux/amd64 manifests (`473cc062…`, `078222f9…`, `6d10e720…`), the
  interpreters (3.13.1 / 3.14.10 / 3.11.18) and the Docker inspect sizes
  (608,572,015 / 673,151,569 / 45,621,338) all reproduce exactly from the
  preserved streams. Pulls were by index digest with `--platform linux/amd64`;
  **no public mutable tag was executed as a digest**, and the report says so.
- **Metadata versus actual runtime.** HA 2025.1.0 upstream metadata *and* the
  installed distribution both declare `Requires-Python >=3.12.0` while the
  official image runs 3.13.1; current installed metadata declares `>=3.14.2`.
  The report keeps official metadata retrieval and actual image runtime
  distinct, and the `2025.1.0` (not `2025.1.4`) pin is exact.
- **Ordering.** Stable metadata was fetched at `20:15:48.305235Z` and returned
  `2026.11.0` as the current default; the last of the three manifest
  resolutions closed at `20:15:49.229671Z`; the first pull started at
  `20:16:40.579768Z`. The report's "all manifest resolutions completed before
  execution" is exact.
- **Locked-credential outcomes versus bare auth-status controls.** On the
  locked hub, bare `GET /api/auth/status` returned `session_level` `none` for
  missing and wrong keys and `control` for the valid key, with
  `control_pin_set=true` — while all three config flows (wrong, missing,
  valid) created entries and reached `loaded` on **both** HA versions. The
  report's FAIL row and its "HA's probe did not validate these distinct
  credentials" are exactly what the receipts show.
- **Options validation.** The explicit `fc-disposable-invalid` option with
  `scan_interval` 5 was accepted and the entry stayed `loaded`; the persisted
  options still contain the invalid key. Confirmed in both versions.
- **Effective key after reconfigure.** `reconfigure_successful`, `data.api_key`
  became `fc-disposable-valid` while `options.api_key` remained
  `fc-disposable-invalid`. The precedence claim is **source-linked and true at
  the reviewed commit**: `custom_components/hdmi_matrix/__init__.py` reads
  `entry.options.get(CONF_API_KEY, entry.data.get(CONF_API_KEY))`, and
  `config_flow.py` never reads `auth-status` while `api.py` accepts only
  `success`/`data` envelopes whereas `src/rest_api/security.py` returns bare
  JSON. The report's "existing setup chooses the options override" is correct.
- **Unload/reload and restart identity.** The supported WebSocket disable/enable
  produced `not_loaded` then `loaded` on the current server and in the floor's
  locked-hub continuation. The floor's **initial HTTP POST attempts returned
  405 and are retained as operator API errors, not product unload failures** —
  confirmed verbatim in the floor live cases. Both original containers restarted
  with Docker direct exit 0, and later authenticated `/api/config` plus entry
  inventory confirmed the same entry IDs loaded.
- **Offline continuation.** With only the disposable simulator stopped, a
  valid-key flow produced `setup_retry` with
  `/api/status: Matrix not connected (HTTP 503)` on both versions; the report
  does not claim offline polling or reconnect recovery.
- **Zero-write observation.** The locked/offline continuation proxies captured
  exactly **32 floor + 28 current** hub requests, **all GET**, **no cookies**,
  **no guard rejections**; the simulator logs held **56 records each** with
  **zero `mutated=true`**. The report explicitly states the guard was **not**
  separately sensitivity-tested and that the observation is not proof for
  unobserved intervals or write behaviour. The remaining cookie/revocation/
  malformed/legacy/5xx/recovery controls stay **HOLD**.
- **HACS boundary.** Release metadata selected 2.0.5; I independently
  recomputed the retained `hacs-2.0.5.zip` as **19,021,117 bytes, SHA256
  `97be6b824a4f38e683728cc6dd72367f6b8bad0a43428b1b3b987a3087adf413`**, matching
  both the report and the GitHub asset size. Extraction was verified
  file-by-file against the retained archive (2,260 files; 48,047,695 extracted
  bytes) with no absolute/parent paths and no ZIP symlinks. On floor HA the
  genuine HACS code returned its four-acknowledgement user form, and the
  unmodified next step does call `GitHubDeviceAPI` register/activation and
  persist `activation.access_token`. `hacs/repositories/add` returned
  `unknown_command` while unconfigured. On current HA the config-flow
  initialization returned HTTP 404 `Invalid handler specified`, and the HA log
  shows built-in `homeassistant.components.marketplace` attempting to remove
  the read-only HACS mount — no trust check or mount protection was modified.
  **No custom-repository install and no upgrade is claimed.**
- **Public prior release.** The release list contains prerelease `v0.1.0` with
  **zero attached assets**; its public HA manifest reports component version
  `1.0.0` while this exact source reports `1.0.0rc1`. The report explicitly
  declines to claim a previous source is absent and claims no suitable
  same-target upgrade sequence — no "no previous release" overclaim, and no
  default-store listing counted as install/upgrade.
- **Python 3.11.** The checked-in lock install failed with direct exit 1
  because `pyee==14.0.0` requires Python `>=3.12` (exact stderr preserved); no
  pin or hash was removed or changed. The independent metadata install is
  distinct from the locked pass (pyee 13.0.1, aiohttp 3.14.5, pip check exit 0).
  The `--no-deps` build's immediate missing-dependency pip check and import
  failures are retained (four missing distributions; `ModuleNotFoundError:
  aiohttp`). The shipped `/usr/local/bin/orei-matrix-driver` produced real
  health/info, healthcheck exit 0, orderly stop exit 0 and a stopped
  healthcheck exit 1 connection-refused negative control; early health showed
  the matrix not yet connected, which the report states. In-run package origins
  are from `site-packages` and are separate from the source-mounted core run.
  The first smoke's observer file was overwritten by a healthcheck child and
  is explicitly not treated as runtime-origin proof; the corrected second
  observation disabled observer output only for the healthcheck children. The
  post-run installed-byte comparison exited 1 with **91 matched** shipped
  files and exactly the blanket-mapping expectation of an unshipped top-level
  `src/__init__.py` — retained as an inventory mismatch, not a changed module.
- **Core execution.** Exactly one invocation of the recorded argv; direct exit
  1 from `20:21:04.746473Z` to `20:39:26.690667Z`; stdout 2,787,454 bytes and
  stderr 3,566 bytes preserved; terminal summary
  `1 failed, 48 passed, 35 deselected, 2725 warnings, 8225 errors in 1100.05s`.
  Independent JUnit re-parse: **4,162 testcase elements, 4,161 unique nodes**,
  the single duplicate being `hil_tools.test_capture_read::test_cli_options_mapping`
  for its failure and teardown; **one failure element, 4,112 setup-error and
  4,113 teardown-error elements, zero skipped**. Every error element is
  `FileNotFoundError`; the first failing trace is pytest/contextlib capture
  handling and stderr ends in `_pytest/capture.py` `tmpfile.truncate()`
  `FileNotFoundError`. The report correctly treats 8,225 as **phase events, not
  8,225 tests**, and infers no product regression or full-suite pass.
- **Route evidence.** `core-root/route-coverage.json` is strict and reports
  **9/177 (5.1%), 168 uncovered**. The stock recorder stayed enabled, its
  rootpath was redirected to the owned `/evidence/core-root` with
  `/source/pyproject.toml` preserved as inipath, and no canonical route output
  or ledger was regenerated (the `docs/validation` tree is byte-identical
  between parent and commit).
- **Tool bounds.** Ruff and Mypy ran once each as metadata-resolved, bounded
  checks (exit 0; `All checks passed!`; `Success: no issues found in 92 source
  files`). They are not presented as all CI jobs or as Python 3.12 lock proof.
- **Initial failures remain explicit.** The floor's 120-second wrapper timeout
  is recorded as a wrapper sentinel 124 (not a direct child exit 124), the
  current run's authenticated readiness timeout is recorded as a **direct exit
  0** that does *not* mean all cases passed, the interrupted floor observation
  and its reason are preserved, and the 405 operator errors are retained. No
  silent unchanged failed retry and no fabricated raw original was found.
- **Source/config/sole-report boundary.** The commit adds only `REPORT.md`;
  `git diff --exit-code` over `src`, `tests`, `tools`, `custom_components`,
  `pyproject.toml`, `requirements*.txt`, `docs/validation` and the allocation
  ledger is empty. The accepted `9b783d72` product tree is unchanged, the
  accepted `e542` component remains unwired (`ws_request_work.py` is present
  and unreferenced by `src/rest_api/app.py`), and the scoped
  `.codex/config.toml` (`multi_agent = false`, SHA256 `92207a5a…`) remains
  untracked and unstaged.
- **Custody and settlement.** Container IDs chain create → pre-stop inspect →
  stopped inspect without change; the label-scoped final `docker ps -a` is
  empty; removal proofs are empty; shared images/caches were never pruned. The
  extracted-HACS duplicate cleanup was **rejected by automatic approval as
  `blocked by policy`**, with `bytes_removed: 0`, the tree still present
  (2,260 files) and **no bypass or retry**.
- **Storage and the report's own accounting.** The report cites
  `storage-receipt.json` for final logical bytes, generated runtime layers,
  retention and outside-payload outputs, states the review date **2026-12-04**,
  records that test-created symlinks/reparse points were recorded **without
  being followed**, keeps diagnostic streams below the 100 MiB budget
  (6,338,091 bytes of logs+JUnit), and separates Docker logical layer sizes
  from unmeasured physical reclamation. The retained
  `hacs-2.0.5.zip` (19,021,117 bytes) and extracted tree (48,047,695 bytes)
  are reported as separately accounted runtime assets, not workspace copies.

## Findings

| ID | Severity | Exact source location | Violated invariant and impact | Reproduction/evidence | Author-owned correction | Current disposition |
| --- | --- | --- | --- | --- | --- | --- |
| F-1 | LOW | [REPORT.md](REPORT.md) line 22, "**PASS: environment/isolation.** … Host C: free 1,012,058,304,512 bytes." | An environment figure is stated as an observed fact inside a PASS row, but no receipt in the author payload measures free space. The only occurrence of the value is the author's own literal in `pull.py` written into `runtime-layer-plan.json`. Impact: the isolation verdict itself is unaffected (read-only mounts, no private data, unique container names/labels and untouched shared caches are separately receipted), and no acceptance outcome depends on this number; the defect is that a plan-time input is presented as a measurement. | Searched every receipt in `46e9b51573c14941955674ab0afe0cca/payload/logs` for a free-space command (`Get-PSDrive`, `disk_usage`, `fsutil`, `Get-Volume`, `Win32_LogicalDisk`) — none exists; `1012058304512` occurs only in `pull.py` and `runtime-layer-plan.json`. | Either attach a free-space measurement receipt for the quoted figure, or re-label the number as the pre-pull plan input it is. No re-execution or source change needed. | Non-blocking. Recorded for the author; does not affect the verdict or any gate. |
| F-2 | LOW | [REPORT.md](REPORT.md) line 22, "initially 60 stopped and zero running containers." | The count "60 stopped" is presented as a container census, but its source is `docker system df`'s **Containers TOTAL** column (`Containers 60 0`), not an enumeration. The same payload's `docker ps -a --no-trunc --format {{json .}}` census, taken ~57 seconds earlier on the same daemon, enumerates **24** containers, all `exited`. Impact: "zero running" is fully correct and independently corroborated by both receipts; only the "60 … stopped" denominator is not a per-container census, and publishing a count without its population conflicts with this repository's standing rule to publish definitions and denominators for each count. | `logs/docker-disk.stdout` → `Containers 60 0` (TOTAL, ACTIVE); `logs/docker-containers.stdout` → 24 parseable JSON rows, `State` all `exited`, running 0, last line a complete JSON object. | State the `docker system df` TOTAL/ACTIVE semantics explicitly and cite the `docker ps -a` enumeration (24 exited, 0 running) as the separate census, or drop the "60 stopped" phrasing. No re-execution needed. | Non-blocking. Recorded for the author. |
| F-3 | LOW | [REPORT.md](REPORT.md) line 24, "root directory inventory was ordinary directories." | The clause asserts a directory-level inventory that no receipt records. `source-safety.json` and the `prereq`/`prereq2` scripts enumerate only **tracked file paths** from `git ls-files` and test each for reparse/symlink attributes; they do not enumerate the source root's directories. Impact: the adjacent, load-bearing claims (4,882 tracked paths, no file reparse points, read-only mounts, no private runtime data) are exact; only this sub-assertion is unreceipted. | `source-safety.json` → `{"tracked_paths": 4882, "reparse_points": [], "root": …}`; `prereq2.py` iterates `git ls-files -z` only; no receipt enumerates root directories of the source checkout. | Restrict the sentence to what `source-safety.json` records (tracked paths and their reparse status), or attach a directory inventory receipt. | Non-blocking. Recorded for the author. |

No finding changes a reported outcome, a PASS/FAIL/HOLD/PARTIAL verdict, or any
gate. No invented receipt, fabricated raw original, silent retry, mutable tag
executed as a digest, domain acceptance, or source change was found.

## Non-blocking refinements

- **R-1 (wording).** Line 22's "Engine routes Docker Hub through its ordinary
  Desktop proxy" is a Desktop-internal behavior; the preserved
  `docker info` receipt directly evidences only `RegistryConfig.Mirrors: []`,
  a `docker.io` IndexConfig with `Mirrors: []`, the local
  `hubproxy.docker.internal:5555` IndexConfig, `NoProxy:
  hubproxy.docker.internal` and null daemon `HTTPProxy`/`HTTPSProxy`. Citing
  those observed fields would keep the statement fully receipt-anchored.
- **R-2 (wording).** Line 57 describes the flow probe as reading
  "health/device"; the receipts show `config_flow._probe` awaiting
  `client.health()` and then `client.device()`, with the device MAC used for
  the unique id. Naming both endpoints precisely removes an implicit
  inference.
- **R-3 (wording).** Line 44's "`python -m homeassistant --config /config`"
  is the invocation; the recorded in-run `argv[0]` is
  `/usr/src/homeassistant/homeassistant/__main__.py`. Both describe the same
  command; quoting the recorded argv verbatim would remove the paraphrase.
- **R-4 (scope clarity, already honest).** Line 97 correctly states the
  coordinator's inventory was a *later* measurement than the author's
  `storage-receipt.json`, but the report does not itself restate the two byte
  totals, so no reconciliation is owed by the report. The reconciliation is
  supplied in this review below.

## Custody reconciliation (measurement timing and population, not fabrication)

The brief asked me to explain the difference between the author's
`storage-receipt.json` figure (**143,590,938 bytes / 17,325 regular files**)
and the coordinator's later inventory (**143,680,593 bytes / 17,327 files /
912 unfollowed links**). I reproduced the later figure independently and
reconciled both. **There is no fabrication and no missing evidence:**

1. **The author's measurement is a labelled lower bound taken before its own
   final two files existed.** `closeout.py` walks the payload, then writes
   `storage-receipt.json` (62,004 bytes) and `completion-receipt.json`
   (27,651 bytes) *into that same payload*. The field is named
   `retained_payload_regular_file_bytes_at_measurement`. Adding the two
   receipts gives 62,004 + 27,651 = **89,655 bytes** and **2 files**; the
   coordinator's inventory measured the payload *after* they landed:
   143,590,938 + 89,655 = **143,680,593**, and 17,325 + 2 = **17,327**.
2. **My independent scan agrees with the coordinator exactly.** Walking the
   payload without following any reparse point I measure **17,327 regular
   files totalling 143,680,593 bytes**, plus **912 reparse points** (all
   `core-tmp/*current` test-created entries) and **2 inaccessible entries**
   (`core-tmp/installed-runtime{0,1}/venv/lib64`). 17,327 + 912 = 18,239
   file entries, matching the coordinator's manifest file count.
3. **The link-count difference is a population definition, not a gap.** The
   author's `links_not_followed` has 914 entries (the 912 reparse points plus
   the 2 inaccessible `lib64` directories), while the coordinator's manifest
   records 912 reparse points and the coordinator's resumed inventory treated
   the 2 inaccessible directories the same way — not followed, not repaired, not
   removed. The coordinator's continuation helper reproduces the original
   `WinError1920` condition I hit independently on
   `core-tmp/flic_live_stackcurrent` (`os.stat` → `WinError 1920`, while
   `os.lstat` succeeds and reports reparse attributes 1056), and the resumed
   inventory records reparse/inaccessible entries without following them and
   runs no tests and no source command.
4. **No cleanup authority was used.** The rejected HACS duplicate deletion was
   not retried or bypassed; the coordinator payload contains no `checkout`,
   `reset`, `merge`, `rebase` or `cherry-pick` and no pytest execution.

## My own verification run (this review, once)

Per the review brief I ran the five mandated documentation modules **once** in
this review checkout with the absolute root-venv interpreter, inherited Windows
environment overlaid with fresh owned roots, and `-p no:tests.route_inventory
-p no:cacheprovider`. Full argv, cwd, UTC start/end, direct exit, complete
stdout/stderr bytes, JUnit result and in-run module origins are retained in my
payload (`docs-receipt.json`, `docs.stdout`, `docs.stderr`, `docs.xml`,
`docs-inrun.json`).

- cwd: `C:\Users\ryanh\orca\workspaces\unfoldedcircle-orei-hdmi-matrix-integration\wp-fc26-fc-support-run-review`
- interpreter: `C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\.venv\Scripts\python.exe` (Windows CPython 3.12.10), `-B`
- fresh owned roots: `TEMP`/`TMP`/`TMPDIR`, `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `--basetemp` and `--junitxml`, all inside my registered payload; the payload plugin directory was the only `PYTHONPATH` addition
- direct exit: **0**; stdout **588 bytes**, stderr **0 bytes**
- stdout summary: `489 passed in 3.07s`
- JUnit: `tests=489, errors=0, failures=0, skipped=0`, 489 testcase elements
- in-run origins (captured by the `run_origins` plugin inside the live pytest
  session, never by a post-run probe): all five target modules and
  `tests/conftest.py` resolve inside **this review checkout**;
  `rootpath` and `inipath` are this checkout and its `pyproject.toml`;
  **zero** origins point at the author checkout or at `C:\scripts`
- no retry was performed and no unchanged failed check was re-run.

These five modules are prose checks and confer **no** route, ledger, feature,
support or domain proof.

## Read limits and negative controls

- I did not follow, read, repair or remove any of the 912 reparse points or 2
  inaccessible entries in the author payload, and I did not delete anything.
- I did not re-run the author's HA, HACS or Python 3.11 workloads: the review
  is a receipt audit, and re-execution would create a second evidence
  population rather than verify the first. The author's original failures were
  re-read from preserved bytes, never re-litigated by re-running them.
- I did not verify the underlying **product** behaviour beyond what the
  preserved receipts show, and I did not assess the HA/packaging effect of any
  observed failure. The source-linked claims I checked were read at the
  reviewed commit from the paths named above.
- Docker state was read-only. My own `docker ps -a` / `docker system df`
  observations are later than the author's window and are used only to
  characterise population semantics (see F-2), never as author evidence.
- "Loaded", "reached `loaded`", "healthy" and similar terms are the author's
  observed HA/entry states. I confirm they were recorded; I do not certify
  them as correct product behaviour.
- Missing evidence stays missing: cookie contamination, issued-then-revoked
  credentials, malformed/legacy/5xx auth-status fixtures, reconnect recovery
  and guard sensitivity remain **HOLD**; the "60 stopped" denominator remains
  a df TOTAL, not an enumeration; the free-space figure remains unreceipted.
- I read no other reviewer's decision on this commit.

## Final decision

**PASS** for receipt fidelity of [REPORT.md](REPORT.md) at
exact commit `abb52542858845cf488a63b01f6ac619f3f38173` (parent
`436af63f44d2c4200c680909221343c9d6b976ae`), with LOW-severity non-blocking
findings F-1..F-3 and refinements R-1..R-4 recorded above for the actual
author.

Fidelity PASS means only that **the report faithfully represents the
receipts it cites**. It does **not** mean:

- HA 2025.1.0 or current HA support is qualified, or any support promise is
  established;
- the missing/wrong-key, options-validation, effective-key or lock-install
  failures are fixed, or the product defect the report describes is closed;
- HACS custom-repository install or upgrade is established, or the
  cookie/revocation/malformed/legacy/5xx/recovery/guard-sensitivity controls
  are exercised;
- complete core validation, the strict 9/177 route gate, Python 3.11
  packaging or lock support, canonical route/ledger evidence, feature or
  capability closure, source acceptance, or compatibility promotion is
  granted;
- any owner privacy-budget, hardware, visual, 72-hour soak, field-week,
  main-merge, tag or final-artifact gate is waived;
- the report's own "necessary later correction" (a strict auth-status reader
  and common effective-key validation/override handling with qualified review
  and discriminating controls) is implemented, reviewed or accepted.

Those remain exactly as the report and the adopted packet record them, and
still require their own qualified source and domain review. No assessment
retake and no new judge is implied by this review.
