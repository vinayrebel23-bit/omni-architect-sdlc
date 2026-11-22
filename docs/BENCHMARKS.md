# Benchmarks

Pinned with `forge-harness bench --pinned-cores 0-3` (`taskset` from util-linux). Host: Linux aarch64, 8 logical cores. `perf` is not installed, so there is no flamegraph. `cargo-deny` is not installed, so no CVE audit is claimed.

The timed loop is `admit` of `fix mobile login`: sanitize, route, spawn `/bin/true`, write one SQLite row. `hotpath_allocs` is 3 instrumented sites in that loop, not a dhat count.

## Delivered binary

`rewrite/native-prod` at `7cac52d`. Three pinned runs of 200 iterations. The binary did not change between them. The third run was after the subtractive commit; that commit does not touch the timed path.

| Run | p50_ns | p99_ns | throughput_ops | peak_rss_kb | binary_kb | crates | unsafe |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20200307 | 35026846 | 48.77 | 6068 | 2609 | 54 | 0 |
| 2 | 15273308 | 31009000 | 55.82 | 6072 | 2609 | 54 | 0 |
| 3 | 19954769 | 116078847 | 41.55 | 6036 | 2609 | 54 | 0 |

The p99 band is 31009000 ns to 116078847 ns. That is host noise, not a code change. Do not quote a single p99 as stable. `forbid(unsafe_code)` is set on `src/lib.rs` and `src/main.rs`.

## Python scaffold

Not measured. Importing `orchestrator/main.py` constructs model clients. SPEC.md says not to invent a p99. There is no sleep-adjusted figure because no Python sample was taken.

## Ratchet

| Hypothesis | Baseline p99 | Candidate p99 | Gain | Kept |
|---|---:|---:|---:|---|
| verifier poll 5ms to 1ms | 31009000 | 31949923 | -3.03% | no, harness reset to `58379ce` |

No further iterations. The 2% bar is smaller than the pinned band above. Logged in `workspace/results.tsv` as `oa-s2-dst`.

## Tournament

S2 seats were claimed with `forge-harness worktree-claim` and executed with `forge-harness seat`. All three DNF. No survivor was judged. `forge-harness score` was still run on the DNF file.

| Seat | CLI | Result |
|---|---|---|
| seat-a | opencode 1.18.21 | DNF, unknown server error `err_455a0344` |
| seat-b | pi 1.6.0 | DNF, timed out at 25 s with no stdout |
| seat-c | hermes | DNF, provider HTTP 401 |

codex, kimi, antigravity, goose, and zeroclaw are `available: false` and were not launched.

## OSS swaps

None measured as a swap. `rusqlite` is the ledger, as specified. No HTTP client. See `.forge/OSS_SWAP.md`.

## Tests

- Rust: 13 (`forge-harness test-drop` before 13, after 13, PASSED)
- DST: `FORGE_DST_SEED=0..16` in `tests/dst_sweep.rs`, `sockets_opened=0`
- Locked Python oracle: 2, hash `07ee90c13630cd2223bcb29dd193839487cbc2fcbd5751a35a18e0aafd4b7bef`
- `forge-harness oracle-verify`: VERIFIED

## Subtractive critique

`.forge/CRITIQUE_REPORT.md`. Deleted `Ledger::get` (no caller) and a redundant `db_path` clone. 14 deletions, 35 insertions in `7cac52d`, most of the insertions are the critique and swap notes. No test was removed.
