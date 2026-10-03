"""Enabled reboots are confined to the disposable simulator."""

from tools.validate.model import (
    ClientState,
    CommandSent,
    DeviceUnchanged,
    Hub,
    NoProtocolWarnings,
    Response,
    Scenario,
    WsEvent,
    act,
)

from ._paths import CONTROL, HUB_CORE, SHORTCUTS, WEB_CORE

SCENARIOS = []
for sid, action, clients in (
    ("direct", act("request", method="POST", path="/api/system/reboot", json={}), ("api",)),
    ("legacy_shortcut", act("request", method="POST", path="/api/shortcuts/system_reboot/execute", json={}), ("api",)),
    ("enabled_shortcut", act("shortcut_run", key="system_reboot", params={}), ("api", "browser")),
):
    SCENARIOS.append(Scenario(
        id=f"reboot.{sid}",
        title=f"Enabled reboot ({sid}): one Telnet command, link loss, automatic recovery",
        features=("F-MTX-021", "F-API-013", "F-REL-001", "F-REL-005", "F-API-032",
                  *(("F-DOM-027",) if "shortcut" in sid else ())),
        clients=clients,
        targets=("sim",),
        setup=(act("request", method="PUT", path="/api/system-shortcuts/system_reboot", json={"enabled": True}),),
        cleanup=(act("request", method="PUT", path="/api/system-shortcuts/system_reboot", json={"enabled": False}),),
        action=action,
        expect=(
            Response(status=200, json={"success": True}),
            WsEvent("matrix_connection", {"connected": False}, timeout=15),
            WsEvent("matrix_connection", {"connected": True, "state": "connected"}, timeout=30),
            Hub("/api/health", "data.matrix.connected", equals=True),
            Hub("/api/health", "data.matrix.telnet_connected", equals=True),
            Hub("/api/status", "data.routing.1", equals=2),
            CommandSent("reboot", channel="telnet", count=1),
            CommandSent("reboot", channel="http", count=0),
            DeviceUnchanged(), NoProtocolWarnings(),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        covers=(*HUB_CORE, *CONTROL, *SHORTCUTS, *WEB_CORE, "src/rest_api/audio.py", "src/_telnet_proto.py",
                "web/js/components/shortcuts-drawer.js", "web/js/components/toast.js"),
        notes="Simulator reboot acknowledgement and timing are assumptions pending HIL-09. "
              "Pytest also covers HTTP-only reboot, refusal, dropped HTTP response and silent Telnet fallback. "
              "A missing acknowledgement does not prove that real hardware ignored a command.",
    ))
