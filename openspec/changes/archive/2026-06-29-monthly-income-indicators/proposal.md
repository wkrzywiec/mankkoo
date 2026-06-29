## Why

The main dashboard has a "Last Month Income" indicator tile and a monthly income history chart section, both currently showing "no data". Income — defined as the change in total wealth (balance on last day minus balance on first day of a month) across all wealth-included streams — is a key personal finance signal that is not yet computed or surfaced.

## What Changes

- Add a new `monthly-income` pre-computed view that stores per-month income history as a date/total series
- Wire the `lastMonthIncome` field in the existing `main-indicators` view (currently stored as `null`) with the most recent complete month's income value
- Expose the monthly income history via the existing (stub) `/api/main/monthly-profits` endpoint, renamed to use the `monthly-income` view key
- Fix a field name mismatch: rename `lastMonthProfit` → `lastMonthIncome` in the frontend TypeScript interface
- Wire the "Last Month Income" indicator on the main page to display real data
- Feed the existing placeholder bar chart on the main page with monthly income history

## Capabilities

### New Capabilities

- `monthly-income`: Pre-computed monthly income view — income per calendar month computed as (last-day balance − first-day balance) summed across all wealth-included streams. Includes history for all complete months and powers both the KPI indicator and history chart.

### Modified Capabilities

- `net-worth-dashboard`: The `main-indicators` view gains a computed `lastMonthIncome` value (was always `null`). A new `monthly-income` view is added to the view update pipeline. The existing stub `/api/main/monthly-profits` endpoint is wired to serve real data.

## Impact

- **Backend**: `services/mankkoo/mankkoo/views.py` — new `__monthly_income()` function, updated `__main_indicators()`, updated `update_views()`
- **Backend**: `services/mankkoo/mankkoo/controller/main_controller.py` — wire `monthly_profits()` endpoint to the new view
- **Frontend**: `services/mankkoo-ui/api/MainPageResponses.ts` — rename field, add new interface
- **Frontend**: `services/mankkoo-ui/app/page.tsx` — wire indicator and bar chart to real data
- **No event schema changes** — income is derived from existing `balance` field in event data
- **No new DB tables** — the new view is stored in the existing `views` table
