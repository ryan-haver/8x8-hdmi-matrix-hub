# R8B independent follow-up review

**Disposition: hold runtime release. R8-01 is corrected in the focused source
and image checks; R8-02 remains open at the rollback cleanup deadline.** The
original six desired-behavior cases now pass without xfail or skip, but a new
actual-socket reproduction fails in both source and the new immutable image.
This completes the review and reproduction assignment, not product acceptance.

## Source, identity and immutable image

Reviewed on 2026-10-19 UTC in the fresh Orca child:

```text
C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-runtime-postfix-independent-review
```

Initial and production HEAD is `e58a56b208dea99866edcc3b94a31233fc0f79a8`, the
actual current `wp-runtime-completion` tip when dispatched. The tracked checkout
was clean before the single build; only ignored `build/r8b/` evidence had been
created. Initial/prebuild Git status commands printed no changes; PowerShell's
empty `git status | Set-Content` pipeline did not materialize the requested
status file, so there is no separate raw prebuild-status file. This limitation
is retained in `audit-first.txt`; later byte parity independently verifies the
production inputs. No historical reset or other-checkout edit occurred. Production changes
relative to `4adbc136a4c1fb6be4b20b58530a47dd521efac8` are confined to
`hub/persistence/startup.py` and `hub/runtime/composition.py`:

- R2D: `def66d262fbdf8e7f09be0bd92df1710c7fb3e3d`, merged at `e58a56b2`.
- R1G: `c2e02f00b0e3d77b471a9b2a86bab228de877dbc`, merged at `92b507d1`.

Orca `worker-show --dispatch ctx_5ef48bc11df3 --json` records requested **and
effective** agent `codex`, model `gpt-6-astra`, effort `high`. These are Orca
control-plane observations, preserved in `build/r8b/orca-launch.json`. The session
identity is generic OpenAI Codex based on GPT-6; it does not independently attest
the backend model/effort. No Anthropic, secondary, helper, nested or fallback
agent ran. No applicable `AGENTS.md` was found in this checkout or its ancestors.

Read the current [runtime contract](../planning/RUNTIME_CONTRACT.md), original
[independent review](RUNTIME_INDEPENDENT_REVIEW.md),
[runtime validation report](RUNTIME_VALIDATION_REPORT.md), and the coordinator's
root evidence `build/runtime-completion/r1g-worker-evidence/R1G_REPORT.txt` and
`r2d-worker-evidence/report.txt`. Their earlier green counts were treated as
scoped history, not substituted for this review's execution.

One image was built before editing tracked review files:

```powershell
docker build --platform linux/amd64 --build-arg VERSION=1.0.0rc1 --label org.opencontainers.image.revision=e58a56b208dea99866edcc3b94a31233fc0f79a8 -t hub-r8b-e58a56b2-ctx5ef48 --iidfile build/r8b/image-id.txt .
```

Build exit: 0. Immutable image ID:

```text
sha256:f398fbf0aa9ee9ede4e4fa042243b5253b6722f24a3b06577896c48b6157355a
```

Inspection reports Linux/amd64, null entrypoint and command `["python","run.py"]`.
OCI labels include version `1.0.0rc1`, revision `e58a56b208dea99866edcc3b94a31233fc0f79a8`,
title `8x8 HDMI Matrix Hub`, license `MPL-2.0`, source
`https://github.com/ryan-haver/8x8-hdmi-matrix-hub`, and description
`REST API, web UI, kiosk and integrations for 8x8 HDMI matrix switches`.
The version matches current `src/hub/__init__.py`. Full inspection/build output
is in `image-inspect.json` and `docker-build.log` under `build/r8b/`.

Independent read-only image inspection matched **257/257 tracked shipped input
files** against actual working-tree bytes, not Git blobs affected by CRLF
conversion. `production-image-parity.json` contains both complete hash maps;
`parity-command.json` records the one temporary hash-inspection container, which
uses a Python entrypoint override only for reading bytes, not behavioral proof.
All behavioral image tests use the image's unchanged normal command, bind only
synthetic disposable `/data`, and connect to actual HTTPS/Telnet Simulator
sockets through Docker Desktop's `host.docker.internal`. No app source is
mounted. UC-on starts the real SDK; Flic, HA and UC mDNS are disabled here.

Actual working-tree SHA-256 values (also matching the shipped copies for source):

| File | SHA-256 |
| --- | --- |
| `src/hub/persistence/startup.py` | `1102b2800bb3b3c2634da8521519ad70a89017947cc789d020d1a09892b8ae6b` |
| `src/hub/runtime/composition.py` | `62cc68fd96f3344b2e80ee40474f1c41b35d981153d48d907fcc12b295a10d82` |
| `run.py` | `701c5a99e33040913c99078956d09c86dfa0c6cd00177d3c9ff7272d9fe1444f` |
| `Dockerfile` (build input) | `aff58889f4d0aec937b3b8a7cd13cd0370ed280fe0bbf9cf1a4130c0554baa5b` |

Module-origin checks resolve composition, persistence startup, transport and
simulator modules to this child checkout. Python uses the existing dependency
environment at `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
with this child cwd and process-local `PYTHONPATH=<child>/src;<child>`.
No installation or global configuration change occurred.

## R8-01 disposition: focused correction accepted

The production delta permits legacy output-state sources to coexist with a new
unified scene catalog only after validating the profile catalog and matching
its import digest to the config-side legacy source. For a split layout, that
source must also match the complete parsed data-side source. This accounts for
the old-location importer's whitespace reserialization while retaining unknown
content. Provenance represents ancestry: later profile edits, PIN rehashes and
intentional deletions must remain authoritative.

The proof runs in preflight, before imports/default writers could manufacture
provenance. Standalone scene readers use a resolved-data-path binding created by
successful preparation, revalidate on-disk proof, and lose that binding when
explicit re-preparation starts. A different prepared volume cannot authorize
the target installation. Existing canonical validation and unified-source
conflict checks remain in place. No consequential remaining R8-01 defect was
demonstrated in this focused review.

Both shared/separate source layouts pass the original desired behavior. Both
normal-image UC modes now start, list the migrated profile, create with HTTP
201, restart within the unchanged six-second bound, list both catalogs and
execute the new scene with HTTP 200/success. Original legacy source and backup
bytes remain identical; profile and unified catalog bytes do not change on
restart. Execution may legitimately append history/update `last_executed`, so
the canonical scene-byte restart assertion precedes execution.

The 203-case focused regression selection includes the R2D actual normal
`run.py` subprocess tests for both layouts and UC modes, repeated preparation,
profile edits/deletion/PIN rehash, private-field retention, corrupt/future
catalogs, missing/wrong/malformed provenance, changed sources, mixed shapes,
unimported coexistence, cross-installation isolation and blocked writes.
This is bounded acceptance of R8-01, not a complete fresh release campaign.

## R8-02 disposition: original trigger corrected, timeout boundary still high

**Remaining finding R8B-01, within R8-02: rollback cleanup timeout abandons
automatic recovery. Owner: runtime composition; release blocker.**

The R1G delta correctly hands a returned false rollback result to the existing
transport's optional callable `start_auto_reconnect()`, only when not stopping.
It adds no runtime retry loop. The original two-immediate-503 trigger now
recovers automatically in source and image. Focused regressions also pass for
changed-address credential/config rollback, cancellation of the candidate,
shutdown during rollback/backoff, following reconfigure, disabled reconnect,
initial-offline startup and structural clients lacking the optional seam.

The remaining trigger is a slow rollback failure:

1. Start connected against the actual Simulator, then reconfigure the same
   address. Inject exactly two login HTTP 503 responses.
2. Deliver the candidate's 503 immediately. Dispatch the third overall login
   (the old client's rollback attempt) normally, consuming the second fault,
   but hold delivery of its response on an `asyncio.Event` in the Simulator.
3. Keep the production `CLEANUP_TIMEOUT = 5.0` unchanged. Await reconfigure's
   failed result, which arrives when `_cleanup(rollback)` cancels the rollback
   waiter at that deadline. Runtime is not stopping.
4. Release the actual socket response. All faults are already cleared. The
   original transport's shielded connection attempt finishes false, but there
   is no reconnect supervisor. Observe automatic recovery only; no manual
   reconnect occurs within the acceptance window.

Source reproduction verifies restored original address/client/effective
credentials, unchanged saved configuration, a live refresh task and no candidate
session/connect/reconnect/Telnet owner. It then drains the shielded failed login
and observes two seconds without recovery at the original 20–40 ms test retry
delays: `_reconnect_task is None`, exactly three logins. No retry delay or
production cleanup bound was weakened.

The normal immutable image reproduces the same failure without production
monkeypatching. In `timeout-source-image-tmp`'s image log, rollback login begins
at `07:51:23.182`, cleanup times out at `07:51:28.183`, and its released HTTP 503
arrives at `07:51:28.186` UTC. Twelve seconds of health polling remain
disconnected. Only the subsequent diagnostic manual connection request at
`07:51:40.205` starts another login and authenticates immediately. Manual success
is explicitly excluded from the automatic-recovery oracle. The two new tests
fail at the final desired-behavior assertions, not fixture setup.

Cause: `composition.py`'s reconnect handoff is after the await at line 501.
The five-second `_cleanup` wrapper cancels that waiter before the new handoff
can execute. `OreiMatrix.connect()` shields its single-flight inner attempt;
the late false result has no consumer that starts retries. `_cleanup` logs and
swallows the timeout, and the resumed refresh worker skips disconnected state.
Longer ordinary polling cannot repair the missing owner.

No production fix was made. The coordinator acknowledged the finding and will
assign a fresh R1H owner. Correction must keep bounded cleanup, cancellation
propagation, shutdown fencing, address-bound credentials and one transport
reconnect owner, including a still-pending shielded attempt. Raising the cleanup
timeout or accepting manual recovery would not close this finding.

## Executed checks and preserved history

The owned files are this report, the minimal corrected-expectation/image-target
and behavioral strengthening in [test_runtime_review_r8.py](../../tests/test_runtime_review_r8.py),
and [test_runtime_review_r8b.py](../../tests/test_runtime_review_r8b.py).
The new timeout tests remain ordinary failing desired-behavior tests, without
xfail/skip markers, for the next owner to correct. Existing production and all
other existing tests are untouched.

Original pinned strict-xfail reproductions remain available at
**`dfbd87cd2af8df9e8a104e801f341f5738f42a41`**. The original
`RUNTIME_INDEPENDENT_REVIEW.md`, its failed source/image evidence, historical
candidate `4adbc136a4c1fb6be4b20b58530a47dd521efac8` and old image
`sha256:1a5de3b5b58a3e1c56d3269bd5c1c6e3e12be2d6fea1abceea36067d733df69e`
remain historical, not accepted or relabeled. Current Docker cases require an
explicit immutable `R8_REVIEW_IMAGE`; absent configuration fails with a clear
prerequisite and cannot count as proof. All obsolete original strict-xfail
markers were removed only after independently observing corrected source behavior.

All commands below run in the child checkout. `PY` abbreviates the absolute
interpreter above, invoked with PowerShell `&`; it is not a newly installed tool.
Set process-local environment first:

```powershell
$env:PYTHONPATH = "$($PWD.Path)/src;$($PWD.Path)"
$env:R8_REVIEW_IMAGE = 'sha256:f398fbf0aa9ee9ede4e4fa042243b5253b6722f24a3b06577896c48b6157355a'
```

Each pytest command uses `-q --tb=short -p no:tests.route_inventory`, plus
`--junitxml=build/r8b/<stem>.xml --basetemp=build/r8b/<stem>-tmp`, with output
and numeric exit saved as `<stem>.txt` and `<stem>-exit.txt`.

| Exact pytest arguments before those common flags | Stem | Result |
| --- | --- | --- |
| `-m pytest tests/test_runtime_review_r8.py --runxfail` | `source-before` | 3 passed, 3 image cases deselected; 1.26 s; exit 0; before tracked edits |
| `-m pytest tests/test_runtime_review_r8.py -m 'not hardware'` | `six-cases` | 4 passed, 2 failed; 14.59 s; exit 1; initial misplaced post-execution byte oracle, retained |
| `-m pytest tests/test_runtime_review_r8.py -m 'not hardware'` | `six-cases-corrected` | **6 passed, zero failed/error/xfail/skip**, 14.39 s; exit 0; all three source and all three image cases |
| `-m pytest tests/test_runtime_review_r8b.py` | `timeout-source` | 1 failed at automatic-recovery assertion; 7.94 s; exit 1; before adding image case |
| `-m pytest tests/test_runtime_review_r8b.py -m 'not hardware'` | `timeout-source-image` | **2 failed**, 27.91 s; exit 1; source and current image confirm remaining defect |
| `-m pytest tests/test_runtime_review_r8.py tests/test_runtime_review_r8b.py -m 'not hardware'` | `final-eight` | Final formatted test tree: **6 passed, 2 failed**, 41.84 s, exit 1; zero errors/xfails/skips; not a green combined run |

Focused regression command:

```text
PY -m pytest tests/test_runtime_legacy_scene_restart_r2d.py tests/test_runtime_rollback_reconnect_r1g.py tests/test_runtime_persistence_isolation_r2c.py tests/test_runtime_persistence_readers_r2.py tests/test_runtime_shutdown_r1.py tests/test_runtime_transport_drain_r1c.py tests/test_runtime_uc_transaction_r3b.py tests/test_runtime_uc_setup_r3.py tests/test_runtime_uc_outage_r3d.py -q --tb=short -p no:tests.route_inventory --junitxml=build/r8b/targeted.xml --basetemp=build/r8b/targeted-tmp
```

Result: **203 passed**, 56.93 s, exit 0, no fixture errors or skips. The imported
R1G fixture in the new review file is explicitly re-exported for pytest; all
selected fixture setup succeeded. This did not repeat the full product/source
1506, dedicated HA/UI or multiarch campaigns. The route-inventory plugin is
disabled locally to avoid writing partial shared route evidence.

Scoped final static checks, all exit 0:

```text
PY -m ruff check src/hub/persistence/startup.py src/hub/runtime/composition.py tests/test_runtime_review_r8.py tests/test_runtime_review_r8b.py
PY -m mypy --follow-imports=silent src/hub/persistence/startup.py src/hub/runtime/composition.py tests/test_runtime_review_r8.py tests/test_runtime_review_r8b.py
PY -m black --check tests/test_runtime_review_r8.py tests/test_runtime_review_r8b.py
git diff --check
```

Initial Ruff import-order and Black formatting checks were unsuccessful and
remain in `ruff-first.txt`/`black-first.txt`; only owned test formatting changed.
The first strengthened image run's two assertion failures are preserved rather
than overwritten. A read-only command also mistyped a truncated pytest temp
directory name; the subsequent exact-path read confirmed execution history was
the byte difference. None of these harness issues is represented as a product
finding or full passing run. Mypy is scoped with silent imports, not a whole-repo
type-check claim. The final artifact audit initially failed on the missing empty
prebuild-status file described above; its corrected form does not infer clean
state from absence and verifies totals, links, unchanged production and cleanup.

Raw evidence is ignored/local under this child's `build/r8b/`, including every
run's XML, output, exit status, disposable data, image logs/states, build log,
launch identity and parity hashes. The coordinator must copy it before removing
the child. Unique test containers and the unique parity container were stopped
and removed; no shared container/network/volume cleanup ran. The single image
is retained. Commit uses authorized per-command empty `core.hooksPath`, without
changing global hooks/config; final review SHA is in the completion message and
`build/r8b/final-sha.txt`.

Fresh complete source/client/image campaigns remain coordinator-owned and
pending after the remaining correction. The three owner-pending Tron visuals,
CI/PR/release approval, physical matrix/CEC/Remote/Flic, owner HA/LAN discovery,
continuous 72-hour HIL-D soak, week-of-daily-use sign-off, arm64 coverage and
final version/rebuild/publication gates remain separate and open. No push,
merge, tag, publish, real matrix command or release approval occurred.
