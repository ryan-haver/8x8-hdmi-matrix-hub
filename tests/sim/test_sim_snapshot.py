"""Status snapshot caching against the simulator (BE-03, API-11).

- every status cache expires after OREI_STATUS_CACHE_TTL (they never did);
- concurrent refreshes of one cache share a single request;
- writes invalidate every cache, and a refresh that started before a write
  is neither cached nor joined afterwards.
"""

import asyncio

import pytest


def _http(simulator, comhead: str) -> int:
    return sum(1 for e in simulator.log if e["channel"] == "http" and e["command"] == comhead)


def _telnet(simulator, command: str) -> int:
    return sum(1 for e in simulator.log if e["channel"] == "telnet" and e["command"] == command)


@pytest.fixture
def short_ttl(matrix):
    matrix._status_cache_ttl = 0.2
    return matrix


@pytest.mark.parametrize(
    ("getter", "comhead"),
    [
        ("get_output_status", "get output status"),
        ("get_input_status", "get input status"),
        ("get_status", "get video status"),
    ],
)
async def test_http_caches_expire_after_ttl(short_ttl, simulator, getter, comhead):
    """BE-03: a cache hit within the TTL, a fresh read after it."""
    m = short_ttl
    await m.connect()
    first = await getattr(m, getter)()
    assert await getattr(m, getter)() == first
    assert _http(simulator, comhead) == 1
    await asyncio.sleep(0.25)
    await getattr(m, getter)()
    assert _http(simulator, comhead) == 2


async def test_output_cache_reflects_device_change_after_ttl(short_ttl, simulator):
    """BE-03 end to end: a cable plugged in shows up once the TTL has passed."""
    m = short_ttl
    await m.connect()
    assert (await m.get_output_status())["allconnect"][2] == 0
    await simulator.cable_event("output", 3, True)
    assert (await m.get_output_status())["allconnect"][2] == 0  # still cached
    await asyncio.sleep(0.25)
    assert (await m.get_output_status())["allconnect"][2] == 1


async def test_cable_cache_expires_after_ttl(matrix_with_telnet, simulator):
    m = matrix_with_telnet
    await m.connect()
    m._status_cache_ttl = 0.2
    simulator.log.clear()
    assert (await m.get_all_cable_status())["inputs"][3] is False
    await simulator.cable_event("input", 3, True)
    assert (await m.get_all_cable_status())["inputs"][3] is False  # cached
    await asyncio.sleep(0.25)
    assert (await m.get_all_cable_status())["inputs"][3] is True
    assert _telnet(simulator, "status") == 2


@pytest.mark.parametrize(
    ("getter", "comhead"),
    [
        ("get_output_status", "get output status"),
        ("get_input_status", "get input status"),
        ("get_status", "get video status"),
    ],
)
async def test_concurrent_refreshes_share_one_request(matrix, simulator, getter, comhead):
    await matrix.connect()
    simulator.faults.update({"latency_ms": 50})  # keep the first request in flight
    results = await asyncio.gather(*(getattr(matrix, getter)() for _ in range(5)))
    assert all(r == results[0] for r in results)
    assert _http(simulator, comhead) == 1
    # Forced refreshes that overlap also share one request.
    await asyncio.gather(*(getattr(matrix, getter)(force_refresh=True) for _ in range(5)))
    assert _http(simulator, comhead) == 2


async def test_concurrent_cable_polls_share_one_status(matrix_with_telnet, simulator):
    m = matrix_with_telnet
    await m.connect()
    simulator.log.clear()
    await asyncio.gather(*(m.get_all_cable_status(force_refresh=True) for _ in range(4)))
    assert _telnet(simulator, "status") == 1


async def test_callers_get_independent_copies(matrix):
    await matrix.connect()
    a, b = await asyncio.gather(matrix.get_output_status(), matrix.get_output_status())
    a["allconnect"] = "mutated"
    assert b["allconnect"] != "mutated"
    assert (await matrix.get_output_status())["allconnect"] != "mutated"


async def test_refresh_from_before_invalidation_is_not_joined_or_cached(matrix, simulator):
    await matrix.connect()
    simulator.faults.update({"latency_ms": 100})
    before = asyncio.ensure_future(matrix.get_status(force_refresh=True))
    await asyncio.sleep(0.02)  # in flight
    generation = matrix._cache_generation
    matrix._invalidate_status_caches()  # what every write does
    after = asyncio.ensure_future(matrix.get_status(force_refresh=True))
    await asyncio.gather(before, after)
    assert _http(simulator, "get video status") == 2  # the later caller did not join
    assert matrix._cache_generation == generation + 1
    assert matrix._status_cache is not None  # cached by the post-invalidation refresh only


async def test_write_invalidates_and_is_not_overwritten_by_older_refresh(matrix, simulator):
    """A refresh that started before a write must not repopulate the cache with old data."""
    await matrix.connect()
    simulator.faults.update({"latency_ms": 100})
    stale_read = asyncio.ensure_future(matrix.get_status(force_refresh=True))
    await asyncio.sleep(0.02)  # the read is in flight
    simulator.faults.update({"latency_ms": 0})
    # The write queues behind the in-flight read (one HTTP request at a time)
    # and invalidates the caches when it lands.
    assert await matrix.switch_input(8, 1)
    await stale_read
    assert matrix._status_cache is None  # the pre-write read was not cached
    status = await matrix.get_status()
    assert status["routing"][0] == 8
