## 1. Backend — Snapshot Views

- [ ] 1.1 Add view keys `investment-deposited-vs-value` and `investment-deposited-vs-value-per-wallet` as constants in `views.py`
- [ ] 1.2 Implement `__load_investment_deposited_vs_value()` SQL function — query investment+stocks streams (wealth filter), sum `totalValue` on `*Bought` events minus `*Sold`/`*Matured` events for deposited, latest event `balance` per stream for value, group by subtype
- [ ] 1.3 Implement `__investment_deposited_vs_value()` view update function calling the loader and `__store_view()`
- [ ] 1.4 Implement `__load_investment_deposited_vs_value_per_wallet()` SQL function — same logic but group by `labels->>'wallet'`
- [ ] 1.5 Implement `__investment_deposited_vs_value_per_wallet()` view update function
- [ ] 1.6 Add both snapshot view update calls to `update_views()`

## 2. Backend — Time-Series History Views

- [ ] 2.1 Add view keys `investment-deposited-vs-value-history` and `investment-deposited-vs-value-history-per-wallet` as constants in `views.py`
- [ ] 2.2 Implement `__load_investment_deposited_vs_value_history()` SQL function — derive distinct month-end dates from events, for each month compute cumulative deposited and carry-forward value per subtype, build result dict with `dates` array and `types` dict (each subtype + `total`)
- [ ] 2.3 Implement `__investment_deposited_vs_value_history()` view update function
- [ ] 2.4 Implement `__load_investment_deposited_vs_value_history_per_wallet()` SQL function — same as 2.2 but grouped by `labels->>'wallet'`, result uses `wallets` dict key
- [ ] 2.5 Implement `__investment_deposited_vs_value_history_per_wallet()` view update function
- [ ] 2.6 Add both history view update calls to `update_views()`

## 3. Backend — API Endpoints

- [ ] 3.1 Add `GET /api/investments/deposited-vs-value` endpoint in `investment_controller.py` — reads `investment-deposited-vs-value` view and returns JSON array
- [ ] 3.2 Add `GET /api/investments/deposited-vs-value/per-wallet` endpoint — reads `investment-deposited-vs-value-per-wallet` view
- [ ] 3.3 Add `GET /api/investments/deposited-vs-value/history` endpoint — reads `investment-deposited-vs-value-history` view
- [ ] 3.4 Add `GET /api/investments/deposited-vs-value/history/per-wallet` endpoint — reads `investment-deposited-vs-value-history-per-wallet` view
- [ ] 3.5 Define APIFlask output schemas for all four endpoints

## 4. Backend — Tests

- [ ] 4.1 Add tests for `investment-deposited-vs-value` view: ETF buy+sell, gold buy, treasury bonds buy — verify deposited and value correctness
- [ ] 4.2 Add test: stream excluded from wealth (`include_in_wealth = "false"`) is omitted from snapshot view
- [ ] 4.3 Add test: stream with no price update shows `value == deposited`
- [ ] 4.4 Add tests for `investment-deposited-vs-value-per-wallet` view: multiple wallets, multiple stream types per wallet
- [ ] 4.5 Add tests for `investment-deposited-vs-value-history` view: verify deposited carry-forward (step function), value carry-forward, total aggregate
- [ ] 4.6 Add tests for `investment-deposited-vs-value-history-per-wallet` view
- [ ] 4.7 Add tests for all four API endpoints (integration tests via controller test pattern)
- [ ] 4.8 Run backend tests: `uv run pytest -s -vv`
- [ ] 4.9 Run backend linter: `uv run autoflake ... && uv run isort . && uv run autopep8 ... && uv run black .`

## 5. Frontend — API Types and Data Hook

- [ ] 5.1 Add TypeScript interfaces for all four endpoint responses in `api/InvestmentsPageResponses.ts` (`DepositedVsValueItem`, `DepositedVsValuePerWalletItem`, `DepositedVsValueHistory`, `DepositedVsValueHistoryPerWallet`)
- [ ] 5.2 Add four `useGetHttp` calls in `useInvestmentsData.ts` for the new endpoints, returning isFetching flags and data

## 6. Frontend — Chart Components

- [ ] 6.1 Create `components/charts/DepositedVsValueLineChart.tsx` — dual-line Chart.js line chart; props: `dates`, `series` (record of type/wallet name to `{deposited, value}` arrays); toggle buttons per series; deposited lines dashed, value lines solid; uses `mankkooColors`; registered with `next/dynamic ssr:false`
- [ ] 6.2 Create `components/charts/DepositedVsValueLineChart.module.css` — toggle button styles
- [ ] 6.3 Create `components/charts/DepositedVsValueBarChart.tsx` — grouped bar chart; props: items array of `{label, deposited, value}`; two bars per group (deposited, value); uses `mankkooColors`; registered with `next/dynamic ssr:false`

## 7. Frontend — Investments Page Wiring

- [ ] 7.1 Wire the existing "Investments History" `<LineChart />` placeholder (full-width section, line 294-297 in `page.tsx`) to `DepositedVsValueLineChart` using by-type history data from `useInvestmentsData`
- [ ] 7.2 Add a new "Results by Type" grid section below the existing diversification row using `DepositedVsValueBarChart` with snapshot-by-type data
- [ ] 7.3 Wire the per-wallet "History" `<LineChart />` placeholder (inside `renderTabContent`, line 219-221) to `DepositedVsValueLineChart` using by-wallet history data filtered to the selected wallet
- [ ] 7.4 Add a per-wallet "Results" section inside `renderTabContent` using `DepositedVsValueBarChart` with snapshot-per-wallet data filtered to the selected wallet

## 8. Frontend — Verification

- [ ] 8.1 Run `npm run build` and confirm no TypeScript errors
