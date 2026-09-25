"""Routing: one input to one output, one input to every output."""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    Response,
    Scenario,
    WsEvent,
    act,
)

from ._paths import CONTROL, HUB_CORE, STATUS, WEB_CORE, WEB_DRAWERS, WEB_GRID

# Seed routing (tools/simulator/states/default.json): [2, 2, 1, 1, 5, 6, 1, 1]

SCENARIOS = [
    Scenario(
        id="routing.switch_one",
        title="Route input 6 to output 1; nothing else changes",
        features=("F-MTX-001",),
        client_features={"api": ("F-API-005", "F-API-033"), "browser": ("F-UI-002",)},
        clients=("api", "browser"),
        writes=("routing",),
        action=act("route", input=6, output=1),
        expect=(
            Response(status=200),
            Device("outputs[0].source", equals=6),
            DeviceUnchanged(allow=("outputs[0].source", "routing[0]")),
            CommandSent("video switch", {"source": [1, 6]}, count=1),
            # /api/switch broadcasts; the grid's own route is checked in routing.grid_notifies_other_clients.
            WsEvent("switch", {"input": 6, "output": 1}, clients=("api",)),
            Hub("/api/status", "data.routing.1", equals=6),
        ),
        observe=("Does the display on output 1 now show the source connected to input 6?",),
        covers=(*HUB_CORE, *CONTROL, *STATUS, *WEB_CORE, *WEB_GRID),
    ),
    Scenario(
        id="routing.route_all",
        title="Route input 4 to every output",
        features=("F-MTX-002",),
        client_features={"api": ("F-API-005", "F-API-034"), "browser": ("F-UI-004",)},
        clients=("api", "browser"),
        writes=("routing",),
        action=act("route_all", input=4),
        expect=(
            Response(status=200),
            Device("routing", equals=[4] * 8),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
            CommandSent("video switch", {"source": [0, 4]}, count=1),
            WsEvent("switch_all", {"input": 4}),
            Hub("/api/status", "data.routing.8", equals=4),
        ),
        observe=("Do all connected displays now show the source connected to input 4?",),
        covers=(*HUB_CORE, *CONTROL, *STATUS, *WEB_CORE, *WEB_DRAWERS),
    ),
    Scenario(
        id="routing.grid_notifies_other_clients",
        title="Routing from the matrix grid is announced to the other open clients (WebSocket)",
        features=("F-UI-024",),
        clients=("browser",),
        writes=("routing",),
        action=act("route", input=5, output=1),
        expect=(
            Device("outputs[0].source", equals=5),
            WsEvent("switch", {"input": 5, "output": 1}, finding="VAL-05",
                    note="the grid posts /api/output/1/source, which does not broadcast"),
        ),
        observe=("Does the display on output 1 now show the source connected to input 5?",),
        covers=(*HUB_CORE, *CONTROL, *WEB_CORE, *WEB_GRID),
    ),
]
