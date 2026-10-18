"""OpenAPI 3.1 specification generator for the hub REST API (API-21, TD-09, DOC-03).

The routes are the contract, so the specification is generated from the live
:class:`aiohttp.web.Application` rather than maintained by hand: a registered
route is a path in the document, and a removed route disappears from it.
:func:`build_openapi_spec` accepts any application; called with no argument it
builds the hub's own REST app in a throwaway data directory and introspects
that, so a script can produce the document without a running hub.

Two things are asserted rather than derived:

``components.schemas.ApiResponseEnvelope``
    Every JSON endpoint answers with the same envelope (API-21): ``success``,
    ``data``, ``error`` and ``error_id`` — the correlation id a client quotes
    when reporting a failure. Endpoints that answer with something else (the
    web UI, static assets, the WebSocket upgrade) are described as such instead
    of being forced into the envelope.

``components.securitySchemes``
    The hub has three ways to prove who is calling: the admin session cookie,
    an API key in ``X-API-Key``, and the same key in ``?key=`` for clients that
    cannot set headers.

:func:`validate_openapi_spec` re-checks the structural rules the 3.1 schema
requires, so a generator change that would produce an unusable document fails a
test instead of shipping.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aiohttp import web

import hub

_LOG = logging.getLogger("hub.openapi")

#: The OpenAPI version this generator emits.
OPENAPI_VERSION = "3.1.0"

#: The cookie the admin session is stored in (``rest_api.security.SESSION_COOKIE``).
SESSION_COOKIE_NAME = "orei_session"

#: The header an API key is read from (``rest_api.security.SecurityManager``).
API_KEY_HEADER_NAME = "X-API-Key"

#: The query parameter the same API key may be passed in.
API_KEY_QUERY_NAME = "key"

#: HTTP methods that carry no operation of their own (``HEAD`` is added implicitly).
_SKIPPED_METHODS = frozenset({"HEAD", "OPTIONS", "TRACE"})

#: Methods that may carry a JSON request body.
_BODY_METHODS = frozenset({"POST", "PUT", "PATCH"})

#: aiohttp renders path converters as ``{name:regex}``; OpenAPI only knows ``{name}``.
_PATH_PARAM_RE = re.compile(r"\{([^}:]+)(?::[^}]*)?\}")

#: Path segment -> OpenAPI tag. Segments not listed are used as their own tag.
_PATH_TAGS: dict[str, str] = {
    "auth": "auth",
    "cec": "cec",
    "dashboard": "dashboard",
    "device-settings": "device-settings",
    "docs": "docs",
    "edid": "status",
    "ext-audio": "audio",
    "input": "matrix",
    "inputs": "matrix",
    "integrations": "integrations",
    "openapi.json": "docs",
    "output": "matrix",
    "outputs": "matrix",
    "power": "matrix",
    "preset": "matrix",
    "presets": "matrix",
    "profile": "profiles",
    "profiles": "profiles",
    "scene": "scenes",
    "scenes": "scenes",
    "settings": "settings",
    "shortcuts": "shortcuts",
    "status": "status",
    "switch": "matrix",
    "system": "system",
    "themes": "settings",
    "ui": "settings",
    "v2": "v2",
}

#: Paths outside ``/api`` get their own tags (longest prefix wins).
_NON_API_TAGS: tuple[tuple[str, str], ...] = (
    ("/css/", "static"),
    ("/js/", "static"),
    ("/assets/", "static"),
    ("/ws", "websocket"),
    ("/ui", "web-ui"),
    ("/kiosk", "web-ui"),
)

#: Description per response code an operation may answer with.
_RESPONSE_DESCRIPTIONS: dict[str, str] = {
    "400": "Malformed request",
    "401": "No session, API key or unlock",
    "403": "Authenticated, but not allowed at this access level",
    "404": "No such resource",
    "429": "Rate limited",
    "503": "The matrix is not connected",
}

#: Tags in the order the reference document lists them.
_TAG_ORDER: tuple[str, ...] = (
    "status",
    "matrix",
    "cec",
    "audio",
    "profiles",
    "scenes",
    "v2",
    "shortcuts",
    "macros",
    "dashboard",
    "device-settings",
    "integrations",
    "settings",
    "auth",
    "system",
    "docs",
    "websocket",
    "web-ui",
    "static",
    "root",
)

_TAG_DESCRIPTIONS: dict[str, str] = {
    "auth": "Sessions, the admin PIN and API keys.",
    "docs": "OpenAPI 3.1 specification and interactive Swagger UI documentation.",
    "matrix": "Routing, presets, power and port names.",
    "status": "Matrix status snapshots.",
    "cec": "CEC capabilities, commands and macros.",
    "settings": "Hub, theme and UI preferences.",
    "websocket": "The /ws live event stream (an upgrade, not JSON).",
    "web-ui": "The bundled web UI and kiosk (HTML, not JSON).",
    "static": "Static assets for the web UI.",
}


@dataclass(frozen=True)
class RouteInfo:
    """One operation, as introspected from an aiohttp router.

    ``path`` is the OpenAPI path template (``/api/output/{output}/source``);
    ``source_path`` keeps aiohttp's converter suffix (``{output:\\d+}``) so the
    path parameters can carry the pattern.
    """

    method: str
    path: str
    source_path: str
    operation_id: str
    tag: str
    summary: str

    @property
    def is_write(self) -> bool:
        return self.method in ("POST", "PUT", "PATCH", "DELETE")

    @property
    def path_parameters(self) -> tuple[str, ...]:
        return tuple(_PATH_PARAM_RE.findall(self.path))

    @property
    def is_api(self) -> bool:
        return self.path == "/api" or self.path.startswith("/api/")


def tag_for(path: str) -> str:
    """The OpenAPI tag a route belongs to, derived from its path."""
    for prefix, tag in _NON_API_TAGS:
        if path.startswith(prefix):
            return tag
    parts = path.strip("/").split("/")
    if not parts or parts[0] == "":
        return "root"
    if parts[0] != "api":
        return "web-ui"
    if len(parts) == 1:
        return "root"
    return _PATH_TAGS.get(parts[1], parts[1])


def _openapi_path(canonical: str) -> str:
    """Normalise an aiohttp path template to the OpenAPI form.

    aiohttp's ``Resource.canonical`` already drops path converters, but the
    format it produces is an implementation detail; a template must never carry
    a regex, so it is normalised here.
    """
    return _PATH_PARAM_RE.sub(r"{\1}", canonical)


def _operation_id(method: str, path: str) -> str:
    """A stable, unique-per-operation id (``post_api_output_output_source``).

    ``/ui`` and ``/ui/`` are two different routes with the same slug, so the
    trailing slash gets its own marker rather than a duplicate id.
    """
    slug = re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_") or "root"
    if len(path) > 1 and path.endswith("/"):
        slug += "_index"
    return f"{method.lower()}_{slug}"


def _handler_summary(handler: Any, method: str, path: str) -> str:
    """A one-line description: the handler's docstring, else its name."""
    doc = (getattr(handler, "__doc__", "") or "").strip()
    if doc:
        return doc.splitlines()[0].strip()
    name = getattr(handler, "__name__", "")
    if name and name != "<lambda>":
        return name.replace("_", " ").strip()
    return f"{method} {path}"


def route_inventory(app: web.Application) -> list[RouteInfo]:
    """Every (method, path) pair the application answers, deduplicated and sorted.

    ``HEAD`` is dropped (aiohttp adds it implicitly for every ``add_get``) and
    ``*`` catch-all routes are skipped, because OpenAPI has no wildcard method.
    """
    seen: dict[tuple[str, str], RouteInfo] = {}
    for resource in app.router.resources():
        canonical = resource.canonical
        path = _openapi_path(canonical)
        tag = tag_for(path)
        for route in resource:
            method = (route.method or "").upper()
            if not method or method in _SKIPPED_METHODS or method == "*":
                continue
            key = (method, path)
            if key in seen:
                continue
            seen[key] = RouteInfo(
                method=method,
                path=path,
                source_path=canonical,
                operation_id=_operation_id(method, path),
                tag=tag,
                summary=_handler_summary(route.handler, method, path),
            )
    return [seen[key] for key in sorted(seen)]


def _path_parameters(route: RouteInfo) -> list[dict[str, Any]]:
    """Path parameters, one per ``{name}`` in the template."""
    parameters: list[dict[str, Any]] = []
    for raw in re.findall(r"\{([^}]+)\}", route.source_path):
        name, _, converter = raw.partition(":")
        parameters.append(
            {
                "name": name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": f"{name} identifier" + (f" (path converter: {converter})" if converter else ""),
            }
        )
    return parameters


def envelope_schema() -> dict[str, Any]:
    """The one response shape every JSON endpoint uses (API-21)."""
    return {
        "type": "object",
        "description": (
            "The uniform response envelope. `success` is false whenever `error` is set; "
            "`error_id` correlates the response with the hub's log line."
        ),
        "required": ["success", "data", "error"],
        "properties": {
            "success": {"type": "boolean", "description": "True when the request succeeded."},
            "data": {"description": "The payload; null on failure."},
            "error": {"type": ["string", "null"], "description": "A client-safe message, or null on success."},
            "error_id": {
                "type": ["string", "null"],
                "description": "Correlation id for the server log entry; quote it in bug reports.",
            },
        },
        "additionalProperties": False,
    }


def security_schemes() -> dict[str, Any]:
    """The three ways a caller authenticates against the hub."""
    return {
        "AdminSessionCookie": {
            "type": "apiKey",
            "in": "cookie",
            "name": SESSION_COOKIE_NAME,
            "description": "Set by POST /api/auth/unlock (or /api/auth/pin) after the admin PIN.",
        },
        "ControlApiKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": API_KEY_HEADER_NAME,
            "description": "An API key created through /api/auth/api-keys; grants control-level access.",
        },
        "ControlApiKeyQuery": {
            "type": "apiKey",
            "in": "query",
            "name": API_KEY_QUERY_NAME,
            "description": "The same API key, for clients that cannot set headers.",
        },
    }


def default_operation_security() -> list[dict[str, Any]]:
    """A session cookie, or an API key in either place it is accepted."""
    return [
        {"AdminSessionCookie": []},
        {"ControlApiKeyHeader": []},
        {"ControlApiKeyQuery": []},
    ]


def _error_response(code: str) -> dict[str, Any]:
    return {
        "description": _RESPONSE_DESCRIPTIONS[code],
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ApiResponseEnvelope"}}},
    }


def _responses(route: RouteInfo) -> dict[str, Any]:
    if not route.is_api:
        return {"200": {"description": route.summary or "Success"}}

    responses: dict[str, Any] = {
        "200": {
            "description": route.summary or "Success",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ApiResponseEnvelope"}}},
        }
    }
    if route.method in ("POST", "PUT", "DELETE"):
        responses["400"] = _error_response("400")
    if route.method != "GET":
        responses["401"] = _error_response("401")
        responses["403"] = _error_response("403")
    if route.path_parameters:
        responses["404"] = _error_response("404")
    if route.is_write:
        responses["503"] = _error_response("503")
    if route.method in _BODY_METHODS:
        responses["429"] = _error_response("429")
    return dict(sorted(responses.items()))


def _operation(route: RouteInfo, security: Sequence[dict[str, Any]]) -> dict[str, Any]:
    operation: dict[str, Any] = {
        "operationId": route.operation_id,
        "summary": route.summary,
        "tags": [route.tag],
        "responses": _responses(route),
    }
    parameters = _path_parameters(route)
    if parameters:
        operation["parameters"] = parameters
    if route.is_api:
        operation["security"] = list(security)
        if route.method in _BODY_METHODS:
            operation["requestBody"] = {
                "required": False,
                "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}},
            }
    return operation


def _tags(routes: Iterable[RouteInfo]) -> list[dict[str, Any]]:
    present = {route.tag for route in routes}
    ordered = [tag for tag in _TAG_ORDER if tag in present]
    ordered.extend(sorted(present.difference(_TAG_ORDER)))
    return [{"name": tag, "description": _TAG_DESCRIPTIONS.get(tag, f"Hub {tag} endpoints.")} for tag in ordered]


def _default_app() -> web.Application | None:
    """Build the hub's REST app in a throwaway data directory.

    This is the same trick ``tests/route_inventory.py`` uses: the app factory is
    the only authority on which routes exist, and calling it against a
    temporary directory keeps generation side-effect free.
    """
    src_dir = Path(__file__).resolve().parents[1]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    try:
        from rest_api.app import create_rest_app
    except ImportError as exc:  # pragma: no cover - only when the runtime deps are absent
        _LOG.warning("Could not import the REST app; the specification will have no paths (%s)", exc)
        return None

    with tempfile.TemporaryDirectory(prefix="hub-openapi-") as tmp:
        return create_rest_app(Path(tmp))


def build_openapi_spec(
    app: web.Application | None = None,
    *,
    title: str = "8x8 HDMI Matrix Hub API",
    version: str = hub.__version__,
) -> dict[str, Any]:
    """Build the OpenAPI 3.1 document for the hub.

    :param app: the application to introspect. ``None`` builds the hub's own
        REST app in a temporary data directory, so calling this with no
        arguments produces the full document without a running hub.
    :param title: ``info.title``.
    :param version: ``info.version``.
    :returns: a JSON-serialisable OpenAPI 3.1.0 document.
    """
    resolved = app if app is not None else _default_app()
    routes = route_inventory(resolved) if resolved is not None else []
    security = default_operation_security()

    paths: dict[str, dict[str, Any]] = {}
    for route in routes:
        operation = _operation(route, security)
        item = paths.setdefault(route.path, {})
        item[route.method.lower()] = operation

    return {
        "openapi": OPENAPI_VERSION,
        "info": {
            "title": title,
            "version": version,
            "summary": "Control the OREI 8x8 HDMI matrix, its profiles, scenes, macros and shortcuts.",
            "license": {"name": "Mozilla Public License 2.0", "identifier": "MPL-2.0"},
        },
        "servers": [{"url": "/", "description": "This hub, on the port API_PORT listens on."}],
        "tags": _tags(routes),
        "paths": dict(sorted(paths.items())),
        "components": {
            "schemas": {"ApiResponseEnvelope": envelope_schema()},
            "securitySchemes": security_schemes(),
        },
        "security": security,
    }


def validate_openapi_spec(spec: dict[str, Any]) -> list[str]:
    """Return every structural problem that would make ``spec`` unusable.

    Not a full JSON-Schema check: it covers the 3.1 rules a generator is most
    likely to break (missing root fields, ``$ref`` targets that do not resolve,
    operations without responses, path templates whose parameters are not
    declared) so the "valid OpenAPI 3.1.0" claim is testable.
    """
    problems: list[str] = []
    if spec.get("openapi") != OPENAPI_VERSION:
        problems.append(f"openapi must be {OPENAPI_VERSION!r}, got {spec.get('openapi')!r}")
    info = spec.get("info")
    if not isinstance(info, dict):
        problems.append("info must be an object")
    else:
        for key in ("title", "version"):
            if not isinstance(info.get(key), str) or not info.get(key):
                problems.append(f"info.{key} must be a non-empty string")
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        problems.append("paths must be an object")
        return problems

    components = spec.get("components") if isinstance(spec.get("components"), dict) else {}
    schemas = components.get("schemas") if isinstance(components.get("schemas"), dict) else {}
    schemes = components.get("securitySchemes") if isinstance(components.get("securitySchemes"), dict) else {}

    def _refs(value: Any) -> Iterable[str]:
        if isinstance(value, dict):
            ref = value.get("$ref")
            if isinstance(ref, str):
                yield ref
            for item in value.values():
                yield from _refs(item)
        elif isinstance(value, list):
            for item in value:
                yield from _refs(item)

    for ref in _refs(spec):
        if ref.startswith("#/components/schemas/") and ref.rsplit("/", 1)[-1] not in schemas:
            problems.append(f"unresolvable $ref {ref}")

    if "ApiResponseEnvelope" not in schemas:
        problems.append("components.schemas.ApiResponseEnvelope is required (API-21)")
    for scheme in ("AdminSessionCookie", "ControlApiKeyHeader", "ControlApiKeyQuery"):
        if scheme not in schemes:
            problems.append(f"components.securitySchemes.{scheme} is required")

    for path, item in paths.items():
        if not isinstance(item, dict):
            problems.append(f"{path}: path item must be an object")
            continue
        if not item:
            problems.append(f"{path}: path item has no operations")
            continue
        declared = {
            parameter.get("name")
            for operation in item.values()
            if isinstance(operation, dict)
            for parameter in operation.get("parameters", [])
            if parameter.get("in") == "path"
        }
        for template in _PATH_PARAM_RE.findall(path):
            if template not in declared:
                problems.append(f"{path}: path parameter {template!r} is not declared")
        for method, operation in item.items():
            if not isinstance(operation, dict):
                problems.append(f"{path} {method}: operation must be an object")
                continue
            if not operation.get("responses"):
                problems.append(f"{path} {method}: operation has no responses")
            if not operation.get("operationId"):
                problems.append(f"{path} {method}: operation has no operationId")
    return problems


def spec_to_json(spec: dict[str, Any], *, indent: int = 2) -> str:
    """Serialise the specification, for ``/api/openapi.json`` and the docs build."""
    return json.dumps(spec, indent=indent, sort_keys=True) + "\n"


def swagger_ui_html(
    *,
    spec_url: str = "/api/openapi.json",
    title: str = "8x8 HDMI Matrix Hub API — Swagger UI",
) -> str:
    """Return a lightweight Swagger UI HTML page for ``/api/docs`` (DOC-03, TD-09).

    Loads ``SwaggerUIBundle`` pointed at ``spec_url`` when online and includes a
    self-contained offline fallback that fetches ``spec_url`` and renders the
    route catalog directly when the browser has no internet access.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css" />
  <style>
    body {{
      margin: 0;
      background: #0b0f17;
      color: #e6edf3;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .hub-docs-banner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 20px;
      background: #111827;
      border-bottom: 1px solid #1f2937;
      font-size: 14px;
    }}
    .hub-docs-banner a {{
      color: #38bdf8;
      text-decoration: none;
      margin-left: 16px;
    }}
    #swagger-ui {{
      background: #ffffff;
      color: #111827;
      min-height: calc(100vh - 49px);
    }}
    .offline-fallback {{
      padding: 24px;
      background: #0b0f17;
      color: #e6edf3;
    }}
    .offline-fallback code {{
      color: #38bdf8;
    }}
  </style>
</head>
<body>
  <header class="hub-docs-banner">
    <strong>{title}</strong>
    <nav>
      <a href="{spec_url}">OpenAPI 3.1 JSON ({spec_url})</a>
      <a href="/ui">Web UI</a>
      <a href="/kiosk">Kiosk</a>
    </nav>
  </header>
  <main id="swagger-ui"></main>
  <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js" crossorigin></script>
  <script>
    (function () {{
      var specUrl = {json.dumps(spec_url)};
      if (window.SwaggerUIBundle) {{
        var presets = [window.SwaggerUIBundle.presets.apis];
        if (window.SwaggerUIBundle.SwaggerUIStandalonePreset) {{
          presets.push(window.SwaggerUIBundle.SwaggerUIStandalonePreset);
        }}
        window.ui = window.SwaggerUIBundle({{
          url: specUrl,
          dom_id: "#swagger-ui",
          layout: "BaseLayout",
          deepLinking: true,
          persistAuthorization: true,
          presets: presets
        }});
        return;
      }}
      fetch(specUrl)
        .then(function (r) {{ return r.json(); }})
        .then(function (spec) {{
          var root = document.getElementById("swagger-ui");
          var wrap = document.createElement("div");
          wrap.className = "offline-fallback";
          var h1 = document.createElement("h1");
          h1.textContent = (spec.info && spec.info.title) || "API Reference";
          wrap.appendChild(h1);
          var paths = spec.paths || {{}};
          Object.keys(paths).sort().forEach(function (p) {{
            Object.keys(paths[p]).forEach(function (m) {{
              var row = document.createElement("div");
              var code = document.createElement("code");
              code.textContent = m.toUpperCase() + " " + p;
              row.appendChild(code);
              var summary = (paths[p][m] && paths[p][m].summary) ? " — " + paths[p][m].summary : "";
              row.appendChild(document.createTextNode(summary));
              wrap.appendChild(row);
            }});
          }});
          root.replaceChildren(wrap);
        }})
        .catch(function () {{}});
    }})();
  </script>
</body>
</html>
"""


__all__ = [
    "API_KEY_HEADER_NAME",
    "API_KEY_QUERY_NAME",
    "OPENAPI_VERSION",
    "SESSION_COOKIE_NAME",
    "RouteInfo",
    "build_openapi_spec",
    "default_operation_security",
    "envelope_schema",
    "route_inventory",
    "security_schemes",
    "spec_to_json",
    "swagger_ui_html",
    "tag_for",
    "validate_openapi_spec",
]
