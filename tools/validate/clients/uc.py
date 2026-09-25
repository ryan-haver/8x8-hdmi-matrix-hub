"""The ``uc`` client: a scripted Remote 3 driving the hub's Unfolded Circle integration (WP-B1, UC-21).

The runner starts the hub the way it ships with the integration enabled (``run.py``
legacy mode, ``src/driver.py``; see ``tools/validate/stack.py``), and this client
talks to the integration WebSocket exactly as a Remote does
(``tools/uc_remote_sim.py``, per the pinned Integration-API spec): it connects,
authenticates, sends ``connect``, subscribes every available entity, and then
turns each intent into the entity command a Remote user would trigger:

=============  ===================================================================
route          ``media_player.output_N`` ``select_source`` with the input's name
               from the entity's source list (what the Remote shows)
preset_recall  ``button.preset_N`` ``push``
matrix_power   ``switch.matrix_power`` ``on`` / ``off``
cec_input      ``remote.input_N_cec`` ``send_cmd`` with the simple command
cec_output     ``remote.output_N_cec`` ``send_cmd`` with the simple command
uc_command     any entity command (``entity_id``, ``cmd_id``, ``params``)
=============  ===================================================================

The driver closing the connection (UC-01) is a result, not an infrastructure
error: it is reported with its close code, and the next action reconnects.
"""

from __future__ import annotations

import time
from typing import Any

import aiohttp

from tools.uc_remote_sim import SPEC_VERSION, ConnectionClosedError, UcRemoteSim

from ..model import Action
from .base import ActionResult, Client, HubInfo, NotSupportedError


def _cec_command(name: str) -> str:
    """Intent command names are the REST spelling (``power_on``); the Remote's simple commands are ``POWER_ON``."""
    return name.upper()


class RemoteClient(Client):
    name = "uc"
    hub_mode = "uc"
    intents = frozenset({"route", "preset_recall", "matrix_power", "cec_input", "cec_output", "uc_command"})

    def __init__(self) -> None:
        super().__init__()
        self.hub: HubInfo | None = None
        self.remote: UcRemoteSim | None = None
        self.connections = 0
        self.driver_version: dict[str, Any] = {}

    async def start(self, hub: HubInfo) -> None:
        if not hub.uc_url:
            raise RuntimeError("the 'uc' client needs a hub started by the runner with the UC integration "
                               "(--hub-url points at an external hub)")
        self.hub = hub
        await self._session()

    async def stop(self) -> None:
        if self.remote is not None:
            await self.remote.close()
            self.remote = None

    async def _session(self) -> UcRemoteSim:
        """The Remote's connection; (re)connects after the driver dropped it or the hub restarted."""
        if self.remote is not None and not self.remote.closed:
            return self.remote
        if self.remote is not None:
            await self.remote.close()
        assert self.hub is not None and self.hub.uc_url
        remote = UcRemoteSim(self.hub.uc_url)
        await remote.connect()
        await remote.attach()
        self.connections += 1
        self.driver_version = (await remote.get_driver_version()).get("msg_data") or {}
        self.remote = remote
        return remote

    async def _source_name(self, remote: UcRemoteSim, output: int, input_num: int) -> str:
        """The name the Remote lists for ``input_num`` in the output's source list."""
        state = await remote.entity_state(f"media_player.output_{output}") or {}
        sources = state.get("source_list") or []
        if not 1 <= input_num <= len(sources):
            raise NotSupportedError(f"input {input_num} is not in the source list {sources}")
        return str(sources[input_num - 1])

    async def _command(self, remote: UcRemoteSim, action: Action) -> tuple[str, str, dict[str, Any] | None]:
        p = action.params
        match action.intent:
            case "route":
                name = await self._source_name(remote, p["output"], p["input"])
                return f"media_player.output_{p['output']}", "select_source", {"source": name}
            case "preset_recall":
                return f"button.preset_{p['preset']}", "push", None
            case "matrix_power":
                return "switch.matrix_power", "on" if p["on"] else "off", None
            case "cec_input":
                return f"remote.input_{p['input']}_cec", "send_cmd", {"command": _cec_command(p["command"])}
            case "cec_output":
                return f"remote.output_{p['output']}_cec", "send_cmd", {"command": _cec_command(p["command"])}
            case "uc_command":
                return p["entity_id"], p["cmd_id"], p.get("params")
        raise NotSupportedError(action.intent)

    async def perform(self, action: Action) -> ActionResult:
        if action.intent not in self.intents:
            raise NotSupportedError(action.intent)
        result = ActionResult(intent=action.intent, ok=False)
        t0 = time.perf_counter()
        remote = await self._session()
        if remote.closed:  # pragma: no cover - _session reconnects
            raise RuntimeError("no connection to the integration")
        entity_id, cmd_id, params = await self._command(remote, action)
        since = remote.mark()
        # Evidence record shape (evidence.schema.json "requests"): method = the Integration-API message,
        # path = the entity, body = msg_data as sent.
        request: dict[str, Any] = {
            "method": "entity_command", "path": entity_id, "via": "uc integration websocket",
            "body": {"entity_id": entity_id, "cmd_id": cmd_id, **({"params": params} if params is not None else {})},
        }
        try:
            resp = await remote.entity_command(entity_id, cmd_id, params)
            result.status = int(resp.get("code", 0))
            result.ok = result.status == 200
            request.update(status=result.status, response=resp)
            result.steps.append(f"entity_command {entity_id} {cmd_id}" + (f" {params}" if params else "")
                                + f" -> {result.status}")
        except ConnectionClosedError as exc:
            result.error = str(exc)
            request.update(status=None, closed=exc.code)
            result.steps.append(f"entity_command {entity_id} {cmd_id}" + (f" {params}" if params else "")
                                + f" -> connection closed by the driver (code {exc.code})")
        except TimeoutError:
            result.error = "no response from the driver"
            request.update(status=None)
            result.steps.append(f"entity_command {entity_id} {cmd_id} -> no response")
        request["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        result.requests.append(request)
        # What the Remote was told right after the command (first poll excluded: too slow to wait for).
        result.body = {
            "response": request.get("response"),
            "close_code": remote.close_code if remote.closed else None,
            "entity_changes": remote.entity_changes(since)[:20],
        }
        result.elapsed_ms = request["elapsed_ms"]
        return result

    def environment(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "client": "tools/uc_remote_sim.py (scripted Remote 3)",
            "integration_api_spec": SPEC_VERSION,
            "driver": self.driver_version,
            "connections": self.connections,
            "aiohttp": aiohttp.__version__,
        }
