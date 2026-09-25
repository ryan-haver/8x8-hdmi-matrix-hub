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
        (("protocol.py", "a wrong user/password still echoes"),),
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
        "unknown-comhead-result", "Answer to an unknown comhead",
        "protocol.UNKNOWN_COMMAND_RESULT", (), ("probe",),
        (("protocol.py", "unknown comheads are echoed"),),
    ),
    Assumption(
        "garbage-body", "Answer to a request body that is not JSON",
        "server.Simulator._process", (), ("probe",),
        (("server.py", "garbage bodies"),),
    ),
    Assumption(
        "write-ok-results", "`result` of each successful write (incl. unverified beep/lock/EDID/LCD)",
        "protocol.RESULT_OK, protocol.WRITE_RESULT_OVERRIDES", ("BE-12",), ("write",),
        (("protocol.py", "writes that the docs show returning"),),
    ),
    Assumption(
        "write-fail-result", "`result` of a write with invalid parameters",
        "protocol.RESULT_FAIL", ("BE-12",), ("write",),
        (("protocol.py", "writes the device rejects"),),
    ),
    Assumption(
        "reboot-replies-first", "`set reboot` answers before the device drops off",
        "protocol.REBOOT_REPLIES_FIRST", (), ("write [reboot]",),
        (("protocol.py", "``set reboot`` answers before"),),
    ),
    Assumption(
        "standby-behaviour", "Commands keep working in standby; reads report power 0",
        "http_commands._set_power", (), ("write",),
        (("http_commands.py", "other commands keep working while in standby"),),
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
        "what it is, and whether writes change it",
        "state.DeviceState.ninth_output", ("HIL-04",), ("read", "write"),
        (("state.py", "the ninth entry never changes"),),
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
        "ext-audio-index", "Meaning of `index` in `get ext-audio status`",
        "http_commands._get_ext_audio_status", (), ("read",),
        (("http_commands.py", 'meaning of "index" is unknown'),),
    ),
    Assumption(
        "preset-get-shape", "Whether the device answers `preset get` / `get routing status` at all "
        "(V1.10.01: no answer, HIL-01)",
        "protocol.UNANSWERED_COMHEADS", ("HIL-01",), ("read",),
    ),
    # ------------------------------------------------------------ HTTP writes
    Assumption(
        "name-truncation", "The device truncates names to 32 characters",
        "http_commands._set_input_name", (), ("write",),
        (("http_commands.py", "the device truncates to 32 characters"),),
    ),
    Assumption(
        "edid-range", "Which EDID mode numbers the device accepts (simulator: 1-47)",
        "protocol.EDID_RANGE", (), ("write",),
        (("protocol.py", "EDID modes 1-47"),),
    ),
    Assumption(
        "copy-edid", "What `copy edid` does, and whether `set input edid` 14+N copies output N",
        "http_commands._copy_edid", ("BE-25",), ("write",),
        (("http_commands.py", "equivalent to EDID mode 14 + output"),),
    ),
    Assumption(
        "cec-index-single-port", "The hub's single-port `set cec index` payload works",
        "http_commands._set_cec_index", ("BE-13",), ("probe", "write"),
        (("http_commands.py", "the single-port shape sent by"),),
    ),
    Assumption(
        "cec-disabled-port", "CEC commands are accepted when CEC is disabled on the port",
        "http_commands._cec_command", (), ("write [cec-live]",),
        (("http_commands.py", "commands are accepted even when CEC is disabled"),),
    ),
    Assumption(
        "exa-commands", "Ext-audio write comheads/payloads, exa 1 = enable / 2 = disable",
        "http_commands._set_exa_mode/_set_exa/_set_exa_source", (), ("write",),
        (("http_commands.py", "comhead and payload taken from the hub"),
         ("http_commands.py", "exa 1 = enable, 2 = disable")),
    ),
    Assumption(
        "output-mode-text", "Telnet wording of HDCP/HDR/scaler/EDID codes; which scaler code is audio-only",
        "protocol.HDCP_TEXT / HDR_TEXT / SCALER_TEXT / EDID_TEXT", ("BE-15", "HIL-02"), ("read", "write"),
        (("protocol.py", "wording of every value below"),),
    ),
    Assumption(
        "lcd-codes", "LCD timeout codes 0-4 and their Telnet wording",
        "protocol.LCD_SECONDS, telnet_commands._lcd_line", ("API-07",), ("write",),
        (("telnet_commands.py", "wording; the client only parses"),),
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
        "protocol.TELNET_ERR_UNKNOWN / TELNET_ERR_PARAM", ("BE-07",), ("probe",),
        (("protocol.py", "error codes"),),
    ),
    Assumption(
        "telnet-set-acks", "Acknowledgement text of set commands (routing, presets, beep, lock, stream, CEC)",
        "telnet_commands.handle", ("BE-07",), ("probe", "write"),
        (("telnet_commands.py", "success is acknowledged by echoing"),
         ("telnet_commands.py", "acknowledgement wording")),
    ),
    Assumption(
        "telnet-bare-power", "Whether bare `power N` (sent by TelnetClient) works, vs `s power N`",
        "telnet_commands.handle", (), ("write",),
        (("telnet_commands.py", 'the bare "power <0|1>"'),),
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
