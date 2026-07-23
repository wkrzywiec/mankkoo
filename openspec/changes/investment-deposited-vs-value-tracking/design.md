## Context

The investment dashboard currently tracks and displays the **current market value** of each investment stream (`balance` field on the latest event). There is no distinction between money the user physically deposited (cost basis) and value that came from market appreciation. This makes it impossible to answer "how much have I actually earned?"

The event store already contains everything needed:
- `*Bought` events carry `totalValue` = cash spent at purchase time (positive number)
- `*Sold` / `*Matured` events carry `totalValue` = cash received at sale time (**stored as a negative number** in the test helpers and real event data)
- Every event carries `balance` = running market value at that point in time

No event schema changes are required — it is purely a view and API layer addition.

Current investment page has two empty `<LineChart />` placeholders (no data wired up) and a "Investments History" section header. These will be filled in by this change.

## Goals / Non-Goals

**Goals:**
- Track and display **deposited amount** (cost basis) vs **current market value** for each investment/stocks stream
- Show time-series history (line chart, dual lines: deposited + value) filterable by investment type, by wallet, or by investment type within wallet
- Show current snapshot as tables (with Gain and Gain % columns) by investment type and by wallet
- Respect `include_in_wealth` label filter (same as existing wealth views)
- Wire up the existing empty line chart placeholders on the investments page
- Add all-time gain and year-to-year gain indicators to the investments page
- Update main dashboard investments chart to show total deposited vs value over time
- Savings accounts are excluded from scope (investment/stocks streams only)

**Non-Goals:**
- Per-stream (individual investment) deposited vs value history
- Real-time or sub-monthly granularity
- Inflation-adjusted returns
- IRR / CAGR calculations
- Modifying existing event types or event data structures

## Decisions

### Decision 1: Compute deposited from existing events (no schema changes)

**Choice:** Derive "deposited" by summing `totalValue` across all `*Bought`, `*Sold`, and `*Matured` events. Because `*Sold`/`*Matured` events store `totalValue` as a **negative number**, a simple `SUM` across all three event types yields the correct net deposited amount. Derive "value" from the `balance` field of the latest event up to a given point in time.

**Rationale:** The data is already there. `*Sold`/`*Matured` events already carry their sign — no need to subtract. Using a single `SUM` is simpler and less error-prone than a buy-minus-sell expression.

**Pattern for deposited (SQL):**
```sql
SUM((e.data->>'totalValue')::numeric)
WHERE e.type LIKE '%Bought' OR e.type LIKE '%Sold' OR e.type LIKE '%Matured'
```

**Pattern for value at a point in time (per stream):**
```sql
DISTINCT ON (stream_id) balance ORDER BY stream_id, version DESC
WHERE occured_at <= <cutoff_date>
```

**Edge case:** If a stream has no price update yet, `balance` from the latest buy event equals the cost basis — so deposited and value are equal until a price update occurs. No special casing needed.

---

### Decision 2: Monthly granularity using event-driven dates (approach 1)

**Choice:** Emit one data point per distinct month-end where any event occurred across all relevant streams (not a dense generated date series).

**Rationale:** Avoids expensive `generate_series` over years of calendar months. Personal finance data has sparse updates — most months will have at least one event, but generating a full calendar series is wasteful. The frontend chart library handles sparse date arrays fine.

**Month-end cutoff:** The last calendar day of each month where at least one event exists. SQL: `date_trunc('month', occured_at) + interval '1 month - 1 day'`.

---

### Decision 3: Five separate views (not one combined view)

**Choice:** Five views — two snapshots (by type, by wallet) and three time-series (by type, by wallet, by type-within-wallet).

**Alternatives considered:**
- One mega-view with all dimensions: harder to read in the API, larger JSONB blob
- Compute snapshot from time-series (last data point): adds API-layer complexity for what is a simple query

**Rationale:** Follows the existing pattern in `views.py` — each view has a single, narrow responsibility. The fifth view (`by-type-per-wallet`) is needed for the per-wallet history chart to show individual investment type series within a wallet, which neither the by-type nor by-wallet views can serve alone.

---

### Decision 4: View data shapes

**Snapshot views** (simple list):
```json
[
  { "type": "ETF",            "deposited": 15000, "value": 16200 },
  { "type": "Gold",           "deposited": 5000,  "value": 6100  },
  { "type": "Treasury Bonds", "deposited": 20000, "value": 20800 }
]
```

**Time-series by type** (shared date axis, parallel arrays per subtype + total):
```json
{
  "dates": ["2022-01", "2022-03", "2022-06"],
  "types": {
    "ETF":   { "deposited": [10000, 10000, 15000], "value": [10000, 10400, 16200] },
    "Gold":  { "deposited": [5000, 5000, 5000],   "value": [5000, 5300, 6100]  },
    "total": { "deposited": [15000, 15000, 20000], "value": [15000, 15700, 22300] }
  }
}
```

**Time-series by wallet** (same structure, `wallets` key instead of `types`):
```json
{
  "dates": ["2022-01", "2022-03"],
  "wallets": {
    "IKE":   { "deposited": [...], "value": [...] },
    "total": { "deposited": [...], "value": [...] }
  }
}
```

**Time-series by type within wallet** (nested — wallets → types → series):
```json
{
  "dates": ["2022-01", "2022-03"],
  "wallets": {
    "IKE": {
      "ETF":   { "deposited": [...], "value": [...] },
      "total": { "deposited": [...], "value": [...] }
    },
    "Personal": {
      "Gold":  { "deposited": [...], "value": [...] },
      "total": { "deposited": [...], "value": [...] }
    }
  }
}
```

---

### Decision 5: Frontend — snapshot as table, not bar chart

**Choice:** Current snapshot (deposited vs value) is presented as a plain table with columns: Label | Deposited | Current Value | Gain | Gain %, with a bold Total row. Two tables side-by-side: one by investment type, one by wallet.

**Rationale:** Tables are more precise for financial data. The user wants to read exact numbers and percentages, not compare bar heights. A grouped bar chart was the original plan but was superseded during implementation review.

**Gain %** is computed as `(value − deposited) / deposited × 100`. Shows `"—"` when deposited is zero.

---

### Decision 6: Frontend — toggleable line chart with optional props

**Choice:** `DepositedVsValueLineChart` is a single reusable component with props:
- `dates: string[]` — shared x-axis labels (YYYY-MM)
- `series: Record<string, { deposited: number[]; value: number[] }>` — one entry per toggle
- `hideYAxis?: boolean` — hides y-axis tick numbers (default false)
- `hideToggle?: boolean` — hides the toggle button row (default false)
- `height?: string` — chart container height (default "320px")

Toggle buttons show/hide both deposited and value lines for a series as a pair. Deposited lines are dashed, value lines are solid. Registers `chartjs-plugin-zoom` (Ctrl+wheel, pinch on x-axis) and `chartjs-plugin-datalabels` (hidden).

---

### Decision 7: New API endpoints under `/api/investments`

Five new GET endpoints added to `investment_controller.py`:
- `GET /api/investments/deposited-vs-value` → snapshot by type
- `GET /api/investments/deposited-vs-value/per-wallet` → snapshot by wallet
- `GET /api/investments/deposited-vs-value/history` → time-series by type
- `GET /api/investments/deposited-vs-value/history/per-wallet` → time-series by wallet
- `GET /api/investments/deposited-vs-value/history/by-type-per-wallet` → time-series by type within wallet

---

### Decision 8: Derived indicators on frontend (no new backend views)

All-time gain and year-to-year gain indicators on the investments page are computed from the `investment-deposited-vs-value-history` view already fetched on the page — no additional API calls.

- **All-time gain**: `(total.value[last] − total.deposited[last])` and `/ total.deposited[last]`. Shows how much the portfolio has earned above total deposited capital.

- **Year-to-year gain** (market performance only, deposits excluded):
  ```
  targetLabel  = same month, prior year (e.g. "2025-07" for "2026-07")
  newDeposits  = total.deposited[last] − total.deposited[targetIdx]
  gainAmt      = (total.value[last] − total.value[targetIdx]) − newDeposits
  gainPct      = gainAmt / total.value[targetIdx] × 100
  ```
  Subtracting `newDeposits` removes capital injections from the result so only market appreciation/depreciation is shown. Returns `null` (displays "no data") if the target month is not present in the dates array (i.e. no investment events occurred exactly 12 months ago).

## Risks / Trade-offs

**[Risk] Time-series views are heavier to compute than snapshot views** → Mitigation: monthly granularity (event-driven dates) keeps the result set small. The existing `total-history-per-day` view already runs a heavier per-day computation; monthly is lighter.

**[Risk] `%Bought` / `%Sold` / `%Matured` pattern matching on event type names could miss future event types** → Mitigation: document the naming convention in `views.py`; any new investment event types must follow the `*Bought` / `*Sold` / `*Matured` / `*Priced` naming pattern (see `investment-tracking` spec).

**[Risk] The `total` aggregate in the time-series view may have gaps per type (not all types have events every month)** → Mitigation: carry-forward logic in Python post-processing ensures the deposited line is a proper step function and the value line shows the most recent known value even in months with no new events.

**[Risk] `*Sold`/`*Matured` totalValue sign convention** → The deposited formula relies on sell/maturity events storing `totalValue` as a negative number. This is established by the existing event helpers and real event data. Any future importer or event creator must follow the same sign convention.

## Migration Plan

Purely additive — no existing data, endpoints, or views are modified. Deploy backend first (new views computed on next event or manual trigger), then deploy frontend. Rollback: remove new endpoints and view keys; existing views are unaffected.

## Open Questions

- None — all decisions made during exploration and implementation.
