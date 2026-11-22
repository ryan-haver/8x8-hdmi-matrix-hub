"""Outage causality through real source startup, SDK sockets and matrix simulator.

The reused UC fixtures run normal subprocess entrypoints; there is no runtime,
SDK or transport double. Projector-only cases below explicitly inject snapshots.
"""

from __future__ import annotations

import asyncio
import json

import pytest

from hub.integrations.unfolded_circle.state import EntityStateProjector
from tests.uc import conftest as uc_fixtures
from tests.uc._helpers import CYCLE, POLL, wait_for
from tests.uc.test_state_sync import STATEFUL, _outage, expected_attributes, mismatches
from tools.uc_remote_sim import UcRemoteSim

uc_log_dir = uc_fixtures.uc_log_dir
uc_simulator = uc_fixtures.uc_simulator
sim = uc_fixtures.sim
uc_hub_factory = uc_fixtures.uc_hub_factory


@pytest.mark.parametrize("complete_observation", [False, True], ids=["first-event", "complete-truth"])
async def test_sdk_readback_before_outage_and_after_recovery(uc_hub_factory, sim, complete_observation):
    hub = await uc_hub_factory(extra_env={"OREI_STATUS_CACHE_TTL": "600"})
    truth = expected_attributes(await sim.state())
    async with UcRemoteSim(hub.uc_url) as remote:
        await remote.attach()
        await remote.wait_event("entity_change", lambda d: d["entity_id"] == "media_player.output_8", timeout=CYCLE)
        if complete_observation:
            async def in_sync():
                return mismatches(await remote.get_entity_states(), truth) == []

            assert await wait_for(in_sync)
        before = {e["entity_id"]: e["attributes"] for e in await remote.get_entity_states()}
        prior_changes = remote.entity_changes()
        since = await _outage(remote, sim)
        await asyncio.sleep(3 * POLL)
        after = {e["entity_id"]: e["attributes"] for e in await remote.get_entity_states()}
        changes = remote.entity_changes(since)
        print(json.dumps({"complete_observation": complete_observation, "before_fault": before,
                          "prior_changes": prior_changes, "after_fault": after, "outage_changes": changes}))
        assert len(before) == len(after) == 74
        for eid, attrs in before.items():
            if eid.startswith(STATEFUL):
                assert after[eid]["state"] == "UNAVAILABLE"
            for key in ("value", "source", "source_list"):
                if key in attrs and attrs[key] not in ("Unknown", ""):
                    assert after[eid][key] == attrs[key], (eid, key, attrs, after[eid])
                    assert all(c["attributes"].get(key, attrs[key]) == attrs[key]
                               for c in changes if c["entity_id"] == eid)
        if complete_observation:
            assert mismatches(await remote.get_entity_states(), truth) == []
            assert all(not any(truth.get(c["entity_id"], {}).get(k, v) != v
                               for k, v in c["attributes"].items()) for c in changes)
        else:
            # A never-observed value can remain unknown; an observed value cannot regress.
            for eid, attrs in after.items():
                if attrs.get("value") == "Unknown":
                    assert before[eid]["value"] == "Unknown"
                    assert not any(c["entity_id"] == eid and c["attributes"].get("value")
                                   not in (None, "Unknown") for c in prior_changes)

        recovery = remote.mark()
        await sim.clear_faults()
        await remote.wait_event("device_state", lambda d: d.get("state") == "CONNECTED",
                                since=recovery, timeout=15)

        async def recovered():
            states = await remote.get_entity_states()
            return not mismatches(states, truth) and all(
                e["attributes"].get("state") != "UNAVAILABLE" for e in states if e["entity_id"].startswith(STATEFUL))

        assert await wait_for(recovered, timeout=CYCLE)


@pytest.mark.parametrize("observed", [None, True, False], ids=["never-observed", "connected", "disconnected"])
def test_partial_snapshot_and_outage_preserve_observed_display(observed):
    projector = EntityStateProjector(compatible=True, include_legacy_sensors=True)
    eid = "sensor.output_1_connected"
    projector.subscribe_entities([eid])
    if observed is not None:
        projector.project_snapshot({"connected": True, "output_displays": {1: observed}})
    value = "Unknown" if observed is None else "Connected" if observed else "Disconnected"
    projector.project_snapshot({"connected": True, "routing": {1: 3}})
    assert projector.projected_attributes(eid)["value"] == value
    # Even supplied stale/false data in a disconnected snapshot must not replace truth.
    projector.project_snapshot({"connected": False, "output_displays": {1: not observed}})
    assert projector.projected_attributes(eid) == {"state": "UNAVAILABLE", "value": value}
    projector.project_snapshot({"connected": True, "output_displays": {1: True}})
    assert projector.projected_attributes(eid) == {"state": "ON", "value": "Connected"}
