"""Drift check for the REST API contract fixtures (TST-02).

``tests/fixtures/api/*.json`` are the hub's real responses for a fixed device
state, produced by ``tools/gen_contract_fixtures.py``. Client tests (for
example ``tests/ha/``) use them in place of hand-written response shapes.
This test regenerates them in memory and fails when a response changed
without the fixtures being regenerated.
"""

import json

import pytest

from tools import gen_contract_fixtures as gen

REGEN_HINT = (
    "The hub's response for {route} no longer matches tests/fixtures/api/{name}.\n"
    "If the change is intentional, run `python tools/gen_contract_fixtures.py`, then review and "
    "commit the updated fixture, because the clients (Home Assistant component, web UI) are tested "
    "against it. If it is not intentional, you changed the API contract by accident."
)


@pytest.fixture(scope="module")
def generated():
    """Regenerate all fixtures once per module (fresh event loop)."""
    import asyncio

    return asyncio.run(gen.generate())


@pytest.mark.parametrize(("name", "route"), sorted(gen.FIXTURES.items()))
def test_fixture_matches_live_response(generated, name, route):
    path = gen.FIXTURE_DIR / name
    assert path.exists(), f"Missing fixture {path}. Run `python tools/gen_contract_fixtures.py`."
    committed = json.loads(path.read_text(encoding="utf-8"))
    assert generated[name] == committed, REGEN_HINT.format(route=route, name=name)


def test_fixture_files_are_canonical(generated):
    """Committed files are exactly what the generator writes (no hand edits)."""
    for name, payload in generated.items():
        text = (gen.FIXTURE_DIR / name).read_text(encoding="utf-8")
        assert text.replace("\r\n", "\n") == gen.render(payload), REGEN_HINT.format(route=gen.FIXTURES[name], name=name)


def test_no_orphan_fixtures():
    """Every file in tests/fixtures/api/ is produced by the generator."""
    on_disk = {p.name for p in gen.FIXTURE_DIR.glob("*.json")}
    assert on_disk == set(gen.FIXTURES), (
        f"Unexpected fixture files: {sorted(on_disk - set(gen.FIXTURES))}; "
        "add them to FIXTURES in tools/gen_contract_fixtures.py or delete them."
    )
