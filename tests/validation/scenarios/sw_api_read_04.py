"""F-API-031: actual CORS exchanges, API V2 only; no WebSocket qualification."""

from tools.validate.model import DeviceUnchanged, NoCommand, NoProtocolWarnings, Response, Scenario, act

from ._paths import HUB_CORE

COVERS = (
    *HUB_CORE, "src/rest_api/security.py", "src/rest_api/core.py",
    "tools/validate/clients/api.py", "tools/validate/model.py", "tools/validate/runner.py",
    "tools/validate/stack.py", "tests/validation/scenarios/sw_api_read_04.py",
    "tests/validation/test_sw_api_read_04.py", "tests/e2e/fixtures/data",
)
ALLOWED = "https://allowed.example"
DENIED = "https://denied.example"
CORS_HEADERS = {
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-API-Key, X-Admin-PIN",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
}


def exchange(name, *, config="", origin=None, method="GET", allow=None, host=None, status=200):
    headers = {"Origin": origin} if origin else {}
    if host:
        headers["Host"] = host
    if method == "OPTIONS":
        headers.update({
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, X-API-Key, X-Admin-PIN",
        })
    expected = {**CORS_HEADERS, **({"Access-Control-Allow-Origin": allow} if allow else {})}
    absent = ("Access-Control-Allow-Credentials",)
    if not allow:
        absent += ("Access-Control-Allow-Origin",)
    if status == 403:
        # The earlier security guard rejects a cross-origin write before CORS.
        expected = {}
        absent += tuple(CORS_HEADERS)
    return Scenario(
        id=f"sw_api_read_04.{name}", title=f"CORS: {name.replace('_', ' ')}",
        features=("F-API-031",), clients=("api",), targets=("sim",), covers=COVERS,
        kind="failure" if status == 403 else "happy",
        hub_env={"CORS_ALLOWED_ORIGINS": config},
        action=act("request", method=method, path="/api/health" if method == "GET" else "/api/switch",
                   headers=headers, **({"json": {"input": 6, "output": 1}} if method == "POST" else {})),
        expect=(Response(status=status, headers=expected, absent_headers=absent),
                DeviceUnchanged(), NoCommand(), NoProtocolWarnings()),
        notes="Explicit CORS config; public response headers and unchanged simulator only. No browser, image or F-API-032 proof.",
    )


SCENARIOS = [
    exchange("default_no_origin"),
    exchange("default_same_origin", origin="http://hub.local", host="hub.local", allow="http://hub.local"),
    exchange("default_denied_origin", origin=DENIED),
    exchange("default_preflight", origin=DENIED, method="OPTIONS"),
    exchange("default_no_origin_preflight", method="OPTIONS"),
    exchange("default_denied_mutation", origin=DENIED, method="POST", status=403),
    exchange("configured_allowed", config=ALLOWED, origin=ALLOWED, allow=ALLOWED),
    exchange("configured_denied", config=ALLOWED, origin=DENIED),
    exchange("configured_allowed_preflight", config=ALLOWED, origin=ALLOWED, method="OPTIONS", allow=ALLOWED),
    exchange("configured_denied_preflight", config=ALLOWED, origin=DENIED, method="OPTIONS"),
    exchange("wildcard_origin", config="*", origin=DENIED, allow="*"),
    exchange("wildcard_no_origin", config="*", allow="*"),
    exchange("wildcard_preflight", config="*", origin=DENIED, method="OPTIONS", allow="*"),
]
