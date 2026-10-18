# Contributing Guide

Thank you for your interest in contributing to the **8x8 HDMI Matrix Hub** —
the OREI BK-808 (and other HDCVT HDP-MXC88A-based) matrix integration that
exposes a REST API, a web UI, a kiosk and the Unfolded Circle Remote 3
integration on a single image.

This guide covers the everyday workflow: development setup, the project
layout, the tools (Ruff, Mypy, pytest, Docker), the test markers and the
release gates. Architecture and validation lives in `docs/ARCHITECTURE.md`
and `docs/validation/README.md`; client-facing guides in `docs/DOCKER.md`,
`docs/HOME_ASSISTANT.md`, `docs/FLIC_SETUP.md` and `docs/UNFOLDED_CIRCLE.md`.

## Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/ryan-haver/8x8-hdmi-matrix-hub.git
cd 8x8-hdmi-matrix-hub
```

### 2. Create a virtual environment (Python 3.12 for the checked-in locks)

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Linux / macOS
```

The repo pins a single `__version__` (`src/hub/__init__.py`) that feeds
`driver.json`, the HA `manifest.json`, `/api/info` and the Docker image
labels (DEP-06). The runtime entry point is **`run.py`** — `python run.py`
boots the core (REST API, web UI at `/ui`, kiosk at `/kiosk`); setting
`UC_ENABLED=true` also starts the Remote 3 integration on WebSocket
port `9095` (`docs/DOCKER.md`, `run.py:9-12`). Tests target Python 3.12
(the metadata supports Python 3.11 and Python 3.12; HA tests need 3.13+).

### 3. Install dependencies (hashed, locked)

`requirements.txt` locks the runtime and integration dependencies, including
Unfolded Circle's `ucapi`. `requirements-uc.txt` is a compatibility include.
`requirements-dev.txt` adds the development and build tools with hashes.
It includes pytest, pytest-asyncio, Ruff, Mypy, and the packaging tools.

```bash
python -m pip install --require-hashes -r requirements-dev.txt
python -m pip install --no-deps -e .
python -m pip check
```

### 4. (Optional) Install git hooks

```bash
git config core.hooksPath .githooks
```

The pre-commit hook runs Ruff over the source and test trees, followed by
pytest excluding the separate Home Assistant and scripted-Remote suites.
Mypy runs separately in CI; run it locally before a Python change.

## Project Structure

```
8x8-hdmi-matrix-hub/
├── run.py                  # ONE entry point: core + opt-in integrations
├── run_server.py           # thin wrapper kept for backwards compatibility
├── driver.json             # UC Remote 3 driver metadata (port 9095)
├── requirements.txt        # core runtime deps (hashed)
├── requirements-uc.txt     # compatibility include of the runtime lock
├── pyproject.toml          # packaging, ruff, mypy, pytest config (DEP-04)
├── Dockerfile              # one image; UC off unless UC_ENABLED=true
├── docker-compose.yml      # core service (REST API + web UI + kiosk)
├── docker-compose.uc-host.yml    # UC override — host networking, mDNS on
├── docker-compose.uc-bridge.yml  # UC override — bridge networking, no mDNS
├── src/
│   ├── hub/                # canonical env vars, OpenAPI, persistence
│   │   ├── env.py          # framework environment metadata
│   │   ├── openapi.py
│   │   ├── core/           # MatrixService framework; runtime wiring pending
│   │   ├── domain/         # ActionRunner, VisibilityStore, profiles
│   │   ├── persistence/
│   │   └── integrations/   # modular integrations framework
│   │       ├── unfolded_circle/  # UC_ENABLED / UC_PORT / UC_DISABLE_MDNS
│   │       ├── flic/            # FLIC_ENABLED (defaults true)
│   │       └── homeassistant/   # HA_DISCOVERY_ENABLED
│   ├── integrations/       # legacy module imports
│   ├── rest_api/           # aiohttp REST API: app.py routes, security.py
│   ├── driver.py           # UC Remote 3 driver (run.py delegates here)
│   ├── orei_matrix.py      # matrix transport (HTTPS + Telnet)
│   ├── cec_commands.py / cec_macros.py / cec_resolver.py
│   ├── config.py / persistence.py / password.py
│   └── …
├── custom_components/
│   └── hdmi_matrix/        # Home Assistant HACS integration
├── web/                    # web UI, kiosk, PWA assets
├── tests/                  # pytest suite (TST-05: mock by default)
│   ├── tests/conftest.py    # global state isolation (TST-06), the shared fixtures
│   ├── test_*.py           # core REST, security, persistence, profiles, …
│   ├── tests/uc/           # UC driver + Remote simulator
│   ├── tests/sim/          # simulator-backed REST contract
│   ├── tests/ha/           # HA integration (Python 3.13+; auto-skipped)
│   ├── tests/deploy/       # Docker image (gated by `pytest -m docker`)
│   ├── tests/validation/   # feature registry, evidence, ledger
│   ├── tests/hil_tools/    # interactive hardware scripts (not collected)
│   └── tests/test_client_guides_docs.py # owned by wp-g2-client-guides-doc-archive
├── docs/                   # all documentation
│   ├── API_REFERENCE.md / api/WEBSOCKET.md / api/websocket.schema.json
│   ├── ARCHITECTURE.md / CONFIGURATION.md (planned)
│   ├── DOCKER.md / HOME_ASSISTANT.md / FLIC_SETUP.md / UNFOLDED_CIRCLE.md
│   ├── CEC_CONTROL_ARCHITECTURE.md / PHASE_8_SPEC.md / IR_CONTROL_ROADMAP.md / WEB_UI_IMPLEMENTATION_PLAN.md
│   │   # Legacy design plans — slated for `docs/archive/design/` once DOC-06…09 are resolved
│   ├── INTEGRATION_TEMPLATE.md
│   ├── REMEDIATION_PLAN.md / PROJECT_ROADMAP.md / MASTER_INDEX.md
│   ├── validation/         # LEDGER.md, VALIDATION_PLAN.md, evidence/
│   ├── audits/             # UC_INTEGRATION_AUDIT.md, UC_CORE_SIMULATOR.md
│   └── vendor/             # UC pinned references
├── scripts/                # utility scripts (validate, uc_reference.py)
├── tools/                  # test harnesses, simulators, evidence
├── data/                   # runtime data (gitignored; mounted to /data)
└── build/                  # CI build output
```

### Key Files

| File | Purpose |
|------|---------|
| `run.py` | The single runtime entry point (core + opt-in integrations) |
| `src/hub/__init__.py` | `__version__`, the single source of versions (DEP-06) |
| `src/hub/env.py` | Canonical env-var table (every variable the hub reads) |
| `src/hub/openapi.py` | OpenAPI spec served at `/api/docs` (DOC-03) |
| `src/hub/integrations/` | Modular integration framework |
| `src/rest_api/app.py` | REST routes (every `app.router.add_*` lives here) |
| `src/rest_api/security.py` | `CONTROL_PIN`/`ADMIN_PIN` gates, API keys, sessions |
| `src/driver.py` | UC Remote 3 driver (delegated to by `run.py`) |
| `src/orei_matrix.py` | Matrix HTTPS + Telnet transport |
| `driver.json` | UC Remote 3 driver metadata |
| `custom_components/hdmi_matrix/` | Home Assistant HACS integration |

## Code Style

The project uses:

- **[Ruff](https://docs.astral.sh/ruff/)** for linting (config: `pyproject.toml [tool.ruff]`, line length 120, rules `E F W I N UP`, ignoring `E501`, `E402`, `N806`)
- **[Mypy](https://mypy-lang.org/)** for type checking (config: `pyproject.toml [tool.mypy]`, `mypy_path = "src"`)
- **Type hints** on every public function (the suite enforces this through Mypy on CI)

### Lint and type-check

```bash
# Lint
python -m ruff check src tests
python -m ruff format --check src tests

# Type-check (CI runs this and fails on any new error)
python -m mypy src
```

### Run tests

```bash
# Default: offline, mock matrix (TST-05)
python -m pytest

# Only the suite owned by this track
python -m pytest tests/test_client_guides_docs.py

# Targeted suite
python -m pytest tests/uc -k "setup or handshake"

# Hardware (requires MATRIX_HOST; you must run the matrix through `tools/hil/`)
MATRIX_HOST=192.168.1.50 python -m pytest -m hardware

# Docker image (the `deploy` suite; CI runs this in `docker-build`)
python -m pytest -m docker tests/deploy
```

Markers are declared in `pyproject.toml [tool.pytest.ini_options]`:

| Marker | When it runs |
|--------|--------------|
| `hardware` | `pytest -m hardware` (real matrix at `$MATRIX_HOST`) |
| `docker` | `pytest -m docker tests/deploy` (real image) |
| `mock` | default — uses the mock matrix (RFC 5737 TEST-NET-1) |

## Making Changes

### 1. Branch off the integration branch

```bash
git fetch origin
git checkout -b ryan-haver/<your-track-name> origin/wp-g1-g2-release-and-docs
```

### 2. Make your changes

| Area | Where it lives |
|------|----------------|
| Matrix control, REST routes | `src/rest_api/*.py`, `src/orei_matrix.py` |
| Hub state, actions, profiles | `src/hub/core/`, `src/hub/domain/` |
| Persistence / migrations | `src/hub/persistence/` |
| Integrations (UC / Flic / HA) | `src/hub/integrations/<name>/` |
| Web UI / kiosk | `web/js/`, `web/css/`, `web/index.html`, `web/kiosk.html` |
| Home Assistant integration | `custom_components/hdmi_matrix/` |
| Driver metadata, versions | `driver.json`, `src/hub/__init__.py`, `custom_components/hdmi_matrix/manifest.json` |
| Client docs (this track) | `docs/HOME_ASSISTANT.md`, `docs/DOCKER.md`, `docs/FLIC_SETUP.md`, `docs/UNFOLDED_CIRCLE.md`, `CONTRIBUTING.md` |

### 3. Add tests

Every change to a route, integration, or persistence path needs a test
under `tests/`. Follow the existing patterns:

- REST routes → `tests/test_rest_api.py` (or a topic-specific module like
  `test_profiles_scenes_pins.py`, `test_dashboard_layout.py`).
- Integrations → `tests/test_hub_<name>_integration.py` (mock the framework).
- Driver / UC → `tests/uc/test_<topic>.py` (with `UcRemoteSim`).
- Pure helpers / env / openapi → `tests/test_hub_<topic>.py`.
- Docs → `tests/test_<doc>_docs.py` (read the file, assert required
  sections and references — `test_security_docs.py` is the template).

### 4. Update documentation

- `README.md` and the docs under `docs/` reflect user-facing changes
  (start with `docs/HOME_ASSISTANT.md`, `docs/DOCKER.md`, `docs/FLIC_SETUP.md`,
  `docs/UNFOLDED_CIRCLE.md`).
- `docs/CHANGELOG.md` and `docs/PROJECT_ROADMAP.md` for milestone work.
- `docs/validation/LEDGER.md` and `docs/validation/features.yaml` for
  per-feature status (the `python -m tools.validate` tool reads them).
- `docs/REMEDIATION_PLAN.md` for register IDs (`DOC-*` such as DOC-04,
  DOC-05 and DOC-13, `UC-*` such as UC-20, `BE-*`, …).

### 5. Lint, type-check, and run the targeted tests

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
python -m pytest tests/<your-suite>
```

### 6. Commit

Use clear, descriptive commit messages — the project follows
[Conventional Commits](https://www.conventionalcommits.org/):

```text
feat(rest): add /api/profile/{id}/execution-log route
fix(driver): never send the configured login to a new matrix address
docs(home-assistant): update HACS config flow for the control PIN
refactor(hub): move env parsing to a single table in src/hub/env.py
test(rest): cover the new control-lock return code on POST /api/preset/2
```

### 7. Open a pull request

Push the branch and open a PR against `wp-g1-g2-release-and-docs`
(or the integration branch your track fans out from). CI runs 13 gates
(see `docs/PROJECT_ROADMAP.md`); all green is required before merge.

## Testing with Docker

The fastest path to a running hub is Docker Compose (see `docs/DOCKER.md`).
The container user is UID/GID 1000 by default — `mkdir -p data && sudo
chown 1000:1000 data` once on the host.

```bash
# Core only (REST API + web UI at /ui + kiosk at /kiosk)
MATRIX_HOST=192.168.1.50 docker compose up -d

# Core + Unfolded Circle Remote 3 integration (host networking, mDNS)
HUB_HOST_IP=192.168.1.20 docker compose \
  -f docker-compose.yml -f docker-compose.uc-host.yml up -d

# Follow logs
docker compose logs -f

# Stop
docker compose down
```

The image carries a `HEALTHCHECK` (`python run.py healthcheck`, which
calls `/api/health` on `API_PORT`), so `docker ps` shows `healthy` once
the hub answers.

## Documentation

- `README.md` — entry point, quick start, badges
- `docs/ARCHITECTURE.md` — runtime structure, ownership, data flow
- `docs/API_REFERENCE.md` — REST API surface (generated; `docs/api/WEBSOCKET.md` for WebSocket)
- `docs/CONFIGURATION.md` — every environment variable and compose-level variable (DOC-12)
- `docs/DOCKER.md` — Docker, compose files, networking, persistence, troubleshooting
- `docs/HOME_ASSISTANT.md` — REST commands **and** the HACS custom component (DOC-04)
- `docs/FLIC_SETUP.md` — Flic button + Flic Hub SDK + profiles + CEC macros
- `docs/UNFOLDED_CIRCLE.md` — Remote 3 integration, `UC_ENABLED`/`UC_PORT`/`UC_DISABLE_MDNS` (UC-20)
- `docs/INTEGRATION_TEMPLATE.md` — building a new modular integration (template + register contract)
- `docs/SECURITY.md` — threat model, two-level access, disclosure
- `docs/REMEDIATION_PLAN.md` — the register of findings (`DOC-*`, `UC-*`, `BE-*`, …)
- `docs/validation/LEDGER.md` — feature × client × evidence matrix (VALIDATION_PLAN §4)
- `docs/vendor/UNFOLDED_CIRCLE.md` — pinned UC reference sources

## Commit Messages

Use clear, descriptive commit messages following Conventional Commits:

- `feat: Add CEC volume control`
- `fix: Handle connection timeout`
- `docs: Update installation guide`
- `refactor: Move config to separate module`
- `test: Cover control PIN on preset routes`

Release integration branches use merge commits so the validated track history
remains available to reviewers and `git blame`.

## Questions?

Open an issue on GitHub for questions or feature requests, or use the
project's discussion board. Security issues follow
`SECURITY.md` — disclose through GitHub Security Advisories, never a
public issue.
