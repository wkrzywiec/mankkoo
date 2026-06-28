# Frontend — Technical Context

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI library**: React 18
- **Language**: TypeScript 5 (strict mode)
- **HTTP client**: Axios via `hooks/useHttp.ts`
- **Charts**: Chart.js 4 + react-chartjs-2 5
- **Styling**: CSS Modules + CSS custom properties
- **Layout**: Custom 4-column CSS Grid (`app/globals.css`)
- **Icons**: FontAwesome
- **Notifications**: SweetAlert2
- **Font**: Inter via `next/font/google`
- **Package manager**: npm (use npm — not pnpm, despite `pnpm-lock.yaml` existing)

## Commands

```bash
npm install          # install dependencies
npm run dev          # dev server on port 3000
npm run build        # production build (CI verification)
npm run lint         # ESLint (next lint)
```

## Development Setup

- Node.js 20+
- Run `npm install` first
- Dev server at `http://localhost:3000`
- Requires backend running at `http://localhost:5000` for API calls

## API Base URL

Hardcoded in `api/ApiUrl.ts` as `http://localhost:5000/api`.  
Change this file if the backend URL changes — it is the single source for the base URL.

## Styling Rules

- **CSS Modules only** — no CSS-in-JS, no Tailwind, no inline styles (except dynamic sizing)
- Co-locate `.module.css` files next to their component
- CSS custom properties from `app/globals.css` for colors (e.g., `var(--main-bg-color)`, `var(--accent-red)`)
- Import the module as `classes` or `styles`:
  ```ts
  import classes from './Component.module.css';
  ```

## Formatting Utilities (`utils/Formatter.ts`)

| Function | Purpose |
|---|---|
| `currencyFormat(value)` | Format numbers as PLN currency |
| `percentage(value)` | Format as percentage |
| `iban(value)` | Format bank account numbers with spaces |

Always use these instead of ad-hoc number formatting.

## CI

- `npm run build` is the CI gate for the frontend (`services-branch.yaml`, `services-main.yaml`)
- Production Docker image published to `ghcr.io/wkrzywiec/mankkoo-ui:latest`
