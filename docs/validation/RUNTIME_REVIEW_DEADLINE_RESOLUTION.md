# R8C independent rollback deadline resolution review

**Disposition: hold the runtime candidate.** All eight required source/image
checks pass, accepting the original startup, immediate rollback-failure and
rollback-login deadline corrections within their focused scope. A new consequential
failure, **R8C-01**, interrupts rollback during candidate cleanup before original
identity restoration; it leaves a healthy original target abandoned. This review
is complete as a review/reproduction task, not focused acceptance of the entire
reconfiguration boundary or approval of a release.

## Provenance and immutable build

Reviewed 2026-10-19 UTC from the fresh Orca child
`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-runtime-deadline-resolution-review`.
Initial HEAD and actual `wp-runtime-completion` both resolved to
`dd184725da2bc4f30b1f48d2b2f6b59f350ef202`, with empty tracked/untracked status
before the build (`build/r8c/prebuild.json` explicitly records an empty array).
This includes R1H `c36edb91f7c369f003e2d2bae5ce11dd0aad4e50` and the accepted
R1G/R2D corrections. No checkout reset or production edit occurred.

`orca orchestration worker-show --dispatch ctx_a441e7bf3d46 --json` records
requested and effective agent/provider `codex`, model `gpt-6-astra`, effort
`high`; projection also reports provider `codex` and model `gpt-6-astra`.
The receipt is `build/r8c/orca-launch.json`. These are Orca control-plane
observations, not independent backend attestation; the session identifies itself
as OpenAI Codex based on GPT-6. No Anthropic, helper, nested or fallback agents ran.
No applicable `AGENTS.md` was found in this checkout or its ancestors.

Read the current [runtime contract](../planning/RUNTIME_CONTRACT.md), original
[R8 report](RUNTIME_INDEPENDENT_REVIEW.md), [R8B follow-up](RUNTIME_REVIEW_FOLLOWUP.md)
and coordinator-supplied root evidence under
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/runtime-completion/`:
`r1h-worker-evidence/result.json`, its retained native-HTTP-budget failed run,
controlled-red and final controlled-green logs, plus `r1h-coordinator.log`.
Earlier results are attributed history, not acceptance of this revision.

One successful canonical normal-command amd64 build preceded tracked review edits:

```powershell
docker build --platform linux/amd64 --build-arg VERSION=1.0.0rc1 --label org.opencontainers.image.revision=dd184725da2bc4f30b1f48d2b2f6b59f350ef202 -t hub-r8c-dd184725-ctxa441 --iidfile build/r8c/image-id.txt .
```

The first invocation could not initialize because another process held Docker's
`desktop-linux` context `meta.json`; no build started. Its output and nonzero exit
remain in `docker-build-setup-failed.log` and `docker-build-setup-failed-exit.txt`.
The identical retry completed successfully, exit 0, without configuration changes;
`docker-build.log` and `docker-build-exit.txt` preserve it.

Immutable inspected image ID:

```text
sha256:3abd3745cbe361c1c9fc7ead88774b66e7c507e5eb63f6816239e56d7c455af0
```

Inspection reports Linux/amd64, null entrypoint, command `["python", "run.py"]`,
OCI revision `dd184725da2bc4f30b1f48d2b2f6b59f350ef202` and version `1.0.0rc1`,
matching `hub.__version__`. Other labels retain title `8x8 HDMI Matrix Hub`,
license `MPL-2.0`, source `https://github.com/ryan-haver/8x8-hdmi-matrix-hub` and
its REST/UI/integration description. Full inspection is `image-inspect.json`.

Read-only comparison of actual image bytes matches **257/257 tracked shipped
inputs** to this checkout's actual bytes, including CRLF conversion. Both maps
are in `production-image-parity.json`; `parity.py`, `parity-command.json` and
`parity.log` record the inspection. Its uniquely named temporary container used
an overridden Python entrypoint only to read hashes. All four behavioral image
cases use the unchanged normal command, bind only disposable synthetic `/data`,
and connect to actual HTTPS/Telnet Simulator sockets through
`host.docker.internal`. No application source is mounted into the image.

| Working-tree input | SHA-256, also matching image for shipped files |
| --- | --- |
| `src/hub/runtime/composition.py` | `4a4c009b281daebd197ad267a50718729e122e9581485965d505e04be928614a` |
| `src/hub/persistence/startup.py` | `1102b2800bb3b3c2634da8521519ad70a89017947cc789d020d1a09892b8ae6b` |
| `src/orei_matrix.py` | `b19e615949396b5871547b86ae46a493f882c8dd8aaca7169431025035d73d94` |
| `run.py` | `701c5a99e33040913c99078956d09c86dfa0c6cd00177d3c9ff7272d9fe1444f` |
| `Dockerfile`, build input | `aff58889f4d0aec937b3b8a7cd13cd0370ed280fe0bbf9cf1a4130c0554baa5b` |

`origins.json` verifies runtime composition, startup preparation, Orei transport
and Simulator imports resolve inside this child. Existing dependencies come from
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
with explicit own cwd and process-local `PYTHONPATH=<child>/src;<child>`.
No install, dependency change or global configuration change occurred.

## Required findings: specific disposition

**R8-01: focused correction accepted.** Both source layouts pass. Both normal-image
UC-off/on cases migrate the legacy profile, create a new scene, restart within
the unchanged six-second health bound, list both catalogs and execute the new
scene. Original source/backup bytes and catalog bytes across restart retain the
existing strict oracles. UC-on starts the actual SDK; HA, Flic and UC mDNS are
explicitly disabled in these image cases. No new startup defect was demonstrated;
this does not repeat the whole persistence campaign.

**R8-02: original immediate-failure and R8B rollback-login deadline triggers are
corrected, but the wider rollback invariant remains blocked by R8C-01.** The two
immediate login-503 failures recover automatically in source and image. The held
third login response crossing the unchanged production five-second cleanup limit
also recovers automatically in source and the new image. The image oracle records
successful automatic health recovery before its subsequent diagnostic manual
connection request; manual success does not count as recovery proof.

R1H's `finally` around `service.connect()` ensures that an interrupted restored
login hands ownership to the original transport supervisor. It keeps the stopping
fence and optional callable seam. `OreiMatrix.connect()` joins its shielded
single-flight attempt; `start_auto_reconnect()` delegates to the existing single
supervisor, honors disabled auto-reconnect and refuses pending disconnect work.
No runtime retry loop was added. The 39 selected regressions pass, covering original
identity/address/effective credentials/names/storage, changed-address rollback,
late login success, cancellation propagation, disabled retries, following
reconfiguration, pending-login/backoff stop and transport drain/fences.

The transaction and reconfigure locks serialize foreground work, with tracked
operations released on return/cancellation and a single resumed refresh worker.
Shutdown sets `_stopping` before cancelling owned work, so the corrected handoff
cannot restart retries once shutdown begins. The selected stop cases pass their
existing bounds; no new post-stop revival was demonstrated. This is not proof
that arbitrary cancellation-resistant external cleanup always respects a global
shutdown deadline.

## R8C-01: interruption during candidate close skips original restoration

**High availability impact; runtime composition owner; hold candidate pending a
fresh assigned production owner.** The original client is already closed, the
failed candidate is current, and `rollback()` awaits `candidate.disconnect()`
(`composition.py:499`) before restoring original address/client/names at lines
501-503. `OreiMatrix.disconnect()` correctly drains its shielded cleanup and then
re-raises a cancelled waiter's `CancelledError` (`orei_matrix.py:886`). That
exception exits rollback before restoration and before the R1H reconnect `finally`
is entered. Cleanup timeout is logged/swallowed; caller cancellation propagates,
but either path leaves the runtime pointing at the closed failed candidate.

The new [review test](../../tests/test_runtime_review_r8c.py) starts a real runtime,
OreiMatrix and HTTPS/Telnet Simulator, connects with the original credentials,
then attempts `localhost` as a changed address with separate candidate credentials.
Exactly one actual login HTTP 503 rejects the candidate; the Simulator then has
no remaining fault. The test wraps the actual `aiohttp.ClientSession.close()`
only for the candidate's real session; the original close always runs, and no
connect result, state, transport drain or production timeout is replaced.

| Case | Intervention and observed result |
| --- | --- |
| `release` | Gate close scheduling, release normally: restores all identity/address/names/credentials, connects to the original and records exactly 3 logins; **passes**, 0.891 s to setup result. |
| `cancel` | Cancel the caller while candidate close is pending, release the real close: caller cancellation propagates, candidate closes, original restoration is skipped; **fails** desired identity invariant, 0.265 s to setup result. |
| `deadline` | Hold close until the actual unchanged `CLEANUP_TIMEOUT == 5.0` cancels the waiter, then release: failed result returns at 5.266 s, candidate closes, original restoration is skipped; **fails** desired identity invariant. |
| `cancel_at_close` | Schedule `setup.cancel` with `loop.call_soon` at entry to the actual close; **no delay or blocking gate is added**: same stranded state, caller cancelled at 0.266 s; **fails** desired identity invariant. |

All three failing cases reach the final desired-behavior assertion after verifying
actual candidate cleanup, unchanged complete storage bytes, released reconfigure
lock and operation ownership, and a live resumed refresh worker. Their JSON
observations show original identity/address/names/effective-credentials comparisons
all false, disconnected state, exactly two login requests and no original retry
owner after two seconds of automatic observation. Existing source fixture retry
delays are 20-40 ms; no manual connection occurs. The failed candidate has no
session/Telnet/connect/reconnect owner. Saved configuration is intact, but the
live configuration retains the unsuccessful candidate, so ordinary disconnected
refresh cannot restore the original target. There is no evidence here of a
surviving candidate socket, data loss, or post-stop transport resurrection.

This is a **source-level phase-controlled reproduction**, not a newly reproduced
normal-image failure or a measured natural five-second close delay. The un-delayed
cancellation case establishes that slow-close injection is unnecessary for the
cancellation defect; the separate gated deadline case establishes the cleanup
phase's behavior when that production deadline expires. The four requested image
cases remain green and do not exercise cancellation during candidate disposal.
No hypothetical severity is assigned to untested cleanup exceptions.

A correction must preserve cancellation propagation while finishing safe original
state restoration/reconnect ownership after candidate cleanup interruption, retain
stop fences and bounds, and never reconnect the original while a candidate owner
remains live. It must address the cleanup phase preceding the current R1H `finally`,
not just the returned-false rollback-login path. Production was not edited, and the
new desired-behavior failures remain ordinary tests without xfail/skip markers.

## Commands, results and evidence retention

All commands below run in the child. `PY` means the absolute existing interpreter
above, invoked with PowerShell `&`. Set only process-local variables:

```powershell
$env:PYTHONPATH = "$($PWD.Path)/src;$($PWD.Path)"
$env:R8_REVIEW_IMAGE = 'sha256:3abd3745cbe361c1c9fc7ead88774b66e7c507e5eb63f6816239e56d7c455af0'
```

Every pytest invocation appends these exact common flags, substituting the table's
stem, and redirects stdout/stderr to `build/r8c/<stem>.log`; numeric exit is saved
in `<stem>-exit.txt`:

```text
-q --tb=short -p no:tests.route_inventory --junitxml=build/r8c/<stem>.xml --basetemp=build/r8c/<stem>-tmp --log-file=build/r8c/<stem>-detail.log --log-file-level=INFO
```

| Exact pytest selection after `PY -m pytest` | Stem | Result |
| --- | --- | --- |
| `tests/test_runtime_review_r8.py tests/test_runtime_review_r8b.py -m 'not hardware'` | `eight` | **8 passed**, 28.59 s, exit 0; 4 source + 4 image; zero fail/error/xfail/skip |
| `tests/test_runtime_rollback_deadline_r1h.py tests/test_runtime_rollback_reconnect_r1g.py tests/test_runtime_shutdown_r1.py tests/test_runtime_transport_drain_r1c.py` | `targeted` | **39 passed**, 64.61 s, exit 0; zero fail/error/xfail/skip |
| `tests/test_runtime_review_r8c.py` | `cleanup-phase` | **3 failed**, 12.86 s, exit 1; initial 3-case probe, retained |
| `tests/test_runtime_review_r8c.py` | `cleanup-phase-final` | **1 passed, 2 failed**, 12.58 s, exit 1; corrected control ownership assertion; no errors/xfails/skips |
| `tests/test_runtime_review_r8c.py` | `cleanup-native` | **1 passed, 3 failed**, 15.63 s, exit 1; final 4-case test including un-delayed real-close cancellation; no errors/xfails/skips |

R1H's own pending-login tests extend only their HTTP budget to 15 seconds to isolate
an unfinished shielded attempt at production cleanup 5; they do not alter cleanup.
The required R8B source/image deadline cases retain their original network budgets.
No full source 1506, dedicated HA/UI, client campaign or multiarch run was repeated.
The route-inventory plugin is disabled locally to avoid writing shared partial
coverage evidence.

The first new-test run's release control incorrectly asserted that the whole
operation set was empty, although the resumed refresh legitimately owned an
operation. The corrected assertion checks that the completed setup is no longer
an operation owner; it does not relax identity/state/time recovery oracles.
The initial test bytes are `cleanup-phase-first-test.py`; its complete failed
log/XML remains separate. Both interruption findings already reached the intended
identity failure in that initial run. Initial Black check requested formatting;
`black-first.log` preserves that failure. No existing test/marker/config was edited.

Final scoped static commands all pass, exit 0:

```text
PY -m ruff check tests/test_runtime_review_r8c.py
PY -m mypy --follow-imports=silent tests/test_runtime_review_r8c.py
PY -m black --check tests/test_runtime_review_r8c.py
git diff --check
```

Mypy is scoped with silent imports, not a whole-repository type-check claim.
Only this report and the new review test are committed, using authorized
per-command `git -c core.hooksPath= commit`; no persistent hook change occurs.
The exact review commit is supplied in worker completion and
`build/r8c/final-sha.txt`. The new failing cases are intentionally preserved findings,
so the new review module is explicitly **not green**.

All raw evidence remains local/ignored under `build/r8c/`: image logs/states,
synthetic data, XML/text/exit records, observations, provenance and hashes.
Unique test containers and the unique parity container were removed by their
own cleanup; no shared network/volume cleanup ran, and this review created no
named network/volume. The uniquely tagged image is retained. Coordinator must
copy `build/r8c/` before deleting this child; original R8/R8B reports and evidence
remain unchanged history.

The fresh complete campaign and renewed independent review after correction remain
pending, as do owner approval of the three Tron visuals, CI/PR/approved release
sequence, physical matrix/CEC/Remote/Flic, owner HA/LAN discovery, HIL-B/C/E,
continuous 72-hour HIL-D soak, week-of-daily-use sign-off, arm64 and final version/
rebuild/publication gates. No push, merge, tag, publish, real-hardware command or
final-release approval occurred.
