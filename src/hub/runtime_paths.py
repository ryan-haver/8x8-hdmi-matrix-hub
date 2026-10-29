"""Read-only distribution resources and source/Docker configuration defaults."""

from __future__ import annotations

import csv
from importlib.metadata import distribution
from pathlib import Path, PurePosixPath

_PACKAGE = Path(__file__).resolve().parent
_PROJECT = _PACKAGE.parents[1]
# Only the package's own source tree qualifies; cwd and editable-install metadata
# must never redirect an installed wheel back to a checkout.
SOURCE_ROOT = (
    _PROJECT
    if _PROJECT / "src" / "hub" == _PACKAGE and (_PROJECT / "run.py").is_file() and (_PROJECT / "driver.json").is_file()
    else None
)


def default_config_dir(*, data_dir: Path | None = None) -> Path:
    """Keep local config separate; installed callers must supply writable storage."""
    if data_dir is not None:
        return data_dir
    if SOURCE_ROOT is not None:
        return SOURCE_ROOT / "config"
    raise ValueError("Installed runtime requires an explicit writable DATA_DIR (or MATRIX_DATA_DIR)")


def driver_metadata_path() -> Path:
    """Locate the one driver.json shipped by setuptools' distribution data-files."""
    if SOURCE_ROOT is not None:
        return SOURCE_ROOT / "driver.json"
    installed = distribution("ucapi-orei-hdmi-matrix")
    # Read RECORD itself: importlib.metadata.files can filter out paths which
    # pip --target relocated, including the prefix-relative driver.json entry.
    for row in csv.reader((installed.read_text("RECORD") or "").splitlines()):
        if row and PurePosixPath(row[0]).name == "driver.json":
            recorded = Path(str(installed.locate_file(row[0]))).resolve()
            if recorded.is_file():
                return recorded
            # pip --target relocates data-files beside the packages but retains
            # the original prefix-relative RECORD entry. Resolve that relocation
            # only from this distribution, never from cwd or another checkout.
            relocated = Path(str(installed.locate_file("driver.json"))).resolve()
            if relocated.is_file():
                return relocated
    raise FileNotFoundError("Installed ucapi-orei-hdmi-matrix distribution has no driver.json data-file")
