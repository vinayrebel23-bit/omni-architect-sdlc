# ADR 0003: No default credentials

## Status

Accepted

## Context

The scaffold has credential defaults in `orchestrator/main.py:20`, `orchestrator/graph_memory.py:9`, and `docker-compose.yml:31` and `:75`. The values are not repeated here.

## Decision

Missing secrets fail startup. Compose files, if kept, reference environment variables and do not inline passwords or agent secrets.

## Rejected

- Copy the current defaults into the Rust binary so local boot still works. That ships the defect.
- Log the secret when startup fails.

## Consequences

Stage 1.1 docs and oracles do not contain those strings. A secret scan of this commit must stay clean.
