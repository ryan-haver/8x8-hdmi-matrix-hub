# Preparing hardware session 2: preset checks that work on a real matrix

Branch `hil-session-2-prep`, tooling commit `b6dbfac`. The owner's steps are in
[`HIL_SESSION_2_RUNBOOK.md`](HIL_SESSION_2_RUNBOOK.md). No real hardware was contacted.

## Why

The v0.2.0 gate needs routing, presets, matrix power and TV CEC power at V4. Preparing the session
found two tooling defects that would have failed the preset proof on any real matrix:

- **VAL-13.** `presets.recall` expected the routing the *simulator seed* stores in preset 3 (`[6] * 8`).
  The runner also had no way to read a real slot: the firmware answers no HTTP preset read (HIL-01).
- **VAL-12.** On the hardware target the runner did not wait for its hub's Telnet link. The first
  Telnet-dependent read (preset slots, BE-36) could come too early, and the catalog then reported
  every slot as `routing_source: "saved"`.

## What changed

- **`HardwareDevice.preset_slots()`** reads all eight slots on a Telnet session of its own
  (`r preset N`), without the hub. It reuses the HIL capture tool's client and parser, both proven
  on the device in session 1, which also showed that a second concurrent Telnet session works.
- **`PresetCatalog`:** `GET /api/presets` must report each slot as read from the matrix, equal to the
  device's own slot (`{}` for an empty one). The new scenario `preset_read.catalog_matches_device`
  is read-only, so it runs on hardware without any flags.
- **`PresetRouting(slot)`:** after a recall, the routing equals what the slot stores on the device.
  The check fails as inconclusive if that routing was already live. `presets.recall` uses it for
  preset 3.
- **Readiness:** the runner waits up to 10 s for the Telnet link of any hub it started. That now
  includes hardware runs; an operator's own `--hub-url` hub is still not waited for.

Not covered: `presets.save_custom_mapping` still reads slot routing from the general device state,
which has none on hardware. It also overwrites a real slot, so it is not part of session 2.

## Proof

- **Failing first** (`tests/validation/test_preset_slots.py`):
  - The suite first failed to import: the reader and checks did not exist.
  - The hardware-mode catalog scenario, against the simulator standing in for the matrix, then
    failed with all 8 slots `"saved"` until the readiness fix.
  - `presets.recall` against owner-style slot contents failed on `[6] * 8`.
- **After:** all 5 tests pass, and so does the validation suite (80 tests).
- **Rehearsal:** the runbook's steps 1, 4 and 5 were rehearsed with its exact commands against the
  simulator as the matrix, with owner-like slots (preset 3 different from the live routing, preset 8
  empty) and scripted answers. All 12 scenarios passed. Rehearsal records are not evidence.

## Scenario evidence (shipped image)

- **Setup:** the image built at `b6dbfac` (`sha256:2bd619278c98d61294ab82371f95113d05b659b352f970dc6dea08534226fd96`)
  with a simulator container.
- **Results:** `preset_read.catalog_matches_device` passed at V2 (API), and `presets.recall` passed at
  V2 (API) and V3 (browser). The device login was redacted (6 values).
- **Pruning:** the owner's pruner treats records linked from the generated `LEDGER.md` as cited. The
  UI round 2 prune had therefore kept 25 superseded records, which `LEDGER.md` still linked when it
  ran. Pruning and regenerating again until nothing more dropped removed them (40 `features.yaml`
  lines). Each has a newer passing record, and the ledger is identical before and after.
- **Ledger:** unchanged levels (V3 92, V2 67, V1 83, V0 26, V4 0). 0 stale. The gate passes.
