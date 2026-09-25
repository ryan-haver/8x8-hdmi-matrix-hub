"""The device side of a scenario run: what the matrix *really* did.

* :class:`SimDevice` talks to the simulator's control API (``/_sim/*``): full
  ground-truth state, command log, fault injection.
* :class:`HardwareDevice` talks to a real BK-808 (or anything that speaks its
  HTTP API) directly, **independently of the hub under test**: read-only
  readback normalised to the simulator's state shape, a snapshot, and a
  restore that writes back only the fields that differ and verifies them.

Both return state documents with the same keys (``system``, ``inputs[]``,
``outputs[]``, ``ext_audio``, ``presets[].name``, and a derived ``routing``),
so scenario expectations such as ``outputs[0].source`` work on either target.
"""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
from pathlib import Path
from typing import Any

import aiohttp

_LOG = logging.getLogger("validate.device")

ROOT = Path(__file__).resolve().parents[2]
SEED_STATE = ROOT / "tools" / "simulator" / "states" / "default.json"

#: Fields compared/restored on hardware, per state domain.
OUTPUT_FIELDS = ("source", "stream", "hdcp", "hdr", "scaler", "arc", "audio_mute", "name")
#: Domains a hardware restore can put back. ``presets`` cannot be restored
#: without re-routing live outputs (see DI-4). ``cec`` enable is restored with
#: the 8-element array form of ``set cec index`` (captured working on V1.10.01;
#: the single-port form is rejected, BE-13/HIL-10). Output settings, EDID and
#: ext-audio use the device web interface's commands (WP-A4 part 2); their
#: values here are the device's own codes, as read.
RESTORABLE_DOMAINS = frozenset({"routing", "outputs", "power", "names", "system", "edid", "ext_audio", "cec"})


def with_routing(state: dict[str, Any]) -> dict[str, Any]:
    """Add the derived ``routing`` list (output N -> input) to a state document."""
    doc = dict(state)
    doc["routing"] = [o.get("source") for o in state.get("outputs", [])]
    return doc


class SimDevice:
    """Simulator control API client (``http://host:port/_sim``)."""

    kind = "sim"
    has_log = True

    def __init__(self, control_url: str) -> None:
        self.control_url = control_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None
        self._seed = json.loads(SEED_STATE.read_text(encoding="utf-8"))

    async def __aenter__(self) -> SimDevice:
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._session:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        assert self._session is not None, "use 'async with SimDevice(...)'"
        return self._session

    async def _call(self, method: str, path: str, body: Any = None) -> Any:
        async with self.session.request(method, f"{self.control_url}{path}", json=body) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(f"simulator {method} {path}: HTTP {resp.status}: {text[:300]}")
            return json.loads(text) if text else None

    async def health(self) -> dict[str, Any]:
        return await self._call("GET", "/_sim/health")

    async def state(self) -> dict[str, Any]:
        return with_routing(await self._call("GET", "/_sim/state"))

    async def reset(self, patch: dict[str, Any] | None = None) -> None:
        """Seed state, no faults, empty log.

        Deliberately not ``POST /_sim/reset``: that also drops the hub's login
        session and the hub never logs in again (BE-04). ``PUT /_sim/state``
        keeps sessions (same approach as tests/e2e/support/stack.ts).
        """
        await self._call("PUT", "/_sim/state", self._seed)
        if patch:
            await self._call("PATCH", "/_sim/state", patch)
        await self._call("DELETE", "/_sim/faults")
        await self._call("DELETE", "/_sim/log")

    async def set_faults(self, faults: dict[str, Any]) -> None:
        await self._call("POST", "/_sim/faults", faults)

    async def clear_faults(self) -> None:
        await self._call("DELETE", "/_sim/faults")

    async def log(self) -> list[dict[str, Any]]:
        return list(await self._call("GET", "/_sim/log"))

    async def info(self) -> dict[str, Any]:
        st = await self._call("GET", "/_sim/state")
        return {
            "model": st["device"].get("model"),
            "firmware_version": st["device"].get("firmware_version"),
            "web_version": st["device"].get("web_version"),
        }


class HardwareDevice:
    """Direct, hub-independent access to a real BK-808 over its HTTP API.

    Reads use the documented read comheads. Writes are used **only** by
    :meth:`restore`, which the runner calls only when ``--allow-writes`` was
    given, to put back fields a scenario changed.
    """

    kind = "hardware"
    has_log = False

    def __init__(self, host: str, port: int = 443, *, https: bool = True, user: str = "Admin",
                 password: str = "admin", verify_tls: bool = False) -> None:
        scheme = "https" if https else "http"
        self.url = f"{scheme}://{host}:{port}/cgi-bin/instr"
        self.host, self.port = host, port
        self._user, self._password = user, password
        self._ssl: ssl.SSLContext | bool = ssl.create_default_context() if verify_tls else False
        self._session: aiohttp.ClientSession | None = None
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> HardwareDevice:
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8))
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._session:
            await self._session.close()

    async def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        assert self._session is not None, "use 'async with HardwareDevice(...)'"
        async with self._session.post(self.url, json=payload, ssl=self._ssl) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"device HTTP {resp.status} for {payload.get('comhead')!r}")
            try:
                return json.loads(text)
            except ValueError as exc:
                raise RuntimeError(f"device sent non-JSON for {payload.get('comhead')!r}: {text[:120]!r}") from exc

    async def login(self) -> None:
        resp = await self._post({"comhead": "login", "user": self._user, "password": self._password})
        if resp.get("result") not in (1, "1", "success", True):
            raise RuntimeError(f"device login rejected: {resp}")

    async def read(self, comhead: str, **extra: Any) -> dict[str, Any]:
        async with self._lock:
            payload = {"comhead": comhead, "language": 0, **extra}
            resp = await self._post(payload)
            if resp.get("comhead") != comhead or "result" in resp and resp.get("result") in (0, "0"):
                # Not logged in (or session expired): log in once and retry.
                await self.login()
                resp = await self._post(payload)
            return resp

    async def info(self) -> dict[str, Any]:
        st = await self.read("get status")
        return {
            "model": st.get("model"),
            "firmware_version": st.get("version"),
            "web_version": st.get("webversion"),
            "host": self.host,
        }

    async def state(self) -> dict[str, Any]:
        """Normalised readback (same keys as the simulator state document)."""
        video = await self.read("get video status")
        outs = await self.read("get output status")
        ins = await self.read("get input status")
        cec = await self.read("get cec status")
        system = await self.read("get system status")
        exa = await self.read("get ext-audio status")

        def col(doc: dict[str, Any], key: str, i: int, default: Any = None) -> Any:
            arr = doc.get(key) or []
            return arr[i] if i < len(arr) else default

        in_names = video.get("allinputname") or ins.get("inname") or []
        out_names = video.get("alloutputname") or outs.get("alloutputname") or []
        inputs = [
            {
                "name": in_names[i] if i < len(in_names) else None,
                "edid": col(ins, "edid", i),
                "signal": col(ins, "inactive", i),
                "cec_enabled": col(cec, "inputindex", i),
            }
            for i in range(8)
        ]
        outputs = [
            {
                "name": out_names[i] if i < len(out_names) else None,
                "source": col(video, "allsource", i),
                "connected": col(outs, "allconnect", i),
                "stream": col(outs, "allout", i),
                "hdcp": col(outs, "allhdcp", i),
                "hdr": col(outs, "allhdr", i),
                "scaler": col(outs, "allscaler", i),
                "arc": col(outs, "allarc", i),
                "audio_mute": col(outs, "allaudiomute", i),
                "cec_enabled": col(cec, "outputindex", i),
                "ext_audio_enabled": col(exa, "allout", i),
                "ext_audio_source": col(exa, "allsource", i),
            }
            for i in range(8)
        ]
        return with_routing(
            {
                "system": {
                    "power": video.get("power", system.get("power")),
                    "beep": system.get("beep"),
                    "panel_lock": system.get("lock"),
                },
                "inputs": inputs,
                "outputs": outputs,
                "ext_audio": {"mode": exa.get("mode")},
                "presets": [{"name": n} for n in (video.get("allname") or [])],
            }
        )

    # ------------------------------------------------------------ restore

    async def _write(self, payload: dict[str, Any]) -> bool:
        async with self._lock:
            resp = await self._post(payload)
            if resp.get("comhead") != payload["comhead"]:
                await self.login()
                resp = await self._post(payload)
            return resp.get("result") in (1, "1", None)

    def _restore_commands(self, snap: dict[str, Any], now: dict[str, Any], domains: set[str]) -> list[dict[str, Any]]:
        cmds: list[dict[str, Any]] = []
        if "power" in domains and snap["system"].get("power") != now["system"].get("power"):
            cmds.append({"comhead": "set poweronoff", "language": 0, "power": snap["system"]["power"]})
        if "system" in domains:
            if snap["system"].get("beep") != now["system"].get("beep"):
                cmds.append({"comhead": "set beep", "language": 0, "beep": snap["system"]["beep"]})
            if snap["system"].get("panel_lock") != now["system"].get("panel_lock"):
                cmds.append({"comhead": "set panel lock", "language": 0, "lock": snap["system"]["panel_lock"]})
        for i in range(8):
            s, n = snap["outputs"][i], now["outputs"][i]
            o = i + 1
            if "routing" in domains and s["source"] != n["source"]:
                cmds.append({"comhead": "video switch", "language": 0, "source": [o, s["source"]]})
            if "outputs" in domains:
                for key, comhead, field in (("stream", "tx stream", "out"), ("hdcp", "tx hdcp", "hdcp"),
                                            ("hdr", "set hdr conversion", "hdr"),
                                            ("scaler", "set video scaler", "scaler"), ("arc", "set arc", "arc"),
                                            ("audio_mute", "set output audio mute", "mute")):
                    if s[key] != n[key]:
                        cmds.append({"comhead": comhead, "language": 0, field: [o, s[key]]})
            if "names" in domains and s["name"] != n["name"]:
                cmds.append({"comhead": "set output name", "language": 0, "name": s["name"], "index": o})
            if "ext_audio" in domains:
                if s["ext_audio_enabled"] != n["ext_audio_enabled"]:
                    cmds.append({"comhead": "set ext-audio out", "language": 0, "out": [o, s["ext_audio_enabled"]]})
                if s["ext_audio_source"] != n["ext_audio_source"]:
                    cmds.append({"comhead": "ext-audio switch", "language": 0, "source": [o, s["ext_audio_source"]]})
        for i in range(8):
            s, n = snap["inputs"][i], now["inputs"][i]
            if "names" in domains and s["name"] != n["name"]:
                cmds.append({"comhead": "set input name", "language": 0, "name": s["name"], "index": i + 1})
            if "edid" in domains and s["edid"] != n["edid"]:
                cmds.append({"comhead": "set edid", "language": 0, "edid": [i + 1, s["edid"]]})
        if "ext_audio" in domains and snap["ext_audio"].get("mode") != now["ext_audio"].get("mode"):
            cmds.append({"comhead": "set ext-audio mode", "language": 0, "mode": snap["ext_audio"]["mode"]})
        if "cec" in domains:
            cin = [p["cec_enabled"] for p in snap["inputs"]]
            cout = [o["cec_enabled"] for o in snap["outputs"]]
            if cin != [p["cec_enabled"] for p in now["inputs"]] or cout != [o["cec_enabled"] for o in now["outputs"]]:
                cmds.append({"comhead": "set cec index", "language": 0, "inputindex": cin, "outputindex": cout})
        return cmds

    async def restore(self, snapshot: dict[str, Any], domains: set[str]) -> dict[str, Any]:
        """Write back every restorable field that differs from ``snapshot``; verify by readback."""
        unrestorable = set(domains) - RESTORABLE_DOMAINS
        now = await self.state()
        cmds = self._restore_commands(snapshot, now, set(domains) & RESTORABLE_DOMAINS)
        sent = []
        for cmd in cmds:
            ok = await self._write(cmd)
            sent.append({"command": cmd, "ok": ok})
        after = await self.state()
        remaining = self._restore_commands(snapshot, after, set(domains) & RESTORABLE_DOMAINS)
        return {
            "commands": sent,
            "verified": not remaining,
            "remaining_differences": remaining,
            "unrestorable_domains": sorted(unrestorable),
        }
