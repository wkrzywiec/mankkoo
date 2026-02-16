# Solution Design Guidelines

These principles govern how all code in this project should be designed and structured. They apply to every new feature, refactoring, and architectural decision.

## 1. Simplicity First

- Prefer the simplest solution that solves the problem.
- Avoid framework magic, clever abstractions, and hidden behavior. Code should be explicit and easy to follow.
- If a plain function solves the problem, do not introduce a class. If a class solves it, do not introduce a framework feature.
- When choosing between a "smart" solution and a "boring" one, pick boring. Boring code is easy to read, debug, and delete.

## 2. Composition Over Inheritance

- Build behavior by combining small, focused components rather than extending base classes.
- Avoid deep inheritance hierarchies. If you find yourself creating a class just to inherit from it, reconsider.
- Use functions, interfaces, and dependency injection to compose behavior.

## 3. Vertical Slices (Module-per-Process)

Organize code in vertical slices, where each module owns the full stack for a specific **process** (a verb/action), not for a data entity (a noun).

### What a vertical slice looks like

A module contains all the layers it needs: from database access, through business logic, to API (or even UI). It is a self-contained unit for one process.

```
Example: "Importing Bank Transactions" is a process — it gets its own module.

importing/
  orchestrator         <- coordinates the import workflow
  parsers/             <- format-specific parsers (one per source format)
  models               <- data structures used only by this module
  db                   <- database access used only by this module
  tests/               <- tests for this module

This module does NOT share its DB tables with other modules.
If another module needs import data, it calls this module's API.
```

### Key rules

- **Split by process, not by data.** A module represents a business process (e.g., "importing transactions", "calculating net worth"), not a data entity (e.g., "account", "transaction").
- **Each module owns its database.** At minimum, a module owns its own tables/collections. Other modules must NOT read from or write to those tables directly. They communicate through the module's public API (function calls, queries, commands, or events).
- **Modules communicate via queries, commands, or events.** Never via shared database access. This keeps modules independently deployable and deletable.

## 4. Loose Coupling

- Every module and class that is responsible for a different task should be independent from others.
- A well-designed module can be **deleted** without breaking unrelated parts of the system. If removing a module causes a cascade of failures elsewhere, the coupling is too tight.
- Depend on abstractions (interfaces, protocols), not on concrete implementations of other modules.
- Keep the public surface area of each module small: expose only what other modules genuinely need.
- Avoid shared mutable state between modules.
