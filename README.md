# Ping-pong API

Small HTTP API with TypeScript, Go, Rust, and Python implementations.

## TypeScript

Run locally:

```bash
npm install
npm run dev
```

The server listens on port `3000` by default. Set `PORT` or `HOST` to change
the binding.

## Configuration

Keep the API key in your local environment; do not commit the real value:

```bash
export API_KEY="replace-with-your-api-key"
```

## Endpoint

```bash
curl http://localhost:3000/ping
# {"message":"pong","count":1}
```

Only `GET /ping` is supported. Unknown routes return `404`, and other methods
on `/ping` return `405`.

Each successful ping is logged with the current pong counter.

## Go

Run locally from the Go implementation directory:

```bash
cd go
go run .
```

Run its tests with `go test ./...`.

## Rust

Run locally from the Rust implementation directory:

```bash
cd rust
cargo run
```

Run its tests with `cargo test`.

Run formal verification with [Kani](https://model-checking.github.io/kani/):

```bash
cargo install --locked kani-verifier
cd rust
cargo kani
```

## Zig

Run locally with Zig 0.12 or newer:

```bash
cd zig
zig run main.zig
```

Run its tests with `zig test main.zig`.

## Python

Run locally with Python's standard library:

```bash
python -m python.server
```

Run the Python tests:

```bash
python -m unittest discover -s python -p 'test_*.py'
```

## Verify

```bash
npm test
```

## Implementations

The implementations live in:

- TypeScript: [`src/`](src/)
- Go: [`go/`](go/)
- Rust: [`rust/`](rust/)
- Zig: [`zig/`](zig/)
- Python: [`python/`](python/)

Each implementation includes its own run and test instructions.

All implementations expose the same contract:

- `GET /ping` returns `200` with `{"message":"pong","count":n}` and
  increments the in-memory pong counter.
- Other methods on `/ping` return `405` with `Allow: GET`.
- Unknown routes return `404` with `{"error":"Not Found"}`.
