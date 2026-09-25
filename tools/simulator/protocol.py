"""Wire-level protocol constants for the BK-808 simulator.

Everything the simulator *guesses* about the real device lives here (or is
marked ``# ASSUMPTION(HIL-A)`` next to the code that uses it), so the HIL-A
capture session can correct the simulator in one place. Search the package for
``ASSUMPTION(HIL-A)`` to find every guess.

Sources used for the current values, in order of trust:

1. ``docs/OREI_API_COMMANDS.md`` entries marked verified.
2. What ``src/orei_matrix.py`` / ``src/telnet_client.py`` parse (they were
   written against the real device, but several parsers are known to be wrong,
   see the BE-* rows in ``docs/REMEDIATION_PLAN.md``).
3. The vendor serial command reference summarised in the API doc.
"""

from __future__ import annotations

PORT_COUNT = 8

# ---------------------------------------------------------------------------
# HTTP (POST /cgi-bin/instr)
# ---------------------------------------------------------------------------

#: Path of the JSON command endpoint.
INSTR_PATH = "/cgi-bin/instr"

#: The real device answers with ``text/plain`` (orei_matrix.py reads
#: ``response.text()`` then ``json.loads`` for exactly this reason).
RESPONSE_CONTENT_TYPE = "text/plain"

#: Bytes the device appends to every JSON body. Captured on V1.10.01: compact
#: JSON (``","`` / ``":"`` separators, keys in a fixed order per comhead)
#: followed by CR LF (``tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/http``).
RESPONSE_BODY_SUFFIX = b"\r\n"

#: ``result`` value for a successful write. Verified for ``video switch``,
#: ``preset set`` and ``set poweronoff``.
RESULT_OK = 1

# ASSUMPTION(HIL-A): writes the device rejects (bad index, bad value) echo the
# comhead with ``result: 0``. Never observed; chosen as the natural opposite of
# RESULT_OK.
RESULT_FAIL = 0

#: Login success is ``{"comhead":"login","result":1}`` (captured on V1.10.01,
#: ``http/login``). The API doc's ``"result": "success"`` is wrong for this
#: firmware; orei_matrix.py accepts ``result == 1``.
LOGIN_OK_RESULT: int | str = 1

# ASSUMPTION(HIL-A): a wrong user/password still echoes ``comhead: "login"``
# (that is what BE-05 says the hub mis-reads as success) with a failure result.
# The exact failure token is unknown; "fail" mirrors the "success" string.
LOGIN_FAIL_RESULT: int | str = "fail"

# ASSUMPTION(HIL-A): unknown comheads are echoed with RESULT_FAIL rather than
# an HTTP error. Unrecognised commands are also recorded in the simulator log
# so tests can assert "every command the code sends is recognised" (plan §5 L2).
UNKNOWN_COMMAND_RESULT = RESULT_FAIL

# ASSUMPTION(HIL-A): writes that the docs show returning "success" but that are
# not verified (beep, panel lock, input EDID, copy EDID, LCD time) return
# RESULT_OK like every verified write. The hub checks ``result == 1`` for beep
# and panel lock (orei_matrix.py:1522,1543), which contradicts the doc; HIL-A
# must record the real value. Override per comhead here once known.
WRITE_RESULT_OVERRIDES: dict[str, int | str] = {}

# ASSUMPTION(HIL-A): commands sent without a prior login (or after the session
# expired) get a JSON echo with RESULT_FAIL and no data. Alternatives HIL-A
# should look for: an HTML login page, or an HTTP 401/302. The simulator can
# emulate those via the ``session_expired_style`` fault ("html" / "http401").
SESSION_EXPIRED_STYLE = "json"

#: Minimal stand-in for the login page some firmwares return instead of JSON.
SESSION_EXPIRED_HTML = (
    "<html><head><title>BK-808</title></head>"
    '<body><script>location.href="/login.html";</script></body></html>'
)

# ASSUMPTION(HIL-A): session lifetime. The real cookie/session lifetime is
# unknown (HIL-A: "leave idle past cookie lifetime"). ``None`` = never expires.
# The hub's aiohttp CookieJar refuses cookies for bare IP hosts, and the hub
# works against the real device, so sessions are tracked per client IP rather
# than by cookie.
DEFAULT_SESSION_TTL_S: float | None = None

#: Reads this firmware does not implement: the device accepts the request and
#: never answers (the capture client gave up with a TimeoutError after 5 s,
#: ``http/get_routing_status`` and ``http/preset_get_1..8`` on V1.10.01,
#: HIL-01). The simulator holds these requests open the same way until the
#: client gives up, or the simulator is reset or stopped.
UNANSWERED_COMHEADS = frozenset({"get routing status", "preset get"})

# ASSUMPTION(HIL-A): ``set reboot`` answers before the device drops off the
# network (the doc only says "connection will drop").
REBOOT_REPLIES_FIRST = True
DEFAULT_REBOOT_SECONDS = 5.0

# ---------------------------------------------------------------------------
# Telnet (port 23)
# ---------------------------------------------------------------------------

#: Commands end with ``!`` (the client appends ``!\r\n``).
TELNET_COMMAND_TERMINATOR = b"!"

#: Line ending used in every response line.
TELNET_EOL = "\r\n"

# ASSUMPTION(HIL-A): error codes. The client and the ad-hoc scripts treat
# ``E00`` as "command not recognised"; ``E01`` is assumed to mean "bad
# parameter". The client (src/_telnet_proto.py, BE-07) follows the same
# assumptions: E0x means failure, and a set command completes on its
# acknowledgement line. The simulator never sends E00/E01 for a successful
# command.
TELNET_ERR_UNKNOWN = "E00"
TELNET_ERR_PARAM = "E01"

#: Connection banner, captured on V1.10.01 (``telnet/banner``). The version
#: is the MCU firmware in lower case (``v1.10.01``). The client only extracts
#: ``fw version :v<digits>`` from it (telnet_client.py ``connect``).
TELNET_BANNER_LINES = (
    "****************welcome **************",
    "            fw version :{fw_version_lower}        ",
    "**************************************",
    "",
)

#: The device opens every connection with Telnet option negotiation, before
#: the banner text (``telnet/banner`` on V1.10.01):
#: IAC WILL SGA, IAC WONT ECHO, IAC DONT ECHO, IAC DONT BINARY, IAC WONT SGA.
TELNET_SEND_IAC_NEGOTIATION = True
TELNET_IAC_NEGOTIATION = bytes.fromhex("fffb03fffc01fffe01fffe00fffc03")

#: The device echoes every command line (``r link in 1!``, CR LF) before its
#: answer (every ``telnet/*`` read capture on V1.10.01).
TELNET_ECHO_COMMANDS = True

#: CEC command words accepted after ``s cec in <n>`` (telnet_client.py
#: _CEC_INDEX_TO_TELNET and the cec_input_* helpers).
TELNET_CEC_INPUT_WORDS = frozenset(
    {
        "on", "off", "menu", "back", "up", "down", "left", "right", "enter",
        "play", "pause", "stop", "previous", "next", "rew", "ff",
        "vol+", "vol-", "mute",
    }
)

# ASSUMPTION(HIL-A): the output (TV) CEC table accepts the same words plus
# ``active``. BE-14 says captures show a *different* output table; HIL-A must
# record it.
TELNET_CEC_OUTPUT_WORDS = TELNET_CEC_INPUT_WORDS | {"active"}

# ---------------------------------------------------------------------------
# Value -> text maps used in the Telnet ``status`` dump.
# ASSUMPTION(HIL-A): wording of every value below. The client only needs the
# ``<label>: <text>`` shape (telnet_client.py ``_parse_status_response``).
#
# Read-capture evidence (V1.10.01: ``get output status`` values next to the
# ``status`` dump lines): HDCP 3 = "follow sink", HDR 0 = "pass-through",
# scaler 0 = "pass-through", scaler 4 = "audio only", EDID 36 =
# "frl12g_8k_hdr,7.1ch". Every other code is still a guess. The reads use 0
# and 4 where the API doc's write tables use 1 (passthrough) and 5 (audio
# only), so reads may be 0-based and writes 1-based; only a write capture can
# tell (HIL-02, BE-15).
# ---------------------------------------------------------------------------

HDCP_TEXT = {1: "hdcp1.4", 2: "hdcp2.2", 3: "follow sink", 4: "follow source", 5: "user mode"}
HDR_TEXT = {0: "pass-through", 1: "pass-through", 2: "hdr to sdr", 3: "auto"}
SCALER_TEXT = {0: "pass-through", 1: "pass-through", 2: "8k to 4k", 3: "8k/4k to 1080p", 4: "audio only",
               5: "audio only"}
EDID_TEXT = {36: "frl12g_8k_hdr,7.1ch"}
EXT_AUDIO_MODE_TEXT = {0: "bind to input", 1: "bind to output", 2: "matrix"}
LCD_SECONDS = {2: 15, 3: 30, 4: 60}

# ---------------------------------------------------------------------------
# Value ranges (from docs/OREI_API_COMMANDS.md and orei_matrix.py validators)
# ---------------------------------------------------------------------------

HDCP_RANGE = (1, 5)
#: HDR 0 is what V1.10.01 reports for every output (``http/get_output_status``)
#: and prints as "pass-through" in ``status``. Its meaning next to the
#: documented 1-3, and whether 0 can be written, is unknown pending a
#: write-mode capture (HIL-02). The simulator accepts 0 in reads and writes.
HDR_RANGE = (0, 3)
#: Scaler 0 is reported by V1.10.01 (``pass-through``); see HDR_RANGE.
SCALER_RANGE = (0, 5)
LCD_RANGE = (0, 4)
EXT_AUDIO_MODE_RANGE = (0, 2)
CEC_INDEX_RANGE = (1, 19)
# ASSUMPTION(HIL-A): EDID modes 1-47 (the API doc's "preset EDID modes (1-47)").
EDID_RANGE = (1, 47)
