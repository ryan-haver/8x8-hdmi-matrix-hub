"""
Profile management endpoints.

Handles profile CRUD, recall, and macro associations.
"""

import json
import logging
from aiohttp import web

from .utils import _json_response, get_matrix_device, get_profile_manager, get_macro_manager

_LOG = logging.getLogger("rest_api.profiles")


async def handle_list_profiles(request: web.Request) -> web.Response:
    """List all saved profiles."""
    profile_manager = get_profile_manager()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    try:
        profiles = profile_manager.list_profiles()
        return _json_response(True, {"profiles": profiles})
    except Exception as e:
        _LOG.error(f"Error listing profiles: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_get_profile(request: web.Request) -> web.Response:
    """Get details of a specific profile."""
    profile_manager = get_profile_manager()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    try:
        profile_id = request.match_info.get("profile_id", "")
        if not profile_id:
            return _json_response(False, error="Profile ID required", status=400)
        
        profile = profile_manager.get_profile(profile_id)
        if profile is None:
            return _json_response(False, error=f"Profile '{profile_id}' not found", status=404)
        
        return _json_response(True, profile.to_dict())
    except Exception as e:
        _LOG.error(f"Error getting profile: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_create_profile(request: web.Request) -> web.Response:
    """Create or update a profile."""
    profile_manager = get_profile_manager()
    macro_manager = get_macro_manager()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    try:
        data = await request.json()
        
        profile_id = data.get("id")
        name = data.get("name")
        outputs = data.get("outputs", {})
        cec_config = data.get("cec_config")
        icon = data.get("icon", "📺")
        macros = data.get("macros", [])
        power_on_macro = data.get("power_on_macro")
        power_off_macro = data.get("power_off_macro")
        
        if not profile_id:
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
        
        # Validate macro references if provided
        if macros and macro_manager:
            for macro_id in macros:
                if not macro_manager.get_macro(macro_id):
                    _LOG.warning(f"Profile references non-existent macro: {macro_id}")
        
        profile = profile_manager.create_profile(
            profile_id=profile_id,
            name=name,
            outputs=outputs,
            icon=icon,
            cec_config=cec_config,
            macros=macros,
            power_on_macro=power_on_macro,
            power_off_macro=power_off_macro
        )
        _LOG.info(f"Profile '{name}' ({profile_id}) created/updated")
        
        return _json_response(True, profile.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error creating profile: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_update_profile(request: web.Request) -> web.Response:
    """Update an existing profile's properties."""
    profile_manager = get_profile_manager()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    try:
        profile_id = request.match_info.get("profile_id", "")
        if not profile_id:
            return _json_response(False, error="Profile ID required", status=400)
        
        profile = profile_manager.get_profile(profile_id)
        if profile is None:
            return _json_response(False, error=f"Profile '{profile_id}' not found", status=404)
        
        data = await request.json()
        
        updated = profile_manager.update_profile(profile_id, **data)
        if updated:
            _LOG.info(f"Profile '{profile_id}' updated")
            return _json_response(True, updated.to_dict())
        else:
            return _json_response(False, error="Failed to update profile", status=500)
            
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error updating profile: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_delete_profile(request: web.Request) -> web.Response:
    """Delete a profile."""
    profile_manager = get_profile_manager()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    try:
        profile_id = request.match_info.get("profile_id", "")
        if not profile_id:
            return _json_response(False, error="Profile ID required", status=400)
        
        if profile_manager.delete_profile(profile_id):
            _LOG.info(f"Profile '{profile_id}' deleted")
            return _json_response(True, {"deleted": profile_id})
        else:
            return _json_response(False, error=f"Profile '{profile_id}' not found", status=404)
    except Exception as e:
        _LOG.error(f"Error deleting profile: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_recall_profile(request: web.Request) -> web.Response:
    """Recall a profile, applying all its settings to the matrix."""
    profile_manager = get_profile_manager()
    macro_manager = get_macro_manager()
    matrix_device = get_matrix_device()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        profile_id = request.match_info.get("profile_id", "")
        if not profile_id:
            return _json_response(False, error="Profile ID required", status=400)
        
        profile = profile_manager.get_profile(profile_id)
        if profile is None:
            return _json_response(False, error=f"Profile '{profile_id}' not found", status=404)
        
        # Execute power-on macro if configured
        power_on_result = None
        if profile.power_on_macro and macro_manager:
            macro = macro_manager.get_macro(profile.power_on_macro)
            if macro:
                _LOG.info(f"Executing power-on macro '{macro.name}' for profile '{profile.name}'")
                try:
                    power_on_result = await macro_manager.execute_macro(profile.power_on_macro)
                except Exception as e:
                    _LOG.warning(f"Power-on macro failed: {e}")
                    power_on_result = {"error": str(e)}
        
        # Apply profile settings
        applied = []
        errors = []
        
        for output_num, output_config in profile.outputs.items():
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
        
        _LOG.info(f"Profile '{profile.name}' recalled: {len(applied)} outputs configured")
        
        return _json_response(True, {
            "profile": profile.name,
            "applied": applied,
            "errors": errors if errors else None,
            "power_on_macro": power_on_result,
        })
    except Exception as e:
        _LOG.error(f"Error recalling profile: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_profile_cec_config(request: web.Request) -> web.Response:
    """Get or update CEC configuration for a profile."""
    profile_manager = get_profile_manager()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    try:
        profile_id = request.match_info.get("profile_id", "")
        if not profile_id:
            return _json_response(False, error="Profile ID required", status=400)
        
        profile = profile_manager.get_profile(profile_id)
        if profile is None:
            return _json_response(False, error=f"Profile '{profile_id}' not found", status=404)
        
        if request.method == "GET":
            if profile.cec_config is not None:
                return _json_response(True, {
                    "profile_id": profile_id,
                    "cec_config": profile.cec_config.to_dict()
                })
            else:
                from config import CecConfig
                return _json_response(True, {
                    "profile_id": profile_id,
                    "cec_config": CecConfig.create_default().to_dict()
                })
        
        elif request.method in ("POST", "PUT"):
            data = await request.json()
            cec_config = data.get("cec_config", data)
            
            updated = profile_manager.update_profile_cec_config(profile_id, cec_config)
            if updated and updated.cec_config:
                _LOG.info(f"Profile '{profile_id}' CEC config updated")
                return _json_response(True, {
                    "profile_id": profile_id,
                    "cec_config": updated.cec_config.to_dict()
                })
            elif updated:
                return _json_response(True, {
                    "profile_id": profile_id,
                    "cec_config": None
                })
            else:
                return _json_response(False, error="Failed to update CEC config", status=500)
        
        else:
            return _json_response(False, error="Method not allowed", status=405)
            
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error handling profile CEC config: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_profile_macros(request: web.Request) -> web.Response:
    """Get or update the macros assigned to a profile."""
    profile_manager = get_profile_manager()
    macro_manager = get_macro_manager()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    try:
        profile_id = request.match_info.get("profile_id", "")
        if not profile_id:
            return _json_response(False, error="Profile ID required", status=400)
        
        profile = profile_manager.get_profile(profile_id)
        if profile is None:
            return _json_response(False, error=f"Profile '{profile_id}' not found", status=404)
        
        if request.method == "GET":
            macro_details = []
            if macro_manager:
                for macro_id in profile.macros:
                    macro = macro_manager.get_macro(macro_id)
                    if macro:
                        macro_details.append({
                            "id": macro.id,
                            "name": macro.name,
                            "icon": macro.icon,
                            "description": macro.description,
                        })
                    else:
                        macro_details.append({"id": macro_id, "error": "Macro not found"})
            
            return _json_response(True, {
                "profile_id": profile_id,
                "macros": profile.macros,
                "macro_details": macro_details,
                "power_on_macro": profile.power_on_macro,
                "power_off_macro": profile.power_off_macro,
            })
        
        elif request.method in ("POST", "PUT"):
            data = await request.json()
            
            updates = {}
            if "macros" in data:
                updates["macros"] = data["macros"]
            if "power_on_macro" in data:
                updates["power_on_macro"] = data["power_on_macro"]
            if "power_off_macro" in data:
                updates["power_off_macro"] = data["power_off_macro"]
            
            if not updates:
                return _json_response(False, error="No macro fields to update", status=400)
            
            updated = profile_manager.update_profile(profile_id, **updates)
            if updated:
                _LOG.info(f"Profile '{profile_id}' macros updated")
                return _json_response(True, {
                    "profile_id": profile_id,
                    "macros": updated.macros,
                    "power_on_macro": updated.power_on_macro,
                    "power_off_macro": updated.power_off_macro,
                })
            else:
                return _json_response(False, error="Failed to update macros", status=500)
        
        else:
            return _json_response(False, error="Method not allowed", status=405)
            
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error handling profile macros: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_reorder_profiles(request: web.Request) -> web.Response:
    """Bulk update pin order and pinned status for profiles."""
    profile_manager = get_profile_manager()
    
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    
    try:
        data = await request.json()
        profiles = data.get("profiles", [])
        
        if not profiles:
            return _json_response(False, error="No profiles specified", status=400)
        
        updated = []
        errors = []
        
        for item in profiles:
            profile_id = item.get("id")
            if not profile_id:
                errors.append("Missing profile id")
                continue
            
            profile = profile_manager.get_profile(profile_id)
            if profile is None:
                errors.append(f"Profile '{profile_id}' not found")
                continue
            
            updates = {}
            if "pinned" in item:
                updates["pinned"] = item["pinned"]
            if "pin_order" in item:
                updates["pin_order"] = item["pin_order"]
            
            if updates:
                result = profile_manager.update_profile(profile_id, **updates)
                if result:
                    updated.append(profile_id)
                else:
                    errors.append(f"Failed to update '{profile_id}'")
        
        _LOG.info(f"Reordered {len(updated)} profiles")
        return _json_response(True, {
            "updated": updated,
            "errors": errors if errors else None,
        })
        
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.error(f"Error reordering profiles: {e}")
        return _json_response(False, error=str(e), status=500)
