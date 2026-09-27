"""Scenario DSL, levels and state-path helpers."""

from __future__ import annotations

import pytest

from tools.validate.clients.api import rest_call
from tools.validate.clients.base import NotSupportedError
from tools.validate.clients.ha import HomeAssistantClient
from tools.validate.clients.uc import RemoteClient
from tools.validate.model import (
    INTENTS,
    ClientState,
    Device,
    Level,
    Scenario,
    act,
    diff_states,
    flatten,
    level_for,
    path_matches,
    resolve,
)
from tools.validate.scenarios import discover, select

STATE = {"system": {"power": 1}, "outputs": [{"source": 2}, {"source": 5}], "data": {"routing": {"1": 6}}}


def test_levels():
    assert Level.parse("v2") is Level.V2 and str(Level.V3) == "V3"
    assert level_for("sim", "api") is Level.V2
    assert level_for("sim", "browser") is Level.V3
    assert level_for("hardware", "api") is Level.V4
    with pytest.raises(ValueError):
        Level.parse("V9")


def test_resolve_paths():
    assert resolve(STATE, "system.power") == 1
    assert resolve(STATE, "outputs[1].source") == 5
    assert resolve(STATE, "outputs[-1].source") == 5
    assert resolve(STATE, "data.routing.1") == 6
    for bad in ("outputs[5].source", "system.nope", "outputs.source"):
        with pytest.raises(KeyError):
            resolve(STATE, bad)


def test_flatten_diff_and_globs():
    assert flatten(STATE)["outputs[0].source"] == 2
    after = {"system": {"power": 0}, "outputs": [{"source": 2}, {"source": 6}], "data": {"routing": {"1": 6}}}
    assert diff_states(STATE, after) == [
        {"path": "outputs[1].source", "before": 5, "after": 6},
        {"path": "system.power", "before": 1, "after": 0},
    ]
    assert path_matches("outputs[3].source", "outputs[*].source")
    assert path_matches("outputs[3].source", "outputs[3]")
    assert path_matches("routing[0]", "routing")
    assert not path_matches("outputs[3].hdcp", "outputs[*].source")


def _scenario(**kw):
    base = dict(id="x.y", title="t", features=("F-MTX-001",), action=act("route", input=1, output=1),
                expect=(Device("outputs[0].source", equals=1),), covers=("src/x.py",))
    base.update(kw)
    return Scenario(**base)


def test_scenario_validation():
    assert _scenario().features_for("browser") == ("F-MTX-001",)
    assert _scenario(client_features={"browser": ("F-UI-002",)}).features_for("browser") == ("F-MTX-001", "F-UI-002")
    for bad in (dict(id="Bad Id"), dict(features=()), dict(features=("MTX-1",)), dict(covers=()),
                dict(action=act("teleport")), dict(faults={"drop_http": True})):
        with pytest.raises(ValueError):
            _scenario(**bad)
    # faults are fine when the scenario is simulator-only
    assert _scenario(faults={"drop_http": True}, targets=("sim",)).faults
    # so is a change made behind the hub's back (the runner patches the simulator)
    change = act("device_change", event={"type": "signal", "port": 3, "present": True})
    with pytest.raises(ValueError):
        _scenario(action=change)
    assert _scenario(action=change, targets=("sim",)).action.intent == "device_change"


def test_known_findings_collects_check_links():
    sc = _scenario(expect=(Device("a", equals=1, finding="BE-12"),), findings=("VAL-01",))
    assert sc.known_findings == {"BE-12", "VAL-01"}


def test_every_scenario_is_well_formed():
    scenarios = discover()
    assert len(scenarios) >= 10
    kinds = {s.kind for s in scenarios.values()}
    assert kinds == {"happy", "failure"}
    assert any("browser" in s.clients for s in scenarios.values())
    for sc in scenarios.values():
        assert sc.action.intent in INTENTS
        assert sc.expect, sc.id
        if "hardware" in sc.targets and sc.kind == "happy" and sc.writes:
            assert sc.observe, f"{sc.id} changes the matrix on hardware but asks the operator nothing"


def test_select_by_feature_and_id():
    scenarios = discover()
    assert {s.id for s in select(scenarios, features=["F-UI-002"])} == {"routing.switch_one"}
    assert [s.id for s in select(scenarios, ids=["presets.recall"])] == ["presets.recall"]
    with pytest.raises(SystemExit):
        select(scenarios, ids=["nope.nope"])


def test_api_client_maps_every_intent():
    samples = {
        "route": {"input": 1, "output": 2}, "route_all": {"input": 1}, "preset_recall": {"preset": 1},
        "preset_save": {"preset": 1}, "preset_rename": {"preset": 1, "name": "x"}, "matrix_power": {"on": True},
        "output_mute": {"output": 1, "muted": True}, "output_setting": {"output": 1, "setting": "hdcp", "body": {"mode": 1}},
        "cec_input": {"input": 1, "command": "power_on"}, "cec_output": {"output": 1, "command": "power_on"},
        "profile_recall": {"profile_id": "p"}, "request": {"method": "GET", "path": "/api/health"},
    }
    # uc_command / ha_* are the Remote's and Home Assistant's own actions, as `request` is the api client's;
    # device_change is carried out by the runner itself.
    assert set(samples) == set(INTENTS) - {"uc_command", "ha_service", "ha_config_flow", "ha_reconfigure",
                                           "device_change"}
    for intent, params in samples.items():
        method, path, _ = rest_call(act(intent, **params))
        assert method in ("GET", "POST") and path.startswith("/api/")
    with pytest.raises(NotSupportedError):
        rest_call(act("uc_command", entity_id="button.preset_1", cmd_id="push"))
    assert rest_call(act("route_all", input=3)) == ("POST", "/api/switch", {"input": 3})


def test_ha_client_intents_exist_and_it_observes():
    assert HomeAssistantClient.intents <= set(INTENTS)
    assert HomeAssistantClient.observes and not RemoteClient.observes
    assert "request" not in HomeAssistantClient.intents
    assert ClientState("switch.power", equals="on", before="off").describe() == \
        "client shows switch.power == 'on' (was 'off')"


class _StubHa(HomeAssistantClient):
    """The ha client's intent mapping, without a container: entity ids and select options are stubbed."""

    def __init__(self) -> None:
        super().__init__()
        self.entry_id = "entry1"

    async def _entity_id(self, key: str) -> str:
        return f"{key.split('.')[0]}.hdmi_matrix_{key.split('.', 1)[1]}"

    async def _state(self, entity_id: str) -> dict:
        return {"state": "AppleTV", "attributes": {"options": ["PS3", "AppleTV", "Computer", "Switch", "Shield", "PS5"]}}


@pytest.mark.parametrize(
    ("action", "call"),
    [
        (act("route", input=6, output=1),
         ("select", "select_option", {"entity_id": "select.hdmi_matrix_output_1_source", "option": "PS5"})),
        (act("preset_recall", preset=3), ("button", "press", {"entity_id": "button.hdmi_matrix_preset_3"})),
        (act("matrix_power", on=False), ("switch", "turn_off", {"entity_id": "switch.hdmi_matrix_power"})),
        (act("output_mute", output=2, muted=True), ("switch", "turn_on", {"entity_id": "switch.hdmi_matrix_output_2_mute"})),
        (act("output_setting", output=3, setting="enable", body={"enabled": False}),
         ("switch", "turn_off", {"entity_id": "switch.hdmi_matrix_output_3_stream"})),
        (act("cec_output", output=1, command="power_on"),
         ("hdmi_matrix", "send_cec_command", {"port_type": "output", "port_num": 1, "command": "power_on"})),
        (act("ha_service", domain="hdmi_matrix", service="recall_preset", data={"preset": 2}, target="entry"),
         ("hdmi_matrix", "recall_preset", {"preset": 2, "config_entry_id": "entry1"})),
    ],
)
def test_ha_client_maps_intents_to_service_calls(action, call):
    import asyncio

    assert asyncio.run(_StubHa()._service_call(action)) == call


def test_ha_client_rejects_what_home_assistant_cannot_do():
    import asyncio

    with pytest.raises(NotSupportedError):
        asyncio.run(_StubHa()._service_call(act("output_setting", output=1, setting="hdcp", body={"mode": 1})))
    with pytest.raises(NotSupportedError):
        asyncio.run(_StubHa()._service_call(act("route", input=8, output=1)))  # only 6 options stubbed


def test_uc_client_intents_exist_and_need_the_uc_hub():
    assert RemoteClient.intents <= set(INTENTS)
    assert "request" not in RemoteClient.intents
    assert RemoteClient.hub_mode == "uc"
