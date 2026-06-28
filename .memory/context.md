# Mankkoo — Context

## Why This Project Exists

Polish banks export transaction history as CSV files but provide no unified way to track overall net worth across multiple accounts, investment portfolios, and retirement funds. Mankkoo solves this by being a local aggregator — the user periodically imports CSVs and gets a consolidated financial picture.

## Problems It Solves

- **Fragmented data**: accounts at multiple banks, investments at multiple brokers — no single view
- **No history**: banks show current state; Mankkoo keeps the full immutable history
- **Manual reconciliation**: spreadsheets are error-prone; Mankkoo structures the data properly
- **Opacity on net worth**: no easy way to see total savings + investments + stocks in one number

## How It Works

1. User logs into the dashboard (port 3000)
2. User uploads a CSV file from their bank
3. Backend parses the CSV, creates account events, stores them in PostgreSQL
4. A PostgreSQL trigger fires `NOTIFY 'events_added'`
5. A background thread in the backend rebuilds 7 materialized views
6. Dashboard refreshes — charts, totals, and distribution charts update

## User Experience Goals

- Dashboard is the primary surface: overview of net worth, savings breakdown, investment performance
- Minimal friction for importing: upload a file, done
- Data is always correct — the system must never silently lose or corrupt events
- Read performance is fast thanks to pre-computed views (not live aggregation queries)
- Polish language context: amounts in PLN, account numbers formatted as IBANs
