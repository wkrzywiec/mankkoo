## Context

The main dashboard (`app/page.tsx`) already has four KPI indicator tiles. Three show "no data": Net Worth, Last Month Income, and Last Month Spendings. The "Savings" indicator is the only one wired to real data via the `main-indicators` view.

The `main-indicators` view already stores `lastMonthIncome: null` as a placeholder — the field exists in both the backend schema and the API controller, but is never computed.

The dashboard History section also has a placeholder bar chart slot with the label "Income per each month" — it is rendered with no data. The backend has a stub endpoint `/api/main/monthly-profits` with an empty implementation.

The existing `total-history-per-day` view computes daily total wealth across all `include_in_wealth` streams using a correlated subquery pattern: for each stream × day, fetch the latest event balance on or before that day. Monthly income is a natural derivation of this same pattern applied at month boundaries.

**Key field name mismatch to fix**: the frontend TypeScript interface uses `lastMonthProfit` but the backend stores `lastMonthIncome`. This mismatch means the indicator would silently show nothing even if the backend computed a value.

## Goals / Non-Goals

**Goals:**
- Compute `lastMonthIncome` (most recent complete month's income) and store it in `main-indicators`
- Add a new `monthly-income` view with full per-month income history
- Wire the "Last Month Income" indicator tile to display real data
- Wire the existing placeholder bar chart to display monthly income history
- Fix the `lastMonthProfit` → `lastMonthIncome` field name mismatch throughout

**Non-Goals:**
- Computing `lastMonthSpending` or `netWorth` (other null indicators — separate work)
- Year-over-year comparison charts
- Current (partial) month income
- Per-account income breakdown

## Decisions

### Decision 1: Query events directly rather than deriving from `total-history-per-day`

**Choice**: Write a fresh SQL query against the `events` table directly, mirroring the pattern from `__load_total_history_per_day`.

**Rationale**: The `total-history-per-day` view is stored as a JSONB blob `{"date": [...], "total": [...]}`. Querying inside JSONB arrays in PostgreSQL to extract first/last values per month is awkward and fragile. Writing SQL against `events` directly is consistent with every other view function, is independently correct, and produces a clean month-granularity result without loading large intermediate data.

**Alternative considered**: Derive from `total-history-per-day` in Python after loading the view. Rejected: would require loading potentially thousands of daily rows into Python memory just to compute a monthly aggregate, and creates an ordering dependency between views.

### Decision 2: Income = last-day-of-month balance − first-day-of-month balance, summed across all wealth-included streams

**Choice**: For each month, for each wealth-included stream, fetch the balance from the latest event on or before the last day of the month, and the balance from the latest event on or before the first day of the month. Sum the deltas across all streams.

**Rationale**: This definition is consistent with the `include_in_wealth` filter used across all other wealth views. It naturally handles sparse event streams (streams with no activity in a month inherit the last known balance, so their delta is 0 — correct). It matches the user's stated definition.

**Edge case**: If a stream has no events before a given month's first day, its balance is 0 on that day (via `COALESCE(..., 0)`). This is consistent with `total-history-per-day`.

### Decision 3: Monthly income view key is `monthly-income`; endpoint path stays `/api/main/monthly-profits`

**Choice**: Store the new view under the key `monthly-income` in the `views` table. Keep the existing endpoint path `/api/main/monthly-profits` (it was never shipped, but renaming the URL would require no migration since nothing uses it).

**Rationale**: The view key `monthly-income` is semantically precise. The endpoint path `/monthly-profits` is already defined in the controller stub — changing it would be an unnecessary rename of something unused.

### Decision 4: Monthly history shape matches `total-history-per-day`

**Choice**: The `monthly-income` view stores `{"date": ["2024-01", "2024-02", ...], "total": [1200.0, -300.0, ...]}` — same parallel-list structure as `total-history-per-day`, but with month strings (`YYYY-MM`) instead of day strings.

**Rationale**: Consistent with the existing view pattern. The frontend can consume it with the same chart binding approach used for the total history line chart.

### Decision 5: `lastMonthIncome` is the last row in the monthly income query (most recent complete month)

**Choice**: Run the monthly income query ordered by month descending, take the first row's income value, and store it in `main-indicators.lastMonthIncome`.

**Rationale**: Avoids a second separate query. The monthly income query already produces the data needed; the KPI is just the most recent value from it.

### Decision 6: Bar chart for monthly income history (not line chart)

**Choice**: Use the existing `BarChart` component in the placeholder slot at `page.tsx` lines 155–165.

**Rationale**: Monthly income is a discrete per-period delta (can be positive or negative). Bar charts communicate this better than line charts — negative months appear as bars below the axis. A line chart implies continuous movement, which is less meaningful for period deltas.

## API Shape

### Existing endpoint (wired):
```
GET /api/main/indicators
Response:
{
  "savings": 45000.0,
  "netWorth": null,
  "lastMonthIncome": 1200.0,   ← was always null, now computed
  "lastMonthSpending": null
}
```

### Existing stub endpoint (now implemented):
```
GET /api/main/monthly-profits
Response:
{
  "date":  ["2024-01", "2024-02", "2024-03"],
  "total": [1200.0,   -300.0,    800.0]
}
```
Dates are in `YYYY-MM` format, ordered ascending. Only complete months are included (current in-progress month is excluded). Returns `null` if no view data exists.

## View: `monthly-income`

New entry in the `views` table. Shape:
```json
{
  "date":  ["2024-01", "2024-02", ...],
  "total": [1200.0,   -300.0, ...]
}
```

Computed by `__monthly_income()` in `views.py`. Added to `update_views()` call sequence.

## SQL Approach

Uses the same correlated subquery pattern as `__load_total_history_per_day`:

1. Generate a month series from the earliest event date to the last complete month (`date_trunc('month', now()) - interval '1 month'`).
2. Cross join with all wealth-included stream IDs.
3. For each stream × month pair, fetch `balance` from the latest event on or before the first day of the month.
4. For each stream × month pair, fetch `balance` from the latest event on or before the last day of the month.
5. Compute `income = last_day_balance − first_day_balance` per stream, sum across streams, group by month.

## Risks / Trade-offs

**[Performance — correlated subqueries at month granularity]** → The query uses the same pattern as `total-history-per-day` (stream × period correlated subqueries). Monthly has far fewer rows than daily so performance should be better. If it proves slow, an index on `(stream_id, occured_at, version)` would help — the same index that benefits the daily view. Mitigation: acceptable for now; monitor if event volume grows.

**[Edge case — no events at all]** → If the `events` table is empty, `MIN(occured_at)` returns NULL, and `generate_series` with a NULL start produces no rows. The view stores `{"date": [], "total": []}` and `lastMonthIncome` stays `null`. Frontend must handle null/empty gracefully. Mitigation: already handled by `COALESCE` and null checks on the frontend.

**[Field name fix is a silent breaking change]** → Renaming `lastMonthProfit` → `lastMonthIncome` in the TypeScript interface is technically a breaking change if any other component referenced the old field name. Currently only `page.tsx` uses the `MainIndicatorsResponse` type, and it does not read `lastMonthProfit` (the income indicator shows "no data" unconditionally). Mitigation: grep for `lastMonthProfit` in the frontend codebase before applying to confirm no other references.

## Migration Plan

No database migration required. The new `monthly-income` view is inserted into the `views` table on the next `update_views()` call after deployment — same pattern as all other views. On first startup or after the next event import, all views including the new one will be computed.

Rollback: remove the `__monthly_income()` call from `update_views()` and revert frontend changes. The `views` table row for `monthly-income` can be left or deleted with `DELETE FROM views WHERE name = 'monthly-income'`.

## Open Questions

- None. All design decisions are resolved.
