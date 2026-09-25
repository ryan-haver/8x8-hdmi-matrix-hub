"""Connection handshake and driver information (audit §7 case 1).

Message shapes per core-api integration-api/UCR-integration-asyncapi.yaml and
doc/integration-driver/websocket.md (pinned, docs/vendor/UNFOLDED_CIRCLE.md).
"""

from __future__ import annotations

import socket

from tools.uc_remote_sim import UcRemoteSim
from tools.validate.stack import HubProcess

from ._helpers import DRIVER_JSON, known_bug


async def test_connection_is_authenticated_without_a_token(uc_hub: HubProcess) -> None:
    """No authentication: the driver sends `authentication` (code 200) right after the connection opens."""
    remote = UcRemoteSim(uc_hub.uc_url)
    try:
        auth = await remote.connect()
        assert auth["kind"] == "resp"
        assert auth["msg"] == "authentication"
        assert auth["code"] == 200
        assert auth["req_id"] == 0
        # the first message on the connection, before anything was asked
        assert remote.messages[0].data is auth
    finally:
        await remote.close()


async def test_driver_version_matches_driver_json(uc_hub: HubProcess) -> None:
    async with UcRemoteSim(uc_hub.uc_url) as remote:
        resp = await remote.get_driver_version()
    assert resp["msg"] == "driver_version" and resp["code"] == 200
    assert resp["msg_data"] == {
        "name": DRIVER_JSON["name"]["en"],
        "version": {"api": DRIVER_JSON["min_core_api"], "driver": DRIVER_JSON["version"]},
    }


async def test_driver_metadata_matches_driver_json(uc_hub: HubProcess) -> None:
    """Everything the Remote shows in its integration list and setup form comes from driver.json."""
    async with UcRemoteSim(uc_hub.uc_url) as remote:
        resp = await remote.get_driver_metadata()
    assert resp["msg"] == "driver_metadata" and resp["code"] == 200
    meta = resp["msg_data"]
    # ucapi rewrites an empty driver_url (see the UC-03 test); every other field is driver.json verbatim.
    assert {k: v for k, v in meta.items() if k != "driver_url"} == \
        {k: v for k, v in DRIVER_JSON.items() if k != "driver_url"}
    assert meta["setup_data_schema"]["settings"][1]["id"] == "host"


@known_bug("UC-03", "driver_url \"\" makes ucapi advertise ws://<socket hostname>:<port> (the container id in "
           "bridge-mode Docker) instead of leaving the URL to mDNS or a configured UC_DRIVER_URL")
async def test_driver_metadata_does_not_advertise_the_socket_hostname(uc_hub: HubProcess) -> None:
    async with UcRemoteSim(uc_hub.uc_url) as remote:
        meta = (await remote.get_driver_metadata())["msg_data"]
    assert meta.get("driver_url", "") in ("", None) or socket.gethostname() not in meta["driver_url"]


async def test_connect_event_reports_device_state(uc_hub: HubProcess, uc_remote_factory) -> None:
    """`connect` (cat DEVICE) -> the driver connects its device and sends `device_state`."""
    remote = await uc_remote_factory(attach=False)
    since = remote.mark()
    await remote.send_connect()
    event = await remote.wait_event("device_state", since=since, timeout=15)
    assert event.data["cat"] == "DEVICE"
    assert event.msg_data == {"state": "CONNECTED"}
    assert (await remote.get_device_state())["msg_data"] == {"state": "CONNECTED"}


async def test_unknown_request_does_not_break_the_connection(uc_hub: HubProcess, uc_remote_factory) -> None:
    """Newer Remotes send requests ucapi 0.5.1 does not know (spec 0.16: get_runtime_info, ...).

    ucapi 0.5.1 drops them without an answer; whatever a later ucapi does, the connection must stay usable.
    """
    remote = await uc_remote_factory(attach=False)
    try:
        resp = await remote.request("get_runtime_info", timeout=1.5)
        assert resp["req_id"] > 0
    except TimeoutError:
        pass  # ucapi 0.5.1: no response
    assert not remote.closed
    assert (await remote.get_driver_version())["code"] == 200
