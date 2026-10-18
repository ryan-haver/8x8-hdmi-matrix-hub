"""Read-only liveness and API-documentation evidence for F-API-001.

HTTP reads establish V2; rendering Swagger and real-device behavior need their
own client/hardware evidence.
"""

from pathlib import Path

from scripts.bump_version import canonical_version
from tools.validate.model import DeviceUnchanged, NoCommand, NoProtocolWarnings, Response, Scenario, act

from ._paths import HUB_CORE

SCENARIOS = [
    Scenario(
        id="contracts.api_info",
        title="API info reports the canonical application version and driver identity",
        kind="happy",
        features=("F-API-002",),
        targets=("sim",),
        action=act("request", method="GET", path="/api/info"),
        expect=(
            Response(status=200, json={"success": True, "data": {
                "version": canonical_version(Path(__file__).resolve().parents[3]),
                "driver_id": "hdmi_matrix", "driver_name": "HDMI Matrix"
            }}),
            DeviceUnchanged(), NoProtocolWarnings(),
        ),
        covers=(*HUB_CORE, "driver.json", "src/hub/__init__.py"),
    ),
    Scenario(
        id="contracts.openapi_spec",
        title="Live OpenAPI document describes its JSON and HTML endpoints",
        kind="happy",
        features=("F-API-001",),
        targets=("sim",),
        action=act("request", method="GET", path="/api/openapi.json"),
        expect=(
            Response(status=200, json={
                "openapi": "3.1.0",
                "paths": {
                    "/api/docs": {"get": {"security": [], "responses": {
                        "200": {"content": {"text/html": {"schema": {"type": "string"}}}}
                    }}},
                    "/api/openapi.json": {"get": {"security": [], "responses": {
                        "200": {"content": {"application/json": {"schema": {"type": "object"}}}}
                    }}},
                },
            }),
            NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings(),
        ),
        covers=(*HUB_CORE, "src/hub/openapi.py", "src/rest_api/static.py"),
    ),
    Scenario(
        id="contracts.api_docs",
        title="Swagger HTML route responds without writing to the matrix",
        kind="happy",
        features=("F-API-001",),
        targets=("sim",),
        action=act("request", method="GET", path="/api/docs"),
        expect=(Response(status=200), NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=(*HUB_CORE, "src/hub/openapi.py", "src/rest_api/static.py"),
        notes="Response text is captured; this HTTP scenario does not prove browser rendering.",
    ),
    Scenario(
        id="contracts.health",
        title="Liveness read reports the simulator connection without a device write",
        kind="happy",
        features=("F-API-001",),
        targets=("sim",),
        action=act("request", method="GET", path="/api/health"),
        expect=(
            Response(status=200, json={"success": True, "data": {"matrix": {"connected": True}}}),
            NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings(),
        ),
        covers=HUB_CORE,
    ),
]
