import assert from "node:assert/strict";
import { createServer } from "node:http";
import { once } from "node:events";
import test from "node:test";
import { createRequestHandler } from "../dist/app.js";

async function startTestServer() {
  const server = createServer(createRequestHandler());
  server.listen(0, "127.0.0.1");
  await once(server, "listening");

  const address = server.address();
  if (address === null || typeof address === "string") {
    throw new Error("Could not determine test server address");
  }

  return { server, url: `http://127.0.0.1:${address.port}` };
}

test("GET /ping returns pong", async (t) => {
  const { server, url } = await startTestServer();
  t.after(() => server.close());

  const response = await fetch(`${url}/ping`);

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { message: "pong", count: 1 });
  assert.match(response.headers.get("content-type"), /application\/json/);
});

test("GET /ping increments the pong counter", async (t) => {
  const { server, url } = await startTestServer();
  t.after(() => server.close());

  await fetch(`${url}/ping`);
  const response = await fetch(`${url}/ping`);

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { message: "pong", count: 2 });
});

test("unknown routes return 404", async (t) => {
  const { server, url } = await startTestServer();
  t.after(() => server.close());

  const response = await fetch(`${url}/unknown`);

  assert.equal(response.status, 404);
  assert.deepEqual(await response.json(), { error: "Not Found" });
});

test("non-GET requests to /ping return 405", async (t) => {
  const { server, url } = await startTestServer();
  t.after(() => server.close());

  const response = await fetch(`${url}/ping`, { method: "POST" });

  assert.equal(response.status, 405);
  assert.equal(response.headers.get("allow"), "GET");
  assert.deepEqual(await response.json(), { error: "Method Not Allowed" });
});
