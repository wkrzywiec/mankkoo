# Mankkoo — Project-Level Agent Guidelines

Mankkoo is a personal finance application for tracking bank accounts, investments, and net worth. It imports bank transactions from CSV files, stores them as immutable events (event sourcing), and visualizes financial data through a dashboard. Polish localization (PLN currency).

## Architecture

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

| Service | Container | Port | Image |
|---|---|---|---|
| **UI** | `mankkoo-ui` | 3000 | `ghcr.io/wkrzywiec/mankkoo-ui:latest` |
| **Backend** | `mankkoo-core` | 5000 | `ghcr.io/wkrzywiec/mankkoo-core:latest` |
| **PostgreSQL** | `mankkoo-postgres` | 5432 | `postgres:16` |
| **pgAdmin** | `pgadmin` | 5050 | `dpage/pgadmin4:9.4` |

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript 5 (strict), Chart.js 4, Axios, CSS Modules |
| **Backend** | Python 3.10+, Flask / APIFlask, pandas, psycopg2, uv |
| **Database** | PostgreSQL 16 with JSONB, NOTIFY/LISTEN triggers, event sourcing schema |
| **CI/CD** | GitHub Actions — test on branch push, build + publish Docker images on `main` |
| **Dev Env** | VS Code DevContainers, Taskfile (task runner) |

## Core Concept: Event Sourcing

The backend stores all financial operations as immutable events rather than mutable rows. The database has three tables:

- **`streams`** — financial entities (accounts, investments, stocks, retirement accounts)
- **`events`** — append-only log of operations per stream (with version-based optimistic concurrency)
- **`views`** — pre-computed JSONB materialized views for fast API responses

When events are inserted, a PostgreSQL trigger fires `NOTIFY 'events_added'`. A background listener thread in the backend rebuilds materialized views asynchronously.

## Repository Structure

```
mankkoo/
  docker-compose.yaml       # Orchestrates all containers
  Taskfile.yaml             # Dev task runner (test, lint, backup, etc.)
  .devcontainer/            # VS Code DevContainer config
  .github/
    workflows/              # CI: branch tests, main build + Docker publish
  services/
    mankkoo/                # Backend service (Python/Flask)
      agents.md             # Backend-specific agent guidelines (detailed)
      mankkoo/              # Application source code
      tests/                # pytest + testcontainers
    mankkoo-ui/             # Frontend service (Next.js/React)
      agents.md             # UI-specific agent guidelines
      app/                  # Next.js App Router pages
      components/           # Reusable UI components
    infra/
      postgres/             # init-db.sql (creates test/dev/mankkoo DBs), backup/restore scripts
      pgadmin/              # Auto-connect server config
  backup/                   # PostgreSQL dump files (.dump.gz)
  docs/                     # MkDocs documentation source
```

**Note**: `globals.css`, `layout.tsx`, and `mankkoo_logo.svg` at the repo root are stray files — the real frontend lives in `services/mankkoo-ui/`.

## Service-Specific Guidelines

Each service has its own `agents.md` with detailed conventions:

- **Backend** (`services/mankkoo/agents.md`) — event sourcing patterns, database schema, API endpoints, bank importer system, testing with testcontainers, Python coding conventions
- **Frontend** (`services/mankkoo-ui/agents.md`) — component patterns, TypeScript rules, CSS Modules, hooks, Chart.js usage, grid layout system

**Always read the relevant service-level `agents.md` before making changes in that service.**

## Development Workflow

### Prerequisites

- Docker (for PostgreSQL, pgAdmin, and full-stack runs)
- Python 3.10+ with uv (backend development)
- Node.js 20+ with npm (frontend development) — CI uses `npm`; a `pnpm-lock.yaml` exists in `mankkoo-ui/` but is not used in CI
- [Taskfile](https://taskfile.dev) CLI (optional but recommended)

### Common Tasks (via Taskfile)

```bash
task infra               # Start PostgreSQL + pgAdmin containers
task mankkoo:dev         # Start backend (Flask) in dev mode with DB
task ui:dev              # Start frontend (Next.js) in dev mode
task mankkoo:test        # Run backend tests (pytest + testcontainers)
task ui:build            # Build frontend for production
task mankkoo:lint        # Format + lint backend: autoflake → isort → autopep8 → black
task run                 # Run entire stack in Docker
task backup              # Create PostgreSQL backup (requires running mankkoo-postgres container)
task restore             # Restore PostgreSQL from dump (edit vars.file in Taskfile first)
task mankkoo:update      # Upgrade all backend dependencies and regenerate uv.lock
task mankkoo:req         # Export requirements.txt from uv (for Docker/reference)
```

### Running Without Taskfile

```bash
# Backend
cd services/mankkoo
uv sync
uv run flask run --reload      # Dev server on port 5000

# Frontend
cd services/mankkoo-ui
npm install
npm run dev                    # Dev server on port 3000

# Infrastructure only
docker compose up -d mankkoo-postgres pgadmin
```

### Full Docker Stack

```bash
docker compose up -d           # All services on published images
```

### First-Time PostgreSQL Setup

After first `docker compose up`, the `pg_hba.conf` must be copied manually for auth to work:

```bash
docker cp services/infra/postgres/pg_hba.conf mankkoo-postgres:/var/lib/postgresql/data/pg_hba.conf
docker exec mankkoo-postgres psql -U postgres -c "SELECT pg_reload_conf();"
```

## CI/CD

Defined in `.github/workflows/`:

- **Branch push** (`services-branch.yaml`) — runs backend pytest (`uv sync --frozen`) and frontend `npm run build`; triggers only when `services/**` changes
- **Main push** (`services-main.yaml`) — tests + builds and publishes Docker images to `ghcr.io`; coverage uploaded to Codecov
- **Pull requests** (`pull-request.yaml`) — runs wemake-python-styleguide linter with inline PR review comments

CI installs backend deps with `uv sync --frozen` (locked versions). Local dev uses `uv sync` (allows updates).

## Cross-Service Conventions

- The UI calls the backend at `http://localhost:5000/api/` — hardcoded in `services/mankkoo-ui/api/ApiUrl.ts`; change this file if the backend URL changes
- The backend API is documented via OpenAPI/Swagger at `http://localhost:5000/docs`
- All financial values use PLN (Polish zloty) currency
- The database schema is created programmatically by the backend on startup (`database.py:init_db()`) — no separate migration tool
- Three database environments: `test`, `dev`, `mankkoo` (production) — created by `services/infra/postgres/init-db.sql`
- FLASK_ENV selects the config: `test` → TestConfig, `dev` → DevConfig, anything else → ProdConfig (default)
