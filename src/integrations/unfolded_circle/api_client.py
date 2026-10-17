"""Compatibility methods for UC factories over the shared HTTP hub client."""

from collections.abc import Callable
from typing import Any

from hub.integrations import HubClientHttp, HubEvent


class MatrixApiClient(HubClientHttp):
    """Keep the existing UC client API while using the common transport contract."""

    async def get_health(self) -> dict[str, Any]:
        return await self._get("/api/health")

    async def get_status(self) -> dict[str, Any]:
        return await self._get("/api/status")

    async def get_full_status(self) -> dict[str, Any]:
        return await self._get("/api/status/full")

    async def get_presets(self) -> dict[str, Any]:
        return await self._get("/api/presets")

    async def get_inputs(self) -> dict[str, Any]:
        return await self._get("/api/inputs")

    async def get_outputs(self) -> dict[str, Any]:
        return await self._get("/api/outputs")

    async def get_cable_status(self) -> dict[str, Any]:
        return await self._get("/api/status/cables")

    async def get_cec_status(self) -> dict[str, Any]:
        return await self._get("/api/status/cec")

    async def switch_input(self, input_num: int, output_num: int) -> bool:
        return await self.switch(input_num, output_num)

    async def switch_all_outputs(self, input_num: int) -> bool:
        return await self.switch(input_num)

    async def power_on(self) -> bool:
        return await self.power(True)

    async def power_off(self) -> bool:
        return await self.power(False)

    async def next_input(self, output: int = 1) -> bool:
        return await self.cycle_input("next", output)

    async def previous_input(self, output: int = 1) -> bool:
        return await self.cycle_input("previous", output)

    async def send_cec_input(self, input_num: int, command: str) -> bool:
        return await self.send_cec("input", input_num, command)

    async def send_cec_output(self, output_num: int, command: str) -> bool:
        return await self.send_cec("output", output_num, command)

    async def get_cec_commands(self) -> dict[str, Any]:
        return await self._get("/api/cec/commands")

    async def get_scenes(self) -> list[dict[str, Any]]:
        return (await self._get("/api/scenes")).get("scenes", [])

    async def recall_scene(self, scene_id: str, *, passcode: str | None = None) -> bool:
        return (await self.run_action("scene", scene_id, passcode=passcode)).get("success") is True

    async def get_profiles(self) -> list[dict[str, Any]]:
        return (await self._get("/api/profiles")).get("profiles", [])

    async def recall_profile(self, profile_id: str, *, passcode: str | None = None) -> bool:
        return (await self.run_action("profile", profile_id, passcode=passcode)).get("success") is True

    async def set_output_hdcp(self, output: int, mode: str) -> bool:
        return (await self._post(f"/api/output/{output}/hdcp", {"mode": mode})).get("success") is True

    async def set_output_hdr(self, output: int, mode: str) -> bool:
        return (await self._post(f"/api/output/{output}/hdr", {"mode": mode})).get("success") is True

    async def set_output_scaler(self, output: int, mode: str) -> bool:
        return (await self._post(f"/api/output/{output}/scaler", {"mode": mode})).get("success") is True

    async def set_output_arc(self, output: int, enabled: bool) -> bool:
        return (await self._post(f"/api/output/{output}/arc", {"enabled": enabled})).get("success") is True

    async def set_output_mute(self, output: int, muted: bool) -> bool:
        return (await self._post(f"/api/output/{output}/mute", {"muted": muted})).get("success") is True

    async def get_device_settings(self) -> dict[str, Any]:
        return await self._get("/api/device-settings")

    async def set_input_name(self, input_num: int, name: str) -> bool:
        return (await self._post(f"/api/input/{input_num}/name", {"name": name})).get("success") is True

    async def set_output_name(self, output_num: int, name: str) -> bool:
        return (await self._post(f"/api/output/{output_num}/name", {"name": name})).get("success") is True

    def on_status_update(self, callback: Callable[[dict], Any]) -> Callable[[], None]:
        """Subscribe to normalized HubEvents with the legacy dictionary callback."""

        def forward(event: HubEvent) -> Any:
            return callback({"event": event.kind, "data": event.data})

        unsubscribe = self.subscribe(forward)
        if not hasattr(self, "_legacy_callbacks"):
            self._legacy_callbacks: dict[Callable, Callable[[], None]] = {}
        old = self._legacy_callbacks.get(callback)
        if old is not None:
            old()
        self._legacy_callbacks[callback] = unsubscribe
        return unsubscribe

    def remove_status_callback(self, callback: Callable[[dict], Any]) -> None:
        unsubscribe = getattr(self, "_legacy_callbacks", {}).pop(callback, None)
        if unsubscribe is not None:
            unsubscribe()

    async def close(self) -> None:
        await super().close()
        if hasattr(self, "_legacy_callbacks"):
            self._legacy_callbacks.clear()
