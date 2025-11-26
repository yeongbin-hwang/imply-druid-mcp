# Contributing to imply-druid-mcp

Thank you for your interest in contributing!

## How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Provide detailed reproduction steps
- Include Python version and environment details

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run linting (`ruff check src/`)
6. Commit with clear messages
7. Push and open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/yeongbin-hwang/imply-druid-mcp.git
cd imply-druid-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/

# Run type checking
mypy src/

# Format code
black src/
```

### Code Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Add type hints where possible
- Write docstrings for public functions

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## Security

For security vulnerabilities, please create a private security advisory on GitHub instead of a public issue.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Publishing (Maintainers Only)

### Release New Version

1. Update version in `pyproject.toml` and `src/imply_druid_mcp/__init__.py`
2. Update `CHANGELOG.md`
3. Build and upload to PyPI:
   ```bash
   rm -rf dist/
   python -m build
   python -m twine upload dist/*
   ```
4. Create git tag and push:
   ```bash
   git tag -a v0.x.x -m "Release v0.x.x"
   git push origin v0.x.x
   ```
