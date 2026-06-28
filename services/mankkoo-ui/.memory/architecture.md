# Frontend — Architecture

## Project Structure

```
services/mankkoo-ui/
  api/              # API response type interfaces & base URL
    ApiUrl.ts       # hardcoded base URL: http://localhost:5000/api
  app/              # Next.js App Router pages (file-system routing)
    globals.css     # CSS custom properties + global grid utility classes
    colors.tsx      # mankkooColors array and getColor(index) helper
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

## Component Guidelines

- `"use client"` directive at the top of every client component
- Chart components must use `next/dynamic` with `{ ssr: false }`:
  ```ts
  const LineChart = dynamic(() => import('@/components/charts/Line'), { ssr: false });
  ```
- Each chart type is a **separate reusable component** in `components/charts/` — accept typed props, never hardcode data
- Register only the Chart.js elements/plugins the specific chart needs (`ChartJS.register(...)`)
- Colors from `mankkooColors` array or `getColor(index)` in `app/colors.tsx`
- Reusable UI elements go in `components/elements/`

## HTTP & Data Fetching

All HTTP helpers in `hooks/useHttp.ts`:

| Helper | Usage |
|---|---|
| `useGetHttp<Type>(apiPath, enabled?)` | GET — returns `{ isFetching, fetchedData, setFetchedData, error }` |
| `postJson(apiPath, body, successMsg?, failureMsg?)` | POST with toast feedback |
| `patchJson(apiPath, body, successMsg?, failureMsg?)` | PATCH with toast feedback |
| `uploadFile(apiPath, file)` | multipart file upload |

Create domain-specific hooks (like `useInvestmentsData`, `useWallets`) to aggregate related API calls.

## Layout & Grid System

4-column CSS Grid defined in `app/globals.css`:

| Class | Effect |
|---|---|
| `.mainContainer` | 4-column grid wrapper |
| `.gridItem` | Standard grid cell with margin |
| `.span2Columns` | Span 2 of 4 columns |
| `.span3Columns` | Span 3 of 4 columns |
| `.span4Columns` | Full-width row |
| `.span2Rows` | Span 2 rows vertically |

Combine grid classes with page-scoped CSS Module classes (`.horizontalAlignment`, `.verticalAlignment`) for sub-layouts within cells.

## State Management

- React built-in only: `useState`, `useEffect`, `useMemo`, `useCallback`
- No external state management libraries

## TypeScript Rules

- Strict mode — do not weaken it
- `interface` for all component props
- API response shapes in `api/` as dedicated files (e.g., `api/AccountsPageResponses.ts`)
- Never `any` — use `unknown` + type narrowing

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Components | PascalCase | `Piechart.tsx`, `EditableTable.tsx` |
| Hooks | camelCase + `use` prefix | `useHttp.ts`, `useWallets.ts` |
| CSS Modules | match component name | `Piechart.module.css` |
| API type files | PascalCase + page description | `AccountsPageResponses.ts` |
| Utility files | PascalCase | `Formatter.ts` |
