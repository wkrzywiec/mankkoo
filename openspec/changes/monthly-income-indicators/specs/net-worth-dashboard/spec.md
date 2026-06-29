## MODIFIED Requirements

### Requirement: Main Indicators

The system SHALL provide a pre-computed view of top-level net worth KPIs, including a computed value for last month's income.

#### Scenario: Net worth reflects all included streams
- **WHEN** the frontend requests `/api/main/indicators`
- **THEN** the response includes total savings from all streams where `include_in_wealth` is `"true"` or absent
- **AND** values are in PLN

#### Scenario: Last month income is computed and non-null
- **WHEN** at least one complete calendar month of event data exists
- **THEN** `lastMonthIncome` in the `/api/main/indicators` response contains the income for the most recent complete calendar month
- **AND** income is defined as total wealth on the last day of that month minus total wealth on the first day of that month, summed across all wealth-included streams

#### Scenario: Last month income is null when no complete months exist
- **WHEN** the `events` table is empty or all events are within the current calendar month
- **THEN** `lastMonthIncome` in the response is `null`

## ADDED Requirements

### Requirement: Monthly Profits Endpoint

The system SHALL expose the monthly income history via a dedicated API endpoint.

#### Scenario: Monthly profits endpoint returns income history
- **WHEN** the frontend requests `/api/main/monthly-profits`
- **THEN** the response contains the full `monthly-income` view data
- **AND** the shape is `{"date": ["YYYY-MM", ...], "total": [float, ...]}`

#### Scenario: Monthly profits endpoint returns empty when no data
- **WHEN** no `monthly-income` view exists (e.g., on first startup before any events)
- **THEN** the endpoint returns `null` or an empty structure (not an error)
