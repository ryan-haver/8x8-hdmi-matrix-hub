"""Live updates: changes made behind the hub's back reach every client (docs/api/WEBSOCKET.md).

The runner changes the simulator directly (front panel, cable, source signal,
a rename by another controller, a power loss) and nothing goes through the hub.
The hub's own event stream has to notice and announce it (UC-17): the runner's
/ws observer checks the event (and every message against the contract schema),
and the browser client checks what a /ui page and a /kiosk page that stay open
show.
Those two pages get later changes only over the WebSocket: after they load,
their status reads are stripped of all matrix state
(tools/validate/clients/browser_driver.mjs).

Seed (tools/simulator/states/default.json): routing [2, 2, 1, 1, 5, 6, 1, 1];
input 3 "Computer" has no signal and no cable; output 1 "TV" is connected and
shows input 2 (signal).
"""

from tools.validate.model import ClientState, Device, Hub, Scenario, WsEvent, act

from ._paths import HUB_CORE, STATUS, WEB_CORE, WEB_GRID

KIOSK = ("web/kiosk.html", "web/js/websocket.js")
BROWSER = ("browser",)

SCENARIOS = [
    Scenario(
        id="live.front_panel_route",
        title="Routing changed on the matrix itself reaches every client once",
        features=("F-MTX-031", "F-REL-012", "F-API-040", "F-UI-024", "F-KIO-010"),
        clients=BROWSER,
        targets=("sim",),
        action=act("device_change", patch={"outputs": {"1": {"source": 6}}}),
        expect=(
            Device("outputs[1].source", equals=6),
            WsEvent("routing_change", {"output": 2, "input": 6, "input_name": "PS5"}, timeout=12),
            Hub("/api/status", "data.routing.2", equals=6),
            ClientState("ui.route.2", before=2, equals=6, timeout=15),
            ClientState("kiosk.route.2", before=2, equals=6, timeout=15),
        ),
        covers=(*HUB_CORE, *STATUS, *WEB_CORE, *WEB_GRID, *KIOSK),
    ),
    Scenario(
        id="live.input_signal",
        title="A source switched on is shown as signal present",
        features=("F-MTX-031", "F-API-040", "F-UI-024", "F-KIO-010"),
        clients=BROWSER,
        targets=("sim",),
        action=act("device_change", event={"type": "signal", "port": 3, "present": True}),
        expect=(
            Device("inputs[2].signal", equals=1),
            WsEvent("signal_change", {"input": 3, "has_signal": True}, timeout=12),
            ClientState("ui.input.3", before="disconnected", equals="signal", timeout=15),
            ClientState("kiosk.input.3", before="disconnected", equals="signal", timeout=15),
        ),
        covers=(*HUB_CORE, *STATUS, *WEB_CORE, *WEB_GRID, *KIOSK),
    ),
    Scenario(
        id="live.display_unplugged",
        title="A display unplugged is announced from the matrix's Telnet push",
        features=("F-MTX-031", "F-API-040", "F-UI-024"),
        clients=BROWSER,
        targets=("sim",),
        action=act("device_change", event={"type": "cable", "port_type": "output", "port": 1, "connected": False}),
        expect=(
            Device("outputs[0].connected", equals=0),
            # The push makes the hub read at once: well before the next poll (5 s)
            WsEvent("cable_change", {"type": "output", "port": 1, "connected": False}, timeout=4),
            WsEvent("connection_change", {"output": 1, "connected": False}, timeout=4),
            ClientState("ui.output.1", before="signal", equals="disconnected", timeout=15),
        ),
        covers=(*HUB_CORE, *STATUS, *WEB_CORE, *WEB_GRID),
    ),
    Scenario(
        id="live.rename_elsewhere",
        title="An input renamed by another controller shows its new name",
        features=("F-MTX-031", "F-API-040", "F-UI-024"),
        clients=BROWSER,
        targets=("sim",),
        action=act("device_change", patch={"inputs": {"2": {"name": "Retro PC"}}}),
        expect=(
            Device("inputs[2].name", equals="Retro PC"),
            WsEvent("input_name_change", {"input": 3, "name": "Retro PC"}, timeout=12),
            Hub("/api/status", "data.input_names.3", equals="Retro PC"),
            ClientState("ui.input_name.3", before="Computer", equals="Retro PC", timeout=15),
        ),
        covers=(*HUB_CORE, *STATUS, *WEB_CORE, *WEB_GRID),
    ),
    Scenario(
        id="live.matrix_offline",
        title="The matrix drops off the network and comes back: every client says so, nothing is made up",
        kind="failure",
        features=("F-REL-009", "F-API-032", "F-KIO-011"),
        clients=BROWSER,
        targets=("sim",),
        # Long enough that every "down" check runs inside the outage: the hub notices at its next read
        # (STATUS_POLL_INTERVAL, 5 s) and the checks run one after another.
        action=act("device_change", reboot=30),
        expect=(
            WsEvent("matrix_connection", {"connected": False}, timeout=15),
            Hub("/api/status", "success", equals=False, status=None,
                note="VAL-04: 503 with the link state, never 200 with made-up names"),
            Hub("/api/status", "data.connected", equals=False, status=None),
            ClientState("ui.header", before="connected", equals="disconnected", timeout=10),
            ClientState("kiosk.status", before="Connected", equals="Disconnected", timeout=10),
            # "state": the Telnet drop at the start of the outage is announced as connected/degraded first
            WsEvent("matrix_connection", {"connected": True, "state": "connected"}, timeout=90),
            Hub("/api/health", "data.matrix.connected", equals=True),
            ClientState("ui.header", equals="connected", timeout=60),
            ClientState("kiosk.status", equals="Connected", timeout=60),
        ),
        restart_after=True,
        covers=(*HUB_CORE, *STATUS, *WEB_CORE, *KIOSK),
    ),
]
