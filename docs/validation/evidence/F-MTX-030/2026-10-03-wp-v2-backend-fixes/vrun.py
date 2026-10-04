"""`python -m tools.validate ...` with a high-resolution wall clock (see campaign.py: Windows +
Python 3.12 time.time() ticks every 15.6 ms, which lets WsObserver.sync() skip the fresh read).

Run from the repository root: python vrun.py run --client uc --record ...
"""
import runpy
import sys
import time

_WALL0, _PERF0 = time.time(), time.perf_counter()
time.time = lambda: _WALL0 + (time.perf_counter() - _PERF0)  # type: ignore[assignment]
sys.path.insert(0, ".")
sys.argv = ["tools.validate", *sys.argv[1:]]
runpy.run_module("tools.validate", run_name="__main__", alter_sys=True)
