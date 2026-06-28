# Backend — Project

## What It Is

Python/Flask REST API for Mankkoo. Owns all business logic, event sourcing, database access, bank CSV parsing, and materialized view computation.

## Responsibilities

- Expose REST API consumed by the Next.js frontend
- Parse and import bank transaction CSV files (ING, mBank, Millennium)
- Store financial operations as immutable events in PostgreSQL
- Maintain 7 pre-computed materialized views for fast dashboard reads
- Listen for DB change notifications and rebuild views asynchronously

## Stream Types & Key Events

| Type | Subtypes | Key Events |
|---|---|---|
| `account` | `checking`, `savings`, `cash` | `AccountOpened`, `MoneyDeposited`, `MoneyWithdrawn` |
| `investment` | `treasury_bonds`, `corporate_bonds`, `real_estate` | `TreasuryBondsBought`, `TreasuryBondsMatured` |
| `stocks` | `ETF`, `stock` | `ETFBought`, `ETFSold`, `StockBought`, `StockSold` |
| `retirement` | same as account | same as account |

## Non-Negotiable Rules

- **Never INSERT into `events` directly** — always use `es.store([event])`
- **Never UPDATE an event** — append a correcting event instead
- **Version must be sequential per stream** — read `stream.version`, set `event.version = stream.version + 1`
- Test files must end with `_test.py` (not `test_*.py`) — wrong suffix breaks pytest discovery
