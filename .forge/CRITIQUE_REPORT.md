# Subtractive critique

Fresh CLI seats did not produce this report. Seat A (opencode) returned an unknown server error, seat B (pi) timed out at 25s with no stdout, and seat C (hermes) returned HTTP 401. This pass is the primary worker reading the tree at `58379ce` with the Stage 1.1 docs, not a second model.

## Findings

| Severity | Item | Action |
|---|---|---|
| HIGH | none | |
| CRITICAL | none | |
| MEDIUM | `Ledger::get` has no caller | Delete it |
| LOW | `bench_metrics` cloned `db_path` twice | Delete the second clone |
| INFO | `hotpath_allocs` counts three instrumented sites, not allocator events | Say so in `docs/BENCHMARKS.md`. Do not pretend it is dhat |
| INFO | Four modules match `docs/ARCHITECTURE.md` | Do not collapse them |
| INFO | `signal-hook` exists only to stop admission on SIGTERM | Keep it |

## Rejected deletions

- Do not drop `tests/dst_sweep.rs` or the timeout test. A shorter bench is not a reason to remove a test.
- Do not remove `orchestrator/main.py`. The locked oracle reads it.
- Do not add an HTTP client to "use" the DST sweep. ADR 0006 stands.
