# Contributing Guide

Thank you for your interest in contributing to the OREI HDMI Matrix Integration!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd unfoldedcircle-orei-hdmi-matrix-integration
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/macOS
   ```

3. **Install dependencies with dev tools**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

## Project Structure

```
src/                # Source code - main application logic
tests/              # Test files
docs/               # Documentation
scripts/            # Utility scripts (shell scripts, helpers)
data/               # Runtime data (gitignored)
```

### Key Files

| File | Purpose |
|------|---------|
| `src/driver.py` | Main UC integration driver |
| `src/orei_matrix.py` | OREI matrix control library |
| `src/config.py` | Configuration utilities |
| `driver.json` | UC driver metadata |

## Code Style

This project uses:
- **Black** for code formatting
- **Ruff** for linting
- **Type hints** for all functions

### Format your code
```bash
black src/ tests/
ruff check src/ tests/ --fix
```

### Run tests
```bash
pytest tests/
```

## Making Changes

1. **Create a branch** for your feature/fix
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** in the `src/` directory

3. **Add tests** if applicable in `tests/`

4. **Update documentation** in `docs/` if needed

5. **Format and lint**
   ```bash
   black src/ tests/
   ruff check src/ tests/
   ```

6. **Test locally**
   ```bash
   python src/driver.py
   ```

7. **Submit a pull request**

## Testing with Docker

```bash
# Build and run
docker-compose up --build

# View logs
docker logs -f uc-orei-hdmi-matrix

# Stop
docker-compose down
```

## Documentation

- Keep `README.md` up to date with user-facing changes
- Update `docs/PROJECT_ROADMAP.md` for feature progress
- Add API documentation to `docs/API_REFERENCE.md`

## Commit Messages

Use clear, descriptive commit messages:
- `feat: Add CEC volume control`
- `fix: Handle connection timeout`
- `docs: Update installation guide`
- `refactor: Move config to separate module`

## Questions?

Open an issue on GitHub for questions or feature requests.
