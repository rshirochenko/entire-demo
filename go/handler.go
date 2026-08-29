package main

import (
	"encoding/json"
	"net/http"
	"strconv"
)

const jsonContentType = "application/json; charset=utf-8"

type messageResponse struct {
	Message string `json:"message"`
}

type errorResponse struct {
	Error string `json:"error"`
}

// newHandler returns the HTTP handler for the ping-pong API.
func newHandler() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		path := "/"
		if r.URL != nil {
			// EscapedPath keeps encoded paths distinct from their decoded form,
			// matching the TypeScript implementation's pathname comparison.
			path = r.URL.EscapedPath()
		}

		if path != "/ping" {
			writeJSON(w, http.StatusNotFound, errorResponse{Error: "Not Found"})
			return
		}

		if r.Method != http.MethodGet {
			w.Header().Set("Allow", http.MethodGet)
			writeJSON(w, http.StatusMethodNotAllowed, errorResponse{Error: "Method Not Allowed"})
			return
		}

		writeJSON(w, http.StatusOK, messageResponse{Message: "pong"})
	})
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	payload, err := json.Marshal(value)
	if err != nil {
		// The API only passes fixed response structs, so this cannot occur.
		panic("failed to marshal JSON response: " + err.Error())
	}

	w.Header().Set("Content-Type", jsonContentType)
	w.Header().Set("Content-Length", strconv.Itoa(len(payload)))
	w.WriteHeader(status)
	_, _ = w.Write(payload)
}
