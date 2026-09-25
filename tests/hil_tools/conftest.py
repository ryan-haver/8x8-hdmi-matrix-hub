"""Fixtures for the HIL capture tool tests (all against the in-process simulator)."""

from __future__ import annotations

import pytest

from tests.hil_tools.helpers import new_sim


@pytest.fixture
async def sim():
    """A fresh simulator (default state) on ephemeral 127.0.0.1 ports.

    It answers `get routing status` and `preset get`, which the real V1.10.01
    never does (HIL-01), so the capture-tool mechanics tested here do not wait
    out an HTTP timeout per run. Use :func:`device_like_sim` for the real behaviour.
    """
    s = new_sim(unanswered_comheads=frozenset())
    await s.start()
    try:
        yield s
    finally:
        await s.stop()


@pytest.fixture
async def device_like_sim():
    """Like ``sim``, but `get routing status` / `preset get` go unanswered, as on V1.10.01."""
    s = new_sim()
    await s.start()
    try:
        yield s
    finally:
        await s.stop()
