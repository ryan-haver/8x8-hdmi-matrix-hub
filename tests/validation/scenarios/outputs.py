"""Output settings: audio mute (happy path and a write the matrix rejects)."""

from tools.validate.model import CommandSent, Device, DeviceUnchanged, Hub, Response, Scenario, WsEvent, act

from ._paths import HUB_CORE, OUTPUTS

SCENARIOS = [
    Scenario(
        id="outputs.audio_mute",
        title="Mute the audio of output 2",
        features=("F-MTX-007",),
        client_features={"api": ("F-API-036",)},
        writes=("outputs",),
        action=act("output_mute", output=2, muted=True),
        expect=(
            Response(status=200),
            Device("outputs[1].audio_mute", equals=1),
            DeviceUnchanged(allow=("outputs[1].audio_mute",)),
            CommandSent("set output mute", {"output": 2, "mute": 1}, count=1),
            WsEvent("audio_mute", {"output": 2, "muted": True}),
            Hub("/api/status/outputs", "data.outputs[1].muted", equals=True),
        ),
        observe=("Is the audio on output 2 now muted?",),
        covers=(*HUB_CORE, *OUTPUTS),
    ),
    Scenario(
        id="outputs.audio_mute_rejected",
        title="The matrix rejects a mute command: the hub must report the failure",
        kind="failure",
        features=("F-REL-008",),
        targets=("sim",),
        faults={"reject_writes": True},
        action=act("output_mute", output=2, muted=True),
        expect=(
            Response(min_status=400, json={"success": False}, finding="BE-12"),
            Device("outputs[1].audio_mute", equals=0),
            DeviceUnchanged(),
            Hub("/api/status/outputs", "data.outputs[1].muted", equals=False),
        ),
        covers=(*HUB_CORE, *OUTPUTS),
    ),
]
