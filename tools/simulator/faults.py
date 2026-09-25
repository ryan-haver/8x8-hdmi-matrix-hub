"""Fault-injection settings for the simulator.

Set through the control API (``POST /_sim/faults``) or directly on
``Simulator.faults`` in tests. Every field defaults to "healthy device".
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any

from . import protocol as proto

SESSION_EXPIRED_STYLES = ("json", "html", "http401")


@dataclass
class Faults:
    #: Extra delay before every HTTP and Telnet response.
    latency_ms: float = 0.0

    # --- HTTP (POST /cgi-bin/instr) --------------------------------------
    #: Answer with this HTTP status (e.g. 500) instead of the JSON response.
    http_status: int | None = None
    #: Send a truncated, unparseable JSON body.
    malformed_json: bool = False
    #: Close the TCP connection without answering (client sees a disconnect).
    drop_http: bool = False
    #: Never answer (client sees its own timeout).
    hang_http: bool = False
    #: Only apply the HTTP faults above to these comheads (None = all).
    comheads: list[str] | None = None
    #: Apply the HTTP faults above to the next N matching requests, then
    #: clear them (None = until cleared).
    http_fault_count: int | None = None

    # --- Device behaviour -------------------------------------------------
    #: Reject every login, even with correct credentials.
    wrong_password: bool = False
    #: Answer every write with result 0 and do not change state.
    reject_writes: bool = False
    #: How "not logged in / session expired" is reported.
    session_expired_style: str = proto.SESSION_EXPIRED_STYLE

    # --- Telnet -----------------------------------------------------------
    #: Accept Telnet connections and close them immediately.
    telnet_refuse: bool = False
    #: Send half of the next response, then close the connection.
    telnet_close_mid_command: bool = False
    #: Read commands but never answer.
    telnet_silent: bool = False
    #: Apply the two Telnet command faults above to the next N commands
    #: (None = until cleared).
    telnet_fault_count: int | None = None

    def update(self, patch: dict[str, Any]) -> None:
        known = {f.name: f for f in fields(self)}
        unknown = set(patch) - set(known)
        if unknown:
            raise ValueError(f"unknown fault(s): {sorted(unknown)}")
        for key, value in patch.items():
            if key == "session_expired_style" and value not in SESSION_EXPIRED_STYLES:
                raise ValueError(f"session_expired_style must be one of {SESSION_EXPIRED_STYLES}")
            if key == "comheads" and value is not None and not (
                isinstance(value, list) and all(isinstance(v, str) for v in value)
            ):
                raise ValueError("comheads must be a list of strings or null")
            setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    # ------------------------------------------------------------- helpers

    @property
    def any_http(self) -> bool:
        return bool(self.http_status or self.malformed_json or self.drop_http or self.hang_http)

    def http_applies(self, comhead: str | None) -> bool:
        if not self.any_http:
            return False
        if self.comheads is not None and comhead not in self.comheads:
            return False
        return self.http_fault_count is None or self.http_fault_count > 0

    def consume_http(self) -> None:
        if self.http_fault_count is not None:
            self.http_fault_count -= 1
            if self.http_fault_count <= 0:
                self.http_status = None
                self.malformed_json = self.drop_http = self.hang_http = False
                self.http_fault_count = None

    @property
    def any_telnet_command(self) -> bool:
        return self.telnet_close_mid_command or self.telnet_silent

    def consume_telnet(self) -> None:
        if self.telnet_fault_count is not None:
            self.telnet_fault_count -= 1
            if self.telnet_fault_count <= 0:
                self.telnet_close_mid_command = self.telnet_silent = False
                self.telnet_fault_count = None
