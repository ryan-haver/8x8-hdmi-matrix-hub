# Unfolded Circle Reference Sources

The Remote 3 integration must follow Unfolded Circle's official specification and SDK. Pinned copies of the official sources are fetched locally, not redistributed:

```bash
python tools/uc_reference.py          # clone/update to the pinned refs → reference/unfoldedcircle/ (git-ignored)
python tools/uc_reference.py --check  # report missing or drifted sources
```

Pins live in [`unfoldedcircle-references.json`](unfoldedcircle-references.json). Change a pin deliberately, in its own PR, with a note below on what changed and what the integration must adopt.

## What to consult for what

| Task | Source (under `reference/unfoldedcircle/`) |
| --- | --- |
| Integration WebSocket protocol, messages, error codes | `core-api/integration-api/` (AsyncAPI spec), `core-api/doc/integration-driver/websocket.md` |
| Writing a driver, lifecycle, standby, device states | `core-api/doc/integration-driver/write-integration-driver.md` |
| Setup flow (multi-step, credentials, errors) | `core-api/doc/integration-driver/driver-setup.md` |
| `driver.json` metadata, discovery, registration, auth token | `core-api/doc/integration-driver/{driver-advertisement,driver-registration}.md` |
| Installing the integration on the Remote itself (DI-10) | `core-api/doc/integration-driver/driver-installation.md` |
| Entity types: remote (UI pages, button mapping, simple commands), select, media player, sensor, switch, button | `core-api/doc/entities/entity_*.md` |
| Remote UI layout rules (pages, grid, icons) | `core-api/doc/remote-ui.md` |
| Python SDK API and changes | `integration-python-library/` (`ucapi/`, `CHANGELOG.md`, `examples/`) |
| Good patterns: select entities, sensors, changed-only updates, standby | `integration-denonavr/` |
| Good patterns: remote UI pages, button mapping, aarch64 build workflow | `integration-androidtv/` (`.github/workflows/`) |
| Good patterns: credential setup flow, icons | `integration-appletv/` |
| Running the real Remote core for end-to-end tests | `core-simulator/` (no licence declared; local testing only until terms are confirmed; evaluation in [`../audits/UC_CORE_SIMULATOR.md`](../audits/UC_CORE_SIMULATOR.md)) |

## Facts relied on by this project (from the pinned sources)

- **SDK:** `ucapi` 0.7.0 is current (2026-05-10). Remote entity commands are only `on`, `off`, `toggle`, `send_cmd`, `send_cmd_sequence`. Everything else is a `send_cmd` simple command.
- **Select entity:** attributes `current_option` and `options`, the latter changeable at runtime. It fits "which input is on this output".
- **Remote entity:** optional `button_mapping` and `user_interface` pages. If they're missing, the Remote attempts an automatic mapping from standard command names.
- **On-Remote custom integrations:** firmware ≥ 1.9.0; `.tar.gz` ≤ 100 MB with an aarch64 `driver` executable and the Python runtime packed in; runs in a sandbox with a dynamic user; only `$UC_CONFIG_HOME` and `$UC_DATA_HOME` persist; ≤ 100 MB of memory recommended (throttled at 250 MB, killed at 350 MB); at most 10 custom integrations sharing 1 GB; driver update in place requires firmware ≥ 2.9.3; `driver_id` ≥ 5 characters, starting with a lower-case letter.

## Pin history

| Date | Change |
| --- | --- |
| 2026-09-25 | Initial pins: core-api `84e7a5b`, ucapi `v0.7.0`, denonavr `75bd4d7`, androidtv `53955d2`, appletv `22684d8`, core-simulator `5104764`. |
