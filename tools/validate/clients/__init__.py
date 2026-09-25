"""Validation clients (VALIDATION_PLAN §4 "Real clients for V3").

``api`` and ``browser`` are implemented. ``ha``, ``uc`` and ``flic`` are
placeholders with the interface fixed, delivered by later work packages.
"""

from __future__ import annotations

from .api import ApiClient
from .base import ActionResult, Client, HubInfo, NotSupportedError, UnimplementedClient
from .browser import BrowserClient


class HomeAssistantClient(UnimplementedClient):
    name = "ha"
    work_package = "WP-D1"
    plan = ("a real homeassistant/home-assistant container with custom_components/hdmi_matrix installed and "
            "configured through HA's own API; service calls and entity states checked against the device")


class RemoteClient(UnimplementedClient):
    name = "uc"
    work_package = "WP-B1"
    plan = "the scripted Remote 3 (tools/uc_remote_sim.py) driving the integration WebSocket on port 9095"


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
    "HubInfo",
    "NotSupportedError",
    "make_client",
]
