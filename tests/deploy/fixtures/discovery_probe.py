"""Observe real mDNS traffic in a separate container, then fetch the advertised API.

This helper runs only in the observer container. It does not replace the hub's
entrypoint, Zeroconf implementation, REST server, or integration loader.
"""

from __future__ import annotations

import json
import sys
import threading
import urllib.request

from zeroconf import IPVersion, ServiceBrowser, Zeroconf

SERVICE_TYPE = "_orei-hdmi-matrix._tcp.local."


class Listener:
    def __init__(self, name: str) -> None:
        self.name = name
        self.added = threading.Event()
        self.removed = threading.Event()

    def add_service(self, zc: Zeroconf, service_type: str, name: str) -> None:
        if name != self.name or self.added.is_set():
            return
        info = zc.get_service_info(service_type, name, timeout=5000)
        if info is None:
            return
        addresses = info.parsed_addresses(IPVersion.V4Only)
        if not addresses:
            return
        with urllib.request.urlopen(  # noqa: S310 - isolated test network
            f"http://{addresses[0]}:{info.port}/api/health", timeout=5
        ) as response:
            health = json.loads(response.read())
        print(json.dumps({
            "event": "found", "name": name, "addresses": addresses,
            "port": info.port, "server": info.server,
            "properties": {k.decode(): v.decode() for k, v in info.properties.items()},
            "health": health,
        }), flush=True)
        self.added.set()

    def update_service(self, zc: Zeroconf, service_type: str, name: str) -> None:
        self.add_service(zc, service_type, name)

    def remove_service(self, zc: Zeroconf, service_type: str, name: str) -> None:
        if name == self.name and self.added.is_set():
            self.removed.set()


def main() -> None:
    listener = Listener(sys.argv[1])
    zc = Zeroconf(ip_version=IPVersion.V4Only)
    browser = ServiceBrowser(zc, SERVICE_TYPE, listener)
    try:
        assert listener.added.wait(35), "No reachable matching advertisement observed"
        assert listener.removed.wait(25), "No matching mDNS goodbye observed after hub shutdown"
        print(json.dumps({"event": "removed", "name": listener.name}), flush=True)
    finally:
        browser.cancel()
        zc.close()


if __name__ == "__main__":
    main()
