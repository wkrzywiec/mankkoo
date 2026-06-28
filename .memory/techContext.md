# Mankkoo — Technical Context

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript 5 (strict), Chart.js 4, Axios, CSS Modules |
| **Backend** | Python 3.10+, Flask / APIFlask, pandas, psycopg2, uv |
| **Database** | PostgreSQL 16 with JSONB, NOTIFY/LISTEN triggers, event sourcing schema |
| **CI/CD** | GitHub Actions — test on branch push, build + publish Docker images on `main` |
| **Dev Env** | VS Code DevContainers, Taskfile (task runner) |

## Development Setup

### Prerequisites

- Docker (for PostgreSQL, pgAdmin, and full-stack runs)
- Python 3.10+ with `uv` (backend development)
- Node.js 20+ with `npm` (frontend) — CI uses `npm`; `pnpm-lock.yaml` exists in `mankkoo-ui/` but is NOT used in CI
- [Taskfile CLI](https://taskfile.dev) (optional but recommended)

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
uv run flask run --reload      # dev server on port 5000

# Frontend
cd services/mankkoo-ui
npm install
npm run dev                    # dev server on port 3000

# Infrastructure only
docker compose up -d mankkoo-postgres pgadmin
```

### Full Docker Stack

```bash
docker compose up -d           # All services on published images
```

### First-Time PostgreSQL Setup

After first `docker compose up`, copy `pg_hba.conf` manually:

```bash
docker cp services/infra/postgres/pg_hba.conf mankkoo-postgres:/var/lib/postgresql/data/pg_hba.conf
docker exec mankkoo-postgres psql -U postgres -c "SELECT pg_reload_conf();"
```

## Database Environments

Three environments created by `services/infra/postgres/init-db.sql`:

| `FLASK_ENV` | Config | DB name |
|---|---|---|
| `"prod"` (default) | `ProdConfig` | `mankkoo` |
| anything else | `DevConfig` | `dev` |
| set by test fixtures | `TestConfig` | `test` |

DB connection env vars (all default to `postgres`/`localhost`/`5432`): `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`.

## CI/CD

Defined in `.github/workflows/`:

- **Branch push** (`services-branch.yaml`) — backend pytest + frontend `npm run build`; triggers only on `services/**` changes
- **Main push** (`services-main.yaml`) — tests + builds and publishes Docker images to `ghcr.io`; coverage to Codecov
- **Pull requests** (`pull-request.yaml`) — wemake-python-styleguide linter with inline PR review comments

CI installs backend deps with `uv sync --frozen` (locked versions). Local dev uses `uv sync` (allows updates).

## Cross-Service Conventions

- UI → Backend URL: `http://localhost:5000/api/` — hardcoded in `services/mankkoo-ui/api/ApiUrl.ts`
- Backend API docs: `http://localhost:5000/docs` (Swagger UI), `http://localhost:5000/openapi.yaml`
- All financial values: **PLN (Polish zloty)**
- Database schema: created programmatically by `database.py:init_db()` on startup — **no migration tool**
- Stream types: `account`, `investment`, `stocks`, `retirement`

## Dependencies (key)

### Backend
- `flask` / `apiflask` — web framework + OpenAPI
- `psycopg2` — PostgreSQL driver
- `pandas` — CSV parsing for bank importers
- `uv` — Python package manager (replaces pip/poetry)

### Frontend
- `next` 14 — React framework
- `react` 18
- `axios` — HTTP client
- `chart.js` 4 + `react-chartjs-2` 5 — charting
- `sweetalert2` — notifications
- `@fortawesome/*` — icons
