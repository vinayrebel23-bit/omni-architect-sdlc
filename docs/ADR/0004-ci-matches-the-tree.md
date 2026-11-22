# ADR 0004: CI matches the tree

## Status

Accepted

## Context

`.woodpecker.yml:6-14` runs `npm ci` in a repository with no `package.json`. The programs are Python modules under `orchestrator/` and `swarms/`.

## Decision

The rewrite's workflow builds and tests the native binary. It does not run `npm ci` unless a `package.json` exists.

## Rejected

- Add an empty `package.json` so the current Woodpecker file goes green. That preserves a mismatched pipeline.
- Delete CI entirely.

## Consequences

Stage 1.2 adds `.github/workflows/ci.yml` for the binary, not a Node build.
