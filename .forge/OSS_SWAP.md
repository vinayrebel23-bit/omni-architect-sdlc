# OSS swap decisions

`cargo deny check advisories` and `cargo deny check licenses` pass on this tree with `cargo-deny` 0.22.0. `deny.toml` is in the repo. The Windows note below is the swap that cleared `RUSTSEC-2026-0459`.

| Seam | Choice | Kept? | Why |
|---|---|---|---|
| Ledger | `rusqlite` 0.41.1, MIT, bundled SQLite 3.54.1 | yes | Replaced 0.32.1 after `cargo deny` reported `RUSTSEC-2026-0459` on the bundled SQLite. 0.41.1 clears `cargo deny check advisories` and `cargo deny check licenses`. Tests stayed at 13. Not a p99 win. |
| Verifier | local `std::process::Command` | yes | `reqwest` / `tonic` would open sockets. ADR 0006. No DST result authorizes a remote client. |
| Route | the table in `src/route.rs` | yes | No parser crate. The function is smaller than a dependency. |
| Hash, ring, compression, crypto | none | n/a | This binary has no such seam. |
| SIGTERM | `signal-hook` 0.3, MIT/Apache-2.0 | yes | Safe wrapper so the binary can keep `forbid(unsafe_code)`. |

No swap was reset with `git reset --hard`. None was promoted on a benchmark.
