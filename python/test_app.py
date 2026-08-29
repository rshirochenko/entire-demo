import unittest
from http.client import HTTPConnection
from io import BytesIO
from threading import Thread
from http.server import ThreadingHTTPServer

try:
    from .app import (
        JSON_CONTENT_TYPE,
        PingRequestHandler,
        response_for,
    )
    from .server import parse_port
except ImportError:
    from app import JSON_CONTENT_TYPE, PingRequestHandler, response_for
    from server import parse_port


class ResponseForTests(unittest.TestCase):
    def test_get_ping_returns_pong(self):
        response = response_for("GET", "/ping?from=test")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, JSON_CONTENT_TYPE)
        self.assertEqual(response.body, '{"message":"pong"}')
        self.assertIsNone(response.allow())

    def test_non_get_ping_returns_method_not_allowed(self):
        response = response_for("POST", "/ping")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.body, '{"error":"Method Not Allowed"}')
        self.assertEqual(response.allow(), "GET")

    def test_unknown_route_returns_not_found(self):
        response = response_for("GET", "/unknown")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body, '{"error":"Not Found"}')
        self.assertIsNone(response.allow())

    def test_trailing_slash_is_not_the_ping_route(self):
        response = response_for("GET", "/ping/")

        self.assertEqual(response.status_code, 404)

    def test_write_to_emits_json_headers_and_body(self):
        output = BytesIO()

        response_for("POST", "/ping").write_to(output)

        self.assertEqual(
            output.getvalue().decode("utf-8"),
            "".join(
                (
                    "HTTP/1.1 405 Method Not Allowed\r\n",
                    "Content-Type: application/json; charset=utf-8\r\n",
                    "Content-Length: 30\r\n",
                    "Allow: GET\r\n",
                    "Connection: close\r\n",
                    "\r\n",
                    '{"error":"Method Not Allowed"}',
                )
            ),
        )


class PortTests(unittest.TestCase):
    def test_parse_port_accepts_valid_port(self):
        self.assertEqual(parse_port("8080"), 8080)

    def test_parse_port_rejects_invalid_port(self):
        for value in ("0", "65536", "not-a-port"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "1 and 65535"):
                    parse_port(value)


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), PingRequestHandler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path):
        connection = HTTPConnection("127.0.0.1", self.port)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            body = response.read()
            return response, body
        finally:
            connection.close()

    def test_get_ping_returns_json(self):
        response, body = self.request("GET", "/ping?from=test")

        self.assertEqual(response.status, 200)
        self.assertEqual(body, b'{"message":"pong"}')
        self.assertEqual(response.getheader("Content-Type"), JSON_CONTENT_TYPE)
        self.assertEqual(response.getheader("Content-Length"), "18")

    def test_non_get_ping_returns_405_and_allow_header(self):
        response, body = self.request("POST", "/ping")

        self.assertEqual(response.status, 405)
        self.assertEqual(response.getheader("Allow"), "GET")
        self.assertEqual(body, b'{"error":"Method Not Allowed"}')

    def test_unknown_route_returns_404(self):
        response, body = self.request("GET", "/unknown")

        self.assertEqual(response.status, 404)
        self.assertEqual(body, b'{"error":"Not Found"}')


if __name__ == "__main__":
    unittest.main()
