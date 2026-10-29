"""F-API-034: unavailable route-all refusal through the real API (V2 only)."""

from tools.validate.model import DeviceUnchanged, NoCommand, NoWsEvent, Response, Scenario, WsEvent, act

from ._paths import CONTROL, HUB_CORE

SCENARIOS = [
    Scenario(
        id="sw_api_client_02_c1.switch_all_failed",
        title="Unavailable matrix refuses route-all with the validated input and no routing success",
        features=("F-API-034",), clients=("api",), targets=("sim",), kind="failure",
        # The disposable simulator uses a self-signed TLS certificate. Requiring
        # normal verification leaves the real matrix client disconnected, without
        # mocks, external addresses, fixed ports or changes to the shared runner.
        hub_env={"OREI_VERIFY_SSL": "true", "MATRIX_CA_CERT": "", "MATRIX_TLS_FINGERPRINT": ""},
        action=act("route_all", input=6),
        expect=(
            Response(status=503, json={"success": False, "data": None, "error": "Matrix not connected"}),
            WsEvent("switch_all_failed", {"input": 6}),
            NoWsEvent("routing_change"),
            NoWsEvent("switch_failed", timeout=0.2),
            NoCommand("video switch"),
            NoCommand(),
            DeviceUnchanged(),
        ),
        covers=(*HUB_CORE, *CONTROL, "src/rest_api/validation.py", "tools/simulator/tls.py",
                "tools/validate/clients/api.py", "tools/validate/model.py", "tools/validate/runner.py",
                "tools/validate/stack.py", "tests/validation/scenarios/sw_api_client_02_c1.py",
                "tests/validation/test_sw_api_client_02_c1.py"),
        notes="Requires an explicitly configured external disposable source stack: managed runner preparation "
              "requires healthy Telnet and cannot prepare this unavailable hub. Apply hub_env before launching "
              "the owned HubProcess and pass its URLs via existing hub_url/sim_control_url. API plus /ws observer, "
              "simulator V2 only; no browser/image V3, target completion or canonical evidence admission.",
    ),
]
