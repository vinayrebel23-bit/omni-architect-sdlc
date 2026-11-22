# OSS swap decisions

`cargo-deny` is not installed. No CVE audit is claimed. Licenses below are the crate metadata, not a deny-gate result.

| Seam | Choice | Kept? | Why |
|---|---|---|---|
| Ledger | `rusqlite` 0.32, MIT, bundled SQLite | yes | Architecture already rejects Neo4j for five strings. A custom file ledger would reimplement a transaction. Not measured against a second implementation. |
| Verifier | local `std::process::Command` | yes | `reqwest` / `tonic` would open sockets. ADR 0006. No DST result authorizes a remote client. |
| Route | the table in `src/route.rs` | yes | No parser crate. The function is smaller than a dependency. |
| Hash, ring, compression, crypto | none | n/a | This binary has no such seam. |
| SIGTERM | `signal-hook` 0.3, MIT/Apache-2.0 | yes | Safe wrapper so the binary can keep `forbid(unsafe_code)`. |

No swap was reset with `git reset --hard`. None was promoted on a benchmark.
