"""TST-19: one CI run must meet each scenario's transport/read preconditions."""

import asyncio

import pytest

from tools.validate.runner import Runner, RunOptions
from tools.validate.scenarios import discover
from tools.validate.stack import HubProcess


def test_mixed_http_and_telnet_cec_scenarios_pass_in_one_run(tmp_path):
    scenarios = discover()
    chosen = [scenarios[name] for name in (
        "cec_controls.input_1_power_on",
        "cec_telnet.input_1_power_on",
        "cec_telnet.input_interrupted_power_on",
        "cec_telnet.input_interrupted_power_off",
        "cec_controls.output_1_power_on",
    )]
    runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path))
    outcomes = asyncio.run(runner.run(chosen))
    assert all(outcome.status == "pass" for outcome in outcomes), [
        (outcome.scenario, outcome.failed_checks) for outcome in outcomes if outcome.status != "pass"
    ]


def test_simulator_reads_are_ready_and_faults_reach_the_measured_read(tmp_path):
    scenarios = discover()
    chosen = [scenarios[name] for name in (
        "contracts.cables", "profile_state.capture_output_read_failure",
    )]
    runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path))
    outcomes = asyncio.run(runner.run(chosen))
    assert all(outcome.status == "pass" for outcome in outcomes), [
        (outcome.scenario, outcome.failed_checks) for outcome in outcomes if outcome.status != "pass"
    ]


@pytest.mark.parametrize("external", [False, True])
def test_operator_hub_settings_are_not_changed(tmp_path, external):
    runner = Runner(RunOptions(target="sim" if external else "hardware", out_dir=tmp_path))
    runner.hub = HubProcess(matrix_host="unused", matrix_port=443, telnet_port=23, log_dir=tmp_path,
                            external_url="http://unused" if external else None,
                            extra_env={"OREI_USE_TELNET_CEC": "false", "OREI_STATUS_CACHE_TTL": "5"})
    scenario = discover()["cec_telnet.input_1_power_on"]
    runner._use_scenario_environment(scenario)
    assert runner.hub.extra_env == {"OREI_USE_TELNET_CEC": "false", "OREI_STATUS_CACHE_TTL": "5"}
    assert runner.hub.starts == 0
