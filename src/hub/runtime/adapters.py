"""Typed commands and a stable legacy facade over the sole active client."""

from __future__ import annotations

import asyncio
import inspect
from copy import deepcopy


class TransactionLock:
    """Reentrant within one task so compound actions can call the facade safely."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._owner = None
        self._depth = 0

    async def __aenter__(self):
        task = asyncio.current_task()
        if self._owner is not task:
            await self._lock.acquire()
            self._owner = task
        self._depth += 1
        return self

    async def __aexit__(self, *_):
        self._depth -= 1
        if not self._depth:
            self._owner = None
            self._lock.release()


class NullMatrix:
    """Unconfigured Remote setup has no transport or reconnect supervisor."""

    host = ""
    port = 443
    connected = False
    telnet_connected = False
    password = None
    login_failure = None

    async def connect(self):
        return False

    async def disconnect(self):
        pass


class CommandProvider:
    def __init__(self, runtime):
        self.runtime = runtime
        self.cycle_locks = {port: asyncio.Lock() for port in range(1, 10)}

    def snapshot(self):
        return self.runtime.snapshot()

    async def switch(self, input_num, output_num=None):
        return await self.runtime.command(self.runtime.service.switch, input_num, output_num)

    async def power(self, on):
        return await self.runtime.command(self.runtime.service.set_power, on)

    async def send_cec(self, target_kind, port, command):
        if target_kind not in {"input", "output"}:
            raise ValueError("target_kind must be input or output")
        return await self.runtime.protocol("send_cec", command, port, is_output=target_kind == "output")

    async def recall_preset(self, preset):
        return await self.runtime.command(self.runtime.service.recall_preset, preset)

    async def save_preset(self, preset):
        return await self.runtime.command(self.runtime.service.save_preset, preset)

    async def cycle_input(self, direction, output_num=1):
        if direction not in {"next", "previous"}:
            raise ValueError("direction must be next or previous")
        async with self.cycle_locks[output_num]:
            async with self.runtime.transaction:
                current = self.runtime.snapshot().routing.get(output_num)
                if current is None:
                    return False
                target = (current - 1 + (1 if direction == "next" else -1)) % 8 + 1
                return await self.switch(target, output_num)


class MatrixFacade:
    """Managers retain this identity across address changes; reads use the service cache."""

    def __init__(self, runtime):
        self.runtime = runtime

    @property
    def connected(self):
        return self.runtime.service.connected

    @property
    def configured(self):
        return self.runtime.address is not None

    @property
    def host(self):
        return self.runtime.address.host if self.runtime.address else None

    @property
    def port(self):
        return self.runtime.address.port if self.runtime.address else 443

    async def connect(self):
        return await self.runtime.connect()

    async def disconnect(self):
        async with self.runtime.transaction:
            await self.runtime.service.disconnect()

    async def switch_input(self, input_num, output_num):
        return await self.runtime.commands.switch(input_num, output_num)

    async def switch_input_to_all(self, input_num):
        return await self.runtime.commands.switch(input_num)

    route_input_to_all_outputs = switch_input_to_all

    async def power_on(self):
        return await self.runtime.commands.power(True)

    async def power_off(self):
        return await self.runtime.commands.power(False)

    async def recall_preset(self, preset):
        return await self.runtime.commands.recall_preset(preset)

    async def save_preset(self, preset):
        return await self.runtime.commands.save_preset(preset)

    async def set_input_name(self, port, name):
        return await self.runtime.command(self.runtime.service.rename_port, "input", port, name)

    async def set_output_name(self, port, name):
        return await self.runtime.command(self.runtime.service.rename_port, "output", port, name)

    async def set_preset_name(self, port, name):
        return await self.runtime.command(self.runtime.service.rename_preset, port, name)

    async def get_current_input_for_output(self, port):
        return self.runtime.snapshot().routing.get(port)

    async def get_status(self, force_refresh=False):
        if force_refresh:
            await self.runtime.refresh()
        return self.runtime.service.raw_snapshot().get(
            "status", {"connected": self.connected, "host": self.host, "port": self.port}
        )

    async def _read(self, key, force_refresh=False):
        if force_refresh:
            await self.runtime.refresh()
        return self.runtime.service.raw_snapshot().get(key)

    async def get_video_status(self):
        return await self._read("video")

    async def get_input_status(self, force_refresh=False):
        return await self._read("inputs", force_refresh)

    async def get_output_status(self, force_refresh=False):
        return await self._read("outputs", force_refresh)

    async def get_all_cable_status(self, force_refresh=False):
        return await self._read("cables", force_refresh) or {"inputs": {}, "outputs": {}}

    async def get_output_names(self):
        return self.runtime.snapshot().output_names

    async def get_all_input_names(self):
        return self.runtime.snapshot().input_names

    async def get_preset_names(self):
        return list(self.runtime.snapshot().preset_names.values())

    async def get_full_status(self):
        from orei_matrix import api_output_settings, per_output

        async with self.runtime.operation():
            result = await self.get_status()
            outputs = await self.get_output_status() or {}
            inputs = await self.get_input_status() or {}
            if outputs:
                settings = api_output_settings(outputs)
                result.update(
                    outputs_connected=outputs.get("allconnect", []),
                    output_scaler=settings["scaler"],
                    output_hdr=settings["hdr"],
                    output_hdcp=settings["hdcp"],
                    output_arc=per_output(outputs.get("allarc")),
                    output_enabled=per_output(outputs.get("allout")),
                    output_muted=per_output(outputs.get("allaudiomute")),
                )
            if inputs:
                result.update(input_edid=inputs.get("edid", []), inputs_inactive=inputs.get("inactive", []))
            cec = await self.runtime.protocol("get_cec_status")
            system = await self.runtime.protocol("get_system_status")
            info = await self.runtime.protocol("get_device_info")
            if cec:
                result.update(
                    cec_inputs_enabled=cec.get("inputindex", []), cec_outputs_enabled=cec.get("outputindex", [])
                )
            if system:
                result.update(
                    beep_enabled=system.get("beep") == 1,
                    panel_locked=system.get("lock") == 1,
                    system_mode=system.get("mode"),
                )
            if info:
                result.update(
                    firmware_version=info.get("version"),
                    web_version=info.get("webversion"),
                    model=info.get("model"),
                    mac_address=info.get("macaddress"),
                )
            return result

    def __getattr__(self, name):
        # Diagnostic protocol reads and uncommon writes still use the sole client.
        value = getattr(self.runtime.service.client, name)
        if not inspect.iscoroutinefunction(value):
            return deepcopy(value) if isinstance(value, (dict, list)) else value

        async def invoke(*args, **kwargs):
            return await self.runtime.protocol(name, *args, **kwargs)

        return invoke
