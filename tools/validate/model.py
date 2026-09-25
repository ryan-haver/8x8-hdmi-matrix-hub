"""Verification levels and the scenario DSL (docs/validation/VALIDATION_PLAN.md §2, §4).

A scenario is a small declarative object: which features it proves, how to
prepare the device, one user action (an *intent* such as ``route``), and the
effects to check. The same scenario runs with every client that implements the
intent (``api``, ``browser``, later ``ha``/``uc``/``flic``) and against the
simulator or a real matrix. See ``docs/validation/README.md`` for a worked
example.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Literal

# --------------------------------------------------------------------------- levels


class Level(IntEnum):
    """Verification levels V0 (claimed) to V5 (field-proven)."""

    V0 = 0
    V1 = 1
    V2 = 2
    V3 = 3
    V4 = 4
    V5 = 5

    @classmethod
    def parse(cls, value: str | int | Level) -> Level:
        if isinstance(value, Level):
            return value
        if isinstance(value, int):
            return cls(value)
        text = str(value).strip().upper()
        if not re.fullmatch(r"V[0-5]", text):
            raise ValueError(f"not a verification level: {value!r} (expected V0..V5)")
        return cls[text]

    def __str__(self) -> str:  # "V2", not "Level.V2"
        return self.name


LEVEL_NAMES = {
    Level.V0: "Claimed",
    Level.V1: "Unit",
    Level.V2: "Simulated integration",
    Level.V3: "End-to-end",
    Level.V4: "Hardware",
    Level.V5: "Field",
}

Target = Literal["sim", "hardware"]
ClientName = Literal["api", "browser", "ha", "uc", "flic"]

#: Clients that count as a *real client* on the simulator (V3). ``api`` drives
#: the hub's REST API directly, which proves the hub code path (V2).
REAL_CLIENTS = frozenset({"browser", "ha", "uc", "flic"})


def level_for(target: str, client: str) -> Level:
    """The level a passing run proves."""
    if target == "hardware":
        return Level.V4
    return Level.V3 if client in REAL_CLIENTS else Level.V2


# --------------------------------------------------------------------------- state paths

_PATH_TOKEN = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_\-]*)|\[(-?\d+)\]")


def resolve(doc: Any, path: str) -> Any:
    """Read ``outputs[0].source`` / ``system.power`` / ``data.routing.1`` from a JSON document.

    Dotted segments are mapping keys (digits allowed: JSON object keys are
    strings), ``[n]`` indexes a list. Raises ``KeyError`` for a missing path.
    """
    cur = doc
    for part in path.split("."):
        pos = 0
        for m in _PATH_TOKEN.finditer(part):
            if m.start() != pos:
                raise KeyError(f"bad path segment {part!r} in {path!r}")
            pos = m.end()
            if m.group(1) is not None:
                if not isinstance(cur, dict) or m.group(1) not in cur:
                    raise KeyError(path)
                cur = cur[m.group(1)]
            else:
                idx = int(m.group(2))
                if not isinstance(cur, list) or not -len(cur) <= idx < len(cur):
                    raise KeyError(path)
                cur = cur[idx]
        if pos != len(part):
            raise KeyError(f"bad path segment {part!r} in {path!r}")
    return cur


def flatten(doc: Any, prefix: str = "") -> dict[str, Any]:
    """``{"outputs[0].source": 2, ...}`` for diffing two state documents."""
    out: dict[str, Any] = {}
    if isinstance(doc, dict):
        for k, v in doc.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = doc
    return out


def diff_states(before: dict[str, Any] | None, after: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Leaf-level differences between two state documents."""
    a, b = flatten(before or {}), flatten(after or {})
    return [
        {"path": k, "before": a.get(k), "after": b.get(k)}
        for k in sorted(set(a) | set(b))
        if a.get(k) != b.get(k)
    ]


def path_matches(path: str, pattern: str) -> bool:
    """``outputs[*].source`` style glob over flattened paths (``*`` matches one index or key)."""
    rx = re.escape(pattern).replace(r"\[\*\]", r"\[\d+\]").replace(r"\*", r"[^.\[\]]+")
    return re.fullmatch(rx + r"(\..*|\[.*)?", path) is not None


# --------------------------------------------------------------------------- actions


@dataclass(frozen=True)
class Action:
    """A user intent, carried out by a client (REST call, UI clicks, HA service, ...)."""

    intent: str
    params: dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        args = ", ".join(f"{k}={v!r}" for k, v in self.params.items())
        return f"{self.intent}({args})"


def act(intent: str, **params: Any) -> Action:
    return Action(intent, params)


#: Intents and what they mean. Clients implement a subset; ``request`` is the
#: raw escape hatch for the api client (failure paths, bad input).
INTENTS: dict[str, str] = {
    "route": "route input `input` to output `output`",
    "route_all": "route input `input` to every output",
    "preset_recall": "recall matrix preset `preset`",
    "preset_save": "save the current routing to preset `preset`",
    "preset_rename": "rename preset `preset` to `name` (hub-side name)",
    "matrix_power": "switch the matrix on (`on=True`) or to standby",
    "output_mute": "mute (`muted=True`) or unmute output `output` audio",
    "output_setting": "set output `output` `setting` (hdcp|hdr|scaler|arc|enable) with `body`",
    "cec_input": "send CEC `command` to the source on input `input`",
    "cec_output": "send CEC `command` to the display on output `output`",
    "profile_recall": "recall profile `profile_id` (optional `passcode`)",
    "request": "raw HTTP `method` `path` with optional `json` body (api client only)",
}


# --------------------------------------------------------------------------- expectations


@dataclass(frozen=True)
class Expectation:
    """Base class; ``finding`` names an open register row that makes this check fail today."""

    finding: str | None = field(default=None, kw_only=True)
    note: str = field(default="", kw_only=True)
    #: Evaluate only for these clients (``None`` = all). Use it when a check is
    #: about the client's own request, e.g. the REST route the api client calls.
    clients: tuple[str, ...] | None = field(default=None, kw_only=True)

    def describe(self) -> str:  # pragma: no cover - overridden
        raise NotImplementedError


@dataclass(frozen=True)
class Device(Expectation):
    """The device (simulator state or hardware readback) shows ``path == equals`` after the action.

    ``not_equals`` instead asserts a value is *not* present. Polled until
    ``timeout`` seconds (effects may land asynchronously).
    """

    path: str
    equals: Any = None
    not_equals: Any = None
    timeout: float = 5.0

    def describe(self) -> str:
        if self.not_equals is not None:
            return f"device {self.path} != {self.not_equals!r}"
        return f"device {self.path} == {self.equals!r}"


@dataclass(frozen=True)
class DeviceUnchanged(Expectation):
    """Nothing on the device changed except paths matching ``allow`` (globs, e.g. ``outputs[0].source``)."""

    allow: tuple[str, ...] = ()

    def describe(self) -> str:
        return "device otherwise unchanged" + (f" (allowed: {', '.join(self.allow)})" if self.allow else "")


@dataclass(frozen=True)
class CommandSent(Expectation):
    """The device received ``command`` whose payload contains ``payload`` (simulator command log).

    On hardware there is no command log; the check is reported as ``n/a`` and
    the effect is proven by readback and observation instead.
    """

    command: str
    payload: dict[str, Any] | None = None
    channel: str = "http"
    count: int | None = None  # exact number of matching commands, if given

    def describe(self) -> str:
        extra = f" with {self.payload}" if self.payload else ""
        n = f" exactly {self.count}x" if self.count is not None else ""
        return f"device received {self.channel} '{self.command}'{extra}{n}"


@dataclass(frozen=True)
class NoCommand(Expectation):
    """The device received no command matching ``command`` (``*`` = any write)."""

    command: str = "*"

    def describe(self) -> str:
        return "no write command reached the device" if self.command == "*" else f"device never received '{self.command}'"


@dataclass(frozen=True)
class NoProtocolWarnings(Expectation):
    """The simulator flagged no payload as malformed/undocumented for this action."""

    def describe(self) -> str:
        return "simulator raised no protocol warnings"


@dataclass(frozen=True)
class Response(Expectation):
    """The client's HTTP response (api client only; other clients report ``n/a``)."""

    status: int | tuple[int, ...] | None = None
    min_status: int | None = None
    json: dict[str, Any] | None = None  # subset match on the response body

    def describe(self) -> str:
        parts = []
        if self.status is not None:
            parts.append(f"HTTP {self.status}")
        if self.min_status is not None:
            parts.append(f"HTTP >= {self.min_status}")
        if self.json:
            parts.append(f"body contains {self.json}")
        return "response " + " and ".join(parts)


@dataclass(frozen=True)
class Hub(Expectation):
    """Read the hub's REST API after the action: ``GET path`` and check ``field`` (dotted path in the body)."""

    path: str
    field_path: str = ""
    equals: Any = None
    status: int | None = 200
    not_equals: Any = None
    absent_or_false: bool = False

    def describe(self) -> str:
        if self.absent_or_false:
            return f"hub GET {self.path} does not report {self.field_path} as true"
        if self.not_equals is not None:
            return f"hub GET {self.path} -> {self.field_path} != {self.not_equals!r}"
        target = f" -> {self.field_path} == {self.equals!r}" if self.field_path else ""
        st = f" (HTTP {self.status})" if self.status is not None else ""
        return f"hub GET {self.path}{target}{st}"


@dataclass(frozen=True)
class WsEvent(Expectation):
    """A WebSocket client connected to /ws received ``event`` whose data contains ``data``."""

    event: str
    data: dict[str, Any] | None = None
    timeout: float = 3.0

    def describe(self) -> str:
        return f"WebSocket event '{self.event}'" + (f" with {self.data}" if self.data else "")


@dataclass(frozen=True)
class NoWsEvent(Expectation):
    event: str
    timeout: float = 1.0

    def describe(self) -> str:
        return f"no WebSocket event '{self.event}'"


# --------------------------------------------------------------------------- scenario


@dataclass(frozen=True)
class Scenario:
    """One validated user flow.

    :param id: ``<area>.<flow>``, unique; referenced from ``features.yaml``.
    :param features: feature IDs this scenario proves (``F-MTX-001``...).
    :param covers: repo paths/globs whose change makes this evidence stale.
    :param writes: device state domains the action changes (``routing``,
        ``outputs``, ``power``, ``names``, ``presets``, ``system``, ``cec``,
        ``edid``, ``ext_audio``). Empty = read-only. Hardware runs refuse
        write scenarios without ``--allow-writes`` and refuse domains that
        cannot be restored (``presets``) without ``--allow-unrestorable``.
    :param sim_state: partial simulator state applied after the reset (sim only).
    :param faults: simulator faults applied just before the action (sim only).
    :param setup: actions run through the api client before the measured action.
    :param observe: questions for the operator on hardware (physical effect).
    :param cleanup: actions run through the api client afterwards (hub-side data).
    :param findings: open register rows known to make this scenario fail as a whole.
    :param restart_after: restart the hub afterwards (it may be left in a bad state).
    :param client_features: extra features proven only with that client, e.g.
        ``{"browser": ("F-UI-002",)}`` - the UI flow is only exercised in the browser.
    """

    id: str
    title: str
    features: tuple[str, ...]
    action: Action
    expect: tuple[Expectation, ...]
    covers: tuple[str, ...]
    kind: Literal["happy", "failure"] = "happy"
    clients: tuple[str, ...] = ("api",)
    targets: tuple[str, ...] = ("sim", "hardware")
    writes: tuple[str, ...] = ()
    sim_state: dict[str, Any] | None = None
    faults: dict[str, Any] | None = None
    setup: tuple[Action, ...] = ()
    observe: tuple[str, ...] = ()
    cleanup: tuple[Action, ...] = ()
    findings: tuple[str, ...] = ()
    restart_after: bool = False
    client_features: dict[str, tuple[str, ...]] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z0-9_]+\.[a-z0-9_]+", self.id):
            raise ValueError(f"scenario id {self.id!r} must look like 'area.flow'")
        if not self.features:
            raise ValueError(f"scenario {self.id} proves no feature")
        for f in (*self.features, *(x for fs in self.client_features.values() for x in fs)):
            if not re.fullmatch(r"F-[A-Z]+-\d{3}", f):
                raise ValueError(f"scenario {self.id}: bad feature id {f!r}")
        if self.action.intent not in INTENTS:
            raise ValueError(f"scenario {self.id}: unknown intent {self.action.intent!r}")
        if not self.covers:
            raise ValueError(f"scenario {self.id} must declare the code paths it covers (staleness)")
        if self.faults and "hardware" in self.targets:
            raise ValueError(f"scenario {self.id}: fault injection is simulator-only; set targets=('sim',)")

    def features_for(self, client: str) -> tuple[str, ...]:
        return (*self.features, *self.client_features.get(client, ()))

    @property
    def all_features(self) -> set[str]:
        return set(self.features).union(*self.client_features.values())

    @property
    def known_findings(self) -> set[str]:
        ids = set(self.findings)
        ids.update(e.finding for e in self.expect if e.finding)
        return ids
