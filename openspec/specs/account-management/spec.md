# Spec: Account Management

## Purpose

Defines how bank accounts and retirement accounts are created, tracked, and updated as streams of immutable events.

---

## Requirements

### Requirement: Open an Account

The system SHALL create a new account stream when a user opens an account.

#### Scenario: Create a checking account
- **WHEN** a user submits a new account with type `checking` and a name
- **THEN** a new stream of type `account` and subtype `checking` is created
- **AND** an `AccountOpened` event is appended as version 1

#### Scenario: Create a savings account
- **WHEN** a user submits a new account with type `savings`
- **THEN** a new stream of type `account` and subtype `savings` is created

#### Scenario: Create a cash account
- **WHEN** a user submits a new account with type `cash`
- **THEN** a new stream of type `account` and subtype `cash` is created

---

### Requirement: Record a Deposit

The system SHALL record a money deposit on an account stream.

#### Scenario: Deposit money
- **WHEN** a deposit is recorded on an account
- **THEN** a `MoneyDeposited` event is appended with `amount`, `balance`, and `currency` in the data payload
- **AND** the event version is exactly `stream.version + 1`

---

### Requirement: Record a Withdrawal

The system SHALL record a money withdrawal on an account stream.

#### Scenario: Withdraw money
- **WHEN** a withdrawal is recorded on an account
- **THEN** a `MoneyWithdrawn` event is appended with `amount`, `balance`, and `currency` in the data payload
- **AND** the event version is exactly `stream.version + 1`

---

### Requirement: Optimistic Concurrency

The system SHALL reject duplicate or out-of-order event versions.

#### Scenario: Version conflict
- **WHEN** two events are appended with the same version for the same stream
- **THEN** the second append fails with a concurrency error
- **AND** the stream state is unchanged

---

### Requirement: Wealth Inclusion Control

The system SHALL allow individual accounts to be excluded from net worth totals.

#### Scenario: Account included in wealth (default)
- **WHEN** a stream has no `include_in_wealth` label
- **THEN** it is included in all wealth-total views (backward-compatible default)

#### Scenario: Account explicitly included
- **WHEN** a stream has `labels["include_in_wealth"] = "true"` (exact lowercase string)
- **THEN** it is included in wealth-total views

#### Scenario: Account excluded from wealth
- **WHEN** a stream has `labels["include_in_wealth"]` set to any value other than `"true"`
- **THEN** it is excluded from wealth-total views (`main-indicators`, `current-savings-distribution`, `total-history-per-day`)
- **AND** it remains visible in composition views (`investment-wallets-distribution`, `investment-types-distribution-per-wallet`)
