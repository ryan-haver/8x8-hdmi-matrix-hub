"""HIL capture tool, read mode and redaction, against the simulator."""

from __future__ import annotations

import json

import pytest

from tests.hil_tools.helpers import FW, load, make_opts, new_sim, quiet
from tools.hil.capture import cli, run_capture
from tools.hil.capture import fixtures as fx
from tools.hil.capture.catalog import HTTP_READS, TELNET_READS
from tools.hil.capture.fixtures import REDACTED, RecordIds, firmware_folder_name, response_body
from tools.simulator import DeviceState
from tools.simulator.http_commands import dispatch
from tools.simulator.telnet_commands import banner, handle


async def test_read_mode_records_every_read_byte_for_byte(sim, tmp_path):
    code, cap = await run_capture(make_opts(sim, tmp_path / "{firmware}"), quiet())
    assert code == cli.EXIT_OK, cap.errors
    root = tmp_path / FW
    assert cap.writer.root == root

    for spec in HTTP_READS:
        record = load(root, RecordIds.http_read(spec.slug))
        (ex,) = record["exchanges"]
        expected = dispatch(sim.state.copy(), dict(spec.payload)).response
        assert response_body(ex) == json.dumps(expected, separators=(",", ":")).encode(), spec.slug
        assert ex["request"]["json"] == spec.payload
        assert ex["response"]["status"] == 200
        assert any(h.lower().startswith("content-type: text/plain") for h in ex["response"]["headers"])
    for spec in TELNET_READS:
        (ex,) = load(root, RecordIds.telnet_read(spec.slug))["exchanges"]
        assert response_body(ex) == handle(sim.state.copy(), spec.command).text.encode(), spec.command
        assert fx.unb64(ex["sent_b64"]) == spec.command.encode() + b"!\r\n"  # exactly what the hub sends
        assert ex["response"]["analysis"]["line_endings"]["lf"] == 0
    (ex,) = load(root, RecordIds.TELNET_BANNER)["exchanges"]
    assert response_body(ex) == banner(sim.state).encode()
    assert load(root, RecordIds.INDEX_PAGE)["exchanges"][0]["response"]["status"] == 200

    # Read mode is read-only.
    assert not [e for e in sim.log if e.get("mutated")]
    assert sim.state.to_dict() == sim.initial_state.to_dict()
    # Every HTTP request the simulator saw was recognised.
    assert not sim.unrecognised()

    manifest = fx.load_manifest(root)
    assert manifest["format"] == fx.FORMAT
    assert manifest["device"]["mcu_version"] == "V1.10.02"
    (run,) = manifest["runs"]
    assert run["mode"] == "read" and run["target"]["port"] == sim.https_port
    assert "password" not in run["options"]
    assert {"login-ok-result", "http-read-shapes", "telnet-status-wording"} <= set(manifest["answers"])


async def test_second_run_appends_to_manifest(sim, tmp_path):
    for _ in range(2):
        code, _ = await run_capture(make_opts(sim, tmp_path / "{firmware}", telnet=False), quiet())
        assert code == cli.EXIT_OK
    assert len(fx.load_manifest(tmp_path / FW)["runs"]) == 2


async def test_no_telnet_skips_telnet_records(sim, tmp_path):
    code, cap = await run_capture(make_opts(sim, tmp_path / "out", telnet=False), quiet())
    assert code == cli.EXIT_OK
    assert not (tmp_path / "out" / "telnet").exists()
    assert (tmp_path / "out" / "http" / "get_video_status.json").exists()


async def test_telnet_unreachable_is_a_warning_not_a_failure(sim, tmp_path):
    opts = make_opts(sim, tmp_path / "out", telnet_port=1)
    code, cap = await run_capture(opts, quiet())
    assert code == cli.EXIT_OK
    assert any("Telnet" in w for w in cap.warnings)


async def test_wrong_credentials_fail_cleanly(sim, tmp_path):
    sim.faults.update({"wrong_password": True})
    code, cap = await run_capture(make_opts(sim, tmp_path / "out"), quiet())
    assert code == cli.EXIT_FAILED
    assert "wrong user/password" in cap.errors[0]
    assert not (tmp_path / "out").exists()


async def test_unreachable_device_fails_cleanly(tmp_path):
    from tools.hil.capture import Options

    opts = Options(host="127.0.0.1", port=1, telnet_port=1, password="x", out=str(tmp_path / "o"), yes=True,
                   http_timeout=1.0)
    code, cap = await run_capture(opts, quiet())
    assert code == cli.EXIT_FAILED
    assert "cannot reach" in cap.errors[0]


# ------------------------------------------------------------------ redaction

SECRET = "Tr0ub4dor&3-hil-secret"
MAC = "02:00:00:0B:08:08"


async def test_password_and_redact_values_never_reach_disk(tmp_path):
    state = DeviceState.default()
    state.auth["password"] = SECRET
    async with new_sim(state) as s:
        out = tmp_path / "{firmware}"
        for mode, telnet in (("read", True), ("probe", False)):
            code, cap = await run_capture(make_opts(s, out, mode=mode, redact=[MAC], telnet=telnet), quiet())
            assert code == cli.EXIT_OK, cap.errors
    root = tmp_path / FW
    files = [p for p in root.rglob("*") if p.is_file()]
    assert len(files) > 40
    for path in files:
        assert not fx.find_secrets(path, [SECRET, MAC]), path
        raw = path.read_bytes()
        assert SECRET.encode() not in raw and MAC.encode() not in raw
    login = load(root, RecordIds.LOGIN)["exchanges"][0]
    assert login["request"]["json"]["password"] == REDACTED
    assert login["redacted"] == ["request.password"]
    network = load(root, "http/get_network")
    assert "scrubbed" in " ".join(network.get("redactions", []))
    assert REDACTED.encode() in response_body(network["exchanges"][0])
    manifest = fx.load_manifest(root)
    assert all("password" not in run["options"] for run in manifest["runs"])


async def test_a_leak_is_detected_and_fails_the_run(sim, tmp_path, monkeypatch):
    """If scrubbing ever breaks, the final scan still catches the secret."""
    monkeypatch.setattr(fx, "scrub", lambda obj, secrets: (obj, False))
    code, cap = await run_capture(make_opts(sim, tmp_path / "out", telnet=False, redact=[MAC]), quiet())
    assert code == cli.EXIT_SECRET_LEAK


def test_scrub_and_find_secrets_cover_base64(tmp_path):
    doc = {"a": f"x{SECRET}y", "body_b64": fx.b64(f"<{SECRET}>".encode()), "n": [SECRET], "k": 5}
    clean, changed = fx.scrub(doc, [SECRET])
    assert changed and SECRET not in json.dumps(clean)
    assert fx.unb64(clean["body_b64"]) == f"<{REDACTED}>".encode()
    dirty = tmp_path / "leak.json"
    dirty.write_text(json.dumps({"body_b64": fx.b64(SECRET.encode())}), encoding="utf-8")
    assert fx.find_secrets(dirty, [SECRET]) == [f"{dirty}: base64 field body_b64"]
    # Too-short secrets are not scrubbed from free text (they would mangle data).
    assert fx.scrub({"a": "abc"}, ["ab"]) == ({"a": "abc"}, False)


# --------------------------------------------------------------------- naming


@pytest.mark.parametrize(
    "device, name",
    [
        ({"model": "BK-808", "mcu_version": "V1.10.02", "web_version": "V2.00.03"}, "BK-808_V1.10.02_web-V2.00.03"),
        ({"model": "BK 808/X", "mcu_version": "V1.2"}, "BK-808-X_V1.2"),
        ({}, "unknown-model_unknown-fw"),
    ],
)
def test_firmware_folder_name(device, name):
    assert firmware_folder_name(device) == name


async def test_out_placeholders_and_firmware_override(sim, tmp_path):
    code, cap = await run_capture(make_opts(sim, tmp_path / "<firmware>", telnet=False), quiet())
    assert code == cli.EXIT_OK and cap.writer.root == tmp_path / FW
    code, cap = await run_capture(make_opts(sim, tmp_path / "{firmware}", telnet=False, firmware="custom"), quiet())
    assert cap.writer.root == tmp_path / "custom"


# ------------------------------------------------------------------------ CLI


def test_cli_write_mode_needs_the_danger_flag(capsys):
    assert cli.main(["--host", "127.0.0.1", "--password", "x", "--mode", "write"]) == cli.EXIT_USAGE
    assert cli.DANGER_FLAG in capsys.readouterr().err


def test_cli_needs_a_password_when_not_interactive(monkeypatch, capsys):
    monkeypatch.delenv("OREI_PASSWORD", raising=False)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert cli.main(["--host", "127.0.0.1"]) == cli.EXIT_USAGE
    assert "no password" in capsys.readouterr().err


def test_cli_options_mapping():
    args = cli.build_parser().parse_args([
        "--host", "10.0.0.5", "--mode", "probe", "--idle-waits", "60,300.5", "--push-seconds", "0",
        "--only", "routing,names", "--include", "reboot", "--test-output", "3", "--no-tls", "--no-telnet",
        "--redact", "a", "--redact", "b",
    ])
    opts = cli.options_from_args(args, password="pw")
    assert (opts.host, opts.port, opts.tls, opts.telnet) == ("10.0.0.5", 443, False, False)
    assert opts.idle_waits == [60.0, 300.5] and opts.push_seconds == 0
    assert opts.only == ["routing", "names"] and opts.include == ["reboot"] and opts.test_output == 3
    assert opts.redact == ["a", "b"]
    assert "password" not in opts.public() and opts.public()["redact"] == ["<1 chars>", "<1 chars>"]
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["--host", "x", "--test-output", "9"])
