# HIL Session 1 — Part 1: read-only capture

| | |
| --- | --- |
| **Date** | 2026-09-25 |
| **Device** | OREI BK-808 at 192.168.0.100, MCU firmware V1.10.01, web module V2.00.03 |
| **Hub commit** | `26bb3cf` (main) |
| **Operator** | automation (read-only; no device state changed) |
| **Tool** | `python -m tools.hil.capture --mode read` (see `tools/hil/README.md`) |
| **Output** | `tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/` (47 records; MAC address and hostname redacted) |

## What was done

- TCP reachability from the capture PC (192.168.0.229, same subnet): HTTPS 443 open (23 ms), Telnet 23 open (1 ms).
- `read` mode: login, every HTTP read the hub sends plus documented reads, and every Telnet read (`status`, `r fw version`, `r type`, `r link in/out 1–8`, `r preset 1–8`), stored byte-exact.
- `python -m tools.simulator --golden <captures> --report`: compared every captured answer with the simulator's assumptions.

`probe` and `write` modes were **not** run. They need the owner present: probe tries one wrong-password login and prompts for front-panel actions, and write changes live routing and settings, restoring them afterwards.

## Results

| Check | Result |
| --- | --- |
| Login | Succeeds with `{"comhead":"login","result":1}`. The hub accepts this; the simulator assumed `"success"`. |
| HTTP reads | All 8 status reads answered 200 with JSON. None is byte-identical to the simulator: field sets and formatting differ. |
| `get output status` | Uses a `name` field. The hub was right; the simulator was wrong. |
| `get video status` | `allsource` has **9** entries; names match the hub's saved config (NES, SNES, Sega, N64, Switch, PS3, Apple, Switcher / TV, Sound, Out3–8). |
| HDR value | The device reports HDR **0** on output 1. The hub and simulator only accept 1–3. |
| `get routing status`, `preset get 1–8` | **No answer (timeout).** This firmware doesn't implement them. |
| Telnet banner | Starts with option negotiation (IAC) and a "welcome" banner (`fw version :v1.10.01`). The hub filters IAC. |
| Telnet reads | The device **echoes each command** (e.g. `r link in 1!`) before the answer. `status` returns 111 lines headed "get the unit all status:"; the simulator had 88. |
| Assumption report | 8 contradicted, 1 needs review (`ext-audio index`), 26 not yet captured (need probe/write), 3 confirmed. |

## Findings raised

HIL-01 … HIL-04 in `docs/REMEDIATION_PLAN.md` §4.11. The simulator corrections (8 contradicted assumptions) are WP-A4.

## Follow-up: WP-A4, read part (no device contact)

- **Simulator** corrected to the captures: the report now shows **0 contradicted, 12 confirmed**, 2 need review (`ninth-entry`, `ext-audio-index`), 25 without evidence (probe/write). All 8 HTTP reads are byte-identical to the simulator's own answers for the captured state (compact JSON + CR LF, device key order), as are the banner with its IAC negotiation, the `status` dump and all 26 `r ...` answers (including the echo). `get routing status` and `preset get` are never answered, like the device.
- **Hub proven against the real bytes** (V2 against real data where REST is in the path, V1 driver-level otherwise; no V4 claimed): `tests/test_telnet_real_captures.py` replays the captured Telnet segments with their timing to the real `TelnetClient`; `tests/sim/test_golden_hub.py` runs `OreiMatrix`, the Telnet client and the REST API against the simulator in golden mode.
- **Hub bugs found with the real data and fixed:** HIL-05 (multi-line Telnet answers cut short; `r preset` returned one output), HIL-06 (save-current scene read a field the device does not send), HIL-08 (input names cut at `-`), HIL-01 (no HTTP preset fallback). HIL-04: the hub keeps outputs 1-8 of the 9-entry arrays.
- **Read-side evidence for BE-15:** the audio-only output reports scaler **4**, and the Telnet status prints it as "audio only", which is what the hub checks. Pass-through is **0** for both scaler and HDR. Whether writes use 1-based codes (1 = passthrough, 5 = audio only as documented) is for the write capture.
- **HIL-07:** `telnet/status.json` contains the matrix's MAC in lower case: the capture tool's `--redact` was case-sensitive. The tool is fixed; the committed file needs an owner decision (re-capture, or rewrite the branch before merge).
- **Capture tool changes for the next session:** unanswered `get routing status` / `preset get` are warnings, not errors (the read run exited 1 because of them), later snapshots skip them, and the HDR/scaler write tests now try 0 as a value. The preset write tests need `get routing status` for their snapshot, so they are skipped on this firmware until they read presets over Telnet.

## Next (needs the owner present)

1. `--mode probe`: wrong-password login (check that the account isn't locked afterwards by logging in through the matrix web page), session behaviour, Telnet error codes, and front-panel notifications (the tool prompts for button presses).
2. `--mode write`: every write command with snapshot and restore. Watch the TV on output 1; routing changes briefly.
3. First V4 scenarios with `python -m tools.validate run --target hardware --allow-writes`: routing, presets, matrix power, TV CEC power, one profile. The operator confirms what the TV shows.
