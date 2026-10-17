"""
Request body validation helpers (API-15).

Handlers read their body with :func:`parse_json_object` and check each field
with the bounded validators below. Every helper raises :class:`BadRequestError`
on bad input, which a handler answers with ``exc.response()`` (400). A body
that is not a JSON object (``[]``, ``"str"``, ``123``, ``null``), invalid JSON,
or a field of the wrong type is therefore a 400, never a 500 from an
``AttributeError`` or ``TypeError`` further down.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from aiohttp import web

from .utils import _json_response

#: Matrix ports (inputs and outputs) and hardware preset slots are numbered 1-8.
MIN_PORT = 1
MAX_PORT = 8
MIN_PRESET = 1
MAX_PRESET = 8

#: Default limits for fields that had none before API-15. Endpoints with
#: documented limits of their own (macros, matrix port names) keep them.
NAME_MAX_LENGTH = 64
DESCRIPTION_MAX_LENGTH = 500
ICON_MAX_LENGTH = 64
MAX_STEPS = 50
MAX_LIST_ITEMS = 500

_INT_STRING = re.compile(r"-?[0-9]+")


class BadRequestError(Exception):
    """A malformed request, answered with 400 and ``message``."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def response(self) -> web.Response:
        """The 400 response for this error."""
        error_id = uuid.uuid4().hex[:8]
        resp = _json_response(False, error=self.message, status=400)
        body = json.loads(resp.text or "{}")
        body["error_id"] = error_id
        return web.json_response(body, status=400, headers={"X-Error-Id": error_id})


async def parse_json_object(request: web.Request, *, allow_empty: bool = False) -> dict[str, Any]:
    """Return the request body, which must be a JSON object.

    With ``allow_empty`` a request without a body is read as ``{}`` (for
    endpoints whose body is optional).
    """
    if allow_empty and not request.can_read_body:
        return {}
    try:
        body = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        raise BadRequestError("Invalid JSON body") from None
    if not isinstance(body, dict):
        raise BadRequestError("Request body must be a JSON object")
    return body


def require_field(body: dict[str, Any], key: str, message: str | None = None) -> Any:
    """Return ``body[key]``; a missing or null field is refused."""
    value = body.get(key)
    if value is None:
        raise BadRequestError(message or f"Missing '{key}' parameter")
    return value


def validate_int(value: Any, name: str, *, minimum: int, maximum: int, message: str | None = None) -> int:
    """Return ``value`` as an int within ``minimum``-``maximum``.

    Integers and integer strings (path and query parameters are strings) are
    accepted; booleans, floats, lists and objects are refused.
    """
    error = message or f"{name} must be {minimum}-{maximum}"
    if isinstance(value, bool):
        raise BadRequestError(error)
    if isinstance(value, int):
        number = value
    elif isinstance(value, str) and _INT_STRING.fullmatch(value.strip()):
        number = int(value.strip())
    else:
        raise BadRequestError(error)
    if not minimum <= number <= maximum:
        raise BadRequestError(error)
    return number


def validate_port(value: Any, name: str = "Port", message: str | None = None) -> int:
    """Return a matrix port number (1-8)."""
    return validate_int(value, name, minimum=MIN_PORT, maximum=MAX_PORT, message=message)


def validate_preset(value: Any, name: str = "Preset", message: str | None = None) -> int:
    """Return a hardware preset number (1-8)."""
    return validate_int(value, name, minimum=MIN_PRESET, maximum=MAX_PRESET, message=message)


def validate_bool(value: Any, name: str) -> bool:
    """Return ``value`` if it is a JSON boolean; ``"false"`` and ``0`` are refused, not read as truthy."""
    if not isinstance(value, bool):
        raise BadRequestError(f"'{name}' must be true or false")
    return value


def optional_bool(body: dict[str, Any], key: str, default: bool | None = None) -> bool | None:
    """Return the boolean ``body[key]``, or ``default`` when it is absent or null."""
    value = body.get(key)
    if value is None:
        return default
    return validate_bool(value, key)


def validate_string(
    value: Any, name: str, *, max_length: int = NAME_MAX_LENGTH, allow_empty: bool = False, strip: bool = True
) -> str:
    """Return ``value`` as a string of at most ``max_length`` characters."""
    if not isinstance(value, str):
        raise BadRequestError(f"'{name}' must be a string")
    if strip:
        value = value.strip()
    if not value and not allow_empty:
        raise BadRequestError(f"'{name}' must not be empty")
    if len(value) > max_length:
        raise BadRequestError(f"'{name}' cannot exceed {max_length} characters")
    return value


def optional_string(
    body: dict[str, Any], key: str, *, max_length: int = NAME_MAX_LENGTH, allow_empty: bool = False
) -> str | None:
    """Return the string ``body[key]``, or None when it is absent or null."""
    value = body.get(key)
    if value is None:
        return None
    return validate_string(value, key, max_length=max_length, allow_empty=allow_empty)


def validate_list(value: Any, name: str, *, max_items: int = MAX_LIST_ITEMS) -> list:
    """Return ``value`` if it is a list of at most ``max_items`` entries."""
    if not isinstance(value, list):
        raise BadRequestError(f"'{name}' must be a list")
    if len(value) > max_items:
        raise BadRequestError(f"'{name}' cannot have more than {max_items} items")
    return value


def validate_steps(value: Any, name: str = "steps", *, max_steps: int = MAX_STEPS) -> list:
    """Return a non-empty step list of at most ``max_steps`` entries."""
    steps = validate_list(value, name, max_items=max_steps)
    if not steps:
        raise BadRequestError(f"'{name}' must not be empty")
    return steps
