# omni-architect

Native ticket router for the Stage-1 rewrite. The production entrypoint is the Rust binary. `orchestrator/main.py` stays in the tree because the locked routing oracle reads that file. Do not delete it until the oracle is replaced.

## Run

```bash
export OPENROUTER_API_KEY=...   # required, no default
export OMNI_VERIFY_PROGRAM=/bin/false
cargo build --release
./target/release/omni-architect health
./target/release/omni-architect admit --id t1 --text "fix mobile login"
```

`health` does not call a model. It still refuses to start when `OPENROUTER_API_KEY` is unset.

Missing `OMNI_VERIFY_PROGRAM` records `ci_status=fail`. It does not default to pass. A ticket that looks like prompt injection is not dispatched.

`SIGTERM` stops admission. The queue cap is 32.

## Checks

```bash
cargo test --release --locked
python3 -m pytest -q tests/oracle/test_routing_contract.py
```

Pinned bench, after the key and verifier are set:

```bash
./target/release/omni-architect bench --iters 200 --program /bin/true --db ./bench.db
```

Stdout is `BenchMetrics` JSON. The loop includes a real local process spawn, so the number is not a CPU-kernel figure.

## What this is not

The Python swarms still import a model client at import time. They now fail if `OPENROUTER_API_KEY` is unset. They are not the production path. Neo4j, Chroma, and a Woodpecker HTTP client are not in the binary.
