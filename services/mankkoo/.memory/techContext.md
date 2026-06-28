# Backend — Technical Context

## Tech Stack

- **Language**: Python 3.10+
- **Framework**: Flask + APIFlask (OpenAPI/Swagger auto-generation)
- **Database driver**: psycopg2
- **CSV parsing**: pandas
- **Package manager**: uv (replaces pip/poetry)
- **Testing**: pytest + testcontainers (real PostgreSQL)
- **Linting**: autoflake, isort, autopep8, black, flake8, mypy
- **Type checking**: mypy

## Commands

```bash
# Install deps
uv sync                                       # local dev (updates allowed)
uv sync --frozen                              # CI / reproducible (use this in scripts)

# Run
uv run flask run --reload                     # dev server on port 5000

# Test
uv run pytest -s -vv --cov=./mankkoo          # all tests
uv run pytest -s -vv tests/account/account_test.py                          # single file
uv run pytest -s -vv tests/account/account_test.py::test_name               # single test

# Lint (order matters — run in this sequence)
uv run autoflake --in-place --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports -r .
uv run isort .
uv run autopep8 --in-place --aggressive --recursive .
uv run black .

# Type check / lint
uv run mypy mankkoo/
uv run flake8 mankkoo/

# Dependency management
uv lock --upgrade                             # upgrade all deps, regenerate uv.lock
uv export --no-hashes --no-dev -o requirements.txt   # for Docker reference
```

**Always run `uv lock` after editing `pyproject.toml`.**

## Environment & Config

`config.py` defines three configs selected via `FLASK_ENV`:

| `FLASK_ENV` | Config | DB | Port |
|---|---|---|---|
| `"prod"` (default) | `ProdConfig` | `mankkoo` | 8080 |
| anything else | `DevConfig` | `dev` | 5000 |
| set by test fixtures | `TestConfig` | `test` | 5555 |

`TestConfig` is passed directly in tests — `FLASK_ENV` is set to `"test"` by `conftest.py`.

DB connection env vars (default to `postgres`/`localhost`/`5432`): `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`.

## Testing Conventions

- **Test file suffix: `_test.py`** (not `test_*.py`) — wrong prefix breaks pytest discovery
- Tests use a real PostgreSQL testcontainer (`postgres:16-alpine`) started once per session
- Every test gets a fresh DB — `conftest.py` truncates `events, streams, views` before each test
- Deadlock on truncate is retried automatically (3 attempts, 5s delay)
- Views update asynchronously — poll with timeout, never assert immediate consistency

### Test Data Helpers (`mankkoo/data_for_test.py`)

```python
import mankkoo.data_for_test as td

stream = td.any_account_stream(account_type='checking', active=True, wallet='Personal')
stream = td.any_account_stream(include_in_wealth=False)   # sets label to string "false"
stream = td.any_stream(stream_type='investment', stream_subtype='treasury_bonds')

data = td.an_account_with_operations(
    operations=[{"operation": 1000.0, "date": "01-01-2021"}]
)
# Returns {"stream": Stream, "events": [Event, ...]}

td.stock_events(operations=[...], type='ETF', wallet='IKE')
td.investment_events(operations=[...], category='treasury_bonds')
```

## Coding Conventions

- Max line length: **160** characters (configured in `pyproject.toml`)
- Private module-level functions: double underscore prefix (`__load_current_total_savings()`)
- Logging: `from mankkoo.base_logger import log` → `log.info()`, `log.debug()`, `log.error(..., exc_info=True)`
- DB queries: always use `with db.get_connection() as conn:` + `with conn.cursor() as cur:`
- Parameterize user input with `%s` tuples; f-strings only for table/column names
