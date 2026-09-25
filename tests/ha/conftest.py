"""pytest configuration for the Home Assistant component tests.

These tests need ``homeassistant`` and ``pytest-homeassistant-custom-component``
(``pip install -r requirements-test-ha.txt``, Python 3.13). Without them,
nothing here is collected: ``tests/conftest.py`` leaves the directory out of
the normal suite, and an explicit ``pytest tests/ha`` reports "no tests ran"
instead of an import error.
"""

import importlib.util

if importlib.util.find_spec("homeassistant") is None:
    collect_ignore_glob = ["test_*.py"]
else:
    from .helpers import (  # noqa: F401  (fixtures registered by import)
        auto_enable_custom_integrations,
        config_entry,
        hub,
        setup_integration,
    )
