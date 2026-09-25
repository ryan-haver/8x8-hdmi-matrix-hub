"""PER-02: the Flic button registry is persisted with the atomic JSON helper."""

import json

from rest_api import integrations


def test_save_round_trips_through_load():
    integrations._registered_buttons = {"aa:bb": {"bdaddr": "aa:bb", "name": "Den", "serial": "S1"}}
    integrations._save_buttons()

    path = integrations._get_flic_file_path()
    assert json.loads(path.read_text(encoding="utf-8")) == integrations._registered_buttons
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []

    integrations._registered_buttons = {}
    integrations._loaded = False
    integrations._load_buttons_if_needed()
    assert integrations._registered_buttons == {"aa:bb": {"bdaddr": "aa:bb", "name": "Den", "serial": "S1"}}


def test_failed_save_leaves_previous_registry_intact():
    """A write that fails mid-serialization must not truncate the existing file."""
    integrations._registered_buttons = {"aa:bb": {"bdaddr": "aa:bb", "name": "Den"}}
    integrations._save_buttons()
    path = integrations._get_flic_file_path()
    before = path.read_text(encoding="utf-8")

    # json.dump streams output, so an unserializable value fails part-way through.
    integrations._registered_buttons = {"aa:bb": {"bdaddr": "aa:bb", "name": "Den"}, "zz": object()}
    integrations._save_buttons()  # logs a warning, does not raise

    assert path.read_text(encoding="utf-8") == before
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []
