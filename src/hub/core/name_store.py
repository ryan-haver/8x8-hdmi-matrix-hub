"""The single store of input, output and preset names (BE-16, UC-08).

Each name has three layers, highest first:

1. a user override (configured in the hub, e.g. a name the device cannot hold),
2. the name the matrix reports,
3. the generic default ("Input 3").

:meth:`NameStore.snapshot` gives the effective names. Every change of an
effective name publishes one ``"names"`` event, so a rename made anywhere
(web app, Remote, device front panel) reaches every subscriber.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Literal

from .event_bus import TOPIC_NAMES, EventBus
from .models import BK808_MODEL, MatrixModel

NameKind = Literal["inputs", "outputs", "presets"]
NAME_KINDS: tuple[NameKind, ...] = ("inputs", "outputs", "presets")

_DEFAULT_LABEL: dict[NameKind, str] = {"inputs": "Input", "outputs": "Output", "presets": "Preset"}

DeviceNames = Mapping[int, object] | Sequence[object]
"""Names keyed by 1-based port, or a device array (index 0 = port 1); non-strings count as empty."""


def _clean(name: object) -> str | None:
    if not isinstance(name, str):
        return None
    name = name.strip()
    return name or None


class NameStore:
    """Effective names for every input, output and preset of one matrix."""

    def __init__(
        self,
        model: MatrixModel = BK808_MODEL,
        bus: EventBus | None = None,
        overrides: Mapping[str, Mapping[int, str]] | None = None,
    ) -> None:
        self._model = model
        self._bus = bus
        self._device: dict[NameKind, dict[int, str]] = {kind: {} for kind in NAME_KINDS}
        self._overrides: dict[NameKind, dict[int, str]] = {kind: {} for kind in NAME_KINDS}
        for kind, names in (overrides or {}).items():
            k = self._kind(kind)
            for port, name in names.items():
                cleaned = _clean(name)
                if cleaned is not None:
                    self._overrides[k][self._validate(k, port)] = cleaned

    @property
    def model(self) -> MatrixModel:
        return self._model

    @property
    def bus(self) -> EventBus | None:
        return self._bus

    # -- lookups ----------------------------------------------------------

    @staticmethod
    def _kind(kind: str) -> NameKind:
        for k in NAME_KINDS:
            if kind == k:
                return k
        raise ValueError(f"Unknown name kind {kind!r} (expected one of {', '.join(NAME_KINDS)})")

    def _validate(self, kind: NameKind, port: int) -> int:
        if kind == "inputs":
            return self._model.validate_input(port)
        if kind == "outputs":
            return self._model.validate_output(port)
        return self._model.validate_preset(port)

    def _ports(self, kind: NameKind) -> range:
        if kind == "inputs":
            return self._model.input_range()
        if kind == "outputs":
            return self._model.output_range()
        return self._model.preset_range()

    def _effective(self, kind: NameKind, port: int) -> str:
        return self._overrides[kind].get(port) or self._device[kind].get(port) or f"{_DEFAULT_LABEL[kind]} {port}"

    def name(self, kind: str, port: int) -> str:
        """The effective name of ``port`` of ``kind`` ("inputs", "outputs", "presets")."""
        k = self._kind(kind)
        return self._effective(k, self._validate(k, port))

    def input_name(self, port: int) -> str:
        return self.name("inputs", port)

    def output_name(self, port: int) -> str:
        return self.name("outputs", port)

    def preset_name(self, preset: int) -> str:
        return self.name("presets", preset)

    def snapshot(self) -> dict[str, dict[int, str]]:
        """Effective names of every port: ``{"inputs": {1: ...}, "outputs": ..., "presets": ...}``."""
        return {kind: {port: self._effective(kind, port) for port in self._ports(kind)} for kind in NAME_KINDS}

    def overrides(self) -> dict[str, dict[int, str]]:
        """The user overrides only (what the hub persists)."""
        return {kind: dict(names) for kind, names in self._overrides.items()}

    # -- changes ----------------------------------------------------------

    def _set_override(self, kind: NameKind, port: int, name: str | None) -> bool:
        port = self._validate(kind, port)
        before = self.snapshot()
        cleaned = _clean(name)
        if cleaned is None:
            self._overrides[kind].pop(port, None)  # None or "" clears the override
        else:
            self._overrides[kind][port] = cleaned
        return self._announce(before, "user")

    def set_input_name(self, port: int, name: str | None) -> bool:
        """Set (or with ``None``/``""`` clear) the user override for an input.

        Returns True if the effective name changed.
        """
        return self._set_override("inputs", port, name)

    def set_output_name(self, port: int, name: str | None) -> bool:
        """Set (or clear) the user override for an output. True if the name changed."""
        return self._set_override("outputs", port, name)

    def set_preset_name(self, preset: int, name: str | None) -> bool:
        """Set (or clear) the user override for a preset. True if the name changed."""
        return self._set_override("presets", preset, name)

    def set_device_name(self, kind: str, port: int, name: str) -> bool:
        """Record that the matrix now holds ``name`` for ``port``.

        Used after a rename the matrix accepted: the device name is updated and
        any override for the port is dropped, so the new name is the one shown.
        Returns True if the effective name changed.
        """
        k = self._kind(kind)
        port = self._validate(k, port)
        before = self.snapshot()
        self._overrides[k].pop(port, None)
        cleaned = _clean(name)
        if cleaned is None:
            self._device[k].pop(port, None)
        else:
            self._device[k][port] = cleaned
        return self._announce(before, "device")

    def apply_device_names(
        self,
        inputs: DeviceNames | None = None,
        outputs: DeviceNames | None = None,
        presets: DeviceNames | None = None,
    ) -> bool:
        """Merge names reported by the matrix.

        Entries beyond the model's port count (the device sends a ninth
        terminator entry) and empty names are ignored; an empty name falls
        back to the generic default rather than keeping a stale one. Kinds left
        as ``None`` are untouched. Returns True if any effective name changed;
        then one ``"names"`` event carries every change.
        """
        before = self.snapshot()
        for kind, names in (("inputs", inputs), ("outputs", outputs), ("presets", presets)):
            if names is None:
                continue
            if isinstance(names, str):
                raise TypeError(f"{kind} names must be a mapping or a list of names, not a string")
            k = self._kind(kind)
            ports = self._ports(k)
            items: Iterable[tuple[object, object]] = (
                names.items() if isinstance(names, Mapping) else enumerate(names, start=1)
            )
            for port, raw in items:
                if type(port) is not int or port not in ports:
                    continue
                cleaned = _clean(raw)
                if cleaned is None:
                    self._device[k].pop(port, None)
                else:
                    self._device[k][port] = cleaned
        return self._announce(before, "device")

    def _announce(self, before: dict[str, dict[int, str]], source: str) -> bool:
        after = self.snapshot()
        changes = {
            kind: {port: name for port, name in after[kind].items() if before[kind].get(port) != name}
            for kind in NAME_KINDS
        }
        changes = {kind: ports for kind, ports in changes.items() if ports}
        if not changes:
            return False
        if self._bus is not None:
            self._bus.publish(TOPIC_NAMES, {"source": source, "changes": changes, "names": after})
        return True
