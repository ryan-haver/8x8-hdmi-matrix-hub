# Backend fixes BE-36, BE-37, API-22, API-27, API-28

`fix-backend-wp-v2-bugs` fixes the five medium findings that the WP-V2 C0
batches recorded as known failures, then refreshes the simulator evidence that
the transport changes made stale. All five reproducing scenarios now pass.
**1,441 records were recorded and all of them pass**, with no known failures.
The ledger reports **zero stale features and zero fresh failures**.

| Finding | Fix | Failed before the fix | Scenarios now passing |
| --- | --- | --- | --- |
| BE-36 | `GET /api/presets` reads each slot from the matrix (Telnet `r preset N`, cached for `OREI_STATUS_CACHE_TTL`, expired by writes and forced status reads) and adds `routing_source`: `matrix`, or `saved` when the slot cannot be read. An incomplete `r preset` answer is never reported as read. A custom save keeps the full stored mapping as the hub copy | `tests/sim/test_sim_preset_slots.py` (6), `tests/test_telnet_outcomes.py` preset cases | `preset_read.device_slot_1..8`, `saved_current_1..8`, `saved_partial_1..8` |
| BE-37 | `TelnetClient.send_cec` reports one of four outcomes: acknowledged, rejected, not sent or unknown. HTTP fallback happens only after `E00`/`E01` or when Telnet was not connected. After an unknown outcome, the command is not resent and the request fails | `tests/sim/test_sim_cec_ambiguity.py` (5 of 7) | `cec_telnet.input_interrupted_volume`, `cec_telnet.output_interrupted_volume` and the 200 healthy `cec_telnet.*` |
| API-22 | Profile outputs keep and return `scaler_mode` (`device_codes.SCALER_MODES`, 1-5) and `arc` (boolean). Create and edit share one validator | `tests/sim/test_sim_profile_capture.py` (18 of 20) | `profile_crud.post/put_scaler_arc`, new `profile_crud.post/put_scaler_invalid`, `post/put_arc_invalid` |
| API-27 | Save-current needs complete video and output reads. A failed or incomplete read answers 502 with the reason and creates no profile | `tests/sim/test_sim_profile_capture.py` save-current cases | `profile_state.capture_output_read_failure`, `capture_video_read_failure` |
| API-28 | Macro create and edit share one name/description validator | `tests/test_macro_validation.py::TestMacroDescriptionValidation` (2 of 4) | `domain_manage.macro_update_description_long` |

Each new test was run against the `origin/main` sources first, and the failures
are listed above. The same tests pass with the fixes. The scenarios' `finding=`
links are removed. Recall does not apply the saved `scaler_mode`/`arc`
(API-29, owner decision).

## Evidence

The evidence comes from the packaged image `hdmi-matrix-hub:fix-backend-wp-v2-bugs`
(`sha256:069076733456776b1b9b4be9c490b35f64293ea289dae6cc23ebf80da4abd14a`, built
from `b30436afd26eba01a32f2202063ad187477d0066`) and a simulator image built on
it. Each scenario module gets a fresh simulator, hub and fixture-data volume.
The records hold the container's actual hub environment.

| Client | Records | Hub environment |
| --- | ---: | --- |
| API, `cec_telnet.*` | 202 | `OREI_USE_TELNET_CEC=true` |
| API, `profile_state.*` | 108 | `OREI_USE_TELNET_CEC=false`, `OREI_STATUS_CACHE_TTL=0` |
| API, every other scenario | 1,038 | `OREI_USE_TELNET_CEC=false` |
| Browser (Chromium, shipped web UI) | 53 | default |
| Home Assistant 2026.9.3 container | 19 | default |
| Scripted Remote 3 | 18 | source hub in UC mode (it cannot run in an external container) |
| Deployment (`pytest tests/deploy -m docker`) | 3 | image and compose |

Superseded records with the same scenario, client, target, level and result were
deleted, along with their `features.yaml` lines (owner's evidence policy). That
removed 1,091 records, and the ledger was unchanged before and after the
pruning. The C0 failure records cited by earlier reports are kept; they are
stale after the fix. The
[combined run summary](evidence/F-MTX-030/2026-10-03-wp-v2-backend-fixes/run-summary.json)
and the harness (`campaign.py`, `vrun.py`, `run_api.sh`) are archived next to it.

## Harness notes

Two problems in running the runner from a Windows host affected the first
attempt. Neither is a hub defect. The failing records from that attempt were
deleted before recording again:

- With Python 3.12 on Windows, `time.time()` has a 15.6 ms tick.
  `WsObserver.sync()` keeps events with `t >= t0`. It can therefore take the
  welcome snapshot for the answer to its `get_status`, which skips the hub's
  fresh read. `cec_caps.*` then failed on stale names with the `origin/main`
  image too (11 of 88). The harness anchors `time.time` to `perf_counter`.
- The api client sends every action with the X-Forwarded-For value fixed at
  client start. Fast modules exceed the hub's limit of 60 requests per 10 s per
  IP and get 429. The harness spaces scenarios 0.3 s apart.

## What this does not prove

Slot contents and Telnet CEC acknowledgements on the real BK-808 still need
hardware evidence (V4), and so does a single physical volume step. Simulator
acknowledgements follow the documented HIL assumption.
