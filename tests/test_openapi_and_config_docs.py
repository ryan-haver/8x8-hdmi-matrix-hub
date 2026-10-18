"""Tests for OpenAPI 3.1 / Swagger UI routes, API reference, and configuration docs (DOC-03, DOC-12, TD-09)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

import hub
from hub.env import (
    ALL_ENV_VARS,
    CORE_ENV_VARS,
    ENV_ALIASES,
    INTEGRATION_ENV_VARS,
    RETIRED_ENV_VARS,
)
from hub.openapi import (
    OPENAPI_VERSION,
    _default_app,
    route_inventory,
    swagger_ui_html,
    validate_openapi_spec,
)
from rest_api.app import create_rest_app

REPO_ROOT = Path(__file__).resolve().parents[1]
API_REFERENCE_MD = REPO_ROOT / "docs" / "API_REFERENCE.md"
CONFIGURATION_MD = REPO_ROOT / "docs" / "CONFIGURATION.md"
WEBSOCKET_SCHEMA_JSON = REPO_ROOT / "docs" / "api" / "websocket.schema.json"
FEATURES_YAML = REPO_ROOT / "docs" / "validation" / "features.yaml"


class TestOpenApiAndSwaggerRoutes:
    """Verify GET /api/openapi.json and GET /api/docs routes, schema, and security middleware."""

    @pytest.mark.asyncio
    async def test_get_openapi_json_serves_valid_3_1_spec(self, aiohttp_client, tmp_path: Path):
        app = create_rest_app(data_dir=tmp_path)
        client = await aiohttp_client(app)

        resp = await client.get("/api/openapi.json")
        assert resp.status == 200
        assert resp.content_type == "application/json"

        spec = await resp.json()
        assert spec["openapi"] == OPENAPI_VERSION
        assert spec["info"]["version"] == hub.__version__
        assert spec["servers"] == [{"url": "/", "description": "This hub, on the port API_PORT listens on."}]
        assert validate_openapi_spec(spec) == []

        expected_routes = route_inventory(app)
        for route in expected_routes:
            assert route.path in spec["paths"]
            assert route.method.lower() in spec["paths"][route.path]

    @pytest.mark.asyncio
    async def test_get_api_docs_serves_swagger_ui_with_presets_and_offline_fallback(
        self, aiohttp_client, tmp_path: Path
    ):
        app = create_rest_app(data_dir=tmp_path)
        client = await aiohttp_client(app)

        resp = await client.get("/api/docs")
        assert resp.status == 200
        assert resp.content_type == "text/html"

        html = await resp.text()
        assert 'id="swagger-ui"' in html
        assert "window.SwaggerUIBundle" in html
        assert "window.SwaggerUIBundle.presets.apis" in html
        assert 'layout: "BaseLayout"' in html
        assert '"/api/openapi.json"' in html
        assert "offline-fallback" in html

    def test_swagger_ui_html_custom_parameters(self):
        html = swagger_ui_html(spec_url="/custom/openapi.json", title="Custom Docs Title")
        assert "<title>Custom Docs Title</title>" in html
        assert '"/custom/openapi.json"' in html

    @pytest.mark.asyncio
    async def test_api_root_lists_openapi_and_docs_endpoints(self, aiohttp_client, tmp_path: Path):
        app = create_rest_app(data_dir=tmp_path)
        client = await aiohttp_client(app)

        for root_path in ("/", "/api"):
            resp = await client.get(root_path)
            assert resp.status == 200
            payload = await resp.json()
            assert payload["success"] is True
            status_endpoints = payload["data"]["endpoints"]["status"]
            assert "GET /api/openapi.json" in status_endpoints
            assert "GET /api/docs" in status_endpoints

    @pytest.mark.asyncio
    async def test_openapi_and_docs_obey_security_and_cors_middleware(
        self, aiohttp_client, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("ADMIN_PIN", "123456")
        monkeypatch.setenv("CONTROL_PIN", "654321")
        app = create_rest_app(data_dir=tmp_path)
        client = await aiohttp_client(app)

        # Unrecognized Host header is rejected with 421 by security_middleware
        for path in ("/api/openapi.json", "/api/docs"):
            bad_host_resp = await client.get(path, headers={"Host": "evil.example.com"})
            assert bad_host_resp.status == 421

        # Valid Host header + same-origin Origin header succeeds even when PINs are configured,
        # and includes CORS headers from cors_middleware.
        host_header = f"127.0.0.1:{client.server.port}"
        origin_header = f"http://{host_header}"
        for path in ("/api/openapi.json", "/api/docs"):
            ok_resp = await client.get(path, headers={"Host": host_header, "Origin": origin_header})
            assert ok_resp.status == 200
            assert ok_resp.headers.get("Access-Control-Allow-Origin") == origin_header
            assert ok_resp.headers.get("Vary") == "Origin"

    @pytest.mark.asyncio
    async def test_api_info_includes_hub_version_and_api_version(self, aiohttp_client, tmp_path: Path):
        app = create_rest_app(data_dir=tmp_path)
        client = await aiohttp_client(app)

        resp = await client.get("/api/info")
        assert resp.status == 200
        payload = await resp.json()
        assert payload["success"] is True
        assert payload["data"]["version"] == hub.__version__
        assert payload["data"]["api_version"] == "2.10.0"

    def test_wheel_install_path_fallbacks_exist_in_rest_api_modules(self):
        from rest_api import core as rest_core
        from rest_api import static as rest_static
        from rest_api import utils as rest_utils

        assert rest_core.DRIVER_JSON.name == "driver.json"
        assert rest_core.DRIVER_JSON.exists()
        assert rest_static._WEB_DIR.name == "web"
        assert rest_static._WEB_DIR.exists()
        assert rest_utils._WEB_DIR == rest_static._WEB_DIR
        assert hasattr(rest_core, "_REPO_DRIVER_JSON")
        assert hasattr(rest_static, "_REPO_WEB_DIR")
        assert hasattr(rest_utils, "_REPO_WEB_DIR")
        assert Path(sys.prefix).exists()


class TestApiReferenceDocumentation:
    """Verify docs/API_REFERENCE.md covers all routes, schemas, security schemes, and WebSocket events."""

    def test_api_reference_documents_every_registered_route(self):
        content = API_REFERENCE_MD.read_text(encoding="utf-8")
        app = _default_app()
        assert app is not None
        missing = []
        for route in route_inventory(app):
            marker = f"`{route.method} {route.path}`"
            if marker not in content:
                missing.append(marker)
        assert missing == [], f"Routes missing from docs/API_REFERENCE.md: {missing}"

    def test_api_reference_documents_websocket_contract_events(self):
        content = API_REFERENCE_MD.read_text(encoding="utf-8")
        schema = json.loads(WEBSOCKET_SCHEMA_JSON.read_text(encoding="utf-8"))
        ws_events = [item["$ref"].rsplit("/", 1)[-1] for item in schema["oneOf"]]
        assert len(ws_events) == 21
        for event_name in ws_events:
            assert f"`{event_name}`" in content, f"WebSocket event {event_name!r} missing from docs/API_REFERENCE.md"

    def test_api_reference_documents_security_schemes_and_legacy_scenes(self):
        content = API_REFERENCE_MD.read_text(encoding="utf-8")
        for scheme in ("AdminSessionCookie", "ControlApiKeyHeader", "ControlApiKeyQuery"):
            assert scheme in content
        assert "ApiResponseEnvelope" in content
        assert "error_id" in content
        assert "legacy" in content.lower()
        assert "/api/openapi.json" in content
        assert "/api/docs" in content


class TestConfigurationDocumentation:
    """Verify docs/CONFIGURATION.md covers all canonical, alias, retired, and direct module env vars."""

    def test_configuration_md_documents_all_canonical_core_and_integration_vars(self):
        content = CONFIGURATION_MD.read_text(encoding="utf-8")
        for name, spec in ALL_ENV_VARS.items():
            assert f"`{name}`" in content, f"Canonical env var {name} missing from docs/CONFIGURATION.md"
            if spec.default is not None:
                assert f'"{spec.default}"' in content or f"`{spec.default}`" in content, (
                    f"Default {spec.default!r} for {name} missing from docs/CONFIGURATION.md"
                )
        assert set(CORE_ENV_VARS) | set(INTEGRATION_ENV_VARS) == set(ALL_ENV_VARS)

    def test_configuration_md_documents_all_deprecated_aliases_and_retired_vars(self):
        content = CONFIGURATION_MD.read_text(encoding="utf-8")
        for canonical, aliases in ENV_ALIASES.items():
            assert f"`{canonical}`" in content
            for alias in aliases:
                assert f"`{alias}`" in content, f"Deprecated alias {alias} missing from docs/CONFIGURATION.md"
                assert f"{alias} -> use {canonical}" in content

        for retired, reason in RETIRED_ENV_VARS.items():
            assert f"`{retired}`" in content, f"Retired var {retired} missing from docs/CONFIGURATION.md"
            assert reason in content

        assert "`REST_API_ENABLED`" in content

    def test_configuration_md_documents_direct_transport_security_and_runtime_vars(self):
        content = CONFIGURATION_MD.read_text(encoding="utf-8")
        direct_vars = (
            "OREI_USER",
            "OREI_PASSWORD",
            "OREI_VERIFY_SSL",
            "MATRIX_TLS_FINGERPRINT",
            "MATRIX_CA_CERT",
            "OREI_TELNET_PORT",
            "OREI_AUTO_RECONNECT",
            "OREI_USE_TELNET_CEC",
            "OREI_MAX_RETRIES",
            "OREI_RETRY_DELAY",
            "OREI_MAX_RETRY_DELAY",
            "OREI_CEC_CACHE_TTL",
            "OREI_STATUS_CACHE_TTL",
            "ADMIN_PIN_RESET",
            "API_KEY",
            "CONTROL_API_KEY",
            "MATRIX_PASSWORD_ITERATIONS",
            "ALLOW_PUBLIC_MATRIX_HOST",
            "TRUST_PROXY_HEADERS",
            "TRUSTED_PROXY_IPS",
            "RATE_LIMIT_READ_REQUESTS",
            "STATUS_POLL_INTERVAL",
            "MAX_WS_CLIENTS",
            "POLLING_INTERVAL",
            "POLLING_ENABLED",
            "HUB_URL",
            "HUB_API_KEY",
            "HOST_IP",
            "API_HOST",
            "HA_DISCOVERY_SERVICE_NAME",
        )
        for var_name in direct_vars:
            assert f"`{var_name}`" in content, f"Direct env var {var_name} missing from docs/CONFIGURATION.md"

    def test_configuration_md_referenced_source_paths_exist(self):
        import re

        content = CONFIGURATION_MD.read_text(encoding="utf-8")
        referenced = set(re.findall(r"`(src/[A-Za-z0-9_./-]+)`", content))
        assert referenced, "Expected source paths to be referenced in docs/CONFIGURATION.md"
        for rel_path in sorted(referenced):
            clean = rel_path.split("::")[0].rstrip("/")
            target = REPO_ROOT / clean
            assert target.exists(), f"Referenced path {clean!r} in docs/CONFIGURATION.md does not exist"
        for expected in (
            "src/hub/core/matrix_service.py",
            "src/hub/domain/action_runner.py",
            "src/hub/integrations/base.py",
            "src/hub/integrations/hub_client.py",
            "src/hub/integrations/flic",
        ):
            assert expected in referenced


class TestFeatureRegistryEntry:
    """Verify F-API-001 registers GET /api/openapi.json and GET /api/docs."""

    def test_f_api_001_includes_openapi_and_docs_routes(self):
        features = yaml.safe_load(FEATURES_YAML.read_text(encoding="utf-8"))["features"]
        f_api_001 = next(item for item in features if item["id"] == "F-API-001")
        rest_routes = f_api_001["interfaces"]["rest"]
        assert "GET /api/health" in rest_routes
        assert "GET /api/openapi.json" in rest_routes
        assert "GET /api/docs" in rest_routes
