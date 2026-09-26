"""Golden mode: serve HIL-A device captures from the simulator, byte for byte.

``python -m tools.simulator --golden tests/fixtures/device/<fw>/`` loads the
records written by ``python -m tools.hil.capture`` (format:
``tests/fixtures/device/README.md``) and:

1. **Seeds the state** from the captured reads (routing, names, output
   settings, EDID, CEC, ext-audio, presets; cable and LCD from the Telnet
   captures), on top of ``--state``.
2. **Serves captured bytes.** For each captured read the simulator computes
   its own answer from the *seed* state once (the *baseline*). At request time:

   * current answer == baseline (nothing relevant changed): the captured body
     is sent verbatim - same bytes, status and ``Content-Type``;
   * something changed (a write, ``/_sim/state``, an event): the captured
     document is *patched*: only the values that differ between baseline and
     the current answer are replaced (list elements individually), keys the
     simulator does not know keep their captured values, and the document is
     re-serialised in the capture's own JSON style (separators, escaping,
     surrounding bytes). So a device-only field or a name prefix survives a
     routing change, and ``allsource`` still follows the routing.

   Telnet reads work the same way, except a changed answer falls back to the
   simulator's own text (patching free text is not attempted). Other Telnet
   commands captured verbatim (set-command acks, error probes) are answered
   with the captured bytes after the simulator has applied them. The banner is
   served verbatim. Logins, the no-session answer, and write results come from
   the captures too (write results by outcome: applied vs. rejected).
3. **Reports** (``--report``) which ``ASSUMPTION(HIL-A)`` guesses the captures
   confirm or contradict, and which are still unconfirmed.

Anything with no capture is answered exactly as without ``--golden``.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

from tools.hil.capture.assumptions import ASSUMPTIONS, BY_ID
from tools.hil.capture.fixtures import (
    REDACTED,
    RecordIds,
    header,
    iter_exchanges,
    iter_records,
    load_manifest,
    unb64,
)

from . import protocol as proto
from .http_commands import HANDLERS, READ_COMMANDS, dispatch
from .state import DeviceState, StateError
from .telnet_commands import _lcd_line, edid_text
from .telnet_commands import banner_bytes as sim_banner_bytes
from .telnet_commands import handle as telnet_handle

CONFIRMED = "confirmed"
CONTRADICTED = "contradicted"
REVIEW = "needs-review"
MISSING = "no-evidence"

_PUSH_RE = re.compile(r"^hdmi\s+(input|output)\s+(\d+)\s*:\s*(connect|disconnect)$", re.IGNORECASE)
_LINK_RE = re.compile(r"hdmi\s+(input|output)\s+(\d+)\s*:\s*(connect|disconnect)", re.IGNORECASE)
_ROUTE_RE = re.compile(r"^output(\d+)->input(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
_PRESET_NONE_RE = re.compile(r"preset\s+\d+\s+is\s+none", re.IGNORECASE)
_MAC_LINE_RE = re.compile(r"^mac address:\s*(\S+)", re.IGNORECASE | re.MULTILINE)


class GoldenError(ValueError):
    """The golden directory is missing or holds no capture records."""


# ------------------------------------------------------------------ JSON style


@dataclass(frozen=True)
class JsonStyle:
    """How the device serialises JSON, so patched documents look the same."""

    separators: tuple[str, str] = (",", ":")
    ensure_ascii: bool = False
    prefix: bytes = b""
    suffix: bytes = b""

    def render(self, doc: Any) -> bytes:
        text = json.dumps(doc, separators=self.separators, ensure_ascii=self.ensure_ascii)
        return self.prefix + text.encode("utf-8") + self.suffix


def detect_style(body: bytes, doc: Any) -> JsonStyle | None:
    """The style that reproduces ``body`` exactly from ``doc`` (None if none does)."""
    for seps in ((",", ":"), (", ", ": "), (",", ": "), (", ", ":")):
        for ensure_ascii in (False, True):
            text = json.dumps(doc, separators=seps, ensure_ascii=ensure_ascii).encode("utf-8")
            idx = body.find(text)
            if idx >= 0 and body[:idx].strip() == b"" and body[idx + len(text):].strip(b" \t\r\n\x00") == b"":
                return JsonStyle(seps, ensure_ascii, body[:idx], body[idx + len(text):])
    return None


def _patch(captured: Any, base: Any, now: Any) -> Any:
    """Apply the change ``base -> now`` to ``captured``, keeping everything else."""
    if base == now:
        return captured
    if isinstance(captured, dict) and isinstance(base, dict) and isinstance(now, dict):
        out = dict(captured)
        for key in captured:
            if key in base and key in now:
                out[key] = _patch(captured[key], base[key], now[key])
        return out
    if (
        isinstance(captured, list) and isinstance(base, list) and isinstance(now, list)
        and len(base) == len(now) and len(captured) >= len(base)
    ):
        head = [_patch(c, b, n) for c, b, n in zip(captured, base, now, strict=False)]
        return head + captured[len(base):]
    return now


def params_key(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    return json.dumps({k: v for k, v in payload.items() if k not in ("comhead", "language")}, sort_keys=True)


def telnet_key(command: str) -> str:
    return re.sub(r"\s+", " ", command.strip().lower())


# ------------------------------------------------------------------- templates


@dataclass
class HttpTemplate:
    source: str
    comhead: str | None
    request: Any
    status: int
    content_type: str
    body: bytes
    doc: Any
    style: JsonStyle | None


@dataclass
class TelnetTemplate:
    source: str
    command: str
    role: str
    body: bytes


@dataclass
class GoldenReply:
    status: int
    content_type: str
    body: bytes
    #: "verbatim" or "patched"
    kind: str
    source: str


def _priority(record_id: str) -> int:
    # Dedicated read captures win over the same command seen during probes/writes.
    for i, prefix in enumerate(("http/", "telnet/", "probe/", "write/")):
        if record_id.startswith(prefix):
            return i
    return 9


_TELNET_TEMPLATE_ROLES = ("read", "write", "write-invalid", "probe-error", "probe-noop-ack")


class GoldenSet:
    """All capture records of one firmware folder, indexed for serving."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        if not self.root.is_dir():
            raise GoldenError(f"golden directory {self.root} does not exist")
        self.manifest = load_manifest(self.root)
        self.records: dict[str, dict[str, Any]] = dict(iter_records(self.root))
        if not self.records:
            raise GoldenError(f"no capture records under {self.root}")
        self.reads: dict[tuple[str, str], HttpTemplate] = {}
        self.reads_by_comhead: dict[str, list[tuple[tuple[str, str], HttpTemplate]]] = {}
        self.login_ok: HttpTemplate | None = None
        self.login_fail: HttpTemplate | None = None
        self.no_session: HttpTemplate | None = None
        self.write_ok: dict[str, HttpTemplate] = {}
        self.write_fail: dict[str, HttpTemplate] = {}
        self.telnet_banner: TelnetTemplate | None = None
        self.telnet: dict[str, TelnetTemplate] = {}
        self.warnings: list[str] = []
        self._baseline_http: dict[tuple[str, str], Any] = {}
        self._baseline_telnet: dict[str, str] = {}
        self._index()

    @classmethod
    def load(cls, root: str | Path) -> GoldenSet:
        return cls(root)

    # ----------------------------------------------------------------- index

    def _index(self) -> None:
        for record_id in sorted(self.records, key=lambda r: (_priority(r), r)):
            record = self.records[record_id]
            for ex in iter_exchanges(record):
                if ex.get("error") or not isinstance(ex.get("response"), dict):
                    continue
                if ex["kind"] == "http":
                    self._index_http(record_id, record, ex)
                else:
                    self._index_telnet(record_id, ex)

    def _http_template(self, record_id: str, ex: dict[str, Any]) -> HttpTemplate | None:
        resp = ex["response"]
        if "body_b64" not in resp:
            return None
        body = unb64(resp["body_b64"])
        doc = resp.get("json")
        return HttpTemplate(
            source=record_id,
            comhead=ex.get("comhead"),
            request=(ex.get("request") or {}).get("json"),
            status=int(resp.get("status") or 200),
            content_type=header(resp.get("headers"), "Content-Type") or proto.RESPONSE_CONTENT_TYPE,
            body=body,
            doc=doc,
            style=detect_style(body, doc) if doc is not None else None,
        )

    def _index_http(self, record_id: str, record: dict[str, Any], ex: dict[str, Any]) -> None:
        role = ex.get("role")
        comhead = ex.get("comhead")
        t = self._http_template(record_id, ex)
        if t is None:
            return
        data = isinstance(t.doc, dict) and bool(set(t.doc) - {"comhead", "result"})
        if role == "read" and comhead in READ_COMMANDS and t.status == 200 and data:
            key = (comhead, params_key(t.request))
            if key not in self.reads:
                self.reads[key] = t
                self.reads_by_comhead.setdefault(comhead, []).append((key, t))
        elif role == "login" and self.login_ok is None and t.status == 200:
            self.login_ok = t
        elif role == "login-wrong" and self.login_fail is None:
            self.login_fail = t
        elif role == "no-session" and self.no_session is None:
            if (record.get("findings") or {}).get("classification") != "data":
                self.no_session = t
        elif role == "write" and comhead in HANDLERS and ex.get("outcome") == "applied":
            self.write_ok.setdefault(comhead, t)
        elif (role == "write-invalid" and comhead in HANDLERS and ex.get("outcome") == "rejected"
              and isinstance(t.doc, dict) and t.doc.get("result") == proto.RESULT_FAIL):
            # Only real rejections: V1.10.01 answers some invalid `cec command`s with result 1.
            self.write_fail.setdefault(comhead, t)

    def _index_telnet(self, record_id: str, ex: dict[str, Any]) -> None:
        resp = ex["response"]
        body = unb64(resp.get("body_b64") or "")
        role = ex.get("role")
        if role == "banner" and record_id == RecordIds.TELNET_BANNER and self.telnet_banner is None:
            self.telnet_banner = TelnetTemplate(record_id, "", role, body)
            return
        command = ex.get("command")
        if role not in _TELNET_TEMPLATE_ROLES or not command or not body or resp.get("completion") == "closed":
            return
        self.telnet.setdefault(telnet_key(command), TelnetTemplate(record_id, command, role, body))

    # ------------------------------------------------------------------ seed

    def captured_reads(self) -> dict[str, Any]:
        """comhead -> captured JSON (one per comhead), as ``apply_http_captures`` wants."""
        out: dict[str, Any] = {}
        for (comhead, _), t in self.reads.items():
            if isinstance(t.doc, dict):
                out.setdefault(comhead, t.doc)
        return out

    def seed(self, state: DeviceState) -> None:
        """Overwrite ``state`` with everything the captures say about the device."""
        backup = state.copy()
        try:
            state.apply_http_captures(self.captured_reads())
            self._seed_presets(state)
            self._seed_telnet(state)
            state.validate()
        except (StateError, TypeError, ValueError, KeyError, IndexError) as exc:
            for f in fields(DeviceState):
                setattr(state, f.name, getattr(backup, f.name))
            self.warnings.append(f"captures could not seed the state ({exc}); using --state as is")

    def _seed_presets(self, state: DeviceState) -> None:
        routing = self.captured_reads().get("get routing status") or {}
        for preset, entry in zip(state.presets, routing.get("allpreset") or [], strict=False):
            if not isinstance(entry, dict):
                continue
            src = entry.get("allsource")
            if isinstance(src, list) and len(src) >= 8 and all(isinstance(v, int) and 1 <= v <= 8 for v in src[:8]):
                preset.routing = list(src[:8])
            if isinstance(entry.get("name"), str):
                preset.name = entry["name"][:32]

    def _seed_telnet(self, state: DeviceState) -> None:
        texts = [t.body.decode("utf-8", errors="replace") for k, t in self.telnet.items()
                 if t.role == "read" and (k == "status" or k.startswith("r link"))]
        for text in texts:
            for kind, port, value in _LINK_RE.findall(text):
                n = int(port)
                if 1 <= n <= 8:
                    if kind.lower() == "input":
                        state.inputs[n - 1].cable = int(value.lower() == "connect")
                    else:
                        state.outputs[n - 1].connected = int(value.lower() == "connect")
        status = self.telnet.get("status")
        if status is not None:
            text = status.body.decode("utf-8", errors="replace")
            lines = {ln.strip() for ln in text.splitlines()}
            for mode in range(5):
                if _lcd_line(mode) in lines:
                    state.system["lcd_timeout"] = mode
            # The MAC as the status dump prints it, when the HTTP reads only
            # have the redaction marker (captures redact what the owner asked).
            mac = _MAC_LINE_RE.search(text)
            if mac and REDACTED in str(state.device.get("mac_address")) and REDACTED not in mac.group(1):
                state.device["mac_address"] = mac.group(1).upper()
        self._seed_telnet_presets(state)
        self._seed_telnet_versions(state)

    def _telnet_read_text(self, command: str) -> str | None:
        t = self.telnet.get(command)
        if t is None or t.role != "read":
            return None
        return t.body.decode("utf-8", errors="replace")

    def _seed_telnet_presets(self, state: DeviceState) -> None:
        """Preset routing and empty slots from ``r preset N`` (V1.10.01 has no HTTP preset read)."""
        for n, preset in enumerate(state.presets, 1):
            text = self._telnet_read_text(f"r preset {n}")
            if text is None:
                continue
            if _PRESET_NONE_RE.search(text):
                preset.saved = False
                continue
            routing = {int(o): int(i) for o, i in _ROUTE_RE.findall(text)}
            if sorted(routing) == list(range(1, 9)) and all(1 <= v <= 8 for v in routing.values()):
                preset.routing = [routing[o] for o in range(1, 9)]
                preset.saved = True

    def _seed_telnet_versions(self, state: DeviceState) -> None:
        text = self._telnet_read_text("r fw version")
        if text is not None:
            for label, key in (("key mcu", "key_mcu_version"), ("cpld version", "cpld_version")):
                m = re.search(rf"^{label}\s*:\s*(\S+)", text, re.IGNORECASE | re.MULTILINE)
                if m:
                    state.device[key] = m.group(1).upper()
        text = self._telnet_read_text("r type")
        if text is not None:
            answer = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().endswith("!")]
            if answer:
                state.device["type"] = answer[0]

    def bind(self, seed_state: DeviceState) -> None:
        """Record the simulator's own answers for the seed state (the baselines)."""
        for key, t in self.reads.items():
            self._baseline_http[key] = dispatch(seed_state.copy(), dict(t.request or {})).response
        for key, t in self.telnet.items():
            if t.role == "read":
                self._baseline_telnet[key] = telnet_handle(seed_state.copy(), t.command).text

    # ----------------------------------------------------------------- serve

    def _find_read(self, payload: dict[str, Any]) -> tuple[tuple[str, str] | None, HttpTemplate | None]:
        comhead = payload.get("comhead")
        key = (comhead, params_key(payload))
        if key in self.reads:
            return key, self.reads[key]
        candidates = self.reads_by_comhead.get(comhead) or []
        if len(candidates) == 1:
            return candidates[0]
        return None, None

    @staticmethod
    def _verbatim(t: HttpTemplate) -> GoldenReply:
        return GoldenReply(t.status, t.content_type, t.body, "verbatim", t.source)

    def _with_comhead(self, t: HttpTemplate, comhead: Any) -> GoldenReply:
        """A captured echo document answered for another comhead."""
        if isinstance(t.doc, dict) and t.doc.get("comhead") == t.comhead and comhead != t.comhead:
            doc = {**t.doc, "comhead": comhead}
            return GoldenReply(t.status, t.content_type, (t.style or JsonStyle()).render(doc), "patched", t.source)
        return self._verbatim(t)

    def http_reply(self, payload: Any, response: Any, entry: dict[str, Any], *,
                   default_session_style: bool = True) -> GoldenReply | None:
        """The golden answer for one ``/cgi-bin/instr`` request, or None."""
        comhead = payload.get("comhead") if isinstance(payload, dict) else None
        if entry.get("fault") == "not_logged_in":
            if self.no_session is None or not default_session_style:
                return None
            return self._with_comhead(self.no_session, comhead)
        if comhead == "login" and "login_ok" in entry:
            t = self.login_ok if entry["login_ok"] else self.login_fail
            return self._verbatim(t) if t is not None else None
        if not isinstance(response, dict) or not isinstance(comhead, str):
            return None
        if comhead in READ_COMMANDS:
            key, t = self._find_read(payload)
            if t is None or key is None:
                return None
            baseline = self._baseline_http.get(key)
            if baseline is None or response == baseline:
                return self._verbatim(t)
            patched = _patch(t.doc, baseline, response)
            return GoldenReply(t.status, t.content_type, (t.style or JsonStyle()).render(patched), "patched", t.source)
        if comhead in HANDLERS:
            ok = response.get("result") != proto.RESULT_FAIL
            t = (self.write_ok if ok else self.write_fail).get(comhead)
            return self._verbatim(t) if t is not None else None
        return None

    def banner_bytes(self) -> bytes | None:
        return self.telnet_banner.body if self.telnet_banner is not None else None

    def telnet_reply(self, command: str, generated_text: str) -> bytes | None:
        """Captured bytes for a Telnet command, or None to use the simulator's text."""
        t = self.telnet.get(telnet_key(command))
        if t is None:
            return None
        if t.role == "read":
            base = self._baseline_telnet.get(telnet_key(command))
            if base is not None and generated_text != base:
                return None
        return t.body

    def describe(self) -> str:
        return (
            f"golden {self.root}: {len(self.reads)} HTTP reads, {len(self.write_ok)} write results, "
            f"{len(self.write_fail)} rejection results, {len(self.telnet)} Telnet answers"
            f"{', banner' if self.telnet_banner else ''}"
            f"{', login' if self.login_ok else ''}{', wrong-password login' if self.login_fail else ''}"
            f"{', no-session answer' if self.no_session else ''}"
        )


# ====================================================================== report


@dataclass
class Verdict:
    id: str
    status: str
    detail: str
    sources: list[str] = field(default_factory=list)


def _sim_body(doc: Any) -> bytes:
    """Exactly what ``Simulator._reply`` sends."""
    return json.dumps(doc, separators=(",", ":")).encode("utf-8") + proto.RESPONSE_BODY_SUFFIX


_REDACTED_B = REDACTED.encode()


def same_bytes(device: bytes, sim: bytes) -> bool:
    """``device == sim``, where a redaction marker in the capture matches any one token.

    The capture tool replaces secrets and the ``--redact`` values (MAC address,
    hostname) with ``***REDACTED***``, so those bytes cannot be compared; the
    rest of the answer still must be identical.
    """
    if device == sim:
        return True
    if _REDACTED_B not in device:
        return False
    pattern = b"[^\\s\",]*".join(re.escape(part) for part in device.split(_REDACTED_B))
    return re.fullmatch(pattern, sim, re.DOTALL) is not None


#: Marker for "the device (or the simulator) sent no answer at all".
UNANSWERED = "no answer"

#: Comheads the hub sends since WP-A4 part 2 that come from the device web interface.
WEB_UI_COMHEADS = frozenset({
    "tx stream", "tx hdcp", "set hdr conversion", "set video scaler", "set arc", "set output audio mute",
    "set edid", "set lcd on time", "set ext-audio mode", "set ext-audio out", "set ext-audio index",
    "ext-audio switch", "preset name", "preset clear", "reboot",
})


def device_unanswered(ex: dict[str, Any]) -> bool:
    """The capture client gave up waiting (no response at all)."""
    return (ex.get("error") or {}).get("type") == "TimeoutError" and not isinstance(ex.get("response"), dict)


def _show(value: Any) -> str:
    return value if value == UNANSWERED else f"result {value!r}"


class _Checks:
    def __init__(self, g: GoldenSet, state: DeviceState) -> None:
        self.g = g
        self.st = state

    # helpers
    def rec(self, record_id: str) -> dict[str, Any] | None:
        return self.g.records.get(record_id)

    def findings(self, record_id: str) -> dict[str, Any] | None:
        rec = self.rec(record_id)
        return rec.get("findings") if rec else None

    def read(self, comhead: str) -> HttpTemplate | None:
        items = self.g.reads_by_comhead.get(comhead) or []
        return items[0][1] if items else None

    def sim(self, payload: dict[str, Any]) -> dict[str, Any]:
        return dispatch(self.st.copy(), dict(payload)).response

    def sim_telnet(self, command: str) -> str:
        return telnet_handle(self.st.copy(), command).text

    def steps(self, test_id: str) -> list[dict[str, Any]]:
        rec = self.rec(RecordIds.write(test_id))
        return list(rec.get("steps") or []) if rec else []

    def sim_result(self, payload: dict[str, Any]) -> Any:
        """The simulator's ``result`` for ``payload`` on the seeded state, or UNANSWERED."""
        r = dispatch(self.st.copy(), dict(payload))
        return UNANSWERED if r.unanswered else r.response.get("result")

    @staticmethod
    def device_result(ex: dict[str, Any]) -> Any:
        """The device's ``result`` for one HTTP exchange, UNANSWERED on a timeout, None without JSON."""
        if device_unanswered(ex):
            return UNANSWERED
        doc = (ex.get("response") or {}).get("json")
        return doc.get("result") if isinstance(doc, dict) else None

    def http_exchanges(self, comheads: frozenset[str] | set[str], roles: tuple[str, ...]) -> list[
        tuple[str, dict[str, Any]]
    ]:
        """(record id, exchange) for every captured HTTP exchange with one of ``comheads`` and ``roles``."""
        out = []
        for rid, rec in sorted(self.g.records.items()):
            for ex in iter_exchanges(rec):
                if ex.get("kind") == "http" and ex.get("comhead") in comheads and ex.get("role") in roles:
                    out.append((rid, ex))
        return out

    def web_ui_steps(self) -> list[tuple[str, dict[str, Any]]]:
        """(record id, step) for every write-mode step that sent a web-UI-derived comhead."""
        out = []
        for rid, rec in sorted(self.g.records.items()):
            for step in rec.get("steps") or []:
                ex = step.get("exchange") or {}
                payload = (ex.get("request") or {}).get("json") or {}
                if ex.get("kind") != "http" or ex.get("comhead") not in WEB_UI_COMHEADS:
                    continue
                if ex.get("comhead") == "set lcd on time" and "lcd on time" not in payload:
                    continue  # the old {"time": N} payload: legacy-unanswered / lcd-codes
                out.append((rid, step))
        return out

    # ---------------------------------------------------------------- checks

    def login_ok_result(self) -> Verdict:
        t = self.g.login_ok
        if t is None or not isinstance(t.doc, dict):
            return Verdict("login-ok-result", MISSING, "no successful login captured")
        v = t.doc.get("result")
        return Verdict("login-ok-result", CONFIRMED if v == proto.LOGIN_OK_RESULT else CONTRADICTED,
                       f"device result={v!r}, simulator LOGIN_OK_RESULT={proto.LOGIN_OK_RESULT!r}", [t.source])

    def login_fail_result(self) -> Verdict:
        t = self.g.login_fail
        if t is None:
            return Verdict("login-fail-result", MISSING, "no wrong-password login captured (run --mode probe)")
        if not isinstance(t.doc, dict):
            return Verdict("login-fail-result", CONTRADICTED,
                           f"device answered HTTP {t.status} with non-JSON {t.body[:80]!r}", [t.source])
        v = t.doc.get("result")
        echo = t.doc.get("comhead") == "login"
        note = " (echoes comhead 'login': the hub's BE-05 check mistakes this for success)" if echo else ""
        return Verdict("login-fail-result", CONFIRMED if v == proto.LOGIN_FAIL_RESULT and echo else CONTRADICTED,
                       f"device {t.doc!r}, simulator result={proto.LOGIN_FAIL_RESULT!r}{note}", [t.source])

    def write_ok_results(self) -> Verdict:
        if not self.g.write_ok:
            return Verdict("write-ok-results", MISSING, "no applied writes captured (run --mode write)")
        bad = []
        for comhead, t in sorted(self.g.write_ok.items()):
            expected = proto.WRITE_RESULT_OVERRIDES.get(comhead, proto.RESULT_OK)
            got = t.doc.get("result") if isinstance(t.doc, dict) else t.body[:40]
            if got != expected:
                bad.append(f"{comhead}: device {got!r}, simulator {expected!r}")
        return Verdict("write-ok-results", CONTRADICTED if bad else CONFIRMED,
                       "; ".join(bad) if bad else f"{len(self.g.write_ok)} comheads match",
                       sorted({t.source for t in self.g.write_ok.values()}))

    def write_fail_result(self) -> Verdict:
        """Each captured invalid write: the device's answer (or silence) vs. the simulator's."""
        accepted, bad, same, src = [], [], 0, set()
        for rid, rec in self.g.records.items():
            for ex in iter_exchanges(rec):
                if ex.get("kind") != "http" or ex.get("role") != "write-invalid":
                    continue
                payload = (ex.get("request") or {}).get("json")
                if not isinstance(payload, dict):
                    continue
                src.add(rid)
                if ex.get("outcome") == "accepted-invalid":
                    accepted.append(f"{ex.get('comhead')} {params_key(payload)}")
                device, sim = self.device_result(ex), self.sim_result(payload)
                if device == sim:
                    same += 1
                else:
                    bad.append(f"{ex.get('comhead')} {params_key(payload)}: device {device!r}, simulator {sim!r}")
        if not src:
            return Verdict("write-fail-result", MISSING, "no rejected writes captured (run --mode write)")
        detail = f"{same} invalid writes answered like the simulator (result 0, or result 1 for the `cec command` " \
                 "parameters the device does not check, or no answer)"
        if bad:
            detail += f"; mismatches: {bad[:4]}"
        if accepted:
            detail += f"; device CHANGED state on invalid parameters: {accepted}"
        return Verdict("write-fail-result", CONTRADICTED if bad or accepted else CONFIRMED, detail, sorted(src))

    def _single_exchange_doc(self, aid: str, record_id: str, expected: Any) -> Verdict:
        rec = self.rec(record_id)
        exs = list(iter_exchanges(rec)) if rec else []
        if not exs or not isinstance(exs[0].get("response"), dict):
            return Verdict(aid, MISSING, "not captured (run --mode probe)")
        doc = exs[0]["response"].get("json")
        return Verdict(aid, CONFIRMED if doc == expected else CONTRADICTED,
                       f"device {doc!r}, simulator {expected!r}", [record_id])

    def unknown_comhead_result(self) -> Verdict:
        rec = self.rec(RecordIds.PROBE_UNKNOWN_COMHEAD)
        exs = list(iter_exchanges(rec)) if rec else []
        if not exs:
            return Verdict("unknown-comhead-result", MISSING, "not captured (run --mode probe)")
        device = self.device_result(exs[0])
        sim = self.sim_result({"comhead": "hil capture unknown", "language": 0})
        return Verdict("unknown-comhead-result", CONFIRMED if device == sim else CONTRADICTED,
                       f"device {_show(device)}, simulator {_show(sim)}", [RecordIds.PROBE_UNKNOWN_COMHEAD])

    def garbage_body(self) -> Verdict:
        rec = self.rec(RecordIds.PROBE_GARBAGE_BODY)
        exs = list(iter_exchanges(rec)) if rec else []
        if not exs:
            return Verdict("garbage-body", MISSING, "not captured (run --mode probe)")
        device = self.device_result(exs[0])
        sim = UNANSWERED if proto.UNKNOWN_COMMANDS_UNANSWERED else proto.RESULT_FAIL
        return Verdict("garbage-body", CONFIRMED if device == sim else CONTRADICTED,
                       f"device {_show(device)}, simulator {_show(sim)}", [RecordIds.PROBE_GARBAGE_BODY])

    def session_expired_style(self) -> Verdict:
        f = self.findings(RecordIds.PROBE_NO_SESSION)
        if f is None:
            return Verdict("session-expired-style", MISSING, "not captured (run --mode probe)")
        kind = f.get("classification")
        src = [RecordIds.PROBE_NO_SESSION]
        if kind == "data":
            return Verdict("session-expired-style", REVIEW, "the no-session read returned data (a session from the "
                           "capture host was active); re-run probe with the hub stopped", src)
        mapping = {"json": "json", "html": "html", "http401": "http401"}
        style = mapping.get(str(kind))
        if style != proto.SESSION_EXPIRED_STYLE:
            return Verdict("session-expired-style", CONTRADICTED,
                           f"device answers {kind!r}, simulator SESSION_EXPIRED_STYLE={proto.SESSION_EXPIRED_STYLE!r}",
                           src)
        t = self.g.no_session
        expected = {"comhead": "get system status", "result": proto.RESULT_FAIL}
        if style == "json" and t is not None and t.doc != expected:
            return Verdict("session-expired-style", CONTRADICTED, f"device JSON {t.doc!r}, simulator {expected!r}", src)
        return Verdict("session-expired-style", CONFIRMED, f"device answers {kind!r}", src)

    def session_mechanism(self) -> Verdict:
        f = self.findings(RecordIds.PROBE_SESSION_MECHANISM)
        if f is None:
            return Verdict("session-mechanism", MISSING, "not captured (run --mode probe)")
        m = f.get("mechanism")
        status = {"ip": CONFIRMED, "cookie": CONTRADICTED}.get(m, REVIEW)
        return Verdict("session-mechanism", status, f"device session mechanism: {m} "
                       f"(cookies set: {f.get('cookies_set')})", [RecordIds.PROBE_SESSION_MECHANISM])

    def session_ttl(self) -> Verdict:
        f = self.findings(RecordIds.PROBE_IDLE_EXPIRY)
        if f is None:
            return Verdict("session-ttl", MISSING, "not captured (run --mode probe --idle-waits ...)")
        alive, expired = f.get("alive_after_s"), f.get("expired_after_s")
        ttl = proto.DEFAULT_SESSION_TTL_S
        src = [RecordIds.PROBE_IDLE_EXPIRY]
        if expired is None:
            return Verdict("session-ttl", REVIEW, f"no expiry within {max(f.get('waits') or [0])} s idle "
                           f"(simulator: {ttl})", src)
        if ttl is None:
            return Verdict("session-ttl", CONTRADICTED,
                           f"device session expired after {alive or 0}-{expired} s idle; simulator never expires", src)
        ok = (alive or 0) < ttl <= expired
        return Verdict("session-ttl", CONFIRMED if ok else CONTRADICTED,
                       f"device expires between {alive or 0} and {expired} s; simulator {ttl} s", src)

    def reboot_replies_first(self) -> Verdict:
        steps = self.steps("http_reboot")
        if not steps:
            return Verdict("reboot-replies-first", MISSING, "not captured (write --include reboot)")
        ex = steps[0]["exchange"]
        replied = isinstance(ex.get("response"), dict) and not ex.get("error")
        return Verdict("reboot-replies-first", CONFIRMED if replied == proto.REBOOT_REPLIES_FIRST else CONTRADICTED,
                       f"device {'answered' if replied else 'dropped the connection'}; back after "
                       f"{steps[0].get('reboot', {}).get('seconds')} s", [RecordIds.write("http_reboot")])

    def standby_behaviour(self) -> Verdict:
        steps = self.steps("http_power")
        if not steps:
            return Verdict("standby-behaviour", MISSING, "not captured (run --mode write)")
        read = next((s for s in steps if s["kind"] == "read"), None)
        noop = next((s for s in steps if s["kind"] == "noop"), None)
        doc = ((read or {}).get("exchange", {}).get("response") or {}).get("json")
        power = doc.get("power") if isinstance(doc, dict) else None
        noop_doc = ((noop or {}).get("exchange", {}).get("response") or {}).get("json")
        noop_result = noop_doc.get("result") if isinstance(noop_doc, dict) else None
        ok = read is not None and read.get("outcome") == "data" and power == 0 and noop_result != proto.RESULT_FAIL
        return Verdict("standby-behaviour", CONFIRMED if ok else CONTRADICTED,
                       f"read in standby: {read.get('outcome') if read else None} (power={power}); "
                       f"write in standby: result={noop_result!r}", [RecordIds.write("http_power")])

    def video_status_names(self) -> Verdict:
        t = self.read("get video status")
        if t is None or not isinstance(t.doc, dict):
            return Verdict("video-status-names", MISSING, "get video status not captured")
        issues = []
        for key in ("allinputname", "alloutputname"):
            names = t.doc.get(key)
            if not isinstance(names, list):
                issues.append(f"{key} missing")
                continue
            if len(names) != 8:
                issues.append(f"{key} has {len(names)} entries: {names!r}")
            prefixed = [n for n in names if isinstance(n, str) and re.match(r"^(IN|OUT)\d+[-_ ]", n)]
            if prefixed:
                issues.append(f"{key} prefixed: {prefixed[:3]}")
            if any(not isinstance(n, str) for n in names):
                issues.append(f"{key} has non-strings")
        return Verdict("video-status-names", CONTRADICTED if issues else CONFIRMED,
                       "; ".join(issues) if issues else "8 plain strings each", [t.source])

    def output_status_name_field(self) -> Verdict:
        t = self.read("get output status")
        if t is None or not isinstance(t.doc, dict):
            return Verdict("output-status-name-field", MISSING, "get output status not captured")
        sim = self.sim(t.request or {"comhead": "get output status"})
        keys = ("name", "allinputname", "alloutputname")
        device_keys = [k for k in keys if k in t.doc]
        sim_keys = [k for k in keys if k in sim]
        return Verdict("output-status-name-field", CONFIRMED if device_keys == sim_keys else CONTRADICTED,
                       f"device sends {device_keys or 'no name arrays'}, simulator {sim_keys or 'none'}", [t.source])

    def _keys(self, aid: str, comhead: str) -> Verdict:
        t = self.read(comhead)
        if t is None or not isinstance(t.doc, dict):
            return Verdict(aid, MISSING, f"{comhead} not captured")
        sim = self.sim(t.request or {"comhead": comhead})
        missing, extra = sorted(set(sim) - set(t.doc)), sorted(set(t.doc) - set(sim))
        if not missing and not extra:
            return Verdict(aid, CONFIRMED, f"same {len(sim)} keys", [t.source])
        return Verdict(aid, CONTRADICTED, f"simulator-only keys {missing}; device-only keys {extra}", [t.source])

    def get_status_fields(self) -> Verdict:
        return self._keys("get-status-fields", "get status")

    def get_network_fields(self) -> Verdict:
        return self._keys("get-network-fields", "get network")

    def preset_get_shape(self) -> Verdict:
        """``preset get`` / ``get routing status``: does the device answer at all (HIL-01)?"""
        notes, bad, src = [], [], []
        for comhead in ("preset get", "get routing status"):
            answered, silent = 0, 0
            for rid, rec in sorted(self.g.records.items()):
                for ex in iter_exchanges(rec):
                    if ex.get("kind") != "http" or ex.get("comhead") != comhead or ex.get("role") != "read":
                        continue
                    src.append(rid)
                    if ex.get("error") or not isinstance(ex.get("response"), dict):
                        silent += 1
                    else:
                        answered += 1
            if not answered and not silent:
                continue
            sim_silent = comhead in proto.UNANSWERED_COMHEADS
            notes.append(f"{comhead}: device {'never answered' if not answered else f'answered {answered}x'}"
                         f"{f' ({silent} without answer)' if answered and silent else ''}, "
                         f"simulator {'does not answer' if sim_silent else 'answers'}")
            if bool(answered) == sim_silent:
                bad.append(comhead)
        if not notes:
            return Verdict("preset-get-shape", MISSING, "preset get / get routing status not captured")
        return Verdict("preset-get-shape", CONTRADICTED if bad else CONFIRMED, "; ".join(notes), sorted(set(src)))

    def ext_audio_index(self) -> Verdict:
        t = self.read("get ext-audio status")
        if t is None or not isinstance(t.doc, dict):
            return Verdict("ext-audio-index", MISSING, "get ext-audio status not captured")
        if "index" not in t.doc:
            return Verdict("ext-audio-index", CONTRADICTED, "device sends no 'index'", [t.source])
        steps = [s for s in self.steps("http_ext_audio_index") if s["kind"] == "write"]
        if steps:
            bad = [s["describe"] for s in steps if s["outcome"] != "applied"]
            return Verdict("ext-audio-index", CONTRADICTED if bad else CONFIRMED,
                           f"`set ext-audio index` read back as `index`: {len(steps) - len(bad)}/{len(steps)} applied",
                           [t.source, RecordIds.write("http_ext_audio_index")])
        return Verdict("ext-audio-index", REVIEW, f"device index={t.doc['index']!r}; the device web interface "
                       "sets it with `set ext-audio index` (the selected audio output); not written on hardware yet",
                       [t.source])

    def http_read_shapes(self) -> Verdict:
        if not self.g.reads:
            return Verdict("http-read-shapes", MISSING, "no reads captured (run --mode read)")
        identical, key_diff, value_diff = [], [], []
        for (comhead, _), t in sorted(self.g.reads.items()):
            sim = self.sim(t.request or {"comhead": comhead})
            label = f"{comhead}{' ' + params_key(t.request) if params_key(t.request) != '{}' else ''}"
            if same_bytes(t.body, _sim_body(sim)):
                identical.append(label)
            elif not isinstance(t.doc, dict) or set(sim) != set(t.doc):
                key_diff.append(label)
            else:
                diffs = [k for k in sim if sim[k] != t.doc.get(k)]
                value_diff.append(f"{label} ({'format' if not diffs else 'values: ' + ', '.join(diffs[:4])})")
        status = CONTRADICTED if key_diff else (REVIEW if value_diff else CONFIRMED)
        detail = f"{len(identical)}/{len(self.g.reads)} byte-identical"
        if key_diff:
            detail += f"; different keys: {key_diff}"
        if value_diff:
            detail += f"; same keys, different bytes: {value_diff}"
        return Verdict("http-read-shapes", status, detail, sorted({t.source for t in self.g.reads.values()}))

    def name_truncation(self) -> Verdict:
        lens, src, sim_lens = [], [], []
        for tid, comhead in (("http_input_name", "set input name"), ("http_output_name", "set output name"),
                             ("http_preset_name", "preset name")):
            f = self.findings(RecordIds.write(tid))
            if f and "long_name_stored_len" in f:
                lens.append(f.get("long_name_stored_len"))
                src.append(RecordIds.write(tid))
                state = self.st.copy()
                dispatch(state, {"comhead": comhead, "language": 0, "index": 1, "name": "x" * f["long_name_sent_len"]})
                names = {"set input name": state.column("inputs", "name"),
                         "set output name": state.column("outputs", "name"),
                         "preset name": [pr.name for pr in state.presets]}[comhead]
                sim_lens.append(len(names[0]))
        if not lens:
            return Verdict("name-truncation", MISSING, "not captured (run --mode write)")
        return Verdict("name-truncation", CONFIRMED if lens == sim_lens else CONTRADICTED,
                       f"40-char names stored as {lens} chars (simulator {sim_lens})", src)

    def _legacy_consistent(self, comheads: frozenset[str] | set[str]) -> tuple[list[str], list[str], list[str]]:
        """Captured exchanges of legacy comheads: (agree with the simulator, disagree, records)."""
        good, bad, src = [], [], []
        for rid, ex in self.http_exchanges(comheads, ("write", "write-invalid", "write-legacy")):
            payload = (ex.get("request") or {}).get("json") or {}
            device, sim = self.device_result(ex), self.sim_result(payload)
            src.append(rid)
            (good if device == sim else bad).append(f"{ex.get('comhead')}: device {_show(device)}, "
                                                    f"simulator {_show(sim)}")
        return good, bad, sorted(set(src))

    def edid_range(self) -> Verdict:
        steps = [s for s in self.steps("http_set_edid") if s["kind"] in ("write", "invalid")]
        old_good, old_bad, old_src = self._legacy_consistent({"set input edid"})
        if not steps:
            status = CONTRADICTED if old_bad else MISSING
            return Verdict("edid-range", status, f"the old 'set input edid' went unanswered {len(old_good)}x on the "
                           "device and in the simulator" + (f"; mismatches {old_bad[:3]}" if old_bad else "")
                           + "; 'set edid' is not captured yet (run --mode write)", old_src)
        lo, hi = proto.EDID_RANGE
        bad, seen = [], []
        for s in steps:
            port, v = (s["exchange"]["request"]["json"].get("edid") or [None, None])[:2]
            accepted = s.get("outcome") in ("applied", "accepted-invalid")
            seen.append(f"{v}:{'yes' if accepted else 'no'}")
            # An invalid input port is rejected whatever the id; only judge ids sent to a valid port.
            port_ok = isinstance(port, int) and 1 <= port <= proto.PORT_COUNT
            if accepted != (port_ok and isinstance(v, int) and lo <= v <= hi):
                bad.append(v)
        return Verdict("edid-range", CONTRADICTED if bad or old_bad else CONFIRMED,
                       f"set edid accepted {seen}; simulator range {lo}-{hi}" + (f"; mismatches {bad}" if bad else ""),
                       [RecordIds.write("http_set_edid"), *old_src])

    def copy_edid(self) -> Verdict:
        old_good, old_bad, old_src = self._legacy_consistent({"copy edid", "set input edid"})
        copies = [s for s in self.steps("http_set_edid") if s["kind"] == "write"
                  and (s["exchange"]["request"]["json"].get("edid") or [0, 0])[1] > 39]
        note = f"'copy edid' / 'set input edid 14+N' unanswered like the simulator ({len(old_good)}x)"
        if old_bad:
            note += f"; mismatches {old_bad[:3]}"
        if not copies:
            return Verdict("copy-edid", CONTRADICTED if old_bad else MISSING,
                           note + "; copy via 'set edid' 40-47 is not captured yet", old_src)
        bad = [s["describe"] for s in copies if s["outcome"] != "applied"]
        return Verdict("copy-edid", CONTRADICTED if bad or old_bad else CONFIRMED,
                       note + f"; set edid 40+ applied {len(copies) - len(bad)}/{len(copies)}",
                       [RecordIds.write("http_set_edid"), *old_src])

    def cec_index_single_port(self) -> Verdict:
        steps = self.steps("http_cec_index_single")
        if steps:
            notes, ok = [], True
            for s in steps:
                device = self.device_result(s["exchange"])
                sim = self.sim_result(s["exchange"]["request"]["json"])
                applied = s["outcome"] in ("applied", "accepted-invalid")
                notes.append(f"{s['outcome']} (device {_show(device)}, simulator {_show(sim)})")
                ok &= not applied and device == sim
            return Verdict("cec-index-single-port", CONFIRMED if ok else CONTRADICTED,
                           f"single-port payload: {notes}; the simulator rejects it like the device",
                           [RecordIds.write("http_cec_index_single")])
        f = self.findings(RecordIds.PROBE_CEC_SHAPES)
        if f:
            return Verdict("cec-index-single-port", REVIEW, f"no-op probe only: bulk result {f.get('bulk_result')!r}, "
                           f"single result {f.get('single_result')!r}; run write mode to see the effect",
                           [RecordIds.PROBE_CEC_SHAPES])
        return Verdict("cec-index-single-port", MISSING, "not captured")

    def cec_disabled_port(self) -> Verdict:
        steps = self.steps("cec_live_output")
        if not steps:
            return Verdict("cec-disabled-port", MISSING, "not captured (write --include cec-live)")
        notes = [s.get("operator_note") for s in steps if s.get("operator_note")]
        return Verdict("cec-disabled-port", REVIEW, f"{len(steps)} live CEC commands, {len(notes)} operator notes; "
                       "compare with the CEC enable state in the record's 'before' snapshot",
                       [RecordIds.write("cec_live_output")])

    def exa_commands(self) -> Verdict:
        old_good, old_bad, old_src = self._legacy_consistent(
            {"set output exa mode", "set output exa", "set output exa in source"})
        outcomes, src = [], []
        for tid in ("http_ext_audio_mode", "http_ext_audio_out", "http_ext_audio_switch", "http_ext_audio_index"):
            steps = [s for s in self.steps(tid) if s["kind"] == "write"]
            if steps:
                src.append(RecordIds.write(tid))
                outcomes += [f"{tid}:{s['outcome']}" for s in steps]
        note = f"old 'set output exa*' unanswered like the simulator ({len(old_good)}x)"
        if old_bad:
            note += f"; mismatches {old_bad[:3]}"
        if not outcomes:
            return Verdict("exa-commands", CONTRADICTED if old_bad else MISSING,
                           note + "; 'set ext-audio *' / 'ext-audio switch' not captured yet", old_src)
        bad = [o for o in outcomes if not o.endswith(":applied")]
        return Verdict("exa-commands", CONTRADICTED if bad or old_bad else CONFIRMED,
                       note + (f"; not applied: {bad}" if bad else f"; {len(outcomes)} writes applied"), src + old_src)

    def output_mode_text(self) -> Verdict:
        maps = {"hdcp": ("http_tx_hdcp", "hdcp", proto.HDCP_TEXT),
                "hdr": ("http_hdr_conversion", "hdr mode", proto.HDR_TEXT),
                "scaler": ("http_video_scaler", "video mode", proto.SCALER_TEXT)}
        bad, good, unparsed, src = [], 0, [], []
        audio_only = None
        for setting, (test_id, label, table) in maps.items():
            for s in self.steps(test_id):
                if s["kind"] != "write" or s["outcome"] != "applied":
                    continue
                payload = s["exchange"]["request"]["json"]
                pair = payload.get(setting) or [None, None]
                port, value = pair[0], pair[1]
                added = (s.get("status_changes") or {}).get("added") or []
                texts = [m.group(1).strip() for ln in added
                         if (m := re.match(rf"output\s*{port}\s+{label}\s*:\s*(.+)$", ln, re.IGNORECASE))]
                if not texts:
                    if added:
                        unparsed.append(f"{setting}={value}: {added[:2]}")
                    continue
                src.append(RecordIds.write(test_id))
                if setting == "scaler" and "audio" in texts[0].lower():
                    audio_only = value
                if texts[0] != table.get(value):
                    bad.append(f"{setting} {value}: device {texts[0]!r}, simulator {table.get(value)!r}")
                else:
                    good += 1
        read_good, read_bad, read_src = self._read_mode_text()
        bad += read_bad
        src += read_src
        if not (bad or good or unparsed):
            if read_good:
                return Verdict("output-mode-text", MISSING,
                               f"read captures agree for {', '.join(read_good)}; every other code needs "
                               "--mode write with Telnet", sorted(set(src)))
            return Verdict("output-mode-text", MISSING, "not captured (run --mode write with Telnet)")
        detail = f"{good} match" + (f"; mismatches: {bad}" if bad else "") + (
            f"; unrecognised status lines: {unparsed}" if unparsed else "")
        if audio_only is not None:
            detail += f"; audio-only scaler code = {audio_only}"
        return Verdict("output-mode-text", CONTRADICTED if bad or unparsed else CONFIRMED, detail, sorted(set(src)))

    def _read_mode_text(self) -> tuple[list[str], list[str], list[str]]:
        """Pair the captured ``get output/input status`` codes with the ``status`` dump wording.

        Returns (codes that agree, mismatches, evidence records).
        """
        status = self.g.telnet.get("status")
        out, inp = self.read("get output status"), self.read("get input status")
        if status is None or status.role != "read":
            return [], [], []
        text = status.body.decode("utf-8", errors="replace")
        tables = [  # (setting, read, key, dump label, code -> simulator text)
            ("hdcp", out, "allhdcp", "hdcp", proto.HDCP_TEXT.get),
            ("hdr", out, "allhdr", "hdr mode", proto.HDR_TEXT.get),
            ("scaler", out, "allscaler", "video mode", proto.SCALER_TEXT.get),
            ("edid", inp, "edid", "edid", edid_text),
        ]
        good: set[str] = set()
        bad: set[str] = set()
        src: set[str] = set()
        for setting, t, key, label, table in tables:
            if t is None or not isinstance(t.doc, dict) or not isinstance(t.doc.get(key), list):
                continue
            values = t.doc[key]
            port_kind = "input" if setting == "edid" else "output"
            for port, value in enumerate(values[:8], 1):
                m = re.search(rf"^{port_kind} {port} {label}\s*:\s*(.+?)\s*$", text, re.IGNORECASE | re.MULTILINE)
                if not m:
                    continue
                src.update({t.source, status.source})
                if table(value) == m.group(1):
                    good.add(f"{setting} {value}")
                else:
                    bad.add(f"{setting} {value}: device {m.group(1)!r}, simulator {table(value)!r}")
        return sorted(good), sorted(bad), sorted(src)

    def ninth_entry(self) -> Verdict:
        """HIL-04: the ninth entry of the per-output arrays."""
        t_out, t_video = self.read("get output status"), self.read("get video status")
        seen, bad, src = [], [], []
        for t, keys in ((t_video, ("allsource",)),
                        (t_out, ("allscaler", "allhdr", "allhdcp", "allarc", "allout", "allaudiomute"))):
            if t is None or not isinstance(t.doc, dict):
                continue
            sim = self.sim(t.request or {"comhead": t.comhead})
            for key in keys:
                dev_v, sim_v = t.doc.get(key), sim.get(key)
                if not isinstance(dev_v, list):
                    continue
                src.append(t.source)
                dev9 = dev_v[8] if len(dev_v) > 8 else None
                sim9 = sim_v[8] if isinstance(sim_v, list) and len(sim_v) > 8 else None
                seen.append(f"{key}={dev9}")
                if len(dev_v) != (len(sim_v) if isinstance(sim_v, list) else -1) or dev9 != sim9:
                    bad.append(f"{key}: device {len(dev_v)} entries (9th {dev9!r}), simulator "
                               f"{len(sim_v) if isinstance(sim_v, list) else None} (9th {sim9!r})")
        if not seen:
            return Verdict("ninth-entry", MISSING, "get video/output status not captured")
        if bad:
            return Verdict("ninth-entry", CONTRADICTED, "; ".join(bad), sorted(set(src)))
        return Verdict("ninth-entry", REVIEW, f"the simulator derives the ninth entries as the device web interface's "
                       f"'All Output' row (common value, 255 when mixed) and reproduces all of them ({', '.join(seen)}); "
                       "how writes with port 0 change them is not captured yet", sorted(set(src)))

    def lcd_codes(self) -> Verdict:
        old_good, old_bad, old_src = self._legacy_consistent({"set lcd on time"})
        old = f"the old {{'time': N}} payload answered like the simulator {len(old_good)}x (result 0)"
        if old_bad:
            old += f"; mismatches {old_bad[:3]}"
        f = self.findings(RecordIds.write("http_lcd_on_time"))
        if not f or not f.get("lcd_outcomes"):
            return Verdict("lcd-codes", CONTRADICTED if old_bad else MISSING,
                           old + "; 'set lcd on time' with 'lcd on time' not captured yet (run --mode write with "
                           "Telnet)", old_src)
        bad = [f"code {m}: {o}" for m, o in sorted(f["lcd_outcomes"].items()) if o != "applied"]
        for mode, line in sorted((f.get("lcd_lines") or {}).items()):
            expected = _lcd_line(int(mode))
            if line is not None and line != expected:
                bad.append(f"code {mode}: device {line!r}, simulator {expected!r}")
        return Verdict("lcd-codes", CONTRADICTED if bad or old_bad else CONFIRMED,
                       "; ".join(bad) or f"{len(f['lcd_outcomes'])} codes applied (read back as `mode`), wording matches",
                       [RecordIds.write("http_lcd_on_time"), *old_src])

    def telnet_banner(self) -> Verdict:
        t = self.g.telnet_banner
        if t is None:
            return Verdict("telnet-banner", MISSING, "banner not captured (run --mode read)")
        sim = sim_banner_bytes(self.st)
        same = same_bytes(t.body, sim)
        return Verdict("telnet-banner", CONFIRMED if same else CONTRADICTED,
                       "identical" if same else f"device {t.body!r}, simulator {sim!r}", [t.source])

    def telnet_iac(self) -> Verdict:
        t = self.g.telnet_banner
        if t is None:
            return Verdict("telnet-iac", MISSING, "banner not captured")
        iac = b"\xff" in t.body
        sim = proto.TELNET_IAC_NEGOTIATION if proto.TELNET_SEND_IAC_NEGOTIATION else b""
        device = t.body[: t.body.rfind(b"\xff") + 3] if iac else b""
        return Verdict("telnet-iac", CONFIRMED if device == sim else CONTRADICTED,
                       f"device sends {device!r}, simulator {sim!r}", [t.source])

    def _telnet_compare(self, aid: str, keys: list[str]) -> Verdict:
        same, diff_ = [], []
        for key in keys:
            t = self.g.telnet[key]
            sim = self.sim_telnet(t.command).encode()
            if same_bytes(t.body, sim):
                same.append(key)
            else:
                diff_.append(f"{key}: device {t.body[:60]!r} vs simulator {sim[:60]!r}")
        if not keys:
            return Verdict(aid, MISSING, "not captured")
        return Verdict(aid, CONTRADICTED if diff_ else CONFIRMED,
                       f"{len(same)}/{len(keys)} identical" + (f"; {diff_[:4]}" if diff_ else ""),
                       sorted({self.g.telnet[k].source for k in keys}))

    def telnet_status_wording(self) -> Verdict:
        if "status" not in self.g.telnet or self.g.telnet["status"].role != "read":
            return Verdict("telnet-status-wording", MISSING, "status not captured (run --mode read)")
        t = self.g.telnet["status"]
        sim = self.sim_telnet("status")
        if same_bytes(t.body, sim.encode()):
            return Verdict("telnet-status-wording", CONFIRMED, "identical", [t.source])
        dev_lines = t.body.decode("utf-8", errors="replace").splitlines()
        sim_lines = sim.splitlines()
        firsts = [f"device {a!r} / simulator {b!r}" for a, b in zip(dev_lines, sim_lines, strict=False) if a != b]
        return Verdict("telnet-status-wording", CONTRADICTED,
                       f"{len(dev_lines)} device lines vs {len(sim_lines)}; first differences: {firsts[:3]}",
                       [t.source])

    def telnet_read_wording(self) -> Verdict:
        keys = [k for k, t in self.g.telnet.items() if t.role == "read" and k != "status"
                and t.source.startswith("telnet/")]
        return self._telnet_compare("telnet-read-wording", sorted(keys))

    def telnet_error_codes(self) -> Verdict:
        keys = [k for k, t in self.g.telnet.items() if t.role == "probe-error"]
        return self._telnet_compare("telnet-error-codes", sorted(keys))

    def telnet_set_acks(self) -> Verdict:
        keys = [k for k, t in self.g.telnet.items() if t.role in ("probe-noop-ack", "write")
                and not k.startswith("s cec") and k != "reboot"]
        return self._telnet_compare("telnet-set-acks", sorted(keys))

    def telnet_terminators(self) -> Verdict:
        problems, count, src = [], 0, set()
        for rid, rec in self.g.records.items():
            for ex in iter_exchanges(rec):
                if ex.get("kind") != "telnet" or ex.get("role") not in ("read", "banner"):
                    continue
                a = (ex.get("response") or {}).get("analysis") or {}
                count += 1
                src.add(rid)
                le = a.get("line_endings") or {}
                if le.get("lf") or le.get("cr"):
                    problems.append(f"{rid}: bare LF/CR {le}")
                if a.get("trailing_without_newline"):
                    problems.append(f"{rid}: text after the last newline {a['trailing_without_newline']!r}")
        framing = self.rec(RecordIds.PROBE_TELNET_FRAMING)
        notes = []
        for v in (framing or {}).get("variants") or []:
            notes.append(f"{v.get('variant')}: {v.get('first_response')!r}")
        if not count:
            return Verdict("telnet-terminators", MISSING, "no Telnet reads captured")
        detail = f"{count} responses; " + ("; ".join(problems[:4]) if problems else "all CRLF, no prompt")
        if notes:
            detail += f"; framing probe: {notes}"
        return Verdict("telnet-terminators", CONTRADICTED if problems else CONFIRMED, detail, sorted(src))

    def telnet_bare_power(self) -> Verdict:
        steps = self.steps("telnet_power_bare")
        if not steps:
            return Verdict("telnet-bare-power", MISSING, "not captured (run --mode write with Telnet)")
        applied = steps[0]["outcome"] == "applied"
        sim_ok = telnet_handle(self.st.copy(), "power 0").recognised
        return Verdict("telnet-bare-power", CONFIRMED if applied == sim_ok else CONTRADICTED,
                       f"'power 0' {'works' if applied else 'does not work'} on the device "
                       f"({steps[0]['exchange'].get('response', {}).get('text')!r})",
                       [RecordIds.write("telnet_power_bare")])

    def telnet_reboot(self) -> Verdict:
        steps = self.steps("telnet_reboot")
        if not steps:
            return Verdict("telnet-reboot", MISSING, "not captured (write --include reboot)")
        text = (steps[0]["exchange"].get("response") or {}).get("text")
        sim = telnet_handle(self.st.copy(), "reboot").text
        return Verdict("telnet-reboot", CONFIRMED if text == sim else CONTRADICTED,
                       f"device {text!r}, simulator {sim!r}", [RecordIds.write("telnet_reboot")])

    def telnet_cec_output_words(self) -> Verdict:
        steps = [s for s in self.steps("cec_live_output") if s["exchange"].get("kind") == "telnet"]
        if not steps:
            return Verdict("telnet-cec-output-words", MISSING, "not captured (write --include cec-live)")
        bad = []
        for s in steps:
            word = s["exchange"]["command"].split()[-1]
            analysis = (s["exchange"].get("response") or {}).get("analysis") or {}
            accepted = not analysis.get("error_codes_seen")
            if accepted != (word in proto.TELNET_CEC_OUTPUT_WORDS):
                bad.append(f"{word}: device {'accepts' if accepted else 'rejects'}")
        return Verdict("telnet-cec-output-words", CONTRADICTED if bad else CONFIRMED,
                       "; ".join(bad) or f"{len(steps)} words agree", [RecordIds.write("cec_live_output")])

    def push_wording(self) -> Verdict:
        lines, src = [], set()
        f = self.findings(RecordIds.PROBE_PUSH_WINDOW)
        if f is not None:
            lines += f.get("lines") or []
            src.add(RecordIds.PROBE_PUSH_WINDOW)
        for rid, rec in self.g.records.items():
            for step in rec.get("steps") or []:
                for chunk in step.get("pushes") or []:
                    lines += [ln.strip() for ln in chunk.get("text", "").splitlines() if ln.strip()]
                    src.add(rid)
        if not lines:
            status = REVIEW if f is not None else MISSING
            return Verdict("push-wording", status, "no unsolicited Telnet lines seen" if f is not None
                           else "not captured (run --mode probe)", sorted(src))
        unknown = sorted({ln for ln in lines if not _PUSH_RE.match(ln)})
        return Verdict("push-wording", CONTRADICTED if unknown else CONFIRMED,
                       f"{len(lines)} lines" + (f"; lines the simulator never sends: {unknown[:6]}" if unknown else
                                                "; all are cable events the simulator sends"), sorted(src))

    def web_ui_commands(self) -> Verdict:
        """The web-UI-derived writes on hardware: answer and readback as the simulator predicts."""
        items = self.web_ui_steps()
        if not items:
            return Verdict("web-ui-commands", MISSING, "not captured yet (run --mode write)")
        bad, good = [], 0
        for rid, s in items:
            ex = s["exchange"]
            payload = ex["request"]["json"]
            device, sim = self.device_result(ex), self.sim_result(payload)
            expected_outcome = {"write": "applied", "invalid": "rejected"}.get(s["kind"])
            ok = device == sim and (expected_outcome is None or s["outcome"] == expected_outcome)
            if ok:
                good += 1
            else:
                bad.append(f"{rid}: {s['describe']}: {s['outcome']}, device {_show(device)}, simulator {_show(sim)}")
        return Verdict("web-ui-commands", CONTRADICTED if bad else CONFIRMED,
                       f"{good}/{len(items)} steps as predicted" + (f"; differences: {bad[:5]}" if bad else ""),
                       sorted({rid for rid, _ in items}))

    def preset_set_empty(self) -> Verdict:
        steps = [s for s in self.steps("http_preset_recall")
                 if s["kind"] == "invalid" and "empty" in s.get("describe", "")]
        if not steps:
            return Verdict("preset-set-empty", MISSING, "not captured (run --mode write with an empty test preset)")
        s = steps[0]
        device = self.device_result(s["exchange"])
        ok = device == proto.RESULT_FAIL and s["outcome"] == "rejected"
        return Verdict("preset-set-empty", CONFIRMED if ok else CONTRADICTED,
                       f"recall of an empty slot: device {_show(device)} ({s['outcome']}), simulator "
                       f"{proto.RESULT_FAIL!r}", [RecordIds.write("http_preset_recall")])

    def legacy_unanswered(self) -> Verdict:
        good, bad, src = self._legacy_consistent(proto.LEGACY_UNANSWERED_WRITES)
        if not src:
            return Verdict("legacy-unanswered", MISSING, "no old-hub commands captured (run --mode write)")
        return Verdict("legacy-unanswered", CONTRADICTED if bad else CONFIRMED,
                       f"{len(good)} exchanges of the old hub's comheads, answered (or not) like the simulator"
                       + (f"; mismatches {bad[:4]}" if bad else ""), src)

    def telnet_multi_session(self) -> Verdict:
        f = self.findings(RecordIds.PROBE_TELNET_SECOND_SESSION)
        if f is None:
            return Verdict("telnet-multi-session", MISSING, "not captured (run --mode probe)")
        ok = bool(f.get("second_session_works")) and bool(f.get("first_session_still_works"))
        return Verdict("telnet-multi-session", CONFIRMED if ok else CONTRADICTED, json.dumps(f),
                       [RecordIds.PROBE_TELNET_SECOND_SESSION])


def assumption_report(golden: GoldenSet | None, base_state: DeviceState | None = None) -> list[Verdict]:
    """One verdict per registered assumption, in registry order."""
    if golden is None:
        return [Verdict(a.id, MISSING, "no --golden directory given") for a in ASSUMPTIONS]
    state = (base_state or DeviceState.default()).copy()
    golden.seed(state)
    checks = _Checks(golden, state)
    verdicts = []
    for a in ASSUMPTIONS:
        method = getattr(checks, a.id.replace("-", "_"))
        try:
            verdicts.append(method())
        except Exception as exc:  # noqa: BLE001 - a malformed capture must not kill the report
            verdicts.append(Verdict(a.id, REVIEW, f"check failed: {type(exc).__name__}: {exc}"))
    return verdicts


_ORDER = ((CONTRADICTED, "CONTRADICTED - the device differs from the simulator: fix tools/simulator"),
          (REVIEW, "NEEDS REVIEW - evidence captured, a human must decide"),
          (MISSING, "NO EVIDENCE - not captured yet"),
          (CONFIRMED, "CONFIRMED - the device matches the simulator"))


def format_report(verdicts: list[Verdict], golden: GoldenSet | None = None) -> str:
    lines = []
    if golden is not None:
        device = golden.manifest.get("device") or {}
        lines.append(f"Simulator assumption report: {golden.root}")
        lines.append(f"  device: {device}")
        lines.append(f"  {golden.describe()}")
        for w in golden.warnings:
            lines.append(f"  warning: {w}")
    else:
        lines.append("Simulator assumption report (no captures)")
    for status, title in _ORDER:
        group = [v for v in verdicts if v.status == status]
        if not group:
            continue
        lines.append("")
        lines.append(f"{title} ({len(group)}):")
        for v in group:
            a = BY_ID[v.id]
            refs = f" [{', '.join(a.refs)}]" if a.refs else ""
            lines.append(f"  {v.id}{refs}: {a.question}")
            lines.append(f"      simulator: {a.where}")
            lines.append(f"      {v.detail}")
            if v.sources:
                shown = ", ".join(v.sources[:4]) + (f" (+{len(v.sources) - 4})" if len(v.sources) > 4 else "")
                lines.append(f"      evidence: {shown}")
    counts = {s: sum(1 for v in verdicts if v.status == s) for s, _ in _ORDER}
    unconfirmed = [v.id for v in verdicts if v.status != CONFIRMED]
    lines.append("")
    lines.append(f"{counts[CONFIRMED]} confirmed, {counts[CONTRADICTED]} contradicted, {counts[REVIEW]} need review, "
                 f"{counts[MISSING]} without evidence.")
    lines.append(f"Still unconfirmed ({len(unconfirmed)}): {', '.join(unconfirmed) or 'none'}")
    return "\n".join(lines)
