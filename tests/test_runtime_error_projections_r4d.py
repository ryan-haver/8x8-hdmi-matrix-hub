"""R4D exception privacy at the service and registered profile REST boundaries."""

import asyncio
import logging
import re
from unittest.mock import AsyncMock, Mock

import pytest

from hub.core.matrix_service import MatrixService
from tests.test_hub_core_matrix_service import FakeMatrix
from tests.test_runtime_preset_errors_r4b import preset_runtime as preset_runtime

PRIVATE = r"private-r4d at C:\private-r4d\matrix.cfg host 10.93.82.71"
USER = "r4d-user-canary"
PASSWORD = "r4d-password-canary"
REF = re.compile(r"Internal server error \(ref: ([0-9a-f]{8})\)")


def assert_no_private(value):
    text = repr(value)
    for fragment in ("private-r4d", "matrix.cfg", "10.93.82.71", USER, PASSWORD, "RuntimeError", "OSError"):
        assert fragment not in text


def diagnostic(message, caplog):
    match = REF.fullmatch(message)
    assert match is not None
    records = [record for record in caplog.records if f"[{match[1]}]" in record.getMessage()]
    assert len(records) == 1
    assert PRIVATE in records[0].getMessage()
    assert_no_private(message)
    return records[0]


def data_files(runtime):
    root = runtime.prepared.paths.data_dir
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


async def test_runtime_protocol_read_failure_snapshot_health_and_private_redacted_log(
    preset_runtime, monkeypatch, caplog
):
    runtime, client, _ = preset_runtime
    service = runtime.service
    matrix = service.client
    original_read = matrix.get_video_status
    monkeypatch.setattr(matrix, "_user", USER)
    monkeypatch.setattr(matrix, "password", PASSWORD)
    assert matrix.credentials() == (USER, PASSWORD)
    before = service.snapshot()
    generation = service._write_generation
    events = []
    unsubscribe = runtime.bus.subscribe(events.append)

    async def broken_read():
        matrix._connected = False
        raise RuntimeError(f"{PRIVATE} user={USER} password={PASSWORD}")

    read = AsyncMock(side_effect=broken_read)
    monkeypatch.setattr(matrix, "get_video_status", read)
    try:
        with caplog.at_level(logging.ERROR):
            await runtime.refresh()
        read.assert_awaited_once_with()
        record = diagnostic(service.last_error, caplog)
        assert "Matrix status read failed" in record.getMessage()
        assert "user=[redacted] password=[redacted]" in record.getMessage()
        assert USER not in caplog.text and PASSWORD not in caplog.text
        # A raw traceback would reintroduce the configured credentials.
        assert record.exc_info is None
        assert_no_private(service.snapshot())
        assert_no_private(runtime.snapshot())
        assert_no_private(await runtime.local.snapshot())
        response = await client.get("/api/health")
        assert response.status == 200
        health = await response.json()
        assert health["success"] is True
        assert health["data"]["matrix"]["connected"] is False
        assert health["data"]["matrix"]["host"] == "127.0.0.1"
        assert_no_private(health)
        assert service._write_generation == generation
        assert service.routing == before["routing"]
        assert service.snapshot()["last_refresh"] == before["last_refresh"]
        assert service.connected is matrix.connected is False
        await runtime.bus.drain(timeout=1)
        connection = [event for event in events if event.topic == "hub_connection"]
        assert len(connection) == 1
        assert connection[0].data["error"] == service.last_error
        assert_no_private([event.data for event in events])

        monkeypatch.setattr(matrix, "get_video_status", original_read)
        matrix._connected = True
        await runtime.refresh()
        assert service.connected and service.last_error is None
        assert service._write_generation == generation
    finally:
        unsubscribe()


@pytest.mark.parametrize("exception_type", [RuntimeError, OSError])
@pytest.mark.parametrize("method,path,manager_method,body", [
    ("GET", "/api/profiles", "list_profiles", None),
    ("GET", "/api/profile/movie", "get_profile", None),
    ("POST", "/api/profile", "get_profile", {"id": "movie", "name": "Movie", "outputs": {"1": {"input": 2}}}),
    ("PUT", "/api/profile/movie", "get_profile", {"name": "Movie"}),
    ("DELETE", "/api/profile/movie", "get_profile", None),
    ("GET", "/api/profile/movie/cec", "get_profile", None),
    ("GET", "/api/profile/movie/macros", "get_profile", None),
    ("POST", "/api/profiles/reorder", "get_profile", {"profiles": [{"id": "movie", "pinned": True}]}),
    ("GET", "/api/profiles/favorites", "list_favorites", None),
    ("POST", "/api/profile/movie/favorite", "toggle_favorite", None),
    ("PUT", "/api/profile/movie/favorite", "set_favorite", {"favorite": True}),
    ("POST", "/api/profile/movie/dashboard", "toggle_dashboard_visible", None),
    ("PUT", "/api/profile/movie/dashboard", "set_dashboard_visible", {"dashboard_visible": True}),
])
async def test_registered_profile_generic_errors_are_opaque_without_mutation(
    preset_runtime, monkeypatch, caplog, method, path, manager_method, body, exception_type
):
    runtime, client, sim = preset_runtime
    # Initialize the normal auth middleware's lazy security store before the
    # no-mutation baseline; its first request is unrelated to profile storage.
    response = await client.get("/api/profiles")
    assert response.status == 200
    before_files = data_files(runtime)
    before_snapshot = runtime.snapshot()
    generation = runtime.service._write_generation
    sim.log.clear()
    failure = Mock(side_effect=exception_type(PRIVATE))
    with monkeypatch.context() as patch:
        patch.setattr(runtime.managers.profiles, manager_method, failure)
        with caplog.at_level(logging.ERROR):
            response = await client.request(method, path, **({"json": body} if body is not None else {}))
        assert response.status == 500
        payload = await response.json()
        assert payload["success"] is False and payload["data"] is None
        assert set(payload) == {"success", "data", "error"}
        record = diagnostic(payload["error"], caplog)
        assert record.exc_info[0] is exception_type
        assert record.exc_info[2] is not None
        assert_no_private(payload)
        assert failure.call_count == 1
    assert data_files(runtime) == before_files
    assert runtime.snapshot() == before_snapshot
    assert runtime.service._write_generation == generation
    assert not sim.log
    assert not runtime._operations and runtime.transaction._owner is None


async def test_safe_stale_read_exception_does_not_replace_new_client_error(monkeypatch, caplog):
    old = FakeMatrix()
    monkeypatch.setattr(old, "user", USER, raising=False)
    monkeypatch.setattr(old, "password", PASSWORD, raising=False)
    service = MatrixService(old)
    assert await service.connect()
    started, release = asyncio.Event(), asyncio.Event()

    async def stale_read():
        started.set()
        await release.wait()
        raise RuntimeError(f"{PRIVATE} user={USER} password={PASSWORD}")

    monkeypatch.setattr(old, "get_video_status", stale_read)
    task = asyncio.create_task(service.refresh_snapshot())
    await asyncio.wait_for(started.wait(), 1)
    replacement = FakeMatrix()
    service.replace_client(replacement)
    # The new generation already has its own failure reference.
    replacement.connect_error = OSError("new private failure")
    with caplog.at_level(logging.ERROR):
        assert await service.connect() is False
        current_error = service.last_error
        release.set()
        assert await asyncio.wait_for(task, 1) is False
    assert service.client is replacement
    assert service.last_error == current_error and REF.fullmatch(current_error)
    assert service._client_generation == 1 and service._write_generation == 0
    assert not service.connected and service.routing == dict.fromkeys(range(1, 9))
    assert_no_private(service.snapshot())
    assert any(PRIVATE in record.getMessage() for record in caplog.records)
    assert USER not in caplog.text and PASSWORD not in caplog.text


async def test_safe_read_cancellation_propagates_without_error_or_state_change(monkeypatch, caplog):
    matrix = FakeMatrix()
    service = MatrixService(matrix)
    assert await service.connect()
    before = service.snapshot()
    started, cleaned = asyncio.Event(), asyncio.Event()

    async def blocked_read():
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()

    monkeypatch.setattr(matrix, "get_video_status", blocked_read)
    task = asyncio.create_task(service.refresh_snapshot())
    await asyncio.wait_for(started.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert cleaned.is_set()
    assert service.snapshot() == before
    assert service._write_generation == 0 and service._client_generation == 0
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


async def test_default_safe_write_exception_remains_false_and_preserves_state(monkeypatch, caplog):
    matrix = FakeMatrix()
    service = MatrixService(matrix)
    assert await service.connect()
    routing = service.routing
    monkeypatch.setattr(matrix, "recall_preset", AsyncMock(side_effect=RuntimeError(PRIVATE)))
    with caplog.at_level(logging.ERROR):
        assert await service.recall_preset(1) is False
    assert service.routing == routing and service._write_generation == 0
    assert service.connected is matrix.connected is True
    assert service.last_error is None  # Existing connection sync clears the error on an up link.
    assert_no_private(service.snapshot())
    assert any(
        PRIVATE in record.getMessage() and "Matrix recall preset 1 failed" in record.getMessage()
        for record in caplog.records
    )
