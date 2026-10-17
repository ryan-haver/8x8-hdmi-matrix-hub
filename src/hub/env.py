"""The canonical environment variable specification for the hub (DI-12).

One table, one resolver. Every variable the hub reads is listed in
:data:`CORE_ENV_VARS` (the core hub) or :data:`INTEGRATION_ENV_VARS` (opt-in
integrations), each with its default, its meaning and the retired name that
still maps onto it. :func:`resolve_hub_env` turns an environment mapping into
canonical values plus one deprecation message per retired name, so start-up can
say exactly what to change instead of silently preferring one spelling.

    >>> values, warnings = resolve_hub_env({"OREI_HOST": "10.0.0.5"})
    >>> values["MATRIX_HOST"], warnings
    ('10.0.0.5', ['OREI_HOST -> use MATRIX_HOST'])

Precedence
==========
A canonical name always wins over its aliases. An alias is only read when the
canonical name is unset or empty, and an alias that disagrees with an explicit
canonical value is reported as ignored rather than silently dropped.

Retired names
=============
:data:`RETIRED_ENV_VARS` holds names that no longer change anything (the mode
follows ``UC_ENABLED``; the web UI is part of the core). Setting one produces a
warning saying so, once, and never a behaviour change.

Deliberately *not* aliases
==========================
``OREI_USER``, ``OREI_PASSWORD``, ``OREI_VERIFY_SSL``, ``OREI_TELNET_PORT`` and
the ``OREI_*`` tuning knobs are still read directly by the transport layer
(``orei_matrix.py``) and are not spellings of a canonical hub variable. This
module does not pretend otherwise.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

#: Values accepted as "true" for a boolean variable.
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})

#: Values accepted as "false" for a boolean variable.
FALSE_VALUES = frozenset({"0", "false", "no", "off"})


@dataclass(frozen=True)
class EnvVar:
    """One environment variable: what it is called, what it means, what to use."""

    name: str
    description: str
    default: str | None = None
    kind: str = "core"
    aliases: tuple[str, ...] = ()
    secret: bool = False
    choices: tuple[str, ...] = ()

    @property
    def is_boolean(self) -> bool:
        """True when the variable is a flag, i.e. its choices are true/false."""
        return bool(self.choices) and set(self.choices) <= TRUE_VALUES | FALSE_VALUES

    def describe(self) -> dict[str, Any]:
        """A JSON-friendly summary, for the docs build and ``/api/system/info``."""
        return {
            "name": self.name,
            "description": self.description,
            "default": self.default,
            "kind": self.kind,
            "aliases": list(self.aliases),
            "deprecated_aliases": list(ENV_ALIASES.get(self.name, ())),
            "secret": self.secret,
            "choices": list(self.choices),
        }


_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_SCHEMES = ("true", "false")


# ---------------------------------------------------------------------------
# Canonical names -> retired names still accepted (first one set wins).
# ---------------------------------------------------------------------------

ENV_ALIASES: dict[str, tuple[str, ...]] = {
    "MATRIX_HOST": ("OREI_HOST",),
    "MATRIX_PORT": ("OREI_PORT",),
    "API_PORT": ("REST_API_PORT", "OREI_API_PORT"),
    "DATA_DIR": ("MATRIX_DATA_DIR",),
    "UC_INTEGRATION_HTTP_PORT": ("UC_PORT",),
    "UC_DISABLE_MDNS_PUBLISH": ("UC_DISABLE_MDNS",),
}

#: Variables that no longer change anything, with the reason logged when set.
RETIRED_ENV_VARS: dict[str, str] = {
    "USE_MODULAR": "the mode follows UC_ENABLED",
    "WEBUI_ENABLED": "the web UI and kiosk are part of the core and always served",
}


# ---------------------------------------------------------------------------
# The core hub
# ---------------------------------------------------------------------------

CORE_ENV_VARS: dict[str, EnvVar] = {
    var.name: var
    for var in (
        EnvVar(
            name="MATRIX_HOST",
            description="IP address or host name of the OREI matrix.",
            kind="core",
        ),
        EnvVar(
            name="MATRIX_PORT",
            description="HTTPS port of the matrix's web API.",
            default="443",
            kind="core",
        ),
        EnvVar(
            name="MATRIX_USER",
            description="User name for the matrix's Telnet command interface.",
            default="Admin",
            kind="core",
        ),
        EnvVar(
            name="MATRIX_PASSWORD",
            description="Password for the matrix's Telnet command interface.",
            kind="core",
            secret=True,
        ),
        EnvVar(
            name="MATRIX_VERIFY_TLS",
            description="Verify the matrix's HTTPS certificate.",
            default="false",
            kind="core",
            choices=_SCHEMES,
        ),
        EnvVar(
            name="API_PORT",
            description="Port for the REST API, the web UI and the kiosk.",
            default="8080",
            kind="core",
        ),
        EnvVar(
            name="DATA_DIR",
            description="Directory for every persistent file the hub writes.",
            kind="core",
        ),
        EnvVar(
            name="LOG_LEVEL",
            description="Root log level for the hub.",
            default="INFO",
            kind="core",
            choices=_LOG_LEVELS,
        ),
        EnvVar(
            name="ADMIN_PIN",
            description="PIN for the web admin. Unset means no admin session.",
            kind="core",
            secret=True,
        ),
        EnvVar(
            name="CONTROL_PIN",
            description="Optional second PIN that unlocks control-level access only.",
            kind="core",
            secret=True,
        ),
        EnvVar(
            name="ALLOWED_HOSTS",
            description="Comma-separated Host header values accepted in addition to IPs and localhost.",
            kind="core",
        ),
        EnvVar(
            name="CORS_ALLOWED_ORIGINS",
            description="Comma-separated allowed origins, or '*'. Same-origin is always allowed.",
            kind="core",
        ),
    )
}


# ---------------------------------------------------------------------------
# Opt-in integrations
# ---------------------------------------------------------------------------

INTEGRATION_ENV_VARS: dict[str, EnvVar] = {
    var.name: var
    for var in (
        EnvVar(
            name="UC_ENABLED",
            description="Start the Unfolded Circle Remote integration. A disabled integration is never imported.",
            default="false",
            kind="integration",
            choices=_SCHEMES,
        ),
        EnvVar(
            name="UC_INTEGRATION_HTTP_PORT",
            description="WebSocket port the Remote 3 integration listens on.",
            default="9095",
            kind="integration",
        ),
        EnvVar(
            name="UC_INTEGRATION_INTERFACE",
            description="Bind address for the integration; also the address published by mDNS.",
            kind="integration",
        ),
        EnvVar(
            name="UC_DISABLE_MDNS_PUBLISH",
            description="Do not announce the integration over mDNS (bridge networking).",
            default="false",
            kind="integration",
            choices=_SCHEMES,
        ),
        EnvVar(
            name="UC_CONFIG_HOME",
            description="Integration state directory (defaults to DATA_DIR).",
            kind="integration",
        ),
        EnvVar(
            name="UC_DRIVER_URL",
            description="ws:// or wss:// URL the Remote should dial, when mDNS cannot reach it.",
            kind="integration",
        ),
        EnvVar(
            name="UC_AUTH_TOKEN",
            description="Shared token the Remote presents to the hub (falls back to ADMIN_PIN).",
            kind="integration",
            secret=True,
        ),
        EnvVar(
            name="FLIC_ENABLED",
            description="Accept button registrations from a Flic Hub.",
            default="false",
            kind="integration",
            choices=_SCHEMES,
        ),
        EnvVar(
            name="HA_DISCOVERY_ENABLED",
            description="Publish the hub to Home Assistant over mDNS/zeroconf.",
            default="false",
            kind="integration",
            choices=_SCHEMES,
        ),
    )
}

#: Every canonical variable, core first.
ALL_ENV_VARS: dict[str, EnvVar] = {**CORE_ENV_VARS, **INTEGRATION_ENV_VARS}


def canonical_env_names() -> tuple[str, ...]:
    """Every canonical variable name, core first, in declaration order."""
    return tuple(ALL_ENV_VARS)


def env_var(name: str) -> EnvVar | None:
    """The specification of one canonical variable, or ``None`` if unknown."""
    return ALL_ENV_VARS.get(name)


def describe_env() -> dict[str, Any]:
    """The whole specification, plus the retired names, for docs and the API."""
    return {
        "core": [var.describe() for var in CORE_ENV_VARS.values()],
        "integrations": [var.describe() for var in INTEGRATION_ENV_VARS.values()],
        "retired": {name: reason for name, reason in RETIRED_ENV_VARS.items()},
    }


def env_bool(value: str | None, default: bool = False) -> bool:
    """Read a boolean variable. Empty, missing or unrecognised means ``default``."""
    if value is None:
        return default
    text = value.strip()
    if not text:
        return default
    lowered = text.lower()
    if lowered in TRUE_VALUES:
        return True
    if lowered in FALSE_VALUES:
        return False
    return default


def _value(environ: Mapping[str, str], name: str) -> str:
    raw = environ.get(name)
    return raw.strip() if isinstance(raw, str) else ""


def resolve_hub_env(environ: Mapping[str, str]) -> tuple[dict[str, str], list[str]]:
    """Resolve every canonical variable and collect one warning per retired name.

    Only non-empty values count, so ``FOO=""`` is treated as unset — which is
    what the modules that read these variables do.

    :returns: ``(canonical values, deprecation warnings)``. Both are in
        declaration order, so the warnings read the same way on every start-up.
    """
    values: dict[str, str] = {}
    warnings: list[str] = []

    for name in ALL_ENV_VARS:
        value = _value(environ, name)
        for alias in ENV_ALIASES.get(name, ()):
            alias_value = _value(environ, alias)
            if not alias_value:
                continue
            if not value:
                value = alias_value
                warnings.append(f"{alias} -> use {name}")
            elif alias_value != value:
                warnings.append(f"{alias} ignored ({name} is set)")
        if value:
            values[name] = value

    for name, reason in RETIRED_ENV_VARS.items():
        if _value(environ, name):
            warnings.append(f"{name} is ignored ({reason})")

    return values, warnings


def resolve_hub_env_from_os() -> tuple[dict[str, str], list[str]]:
    """:func:`resolve_hub_env` over the real process environment."""
    return resolve_hub_env(os.environ)


__all__ = [
    "ALL_ENV_VARS",
    "CORE_ENV_VARS",
    "ENV_ALIASES",
    "FALSE_VALUES",
    "INTEGRATION_ENV_VARS",
    "RETIRED_ENV_VARS",
    "TRUE_VALUES",
    "EnvVar",
    "canonical_env_names",
    "describe_env",
    "env_bool",
    "env_var",
    "resolve_hub_env",
    "resolve_hub_env_from_os",
]
