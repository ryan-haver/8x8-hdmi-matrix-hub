"""DataUpdateCoordinator for OREI HDMI Matrix integration."""

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER


class OreiMatrixCoordinator(DataUpdateCoordinator):
    """Class to manage fetching status data from the OREI HDMI Matrix REST API."""

    def __init__(self, hass, host, port):
        """Initialize the coordinator."""
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self._poll_lock = asyncio.Lock()  # prevent overlapping polls

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=15),
        )

    async def _async_update_data(self):
        """Fetch status data from OREI REST API endpoints."""
        if self._poll_lock.locked():
            LOGGER.warning("Previous poll still running, skipping this interval")
            return self.data  # return stale data rather than overlapping

        async with self._poll_lock:
            session = async_get_clientsession(self.hass)

            try:
                # Fetch all statuses in parallel. Each call has a 10s timeout so
                # the coordinator never blocks the HA event loop longer than that,
                # even when the matrix is unreachable.
                _timeout = aiohttp.ClientTimeout(total=10)
                status_task = session.get(f"{self.base_url}/api/status", timeout=_timeout)
                outputs_task = session.get(f"{self.base_url}/api/status/outputs", timeout=_timeout)
                inputs_task = session.get(f"{self.base_url}/api/status/inputs", timeout=_timeout)

                responses = await asyncio.gather(status_task, outputs_task, inputs_task, return_exceptions=True)

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
                # CRITICAL: handle null data explicitly. `.get("data", {})` only
                # handles missing key — if the API returns `{"data": null}` the
                # default {} is NOT used and data["status"] becomes None,
                # which crashes every HA entity that accesses it.
                status_data = status_json.get("data")
                if status_data is None:
                    raise UpdateFailed("Matrix API returned null status data")
                data["status"] = status_data

                # 2. Parse outputs status
                outputs_resp = responses[1]
                if not isinstance(outputs_resp, Exception) and outputs_resp.status == 200:
                    outputs_json = await outputs_resp.json()
                    if outputs_json.get("success"):
                        data["outputs"] = outputs_json.get("data", {}).get("outputs", [])
                    else:
                        LOGGER.warning("Output status API returned error: %s", outputs_json.get("error"))
                elif isinstance(outputs_resp, Exception):
                    LOGGER.warning("Failed to fetch output status: %s", outputs_resp)
                else:
                    LOGGER.warning("Output status endpoint returned HTTP %s", outputs_resp.status)

                # 3. Parse inputs status
                inputs_resp = responses[2]
                if not isinstance(inputs_resp, Exception) and inputs_resp.status == 200:
                    inputs_json = await inputs_resp.json()
                    if inputs_json.get("success"):
                        data["inputs"] = inputs_json.get("data", {}).get("inputs", [])
                    else:
                        LOGGER.warning("Input status API returned error: %s", inputs_json.get("error"))
                elif isinstance(inputs_resp, Exception):
                    LOGGER.warning("Failed to fetch input status: %s", inputs_resp)
                else:
                    LOGGER.warning("Input status endpoint returned HTTP %s", inputs_resp.status)

                return data

            except Exception as err:
                raise UpdateFailed(f"Error communicating with OREI Matrix: {err}")
