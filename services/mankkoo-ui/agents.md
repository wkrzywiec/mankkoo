# Mankkoo UI — Agent Guidelines

Personal finance management dashboard built with Next.js 14 (App Router), React 18, and TypeScript 5 (strict mode). Polish localization (PLN currency).

## Tech Stack

- **Framework:** Next.js 14 App Router, React 18
- **Language:** TypeScript 5 — strict mode enabled, no `any` types
- **HTTP:** Axios (`hooks/useHttp.ts`)
- **Charts:** Chart.js 4 + react-chartjs-2 5
- **Styling:** CSS Modules (co-located `.module.css` files), CSS custom properties in `globals.css`
- **Layout:** Custom 4-column CSS Grid system
- **Icons:** FontAwesome
- **Notifications:** SweetAlert2
- **Font:** Inter via `next/font/google`

## Project Structure

```
api/              # API response type interfaces & base URL
app/              # Next.js App Router pages (file-system routing)
components/
  charts/         # Reusable chart components (Bar, Line, Piechart, Table)
  elements/       # Reusable UI components (Button, Modal, Input, etc.)
  menu/           # Navigation sidebar
hooks/            # Custom React hooks (useHttp)
utils/            # Utility functions (Formatter)
```

Path alias `@/*` maps to the project root. Always use it for imports:
```ts
import { useGetHttp } from '@/hooks/useHttp';
```

## TypeScript Rules

- Strict mode is on — do not weaken it.
- Define TypeScript `interface` for all component props.
- API response shapes go in `api/` as dedicated interface files (e.g., `api/AccountsPageResponses.ts`).
- Never use `any`. Use `unknown` + type narrowing when the type is truly unknown.

## Component Guidelines

- Use `"use client"` directive at the top of every client component.
- Chart components must be imported via `next/dynamic` with `{ ssr: false }` to avoid hydration errors:
  ```ts
  const LineChart = dynamic(() => import('@/components/charts/Line'), { ssr: false });
  ```
- Each new chart type must be a **separate, reusable component** in `components/charts/`. Accept data and configuration via typed props — never hardcode data inside chart components.
- Register only the Chart.js elements/plugins that the specific chart needs (`ChartJS.register(...)`).
- Use colors from `mankkooColors` array or `getColor(index)` in `app/colors.tsx`.
- Reusable UI elements go in `components/elements/`.

## HTTP & Data Fetching

- **GET requests:** Use the `useGetHttp<Type>(apiPath, enabled?)` hook from `hooks/useHttp.ts`. It returns `{ isFetching, fetchedData, setFetchedData, error }`.
- **POST requests:** Use `postJson(apiPath, body, successMsg?, failureMsg?)` from the same file.
- **File uploads:** Use `uploadFile(apiPath, file)`.
- API base URL is defined in `api/ApiUrl.ts`.
- Create domain-specific custom hooks (like `useInvestmentsData`, `useWallets`) to aggregate related API calls into a single hook.

## Layout & Grid System

The app uses a **4-column CSS Grid** defined in `globals.css`. Available utility classes:

| Class | Effect |
|---|---|
| `.mainContainer` | 4-column grid wrapper |
| `.gridItem` | Standard grid cell with margin |
| `.span2Columns` | Span 2 of 4 columns |
| `.span3Columns` | Span 3 of 4 columns |
| `.span4Columns` | Full-width row |
| `.span2Rows` | Span 2 rows vertically |

Use these classes for page layout. Combine with page-scoped CSS Module classes (`.horizontalAlignment`, `.verticalAlignment`) for flex-based sub-layouts within grid cells.

## Styling Rules

- Use **CSS Modules** only. No CSS-in-JS, no Tailwind, no inline styles (except for dynamic sizing).
- Co-locate `.module.css` files next to their component.
- Use CSS custom properties from `globals.css` for colors (e.g., `var(--main-bg-color)`, `var(--accent-red)`).
- Import the module as `classes` or `styles`:
  ```ts
  import classes from './Component.module.css';
  ```

## State Management

- Use React built-in state only: `useState`, `useEffect`, `useMemo`, `useCallback`.
- No external state management libraries.
- Derive state with `useMemo`/`useCallback` where appropriate to avoid unnecessary re-renders.
- Encapsulate page-level data fetching logic in custom hooks when a page needs multiple API calls.

## Formatting Utilities

Use existing formatters from `utils/Formatter.ts`:

- `currencyFormat(value)` — formats numbers as PLN currency.
- `percentage(value)` — formats as percentage.
- `iban(value)` — formats bank account numbers with spaces.

## Naming Conventions

- Components: PascalCase (`Piechart.tsx`, `EditableTable.tsx`)
- Hooks: camelCase prefixed with `use` (`useHttp.ts`, `useWallets.ts`)
- CSS Modules: match component name (`Piechart.module.css`)
- API type files: PascalCase describing the page (`AccountsPageResponses.ts`)
- Utility files: PascalCase (`Formatter.ts`)
