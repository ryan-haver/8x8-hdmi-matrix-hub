"""Redaction keeps recorded TCP segment lengths consistent with the body.

A redacted Telnet answer is replayed to the hub split at the recorded segment
boundaries; if the lengths still describe the unredacted body, the replay
splits at the wrong offsets (this happened to the HIL Session 1 status dump
when its MAC address was redacted).
"""

from __future__ import annotations

from tools.hil.capture.fixtures import REDACTED, b64, find_secrets, scrub, unb64

SECRET = "6c:00:00:aa:bb:cc"


def _exchange(parts: list[bytes]) -> dict:
    body = b"".join(parts)
    return {"response": {"body_b64": b64(body), "chunks": [{"t_ms": i, "len": len(p)} for i, p in enumerate(parts)]}}


def _segments(ex: dict) -> list[bytes]:
    data, out, pos = unb64(ex["response"]["body_b64"]), [], 0
    for chunk in ex["response"]["chunks"]:
        out.append(data[pos:pos + chunk["len"]])
        pos += chunk["len"]
    assert pos == len(data)
    return out


def test_secret_inside_one_segment_adjusts_only_that_segment():
    parts = [b"status!\r\n", b"power on\r\n", f"mac address: {SECRET}\r\n".encode(), b"\r\n"]
    new, changed = scrub(_exchange(parts), [SECRET])
    assert changed
    segs = _segments(new)
    assert segs[:2] == parts[:2] and segs[3] == parts[3]
    assert segs[2] == f"mac address: {REDACTED}\r\n".encode()


def test_secret_spanning_segments_keeps_the_total_consistent():
    whole = f"mac address: {SECRET}\r\n".encode()
    parts = [whole[:18], whole[18:]]  # the secret is split across the two segments
    new, changed = scrub(_exchange(parts), [SECRET])
    assert changed
    assert b"".join(_segments(new)) == f"mac address: {REDACTED}\r\n".encode()


def test_secret_in_per_chunk_b64_field_is_scrubbed(tmp_path):
    doc = {"chunks": [{"t": "x", "b64": b64(f"mac {SECRET}".encode()), "text": f"mac {SECRET}"}]}
    new, changed = scrub(doc, [SECRET])
    assert changed
    assert SECRET.encode() not in unb64(new["chunks"][0]["b64"])
    path = tmp_path / "rec.json"
    import json

    path.write_text(json.dumps(doc), encoding="utf-8")
    assert find_secrets(path, [SECRET])  # the unredacted per-chunk b64 is detected
