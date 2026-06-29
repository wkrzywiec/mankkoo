## 1. Backend — Monthly Income View

- [x] 1.1 In `services/mankkoo/mankkoo/views.py`, add the `monthly_income_key = "monthly-income"` constant alongside existing view key constants
- [x] 1.2 In `views.py`, implement `__load_monthly_income()` — SQL query that generates a month series from earliest event to last complete month, cross-joins with wealth-included streams, fetches first-day and last-day balances using the correlated subquery pattern, and returns `{"date": ["YYYY-MM", ...], "total": [float, ...]}` ordered ascending
- [x] 1.3 In `views.py`, implement `__monthly_income()` — calls `__load_monthly_income()` and stores the result via `__store_view(monthly_income_key, view_content)`
- [x] 1.4 In `views.py`, update `__main_indicators()` to compute `lastMonthIncome` by calling `__load_monthly_income()` and taking the income value from the last entry (most recent complete month); keep `null` if no data
- [x] 1.5 In `views.py`, add `__monthly_income()` call inside `update_views()` alongside the existing view update calls

## 2. Backend — API Endpoint

- [x] 2.1 In `services/mankkoo/mankkoo/controller/main_controller.py`, replace the commented-out body of `monthly_profits()` with `return views.load_view(views.monthly_income_key)`

## 3. Backend — Tests

- [x] 3.1 In `services/mankkoo/tests/views_test.py`, add a test for `__monthly_income`: given events across two complete months, assert the view contains two entries with correct income values (last-day minus first-day balance, summed across streams)
- [x] 3.2 Add a test for the zero-income edge case: a month with no events for a stream contributes 0 to that month's income
- [x] 3.3 Add a test for negative income: a month where total wealth decreases produces a negative income value
- [x] 3.4 Add a test verifying `lastMonthIncome` in `main-indicators` equals the most recent complete month's income value
- [x] 3.5 Add a test verifying streams with `include_in_wealth = "false"` are excluded from monthly income
- [x] 3.6 Run `uv run pytest -s -vv tests/views_test.py` and confirm all tests pass

## 4. Backend — Lint

- [x] 4.1 Run the lint sequence in `services/mankkoo/`: `uv run autoflake ...` → `uv run isort .` → `uv run autopep8 ...` → `uv run black .` and resolve any issues

## 5. Frontend — Type Fixes

- [x] 5.1 In `services/mankkoo-ui/api/MainPageResponses.ts`, rename `lastMonthProfit` → `lastMonthIncome` in the `MainIndicatorsResponse` interface
- [x] 5.2 In `MainPageResponses.ts`, add a new `MonthlyIncome` interface: `{ date: string[]; total: number[] }`

## 6. Frontend — Wire Indicator and Chart

- [x] 6.1 In `services/mankkoo-ui/app/page.tsx`, add `useGetHttp<MonthlyIncome>('/main/monthly-profits')` to fetch monthly income history
- [x] 6.2 In `page.tsx`, wire the "Last Month Income" `Indicator` tile to display `currencyFormat(indicators?.lastMonthIncome)` with a loading state (pass `isFetching={isFetchingMainIndicators}`)
- [x] 6.3 In `page.tsx`, replace the empty placeholder `<BarChart />` in the "Income per each month" section with `<BarChart x={monthlyIncome?.date} y={monthlyIncome?.total} />` (or equivalent props matching the `BarChart` component's API), guarded with a `Loader` while fetching

## 7. Frontend — Build Verification

- [x] 7.1 Run `npm run build` in `services/mankkoo-ui/` and confirm no TypeScript errors or build failures
