"""Tests for the hub core package: MatrixModel, EventBus, NameStore, MatrixService (WP-C3).

BE-16 / UC-08: one name store whose changes reach every subscriber.
BE-26 / D9: port counts come from the MatrixModel (a 4x4 model is exercised).
UC-17: the service owns connection state and the snapshot, independent of any Remote.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import pytest

from hub import __version__
from hub.core import (
    BK404_MODEL,
    BK808_MODEL,
    STANDARD_TOPICS,
    EventBus,
    HubEvent,
    MatrixModel,
    MatrixService,
    NameStore,
    get_matrix_model,
)

# =============================================================================
# Helpers
# =============================================================================


class Recorder:
    """Collects events, optionally filtered by topic."""

    def __init__(self, bus: EventBus, topics: list[str] | None = None) -> None:
        self.events: list[HubEvent] = []
        self.unsubscribe = bus.subscribe(self.events.append, topics)

    def topics(self) -> list[str]:
        return [e.topic for e in self.events]

    def of(self, topic: str) -> list[HubEvent]:
        return [e for e in self.events if e.topic == topic]


class FakeMatrix:
    """In-memory matrix with OreiMatrix's API (the MatrixClient protocol)."""

    def __init__(self, host: str = "192.0.2.100", port: int = 443, size: int = 8) -> None:
        self.host = host
        self.port = port
        self.size = size
        self.connected = False
        self.connect_result = True
        self.connect_error: Exception | None = None
        self.fail_writes = False
        self.fail_video = False
        self.power = 1
        self.allsource = [1] * size + [0]  # the device sends a ninth entry
        self.input_names = [f"Src{i}" for i in range(1, size + 1)] + [""]
        self.output_names = [f"TV{i}" for i in range(1, size + 1)] + [""]
        self.preset_names = [f"Scene{i}" for i in range(1, 9)]
        self.inactive = [1] * size
        self.cables: dict[str, dict[int, bool | None]] = {
            "inputs": dict.fromkeys(range(1, size + 1), True),
            "outputs": dict.fromkeys(range(1, size + 1), True),
        }
        self.output_status: dict[str, Any] = {
            "allconnect": [1] * size,
            "allout": [1] * size,
            "allarc": [0] * size,
            "allaudiomute": [0] * size,
        }
        self.presets: dict[int, list[int]] = {}
        self.calls: list[tuple[str, tuple[Any, ...]]] = []
        self.video_gate: asyncio.Event | None = None

    async def connect(self) -> bool:
        self.calls.append(("connect", ()))
        if self.connect_error is not None:
            raise self.connect_error
        self.connected = self.connect_result
        return self.connect_result

    async def disconnect(self) -> None:
        self.calls.append(("disconnect", ()))
        self.connected = False

    async def get_video_status(self) -> dict[str, Any] | None:
        self.calls.append(("get_video_status", ()))
        snapshot = {
            "power": self.power,
            "allsource": list(self.allsource),
            "allinputname": list(self.input_names),
            "alloutputname": list(self.output_names),
            "allname": list(self.preset_names),
        }
        if self.video_gate is not None:
            await self.video_gate.wait()
        if self.fail_video:
            self.connected = False
            return None
        return snapshot

    async def get_input_status(self, force_refresh: bool = False) -> dict[str, Any] | None:
        return {"inactive": list(self.inactive)}

    async def get_output_status(self, force_refresh: bool = False) -> dict[str, Any] | None:
        return {k: list(v) for k, v in self.output_status.items()}

    async def get_all_cable_status(self, force_refresh: bool = False) -> dict[str, dict[int, bool | None]]:
        return {side: dict(ports) for side, ports in self.cables.items()}

    def _accept(self, name: str, *args: Any) -> bool:
        self.calls.append((name, args))
        return not self.fail_writes

    async def switch_input(self, input_num: int, output_num: int) -> bool:
        if not self._accept("switch_input", input_num, output_num):
            return False
        self.allsource[output_num - 1] = input_num
        return True

    async def switch_input_to_all(self, input_num: int) -> bool:
        if not self._accept("switch_input_to_all", input_num):
            return False
        self.allsource[: self.size] = [input_num] * self.size
        return True

    async def recall_preset(self, preset: int) -> bool:
        if not self._accept("recall_preset", preset):
            return False
        if preset in self.presets:
            self.allsource[: self.size] = self.presets[preset]
        return True

    async def save_preset(self, preset_num: int) -> bool:
        if not self._accept("save_preset", preset_num):
            return False
        self.presets[preset_num] = self.allsource[: self.size]
        return True

    async def power_on(self) -> bool:
        if not self._accept("power_on"):
            return False
        self.power = 1
        return True

    async def power_off(self) -> bool:
        if not self._accept("power_off"):
            return False
        self.power = 0
        return True

    async def set_input_name(self, input_num: int, name: str) -> bool:
        if not self._accept("set_input_name", input_num, name):
            return False
        self.input_names[input_num - 1] = name
        return True

    async def set_output_name(self, output_num: int, name: str) -> bool:
        if not self._accept("set_output_name", output_num, name):
            return False
        self.output_names[output_num - 1] = name
        return True

    async def set_preset_name(self, preset_num: int, name: str) -> bool:
        if not self._accept("set_preset_name", preset_num, name):
            return False
        self.preset_names[preset_num - 1] = name
        return True


@pytest.fixture
def matrix() -> FakeMatrix:
    return FakeMatrix()


@pytest.fixture
def service(matrix: FakeMatrix) -> MatrixService:
    return MatrixService(matrix)


@pytest.fixture
async def connected(service: MatrixService) -> MatrixService:
    assert await service.connect()
    return service


def test_package_version() -> None:
    assert __version__ == "0.3.0"


# =============================================================================
# MatrixModel (BE-26, D9)
# =============================================================================


def test_bk808_is_the_8x8_default() -> None:
    assert (BK808_MODEL.input_count, BK808_MODEL.output_count, BK808_MODEL.preset_count) == (8, 8, 8)
    assert get_matrix_model() is BK808_MODEL
    assert get_matrix_model("") is BK808_MODEL
    assert list(BK808_MODEL.input_range()) == list(range(1, 9))


def test_bk404_has_four_ports_each_way() -> None:
    assert list(BK404_MODEL.input_range()) == [1, 2, 3, 4]
    assert list(BK404_MODEL.output_range()) == [1, 2, 3, 4]
    assert BK404_MODEL.validate_output(4) == 4
    with pytest.raises(ValueError):
        BK404_MODEL.validate_output(5)


@pytest.mark.parametrize("name", ["bk808", "BK-808", "OREI BK-808", "orei_bk808"])
def test_get_matrix_model_accepts_id_and_display_name(name: str) -> None:
    assert get_matrix_model(name) is BK808_MODEL


def test_get_matrix_model_rejects_unknown_names() -> None:
    with pytest.raises(ValueError, match="Unknown matrix model"):
        get_matrix_model("bk1616")


@pytest.mark.parametrize("bad", [0, 9, -1, True, 1.0, "1", None])
def test_validate_rejects_out_of_range_and_non_int(bad: Any) -> None:
    for validate in (BK808_MODEL.validate_input, BK808_MODEL.validate_output, BK808_MODEL.validate_preset):
        with pytest.raises(ValueError):
            validate(bad)


def test_validate_returns_the_port_at_both_ends() -> None:
    assert BK808_MODEL.validate_input(1) == 1
    assert BK808_MODEL.validate_input(8) == 8
    assert BK808_MODEL.validate_preset(8) == 8


def test_model_is_frozen_and_rejects_bad_counts() -> None:
    with pytest.raises(AttributeError):
        BK808_MODEL.input_count = 4  # type: ignore[misc]
    with pytest.raises(ValueError):
        MatrixModel(model_id="x", name="X", input_count=0)


# =============================================================================
# EventBus
# =============================================================================


def test_standard_topics() -> None:
    assert STANDARD_TOPICS == {
        "routing",
        "signal",
        "cable",
        "display",
        "power",
        "names",
        "presets",
        "hub_connection",
    }


def test_publish_reaches_matching_subscribers_only() -> None:
    bus = EventBus()
    everything = Recorder(bus)
    routing_only = Recorder(bus, ["routing"])
    bus.publish("routing", {"x": 1})
    bus.publish("power", {"power": True})
    assert everything.topics() == ["routing", "power"]
    assert routing_only.topics() == ["routing"]
    event = routing_only.events[0]
    assert event.data == {"x": 1}
    assert isinstance(event.timestamp, float) and event.timestamp > 0


def test_a_single_topic_string_is_one_topic() -> None:
    bus = EventBus()
    rec = Recorder(bus, "names")  # type: ignore[arg-type]
    bus.publish("names", {})
    bus.publish("n", {})
    assert rec.topics() == ["names"]


def test_unsubscribe_stops_delivery_and_is_idempotent() -> None:
    bus = EventBus()
    rec = Recorder(bus)
    rec.unsubscribe()
    rec.unsubscribe()
    bus.publish("routing", {})
    assert rec.events == []
    assert bus.subscriber_count == 0


def test_failing_sync_subscriber_does_not_break_others(caplog: pytest.LogCaptureFixture) -> None:
    bus = EventBus()

    def boom(event: HubEvent) -> None:
        raise RuntimeError("subscriber bug")

    bus.subscribe(boom)
    rec = Recorder(bus)
    with caplog.at_level(logging.ERROR):
        bus.publish("power", {"power": False})
    assert rec.topics() == ["power"]
    assert "subscriber bug" in caplog.text


def test_publish_copies_the_data_dict() -> None:
    bus = EventBus()
    rec = Recorder(bus)
    data = {"a": 1}
    bus.publish("routing", data)
    data["a"] = 2
    assert rec.events[0].data == {"a": 1}


async def test_async_subscribers_run_and_failures_are_isolated(caplog: pytest.LogCaptureFixture) -> None:
    bus = EventBus()
    seen: list[str] = []

    async def good(event: HubEvent) -> None:
        await asyncio.sleep(0)
        seen.append(event.topic)

    async def bad(event: HubEvent) -> None:
        raise RuntimeError("async subscriber bug")

    bus.subscribe(bad)
    bus.subscribe(good)
    with caplog.at_level(logging.ERROR):
        bus.publish("signal", {})
        await bus.drain()
    assert seen == ["signal"]
    assert "async subscriber bug" in caplog.text


def test_async_subscriber_without_a_loop_is_dropped_not_crashing(caplog: pytest.LogCaptureFixture) -> None:
    bus = EventBus()

    async def handler(event: HubEvent) -> None:  # pragma: no cover - never runs
        pass

    bus.subscribe(handler)
    rec = Recorder(bus)
    with caplog.at_level(logging.ERROR):
        bus.publish("cable", {})
    assert rec.topics() == ["cable"]
    assert "running event loop" in caplog.text


def test_subscriber_may_unsubscribe_during_delivery() -> None:
    bus = EventBus()
    calls: list[str] = []
    unsub: list[Any] = []

    def once(event: HubEvent) -> None:
        calls.append("once")
        unsub[0]()

    unsub.append(bus.subscribe(once))
    rec = Recorder(bus)
    bus.publish("routing", {})
    bus.publish("routing", {})
    assert calls == ["once"]
    assert len(rec.events) == 2


# =============================================================================
# NameStore (BE-16, UC-08)
# =============================================================================


def test_names_default_to_generic_labels() -> None:
    store = NameStore(BK404_MODEL)
    snap = store.snapshot()
    assert snap["inputs"] == {1: "Input 1", 2: "Input 2", 3: "Input 3", 4: "Input 4"}
    assert snap["outputs"][4] == "Output 4"
    assert snap["presets"][8] == "Preset 8"


def test_device_names_merge_and_extra_entries_are_ignored() -> None:
    bus = EventBus()
    rec = Recorder(bus, ["names"])
    store = NameStore(BK404_MODEL, bus)
    assert store.apply_device_names(
        inputs=["Apple TV", "", "Xbox", "PS5", "terminator"], outputs={2: "Projector", 9: "x"}
    )
    snap = store.snapshot()
    assert snap["inputs"] == {1: "Apple TV", 2: "Input 2", 3: "Xbox", 4: "PS5"}
    assert snap["outputs"][2] == "Projector"
    assert len(rec.events) == 1
    assert rec.events[0].data["source"] == "device"
    assert rec.events[0].data["changes"] == {
        "inputs": {1: "Apple TV", 3: "Xbox", 4: "PS5"},
        "outputs": {2: "Projector"},
    }


def test_user_override_beats_device_name_and_clearing_restores_it() -> None:
    bus = EventBus()
    store = NameStore(bus=bus)
    store.apply_device_names(inputs=["NES"])
    rec = Recorder(bus, ["names"])
    assert store.set_input_name(1, "  Retro  ")
    assert store.input_name(1) == "Retro"
    store.apply_device_names(inputs=["NES 2"])  # masked by the override: no visible change
    assert store.input_name(1) == "Retro"
    assert store.set_input_name(1, None)
    assert store.input_name(1) == "NES 2"
    assert [e.data["changes"] for e in rec.events] == [{"inputs": {1: "Retro"}}, {"inputs": {1: "NES 2"}}]
    assert store.overrides()["inputs"] == {}


def test_unchanged_names_publish_nothing() -> None:
    bus = EventBus()
    store = NameStore(bus=bus)
    store.set_output_name(3, "Kitchen")
    rec = Recorder(bus)
    assert not store.set_output_name(3, "Kitchen")
    assert not store.apply_device_names(outputs=["Output 1"])  # same as the default
    assert rec.events == []


def test_preset_names_and_overrides_from_config() -> None:
    bus = EventBus()
    rec = Recorder(bus, ["names"])
    store = NameStore(BK808_MODEL, bus, overrides={"presets": {2: "Movie Night"}})
    assert store.preset_name(2) == "Movie Night"
    assert store.set_preset_name(3, "Game Day")
    assert rec.events[-1].data["changes"] == {"presets": {3: "Game Day"}}
    assert store.overrides()["presets"] == {2: "Movie Night", 3: "Game Day"}


def test_name_store_validates_ports_and_kinds() -> None:
    store = NameStore(BK404_MODEL)
    with pytest.raises(ValueError):
        store.set_input_name(5, "x")
    with pytest.raises(ValueError):
        store.name("speakers", 1)
    with pytest.raises(TypeError):
        store.apply_device_names(inputs="NES")


def test_set_device_name_drops_the_override() -> None:
    store = NameStore()
    store.set_output_name(1, "Override")
    assert store.set_device_name("outputs", 1, "Living Room")
    assert store.output_name(1) == "Living Room"
    assert store.overrides()["outputs"] == {}


# =============================================================================
# MatrixService (UC-17)
# =============================================================================


async def test_connect_publishes_connection_and_full_snapshot(service: MatrixService, matrix: FakeMatrix) -> None:
    rec = Recorder(service.bus)
    assert await service.connect()
    assert service.connected
    assert rec.topics()[0] == "hub_connection"
    assert rec.events[0].data == {"connected": True, "host": "192.0.2.100", "port": 443, "error": None}
    assert {"routing", "power", "names", "signal", "cable", "display"} <= set(rec.topics())

    snap = service.snapshot()
    assert snap["connected"] is True
    assert snap["routing"] == dict.fromkeys(range(1, 9), 1)
    assert snap["power"] is True
    assert snap["inputs"][3] == "Src3"
    assert snap["outputs"][8] == "TV8"
    assert snap["presets"][1] == "Scene1"
    assert snap["signal"] == dict.fromkeys(range(1, 9), True)
    assert snap["cables"]["outputs"][1] is True
    assert snap["display"][1] == {"connected": True, "enabled": True, "arc": False, "audio_mute": False}
    assert snap["model"]["model_id"] == "bk808"
    assert snap["last_refresh"] is not None


async def test_connect_failure_and_exception(matrix: FakeMatrix) -> None:
    service = MatrixService(matrix)
    rec = Recorder(service.bus)
    matrix.connect_result = False
    assert not await service.connect()
    assert not service.connected
    assert rec.events == []  # was never connected: no transition
    matrix.connect_error = OSError("unreachable")
    assert not await service.connect()
    assert "unreachable" in (service.last_error or "")


async def test_no_host_means_no_connect_attempt() -> None:
    matrix = FakeMatrix(host="")
    service = MatrixService(matrix)
    assert service.host is None
    assert not await service.connect()
    assert matrix.calls == []
    assert service.last_error == "no matrix host configured"


async def test_disconnect_publishes_transition(connected: MatrixService) -> None:
    rec = Recorder(connected.bus, ["hub_connection"])
    await connected.disconnect()
    await connected.disconnect()
    assert not connected.connected
    assert [e.data["connected"] for e in rec.events] == [False]


async def test_link_loss_during_refresh_is_announced(connected: MatrixService, matrix: FakeMatrix) -> None:
    rec = Recorder(connected.bus, ["hub_connection"])
    matrix.fail_video = True
    assert not await connected.refresh_snapshot()
    assert not connected.connected
    assert rec.events[0].data["connected"] is False


async def test_refresh_without_changes_publishes_nothing(connected: MatrixService) -> None:
    rec = Recorder(connected.bus)
    assert await connected.refresh_snapshot()
    assert rec.events == []


async def test_front_panel_change_is_seen_on_refresh(connected: MatrixService, matrix: FakeMatrix) -> None:
    rec = Recorder(connected.bus)
    matrix.allsource[2] = 5
    matrix.power = 0
    matrix.inactive[6] = 0
    matrix.cables["inputs"][7] = False
    matrix.output_status["allconnect"][3] = 0
    await connected.refresh_snapshot()
    by_topic = {e.topic: e.data for e in rec.events}
    assert by_topic["routing"]["changed"] == {3: 5}
    assert by_topic["routing"]["source"] == "refresh"
    assert by_topic["power"] == {"power": False, "source": "refresh"}
    assert by_topic["signal"]["changed"] == {7: False}
    assert by_topic["cable"]["changed"] == {"inputs": {7: False}}
    assert by_topic["display"]["changed"][4]["connected"] is False
    assert connected.routing[3] == 5


async def test_switch_one_output_and_all_outputs(connected: MatrixService, matrix: FakeMatrix) -> None:
    rec = Recorder(connected.bus, ["routing"])
    assert await connected.switch(4, 2)
    assert connected.routing[2] == 4
    assert rec.events[-1].data["changed"] == {2: 4}
    assert rec.events[-1].data["source"] == "switch"
    assert await connected.switch(6)
    assert connected.routing == dict.fromkeys(range(1, 9), 6)
    assert ("switch_input_to_all", (6,)) in matrix.calls


async def test_switch_validates_ports_before_touching_the_matrix(connected: MatrixService, matrix: FakeMatrix) -> None:
    calls_before = len(matrix.calls)
    with pytest.raises(ValueError):
        await connected.switch(9, 1)
    with pytest.raises(ValueError):
        await connected.switch(1, 0)
    assert len(matrix.calls) == calls_before


async def test_rejected_write_changes_nothing(connected: MatrixService, matrix: FakeMatrix) -> None:
    rec = Recorder(connected.bus)
    matrix.fail_writes = True
    assert not await connected.switch(3, 1)
    assert not await connected.set_power(False)
    assert not await connected.rename_port("input", 1, "New")
    assert not await connected.save_preset(1)
    assert connected.routing[1] == 1
    assert connected.power is True
    assert connected.inputs[1] == "Src1"
    assert rec.events == []


async def test_set_power(connected: MatrixService) -> None:
    rec = Recorder(connected.bus, ["power"])
    assert await connected.set_power(False)
    assert connected.power is False
    assert await connected.set_power(False)  # accepted again but no transition
    assert [e.data for e in rec.events] == [{"power": False, "source": "command"}]


async def test_rename_port_reaches_name_store_and_subscribers(connected: MatrixService, matrix: FakeMatrix) -> None:
    connected.names.set_output_name(2, "Old override")
    rec = Recorder(connected.bus, ["names"])
    assert await connected.rename_port("output", 2, "  Patio TV  ")
    assert ("set_output_name", (2, "Patio TV")) in matrix.calls
    assert connected.outputs[2] == "Patio TV"
    assert rec.events[-1].data["changes"] == {"outputs": {2: "Patio TV"}}
    # the next refresh agrees with the device: no further event
    rec.events.clear()
    await connected.refresh_snapshot()
    assert rec.events == []


async def test_rename_validates_kind_name_and_length(connected: MatrixService, matrix: FakeMatrix) -> None:
    with pytest.raises(ValueError):
        await connected.rename_port("preset", 1, "x")
    with pytest.raises(ValueError):
        await connected.rename_port("input", 1, "   ")
    with pytest.raises(ValueError):
        await connected.rename_port("inputs", 9, "x")
    assert await connected.rename_port("inputs", 1, "x" * 40)
    assert connected.inputs[1] == "x" * 32


async def test_rename_preset(connected: MatrixService, matrix: FakeMatrix) -> None:
    rec = Recorder(connected.bus, ["names"])
    assert await connected.rename_preset(5, "Party")
    assert connected.presets[5] == "Party"
    assert rec.events[-1].data["changes"] == {"presets": {5: "Party"}}
    with pytest.raises(ValueError):
        await connected.rename_preset(9, "x")


async def test_save_and_recall_preset_publish_and_refresh(connected: MatrixService, matrix: FakeMatrix) -> None:
    await connected.switch(2, 1)
    rec = Recorder(connected.bus)
    assert await connected.save_preset(3)
    saved = rec.of("presets")[-1].data
    assert saved["action"] == "save" and saved["preset"] == 3 and saved["name"] == "Scene3"
    assert saved["routing"][1] == 2

    await connected.switch(7)
    rec.events.clear()
    assert await connected.recall_preset(3)
    assert rec.topics()[0] == "presets"
    assert rec.events[0].data == {"action": "recall", "preset": 3, "name": "Scene3"}
    routing_events = rec.of("routing")
    assert routing_events and routing_events[-1].data["source"] == "refresh"
    assert connected.routing == {1: 2, **dict.fromkeys(range(2, 9), 1)}  # preset 3, not the switch to 7


async def test_refresh_started_before_a_write_does_not_undo_it(connected: MatrixService, matrix: FakeMatrix) -> None:
    gate = asyncio.Event()
    matrix.video_gate = gate
    refresh = asyncio.create_task(connected.refresh_snapshot())
    await asyncio.sleep(0)  # the refresh has read the (old) routing and waits
    matrix.video_gate = None
    assert await connected.switch(5, 1)
    gate.set()
    assert await refresh
    assert connected.routing[1] == 5


async def test_old_input_name_prefix_is_stripped(matrix: FakeMatrix) -> None:
    matrix.input_names[0] = "IN01-Sega-CD"
    matrix.input_names[1] = "Sega-CD"
    service = MatrixService(matrix)
    await service.connect()
    assert service.inputs[1] == "Sega-CD"
    assert service.inputs[2] == "Sega-CD"


async def test_four_port_model_limits_snapshot_and_validation() -> None:
    matrix = FakeMatrix(size=4)
    service = MatrixService(matrix, model=BK404_MODEL)
    await service.connect()
    snap = service.snapshot()
    assert list(snap["routing"]) == [1, 2, 3, 4]
    assert list(snap["inputs"]) == [1, 2, 3, 4]
    assert list(snap["signal"]) == [1, 2, 3, 4]
    assert list(snap["cables"]["outputs"]) == [1, 2, 3, 4]
    assert list(snap["display"]) == [1, 2, 3, 4]
    with pytest.raises(ValueError):
        await service.switch(5, 1)
    assert await service.switch(4)
    assert service.routing == {1: 4, 2: 4, 3: 4, 4: 4}


async def test_unknown_routing_entries_read_as_none(matrix: FakeMatrix) -> None:
    matrix.allsource = [1, 0, 9, "x", 2]  # short, out of range, garbage
    service = MatrixService(matrix)
    await service.connect()
    assert service.routing == {1: 1, 2: None, 3: None, 4: None, 5: 2, 6: None, 7: None, 8: None}


async def test_best_effort_reads_failing_keep_the_main_snapshot(matrix: FakeMatrix) -> None:
    async def broken(force_refresh: bool = False) -> None:
        raise RuntimeError("telnet down")

    matrix.get_all_cable_status = broken  # type: ignore[assignment,method-assign]
    service = MatrixService(matrix)
    assert await service.connect()
    assert service.routing[1] == 1
    assert service.cables["inputs"][1] is None


async def test_names_store_and_bus_wiring() -> None:
    bus = EventBus()
    names = NameStore(BK808_MODEL, bus)
    service = MatrixService(FakeMatrix(), names=names)
    assert service.bus is bus
    assert service.names is names
    with pytest.raises(ValueError):
        MatrixService(FakeMatrix(), model=BK404_MODEL, names=names)
    with pytest.raises(ValueError):
        MatrixService(FakeMatrix(), names=names, bus=EventBus())
    with pytest.raises(ValueError):
        MatrixService(FakeMatrix(), names=NameStore())


async def test_async_subscriber_sees_service_events(connected: MatrixService) -> None:
    seen: list[dict[str, Any]] = []

    async def on_routing(event: HubEvent) -> None:
        seen.append(event.data)

    connected.bus.subscribe(on_routing, ["routing"])
    await connected.switch(8, 8)
    await connected.bus.drain()
    assert seen and seen[-1]["changed"] == {8: 8}


async def test_snapshot_returns_copies(connected: MatrixService) -> None:
    snap = connected.snapshot()
    snap["routing"][1] = 99
    snap["cables"]["inputs"][1] = False
    snap["display"][1]["connected"] = False
    assert connected.routing[1] == 1
    assert connected.cables["inputs"][1] is True
    assert connected.display[1]["connected"] is True
