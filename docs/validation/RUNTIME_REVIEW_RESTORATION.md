# R8D independent restoration review

**Focused supported-Orei acceptance passes.** All twelve mandatory unchanged
source/image cases pass, along with 102 selected regressions and two new supported
transport controls. No remaining consequential failure of the supported Orei
implementation was demonstrated. This accepts the recorded fixes within this
review's scope, not the complete candidate or release.

A stronger, conditional public-disconnect guarantee is **not implemented**:
replacing `disconnect()` with a function that throws before invoking the actual
Orei body can leave a pre-existing transport supervisor running. That probe still
fails; it is preserved in full below. The coordinator explicitly classified this
as an extension beyond the supported transport contract, rather than a demonstrated
production/image regression. It must not be cited as a passing universal guarantee.

## Revision, identity and immutable image

Reviewed 2026-10-19 UTC in the fresh Orca child
`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-runtime-restoration-independent-review`.
Initial HEAD and actual `wp-runtime-completion` both resolved to
`619baccc4120e4bc8144272506bf09d0637c194d`, including accepted R1I
`0ea3b7adcf75cab7436adacbd1be26aef6c0d189`. The initial tracked/untracked status
was empty, explicitly recorded as `status: []` in `build/r8d/prebuild.json`.
The image was built before any tracked review edit. No reset or other-checkout
edit occurred; production and every pre-existing test/report remain unchanged.
No applicable `AGENTS.md` was found in the checkout or its ancestors.

`orca orchestration worker-show --dispatch ctx_823bd240354b --json` records
requested and effective agent/provider `codex`, model `gpt-6-astra`, effort
`high`; the projection also identifies provider `codex` and model `gpt-6-astra`.
The receipt is `build/r8d/orca-launch.json`. These are Orca control-plane facts,
not independent backend attestation. This is an OpenAI Codex session; no
Anthropic, helper, nested or fallback agents ran.

Read the [runtime contract](../planning/RUNTIME_CONTRACT.md),
[R8](RUNTIME_INDEPENDENT_REVIEW.md), [R8B](RUNTIME_REVIEW_FOLLOWUP.md), and
[R8C](RUNTIME_REVIEW_DEADLINE_RESOLUTION.md), plus the coordinator's copied
R1I evidence at
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/runtime-completion/r1i-worker-evidence/`:
`report.txt`, `result.json`, final focused logs, original R8C/owned/pending-drain
red logs, and the adjacent `r1i-coordinator.json`. The coordinator's two policy
decisions in root `.git/r1i-settling-decision.txt` and
`.git/r1i-failed-retirement-decision.txt` were also read. Their historical counts
are attributed evidence, not substituted for execution on this revision.

One successful canonical build, exit 0:

```powershell
docker build --platform linux/amd64 --build-arg VERSION=1.0.0rc1 --label org.opencontainers.image.revision=619baccc4120e4bc8144272506bf09d0637c194d -t hub-r8d-619baccc-ctx823b --iidfile build/r8d/image-id.txt .
```

Immutable inspected image ID:

```text
sha256:900fb2b80078cb543be84ea869d07f9eaf0aee8691cdde946fab69b59e1a99a9
```

Inspection confirms Linux/amd64, null entrypoint, command `["python", "run.py"]`,
OCI revision `619baccc4120e4bc8144272506bf09d0637c194d`, and version `1.0.0rc1`,
matching `hub.__version__`. Full labels/inspection are in `image-inspect.json`;
the build output and numeric exit are `docker-build.log`/`docker-build-exit.txt`.

Independent inspection matched **257/257 shipped tracked files** against both
prebuild and current working-tree bytes, including checkout line endings.
`production-image-parity.json` contains all three hash maps. The read-only
`parity.py` inspection uses one uniquely named `--rm` container with Python
entrypoint override solely to hash files. Its exact argv is `parity-command.json`.
All four behavioral image cases use the unchanged normal command and actual
HTTPS/Telnet Simulator sockets through `host.docker.internal`. They bind only
their uniquely owned disposable synthetic `/data`; no application source is mounted.

| Actual input | SHA-256, also matching image for shipped files |
| --- | --- |
| `src/hub/runtime/composition.py` | `fb5cad66ad2a9aab138374ab754a6f1e74241f4b6e0f6b40e1484c7a78d610c1` |
| `src/hub/persistence/startup.py` | `1102b2800bb3b3c2634da8521519ad70a89017947cc789d020d1a09892b8ae6b` |
| `src/orei_matrix.py` | `b19e615949396b5871547b86ae46a493f882c8dd8aaca7169431025035d73d94` |
| `run.py` | `701c5a99e33040913c99078956d09c86dfa0c6cd00177d3c9ff7272d9fe1444f` |
| `Dockerfile`, build input | `aff58889f4d0aec937b3b8a7cd13cd0370ed280fe0bbf9cf1a4130c0554baa5b` |

`origins.json` verifies composition, persistence startup, Orei transport and
Simulator imports resolve inside this child. Dependencies come from the existing
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
with explicit own cwd and process-local `PYTHONPATH=<child>/src;<child>`.
No installation, dependency or global configuration change occurred.

## Disposition of earlier findings and restoration boundaries

**R8-01: focused correction accepted.** Both source layouts and both normal-image
UC-off/on cases pass. The image cases migrate a legacy profile, create a v2 scene,
restart within the unchanged six-second health bound, list both catalogs and
execute the new scene. Source, backup and catalog byte oracles remain unchanged.
UC-on runs the actual SDK; Flic, HA and UC mDNS are disabled in this focused image
selection. The 34 R2D regressions pass, including supported coexistence and
fail-closed provenance cases; this is not a full persistence campaign.

**R8-02 / R8B-01: focused corrections accepted.** The original immediate two-503
rollback failure and delayed rollback-login cleanup deadline recover automatically
in source and the new immutable image. The R8B image oracle observes recovery
before its diagnostic manual test-connection request; that later request cannot
satisfy the recovery assertion. No manual connection is used in source recovery.

**R8C-01: focused restoration correction accepted.** Every original phase case
passes without changing its assertions, markers, production deadline or native
cancellation scheduling. Exact measured time from setup start to result/cancellation:

| Unchanged phase case | Elapsed | Caller cancellation | Result |
| --- | ---: | --- | --- |
| `release` | 0.891 s | no | Original restored and connected |
| `cancel` | 0.266 s | propagated | Original restored and connected |
| `deadline` | 5.266 s | cleanup deadline, not caller cancellation | Original restored and connected |
| `cancel_at_close` | 0.266 s | propagated | Original restored and connected |

Each records original client/address/name-store identity, effective credentials,
saved input/output names, unchanged complete storage, actual candidate closure,
and exactly three real logins. `cancel_at_close` still schedules cancellation
at real aiohttp close entry with **no delay or blocking gate added**. The original
under-three-second prompt bounds and under-seven-second deadline bound hold.

The implementation was inspected across early runtime drain, initial login,
original disconnect, candidate disconnect, rollback login, timeout and repeated
caller cancellation. `restore()` synchronously reinstates address, original client,
name-store, listener binding, generation and REST binding before further
cancellable settling. A `finally` also covers public cleanup exceptions. The
outer transition `finally` hands off an interrupted initial login and resumes
one refresh worker even if cancellation happened before client replacement.

Retirement tasks retain their owning client and retrieve eventual results.
`operation()` fences commands/refresh while retirement is pending or failed;
failed public calls cannot silently certify disposal. `_handoff_reconnect()`
requires current client and generation, checks stop, and defers while retirements
remain. It delegates to the existing optional transport supervisor; there is no
runtime retry loop. Actual Orei `connect()` is single-flight, and its existing
supervisor enforces `autoReconnect` and intentional-disconnect fences.

All 12 R1I controls pass on this source. They cover actual-drain cancellation,
pending initial-login handoff, native original-close cancellation, public candidate
errors before/after disposal, unreleased original/candidate close, repeated
cancellation, late successful closure, disabled reconnect, superseding setup and
stop. R1G/R1H, shutdown, transport-drain and UC transaction regressions also pass.
These include identity/credential/storage retention and final real state readback,
not only task-count assertions. Some shutdown/UC transaction tests use structural
transport doubles; the entire 102-case selection is not claimed as all-real-network.

Production `CLEANUP_TIMEOUT` remains **5.0 s**. A separately bounded settling
phase can use another five seconds; repeated cancellation does not restart it.
The R1I unreleased-candidate control returned at **10.266 s**, including transition
overhead, within its unchanged `10 <= elapsed < 11` oracle. Its subsequent stop
also passes the distinct `5 <= elapsed < 6` public-drain bound, retaining the
still-pending retirement until actual close succeeds after stop. No revival occurs.
These are bounded cleanup phases, not a universal ten-second limit for every
transaction or every shutdown phase.

The new supported late-original-close control cancels the caller during a real
gated aiohttp close, returns cancellation after **5.000 s**, and verifies logical
restoration and retained pending ownership. After real close is released, the
existing original transport reconnects automatically with exactly two total
logins, actual routing readback reaches input 6, and a public runtime switch
changes Simulator output 1 to input 7. Listener counts and storage remain correct.
No replacement candidate is created and no manual connect occurs.

## Public errors: supported control and conditional extension limit

The new supported in-body exception control starts the real original reconnect
supervisor and holds its second failing HTTP login response. A synchronous public
`Events.DISCONNECTED` listener raises `OSError` from inside actual
`OreiMatrix._dispose_transport()`. The public `disconnect()` body, synchronous
intentional-close fence, cancellation of owned transport work and actual resource
disposal all execute unchanged; no transport method is replaced with success.

This control passes: the public exception is retained on the retirement task,
original client/address/names/credentials/config and listener counts are restored,
the command raises the cleanup-fence error without changing Simulator power,
and releasing the failed HTTP response produces **no third login**. Both transport
and runtime remain disconnected. Supported `stop()` retries the failed public
retirement once under the stop fence; the one-shot listener then permits success,
and no session, Telnet, connect/reconnect task, retirement or runtime listener
remains. This is conservative error containment, **not automatic connectivity
recovery** after an exception. R1I also verifies that a still-failing public close
remains retained even if a test wrapper knows actual disposal already occurred.

**R8D-C1: conditional stronger public-boundary guarantee remains unimplemented.**
The preserved probe replaces `original.disconnect` with a function that raises
*before calling the actual Orei body*. With a real pre-existing reconnect
supervisor and its second failed login gated, reconfiguration restores identity,
retains the exception and rejects commands, but release lets that existing
supervisor perform a third login successfully and open Telnet. Runtime health
still reports disconnected while the original transport is connected. The
after-real-disposal wrapper control keeps two logins and passes. Both stop cleanly.

The runtime did **not** create a new retry through its retirement fence. The
replacement implementation prevented Orei's own synchronous
`_intentional_disconnect = True` from executing. Actual `disconnect()` sets that
fence before its first await (`orei_matrix.py:869`); `_connect_once()` checks it
again after login (`:733`). No natural supported-client in-body exception that
bypasses this fence was demonstrated. The observed extra login is real wire
evidence, but the triggering implementation substitution is conditional. No
wrong-device write, data loss, duplicate-client session or post-stop leak was shown.
No production/image severity is inferred from this probe.

On 2026-10-19 the coordinator explicitly resolved this scope in message
`msg_8f5984f0c7a8`: the contract keeps client-owned reconnect authority and does
not require a new generic factory protocol. The conditional probe is therefore
retained as explicitly invoked evidence, outside default product acceptance;
it is not xfailed, skipped or relabeled green. Upholding that stronger guarantee
for an alternate disconnect implementation would require an independently reliable
public quiescence capability or a stronger implementation contract. No such API
or production change was made. This review does not claim composition alone can
quiesce arbitrary replacements that fail before applying their own close fence.

The complete original three-case probe is byte-preserved as
`build/r8d/conditional-probe.py`, SHA-256
`defca6b53cd9f03e2c00cd26eb00d6c733e6e68fd93294ab455e59debb077df4`.
The explicit rerun selects its before/after public-disconnect cases and still
reports **1 failed, 1 passed, 1 deselected**, exit 1. The deselected case is the
late-original-close test independently retained in the committed supported file.
The full prior three-case executions remain **1 failed, 2 passed**, not green.

## Exact executions and retained evidence

All commands execute in this child. `PY` below denotes the absolute existing
interpreter given above, invoked with PowerShell `&`. `build/r8d/run.py` records
exact subprocess argv, cwd, selected-file hashes, HEAD, environment overrides,
timestamps, elapsed time and exit code in `<stem>-command.json`, with combined
output in `<stem>.log`. It sets only process-local:

```text
PYTHONPATH=<absolute child>/src;<absolute child>
R8_REVIEW_IMAGE=sha256:900fb2b80078cb543be84ea869d07f9eaf0aee8691cdde946fab69b59e1a99a9
```

Each pytest invocation appends exactly:

```text
-q --tb=short -p no:tests.route_inventory --junitxml=build/r8d/<stem>.xml --basetemp=build/r8d/<stem>-tmp --log-file=build/r8d/<stem>-detail.log --log-file-level=INFO
```

| Exact selection after `PY -m pytest` | Stem | Result |
| --- | --- | --- |
| `tests/test_runtime_review_r8.py tests/test_runtime_review_r8b.py tests/test_runtime_review_r8c.py -m 'not hardware'` | `acceptance` | **12 passed**, 40.14 s, exit 0; 4 R8/R8B source + 4 unchanged R8C source + 4 normal image; zero failures/errors/xfails/skips |
| `tests/test_runtime_rollback_restoration_r1i.py tests/test_runtime_rollback_deadline_r1h.py tests/test_runtime_rollback_reconnect_r1g.py tests/test_runtime_shutdown_r1.py tests/test_runtime_transport_drain_r1c.py tests/test_runtime_uc_transaction_r3b.py tests/test_runtime_legacy_scene_restart_r2d.py` | `regressions` | **102 passed**, 143.47 s, exit 0; module counts 12/10/9/10/10/17/34; zero failures/errors/xfails/skips |
| `tests/test_runtime_review_r8d.py` (final supported tests) | `supported-boundaries` | **2 passed**, 6.41 s, exit 0; in-body error and late original close |
| `build/r8d/conditional-probe.py -p tests.conftest -k original_public_disconnect` | `conditional-preserved` | **1 failed, 1 passed, 1 deselected**, 1.34 s, exit 1; conditional guarantee remains red |

The final supported selections total **116 passing cases** across three runs;
this count excludes the conditional probe and duplicate investigation reruns.
No full source-1506, dedicated HA/UI, full client/image or multiarch campaign ran.
The route-inventory plugin is disabled locally to avoid writing partial shared
evidence. `-p tests.conftest` gives the explicitly invoked local probe the same
global-state isolation as the original tests directory.

Unsuccessful attempts are preserved separately. `original-error-first` has two
failures at the new test's nonexistent `listener_count` API, before the intended
boundary; `original-error-first-test.py` preserves those bytes. Correcting it to
`len(events.listeners(event))` produced `original-error`: one conditional failure
and one passing control, 1.45 s. `r8d-final` and `r8d-formatted` each retain the
full three-case conditional file's one failure/two passes, 7.05 s. The initial
Black check in `black.log` failed; `black-format` reformatted only the new test.
Existing review tests, assertions, markers and configuration were never edited.

Final scoped static commands are `PY -m ruff check tests/test_runtime_review_r8d.py`,
`PY -m mypy --follow-imports=silent tests/test_runtime_review_r8d.py`,
`PY -m black --check tests/test_runtime_review_r8d.py`, and `git diff --check`.
Scoped mypy is not a whole-repository type-check claim. Final raw results and
audit records accompany the report. The local conditional probe and all
unsuccessful attempts remain available for coordinator copying before cleanup.

`audit.json` parses exact XML counts and observations and verifies production
still matches the prebuild hashes. The four uniquely named behavioral containers
and the parity container have been removed by their own cleanup. No shared
containers/networks/volumes were removed; this review creates no named network or
volume. The unique review image is retained. All raw evidence, synthetic data,
image states/logs, scripts and observations remain under **`build/r8d/`** and must
be copied before this child is deleted.

Only this report and [the new supported review test](../../tests/test_runtime_review_r8d.py)
are committed, using the authorized per-command empty `core.hooksPath`, without
changing persistent hooks/config. The exact review SHA is supplied in the
completion message and local `final-sha.txt`.

Fresh complete software/source/client/image campaigns, dedicated HA/UI and
multiarch coverage remain coordinator-owned and pending. Owner approval of the
three Tron visuals, physical matrix/CEC/Remote/Flic, owner HA/LAN discovery,
continuous 72-hour soak, week-of-daily-use field gates, CI and release approval,
final version/rebuild and publication remain separate and open. No physical
hardware command, push, merge, tag or publication occurred.
