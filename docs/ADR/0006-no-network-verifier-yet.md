# ADR 0006: No network verifier in the tracer bullet

## Status

Accepted

## Context

The scaffold's verifier returns `pass` without running CI. Architecture allows a Woodpecker HTTP client only after a DST of at least 16 seeds. `forge-harness dst-policy --class network` requires that sweep.

## Decision

The verifier is a local process runner. `pass` means the configured command exited 0. An unset `OMNI_VERIFY_PROGRAM` is `fail`, not a default success. DST seeds `0..16` run with `sockets_opened=0`. No HTTP client is compiled in.

## Rejected

- Add `reqwest` or `tonic` now that the sweep exists. The sweep does not authorize a remote client, and `cargo-deny` is not installed, so a CVE claim would be false.
- Default the command to `/bin/true`. That would make an unconfigured process report pass.

## Consequences

Operators set `OMNI_VERIFY_PROGRAM` to the real CI command. The HTTP seam stays closed.
