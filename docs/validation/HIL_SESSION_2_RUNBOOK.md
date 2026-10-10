# Hardware session 2: runbook

This session gets the v0.2.0 hardware proof (V4) for routing, presets, matrix power and TV CEC power,
on your BK-808 at `192.168.0.100`. You run every command in your own PowerShell, so the hardware
results are attested by you (`--operator "Ryan Haver"`). Allow about 60-90 minutes.

What it changes: routing, matrix power and output settings, each put back after its scenario and
checked by reading the matrix again. CEC turns the TV, soundbar and PS3 on, and changes the
soundbar's volume by one step. Those can't be undone automatically, so they only run in step 5,
with an extra flag. **Nothing overwrites a preset slot.**

Your wiring, as the questions assume it: TV on output 1, soundbar on output 2, PS3 on input 1,
Apple TV on input 2. Inputs 3-8 have nothing connected. When a question asks whether a display
"shows the source on input 4/5/6", **the TV switching to "No signal" counts as yes**. It means the
TV left its previous source.

## 0. Setup (once)

```powershell
cd C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration
git switch main; git pull          # this runbook's tooling must be on main, clean
.\.venv\Scripts\Activate.ps1
$env:OREI_PASSWORD = "admin"; $env:MATRIX_PASSWORD = "admin"
$M = "192.168.0.100"
```

Have the TV on, the TV remote handy, and optionally your phone for photos. When a question asks
for a photo path you can just press Enter.

## 1. Read-only checks (no flags; nothing changes)

```powershell
python -m tools.validate run --target hardware --matrix-host $M --operator "Ryan Haver" --record `
  --out build/hil-session-2/1-read-only --scenario preset_read.catalog_matches_device
```

This compares what the hub reports for presets 1-8 with what the matrix itself stores. The runner
reads the matrix over its own connection, without the hub. Expect `PASS ... V4`.

## 2. Front-panel push window (capture tool, about 3 minutes)

```powershell
python -m tools.hil.capture --host $M --mode probe --push-seconds 90 --out build/hil-session-2
```

During the 90-second window, press a few front-panel buttons: route an input to an output, and
recall a preset. When it asks "Restore it?", answer `Y`.

## 3. Live CEC capture (capture tool)

```powershell
python -m tools.hil.capture --host $M --mode write --i-understand-this-changes-the-matrix `
  --only cec-live --include cec-live --cec-output 1 --out build/hil-session-2
```

It sends real CEC commands to the TV (off/on, mute, volume, input) and asks what the TV did after
each one. This also confirms the shape of the Telnet CEC acknowledgement that BE-37/BE-38 assume.

## 4. Restorable changes: routing, presets, power, profiles

**Before this step:** open the web UI's Presets drawer and look at preset 3's routing. Make sure
the live routing is *different* (route the TV somewhere else if needed). Otherwise the recall
can't show anything and is reported as inconclusive.

```powershell
python -m tools.validate run --target hardware --matrix-host $M --operator "Ryan Haver" --record `
  --allow-writes --out build/hil-session-2/4-writes `
  --scenario routing.switch_one --scenario routing.route_all --scenario presets.recall `
  --scenario power.standby --scenario power.wake `
  --scenario profiles.recall_routing --scenario profiles.recall_output_settings
```

Each scenario snapshots the matrix, makes one change, asks you one y/n question, then restores
the snapshot and verifies it. If a restore can't be verified, the run stops. Questions you'll get:

| Scenario | Question | What to look for |
| --- | --- | --- |
| routing.switch_one | display on output 1 shows input 6 | TV goes to "No signal" |
| routing.route_all | all displays show input 4 | TV "No signal" |
| presets.recall | displays show preset 3's sources | TV shows preset 3's input for output 1 |
| power.standby | front panel in standby | panel dark/standby |
| power.wake | matrix on again | panel lit, picture back |
| profiles.recall_routing | outputs 1-3 show input 5 | TV "No signal" |
| profiles.recall_output_settings | output 2 muted; output 1 HDR per profile | soundbar silent |

## 5. CEC to real devices (not restorable)

```powershell
python -m tools.validate run --target hardware --matrix-host $M --operator "Ryan Haver" --record `
  --allow-writes --allow-unrestorable --out build/hil-session-2/5-cec `
  --scenario cec.output_power_on --scenario cec.output_volume_up --scenario cec.input_power_on `
  --scenario profiles.recall_power_macro
```

Turn the TV **off** with its remote before you start: `cec.output_power_on` asks whether it
turned on. The soundbar's volume goes up one step, and the PS3 and Apple TV may power on. Any
matrix setting a scenario changes on the way (routing, output settings, CEC-enable flags) is still
put back. Only the effects on the devices themselves stay.

## 6. Tablet viewport

On the Galaxy Tab A11, open `https://whatismyviewport.com` in the browser you use for the kiosk.
Note the **viewport width × height** and the **device pixel ratio**, in the orientation the kiosk
uses.

## 7. Remote 3 (manual; note what you see)

- Set up the integration again with a **wrong password** first: it should say the password is
  wrong, then accept the right one.
- UC-28: rename an input in the web UI. Does an entity that's already on a Remote page show the
  new name?
- The CEC toggle (TV power) on the Remote: does it toggle the TV?
- Change routing on the matrix's **front panel**. Does the Remote's matrix power and source state
  follow?

## 8. Hand back

Tell me when you're done, and include:

- the answers to steps 6 and 7;
- anything that surprised you.

I'll do the rest, and nothing is published until you approve the PR:

- check the records in `docs/validation/evidence/` and the captures in `build/hil-session-2/` for
  passwords;
- write `docs/validation/<date>-hil-session-2.md`;
- update the kiosk-tab-a11 viewport, with a gallery for your approval;
- tick the register;
- open the PR.

If something fails or looks wrong, stop and tell me rather than retrying. Each failure is a
finding.
