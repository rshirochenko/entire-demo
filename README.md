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

The equivalent implementations live in [`go/`](go/), [`rust/`](rust/), and
[`python/`](python/). Each directory is self-contained and includes its own
run and test instructions.

All implementations expose the same contract:

- `GET /ping` returns `200` with `{"message":"pong","count":n}` and
  increments the in-memory pong counter.
- Other methods on `/ping` return `405` with `Allow: GET`.
- Unknown routes return `404` with `{"error":"Not Found"}`.
