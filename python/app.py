"""HTTP routing and response handling for the ping-pong API."""

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from typing import BinaryIO, Optional
from urllib.parse import urlsplit

JSON_CONTENT_TYPE = "application/json; charset=utf-8"
PONG_BODY = '{"message":"pong"}'
NOT_FOUND_BODY = '{"error":"Not Found"}'
METHOD_NOT_ALLOWED_BODY = '{"error":"Method Not Allowed"}'


@dataclass(frozen=True)
class HttpResponse:
    """A JSON response produced by the route matcher."""

    status_code: int
    reason_phrase: str
    body: str
    allow_get: bool = False

    @property
    def content_type(self) -> str:
        return JSON_CONTENT_TYPE

    @property
    def content_length(self) -> int:
        return len(self.body.encode("utf-8"))

    def allow(self) -> Optional[str]:
        return "GET" if self.allow_get else None

    def write_to(self, writer: BinaryIO) -> None:
        """Write this response in HTTP/1.1 wire format."""
        headers = [
            f"HTTP/1.1 {self.status_code} {self.reason_phrase}",
            f"Content-Type: {self.content_type}",
            f"Content-Length: {self.content_length}",
        ]
        if self.allow_get:
            headers.append("Allow: GET")
        headers.extend(("Connection: close", "", ""))

        writer.write("\r\n".join(headers).encode("ascii"))
        writer.write(self.body.encode("utf-8"))
        writer.flush()


def response_for(method: str, target: str) -> HttpResponse:
    """Return the API response for an HTTP method and request target."""
    path = urlsplit(target).path or "/"

    if path == "/ping":
        if method == "GET":
            return HttpResponse(200, "OK", PONG_BODY)

        return HttpResponse(
            405,
            "Method Not Allowed",
            METHOD_NOT_ALLOWED_BODY,
            allow_get=True,
        )

    return HttpResponse(404, "Not Found", NOT_FOUND_BODY)


class PingRequestHandler(BaseHTTPRequestHandler):
    """Adapt ``response_for`` to Python's standard HTTP server."""

    protocol_version = "HTTP/1.1"

    def __getattr__(self, name: str):
        # BaseHTTPRequestHandler looks up do_<METHOD> dynamically. Returning
        # the shared handler makes custom methods follow the same 405 contract.
        if name.startswith("do_"):
            return self._handle_request
        raise AttributeError(name)

    def _handle_request(self) -> None:
        response = response_for(self.command, self.path)

        self.send_response(response.status_code, response.reason_phrase)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(response.content_length))
        if response.allow_get:
            self.send_header("Allow", "GET")
        self.send_header("Connection", "close")
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(response.body.encode("utf-8"))

        self.close_connection = True
