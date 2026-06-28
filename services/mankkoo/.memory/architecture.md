# Backend — Architecture

## Project Structure

```
services/mankkoo/
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

## Database Schema

Three tables created by `database.py:init_db()` on startup (no migration tool):

| Table | Key Columns |
|---|---|
| `streams` | `id UUID`, `type TEXT`, `subtype TEXT`, `name TEXT`, `active BOOLEAN`, `version BIGINT`, `metadata JSONB`, `labels JSONB` |
| `events` | `id UUID`, `stream_id UUID`, `type TEXT`, `data JSONB`, `version BIGINT`, `occured_at TIMESTAMPTZ`, `added_at TIMESTAMPTZ`; `UNIQUE(stream_id, version)` |
| `views` | `name TEXT`, `payload JSONB` |

## Event Sourcing Pattern

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

## Views System

7 views in the `views` table as JSONB blobs:

- `main-indicators`
- `current-savings-distribution`
- `total-history-per-day`
- `investment-indicators`
- `investment-types-distribution`
- `investment-wallets-distribution`
- `investment-types-distribution-per-wallet`

Update flow: `INSERT event` → DB trigger → `NOTIFY 'events_added'` → background thread → `views.update_views()`

**Views update asynchronously.** In tests, poll with a timeout — do not assume instant updates:

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

### `include_in_wealth` Label

```json
{ "wallet": "Personal", "include_in_wealth": "true" }   // included
{ "wallet": "Personal", "include_in_wealth": "false" }  // excluded
{ "wallet": "Personal" }                                 // included (default, backward-compat)
```

**Only the exact lowercase string `"true"` means included.** Boolean `true`, `"True"`, missing key → excluded (except missing key = included for backward compat).

SQL filter in wealth views:
```sql
WHERE (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
```

Wealth views: `main-indicators`, `current-savings-distribution`, `total-history-per-day`, `investment-indicators`, `investment-types-distribution`.
Composition views (always all): `investment-wallets-distribution`, `investment-types-distribution-per-wallet`.

## API (Controllers)

| Prefix | Blueprint file |
|---|---|
| `/api/admin` | `admin_controller.py` |
| `/api/main` | `main_controller.py` |
| `/api/accounts` | `account_controller.py` |
| `/api/investments` | `investment_controller.py` |
| `/api/streams` | `stream_controller.py` |

Use `APIBlueprint` + `@blueprint.input` / `@blueprint.output` / `@blueprint.doc`. Schema classes inherit from `apiflask.Schema` with `apiflask.fields` types.

Swagger UI: `http://localhost:5000/docs` | OpenAPI YAML: `http://localhost:5000/openapi.yaml`

## Bank Import System

Each bank parser is in `mankkoo/account/importer/` and inherits `models.Importer` (ABC):

- `load_file_by_filename(file_name)` — load from path
- `load_file_by_contents(contents: bytes)` — load from base64 bytes (from UI upload)
- `format_file(df, account_id)` — transform to standard columns

Supported banks (`models.Bank` enum): `PL_ING`, `PL_MBANK`, `PL_MILLENIUM`, `MANKKOO`.

Standard output columns (in order): `Account`, `Date`, `Title`, `Details`, `Category`, `Comment`, `Operation`, `Currency`, `Balance`.

Parsers use pandas `.pipe()` chains. End with `.pipe(order_columns, db.account_columns)`.

### Adding a New Bank

1. `mankkoo/account/importer/pl_newbank.py` — implement `Importer`
2. Add to `models.Bank` enum
3. Add case in `importer.py:load_bank_data()`
4. Add test CSV in `tests/account/data/test_pl_newbank.csv`
5. Add test in `tests/account/importer_test.py`
