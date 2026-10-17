"""
Security hardening of the REST API (docs/REMEDIATION_PLAN.md §4.2-4.3, WP-F1).

- SEC-11 / F-SEC-011: ``/api/system/storage``, ``/api/system/info`` and
  ``/api/info`` disclose no filesystem paths or file names, and a 500 answers
  ``Internal server error (ref: <8 hex>)`` with the details only in the log.
- SEC-13 / F-SEC-013: static files are served only from inside ``web/``,
  checked on the resolved path (``..``, encoded segments, absolute paths,
  symlinks).
- API-15: a body that is not a JSON object, invalid JSON, or a field of the
  wrong type or out of range is a 400 on every mutating endpoint, never a 500.
"""

import json
import os
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from yarl import URL

from rest_api import create_rest_app, set_matrix_device
from rest_api import static as static_module
from rest_api.validation import (
    DESCRIPTION_MAX_LENGTH,
    MAX_STEPS,
    NAME_MAX_LENGTH,
    BadRequestError,
    optional_bool,
    parse_json_object,
    require_field,
    validate_bool,
    validate_int,
    validate_list,
    validate_port,
    validate_preset,
    validate_steps,
    validate_string,
)

REST_API_DIR = Path(__file__).parent.parent / "src" / "rest_api"
REF_PATTERN = re.compile(r"^Internal server error \(ref: [0-9a-f]{8}\)$")
SECRET = "boom at C:\\secret\\matrix.cfg host 10.9.8.7"


@pytest.fixture
def matrix(mock_matrix):
    """The suite's mock matrix with the extra calls these endpoints make."""
    mock_matrix.set_output_hdcp = AsyncMock(return_value=True)
    mock_matrix.set_output_enable = AsyncMock(return_value=True)
    mock_matrix.set_beep = AsyncMock(return_value=True)
    mock_matrix.get_status = AsyncMock(return_value={"routing": [1, 2, 3, 4, 5, 6, 7, 8]})
    return mock_matrix


@pytest.fixture
async def client(aiohttp_client, matrix, tmp_path, monkeypatch):
    from persistence import reset_data_dir_cache

    monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path))
    reset_data_dir_cache()
    set_matrix_device(matrix, config_dir=str(tmp_path), data_dir=str(tmp_path))
    return await aiohttp_client(create_rest_app(data_dir=tmp_path))


def _assert_no_path_disclosure(text: str, *paths: Path) -> None:
    for path in paths:
        assert str(path) not in text
        assert str(path).replace("\\", "\\\\") not in text  # as JSON-escaped


# =============================================================================
# SEC-11: storage / info endpoints
# =============================================================================


PATH_KEYS = {
    "data_dir",
    "config_dir",
    "matrix_data_dir_env",
    "uc_config_home_env",
    "project_root",
    "path",
    "data_dir_files",
    "data_dir_error",
}


class TestNoPathDisclosure:
    async def test_storage_reports_state_without_paths_or_file_names(self, client, tmp_path):
        (tmp_path / "secret-file-name.json").write_text("{}", encoding="utf-8")

        resp = await client.get("/api/system/storage")

        assert resp.status == 200
        text = await resp.text()
        data = json.loads(text)["data"]
        assert set(data) == {"source", "data_dir_exists", "config_dir_exists", "writable", "file_count"}
        assert data["source"] == "MATRIX_DATA_DIR"
        assert data["data_dir_exists"] is True
        assert data["writable"] is True
        assert isinstance(data["file_count"], int) and data["file_count"] >= 1
        assert "secret-file-name" not in text
        _assert_no_path_disclosure(text, tmp_path)

    async def test_system_info_storage_is_sanitized(self, client, tmp_path):
        resp = await client.get("/api/system/info")

        assert resp.status == 200
        text = await resp.text()
        storage = json.loads(text)["data"]["storage"]
        assert not PATH_KEYS & set(storage)
        assert storage["source"] == "MATRIX_DATA_DIR"
        _assert_no_path_disclosure(text, tmp_path, Path(__file__).parent.parent)

    async def test_api_info_has_no_filesystem_paths(self, client, tmp_path):
        resp = await client.get("/api/info")

        assert resp.status == 200
        text = await resp.text()
        assert not PATH_KEYS & set(json.loads(text)["data"])
        _assert_no_path_disclosure(text, tmp_path, Path(__file__).parent.parent)

    async def test_unlistable_data_dir_is_reported_without_the_error_text(self, client, tmp_path, monkeypatch):
        def refuse(self):
            raise PermissionError(f"[Errno 13] Permission denied: '{tmp_path}'")

        monkeypatch.setattr(Path, "iterdir", refuse)
        resp = await client.get("/api/system/storage")

        assert resp.status == 200
        text = await resp.text()
        assert json.loads(text)["data"]["file_count"] is None
        assert "Permission denied" not in text
        _assert_no_path_disclosure(text, tmp_path)


# =============================================================================
# SEC-11: 500 responses carry a correlation id, never the exception text
# =============================================================================


def _raise_secret(*_args, **_kwargs):
    raise RuntimeError(SECRET)


FAILING_CALLS = [
    ("GET", "/api/status", "get_status", None),
    ("POST", "/api/power/on", "power_on", None),
    ("POST", "/api/preset/1", "recall_preset", None),
    ("POST", "/api/switch", "switch_input", {"input": 1, "output": 2}),
    ("POST", "/api/output/1/hdcp", "set_output_hdcp", {"mode": 2}),
    ("POST", "/api/output/1/enable", "set_output_enable", {"enabled": False}),
    ("POST", "/api/system/beep", "set_beep", {"enabled": True}),
    ("POST", "/api/system/lcd", "set_lcd_timeout", {"mode": 1}),
    ("POST", "/api/ext-audio/mode", "set_ext_audio_mode", {"mode": 1}),
    ("POST", "/api/cec/input/1/enable", "set_cec_enable", {"enabled": True}),
    ("POST", "/api/input/1/name", "set_input_name", {"name": "Apple TV"}),
    ("GET", "/api/status/outputs", "get_output_status", None),
]


class TestInternalErrorsAreOpaque:
    @pytest.mark.parametrize(("method", "path", "call", "body"), FAILING_CALLS)
    async def test_matrix_failure_answers_a_reference_not_the_exception(
        self, client, matrix, caplog, method, path, call, body
    ):
        setattr(matrix, call, AsyncMock(side_effect=RuntimeError(SECRET)))

        resp = await client.request(method, path, json=body)

        assert resp.status == 500
        text = await resp.text()
        payload = json.loads(text)
        assert payload["success"] is False
        assert REF_PATTERN.match(payload["error"]), payload["error"]
        assert "boom" not in text and "secret" not in text and "10.9.8.7" not in text
        # The details and the same reference are in the server log.
        ref = payload["error"][-9:-1]
        assert any(ref in record.getMessage() and SECRET in record.getMessage() for record in caplog.records)

    async def test_manager_failure_answers_a_reference(self, client, monkeypatch):
        from rest_api import utils

        manager = utils.get_system_shortcut_manager()
        monkeypatch.setattr(manager, "list_all", _raise_secret, raising=False)
        monkeypatch.setattr(manager, "list", _raise_secret, raising=False)
        layout_manager = utils.get_dashboard_layout_manager()
        monkeypatch.setattr(layout_manager, "get_layout", _raise_secret)

        resp = await client.get("/api/dashboard/layout")

        assert resp.status == 500
        payload = await resp.json()
        assert REF_PATTERN.match(payload["error"])

    async def test_device_settings_failure_answers_a_reference(self, client, monkeypatch):
        from rest_api import device_settings

        monkeypatch.setattr(device_settings, "get_device_settings", _raise_secret)

        resp = await client.get("/api/device-settings")

        assert resp.status == 500
        assert REF_PATTERN.match((await resp.json())["error"])

    async def test_storage_failure_answers_a_reference(self, client, monkeypatch):
        from rest_api import system

        monkeypatch.setattr(system, "get_data_dir", _raise_secret)

        for path in ("/api/system/storage", "/api/system/info"):
            resp = await client.get(path)
            assert resp.status == 500
            text = await resp.text()
            assert REF_PATTERN.match(json.loads(text)["error"])
            assert "secret" not in text

    @pytest.mark.parametrize(
        "module",
        [
            "system",
            "core",
            "control",
            "outputs",
            "audio",
            "cec",
            "macros",
            "device_settings",
            "dashboard_layout",
            "system_shortcuts",
            "themes",
            "ui",
            "scenes",
        ],
    )
    def test_no_handler_returns_raw_exception_text(self, module):
        source = (REST_API_DIR / f"{module}.py").read_text(encoding="utf-8")
        assert not re.search(r"error\s*=\s*(f?\"[^\"]*\{(e|exc|err)\}|str\((e|exc|err)\))", source)
        assert not re.search(r"=\s*str\((e|exc|err)\)", source)


# =============================================================================
# SEC-13: static file containment
# =============================================================================


def _static_request(path: str) -> MagicMock:
    request = MagicMock()
    request.path = path
    return request


class TestStaticContainment:
    @pytest.fixture
    def web_dir(self, tmp_path, monkeypatch):
        web = tmp_path / "web"
        (web / "css").mkdir(parents=True)
        (web / "css" / "app.css").write_text("body {}", encoding="utf-8")
        (tmp_path / "secret.txt").write_text("top secret", encoding="utf-8")
        monkeypatch.setattr(static_module, "_WEB_DIR", web)
        return web

    async def test_serves_a_file_inside_the_web_directory(self, web_dir):
        resp = await static_module.handle_static_file(_static_request("/css/app.css"))
        assert resp.status == 200
        assert Path(resp._path).resolve() == (web_dir / "css" / "app.css").resolve()

    @pytest.mark.parametrize(
        "path",
        [
            "/css/../../secret.txt",
            "/css/../../../secret.txt",
            "/../secret.txt",
            "/css/..\\..\\secret.txt",
            "/css/sub/../../../secret.txt",
        ],
    )
    async def test_traversal_out_of_the_web_directory_is_forbidden(self, web_dir, path):
        resp = await static_module.handle_static_file(_static_request(path))
        assert resp.status == 403

    async def test_absolute_path_is_forbidden(self, web_dir, tmp_path):
        resp = await static_module.handle_static_file(_static_request("/" + str(tmp_path / "secret.txt")))
        assert resp.status in (403, 404)
        assert getattr(resp, "_path", None) is None

    async def test_null_byte_is_forbidden(self, web_dir):
        resp = await static_module.handle_static_file(_static_request("/css/app.css\x00.png"))
        assert resp.status in (403, 404)

    async def test_symlink_pointing_outside_is_forbidden(self, web_dir, tmp_path):
        link = web_dir / "css" / "escape.txt"
        try:
            os.symlink(tmp_path / "secret.txt", link)
        except (OSError, NotImplementedError):
            pytest.skip("creating symlinks is not permitted here")
        resp = await static_module.handle_static_file(_static_request("/css/escape.txt"))
        assert resp.status == 403

    async def test_linked_directory_pointing_outside_is_forbidden(self, web_dir, tmp_path):
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.css").write_text("top secret", encoding="utf-8")
        link = web_dir / "css" / "linked"
        try:
            if os.name == "nt":
                import _winapi

                _winapi.CreateJunction(str(outside), str(link))  # no privilege needed, unlike a symlink
            else:
                os.symlink(outside, link, target_is_directory=True)
        except (OSError, NotImplementedError, ImportError):
            pytest.skip("creating a directory link is not permitted here")
        assert (link / "secret.css").exists()

        resp = await static_module.handle_static_file(_static_request("/css/linked/secret.css"))
        assert resp.status == 403

    async def test_dot_dot_inside_a_name_is_not_traversal(self, web_dir):
        (web_dir / "css" / "a..b.css").write_text("x", encoding="utf-8")
        resp = await static_module.handle_static_file(_static_request("/css/a..b.css"))
        assert resp.status == 200

    async def test_encoded_traversal_through_the_server_is_refused(self, client):
        for raw in ("/css/..%2F..%2Fdriver.json", "/js/%2e%2e/%2e%2e/driver.json", "/assets/..%5C..%5Cdriver.json"):
            resp = await client.get(URL(raw, encoded=True))
            assert resp.status in (403, 404), raw
            assert "driver_id" not in await resp.text()

    async def test_real_web_assets_are_still_served(self, client):
        resp = await client.get("/css/components.css")
        assert resp.status == 200
        assert resp.content_type == "text/css"


# =============================================================================
# API-15: request body validation
# =============================================================================


MUTATING_ENDPOINTS = [
    ("POST", "/api/switch"),
    ("POST", "/api/output/1/source"),
    ("POST", "/api/preset/1/save"),
    ("POST", "/api/input/1/name"),
    ("POST", "/api/output/1/name"),
    ("POST", "/api/input/1/edid"),
    ("POST", "/api/output/1/enable"),
    ("POST", "/api/output/1/hdcp"),
    ("POST", "/api/output/1/hdr"),
    ("POST", "/api/output/1/scaler"),
    ("POST", "/api/output/1/arc"),
    ("POST", "/api/output/1/mute"),
    ("POST", "/api/system/beep"),
    ("POST", "/api/system/panel_lock"),
    ("POST", "/api/system/lcd"),
    ("POST", "/api/ext-audio/mode"),
    ("POST", "/api/ext-audio/1/enable"),
    ("POST", "/api/ext-audio/1/source"),
    ("POST", "/api/cec/input/1/enable"),
    ("POST", "/api/cec/output/1/enable"),
    ("POST", "/api/cec/macro"),
    ("PUT", "/api/cec/macro/some_macro"),
    ("POST", "/api/device-settings"),
    ("POST", "/api/device-settings/input/1"),
    ("POST", "/api/device-settings/output/1"),
    ("POST", "/api/device-settings/preset/1/name"),
    ("PUT", "/api/device-settings/favorite-presets"),
    ("PUT", "/api/device-settings/dashboard-presets"),
    ("PUT", "/api/dashboard/layout"),
    ("POST", "/api/dashboard/cards"),
    ("POST", "/api/shortcuts"),
    ("PUT", "/api/shortcuts/reorder"),
    ("PUT", "/api/themes"),
    ("PUT", "/api/ui/preferences"),
    ("POST", "/api/scene/save-current"),
]

NON_OBJECT_BODIES = ["[]", '"str"', "123", "null", "true", "{not json", "\xff\xfe"]


class TestNonObjectBodies:
    @pytest.mark.parametrize(("method", "path"), MUTATING_ENDPOINTS)
    async def test_non_object_body_is_a_400(self, client, method, path):
        for raw in NON_OBJECT_BODIES:
            resp = await client.request(
                method, path, data=raw.encode("latin-1"), headers={"Content-Type": "application/json"}
            )
            payload = await resp.json()
            assert resp.status == 400, (path, raw, payload)
            assert payload["success"] is False
            assert payload["error"] in ("Invalid JSON body", "Request body must be a JSON object"), payload

    async def test_shortcut_update_and_execute_refuse_non_object_bodies(self, client):
        shortcuts = (await (await client.get("/api/shortcuts")).json())["data"]["shortcuts"]
        key = shortcuts[0]["key"]
        for method, path in (("PUT", f"/api/shortcuts/{key}"), ("POST", f"/api/shortcuts/{key}/execute")):
            resp = await client.request(method, path, data=b"[]", headers={"Content-Type": "application/json"})
            assert resp.status == 400, path

    async def test_macro_execute_refuses_a_non_object_body(self, client):
        created = await client.post(
            "/api/cec/macro",
            json={"name": "TV on", "steps": VALID_STEPS},
        )
        macro_id = (await created.json())["data"]["id"]
        resp = await client.post(
            f"/api/cec/macro/{macro_id}/execute", data=b"[1]", headers={"Content-Type": "application/json"}
        )
        assert resp.status == 400


VALID_STEPS = [{"command": "POWER_ON", "targets": ["output_1"], "delay_ms": 0}]

INVALID_FIELDS = [
    ("POST", "/api/switch", {"input": [1]}),
    ("POST", "/api/switch", {"input": True}),
    ("POST", "/api/switch", {"input": "two"}),
    ("POST", "/api/switch", {"input": 1, "output": 9}),
    ("POST", "/api/switch", {"input": 1, "output": {"a": 1}}),
    ("POST", "/api/output/1/source", {"input": 0}),
    ("POST", "/api/output/1/source", {"input": 1.5}),
    ("POST", "/api/preset/1/save", {"routing": [1, 2]}),
    ("POST", "/api/preset/1/save", {"routing": {"1": True}}),
    ("POST", "/api/preset/1/save", {"routing": {"9": 1}}),
    ("POST", "/api/input/1/name", {"name": 42}),
    ("POST", "/api/output/1/name", {"name": ["x"]}),
    ("POST", "/api/input/1/edid", {"mode": [1]}),
    ("POST", "/api/input/1/edid", {"copy_from_output": "nine"}),
    ("POST", "/api/output/1/hdcp", {"mode": [2]}),
    ("POST", "/api/output/1/hdcp", {"mode": True}),
    ("POST", "/api/output/1/hdr", {"mode": {"x": 1}}),
    ("POST", "/api/output/1/scaler", {"mode": 9}),
    ("POST", "/api/output/1/enable", {"enabled": "false"}),
    ("POST", "/api/output/1/arc", {"enabled": 0}),
    ("POST", "/api/output/1/mute", {"muted": "yes"}),
    ("POST", "/api/system/beep", {"enabled": "false"}),
    ("POST", "/api/system/panel_lock", {"locked": "no"}),
    ("POST", "/api/system/lcd", {"mode": [1]}),
    ("POST", "/api/ext-audio/mode", {"mode": None}),
    ("POST", "/api/ext-audio/mode", {"mode": {"m": 1}}),
    ("POST", "/api/ext-audio/1/enable", {"enabled": "true"}),
    ("POST", "/api/ext-audio/1/source", {"input": [3]}),
    ("POST", "/api/cec/input/1/enable", {"enabled": "false"}),
    ("POST", "/api/cec/input/abc/enable", {"enabled": True}),
    ("POST", "/api/cec/output/9/enable", {"enabled": True}),
    ("POST", "/api/cec/macro", {"name": "m", "icon": ["x"], "steps": VALID_STEPS}),
    ("POST", "/api/cec/macro", {"name": "m", "id": {"a": 1}, "steps": VALID_STEPS}),
    ("POST", "/api/cec/macro", {"name": "m", "description": {"d": 1}, "steps": VALID_STEPS}),
    ("POST", "/api/device-settings", {"inputs": [1, 2]}),
    ("POST", "/api/device-settings/input/1", {"name": "N" * (NAME_MAX_LENGTH + 1)}),
    ("POST", "/api/device-settings/output/1", {"icon": 7}),
    ("POST", "/api/device-settings/preset/1/name", {"name": "P" * (NAME_MAX_LENGTH + 1)}),
    ("POST", "/api/device-settings/preset/1/name", {"name": ["x"]}),
    ("PUT", "/api/dashboard/layout", {"cards": [], "version": "x"}),
    ("PUT", "/api/dashboard/layout", {"cards": [{}] * 501}),
    ("POST", "/api/shortcuts", {"name": "S" * (NAME_MAX_LENGTH + 1), "type": "power_off_all"}),
    ("POST", "/api/shortcuts", {"name": "S", "type": "power_off_all", "params": [1]}),
    ("PUT", "/api/shortcuts/reorder", {"ordered_ids": [1, 2]}),
    ("PUT", "/api/themes", {"presets": [1, 2, 3, 4]}),
    ("PUT", "/api/themes", {"presets": [{"primaryH": 1, "secondaryH": 2}] * 4, "activePresetIndex": "x"}),
    ("PUT", "/api/themes", {"presets": [{"primaryH": 1, "secondaryH": 2}] * 4, "cardOpacity": "x"}),
    ("PUT", "/api/ui/preferences", {"pinnedTabs": [{"x": 1}], "tabOrder": []}),
    ("PUT", "/api/ui/preferences", {"pinnedTabs": ["t"] * 51, "tabOrder": []}),
    ("POST", "/api/scene/save-current", {"name": ["x"]}),
    ("POST", "/api/scene/save-current", {"id": "i" * (NAME_MAX_LENGTH + 1)}),
]


class TestInvalidFields:
    @pytest.mark.parametrize(("method", "path", "body"), INVALID_FIELDS)
    async def test_invalid_field_is_a_400(self, client, matrix, method, path, body):
        resp = await client.request(method, path, json=body)
        payload = await resp.json()
        assert resp.status == 400, (path, body, payload)
        assert payload["success"] is False
        # Nothing was sent to the matrix for a refused request.
        for call in ("switch_input", "set_output_hdcp", "set_beep", "set_output_enable", "save_preset"):
            mock = getattr(matrix, call)
            if isinstance(mock, AsyncMock):
                mock.assert_not_awaited()

    async def test_shortcut_update_refuses_truthy_strings(self, client):
        shortcuts = (await (await client.get("/api/shortcuts")).json())["data"]["shortcuts"]
        key = shortcuts[0]["key"]
        for body in ({"enabled": "false"}, {"favorite": 1}, {"order": "first"}, {"label": ["x"]}):
            resp = await client.put(f"/api/shortcuts/{key}", json=body)
            assert resp.status == 400, body

    async def test_valid_requests_still_succeed(self, client, matrix):
        assert (await client.post("/api/switch", json={"input": 2, "output": 3})).status == 200
        matrix.switch_input.assert_awaited_with(2, 3)
        # Integer strings stay accepted, as before.
        assert (await client.post("/api/switch", json={"input": "4", "output": "1"})).status == 200
        assert (await client.post("/api/output/1/hdcp", json={"mode": 2})).status == 200
        assert (await client.post("/api/output/1/enable", json={"enabled": False})).status == 200
        matrix.set_output_enable.assert_awaited_with(1, False)
        assert (await client.post("/api/system/beep", json={})).status == 200
        matrix.set_beep.assert_awaited_with(True)
        # The preset-save body stays optional.
        assert (await client.post("/api/preset/1/save")).status == 200
        assert (await client.post("/api/preset/1/save", json={})).status == 200


# =============================================================================
# API-15: the validation helpers
# =============================================================================


def _request_with(body=None, *, raises=None, can_read_body=True):
    request = MagicMock()
    request.can_read_body = can_read_body
    request.json = AsyncMock(side_effect=raises) if raises else AsyncMock(return_value=body)
    return request


class TestValidationHelpers:
    async def test_parse_json_object_returns_a_dict(self):
        assert await parse_json_object(_request_with({"a": 1})) == {"a": 1}

    @pytest.mark.parametrize("body", [[], "str", 123, None, True, 1.5])
    async def test_parse_json_object_refuses_non_objects(self, body):
        with pytest.raises(BadRequestError, match="must be a JSON object"):
            await parse_json_object(_request_with(body))

    @pytest.mark.parametrize(
        "exc", [json.JSONDecodeError("x", "{", 0), UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad"), ValueError("x")]
    )
    async def test_parse_json_object_refuses_invalid_json(self, exc):
        with pytest.raises(BadRequestError, match="Invalid JSON body"):
            await parse_json_object(_request_with(raises=exc))

    async def test_parse_json_object_allow_empty(self):
        assert await parse_json_object(_request_with(can_read_body=False), allow_empty=True) == {}
        with pytest.raises(BadRequestError):
            await parse_json_object(_request_with([], can_read_body=True), allow_empty=True)

    def test_bad_request_error_response_is_a_400(self):
        resp = BadRequestError("nope").response()
        assert resp.status == 400
        assert json.loads(resp.body) == {"success": False, "data": None, "error": "nope"}

    @pytest.mark.parametrize("value", [1, 8, "3", " 5 "])
    def test_validate_port_accepts(self, value):
        assert validate_port(value) == int(str(value).strip())

    @pytest.mark.parametrize("value", [0, 9, -1, True, False, 1.0, "1.0", "x", "", None, [1], {"p": 1}, "٣", "1_0"])
    def test_validate_port_refuses(self, value):
        with pytest.raises(BadRequestError, match="Port must be 1-8"):
            validate_port(value)

    @pytest.mark.parametrize("value", [0, 9, True, "eight", None])
    def test_validate_preset_refuses(self, value):
        with pytest.raises(BadRequestError, match="Preset must be 1-8"):
            validate_preset(value)

    def test_validate_preset_accepts(self):
        assert validate_preset(8) == 8

    def test_validate_int_custom_message(self):
        with pytest.raises(BadRequestError, match=r"^Invalid mode \(0-4\)$"):
            validate_int(5, "mode", minimum=0, maximum=4, message="Invalid mode (0-4)")

    def test_validate_bool(self):
        assert validate_bool(True, "x") is True
        assert validate_bool(False, "x") is False
        for value in ("false", "true", 0, 1, None, []):
            with pytest.raises(BadRequestError, match="'x' must be true or false"):
                validate_bool(value, "x")

    def test_optional_bool_default(self):
        assert optional_bool({}, "enabled", True) is True
        assert optional_bool({"enabled": None}, "enabled", True) is True
        assert optional_bool({"enabled": False}, "enabled", True) is False
        with pytest.raises(BadRequestError):
            optional_bool({"enabled": "false"}, "enabled", True)

    def test_validate_string_bounds(self):
        assert validate_string("  name  ", "name") == "name"
        assert validate_string("n" * NAME_MAX_LENGTH, "name") == "n" * NAME_MAX_LENGTH
        with pytest.raises(BadRequestError, match=f"cannot exceed {NAME_MAX_LENGTH}"):
            validate_string("n" * (NAME_MAX_LENGTH + 1), "name")
        with pytest.raises(BadRequestError, match=f"cannot exceed {DESCRIPTION_MAX_LENGTH}"):
            validate_string("d" * (DESCRIPTION_MAX_LENGTH + 1), "description", max_length=DESCRIPTION_MAX_LENGTH)
        with pytest.raises(BadRequestError, match="must not be empty"):
            validate_string("   ", "name")
        assert validate_string("", "icon", allow_empty=True) == ""
        with pytest.raises(BadRequestError, match="must be a string"):
            validate_string(5, "name")

    def test_validate_steps_bounds(self):
        assert validate_steps([{}] * MAX_STEPS) == [{}] * MAX_STEPS
        with pytest.raises(BadRequestError, match=f"more than {MAX_STEPS}"):
            validate_steps([{}] * (MAX_STEPS + 1))
        with pytest.raises(BadRequestError, match="must not be empty"):
            validate_steps([])
        with pytest.raises(BadRequestError, match="must be a list"):
            validate_steps({"0": {}})

    def test_validate_list_bound(self):
        assert validate_list([1, 2], "x", max_items=2) == [1, 2]
        with pytest.raises(BadRequestError):
            validate_list([1, 2, 3], "x", max_items=2)

    def test_require_field(self):
        assert require_field({"a": 0}, "a") == 0
        with pytest.raises(BadRequestError, match="Missing 'a' parameter"):
            require_field({}, "a")
        with pytest.raises(BadRequestError, match="custom"):
            require_field({"a": None}, "a", "custom")
