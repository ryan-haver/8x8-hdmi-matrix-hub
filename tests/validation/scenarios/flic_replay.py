"""Exact generated Flic requests and Node-stub SDK replay; simulator only.

These scenarios do not claim a physical Flic Hub, SDK version or button was
observed. Common device expectations are reused across client implementations.
"""

from dataclasses import replace

from tools.validate.model import CommandSent, Device, DeviceUnchanged, Hub, NoCommand, Response, Scenario, act

from . import cec, macros, power, presets, profiles, routing

_COVERS = (
    "tools/validate/clients/flic.py", "tools/validate/clients/flic_driver.mjs",
    "web/js/components/integrations-drawer.js", "src/hub/runtime", "run.py",
)
_BASE = {s.id: s for module in (cec, macros, power, presets, profiles, routing) for s in module.SCENARIOS}


def _replay(source, suffix, feature, *, generated=True, **kwargs):
    original = _BASE[source]
    return replace(
        original, id=f"flic.{suffix}", title=f"Flic replay: {original.title}",
        features=(feature, "F-FLIC-010") if generated else (feature,),
        client_features={}, clients=("flic",),
        targets=("sim",), observe=(), covers=(*original.covers, *_COVERS),
        notes="Actual drawer generator runs in Node; manual variants are labeled in request evidence. "
              "Physical Flic SDK/buttons and physical CEC effects remain unobserved.", **kwargs,
    )


SCENARIOS = [
    _replay("presets.recall", "preset", "F-FLIC-001"),
    _replay("power.standby", "power_off", "F-FLIC-002"),
    _replay("power.wake", "power_on", "F-FLIC-002"),
    _replay("cec.input_power_on", "source_power", "F-FLIC-003"),
    _replay("cec.output_volume_up", "display_volume", "F-FLIC-005"),
    _replay("profiles.recall_routing", "profile", "F-FLIC-006"),
    _replay("profiles.recall_needs_passcode", "profile_pin_refused", "F-FLIC-006"),
    _replay("macros.run_volume_up", "manual_macro", "F-FLIC-006", generated=False),
    _replay("macros.run_rejected", "manual_macro_refused", "F-FLIC-006", generated=False),
    _replay("routing.route_all", "all_outputs", "F-FLIC-008"),
    Scenario(
        id="flic.cycle_next", title="Generated Flic cycle request advances output 1 from input 2 to 3",
        features=("F-FLIC-004", "F-FLIC-010"), clients=("flic",), targets=("sim",),
        writes=("routing",), action=act("cycle_input", direction="next", output=1),
        expect=(Response(status=200), Device("outputs[0].source", equals=3),
                CommandSent("video switch", {"source": [1, 3]}, count=1),
                DeviceUnchanged(allow=("outputs[0].source", "routing[0]"))), covers=_COVERS,
    ),
    Scenario(
        id="flic.cec_output_navigation_refused", title="Generated output navigation request reaches REST and is refused",
        kind="failure", features=("F-FLIC-005", "F-FLIC-010"), clients=("flic",), targets=("sim",),
        action=act("cec_output", output=2, command="up"),
        expect=(Response(status=400), NoCommand("*"), DeviceUnchanged()), covers=_COVERS,
    ),
    Scenario(
        id="flic.unknown_profile", title="Generated request for an unknown profile is refused without matrix writes",
        kind="failure", features=("F-FLIC-006",), clients=("flic",), targets=("sim",),
        action=act("profile_recall", profile_id="missing_flic_validation_profile"),
        expect=(Response(status=404), NoCommand("*"), DeviceUnchanged()), covers=_COVERS,
    ),
    Scenario(
        id="flic.register", title="Documented Flic registration updates the button catalog",
        features=("F-FLIC-007",), clients=("flic",), targets=("sim",),
        action=act("flic_register", buttons=[{"name": "Validation", "bdaddr": "80:e4:da:70:00:01", "serial": "sim"}]),
        expect=(Response(status=200), Hub("/api/integrations/flic/buttons", "data.buttons[0].name",
                                        equals="Validation"), NoCommand("*"), DeviceUnchanged()),
        covers=(*_COVERS, "src/rest_api/integrations.py", "src/hub/integrations/flic"),
        cleanup=(act("request", method="POST", path="/api/integrations/flic/register", json={"buttons": [
            {"name": "Couch Button", "bdaddr": "80:e4:da:70:00:01", "serial": "BG12-A00001"},
        ]}),),
    ),
]

_BUTTON = {"name": "Validation", "bdaddr": "80:e4:da:70:00:01", "serial": "sim-sdk"}
_REGISTRY = {_BUTTON["bdaddr"]: _BUTTON}

for _gesture, _event in (
    ("single", {"is_single_click": True}),
    ("double", {"is_double_click": True}),
    ("hold", {"is_hold": True}),
):
    SCENARIOS.append(_replay(
        "routing.switch_one", f"sdk_{_gesture}", "F-FLIC-009",
        action=act("flic_sdk_event", button_identifier="Validation", gesture=_gesture,
                   target_type="switch_output", input_num=6, output_num=1,
                   button_registry=_REGISTRY,
                   event={"bdaddr": _BUTTON["bdaddr"], **_event}),
    ))

SCENARIOS.append(Scenario(
    id="flic.sdk_filter_mismatch", title="Actual generated SDK ignores a mismatching button name",
    features=("F-FLIC-009",), clients=("flic",), targets=("sim",),
    action=act("flic_sdk_event", button_identifier="Other Button", target_type="switch_output",
               input_num=6, output_num=1, button_registry=_REGISTRY,
               event={"bdaddr": _BUTTON["bdaddr"], "is_single_click": True}),
    expect=(NoCommand("*"), DeviceUnchanged()), covers=_COVERS,
))

SCENARIOS.append(_replay(
    "routing.switch_one", "sdk_startup_and_click", "F-FLIC-009",
    action=act("flic_sdk_event", button_identifier="Validation", target_type="switch_output",
               input_num=6, output_num=1, run_startup_registration=True,
               buttons=[_BUTTON], button_registry=_REGISTRY,
               event={"bdaddr": _BUTTON["bdaddr"], "is_single_click": True}),
    cleanup=(act("request", method="POST", path="/api/integrations/flic/register", json={"buttons": [
        {"name": "Couch Button", "bdaddr": "80:e4:da:70:00:01", "serial": "BG12-A00001"},
    ]}),),
))

for _side, _number in (("left", 0), ("right", 1)):
    SCENARIOS.append(_replay(
        "routing.switch_one", f"sdk_duo_{_side}", "F-FLIC-009",
        action=act("flic_sdk_event", button_type="duo", button_identifier=_BUTTON["bdaddr"],
                   gesture=f"{_side}_single", target_type="switch_output", input_num=6, output_num=1,
                   button_registry=_REGISTRY, event={"bdaddr": _BUTTON["bdaddr"], "is_single_click": True,
                                                      "button_number": _number}),
    ))

for _gesture, _direction, _cycle, _input in (("rotate_cw", 1, "next", 3), ("rotate_ccw", -1, "previous", 1)):
    SCENARIOS.append(Scenario(
        id=f"flic.sdk_twist_{_cycle}", title=f"Actual generated Twist {_gesture} callback cycles output 1",
        features=("F-FLIC-004", "F-FLIC-009"), clients=("flic",), targets=("sim",), writes=("routing",),
        action=act("flic_sdk_event", button_type="twist", button_identifier="Validation", gesture=_gesture,
                   target_type="cycle_input", cycle_dir=_cycle, output_num=1, button_registry=_REGISTRY,
                   event={"event_name": "buttonRotate", "bdaddr": _BUTTON["bdaddr"], "direction": _direction}),
        expect=(Response(status=200), Device("outputs[0].source", equals=_input),
                CommandSent("video switch", {"source": [1, _input]}, count=1),
                DeviceUnchanged(allow=("outputs[0].source", "routing[0]"))), covers=_COVERS,
    ))
