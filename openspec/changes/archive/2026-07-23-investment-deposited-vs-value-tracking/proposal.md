## Why

Currently the investment dashboard only shows the current market value of each investment stream — there is no way to see how much money was actually put in (cost basis) versus what it is worth today. This makes it impossible to assess real performance at a glance or over time.

## What Changes

- **Five new materialized views** are added to the backend to track deposited amount vs current value across investment and stocks streams:
  - `investment-deposited-vs-value` — current snapshot grouped by investment subtype
  - `investment-deposited-vs-value-per-wallet` — current snapshot grouped by wallet label
  - `investment-deposited-vs-value-history` — monthly time series per investment type (subtype) + total
  - `investment-deposited-vs-value-history-per-wallet` — monthly time series per wallet label + total
  - `investment-deposited-vs-value-history-by-type-per-wallet` — monthly time series per investment type within each wallet + per-wallet total
- **Five new API endpoints** expose the above views
- **One new chart component** is added to the frontend:
  - `DepositedVsValueLineChart` — a dual-line Chart.js line chart with optional toggle buttons per series (deposited dashed, value solid), optional y-axis hiding, optional toggle hiding, configurable height; supports zoom/pan via `chartjs-plugin-zoom`
- **Current snapshot** (deposited vs value, Gain, Gain %) is presented as **tables** (not bar charts) — one by investment type, one by wallet — placed side-by-side on the investments page
- **The investments page** is updated:
  - "Investments History" section wired to `DepositedVsValueLineChart` with per-type toggles
  - "Results by Type" and "Results by Wallet" snapshot tables added
  - Per-wallet "History" chart shows per-investment-type series within the selected wallet
  - Two indicator tiles now show all-time gain and year-to-year gain computed from history data
- **The main dashboard page** investments chart is replaced with `DepositedVsValueLineChart` showing the total deposited vs value (toggle and y-axis numbers hidden)

## Capabilities

### New Capabilities

- `investment-performance-tracking`: Tracking deposited (cost basis) vs current market value for investment streams, both as time-series history and current snapshots, grouped by investment type, wallet label, and investment type within wallet.

### Modified Capabilities

- `investment-tracking`: New views and API endpoints extend the investment tracking capability with performance/return data.

## Impact

- **Backend**: `views.py` gains 5 new view keys and functions; `investment_controller.py` gains 5 new GET endpoints; `update_views()` is extended.
- **Frontend**: new `DepositedVsValueLineChart` component in `components/charts/`; `useInvestmentsData` hook extended with 5 new fetches; `app/investments/page.tsx` and `app/page.tsx` updated.
- **No event schema changes** — all data is computed from existing `totalValue` (buy/sell events) and `balance` (latest event per stream) fields already present in the event store.
- **No breaking changes** — purely additive.
