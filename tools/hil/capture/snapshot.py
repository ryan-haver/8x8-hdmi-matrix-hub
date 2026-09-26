"""Device state snapshots and diff-based restore (write mode safety net).

A :class:`Snapshot` is built from the HTTP status reads, optionally the LCD
line of the Telnet ``status`` dump (for the wording evidence) and the Telnet
``r preset N`` answers of the preset slots a test touches (V1.10.01 has no
HTTP preset read, HIL-01). :func:`plan_restore` turns "current vs. target"
into the list of writes that puts every restorable setting back; the capture
context executes them, logs each one, and verifies with a fresh snapshot.

Every setting is compared in the device's own codes (HDR 0-2, scaler 0-4,
EDID 1-47, LCD 0-4 from ``get system status.mode``) and restored with the
commands the device's web interface uses (WP-A4 part 2).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from . import catalog as cmd

_ROUTE_RE = re.compile(r"^output(\d+)->input(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
_PRESET_NONE_RE = re.compile(r"preset\s+\d+\s+is\s+none", re.IGNORECASE)


def _arr(doc: dict[str, Any] | None, key: str) -> list[Any] | None:
    if not isinstance(doc, dict):
        return None
    value = doc.get(key)
    return list(value[:8]) if isinstance(value, list) else None


def _val(doc: dict[str, Any] | None, key: str) -> Any:
    return doc.get(key) if isinstance(doc, dict) else None


def parse_preset(text: str | None) -> dict[str, Any] | None:
    """A Telnet ``r preset N`` answer: ``{"saved": True, "routing": [8 x input]}``,
    ``{"saved": False, "routing": None}`` for an empty slot, or None if unreadable."""
    if not text:
        return None
    if _PRESET_NONE_RE.search(text):
        return {"saved": False, "routing": None}
    routes = {int(o): int(i) for o, i in _ROUTE_RE.findall(text)}
    if sorted(routes) != list(range(1, 9)):
        return None
    return {"saved": True, "routing": [routes[o] for o in range(1, 9)]}


@dataclass
class Snapshot:
    power: int | None = None
    beep: int | None = None
    lock: int | None = None
    #: LCD on-time code (``get system status.mode``: 0 off, 1 always, 2-4 = 15/30/60 s)
    lcd: int | None = None
    routing: list[int] | None = None
    input_names: list[str] | None = None
    output_names: list[str] | None = None
    #: ``get video status.allname``
    preset_names: list[str] | None = None
    stream: list[int] | None = None
    hdcp: list[int] | None = None
    hdr: list[int] | None = None
    scaler: list[int] | None = None
    arc: list[int] | None = None
    mute: list[int] | None = None
    edid: list[int] | None = None
    cec_in: list[int] | None = None
    cec_out: list[int] | None = None
    exa_mode: int | None = None
    exa_enable: list[int] | None = None
    exa_source: list[int] | None = None
    exa_index: int | None = None
    #: 8 entries from Telnet ``r preset N`` (:func:`parse_preset`); None = slot not read
    presets: list[dict[str, Any] | None] | None = None
    #: the ``lcd ...`` line of the Telnet status dump (None = not read)
    lcd_line: str | None = None
    #: which reads failed (so a diff can tell "unknown" from "unchanged")
    errors: list[str] = field(default_factory=list)

    @classmethod
    def from_reads(cls, reads: dict[str, Any], lcd_line: str | None = None,
                   presets: list[dict[str, Any] | None] | None = None) -> Snapshot:
        video = reads.get("get video status")
        out = reads.get("get output status")
        inp = reads.get("get input status")
        cec = reads.get("get cec status")
        system = reads.get("get system status")
        ext = reads.get("get ext-audio status")
        return cls(
            power=_val(system, "power") if _val(system, "power") is not None else _val(video, "power"),
            beep=_val(system, "beep"),
            lock=_val(system, "lock"),
            lcd=_val(system, "mode"),
            routing=_arr(video, "allsource") or _arr(out, "allsource"),
            input_names=_arr(video, "allinputname") or _arr(inp, "inname"),
            output_names=_arr(video, "alloutputname") or _arr(out, "name"),
            preset_names=_arr(video, "allname"),
            stream=_arr(out, "allout"),
            hdcp=_arr(out, "allhdcp"),
            hdr=_arr(out, "allhdr"),
            scaler=_arr(out, "allscaler"),
            arc=_arr(out, "allarc"),
            mute=_arr(out, "allaudiomute"),
            edid=_arr(inp, "edid"),
            cec_in=_arr(cec, "inputindex"),
            cec_out=_arr(cec, "outputindex"),
            exa_mode=_val(ext, "mode"),
            exa_enable=_arr(ext, "allout"),
            exa_source=_arr(ext, "allsource"),
            exa_index=_val(ext, "index"),
            presets=presets,
            lcd_line=lcd_line,
            errors=[k for k, v in reads.items() if not isinstance(v, dict)],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SCALARS = ("power", "beep", "lock", "lcd", "exa_mode", "exa_index", "lcd_line")
_LISTS = (
    "routing", "input_names", "output_names", "preset_names", "stream", "hdcp", "hdr", "scaler", "arc", "mute",
    "edid", "cec_in", "cec_out", "exa_enable", "exa_source",
)


def diff(before: Snapshot, after: Snapshot) -> list[list[Any]]:
    """``[[field, port (1-based) or None, before, after], ...]`` for known values."""
    out: list[list[Any]] = []
    for name in _SCALARS:
        a, b = getattr(before, name), getattr(after, name)
        if a is not None and b is not None and a != b:
            out.append([name, None, a, b])
    for name in _LISTS:
        a, b = getattr(before, name), getattr(after, name)
        if a is None or b is None:
            continue
        for i, (x, y) in enumerate(zip(a, b, strict=False), 1):
            if x != y:
                out.append([name, i, x, y])
    if before.presets is not None and after.presets is not None:
        for i, (x, y) in enumerate(zip(before.presets, after.presets, strict=False), 1):
            if x is None or y is None:
                continue
            if x.get("saved") != y.get("saved"):
                out.append(["preset_saved", i, x.get("saved"), y.get("saved")])
            if x.get("routing") != y.get("routing") and x.get("saved") and y.get("saved"):
                out.append(["preset_routing", i, x.get("routing"), y.get("routing")])
    return out


@dataclass
class RestoreAction:
    field: str
    port: int | None
    before: Any
    target: Any
    payload: dict[str, Any] | None
    note: str = ""


def plan_restore(current: Snapshot, target: Snapshot, lcd_modes: dict[str, int] | None = None) -> tuple[
    list[RestoreAction], list[str]
]:
    """Writes that move ``current`` back to ``target``, in a safe order.

    Returns ``(actions, warnings)``; warnings name differences no command can
    restore (an LCD line whose code is unknown when ``get system status``
    carried no ``mode``).
    """
    actions: list[RestoreAction] = []
    warnings: list[str] = []

    def act(name: str, port: int | None, before: Any, tgt: Any, payload: dict[str, Any] | None, note: str = "") -> None:
        actions.append(RestoreAction(name, port, before, tgt, payload, note))

    # 1. power on first, so the rest is accepted
    if current.power == 0 and target.power == 1:
        act("power", None, 0, 1, cmd.power(1))

    # 2. presets: route live to the preset's routing and save it, or clear a
    #    slot that was empty; the live routing is restored below
    live = list(current.routing) if current.routing else None
    if current.presets is not None and target.presets is not None:
        for i, (cur, tgt) in enumerate(zip(current.presets, target.presets, strict=False), 1):
            if cur is None or tgt is None:
                continue
            if tgt.get("saved") and cur.get("routing") != tgt.get("routing") and tgt.get("routing"):
                for out_port, src in enumerate(tgt["routing"], 1):
                    if live is None or live[out_port - 1] != src:
                        act("routing", out_port, None if live is None else live[out_port - 1], src,
                            cmd.video_switch(out_port, src), f"staging preset {i}")
                        if live is not None:
                            live[out_port - 1] = src
                act("preset_routing", i, cur.get("routing"), tgt["routing"], cmd.preset_save(i))
            elif not tgt.get("saved") and cur.get("saved"):
                act("preset_saved", i, True, False, {"comhead": "preset clear", "language": 0, "index": i},
                    "the slot was empty before")
    if current.preset_names is not None and target.preset_names is not None:
        for i, (x, y) in enumerate(zip(current.preset_names, target.preset_names, strict=False), 1):
            if x != y:
                act("preset_names", i, x, y, cmd.preset_name(i, y))

    # 3. live routing
    if live is not None and target.routing is not None:
        for out_port, (cur_src, tgt_src) in enumerate(zip(live, target.routing, strict=False), 1):
            if cur_src != tgt_src:
                act("routing", out_port, cur_src, tgt_src, cmd.video_switch(out_port, tgt_src))

    # 4. names
    for name, builder in (("input_names", cmd.input_name), ("output_names", cmd.output_name)):
        cur, tgt = getattr(current, name), getattr(target, name)
        if cur is not None and tgt is not None:
            for port, (x, y) in enumerate(zip(cur, tgt, strict=False), 1):
                if x != y:
                    act(name, port, x, y, builder(port, y))

    # 5. per-output settings (device codes)
    for setting in cmd.OUTPUT_SETTINGS:
        cur, tgt = getattr(current, setting), getattr(target, setting)
        if cur is not None and tgt is not None:
            for port, (x, y) in enumerate(zip(cur, tgt, strict=False), 1):
                if x != y:
                    act(setting, port, x, y, cmd.output_setting(setting, port, y))

    # 6. EDID
    if current.edid is not None and target.edid is not None:
        for port, (x, y) in enumerate(zip(current.edid, target.edid, strict=False), 1):
            if x != y:
                act("edid", port, x, y, cmd.set_edid(port, y))

    # 7. CEC enable (the 8-element array form; the single-port form is rejected)
    if (
        target.cec_in is not None and target.cec_out is not None
        and (current.cec_in != target.cec_in or current.cec_out != target.cec_out)
    ):
        act("cec", None, [current.cec_in, current.cec_out], [target.cec_in, target.cec_out],
            cmd.cec_index_bulk(target.cec_in, target.cec_out))

    # 8. ext-audio: enable, then sources (``ext-audio switch`` applies in
    #    matrix mode 2, so switch to it first), then the selected output and mode
    if current.exa_enable is not None and target.exa_enable is not None:
        for port, (x, y) in enumerate(zip(current.exa_enable, target.exa_enable, strict=False), 1):
            if x != y:
                act("exa_enable", port, x, y, cmd.exa_out(port, y))
    mode_now = current.exa_mode
    if current.exa_source is not None and target.exa_source is not None:
        changes = [(p, x, y) for p, (x, y) in enumerate(zip(current.exa_source, target.exa_source, strict=False), 1)
                   if x != y]
        if changes and mode_now is not None and mode_now != 2:
            act("exa_mode", None, mode_now, 2, cmd.exa_mode(2), "matrix mode, to restore the sources")
            mode_now = 2
        for port, x, y in changes:
            act("exa_source", port, x, y, cmd.exa_switch(port, y))
    if current.exa_index is not None and target.exa_index is not None and current.exa_index != target.exa_index:
        act("exa_index", None, current.exa_index, target.exa_index, cmd.exa_index(target.exa_index))
    if mode_now is not None and target.exa_mode is not None and mode_now != target.exa_mode:
        act("exa_mode", None, mode_now, target.exa_mode, cmd.exa_mode(target.exa_mode))

    # 9. system
    if current.beep is not None and target.beep is not None and current.beep != target.beep:
        act("beep", None, current.beep, target.beep, cmd.beep(target.beep))
    if current.lock is not None and target.lock is not None and current.lock != target.lock:
        act("lock", None, current.lock, target.lock, cmd.panel_lock(target.lock))
    if current.lcd is not None and target.lcd is not None:
        if current.lcd != target.lcd:
            act("lcd", None, current.lcd, target.lcd, cmd.lcd_time(target.lcd))
    elif current.lcd_line is not None and target.lcd_line is not None and current.lcd_line != target.lcd_line:
        mode = (lcd_modes or {}).get(target.lcd_line)
        if mode is None:
            warnings.append(f"LCD changed {target.lcd_line!r} -> {current.lcd_line!r} and its code is unknown; "
                            "set it back on the front panel or in the web UI")
        else:
            act("lcd", None, current.lcd_line, target.lcd_line, cmd.lcd_time(mode))

    # 10. standby last
    if current.power == 1 and target.power == 0:
        act("power", None, 1, 0, cmd.power(0))
    return actions, warnings


def lcd_line(status_text: str) -> str | None:
    """The LCD line of a Telnet ``status`` dump (first line starting with ``lcd``)."""
    for line in status_text.replace("\r", "\n").split("\n"):
        if line.strip().lower().startswith("lcd"):
            return line.strip()
    return None


def status_changes(before: str, after: str) -> dict[str, list[str]]:
    """Lines of a Telnet ``status`` dump that changed (order-insensitive)."""
    a = [ln.strip() for ln in before.replace("\r", "\n").split("\n") if ln.strip()]
    b = [ln.strip() for ln in after.replace("\r", "\n").split("\n") if ln.strip()]
    sa, sb = set(a), set(b)
    return {"removed": [ln for ln in a if ln not in sb], "added": [ln for ln in b if ln not in sa]}
