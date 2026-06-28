# Frontend — Project

## What It Is

Personal finance management dashboard built with Next.js 14 (App Router), React 18, and TypeScript 5 (strict mode). Polish localization (PLN currency).

## Responsibilities

- Display financial dashboard: net worth KPIs, charts, account/investment tables
- Provide CSV file upload UI for bank transaction imports
- Consume backend REST API at `http://localhost:5000/api/`
- Render charts (bar, line, pie) using Chart.js

## Non-Negotiable Rules

- TypeScript strict mode is on — never use `any`; use `unknown` + type narrowing
- Use `npm` (not pnpm) — CI uses `npm`; `pnpm-lock.yaml` exists but is ignored in CI
- Chart components must be imported via `next/dynamic` with `{ ssr: false }` — required to avoid hydration errors
- Use CSS Modules only — no CSS-in-JS, no Tailwind, no inline styles (except dynamic sizing)
- API response shapes live in `api/` as dedicated interface files
- All financial values formatted in PLN using `currencyFormat()` from `utils/Formatter.ts`
