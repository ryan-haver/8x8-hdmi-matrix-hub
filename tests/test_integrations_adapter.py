"""UC compatibility client regressions against real aiohttp REST and WS handlers."""

from tests.test_hub_integrations_framework import HubClientHttp, eventually
from tests.test_hub_integrations_framework import contract_server as contract_server


async def test_matrix_api_client_unwraps_real_envelopes(contract_server):
    from integrations.unfolded_circle import MatrixApiClient

    client = MatrixApiClient(contract_server.url, api_key=contract_server.api_key)
    try:
        assert isinstance(client, HubClientHttp)
        assert (await client.get_health())["status"] == "healthy"
        assert (await client.get_status())["routing"]["2"] == 2
        assert (await client.get_full_status())["inputs_inactive"][1] is True
        assert (await client.get_inputs())["inputs"][0] == {
            "number": 1,
            "name": "Source 1",
            "cec_endpoint": "/api/cec/input/1",
        }
        assert (await client.get_outputs())["outputs"][0]["name"] == "TV 1"
        assert (await client.get_presets())["presets"][0]["name"] == "Slot 1"
        assert await client.get_profiles() == [{"id": "movie", "name": "Movie"}]
        assert await client.get_scenes() == [{"id": "evening", "name": "Evening"}]
    finally:
        await client.close()


async def test_matrix_api_client_switch_all_and_query_cycling(contract_server):
    from integrations.unfolded_circle import MatrixApiClient

    client = MatrixApiClient(contract_server.url, api_key=contract_server.api_key)
    try:
        assert await client.switch_all_outputs(8)
        assert contract_server.matrix.state.routing == dict.fromkeys(range(1, 9), 8)
        assert await client.next_input(6)
        assert contract_server.matrix.state.routing[6] == 1
        assert contract_server.matrix.state.routing[1] == 8
        assert await client.previous_input(6)
        assert contract_server.matrix.state.routing[6] == 8
        assert await client.switch_input(4, 3)
        assert await client.power_off()
        assert await client.power_on()
        assert await client.send_cec_input(2, "play")
        assert await client.send_cec_output(3, "power_on")
        assert await client.recall_scene("evening")
        assert await client.recall_profile("movie")
        paths = [path for _, path, _ in contract_server.requests]
        assert "/api/input/next?output=6" in paths
        assert "/api/input/previous?output=6" in paths
    finally:
        await client.close()


async def test_matrix_api_client_ws_subscription(contract_server):
    from integrations.unfolded_circle import MatrixApiClient

    client = MatrixApiClient(contract_server.url, api_key=contract_server.api_key)
    events = []
    try:
        client.on_status_update(events.append)
        assert await client.connect_websocket()
        await eventually(lambda: any(event["event"] == "routing" for event in events))
        await contract_server.emit("routing_change", {"input": 6, "output": 8})
        await eventually(
            lambda: any(event["event"] == "routing" and event["data"]["routing"].get(8) == 6 for event in events)
        )
        client.remove_status_callback(events.append)
        count = len(events)
        await contract_server.emit("routing_change", {"input": 4, "output": 8})
        await eventually(lambda: client._snapshot.routing[8] == 4)
        assert len(events) == count
    finally:
        await client.close()


def test_adapter_is_removed():
    import importlib.util

    assert importlib.util.find_spec("integrations.unfolded_circle.adapter") is None
