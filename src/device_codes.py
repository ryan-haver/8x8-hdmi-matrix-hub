"""Device value codes of the OREI BK-808 and how the hub's API maps to them.

This is the one place where a value the hub's public API accepts (REST
bodies, ``OreiMatrix.set_*`` arguments, saved scenes/profiles) is translated
into the code the matrix sends and expects, and back.

Where the tables come from (WP-A4 part 2, HIL-02/09, BE-15):

* **Reads** were captured on a BK-808 with MCU V1.10.01 / web V2.00.03
  (``tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/``): HDR 0 and
  scaler 0 print as "pass-through" in the Telnet ``status`` dump, scaler 4 as
  "audio only", HDCP 3 as "follow sink", EDID 36 as "frl12g_8k_hdr,7.1ch",
  LCD ``mode`` 3 as "lcd on 30 seconds".
* **Writes** use the same codes as the reads: the device's own configuration
  web interface binds each read array (``allhdr``, ``allscaler``,
  ``allhdcp``, ``edid``, ``mode``) directly to its option lists and sends the
  selected option's id back unchanged. Those option lists are the tables
  below. They are *web-UI-derived* until a hardware write run proves each one
  (``docs/OREI_API_COMMANDS.md`` lists the status per command).

API values vs. device codes:

* HDCP, EDID, LCD and ext-audio mode: the API value **is** the device code.
* HDR and scaler: the hub's API has always been 1-based (HDR 1-3, scaler
  1-5, documented that way in the REST API and stored in scenes/profiles),
  while the device is 0-based. ``api = device + 1``. The REST read endpoints
  report the API value too, so what a client reads can be written back.
"""

from __future__ import annotations

# ---------------------------------------------------------------- per-output

#: Output HDCP mode: device code == API value.
HDCP_MODES: dict[int, str] = {
    1: "HDCP 1.4",
    2: "HDCP 2.2",
    3: "Follow Sink",
    4: "Follow Source",
    5: "User Mode",
}

#: Output HDR conversion, device codes (``allhdr`` / ``set hdr conversion``).
HDR_DEVICE_MODES: dict[int, str] = {
    0: "Passthrough",
    1: "HDR to SDR",
    2: "Auto (follow sink EDID)",
}

#: Output video mode (scaler), device codes (``allscaler`` / ``set video scaler``).
SCALER_DEVICE_MODES: dict[int, str] = {
    0: "Passthrough",
    1: "8K to 4K",
    2: "8K/4K to 1080p",
    3: "Auto (follow sink EDID)",
    4: "Audio Only",
}

#: Device scaler code of an audio-only output (BE-15: read and write agree).
SCALER_AUDIO_ONLY = 4

#: Offset between the hub's 1-based HDR/scaler API values and the device codes.
_API_OFFSET = 1

#: HDR modes by API value (1-3), as the REST API documents them.
HDR_MODES: dict[int, str] = {code + _API_OFFSET: name for code, name in HDR_DEVICE_MODES.items()}
#: Scaler modes by API value (1-5), as the REST API documents them.
SCALER_MODES: dict[int, str] = {code + _API_OFFSET: name for code, name in SCALER_DEVICE_MODES.items()}


def hdr_to_device(api_value: int) -> int:
    """HDR API value (1-3) -> device code (0-2). Raises ValueError if out of range."""
    if api_value not in HDR_MODES:
        raise ValueError(f"HDR mode {api_value!r} not in {min(HDR_MODES)}-{max(HDR_MODES)}")
    return api_value - _API_OFFSET


def hdr_from_device(code: object) -> int | None:
    """Device HDR code -> API value; None for anything the device table does not list."""
    return code + _API_OFFSET if isinstance(code, int) and code in HDR_DEVICE_MODES else None


def scaler_to_device(api_value: int) -> int:
    """Scaler API value (1-5) -> device code (0-4). Raises ValueError if out of range."""
    if api_value not in SCALER_MODES:
        raise ValueError(f"scaler mode {api_value!r} not in {min(SCALER_MODES)}-{max(SCALER_MODES)}")
    return api_value - _API_OFFSET


def scaler_from_device(code: object) -> int | None:
    """Device scaler code -> API value; None for anything the device table does not list."""
    return code + _API_OFFSET if isinstance(code, int) and code in SCALER_DEVICE_MODES else None


# --------------------------------------------------------------------- EDID

#: Input EDID ids (``edid`` in ``get input status`` / ``set edid``). Device id == API value.
EDID_MODES: dict[int, str] = {
    1: "1080p 2.0CH",
    2: "1080p 5.1CH",
    3: "1080p 7.1CH",
    4: "4K30 2.0CH",
    5: "4K30 5.1CH",
    6: "4K30 7.1CH",
    7: "4K60 4:2:0 2.0CH",
    8: "4K60 4:2:0 5.1CH",
    9: "4K60 4:2:0 7.1CH",
    10: "4K60 4:4:4 2.0CH",
    11: "4K60 4:4:4 5.1CH",
    12: "4K60 4:4:4 7.1CH",
    13: "1080p HDR 2.0CH",
    14: "1080p HDR 5.1CH",
    15: "1080p HDR 7.1CH",
    16: "4K30 HDR 2.0CH",
    17: "4K30 HDR 5.1CH",
    18: "4K30 HDR 7.1CH",
    19: "4K60 4:2:0 HDR 2.0CH",
    20: "4K60 4:2:0 HDR 5.1CH",
    21: "4K60 4:2:0 HDR 7.1CH",
    22: "4K60 4:4:4 HDR 2.0CH",
    23: "4K60 4:4:4 HDR 5.1CH",
    24: "4K60 4:4:4 HDR 7.1CH",
    25: "4K120 4:2:0 HDR 2.0CH",
    26: "4K120 4:2:0 HDR 5.1CH",
    27: "4K120 4:2:0 HDR 7.1CH",
    28: "4K120 4:4:4 HDR 2.0CH",
    29: "4K120 4:4:4 HDR 5.1CH",
    30: "4K120 4:4:4 HDR 7.1CH",
    31: "8K FRL 10G HDR 2.0CH",
    32: "8K FRL 10G HDR 5.1CH",
    33: "8K FRL 10G HDR 7.1CH",
    34: "8K FRL 12G HDR 2.0CH",
    35: "8K FRL 12G HDR 5.1CH",
    36: "8K FRL 12G HDR 7.1CH",
    37: "User EDID 1",
    38: "User EDID 2",
    39: "User EDID 3",
    **{39 + n: f"Copy from Output {n}" for n in range(1, 9)},
}

#: ``set edid`` id N copies the EDID of output ``N - EDID_COPY_BASE`` (40 = output 1 ... 47 = output 8).
EDID_COPY_BASE = 39


def edid_copy_from_output(output_num: int) -> int:
    """The EDID id that copies the EDID of ``output_num`` (1-8)."""
    if not 1 <= output_num <= 8:
        raise ValueError(f"output {output_num!r} not in 1-8")
    return EDID_COPY_BASE + output_num


# ------------------------------------------------------------ system / audio

#: Front-panel LCD on-time (``mode`` in ``get system status``, ``"lcd on time"`` in the write).
LCD_TIMEOUT_MODES: dict[int, str] = {
    0: "Off",
    1: "Always On",
    2: "15 seconds",
    3: "30 seconds",
    4: "60 seconds",
}

#: External-audio mode (``mode`` in ``get ext-audio status`` / ``set ext-audio mode``).
EXT_AUDIO_MODES: dict[int, str] = {
    0: "Bind to Input",
    1: "Bind to Output",
    2: "Matrix Mode",
}

#: ``ext-audio switch`` source ids: 1-8 = HDMI input N, 9-16 = the ARC of output N-8.
EXT_AUDIO_ARC_BASE = 8

# ---------------------------------------------------------------------- CEC

#: ``cec command`` indices for source devices (``object`` 0). The hub's table,
#: identical to the device web interface's input control pad.
CEC_INPUT_COMMANDS: dict[str, int] = {
    "POWER_ON": 1,
    "POWER_OFF": 2,
    "UP": 3,
    "LEFT": 4,
    "SELECT": 5,
    "RIGHT": 6,
    "MENU": 7,
    "DOWN": 8,
    "BACK": 9,
    "PREVIOUS": 10,
    "PLAY": 11,
    "NEXT": 12,
    "REWIND": 13,
    "PAUSE": 14,
    "FAST_FORWARD": 15,
    "STOP": 16,
    "MUTE": 17,
    "VOLUME_DOWN": 18,
    "VOLUME_UP": 19,
}

#: ``cec command`` indices for displays (``object`` 1): a different, 0-based
#: table of six commands (the device web interface's output control pad,
#: BE-14). ``ACTIVE`` is the pad's "input/source" key (make the display switch
#: to the matrix); its exact CEC meaning needs the live CEC run.
CEC_OUTPUT_COMMANDS: dict[str, int] = {
    "POWER_ON": 0,
    "POWER_OFF": 1,
    "MUTE": 2,
    "VOLUME_DOWN": 3,
    "VOLUME_UP": 4,
    "ACTIVE": 5,
}
