"""Fixtures for the HIL capture tool tests (all against the in-process simulator)."""

from __future__ import annotations

import pytest

from tests.hil_tools.helpers import new_sim


@pytest.fixture
async def sim():
    """A fresh simulator (default state) on ephemeral 127.0.0.1 ports."""
    s = new_sim()
    await s.start()
    try:
        yield s
    finally:
        await s.stop()
