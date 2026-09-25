"""Tests for the /api/health detail (Phase 0: connection state, last poll, loop lag, tasks)."""

import asyncio
import datetime
import time
from unittest.mock import MagicMock

import pytest

import rest_api.utils as api_utils
from rest_api.app import create_rest_app
from rest_api.core import _matrix_health
from rest_api.runtime import RUNTIME_MONITOR_KEY, LoopLagMonitor, runtime_snapshot
from rest_api.utils import API_VERSION, reset_rate_limiter


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setattr(api_utils, "_matrix_device", None)
    reset_rate_limiter()
    return create_rest_app(data_dir=tmp_path)


async def _health(client):
    resp = await client.get("/api/health")
    assert resp.status == 200
    body = await resp.json()
    assert body["success"] is True
    return body["data"]


async def test_health_keeps_legacy_fields(aiohttp_client, app):
    data = await _health(await aiohttp_client(app))
    # The HA config flow and existing clients rely on these.
    assert data["status"] == "healthy"
    assert data["service"] == "orei-hdmi-matrix"
    assert data["api_version"] == API_VERSION
    assert data["version"] == API_VERSION


async def test_health_without_matrix(aiohttp_client, app):
    data = await _health(await aiohttp_client(app))
    assert data["matrix"] == {
        "configured": False,
        "connected": False,
        "host": None,
        "last_successful_poll": None,
        "telnet_connected": None,
    }


async def test_health_with_matrix(aiohttp_client, app, monkeypatch):
    device = MagicMock()
    device.connected = True
    device.host = "10.0.0.5"
    device.telnet_connected = False
    device.last_successful_poll = datetime.datetime(2026, 9, 24, 12, 0, tzinfo=datetime.UTC)
    monkeypatch.setattr(api_utils, "_matrix_device", device)
    data = await _health(await aiohttp_client(app))
    assert data["matrix"] == {
        "configured": True,
        "connected": True,
        "host": "10.0.0.5",
        "last_successful_poll": "2026-09-24T12:00:00+00:00",
        "telnet_connected": False,
    }


def test_matrix_health_tolerates_bare_mocks():
    """A MagicMock matrix (as used across the suite) must still serialise."""
    health = _matrix_health(MagicMock())
    assert health["connected"] is False
    assert health["host"] is None
    assert health["last_successful_poll"] is None
    assert health["telnet_connected"] is None


async def test_runtime_section(aiohttp_client, app):
    client = await aiohttp_client(app)
    monitor = app[RUNTIME_MONITOR_KEY]
    assert monitor.running
    await monitor.stop()
    monitor.interval = 0.01
    monitor.start()
    await asyncio.sleep(0.05)
    data = await _health(client)
    runtime = data["runtime"]
    assert runtime["uptime_s"] >= 0
    assert isinstance(runtime["loop_lag_ms"], float) and runtime["loop_lag_ms"] >= 0
    assert runtime["loop_lag_max_ms"] >= runtime["loop_lag_ms"]
    assert runtime["task_count"] >= 2  # at least this test and the monitor


async def test_monitor_stopped_on_cleanup(aiohttp_client, app):
    client = await aiohttp_client(app)
    monitor = app[RUNTIME_MONITOR_KEY]
    assert monitor.running
    await client.close()
    assert not monitor.running


async def test_monitor_measures_lag():
    monitor = LoopLagMonitor(interval=0.01)
    monitor.start()
    try:
        await asyncio.sleep(0.02)
        time.sleep(0.1)  # block the loop on purpose
        await asyncio.sleep(0.05)
        snap = monitor.snapshot()
        assert snap["loop_lag_max_ms"] >= 50
    finally:
        await monitor.stop()
    assert not monitor.running


async def test_runtime_snapshot_without_monitor():
    from aiohttp import web

    snap = runtime_snapshot(web.Application())
    assert snap["loop_lag_ms"] is None and snap["uptime_s"] is None
