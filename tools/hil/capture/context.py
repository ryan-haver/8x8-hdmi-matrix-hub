"""Shared state of one capture run: clients, output folder, records, restore."""

from __future__ import annotations

import asyncio
import platform
import subprocess
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from . import catalog as cmd
from .assumptions import BY_ID
from .fixtures import RESTORE_LOG, CaptureWriter, firmware_folder_name, utc_now
from .snapshot import Snapshot, diff, lcd_line, plan_restore
from .transport import HttpRecorder, TelnetRecorder, is_data_response

TOOL_VERSION = "1.0"
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = "tests/fixtures/device/{firmware}"


class CaptureError(Exception):
    """A fatal problem (device unreachable, login rejected, aborted)."""


class RestoreError(CaptureError):
    """The device could not be put back into its original state."""


@dataclass
class Options:
    host: str
    port: int = 443
    telnet_port: int = 23
    tls: bool = True
    user: str = "Admin"
    password: str = ""
    out: str = DEFAULT_OUT
    firmware: str | None = None
    mode: str = "read"
    telnet: bool = True
    http_timeout: float = 5.0
    telnet_idle: float = 1.0
    telnet_timeout: float = 5.0
    banner_idle: float = 1.5
    redact: list[str] = field(default_factory=list)
    yes: bool = False
    # write mode
    i_understand: bool = False
    only: list[str] = field(default_factory=list)
    skip: list[str] = field(default_factory=list)
    include: list[str] = field(default_factory=list)
    test_output: int = 8
    test_input: int = 8
    test_preset: int = 8
    cec_output: int = 1
    cec_input: int = 1
    push_grace: float = 0.3
    reboot_wait: float = 180.0
    # probe mode
    idle_waits: list[float] = field(default_factory=list)
    push_seconds: float = 30.0

    def public(self) -> dict[str, Any]:
        """Options as stored in the manifest (no secrets)."""
        doc = asdict(self)
        doc.pop("password", None)
        doc["redact"] = [f"<{len(v)} chars>" for v in self.redact]
        return doc


class Console:
    """Prints progress and asks questions. Tests replace ``ask``."""

    def __init__(self, *, interactive: bool | None = None, stream: Any = None) -> None:
        self.interactive = sys.stdin.isatty() if interactive is None else interactive
        self.stream = stream

    def print(self, *parts: Any) -> None:
        print(*parts, file=self.stream or sys.stdout, flush=True)

    def ask(self, prompt: str) -> str | None:
        """Return the answer, or None when there is nobody to ask."""
        if not self.interactive:
            return None
        try:
            return input(prompt)
        except EOFError:
            return None


def _git_sha() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


class Capture:
    """One capture run against one device."""

    def __init__(self, opts: Options, console: Console | None = None) -> None:
        self.opts = opts
        self.console = console or Console()
        self.http = HttpRecorder(opts.host, opts.port, tls=opts.tls, timeout=opts.http_timeout)
        self.telnet: TelnetRecorder | None = None
        self.writer: CaptureWriter | None = None
        self.device: dict[str, Any] = {}
        self.records: dict[str, dict[str, Any]] = {}
        self._pending: list[tuple[str, dict[str, Any]]] = []
        self.answers: dict[str, list[str]] = {}
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.started_at = utc_now()
        #: LCD status line -> code, learned by the LCD write test
        self.lcd_modes: dict[str, int] = {}
        #: extra clients to close at the end
        self._extra: list[Any] = []
        #: test hook: called after every write-mode step (may raise)
        self.after_step: Callable[[str, int], Any] | None = None
        #: comheads the device left unanswered (timeout) in this run; later
        #: snapshots skip them (V1.10.01 never answers ``get routing status``,
        #: HIL-01, and each try costs the whole HTTP timeout)
        self.unanswered: set[str] = set()

    def note_unanswered(self, comhead: str, exchange: dict[str, Any]) -> bool:
        """Remember ``comhead`` if ``exchange`` timed out; True if it did."""
        if (exchange.get("error") or {}).get("type") != "TimeoutError":
            return False
        if comhead not in self.unanswered:
            self.unanswered.add(comhead)
            self.warnings.append(f"no answer to {comhead!r} within {self.opts.http_timeout:g} s; "
                                 "not sent again in this run")
        return True

    # ------------------------------------------------------------ lifecycle

    @property
    def secrets(self) -> list[str]:
        """The password (exact) and every ``--redact`` value in any letter case.

        The device prints the same value in different cases: the MAC address is
        upper case over HTTP but lower case in the Telnet ``status`` dump, where
        an exact match let it through (HIL Session 1, ``telnet/status``).
        """
        variants = [v for s in self.opts.redact if s for v in (s, s.lower(), s.upper())]
        return list(dict.fromkeys(s for s in [self.opts.password, *variants] if s))

    def track(self, client: Any) -> Any:
        self._extra.append(client)
        return client

    async def close(self) -> None:
        for client in [self.http, self.telnet, *self._extra]:
            if client is not None:
                try:
                    await client.close()
                except Exception:  # noqa: BLE001 - best effort on shutdown
                    pass

    # --------------------------------------------------------------- records

    def add(self, record_id: str, record: dict[str, Any]) -> None:
        """Store a record (buffered until the output folder is known)."""
        record.setdefault("mode", self.opts.mode)
        record.setdefault("captured_at", utc_now())
        answers = list(dict.fromkeys(record.get("answers") or []))
        record["answers"] = answers
        for aid in answers:
            if aid not in BY_ID:
                raise ValueError(f"unknown assumption id {aid!r} in {record_id}")
            ids = self.answers.setdefault(aid, [])
            if record_id not in ids:
                ids.append(record_id)
        self.records[record_id] = record
        if self.writer is None:
            self._pending.append((record_id, record))
        else:
            self.writer.write_record(record_id, record)

    def log_restore(self, entry: dict[str, Any]) -> None:
        entry = {"t": utc_now(), **entry}
        if self.writer is not None:
            self.writer.append_jsonl(RESTORE_LOG, entry)

    # -------------------------------------------------------------- identify

    async def login(self, client: HttpRecorder | None = None, *, role: str = "login",
                    password: str | None = None) -> dict[str, Any]:
        client = client or self.http
        return await client.post(
            cmd.login(self.opts.user, self.opts.password if password is None else password), role=role,
            label="login",
        )

    async def read_json(self, comhead: str, *, client: HttpRecorder | None = None, role: str = "snapshot",
                        relogin: bool = True) -> Any:
        """A read's JSON; logs in again once if the answer carries no data (session expired)."""
        http = client or self.http
        if comhead in self.unanswered:
            return None
        for attempt in (1, 2):
            ex = await http.post(cmd.snapshot_payload(comhead), role=role)
            if self.note_unanswered(comhead, ex):
                return None
            resp = ex.get("response") or {}
            doc = resp.get("json") if resp.get("status") == 200 else None
            if is_data_response(doc) or not relogin or attempt == 2 or ex.get("error"):
                return doc
            await self.login(http, role="relogin")
        return None

    async def ensure_session(self) -> bool:
        """Make sure the main client can read; log in again if not."""
        if is_data_response(await self.read_json("get system status", relogin=False)):
            return True
        await self.login(role="relogin")
        return is_data_response(await self.read_json("get system status", relogin=False))

    async def identify(self) -> dict[str, Any]:
        """Log in, read the device identity, and open the output folder.

        Returns the login exchange. Raises :class:`CaptureError` when the
        device is unreachable or the credentials are rejected.
        """
        login_ex = await self.login()
        if login_ex.get("error"):
            raise CaptureError(f"cannot reach {self.http.base_url}: {login_ex['error']['message']}")
        status = await self.read_json("get status")
        network = await self.read_json("get network")
        if not is_data_response(status) and not is_data_response(network):
            body = (login_ex.get("response") or {}).get("body_text", "")
            raise CaptureError(
                "logged in but reads return no data: wrong user/password? "
                f"(login answered {body[:120]!r})"
            )
        status = status if isinstance(status, dict) else {}
        network = network if isinstance(network, dict) else {}
        device: dict[str, Any] = {
            "model": status.get("model") or network.get("model"),
            "mcu_version": status.get("version"),
            "web_version": status.get("webversion"),
            "hostname": status.get("hostname") or network.get("hostname"),
        }
        for doc in (status, network):
            for key, value in doc.items():
                if "version" in key.lower() and key not in ("version", "webversion"):
                    device[f"http_{key}"] = value
        self.device = {k: v for k, v in device.items() if v is not None}
        self.open_output()
        return login_ex

    def open_output(self) -> Path:
        folder = self.opts.firmware or firmware_folder_name(self.device)
        out = self.opts.out.replace("{firmware}", folder).replace("<firmware>", folder)
        root = Path(out)
        if not root.is_absolute():
            root = Path.cwd() / root
        self.writer = CaptureWriter(root, self.secrets)
        for record_id, record in self._pending:
            self.writer.write_record(record_id, record)
        self._pending.clear()
        return root

    async def open_telnet(self) -> dict[str, Any] | None:
        """Connect the main Telnet client; returns the banner exchange."""
        if not self.opts.telnet:
            return None
        self.telnet = TelnetRecorder(
            self.opts.host, self.opts.telnet_port, idle=self.opts.telnet_idle,
            timeout=self.opts.telnet_timeout, banner_idle=self.opts.banner_idle,
            connect_timeout=max(self.opts.telnet_timeout, 0.5),
        )
        banner = await self.telnet.connect()
        if banner.get("error"):
            self.warnings.append(f"Telnet {self.opts.host}:{self.opts.telnet_port} unavailable: "
                                 f"{banner['error']['message']}")
            self.telnet = None
        else:
            text = (banner.get("response") or {}).get("text", "")
            for line in text.splitlines():
                if "version" in line.lower():
                    self.device.setdefault("telnet_banner_version", line.strip())
                    break
        return banner

    # -------------------------------------------------------------- snapshot

    async def snapshot(self, *, with_lcd: bool = False) -> Snapshot:
        reads: dict[str, Any] = {}
        for comhead in cmd.SNAPSHOT_READS:
            doc = await self.read_json(comhead)
            if comhead not in self.unanswered:  # a read the firmware lacks is not an "unreadable" state
                reads[comhead] = doc
        lcd = None
        if with_lcd:
            status = await self.telnet_status()
            lcd = lcd_line(status) if status is not None else None
        return Snapshot.from_reads(reads, lcd)

    async def telnet_status(self) -> str | None:
        if self.telnet is None:
            return None
        if not self.telnet.connected:
            await self.reconnect_telnet()
            if self.telnet is None or not self.telnet.connected:
                return None
        ex = await self.telnet.command("status", role="snapshot")
        resp = ex.get("response") or {}
        return resp.get("text") if not ex.get("error") else None

    async def reconnect_telnet(self) -> None:
        if self.telnet is None:
            return
        await self.telnet.close()
        banner = await self.telnet.connect()
        if banner.get("error"):
            self.warnings.append("Telnet reconnect failed")

    # --------------------------------------------------------------- restore

    async def restore_to(self, target: Snapshot, *, reason: str, attempts: int = 2) -> list[list[Any]]:
        """Put the device back to ``target``; returns the differences left.

        Every write is logged to ``write/restore-log.jsonl`` as it happens, so
        a crash mid-restore still leaves a record of what was done.
        """
        with_lcd = target.lcd_line is not None
        remaining: list[list[Any]] = []
        for attempt in range(1, attempts + 1):
            await self.ensure_session()
            current = await self.snapshot(with_lcd=with_lcd)
            actions, warnings = plan_restore(current, target, self.lcd_modes)
            for w in warnings:
                if w not in self.warnings:
                    self.warnings.append(w)
                    self.console.print(f"  ! {w}")
            if not actions:
                remaining = _fatal(diff(target, current)) + _unreadable(current)
                if not remaining:
                    break
                continue
            for action in actions:
                ex = await self.http.post(action.payload, role="restore")
                resp = ex.get("response") or {}
                self.log_restore({
                    "reason": reason, "attempt": attempt, "field": action.field, "port": action.port,
                    "from": action.before, "to": action.target, "note": action.note,
                    "payload": action.payload, "status": resp.get("status"), "result": resp.get("json"),
                    "error": ex.get("error"),
                })
            verify = await self.snapshot(with_lcd=with_lcd)
            remaining = _fatal(diff(target, verify)) + _unreadable(verify)
            self.log_restore({"reason": reason, "attempt": attempt, "verified": not remaining,
                              "remaining": remaining})
            if not remaining:
                break
        return remaining

    # --------------------------------------------------------------- summary

    def run_info(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "mode": self.opts.mode,
            "started_at": self.started_at,
            "finished_at": utc_now(),
            "tool_version": TOOL_VERSION,
            "hub_commit": _git_sha(),
            "host_os": platform.platform(),
            "python": platform.python_version(),
            "target": {"host": self.opts.host, "port": self.opts.port, "telnet_port": self.opts.telnet_port,
                       "tls": self.opts.tls, "user": self.opts.user},
            "options": self.opts.public(),
            "records": sorted(self.records),
            "answers": {k: sorted(v) for k, v in sorted(self.answers.items())},
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            **(extra or {}),
        }

    def summary_lines(self) -> list[str]:
        lines = ["", "Assumptions (tools/simulator ASSUMPTION(HIL-A)) this capture provides evidence for:"]
        if not self.answers:
            lines.append("  (none)")
        width = max((len(a) for a in self.answers), default=10)
        for aid in sorted(self.answers):
            files = self.answers[aid]
            shown = ", ".join(files[:3]) + (f" (+{len(files) - 3} more)" if len(files) > 3 else "")
            lines.append(f"  {aid:<{width}}  {shown}")
        missing = [a for a in BY_ID if a not in self.answers]
        if missing:
            lines.append("")
            lines.append("Not covered by this run (other modes / opt-in groups):")
            for aid in missing:
                lines.append(f"  {aid:<{width}}  [{', '.join(BY_ID[aid].modes)}]")
        lines.append("")
        lines.append("Check them against the simulator with:")
        root = self.writer.root if self.writer else "<out>"
        lines.append(f"  python -m tools.simulator --golden {root} --report")
        return lines


def _fatal(differences: list[list[Any]]) -> list[list[Any]]:
    """Differences that count as "not restored".

    Preset names cannot be restored by any command, and the LCD timeout is
    cosmetic; both are reported as warnings instead.
    """
    return [d for d in differences if d[0] not in ("preset_name", "lcd_line")]


def _unreadable(snap: Snapshot) -> list[list[Any]]:
    """A snapshot with failed reads cannot prove anything was restored."""
    return [["unreadable", None, None, snap.errors]] if snap.errors else []


async def wait_until(predicate: Callable[[], Any], timeout: float, interval: float = 2.0) -> bool:
    """Poll an async predicate until it returns truthy or ``timeout`` passes."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if await predicate():
            return True
        await asyncio.sleep(interval)
    return False
