"""DataUpdateCoordinator for OREI HDMI Matrix integration."""
from datetime import timedelta
import asyncio
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOGGER

class OreiMatrixCoordinator(DataUpdateCoordinator):
    """Class to manage fetching status data from the OREI HDMI Matrix REST API."""

    def __init__(self, hass, host, port):
        """Initialize the coordinator."""
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=15),
        )

    async def _async_update_data(self):
        """Fetch status data from OREI REST API endpoints."""
        session = async_get_clientsession(self.hass)
        
        try:
            # Fetch all statuses in parallel
            status_task = session.get(f"{self.base_url}/api/status")
            outputs_task = session.get(f"{self.base_url}/api/output/status")
            inputs_task = session.get(f"{self.base_url}/api/input/status")
            
            responses = await asyncio.gather(
                status_task, outputs_task, inputs_task, return_exceptions=True
            )
            
            data = {}
            
            # 1. Parse basic status
            status_resp = responses[0]
            if isinstance(status_resp, Exception):
                raise UpdateFailed(f"Failed to reach matrix: {status_resp}")
            if status_resp.status != 200:
                raise UpdateFailed(f"Status endpoint returned HTTP {status_resp.status}")
            status_json = await status_resp.json()
            if not status_json.get("success"):
                raise UpdateFailed(f"Status API error: {status_json.get('error')}")
            data["status"] = status_json.get("data", {})
            
            # 2. Parse outputs status
            outputs_resp = responses[1]
            if not isinstance(outputs_resp, Exception) and outputs_resp.status == 200:
                outputs_json = await outputs_resp.json()
                if outputs_json.get("success"):
                    data["outputs"] = outputs_json.get("data", {}).get("outputs", [])
            
            # 3. Parse inputs status
            inputs_resp = responses[2]
            if not isinstance(inputs_resp, Exception) and inputs_resp.status == 200:
                inputs_json = await inputs_resp.json()
                if inputs_json.get("success"):
                    data["inputs"] = inputs_json.get("data", {}).get("inputs", [])
            
            return data
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with OREI Matrix: {err}")
