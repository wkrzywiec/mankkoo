# Mankkoo — Project

## What It Is

Mankkoo is a **personal finance application** for tracking bank accounts, investments, and net worth. It is a self-hosted, single-user tool designed for the Polish market (PLN currency).

## Core Requirements

- Import bank transactions from CSV files exported by Polish banks (ING, mBank, Millennium)
- Store all financial operations as **immutable events** (event sourcing — never mutate history)
- Compute and display net worth, savings distribution, and investment portfolio
- Provide a visual dashboard with charts and tables
- Support multiple stream types: bank accounts, investments, stocks, retirement accounts

## Goals

- Accurate, trustworthy financial history — no data loss, no silent mutations
- Fast dashboard reads via pre-computed materialized views
- Simple self-hosted deployment via Docker Compose
- Polish localization: PLN currency throughout

## Scope

Two services:
1. **Backend** (`services/mankkoo`) — Python/Flask REST API + PostgreSQL event store
2. **Frontend** (`services/mankkoo-ui`) — Next.js dashboard UI

Infrastructure: PostgreSQL 16 + pgAdmin 4, orchestrated via Docker Compose.

## Out of Scope

- Multi-user / authentication
- Non-PLN currencies (not currently)
- Real-time bank sync (manual CSV import only)
