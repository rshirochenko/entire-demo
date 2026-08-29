package main

import (
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
)

func TestPingPongHandler(t *testing.T) {
	tests := []struct {
		name        string
		method      string
		target      string
		wantStatus  int
		wantBody    string
		wantAllow   string
		wantContent string
	}{
		{
			name:        "GET /ping",
			method:      http.MethodGet,
			target:      "/ping",
			wantStatus:  http.StatusOK,
			wantBody:    `{"message":"pong"}`,
			wantContent: jsonContentType,
		},
		{
			name:        "GET /ping with query string",
			method:      http.MethodGet,
			target:      "/ping?source=test",
			wantStatus:  http.StatusOK,
			wantBody:    `{"message":"pong"}`,
			wantContent: jsonContentType,
		},
		{
			name:        "POST /ping",
			method:      http.MethodPost,
			target:      "/ping",
			wantStatus:  http.StatusMethodNotAllowed,
			wantBody:    `{"error":"Method Not Allowed"}`,
			wantAllow:   http.MethodGet,
			wantContent: jsonContentType,
		},
		{
			name:        "unknown route",
			method:      http.MethodGet,
			target:      "/unknown",
			wantStatus:  http.StatusNotFound,
			wantBody:    `{"error":"Not Found"}`,
			wantContent: jsonContentType,
		},
		{
			name:        "encoded ping route",
			method:      http.MethodGet,
			target:      "/%70ing",
			wantStatus:  http.StatusNotFound,
			wantBody:    `{"error":"Not Found"}`,
			wantContent: jsonContentType,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			request := httptest.NewRequest(test.method, test.target, nil)
			response := httptest.NewRecorder()

			newHandler().ServeHTTP(response, request)

			result := response.Result()
			defer result.Body.Close()

			if result.StatusCode != test.wantStatus {
				t.Fatalf("status = %d, want %d", result.StatusCode, test.wantStatus)
			}

			body, err := io.ReadAll(result.Body)
			if err != nil {
				t.Fatalf("read response body: %v", err)
			}
			if string(body) != test.wantBody {
				t.Errorf("body = %q, want %q", body, test.wantBody)
			}

			if contentType := result.Header.Get("Content-Type"); contentType != test.wantContent {
				t.Errorf("Content-Type = %q, want %q", contentType, test.wantContent)
			}

			if allow := result.Header.Get("Allow"); allow != test.wantAllow {
				t.Errorf("Allow = %q, want %q", allow, test.wantAllow)
			}
		})
	}
}

func TestConfiguredPort(t *testing.T) {
	tests := []struct {
		name  string
		value *string
		want  int
		err   bool
	}{
		{name: "unset uses default", value: nil, want: defaultPort},
		{name: "valid port", value: stringPtr("8080"), want: 8080},
		{name: "zero is invalid", value: stringPtr("0"), err: true},
		{name: "port above range is invalid", value: stringPtr("65536"), err: true},
		{name: "non-numeric port is invalid", value: stringPtr("not-a-port"), err: true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if test.value == nil {
				t.Setenv("PORT", "")
				if err := os.Unsetenv("PORT"); err != nil {
					t.Fatalf("unset PORT: %v", err)
				}
			} else {
				t.Setenv("PORT", *test.value)
			}

			got, err := configuredPort()
			if (err != nil) != test.err {
				t.Fatalf("configuredPort() error = %v, want error: %t", err, test.err)
			}
			if !test.err && got != test.want {
				t.Errorf("configuredPort() = %d, want %d", got, test.want)
			}
		})
	}
}

func stringPtr(value string) *string {
	return &value
}
