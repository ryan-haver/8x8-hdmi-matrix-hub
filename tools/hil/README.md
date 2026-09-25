# Hardware-in-the-loop tools

Tools in this folder talk to a **real OREI BK-808 matrix**. None of them run in CI. pytest only collects `tests/`, and the capture tool's own tests (`tests/hil_tools/`) run it against the simulator.

- [`capture/`](capture/) is the scripted HIL-A capture tool: `python -m tools.hil.capture`. The runbook below explains how to use it.
- The [older ad-hoc scripts](#older-ad-hoc-scripts) are listed at the end.

---

## Runbook: HIL Session 1 (HIL-A, protocol conformance and capture)

Plan reference: `docs/REMEDIATION_PLAN.md` §5.2 (HIL-A). The goal is to record how the real BK-808 answers every command the hub sends. The recordings become the simulator's golden fixtures, and they settle the open protocol questions (BE-04, BE-05, BE-07, BE-13, BE-14, BE-15, BE-25, API-07, push notifications).

The session has three captures. Run them in this order:

| # | Mode | Changes the matrix? | Time |
| --- | --- | --- | --- |
| 1 | `probe` | No. It sends one wrong-password login and a few commands that write the value the device already has. During the push window **you** change things on the front panel, and the tool puts the routing back afterwards. | 2-3 min, plus the `--idle-waits` you choose (up to ~20 min) |
| 2 | `read` | No. Reads only. | about 1 min |
| 3 | `write` | **Yes.** It changes routing, names, output settings, EDID, CEC enable, ext-audio, beep, lock, LCD and power, and restores each one. | roughly 10-20 min |

Run `probe` first. The device may track sessions per client IP (the probe finds out), so right after `read` it would still see a live session and could not record the "not logged in" answer.

### 1. Prerequisites

- [ ] The BK-808 is on the LAN and you know its IP address. The examples use `192.168.1.50`.
- [ ] You know the web login. The factory default is `Admin` / `admin`.
- [ ] You are standing at the matrix. The probe asks you to press front-panel buttons and to unplug and replug a cable.
- [ ] The repository is checked out at the commit you are validating, with the dev environment:

  ```bash
  python -m venv .venv
  .venv/bin/pip install -e ".[dev]"          # Windows: .venv\Scripts\pip install -e ".[dev]"
  ```

- [ ] **Nothing else is talking to the matrix.** This matters for the session measurements and for write mode:
  - Stop the hub: `docker compose stop`, or stop `run.py` / `run_server.py`. Also stop the Remote 3 integration driver if it runs elsewhere.
  - Disable the Home Assistant integration, or stop HA.
  - Close every browser tab that has the matrix web UI open.
  - Then wait about 2 minutes, so the matrix sees no traffic before the probe starts.
- [ ] Decide which ports the write tests may use. The defaults are **output 8, input 8 and preset 8**. Choose ports whose temporary changes do not matter, ideally with nothing connected, and pass them with `--test-output`, `--test-input` and `--test-preset`.
- [ ] Write down the firmware versions shown in the web UI (system/about page), including the IP-module version, for the session report.

The password is never stored. You can pass it with `--password`, or put it in the `OREI_PASSWORD` environment variable, or type it when prompted (the default).

### 2. Safety notes

#### probe mode

- It sends one login with a deliberately wrong password. If the firmware locks the account after failed logins, you will see that in the output. Wait, then log in through the web UI to check.
- It sends `set cec index` in the documented shape and in the hub's single-port shape, both with the values the device already has. It also sends the Telnet commands `s output 8 in source <current>`, `s beep <current>`, `s lock <current>` and `s out 8 stream <current>`. It then checks that nothing changed, and restores and warns if something did.
- The Telnet error probes send invalid commands (port 9, unknown words). The tool checks the state afterwards and restores it if anything changed.
- During the push window **you** change things. When the window closes, the tool compares the state before and after and asks "Restore it? [Y/n]".

#### write mode

- Every command it will send is printed before anything happens. Nothing is sent until you type `yes`, unless you pass `--yes`.
- Things you will notice: routing changes on the test output, and on **all outputs** for the "route all", preset-recall and `s output 0` tests. The matrix goes into **standby** and back (all displays go dark for a few seconds). The test input's **EDID changes**, so its source device renegotiates HDMI. The panel lock and beep toggle.
- After each test the tool restores the state it saw before that test, and checks the result with a fresh read. At the end it restores the state from before the first test and checks again.
- **Ctrl+C:** the first press stops the run and starts the restore. Further presses are ignored while the restore runs. The fourth press forces an exit without finishing the restore (don't do that).
- These cannot be restored automatically:
  - **Preset names.** No command sets them. A preset save might rename a preset; you get a warning if it does.
  - **The LCD timeout**, if the LCD test did not run with Telnet. You get a warning; set it back on the front panel.
- If a restore fails, the tool prints `THE MATRIX WAS NOT FULLY RESTORED` with the differences and exits with code 3. `write/snapshot-initial.json` has every original value, and `write/restore-log.jsonl` shows what was already put back. Fix the rest in the web UI.
- Opt-in groups, which never run unless you add them with `--include`:
  - `cec-live` sends real CEC commands to the display on `--cec-output`. The display will turn off and on, mute, and change volume and input, and the tool asks you what the display did after each command.
  - `reboot` reboots the matrix, once over HTTP and once over Telnet, and waits for it to come back each time.

### 3. Commands

The examples use bash with `.venv` activated. In PowerShell, write `$env:OREI_PASSWORD='...'` instead of `export`. Everything else is the same.

```bash
export OREI_PASSWORD='admin'          # or leave it unset and type it when asked
HOST=192.168.1.50
```

**Step 1: probe.** Pick idle periods for the session-expiry measurement. Each one waits that long without sending anything, and the tool stops at the first expiry. Try `60,300,900` first. If the session survives 15 minutes, `1800` is enough.

```bash
python -m tools.hil.capture --host $HOST --mode probe --idle-waits 60,300,900 --push-seconds 45
```

When the output reaches `PUSH NOTIFICATION WINDOW`, press Enter and then, during the 45 seconds:

1. change the routing of an output with the front-panel buttons;
2. unplug the HDMI cable of a connected display, wait 3 s, and plug it back in;
3. if you can, switch a source device off and on.

**Step 2: read.**

```bash
python -m tools.hil.capture --host $HOST --mode read
```

**Step 3: write.** This one changes the matrix.

```bash
python -m tools.hil.capture --host $HOST --mode write --i-understand-this-changes-the-matrix \
    --test-output 8 --test-input 8 --test-preset 8
```

Read the printed plan, then type `yes`. To run only some groups, use `--only routing,names` or `--skip power`. The groups are `routing`, `presets`, `names`, `output`, `edid`, `cec-enable`, `cec-invalid`, `ext-audio`, `system`, `telnet`, `power`, plus the opt-in `cec-live` and `reboot`.

**Optional: live CEC (BE-14) and reboot.**

```bash
# a display with CEC on output 1; you will be asked what it did after each command
python -m tools.hil.capture --host $HOST --mode write --i-understand-this-changes-the-matrix \
    --only cec-live --include cec-live --cec-output 1
python -m tools.hil.capture --host $HOST --mode write --i-understand-this-changes-the-matrix \
    --only reboot --include reboot
```

Every run writes into the same folder, `tests/fixtures/device/<model>_<MCU version>_web-<web version>/`. The folder name comes from the versions the device reports. `manifest.json` gets one entry per run. Other options: `--out DIR` (`{firmware}` in it is replaced by the derived name), `--firmware NAME`, `--port`, `--telnet-port`, `--no-tls`, `--no-telnet`, and `--redact TEXT` to scrub more values such as the MAC address. See `--help` for the full list.

**Timing options.** A Telnet response counts as complete after `--telnet-idle` seconds of silence (default 1.0). If the `status` dump in `telnet/status.json` looks cut short (`"completion": "idle"` and it does not end with the `mac address:` line), re-run with `--telnet-idle 2`.

#### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | done |
| 1 | a problem was recorded (see `errors` in the output and in `manifest.json`), or the device was unreachable or rejected the login |
| 2 | usage error (for example write mode without `--i-understand-this-changes-the-matrix`) |
| 3 | **write mode could not restore the matrix**; fix it by hand (section 2) |
| 4 | a secret was found in the output; **do not commit** it, and report a bug |
| 130 | interrupted (the write-mode restore still ran) |

### 4. What each mode sends

**read.** Nothing that changes the device:

- HTTP: `login`, then `get video status`, `get output status`, `get input status`, `get cec status`, `get system status`, `get status`, `get network`, `get ext-audio status` (all with `"language": 0`, as the hub sends them), `get routing status` (documented, `"index": 1`), `preset get` for index 1-8, and `GET /`.
- Telnet (each command followed by `!\r\n`, like the hub): it records the banner, then sends `status`, `r fw version`, `r type`, `r link in 1-8`, `r link out 1-8` and `r preset 1-8`.

**probe.**

- HTTP: a `get system status` with no login. A `login` with a wrong password, followed by reads. A `login` from a fresh client, followed by reads with and without the cookie. The login-and-idle cycle for each `--idle-waits` value. `{"comhead": "hil capture unknown"}`, and a body that is not JSON. `set cec index` in both shapes with the current values.
- Telnet:
  - error probes: `hilcapture unknown`, `r link in 9`, `r link out 0`, `r preset 9`, `r link in x`, `s cec in 9 on`, `s cec hdmi out 1 hilbogus`, `s output 9 in source 1`;
  - framing variants, each on a new connection: `r type` without `!` then `!` alone, `r type!` with no CR LF, with LF only, in upper case, and two commands in one write;
  - the no-op set commands above;
  - a second connection sending `r type`;
  - the listening window.

**write.** The printed plan lists every exact command. In short, all against the test ports:

- HTTP: `video switch` (one output, all outputs, invalid ports), `preset set` / `preset save`, `set input name` / `set output name` (including a 40-character name), `set output stream|hdcp|hdr|scaler|arc|mute` (every value, with the Telnet `status` text read back for each), `set input edid` (including 38, 39, 47, 48), `copy edid` and `set input edid 15` (BE-25), `set cec index` in both shapes, invalid `cec command`s, `set output exa mode|exa|exa in source`, `set beep`, `set panel lock`, `set lcd on time` 0-4 (with the Telnet LCD line for each), `set poweronoff` (a read and a write while in standby).
- Telnet: `s output N in source M`, `s av M N`, `s output 0 in source M`, `s recall|save|clear preset P`, `s preset recall|save P`, `s beep`, `s lock`, `s out N stream`, `power 0/1` (what TelnetClient sends) and `s power 0/1`.
- With `cec-live`: every `s cec hdmi out N <word>`, and `cec command` object 1 index 1-6.
- With `reboot`: `set reboot`, and the Telnet `reboot`.

### 5. After the session

1. **Check the summary.** At the end of each run, the tool lists which simulator assumptions the capture has evidence for. Then run the report:

   ```bash
   python -m tools.simulator --golden tests/fixtures/device/<folder> --report
   ```

   It sorts every `ASSUMPTION(HIL-A)` into CONTRADICTED (the simulator must be fixed), NEEDS REVIEW, NO EVIDENCE, and CONFIRMED, and lists the ones that are still unconfirmed. Save the output for the session report.

2. **Look for anything you don't want to publish.** The tool already scans for the password, and the run fails with exit code 4 if it finds it. Also check by hand:

   ```bash
   git grep -n "$OREI_PASSWORD" -- tests/fixtures/device || echo "password not found"
   ```

   The captures include the matrix's LAN IP, MAC address and hostname. If that is a problem, capture again with `--redact <value>`.

3. **Try the simulator on the captures.** `python -m tools.simulator --golden tests/fixtures/device/<folder>` should start and print `golden ...: N HTTP reads, ...`. You can also point the dev stack at it.

4. **Write the session report** in `docs/validation/YYYY-MM-DD-hil-a.md`:

   ```markdown
   # HIL-A — Protocol conformance & capture (Session 1)

   - Date:
   - Operator:
   - BK-808 MCU firmware / web version / IP-module firmware:
   - Hub commit (git rev-parse HEAD):
   - Host OS / Python:
   - Capture folder: tests/fixtures/device/<folder>/
   - Test ports: output 8, input 8, preset 8

   | Check | Result | Evidence |
   | --- | --- | --- |
   | Every read command captured | | http/, telnet/ |
   | Every write: sent, read back, changed, restored | | write/*.json, restore-log.jsonl |
   | Wrong-password login response (BE-05) | | probe/login_wrong_password.json |
   | Session behaviour / expiry (BE-04) | | probe/session_*.json |
   | CEC enable payload (BE-13) | | probe/cec_enable_shapes.json, write/http_cec_index_single.json |
   | Output CEC table (BE-14) | | write/cec_live_output.json |
   | Audio-only scaler code (BE-15) | | write/http_output_scaler.json |
   | EDID copy (BE-25) | | write/http_copy_edid.json |
   | LCD codes (API-07) | | write/http_lcd.json |
   | Telnet E00/E01 and terminators (BE-07) | | probe/telnet_*.json |
   | Push notifications on front-panel changes | | probe/telnet_push_window.json |

   ## Simulator assumption report
   (paste the output of --report)

   ## Notes / anomalies
   ```

5. **Open a pull request** with the captures and the report:

   ```bash
   git switch -c hil/session-1-<folder>
   git add tests/fixtures/device/<folder>/ docs/validation/YYYY-MM-DD-hil-a.md
   git commit -m "test(hil): HIL-A captures from BK-808 <versions>"
   git push -u origin HEAD
   gh pr create --title "HIL-A captures: BK-808 <versions>" \
       --body "Session report: docs/validation/YYYY-MM-DD-hil-a.md. Simulator report attached below."
   ```

   Paste the `--report` output into the PR description. The captures are not used by anything yet. Phase 1 then fixes the simulator and the hub based on the report ("Update simulator with HIL-A golden captures", BE-07, BE-13, BE-14, BE-15, BE-25, API-07) and adds a golden-fixture test for each correction.

### 6. Troubleshooting

| Symptom | What to do |
| --- | --- |
| `logged in but reads return no data` | Wrong user or password, or the account is locked after the wrong-password probe. Log in through the web UI to check. |
| Warning `no-session probe: the read returned data without a login` | A session from this computer was still active. The tool retries after the wrong-password login. If the retry also returns data, stop everything that talks to the matrix (section 1), wait for the session to expire, and run probe again. |
| `Telnet ... unavailable` | Port 23 is closed or taken. Check whether another Telnet client is connected (only one may be allowed). Run with `--no-telnet` to capture HTTP only. LCD and Telnet write tests are then skipped. |
| A Telnet response looks cut short | Increase `--telnet-idle` (section 3). |
| Many `not-applied` outcomes in write mode | The session may have expired mid-run, or the device ignores that command. Look at the `result` in the exchange and at `pushes`. The report shows which assumptions this contradicts. |
| Exit code 3 | See the write-mode notes in section 2. |

---

## Older ad-hoc scripts

These scripts used to live in `tests/` as `test_*.py`. pytest collected them there, and they failed with fixture errors whenever `MATRIX_HOST` was set (TST-05). They are interactive: they ask for input with `input()`, and some change the live routing or power state. Run them only while you are watching the matrix. None of them has a default IP address; you must always give the target.

| Script | What it does | Usage |
| --- | --- | --- |
| `connection.py` | Connects, recalls presets 1-3, and prints the status. `-i` starts an interactive preset/status loop. | `python tools/hil/connection.py <ip> [port]` or `MATRIX_HOST=<ip> python tools/hil/connection.py` |
| `all_features.py` | Power off/on (it asks first), switches input 2 and then input 5 to output 1, recalls presets 1-2, and prints the status. | `python tools/hil/all_features.py <ip> [port]` |
| `input_names.py` | Prints the input names the matrix reports. Read-only. | `python tools/hil/input_names.py <ip> [port]` |
| `manual.py` | Sends `preset set` over HTTP(S) one preset at a time and asks whether the routing changed. | `python tools/hil/manual.py <ip> [port]` |
| `http_vs_https.py` | Sends the same preset command over HTTP (80) and HTTPS (443) so you can compare the responses. | `python tools/hil/http_vs_https.py <ip> [preset]` |
| `all_formats.py` | A Telnet (port 23) probe that tries many preset command spellings and line terminators. It was used to reverse-engineer the protocol. | `python tools/hil/all_formats.py <ip>` |

The capture tool now covers most of what these do. Delete each one once a scripted HIL check (HIL-B…E, plan §5.2) replaces it.

pytest tests that really need hardware use the `hardware` marker (`@pytest.mark.hardware`). They are deselected by default and run with `pytest -m hardware`.
