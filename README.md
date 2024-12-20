# Mankkoo

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3.10/)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

 [![App main workflow](https://github.com/wkrzywiec/mankkoo/actions/workflows/services-main.yaml/badge.svg?branch=main)](https://github.com/wkrzywiec/mankkoo/actions/workflows/services-main.yaml)
 [![codecov](https://codecov.io/gh/wkrzywiec/mankkoo/branch/main/graph/badge.svg?token=53N40DW01T)](https://codecov.io/gh/wkrzywiec/mankkoo)
[![CodeFactor](https://www.codefactor.io/repository/github/wkrzywiec/mankkoo/badge)](https://www.codefactor.io/repository/github/wkrzywiec/mankkoo) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

> 🚧 Attention: This project is still under construction!

A personal finance dashboard designed to simplify money management by delivering insightful visualizations of investments, tracking financial goals, and optimizing budgets.

## About

I have always wanted a quick yet insightful way to glance at my personal finances while avoiding spending too much time managing them.

Additionally, I strive to work on projects that allow me to explore new technologies or approaches to building software (e.g. event sourcing, CQRS). To address both of these goals, *Mankkoo* was created.

With *Mankkoo*, I can effortlessly import transactions from all my bank accounts and investments into one centralized platform for analysis. This enables me to gain insights into their history and distribution. By having an overall view, I can effectively plan my future financial steps.

Below are screenshots of the mockups. Real screenshots will be added soon.

<p align="center">
  <img src="./img/home.png" alt="Home page" width="400"/>
  <img src="./img/history.png" alt="Financial History" width="400"/>
  <img src="./img/accounts.png" alt="Bank Accounts page" width="400"/>
</p>

### Architecture

Initially, *Mankkoo* was developed as a single-runtime Python application, where all data was stored in files. However, due to limitations and a desire to adopt more popular tools, the application was split into two services: a frontend and a backend, each implemented using different technologies. For the persistence layer, a PostgreSQL database was chosen.

```mermaid
graph TD
    Frontend[Frontend Service] -->|HTTP API Calls| Backend[Backend Service]
    Backend -->|Read/Write| Database[(PostgreSQL Database)]
    Frontend <-->|Responses| Backend
```

A key feature of the backend service is its ability to import transaction files downloaded from bank websites. Each transaction is recorded as an event in an append-only event log, which serves as the source of truth for all operations performed on bank accounts and investments.

Whenever a new batch of events is added to the event log, it triggers updates to multiple projections used to render charts and indicators. This functionality is powered by PostgreSQL’s built-in `pg_notify()` and `LISTEN` functions, enabling efficient real-time updates ([docs](https://www.postgresql.org/docs/current/sql-notify.html)).

Here is a schematic diagram of the data structure:

```mermaid
erDiagram
    STREAMS {
        UUID id PK
        TEXT type
        BIGINT version
        JSONB metadata
    }
    EVENTS {
        UUID id PK
        UUID stream_id FK
        TEXT type
        JSONB data
        BIGINT version
        TIMESTAMP occured_at
        TIMESTAMP added_at
    }
    VIEWS {
        TEXT name PK
        JSONB content
        TIMESTAMP updated_at
    }

    STREAMS ||--o{ EVENTS : has

```

### Technologies

* **Frontend**: React 18, NextJS, TypeScript, ChartJS
* **Backend**: Python 3.10, Flask, Pandas, Pytest, Poetry
* **Database**: PostgreSQL 16

## Roadmap

- [ ] Prepare data for demo
- [ ] Basic view for all streams and events
- [ ] Creating and modifying streams on UI
- [ ] Investments summary 

See the [open issues](https://github.com/wkrzywiec/mankkoo/issues) for a full list of proposed features (and known issues).

## Getting Started

### Prerequisites
### Installation

> devcontainer
> use taskFile

### Running locally

## Usage

enter website
enter postgresql
create backup
restore backup


