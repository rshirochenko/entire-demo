import { createServer } from "node:http";
import { requestHandler } from "./app.js";

const defaultPort = 3000;
const port = parsePort(process.env.PORT ?? String(defaultPort));
const host = process.env.HOST ?? "0.0.0.0";

const server = createServer(requestHandler);

server.listen(port, host, () => {
  console.log(`Ping-pong API listening on http://${host}:${port}`);
});

function parsePort(value: string): number {
  const parsedPort = Number(value);

  if (!Number.isInteger(parsedPort) || parsedPort < 1 || parsedPort > 65_535) {
    throw new Error("PORT must be an integer between 1 and 65535");
  }

  return parsedPort;
}
