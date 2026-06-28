# Backend — Context

## Why It Exists

The backend is the single source of truth for all financial data. It enforces the event sourcing invariants — no other part of the system is allowed to mutate financial history.

## Problems It Solves

- **Bank CSV diversity**: each Polish bank exports a different CSV format; the importer layer normalizes them all to a standard column set
- **Concurrency safety**: `append_event()` PostgreSQL function uses optimistic concurrency (version check) to prevent duplicate or out-of-order events
- **Read performance**: raw event replay would be too slow for dashboard queries; 7 materialized views pre-aggregate the data

## How It Works

1. Frontend calls REST endpoints (Flask blueprints, one per domain)
2. Controllers call domain functions (e.g., `account.py`, `investment_db.py`)
3. Domain functions use `event_store.py` to append events
4. DB trigger fires `NOTIFY 'events_added'` on every event insert
5. Background listener thread in `app.py` wakes up and calls `views.update_views()`
6. Next API call reads from pre-computed `views` table — fast

## Key Design Choices

- **Event sourcing over CRUD**: financial data is immutable by design; auditability is a first-class concern
- **Async view updates**: views are eventually consistent, not synchronously updated — keeps write path fast
- **Testcontainers**: integration tests use a real PostgreSQL container, not mocks — ensures DB behavior is tested accurately
- **uv over pip/poetry**: faster installs, reproducible lockfile, used in both local dev and CI
