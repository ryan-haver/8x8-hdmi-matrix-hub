"""Registry of the simulator's ``ASSUMPTION(HIL-A)`` guesses.

Every ``# ASSUMPTION(HIL-A)`` marker in ``tools/simulator/`` maps to one entry
here (``tests/sim/test_capture_assumptions.py`` enforces it). The capture tool
tags each record with the ids it provides evidence for and prints a summary;
the simulator's golden report (``python -m tools.simulator --golden DIR
--report``) checks each entry against the captures.

Pure data, no imports from the simulator.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Assumption:
    id: str
    question: str
    #: Where the guess lives in the simulator.
    where: str
    #: Findings register ids from docs/REMEDIATION_PLAN.md.
    refs: tuple[str, ...] = ()
    #: Capture modes that collect evidence (read / probe / write, plus the
    #: opt-in write groups in brackets).
    modes: tuple[str, ...] = ()
    #: (simulator file name, text on the ASSUMPTION(HIL-A) marker line).
    markers: tuple[tuple[str, str], ...] = field(default=())


ASSUMPTIONS: tuple[Assumption, ...] = (
    # ------------------------------------------------------------ HTTP / auth
    # Entries without markers were resolved from captures (V1.10.01 read
    # capture, WP-A4); they stay registered so the report keeps checking them.
    Assumption(
        "login-ok-result", "Login success `result` value (doc: \"success\"; V1.10.01 answers 1)",
        "protocol.LOGIN_OK_RESULT", ("BE-05",), ("read", "probe"),
    ),
    Assumption(
        "login-fail-result", "Exact response to a wrong-password login",
        "protocol.LOGIN_FAIL_RESULT", ("BE-05",), ("probe",),
    ),
    Assumption(
        "session-expired-style", "What a command gets without a session (JSON echo, HTML page, 401...)",
        "protocol.SESSION_EXPIRED_STYLE", ("BE-04",), ("probe",),
        (("protocol.py", "commands sent without a prior login"),),
    ),
    Assumption(
        "session-mechanism", "Sessions are tracked per client IP, not by cookie",
        "protocol.DEFAULT_SESSION_TTL_S comment, server.Simulator.sessions", ("BE-04",), ("probe",),
    ),
    Assumption(
        "session-ttl", "Idle session lifetime (simulator: never expires)",
        "protocol.DEFAULT_SESSION_TTL_S", ("BE-04",), ("probe --idle-waits",),
        (("protocol.py", "session lifetime"),),
    ),
    Assumption(
        "unknown-comhead-result", "Answer to an unknown comhead (V1.10.01: none, the client times out; HIL-12)",
        "protocol.UNKNOWN_COMMANDS_UNANSWERED, http_commands.dispatch", ("HIL-12",), ("probe", "write"),
    ),
    Assumption(
        "garbage-body", "Answer to a request body that is not JSON",
        "server.Simulator._process", (), ("probe",),
    ),
    Assumption(
        "write-ok-results", "`result` of each successful write",
        "protocol.RESULT_OK, protocol.WRITE_RESULT_OVERRIDES", ("BE-12",), ("write",),
    ),
    Assumption(
        "write-fail-result", "`result` of a write with invalid parameters",
        "protocol.RESULT_FAIL", ("BE-12",), ("write",),
    ),
    Assumption(
        "web-ui-commands", "The commands of the device's web interface (tx stream/hdcp, set hdr conversion, "
        "set video scaler, set arc, set output audio mute, set edid, set lcd on time, set ext-audio *, "
        "ext-audio switch, preset name/clear, reboot): answers and read-back as the simulator predicts",
        "http_commands (web-UI-derived writes), protocol.WRITE_RESULT_OVERRIDES", ("HIL-09",), ("write",),
        (("protocol.py", "the web-UI-derived writes"),),
    ),
    Assumption(
        "legacy-unanswered", "The old hub's output/EDID/ext-audio comheads are never answered, "
        "the old LCD payload is rejected",
        "protocol.LEGACY_UNANSWERED_WRITES", ("HIL-09",), ("write",),
    ),
    Assumption(
        "preset-set-empty", "`preset set` of an empty slot is answered with result 0",
        "http_commands._preset_set", (), ("write",),
        (("http_commands.py", "recalling an empty slot is answered"),),
    ),
    Assumption(
        "reboot-replies-first", "`reboot` answers before the device drops off",
        "protocol.REBOOT_REPLIES_FIRST", (), ("write [reboot]",),
        (("protocol.py", "``reboot`` answers before"),),
    ),
    Assumption(
        "standby-behaviour", "Commands keep working in standby; reads report power 0",
        "http_commands._set_power", (), ("write",),
    ),
    # ------------------------------------------------------------ HTTP reads
    Assumption(
        "http-read-shapes", "Every read's keys, types and formatting match the simulator byte for byte",
        "http_commands (all @command(read=True))", ("L2",), ("read",),
    ),
    Assumption(
        "video-status-names", "`get video status` names are 8 plain strings (no IN01- prefix, no extra entries)",
        "http_commands._get_video_status", (), ("read",),
    ),
    Assumption(
        "output-status-name-field", "`get output status` names its outputs in `name` (not allinputname/alloutputname)",
        "http_commands._get_output_status", (), ("read",),
    ),
    Assumption(
        "ninth-entry", "The ninth entry of allsource/allscaler/allhdr/allhdcp/allarc/allout/allaudiomute: "
        "the 'All Output' row (common value, 255 when mixed), and how port-0 writes change it",
        "state.DeviceState.ninth", ("HIL-04",), ("read", "write"),
    ),
    Assumption(
        "get-status-fields", "Field set of `get status` (versions, model, MAC...)",
        "http_commands._get_status", (), ("read",),
    ),
    Assumption(
        "get-network-fields", "`get network` uses netmask and/or subnet (and which other fields)",
        "http_commands._get_network", (), ("read",),
    ),
    Assumption(
        "ext-audio-index", "`index` in `get ext-audio status` is the audio output set with `set ext-audio index`",
        "http_commands._get_ext_audio_status / _set_exa_index", (), ("read", "write"),
    ),
    Assumption(
        "preset-get-shape", "Whether the device answers `preset get` / `get routing status` at all "
        "(V1.10.01: no answer, HIL-01)",
        "protocol.UNANSWERED_COMHEADS", ("HIL-01",), ("read",),
    ),
    # ------------------------------------------------------------ HTTP writes
    Assumption(
        "name-truncation", "How long a name the device stores (V1.10.01 kept 40 characters)",
        "http_commands._name", (), ("write",),
        (("http_commands.py", "names are stored as sent up to"),),
    ),
    Assumption(
        "edid-range", "Which EDID ids `set edid` accepts (simulator: 1-47)",
        "protocol.EDID_RANGE", (), ("write",),
    ),
    Assumption(
        "copy-edid", "EDID copy: `copy edid` / `set input edid 14+N` do nothing; `set edid` 39+N copies output N",
        "http_commands._set_edid", ("BE-25",), ("write",),
    ),
    Assumption(
        "cec-index-single-port", "The old hub's single-port `set cec index` payload is rejected (result 0)",
        "http_commands._set_cec_index", ("BE-13", "HIL-10"), ("probe", "write"),
    ),
    Assumption(
        "cec-disabled-port", "CEC commands are accepted when CEC is disabled on the port",
        "http_commands._cec_command", (), ("write [cec-live]",),
        (("http_commands.py", "commands are accepted even when CEC is disabled"),),
    ),
    Assumption(
        "exa-commands", "Ext-audio writes: `set ext-audio mode|out|index`, `ext-audio switch` apply; "
        "the old `set output exa*` do nothing",
        "http_commands._set_exa_mode/_set_exa_out/_set_exa_index/_ext_audio_switch", (), ("write",),
    ),
    Assumption(
        "output-mode-text", "Telnet wording of HDCP/HDR/scaler/EDID codes; which scaler code is audio-only",
        "protocol.HDCP_TEXT / HDR_TEXT / SCALER_TEXT / EDID_TEXT", ("BE-15", "HIL-02"), ("read", "write"),
        (("protocol.py", "wording of every value below"),),
    ),
    Assumption(
        "lcd-codes", "LCD on-time codes 0-4 (`set lcd on time`, read back as `get system status.mode`) and "
        "their Telnet wording",
        "protocol.LCD_SECONDS, telnet_commands._lcd_line", ("API-07",), ("write",),
    ),
    # ------------------------------------------------------------ Telnet
    Assumption(
        "telnet-banner", "Connection banner text",
        "protocol.TELNET_BANNER_LINES", (), ("read",),
    ),
    Assumption(
        "telnet-iac", "Telnet option negotiation the device sends on connect",
        "protocol.TELNET_SEND_IAC_NEGOTIATION / TELNET_IAC_NEGOTIATION", (), ("read",),
    ),
    Assumption(
        "telnet-status-wording", "`status` dump lines, order and last line",
        "telnet_commands.status_lines", ("BE-28", "BE-29"), ("read",),
        (("telnet_commands.py", "wording of values not seen in the capture"),),
    ),
    Assumption(
        "telnet-read-wording", "Wording of `r fw version`, `r type`, `r link`, `r preset`",
        "telnet_commands.handle", (), ("read",),
    ),
    Assumption(
        "telnet-terminators", "Response line endings, prompts, and the `!` command terminator",
        "protocol.TELNET_EOL / TELNET_COMMAND_TERMINATOR", ("BE-07",), ("read", "probe"),
    ),
    Assumption(
        "telnet-error-codes", "Meaning of E00 / E01 (unknown command / bad parameter)",
        "protocol.TELNET_ERR_UNKNOWN / TELNET_ERR_PARAM", ("BE-07",), ("probe", "write"),
    ),
    Assumption(
        "telnet-set-acks", "Acknowledgement text of set commands (routing, presets, beep, lock, stream, CEC)",
        "telnet_commands.handle", ("BE-07",), ("probe", "write"),
        (("telnet_commands.py", "success is acknowledged by echoing"),),
    ),
    Assumption(
        "telnet-bare-power", "Whether bare `power N` (sent by TelnetClient) works, vs `s power N`",
        "telnet_commands.handle", (), ("write",),
    ),
    Assumption(
        "telnet-reboot", "`reboot` acknowledgement before the connection drops",
        "telnet_commands.handle", (), ("write [reboot]",),
        (("telnet_commands.py", '"reboot" (what the hub sends)'),),
    ),
    Assumption(
        "telnet-cec-output-words", "Output (TV) CEC command words",
        "protocol.TELNET_CEC_OUTPUT_WORDS", ("BE-14",), ("write [cec-live]",),
        (("protocol.py", "the output (TV) CEC table"),),
    ),
    Assumption(
        "push-wording", "Unsolicited Telnet lines on front-panel / cable / HTTP-driven changes",
        "server.Simulator.cable_event", (), ("probe", "write"),
        (("server.py", "push wording"),),
    ),
    Assumption(
        "telnet-multi-session", "More than one Telnet client can be connected at once",
        "server.Simulator._handle_telnet_client", (), ("probe",),
    ),
)

BY_ID: dict[str, Assumption] = {a.id: a for a in ASSUMPTIONS}


def ids_for_mode(mode: str) -> list[str]:
    """Assumption ids a capture mode can provide evidence for."""
    return [a.id for a in ASSUMPTIONS if any(m.split(" ")[0] == mode for m in a.modes)]
