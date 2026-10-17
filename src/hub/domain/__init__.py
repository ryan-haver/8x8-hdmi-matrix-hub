"""The hub's domain layer (WP-C3).

Two consolidated services live here:

- :class:`~hub.domain.action_runner.ActionRunner` (API-19) — the one executor
  for profiles, scenes, macros, shortcuts and hardware presets. Every run
  returns the same :class:`~hub.domain.action_runner.ActionRunResult`, so REST
  handlers, the WebSocket bridge and the integrations agree on what happened.
- :class:`~hub.domain.visibility.VisibilityStore` (DI-5 / API-20) — the one
  view of the favorite and dashboard flags of everything the hub owns, and the
  one place they are written.

Both take their managers as arguments (see ``from_runtime()`` on each class for
wiring them to the running hub), which keeps the domain layer free of any
dependency on the REST layer's module globals.
"""

from .action_runner import ACTION_KINDS, ActionRunner, ActionRunResult, StepResult
from .visibility import VISIBILITY_KINDS, VisibilityStore

__all__ = [
    "ACTION_KINDS",
    "VISIBILITY_KINDS",
    "ActionRunResult",
    "ActionRunner",
    "StepResult",
    "VisibilityStore",
]
