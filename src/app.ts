import type { IncomingMessage, ServerResponse } from "node:http";

type JsonResponse = Record<string, string | number>;
export type Logger = (message: string) => void;

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

export function createRequestHandler(logger: Logger = console.log) {
  let pongCount = 0;

  return function requestHandler(
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

      pongCount += 1;
      logger(`ping received; pong count=${pongCount}`);
      sendJson(response, 200, { message: "pong", count: pongCount });
      return;
    }

    sendJson(response, 404, { error: "Not Found" });
  };
}

export const requestHandler = createRequestHandler();
