use std::io::{self, BufRead, BufReader, Write};
use std::net::TcpStream;

const JSON_CONTENT_TYPE: &str = "application/json; charset=utf-8";

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct HttpResponse {
    status_code: u16,
    reason_phrase: &'static str,
    body: &'static str,
    allow_get: bool,
}

impl HttpResponse {
    pub fn status_code(self) -> u16 {
        self.status_code
    }

    pub fn content_type(self) -> &'static str {
        JSON_CONTENT_TYPE
    }

    pub fn body(self) -> &'static str {
        self.body
    }

    pub fn allow(self) -> Option<&'static str> {
        self.allow_get.then_some("GET")
    }

    pub fn write_to<W: Write>(self, writer: &mut W) -> io::Result<()> {
        write!(
            writer,
            "HTTP/1.1 {} {}\r\nContent-Type: {}\r\nContent-Length: {}\r\n",
            self.status_code,
            self.reason_phrase,
            JSON_CONTENT_TYPE,
            self.body.len()
        )?;

        if self.allow_get {
            writer.write_all(b"Allow: GET\r\n")?;
        }

        writer.write_all(b"Connection: close\r\n\r\n")?;
        writer.write_all(self.body.as_bytes())?;
        writer.flush()
    }
}

pub fn response_for(method: &str, target: &str) -> HttpResponse {
    let path = target.split(['?', '#']).next().unwrap_or(target);

    if path == "/ping" {
        if method == "GET" {
            return HttpResponse {
                status_code: 200,
                reason_phrase: "OK",
                body: r#"{"message":"pong"}"#,
                allow_get: false,
            };
        }

        return HttpResponse {
            status_code: 405,
            reason_phrase: "Method Not Allowed",
            body: r#"{"error":"Method Not Allowed"}"#,
            allow_get: true,
        };
    }

    HttpResponse {
        status_code: 404,
        reason_phrase: "Not Found",
        body: r#"{"error":"Not Found"}"#,
        allow_get: false,
    }
}

pub fn handle_connection(mut stream: TcpStream) -> io::Result<()> {
    let mut request_line = String::new();
    {
        let mut reader = BufReader::new(&mut stream);
        if reader.read_line(&mut request_line)? == 0 {
            return Ok(());
        }
    }

    let mut request_parts = request_line.split_whitespace();
    let method = request_parts.next().unwrap_or("");
    let target = request_parts.next().unwrap_or("/");

    response_for(method, target).write_to(&mut stream)
}

#[cfg(test)]
mod tests {
    use super::{response_for, HttpResponse};

    fn assert_json_response(response: HttpResponse, status_code: u16, body: &'static str) {
        assert_eq!(response.status_code(), status_code);
        assert_eq!(response.content_type(), "application/json; charset=utf-8");
        assert_eq!(response.body(), body);
    }

    #[test]
    fn get_ping_returns_pong_json() {
        let response = response_for("GET", "/ping?from=test");

        assert_json_response(response, 200, r#"{"message":"pong"}"#);
        assert_eq!(response.allow(), None);
    }

    #[test]
    fn non_get_ping_returns_method_not_allowed_with_allow_header() {
        let response = response_for("POST", "/ping");

        assert_json_response(response, 405, r#"{"error":"Method Not Allowed"}"#);
        assert_eq!(response.allow(), Some("GET"));
    }

    #[test]
    fn unknown_route_returns_not_found_without_allow_header() {
        let response = response_for("GET", "/unknown");

        assert_json_response(response, 404, r#"{"error":"Not Found"}"#);
        assert_eq!(response.allow(), None);
    }

    #[test]
    fn response_writes_http_json_headers_and_body() {
        let response = response_for("POST", "/ping");
        let mut wire_response = Vec::new();

        response.write_to(&mut wire_response).unwrap();

        assert_eq!(
            String::from_utf8(wire_response).unwrap(),
            concat!(
                "HTTP/1.1 405 Method Not Allowed\r\n",
                "Content-Type: application/json; charset=utf-8\r\n",
                "Content-Length: 30\r\n",
                "Allow: GET\r\n",
                "Connection: close\r\n",
                "\r\n",
                "{\"error\":\"Method Not Allowed\"}"
            )
        );
    }
}
