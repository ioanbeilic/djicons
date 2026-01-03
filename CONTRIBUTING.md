# Contributing to djicons

Thank you for your interest in contributing to djicons!

## Branch Strategy

- **`main`** - Production-ready code. Protected branch.
- **`develop`** - Development branch. Protected branch.
- **Feature branches** - Create from `develop`, merge via PR.

## Workflow for Contributors

1. **Fork** the repository
2. **Create a branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit
4. **Push** to your fork
5. **Create a Pull Request** to `develop`

## For Maintainers Only

Direct pushes to `main` and `develop` are restricted to maintainers.

## Code Style

- Use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Run before committing:
  ```bash
  ruff check .
  ruff format .
  ```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src/djicons
```

## Adding New Icon Packs

1. Create pack directory: `src/djicons/packs/{packname}/`
2. Add `__init__.py` with `register()` function
3. Update `scripts/download_icons.py`
4. Update `src/djicons/apps.py`
5. Update `src/djicons/conf.py`
6. Update `README.md`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
