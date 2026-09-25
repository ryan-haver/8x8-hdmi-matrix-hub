"""Code paths scenarios declare in ``covers`` (evidence goes stale when they change)."""

#: The hub process and its device transport: every scenario goes through these.
HUB_CORE = (
    "run.py",
    "src/orei_matrix.py",
    "src/telnet_client.py",
    "src/_task_supervisor.py",
    "src/rest_api/app.py",
    "src/rest_api/utils.py",
    "src/rest_api/websocket.py",
)
CONTROL = ("src/rest_api/control.py",)
OUTPUTS = ("src/rest_api/outputs.py",)
CEC = ("src/rest_api/cec.py", "src/cec_commands.py")
PROFILES = ("src/rest_api/profiles.py", "src/config.py", "src/cec_macros.py")
DEVICE_SETTINGS = ("src/rest_api/device_settings.py", "src/rest_api/core.py")
STATUS = ("src/rest_api/core.py",)

#: Web UI files the browser client drives.
WEB_CORE = ("web/index.html", "web/js/app.js", "web/js/api.js", "web/js/state.js", "web/js/websocket.js")
WEB_GRID = ("web/js/components/matrix-grid.js",)
WEB_DRAWERS = (
    "web/js/components/side-nav-drawer.js",
    "web/js/components/routing-drawer.js",
    "web/js/components/presets-drawer.js",
)

#: The Unfolded Circle integration as it ships (run.py legacy mode -> src/driver.py on ucapi).
UC_DRIVER = ("src/driver.py", "driver.json", "requirements-uc.txt", "src/rest_api/__init__.py")
