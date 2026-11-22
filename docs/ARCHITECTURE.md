# Architecture

The scaffold is a LangGraph script that calls remote models at import time (`orchestrator/main.py:20-37`) and mocks the CI edge. The rewrite is one binary with a pure route function and a verifier seam. No pass-through traits.

```text
Ticket edge
  parse SanitizedTask
        |
     Route (pure, no network)
        |
   Admission (bounded, default 32)
        |
   Verifier seam
        |
     Ledger
```

## Layout

| Path | Owns | Must not own |
|---|---|---|
| `src/route.rs` | The table in SPEC.md | HTTP, models, Neo4j |
| `src/sanitize.rs` | Fail-closed parse | Swarm dispatch |
| `src/verify.rs` | CI status from a real command or a recorded fixture | A hardcoded pass |
| `src/ledger.rs` | Ticket id, swarm, ci_status | Prompt text logs of secrets |

Hot path: none. Do not add SIMD, `io_uring`, or a cache-line ring for a control-plane router.

## What is rejected

- Import-time model clients. Construction of a client happens after secrets are present, and tests never construct one.
- Chroma and Neo4j in the first tracer bullet. They are optional later seams, not the ledger.
- The Woodpecker file as the product. The product is the binary. CI for this repo must build the binary, not `npm ci`.

## Swappable seams

- `Verifier`: a local process runner versus a Woodpecker HTTP client. The HTTP client is not added until a DST of at least 16 seeds is locked.
- `Ledger`: `rusqlite`. Do not pull a graph database for five strings.
