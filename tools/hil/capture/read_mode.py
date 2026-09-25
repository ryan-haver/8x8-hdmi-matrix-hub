"""``--mode read`` (default, safe): every read command, raw.

Sends only commands that do not change the device: the login, every read
comhead the hub uses plus the documented ones, ``GET /``, and the read-only
Telnet commands. Each request/response pair becomes one record.
"""

from __future__ import annotations

from . import catalog as cmd
from .context import Capture
from .fixtures import RecordIds


async def run_read(cap: Capture, login_exchange: dict) -> None:
    con = cap.console
    cap.add(RecordIds.LOGIN, {
        "title": "Login with the configured credentials (password redacted)",
        "answers": ["login-ok-result"],
        "exchanges": [login_exchange],
    })

    con.print(f"HTTP reads ({len(cmd.HTTP_READS)}):")
    for spec in cmd.HTTP_READS:
        comhead = spec.payload["comhead"]
        if comhead in cap.unanswered:
            # One timeout is the evidence; every further try costs the whole
            # HTTP timeout (V1.10.01: `preset get` 1-8, HIL-01).
            con.print(f"  {comhead:<24} {spec.payload.get('index', ''):<2} -> skipped (no answer earlier)")
            continue
        ex = await cap.http.post(spec.payload, role="read")
        status = (ex.get("response") or {}).get("status")
        con.print(f"  {comhead:<24} {spec.payload.get('index', ''):<2} -> "
                  f"{status if status else ex['error']['type']}")
        # A firmware without an optional read: a warning, not a capture failure.
        unanswered = comhead in cmd.OPTIONAL_READS and cap.note_unanswered(comhead, ex)
        if ex.get("error") and not unanswered:
            cap.errors.append(f"{spec.slug}: {ex['error']['message']}")
        cap.add(RecordIds.http_read(spec.slug), {
            "title": f"Read: {spec.payload['comhead']}",
            "note": spec.note,
            "answers": list(spec.answers),
            "exchanges": [ex],
        })

    page = await cap.http.get("/", role="page")
    cap.add(RecordIds.INDEX_PAGE, {"title": "GET / (web UI entry page)", "answers": [], "exchanges": [page]})

    if not cap.opts.telnet:
        con.print("Telnet: skipped (--no-telnet)")
        return
    banner = await cap.open_telnet()
    if banner is None or cap.telnet is None:
        con.print(f"Telnet: unavailable ({banner['error']['message'] if banner else 'disabled'})")
        if banner is not None:
            cap.add(RecordIds.TELNET_BANNER, {"title": "Telnet connect (failed)", "answers": [],
                                              "exchanges": [banner]})
        return
    cap.add(RecordIds.TELNET_BANNER, {
        "title": "Telnet connection banner",
        "answers": ["telnet-banner", "telnet-iac", "telnet-terminators"],
        "exchanges": [banner],
    })
    con.print(f"Telnet reads ({len(cmd.TELNET_READS)}):")
    for spec in cmd.TELNET_READS:
        ex = await cap.telnet.command(spec.command, role="read")
        resp = ex.get("response") or {}
        con.print(f"  {spec.command:<16} -> {resp.get('completion', ex.get('error'))} "
                  f"{len(resp.get('text', ''))} chars")
        if ex.get("error"):
            cap.errors.append(f"telnet {spec.command}: {ex['error']['message']}")
            if not cap.telnet.connected:
                await cap.reconnect_telnet()
        cap.add(RecordIds.telnet_read(spec.slug), {
            "title": f"Telnet read: {spec.command}",
            "answers": list(spec.answers),
            "exchanges": [ex],
        })
