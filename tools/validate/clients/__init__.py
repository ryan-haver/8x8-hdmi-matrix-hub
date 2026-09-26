"""Validation clients (VALIDATION_PLAN §4 "Real clients for V3").

``api``, ``browser``, ``uc`` (the scripted Remote 3, WP-B1) and ``ha`` (a real
Home Assistant container, WP-D1) are implemented. ``flic`` is a placeholder
with the interface fixed, delivered by a later work package.
"""

from __future__ import annotations

from .api import ApiClient
from .base import ActionResult, Client, HubInfo, NotSupportedError, UnimplementedClient
from .browser import BrowserClient
from .ha import HomeAssistantClient
from .uc import RemoteClient


class FlicClient(UnimplementedClient):
    name = "flic"
    work_package = "WP-D1 (Flic replay)"
    plan = "exact replay of the HTTP requests a Flic Hub sends, as documented in docs/FLIC_SETUP.md"


CLIENTS: dict[str, type[Client]] = {
    "api": ApiClient,
    "browser": BrowserClient,
    "ha": HomeAssistantClient,
    "uc": RemoteClient,
    "flic": FlicClient,
}


def make_client(name: str) -> Client:
    try:
        return CLIENTS[name]()
    except KeyError:
        raise ValueError(f"unknown client {name!r} (known: {', '.join(CLIENTS)})") from None


__all__ = [
    "CLIENTS",
    "ActionResult",
    "ApiClient",
    "BrowserClient",
    "Client",
    "HomeAssistantClient",
    "HubInfo",
    "NotSupportedError",
    "RemoteClient",
    "make_client",
]
