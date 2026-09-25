"""Wire-level protocol constants for the BK-808 simulator.

Everything the simulator *guesses* about the real device lives here (or is
marked ``# ASSUMPTION(HIL-A)`` next to the code that uses it), so the HIL-A
capture session can correct the simulator in one place. Search the package for
``ASSUMPTION(HIL-A)`` to find every guess.

Sources used for the current values, in order of trust:

1. Captures from a BK-808 with MCU V1.10.01 / web V2.00.03
   (``tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/``: read, probe and
   write runs of HIL Session 1).
2. The commands, payload shapes and option lists of the device's own
   configuration web interface (WP-A4 part 2). They are marked
   ``web-UI-derived`` and stay guesses until a write capture proves them.
3. ``docs/OREI_API_COMMANDS.md`` and what ``src/orei_matrix.py`` /
   ``src/telnet_client.py`` send and parse.
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

#: ``result`` value for a successful write (captured on V1.10.01 for video
#: switch, names, beep, panel lock, set cec index and set poweronoff).
RESULT_OK = 1

#: Writes the device rejects (bad index, bad value, the single-port
#: ``set cec index``, the old LCD payload) echo the comhead with
#: ``result: 0`` (captured on V1.10.01, ``write/*.json``).
RESULT_FAIL = 0

#: Login success is ``{"comhead":"login","result":1}`` (captured on V1.10.01,
#: ``http/login``). The API doc's ``"result": "success"`` is wrong for this
#: firmware; orei_matrix.py accepts ``result == 1``.
LOGIN_OK_RESULT: int | str = 1

#: A wrong user/password echoes ``comhead: "login"`` with ``result: 0``
#: (captured, ``probe/login_wrong_password``): the echo is what BE-05 says the
#: old hub mistook for success.
LOGIN_FAIL_RESULT: int | str = 0

#: The device never answers a command it does not know, or a body that is not
#: JSON: it accepts the request and the client times out (captured on V1.10.01,
#: ``probe/http_unknown_comhead``, ``probe/http_garbage_body`` and every write
#: the old hub sent with an unknown comhead, HIL-09/HIL-12). The simulator holds
#: such requests open the same way. The ``result`` below is only used by
#: ``dispatch`` callers that want a document anyway (the golden report).
UNKNOWN_COMMANDS_UNANSWERED = True
UNKNOWN_COMMAND_RESULT = RESULT_FAIL

# ASSUMPTION(HIL-A): the web-UI-derived writes (``tx stream``, ``tx hdcp``,
# ``set hdr conversion``, ``set video scaler``, ``set arc``, ``set output
# audio mute``, ``set edid``, ``set lcd on time`` with ``"lcd on time"``,
# ``set ext-audio mode|out|index``, ``ext-audio switch``, ``preset name``,
# ``preset clear``, ``reboot``) answer RESULT_OK when applied and RESULT_FAIL
# for bad parameters, like every captured write. Override per comhead here once
# a capture shows otherwise.
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

#: Comheads this firmware does not implement: the device accepts the request
#: and never answers (the capture client gave up with a TimeoutError after
#: 5 s). Reads: ``get routing status`` and ``preset get`` (HIL-01). Writes: the
#: commands the old hub sent for output settings, EDID and ext-audio (HIL-09,
#: ``write/http_output_*``, ``write/http_input_edid``, ``write/http_copy_edid``,
#: ``write/http_exa_*``). Any other unknown comhead is unanswered as well
#: (UNKNOWN_COMMANDS_UNANSWERED); these are listed so the log can say why.
UNANSWERED_READS = frozenset({"get routing status", "preset get"})
LEGACY_UNANSWERED_WRITES = frozenset({
    "set output stream", "set output hdcp", "set output hdr", "set output scaler", "set output arc",
    "set output mute", "set input edid", "copy edid", "set output exa mode", "set output exa",
    "set output exa in source",
})
UNANSWERED_COMHEADS = UNANSWERED_READS | LEGACY_UNANSWERED_WRITES

# ASSUMPTION(HIL-A): ``reboot`` answers before the device drops off the
# network (the web interface waits for the answer, then polls ``get status``).
REBOOT_REPLIES_FIRST = True
DEFAULT_REBOOT_SECONDS = 5.0

# ---------------------------------------------------------------------------
# Telnet (port 23)
# ---------------------------------------------------------------------------

#: Commands end with ``!`` (the client appends ``!\r\n``).
TELNET_COMMAND_TERMINATOR = b"!"

#: Line ending used in every response line.
TELNET_EOL = "\r\n"

#: Error codes, captured on V1.10.01 (``probe/telnet_errors`` and the Telnet
#: write tests): ``E00`` = unknown command (also an unknown CEC word, ``s av``
#: and ``s out N stream``), ``E01`` = known command with a bad parameter (port
#: out of range, non-numeric port, ``s power N``).
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
# ``active``. The HTTP output table has only six commands (power on/off, mute,
# volume down/up, active: the device web interface, BE-14); whether Telnet
# accepts the other words for outputs needs the live CEC run.
TELNET_CEC_OUTPUT_WORDS = TELNET_CEC_INPUT_WORDS | {"active"}

# ---------------------------------------------------------------------------
# Value -> text maps used in the Telnet ``status`` dump.
# ASSUMPTION(HIL-A): wording of every value below. The client only needs the
# ``<label>: <text>`` shape (telnet_client.py ``_parse_status_response``).
#
# The codes are the device's own (0-based HDR and scaler; reads and writes use
# the same codes: the device web interface writes back what it reads, HIL-02,
# BE-15). Captured wording (V1.10.01 ``get output status`` values next to the
# ``status`` dump lines): HDCP 3 = "follow sink", HDR 0 = "pass-through",
# scaler 0 = "pass-through", scaler 4 = "audio only", EDID 36 =
# "frl12g_8k_hdr,7.1ch", LCD 3 = "lcd on 30 seconds". Every other text is a
# guess until a write run with Telnet.
# ---------------------------------------------------------------------------

HDCP_TEXT = {1: "hdcp1.4", 2: "hdcp2.2", 3: "follow sink", 4: "follow source", 5: "user mode"}
HDR_TEXT = {0: "pass-through", 1: "hdr to sdr", 2: "auto"}
SCALER_TEXT = {0: "pass-through", 1: "8k to 4k", 2: "8k/4k to 1080p", 3: "auto", 4: "audio only"}
EDID_TEXT = {36: "frl12g_8k_hdr,7.1ch"}
EXT_AUDIO_MODE_TEXT = {0: "bind to input", 1: "bind to output", 2: "matrix"}
LCD_SECONDS = {2: 15, 3: 30, 4: 60}

# ---------------------------------------------------------------------------
# Value ranges: the device web interface's option lists (web-UI-derived; the
# read captures agree for every value they contain)
# ---------------------------------------------------------------------------

HDCP_RANGE = (1, 5)
#: HDR conversion: 0 bypass, 1 HDR to SDR, 2 auto (V1.10.01 reports 0).
HDR_RANGE = (0, 2)
#: Video mode: 0 bypass, 1 8K->4K, 2 8K/4K->1080p, 3 auto, 4 audio only.
SCALER_RANGE = (0, 4)
#: LCD on time (``get system status.mode``): 0 off, 1 always, 2/3/4 = 15/30/60 s.
LCD_RANGE = (0, 4)
EXT_AUDIO_MODE_RANGE = (0, 2)
#: ``ext-audio switch`` sources: 1-8 = input N, 9-16 = the ARC of output N-8.
EXT_AUDIO_SOURCE_RANGE = (1, 16)
#: EDID ids: 1-36 built in, 37-39 user EDIDs, 40-47 copy from output 1-8.
EDID_RANGE = (1, 47)
#: ``cec command`` objects: 0 = source (input), 1 = display (output). The
#: device answers ``result: 1`` for any index and for an empty port array, and
#: ``result: 0`` for object 2 (captured, ``write/http_cec_command_invalid``).
CEC_OBJECT_RANGE = (0, 1)
#: Value the device reports in the ninth ("all outputs") entry of a per-output
#: array when the eight outputs differ (captured: ``allscaler`` [0,4,0,...,255]).
MIXED = 255
#: Longest name the simulator stores. V1.10.01 kept a 40-character name
#: unchanged (captured); the device's own web interface stops at 49 bytes.
NAME_MAX = 64
