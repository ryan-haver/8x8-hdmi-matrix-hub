"""Access control and request guards (WP-F1): PIN gate, cross-site protection, matrix host guard.

Every scenario starts and ends with the hub open (no Admin or Control PIN): a
scenario that sets a PIN in ``setup`` clears it again in ``cleanup`` with the
current PIN, so later scenarios in the same run are never left locked.

The ``cross_site_*`` scenarios send raw ``headers`` (``Host``, ``Origin``,
``Referer``) or a non-JSON ``data`` body with the ``request`` intent; the api
client must forward both for them to prove anything.
"""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    Response,
    Scenario,
    act,
)

from ._paths import CONTROL, HUB_CORE

ADMIN_PIN = "4826"
CONTROL_PIN = "1357"
#: Configured through ``hub_env`` (``CONTROL_API_KEY``), so no key id has to be cleaned up.
API_KEY = "validate-control-key-7f3a"

SECURITY = ("src/rest_api/security.py", "src/password.py", "src/_file_io.py")
SETTINGS = ("src/rest_api/settings.py",)

_SET_ADMIN = act("request", method="POST", path="/api/auth/pin", json={"level": "admin", "pin": ADMIN_PIN})
_CLEAR_ADMIN = act("request", method="POST", path="/api/auth/pin",
                   json={"level": "admin", "pin": None, "current_pin": ADMIN_PIN})
_SET_CONTROL = act("request", method="POST", path="/api/auth/pin", json={"level": "control", "pin": CONTROL_PIN})
_CLEAR_CONTROL = act("request", method="POST", path="/api/auth/pin", json={"level": "control", "pin": None})
_ROUTE = {"input": 3, "output": 1}
_NEW_HOST = "192.168.1.250"


def _locked(sid, title, action, expect, *, features=("F-SEC-001",), setup=(_SET_ADMIN,), cleanup=(_CLEAR_ADMIN,),
            covers=(), hub_env=None, restart_after=False):
    """A request refused by the PIN gate: nothing reaches the matrix, the PIN stays set until cleanup."""
    return Scenario(
        id=f"security_auth.{sid}", title=title, kind="failure", features=features, targets=("sim",),
        action=action, setup=setup, cleanup=cleanup,
        expect=(*expect, NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY, *covers), hub_env=hub_env or {}, restart_after=restart_after,
        notes="Sets a PIN in setup and clears it in cleanup, so the hub is open again afterwards.",
    )


def _cross_site(sid, title, status, *, headers=None, data=None):
    """A mutating request a browser on another site could forge: refused before the route runs."""
    params = {"method": "POST", "path": "/api/switch"}
    if data is None:
        params["json"] = _ROUTE
    else:
        params["data"] = data
    if headers:
        params["headers"] = headers
    return Scenario(
        id=f"security_auth.{sid}", title=title, kind="failure", features=("F-SEC-002",), targets=("sim",),
        action=act("request", **params),
        expect=(Response(status=status), NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY, *CONTROL),
        notes="Needs the api client to forward the request's raw headers / data body.",
    )


def _ssrf(sid, host, title):
    """A matrix host that would send the matrix password to the hub itself or a cloud metadata service."""
    return Scenario(
        id=f"security_auth.{sid}", title=title, kind="failure", features=("F-SEC-003",), targets=("sim",),
        action=act("request", method="POST", path="/api/settings/matrix-host",
                   json={"host": host, "port": 443, "password": "admin"}),
        expect=(Response(status=400, json={"success": False, "error": "Invalid host address"}),
                Hub("/api/settings", "data.matrix_host", not_equals=host),
                Hub("/api/settings", "data.connected", equals=True),
                NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY, *SETTINGS),
        # A regressed guard repoints the hub; the restart returns it to the configured matrix.
        restart_after=True,
    )


SCENARIOS = [
    # ------------------------------------------------------------ F-SEC-001: PIN gate
    Scenario(
        id="security_auth.status_open", title="Open by default: no PIN set, no session, no remembered device",
        features=("F-SEC-001",), targets=("sim",),
        action=act("request", method="GET", path="/api/auth/status"),
        expect=(Response(status=200, json={"admin_pin_set": False, "control_pin_set": False,
                                           "session_level": "none", "device_remembered": False}),
                Hub("/api/auth/devices", status=200), NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY),
    ),
    Scenario(
        id="security_auth.credentials_open", title="Without an Admin PIN the API key list is open to the LAN",
        features=("F-SEC-001",), targets=("sim",),
        action=act("request", method="GET", path="/api/auth/api-keys"),
        expect=(Response(status=200), Hub("/api/auth/devices", status=200), NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY),
    ),
    _locked("admin_pin_blocks_admin_route", "Admin PIN set: an admin route without unlock answers 401",
            act("request", method="POST", path="/api/settings/test-connection", json={}),
            (Response(status=401),
             Hub("/api/auth/status", "admin_pin_set", equals=True),
             Hub("/api/auth/devices", status=401),
             Hub("/api/auth/api-keys", status=401))),
    _locked("pin_change_needs_current_pin", "Admin PIN set: changing it without the current PIN answers 401",
            act("request", method="POST", path="/api/auth/pin", json={"level": "admin", "pin": "9999"}),
            (Response(status=401), Hub("/api/auth/status", "admin_pin_set", equals=True))),
    _locked("unlock_wrong_pin", "Admin PIN set: unlocking with a wrong PIN answers 401",
            act("request", method="POST", path="/api/auth/unlock", json={"level": "admin", "pin": "0000"}),
            (Response(status=401), Hub("/api/auth/status", "session_level", equals="none"))),
    Scenario(
        id="security_auth.clear_pin_restores_open",
        title="Clearing the Admin PIN with the current PIN returns the hub to the open default",
        features=("F-SEC-001",), targets=("sim",),
        setup=(_SET_ADMIN,),
        action=_CLEAR_ADMIN,
        expect=(Response(status=200, json={"admin_pin_set": False, "control_pin_set": False}),
                Hub("/api/auth/status", "admin_pin_set", equals=False),
                Hub("/api/auth/status", "control_pin_set", equals=False),
                Hub("/api/auth/devices", status=200), NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY),
    ),
    _locked("control_pin_blocks_routing", "Control PIN set: routing without unlock or API key answers 401",
            act("request", method="POST", path="/api/switch", json=_ROUTE),
            (Response(status=401), Hub("/api/auth/status", "control_pin_set", equals=True)),
            setup=(_SET_CONTROL,), cleanup=(_CLEAR_CONTROL,), covers=CONTROL),
    Scenario(
        id="security_auth.control_api_key_routes",
        title="Control PIN set: an API key (?key=) is enough to route",
        features=("F-SEC-001",), targets=("sim",), writes=("routing",),
        hub_env={"CONTROL_API_KEY": API_KEY},
        setup=(_SET_CONTROL,), cleanup=(_CLEAR_CONTROL,),
        action=act("request", method="POST", path=f"/api/switch?key={API_KEY}", json=_ROUTE),
        expect=(Response(status=200),
                Device("outputs[0].source", equals=3),
                CommandSent("video switch", {"source": [1, 3]}, count=1),
                DeviceUnchanged(allow=("outputs[0].source", "routing"))),
        covers=(*HUB_CORE, *SECURITY, *CONTROL),
    ),
    _locked("api_key_not_admin", "Admin PIN set: an API key does not unlock admin routes",
            act("request", method="POST", path=f"/api/settings/test-connection?key={API_KEY}", json={}),
            (Response(status=401),),
            hub_env={"CONTROL_API_KEY": API_KEY}),
    Scenario(
        id="security_auth.api_key_status_level", title="A valid API key reports control access on /api/auth/status",
        features=("F-SEC-001",), targets=("sim",),
        hub_env={"CONTROL_API_KEY": API_KEY},
        action=act("request", method="GET", path=f"/api/auth/status?key={API_KEY}"),
        expect=(Response(status=200, json={"session_level": "control", "admin_pin_set": False}),
                Hub("/api/auth/status", "session_level", equals="none"), NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY),
    ),
    # ------------------------------------------------------------ F-SEC-002: cross-site request protection
    _cross_site("cross_site_bad_host", "A foreign Host header (DNS rebinding) is refused with 421",
                421, headers={"Host": "evil.example.com"}),
    _cross_site("cross_site_origin", "A cross-origin mutation (Origin: http://evil.example) is refused with 403",
                403, headers={"Origin": "http://evil.example"}),
    _cross_site("cross_site_referer", "A cross-origin mutation known only by its Referer is refused with 403",
                403, headers={"Referer": "http://evil.example/page"}),
    _cross_site("cross_site_content_type", "A mutating POST without a JSON Content-Type is refused with 415",
                415, data='{"input": 3, "output": 1}', headers={"Content-Type": "text/plain"}),
    Scenario(
        id="security_auth.cross_site_allowed_origin",
        title="An origin listed in CORS_ALLOWED_ORIGINS may still route",
        features=("F-SEC-002",), targets=("sim",), writes=("routing",),
        hub_env={"CORS_ALLOWED_ORIGINS": "http://allowed.example"},
        action=act("request", method="POST", path="/api/switch", json=_ROUTE,
                   headers={"Origin": "http://allowed.example"}),
        expect=(Response(status=200), Device("outputs[0].source", equals=3),
                CommandSent("video switch", {"source": [1, 3]}, count=1),
                DeviceUnchanged(allow=("outputs[0].source", "routing"))),
        covers=(*HUB_CORE, *SECURITY, *CONTROL),
        notes="Needs the api client to forward the request's raw headers.",
    ),
    # ------------------------------------------------------------ F-SEC-003: matrix host guard
    Scenario(
        id="security_auth.matrix_host_password_required",
        title="Changing the matrix host without the matrix password is refused",
        kind="failure", features=("F-SEC-003",), targets=("sim",),
        action=act("request", method="POST", path="/api/settings/matrix-host", json={"host": _NEW_HOST, "port": 443}),
        expect=(Response(status=400, json={"success": False,
                                           "error": "Password is required when changing the matrix host"}),
                Hub("/api/settings", "data.matrix_host", not_equals=_NEW_HOST),
                Hub("/api/settings", "data.connected", equals=True),
                NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY, *SETTINGS),
        restart_after=True,
    ),
    _locked("matrix_host_admin_pin", "Admin PIN set: changing the matrix host without unlock answers 401",
            act("request", method="POST", path="/api/settings/matrix-host",
                json={"host": _NEW_HOST, "port": 443, "password": "admin"}),
            (Response(status=401), Hub("/api/settings", "data.matrix_host", not_equals=_NEW_HOST)),
            features=("F-SEC-001", "F-SEC-003"), covers=SETTINGS, restart_after=True),
    _ssrf("matrix_host_loopback", "127.0.0.2", "A loopback matrix host is refused with 400"),
    _ssrf("matrix_host_metadata", "169.254.169.254", "The cloud metadata address as matrix host is refused with 400"),
    _ssrf("matrix_host_link_local", "fe80::1", "A link-local IPv6 matrix host is refused with 400"),
    _ssrf("matrix_host_mapped_loopback", "::ffff:127.0.0.1",
          "An IPv4-mapped loopback matrix host is refused with 400"),
    # Last on purpose: clearing the PIN does not end the session this unlock opens, so a client that
    # keeps cookies (a hub reached by name, not by IP) would pass every later PIN check.
    Scenario(
        id="security_auth.unlock_admin", title="Admin PIN set: unlocking with the PIN opens an admin session",
        features=("F-SEC-001",), targets=("sim",),
        setup=(_SET_ADMIN,), cleanup=(_CLEAR_ADMIN,),
        action=act("request", method="POST", path="/api/auth/unlock", json={"level": "admin", "pin": ADMIN_PIN}),
        expect=(Response(status=200, json={"level": "admin"}),
                Hub("/api/auth/status", "admin_pin_set", equals=True), NoCommand("*"), DeviceUnchanged()),
        covers=(*HUB_CORE, *SECURITY),
    ),
]
