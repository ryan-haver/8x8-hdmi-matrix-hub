"""Test-only portable SIGTERM trigger and origin recorder; no runtime substitution."""

import atexit
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path


def watch():
    while not Path(os.environ["R1P_STOP"]).exists():
        time.sleep(0.02)
    signal.raise_signal(signal.SIGTERM)


def record():
    modules = {
        name: module.__file__
        for name, module in sys.modules.copy().items()
        if (name.startswith(("hub.", "rest_api.")) or name in {"hub", "rest_api", "orei_matrix", "version", "driver"})
        and getattr(module, "__file__", None)
    }
    Path(os.environ["R1P_RESULT"]).write_text(json.dumps(modules), encoding="utf-8")


if "R1P_STOP" in os.environ:
    atexit.register(record)
    threading.Thread(target=watch, daemon=True).start()
