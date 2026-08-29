# Ping-pong API

Small HTTP API with TypeScript, Rust, and Python implementations.

## TypeScript

Run locally:

```bash
npm install
npm run dev
```

The server listens on port `3000` by default. Set `PORT` or `HOST` to change
the binding.

## Endpoint

```bash
curl http://localhost:3000/ping
# {"message":"pong"}
```

Only `GET /ping` is supported. Unknown routes return `404`, and other methods
on `/ping` return `405`.

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

## Rust and Python

The equivalent implementations live in [`rust/`](rust/) and [`python/`](python/).
Each directory is self-contained and includes its own run and test instructions.

All implementations expose the same contract:

- `GET /ping` returns `200` with `{"message":"pong"}`.
- Other methods on `/ping` return `405` with `Allow: GET`.
- Unknown routes return `404` with `{"error":"Not Found"}`.
