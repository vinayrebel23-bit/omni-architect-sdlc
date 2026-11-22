default:
    just test

test:
    cargo test --release --locked

fmt:
    cargo fmt --check

clippy:
    cargo clippy --all-targets --all-features -- -D warnings

oracle:
    python3 -m pytest -q tests/oracle/test_routing_contract.py
