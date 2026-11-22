# ADR 0001: A CI pass is not a mock

## Status

Accepted

## Context

`orchestrator/main.py:109-114` sets `ci_status` to `pass` and comments that it is mocking CI.

## Decision

The rewrite's verifier returns `pass` only when the configured command exits 0. Tests inject a failing command and require `fail`. The mock return is not part of the locked oracle.

## Rejected

- Keep the mock so the current script still "passes". That freezes the defect.
- Treat a log line that says "Waiting for Woodpecker CI" as success.

## Consequences

Stage 1.2 cannot mark the verifier slice done by printing pass.
