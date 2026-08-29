# Ping-pong API

Small HTTP API with TypeScript, Go, and Rust implementations.

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

## Verify

```bash
npm test
```

## Go and Rust

The equivalent implementations live in [`go/`](go/) and [`rust/`](rust/).
Each directory is self-contained and includes its own run and test instructions.

All three implementations expose the same contract:

- `GET /ping` returns `200` with `{"message":"pong"}`.
- Other methods on `/ping` return `405` with `Allow: GET`.
- Unknown routes return `404` with `{"error":"Not Found"}`.
