import type { IncomingMessage, ServerResponse } from "node:http";

type JsonResponse = Record<string, string>;

function sendJson(
  response: ServerResponse,
  statusCode: number,
  body: JsonResponse,
): void {
  const payload = JSON.stringify(body);

  response.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(payload),
  });
  response.end(payload);
}

export function requestHandler(
  request: IncomingMessage,
  response: ServerResponse,
): void {
  const requestUrl = new URL(
    request.url ?? "/",
    `http://${request.headers.host ?? "localhost"}`,
  );

  if (requestUrl.pathname === "/ping") {
    if (request.method !== "GET") {
      response.setHeader("Allow", "GET");
      sendJson(response, 405, { error: "Method Not Allowed" });
      return;
    }

    sendJson(response, 200, { message: "pong" });
    return;
  }

  sendJson(response, 404, { error: "Not Found" });
}
