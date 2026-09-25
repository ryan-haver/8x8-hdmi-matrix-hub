# Device captures (golden fixtures)

This folder holds raw responses recorded from a real OREI BK-808 by the HIL-A capture tool (`python -m tools.hil.capture`, runbook in [`tools/hil/README.md`](../../../tools/hil/README.md)). The simulator replays them byte for byte with `python -m tools.simulator --golden tests/fixtures/device/<firmware>/` (plan §5.1, §5.2 and the L2 row of §5).

No capture file here is written by hand. To change a fixture, capture it again. (Tests in `tests/hil_tools/` edit copies of captures to act as a "different device"; they never edit this folder.)

## Layout

One folder per firmware. The capture tool names it from what the device reports: `<model>_<MCU version>_web-<web version>`, for example `BK-808_V1.10.02_web-V2.00.03`. Characters that are not safe in file names become `-`.

```text
tests/fixtures/device/
  README.md                          this file
  BK-808_V1.10.02_web-V2.00.03/
    manifest.json                    device versions, one entry per capture run, assumption index
    http/                            --mode read
      login.json                     the login (password redacted)
      get_video_status.json          one file per read command
      ...                            get_output_status, get_input_status, get_cec_status,
                                     get_system_status, get_status, get_network,
                                     get_ext_audio_status, get_routing_status, preset_get_1..8
      index_page.json                GET /
    telnet/                          --mode read
      banner.json                    what the device sends on connect
      status.json, r_fw_version.json, r_type.json,
      r_link_in_1..8.json, r_link_out_1..8.json, r_preset_1..8.json
    probe/                           --mode probe
      http_no_session.json           a read without logging in
      login_wrong_password.json      BE-05
      login_ok.json                  Set-Cookie headers (values masked)
      session_mechanism.json         cookie vs. client IP
      session_idle_expiry.json       BE-04 (only with --idle-waits)
      http_unknown_comhead.json, http_garbage_body.json
      cec_enable_shapes.json         BE-13, both payload shapes sent as no-ops
      telnet_errors.json             E00 / E01
      telnet_framing.json            '!' terminator, CR LF, case, pipelining
      telnet_noop_set_acks.json      set-command acknowledgements
      telnet_second_session.json     two Telnet clients at once
      telnet_push_window.json        unsolicited lines while the operator uses the front panel
    write/                           --mode write
      snapshot-initial.json          device state before the first write (the restore target)
      snapshot-final.json            device state after the final restore
      restore-log.jsonl              every restore write, appended as it happened
      http_video_switch.json ...     one file per write test (see "Write records")
```

The folder only has the parts of the capture that were run. A folder with only `http/` and `telnet/` is a valid golden set.

## Common record format

Every `*.json` file except `manifest.json` is a *record*:

```jsonc
{
  "format": "orei-hil-capture/1",      // format version; loaders skip anything else
  "id": "http/get_video_status",       // path without .json
  "title": "Read: get video status",
  "answers": ["http-read-shapes", "video-status-names"],  // assumption ids (below)
  "mode": "read",                      // capture mode that wrote it
  "captured_at": "2026-09-25T15:53:10.033111Z",
  "exchanges": [ ... ],                // read and probe records
  "steps": [ ... ],                    // write records
  "findings": { ... },                 // conclusions the tool drew (probe and write records)
  "redactions": ["..."]                // present if a secret was scrubbed from this record
}
```

### HTTP exchange

```jsonc
{
  "kind": "http",
  "role": "read",                      // see "Roles" below
  "label": "get video status",
  "comhead": "get video status",
  "request": {
    "method": "POST", "path": "/cgi-bin/instr",
    "headers": ["Host: 192.168.1.50:443", "Content-Type: application/json", "..."],
    "json": {"comhead": "get video status", "language": 0},
    "body_text": "{\"comhead\": \"get video status\", \"language\": 0}"
  },
  "response": {
    "status": 200, "reason": "OK", "http_version": "1.1",
    "headers": ["Content-Type: text/plain", "..."],   // wire order; cookie values masked
    "body_b64": "eyJjb21oZWFkIjoi...",               // the EXACT response bytes
    "body_text": "{\"comhead\":\"get video status\",...}",  // UTF-8 view (lossy)
    "json": { ... },                  // parsed body, or null
    "json_error": null                // why it did not parse, if it did not
  },
  "error": null,                      // {"type", "message"} if there was no response (timeout, reset...)
  "timing": {"started_at": "...Z", "elapsed_ms": 12.3},
  "outcome": "applied",               // write records only, see below
  "redacted": ["request.password"]    // login requests only
}
```

`body_b64` holds the real bytes; `body_text` and `json` are there to read and diff. Git may change line endings in these files, but that cannot affect `body_b64`, so byte-level checks stay valid.

The request body is what the hub sends: `json.dumps(payload)` with the default separators, which is exactly what `aiohttp`'s `session.post(url, json=...)` does in `src/orei_matrix.py`.

### Telnet exchange

```jsonc
{
  "kind": "telnet",
  "role": "read",
  "label": "r link in 1",
  "command": "r link in 1",
  "sent_b64": "ciBsaW5rIGluIDEhDQo=",           // exact bytes sent: "r link in 1!\r\n", like TelnetClient
  "sent_text": "r link in 1!\r\n",
  "unsolicited_before": [{"t": "...", "b64": "...", "text": "..."}],  // anything that arrived before the command
  "response": {
    "body_b64": "aGRtaSBpbnB1dCAxOiBjb25uZWN0DQo=",   // exact bytes received, IAC negotiation included
    "text": "hdmi input 1: connect\r\n",             // UTF-8 view without IAC bytes
    "chunks": [{"t_ms": 10.36, "len": 23}],          // arrival time of each TCP read
    "completion": "idle",           // idle | timeout | closed | no-data | window-ended
    "idle_ms": 1000,                // silence that ended the response
    "first_byte_ms": 10.36,
    "elapsed_ms": 1011.6,
    "analysis": {
      "line_endings": {"crlf": 1, "lf": 0, "cr": 0},
      "lines": ["hdmi input 1: connect"],
      "ends_with_newline": true,
      "trailing_without_newline": "",               // a prompt, if the device prints one
      "last_line": "hdmi input 1: connect",
      "error_code": null,                           // "E00" etc. if the last line is one
      "error_codes_seen": [],
      "iac": []                                     // Telnet negotiation seen, e.g. "IAC WILL 1"
    }
  },
  "error": null,
  "timing": {"started_at": "...Z", "elapsed_ms": 1011.6}
}
```

The protocol has no known end-of-response marker (that is part of what HIL-A measures, BE-07), so a response ends after `idle_ms` of silence, or at the timeout. `chunks` shows whether the device sends a response in one piece or in bursts. The capture tool answers any Telnet option negotiation with WONT/DONT.

### Roles

| Role | Where | Meaning |
| --- | --- | --- |
| `login` | http/login, probe/login_ok | login with the right password |
| `read` | http/, telnet/ | a read command (golden templates come from these) |
| `page` | http/index_page | `GET /` |
| `banner` | telnet/banner | bytes sent on connect |
| `no-session` | probe/http_no_session | a read with no session |
| `no-session-but-session-active` | probe/http_no_session | the first try found a live session from this IP; see its findings |
| `login-wrong` | probe/login_wrong_password | login with a deliberately wrong password |
| `after-wrong-login`, `main-after-wrong-login` | probe/login_wrong_password | reads right after the failed login |
| `session-check-cookie`, `session-check-no-cookie`, `idle-check`, `after-relogin` | probe/session_* | session tests |
| `unknown-comhead`, `garbage` | probe/http_* | an unknown comhead, a body that is not JSON |
| `cec-shape-bulk-noop`, `cec-shape-single-noop` | probe/cec_enable_shapes | both `set cec index` shapes with the current values |
| `probe-error` | probe/telnet_errors | Telnet commands that should be rejected |
| `framing`, `framing-banner` | probe/telnet_framing | raw framing variants, each on its own connection |
| `probe-noop-ack` | probe/telnet_noop_set_acks | set commands that write the current value |
| `push-window` | probe/telnet_push_window | everything received during the operator window |
| `write`, `write-invalid`, `write-noop`, `write-cec`, `read-during-test` | write/* | the step types of a write test |
| `readback`, `snapshot`, `relogin`, `restore`, `reboot-poll` | (not stored as records) | bookkeeping traffic |

## Write records

Each write test (`write/<test>.json`) has the state before it, one entry per step, and whether the restore worked:

```jsonc
{
  "title": "Output HDCP mode (every code)", "group": "output",
  "before": { /* snapshot, see snapshot-initial.json */ },
  "steps": [
    {
      "describe": "output 8 hdcp -> 1",
      "kind": "write",                    // write | invalid | read | noop | cec
      "exchange": { /* HTTP or Telnet exchange, with "outcome" */ },
      "outcome": "applied",               // see below
      "diff": [["hdcp", 8, 3, 1]],        // [field, port or null, before, after] from a fresh snapshot
      "pushes": [ ... ],                  // unsolicited Telnet data after the write
      "status_changes": {"removed": ["output 8 hdcp: follow sink"], "added": ["output 8 hdcp: hdcp1.4"]},
      "lcd_line": "lcd on 30 seconds",    // LCD test only
      "operator_note": "TV turned off"    // cec-live only
    }
  ],
  "restored": true,
  "restore_remaining": [],
  "findings": {"results_by_outcome": {"applied": [1], "rejected": [0]}, "...": "test-specific"},
  "error": null                           // an exception that interrupted the test
}
```

| Outcome | Step kind | Meaning |
| --- | --- | --- |
| `applied` | write | the snapshot after the write shows the expected change |
| `not-applied` | write | the expected change did not happen (the result code is in the exchange) |
| `rejected` | invalid | invalid parameters, and nothing changed |
| `accepted-invalid` | invalid | invalid parameters, and the device changed something anyway |
| `data` / `no-data` | read | a read during the test (for example in standby) returned data or not |
| `sent` | noop, cec | nothing to verify (no read-back exists) |

`restore-log.jsonl` has one JSON object per line: every restore write (`reason`, `field`, `port`, `from`, `to`, `payload`, `status`, `result`) and every verification (`verified`, `remaining`).

## Manifest

```jsonc
{
  "format": "orei-hil-capture/1",
  "firmware_folder": "BK-808_V1.10.02_web-V2.00.03",
  "device": {"model": "BK-808", "mcu_version": "V1.10.02", "web_version": "V2.00.03", "hostname": "...",
             "telnet_banner_version": "fw version : V1.10.02"},
  "runs": [
    {"mode": "probe", "started_at": "...", "finished_at": "...", "tool_version": "1.0",
     "hub_commit": "<git sha>", "host_os": "...", "python": "3.12.10",
     "target": {"host": "192.168.1.50", "port": 443, "telnet_port": 23, "tls": true, "user": "Admin"},
     "options": { /* CLI options without the password */ },
     "records": ["probe/..."], "answers": {"login-fail-result": ["probe/login_wrong_password"]},
     "errors": [], "warnings": [], "write_outcome": { /* write mode */ }, "interrupted": false}
  ],
  "answers": { /* union of all runs: assumption id -> record ids */ }
}
```

## Assumption ids

`answers` refers to the entries in [`tools/hil/capture/assumptions.py`](../../../tools/hil/capture/assumptions.py). Each entry is one `ASSUMPTION(HIL-A)` guess in `tools/simulator/`. A test makes sure every marker in the simulator has an entry. `python -m tools.simulator --golden <folder> --report` checks every entry against the records.

## Secrets

The password is never written. The login request has it replaced by `***REDACTED***` when it is recorded. Cookie and `Set-Cookie` values are masked (their names and attributes are kept). Before a record is written, every string and every decoded `*_b64` field is scrubbed of the password and of each `--redact` value. After the run the tool scans the whole folder again and exits with code 4 if it finds anything. The files still contain the device's LAN IP address, MAC address and hostname. Pass `--redact <value>` if you do not want those in the repository. Note that a redacted body is no longer byte-identical to what the device sent.

## How the simulator uses these files

`tools/simulator/golden.py` (`--golden`):

- **Seed:** the reads, preset routing, Telnet cable states and the LCD line overwrite the `--state` file.
- **Reads:** the captured bytes are sent unchanged while the simulator's own answer equals its answer for the seed state. After a write, the captured document is patched: only the changed values are replaced, and device-only fields and the device's JSON formatting are kept.
- **Telnet:** the banner and every captured command (reads, acks, errors) are sent unchanged. A read whose state changed falls back to the simulator's text.
- **Login, no-session, write results:** these come from `login`, `login-wrong`, `no-session`, and the `write`/`write-invalid` exchanges with outcome `applied`/`rejected`.
