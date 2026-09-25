"""Device state snapshots and diff-based restore (write mode safety net).

A :class:`Snapshot` is built from the HTTP status reads (plus, optionally, the
LCD line of the Telnet ``status`` dump, the only place the LCD timeout is
visible). :func:`plan_restore` turns "current vs. target" into the list of
writes that puts every restorable setting back; the capture context executes
them, logs each one, and verifies with a fresh snapshot.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from . import catalog as cmd


def _arr(doc: dict[str, Any] | None, key: str) -> list[Any] | None:
    if not isinstance(doc, dict):
        return None
    value = doc.get(key)
    return list(value[:8]) if isinstance(value, list) else None


def _val(doc: dict[str, Any] | None, key: str) -> Any:
    return doc.get(key) if isinstance(doc, dict) else None


@dataclass
class Snapshot:
    power: int | None = None
    beep: int | None = None
    lock: int | None = None
    routing: list[int] | None = None
    input_names: list[str] | None = None
    output_names: list[str] | None = None
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
    #: [{"name": str, "routing": [8 x int]}] from ``get routing status``
    presets: list[dict[str, Any]] | None = None
    #: the ``lcd ...`` line of the Telnet status dump (None = not read)
    lcd_line: str | None = None
    #: which reads failed (so a diff can tell "unknown" from "unchanged")
    errors: list[str] = field(default_factory=list)

    @classmethod
    def from_reads(cls, reads: dict[str, Any], lcd_line: str | None = None) -> Snapshot:
        video = reads.get("get video status")
        out = reads.get("get output status")
        inp = reads.get("get input status")
        cec = reads.get("get cec status")
        system = reads.get("get system status")
        ext = reads.get("get ext-audio status")
        routing = reads.get("get routing status")
        presets = None
        allpreset = _val(routing, "allpreset")
        if isinstance(allpreset, list):
            presets = [
                {"name": p.get("name"), "routing": list(p.get("allsource") or [])[:8]}
                for p in allpreset[:8]
                if isinstance(p, dict)
            ]
        return cls(
            power=_val(system, "power") if _val(system, "power") is not None else _val(video, "power"),
            beep=_val(system, "beep"),
            lock=_val(system, "lock"),
            routing=_arr(video, "allsource") or _arr(out, "allsource"),
            input_names=_arr(video, "allinputname") or _arr(inp, "inname"),
            output_names=_arr(video, "alloutputname") or _arr(out, "alloutputname"),
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
            presets=presets,
            lcd_line=lcd_line,
            errors=[k for k, v in reads.items() if not isinstance(v, dict)],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SCALARS = ("power", "beep", "lock", "exa_mode", "lcd_line")
_LISTS = (
    "routing", "input_names", "output_names", "stream", "hdcp", "hdr", "scaler", "arc", "mute",
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
            if x.get("routing") != y.get("routing"):
                out.append(["preset_routing", i, x.get("routing"), y.get("routing")])
            if x.get("name") != y.get("name"):
                out.append(["preset_name", i, x.get("name"), y.get("name")])
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
    restore (preset names, an LCD line whose code is unknown).
    """
    actions: list[RestoreAction] = []
    warnings: list[str] = []

    def act(name: str, port: int | None, before: Any, tgt: Any, payload: dict[str, Any] | None, note: str = "") -> None:
        actions.append(RestoreAction(name, port, before, tgt, payload, note))

    # 1. power on first, so the rest is accepted
    if current.power == 0 and target.power == 1:
        act("power", None, 0, 1, cmd.power(1))

    # 2. presets: route live to the preset's routing, save, routing restored below
    live = list(current.routing) if current.routing else None
    if current.presets is not None and target.presets is not None:
        for i, (cur, tgt) in enumerate(zip(current.presets, target.presets, strict=False), 1):
            if cur.get("routing") != tgt.get("routing") and tgt.get("routing"):
                for out_port, src in enumerate(tgt["routing"], 1):
                    if live is None or live[out_port - 1] != src:
                        act("routing", out_port, None if live is None else live[out_port - 1], src,
                            cmd.video_switch(out_port, src), f"staging preset {i}")
                        if live is not None:
                            live[out_port - 1] = src
                act("preset_routing", i, cur.get("routing"), tgt["routing"], cmd.preset_save(i))
            if cur.get("name") != tgt.get("name"):
                warnings.append(f"preset {i} name changed {tgt.get('name')!r} -> {cur.get('name')!r}; "
                                "no command restores preset names (fix it in the web UI)")

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

    # 5. per-output settings
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
                act("edid", port, x, y, cmd.input_edid(port, y))

    # 7. CEC enable (documented bulk shape)
    if (
        target.cec_in is not None and target.cec_out is not None
        and (current.cec_in != target.cec_in or current.cec_out != target.cec_out)
    ):
        act("cec", None, [current.cec_in, current.cec_out], [target.cec_in, target.cec_out],
            cmd.cec_index_bulk(target.cec_in, target.cec_out))

    # 8. ext-audio
    if current.exa_mode is not None and target.exa_mode is not None and current.exa_mode != target.exa_mode:
        act("exa_mode", None, current.exa_mode, target.exa_mode, cmd.exa_mode(target.exa_mode))
    for name in ("exa_enable", "exa_source"):
        cur, tgt = getattr(current, name), getattr(target, name)
        if cur is not None and tgt is not None:
            for port, (x, y) in enumerate(zip(cur, tgt, strict=False), 1):
                if x != y:
                    payload = cmd.exa_enable(port, bool(y)) if name == "exa_enable" else cmd.exa_source(port, y)
                    act(name, port, x, y, payload)

    # 9. system
    if current.beep is not None and target.beep is not None and current.beep != target.beep:
        act("beep", None, current.beep, target.beep, cmd.beep(target.beep))
    if current.lock is not None and target.lock is not None and current.lock != target.lock:
        act("lock", None, current.lock, target.lock, cmd.panel_lock(target.lock))
    if current.lcd_line is not None and target.lcd_line is not None and current.lcd_line != target.lcd_line:
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
