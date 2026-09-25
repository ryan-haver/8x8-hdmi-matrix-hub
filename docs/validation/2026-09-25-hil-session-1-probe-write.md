# HIL Session 1 — Part 2: probe and write

| | |
| --- | --- |
| **Date** | 2026-09-25 |
| **Device** | OREI BK-808 at 192.168.0.100, MCU V1.10.01, web module V2.00.03 |
| **Operator** | automation, with the owner's go-ahead ("whenever you want"). Front-panel push window skipped (`--push-seconds 0`); live CEC and reboot groups not run. |
| **Tools** | `python -m tools.hil.capture --mode probe` and `--mode write` (26 tests, 93 commands, snapshot/restore), redaction of MAC and hostname |
| **Output** | `tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/{probe,write}/` (verified: no password, MAC or hostname in any file or base64 body) |
| **Result** | Device **restored to its initial state and verified** after the write run |

## Probe findings

- **Login:** wrong password → `{"comhead":"login","result":0}`; correct → `result: 1`. BE-05 is real on hardware (the old hub treated both as success); the WP-A1 fix handles it.
- **Sessions:** reads from this PC returned data without logging in, and a session was still alive after 300 s idle. Whether reads need a login at all is still open; it needs a run from a machine that has never logged in.
- **Unknown or malformed HTTP requests get no answer** (the client times out). Right after those probes, one `get system status` also timed out, then the device recovered.
- **CEC enable:** the bulk array form (`inputindex`/`outputindex` with 8 entries) → `result: 1`; the hub's single-port form → `result: 0` (BE-13 confirmed).
- **Telnet:** `E00` = unknown command, `E01` = bad parameter. Commands need `!` and CR LF. Upper case works, pipelining works, and a second concurrent session works. A set command answers with an echo, then an acknowledgement such as `output8->input7`. `s out N stream …` → `E00` (unknown).

## Write findings

| Group | Commands the hub sends | Device behaviour |
| --- | --- | --- |
| Routing (HTTP, incl. output 0 = all) | `video switch` | ✅ applied, `result: 1`; invalid ports → `result: 0` |
| Input/output names | `set input name`, `set output name` | ✅ applied (40-character name accepted; truncation needs review) |
| Beep, panel lock | `set beep`, `set panel lock` | ✅ applied |
| Standby / power | `set poweronoff` | ✅ applied; reads still answer in standby |
| CEC enable (bulk) | `set cec index` (arrays) | ✅ applied |
| CEC command | `cec command` | accepted even with an invalid index or no target port (`result: 1`): the device doesn't validate |
| **Output stream, HDCP, HDR, scaler, ARC, audio mute** | `set output stream/hdcp/hdr/scaler/arc/mute` | ❌ **no answer (timeout)**; nothing changes |
| **Input EDID, EDID copy** | `set input edid`, `copy edid` | ❌ no answer |
| **External audio** | `set output exa*` | ❌ no answer |
| **LCD timeout** | `set lcd on time` with `time` | ❌ `result: 0` for every code |
| Telnet routing | `s output N in source M` | ✅ |
| Telnet `s av …` (vendor syntax), `s out N stream` | | ❌ `E00` |

## The protocol the device's own web interface uses

The BK-808 serves its own configuration web interface. Reading how that interface talks to the device (`/cgi-bin/instr`, JSON with `comhead`) shows the commands this firmware actually implements for the settings above. Per-port values are sent as a `[port, value]` pair, where port `0` means all outputs:

| Setting | Command (`comhead`) | Value field |
| --- | --- | --- |
| Output HDCP | `tx hdcp` | `hdcp: [out, value]` |
| Output stream on/off | `tx stream` | `out: [out, value]` |
| Output audio mute | `set output audio mute` | `mute: [out, value]` |
| ARC | `set arc` | `arc: [out, value]` |
| HDR conversion | `set hdr conversion` | `hdr: [out, value]` |
| Scaler | `set video scaler` | `scaler: [out, value]` |
| Output resolution | `set output resolution` | `resolution: [out, value]` |
| Input EDID | `set edid` | `edid: [in, value]` |
| User EDID upload | `set user edid` | — |
| LCD on time | `set lcd on time` | `"lcd on time": value` |
| System HDCP | `set hdcp` | `hdcp: value` |
| Preset save / name | `preset save`, `preset name` | — |
| External audio | `set ext-audio mode`, `set ext-audio out` (`out: [n, value]`), `set ext-audio index` | — |
| Reboot | `reboot` | `reboot: 1` |
| Factory reset, baud rate, test pattern, network | `set factory`, `set baudrate`, `set tpg`, `set network` | — |

These come from the interface's code, **not yet from a device answer**. WP-A4 part 2 implements them and proves each one with another write run (snapshot/restore) before the hub relies on them.

## Findings raised

HIL-09 … HIL-14 in `docs/REMEDIATION_PLAN.md` §4.11.

## Still open (needs the owner at the matrix)

- Front-panel push notifications (`--push-seconds 30`, with the owner pressing buttons).
- Live CEC to the TV (`--include cec-live`), and reboot (`--include reboot`).
- First V4 scenarios with the owner confirming what the TV shows.

## Follow-up: WP-A4 part 2 (no device contact)

- **Hub** (`src/orei_matrix.py`, `src/device_codes.py`): sends the web interface's commands above for output stream/HDCP/HDR/scaler/ARC/audio mute, EDID (copy = `set edid` 39+N), LCD (`"lcd on time"`), ext-audio (`set ext-audio mode|out|index`, `ext-audio switch`), preset name and reboot. `src/device_codes.py` maps the API values to device codes in one place: HDR and scaler are 1-based in the API and 0-based on the device (the device web interface writes back the codes it reads, and the reads agree: HDR 0 / scaler 0 = pass-through, scaler 4 = audio only); HDCP, EDID, LCD and ext-audio mode are identical. REST reads now report API values. CEC enable only uses the array form (HIL-10); displays use the web interface's separate output table (0 on, 1 off, 2 mute, 3 vol-, 4 vol+, 5 active; BE-14). The web interface also shows that the ninth entry of the per-output arrays is its "All Output" row (HIL-04) and that `get system status.mode` is the LCD code.
- **HIL-12**: a timeout, HTTP error or unparseable answer on one command is a failed command ("device did not answer ..."); the link is only marked lost when a follow-up `get system status` (one retry for the stall seen above) fails too.
- **Simulator**: implements the new commands, ignores unknown comheads and non-JSON bodies like the device, and now matches every probe and write capture. `python -m tools.simulator --golden tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03 --report`: **25 confirmed, 0 contradicted**, 5 need review (session behaviour, ninth entry under port-0 writes, ext-audio index), 12 without evidence (the web-UI-derived commands, reboot, live CEC, push lines).
- **Capture tool**: a write test per new command with read-back through the status reads (table in `tools/hil/README.md`, "Verify the WP-A4 part 2 commands"), preset tests that read presets over Telnet `r preset N`, and the old commands as an "expected unanswered" `legacy` group.
- **Status**: the new commands are **web-UI-derived, not proven**. HIL-09 stays open until the verification run; `docs/OREI_API_COMMANDS.md` marks every command as verified (captured), web-UI-derived or not implemented.
