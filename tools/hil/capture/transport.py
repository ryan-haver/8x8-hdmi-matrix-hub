"""Recording HTTP and Telnet clients.

Every request/response pair becomes an *exchange* dict (see
``tests/fixtures/device/README.md``): headers, status, the exact response
bytes (base64), a text/JSON view, and timing. Credentials never enter an
exchange: the login password is replaced at recording time, and cookie values
are masked.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Any

import aiohttp
from aiohttp.abc import AbstractCookieJar

from .fixtures import REDACTED, b64, utc_now

INSTR_PATH = "/cgi-bin/instr"

_SECRET_HEADERS = {"cookie", "authorization", "proxy-authorization"}


def _mask_cookie(value: str) -> str:
    """``SID=abc; Path=/`` -> ``SID=<redacted len=3>; Path=/`` (attributes kept)."""
    parts = [p.strip() for p in value.split(";")]
    if not parts or "=" not in parts[0]:
        return f"<redacted len={len(value)}>"
    name, _, val = parts[0].partition("=")
    return "; ".join([f"{name}=<redacted len={len(val)}>", *parts[1:]])


def _headers(pairs: list[tuple[str, str]]) -> list[str]:
    """Headers in wire order as ``"Name: value"`` strings, secrets masked."""
    out = []
    for k, v in pairs:
        lk = k.lower()
        if lk == "set-cookie":
            v = _mask_cookie(v)
        elif lk in _SECRET_HEADERS:
            v = "; ".join(_mask_cookie(c) for c in v.split(";") if c.strip()) if lk == "cookie" else REDACTED
        out.append(f"{k}: {v}")
    return out


def redact_payload(payload: Any) -> tuple[Any, list[str]]:
    """Copy of a request payload with the password removed."""
    if isinstance(payload, dict) and "password" in payload:
        return {**payload, "password": REDACTED}, ["request.password"]
    return payload, []


def is_data_response(doc: Any) -> bool:
    """A JSON document that carries data (more than comhead/result)."""
    return isinstance(doc, dict) and bool(set(doc) - {"comhead", "result"})


class HttpRecorder:
    """One HTTP client "identity" (its own connection pool and cookie jar)."""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        tls: bool = True,
        timeout: float = 5.0,
        cookies: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.tls = tls
        self.timeout = timeout
        self.cookies = cookies
        self.base_url = f"{'https' if tls else 'http'}://{host}:{port}"
        self._session: aiohttp.ClientSession | None = None

    def clone(self, *, cookies: bool | None = None) -> HttpRecorder:
        """A new independent client (fresh cookie jar and connections)."""
        return HttpRecorder(
            self.host, self.port, tls=self.tls, timeout=self.timeout,
            cookies=self.cookies if cookies is None else cookies,
        )

    async def _client(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=False) if self.tls else aiohttp.TCPConnector()
            # unsafe=True: accept cookies for bare IP hosts, so a cookie-based
            # session would work (the hub's default CookieJar refuses them).
            jar: AbstractCookieJar = (
                aiohttp.CookieJar(unsafe=True) if self.cookies else aiohttp.DummyCookieJar()
            )
            self._session = aiohttp.ClientSession(connector=connector, cookie_jar=jar)
        return self._session

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> HttpRecorder:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    def cookie_names(self) -> list[str]:
        if self._session is None:
            return []
        return sorted({c.key for c in self._session.cookie_jar})

    async def post(
        self,
        payload: Any = None,
        *,
        raw_body: bytes | None = None,
        role: str = "read",
        label: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """POST to ``/cgi-bin/instr``.

        The body is ``json.dumps(payload)`` with default separators, which is
        byte-for-byte what the hub's ``session.post(url, json=command)`` sends.
        """
        body = raw_body if raw_body is not None else json.dumps(payload).encode("utf-8")
        stored_payload, redactions = redact_payload(payload)
        if raw_body is not None:
            body_text = raw_body.decode("utf-8", errors="replace")
        else:
            body_text = json.dumps(stored_payload)
        comhead = payload.get("comhead") if isinstance(payload, dict) else None
        exchange: dict[str, Any] = {
            "kind": "http",
            "role": role,
            "label": label or comhead or "raw",
            "comhead": comhead,
            "request": {
                "method": "POST",
                "path": INSTR_PATH,
                "headers": [],
                "json": stored_payload if raw_body is None else None,
                "body_text": body_text,
            },
        }
        if redactions:
            exchange["redacted"] = redactions
        return await self._send(exchange, "POST", INSTR_PATH, data=body, headers={"Content-Type": content_type})

    async def get(self, path: str = "/", *, role: str = "page", label: str | None = None) -> dict[str, Any]:
        exchange: dict[str, Any] = {
            "kind": "http",
            "role": role,
            "label": label or f"GET {path}",
            "comhead": None,
            "request": {"method": "GET", "path": path, "headers": [], "json": None, "body_text": ""},
        }
        return await self._send(exchange, "GET", path)

    async def _send(self, exchange: dict[str, Any], method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        started = utc_now()
        t0 = time.perf_counter()
        exchange["response"] = None
        exchange["error"] = None
        try:
            client = await self._client()
            async with client.request(
                method, self.base_url + path, timeout=aiohttp.ClientTimeout(total=self.timeout), **kwargs
            ) as resp:
                raw = await resp.read()
                t1 = time.perf_counter()
                exchange["request"]["headers"] = _headers(list(resp.request_info.headers.items()))
                raw_headers = [(k.decode("latin-1"), v.decode("latin-1")) for k, v in resp.raw_headers]
                text = raw.decode("utf-8", errors="replace")
                try:
                    parsed: Any = json.loads(text) if text.strip() else None
                    json_error = None if text.strip() else "empty body"
                except ValueError as exc:
                    parsed, json_error = None, str(exc)
                exchange["response"] = {
                    "status": resp.status,
                    "reason": resp.reason,
                    "http_version": f"{resp.version.major}.{resp.version.minor}" if resp.version else None,
                    "headers": _headers(raw_headers),
                    "body_b64": b64(raw),
                    "body_text": text,
                    "json": parsed,
                    "json_error": json_error,
                }
        except (aiohttp.ClientError, TimeoutError, OSError) as exc:
            t1 = time.perf_counter()
            exchange["error"] = {"type": type(exc).__name__, "message": str(exc)}
        exchange["timing"] = {"started_at": started, "elapsed_ms": round((t1 - t0) * 1000, 2)}
        return exchange


# ----------------------------------------------------------------------- Telnet

_IAC, _DONT, _DO, _WONT, _WILL, _SB, _SE = 255, 254, 253, 252, 251, 250, 240
_ERROR_CODE = re.compile(r"^E\d\d$")


def split_iac(data: bytes) -> tuple[bytes, bytes, list[str]]:
    """Separate Telnet negotiation from data.

    Returns ``(payload, replies, notes)``: ``replies`` refuses every option the
    peer offers or requests (a passive client), ``notes`` describes what was seen.
    """
    out = bytearray()
    replies = bytearray()
    notes: list[str] = []
    i = 0
    while i < len(data):
        b = data[i]
        if b != _IAC:
            out.append(b)
            i += 1
            continue
        nxt = data[i + 1] if i + 1 < len(data) else None
        if nxt == _IAC:
            out.append(_IAC)
            i += 2
        elif nxt in (_WILL, _WONT, _DO, _DONT) and i + 2 < len(data):
            opt = data[i + 2]
            name = {_WILL: "WILL", _WONT: "WONT", _DO: "DO", _DONT: "DONT"}[nxt]
            notes.append(f"IAC {name} {opt}")
            if nxt == _WILL:
                replies += bytes([_IAC, _DONT, opt])
            elif nxt == _DO:
                replies += bytes([_IAC, _WONT, opt])
            i += 3
        elif nxt == _SB:
            end = data.find(bytes([_IAC, _SE]), i + 2)
            notes.append("IAC SB ... SE")
            i = len(data) if end < 0 else end + 2
        else:
            notes.append(f"IAC {nxt}")
            i += 2
    return bytes(out), bytes(replies), notes


def analyse_telnet(data: bytes) -> dict[str, Any]:
    """Describe the framing of a Telnet response (line endings, error code, prompt)."""
    payload, _, iac_notes = split_iac(data)
    text = payload.decode("utf-8", errors="replace")
    crlf = text.count("\r\n")
    bare_lf = text.count("\n") - crlf
    bare_cr = text.count("\r") - crlf
    lines = [ln for ln in re.split(r"\r\n|\n|\r", text)]
    trailing = lines[-1] if lines else ""
    non_empty = [ln.strip() for ln in lines if ln.strip()]
    last = non_empty[-1] if non_empty else ""
    return {
        "line_endings": {"crlf": crlf, "lf": bare_lf, "cr": bare_cr},
        "lines": [ln for ln in lines[:-1]] if text.endswith(("\n", "\r")) else lines,
        "ends_with_newline": text.endswith(("\n", "\r")),
        "trailing_without_newline": trailing if not text.endswith(("\n", "\r")) else "",
        "last_line": last,
        "error_code": last if _ERROR_CODE.match(last) else None,
        "error_codes_seen": sorted({ln for ln in non_empty if _ERROR_CODE.match(ln)}),
        "iac": iac_notes,
    }


class TelnetRecorder:
    """Raw Telnet client that records bytes and chunk timing.

    Responses have no known terminator (that is one of the things HIL-A
    measures), so a response is complete when no byte arrives for ``idle``
    seconds after the first one, or after ``timeout`` seconds overall.
    """

    def __init__(
        self,
        host: str,
        port: int,
        *,
        idle: float = 1.0,
        timeout: float = 5.0,
        banner_idle: float = 1.5,
        connect_timeout: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.idle = idle
        self.timeout = timeout
        self.banner_idle = banner_idle
        self.connect_timeout = connect_timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self.closed_by_peer = False

    def clone(self) -> TelnetRecorder:
        return TelnetRecorder(
            self.host, self.port, idle=self.idle, timeout=self.timeout,
            banner_idle=self.banner_idle, connect_timeout=self.connect_timeout,
        )

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self.closed_by_peer

    async def connect(self, *, role: str = "banner") -> dict[str, Any]:
        """Open the connection; the returned exchange holds the banner."""
        started = utc_now()
        t0 = time.perf_counter()
        exchange: dict[str, Any] = {
            "kind": "telnet", "role": role, "label": "banner", "command": None,
            "sent_b64": "", "response": None, "error": None,
        }
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), self.connect_timeout
            )
            self.closed_by_peer = False
        except (OSError, TimeoutError) as exc:
            exchange["error"] = {"type": type(exc).__name__, "message": str(exc)}
            exchange["timing"] = {"started_at": started, "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)}
            return exchange
        exchange["response"] = await self._read_response(t0, idle=self.banner_idle, timeout=self.timeout)
        exchange["timing"] = {"started_at": started, "elapsed_ms": exchange["response"]["elapsed_ms"]}
        return exchange

    async def close(self) -> None:
        if self._writer is not None:
            try:
                self._writer.close()
                await asyncio.wait_for(self._writer.wait_closed(), 2)
            except (OSError, TimeoutError, ConnectionError):
                pass
        self._reader = self._writer = None

    async def drain_unsolicited(self, wait: float = 0.0) -> list[dict[str, Any]]:
        """Read whatever arrived since the last command (push notifications)."""
        chunks: list[dict[str, Any]] = []
        if self._reader is None:
            return chunks
        deadline = time.perf_counter() + wait
        while True:
            remaining = max(0.0, deadline - time.perf_counter())
            try:
                data = await asyncio.wait_for(self._reader.read(4096), remaining if remaining > 0 else 0.01)
            except TimeoutError:
                break
            except (OSError, ConnectionError):
                self.closed_by_peer = True
                break
            if not data:
                self.closed_by_peer = True
                break
            chunks.append({"t": utc_now(), "b64": b64(data), "text": data.decode("utf-8", errors="replace")})
        return chunks

    async def command(
        self,
        command: str,
        *,
        role: str = "read",
        label: str | None = None,
        suffix: bytes = b"!\r\n",
        raw: bytes | None = None,
        idle: float | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Send ``command + suffix`` (what the hub sends) and record the answer."""
        sent = raw if raw is not None else command.encode("utf-8") + suffix
        exchange: dict[str, Any] = {
            "kind": "telnet",
            "role": role,
            "label": label or command,
            "command": command,
            "sent_b64": b64(sent),
            "sent_text": sent.decode("utf-8", errors="replace"),
            "response": None,
            "error": None,
        }
        started = utc_now()
        t0 = time.perf_counter()
        if self._writer is None or self.closed_by_peer:
            exchange["error"] = {"type": "NotConnected", "message": "telnet connection is not open"}
            exchange["timing"] = {"started_at": started, "elapsed_ms": 0.0}
            return exchange
        unsolicited = await self.drain_unsolicited()
        if unsolicited:
            exchange["unsolicited_before"] = unsolicited
        try:
            self._writer.write(sent)
            await self._writer.drain()
        except (OSError, ConnectionError) as exc:
            self.closed_by_peer = True
            exchange["error"] = {"type": type(exc).__name__, "message": str(exc)}
            exchange["timing"] = {"started_at": started, "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)}
            return exchange
        exchange["response"] = await self._read_response(
            t0, idle=self.idle if idle is None else idle, timeout=self.timeout if timeout is None else timeout
        )
        exchange["timing"] = {"started_at": started, "elapsed_ms": exchange["response"]["elapsed_ms"]}
        return exchange

    async def send_raw(self, data: bytes) -> None:
        if self._writer is None:
            raise ConnectionError("telnet connection is not open")
        self._writer.write(data)
        await self._writer.drain()

    async def listen(self, seconds: float, *, role: str = "push-window", label: str = "listen") -> dict[str, Any]:
        """Record everything the device sends for ``seconds`` (no command sent)."""
        started = utc_now()
        t0 = time.perf_counter()
        chunks: list[dict[str, Any]] = []
        data = bytearray()
        closed = False
        deadline = t0 + seconds
        while self._reader is not None and not closed:
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                break
            try:
                chunk = await asyncio.wait_for(self._reader.read(4096), remaining)
            except TimeoutError:
                break
            except (OSError, ConnectionError):
                closed = True
                break
            if not chunk:
                closed = True
                break
            data += chunk
            chunks.append({"t_ms": round((time.perf_counter() - t0) * 1000, 2), "len": len(chunk),
                           "at": utc_now()})
        if closed:
            self.closed_by_peer = True
        body = bytes(data)
        return {
            "kind": "telnet", "role": role, "label": label, "command": None, "sent_b64": "",
            "response": {
                "body_b64": b64(body),
                "text": body.decode("utf-8", errors="replace"),
                "chunks": chunks,
                "completion": "closed" if closed else "window-ended",
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
                "analysis": analyse_telnet(body),
            },
            "error": None,
            "timing": {"started_at": started, "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)},
        }

    async def _read_response(self, t0: float, *, idle: float, timeout: float) -> dict[str, Any]:
        assert self._reader is not None
        data = bytearray()
        chunks: list[dict[str, Any]] = []
        completion = "no-data"
        first_ms: float | None = None
        deadline = t0 + timeout
        while True:
            now = time.perf_counter()
            remaining = deadline - now
            if remaining <= 0:
                completion = "timeout" if data else "no-data"
                break
            wait = remaining if not data else min(idle, remaining)
            try:
                chunk = await asyncio.wait_for(self._reader.read(4096), wait)
            except TimeoutError:
                if data:
                    completion = "idle" if time.perf_counter() < deadline else "timeout"
                    break
                continue
            except (OSError, ConnectionError):
                completion = "closed"
                self.closed_by_peer = True
                break
            if not chunk:
                completion = "closed"
                self.closed_by_peer = True
                break
            t_ms = round((time.perf_counter() - t0) * 1000, 2)
            if first_ms is None:
                first_ms = t_ms
            payload, replies, _ = split_iac(chunk)
            if replies and self._writer is not None:
                try:
                    self._writer.write(replies)
                    await self._writer.drain()
                except (OSError, ConnectionError):
                    pass
            data += chunk
            chunks.append({"t_ms": t_ms, "len": len(chunk)})
        body = bytes(data)
        return {
            "body_b64": b64(body),
            "text": split_iac(body)[0].decode("utf-8", errors="replace"),
            "chunks": chunks,
            "completion": completion,
            "idle_ms": round(idle * 1000),
            "first_byte_ms": first_ms,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
            "analysis": analyse_telnet(body),
        }
