package main

import (
	"errors"
	"log"
	"net"
	"net/http"
	"os"
	"strconv"
)

const defaultPort = 3000

func main() {
	host := os.Getenv("HOST")
	if host == "" {
		host = "0.0.0.0"
	}

	port, err := configuredPort()
	if err != nil {
		log.Fatal(err)
	}

	address := net.JoinHostPort(host, strconv.Itoa(port))
	log.Printf("Ping-pong API listening on http://%s", address)
	log.Fatal(http.ListenAndServe(address, newHandler()))
}

func configuredPort() (int, error) {
	value, configured := os.LookupEnv("PORT")
	if !configured {
		return defaultPort, nil
	}

	port, err := strconv.Atoi(value)
	if err != nil || port < 1 || port > 65_535 {
		return 0, errors.New("PORT must be an integer between 1 and 65535")
	}

	return port, nil
}
