## ADDED Requirements

### Requirement: Monthly Income View

The system SHALL compute and store a pre-computed view of income per calendar month, where income is defined as the total wealth on the last day of the month minus the total wealth on the first day of the month, across all streams where `include_in_wealth` is `"true"` or absent.

#### Scenario: Monthly income computed for all complete months
- **WHEN** events exist across multiple calendar months
- **THEN** the `monthly-income` view contains one entry per complete calendar month from the earliest event date to the last complete month
- **AND** each entry's income equals `SUM(balance on last day of month) - SUM(balance on first day of month)` across all wealth-included streams

#### Scenario: Month with no activity yields zero income
- **WHEN** a stream has no events during a given month but has a known balance from a prior month
- **THEN** the stream's contribution to that month's income is 0 (last-day balance equals first-day balance)

#### Scenario: New stream with no prior history contributes zero on first-day
- **WHEN** a stream has its first event mid-month
- **THEN** the stream's first-day balance is treated as 0 (no prior event exists)
- **AND** the month's income reflects the balance gained since the start of that month

#### Scenario: Current in-progress month is excluded
- **WHEN** the current calendar month has not yet ended
- **THEN** the `monthly-income` view does NOT include the current month
- **AND** only fully completed months appear in the view

#### Scenario: View reflects include_in_wealth filter
- **WHEN** a stream has `labels["include_in_wealth"] = "false"` or any value other than `"true"` (and the key is present)
- **THEN** that stream's balance is NOT included in any monthly income calculation
- **AND** a stream with no `include_in_wealth` label IS included (default behavior)

#### Scenario: View shape is a parallel date/total list
- **WHEN** the frontend requests `/api/main/monthly-profits`
- **THEN** the response contains `date` (array of `YYYY-MM` strings, ascending order) and `total` (array of floats, matching index)

#### Scenario: No events returns empty view
- **WHEN** the `events` table is empty
- **THEN** the `monthly-income` view stores `{"date": [], "total": []}`
- **AND** `/api/main/monthly-profits` returns an empty date/total structure

#### Scenario: Negative income is valid
- **WHEN** total wealth decreases over the course of a month
- **THEN** the income value for that month is a negative number
- **AND** it is stored and returned as-is (not clamped to zero)
