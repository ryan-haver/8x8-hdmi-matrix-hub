"""In-memory device state of the simulated BK-808.

The state is a plain, JSON-serialisable model grouped per port so state files
are easy to read and edit by hand::

    {
      "schema_version": 1,
      "auth":    {"user": "Admin", "password": "admin"},
      "device":  {...model / firmware / network info...},
      "system":  {"power": 1, "beep": 1, "panel_lock": 0, "lcd_timeout": 3, ...},
      "inputs":  [{"name", "edid", "signal", "cable", "cec_enabled"} x 8],
      "outputs": [{"name", "source", "connected", "stream", "hdcp", "hdr",
                   "scaler", "arc", "audio_mute", "cec_enabled",
                   "ext_audio_enabled", "ext_audio_source"} x 8],
      "ninth_output": {"source", "scaler", "hdr", "hdcp", "arc", "stream", "audio_mute"},
      "ext_audio": {"mode": 0},
      "presets": [{"name", "routing": [8 x input], "saved": true} x 8]
    }

Missing keys fall back to defaults, so partial state files are fine.
:meth:`DeviceState.apply_http_captures` seeds the state from golden responses
captured on real hardware (HIL-A), see ``tools/simulator/README.md``.
"""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

from .protocol import HDCP_RANGE, HDR_RANGE, PORT_COUNT, SCALER_RANGE

SCHEMA_VERSION = 1

DEFAULT_STATE_FILE = Path(__file__).parent / "states" / "default.json"


class StateError(ValueError):
    """Raised when a state document is invalid."""


def _int_in(value: Any, path: str, lo: int, hi: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise StateError(f"{path}: expected integer, got {value!r}")
    if not lo <= value <= hi:
        raise StateError(f"{path}: {value} not in {lo}..{hi}")
    return value


def _flag(value: Any, path: str) -> int:
    if isinstance(value, bool):
        return int(value)
    return _int_in(value, path, 0, 1)


def _str(value: Any, path: str, max_len: int = 64) -> str:
    if not isinstance(value, str):
        raise StateError(f"{path}: expected string, got {value!r}")
    return value[:max_len]


@dataclass
class InputPort:
    name: str
    edid: int = 36
    signal: int = 0  # reported as ``inactive`` (1 = signal present) over HTTP
    cable: int = 0  # Telnet ``r link in N`` / status dump only
    cec_enabled: int = 0


@dataclass
class OutputPort:
    name: str
    source: int = 1
    connected: int = 0  # hot-plug detect: ``allconnect``
    stream: int = 1  # ``allout``
    hdcp: int = 3
    hdr: int = 0  # V1.10.01 reports 0 ("pass-through"), see protocol.HDR_RANGE (HIL-02)
    scaler: int = 0  # V1.10.01 reports 0 ("pass-through") and 4 ("audio only")
    arc: int = 0
    audio_mute: int = 0
    cec_enabled: int = 0
    ext_audio_enabled: int = 0
    ext_audio_source: int = 1


#: Keys of the ninth entry V1.10.01 appends to the per-output arrays (HIL-04).
NINTH_KEYS = ("source", "scaler", "hdr", "hdcp", "arc", "stream", "audio_mute")


def default_ninth_output() -> dict[str, int]:
    """The ninth entry as captured on V1.10.01 (``source`` follows the capture's routing)."""
    return {"source": 1, "scaler": 255, "hdr": 0, "hdcp": 3, "arc": 0, "stream": 255, "audio_mute": 0}


@dataclass
class Preset:
    name: str
    routing: list[int] = field(default_factory=lambda: [1] * PORT_COUNT)
    #: False = the slot is empty: ``r preset N`` answers "preset N is none,please save a preset"
    saved: bool = True


@dataclass
class DeviceState:
    """Complete simulated device state."""

    auth: dict[str, str] = field(default_factory=lambda: {"user": "Admin", "password": "admin"})
    device: dict[str, Any] = field(
        default_factory=lambda: {
            "model": "BK-808",
            "hostname": "BK-808",
            "firmware_version": "V1.10.01",
            "web_version": "V2.00.03",
            "key_mcu_version": "V1.00.08",
            "cpld_version": "V1.00.06",
            #: ``r type`` answer
            "type": "8x8 hdmi2.1 matrix",
            "ip_module_version": "10.01.17",
            "mac_address": "02:00:00:0B:08:08",
            "ip_address": "192.168.0.100",
            "netmask": "255.255.255.0",
            "gateway": "192.168.0.1",
            "dhcp": 0,
            "telnet_port": 23,
            "tcp_port": 8000,
            #: ``get network`` ``username``: an integer on V1.10.01 (1), meaning unknown
            "network_username": 1,
        }
    )
    system: dict[str, int] = field(
        default_factory=lambda: {
            "power": 1,
            "beep": 1,
            "panel_lock": 0,
            "lcd_timeout": 3,
            # ``get system status`` codes, meaning unknown (V1.10.01 reports mode 3, baudrate 6)
            "mode": 3,
            "baudrate": 6,
        }
    )
    inputs: list[InputPort] = field(default_factory=lambda: [InputPort(f"Input {i}") for i in range(1, 9)])
    outputs: list[OutputPort] = field(default_factory=lambda: [OutputPort(f"Output {i}") for i in range(1, 9)])
    #: The ninth entry of ``allsource`` / ``allscaler`` / ``allhdr`` / ``allhdcp`` / ``allarc`` / ``allout`` /
    #: ``allaudiomute`` (HIL-04). What it is (likely the external audio output) is undocumented.
    # ASSUMPTION(HIL-A): the ninth entry never changes with writes (not even
    # "video switch" to all outputs); the simulator reports it from here.
    ninth_output: dict[str, int] = field(default_factory=default_ninth_output)
    ext_audio: dict[str, int] = field(default_factory=lambda: {"mode": 0})
    presets: list[Preset] = field(default_factory=lambda: [Preset(f"Preset {i}") for i in range(1, 9)])

    # ------------------------------------------------------------------ I/O

    @classmethod
    def from_dict(cls, doc: dict[str, Any]) -> DeviceState:
        """Build a validated state from a (possibly partial) document."""
        if not isinstance(doc, dict):
            raise StateError("state document must be a JSON object")
        version = doc.get("schema_version", SCHEMA_VERSION)
        if version != SCHEMA_VERSION:
            raise StateError(f"unsupported schema_version {version!r} (expected {SCHEMA_VERSION})")

        state = cls()
        if "auth" in doc:
            auth = doc["auth"]
            state.auth = {
                "user": _str(auth.get("user", "Admin"), "auth.user"),
                "password": _str(auth.get("password", "admin"), "auth.password"),
            }
        if "device" in doc:
            state.device.update({k: v for k, v in doc["device"].items()})
        if "system" in doc:
            sysdoc = doc["system"]
            for key in state.system:
                if key in sysdoc:
                    state.system[key] = sysdoc[key]
        if "ext_audio" in doc:
            state.ext_audio["mode"] = doc["ext_audio"].get("mode", state.ext_audio["mode"])
        if "ninth_output" in doc:
            ninth = doc["ninth_output"]
            if not isinstance(ninth, dict) or set(ninth) - set(NINTH_KEYS):
                raise StateError(f"ninth_output: expected an object with keys from {list(NINTH_KEYS)}")
            state.ninth_output.update(ninth)

        state.inputs = cls._ports(doc.get("inputs"), InputPort, "inputs", "Input")
        state.outputs = cls._ports(doc.get("outputs"), OutputPort, "outputs", "Output")
        presets = doc.get("presets")
        if presets is not None:
            if not isinstance(presets, list) or len(presets) != PORT_COUNT:
                raise StateError(f"presets: expected a list of {PORT_COUNT}")
            state.presets = [
                Preset(
                    name=p.get("name", f"Preset {i + 1}"),
                    routing=list(p.get("routing", [1] * PORT_COUNT)),
                    saved=bool(p.get("saved", True)),
                )
                for i, p in enumerate(presets)
            ]
        state.validate()
        return state

    @staticmethod
    def _ports(items: Any, kind: type, path: str, default_prefix: str) -> list:
        if items is None:
            return [kind(f"{default_prefix} {i}") for i in range(1, PORT_COUNT + 1)]
        if not isinstance(items, list) or len(items) != PORT_COUNT:
            raise StateError(f"{path}: expected a list of {PORT_COUNT} objects")
        allowed = {f.name for f in fields(kind)}
        ports = []
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise StateError(f"{path}[{i}]: expected object")
            unknown = set(item) - allowed
            if unknown:
                raise StateError(f"{path}[{i}]: unknown keys {sorted(unknown)}")
            data = {"name": f"{default_prefix} {i + 1}", **item}
            ports.append(kind(**data))
        return ports

    @classmethod
    def load(cls, path: str | Path) -> DeviceState:
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    @classmethod
    def default(cls) -> DeviceState:
        """The shipped default state (``states/default.json``)."""
        return cls.load(DEFAULT_STATE_FILE)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "auth": dict(self.auth),
            "device": dict(self.device),
            "system": dict(self.system),
            "inputs": [asdict(p) for p in self.inputs],
            "outputs": [asdict(p) for p in self.outputs],
            "ninth_output": dict(self.ninth_output),
            "ext_audio": dict(self.ext_audio),
            "presets": [asdict(p) for p in self.presets],
        }

    def copy(self) -> DeviceState:
        return copy.deepcopy(self)

    def merged(self, patch: dict[str, Any]) -> DeviceState:
        """Return a new state with ``patch`` deep-merged in (lists of ports by index)."""
        doc = self.to_dict()
        _deep_merge(doc, patch)
        return DeviceState.from_dict(doc)

    # ------------------------------------------------------------ validation

    def validate(self) -> None:
        s = self.system
        _flag(s["power"], "system.power")
        _flag(s["beep"], "system.beep")
        _flag(s["panel_lock"], "system.panel_lock")
        _int_in(s["lcd_timeout"], "system.lcd_timeout", 0, 4)
        _int_in(self.ext_audio["mode"], "ext_audio.mode", 0, 2)
        for i, p in enumerate(self.inputs):
            path = f"inputs[{i}]"
            p.name = _str(p.name, f"{path}.name", 32)
            _int_in(p.edid, f"{path}.edid", 1, 47)
            for key in ("signal", "cable", "cec_enabled"):
                _flag(getattr(p, key), f"{path}.{key}")
        for i, o in enumerate(self.outputs):
            path = f"outputs[{i}]"
            o.name = _str(o.name, f"{path}.name", 32)
            _int_in(o.source, f"{path}.source", 1, PORT_COUNT)
            _int_in(o.hdcp, f"{path}.hdcp", *HDCP_RANGE)
            _int_in(o.hdr, f"{path}.hdr", *HDR_RANGE)
            _int_in(o.scaler, f"{path}.scaler", *SCALER_RANGE)
            _int_in(o.ext_audio_source, f"{path}.ext_audio_source", 1, PORT_COUNT)
            for key in ("connected", "stream", "arc", "audio_mute", "cec_enabled", "ext_audio_enabled"):
                _flag(getattr(o, key), f"{path}.{key}")
        for key in NINTH_KEYS:
            _int_in(self.ninth_output.get(key), f"ninth_output.{key}", 0, 255)
        for i, pr in enumerate(self.presets):
            pr.name = _str(pr.name, f"presets[{i}].name", 32)
            if len(pr.routing) != PORT_COUNT:
                raise StateError(f"presets[{i}].routing: expected {PORT_COUNT} entries")
            for j, src in enumerate(pr.routing):
                _int_in(src, f"presets[{i}].routing[{j}]", 1, PORT_COUNT)

    # -------------------------------------------------------------- helpers

    @property
    def routing(self) -> list[int]:
        return [o.source for o in self.outputs]

    def column(self, ports: str, key: str) -> list:
        return [getattr(p, key) for p in getattr(self, ports)]

    # --------------------------------------------------- golden-capture seed

    def apply_http_captures(self, captures: dict[str, dict[str, Any]]) -> None:
        """Overwrite state from HTTP responses captured on real hardware.

        ``captures`` maps comhead (``"get video status"``, ``"get output
        status"``, ...) to the parsed JSON response. Unknown keys are ignored;
        this is how HIL-A golden fixtures (``tests/fixtures/device/<fw>/``)
        become a simulator seed. See :func:`load_capture_dir`.
        """

        def arr(resp: dict[str, Any], key: str) -> list | None:
            val = resp.get(key)
            return list(val[:PORT_COUNT]) if isinstance(val, list) else None

        def ninth(resp: dict[str, Any], key: str, attr: str) -> None:
            val = resp.get(key)
            if isinstance(val, list) and len(val) > PORT_COUNT:
                self.ninth_output[attr] = val[PORT_COUNT]

        video = captures.get("get video status") or {}
        ninth(video, "allsource", "source")
        if (v := arr(video, "allsource")) is not None:
            for o, src in zip(self.outputs, v, strict=False):
                o.source = src
        if (v := arr(video, "allinputname")) is not None:
            for p, name in zip(self.inputs, v, strict=False):
                p.name = name
        if (v := arr(video, "alloutputname")) is not None:
            for o, name in zip(self.outputs, v, strict=False):
                o.name = name
        if (v := arr(video, "allname")) is not None:
            for pr, name in zip(self.presets, v, strict=False):
                pr.name = name
        if "power" in video:
            self.system["power"] = video["power"]

        out = captures.get("get output status") or {}
        for key, attr in (
            ("allconnect", "connected"),
            ("allscaler", "scaler"),
            ("allhdr", "hdr"),
            ("allhdcp", "hdcp"),
            ("allarc", "arc"),
            ("allout", "stream"),
            ("allaudiomute", "audio_mute"),
            ("allsource", "source"),
        ):
            ninth(out, key, attr)
            if (v := arr(out, key)) is not None:
                for o, val in zip(self.outputs, v, strict=False):
                    setattr(o, attr, val)
        # V1.10.01 names the outputs in ``name`` here (no allinputname/alloutputname).
        if (v := arr(out, "name")) is not None:
            for o, name in zip(self.outputs, v, strict=False):
                o.name = name

        inp = captures.get("get input status") or {}
        if (v := arr(inp, "edid")) is not None:
            for p, val in zip(self.inputs, v, strict=False):
                p.edid = val
        if (v := arr(inp, "inactive")) is not None:
            for p, val in zip(self.inputs, v, strict=False):
                p.signal = val

        cec = captures.get("get cec status") or {}
        if (v := arr(cec, "inputindex")) is not None:
            for p, val in zip(self.inputs, v, strict=False):
                p.cec_enabled = val
        if (v := arr(cec, "outputindex")) is not None:
            for o, val in zip(self.outputs, v, strict=False):
                o.cec_enabled = val

        system = captures.get("get system status") or {}
        for key, attr in (("power", "power"), ("beep", "beep"), ("lock", "panel_lock"), ("mode", "mode"),
                          ("baudrate", "baudrate")):
            if key in system:
                self.system[attr] = system[key]

        info = captures.get("get status") or {}
        for key, attr in (("version", "firmware_version"), ("webversion", "web_version"), ("model", "model"),
                          ("macaddress", "mac_address"), ("hostname", "hostname"), ("ipaddress", "ip_address"),
                          ("subnet", "netmask"), ("gateway", "gateway")):
            if key in info:
                self.device[attr] = info[key]

        net = captures.get("get network") or {}
        for key, attr in (("ipaddress", "ip_address"), ("netmask", "netmask"), ("subnet", "netmask"),
                          ("gateway", "gateway"), ("macaddress", "mac_address"), ("hostname", "hostname"),
                          ("dhcp", "dhcp"), ("telnetport", "telnet_port"), ("tcpport", "tcp_port"),
                          ("username", "network_username"), ("model", "model")):
            if key in net:
                self.device[attr] = net[key]

        ext = captures.get("get ext-audio status") or {}
        if "mode" in ext:
            self.ext_audio["mode"] = ext["mode"]
        if (v := arr(ext, "allsource")) is not None:
            for o, val in zip(self.outputs, v, strict=False):
                o.ext_audio_source = val
        if (v := arr(ext, "allout")) is not None:
            for o, val in zip(self.outputs, v, strict=False):
                o.ext_audio_enabled = val

        self.validate()


def load_capture_dir(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load golden HTTP captures from a directory.

    Each ``*.json`` file holds one response; the comhead is taken from the
    response's ``comhead`` field (falling back to the file stem with ``_``
    replaced by spaces). Files whose stem starts with ``_`` are ignored.
    """
    captures: dict[str, dict[str, Any]] = {}
    for file in sorted(Path(path).glob("*.json")):
        if file.stem.startswith("_"):
            continue
        with open(file, encoding="utf-8") as f:
            doc = json.load(f)
        if isinstance(doc, dict):
            comhead = doc.get("comhead") or file.stem.replace("_", " ")
            captures[comhead] = doc
    return captures


def _deep_merge(target: dict[str, Any], patch: dict[str, Any]) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_merge(target[key], value)
        elif isinstance(value, dict) and isinstance(target.get(key), list):
            # {"outputs": {"0": {"connected": 0}}} patches one port by index
            for idx, item in value.items():
                i = int(idx)
                if isinstance(item, dict) and isinstance(target[key][i], dict):
                    _deep_merge(target[key][i], item)
                else:
                    target[key][i] = item
        else:
            target[key] = value
