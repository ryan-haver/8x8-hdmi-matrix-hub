"""Client interface: how a scenario's user action is carried out.

A client turns an :class:`~tools.validate.model.Action` (an *intent* such as
``route``) into what a real user of that client does: a REST call (``api``),
clicks in the web UI (``browser``), a Home Assistant service call (``ha``), a
Remote 3 entity command (``uc``), or the exact request a Flic Hub sends
(``flic``). The runner only talks to this interface, so a new client plugs in
by subclassing :class:`Client` and registering it in ``clients/__init__.py``.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..model import Action


class NotSupportedError(Exception):
    """This client has no way to perform the intent (the scenario is skipped for it)."""


@dataclass
class HubInfo:
    """Where the hub under test is, handed to clients on start."""

    base_url: str
    forwarded_for: str = "10.99.0.1"
    artifacts_dir: Path | None = None


@dataclass
class ActionResult:
    """What the client did and what came back."""

    intent: str
    ok: bool
    started: float = field(default_factory=time.time)
    elapsed_ms: float = 0.0
    requests: list[dict[str, Any]] = field(default_factory=list)
    status: int | None = None
    body: Any = None
    error: str | None = None
    steps: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)


class Client(ABC):
    """A way for a user to drive the hub."""

    name: str = ""
    #: Intents this client can perform.
    intents: frozenset[str] = frozenset()
    #: Per-action context set by the runner before :meth:`perform`:
    #: ``label`` (scenario id, for artifact names) and ``forwarded_for`` (the
    #: client address this scenario uses; the hub rate-limits per client).
    context: dict[str, Any]

    def __init__(self) -> None:
        self.context = {}

    def supports(self, action: Action) -> bool:
        return action.intent in self.intents

    @abstractmethod
    async def start(self, hub: HubInfo) -> None:
        """Connect / launch (browser, HA container, scripted Remote, ...)."""

    @abstractmethod
    async def perform(self, action: Action) -> ActionResult:
        """Carry out one intent. Raise :class:`NotSupportedError` for unknown intents."""

    @abstractmethod
    async def stop(self) -> None:
        """Release everything started in :meth:`start`."""

    def environment(self) -> dict[str, Any]:
        """Client versions for the evidence record."""
        return {"name": self.name}


class UnimplementedClient(Client):
    """Placeholder for a client that a later work package delivers."""

    work_package = ""
    plan = ""

    async def start(self, hub: HubInfo) -> None:
        raise NotImplementedError(
            f"The '{self.name}' validation client is not implemented yet (planned in {self.work_package}: "
            f"{self.plan}). Implement tools/validate/clients/{self.name}.py by subclassing "
            "tools.validate.clients.base.Client (see docs/validation/README.md, 'Adding a client')."
        )

    async def perform(self, action: Action) -> ActionResult:  # pragma: no cover - start() already raised
        raise NotImplementedError(self.name)

    async def stop(self) -> None:
        return None
