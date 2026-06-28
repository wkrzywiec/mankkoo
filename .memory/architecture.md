# Mankkoo — Architecture

## System Overview

```
Browser (port 3000)
    |
    |  HTTP / JSON (Axios)
    v
Next.js UI (services/mankkoo-ui)
    |
    |  REST API (http://localhost:5000/api/)
    v
Flask Backend (services/mankkoo)
    |
    |  psycopg2 (event sourcing, NOTIFY/LISTEN)
    v
PostgreSQL 16 (services/infra)
    |
    pgAdmin 4 (port 5050) — admin UI
```

## Container Map

| Service | Container | Port | Image |
|---|---|---|---|
| **UI** | `mankkoo-ui` | 3000 | `ghcr.io/wkrzywiec/mankkoo-ui:latest` |
| **Backend** | `mankkoo-core` | 5000 | `ghcr.io/wkrzywiec/mankkoo-core:latest` |
| **PostgreSQL** | `mankkoo-postgres` | 5432 | `postgres:16` |
| **pgAdmin** | `pgadmin` | 5050 | `dpage/pgadmin4:9.4` |

## Key Architectural Decision: Event Sourcing

All financial state is stored as **immutable events**, never mutable rows. This means:
- You can reconstruct any past state by replaying events
- No data is ever deleted or overwritten
- Corrections are new events, not edits

Three PostgreSQL tables:
| Table | Purpose |
|---|---|
| `streams` | Financial entities (accounts, investments, stocks, retirement) |
| `events` | Append-only event log; `UNIQUE(stream_id, version)` enforces ordering |
| `views` | Pre-computed JSONB blobs for fast API reads |

## Materialized View Pattern

To avoid expensive live aggregation on every API call, the backend maintains 7 pre-computed views in the `views` table:

- `main-indicators` — total net worth KPIs
- `current-savings-distribution` — breakdown by account type
- `total-history-per-day` — time-series for line chart
- `investment-indicators` — investment KPIs
- `investment-types-distribution` — by bond/stock/real estate type
- `investment-wallets-distribution` — by wallet label
- `investment-types-distribution-per-wallet` — cross-dimension

**Update flow**: `INSERT event` → PostgreSQL trigger → `NOTIFY 'events_added'` → background listener thread in `app.py` → `views.update_views()`

Views update **asynchronously** — do not assume immediate consistency in tests; poll with a timeout.

## `include_in_wealth` Label

Streams can be excluded from wealth-total views via a label:
- `labels["include_in_wealth"] = "true"` → included (only this exact lowercase string)
- missing key → included (backward-compatible default)
- anything else → excluded

Wealth views: `main-indicators`, `current-savings-distribution`, `total-history-per-day`, `investment-indicators`, `investment-types-distribution`.
Composition views (always include all): `investment-wallets-distribution`, `investment-types-distribution-per-wallet`.

## Component Relationships

- UI → Backend: REST/JSON over HTTP, base URL `http://localhost:5000/api/`
- Backend → DB: psycopg2 connection pool, parameterized queries
- DB → Backend: NOTIFY/LISTEN async channel for view invalidation
- API documented at `http://localhost:5000/docs` (Swagger UI)

## Critical Implementation Paths

### Adding a New Event
1. Read stream version: `stream = es.get_stream_by_id(stream_id)`
2. Build event: `es.Event(version=stream.version + 1, ...)`
3. Store: `es.store([event])` — uses `append_event()` PostgreSQL function (optimistic concurrency)
4. Never INSERT into `events` directly

### Adding a New Bank Importer
1. `mankkoo/account/importer/pl_newbank.py` — implement `models.Importer` ABC
2. Add to `models.Bank` enum
3. Add case in `importer.py:load_bank_data()`
4. Add test CSV + importer test

### Adding a New API Endpoint
1. Add route in the relevant `controller/` blueprint using `APIBlueprint`
2. Define input/output schemas inheriting `apiflask.Schema`
3. Register blueprint in `app.py` if new

## Repository Structure

```
mankkoo/
  docker-compose.yaml       # Orchestrates all containers
  Taskfile.yaml             # Dev task runner
  .devcontainer/            # VS Code DevContainer config
  .github/workflows/        # CI pipelines
  services/
    mankkoo/                # Backend service (Python/Flask)
    mankkoo-ui/             # Frontend service (Next.js/React)
    infra/
      postgres/             # init-db.sql, backup/restore scripts
      pgadmin/              # Auto-connect server config
  backup/                   # PostgreSQL dump files (.dump.gz)
  docs/                     # MkDocs documentation source
```
