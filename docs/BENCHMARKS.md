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

## Windows parity (2026-11-23)

Host: Windows 11, AMD Ryzen 5 5600G, 6 physical / 12 logical. Pinned with `forge-harness bench --affinity 0x0F` after a 10-iteration warmup. The timed loop is the same `admit` of `fix mobile login`, but the verifier is `cmd /c exit 0` because `/bin/true` does not exist here. `hotpath_allocs` is still the three instrumented sites, not a dhat count.

| Run | p50_ns | p99_ns | throughput_ops | peak_rss_kb | binary_kb | crates | unsafe |
|---|---:|---:|---:|---:|---:|---:|---:|
| pinned 1 | 29626300 | 49965900 | 31.14 | 8184 | 2540 | 58 | 0 |
| pinned 2 | 28578400 | 54469400 | 31.25 | 8180 | 2540 | 58 | 0 |

The p99 band is about 9%. That is larger than the 2% Git-Ratchet keep bar, so no poll-interval change was kept. RSS is `tasklist` working set in KB. The earlier 188 and 8 KB readings were a CSV parse bug and are not quoted.

`rusqlite` moved from 0.32.1 to 0.41.1. `cargo deny check advisories` failed on `libsqlite3-sys` 0.30.1 (`RUSTSEC-2026-0459`, bundled SQLite before 3.54.0) and passes on 0.39.1. That is an OSS swap kept because the advisory cleared and the 13 tests still pass, not because p99 improved.

DST is now `FORGE_DST_SEED=0..32`. The socket check counts TCP rows owned by the test process. A host-wide `netstat` delta is other software and was rejected as a false failure.

## OSS swaps

`rusqlite` 0.41.1 replaced 0.32.1. See above. No HTTP client. See `.forge/OSS_SWAP.md`.

## Tests

- Rust: 13 (`forge-harness test-drop` before 13, after 13, PASSED)
- DST: `FORGE_DST_SEED=0..16` in `tests/dst_sweep.rs`, `sockets_opened=0`
- Locked Python oracle: 2, hash `07ee90c13630cd2223bcb29dd193839487cbc2fcbd5751a35a18e0aafd4b7bef`
- `forge-harness oracle-verify`: VERIFIED

## Windows tournament (2026-11-24)

Host: Windows 11, AMD Ryzen 5 5600G, 6 physical / 12 logical. Pinned with `forge-harness bench --affinity 0x0F` after a 10-iteration warmup. Measured tree is `rewrite/native-prod` after the dead-`netstat` deletion. 30 iterations, not 200. `hotpath_allocs` is still the three instrumented sites.

| Run | p50_ns | p99_ns | throughput_ops | peak_rss_kb | binary_kb | crates | unsafe |
|---|---:|---:|---:|---:|---:|---:|---:|
| pinned 1 | 28942100 | 31067400 | 34.54 | 8236 | 2611 | 60 | 0 |
| pinned 2 | 28851300 | 34318500 | 34.42 | 8232 | 2611 | 60 | 0 |

The two 30-iteration p99 samples differ by about 10%. That is larger than the 2% Git-Ratchet keep bar. Do not treat the drop versus the 2026-11-23 200-iteration samples (49965900 ns and 54469400 ns) as a code win. The timed path still spawns `cmd /c exit 0`. The deletion does not touch it. `Cargo.lock` has 60 `[[package]]` rows. An earlier note of 58 does not match this lock. The lock was not edited in this pass.

Seat A and seat C produced the same 31-line deletion. Seat B did not finish. No OSS crate was swapped in this pass. `rusqlite` 0.41.1 stays.

## Subtractive critique

`.forge/CRITIQUE_REPORT.md`. Deleted `Ledger::get` (no caller) and a redundant `db_path` clone. 14 deletions, 35 insertions in `7cac52d`, most of the insertions are the critique and swap notes. No test was removed.
