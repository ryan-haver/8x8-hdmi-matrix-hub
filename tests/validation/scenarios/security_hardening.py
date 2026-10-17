"""WP-F1 security contracts, with disposable profiles and restored scene fixtures.

The runner cannot capture a generated scene ID, send malformed JSON, assert
missing keys/headers, or compare latency. Consequently scene scenarios temporarily
protect ``scene_goodnight01`` and restore its PIN state; pytest additionally
creates scenes through POST, reads their returned IDs, checks storage/hash
omission, concurrent health, correlation IDs, and deletes them in finally blocks.
Do not create anonymous scenes in runner setup: they cannot be cleaned up there.

API runs prove simulated integration (V2); they do not establish browser V3.
"""

from tools.validate.model import DeviceUnchanged, Hub, NoCommand, Response, Scenario, act

from ._paths import HUB_CORE, PROFILES, SCENES

PIN = "1234"
NEW_PIN = "5678"
PROFILE_ID = "validation_security_hardening"
PROFILE_PATH = f"/api/profile/{PROFILE_ID}"
SCENE_PATH = "/api/v2/scenes/scene_goodnight01"
PROFILE_BODY = {
    "id": PROFILE_ID,
    "name": "Security validation",
    "outputs": {"1": {"input": 2}},
    "passcode": PIN,
}


def _request(method, path, body=None):
    return act("request", method=method, path=path, **({"json": body} if body is not None else {}))


def _case(sid, features, action, *, setup=(), cleanup=(), checks=(), status=200, data=None, error=None):
    body = {"success": status < 400}
    if data is not None:
        body["data"] = data
    if error is not None:
        body["error"] = error
    return Scenario(
        id=f"security_hardening.{sid}",
        title=f"Security hardening: {sid.replace('_', ' ')}",
        features=features,
        targets=("sim",),
        kind="failure" if status >= 400 else "happy",
        action=action,
        setup=setup,
        cleanup=cleanup,
        expect=(Response(status=status, json=body), *checks, NoCommand(), DeviceUnchanged()),
        covers=(*HUB_CORE, *PROFILES, *SCENES, "src/password.py", "src/rest_api/static.py",
                "src/rest_api/validation.py", "tests/validation/scenarios/security_hardening.py"),
        notes="Hash absence, PBKDF2 storage, generated scene CRUD, health latency and error IDs are asserted "
              "by tests/test_security_v3_hardening_scenarios.py; the DSL cannot express those checks.",
    )


_CREATE_PROFILE = _request("POST", "/api/profile", PROFILE_BODY)
_DELETE_PROFILE = _request("DELETE", PROFILE_PATH, {"current_passcode": PIN})
_PROTECT_SCENE = _request("PUT", SCENE_PATH, {"passcode": PIN})
_RESTORE_SCENE = _request("PUT", SCENE_PATH, {"remove_passcode": True, "current_passcode": PIN})

SCENARIOS: list[Scenario] = [
    _case("profile_read_protected", ("F-SEC-004", "F-SEC-005"),
          _request("GET", PROFILE_PATH), setup=(_CREATE_PROFILE,), cleanup=(_DELETE_PROFILE,),
          data={"password_protected": True},
          checks=(Hub(PROFILE_PATH, "data.password_protected", equals=True),)),
    _case("scene_read_protected", ("F-SEC-004", "F-SEC-005"),
          _request("GET", SCENE_PATH), setup=(_PROTECT_SCENE,), cleanup=(_RESTORE_SCENE,),
          data={"scene": {"password_protected": True}},
          checks=(Hub(SCENE_PATH, "data.scene.password_protected", equals=True),)),
]

for kind, path, setup, cleanup, field in (
    ("profile", PROFILE_PATH, (_CREATE_PROFILE,), (_DELETE_PROFILE,), "data.password_protected"),
    ("scene", SCENE_PATH, (_PROTECT_SCENE,), (_RESTORE_SCENE,), "data.scene.password_protected"),
):
    for operation, method, body in (
        ("change", "PUT", {"passcode": NEW_PIN}),
        ("remove", "PUT", {"remove_passcode": True}),
        ("delete", "DELETE", None),
    ):
        SCENARIOS.append(_case(
            f"{kind}_{operation}_requires_pin", ("F-SEC-006",), _request(method, path, body),
            setup=setup, cleanup=cleanup, status=403, data={"error": "passcode_required"},
            checks=(Hub(path, field, equals=True),),
        ))
    for operation, body, final_pin, protected in (
        ("change", {"passcode": NEW_PIN, "current_passcode": PIN}, NEW_PIN, True),
        ("remove", {"remove_passcode": True, "current_passcode": PIN}, PIN, False),
    ):
        restore = (_request("DELETE", path, {"current_passcode": final_pin}) if kind == "profile" else
                   _request("PUT", path, {"remove_passcode": True, "current_passcode": final_pin}))
        SCENARIOS.append(_case(
            f"{kind}_{operation}_with_pin", ("F-SEC-006",), _request("PUT", path, body),
            setup=setup, cleanup=(restore,), checks=(Hub(path, field, equals=protected),),
        ))

SCENARIOS.append(_case(
    "profile_delete_with_pin", ("F-SEC-006",),
    _request("DELETE", PROFILE_PATH, {"current_passcode": PIN}), setup=(_CREATE_PROFILE,),
    cleanup=(_DELETE_PROFILE,), checks=(Hub(PROFILE_PATH, "success", equals=False, status=404),),
))

for kind, path, setup, cleanup, suffix in (
    ("profile", PROFILE_PATH, (_CREATE_PROFILE,), (_DELETE_PROFILE,), "recall"),
    ("scene", SCENE_PATH, (_PROTECT_SCENE,), (_RESTORE_SCENE,), "execute"),
):
    SCENARIOS.append(_case(
        f"{kind}_wrong_pin", ("F-SEC-007",), _request("POST", f"{path}/{suffix}", {"passcode": "9999"}),
        setup=setup, cleanup=cleanup, status=403, data={"error": "invalid_passcode"},
        checks=(Hub("/api/health", "data.status", equals="healthy"),),
    ))

for sid, path in (
    ("backslash", "/css/..%5c..%5csecret.txt"),
    ("slash", "/assets/..%2f..%2fsecret.txt"),
):
    SCENARIOS.append(Scenario(
        id=f"security_hardening.static_traversal_{sid}", title="Encoded static traversal is refused",
        features=("F-SEC-010",), action=_request("GET", path), kind="failure",
        expect=(Response(status=(403, 404)), NoCommand(), DeviceUnchanged()),
        covers=(*HUB_CORE, "src/rest_api/static.py"),
    ))

SCENARIOS.extend([
    _case("non_object_json", ("F-SEC-011",), _request("POST", "/api/switch", []),
          status=400, error="Request body must be a JSON object"),
    _case("invalid_schema", ("F-SEC-011",), _request("POST", "/api/switch", {"input": 1, "output": 9}),
          status=400, error="Output must be 1-8"),
])
