"""
Dashboard Layout REST API.

Endpoints for managing the Dashboard tab's card grid (Phase 7).

The dashboard layout is a single ordered list of cards. Each card has a
``type`` discriminator (``profile``, ``preset``, ``system_shortcut``,
``macro``, or ``aggregate_widget``) and an ``id`` whose interpretation
depends on the type (profile id, preset number 1-8, shortcut id, etc.).

Routes (registered in app.py):

- GET    /api/dashboard/layout       — return the full layout
- PUT    /api/dashboard/layout       — replace the full layout atomically
- POST   /api/dashboard/cards        — add a single card (type, id in body)
- DELETE /api/dashboard/cards        — remove a single card (?type=&id=)
"""

import logging

from aiohttp import web

from dashboard_layout import (
    CARD_AGGREGATE_WIDGET,
    CARD_MACRO,
    CARD_PRESET,
    CARD_PROFILE,
    CARD_SYSTEM_SHORTCUT,
    VALID_CARD_TYPES,
    DashboardCard,
    DashboardLayout,
)

from .utils import _json_response, get_dashboard_layout_manager

_LOG = logging.getLogger("rest_api.dashboard_layout")


def _parse_card_type(raw: str) -> str | None:
    """Return the card type if valid, else None."""
    if not isinstance(raw, str):
        return None
    if raw not in VALID_CARD_TYPES:
        return None
    return raw


def _parse_card_id(raw, *, card_type: str) -> str | None:
    """Validate the card id for the given card type.

    For ``preset`` cards the id must be a stringified integer 1-8.
    For all other card types it must be a non-empty string.
    """
    if card_type == CARD_PRESET:
        try:
            n = int(raw)
        except (TypeError, ValueError):
            return None
        if n < 1 or n > 8:
            return None
        return str(n)
    if not isinstance(raw, str) or not raw:
        return None
    return raw


# =============================================================================
# Query endpoints
# =============================================================================


async def handle_get_layout(request: web.Request) -> web.Response:
    """GET /api/dashboard/layout — return the current full layout."""
    manager = get_dashboard_layout_manager()
    if manager is None:
        return _json_response(False, error="Dashboard layout manager not initialized", status=503)
    try:
        layout = manager.get_layout()
        return _json_response(True, layout.to_dict())
    except Exception as exc:
        _LOG.error("Error getting dashboard layout: %s", exc)
        return _json_response(False, error=str(exc), status=500)


# =============================================================================
# Mutation endpoints
# =============================================================================


async def handle_replace_layout(request: web.Request) -> web.Response:
    """PUT /api/dashboard/layout — replace the full layout atomically.

    Body: ``{"version": 1, "cards": [{"type": "...", "id": "...", "order": 0}, ...]}``

    Invalid entries are silently dropped (with a warning log). Duplicates
    are deduplicated by (type, id), keeping the first occurrence.
    """
    manager = get_dashboard_layout_manager()
    if manager is None:
        return _json_response(False, error="Dashboard layout manager not initialized", status=503)
    try:
        body = await request.json()
        cards_raw = body.get("cards", [])
        if not isinstance(cards_raw, list):
            return _json_response(False, error="cards must be a list", status=400)

        cards: list[DashboardCard] = []
        for entry in cards_raw:
            try:
                cards.append(DashboardCard.from_dict(entry))
            except ValueError as exc:
                _LOG.warning("Skipping invalid dashboard card in PUT: %s", exc)
                continue

        new_layout = DashboardLayout(
            cards=cards,
            version=int(body.get("version", 1)),
        )
        if not manager.replace_layout(new_layout):
            return _json_response(False, error="Failed to save layout", status=500)

        return _json_response(True, manager.get_layout().to_dict())
    except Exception as exc:
        _LOG.error("Error replacing dashboard layout: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_add_card(request: web.Request) -> web.Response:
    """POST /api/dashboard/cards — add a single card.

    Body: ``{"type": "profile", "id": "movie_night"}``
    """
    manager = get_dashboard_layout_manager()
    if manager is None:
        return _json_response(False, error="Dashboard layout manager not initialized", status=503)
    try:
        body = await request.json()
        card_type = _parse_card_type(body.get("type", ""))
        if card_type is None:
            return _json_response(
                False,
                error=f"Invalid type. Must be one of: {sorted(VALID_CARD_TYPES)}",
                status=400,
            )
        card_id = _parse_card_id(body.get("id"), card_type=card_type)
        if card_id is None:
            return _json_response(False, error="Invalid id for this card type", status=400)

        if not manager.add_card(card_type, card_id):
            # Could be duplicate or write failure
            if manager.has_card(card_type, card_id):
                return _json_response(
                    False,
                    error="Card already present on dashboard",
                    status=409,
                )
            return _json_response(False, error="Failed to add card", status=500)

        return _json_response(True, manager.get_layout().to_dict(), status=201)
    except Exception as exc:
        _LOG.error("Error adding dashboard card: %s", exc)
        return _json_response(False, error=str(exc), status=500)


async def handle_remove_card(request: web.Request) -> web.Response:
    """DELETE /api/dashboard/cards?type=profile&id=movie_night — remove a card."""
    manager = get_dashboard_layout_manager()
    if manager is None:
        return _json_response(False, error="Dashboard layout manager not initialized", status=503)
    try:
        card_type = _parse_card_type(request.query.get("type", ""))
        if card_type is None:
            return _json_response(
                False,
                error=f"Invalid type. Must be one of: {sorted(VALID_CARD_TYPES)}",
                status=400,
            )
        card_id = _parse_card_id(request.query.get("id"), card_type=card_type)
        if card_id is None:
            return _json_response(False, error="Invalid id for this card type", status=400)

        if not manager.remove_card(card_type, card_id):
            return _json_response(
                False,
                error="Card not found on dashboard",
                status=404,
            )

        return _json_response(True, manager.get_layout().to_dict())
    except Exception as exc:
        _LOG.error("Error removing dashboard card: %s", exc)
        return _json_response(False, error=str(exc), status=500)
