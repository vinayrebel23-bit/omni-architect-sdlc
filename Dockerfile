FROM rust:1.88-bookworm AS build
WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN useradd --create-home --uid 10001 omni
USER omni
WORKDIR /home/omni
COPY --from=build /src/target/release/omni-architect /usr/local/bin/omni-architect
ENV OMNI_DB=/home/omni/omni.db
ENTRYPOINT ["omni-architect"]
CMD ["health"]
