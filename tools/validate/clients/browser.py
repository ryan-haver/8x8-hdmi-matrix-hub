"""The ``browser`` client: a real Chromium driving the shipped web UI (Playwright).

The browser work happens in ``browser_driver.mjs`` (Node, the repo's pinned
``@playwright/test``); this class talks to it over JSON lines on
stdin/stdout. In CI it runs inside the pinned Playwright container, like the
``ui`` job. Locally it needs ``npm ci`` and ``npx playwright install chromium``.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import time
from pathlib import Path
from typing import Any

from ..model import Action
from .base import ActionResult, Client, HubInfo, NotSupportedError

DRIVER = Path(__file__).with_name("browser_driver.mjs")
ROOT = Path(__file__).resolve().parents[3]


class BrowserClient(Client):
    name = "browser"
    intents = frozenset({"route", "route_all", "preset_recall", "preset_rename"})

    def __init__(self) -> None:
        super().__init__()
        self._proc: asyncio.subprocess.Process | None = None
        self._next_id = 0
        self._browser_version = ""

    async def _rpc(self, op: str, **payload: Any) -> dict[str, Any]:
        assert self._proc is not None and self._proc.stdin and self._proc.stdout
        self._next_id += 1
        msg = {"id": self._next_id, "op": op, **payload}
        self._proc.stdin.write((json.dumps(msg) + "\n").encode())
        await self._proc.stdin.drain()
        while True:
            line = await asyncio.wait_for(self._proc.stdout.readline(), timeout=120)
            if not line:
                err = b""
                if self._proc.stderr:
                    err = await self._proc.stderr.read()
                raise RuntimeError(f"browser driver exited: {err.decode(errors='replace')[-2000:]}")
            try:
                reply = json.loads(line)
            except ValueError:
                continue  # stray output from Playwright
            if reply.get("id") == self._next_id:
                if not reply.get("ok"):
                    raise RuntimeError(f"browser driver: {reply.get('error')}")
                return reply.get("result") or {}

    async def start(self, hub: HubInfo) -> None:
        node = shutil.which("node")
        if not node:
            raise RuntimeError("the browser client needs Node.js (>= 20) on PATH")
        if not (ROOT / "node_modules" / "@playwright" / "test").exists():
            raise RuntimeError("the browser client needs the npm dev dependencies: run `npm ci` in the repo root")
        self._proc = await asyncio.create_subprocess_exec(
            node, str(DRIVER),
            cwd=str(ROOT),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=16 * 1024 * 1024,
        )
        result = await self._rpc(
            "start",
            baseURL=hub.base_url,
            forwardedFor=hub.forwarded_for,
            artifacts=str(hub.artifacts_dir) if hub.artifacts_dir else None,
        )
        self._browser_version = result.get("browser", "")

    async def perform(self, action: Action) -> ActionResult:
        if not self.supports(action):
            raise NotSupportedError(action.intent)
        t0 = time.perf_counter()
        res = await self._rpc("perform", intent=action.intent, params=action.params,
                              label=self.context.get("label", action.intent),
                              forwardedFor=self.context.get("forwarded_for"),
                              artifacts=self.context.get("artifacts_dir"))
        if res.get("unsupported"):
            raise NotSupportedError(action.intent)
        result = ActionResult(intent=action.intent, ok=False)
        result.status = res.get("status")
        result.error = res.get("error")
        result.ok = result.error is None and result.status is not None and 200 <= result.status < 300
        result.steps = list(res.get("steps", []))
        result.screenshots = list(res.get("screenshots", []))
        result.requests = [
            {"method": c["method"], "path": c["path"], "body": c.get("body"), "status": c["status"], "via": "page"}
            for c in res.get("apiCalls", [])
        ]
        result.body = {
            "page_api_requests": res.get("apiRequestCount"),
            "page_errors": res.get("pageErrors", []),
            "console_errors": res.get("consoleErrors", []),
        }
        result.elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return result

    async def stop(self) -> None:
        if self._proc is None:
            return
        try:
            await asyncio.wait_for(self._rpc("stop"), timeout=15)
        except (RuntimeError, TimeoutError, ConnectionError):
            pass
        if self._proc.returncode is None:
            self._proc.kill()
        await self._proc.wait()
        self._proc = None

    def environment(self) -> dict[str, Any]:
        return {"name": self.name, "browser": self._browser_version, "driver": "Playwright (@playwright/test, package-lock.json)"}
