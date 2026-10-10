"""Dashboard layout routes (UI-55/UI-57, owner decision 2026-10-09).

Widgets (Routing, CEC Remote) are pinned per browser, never dashboard cards. The
seed layout is a stored pre-UI-57 layout: the three ``aggregate_widget`` cards every
install was seeded with (orders 0-2), then seven item cards (orders 3-9). The hub
drops the widget cards when it loads the file and renumbers the rest from 0.

Other scenarios may append cards later in a run (the browser ``macro_run`` adds a
macro through the card picker), so only the stored seven are checked, by position.
"""

from tools.validate.model import DeviceUnchanged, Hub, NoCommand, NoProtocolWarnings, Response, Scenario, act

from ._paths import HUB_CORE

_LAYOUT = (
    "src/dashboard_layout.py",
    "src/rest_api/dashboard_layout.py",
    "tests/e2e/fixtures/data/dashboard_layout.json",
)

#: The stored item cards after the migration: (type, id), orders 0-6.
_ITEMS = (
    ("scene", "scene_movienight01"),
    ("scene", "scene_kidslocked"),
    ("preset", "2"),
    ("system_shortcut", "builtin.mute_all_audio"),
    ("system_shortcut", "user.a1b2c3d4e5f6"),
    ("profile", "movie_night"),
    ("macro", "macro_tv_on"),
)


def _stored_items_first() -> tuple[Hub, ...]:
    return tuple(
        Hub("/api/dashboard/layout", f"data.cards[{i}]", equals={"type": t, "id": cid, "order": i})
        for i, (t, cid) in enumerate(_ITEMS)
    )


_UNTOUCHED = (NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings())

SCENARIOS = [
    Scenario(
        id="dashboard.widget_cards_dropped",
        title="A stored layout loads without its widget cards; the item cards keep their order, renumbered from 0",
        features=("F-DOM-031",),
        client_features={"api": ("F-API-025",)},
        clients=("api",),
        targets=("sim",),
        action=act("request", method="GET", path="/api/dashboard/layout"),
        expect=(
            Response(status=200, json={"success": True, "data": {"version": 1}}),
            *_stored_items_first(),
            *_UNTOUCHED,
        ),
        covers=(*HUB_CORE, *_LAYOUT),
        notes="Before UI-57 the hub served the three seeded aggregate_widget cards first (orders 0-2) and the "
        "scene card at order 3.",
    ),
    Scenario(
        id="dashboard.widget_card_refused",
        title="POST /api/dashboard/cards refuses a widget card (HTTP 400) and leaves the layout unchanged",
        kind="failure",
        features=("F-DOM-031",),
        client_features={"api": ("F-API-025",)},
        clients=("api",),
        targets=("sim",),
        action=act("request", method="POST", path="/api/dashboard/cards",
                   json={"type": "aggregate_widget", "id": "routing-dashboard"}),
        expect=(
            Response(status=400, json={"success": False}),
            *_stored_items_first(),
            *_UNTOUCHED,
        ),
        covers=(*HUB_CORE, *_LAYOUT),
        notes="Before UI-57 the hub answered 409 (the seeded card was present) or added the card (HTTP 201).",
    ),
]
