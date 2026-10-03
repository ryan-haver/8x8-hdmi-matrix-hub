"""External audio REST controls with independent simulator state/readback.

Mode codes and routing are software proof only. Physical audio and binding
behavior require HIL-09 hardware proof; source writes are exercised in mode 2.
"""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    NoProtocolWarnings,
    Response,
    Scenario,
    act,
)

from ._paths import HUB_CORE

_COVERS = (*HUB_CORE, "src/rest_api/audio.py", "src/device_codes.py",
           "tests/validation/scenarios/external_audio.py")
_STATUS = "/api/status/ext-audio"


def _invalid(sid, feature, path, body):
    return Scenario(
        id=f"audio.{sid}", title=f"{sid}: reject invalid request before any device write",
        features=(feature,), targets=("sim",), kind="failure",
        sim_state={"ext_audio": {"mode": 2}},
        action=act("request", method="POST", path=path, json=body),
        expect=(Response(status=400, json={"success": False}), NoCommand("*"),
                DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
    )


def _refused(sid, feature, path, body, command, payload, state):
    return Scenario(
        id=f"audio.{sid}", title=f"{sid}: device refusal returns failure and preserves audio state",
        features=(feature,), targets=("sim",), kind="failure",
        sim_state=state, faults={"reject_writes": True},
        action=act("request", method="POST", path=path, json=body),
        expect=(Response(status=500, json={"success": False}),
                CommandSent(command, payload, count=2), DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
        notes="Persistent result=0 causes one re-login/retry, then HTTP failure.",
    )


SCENARIOS = [
    Scenario(
        id="audio.mode_catalog", title="External audio mode catalog exposes all three device codes",
        features=("F-MTX-015",), targets=("sim",),
        action=act("request", method="GET", path="/api/ext-audio/modes"),
        expect=(Response(status=200, json={"success": True, "data": {"modes": {
            "0": "Bind to Input", "1": "Bind to Output", "2": "Matrix Mode"}}}),
                NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
    ),
]

# Literal expected codes/names keep the oracle independent of production constants.
for mode, name in ((0, "Bind to Input"), (1, "Bind to Output"), (2, "Matrix Mode")):
    SCENARIOS.append(Scenario(
        id=f"audio.mode_{mode}", title=f"External audio mode {mode}: {name} with raw and API readback",
        features=("F-MTX-015",), targets=("sim",), writes=("ext_audio",),
        sim_state={"ext_audio": {"mode": (mode + 1) % 3}},
        action=act("request", method="POST", path="/api/ext-audio/mode", json={"mode": mode}),
        expect=(Response(status=200, json={"success": True, "data": {"mode": mode, "mode_name": name}}),
                CommandSent("set ext-audio mode", {"mode": mode}, count=1),
                Device("ext_audio.mode", equals=mode),
                Hub(_STATUS, "data.mode", equals=mode), Hub(_STATUS, "data.mode_name", equals=name),
                Hub(_STATUS, "data.raw.mode", equals=mode),
                DeviceUnchanged(allow=("ext_audio.mode",)), NoProtocolWarnings()),
        covers=_COVERS,
    ))

for sid, body in (("negative", {"mode": -1}), ("high", {"mode": 3}),
                  ("missing", {}), ("noninteger", {"mode": "invalid"})):
    SCENARIOS.append(_invalid(f"mode_{sid}", "F-MTX-015", "/api/ext-audio/mode", body))
SCENARIOS.append(_refused("mode_refused", "F-MTX-015", "/api/ext-audio/mode", {"mode": 2},
                         "set ext-audio mode", {"mode": 2}, {"ext_audio": {"mode": 0}}))

for output in range(1, 9):
    idx = output - 1
    field = f"outputs[{idx}].ext_audio_enabled"
    for enabled in (False, True):
        code = int(enabled)
        SCENARIOS.append(Scenario(
            id=f"audio.enable_{output}_{code}", title=f"External audio output {output}: enabled={enabled}",
            features=("F-MTX-016",), targets=("sim",), writes=("outputs",),
            sim_state={"ext_audio": {"mode": 2}, "outputs": {str(idx): {"ext_audio_enabled": 1 - code}}},
            action=act("request", method="POST", path=f"/api/ext-audio/{output}/enable", json={"enabled": enabled}),
            expect=(Response(status=200, json={"success": True, "data": {"output": output, "enabled": enabled}}),
                    CommandSent("set ext-audio out", {"out": [output, code]}, count=1),
                    Device(field, equals=code),
                    Hub(_STATUS, f"data.outputs[{idx}].enabled", equals=enabled),
                    Hub(_STATUS, f"data.raw.allout[{idx}]", equals=code),
                    DeviceUnchanged(allow=(field,)), NoProtocolWarnings()),
            covers=_COVERS,
        ))

    # Every output/input combination catches index swaps and boundary mapping.
    for source in range(1, 9):
        field = f"outputs[{idx}].ext_audio_source"
        SCENARIOS.append(Scenario(
            id=f"audio.source_{output}_{source}", title=f"External audio output {output}: route input {source} in matrix mode",
            features=("F-MTX-017",), targets=("sim",), writes=("outputs",),
            sim_state={"ext_audio": {"mode": 2},
                       "outputs": {str(idx): {"ext_audio_source": source % 8 + 1}}},
            action=act("request", method="POST", path=f"/api/ext-audio/{output}/source", json={"input": source}),
            expect=(Response(status=200, json={"success": True, "data": {"output": output, "input": source}}),
                    CommandSent("ext-audio switch", {"source": [output, source]}, count=1),
                    Device(field, equals=source), Device("ext_audio.mode", equals=2),
                    Hub(_STATUS, f"data.outputs[{idx}].source", equals=source),
                    Hub(_STATUS, f"data.raw.allsource[{idx}]", equals=source),
                    DeviceUnchanged(allow=(field,)), NoProtocolWarnings()),
            covers=_COVERS,
            notes="REST exposes HDMI inputs 1-8; ARC source codes 9-16 and physical audio are outside this proof.",
        ))

for output in (0, 9):
    SCENARIOS.append(_invalid(f"enable_port_{output}", "F-MTX-016",
                              f"/api/ext-audio/{output}/enable", {"enabled": True}))
    SCENARIOS.append(_invalid(f"source_port_{output}", "F-MTX-017",
                              f"/api/ext-audio/{output}/source", {"input": 8}))
SCENARIOS.extend([
    _invalid("enable_missing", "F-MTX-016", "/api/ext-audio/8/enable", {}),
    _refused("enable_refused", "F-MTX-016", "/api/ext-audio/8/enable", {"enabled": True},
             "set ext-audio out", {"out": [8, 1]},
             {"ext_audio": {"mode": 2}, "outputs": {"7": {"ext_audio_enabled": 0}}}),
])
for sid, body in (("low", {"input": 0}), ("high", {"input": 9}),
                  ("missing", {}), ("noninteger", {"input": "invalid"})):
    SCENARIOS.append(_invalid(f"source_{sid}", "F-MTX-017", "/api/ext-audio/8/source", body))
SCENARIOS.append(_refused("source_refused", "F-MTX-017", "/api/ext-audio/8/source", {"input": 8},
                         "ext-audio switch", {"source": [8, 8]},
                         {"ext_audio": {"mode": 2}, "outputs": {"7": {"ext_audio_source": 1}}}))
