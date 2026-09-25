"""The entity set the Remote sees (audit §3 inventory, §7 case 3), and restore after a restart.

``golden/entities.json`` pins the exact available entities today: id, type,
features, device class and simple commands (74 entities). Entity ids are what
users' activities and macros reference, so any change to this set (WP-B2/B3,
the DI-9 entity model) must be deliberate: regenerate the file with

    UPDATE_UC_GOLDEN=1 pytest tests/uc/test_entities.py -k golden

and list the removed/renamed ids in the PR and the release notes (audit §4.3).
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from tools.uc_remote_sim import UcRemoteSim
from tools.validate.device import SimDevice
from tools.validate.stack import HubProcess

from ._helpers import INPUT_NAMES, OUTPUT_NAMES

GOLDEN = Path(__file__).parent / "golden" / "entities.json"


def _golden_view(entity: dict[str, Any]) -> dict[str, Any]:
    view = {
        "entity_id": entity["entity_id"],
        "entity_type": entity["entity_type"],
        "features": entity.get("features") or [],
    }
    if entity.get("device_class"):
        view["device_class"] = entity["device_class"]
    commands = (entity.get("options") or {}).get("simple_commands")
    if commands:
        view["simple_commands"] = commands
    return view


def _name(entity: dict[str, Any]) -> str:
    name = entity.get("name")
    return name.get("en", "") if isinstance(name, dict) else str(name)


async def test_available_entities_match_golden(uc_remote: UcRemoteSim) -> None:
    entities = [_golden_view(e) for e in await uc_remote.get_available_entities()]
    entities.sort(key=lambda e: e["entity_id"])
    if os.environ.get("UPDATE_UC_GOLDEN"):
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(json.dumps({"count": len(entities), "entities": entities}, indent=2) + "\n",
                          encoding="utf-8")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    ids = [e["entity_id"] for e in entities]
    golden_ids = [e["entity_id"] for e in golden["entities"]]
    assert sorted(set(ids) - set(golden_ids)) == [], "new entity ids (update golden deliberately)"
    assert sorted(set(golden_ids) - set(ids)) == [], "entity ids disappeared (breaks users' activities)"
    assert entities == golden["entities"]
    assert len(entities) == golden["count"] == 74


async def test_entity_counts_per_type(uc_remote: UcRemoteSim) -> None:
    """Audit §3: 1 matrix remote, 8 preset buttons, 16 CEC remotes, 8 media players, 1 switch, 40 sensors."""
    entities = await uc_remote.get_available_entities()
    counts: dict[str, int] = {}
    for e in entities:
        counts[e["entity_type"]] = counts.get(e["entity_type"], 0) + 1
    assert counts == {"remote": 17, "button": 8, "media_player": 8, "switch": 1, "sensor": 40}


async def test_entity_names_come_from_the_matrix(uc_remote: UcRemoteSim) -> None:
    """Port names are read from the matrix (seed state), both for the entity names and the source list."""
    by_id = {e["entity_id"]: e for e in await uc_remote.get_available_entities()}
    for n, name in enumerate(INPUT_NAMES, 1):
        assert _name(by_id[f"remote.input_{n}_cec"]) == f"{name} CEC"
        assert _name(by_id[f"sensor.input_{n}_signal"]) == f"{name} Signal"
    for n, name in enumerate(OUTPUT_NAMES, 1):
        assert _name(by_id[f"media_player.output_{n}"]) == name
        # audit §3: "{output} TV", which reads "TV TV" for an output named TV (UC-12 / DI-9 naming)
        assert _name(by_id[f"remote.output_{n}_cec"]) == f"{name} TV"
    state = await uc_remote.entity_state("media_player.output_1")
    assert state is not None
    assert state["source_list"] == INPUT_NAMES


async def test_restore_after_restart(uc_hub: HubProcess, uc_remote_factory, sim: SimDevice) -> None:
    """A restarted driver restores its configuration: same ids, and a Remote that only re-subscribes
    (no new setup) can control the matrix."""
    first = await uc_remote_factory()
    ids = sorted(e["entity_id"] for e in await first.get_available_entities())
    await first.close()

    await asyncio.to_thread(uc_hub.restart)
    remote = await uc_remote_factory(attach=False)
    since = remote.mark()
    await remote.send_connect()
    await remote.wait_event("device_state", since=since, timeout=15)
    # A Remote re-subscribes its configured entities after a driver restart, without a new setup.
    await remote.subscribe_events(["media_player.output_1"])
    resp = await remote.select_source("media_player.output_1", INPUT_NAMES[4])
    assert resp["code"] == 200
    assert (await sim.state())["outputs"][0]["source"] == 5
    assert sorted(e["entity_id"] for e in await remote.get_available_entities()) == ids
