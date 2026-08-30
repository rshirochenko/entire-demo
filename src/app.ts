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

    if (requestUrl.pathname === "/multiply") {
      if (request.method !== "GET") {
        response.setHeader("Allow", "GET");
        sendJson(response, 405, { error: "Method Not Allowed" });
        return;
      }

      const aValue = requestUrl.searchParams.get("a");
      const bValue = requestUrl.searchParams.get("b");
      const a = Number(aValue);
      const b = Number(bValue);

      if (aValue === null || bValue === null || !Number.isInteger(a) || !Number.isInteger(b)) {
        sendJson(response, 400, { error: "a and b must be integers" });
        return;
      }

      sendJson(response, 200, { result: a * b });
      return;
    }

    sendJson(response, 404, { error: "Not Found" });
  };
}

export const requestHandler = createRequestHandler();
