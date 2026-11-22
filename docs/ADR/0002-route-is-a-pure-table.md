# ADR 0002: Routing is a pure table

## Status

Accepted

## Context

`orchestrator/main.py:78-87` chooses a swarm with keyword tests. The surrounding function also calls a cache and, elsewhere, a model.

## Decision

The locked oracle tests the table as a pure function. Model calls are outside the route. First match wins, in the order written in SPEC.md.

## Rejected

- Ask a model to classify the swarm on every ticket. That makes the contract non-deterministic and opens a socket in tests.
- Reorder the rows without an oracle change. `500 error` must not steal a ticket that also contains `refactor`.

## Consequences

A cache hit that forces `general` is a separate decision. It is documented, not locked, so Stage 1.2 can drop it if the table should still run.
