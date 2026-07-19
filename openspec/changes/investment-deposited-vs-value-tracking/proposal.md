## Why

Currently the investment dashboard only shows the current market value of each investment stream — there is no way to see how much money was actually put in (cost basis) versus what it is worth today. This makes it impossible to assess real performance at a glance or over time.

## What Changes

- **Four new materialized views** are added to the backend to track deposited amount vs current value across investment and stocks streams:
  - `investment-deposited-vs-value-history` — monthly time series per investment type (subtype) + total
  - `investment-deposited-vs-value-history-per-wallet` — monthly time series per wallet label + total
  - `investment-deposited-vs-value` — current snapshot grouped by investment subtype
  - `investment-deposited-vs-value-per-wallet` — current snapshot grouped by wallet label
- **Four new API endpoints** expose the above views
- **Two new chart components** are added to the frontend:
  - A toggleable dual-line chart (deposited vs value over time, filterable by investment type or wallet)
  - A grouped bar chart (deposited vs value, current snapshot by type or wallet)
- **The investments page** is updated to wire up existing empty `<LineChart />` placeholders and add grouped bar chart sections

## Capabilities

### New Capabilities

- `investment-performance-tracking`: Tracking deposited (cost basis) vs current market value for investment streams, both as time-series history and current snapshots, grouped by investment type and wallet label.

### Modified Capabilities

- `investment-tracking`: New views and API endpoints extend the investment tracking capability with performance/return data.

## Impact

- **Backend**: `views.py` gains 4 new view functions and keys; `investment_controller.py` gains 4 new GET endpoints; `update_views()` is extended.
- **Frontend**: new chart components in `components/charts/`; `useInvestmentsData` hook extended; `app/investments/page.tsx` updated.
- **No event schema changes** — all data is computed from existing `totalValue` (buy/sell events) and `balance` (latest event per stream) fields already present in the event store.
- **No breaking changes** — purely additive.
