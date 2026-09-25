"""The simulator: HTTPS device API, Telnet server and control API.

Three listeners:

* **device HTTPS** (``https_port``): ``POST /cgi-bin/instr`` like the BK-808.
* **device Telnet** (``telnet_port``): the port-23 text protocol.
* **control HTTP** (``control_port``): ``/_sim/*`` fault injection and state
  access. It stays up while the device "reboots".

Pass port 0 to any listener to get an ephemeral port (tests do this); the bound
ports are available as attributes after :meth:`Simulator.start`.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from collections import deque
from typing import Any

from aiohttp import web

from . import protocol as proto
from .faults import Faults
from .http_commands import HANDLERS, READ_COMMANDS, dispatch
from .state import DeviceState, StateError
from .telnet_commands import banner
from .telnet_commands import handle as handle_telnet
from .tls import server_ssl_context

_LOG = logging.getLogger("tools.simulator")

_IAC = 0xFF
_IAC_WILL, _IAC_WONT, _IAC_DO, _IAC_DONT, _IAC_SB, _IAC_SE = 0xFB, 0xFC, 0xFD, 0xFE, 0xFA, 0xF0
_OPT_ECHO, _OPT_SGA = 0x01, 0x03


def _strip_iac(data: bytes) -> bytes:
    """Drop Telnet negotiation bytes a client sends (DONT/WONT replies etc.)."""
    out = bytearray()
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
        elif nxt in (_IAC_WILL, _IAC_WONT, _IAC_DO, _IAC_DONT):
            i += 3
        elif nxt == _IAC_SB:
            end = data.find(bytes([_IAC, _IAC_SE]), i + 2)
            i = len(data) if end < 0 else end + 2
        else:
            i += 2
    return bytes(out)


def _redact(payload: Any) -> Any:
    if isinstance(payload, dict) and "password" in payload:
        return {**payload, "password": "***"}
    return payload


class Simulator:
    """A simulated OREI BK-808 matrix."""

    def __init__(
        self,
        state: DeviceState | None = None,
        *,
        host: str = "127.0.0.1",
        https_port: int = 8443,
        telnet_port: int = 2323,
        control_port: int = 8444,
        tls: bool = True,
        require_login: bool = True,
        session_ttl_s: float | None = proto.DEFAULT_SESSION_TTL_S,
        reboot_seconds: float = proto.DEFAULT_REBOOT_SECONDS,
        log_limit: int = 2000,
        golden: Any = None,
    ) -> None:
        self.initial_state = (state or DeviceState.default()).copy()
        #: tools.simulator.golden.GoldenSet: serve HIL-A captures byte for byte
        #: (seed ``state`` with ``golden.seed`` first; baselines are bound here).
        self.golden = golden
        if golden is not None:
            golden.bind(self.initial_state)
        self.state = self.initial_state.copy()
        self.faults = Faults()
        self.host = host
        self.https_port = https_port
        self.telnet_port = telnet_port
        self.control_port = control_port
        self.tls = tls
        self.require_login = require_login
        self.session_ttl_s = session_ttl_s
        self.reboot_seconds = reboot_seconds
        #: client IP -> session expiry (monotonic) or None for "never"
        self.sessions: dict[str, float | None] = {}
        self.log: deque[dict[str, Any]] = deque(maxlen=log_limit)
        self.rebooting = False

        self._device_runner: web.AppRunner | None = None
        self._control_runner: web.AppRunner | None = None
        self._telnet_server: asyncio.Server | None = None
        self._telnet_writers: set[asyncio.StreamWriter] = set()
        self._telnet_tasks: set[asyncio.Task] = set()
        self._background: set[asyncio.Task] = set()
        self._hang_release: asyncio.Event | None = None
        self._ssl = server_ssl_context(("localhost", "127.0.0.1", host)) if tls else None

    # ================================================================ lifecycle

    @property
    def scheme(self) -> str:
        return "https" if self.tls else "http"

    @property
    def device_url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.https_port}"

    @property
    def control_url(self) -> str:
        return f"http://{self.host}:{self.control_port}"

    async def start(self) -> None:
        self._hang_release = asyncio.Event()
        await self._start_device_listeners()
        runner = web.AppRunner(self._control_app(), access_log=None, shutdown_timeout=0.5)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.control_port)
        await site.start()
        self._control_runner = runner
        self.control_port = self._bound_port(runner)
        _LOG.info(
            "BK-808 simulator up: %s (device), telnet %s:%d, control %s",
            self.device_url, self.host, self.telnet_port, self.control_url,
        )

    async def stop(self) -> None:
        for task in list(self._background):
            task.cancel()
        for task in list(self._background):
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await task
        await self._stop_device_listeners()
        if self._control_runner:
            await self._control_runner.cleanup()
            self._control_runner = None

    async def __aenter__(self) -> Simulator:
        await self.start()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.stop()

    @staticmethod
    def _bound_port(runner: web.AppRunner) -> int:
        for addr in runner.addresses:
            if isinstance(addr, tuple) and len(addr) >= 2:
                return int(addr[1])
        raise RuntimeError("listener has no bound address")

    async def _start_device_listeners(self) -> None:
        app = web.Application()
        app.router.add_post(proto.INSTR_PATH, self._handle_instr)
        app.router.add_get("/", self._handle_index)
        runner = web.AppRunner(app, access_log=None, shutdown_timeout=0.5)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.https_port, ssl_context=self._ssl)
        await site.start()
        self._device_runner = runner
        self.https_port = self._bound_port(runner)

        self._telnet_server = await asyncio.start_server(self._handle_telnet_client, self.host, self.telnet_port)
        self.telnet_port = self._telnet_server.sockets[0].getsockname()[1]

    async def _stop_device_listeners(self) -> None:
        self._release_hangs()
        if self._telnet_server:
            self._telnet_server.close()
            for writer in list(self._telnet_writers):
                with contextlib.suppress(Exception):
                    writer.close()
            for task in list(self._telnet_tasks):
                task.cancel()
            for task in list(self._telnet_tasks):
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await task
            with contextlib.suppress(Exception):
                await asyncio.wait_for(self._telnet_server.wait_closed(), 2)
            self._telnet_server = None
        if self._device_runner:
            # Kill keep-alive connections abruptly (a real reboot does not
            # finish in-flight requests gracefully).
            server = self._device_runner.server
            for conn in list(server.connections) if server is not None else []:
                with contextlib.suppress(Exception):
                    conn.force_close()
                    if conn.transport is not None:
                        conn.transport.abort()
            await self._device_runner.cleanup()
            self._device_runner = None

    def _spawn(self, coro: Any) -> asyncio.Task:
        task = asyncio.ensure_future(coro)
        self._background.add(task)
        task.add_done_callback(self._background.discard)
        return task

    # ================================================================ actions

    def reset(self, state: DeviceState | None = None) -> None:
        """Restore the seed state and clear faults, sessions and the log."""
        if state is not None:
            self.initial_state = state.copy()
        self.state = self.initial_state.copy()
        self.faults = Faults()
        self.sessions.clear()
        self.log.clear()
        self._release_hangs()

    def clear_faults(self) -> None:
        self.faults = Faults()
        self._release_hangs()

    def expire_sessions(self) -> None:
        self.sessions.clear()
        self._record("sim", "expire sessions")

    async def reboot(self, seconds: float | None = None) -> None:
        """Take both device listeners down for ``seconds``, then bring them back."""
        if self.rebooting:
            return
        seconds = self.reboot_seconds if seconds is None else seconds
        self.rebooting = True
        self._record("sim", f"reboot ({seconds:g}s)")
        _LOG.warning("Simulated reboot: device offline for %.1fs", seconds)
        try:
            await self._stop_device_listeners()
            self.sessions.clear()
            await asyncio.sleep(seconds)
            await self._start_device_listeners()
        finally:
            self.rebooting = False
        _LOG.warning("Simulated reboot complete")

    def schedule_reboot(self, seconds: float | None = None, delay: float = 0.05) -> None:
        async def later() -> None:
            await asyncio.sleep(delay)
            await self.reboot(seconds)

        self._spawn(later())

    async def push(self, line: str) -> int:
        """Send an unsolicited line to every Telnet client; returns client count."""
        data = (line + proto.TELNET_EOL).encode()
        sent = 0
        for writer in list(self._telnet_writers):
            try:
                writer.write(data)
                await writer.drain()
                sent += 1
            except Exception:  # noqa: BLE001 - client went away
                self._telnet_writers.discard(writer)
        self._record("telnet-push", line, response={"clients": sent})
        return sent

    async def cable_event(self, port_type: str, port: int, connected: bool) -> None:
        """Physically (un)plug a cable: update state and push the Telnet event."""
        if port_type not in ("input", "output") or not 1 <= port <= proto.PORT_COUNT:
            raise ValueError("port_type must be input/output and port 1-8")
        if port_type == "input":
            self.state.inputs[port - 1].cable = int(connected)
        else:
            self.state.outputs[port - 1].connected = int(connected)
        # ASSUMPTION(HIL-A): push wording (the client parses
        # "hdmi input|output N: connect|disconnect").
        await self.push(f"hdmi {port_type} {port}: {'connect' if connected else 'disconnect'}")

    # ================================================================ logging

    def _record(self, channel: str, command: Any, **extra: Any) -> dict[str, Any]:
        entry = {"t": round(time.time(), 3), "channel": channel, "command": command, **extra}
        self.log.append(entry)
        return entry

    def unrecognised(self) -> list[dict[str, Any]]:
        return [e for e in self.log if e.get("recognised") is False]

    # ================================================================ HTTP device

    async def _handle_index(self, request: web.Request) -> web.Response:
        d = self.state.device
        return web.Response(
            text=f"<html><body><h1>{d['model']} (simulated)</h1><p>fw {d['firmware_version']}</p></body></html>",
            content_type="text/html",
        )

    def _session_valid(self, client: str) -> bool:
        if not self.require_login:
            return True
        if client not in self.sessions:
            return False
        expiry = self.sessions[client]
        if expiry is not None and time.monotonic() > expiry:
            del self.sessions[client]
            return False
        return True

    def _release_hangs(self) -> None:
        if self._hang_release is not None:
            self._hang_release.set()
            self._hang_release = asyncio.Event()

    @staticmethod
    def _reply(doc: Any) -> web.Response:
        return web.Response(text=json.dumps(doc, separators=(",", ":")), content_type=proto.RESPONSE_CONTENT_TYPE)

    async def _handle_instr(self, request: web.Request) -> web.StreamResponse:
        client = request.remote or "?"
        if self.rebooting:
            if request.transport is not None:
                request.transport.abort()
            return web.Response(status=503)
        text = await request.text()
        try:
            payload = json.loads(text)
        except ValueError:
            payload = None
        comhead = payload.get("comhead") if isinstance(payload, dict) else None

        if self.faults.latency_ms:
            await asyncio.sleep(self.faults.latency_ms / 1000)

        # ---- transport faults
        if self.faults.http_applies(comhead):
            f = self.faults
            hang, drop, status, malformed = f.hang_http, f.drop_http, f.http_status, f.malformed_json
            f.consume_http()
            if hang:
                self._record("http", comhead, client=client, payload=_redact(payload), fault="hang_http")
                _LOG.info("HTTP  <- %s  [fault: hang]", comhead)
                assert self._hang_release is not None
                await self._hang_release.wait()
                drop = True
            if drop:
                self._record("http", comhead, client=client, payload=_redact(payload), fault="drop_http")
                _LOG.info("HTTP  <- %s  [fault: drop connection]", comhead)
                if request.transport is not None:
                    request.transport.abort()
                return web.Response(status=500)
            if status:
                self._record("http", comhead, client=client, payload=_redact(payload), fault=f"http_{status}")
                _LOG.info("HTTP  <- %s  [fault: HTTP %d]", comhead, status)
                return web.Response(status=status, text=f"HTTP {status}", content_type="text/plain")
        else:
            malformed = False

        response, entry = self._process(client, payload, comhead)
        if self.golden is not None:
            golden = self.golden.http_reply(
                payload, response, entry,
                default_session_style=self.faults.session_expired_style == proto.SESSION_EXPIRED_STYLE,
            )
            if golden is not None:
                entry["golden"] = golden.kind
                body = golden.body[: max(1, len(golden.body) // 2)] if malformed else golden.body
                return web.Response(body=body, status=golden.status, headers={"Content-Type": golden.content_type})
        if malformed:
            body = json.dumps(response)
            entry["fault"] = "malformed_json"
            _LOG.info("HTTP  -> [fault: malformed JSON]")
            return web.Response(text=body[: max(1, len(body) // 2)], content_type=proto.RESPONSE_CONTENT_TYPE)
        if isinstance(response, web.Response):
            return response
        return self._reply(response)

    def _process(self, client: str, payload: Any, comhead: Any) -> tuple[Any, dict[str, Any]]:
        """Run one JSON command; returns (response doc or web.Response, log entry)."""
        if not isinstance(payload, dict) or not isinstance(comhead, str):
            # ASSUMPTION(HIL-A): garbage bodies are answered with an empty
            # failure document.
            resp: Any = {"comhead": comhead, "result": proto.RESULT_FAIL}
            entry = self._record("http", comhead, client=client, payload=payload, response=resp, recognised=False)
            _LOG.warning("HTTP  <- unparseable/invalid body from %s", client)
            return resp, entry

        if comhead == "login":
            state = self.state
            ok = (
                payload.get("user") == state.auth["user"]
                and payload.get("password") == state.auth["password"]
                and not self.faults.wrong_password
            )
            if ok:
                ttl = self.session_ttl_s
                self.sessions[client] = None if ttl is None else time.monotonic() + ttl
                resp = {"comhead": "login", "result": proto.LOGIN_OK_RESULT}
            else:
                self.sessions.pop(client, None)
                resp = {"comhead": "login", "result": proto.LOGIN_FAIL_RESULT}
            entry = self._record("http", "login", client=client, payload=_redact(payload), response=resp,
                                 recognised=True, login_ok=ok)
            _LOG.info("HTTP  <- login user=%r -> %s", payload.get("user"), "OK" if ok else "REJECTED")
            return resp, entry

        if not self._session_valid(client):
            style = self.faults.session_expired_style
            entry = self._record("http", comhead, client=client, payload=payload, fault="not_logged_in",
                                 recognised=comhead in HANDLERS)
            _LOG.info("HTTP  <- %s  [not logged in -> %s]", comhead, style)
            if style == "html":
                return web.Response(text=proto.SESSION_EXPIRED_HTML, content_type="text/html"), entry
            if style == "http401":
                return web.Response(status=401, text="Unauthorized"), entry
            resp = {"comhead": comhead, "result": proto.RESULT_FAIL}
            entry["response"] = resp
            return resp, entry

        if self.faults.reject_writes and comhead in HANDLERS and comhead not in READ_COMMANDS:
            resp = {"comhead": comhead, "result": proto.RESULT_FAIL}
            entry = self._record("http", comhead, client=client, payload=payload, response=resp,
                                 recognised=True, fault="reject_writes")
            _LOG.info("HTTP  <- %s  [fault: reject write]", comhead)
            return resp, entry

        result = dispatch(self.state, payload)
        entry = self._record(
            "http", comhead, client=client, payload=payload, response=result.response,
            recognised=result.recognised, mutated=result.mutated, warnings=result.warnings,
        )
        if not result.recognised:
            _LOG.warning("HTTP  <- %s  UNRECOGNISED comhead %r", payload, comhead)
        else:
            _LOG.info("HTTP  <- %s %s", comhead, {k: v for k, v in payload.items() if k != "comhead"})
        for warning in result.warnings:
            _LOG.warning("HTTP     %s: %s", comhead, warning)
        if result.reboot:
            self.schedule_reboot()
        return result.response, entry

    # ================================================================ Telnet

    async def _handle_telnet_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        task = asyncio.current_task()
        if task is not None:
            self._telnet_tasks.add(task)
        peer = writer.get_extra_info("peername")
        client = peer[0] if peer else "?"
        try:
            if self.faults.telnet_refuse:
                self._record("telnet", "<connect>", client=client, fault="telnet_refuse")
                return
            self._telnet_writers.add(writer)
            self._record("telnet", "<connect>", client=client)
            _LOG.info("TELNET connection from %s", client)
            if proto.TELNET_SEND_IAC_NEGOTIATION:
                writer.write(bytes([_IAC, _IAC_WILL, _OPT_ECHO, _IAC, _IAC_WILL, _OPT_SGA]))
            golden_banner = self.golden.banner_bytes() if self.golden is not None else None
            writer.write(golden_banner if golden_banner is not None else banner(self.state).encode())
            await writer.drain()
            buf = b""
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                buf += _strip_iac(data)
                while proto.TELNET_COMMAND_TERMINATOR in buf:
                    raw, buf = buf.split(proto.TELNET_COMMAND_TERMINATOR, 1)
                    cmd = raw.decode("utf-8", errors="replace").strip()
                    if cmd and not await self._telnet_command(client, cmd, writer):
                        return
        except (ConnectionError, OSError):
            pass
        except asyncio.CancelledError:
            pass
        finally:
            self._telnet_writers.discard(writer)
            with contextlib.suppress(Exception):
                writer.close()
            if task is not None:
                self._telnet_tasks.discard(task)

    async def _telnet_command(self, client: str, cmd: str, writer: asyncio.StreamWriter) -> bool:
        """Handle one command; returns False when the connection must close."""
        if self.faults.latency_ms:
            await asyncio.sleep(self.faults.latency_ms / 1000)
        faults = self.faults
        if faults.telnet_silent:
            faults.consume_telnet()
            self._record("telnet", cmd, client=client, fault="telnet_silent")
            _LOG.info("TELNET <- %s  [fault: silent]", cmd)
            return True

        result = handle_telnet(self.state, cmd)
        entry = self._record(
            "telnet", cmd, client=client, response=result.text, recognised=result.recognised,
            mutated=result.mutated, warnings=result.warnings,
        )
        level = logging.INFO if result.recognised else logging.WARNING
        _LOG.log(level, "TELNET <- %s%s", cmd, "" if result.recognised else "  UNRECOGNISED")

        data = result.text.encode()
        if self.golden is not None:
            golden = self.golden.telnet_reply(cmd, result.text)
            if golden is not None:
                entry["golden"] = "verbatim"
                data = golden

        if faults.telnet_close_mid_command:
            faults.consume_telnet()
            entry["fault"] = "telnet_close_mid_command"
            writer.write(data[: max(1, len(data) // 2)])
            with contextlib.suppress(Exception):
                await writer.drain()
            _LOG.info("TELNET     [fault: closed mid-response]")
            return False

        writer.write(data)
        await writer.drain()
        if result.reboot:
            self.schedule_reboot()
            return False
        return True

    # ================================================================ control API

    def _control_app(self) -> web.Application:
        app = web.Application()
        r = app.router
        r.add_get("/_sim/health", self._c_health)
        r.add_get("/_sim/state", self._c_get_state)
        r.add_put("/_sim/state", self._c_put_state)
        r.add_patch("/_sim/state", self._c_patch_state)
        r.add_post("/_sim/reset", self._c_reset)
        r.add_get("/_sim/faults", self._c_get_faults)
        r.add_post("/_sim/faults", self._c_set_faults)
        r.add_delete("/_sim/faults", self._c_clear_faults)
        r.add_post("/_sim/reboot", self._c_reboot)
        r.add_post("/_sim/sessions/expire", self._c_expire)
        r.add_post("/_sim/event", self._c_event)
        r.add_get("/_sim/log", self._c_get_log)
        r.add_delete("/_sim/log", self._c_clear_log)
        return app

    @staticmethod
    async def _json_body(request: web.Request) -> Any:
        if not request.can_read_body:
            return {}
        try:
            return await request.json()
        except ValueError as exc:
            raise web.HTTPBadRequest(text=f"invalid JSON: {exc}") from exc

    async def _c_health(self, request: web.Request) -> web.Response:
        return web.json_response(
            {
                "rebooting": self.rebooting,
                "device_url": self.device_url,
                "https_port": self.https_port,
                "telnet_port": self.telnet_port,
                "control_port": self.control_port,
                "tls": self.tls,
                "sessions": len(self.sessions),
                "telnet_clients": len(self._telnet_writers),
                "faults": self.faults.to_dict(),
                "golden": str(self.golden.root) if self.golden is not None else None,
            }
        )

    async def _c_get_state(self, request: web.Request) -> web.Response:
        return web.json_response(self.state.to_dict())

    async def _c_put_state(self, request: web.Request) -> web.Response:
        body = await self._json_body(request)
        try:
            new_state = DeviceState.from_dict(body)
        except StateError as exc:
            raise web.HTTPBadRequest(text=str(exc)) from exc
        self.state = new_state
        if request.query.get("as_default", "").lower() in ("1", "true", "yes"):
            self.initial_state = new_state.copy()
        self._record("sim", "put state")
        return web.json_response(self.state.to_dict())

    async def _c_patch_state(self, request: web.Request) -> web.Response:
        body = await self._json_body(request)
        try:
            self.state = self.state.merged(body)
        except (StateError, TypeError, IndexError, ValueError) as exc:
            raise web.HTTPBadRequest(text=str(exc)) from exc
        self._record("sim", "patch state", payload=body)
        return web.json_response(self.state.to_dict())

    async def _c_reset(self, request: web.Request) -> web.Response:
        self.reset()
        return web.json_response(self.state.to_dict())

    async def _c_get_faults(self, request: web.Request) -> web.Response:
        return web.json_response(self.faults.to_dict())

    async def _c_set_faults(self, request: web.Request) -> web.Response:
        body = await self._json_body(request)
        try:
            self.faults.update(body)
        except ValueError as exc:
            raise web.HTTPBadRequest(text=str(exc)) from exc
        if not self.faults.hang_http:
            self._release_hangs()
        self._record("sim", "set faults", payload=body)
        _LOG.warning("Faults set: %s", body)
        return web.json_response(self.faults.to_dict())

    async def _c_clear_faults(self, request: web.Request) -> web.Response:
        self.clear_faults()
        self._record("sim", "clear faults")
        return web.json_response(self.faults.to_dict())

    async def _c_reboot(self, request: web.Request) -> web.Response:
        body = await self._json_body(request)
        seconds = float(body.get("seconds", self.reboot_seconds))
        self.schedule_reboot(seconds, delay=0)
        return web.json_response({"rebooting": True, "seconds": seconds})

    async def _c_expire(self, request: web.Request) -> web.Response:
        self.expire_sessions()
        return web.json_response({"sessions": 0})

    async def _c_event(self, request: web.Request) -> web.Response:
        body = await self._json_body(request)
        kind = body.get("type")
        try:
            if kind == "cable":
                await self.cable_event(body["port_type"], int(body["port"]), bool(body["connected"]))
            elif kind == "signal":
                port = int(body["port"])
                if not 1 <= port <= proto.PORT_COUNT:
                    raise ValueError("port must be 1-8")
                self.state.inputs[port - 1].signal = int(bool(body["present"]))
                self._record("sim", f"signal input {port} -> {bool(body['present'])}")
            elif kind == "push":
                await self.push(str(body["line"]))
            else:
                raise ValueError("type must be one of cable, signal, push")
        except (KeyError, ValueError, TypeError) as exc:
            raise web.HTTPBadRequest(text=f"bad event: {exc}") from exc
        return web.json_response(self.state.to_dict())

    async def _c_get_log(self, request: web.Request) -> web.Response:
        entries = list(self.log)
        channel = request.query.get("channel")
        if channel:
            entries = [e for e in entries if e["channel"] == channel]
        limit = int(request.query.get("limit", "0") or 0)
        if limit > 0:
            entries = entries[-limit:]
        return web.json_response(entries)

    async def _c_clear_log(self, request: web.Request) -> web.Response:
        self.log.clear()
        return web.json_response([])
