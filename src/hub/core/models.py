"""Matrix port and capability model (BE-26, D9).

One :class:`MatrixModel` says how many inputs, outputs and presets a matrix
has and which features it supports. Code that loops over ports or checks a
port number asks the model instead of hard-coding ``range(1, 9)``, so a 4x4
matrix (or several matrices, D9) costs a new constant, not a rewrite.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MatrixModel:
    """Port counts and capabilities of one matrix model."""

    model_id: str
    name: str
    input_count: int = 8
    output_count: int = 8
    preset_count: int = 8
    supports_telnet: bool = True
    supports_cec: bool = True
    supports_ext_audio: bool = True
    supports_hdr: bool = True
    supports_scaler: bool = True
    supports_arc: bool = True

    def __post_init__(self) -> None:
        for field_name in ("input_count", "output_count", "preset_count"):
            value = getattr(self, field_name)
            if type(value) is not int or value < 1:
                raise ValueError(f"{field_name} must be a positive integer, got {value!r}")

    @staticmethod
    def _validate(value: int, count: int, what: str) -> int:
        # bool is an int subclass; True must not pass as port 1.
        if type(value) is not int or not 1 <= value <= count:
            raise ValueError(f"{what} must be an integer in 1..{count}, got {value!r}")
        return value

    def validate_input(self, port: int) -> int:
        """Return ``port`` if it is a valid input number, else raise ``ValueError``."""
        return self._validate(port, self.input_count, "input")

    def validate_output(self, port: int) -> int:
        """Return ``port`` if it is a valid output number, else raise ``ValueError``."""
        return self._validate(port, self.output_count, "output")

    def validate_preset(self, preset: int) -> int:
        """Return ``preset`` if it is a valid preset number, else raise ``ValueError``."""
        return self._validate(preset, self.preset_count, "preset")

    def input_range(self) -> range:
        """Input numbers, 1-based."""
        return range(1, self.input_count + 1)

    def output_range(self) -> range:
        """Output numbers, 1-based."""
        return range(1, self.output_count + 1)

    def preset_range(self) -> range:
        """Preset numbers, 1-based."""
        return range(1, self.preset_count + 1)


BK808_MODEL = MatrixModel(model_id="bk808", name="OREI BK-808")
"""The OREI BK-808 8x8 matrix: the default model."""

BK404_MODEL = MatrixModel(
    model_id="bk404",
    name="OREI BK-404",
    input_count=4,
    output_count=4,
    preset_count=8,
)
"""A 4x4 matrix of the same family (D9: not yet tested against hardware)."""

_MODELS: dict[str, MatrixModel] = {m.model_id: m for m in (BK808_MODEL, BK404_MODEL)}


def _normalize(model_name: str) -> str:
    # "OREI BK-808", "bk_808" and "BK808" all name the same model.
    return re.sub(r"[^a-z0-9]", "", model_name.lower()).removeprefix("orei")


def get_matrix_model(model_name: str | None = None) -> MatrixModel:
    """The model called ``model_name`` (id or display name, case-insensitive).

    ``None`` or an empty name gives :data:`BK808_MODEL`. An unknown name raises
    ``ValueError`` rather than silently assuming an 8x8 matrix.
    """
    if model_name is None or not model_name.strip():
        return BK808_MODEL
    key = _normalize(model_name)
    for model in _MODELS.values():
        if key in (_normalize(model.model_id), _normalize(model.name)):
            return model
    known = ", ".join(sorted(_MODELS))
    raise ValueError(f"Unknown matrix model {model_name!r} (known: {known})")
