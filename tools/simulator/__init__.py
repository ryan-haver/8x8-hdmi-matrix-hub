"""OREI BK-808 matrix simulator (plan §5.1).

Run it with ``python -m tools.simulator`` (see ``tools/simulator/README.md``)
or embed it in tests::

    from tools.simulator import DeviceState, Simulator

    async with Simulator(DeviceState.default(), https_port=0, telnet_port=0, control_port=0) as sim:
        ...
"""

from .faults import Faults
from .server import Simulator
from .state import DeviceState, StateError, load_capture_dir

__all__ = ["DeviceState", "Faults", "Simulator", "StateError", "load_capture_dir"]
