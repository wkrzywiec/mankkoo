# Testing Guidelines

These principles govern how tests should be written, organized, and maintained across the project. They apply to every new feature, bug fix, and refactoring.

## Test Types

There are three types of tests. Each serves a distinct purpose and operates under different constraints.

### 1. Unit Tests (preferred)

Unit tests verify **business logic in isolation**, without any I/O (no database, no network, no filesystem).

- **Scope:** Test whole modules or meaningful behavior units, not individual functions or classes in isolation. The goal is to verify that a module produces the correct outcome, not to test implementation details.
- **No I/O:** These tests must not touch databases, queues, streams, HTTP services, or the filesystem. They must be fast — milliseconds per test.
- **Fakes over mocks:** Prefer in-memory fakes (e.g., a fake repository backed by a list/map) for dependencies like databases, queues, or streaming services. For external backend services, mocks are acceptable.
- **When to use:** Whenever the code under test contains meaningful business logic — validation, calculations, state transitions, decision-making.
- **When to reconsider:** If the application has very little business logic and is primarily a shallow integration tool (receives a request, maps it, stores in DB, returns response), unit tests add limited value. In that case, prefer component tests instead.

### 2. Integration Tests

Integration tests verify that **connectors to external dependencies work correctly** — database repositories, cache clients, HTTP clients for other services, queue producers/consumers, streaming adapters.

- **Real dependencies via Docker:** Spin up real instances of external systems (database, cache, message broker, etc.) using Docker containers. Do not fake external systems in integration tests — the whole point is to test the real interaction.
- **Stubbing for backend services:** For external HTTP services (APIs you call), use stubbing tools (e.g., WireMock, MockServer, or equivalent for your stack) to simulate their responses.
- **Test independence:** Each test must be independent. Clean up state after each test (truncate tables, purge queues) so tests can run in any order.
- **Focus areas:**
  - Field mapping — are all fields correctly serialized/deserialized?
  - Error handling — does the connector handle failures (timeouts, malformed responses) correctly?
  - Basic functionality — does the fundamental read/write/send/receive work?

### 3. Component Tests

Component tests verify the **entire application end-to-end**, with all I/O dependencies running (via Docker or stubs).

- **Scope:** The full application is started as a whole. Requests go through the real entry point (HTTP endpoint, message consumer, etc.) and flow through all layers.
- **Focus areas:**
  - Main happy paths — does the primary use case work end-to-end?
  - Core mechanisms — does error handling, retry logic, authentication/authorization work as configured?
  - Application configuration — is security set up correctly? Are middleware/filters wired properly?
- **Keep the count low:** Component tests are slow and expensive. Limit their number. Test only the main paths and cross-cutting concerns here. Push variant testing down to unit or integration tests.
- **When to prefer over unit tests:** When the application is a shallow integration tool with little business logic (e.g., CRUD APIs, pass-through services). In that case, component tests provide more value than unit tests.

## Choosing the Right Test Type

```
Does the code contain meaningful business logic?
  YES → Write unit tests (with fakes, no I/O)
  NO  → Is it a connector to an external system?
          YES → Write integration tests (real deps via Docker)
          NO  → Write component tests (full app, main paths only)
```

As a general rule: push test coverage as far down as possible. Prefer many fast unit tests, a moderate number of integration tests, and a small number of component tests.
