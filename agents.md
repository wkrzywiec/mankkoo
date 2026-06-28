# Mankkoo — Agent Guidelines

Mankkoo is a personal finance app (event sourcing, PLN currency, two services: Flask backend + Next.js frontend).

## Memory Bank

Full project context lives in `.memory/` — always loaded by opencode:

- `.memory/project.md` — requirements and scope
- `.memory/context.md` — why it exists, how it works, UX goals
- `.memory/architecture.md` — system architecture, event sourcing, views, component relationships
- `.memory/techContext.md` — tech stack, dev setup, CI/CD, cross-service conventions

## Service-Specific Context

Before making changes in a service, read its memory bank:

- **Backend** (`services/mankkoo/.memory/`) — event sourcing patterns, DB schema, API endpoints, bank importers, testing conventions, Python coding style
- **Frontend** (`services/mankkoo-ui/.memory/`) — component patterns, TypeScript rules, CSS Modules, Chart.js, HTTP hooks, grid layout

The detailed `agents.md` in each service directory has additional command references and examples.
