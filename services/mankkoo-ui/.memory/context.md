# Frontend — Context

## Why It Exists

The frontend is the primary user interface for Mankkoo. It translates raw event-sourced financial data (served by the backend) into a visual dashboard the user can understand at a glance.

## Problems It Solves

- **Data visibility**: transforms backend API responses into charts, KPI cards, and tables
- **Import UX**: provides a simple file-upload flow for bank CSVs
- **Portfolio overview**: shows net worth breakdown across accounts, investments, stocks, and retirement

## How It Works

1. Pages fetch data using `useGetHttp<Type>(apiPath)` hook (wraps Axios)
2. Data flows into Chart.js components (bar, line, pie) or table components
3. For file uploads, `uploadFile(apiPath, file)` is used
4. Mutations use `postJson` / `patchJson` with optional success/failure toast messages (SweetAlert2)

## User Experience Goals

- Dashboard-first: the home page shows the most important financial indicators immediately
- Consistent PLN formatting everywhere via `currencyFormat()`
- Responsive 4-column grid layout — content fills the screen usefully
- Dark-ish color scheme with accent colors from `app/colors.tsx` (`mankkooColors`, `getColor(index)`)
- Minimal page transitions — the user should feel in control, not waiting
