"""
Scene management endpoints.

Handles scene CRUD operations and recall functionality.
"""

import json
import logging
from aiohttp import web

from .utils import _json_response, get_matrix_device, get_scene_manager

_LOG = logging.getLogger("rest_api.scenes")


async def handle_list_scenes(request: web.Request) -> web.Response:
    """List all saved scenes."""
    scene_manager = get_scene_manager()
    
    if scene_manager is None:
        return _json_response(False, error="Scene manager not initialized", status=503)
    
    try:
        scenes = scene_manager.list_scenes()
        return _json_response(True, {"scenes": scenes})
    except Exception as e:
        _LOG.error(f"Error listing scenes: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_get_scene(request: web.Request) -> web.Response:
    """Get details of a specific scene."""
    scene_manager = get_scene_manager()
    
    if scene_manager is None:
        return _json_response(False, error="Scene manager not initialized", status=503)
    
    try:
        scene_id = request.match_info.get("scene_id", "")
        if not scene_id:
            return _json_response(False, error="Scene ID required", status=400)
        
        scene = scene_manager.get_scene(scene_id)
        if scene is None:
            return _json_response(False, error=f"Scene '{scene_id}' not found", status=404)
        
        return _json_response(True, scene.to_dict())
    except Exception as e:
        _LOG.error(f"Error getting scene: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_create_scene(request: web.Request) -> web.Response:
    """Create or update a scene."""
    scene_manager = get_scene_manager()
    
    if scene_manager is None:
        return _json_response(False, error="Scene manager not initialized", status=503)
    
    try:
        data = await request.json()
        
        scene_id = data.get("id")
        name = data.get("name")
        outputs = data.get("outputs", {})
        cec_config = data.get("cec_config")
        
        if not scene_id:
            return _json_response(False, error="Missing 'id' parameter", status=400)
        
        if not name:
            return _json_response(False, error="Missing 'name' parameter", status=400)
        
        if not outputs:
            return _json_response(False, error="Missing 'outputs' parameter", status=400)
        
        # Validate outputs
        for output_key, config in outputs.items():
            try:
                output_num = int(output_key)
                if output_num < 1 or output_num > 8:
                    return _json_response(False, error=f"Invalid output number: {output_num}", status=400)
                
                input_num = config.get("input")
                if input_num is None:
                    return _json_response(False, error=f"Output {output_num} missing 'input'", status=400)
                if int(input_num) < 1 or int(input_num) > 8:
                    return _json_response(False, error=f"Invalid input for output {output_num}", status=400)
            except (ValueError, TypeError) as e:
                return _json_response(False, error=f"Invalid output configuration: {e}", status=400)
        
        scene = scene_manager.create_scene(scene_id, name, outputs, cec_config)
        _LOG.info(f"Scene '{name}' ({scene_id}) created/updated")
        
        return _json_response(True, scene.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error creating scene: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_delete_scene(request: web.Request) -> web.Response:
    """Delete a scene."""
    scene_manager = get_scene_manager()
    
    if scene_manager is None:
        return _json_response(False, error="Scene manager not initialized", status=503)
    
    try:
        scene_id = request.match_info.get("scene_id", "")
        if not scene_id:
            return _json_response(False, error="Scene ID required", status=400)
        
        if scene_manager.delete_scene(scene_id):
            _LOG.info(f"Scene '{scene_id}' deleted")
            return _json_response(True, {"deleted": scene_id})
        else:
            return _json_response(False, error=f"Scene '{scene_id}' not found", status=404)
    except Exception as e:
        _LOG.error(f"Error deleting scene: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_recall_scene(request: web.Request) -> web.Response:
    """Recall a scene, applying all its settings to the matrix."""
    scene_manager = get_scene_manager()
    matrix_device = get_matrix_device()
    
    if scene_manager is None:
        return _json_response(False, error="Scene manager not initialized", status=503)
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        scene_id = request.match_info.get("scene_id", "")
        if not scene_id:
            return _json_response(False, error="Scene ID required", status=400)
        
        scene = scene_manager.get_scene(scene_id)
        if scene is None:
            return _json_response(False, error=f"Scene '{scene_id}' not found", status=404)
        
        # Apply scene settings
        applied = []
        errors = []
        
        for output_num, output_config in scene.outputs.items():
            try:
                result = await matrix_device.switch_input(output_config.input, output_num)
                if result:
                    applied.append(f"Output {output_num} → Input {output_config.input}")
                else:
                    errors.append(f"Failed to switch output {output_num}")
                
                if hasattr(matrix_device, 'set_output_enable'):
                    await matrix_device.set_output_enable(output_num, output_config.enabled)
                
                if hasattr(matrix_device, 'set_audio_mute'):
                    await matrix_device.set_audio_mute(output_num, output_config.audio_mute)
                
                if output_config.hdr_mode is not None and hasattr(matrix_device, 'set_hdr_mode'):
                    await matrix_device.set_hdr_mode(output_num, output_config.hdr_mode)
                
                if output_config.hdcp_mode is not None and hasattr(matrix_device, 'set_hdcp_mode'):
                    await matrix_device.set_hdcp_mode(output_num, output_config.hdcp_mode)
                
            except Exception as e:
                errors.append(f"Output {output_num}: {e}")
        
        _LOG.info(f"Scene '{scene.name}' recalled: {len(applied)} outputs configured")
        
        return _json_response(True, {
            "scene": scene.name,
            "applied": applied,
            "errors": errors if errors else None,
        })
    except Exception as e:
        _LOG.error(f"Error recalling scene: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_save_current_as_scene(request: web.Request) -> web.Response:
    """Save current matrix state as a new scene."""
    scene_manager = get_scene_manager()
    matrix_device = get_matrix_device()
    
    if scene_manager is None:
        return _json_response(False, error="Scene manager not initialized", status=503)
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        data = await request.json()
        
        scene_id = data.get("id")
        name = data.get("name")
        
        if not scene_id:
            return _json_response(False, error="Missing 'id' parameter", status=400)
        
        if not name:
            return _json_response(False, error="Missing 'name' parameter", status=400)
        
        status = await matrix_device.get_output_status()
        if status is None:
            return _json_response(False, error="Failed to get matrix status", status=500)
        
        outputs = {}
        allsource = status.get("allsource", [])
        allout = status.get("allout", [])
        allaudiomute = status.get("allaudiomute", [])
        allhdr = status.get("allhdr", [])
        allhdcp = status.get("allhdcp", [])
        
        for i in range(8):
            output_num = i + 1
            outputs[output_num] = {
                "input": allsource[i] if i < len(allsource) else 1,
                "enabled": bool(allout[i]) if i < len(allout) else True,
                "audio_mute": bool(allaudiomute[i]) if i < len(allaudiomute) else False,
                "hdr_mode": allhdr[i] if i < len(allhdr) else None,
                "hdcp_mode": allhdcp[i] if i < len(allhdcp) else None,
            }
        
        scene = scene_manager.create_scene(scene_id, name, outputs)
        _LOG.info(f"Current state saved as scene '{name}' ({scene_id})")
        
        return _json_response(True, scene.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error saving current state as scene: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_scene_cec_config(request: web.Request) -> web.Response:
    """Get or update CEC configuration for a scene."""
    scene_manager = get_scene_manager()
    
    if scene_manager is None:
        return _json_response(False, error="Scene manager not initialized", status=503)
    
    try:
        scene_id = request.match_info.get("scene_id", "")
        if not scene_id:
            return _json_response(False, error="Scene ID required", status=400)
        
        scene = scene_manager.get_scene(scene_id)
        if scene is None:
            return _json_response(False, error=f"Scene '{scene_id}' not found", status=404)
        
        if request.method == "GET":
            if scene.cec_config is not None:
                return _json_response(True, {
                    "scene_id": scene_id,
                    "cec_config": scene.cec_config.to_dict()
                })
            else:
                from config import CecConfig
                return _json_response(True, {
                    "scene_id": scene_id,
                    "cec_config": CecConfig.create_default().to_dict()
                })
        
        elif request.method in ("POST", "PUT"):
            data = await request.json()
            cec_config = data.get("cec_config", data)
            
            updated = scene_manager.update_scene_cec_config(scene_id, cec_config)
            if updated and updated.cec_config:
                _LOG.info(f"Scene '{scene_id}' CEC config updated")
                return _json_response(True, {
                    "scene_id": scene_id,
                    "cec_config": updated.cec_config.to_dict()
                })
            elif updated:
                return _json_response(True, {
                    "scene_id": scene_id,
                    "cec_config": None
                })
            else:
                return _json_response(False, error="Failed to update CEC config", status=500)
        
        else:
            return _json_response(False, error="Method not allowed", status=405)
            
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error handling scene CEC config: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_auto_resolve_cec(request: web.Request) -> web.Response:
    """Auto-resolve CEC targets for a scene based on current matrix state."""
    scene_manager = get_scene_manager()
    matrix_device = get_matrix_device()
    
    if scene_manager is None:
        return _json_response(False, error="Scene manager not initialized", status=503)
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    try:
        scene_id = request.match_info.get("scene_id", "")
        if not scene_id:
            return _json_response(False, error="Scene ID required", status=400)
        
        scene = scene_manager.get_scene(scene_id)
        if scene is None:
            return _json_response(False, error=f"Scene '{scene_id}' not found", status=404)
        
        try:
            from cec_resolver import resolve_scene_cec_config
        except ImportError:
            from .cec_resolver import resolve_scene_cec_config
        
        active_inputs = list(scene.get_active_inputs())
        active_outputs = [num for num, out in scene.outputs.items() if out.enabled]
        
        status = await matrix_device.get_status() if matrix_device.connected else {}
        
        resolved = resolve_scene_cec_config(
            active_inputs=active_inputs,
            active_outputs=active_outputs,
            status=status,
        )
        
        apply = request.query.get("apply", "false").lower() == "true"
        
        if apply:
            from config import CecConfig
            cec_config = CecConfig.from_dict(resolved)
            scene.cec_config = cec_config
            scene_manager.save()
            _LOG.info(f"Auto-resolved and applied CEC config for scene '{scene_id}'")
        
        return _json_response(True, {
            "scene_id": scene_id,
            "resolved_cec_config": resolved,
            "applied": apply,
            "active_inputs": active_inputs,
            "active_outputs": active_outputs,
        })
        
    except Exception as e:
        _LOG.error(f"Error auto-resolving CEC config: {e}")
        return _json_response(False, error=str(e), status=500)
