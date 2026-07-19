## Context

The investment dashboard currently tracks and displays the **current market value** of each investment stream (`balance` field on the latest event). There is no distinction between money the user physically deposited (cost basis) and value that came from market appreciation. This makes it impossible to answer "how much have I actually earned?"

The event store already contains everything needed:
- `*Bought` events carry `totalValue` = cash spent at purchase time
- `*Sold` / `*Matured` events carry `totalValue` = cash received at sale time  
- Every event carries `balance` = running market value at that point in time

No event schema changes are required — it is purely a view and API layer addition.

Current investment page has two empty `<LineChart />` placeholders (no data wired up) and a "Investments History" section header. These will be filled in by this change.

## Goals / Non-Goals

**Goals:**
- Track and display **deposited amount** (cost basis) vs **current market value** for each investment/stocks stream
- Show this as a **monthly time-series** (line chart, dual lines: deposited + value) filterable by investment type (subtype) or wallet
- Show this as a **current snapshot** (grouped bar chart) by investment type and by wallet
- Respect `include_in_wealth` label filter (same as existing wealth views)
- Wire up the existing empty line chart placeholders on the investments page
- Savings accounts are excluded from scope (investment/stocks streams only)

**Non-Goals:**
- Per-stream (individual investment) deposited vs value history
- Real-time or sub-monthly granularity
- Inflation-adjusted returns
- IRR / CAGR calculations
- Modifying existing event types or event data structures

## Decisions

### Decision 1: Compute from existing events (no schema changes)

**Choice:** Derive "deposited" by summing `totalValue` on buy events and subtracting on sell/matured events. Derive "value" from the `balance` field of the latest event up to a given point in time.

**Rationale:** The data is already there. Adding a separate `depositedAmount` field to buy events would require updating event creation code and would leave all historical events without that field. Computing from existing fields is backward-compatible and requires no migration.

**Pattern for deposited:**
```sql
SUM(totalValue) WHERE event_type LIKE '%Bought'
MINUS SUM(totalValue) WHERE event_type LIKE '%Sold' OR event_type LIKE '%Matured'
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

### Decision 3: Four separate views (not one combined view)

**Choice:** Four views — two time-series (by type, by wallet) and two snapshots (by type, by wallet).

**Alternatives considered:**
- One mega-view with all dimensions: harder to read in the API, larger JSONB blob
- Compute snapshot from time-series (last data point): adds API-layer complexity for what is a simple query

**Rationale:** Follows the existing pattern in `views.py` — each view has a single, narrow responsibility. Snapshot views are simple queries (latest version JOIN) while time-series views are heavier (date series JOIN). Keeping them separate makes each independently readable and replaceable.

---

### Decision 4: View data shape

**Time-series views** (shared date axis, parallel arrays per type/wallet):
```json
{
  "dates": ["2022-01", "2022-03", "2022-06"],
  "types": {
    "ETF":            { "deposited": [10000, 10000, 15000], "value": [10000, 10400, 16200] },
    "gold":           { "deposited": [5000, 5000, 5000],   "value": [5000, 5300, 6100]  },
    "treasury_bonds": { "deposited": [0, 20000, 20000],    "value": [0, 20000, 20800]   },
    "total":          { "deposited": [15000, 35000, 40000], "value": [15000, 35700, 43100] }
  }
}
```

The `total` key is a synthetic aggregate across all types/wallets.

**Snapshot views** (simple list):
```json
[
  { "type": "ETF",            "deposited": 15000, "value": 16200 },
  { "type": "Gold",           "deposited": 5000,  "value": 6100  },
  { "type": "Treasury Bonds", "deposited": 20000, "value": 20800 }
]
```

---

### Decision 5: Frontend — toggleable line chart

**Choice:** A single `DepositedVsValueLineChart` component with toggle buttons (one per type or wallet). Each toggle shows/hides that type's deposited and value lines as a pair. An "All" toggle shows the total aggregate lines.

**Chart.js implementation:** Dataset visibility is toggled via `chart.getDatasetMeta(i).hidden`. Colors: each type gets a distinct color from `mankkooColors`; deposited line uses a dashed style, value line uses solid. This visually distinguishes cost basis from market value across all types simultaneously.

---

### Decision 6: New API endpoints under `/api/investments`

Four new GET endpoints added to `investment_controller.py`:
- `GET /api/investments/deposited-vs-value/history` → time-series by type
- `GET /api/investments/deposited-vs-value/history/per-wallet` → time-series by wallet
- `GET /api/investments/deposited-vs-value` → snapshot by type
- `GET /api/investments/deposited-vs-value/per-wallet` → snapshot by wallet

## Risks / Trade-offs

**[Risk] Time-series view is heavier to compute than existing snapshot views** → Mitigation: monthly granularity (event-driven dates) keeps the result set small. The existing `total-history-per-day` view already runs a heavier per-day computation; monthly is lighter.

**[Risk] `%Bought` / `%Sold` / `%Matured` pattern matching on event type names could miss future event types** → Mitigation: document the naming convention in `views.py`; any new investment event types must follow the `*Bought` / `*Sold` / `*Matured` / `*Priced` naming pattern.

**[Risk] The `total` aggregate in the time-series view may have gaps per type (not all types have events every month)** → Mitigation: carry-forward logic in SQL (use `LAST_VALUE` or lag-fill per stream before aggregating) ensures the deposited line is a proper step function and the value line shows the most recent known value even in months with no new events.

## Migration Plan

Purely additive — no existing data, endpoints, or views are modified. Deploy backend first (new views computed on next event or manual trigger), then deploy frontend. Rollback: remove new endpoints and view keys; existing views are unaffected.

## Open Questions

- None — all decisions made during exploration.
