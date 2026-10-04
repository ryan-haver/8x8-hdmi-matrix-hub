# Backend follow-ups API-29, API-30, API-31, BE-38

`fix-backend-followups` implements the four follow-ups the owner approved on
2026-10-03, after [the WP-V2 backend fixes](2026-10-03-wp-v2-backend-fixes.md).
Every new test failed against the `origin/main` sources first. All new and
reproducing scenarios pass. The BE-38 change touches `src/orei_matrix.py`,
which every scenario covers. That made 144 features stale, so the simulator
evidence was refreshed again: **1,454 records, all passing**. The ledger reports
**zero stale features and zero fresh failures**.

| Finding | Change | Failed before the change | New scenarios (all pass) |
| --- | --- | --- | --- |
| API-29 | The shared state writer (DI-11) applies a saved `scaler_mode` with `set video scaler` (API 1-5 mapped to device 0-4 by `device_codes`) and `arc` with `set arc`, the HIL-09 commands. Recall and scene profile steps behave the same. Unset fields are not written, scene overrides skip them, and scene validation reports their conflicts | 5 of the 6 API-29 tests in `tests/sim/test_sim_profile_followups.py`. The one that passed, a profile without the settings writes nothing, checks behaviour that must not change. The whole file: 13 of 15 failed | `profiles.recall_scaler_arc` (api V2, browser V3), `profiles.recall_leaves_unset_scaler_arc`, `scenes.profile_step_scaler_arc`, `scenes.override_leaves_scaler_arc`, `scenes.conflicts_scaler_arc` |
| API-30 | One `_validate_outputs` for create and edit. An invalid edit answers 400 with the create error and leaves the profile unchanged | `test_put_refuses_what_post_refuses` (6 cases) | `profile_crud.edit_reject_{missing_input,output_zero,output_nine,input_zero,input_nine}` |
| API-31 | Save-current takes each output's `enabled` from `allout` (1 on, 0 off) and answers 502 for any other value | `test_save_current_records_the_real_stream_state`, `..._refuses_an_unknown_stream_state` | `profile_state.capture_stream_states` |
| BE-38 | After an unknown Telnet CEC outcome, only `CEC_SAFE_TO_RESEND = {POWER_ON, POWER_OFF}` goes on to HTTP; every other command still fails without a resend | `test_the_resend_safe_set_is_power_on_and_off_only` and the four power cases of `test_http_fallback_after_an_unknown_outcome_only_for_power`. The other 21 input and output commands pass unchanged | `cec_telnet.{input,output}_interrupted_power_{on,off}`. `cec_telnet.*_interrupted_volume` still pass |

## Evidence

The evidence was recorded against the packaged image `hdmi-matrix-hub:fix-backend-followups`
(`sha256:0078ebd82f7576c4304650e3f29ee3aaee18d92638594b0b66f2506fa94ad05a`,
source `7dbc4dc70c70610f5e7f0f9becff1c0b7c3c8f23`). The harness is the same as in
the previous report: one fresh stack per scenario module, the high-resolution
clock, and paced scenarios.

| Client | Records | Hub environment |
| --- | ---: | --- |
| API, `cec_telnet.*` | 206 | `OREI_USE_TELNET_CEC=true` |
| API, `profile_state.*` | 109 | `OREI_USE_TELNET_CEC=false`, `OREI_STATUS_CACHE_TTL=0` |
| API, every other scenario | 1,048 | `OREI_USE_TELNET_CEC=false` |
| Browser | 54 | default |
| Home Assistant 2026.9.3 | 19 | default |
| Scripted Remote 3 | 18 | source hub in UC mode |

The deployment records were not re-run. Their covers did not change, and they
stay fresh.

Superseded records were pruned with the owner's script: 1,435 removed, and the
ledger was unchanged before and after. The
[combined run summary](evidence/F-DOM-003/2026-10-04-backend-followups/run-summary.json)
and the harness are archived next to it.

## After merging main (PR #26)

The merge brings main's `web/` changes and its evidence refresh, recorded at
`5674ff51`. The evidence folder is now the union of both parents' records.
`features.yaml` lists both sides. Freshness was checked at the merge commit
`d6baf3ca`:

- main's `web/` change made 45 API pairs stale (scenarios whose covers include
  the web files) and 47 browser pairs;
- this branch's `src/` changes made main's own records stale;
- every other (scenario, client) pair still had a fresh record.

Only those 92 pairs were recorded again, against the image built at `d6baf3ca`
(`sha256:2103d7114eae70bb2b25dfae6ca843a3bedf716a4474dd1551276cc31200c528`). All
92 pass ([summary](evidence/F-DOM-003/2026-10-04-backend-followups/run-summary-merge.json);
selection by `stale_list.py`, run by `run_stale.sh`). The owner's script then
pruned 1,262 superseded records from both sides, and the ledger was unchanged
before and after. The ledger reports zero stale features.

## What this does not prove

The effect of the video mode and ARC writes on a real display or soundbar, and
how the real BK-808 behaves when the CEC power frame is sent twice, still need
hardware evidence (V4).
