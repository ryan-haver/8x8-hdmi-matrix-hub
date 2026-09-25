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
from tools.hil.capture.fixtures import RecordIds, header, iter_exchanges, iter_records, load_manifest, unb64

from . import protocol as proto
from .http_commands import HANDLERS, READ_COMMANDS, dispatch
from .state import DeviceState, StateError
from .telnet_commands import _lcd_line
from .telnet_commands import banner as sim_banner
from .telnet_commands import handle as telnet_handle

CONFIRMED = "confirmed"
CONTRADICTED = "contradicted"
REVIEW = "needs-review"
MISSING = "no-evidence"

_PUSH_RE = re.compile(r"^hdmi\s+(input|output)\s+(\d+)\s*:\s*(connect|disconnect)$", re.IGNORECASE)
_LINK_RE = re.compile(r"hdmi\s+(input|output)\s+(\d+)\s*:\s*(connect|disconnect)", re.IGNORECASE)


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
        elif role == "write-invalid" and comhead in HANDLERS and ex.get("outcome") == "rejected":
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
            lines = {ln.strip() for ln in status.body.decode("utf-8", errors="replace").splitlines()}
            for mode in range(5):
                if _lcd_line(mode) in lines:
                    state.system["lcd_timeout"] = mode

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
    return json.dumps(doc, separators=(",", ":")).encode("utf-8")


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
        accepted = []
        for rid, rec in self.g.records.items():
            for ex in iter_exchanges(rec):
                if ex.get("kind") == "http" and ex.get("outcome") == "accepted-invalid":
                    accepted.append(f"{ex.get('comhead')} {params_key((ex.get('request') or {}).get('json'))}")
        if not self.g.write_fail and not accepted:
            return Verdict("write-fail-result", MISSING, "no rejected writes captured (run --mode write)")
        bad = []
        for comhead, t in sorted(self.g.write_fail.items()):
            got = t.doc.get("result") if isinstance(t.doc, dict) else t.body[:40]
            if got != proto.RESULT_FAIL:
                bad.append(f"{comhead}: device {got!r}")
        detail = "; ".join(bad) if bad else f"{len(self.g.write_fail)} comheads reject with {proto.RESULT_FAIL!r}"
        if accepted:
            detail += f"; device ACCEPTED invalid parameters: {accepted}"
        status = CONTRADICTED if bad or accepted else CONFIRMED
        return Verdict("write-fail-result", status, detail, sorted({t.source for t in self.g.write_fail.values()}))

    def _single_exchange_doc(self, aid: str, record_id: str, expected: Any) -> Verdict:
        rec = self.rec(record_id)
        exs = list(iter_exchanges(rec)) if rec else []
        if not exs or not isinstance(exs[0].get("response"), dict):
            return Verdict(aid, MISSING, "not captured (run --mode probe)")
        doc = exs[0]["response"].get("json")
        return Verdict(aid, CONFIRMED if doc == expected else CONTRADICTED,
                       f"device {doc!r}, simulator {expected!r}", [record_id])

    def unknown_comhead_result(self) -> Verdict:
        return self._single_exchange_doc("unknown-comhead-result", RecordIds.PROBE_UNKNOWN_COMHEAD,
                                         self.sim({"comhead": "hil capture unknown", "language": 0}))

    def garbage_body(self) -> Verdict:
        return self._single_exchange_doc("garbage-body", RecordIds.PROBE_GARBAGE_BODY,
                                         {"comhead": None, "result": proto.RESULT_FAIL})

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
        has_doc = "allinputname" in t.doc and "alloutputname" in t.doc
        detail = "allinputname/alloutputname present" if has_doc else (
            "device sends 'name'" if "name" in t.doc else "no name arrays at all")
        return Verdict("output-status-name-field", CONFIRMED if has_doc else CONTRADICTED, detail, [t.source])

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
        return self._keys("preset-get-shape", "preset get")

    def ext_audio_index(self) -> Verdict:
        t = self.read("get ext-audio status")
        if t is None or not isinstance(t.doc, dict):
            return Verdict("ext-audio-index", MISSING, "get ext-audio status not captured")
        if "index" not in t.doc:
            return Verdict("ext-audio-index", CONTRADICTED, "device sends no 'index'", [t.source])
        return Verdict("ext-audio-index", REVIEW, f"device index={t.doc['index']!r} (simulator sends 1); "
                       "its meaning still needs a human", [t.source])

    def http_read_shapes(self) -> Verdict:
        if not self.g.reads:
            return Verdict("http-read-shapes", MISSING, "no reads captured (run --mode read)")
        identical, key_diff, value_diff = [], [], []
        for (comhead, _), t in sorted(self.g.reads.items()):
            sim = self.sim(t.request or {"comhead": comhead})
            label = f"{comhead}{' ' + params_key(t.request) if params_key(t.request) != '{}' else ''}"
            if _sim_body(sim) == t.body:
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
        lens, src = [], []
        for tid in ("http_input_name", "http_output_name"):
            f = self.findings(RecordIds.write(tid))
            if f and "long_name_stored_len" in f:
                lens.append(f.get("long_name_stored_len"))
                src.append(RecordIds.write(tid))
        if not lens:
            return Verdict("name-truncation", MISSING, "not captured (run --mode write)")
        ok = all(n == 32 for n in lens)
        return Verdict("name-truncation", CONFIRMED if ok else CONTRADICTED,
                       f"40-char names stored as {lens} chars (simulator 32)", src)

    def edid_range(self) -> Verdict:
        f = self.findings(RecordIds.write("http_input_edid"))
        if not f:
            return Verdict("edid-range", MISSING, "not captured (run --mode write)")
        lo, hi = proto.EDID_RANGE
        bad, seen = [], []
        for s in f.get("edid_steps") or []:
            v = (s.get("payload") or {}).get("edid")
            if not isinstance(v, int):
                continue
            accepted = s.get("outcome") in ("applied", "accepted-invalid")
            seen.append(f"{v}:{'yes' if accepted else 'no'}")
            if accepted != (lo <= v <= hi):
                bad.append(v)
        return Verdict("edid-range", CONTRADICTED if bad else CONFIRMED,
                       f"accepted {seen}; simulator range {lo}-{hi}" + (f"; mismatches {bad}" if bad else ""),
                       [RecordIds.write("http_input_edid")])

    def copy_edid(self) -> Verdict:
        f = self.findings(RecordIds.write("http_copy_edid"))
        if not f:
            return Verdict("copy-edid", MISSING, "not captured (run --mode write)")
        notes, ok = [], True
        for s in f.get("edid_steps") or []:
            p = s.get("payload") or {}
            after = [d[3] for d in s.get("edid_after") or []]
            if p.get("comhead") == "copy edid":
                expected = 14 + int(p.get("output", 0))
                notes.append(f"copy edid -> {s.get('outcome')}, EDID now {after or 'unchanged'} "
                             f"(simulator {expected})")
                ok &= after == [expected]
            elif p.get("edid") == 15:
                notes.append(f"set input edid 15 -> {s.get('outcome')}")
                ok &= s.get("outcome") == "applied"
        return Verdict("copy-edid", CONFIRMED if ok else CONTRADICTED, "; ".join(notes),
                       [RecordIds.write("http_copy_edid")])

    def cec_index_single_port(self) -> Verdict:
        steps = self.steps("http_cec_index_single")
        if steps:
            outcomes = [s["outcome"] for s in steps]
            return Verdict("cec-index-single-port", CONFIRMED if all(o == "applied" for o in outcomes) else CONTRADICTED,
                           f"single-port payload outcomes {outcomes}", [RecordIds.write("http_cec_index_single")])
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
        outcomes, src = [], []
        for tid in ("http_exa_mode", "http_exa_enable", "http_exa_source"):
            steps = [s for s in self.steps(tid) if s["kind"] == "write"]
            if steps:
                src.append(RecordIds.write(tid))
                outcomes += [f"{tid}:{s['outcome']}" for s in steps]
        if not outcomes:
            return Verdict("exa-commands", MISSING, "not captured (run --mode write)")
        bad = [o for o in outcomes if not o.endswith(":applied")]
        return Verdict("exa-commands", CONTRADICTED if bad else CONFIRMED,
                       f"not applied: {bad}" if bad else f"{len(outcomes)} writes applied", src)

    def output_mode_text(self) -> Verdict:
        maps = {"hdcp": ("hdcp", proto.HDCP_TEXT), "hdr": ("hdr mode", proto.HDR_TEXT),
                "scaler": ("video mode", proto.SCALER_TEXT)}
        bad, good, unparsed, src = [], 0, [], []
        audio_only = None
        for setting, (label, table) in maps.items():
            for s in self.steps(f"http_output_{setting}"):
                if s["kind"] != "write":
                    continue
                payload = s["exchange"]["request"]["json"]
                value, port = payload.get(setting), payload.get("output")
                added = (s.get("status_changes") or {}).get("added") or []
                texts = [m.group(1).strip() for ln in added
                         if (m := re.match(rf"output\s*{port}\s+{label}\s*:\s*(.+)$", ln, re.IGNORECASE))]
                if not texts:
                    if added:
                        unparsed.append(f"{setting}={value}: {added[:2]}")
                    continue
                src.append(RecordIds.write(f"http_output_{setting}"))
                if setting == "scaler" and "audio" in texts[0].lower():
                    audio_only = value
                if texts[0] != table.get(value):
                    bad.append(f"{setting} {value}: device {texts[0]!r}, simulator {table.get(value)!r}")
                else:
                    good += 1
        if not (bad or good or unparsed):
            return Verdict("output-mode-text", MISSING, "not captured (run --mode write with Telnet)")
        detail = f"{good} match" + (f"; mismatches: {bad}" if bad else "") + (
            f"; unrecognised status lines: {unparsed}" if unparsed else "")
        if audio_only is not None:
            detail += f"; audio-only scaler code = {audio_only}"
        return Verdict("output-mode-text", CONTRADICTED if bad or unparsed else CONFIRMED, detail, sorted(set(src)))

    def lcd_codes(self) -> Verdict:
        f = self.findings(RecordIds.write("http_lcd"))
        if not f or not f.get("lcd_lines"):
            return Verdict("lcd-codes", MISSING, "not captured (run --mode write with Telnet)")
        bad = []
        for mode, line in sorted(f["lcd_lines"].items()):
            expected = _lcd_line(int(mode))
            if line != expected:
                bad.append(f"code {mode}: device {line!r}, simulator {expected!r}")
        return Verdict("lcd-codes", CONTRADICTED if bad else CONFIRMED, "; ".join(bad) or "all 5 codes match",
                       [RecordIds.write("http_lcd")])

    def telnet_banner(self) -> Verdict:
        t = self.g.telnet_banner
        if t is None:
            return Verdict("telnet-banner", MISSING, "banner not captured (run --mode read)")
        sim = sim_banner(self.st).encode()
        return Verdict("telnet-banner", CONFIRMED if t.body == sim else CONTRADICTED,
                       "identical" if t.body == sim else f"device {t.body!r}, simulator {sim!r}", [t.source])

    def telnet_iac(self) -> Verdict:
        t = self.g.telnet_banner
        if t is None:
            return Verdict("telnet-iac", MISSING, "banner not captured")
        iac = b"\xff" in t.body
        return Verdict("telnet-iac", CONFIRMED if iac == proto.TELNET_SEND_IAC_NEGOTIATION else CONTRADICTED,
                       f"device {'sends' if iac else 'sends no'} IAC negotiation", [t.source])

    def _telnet_compare(self, aid: str, keys: list[str]) -> Verdict:
        same, diff_ = [], []
        for key in keys:
            t = self.g.telnet[key]
            sim = self.sim_telnet(t.command).encode()
            if sim == t.body:
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
        if sim.encode() == t.body:
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
