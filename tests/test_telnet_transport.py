"""TelnetClient transport behaviour without a network (fake streams).

BE-28: EOF must stop the push listener (it used to spin on ``b""``).
BE-29: EOF is detected by ``_send_raw``; truncated ``status`` dumps give
       ``None`` (unknown) for missing ports, not ``False``.
BE-11: the socket is closed on error paths.
"""

import asyncio

import pytest

import telnet_client
from _telnet_proto import is_acknowledged, is_response_complete, response_error
from telnet_client import CommandError, ConnectionLostError, MatrixStatus, TelnetClient, TelnetState


class FakeWriter:
    def __init__(self) -> None:
        self.written = bytearray()
        self.closed = False

    def write(self, data: bytes) -> None:
        if self.closed:
            raise ConnectionResetError("closed")
        self.written += data

    async def drain(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        pass


def make_client(reader: asyncio.StreamReader) -> tuple[TelnetClient, FakeWriter]:
    client = TelnetClient("127.0.0.1", 2323)
    writer = FakeWriter()
    client._reader = reader
    client._writer = writer  # type: ignore[assignment]
    client._state = TelnetState.CONNECTED
    return client, writer


@pytest.fixture
def no_reconnect(monkeypatch):
    calls: list[int] = []
    monkeypatch.setattr(TelnetClient, "_schedule_reconnect", lambda self: calls.append(1))
    return calls


async def test_read_available_raises_on_eof():
    reader = asyncio.StreamReader()
    reader.feed_eof()
    client, _ = make_client(reader)
    with pytest.raises(ConnectionLostError):
        await client._read_available(timeout=0.1)


async def test_read_available_timeout_returns_empty():
    client, _ = make_client(asyncio.StreamReader())
    assert await client._read_available(timeout=0.05) == ""


async def test_push_listener_stops_on_eof_and_schedules_reconnect(no_reconnect):
    reader = asyncio.StreamReader()
    client, writer = make_client(reader)
    states: list[TelnetState] = []
    client._on_connection_change = states.append

    listener = asyncio.ensure_future(client._listen_for_push())
    await asyncio.sleep(0.05)
    reader.feed_eof()
    # Before the fix this never returned (and never yielded to the loop).
    await asyncio.wait_for(listener, 1)

    assert client.connected is False
    assert states == [TelnetState.DISCONNECTED]
    assert writer.closed and client._writer is None
    assert no_reconnect == [1]


async def test_push_listener_eof_after_disconnect_does_not_reconnect(no_reconnect):
    reader = asyncio.StreamReader()
    client, _ = make_client(reader)
    client._closing = True  # disconnect() in progress
    reader.feed_eof()
    await asyncio.wait_for(client._listen_for_push(), 1)
    assert client.connected is False
    assert no_reconnect == []


async def test_push_listener_still_dispatches_before_eof(no_reconnect):
    reader = asyncio.StreamReader()
    client, _ = make_client(reader)
    seen: list[MatrixStatus] = []
    client._on_status_update = seen.append
    reader.feed_data(b"hdmi output 2: disconnect\r\n")
    reader.feed_eof()
    await asyncio.wait_for(client._listen_for_push(), 1)
    assert seen and seen[0].outputs[2].connected is False


async def test_send_raw_detects_eof_mid_response(no_reconnect, monkeypatch):
    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", 5.0)
    reader = asyncio.StreamReader()
    client, writer = make_client(reader)
    reader.feed_data(b"power on\r\nbeep on\r\n")  # half a status dump ...
    reader.feed_eof()  # ... then the matrix hangs up

    loop = asyncio.get_running_loop()
    start = loop.time()
    with pytest.raises(CommandError):
        await client._send_raw("status")
    assert loop.time() - start < 1.0, "EOF must not wait for COMMAND_TIMEOUT"
    assert client.state is TelnetState.DISCONNECTED
    assert writer.closed and client._writer is None
    assert no_reconnect == [1]


async def test_send_raw_when_disconnected_raises():
    client = TelnetClient("127.0.0.1", 2323)
    with pytest.raises(telnet_client.ConnectionError):
        await client._send_raw("status")


def test_truncated_status_dump_marks_missing_ports_unknown():
    client = TelnetClient("127.0.0.1", 2323)
    dump = (
        "power on\r\nbeep on\r\n"
        "hdmi input 1: connect\r\nhdmi input 2: disconnect\r\n"
        "hdmi input 3: conn"  # cut off here
    )
    cables = TelnetClient.connections_from_status(client._parse_status_response(dump))
    assert cables["inputs"] == {1: True, 2: False, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}
    assert set(cables["outputs"].values()) == {None}


def test_empty_status_dump_is_all_unknown():
    client = TelnetClient("127.0.0.1", 2323)
    cables = TelnetClient.connections_from_status(client._parse_status_response(""))
    assert set(cables["inputs"].values()) == {None}
    assert set(cables["outputs"].values()) == {None}


async def test_get_all_connections_uses_one_status(monkeypatch):
    client = TelnetClient("127.0.0.1", 2323)
    sent: list[str] = []

    async def fake_send_raw(command: str) -> str:
        sent.append(command)
        return "hdmi input 1: connect\r\nhdmi output 1: disconnect\r\nmac address: 00:11\r\n"

    monkeypatch.setattr(client, "_send_raw", fake_send_raw)
    cables = await client.get_all_connections()
    assert sent == ["status"]
    assert cables["inputs"][1] is True and cables["outputs"][1] is False and cables["inputs"][2] is None


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ("hdmi output 3: connect\r\n", True),
        ("hdmi output 3: disconnect\r\n", False),
        ("", None),
        ("E01\r\n", None),
    ],
)
async def test_link_query_unknown_when_no_answer(monkeypatch, response, expected):
    client = TelnetClient("127.0.0.1", 2323)

    async def fake_send_raw(command: str) -> str:
        return response

    monkeypatch.setattr(client, "_send_raw", fake_send_raw)
    assert await client.get_output_connection(3) is expected


# =============================================================================
# BE-07: completion detection and E00/E01 semantics
# =============================================================================



@pytest.mark.parametrize(
    ("command", "response", "complete"),
    [
        # set commands complete on their acknowledgement ...
        ("s cec in 1 on", "cec in 1 on\r\n", True),
        ("s output 2 in source 3", "output2->input3\r\n", True),
        ("s save preset 1", "save to preset 1\r\n", True),
        # ... not on a bare echo of the command, nor on a partial line
        ("s cec in 1 on", "s cec in 1 on\r\n", False),
        ("s cec in 1 on", "s cec in 1 on!\r\n", False),
        ("s cec in 1 on", "cec in 1", False),
        # error codes complete every command
        ("s cec in 1 bogus", "E01\r\n", True),
        ("power 1", "E00\r\n", True),
        ("status", "power on\r\nE00\r\n", True),
        # status waits for its last line
        ("status", "power on\r\nhdmi input 1: connect\r\n", False),
        ("status", "power on\r\nmac address: 00:11:22:33:44:55\r\n", True),
        ("status", "power on\r\nmac address: 00:11:22:33:44:55", True),
        ("status", "power on\r\nmac address: 00:11:2", False),
        # link queries wait for connect/disconnect
        ("r link in 3", "hdmi input 3: disconnect\r\n", True),
        ("r link in 3", "hdmi input 3", False),
        # other reads complete on their first line (r type has no colon)
        ("r type", "BK-808\r\n", True),
        ("r fw version", "fw version: V1.10.02\r\n", True),
        ("status", "", False),
    ],
)
def test_is_response_complete(command, response, complete):
    assert is_response_complete(response, command) is complete


def test_error_codes_are_failures():
    assert response_error("E00\r\n") == "E00"
    assert response_error("s cec in 1 on\r\nE01\r\n") == "E01"
    assert response_error("E01") == "E01"
    assert response_error("cec in 1 on\r\n") is None
    assert not is_acknowledged("E00\r\n", "power 1")
    assert not is_acknowledged("", "s cec in 1 on")  # timed out, no answer
    assert not is_acknowledged("s cec in 1 on\r\n", "s cec in 1 on")  # echo only
    assert is_acknowledged("cec in 1 on\r\n", "s cec in 1 on")


async def test_set_command_returns_on_ack_not_timeout(monkeypatch):
    """A successful set command returns as soon as the ack line arrives."""
    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", 5.0)
    reader = asyncio.StreamReader()
    client, writer = make_client(reader)
    reader.feed_data(b"cec hdmi out 1 on\r\n")
    loop = asyncio.get_running_loop()
    start = loop.time()
    assert await client.cec_output_power_on(1) is True
    assert loop.time() - start < 1.0
    assert bytes(writer.written) == b"s cec hdmi out 1 on!\r\n"


@pytest.mark.parametrize("answer", [b"E00\r\n", b"E01\r\n"])
async def test_set_command_error_code_is_failure(monkeypatch, answer):
    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", 5.0)
    reader = asyncio.StreamReader()
    client, _ = make_client(reader)
    reader.feed_data(answer)
    loop = asyncio.get_running_loop()
    start = loop.time()
    assert await client.switch_input(3, 2) is False
    assert loop.time() - start < 1.0
    assert client.connected  # an error answer is not a connection problem


async def test_set_command_without_answer_is_failure(monkeypatch):
    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", 0.2)
    client, _ = make_client(asyncio.StreamReader())
    assert await client.save_preset(2) is False
    assert client.connected
