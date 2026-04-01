# retail-intelligence

API for retail using transformer

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed globally


### Installation

```bash
git clone <repo-url>
cd retail-intelligence
uv sync
uv run poe develop
```

### Environment Variables

```bash
cp .env.example .env  # edit as needed
```

## Commands

| Command | What it does |
|---|---|
| `uv run poe develop` | Install pre-commit hooks |
| `uv run poe test` | Run tests with coverage |
| `uv run poe coverage` | Show coverage report |
| `uv run poe coverage-html` | Generate HTML coverage report |
| `uv run poe lint` | Check code for lint errors |
| `uv run poe format` | Auto-format code |
| `uv run poe fix` | Auto-fix lint errors |
| `uv run poe sort` | Sort imports |
| `uv run poe type-check` | Run type checking |
| `uv run poe check` | Run all checks (lint + type-check + test) |
| `uv run poe pre-commit-check` | Run pre-commit hooks on all files |

## Dependencies

```bash
uv add <package>        # add production dependency
uv add --dev <package>  # add dev dependency
uv remove <package>     # remove a dependency
uv sync                 # sync from lockfile
```


## CI/CD

> **TODO:** GitHub Actions pipeline for automated testing, linting, and type checking on push/PR.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
