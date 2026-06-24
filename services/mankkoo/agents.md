# Mankkoo Backend — Agent Guidelines

Python/Flask backend for the Mankkoo personal finance app. Event-sourced architecture — all financial state lives in immutable events, never mutable rows.

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

## Project Structure

```
mankkoo/              # application source
  account/
    importer/         # bank CSV parsers (pl_ing, pl_mbank, pl_millenium)
    account.py        # account operations
    account_db.py     # account DB queries
    models.py         # Bank/Account/Importer enums & ABC
  controller/         # APIFlask blueprints (one per domain)
  investment/
    investment_db.py
  stream/
    stream_db.py
  util/
    data_formatter.py
  app.py              # app factory, NOTIFY listener thread
  config.py           # DevConfig / ProdConfig / TestConfig
  database.py         # schema init, append_event function, get_connection()
  event_store.py      # Stream + Event classes, CRUD helpers
  views.py            # 7 materialized views, update_views()
  data_for_test.py    # test data helpers (use in tests only)

tests/
  conftest.py         # testcontainer setup, per-test TRUNCATE, fixtures
  account/
    data/             # test CSV files for importer tests
  controller/
  event_store_test.py
  views_test.py
```

## Event Sourcing — Critical Rules

- **Never INSERT into `events` directly.** Always use `es.store([event])`, which calls the `append_event()` PostgreSQL function.
- **Never UPDATE an event.** To correct data, append a new correcting event.
- **Version must be sequential per stream.** Always read `stream.version` first, then set `event.version = stream.version + 1`.
- The `append_event` DB function handles optimistic concurrency — it will raise if the version is wrong.

```python
import mankkoo.event_store as es

stream = es.get_stream_by_id(stream_id)
event = es.Event(
    stream_type="account",
    stream_id=stream_id,
    event_type="MoneyDeposited",
    data={"amount": 100.0, "balance": 500.0, "currency": "PLN"},
    occured_at=datetime.now(timezone.utc),
    version=stream.version + 1,
)
es.store([event])
```

## Database Schema

Three tables (created by `database.py:init_db()` on startup — no migration tool):

| Table | Purpose |
|---|---|
| `streams` | Financial entities (accounts, investments, stocks, retirement) |
| `events` | Append-only event log; `UNIQUE(stream_id, version)` |
| `views` | Pre-computed JSONB blobs for fast API responses |

Key columns on `streams`: `id UUID`, `type TEXT`, `subtype TEXT`, `name TEXT`, `active BOOLEAN`, `version BIGINT`, `metadata JSONB`, `labels JSONB`.

Key columns on `events`: `id UUID`, `stream_id UUID`, `type TEXT`, `data JSONB`, `version BIGINT`, `occured_at TIMESTAMPTZ`, `added_at TIMESTAMPTZ`.

## Views System

7 views stored in the `views` table as JSONB:

- `main-indicators`
- `current-savings-distribution`
- `total-history-per-day`
- `investment-indicators`
- `investment-types-distribution`
- `investment-wallets-distribution`
- `investment-types-distribution-per-wallet`

**Views are updated asynchronously.** Flow: `INSERT event` → DB trigger fires `NOTIFY 'events_added'` → background listener thread in `app.py` calls `views.update_views()`.

In tests, poll for view readiness — do not assume they update instantly:

```python
def __wait_for_condition(condition_func, timeout=10):
    import time
    start = time.time()
    while time.time() - start < timeout:
        if condition_func():
            return
        time.sleep(0.5)
    raise TimeoutError("Condition not met")
```

### `include_in_wealth` label

Streams can be excluded from wealth-total views via `labels["include_in_wealth"]`.

**ONLY the exact lowercase string `"true"` means included.** Everything else (missing key, `"false"`, boolean `true`, `"True"`) means excluded.

```json
{ "wallet": "Personal", "include_in_wealth": "true" }   // included
{ "wallet": "Personal", "include_in_wealth": "false" }  // excluded
{ "wallet": "Personal" }                                 // included (default, backward-compat)
```

Affected (wealth) views: `main-indicators`, `current-savings-distribution`, `total-history-per-day`, `investment-indicators`, `investment-types-distribution`.

Composition views (always include all): `investment-wallets-distribution`, `investment-types-distribution-per-wallet`.

SQL filter used in wealth views:
```sql
WHERE (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
```

## Environment & Config

`config.py` defines three configs selected via `FLASK_ENV`:

| `FLASK_ENV` | Config | DB | Port |
|---|---|---|---|
| `"prod"` (default) | `ProdConfig` | `mankkoo` | 8080 |
| anything else | `DevConfig` | `dev` | 5000 |
| set by test fixtures | `TestConfig` | `test` | 5555 |

`TestConfig` is passed directly in tests — `FLASK_ENV` is set to `"test"` by `conftest.py`, not auto-detected.

DB connection env vars (all default to `postgres`/`localhost`/`5432`): `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`.

## Testing Conventions

- **Test file suffix: `_test.py`** (not `test_*.py`). Wrong prefix breaks discovery.
- Tests use a real PostgreSQL testcontainer (`postgres:16-alpine`) started once per session.
- Every test function gets a fresh DB — `conftest.py` truncates `events, streams, views` before each test.
- Deadlock on truncate is retried automatically (3 attempts, 5s delay).

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

## Bank Import System

**Location**: `mankkoo/account/importer/`

Each bank parser inherits `models.Importer` (ABC) and implements:
- `load_file_by_filename(file_name)` — load from path
- `load_file_by_contents(contents: bytes)` — load from base64 bytes (from UI)
- `format_file(df, account_id)` — transform to standard columns

Supported banks (`models.Bank` enum): `PL_ING`, `PL_MBANK`, `PL_MILLENIUM`, `MANKKOO`.

Standard output columns (in order): `Account`, `Date`, `Title`, `Details`, `Category`, `Comment`, `Operation`, `Currency`, `Balance`.

Parsers use pandas `.pipe()` chains. End with `.pipe(order_columns, db.account_columns)` to guarantee column order.

### Adding a New Bank

1. `mankkoo/account/importer/pl_newbank.py` — implement `Importer`
2. Add to `models.Bank` enum
3. Add case in `importer.py:load_bank_data()`
4. Add test CSV in `tests/account/data/test_pl_newbank.csv`
5. Add test in `tests/account/importer_test.py`

## API (Controllers)

Blueprints registered in `app.py`:

| Prefix | Blueprint file |
|---|---|
| `/api/admin` | `admin_controller.py` |
| `/api/main` | `main_controller.py` |
| `/api/accounts` | `account_controller.py` |
| `/api/investments` | `investment_controller.py` |
| `/api/streams` | `stream_controller.py` |

Use `APIBlueprint` + `@blueprint.input` / `@blueprint.output` / `@blueprint.doc` decorators. Schema classes inherit from `apiflask.Schema` with `apiflask.fields` types.

Swagger UI: `http://localhost:5000/docs` | OpenAPI YAML: `http://localhost:5000/openapi.yaml`

## Coding Conventions

- Max line length: **160** characters (configured in `pyproject.toml`).
- Private module-level functions: double underscore prefix (`__load_current_total_savings()`).
- Logging: `from mankkoo.base_logger import log` → `log.info()`, `log.debug()`, `log.error(..., exc_info=True)`.
- DB queries: always use `with db.get_connection() as conn:` + `with conn.cursor() as cur:`. Parameterize user input with `%s` tuples. f-strings are acceptable only for table/column names.

## Stream Types & Subtypes

| Type | Subtypes | Key Events |
|---|---|---|
| `account` | `checking`, `savings`, `cash` | `AccountOpened`, `MoneyDeposited`, `MoneyWithdrawn` |
| `investment` | `treasury_bonds`, `corporate_bonds`, `real_estate` | `TreasuryBondsBought`, `TreasuryBondsMatured` |
| `stocks` | `ETF`, `stock` | `ETFBought`, `ETFSold`, `StockBought`, `StockSold` |
| `retirement` | same as account | same as account |
