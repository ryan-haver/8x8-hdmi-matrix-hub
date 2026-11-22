"""SW-API-READ-01: the two public API indexes, through the simulator stack.

Together with the existing contracts.api_info scenario this proves F-API-002
at API V2 only. Catalog entries describe operations; these reads do not execute
those operations or prove Swagger rendering, other clients, images or hardware.
"""

from tools.validate.model import DeviceUnchanged, Hub, NoCommand, NoProtocolWarnings, Response, Scenario, act

from ._paths import HUB_CORE

# The public API version is distinct from the canonical application version
# checked by contracts.api_info. Pin the documented REST contract rather than
# importing its value from the handler being tested.
_API_VERSION = "2.10.0"
_COVERS = (
    *HUB_CORE,
    "src/rest_api/static.py",
    "src/rest_api/core.py",
    "src/rest_api/security.py",
    "src/hub/__init__.py",
    "driver.json",
    "scripts/bump_version.py",
    "docs/API_REFERENCE.md",
    "tests/test_rest_api.py",
    "tests/test_openapi_and_config_docs.py",
    "tests/sim/test_sim_rest_reads.py",
    "tests/sim/conftest.py",
    "tests/validation/scenarios/_paths.py",
    "tests/validation/scenarios/api_documentation.py",
    "tests/validation/scenarios/sw_api_read_01.py",
    "tools/validate",
    "tools/simulator",
    "tests/e2e/fixtures/data",
)

SCENARIOS = [
    Scenario(
        id=sid,
        title=f"GET {path}: public API documentation and catalog without device mutation",
        features=("F-API-002",),
        clients=("api",),
        targets=("sim",),
        action=act("request", method="GET", path=path),
        expect=(
            Response(status=200, json={
                "success": True,
                "error": None,
                "data": {
                    "name": "OREI HDMI Matrix REST API",
                    "version": _API_VERSION,
                    "endpoints": {
                        "status": {
                            "GET /api/openapi.json": "OpenAPI 3.1.0 specification (JSON)",
                            "GET /api/docs": "Interactive Swagger UI API documentation",
                        },
                        "websocket": {"GET /ws": "WebSocket for real-time status updates"},
                    },
                },
            }),
            # Existing direct tests require these catalog groups too. Avoid
            # freezing the full inventory or its incidental description text.
            Hub(path, "data.endpoints.edid_control", not_equals={}),
            Hub(path, "data.endpoints.scenes", not_equals={}),
            # Cross-check the API version exposed to clients of /api/info;
            # canonical hub version/driver identity retain their original proof.
            Hub("/api/info", "data.api_version", equals=_API_VERSION),
            DeviceUnchanged(),
            NoCommand("*"),
            NoProtocolWarnings(),
        ),
        covers=_COVERS,
        notes="Complements contracts.api_info; read-only API V2, not whole API inventory coverage.",
    )
    for sid, path in (("contracts.api_root", "/"), ("contracts.api_root_alias", "/api"))
]
