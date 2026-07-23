## ADDED Requirements

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
