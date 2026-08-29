use std::env;
use std::io;
use std::net::TcpListener;
use std::thread;

use ping_pong_api::handle_connection;

fn main() -> io::Result<()> {
    let host = env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_owned());
    let port = parse_port(&env::var("PORT").unwrap_or_else(|_| "3000".to_owned()))?;
    let listener = TcpListener::bind((host.as_str(), port))?;

    println!("Ping-pong API listening on http://{host}:{port}");

    for incoming in listener.incoming() {
        match incoming {
            Ok(stream) => {
                thread::spawn(move || {
                    if let Err(error) = handle_connection(stream) {
                        eprintln!("connection error: {error}");
                    }
                });
            }
            Err(error) => eprintln!("accept error: {error}"),
        }
    }

    Ok(())
}

fn parse_port(value: &str) -> io::Result<u16> {
    value
        .parse::<u16>()
        .ok()
        .filter(|port| *port > 0)
        .ok_or_else(|| {
            io::Error::new(
                io::ErrorKind::InvalidInput,
                "PORT must be an integer between 1 and 65535",
            )
        })
}
