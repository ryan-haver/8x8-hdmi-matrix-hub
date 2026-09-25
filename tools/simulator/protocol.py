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

#: ``result`` value for a successful write. Verified for ``video switch``,
#: ``preset set`` and ``set poweronoff``.
RESULT_OK = 1

# ASSUMPTION(HIL-A): writes the device rejects (bad index, bad value) echo the
# comhead with ``result: 0``. Never observed; chosen as the natural opposite of
# RESULT_OK.
RESULT_FAIL = 0

# ASSUMPTION(HIL-A): the API doc lists ``"result": "success"`` for login (the
# only entry marked verified that uses a string). orei_matrix.py:251 accepts
# either ``result == 1`` or any echoed ``comhead == "login"``.
LOGIN_OK_RESULT: int | str = "success"

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
# parameter". BE-07 (telnet_client.py:403-426) is unresolved: the client waits
# for E00/E01 as the *completion* marker of a CEC command and then treats them
# as failure. The simulator never sends E00/E01 for a successful command.
TELNET_ERR_UNKNOWN = "E00"
TELNET_ERR_PARAM = "E01"

# ASSUMPTION(HIL-A): connection banner. The client only extracts
# ``fw version : v<digits>`` from it (telnet_client.py:205).
TELNET_BANNER_LINES = (
    "",
    "Welcome to {model} 8x8 HDMI Matrix",
    "fw version : {fw_version}",
    "",
)

# ASSUMPTION(HIL-A): the device does not start any Telnet option negotiation.
# Set to True to send IAC WILL ECHO / IAC WILL SGA with the banner and exercise
# the client's IAC filter.
TELNET_SEND_IAC_NEGOTIATION = False

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
# ``<label>: <text>`` shape (telnet_client.py:692-788).
# ---------------------------------------------------------------------------

HDCP_TEXT = {1: "hdcp1.4", 2: "hdcp2.2", 3: "follow sink", 4: "follow source", 5: "user mode"}
HDR_TEXT = {1: "pass-through", 2: "hdr to sdr", 3: "auto"}
SCALER_TEXT = {1: "pass-through", 2: "8k to 4k", 3: "8k/4k to 1080p", 4: "auto", 5: "audio only"}
LCD_SECONDS = {2: 15, 3: 30, 4: 60}

# ---------------------------------------------------------------------------
# Value ranges (from docs/OREI_API_COMMANDS.md and orei_matrix.py validators)
# ---------------------------------------------------------------------------

HDCP_RANGE = (1, 5)
HDR_RANGE = (1, 3)
SCALER_RANGE = (1, 5)
LCD_RANGE = (0, 4)
EXT_AUDIO_MODE_RANGE = (0, 2)
CEC_INDEX_RANGE = (1, 19)
# ASSUMPTION(HIL-A): EDID modes 1-47 (the API doc's "preset EDID modes (1-47)").
EDID_RANGE = (1, 47)
