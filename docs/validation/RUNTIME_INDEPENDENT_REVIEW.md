# R8 independent runtime review

**Disposition: hold runtime release. Two high-severity availability defects are
reproduced in the immutable shipped amd64 image.** This review is complete as a
findings/reproduction task; it does not accept the candidate or implement fixes.
Earlier passing campaigns remain valid for their recorded scenarios, but their
zero-known-failures gate predates these findings.

## Revision, identity and scope

- Review date: 2026-10-19 UTC.
- Checkout: `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-runtime-independent-review`.
- Reviewed HEAD: `b84ec72bd8305c7785189f02e2afd9fa4f1d799a`, following accepted R7.
  The dispatch's older `70de5d9` is ancestry, not the reviewed revision.
- Application/image source: `4adbc136a4c1fb6be4b20b58530a47dd521efac8`.
  `git diff 4adbc136 HEAD -- src run.py tools` is empty at the reviewed HEAD.
- Provider/agent identity exposed to this session: OpenAI Codex, based on GPT-6.
  Coordinator dispatch label: `gpt-6-astra`, high effort. The session does not
  independently expose the more specific backend/effort label; it is not inferred
  from a successful launch. No secondary models, nested agents or fallbacks ran.
- New owned artifacts: this report and
  [test_runtime_review_r8.py](../../tests/test_runtime_review_r8.py).
  Production, existing tests, dependencies, versions, scenarios, registry, ledger
  and golden baselines were not edited.

The review read the accepted [runtime contract](../planning/RUNTIME_CONTRACT.md),
[next phases](../planning/NEXT_DEVELOPMENT_PHASES.md),
[execution history](../planning/RUNTIME_EXECUTION.md),
[runtime report](RUNTIME_VALIDATION_REPORT.md),
[evidence index](RUNTIME_VALIDATION_INDEX.md) and
[field gates](RUNTIME_FIELD_GATE_RUNBOOK.md), then inspected actual implementation
and execution records. New execution used synthetic catalogs, local simulators,
actual modules, the real UC SDK in existing regression tests, and disposable
containers only. No physical matrix/CEC commands or remote publication occurred.

## R8-01 — High: creating a scene after legacy migration prevents restart

**Owner:** persistence/startup (R2). **Release blocker.**

**Trigger:** an installation has a valid legacy output-state `data/scenes.json`
and no v2 catalog. Startup correctly imports it into profiles while preserving
the source. The operator then creates an unrelated v2 scene through
`POST /api/v2/scenes`. Creation succeeds, writes `scenes_v2.json`, and returns
HTTP 201. On the next start, preparation rejects the preserved legacy source
and the newly created v2 catalog as incompatible shapes.

**Effect:** normal `python run.py` exits with code 1 before REST/health or UC can
start. Both UC-disabled and UC-enabled normal image runs reproduced this. This
is an availability failure, not an observed deletion: the old source and backup
bytes, imported profile and new v2 scene remain present. Shared config/data and
separate config/data layouts both reproduce when the old scene source is in the
installation's data directory. A config-only legacy file in a separate directory
was not the trigger tested here.

**Source:** `src/hub/persistence/startup.py:166–183`, specifically the unconditional
legacy-shape/target-exists conflict at line 179. `prepare_profile_file()` has
already imported the old scenes to profiles. `SceneManager._ensure_loaded()`
initially leaves the v2 catalog absent for that shape; later successful scene
creation writes the catalog that triggers rejection on restart. The reproduced
scene has a fresh ID and no reference to the legacy profile, so this is not an
actual conflicting scene edit.

**Reproductions:**

- `test_migrated_legacy_scenes_accept_new_scene_and_restart[False/True]` uses
  `config.Scene.to_dict()` and real preparation/managers, verifies profile
  migration, creation, original/backup bytes, then clears preparation state and
  attempts a second startup.
- `test_shipped_image_legacy_upgrade_scene_creation_restart[False/True]` starts
  the unchanged image against a simulator, reads the migrated profile via REST,
  receives HTTP 201 for the new scene, and restarts the same container/volume.

The normal image's traceback terminates at:

```text
/app/run.py -> hub.cli.main -> run_core -> build_runtime
hub.persistence.migrations.MigrationError:
conflicting /data/scenes.json and /data/scenes_v2.json: incompatible record shapes
```

Docker inspection reports `Status=exited`, `ExitCode=1`, `OOMKilled=false`.
This failure is reached before a matrix connection attempt on the second boot.

**Correction boundary:** distinguish a demonstrably imported legacy profile
source from a competing unified-scene source, retaining the primary file,
backup and provenance. Preserve fail-closed handling of genuinely ambiguous or
conflicting files. Do not require operators to delete their original catalog to
use new scenes. The minimal owner investigation is `hub/persistence/startup.py`
and, if needed, the `scene_manager.py` preparation boundary; no execution policy
or shared schema change is implied.

**Acceptance after correction:** both module layouts and both normal-image UC
modes must create, restart, list and execute the new scene while retaining the
old profile and byte-preserved source/backup. Repeat startup and an edit/restart
must not churn data. Existing conflicting/future/corrupt/backup-failure tests
must continue refusing unsafe input.

## R8-02 — High: failed rollback login leaves the hub without automatic recovery

**Owner:** runtime composition (R1). **Release blocker.**

**Trigger:** while connected, reconfigure the same address during a transient
login outage. The candidate login fails, then the old client's rollback login
also fails. The simulator injects exactly two HTTP 503 responses for `login`
and automatically clears the fault; credentials and the address do not change.

**Effect:** the old client/address are restored and the refresh worker restarts,
but no transport reconnect task exists. The hub stays disconnected after the
device is healthy. In the image, twelve seconds of health polling showed no
automatic recovery; an explicit `POST /api/settings/test-connection` immediately
reconnected successfully. Source inspection explains why more polling cannot
repair this: refresh skips hardware work while disconnected and does not start
the transport supervisor. Other direct manual connection attempts or a process
restart can recover; normal background operation cannot in this state.

**Source:** `src/hub/runtime/composition.py:491–502` restores the old client and
awaits `service.connect()` without handling a false result. The reconnect
handoff exists in `_initial_connect()` at lines 332–339, but not in rollback.
`refresh()` at lines 257–264 only reads an already-connected service.
`OreiMatrix.disconnect()` intentionally cancels the old reconnect owner;
`OreiMatrix.connect()` is a single attempt, not an implicit replacement retry
loop. Starting a second runtime-level retry loop would violate the contract.

**Reproductions:**

- `test_failed_reconfigure_recovers_after_transient_login_outage` uses the real
  runtime, real `OreiMatrix` HTTPS/Telnet transport and real simulator. It verifies
  successful initial connection, the restored old client identity, fault removal
  and a live refresh task. Retry delays are shortened to 20–40 ms, yet after two
  seconds the snapshot is disconnected and `_reconnect_task is None`.
- `test_shipped_image_reconfigure_recovers_after_login_outage` sends the actual
  REST host-settings request to the unchanged image. The response is HTTP 200
  with `connected=false` under the existing wire contract. No recovery occurs
  during twelve seconds with the fault cleared. The manual connection-test
  endpoint then returns HTTP 200/connected and health becomes connected.

Image logs record the two failed logins at approximately `07:21:31.497` and
`07:21:31.503` UTC, followed by the next login only at the explicit manual request
at `07:21:43.575`; it authenticates immediately. This is a networked image
reproduction, not a mock of the reconnect method.

**Correction boundary:** restore the old transport's existing reconnect
supervisor after a failed rollback connection, once and only when runtime is
not stopping. Preserve candidate cleanup, the single active transport invariant,
serialized reconfiguration and cancellation propagation. Review failed/cancelled
setup rollback too, since UC uses the same runtime operation. A focused change
should remain in `hub/runtime/composition.py` unless the owner demonstrates a
separate transport defect.

**Acceptance after correction:** rerun source and fresh-image recovery with two
transient login failures, failed new-address setup, abort and shutdown during
rollback. Observe automatic state recovery on REST/WS/UC, no surviving candidate
retry tasks, at most one transport owner and bounded stop. Keep the original
initial-offline and ordinary outage-reconnect regressions.

## Execution and evidence

The pinned historical image is:

```text
sha256:1a5de3b5b58a3e1c56d3269bd5c1c6e3e12be2d6fea1abceea36067d733df69e
```

Its inspected entrypoint is null and command is `["python", "run.py"]`. Each
review image test mounts only its private `/data`, uses a unique container name,
publishes REST on an ephemeral loopback port, connects to the test simulator via
Docker Desktop's `host.docker.internal`, and stops/removes that exact container.
UC discovery is disabled for these disposable runs. No application source is
mounted over the image. This image test setup is Windows/Docker Desktop evidence;
it is not a Linux-host-network or physical LAN discovery test.

Reproduce from the review checkout with installed dependencies supplied by the
existing environment:

```powershell
$env:PYTHONPATH = "$PWD/src;$PWD"
& C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -m pytest tests/test_runtime_review_r8.py --runxfail -q --tb=short -p no:tests.route_inventory
& C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe -m pytest tests/test_runtime_review_r8.py -m docker --runxfail -q --tb=short -p no:tests.route_inventory
```

The first command produces **3 failures** (two R8-01 layouts and one R8-02
recovery). The second produces **3 failures** (two R8-01 modes and one R8-02
image recovery). These are desired-behavior assertions deliberately failing on
the reviewed candidate. Strict xfail markers identify the historical findings
when `--runxfail` is omitted; they are **not passing release gates or accepted
exceptions**. Only the final demonstrated invariant raises the marker's
`ReviewFindingError` exception: broken setup or unrelated assertions still fail.
Fixing owners must remove/transfer markers for the corrected source and verify
fresh candidate images; this pinned old image remains a historical reproduction.

| Review execution | Result | Local raw artifact under this checkout |
| --- | --- | --- |
| New actual-module reproductions, `--runxfail` | 3 failed, 3 image cases deselected | `build/r8-source-reproductions.txt`, `.xml` |
| Normal shipped image reproductions, `-m docker --runxfail` | 3 failed, 3 module cases deselected | `build/r8-image-reproductions.txt`, `.xml` |
| Image state/logs/data retained | Both restart exits and manual recovery captured | `build/r8-image-evidence-1/` |
| Mixed contract regression selection | 1,037 passed, 2 skipped, 3 review xfails, 87 fixture setup errors, 3 image cases deselected | `build/r8-regressions.txt`, `.xml` |
| Separate simulator regression invocation | 107 passed | `build/r8-sim-regressions.txt`, `.xml` |
| UC setup/handshake and persistence/transport boundary selection | 214 passed | `build/r8-boundaries.txt`, `.xml` |
| Narrow module marker check | 3 strict xfails, 3 image cases deselected | `build/r8-review-marker-check.txt`, `.xml` |

The mixed regression invocation is not labeled green: 87 simulator tests could
not resolve `data_hub`/related fixtures. Rerunning the selected simulator files in
their own invocation passed all 107 (including the earlier 20 WS cases). No test
or fixture was changed to obtain that result. Two existing skips and those
fixture errors remain in the original logs. Route-inventory reporting was
disabled locally to avoid generating a partial shared coverage artifact; this
review makes no new 100% route-coverage claim.

The read-only regression selection covers the contract's entry/health,
service/events/WS/SSRF, persistence/atomic/config/scene/macro/shortcut/dashboard/
device-settings, action/PIN/security/framework, Flic/framework/adapter and
validation-runner/client-state paths. It also includes current shutdown,
transactional UC setup, cancellation/action wire parity and integration flag/
lifecycle regressions. Dedicated HA, full client campaigns, full UI and full
deployment suites were not repeated; their archived results retain their exact
scope. Exact command argument arrays are retained in
`build/r8-review-procedure.json`; testcase results are in the named XML/text
artifacts. The coordinator must copy the ignored local evidence before removing
this worktree. The committed report and tests are the durable reproduction.
Owned-file Ruff/Black checks, report links and Git whitespace checks passed.
The commit uses a command-scoped hook override because the configured pre-commit
hook runs the full suite and the coordinator explicitly reserved full campaigns;
no persistent Git or agent setting is changed.

## Independent assessment of the existing evidence and remaining boundaries

The review independently checked all **213/213 Git-blob hashes** indexed by the
archive manifest/milestone journal, recomputed the **193 image outcomes**
(API 79, browser 54, Flic 23, HA 19, UC 18), and parsed the JUnit totals: core
3,966 passed/4 skipped, UC 100 passed, deployment 26 passed/3 skipped. A fresh
read-only container comparison matched **257/257 actual amd64 shipped-file
hashes** to the archived input-parity record. The image ID was independently
inspected before the reproductions. The 42 declared client exclusions remain
non-applicable, not passes. This verifies provenance/counts, not the truth of
every individual oracle or physical behavior.

An initial source-hash comparison used Git blobs where the parity record hashes
working-tree/image bytes; CRLF conversion made that comparison inappropriate.
The actual-image byte check above is the valid comparison. An initial image
pytest invocation also failed before execution because the requested local
artifact parent directory did not exist; the subsequent recorded invocation
created that parent and executed all three image cases. These harness mistakes
are not product findings and do not replace the retained failing application
records.

| Reviewed boundary | Assessment and limit |
| --- | --- |
| Real startup and migration ordering | `run.py` delegates to `hub.cli`; both modes use `build_runtime`. Preparation precedes manager creation and REST construction. Actual image starts/readbacks/restarts exercise that path; R8-01 blocks acceptance. |
| Storage retention and public projection | Actual readers use safe storage helpers and explicit public serializers; unknown extension fields remain private on disk. Existing corruption, future-version, private-field, PIN and edit/reload regressions were included. R8-01 is a missing supported migration lifecycle, not evidence that all storage is unsafe. |
| Configuration/credentials and UC setup | Saved UC address takes priority over environment; core environment has priority and core fallback does not adopt saved secrets. Address-bound credential handling, authorized setup and stable runtime facade were inspected. SDK setup/handshake and existing transactional setup tests provide actual protocol coverage; no physical Remote claim. |
| One transport/refresh/event owner | Composition has one service, facade, runner/local client and refresh task; runtime WS consumes shared state. Existing service/WS/action tests exercise effects and duplicate prevention. R8-02 exposes a missing reconnect handoff; green normal-owner counts do not cover it. |
| REST/UC/Flic action, auth, partial and cancel parity | Shared runner/projections and local action envelope inspected. Current auth/PIN/cancel/partial/wire tests and simulator readback passed in their scoped runs. Flic's generated HTTP uses normal middleware; archived exact replay is not physical button proof. No new authorization bypass was demonstrated. |
| Flags/imports and lifecycle | Effective private mapping and lazy registrations inspected; current flag/lifecycle tests cover disabled imports and rollback. The new image migration case covers both UC modes, with Flic/HA disabled. It does not independently repeat all eight flag configurations in containers. |
| Bounded cleanup | Runtime and UC track/cancel owned work; transport and integration cleanup regressions were selected. Review containers stopped and were removed. No new cleanup leak was demonstrated; arbitrary cancellation-resistant external code and owner deployment outages remain outside these tests. |

The coordinator should record these new findings in its shared register/ledger,
dispatch disjoint fresh implementation owners, and refresh affected source and
shipped-image gates at the corrected source/image digests. This review does not
modify that shared evidence. Do not relabel the historical image or its old green
campaign as the corrected candidate.

The three owner-pending Tron visuals, remaining CI/PR and approved merge/tag
sequence, real matrix/CEC behavior, physical Remote/Flic, owner HA/LAN discovery,
HIL-B/C/E, continuous 72-hour HIL-D soak, week-of-daily-use sign-off and final
`1.0.0` metadata/rebuild/publication gates remain open independently. Arm64's
archived offline startup/health/SIGTERM proof does not cover these new action/
migration failure paths. No final-release approval is given.
