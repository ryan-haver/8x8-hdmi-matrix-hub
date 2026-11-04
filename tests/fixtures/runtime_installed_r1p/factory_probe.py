"""Explicit factory double injected only into a disposable installed-test venv."""

import json
import os
import signal
import sys
from pathlib import Path

from hub import cli
from hub.runtime import composition

result = {}


def build_runtime(settings, *, environ):
    result.update(
        uc_enabled=settings.uc_enabled,
        data_dir=str(settings.data_dir),
        cli=cli.__file__,
        composition=composition.__file__,
        events=["factory"],
    )
    assert environ["UC_ENABLED"] == str(settings.uc_enabled).lower()
    return FactoryDouble()


class FactoryDouble:
    async def start(self):
        result["events"].append("start")
        signal.raise_signal(signal.SIGTERM)

    async def stop(self):
        result["events"].append("stop")
        result["ucapi_imported"] = "ucapi" in sys.modules
        result["legacy_imported"] = "driver" in sys.modules
        Path(os.environ["R1P_RESULT"]).write_text(json.dumps(result), encoding="utf-8")


composition.build_runtime = build_runtime
