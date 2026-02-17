# Agents.md - Mankkoo Backend Service

This document provides comprehensive guidance for AI coding agents working on the **mankkoo** personal finance backend service.

## Project Overview

**Mankkoo** is a personal finance application backend service built with Python. It manages financial data including bank accounts, investments, stocks, and retirement accounts using an event-sourced architecture.

### Key Technologies
- **Language**: Python 3.10+
- **Web Framework**: Flask (APIFlask for OpenAPI/Swagger)
- **Database**: PostgreSQL with event sourcing
- **Package Manager**: 
  - **Development**: Poetry (pyproject.toml)
  - **Production/Docker**: pip (requirements.txt)
- **Testing**: pytest with testcontainers (PostgreSQL)
- **Data Processing**: pandas, numpy
- **API Documentation**: OpenAPI 3.0 (auto-generated via APIFlask)

---

## Core Architecture Principles

### 1. Event Sourcing Architecture

**Critical Concept**: This is the foundation of the entire application.

- **Immutable Events**: Every operation (transaction, investment purchase, etc.) is stored as an immutable event
- **Streams**: Each financial entity (account, investment, stock portfolio) is a "stream"
- **Events Can't Be Updated**: Events are append-only. To correct data, add a new correcting event
- **Version Control**: Each event has a version number that increments sequentially per stream

#### Stream Structure
```python
# Location: mankkoo/event_store.py
class Stream:
    id: UUID              # Unique stream identifier
    type: str             # 'account', 'investment', 'stocks', 'retirement'
    subtype: str          # e.g., 'checking', 'savings', 'ETF', 'treasury_bonds'
    name: str             # Human-readable name
    bank: str             # Bank/institution name
    active: bool          # Whether stream is currently active
    version: int          # Current version (= number of events)
    metadata: dict        # Flexible metadata (account numbers, URLs, etc.)
    labels: dict          # Labels for categorization (e.g., 'wallet': 'Personal')
```

#### Event Structure
```python
# Location: mankkoo/event_store.py
class Event:
    id: UUID              # Unique event identifier
    stream_type: str      # Type of stream this belongs to
    stream_id: UUID       # Which stream this event belongs to
    event_type: str       # e.g., 'MoneyDeposited', 'MoneyWithdrawn', 'ETFBought'
    data: dict            # Event payload (amount, balance, currency, etc.)
    occured_at: datetime  # When the real-world event occurred
    version: int          # Sequential version number for this stream
```

### 2. Database Schema

**Location**: `mankkoo/database.py`

#### Three Main Tables:

1. **`streams`** - Stores stream metadata
   ```sql
   id              UUID PRIMARY KEY
   type            TEXT NOT NULL          -- 'account', 'investment', 'stocks', 'retirement'
   subtype         TEXT NOT NULL          -- specific type categorization
   bank            TEXT
   name            TEXT NOT NULL
   active          BOOLEAN NOT NULL
   version         BIGINT NOT NULL        -- increments with each event
   metadata        JSONB                  -- flexible storage
   labels          JSONB                  -- categorization labels
   ```

2. **`events`** - Stores all events (append-only)
   ```sql
   id              UUID PRIMARY KEY
   stream_id       UUID NOT NULL (FK -> streams.id)
   type            TEXT NOT NULL          -- event type name
   data            JSONB NOT NULL         -- event payload
   version         BIGINT NOT NULL        -- must be sequential per stream
   occured_at      TIMESTAMP WITH TIME ZONE NOT NULL
   added_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
   
   UNIQUE CONSTRAINT: (stream_id, version)  -- ensures version uniqueness
   ```

3. **`views`** - Stores materialized views (denormalized data)
   ```sql
   name            TEXT PRIMARY KEY
   content         JSONB
   updated_at      TIMESTAMP WITH TIME ZONE
   ```

#### Database Function: `append_event`

**Location**: `mankkoo/database.py:87-144`

This PostgreSQL function handles event insertion with optimistic concurrency control:
- Locks the stream for update
- Creates stream if it doesn't exist (version 0)
- Validates expected version (if provided)
- Inserts event with incremented version
- Updates stream version

**Never call INSERT on events directly** - always use `append_event()` via `event_store.store()`

### 3. Database Triggers & View Updates

**Critical**: When events are inserted, a PostgreSQL trigger fires:

1. **Trigger**: `capture_event_added_trigger` (location: `mankkoo/database.py:161-162`)
2. **Function**: `notification_trigger()` (location: `mankkoo/database.py:146-159`)
3. **Action**: Sends PostgreSQL `NOTIFY` on channel `events_added`
4. **Listener**: Background thread in `mankkoo/app.py:74-96` listens for notifications
5. **Updates Views**: Calls `views.update_views()` to rebuild materialized views

#### View System

**Location**: `mankkoo/views.py`

Views are denormalized, pre-computed data structures stored as JSONB for fast API responses:

- `main-indicators` - Current savings, net worth, income/spending
- `current-savings-distribution` - Breakdown by account type
- `total-history-per-day` - Historical balance over time
- `investment-indicators` - Investment totals and performance
- `investment-types-distribution` - Investment breakdown by type
- `investment-wallets-distribution` - Distribution across wallets
- `investment-types-distribution-per-wallet` - Detailed per-wallet breakdown

**Important**: Views are updated asynchronously after events are inserted. Tests may need to wait for view updates using polling patterns (see `tests/account/account_test.py:158-164`).

#### Stream Exclusion from Wealth Calculations (`include_in_wealth` flag)

Streams can be excluded from wealth calculation views while still appearing in composition views (wallets/types distributions). This is useful for tracking wallets that should not be counted toward total net worth.

**Storage**: The exclusion flag is stored in `streams.labels` JSONB as:
```json
{
  "wallet": "Personal",
  "include_in_wealth": "true"  // or "false" (both are STRINGS in JSONB)
}
```

**CRITICAL - String Value Requirement**: 
⚠️ **ONLY the exact lowercase string `'true'` includes a stream in wealth calculations.** Any other value (including `'false'`, `'True'`, boolean `true`, `null`, missing key, etc.) will **EXCLUDE** the stream. This is essential for backward compatibility—streams without the label default to included.

- `"include_in_wealth": "true"` → **INCLUDED** in wealth calculations ✓
- `"include_in_wealth": "false"` → **EXCLUDED** from wealth calculations ✗
- `"include_in_wealth": "True"` (capital T) → **EXCLUDED** from wealth calculations ✗
- `"include_in_wealth": true` (boolean) → **EXCLUDED** from wealth calculations ✗
- Missing `include_in_wealth` key → **INCLUDED** (defaults to included for backward compatibility) ✓

**Warning**: Incorrectly excluding important wallets will cause them to disappear from your total wealth view. Always double-check the exact string value when setting this flag, especially when excluding accounts.

**Default Behavior**: Streams without the `include_in_wealth` label default to included (backward compatible).

**Affected Views** (exclude streams when `include_in_wealth ≠ 'true'`):
1. `main-indicators` - Excludes streams from total savings calculation
2. `current-savings-distribution` - Excludes streams from distribution breakdown
3. `total-history-per-day` - Excludes streams from historical balance calculation
4. `investment-indicators` - Excludes streams from investment total
5. `investment-types-distribution` - Excludes streams from type distribution

**Composition Views** (always include all streams, regardless of flag):
1. `investment-wallets-distribution` - Shows composition across wallets (includes excluded)
2. `investment-types-distribution-per-wallet` - Shows per-wallet breakdown (includes excluded)

**SQL Filter Used**: All wealth views apply this filter to stream CTEs:
```sql
WHERE ... AND (labels->>'include_in_wealth' IS NULL OR labels->>'include_in_wealth' = 'true')
```

**Example**: Exclude a wallet from wealth calculations
```python
import mankkoo.data_for_test as dt

# Create a stream that should NOT be counted in wealth totals
excluded_stream = dt.any_account_stream(
    account_type='savings',
    wallet='Personal',
    include_in_wealth=False  # This sets labels["include_in_wealth"] = "false" (string)
)

# Or manually set the flag on an existing stream (use STRING "false", not boolean)
stream.labels = {
    "wallet": "Personal",
    "include_in_wealth": "false"  # Use exact string "false", NOT boolean or "False"
}
```

**Via Database SQL**:
```sql
-- CORRECT: Include in wealth
UPDATE streams SET labels = jsonb_set(labels, '{include_in_wealth}', '"true"'::jsonb) WHERE id = '...';

-- CORRECT: Exclude from wealth
UPDATE streams SET labels = jsonb_set(labels, '{include_in_wealth}', '"false"'::jsonb) WHERE id = '...';

-- WRONG: Will exclude (boolean, not string)
UPDATE streams SET labels = jsonb_set(labels, '{include_in_wealth}', 'true'::jsonb) WHERE id = '...';
```

---

## Project Structure

```
mankkoo/
├── account/               # Account management module
│   ├── importer/         # Bank transaction import (CRITICAL FEATURE)
│   │   ├── importer.py   # Main importer orchestrator
│   │   ├── pl_ing.py     # ING Bank Poland parser
│   │   ├── pl_mbank.py   # mBank Poland parser
│   │   └── pl_millenium.py # Millenium Bank Poland parser
│   ├── account.py        # Account operations logic
│   ├── account_db.py     # Account database queries
│   └── models.py         # Account-related models & enums
├── controller/           # Flask API endpoints (APIFlask blueprints)
│   ├── account_controller.py
│   ├── admin_controller.py
│   ├── investment_controller.py
│   ├── main_controller.py
│   └── stream_controller.py
├── investment/           # Investment management
│   └── investment_db.py
├── stream/               # Stream operations
│   └── stream_db.py
├── util/                 # Utility functions
│   └── data_formatter.py
├── app.py               # Flask application factory & DB listener
├── base_logger.py       # Logging configuration
├── config.py            # Environment configurations (Dev/Prod/Test)
├── database.py          # Database connection & schema initialization
├── event_store.py       # Core event sourcing logic
├── views.py             # Materialized view management
└── data_for_test.py     # Test data helper functions

tests/                   # Test directory (mirrors mankkoo/ structure)
├── account/
│   ├── account_test.py
│   ├── importer_test.py
│   └── data/           # Test CSV files for importer testing
├── controller/
├── util/
├── conftest.py         # Pytest fixtures & testcontainer setup
├── event_store_test.py
└── views_test.py
```

---

## Module Separation & Common Code

### Module Independence

Each module (`account/`, `investment/`, `stream/`) is designed to be relatively independent:

- Each has its own database query logic (`*_db.py`)
- Each has its own business logic
- Each has its own controller for API endpoints

### Shared/Common Components

1. **event_store.py** - Used by all modules for storing/loading events
2. **database.py** - Database connection and initialization
3. **views.py** - Aggregates data from all modules
4. **base_logger.py** - Centralized logging
5. **data_for_test.py** - Test helpers used across test modules

---

## Coding Conventions

### Python Style

- **Line Length**: Max 160 characters (configured in pyproject.toml)
- **Formatting**: 
  - Black for code formatting
  - isort for import sorting
  - autoflake for removing unused imports
- **Type Hints**: Use type hints (mypy configured)
- **Imports**: Standard library → Third-party → Local imports

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case()`
- **Private Functions**: Prefix with `__` (e.g., `__load_current_total_savings()`)
- **Constants**: `UPPER_CASE` or `lower_case_with_underscores` for keys

### Database Queries

- Use parameterized queries with psycopg2: `cur.execute(query, (param1, param2))`
- **Exception**: Some dynamic queries use f-strings (but only for table/column names, never user input)
- Always use `with db.get_connection() as conn:` for connection management
- Always use `with conn.cursor() as cur:` for cursor management

### Logging

```python
from mankkoo.base_logger import log

log.info("Message")      # Use for important operations
log.debug("Details")     # Use for detailed debugging
log.error("Error", exc_info=True)  # Use for errors
```

---

## Testing Conventions

### Test File Naming

**Important**: Use suffix `_test.py`, NOT prefix `test_*.py`

```
✓ account_test.py
✓ importer_test.py
✓ event_store_test.py
✗ test_account.py  (WRONG)
```

### Test Structure

Tests mirror the source structure:
- `tests/account/` → `mankkoo/account/`
- `tests/controller/` → `mankkoo/controller/`

### Pytest Configuration

**Location**: `tests/conftest.py`

#### Session-Level Setup
- Starts PostgreSQL testcontainer (postgres:16-alpine)
- Initializes database schema
- Creates Flask app with TestConfig

#### Function-Level Setup
- Truncates all tables before each test (clean slate)
- Handles deadlock retries automatically

### Test Fixtures

```python
# Common fixtures in conftest.py
@pytest.fixture
def test_client(app):
    return app.test_client()

@pytest.fixture
def app():
    return create_app(TestConfig)

@pytest.fixture
def account_with_two_operations():
    # Returns pre-configured test events
    ...
```

### Test Data Helpers

**Location**: `mankkoo/data_for_test.py`

Use these helper functions to create test data:

```python
import mankkoo.data_for_test as td

# Create streams
stream = td.any_account_stream(account_type='checking', active=True, wallet='Personal')
stream = td.any_stream(stream_type='investment', stream_subtype='treasury_bonds')

# Create complete test scenarios
account_data = td.an_account_with_operations(
    operations=[
        {"operation": 1000.0, "date": "01-01-2021"},
        {"operation": -200.0, "date": "02-02-2021"}
    ]
)
# Returns: {"stream": Stream, "events": [Event, Event, ...]}

stock_data = td.stock_events(operations=[...], type='ETF', wallet='IKE')
investment_data = td.investment_events(operations=[...], category='treasury_bonds')
```

### Running Tests

```bash
# Install dependencies
poetry install

# Run all tests with coverage
poetry run pytest -s -vv --cov=./mankkoo

# Run specific test file
poetry run pytest -s -vv tests/account/account_test.py

# Run specific test
poetry run pytest -s -vv tests/account/account_test.py::test_new_operations_are_added_to_event_store
```

### Test Patterns

#### Pattern 1: Testing Event Storage
```python
def test_new_operations_are_added_to_event_store(mocker):
    # GIVEN: Create a stream
    account_stream = td.any_account_stream()
    es.create([account_stream])
    
    # WHEN: Perform operation
    account.add_new_operations(account_stream.id, contents=csv_data)
    
    # THEN: Verify events
    events = es.load(account_stream.id)
    assert len(events) == 6
    assert events[0].event_type == "MoneyDeposited"
```

#### Pattern 2: Testing Async View Updates
```python
def test_views_are_updated(mocker):
    # GIVEN: Setup
    account_stream = td.any_account_stream()
    es.create([account_stream])
    app.start_listener_thread()  # Start listener
    
    # WHEN: Add operations
    account.add_new_operations(account_stream.id, contents=csv_data)
    
    # THEN: Wait for async view updates
    def all_views_are_created():
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM views")
                (views_count,) = cur.fetchone()
        return views_count == 7
    
    __wait_for_condition(condition_func=all_views_are_created, timeout=10)
```

#### Pattern 3: Testing Importers
```python
def test_load_pl_ing():
    # GIVEN: Test data file
    ing_file = "tests/account/data/test_pl_ing.csv"
    
    # WHEN: Import
    result = importer.load_bank_data(
        file_path=ing_file,
        contents=None,
        kind=models.Bank.PL_ING,
        account_id="iban-1"
    )
    
    # THEN: Verify DataFrame format
    assert_frame_equal(expected, result)
```

---

## Bank Import System (Critical Feature)

**Location**: `mankkoo/account/importer/`

This is one of the most important features - importing bank transactions from CSV exports.

### Architecture

1. **Importer Interface** (`models.py`):
   ```python
   class Importer(ABC):
       @abstractmethod
       def load_file_by_filename(file_path: str) -> pd.DataFrame
       
       @abstractmethod
       def load_file_by_contents(contents: bytes) -> pd.DataFrame
       
       @abstractmethod
       def format_file(df: pd.DataFrame, account_id: str) -> pd.DataFrame
   ```

2. **Bank-Specific Implementations**:
   - `pl_ing.py` - ING Bank Poland
   - `pl_mbank.py` - mBank Poland
   - `pl_millenium.py` - Bank Millenium Poland

3. **Main Orchestrator** (`importer.py`):
   - Validates input parameters
   - Selects appropriate bank importer
   - Returns standardized DataFrame

### Standard DataFrame Format

All importers must produce a DataFrame with these columns (from `database.py:9-19`):

```python
account_columns = [
    "Account",      # Account ID (string)
    "Date",         # Transaction date (datetime.date)
    "Title",        # Transaction description (string)
    "Details",      # Additional details (optional)
    "Category",     # Category (optional)
    "Comment",      # User comment (optional)
    "Operation",    # Amount (float, negative for withdrawals)
    "Currency",     # Currency code (string, e.g., 'PLN')
    "Balance",      # Running balance (optional, calculated later)
]
```

### Importer Pipeline Pattern

Bank importers use pandas `.pipe()` for transformation pipelines:

```python
def format_file(self, df: pd.DataFrame, account_id: str):
    return (
        df.pipe(remove_non_tabular_data)
          .pipe(prepare_title)
          .pipe(select_only_required_columns)
          .pipe(rename_columns)
          .pipe(format_date_column)
          .pipe(get_operation)
          .pipe(add_account_id_to_each_row, account_id)
          .pipe(sort_rows_by_date)
          .pipe(reset_row_indexes)
          .pipe(order_columns, db.account_columns)
    )
```

### Adding a New Bank Importer

1. Create `mankkoo/account/importer/pl_newbank.py`
2. Inherit from `models.Importer`
3. Implement the three abstract methods
4. Add bank enum to `models.Bank`
5. Add case to `importer.py` load_bank_data()
6. Create test CSV in `tests/account/data/test_pl_newbank.csv`
7. Add test in `tests/account/importer_test.py`

### Event Creation from Import

**Location**: `mankkoo/account/account.py:14-78`

After import, the system:
1. Loads DataFrame from importer
2. Gets current stream version
3. Calculates running balance
4. Creates `MoneyDeposited` or `MoneyWithdrawn` events
5. Stores events via `event_store.store()`

```python
def add_new_operations(account_id: str, file_name=None, contents=None) -> None:
    bank = db.get_bank_type(account_id)
    df_new = importer.load_bank_data(file_name, contents, bank, account_id)
    events = __prepare_events(account_id, df_new)
    es.store(events)
```

---

## API Endpoints (Controllers)

**Location**: `mankkoo/controller/*_controller.py`

### APIFlask Blueprint Pattern

```python
from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Integer, Float

# Create blueprint
account_endpoints = APIBlueprint("account_endpoints", __name__, tag="Account")

# Define schemas for request/response
class AccountOperationResult(Schema):
    result = String()
    details = String()

# Define endpoint
@account_endpoints.route("/<account_id>/operations/import", methods=["POST"])
@account_endpoints.input(OperationsImport, location="files")
@account_endpoints.output(AccountOperationResult, status_code=200)
@account_endpoints.doc(summary="Import account operations", description="...")
def import_operations(account_id, data):
    # Implementation
    return {"result": "Success", "details": "..."}
```

### Endpoint Registration

**Location**: `mankkoo/app.py:57-61`

```python
app.register_blueprint(admin_endpoints, url_prefix="/api/admin")
app.register_blueprint(main_endpoints, url_prefix="/api/main")
app.register_blueprint(account_endpoints, url_prefix="/api/accounts")
app.register_blueprint(investment_endpoints, url_prefix="/api/investments")
app.register_blueprint(stream_endpoints, url_prefix="/api/streams")
```

### API Documentation

- **Swagger UI**: http://localhost:5000/docs
- **OpenAPI Spec**: http://localhost:5000/openapi.yaml
- **Auto-generated** from APIFlask decorators and schemas

---

## Environment Configuration

**Location**: `mankkoo/config.py`

Three environments:
- **DevConfig**: Development (port 5000, DEBUG=True, DB_NAME='dev')
- **ProdConfig**: Production (port 8080, DEBUG=False, DB_NAME='mankkoo')
- **TestConfig**: Testing (port 5555, DEBUG=True, DB_NAME='test')

Selected via environment variable:
```python
profile = os.getenv("FLASK_ENV", "prod")  # default: prod
```

### Database Connection

**Location**: `mankkoo/database.py:176-189`

Environment variables:
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: postgres)
- `DB_USERNAME` (default: postgres)
- `DB_PASSWORD` (default: postgres)

---

## Docker Deployment

**Location**: `Dockerfile`

### Key Points

1. **Base Image**: `python:3.11-slim`
2. **Dependencies**: Uses `requirements.txt` (NOT poetry) for production
3. **Working Directory**: `/app`
4. **Entry Point**: `flask run`

### Building Requirements.txt

Poetry is used for development, but Docker uses pip:

```bash
# Export dependencies from poetry to requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

**Important**: Whenever you update `pyproject.toml`, regenerate `requirements.txt`

---

## Common Operations

### Adding a New Event Type

1. **Define Event Type**: Choose descriptive name (e.g., `MoneyTransferred`)

2. **Create Event in Code**:
   ```python
   event = es.Event(
       stream_type="account",
       stream_id=account_id,
       event_type="MoneyTransferred",
       data={
           "from_account": "...",
           "to_account": "...",
           "amount": 100.0,
           "balance": 500.0,
           "currency": "PLN"
       },
       occured_at=datetime.now(timezone.utc),
       version=next_version
   )
   ```

3. **Store Event**:
   ```python
   es.store([event])
   ```

4. **Update Views** (if needed):
   - Modify view queries in `views.py` to account for new event type
   - Views update automatically via trigger

### Creating a New Stream Manually

```sql
INSERT INTO streams (id, type, subtype, name, bank, version, metadata, labels) 
VALUES (
    gen_random_uuid(), 
    'investment', 
    'treasury_bonds',
    '10-year Treasury Bonds',
    'PKO',
    0,
    '{"active": true, "details": "6.80% interest"}'::jsonb,
    '{"wallet": "Personal"}'::jsonb
);
```

Or via Python:

```python
stream = es.Stream(
    id=uuid.uuid4(),
    type='investment',
    subtype='treasury_bonds',
    name='10-year Treasury Bonds',
    bank='PKO',
    active=True,
    version=0,
    metadata={"active": True, "details": "6.80% interest"},
    labels={"wallet": "Personal"}
)
es.create([stream])
```

### Querying Events

```python
# Load all events for a stream
events = es.load(stream_id)

# Load latest event
latest = es.load_latest_event_id(stream_id)

# Get stream by ID
stream = es.get_stream_by_id(stream_id)

# Get stream by metadata field
stream = es.get_stream_by_metadata("accountNumber", "PL1234567890")
```

### Updating Stream Metadata

```python
# Update metadata
metadata = {
    "accountNumber": "PL1234567890",
    "bankUrl": "https://bank.com",
    "importer": "PL_ING"
}
es.update_stream_metadata(stream_id, metadata)

# Retrieve metadata
meta = es.get_stream_metadata(stream_id)
```

---

## Development Workflow

### Local Development Setup

1. **Install Poetry** (if not installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install Dependencies**:
   ```bash
   poetry install
   ```

3. **Start PostgreSQL** (via Docker):
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16-alpine
   ```

4. **Run Application**:
   ```bash
   poetry run flask run --reload
   ```
   
   Or from within poetry shell:
   ```bash
   poetry shell
   flask run --reload
   ```

5. **Access API**:
   - API: http://localhost:5000/api/
   - Docs: http://localhost:5000/docs

### Running Tests

```bash
# All tests
poetry run pytest -s -vv --cov=./mankkoo

# Specific module
poetry run pytest -s -vv tests/account/

# With coverage report
poetry run pytest --cov=./mankkoo --cov-report=html
```

### Code Quality Tools

```bash
# Format code
poetry run black mankkoo/ tests/

# Sort imports
poetry run isort mankkoo/ tests/

# Remove unused imports
poetry run autoflake --remove-all-unused-imports --in-place mankkoo/**/*.py

# Type checking
poetry run mypy mankkoo/

# Linting
poetry run flake8 mankkoo/
```

---

## Common Patterns & Best Practices

### 1. Working with Events

**Always increment version sequentially**:
```python
stream = es.get_stream_by_id(stream_id)
next_version = stream.version + 1

event = es.Event(
    stream_type="account",
    stream_id=stream_id,
    event_type="MoneyDeposited",
    data={...},
    occured_at=datetime.now(timezone.utc),
    version=next_version  # Important!
)
```

**Handle optimistic concurrency**:
The `append_event` function validates versions. If concurrent operations happen, one will fail with a version mismatch error.

### 2. Working with Views

**Load view data**:
```python
from mankkoo import views

# Load a specific view
main_indicators = views.load_view("main-indicators")
# Returns: {"savings": 10000.0, "netWorth": null, ...}

# Manually trigger view updates
views.update_views(oldest_date)
```

**Views are eventually consistent**: After inserting events, views update asynchronously. In production, this is fast (<1s). In tests, you may need to poll:

```python
import time

def wait_for_view(view_name, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        view = views.load_view(view_name)
        if view is not None:
            return view
        time.sleep(0.5)
    raise TimeoutError(f"View {view_name} not ready")
```

### 3. Database Transactions

**Use context managers**:
```python
with db.get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT ...")
        results = cur.fetchall()
        conn.commit()  # If needed
```

**Avoid manual connection closing**: Context managers handle it.

### 4. Error Handling

```python
try:
    es.store(events)
    return {"result": "Success", "details": "Events stored"}
except Exception as ex:
    log.error(f"Failed to store events: {ex}", exc_info=True)
    return {"result": "Failure", "details": str(ex)}, 500
```

### 5. Pandas DataFrame Handling

**Importer transformations**:
```python
import numpy as np

# Convert to numeric
df["Operation"] = pd.to_numeric(df["Operation"])

# Format dates
df["Date"] = pd.to_datetime(df["Date"])
df["Date"] = df["Date"].dt.date

# Handle missing values
df["Currency"] = df["Currency"].fillna("PLN")
df["Title"] = np.where(df["Title"].isna(), "No title", df["Title"])

# Sort and reset index
df = df.sort_values(by="Date").reset_index(drop=True)
```

---

## Troubleshooting

### Issue: Events Not Storing

**Check**:
1. Stream exists: `es.get_stream_by_id(stream_id)`
2. Version is correct: Should be `stream.version + 1`
3. Database connection: Check environment variables
4. Look for exception in logs

### Issue: Views Not Updating

**Check**:
1. Listener thread is running: Should start automatically in `app.py`
2. PostgreSQL NOTIFY/LISTEN is working: Check logs for "Received notification"
3. View update query is correct: Check `views.py` for SQL errors
4. Database trigger exists: Run `db.init_db()` to recreate

### Issue: Import Fails

**Check**:
1. File encoding: Most Polish banks use `windows-1250` or `utf-8`
2. CSV separator: Usually `;` or `,`
3. Bank type matches: Ensure correct `models.Bank` enum value
4. Account exists: Must have stream with matching `account_id` in metadata

### Issue: Tests Fail with Deadlock

**Solution**: Tests already retry on deadlock (see `conftest.py:48-60`). If persistent:
1. Ensure `setup_data()` fixture is running
2. Check for parallel test execution conflicts
3. Increase retry count or delay

---

## Stream Types & Subtypes

### Current Stream Types

1. **account**
   - Subtypes: `checking`, `savings`, `cash`
   - Events: `AccountOpened`, `MoneyDeposited`, `MoneyWithdrawn`

2. **investment**
   - Subtypes: `treasury_bonds`, `corporate_bonds`, `real_estate`, etc.
   - Events: `TreasuryBondsBought`, `TreasuryBondsMatured`, etc.

3. **stocks**
   - Subtypes: `ETF`, `stock`
   - Events: `ETFBought`, `ETFSold`, `StockBought`, `StockSold`

4. **retirement**
   - Similar to account, but for retirement-specific accounts
   - Events: Same as account

### Adding New Stream Type

1. Add type to database (no code changes needed for type itself)
2. Create module in `mankkoo/<new_type>/`
3. Add controller in `controller/<new_type>_controller.py`
4. Update views to include new type in aggregations
5. Add test fixtures in `data_for_test.py`

---

## Performance Considerations

### Database

- **Indexes**: Critical indexes already exist on `stream_id` and `version`
- **JSONB Queries**: Use JSONB operators for metadata/labels queries
- **View Updates**: Expensive queries run async after events inserted
- **Connection Pooling**: Not currently implemented; single connection per request

### Pandas Operations

- **Large Imports**: For files >10k rows, consider chunking
- **Memory**: DataFrame operations are in-memory; large datasets may need optimization
- **Vectorization**: Use pandas vectorized operations, avoid row iteration where possible

### API Response Times

- **Views**: Pre-computed, very fast (<50ms)
- **Direct Queries**: Can be slow for large date ranges
- **Event Insertion**: Fast (<100ms for small batches)

---

## Security Considerations

### SQL Injection

- **Parameterized Queries**: Use `cur.execute(query, (param,))` for user input
- **JSONB**: Be careful with JSONB queries that interpolate user input
- **View Names**: Hardcoded, not user-controlled

### Authentication

**Currently not implemented**. The API is open. Future work should add:
- User authentication (JWT, OAuth)
- Multi-tenancy (user_id in streams)
- Row-level security in PostgreSQL

### Data Validation

- **APIFlask Schemas**: Validate input at controller level
- **Event Data**: No strict schema validation; rely on application logic
- **File Uploads**: Limited to CSV, but no size limits currently

---

## Future Improvements / Technical Debt

1. **Authentication & Multi-tenancy**: Add user isolation
2. **Connection Pooling**: Use psycopg2 pool or SQLAlchemy
3. **Event Schema Validation**: Consider JSON Schema for event.data
4. **Async Processing**: Use Celery for long-running imports
5. **View Incremental Updates**: Instead of full rebuild, update incrementally
6. **API Rate Limiting**: Protect against abuse
7. **Audit Logging**: Track who made changes (when auth added)
8. **Backup Strategy**: Automated backups of event store

---

## Key Files Reference

### Must-Read Files
1. `mankkoo/database.py` - Schema, triggers, connection
2. `mankkoo/event_store.py` - Core event sourcing
3. `mankkoo/views.py` - View management
4. `mankkoo/app.py` - Application setup, listener thread
5. `tests/conftest.py` - Test configuration

### Important for Feature Work
- `mankkoo/account/importer/` - Bank import system
- `mankkoo/account/account.py` - Account operations
- `mankkoo/controller/` - API endpoints
- `mankkoo/data_for_test.py` - Test data helpers

---

## Quick Command Reference

```bash
# Development
poetry install                          # Install dependencies
poetry run flask run --reload           # Run dev server
poetry shell                            # Enter poetry virtualenv

# Testing
poetry run pytest -s -vv                # Run all tests
poetry run pytest --cov=./mankkoo      # With coverage
poetry run pytest tests/account/        # Specific module

# Code Quality
poetry run black mankkoo/ tests/        # Format code
poetry run isort mankkoo/ tests/        # Sort imports
poetry run mypy mankkoo/                # Type checking
poetry run flake8 mankkoo/              # Linting

# Database (manual operations)
psql -U postgres -d mankkoo             # Connect to DB
SELECT * FROM streams;                  # View streams
SELECT * FROM events ORDER BY added_at DESC LIMIT 10;
SELECT * FROM views;                    # View materialized views

# Docker
docker build -t mankkoo-backend .       # Build image
docker run -p 5000:5000 mankkoo-backend # Run container
poetry export -f requirements.txt --output requirements.txt  # Update deps
```

---

## Questions & Getting Help

When stuck, check:
1. **Logs**: Application logs show detailed operation flow
2. **Database**: Query events/streams directly to verify state
3. **Tests**: Look at test files for usage examples
4. **API Docs**: http://localhost:5000/docs for endpoint specs

Common questions:
- **"How do I add a new operation?"** → Create Event, store via `es.store()`
- **"How do I import transactions?"** → Use `account.add_new_operations()`
- **"How do I query current balance?"** → Load view: `views.load_view("main-indicators")`
- **"How do I add a new bank?"** → Follow bank importer pattern in `importer/`

---

## Glossary

- **Stream**: A sequence of events representing a financial entity (account, investment, etc.)
- **Event**: An immutable record of something that happened (transaction, purchase, etc.)
- **Version**: Sequential number for events in a stream, ensures ordering
- **View**: Pre-computed, denormalized data for fast queries
- **Importer**: Module that parses bank-specific CSV into standard format
- **Event Sourcing**: Architectural pattern of storing all changes as immutable events
- **Optimistic Concurrency**: Version checking to prevent conflicting concurrent updates

---

**End of agents.md**

This document should be treated as the authoritative guide for AI agents working on this codebase. When in doubt, refer to this document and the source code it references.
