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

Three services, all orchestrated via `docker-compose.yaml`:

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
| **Backend** | Python 3.10+, Flask / APIFlask, pandas, psycopg2, Poetry (dev) / pip (prod) |
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
  Taskfile.yaml              # Dev task runner (test, lint, backup, etc.)
  .devcontainer/             # VS Code DevContainer config
  .github/
    workflows/               # CI: branch tests, main build + Docker publish
    copilot-instructions.md  # GitHub Copilot custom instructions
  services/
    mankkoo/                 # Backend service (Python/Flask)
      agents.md              # Backend-specific agent guidelines (detailed)
      mankkoo/               # Application source code
      tests/                 # pytest + testcontainers
    mankkoo-ui/              # Frontend service (Next.js/React)
      agents.md              # UI-specific agent guidelines
      app/                   # Next.js App Router pages
      components/            # Reusable UI components
    infra/                   # Infrastructure config
      postgres/              # init-db.sql, backup/restore scripts
      pgadmin/               # Auto-connect server config
  backup/                    # PostgreSQL dump files
  docs/                      # MkDocs documentation source
```

## Service-Specific Guidelines

Each service has its own `agents.md` with detailed conventions:

- **Backend** (`services/mankkoo/agents.md`) — event sourcing patterns, database schema, API endpoints, bank importer system, testing with testcontainers, Python coding conventions
- **Frontend** (`services/mankkoo-ui/agents.md`) — component patterns, TypeScript rules, CSS Modules, hooks, Chart.js usage, grid layout system

Always read the relevant service-level `agents.md` before making changes in that service.

## Development Workflow

### Prerequisites

- Docker (for PostgreSQL, pgAdmin, and full-stack runs)
- Python 3.10+ with Poetry (backend development)
- Node.js 20+ with npm (frontend development)
- [Taskfile](https://taskfile.dev) CLI (optional but recommended)

### Common Tasks (via Taskfile)

```bash
task infra               # Start PostgreSQL + pgAdmin containers
task mankkoo:dev         # Start backend (Flask) in dev mode with DB
task ui:dev              # Start frontend (Next.js) in dev mode
task mankkoo:test        # Run backend tests (pytest + testcontainers)
task ui:build            # Build frontend for production
task mankkoo:lint        # Format + lint backend code (black, isort, autoflake)
task run                 # Run entire stack in Docker
task backup              # Create PostgreSQL dump
task restore             # Restore PostgreSQL from dump
```

### Running Without Taskfile

```bash
# Backend
cd services/mankkoo
poetry install
poetry run flask run --reload      # Dev server on port 5000

# Frontend
cd services/mankkoo-ui
npm install
npm run dev                        # Dev server on port 3000

# Infrastructure
docker compose up -d mankkoo-postgres pgadmin
```

### Full Docker Stack

```bash
docker compose up -d               # All services on published images
```

## CI/CD

Defined in `.github/workflows/`:

- **Branch push** (`services-branch.yaml`) — runs backend pytest and frontend build
- **Main push** (`services-main.yaml`) — runs tests, then builds and publishes Docker images to GitHub Container Registry (`ghcr.io`)
- **Pull requests** (`pull-request.yaml`) — runs Python linter with PR review comments

## Cross-Service Conventions

- The UI calls the backend at `http://localhost:5000/api/` (hardcoded in `api/ApiUrl.ts`)
- CORS is enabled on the backend for local development
- The backend API is documented via OpenAPI/Swagger at `http://localhost:5000/docs`
- All financial values use PLN (Polish zloty) currency
- The database schema is created programmatically by the backend on startup (`database.py:init_db()`)
- Three database environments: `test`, `dev`, `mankkoo` (production) — created by `init-db.sql`
