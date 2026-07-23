# Spec: Investment Tracking

## Purpose

Defines how investment instruments (treasury bonds, corporate bonds, real estate, ETFs, stocks, retirement) are tracked as event streams.

---

## Requirements

### Requirement: Track Treasury Bond Investment

The system SHALL record treasury bond purchases and maturities as events.

#### Scenario: Buy treasury bonds
- **WHEN** a user records a treasury bond purchase
- **THEN** a `TreasuryBondsBought` event is appended to an `investment` stream with subtype `treasury_bonds`

#### Scenario: Treasury bonds mature
- **WHEN** a user records a bond maturity
- **THEN** a `TreasuryBondsMatured` event is appended

---

### Requirement: Track Stock and ETF Operations

The system SHALL record stock and ETF buy/sell transactions as events.

#### Scenario: Buy ETF
- **WHEN** a user records an ETF purchase
- **THEN** an `ETFBought` event is appended to a `stocks` stream with subtype `ETF`

#### Scenario: Sell ETF
- **WHEN** a user records an ETF sale
- **THEN** an `ETFSold` event is appended

#### Scenario: Buy stock
- **WHEN** a user records a stock purchase
- **THEN** a `StockBought` event is appended to a `stocks` stream with subtype `stock`

#### Scenario: Sell stock
- **WHEN** a user records a stock sale
- **THEN** a `StockSold` event is appended

---

### Requirement: Wallet Label

The system SHALL allow investments to be grouped by wallet label.

#### Scenario: Assign wallet
- **WHEN** a stream has `labels["wallet"]` set to a wallet name (e.g., `"IKE"`, `"Personal"`)
- **THEN** it is grouped under that wallet in the `investment-wallets-distribution` and `investment-types-distribution-per-wallet` views

---

### Requirement: Investment Indicators View

The system SHALL maintain a pre-computed view of investment KPIs.

#### Scenario: View reflects current investments
- **WHEN** investment events are appended
- **THEN** the `investment-indicators` view is updated asynchronously (via NOTIFY/LISTEN)
- **AND** the API returns the updated values on the next request

---

### Requirement: Investment Tracking Naming Convention for Event Types

The system SHALL follow a naming convention for investment event types to ensure the deposited-vs-value views can correctly identify buy, sell, and price update events using pattern matching.

#### Scenario: Buy events follow Bought suffix convention
- **WHEN** a new investment event type represents a purchase (cash out from user)
- **THEN** the event type name SHALL end with `Bought` (e.g., `ETFBought`, `GoldBought`, `TreasuryBondsBought`)

#### Scenario: Sell events follow Sold or Matured suffix convention
- **WHEN** a new investment event type represents a sale or maturity (cash in to user)
- **THEN** the event type name SHALL end with `Sold` or `Matured` (e.g., `ETFSold`, `GoldSold`, `TreasuryBondsMatured`)

#### Scenario: Price update events follow Priced suffix convention
- **WHEN** a new investment event type represents a market value update only (no cash flow)
- **THEN** the event type name SHALL end with `Priced` (e.g., `ETFPriced`, `GoldPriced`, `TreasuryBondsPriced`)
