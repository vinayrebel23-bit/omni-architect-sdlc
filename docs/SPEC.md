# omni-architect-sdlc specification

Baseline: `1d7f67ad80d1`. This file separates the frozen routing contract from defects that must not be preserved.

## Frozen routing contract

Given an intent already lowercased, and no cache hit:

| If the intent contains | Swarm |
|---|---|
| `refactor` or `complexity` | `janitor` |
| else `500 error` or `incident` | `sre` |
| else `cost` or `aws` or `terraform` | `finops` |
| else `conversion` or `drop-off` | `growthops` |
| else | `general` |

Source: `orchestrator/main.py:78-87`. The first matching row wins. A cache hit currently forces `general` (`orchestrator/main.py:71-73`). The rewrite may keep that short-circuit only if the locked oracle still says so. The oracle locks the table, not the cache client.

## Defects, not contracts

- `verification_node` returns `ci_status: pass` with the comment at `orchestrator/main.py:113`. A rewrite that still hardcodes pass fails review even if other tests are green.
- `.woodpecker.yml:6-14` runs `npm ci` and `npm run build`. The tree has no `package.json`.
- `orchestrator/main.py:20` falls back to a demo API key when the environment variable is unset. The rewrite must refuse to start without a real secret source. Do not copy the fallback into new code.
- `orchestrator/graph_memory.py:9` and `docker-compose.yml:31` and `docker-compose.yml:75` embed default credentials. The rewrite reads them only from the environment and fails closed when they are absent.

## Config

Precedence, low to high: built-in empty secret (invalid), file, environment, CLI. Missing `OPENROUTER_API_KEY` is a startup error, not a default string.

## Security

No ticket text is executed. A sanitizer failure is fail-closed: malicious flag true, no swarm dispatch. That matches the exception path in `orchestrator/parser.py:55-62`, which does not need to be preserved as an LLM call.

## Observability and shutdown

Rewrite requirements, not current behavior: one log line per route decision, a health probe that does not call a model, and SIGTERM that stops admission. No unbounded queue.

## Budgets

Not measured. Do not invent a p99. The first tracer bullet is routing plus a real CI status, not a hot path.

## DST

This repo has network and state-machine I/O. Stage 1.2 must lock a DST sweep of at least 16 seeds before implementing the sanitizer or CI client. This Stage 1.1 delivery does not run that sweep, because there is no implementation yet.
