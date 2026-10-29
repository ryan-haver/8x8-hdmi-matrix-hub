"""Template verification and anti-drift proof for Flic button integrations (R6).

Compares generated requests and JS SDK snippets against authoritative sources:
- web/js/components/integrations-drawer.js
- web/js/utils/api-copy.js
- docs/FLIC_SETUP.md
- tests/fixtures/flic_replay_r6/template_manifest.json

Exercises actual generated SDK callbacks in Node.js with stubbed buttons/http.
Proves anti-drift detection by mutating temporary copies of generator paths,
request bodies, and gesture clauses.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.validate.clients import FlicClient
from tools.validate.clients.flic import (
    FlicButtonInfo,
    FlicReplayError,
    FlicSdkEngine,
    FlicSdkEvent,
    build_drawer_request,
    generate_flic_sdk_snippet,
    run_flic_driver,
)
from tools.validate.model import act

REPO_ROOT = Path(__file__).resolve().parents[2]
DRAWER_JS = REPO_ROOT / "web" / "js" / "components" / "integrations-drawer.js"
API_COPY_JS = REPO_ROOT / "web" / "js" / "utils" / "api-copy.js"
DOC_FLIC = REPO_ROOT / "docs" / "FLIC_SETUP.md"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "flic_replay_r6"
MANIFEST_JSON = FIXTURES_DIR / "template_manifest.json"
NODE_HARNESS = FIXTURES_DIR / "node_sdk_harness.cjs"


def test_template_manifest_fixture_exists():
    assert MANIFEST_JSON.is_file()
    data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    assert "pre_fix_templates" in data
    assert "post_fix_templates" in data
    assert data["pre_fix_templates"]["switch_all"]["path_template"] == "/api/input/{input}"
    assert data["post_fix_templates"]["switch_all"]["path_template"] == "/api/switch"


def test_drawer_source_switch_all_updated_to_api_switch():
    content = DRAWER_JS.read_text(encoding="utf-8")
    assert "case 'switch_all':" in content
    switch_all_match = re.search(
        r"case 'switch_all':\s*urlPath = ['\"]/api/switch['\"];\s*bodyObj = \{\s*input:\s*config\.inputNum\s*\};",
        content,
    )
    assert switch_all_match is not None, (
        "integrations-drawer.js must route switch_all to /api/switch with JSON input bodyObj"
    )


def test_drawer_source_all_base_requests_match():
    content = DRAWER_JS.read_text(encoding="utf-8")
    assert "case 'preset':" in content
    assert "`/api/preset/${config.presetNum}`" in content
    assert "case 'profile':" in content
    assert "`/api/profile/${config.profileId}/recall`" in content
    assert "case 'switch_output':" in content
    assert "`/api/output/${config.outputNum}/source`" in content
    assert "case 'cycle_input':" in content
    assert "`/api/input/${config.cycleDir}?output=${config.outputNum}`" in content
    assert "case 'volume_control':" in content
    assert "`/api/cec/output/${config.outputNum}/${config.volDir}`" in content
    assert "case 'power':" in content
    assert "`/api/power/${config.powerCmd}`" in content
    assert "case 'cec':" in content
    assert "`/api/cec/${config.cecTargetType}/${config.cecTargetPort}/${config.cecCmd}`" in content
    assert 'url: API_BASE + "/api/integrations/flic/register"' in content


def test_api_copy_js_matches_rest_endpoints():
    content = API_COPY_JS.read_text(encoding="utf-8")
    assert "endpoint: `/api/preset/${preset}`" in content
    assert "endpoint: `/api/profile/${encodeURIComponent(id)}/recall`" in content
    assert "endpoint: '/api/switch'" in content
    assert "endpoint: `/api/input/next?output=${output}`" in content
    assert "endpoint: `/api/input/previous?output=${output}`" in content
    assert "endpoint: `/api/power/${on ? 'on' : 'off'}`" in content
    assert "endpoint: `/api/cec/${targetType}/${port}/${command}`" in content


def test_flic_setup_doc_matches_table():
    doc = DOC_FLIC.read_text(encoding="utf-8")
    assert "/api/preset/{n}" in doc or "/api/preset/1" in doc or "/api/preset/2" in doc
    assert "/api/profile/{id}/recall" in doc
    assert "/api/switch" in doc
    assert "/api/input/next?output=N" in doc or "/api/input/next?output=1" in doc
    assert "/api/input/previous?output=N" in doc or "/api/input/previous?output=1" in doc
    assert "/api/output/{n}/source" in doc or "/api/output/1/source" in doc
    assert "/api/power/on" in doc
    assert "/api/power/off" in doc
    assert "/api/integrations/flic/register" in doc
    assert "X-API-Key: <key>" in doc
    assert "?key=<key>" in doc
    assert "&key=<key>" in doc


# ==========================================
# ANTI-DRIFT PROOF TESTS
# ==========================================


def test_anti_drift_path_mutation_detected(tmp_path: Path):
    """Mutating a generator path in integrations-drawer.js is immediately detected by the bridge."""
    mutated_drawer = tmp_path / "integrations-drawer.js"
    content = DRAWER_JS.read_text(encoding="utf-8")

    # Baseline verification
    _, base_path, _, _, _ = build_drawer_request(act("preset_recall", preset=1))
    assert base_path == "/api/preset/1"

    # Inject path mutation
    mutated_content = content.replace(
        "`/api/preset/${config.presetNum}`",
        "`/api/drifted_preset_v2/${config.presetNum}`",
    )
    mutated_drawer.write_text(mutated_content, encoding="utf-8")

    # Verify bridge reads and detects the drifted path
    _, drifted_path, _, _, _ = build_drawer_request(
        act("preset_recall", preset=1),
        source_path=mutated_drawer,
    )
    assert drifted_path != base_path
    assert drifted_path == "/api/drifted_preset_v2/1"


def test_anti_drift_body_mutation_detected(tmp_path: Path):
    """Mutating request body serialization in integrations-drawer.js is detected."""
    mutated_drawer = tmp_path / "integrations-drawer.js"
    content = DRAWER_JS.read_text(encoding="utf-8")

    # Baseline verification
    _, _, base_body, _, _ = build_drawer_request(act("route_all", input=4))
    assert base_body == {"input": 4}

    # Inject body mutation
    mutated_content = content.replace(
        "bodyObj = { input: config.inputNum };",
        "bodyObj = { input: config.inputNum, drifted_schema: 'v2', extra: true };",
    )
    mutated_drawer.write_text(mutated_content, encoding="utf-8")

    # Verify bridge detects the drifted payload
    _, _, drifted_body, _, _ = build_drawer_request(
        act("route_all", input=4),
        source_path=mutated_drawer,
    )
    assert drifted_body != base_body
    assert drifted_body == {"input": 4, "drifted_schema": "v2", "extra": True}


def test_anti_drift_gesture_condition_mutation_detected(tmp_path: Path):
    """Mutating gesture condition in integrations-drawer.js is detected and prevents execution."""
    mutated_drawer = tmp_path / "integrations-drawer.js"
    content = DRAWER_JS.read_text(encoding="utf-8")

    # Baseline verification
    base_snippet = generate_flic_sdk_snippet(gesture="single")
    assert "obj.isSingleClick" in base_snippet

    # Mutate gesture condition in drawer
    mutated_content = content.replace(
        "gesture === 'single' ? 'obj.isSingleClick'",
        "gesture === 'single' ? 'obj.isCustomDriftedClick'",
    )
    mutated_drawer.write_text(mutated_content, encoding="utf-8")

    # Verify bridge generated snippet reflects mutation
    mutated_snippet = generate_flic_sdk_snippet(gesture="single", source_path=mutated_drawer)
    assert "obj.isCustomDriftedClick" in mutated_snippet
    assert "obj.isSingleClick" not in mutated_snippet

    # Verify event evaluation in Node harness: standard single-click fails to trigger
    harness_input = {
        "script": mutated_snippet,
        "buttons": [{"name": "B1", "bdaddr": "11:22:33"}],
        "events": [
            {
                "eventName": "buttonSingleOrDoubleClickOrHold",
                "payload": {"bdaddr": "11:22:33", "isSingleClick": True},
            }
        ],
    }
    res = run_flic_driver("--harness", harness_input)
    assert res["eventResults"][0]["requestsTriggered"] == 0, (
        "Mutated gesture clause must fail to match standard event payload"
    )


def test_environment_evidence_node_and_sha256():
    """Environment reports actual source/Node and distinguishes stubs from unknown hardware."""
    client = FlicClient()
    env = client.environment()

    assert env["name"] == "flic"
    assert env["transport"] == "aiohttp"
    assert env["sdk_version"] == "unknown"

    # Real Node version (e.g. v24.20.0)
    assert env["node_version"].startswith("v")
    assert "." in env["node_version"]

    # Real source SHA-256 digest
    assert len(env["drawer_source_sha256"]) == 64
    actual_hash = hashlib.sha256(DRAWER_JS.read_bytes()).hexdigest()
    assert env["drawer_source_sha256"] == actual_hash

    assert "used for generated SDK callback replay" in env["node_stubs"]
    assert env["flic_sdk_runtime"].startswith("unknown")
    assert env["physical_buttons"].startswith("unknown")


# ==========================================
# NODE SDK HARNESS & CALLBACK VERIFICATION
# ==========================================


@pytest.mark.parametrize("mutation", ["path", "body"])
def test_startup_request_consumes_actual_source_and_detects_drift(tmp_path, mutation):
    buttons = [FlicButtonInfo("Kitchen", "aa:bb", "SN-1")]
    baseline = FlicSdkEngine(origin="http://localhost:8080").startup_request(buttons)
    content = DRAWER_JS.read_text(encoding="utf-8")
    if mutation == "path":
        changed = content.replace('/api/integrations/flic/register', '/api/integrations/flic/drifted')
    else:
        changed = content.replace('JSON.stringify({buttons: buttons})', 'JSON.stringify({buttons: buttons, revision: 9})')
    assert changed != content
    source = tmp_path / "mutated.js"
    source.write_text(changed, encoding="utf-8")
    actual = FlicSdkEngine(origin="http://localhost:8080", source_path=source).startup_request(buttons)
    assert actual != baseline
    assert actual["body"]["buttons"] == [{"name": "Kitchen", "bdaddr": "aa:bb", "serial": "SN-1"}]
    if mutation == "path":
        assert actual["url"] == "http://localhost:8080/api/integrations/flic/drifted"
    else:
        assert actual["body"]["revision"] == 9


@pytest.mark.parametrize("mutation, message", [
    ("duplicate", "captured 2"), ("missing", "captured 0"),
    ("body", "Malformed SDK startup registration"), ("json", "Malformed SDK JSON"),
    ("method", "Malformed SDK HTTP"),
])
def test_startup_rejects_actual_multiplicity_and_malformed_requests(tmp_path, mutation, message):
    content = DRAWER_JS.read_text(encoding="utf-8")
    if mutation == "duplicate":
        # Invoke registration twice within the generated SDK script.
        content = content.replace('    http.makeRequest({\n        url: API_BASE + "/api/integrations/flic/register",',
                                  '    for (var repeat = 0; repeat < 2; repeat++) http.makeRequest({\n'
                                  '        url: API_BASE + "/api/integrations/flic/register",')
    elif mutation == "missing":
        content = content.replace('buttonManager.getButtons().map', 'buttonManager.nonexistent().map')
    elif mutation == "body":
        content = content.replace('JSON.stringify({buttons: buttons})', 'JSON.stringify({buttons: "invalid"})')
    elif mutation == "json":
        content = content.replace('JSON.stringify({buttons: buttons})', '"invalid-json"')
    else:
        content = content.replace('method: "POST",\n        headers:', 'method: "GET",\n        headers:')
    source = tmp_path / "invalid.js"
    source.write_text(content, encoding="utf-8")
    engine = FlicSdkEngine(origin="http://localhost:8080", source_path=source)
    with pytest.raises(FlicReplayError, match=message):
        engine.startup_request([])


def test_event_rejects_all_actual_requests_instead_of_selecting_first():
    engine = FlicSdkEngine(origin="http://localhost:8080")
    engine.snippet += '''
buttonManager.on("buttonSingleOrDoubleClickOrHold", function(obj) {
    http.makeRequest({url: API_BASE + "/api/preset/2", method: "POST"}, function() {});
});'''
    capture = run_flic_driver("--harness", {"script": engine.snippet, "events": [{
        "eventName": "buttonSingleOrDoubleClickOrHold", "payload": {"isSingleClick": True},
    }]})
    assert capture["eventResults"][0]["requestsTriggered"] == 2
    assert len(capture["eventResults"][0]["requests"]) == 2
    with pytest.raises(FlicReplayError, match="captured 2"):
        engine.evaluate_event(FlicSdkEvent("buttonSingleOrDoubleClickOrHold", "aa:bb", is_single_click=True), {})


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js runtime not found on PATH")
def test_node_sdk_harness_single_click_and_filter(tmp_path: Path):
    """Exercise generated JavaScript in real Node.js with stubbed buttons/http."""
    snippet = generate_flic_sdk_snippet(
        origin="http://127.0.0.1:8080",
        button_type="button",
        button_identifier="Kitchen Button",
        target_type="switch_output",
        gesture="single",
        output_num=1,
        input_num=2,
    )
    script_file = tmp_path / "kitchen_single.js"
    script_file.write_text(snippet, encoding="utf-8")

    buttons = [
        {"name": "Kitchen Button", "bdaddr": "11:22:33:44:55:66", "serial": "FLIC-001"},
        {"name": "Living Room", "bdaddr": "aa:bb:cc:dd:ee:ff", "serial": "FLIC-002"},
    ]
    events = [
        # 1. Matching button, matching single click -> 1 request
        {
            "eventName": "buttonSingleOrDoubleClickOrHold",
            "payload": {"bdaddr": "11:22:33:44:55:66", "isSingleClick": True, "isDoubleClick": False, "isHold": False},
        },
        # 2. Matching button, non-matching double click -> 0 requests
        {
            "eventName": "buttonSingleOrDoubleClickOrHold",
            "payload": {"bdaddr": "11:22:33:44:55:66", "isSingleClick": False, "isDoubleClick": True, "isHold": False},
        },
        # 3. Non-matching button, matching single click -> 0 requests
        {
            "eventName": "buttonSingleOrDoubleClickOrHold",
            "payload": {"bdaddr": "aa:bb:cc:dd:ee:ff", "isSingleClick": True, "isDoubleClick": False, "isHold": False},
        },
    ]

    harness_input = {
        "scriptPath": str(script_file),
        "buttons": buttons,
        "events": events,
    }
    proc = subprocess.run(
        ["node", str(NODE_HARNESS)],
        input=json.dumps(harness_input),
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    res = json.loads(proc.stdout)

    # 1 startup registration request
    assert res["startupRequestsCount"] == 1
    reg_req = res["allRequests"][0]
    assert reg_req["url"] == "http://127.0.0.1:8080/api/integrations/flic/register"
    assert reg_req["method"] == "POST"
    reg_body = json.loads(reg_req["content"])
    assert len(reg_body["buttons"]) == 2
    assert reg_body["buttons"][0]["name"] == "Kitchen Button"

    # Event 1: matching single click triggered 1 request
    assert res["eventResults"][0]["requestsTriggered"] == 1
    action_req = res["eventResults"][0]["requests"][0]
    assert action_req["url"] == "http://127.0.0.1:8080/api/output/1/source"
    assert json.loads(action_req["content"]) == {"input": 2}

    # Event 2: double click triggered 0 requests
    assert res["eventResults"][1]["requestsTriggered"] == 0

    # Event 3: wrong button triggered 0 requests
    assert res["eventResults"][2]["requestsTriggered"] == 0


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js runtime not found on PATH")
def test_node_sdk_harness_duo_and_twist(tmp_path: Path):
    # Duo left double click
    snippet_duo = generate_flic_sdk_snippet(
        origin="http://127.0.0.1:8080",
        button_type="duo",
        button_identifier="",
        target_type="preset",
        gesture="left_double",
        preset_num=3,
    )
    script_duo = tmp_path / "duo.js"
    script_duo.write_text(snippet_duo, encoding="utf-8")

    duo_events = [
        # Left double click (buttonNumber 0, isDoubleClick true) -> 1 request
        {
            "eventName": "buttonSingleOrDoubleClickOrHold",
            "payload": {"bdaddr": "00:11:22:33:44:55", "buttonNumber": 0, "isSingleClick": False, "isDoubleClick": True, "isHold": False},
        },
        # Right double click (buttonNumber 1) -> 0 requests
        {
            "eventName": "buttonSingleOrDoubleClickOrHold",
            "payload": {"bdaddr": "00:11:22:33:44:55", "buttonNumber": 1, "isSingleClick": False, "isDoubleClick": True, "isHold": False},
        },
    ]

    proc_duo = subprocess.run(
        ["node", str(NODE_HARNESS)],
        input=json.dumps({"scriptPath": str(script_duo), "buttons": [], "events": duo_events}),
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    res_duo = json.loads(proc_duo.stdout)
    assert res_duo["eventResults"][0]["requestsTriggered"] == 1
    assert res_duo["eventResults"][0]["requests"][0]["url"] == "http://127.0.0.1:8080/api/preset/3"
    assert res_duo["eventResults"][1]["requestsTriggered"] == 0

    # Twist rotate clockwise
    snippet_twist = generate_flic_sdk_snippet(
        origin="http://127.0.0.1:8080",
        button_type="twist",
        target_type="cycle_input",
        gesture="rotate_cw",
        cycle_dir="next",
        output_num=1,
    )
    script_twist = tmp_path / "twist.js"
    script_twist.write_text(snippet_twist, encoding="utf-8")

    twist_events = [
        # Rotate CW (direction > 0) -> 1 request
        {"eventName": "buttonRotate", "payload": {"bdaddr": "00:11:22:33:44:55", "direction": 1}},
        # Rotate CCW (direction < 0) -> 0 requests
        {"eventName": "buttonRotate", "payload": {"bdaddr": "00:11:22:33:44:55", "direction": -1}},
    ]

    proc_twist = subprocess.run(
        ["node", str(NODE_HARNESS)],
        input=json.dumps({"scriptPath": str(script_twist), "buttons": [], "events": twist_events}),
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    res_twist = json.loads(proc_twist.stdout)
    assert res_twist["eventResults"][0]["requestsTriggered"] == 1
    assert res_twist["eventResults"][0]["requests"][0]["url"] == "http://127.0.0.1:8080/api/input/next?output=1"
    assert res_twist["eventResults"][1]["requestsTriggered"] == 0
