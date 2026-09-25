"""``--mode probe``: login, session and Telnet protocol semantics.

Mostly read-only. The few probes that must send a set command send the value
the device already has (a no-op), then verify nothing changed and restore if
something did. The push-notification window asks the operator to press
front-panel buttons; routing changed during the window is restored afterwards.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any

from . import catalog as cmd
from .context import Capture
from .fixtures import RecordIds, header, headers_named
from .snapshot import Snapshot, diff
from .transport import HttpRecorder, TelnetRecorder, is_data_response

WRONG_PASSWORD = "hil-capture-deliberately-wrong"
_PUSH_RE = re.compile(r"hdmi\s+(input|output)\s+(\d+)\s*:\s*(connect|disconnect)", re.IGNORECASE)


def _json(ex: dict[str, Any]) -> Any:
    return (ex.get("response") or {}).get("json")


def _status(ex: dict[str, Any]) -> int | None:
    return (ex.get("response") or {}).get("status")


def classify_unauthenticated(ex: dict[str, Any]) -> str:
    """How a response to a command without a valid session looks."""
    if ex.get("error"):
        return f"error:{ex['error']['type']}"
    resp = ex.get("response") or {}
    status = resp.get("status")
    if status != 200:
        return f"http{status}"
    doc = resp.get("json")
    if doc is None:
        ctype = (header(resp.get("headers"), "Content-Type") or "").lower()
        return "html" if "html" in ctype or resp.get("body_text", "").lstrip().startswith("<") else "non-json"
    if is_data_response(doc):
        return "data"
    return "json"


async def probe_before_login(cap: Capture) -> None:
    """Runs before the capture logs in: a read without any session."""
    client = cap.track(cap.http.clone(cookies=False))
    ex = await client.post(cmd.read("get system status"), role="no-session")
    kind = classify_unauthenticated(ex)
    note = ""
    if kind == "data":
        note = ("the read returned data without a login: a session from this IP was probably still active "
                "(stop the hub and close the web UI, wait for the session to expire, then re-run)")
        cap.warnings.append("no-session probe: " + note)
    cap.add(RecordIds.PROBE_NO_SESSION, {
        "title": "Read before any login (fresh client, no cookies)",
        "answers": ["session-expired-style"],
        "exchanges": [ex],
        "findings": {"classification": kind, "note": note},
    })
    cap.console.print(f"  no-session read           -> {kind}")


async def run_probe(cap: Capture) -> None:
    con = cap.console
    opts = cap.opts
    con.print("HTTP probes:")
    await _probe_wrong_password(cap)
    await _probe_login_and_session(cap)
    await _probe_idle_expiry(cap)
    await cap.ensure_session()

    unknown = await cap.http.post({"comhead": "hil capture unknown", "language": 0}, role="unknown-comhead")
    cap.add(RecordIds.PROBE_UNKNOWN_COMHEAD, {
        "title": "Unknown comhead", "answers": ["unknown-comhead-result"], "exchanges": [unknown],
        "findings": {"json": _json(unknown), "status": _status(unknown)},
    })
    con.print(f"  unknown comhead           -> {_status(unknown)} {_json(unknown)}")

    garbage = await cap.http.post(raw_body=b"this is not json", role="garbage", label="non-JSON body")
    cap.add(RecordIds.PROBE_GARBAGE_BODY, {
        "title": "Body that is not JSON", "answers": ["garbage-body"], "exchanges": [garbage],
        "findings": {"json": _json(garbage), "status": _status(garbage)},
    })
    con.print(f"  non-JSON body             -> {_status(garbage)} {_json(garbage)}")
    await cap.ensure_session()
    await _probe_cec_shapes(cap)

    if not opts.telnet:
        con.print("Telnet probes: skipped (--no-telnet)")
        return
    banner = await cap.open_telnet()
    if cap.telnet is None:
        con.print(f"Telnet probes: unavailable ({(banner or {}).get('error')})")
        return
    con.print("Telnet probes:")
    await _probe_telnet_errors(cap)
    await _probe_telnet_framing(cap)
    await _probe_telnet_noop_acks(cap)
    await _probe_second_session(cap)
    await _probe_push_window(cap)


# ------------------------------------------------------------------- HTTP


async def _probe_wrong_password(cap: Capture) -> None:
    client = cap.track(cap.http.clone())
    wrong = await cap.login(client, role="login-wrong", password=WRONG_PASSWORD)
    after = await client.post(cmd.read("get system status"), role="after-wrong-login")
    # Did the failed login also end the session the main client holds?
    main_after = await cap.http.post(cmd.read("get system status"), role="main-after-wrong-login")
    doc = _json(wrong)
    findings = {
        "status": _status(wrong),
        "json": doc,
        "result": doc.get("result") if isinstance(doc, dict) else None,
        "echoes_comhead": isinstance(doc, dict) and doc.get("comhead") == "login",
        "read_after_wrong_login": classify_unauthenticated(after),
        "main_session_after_wrong_login": classify_unauthenticated(main_after),
        "note": "the request used a deliberately wrong password (stored redacted)",
    }
    cap.add(RecordIds.PROBE_WRONG_PASSWORD, {
        "title": "Login with a wrong password (BE-05)",
        "answers": ["login-fail-result", "session-mechanism"],
        "exchanges": [wrong, after, main_after],
        "findings": findings,
    })
    cap.console.print(f"  wrong password            -> {findings['status']} {doc}")
    _second_chance_no_session(cap, main_after)


def _second_chance_no_session(cap: Capture, main_after: dict[str, Any]) -> None:
    """If the first no-session read found a live session, use the read after the failed login.

    Sessions may be per client IP, so a session from an earlier run (or the hub)
    answers the "no session" read with data. If the failed login ended that
    session, the read right after it shows the real "not logged in" answer.
    """
    record = cap.records.get(RecordIds.PROBE_NO_SESSION)
    if not record or record["findings"].get("classification") != "data":
        return
    kind = classify_unauthenticated(main_after)
    if kind == "data":
        return
    for ex in record["exchanges"]:
        ex["role"] = "no-session-but-session-active"
    retry = {**main_after, "role": "no-session", "label": "read after a failed login (session ended)"}
    record["exchanges"].append(retry)
    record["findings"] = {
        "classification": kind,
        "first_attempt": "data",
        "note": "the first read found a session from this IP still active; a failed login ended it, and the "
                "read after it is the 'not logged in' answer",
    }
    cap.warnings[:] = [w for w in cap.warnings if not w.startswith("no-session probe")]
    cap.add(RecordIds.PROBE_NO_SESSION, record)
    cap.console.print(f"  no-session read (retry)   -> {kind}")


async def _probe_login_and_session(cap: Capture) -> None:
    ok_client = cap.track(cap.http.clone(cookies=True))
    ok = await cap.login(ok_client, role="login")
    set_cookies = headers_named((ok.get("response") or {}).get("headers"), "Set-Cookie")
    cap.add(RecordIds.PROBE_LOGIN_OK, {
        "title": "Successful login (fresh client; Set-Cookie values masked)",
        "answers": ["login-ok-result", "session-mechanism"],
        "exchanges": [ok],
        "findings": {"json": _json(ok), "set_cookie": set_cookies, "cookie_names": ok_client.cookie_names()},
    })
    with_cookie = await ok_client.post(cmd.read("get system status"), role="session-check-cookie")
    no_cookie_client: HttpRecorder = cap.track(cap.http.clone(cookies=False))
    without_cookie = await no_cookie_client.post(cmd.read("get system status"), role="session-check-no-cookie")
    a, b = is_data_response(_json(with_cookie)), is_data_response(_json(without_cookie))
    no_session_kind = (cap.records.get(RecordIds.PROBE_NO_SESSION) or {}).get("findings", {}).get("classification")
    if a and b:
        mechanism = "ip-or-no-auth" if no_session_kind == "data" else "ip"
    elif a and not b:
        mechanism = "cookie"
    else:
        mechanism = "unknown"
    cap.add(RecordIds.PROBE_SESSION_MECHANISM, {
        "title": "Session tracking: same read with and without the login cookie",
        "answers": ["session-mechanism"],
        "exchanges": [with_cookie, without_cookie],
        "findings": {
            "mechanism": mechanism,
            "with_cookie": classify_unauthenticated(with_cookie),
            "without_cookie": classify_unauthenticated(without_cookie),
            "cookies_set": bool(set_cookies),
        },
    })
    cap.console.print(f"  login ok                  -> {_json(ok)}; session mechanism: {mechanism}")


async def _probe_idle_expiry(cap: Capture) -> None:
    waits = sorted(w for w in cap.opts.idle_waits if w > 0)
    if not waits:
        cap.console.print("  idle expiry               -> skipped (use --idle-waits 60,300,900)")
        return
    steps: list[dict[str, Any]] = []
    alive_after = None
    expired_after = None
    for wait in waits:
        client = cap.track(cap.http.clone())
        login = await cap.login(client, role="login")
        cap.console.print(f"  idle expiry: logged in, now idle for {wait:g} s (send nothing to the matrix)...")
        await asyncio.sleep(wait)
        check = await client.post(cmd.read("get system status"), role="idle-check")
        alive = is_data_response(_json(check))
        steps.append({"idle_s": wait, "alive": alive, "classification": classify_unauthenticated(check),
                      "exchanges": [login, check]})
        if alive:
            alive_after = wait
        else:
            expired_after = wait
            relogin = await cap.login(client, role="login")
            again = await client.post(cmd.read("get system status"), role="after-relogin")
            steps[-1]["relogin_works"] = is_data_response(_json(again))
            steps[-1]["exchanges"] += [relogin, again]
            break
    cap.add(RecordIds.PROBE_IDLE_EXPIRY, {
        "title": "Idle session expiry (BE-04)",
        "answers": ["session-ttl", "session-expired-style"],
        "steps": steps,
        "findings": {"alive_after_s": alive_after, "expired_after_s": expired_after, "waits": waits},
    })
    cap.console.print(f"  idle expiry               -> alive after {alive_after}, expired after {expired_after}")


async def _probe_cec_shapes(cap: Capture) -> None:
    """BE-13 without changing anything: send both payload shapes with the current values."""
    before_doc = await cap.read_json("get cec status", role="readback")
    if not isinstance(before_doc, dict) or not isinstance(before_doc.get("inputindex"), list):
        cap.console.print("  CEC enable shapes         -> skipped (get cec status unreadable)")
        return
    cin, cout = list(before_doc["inputindex"])[:8], list(before_doc["outputindex"])[:8]
    port = cap.opts.test_input
    bulk = await cap.http.post(cmd.cec_index_bulk(cin, cout), role="cec-shape-bulk-noop")
    single = await cap.http.post(cmd.cec_index_single("input", port, int(cin[port - 1])),
                                 role="cec-shape-single-noop")
    after_doc = await cap.read_json("get cec status", role="readback")
    changed = not isinstance(after_doc, dict) or after_doc.get("inputindex") != before_doc.get("inputindex") \
        or after_doc.get("outputindex") != before_doc.get("outputindex")
    restored = None
    if changed:
        cap.warnings.append("CEC enable changed after a no-op payload; restoring the original arrays")
        fix = await cap.http.post(cmd.cec_index_bulk(cin, cout), role="restore")
        cap.log_restore({"reason": "probe cec shapes", "payload": cmd.cec_index_bulk(cin, cout),
                         "result": _json(fix)})
        final = await cap.read_json("get cec status", role="readback")
        restored = isinstance(final, dict) and final.get("inputindex") == cin and final.get("outputindex") == cout
    cap.add(RecordIds.PROBE_CEC_SHAPES, {
        "title": "set cec index: documented bulk shape vs the hub's single-port shape, both no-op (BE-13)",
        "answers": ["cec-index-single-port"],
        "exchanges": [bulk, single],
        "findings": {
            "bulk_result": (_json(bulk) or {}).get("result") if isinstance(_json(bulk), dict) else None,
            "single_result": (_json(single) or {}).get("result") if isinstance(_json(single), dict) else None,
            "state_changed": changed,
            "restored": restored,
            "before": {"inputindex": cin, "outputindex": cout},
            "after": after_doc if changed else None,
        },
    })
    cap.console.print(f"  CEC enable shapes         -> bulk {_json(bulk)}, single {_json(single)}, "
                      f"changed={changed}")


# ----------------------------------------------------------------- Telnet


async def _routing_guard(cap: Capture) -> Snapshot:
    return await cap.snapshot()


async def _verify_unchanged(cap: Capture, before: Snapshot, reason: str) -> list[list[Any]]:
    after = await cap.snapshot()
    changes = diff(before, after)
    if changes:
        cap.warnings.append(f"{reason}: device state changed {changes}; restoring")
        cap.console.print(f"  ! {reason} changed the device: {changes}; restoring")
        await cap.restore_to(before, reason=reason)
    return changes


async def _probe_telnet_errors(cap: Capture) -> None:
    assert cap.telnet is not None
    before = await _routing_guard(cap)
    exchanges = []
    findings: dict[str, Any] = {}
    try:
        for probe in cmd.TELNET_ERROR_PROBES:
            ex = await cap.telnet.command(probe.command, role="probe-error", label=probe.why)
            exchanges.append(ex)
            analysis = ((ex.get("response") or {}).get("analysis") or {})
            findings[probe.command] = {"why": probe.why, "last_line": analysis.get("last_line"),
                                       "error_code": analysis.get("error_code"),
                                       "completion": (ex.get("response") or {}).get("completion")}
            cap.console.print(f"  {probe.command:<28} -> {analysis.get('last_line')!r}")
            if not cap.telnet.connected:
                await cap.reconnect_telnet()
    finally:
        changes = await _verify_unchanged(cap, before, "telnet error probes")
    cap.add(RecordIds.PROBE_TELNET_ERRORS, {
        "title": "Telnet commands that should fail (E00/E01 semantics, BE-07)",
        "answers": ["telnet-error-codes", "telnet-terminators"],
        "exchanges": exchanges,
        "findings": {"by_command": findings, "state_changed": changes},
    })


_FRAMING = (
    ("no_bang_then_bang", b"r type\r\n", b"!\r\n", "command without '!', then '!' alone"),
    ("bang_no_crlf", b"r type!", None, "'!' but no CR LF"),
    ("bang_lf_only", b"r type!\n", None, "'!' and LF only"),
    ("uppercase", b"R TYPE!\r\n", None, "upper-case command"),
    ("pipelined", b"r type!\r\nr fw version!\r\n", None, "two commands in one write"),
)


async def _probe_telnet_framing(cap: Capture) -> None:
    """Each variant on its own connection, so a half-parsed command cannot leak."""
    assert cap.telnet is not None
    variants = []
    for name, first, second, why in _FRAMING:
        conn: TelnetRecorder = cap.telnet.clone()
        banner = await conn.connect(role="framing-banner")
        entry: dict[str, Any] = {"variant": name, "why": why, "exchanges": [banner]}
        if not banner.get("error"):
            ex1 = await conn.command(first.decode(), raw=first, role="framing", label=f"{name}: first write")
            entry["exchanges"].append(ex1)
            entry["first_response"] = (ex1.get("response") or {}).get("text")
            if second is not None:
                ex2 = await conn.command(second.decode(), raw=second, role="framing", label=f"{name}: second write")
                entry["exchanges"].append(ex2)
                entry["second_response"] = (ex2.get("response") or {}).get("text")
        await conn.close()
        variants.append(entry)
        cap.console.print(f"  framing {name:<20} -> {entry.get('first_response')!r}"
                          + (f" / {entry.get('second_response')!r}" if second else ""))
    cap.add(RecordIds.PROBE_TELNET_FRAMING, {
        "title": "Telnet command framing: terminator '!', CR LF, case, pipelining",
        "answers": ["telnet-terminators"],
        "variants": variants,
    })


async def _probe_telnet_noop_acks(cap: Capture) -> None:
    """Set-command acknowledgements, using the values the device already has."""
    assert cap.telnet is not None
    before = await cap.snapshot()
    t = cap.opts.test_output
    commands: list[str] = []
    if before.routing:
        commands.append(f"s output {t} in source {before.routing[t - 1]}")
    if before.beep is not None:
        commands.append(f"s beep {int(before.beep)}")
    if before.lock is not None:
        commands.append(f"s lock {int(before.lock)}")
    if before.stream:
        commands.append(f"s out {t} stream {int(before.stream[t - 1])}")
    exchanges = []
    try:
        for command in commands:
            ex = await cap.telnet.command(command, role="probe-noop-ack", label="no-op set")
            exchanges.append(ex)
            resp = ex.get("response") or {}
            cap.console.print(f"  {command:<28} -> {resp.get('text')!r} ({resp.get('completion')}, "
                              f"first byte {resp.get('first_byte_ms')} ms)")
    finally:
        changes = await _verify_unchanged(cap, before, "telnet no-op set commands")
    cap.add(RecordIds.PROBE_TELNET_NOOP_ACKS, {
        "title": "Set-command acknowledgements with no-op values (BE-07 completion detection)",
        "answers": ["telnet-set-acks", "telnet-terminators"],
        "exchanges": exchanges,
        "findings": {"state_changed": changes},
    })


async def _probe_second_session(cap: Capture) -> None:
    assert cap.telnet is not None
    second = cap.telnet.clone()
    banner = await second.connect(role="second-session-banner")
    ex2 = await second.command("r type", role="read") if not banner.get("error") else None
    ex1 = await cap.telnet.command("r type", role="read")
    await second.close()
    ok2 = bool(ex2 and (ex2.get("response") or {}).get("text"))
    ok1 = bool((ex1.get("response") or {}).get("text"))
    cap.add(RecordIds.PROBE_TELNET_SECOND_SESSION, {
        "title": "Two Telnet connections at once",
        "answers": ["telnet-multi-session"],
        "exchanges": [e for e in (banner, ex2, ex1) if e],
        "findings": {"second_session_works": ok2, "first_session_still_works": ok1},
    })
    cap.console.print(f"  second Telnet session     -> second works={ok2}, first still works={ok1}")


async def _probe_push_window(cap: Capture) -> None:
    assert cap.telnet is not None
    seconds = cap.opts.push_seconds
    if seconds <= 0:
        cap.console.print("  push window               -> skipped (--push-seconds 0)")
        return
    before = await cap.snapshot()
    await cap.telnet.drain_unsolicited(0.2)
    cap.console.print("")
    cap.console.print(f"PUSH NOTIFICATION WINDOW ({seconds:g} s). While it runs, at the matrix:")
    cap.console.print("  1. press front-panel buttons to change the routing of an output (e.g. output "
                      f"{cap.opts.test_output});")
    cap.console.print("  2. unplug an HDMI cable from an output, wait 3 s, plug it back in;")
    cap.console.print("  3. if you can, power a source device off and on.")
    cap.console.print("Changed routing is restored afterwards.")
    cap.console.ask("Press Enter to start the window... ")
    cap.console.print(f"Listening for {seconds:g} s...")
    window = await cap.telnet.listen(seconds, role="push-window", label="front-panel window")
    after = await cap.snapshot()
    changes = diff(before, after)
    text = (window.get("response") or {}).get("text", "")
    lines = [ln.strip() for ln in re.split(r"\r\n|\n|\r", text) if ln.strip()]
    parsed = [m.groups() for m in (_PUSH_RE.search(ln) for ln in lines) if m]
    restored = None
    if changes:
        answer = cap.console.ask(f"The device changed during the window ({len(changes)} differences). "
                                 "Restore it? [Y/n] ")
        if answer is None or answer.strip().lower() in ("", "y", "yes"):
            remaining = await cap.restore_to(before, reason="push window")
            restored = not remaining
    cap.add(RecordIds.PROBE_PUSH_WINDOW, {
        "title": "Unsolicited Telnet output while the operator uses the front panel",
        "answers": ["push-wording"],
        "exchanges": [window],
        "findings": {
            "lines": lines,
            "cable_events_parsed": parsed,
            "unrecognised_lines": [ln for ln in lines if not _PUSH_RE.search(ln)],
            "state_changes": changes,
            "restored": restored,
        },
    })
    cap.console.print(f"  push window               -> {len(lines)} line(s): {lines[:5]}")
    if not cap.telnet.connected:
        await cap.reconnect_telnet()
