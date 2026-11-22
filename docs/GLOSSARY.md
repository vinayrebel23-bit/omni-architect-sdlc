# Glossary

Names for the omni-architect-sdlc rewrite. Do not introduce `Manager`, `Helper`, `Handler`, or `Utils`.

| Term | Meaning | Not this |
|---|---|---|
| Ticket | One inbound request, raw text plus metadata. | A GitHub issue object copied wholesale. |
| SanitizedTask | The edge parse of a ticket: malicious flag, target files, technical objective. | A prompt string passed through. |
| Intent | The lowercased technical objective used for routing. | The raw human message. |
| Swarm | One of `janitor`, `sre`, `finops`, `growthops`, or `general`. | A thread pool. |
| Route | The pure function from Intent to Swarm. Current source: `orchestrator/main.py:78-87`. | An LLM call. |
| CacheHit | A stored plan that short-circuits routing. Current code returns swarm `general` on a hit (`orchestrator/main.py:71-73`). | A successful CI run. |
| CiStatus | `pass` or `fail` from a real verifier. The scaffold returns `pass` unconditionally (`orchestrator/main.py:109-114`). | A printed log line. |
| Ledger | The durable record of ticket, route, and CI result. Absent today. | Chroma or Neo4j used as the system of record. |

Rejected names: `SwarmManager`, `TicketHelper`, `CiHandler`.
