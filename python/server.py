"""Run the ping-pong API with Python's standard library."""

import os
from http.server import ThreadingHTTPServer

try:
    from .app import PingRequestHandler
except ImportError:  # Support ``python python/server.py`` as well.
    from app import PingRequestHandler


DEFAULT_PORT = 3000
DEFAULT_HOST = "0.0.0.0"


def parse_port(value: str) -> int:
    """Validate and convert a TCP port value."""
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise ValueError("PORT must be an integer between 1 and 65535") from None

    if not 1 <= port <= 65_535:
        raise ValueError("PORT must be an integer between 1 and 65535")

    return port


def main() -> None:
    host = os.environ.get("HOST", DEFAULT_HOST)
    port = parse_port(os.environ.get("PORT", str(DEFAULT_PORT)))
    server = ThreadingHTTPServer((host, port), PingRequestHandler)

    print(f"Ping-pong API listening on http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
