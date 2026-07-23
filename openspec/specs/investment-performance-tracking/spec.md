# Spec: Investment Performance Tracking

## Purpose

Defines how the system tracks and exposes deposited amount (cost basis) versus current market value for investment and stocks streams, both as point-in-time snapshots and as time-series history, grouped by investment subtype and by wallet.

---

## Requirements

### Requirement: Deposited vs Value Snapshot by Investment Type

The system SHALL maintain a pre-computed view of the current deposited amount (cost basis) and current market value for each investment subtype across all active `investment` and `stocks` streams that are included in wealth.

Deposited amount is computed as: sum of `totalValue` from all `*Bought` events minus sum of `totalValue` from all `*Sold` and `*Matured` events for each stream.

Current value is the `balance` field from the latest event (by version) for each stream.

Only streams where `labels["include_in_wealth"]` is `null` or `"true"` are included.

#### Scenario: Snapshot reflects current deposited and value per type
- **WHEN** an `investment-deposited-vs-value` view is requested
- **THEN** the system returns a list of entries, one per subtype, each containing `type`, `deposited`, and `value`

#### Scenario: Streams excluded from wealth are omitted
- **WHEN** a stream has `labels["include_in_wealth"] = "false"`
- **THEN** that stream's events are excluded from the deposited and value totals

#### Scenario: Stream with no price update shows value equal to deposited
- **WHEN** a stream has only buy events and no price update events
- **THEN** `value` equals `deposited` for that stream's contribution

---

### Requirement: Deposited vs Value Snapshot by Wallet

The system SHALL maintain a pre-computed view of the current deposited amount and current market value grouped by `labels["wallet"]` label across all active `investment` and `stocks` streams included in wealth.

#### Scenario: Snapshot reflects current deposited and value per wallet
- **WHEN** an `investment-deposited-vs-value-per-wallet` view is requested
- **THEN** the system returns a list of entries, one per wallet, each containing `wallet`, `deposited`, and `value`

#### Scenario: Multiple stream types in the same wallet are aggregated
- **WHEN** a wallet contains both `investment` and `stocks` streams
- **THEN** their deposited and value totals are summed together under the same wallet entry

---

### Requirement: Deposited vs Value Time-Series History by Investment Type

The system SHALL maintain a pre-computed time-series view showing deposited amount and market value at monthly intervals for each investment subtype and a synthetic `total` aggregate, for streams included in wealth.

Monthly data points are derived from actual event dates (event-driven, not a dense calendar series). Each data point represents the state at the end of the month in which events occurred.

At each month-end point:
- `deposited` = cumulative sum of all buy `totalValue` minus sell/matured `totalValue` for events up to and including that month-end
- `value` = sum of the most recent `balance` per stream for events up to and including that month-end; if a stream has no events yet at that point its contribution is zero

#### Scenario: History view contains one entry per month with events
- **WHEN** investment or stocks events exist across multiple months
- **THEN** the `investment-deposited-vs-value-history` view contains one date entry per distinct month in which any event occurred

#### Scenario: Deposited line is a step function
- **WHEN** no buy or sell events occur in a given month
- **THEN** the `deposited` value for that month equals the previous month's deposited value (carry-forward)

#### Scenario: Value reflects most recent known balance
- **WHEN** no price update occurs in a given month
- **THEN** the `value` for that month equals the most recent `balance` from any prior event for that stream (carry-forward)

#### Scenario: History includes a total aggregate
- **WHEN** the `investment-deposited-vs-value-history` view is requested
- **THEN** the `types` object contains a `total` key with deposited and value arrays summing all types

---

### Requirement: Deposited vs Value Time-Series History by Wallet

The system SHALL maintain a pre-computed time-series view showing deposited amount and market value at monthly intervals grouped by `labels["wallet"]` label, plus a synthetic `total`, for streams included in wealth.

Same computation rules as the by-type history view, but grouped by wallet instead of subtype.

#### Scenario: History view per wallet contains entries per distinct month
- **WHEN** investment or stocks events exist across multiple months in multiple wallets
- **THEN** the `investment-deposited-vs-value-history-per-wallet` view contains entries for each wallet keyed by wallet name, sharing the same `dates` array

#### Scenario: History per wallet includes a total aggregate
- **WHEN** the `investment-deposited-vs-value-history-per-wallet` view is requested
- **THEN** the `wallets` object contains a `total` key summing all wallets

---

### Requirement: Deposited vs Value Time-Series History by Type Within Wallet

The system SHALL maintain a pre-computed time-series view showing deposited amount and market value at monthly intervals, broken down by investment subtype within each wallet, for streams included in wealth.

For each wallet the result contains one series per subtype present in that wallet, plus a synthetic `total` series aggregating all subtypes within the wallet.

#### Scenario: History by type within wallet contains per-subtype series per wallet
- **WHEN** the `investment-deposited-vs-value-history-by-type-per-wallet` view is requested
- **THEN** the response contains `dates` and `wallets`, where each wallet key maps to a record of subtype keys (e.g. `ETF`, `Gold`) each with `deposited` and `value` arrays, plus a `total` key

#### Scenario: Each wallet total aggregates its subtypes only
- **WHEN** a wallet contains ETF and Gold streams
- **THEN** the `total` series within that wallet sums only ETF and Gold — not streams from other wallets

---

### Requirement: API Endpoints for Performance Views

The system SHALL expose five GET endpoints returning the above views.

#### Scenario: Get snapshot by type
- **WHEN** `GET /api/investments/deposited-vs-value` is called
- **THEN** the system returns HTTP 200 with a JSON array of `{ type, deposited, value }` objects

#### Scenario: Get snapshot by wallet
- **WHEN** `GET /api/investments/deposited-vs-value/per-wallet` is called
- **THEN** the system returns HTTP 200 with a JSON array of `{ wallet, deposited, value }` objects

#### Scenario: Get time-series history by type
- **WHEN** `GET /api/investments/deposited-vs-value/history` is called
- **THEN** the system returns HTTP 200 with `{ dates: [...], types: { <subtype>: { deposited: [...], value: [...] }, total: { ... } } }`

#### Scenario: Get time-series history by wallet
- **WHEN** `GET /api/investments/deposited-vs-value/history/per-wallet` is called
- **THEN** the system returns HTTP 200 with `{ dates: [...], wallets: { <wallet>: { deposited: [...], value: [...] }, total: { ... } } }`

#### Scenario: Get time-series history by type within wallet
- **WHEN** `GET /api/investments/deposited-vs-value/history/by-type-per-wallet` is called
- **THEN** the system returns HTTP 200 with `{ dates: [...], wallets: { <wallet>: { <subtype>: { deposited: [...], value: [...] }, total: { ... } } } }`

#### Scenario: Views update after new investment event
- **WHEN** a new investment or stocks event is appended
- **THEN** all five performance views are updated asynchronously via the NOTIFY/LISTEN mechanism
