"""Simulator golden mode: capture -> load as golden -> identical responses; the report."""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import shutil
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from tests.hil_tools.helpers import FW, bodies, load, make_opts, new_sim, quiet
from tools.hil.capture import catalog as cmd
from tools.hil.capture import run_capture
from tools.hil.capture.assumptions import BY_ID
from tools.hil.capture.catalog import HTTP_READS, TELNET_READS
from tools.hil.capture.fixtures import RecordIds, b64, iter_exchanges, response_body
from tools.hil.capture.transport import HttpRecorder, TelnetRecorder
from tools.simulator import DeviceState
from tools.simulator import __main__ as sim_main
from tools.simulator.golden import (
    CONFIRMED,
    CONTRADICTED,
    MISSING,
    GoldenError,
    GoldenSet,
    JsonStyle,
    _patch,
    assumption_report,
    detect_style,
    format_report,
)


@pytest.fixture(scope="module")
def golden_src(tmp_path_factory) -> Path:
    """read + probe + a write subset, captured once from a default simulator."""
    out = tmp_path_factory.mktemp("golden")

    async def capture() -> None:
        async with new_sim() as s:
            runs: list[tuple[str, dict[str, Any]]] = [
                ("read", {}),
                ("probe", {"telnet_timeout": 0.5}),
                ("write", {"i_understand": True, "only": ["routing", "system", "names", "telnet"]}),
            ]
            for mode, extra in runs:
                code, cap = await run_capture(make_opts(s, out / "{firmware}", mode=mode, **extra), quiet())
                assert code == 0, (mode, cap.errors)

    # Own thread and event loop, so pytest-asyncio's loop is left alone.
    with concurrent.futures.ThreadPoolExecutor(1) as pool:
        pool.submit(asyncio.run, capture()).result()
    return out / FW


def _copy(src: Path, dst: Path) -> Path:
    shutil.copytree(src, dst)
    return dst


def set_body(root: Path, record_id: str, body: bytes, match: Any = None) -> None:
    """Replace the response bytes of one exchange in a capture record (a "device" answer)."""
    path = root / f"{record_id}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    exchanges = [ex for ex in iter_exchanges(record) if match is None or match(ex)]
    ex = exchanges[0]
    ex["response"]["body_b64"] = b64(body)
    ex["response"]["body_text" if ex["kind"] == "http" else "text"] = body.decode("utf-8", errors="replace")
    if ex["kind"] == "http":
        try:
            ex["response"]["json"] = json.loads(body)
        except ValueError:
            ex["response"]["json"] = None
    path.write_text(json.dumps(record), encoding="utf-8")


def golden_sim(root: Path):
    golden = GoldenSet.load(root)
    state = DeviceState.default()
    golden.seed(state)
    return new_sim(state, golden=golden), golden, state


# ------------------------------------------------------------------ round trip


async def test_round_trip_capture_golden_capture_is_byte_identical(golden_src, tmp_path):
    sim, golden, _ = golden_sim(golden_src)
    async with sim as s:
        code, cap = await run_capture(make_opts(s, tmp_path / "{firmware}"), quiet())
        assert code == 0, cap.errors
        served = [e for e in s.log if e.get("golden")]
    second = tmp_path / FW
    ids = [RecordIds.LOGIN, RecordIds.TELNET_BANNER]
    ids += [RecordIds.http_read(r.slug) for r in HTTP_READS] + [RecordIds.telnet_read(r.slug) for r in TELNET_READS]
    for record_id in ids:
        assert bodies(load(golden_src, record_id)) == bodies(load(second, record_id)), record_id
    # ...and they really came from the captures: every read and the login.
    assert len([e for e in served if e["channel"] == "http"]) >= len(HTTP_READS) + 1
    assert len([e for e in served if e["channel"] == "telnet"]) == len(TELNET_READS)


async def test_golden_serves_device_bytes_and_patches_state_changes(golden_src, tmp_path):
    """Device formatting, an unknown field and name prefixes survive; routing still updates."""
    root = _copy(golden_src, tmp_path / "g")
    doc = load(root, "http/get_video_status")["exchanges"][0]["response"]["json"]
    device_doc: dict[str, Any] = {"comhead": doc["comhead"], "devicefield": "kept",
                  **{k: v for k, v in doc.items() if k != "comhead"}}
    device_doc["allinputname"] = [f"IN{i:02d}-{n}" for i, n in enumerate(doc["allinputname"], 1)]

    def device_bytes(d: dict[str, Any]) -> bytes:
        return json.dumps(d, separators=(", ", ": ")).encode() + b"\r\n"

    set_body(root, "http/get_video_status", device_bytes(device_doc))
    sim, _, state = golden_sim(root)
    assert state.inputs[0].name == "IN01-PS3"  # seeded from the capture
    async with sim as s, HttpRecorder("127.0.0.1", s.https_port) as http:
        await http.post(cmd.login("Admin", "admin"))
        first = await http.post(cmd.read("get video status"))
        assert response_body(first) == device_bytes(device_doc)
        assert (await http.post(cmd.video_switch(8, 3)))["response"]["json"]["result"] == 1
        second = await http.post(cmd.read("get video status"))
        expected = {**device_doc, "allsource": [*doc["allsource"][:7], 3]}
        assert response_body(second) == device_bytes(expected)
        await http.post(cmd.input_name(2, "Xbox"))
        names = (await http.post(cmd.read("get video status")))["response"]["json"]["allinputname"]
        assert names[:3] == ["IN01-PS3", "Xbox", "IN03-Computer"]
        kinds = [e["golden"] for e in s.log if e["command"] == "get video status"]
    assert kinds == ["verbatim", "patched", "patched"]


async def test_golden_telnet_banner_reads_and_fallback(golden_src, tmp_path):
    root = _copy(golden_src, tmp_path / "g")
    set_body(root, RecordIds.TELNET_BANNER, b"\r\nHELLO FROM THE DEVICE\r\n")
    set_body(root, "telnet/r_type", b"BK-808 GOLDEN\r\n")
    status_capture = response_body(load(root, RecordIds.TELNET_STATUS)["exchanges"][0])
    sim, _, _ = golden_sim(root)
    async with sim as s:
        t = TelnetRecorder("127.0.0.1", s.telnet_port, idle=0.05, banner_idle=0.1, timeout=1.0)
        try:
            assert response_body(await t.connect()) == b"\r\nHELLO FROM THE DEVICE\r\n"
            assert response_body(await t.command("r type")) == b"BK-808 GOLDEN\r\n"
            assert response_body(await t.command("status")) == status_capture
            await t.command("s output 8 in source 3")
            # The dump no longer matches the capture's state: the simulator's own text is used.
            after = response_body(await t.command("status"))
            assert after != status_capture and b"output8->input3" in after
        finally:
            await t.close()


async def test_golden_login_no_session_and_write_results(golden_src, tmp_path):
    root = _copy(golden_src, tmp_path / "g")
    set_body(root, RecordIds.PROBE_WRONG_PASSWORD, b'{"comhead":"login","result":-1}',
             match=lambda ex: ex["role"] == "login-wrong")
    # The module capture ran probe after read, so its first no-session read met a live
    # session; the retry after the failed login is the real "not logged in" answer.
    no_session = load(root, RecordIds.PROBE_NO_SESSION)
    assert no_session["findings"]["first_attempt"] == "data"
    set_body(root, RecordIds.PROBE_NO_SESSION, b"<html>please log in</html>",
             match=lambda ex: ex["role"] == "no-session")
    set_body(root, RecordIds.write("http_beep"), b'{"comhead":"set beep","result":"success"}',
             match=lambda ex: ex.get("outcome") == "applied")
    sim, _, _ = golden_sim(root)
    async with sim as s, HttpRecorder("127.0.0.1", s.https_port) as http:
        wrong = await http.post(cmd.login("Admin", "nope"))
        assert response_body(wrong) == b'{"comhead":"login","result":-1}'
        no_session = await http.post(cmd.read("get output status"))
        assert response_body(no_session) == b"<html>please log in</html>"
        ok = await http.post(cmd.login("Admin", "admin"))
        assert response_body(ok) == response_body(load(root, RecordIds.LOGIN)["exchanges"][0])
        applied = await http.post(cmd.beep(0))
        assert response_body(applied) == b'{"comhead":"set beep","result":"success"}'
        assert s.state.system["beep"] == 0  # the simulator still applied it
        rejected = await http.post(cmd.beep(2))
        assert rejected["response"]["json"] == {"comhead": "set beep", "result": 0}


async def test_hub_parses_device_style_golden_responses(golden_src, tmp_path, monkeypatch):
    import orei_matrix

    root = _copy(golden_src, tmp_path / "g")
    doc = load(root, "http/get_video_status")["exchanges"][0]["response"]["json"]
    set_body(root, "http/get_video_status", json.dumps(doc, separators=(", ", ": ")).encode() + b"\n")
    sim, _, _ = golden_sim(root)
    async with sim as s:
        m = orei_matrix.OreiMatrix("127.0.0.1", port=s.https_port, use_https=True)
        monkeypatch.setattr(m, "_connect_telnet", AsyncMock(return_value=False))
        try:
            assert await m.connect()
            status = await m.get_video_status()
            assert status is not None and status["allsource"] == doc["allsource"]
        finally:
            await m.disconnect()


# ------------------------------------------------------------------ report


def test_report_on_simulator_captures_confirms_the_simulator(golden_src):
    golden = GoldenSet.load(golden_src)
    verdicts = {v.id: v for v in assumption_report(golden)}
    assert set(verdicts) == set(BY_ID)
    assert [v for v in verdicts.values() if v.status == CONTRADICTED] == []
    for aid in ("login-ok-result", "login-fail-result", "session-expired-style", "session-mechanism",
                "unknown-comhead-result", "garbage-body", "write-ok-results", "write-fail-result",
                "http-read-shapes", "video-status-names", "output-status-name-field", "get-status-fields",
                "get-network-fields", "preset-get-shape", "name-truncation", "lcd-codes", "telnet-banner",
                "telnet-iac", "telnet-status-wording", "telnet-read-wording", "telnet-terminators",
                "telnet-error-codes", "telnet-set-acks", "telnet-multi-session"):
        assert verdicts[aid].status == CONFIRMED, (aid, verdicts[aid].detail)
    assert verdicts["reboot-replies-first"].status == MISSING
    text = format_report(list(verdicts.values()), golden)
    assert "Still unconfirmed" in text and "reboot-replies-first" in text.split("Still unconfirmed")[1]


def test_report_flags_device_differences(golden_src, tmp_path):
    root = _copy(golden_src, tmp_path / "g")
    set_body(root, RecordIds.PROBE_WRONG_PASSWORD, b'{"comhead":"login","result":0}',
             match=lambda ex: ex["role"] == "login-wrong")
    set_body(root, RecordIds.TELNET_STATUS, b"power on\r\nmac address: x\r\n")
    status_doc = load(root, "http/get_status")["exchanges"][0]["response"]["json"]
    set_body(root, "http/get_status", json.dumps({**status_doc, "ipmoduleversion": "10.01.17"}).encode())
    set_body(root, RecordIds.write("http_beep"), b'{"comhead":"set beep","result":"success"}',
             match=lambda ex: ex.get("outcome") == "applied")
    verdicts = {v.id: v for v in assumption_report(GoldenSet.load(root))}
    assert verdicts["login-fail-result"].status == CONTRADICTED
    assert verdicts["telnet-status-wording"].status == CONTRADICTED
    assert verdicts["get-status-fields"].status == CONTRADICTED
    assert "ipmoduleversion" in verdicts["get-status-fields"].detail
    assert verdicts["write-ok-results"].status == CONTRADICTED and "set beep" in verdicts["write-ok-results"].detail
    assert verdicts["http-read-shapes"].status == CONTRADICTED


def test_report_without_captures_is_all_missing():
    assert {v.status for v in assumption_report(None)} == {MISSING}


def test_simulator_cli_report_and_errors(golden_src, tmp_path, capsys):
    assert sim_main.main(["--golden", str(golden_src), "--report"]) == 0
    out = capsys.readouterr().out
    assert "CONFIRMED" in out and "Still unconfirmed" in out
    assert sim_main.main(["--golden", str(tmp_path), "--report"]) == 2
    assert "no capture records" in capsys.readouterr().err
    with pytest.raises(GoldenError):
        GoldenSet.load(tmp_path / "missing")


def test_seed_rejects_out_of_range_captures_without_breaking_the_state(golden_src, tmp_path):
    root = _copy(golden_src, tmp_path / "g")
    doc = load(root, "http/get_input_status")["exchanges"][0]["response"]["json"]
    set_body(root, "http/get_input_status", json.dumps({**doc, "edid": [99] * 8}).encode())
    golden = GoldenSet.load(root)
    state = DeviceState.default()
    golden.seed(state)
    assert state.to_dict() == DeviceState.default().to_dict()
    assert golden.warnings and "could not seed" in golden.warnings[0]


# ------------------------------------------------------------------ helpers


def test_detect_style_and_patch():
    doc = {"a": [1, 2], "n": "é"}
    body = b"  " + json.dumps(doc, separators=(", ", ": "), ensure_ascii=True).encode() + b"\r\n\x00"
    style = detect_style(body, doc)
    assert style == JsonStyle((", ", ": "), True, b"  ", b"\r\n\x00")
    assert style.render(doc) == body
    assert detect_style(b'{"a":1} trailing', {"a": 1}) is None
    captured = {"all": ["IN01-A", "IN02-B", "extra"], "k": 1, "dev": "x"}
    base = {"all": ["IN01-A", "IN02-B"], "k": 1}
    now = {"all": ["IN01-A", "C"], "k": 2}
    assert _patch(captured, base, now) == {"all": ["IN01-A", "C", "extra"], "k": 2, "dev": "x"}
