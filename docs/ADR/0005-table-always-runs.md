# ADR 0005: The routing table always runs

## Status

Accepted

## Context

`orchestrator/main.py:71-73` returns swarm `general` on a cache hit and never evaluates the table. ADR 0002 says that short-circuit is documented, not locked.

## Decision

Stage 1.2 drops the short-circuit. `route_swarm` is the table in SPEC.md and nothing else. A later cache may store a plan, but it must not replace the table unless the oracle changes.

## Rejected

- Preserve the cache hit so behavior matches the scaffold line for line. That hides tickets that should reach `janitor` or `sre`.
- Call a model when the cache misses. Tests would open a socket.

## Consequences

The locked oracle still passes. A cache client is not part of this binary.
