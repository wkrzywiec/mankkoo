# Spec: Net Worth Dashboard

## Purpose

Defines the dashboard views and API endpoints that surface aggregated financial data to the frontend.

---

## Requirements

### Requirement: Main Indicators

The system SHALL provide a pre-computed view of top-level net worth KPIs.

#### Scenario: Net worth reflects all included streams
- **WHEN** the frontend requests `/api/main`
- **THEN** the response includes total net worth from all streams where `include_in_wealth` is `"true"` or absent
- **AND** values are in PLN

---

### Requirement: Savings Distribution

The system SHALL provide a breakdown of savings by account type.

#### Scenario: Distribution by account subtype
- **WHEN** the frontend requests the savings distribution view
- **THEN** the `current-savings-distribution` view data is returned
- **AND** streams excluded from wealth are not included

---

### Requirement: Total History Per Day

The system SHALL provide a time-series of net worth for charting.

#### Scenario: Daily history available
- **WHEN** the frontend requests the historical trend
- **THEN** the `total-history-per-day` view returns a date-indexed series of total values
- **AND** only wealth-included streams contribute to the totals

---

### Requirement: Asynchronous View Updates

The system SHALL update all dashboard views asynchronously after any event is appended.

#### Scenario: View updates after import
- **WHEN** new events are appended (e.g., after CSV import)
- **THEN** a PostgreSQL `NOTIFY 'events_added'` is fired by trigger
- **AND** the background listener thread calls `views.update_views()`
- **AND** the next API call returns the updated view data

#### Scenario: Views are eventually consistent
- **WHEN** events are just appended
- **THEN** there is a brief window where views may not yet reflect the new events
- **AND** this is expected behavior (not a bug)

---

### Requirement: Investment Dashboard Views

The system SHALL maintain pre-computed investment breakdown views.

#### Scenario: Investment type distribution
- **WHEN** investment events exist
- **THEN** `investment-types-distribution` reflects the breakdown by bond/stock/real-estate type

#### Scenario: Wallet distribution
- **WHEN** streams have wallet labels
- **THEN** `investment-wallets-distribution` groups totals by wallet
- **AND** all streams are included regardless of `include_in_wealth`

#### Scenario: Type distribution per wallet
- **WHEN** both wallet labels and investment types are present
- **THEN** `investment-types-distribution-per-wallet` provides the cross-dimension breakdown
