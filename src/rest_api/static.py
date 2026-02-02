"""
Static file and Web UI handlers.

Serves the web UI, kiosk mode, and static assets.
"""

import logging
from pathlib import Path
from aiohttp import web

from .utils import API_VERSION, _json_response

_LOG = logging.getLogger("rest_api.static")

# Web UI directory (from src/rest_api/ up to project root /web)
_WEB_DIR = Path(__file__).parent.parent.parent / "web"


async def handle_web_ui(request: web.Request) -> web.Response:
    """Serve the main Web UI page."""
    index_path = _WEB_DIR / "index.html"
    if index_path.exists():
        return web.FileResponse(index_path)
    return web.Response(text="Web UI not found", status=404)


async def handle_kiosk_ui(request: web.Request) -> web.Response:
    """Serve the Kiosk Mode page for simple input switching on tablets."""
    kiosk_path = _WEB_DIR / "kiosk.html"
    if kiosk_path.exists():
        return web.FileResponse(kiosk_path)
    return web.Response(text="Kiosk UI not found", status=404)


async def handle_static_file(request: web.Request) -> web.Response:
    """Serve static files (CSS, JS, assets)."""
    request_path = request.path
    
    # Security: prevent directory traversal
    if '..' in request_path:
        return web.Response(text="Forbidden", status=403)
    
    content_types = {
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.svg': 'image/svg+xml',
        '.png': 'image/png',
        '.ico': 'image/x-icon',
        '.json': 'application/json',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
    }
    
    full_path = _WEB_DIR / request_path.lstrip('/')
    
    if full_path.exists() and full_path.is_file():
        suffix = full_path.suffix.lower()
        content_type = content_types.get(suffix, 'application/octet-stream')
        headers = {
            'Content-Type': content_type,
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        return web.FileResponse(full_path, headers=headers)
    
    return web.Response(text="File not found", status=404)


async def handle_api_root(request: web.Request) -> web.Response:
    """API documentation/index endpoint."""
    docs = {
        "name": "OREI HDMI Matrix REST API",
        "version": API_VERSION,
        "endpoints": {
            "websocket": {
                "GET /ws": "WebSocket for real-time status updates",
            },
            "status": {
                "GET /api/health": "Health check",
                "GET /api/status": "Basic matrix status",
                "GET /api/status/full": "Comprehensive status from all endpoints",
                "GET /api/presets": "List all presets with names",
                "GET /api/inputs": "List all inputs with names",
                "GET /api/outputs": "List all outputs with names",
            },
            "extended_status": {
                "GET /api/status/outputs": "Detailed output status (connection detection, HDCP, HDR, etc.)",
                "GET /api/status/inputs": "Detailed input status (signal detection, EDID)",
                "GET /api/status/edid": "EDID configuration per input",
                "GET /api/status/ext-audio": "External audio matrix status",
                "GET /api/status/cec": "CEC configuration per port",
                "GET /api/status/system": "System settings (beep, panel lock, mode)",
                "GET /api/status/device": "Device/firmware information",
            },
            "control": {
                "POST /api/preset/{1-8}": "Recall a preset",
                "POST /api/preset/{1-8}/save": "Save current routing to preset",
                "POST /api/switch": "Route input to output (body: {input: N, output: N})",
                "POST /api/power/on": "Power on matrix",
                "POST /api/power/off": "Power off matrix",
            },
            "input_cycling": {
                "POST /api/input/next": "Cycle to next input on output (query: ?output=1)",
                "POST /api/input/previous": "Cycle to previous input on output (query: ?output=1)",
                "POST /api/output/{1-8}/source": "Set source for specific output (body: {input: N})",
            },
            "output_control": {
                "POST /api/output/{1-8}/enable": "Enable/disable output stream (body: {enabled: bool})",
                "POST /api/output/{1-8}/hdcp": "Set HDCP mode (body: {mode: 1-5})",
                "POST /api/output/{1-8}/hdr": "Set HDR mode (body: {mode: 1-3})",
                "POST /api/output/{1-8}/scaler": "Set scaler mode (body: {mode: 1-5})",
                "POST /api/output/{1-8}/arc": "Enable/disable ARC (body: {enabled: bool})",
                "POST /api/output/{1-8}/mute": "Mute/unmute audio (body: {muted: bool})",
            },
            "system_control": {
                "POST /api/system/beep": "Enable/disable beep (body: {enabled: bool})",
                "POST /api/system/panel_lock": "Lock/unlock front panel (body: {locked: bool})",
                "POST /api/system/reboot": "Reboot the matrix",
                "GET /api/system/lcd/modes": "List available LCD timeout modes",
                "POST /api/system/lcd": "Set LCD display timeout (body: {mode: 0-4})",
            },
            "edid_control": {
                "GET /api/edid/modes": "List available EDID modes",
                "POST /api/input/{1-8}/edid": "Set EDID mode for input (body: {mode: N})",
            },
            "ext_audio_control": {
                "GET /api/ext-audio/modes": "List available ext-audio modes",
                "POST /api/ext-audio/mode": "Set ext-audio mode (body: {mode: 0-2})",
                "POST /api/ext-audio/{1-8}/enable": "Enable/disable ext-audio output (body: {enabled: bool})",
                "POST /api/ext-audio/{1-8}/source": "Set ext-audio source (body: {input: 1-8})",
            },
            "scenes": {
                "GET /api/scenes": "List all saved scenes (legacy)",
                "GET /api/scene/{id}": "Get scene details (legacy)",
                "POST /api/scene": "Create/update scene (legacy)",
                "DELETE /api/scene/{id}": "Delete a scene (legacy)",
                "POST /api/scene/{id}/recall": "Apply scene to matrix (legacy)",
                "POST /api/scene/save-current": "Save current state as scene (legacy)",
            },
            "profiles": {
                "GET /api/profiles": "List all saved profiles",
                "GET /api/profile/{id}": "Get profile details",
                "POST /api/profile": "Create profile (body: {id, name, outputs, icon?, macros?, power_on_macro?, power_off_macro?})",
                "PUT /api/profile/{id}": "Update profile properties",
                "DELETE /api/profile/{id}": "Delete a profile",
                "POST /api/profile/{id}/recall": "Apply profile to matrix (runs power_on_macro if set)",
                "GET /api/profile/{id}/cec": "Get profile CEC configuration",
                "POST /api/profile/{id}/cec": "Update profile CEC configuration",
                "GET /api/profile/{id}/macros": "Get macros assigned to profile",
                "POST /api/profile/{id}/macros": "Update profile macro assignments",
            },
            "cec": {
                "GET /api/cec/commands": "List available CEC commands",
                "POST /api/cec/input/{1-8}/{command}": "Send CEC to input device",
                "POST /api/cec/output/{1-8}/{command}": "Send CEC to output device (TV)",
                "POST /api/cec/{input|output}/{1-8}/enable": "Enable/disable CEC on port",
            },
            "cec_macros": {
                "GET /api/cec/macros": "List all CEC macros",
                "GET /api/cec/macro/{id}": "Get macro details",
                "POST /api/cec/macro": "Create macro (body: {name, steps: [{command, targets, delay_ms}]})",
                "PUT /api/cec/macro/{id}": "Update macro",
                "DELETE /api/cec/macro/{id}": "Delete macro",
                "POST /api/cec/macro/{id}/execute": "Execute macro",
                "POST /api/cec/macro/{id}/test": "Validate macro (dry run)",
            },
        },
        "websocket_events": {
            "connected": "Sent on initial connection with client count",
            "routing_change": "Sent when input routing changes on an output",
            "connection_change": "Sent when display connection status changes",
            "signal_change": "Sent when input signal status changes",
            "status_update": "Full status response (on request or periodic)",
            "pong": "Response to ping command",
            "error": "Error message",
        },
        "websocket_commands": {
            "ping": "Request a pong response",
            "get_status": "Request full status update",
        },
        "mode_values": {
            "hdcp": {"1": "HDCP 1.4", "2": "HDCP 2.2", "3": "Follow Sink", "4": "Follow Source", "5": "User Mode"},
            "hdr": {"1": "Passthrough", "2": "HDR to SDR", "3": "Auto"},
            "scaler": {"1": "Passthrough", "2": "8K→4K", "3": "8K/4K→1080p", "4": "Auto", "5": "Audio Only"},
            "edid": {
                "1": "1080p 2CH", "2": "1080p 5.1CH", "3": "1080p 7.1CH",
                "4": "1080p 3D 2CH", "5": "1080p 3D 5.1CH", "6": "1080p 3D 7.1CH",
                "7": "4K30 2CH", "8": "4K30 5.1CH", "9": "4K30 7.1CH",
                "10": "4K60 420 2CH", "11": "4K60 420 5.1CH", "12": "4K60 420 7.1CH",
                "13": "4K60 444 2CH", "14": "4K60 444 7.1CH",
                "15-22": "Copy from Output 1-8",
                "33": "4K60 HDR 2CH", "34": "4K60 HDR 5.1CH", "35": "4K60 HDR 7.1CH",
                "36": "4K60 HDR Atmos", "37": "8K30", "38": "8K60"
            },
            "lcd_timeout": {"0": "Off", "1": "Always On", "2": "15 seconds", "3": "30 seconds", "4": "60 seconds"},
            "ext_audio_mode": {"0": "Bind to Input", "1": "Bind to Output", "2": "Matrix Mode"},
        },
        "cec_commands": {
            "navigation": ["up", "down", "left", "right", "select", "menu", "back"],
            "playback": ["play", "pause", "stop", "previous", "next", "rewind", "fast_forward"],
            "power": ["power_on", "power_off"],
            "volume": ["volume_up", "volume_down", "mute"],
        },
        "examples": {
            "websocket_connect": "wscat -c ws://HOST:8080/ws",
            "websocket_ping": '{"command": "ping"}',
            "websocket_status": '{"command": "get_status"}',
            "recall_preset": "curl -X POST http://HOST:8080/api/preset/2",
            "save_preset": "curl -X POST http://HOST:8080/api/preset/3/save",
            "switch_routing": 'curl -X POST http://HOST:8080/api/switch -d \'{"input": 3, "output": 1}\'',
            "next_input": "curl -X POST 'http://HOST:8080/api/input/next?output=1'",
            "set_hdcp": 'curl -X POST http://HOST:8080/api/output/1/hdcp -d \'{"mode": 2}\'',
            "set_hdr": 'curl -X POST http://HOST:8080/api/output/1/hdr -d \'{"mode": 1}\'',
            "enable_arc": 'curl -X POST http://HOST:8080/api/output/1/arc -d \'{"enabled": true}\'',
            "mute_output": 'curl -X POST http://HOST:8080/api/output/1/mute -d \'{"muted": true}\'',
            "disable_output": 'curl -X POST http://HOST:8080/api/output/3/enable -d \'{"enabled": false}\'',
            "enable_cec": 'curl -X POST http://HOST:8080/api/cec/input/2/enable -d \'{"enabled": true}\'',
            "cec_play": "curl -X POST http://HOST:8080/api/cec/input/2/play",
            "reboot": "curl -X POST http://HOST:8080/api/system/reboot",
            "get_edid_modes": "curl http://HOST:8080/api/edid/modes",
            "get_edid_status": "curl http://HOST:8080/api/status/edid",
            "set_edid": 'curl -X POST http://HOST:8080/api/input/1/edid -d \'{"mode": 36}\'',
            "copy_edid": 'curl -X POST http://HOST:8080/api/input/1/edid -d \'{"mode": 15}\'',
            "get_lcd_modes": "curl http://HOST:8080/api/system/lcd/modes",
            "set_lcd_timeout": 'curl -X POST http://HOST:8080/api/system/lcd -d \'{"mode": 3}\'',
            "get_ext_audio_status": "curl http://HOST:8080/api/status/ext-audio",
            "get_ext_audio_modes": "curl http://HOST:8080/api/ext-audio/modes",
            "set_ext_audio_mode": 'curl -X POST http://HOST:8080/api/ext-audio/mode -d \'{"mode": 2}\'',
            "enable_ext_audio": 'curl -X POST http://HOST:8080/api/ext-audio/1/enable -d \'{"enabled": true}\'',
            "set_ext_audio_source": 'curl -X POST http://HOST:8080/api/ext-audio/1/source -d \'{"input": 3}\'',
            "list_scenes": "curl http://HOST:8080/api/scenes",
            "get_scene": "curl http://HOST:8080/api/scene/movie_night",
            "create_scene": 'curl -X POST http://HOST:8080/api/scene -d \'{"id": "movie_night", "name": "Movie Night", "outputs": {"1": {"input": 2}, "2": {"input": 2}}}\'',
            "recall_scene": "curl -X POST http://HOST:8080/api/scene/movie_night/recall",
            "save_current_as_scene": 'curl -X POST http://HOST:8080/api/scene/save-current -d \'{"id": "current", "name": "Current Setup"}\'',
            "delete_scene": "curl -X DELETE http://HOST:8080/api/scene/movie_night",
        },
    }
    return _json_response(True, docs)
