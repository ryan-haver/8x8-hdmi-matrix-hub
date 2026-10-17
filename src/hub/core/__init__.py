"""Hub core: matrix model, names, events and the matrix service (WP-C3).

- :class:`MatrixModel` describes a matrix's port counts and capabilities
  (BE-26, D9), so nothing else hard-codes ``range(1, 9)``.
- :class:`NameStore` is the one store of input, output and preset names
  (BE-16, UC-08): device names merged with user overrides.
- :class:`EventBus` carries state changes to every subscriber.
- :class:`MatrixService` owns the connection and the last known snapshot
  (UC-17) and announces each change on the bus.
"""

from .event_bus import (
    STANDARD_TOPICS,
    TOPIC_CABLE,
    TOPIC_DISPLAY,
    TOPIC_HUB_CONNECTION,
    TOPIC_NAMES,
    TOPIC_POWER,
    TOPIC_PRESETS,
    TOPIC_ROUTING,
    TOPIC_SIGNAL,
    EventBus,
    HubEvent,
)
from .matrix_service import MatrixClient, MatrixService
from .models import BK404_MODEL, BK808_MODEL, MatrixModel, get_matrix_model
from .name_store import NameStore

__all__ = [
    "BK404_MODEL",
    "BK808_MODEL",
    "STANDARD_TOPICS",
    "TOPIC_CABLE",
    "TOPIC_DISPLAY",
    "TOPIC_HUB_CONNECTION",
    "TOPIC_NAMES",
    "TOPIC_POWER",
    "TOPIC_PRESETS",
    "TOPIC_ROUTING",
    "TOPIC_SIGNAL",
    "EventBus",
    "HubEvent",
    "MatrixClient",
    "MatrixModel",
    "MatrixService",
    "NameStore",
    "get_matrix_model",
]
