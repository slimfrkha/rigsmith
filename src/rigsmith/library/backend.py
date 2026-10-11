"""Backend development: APIs, load testing, local TLS."""

from rigsmith.library._util import tool

tool("grpcurl", "curl for gRPC: call and inspect gRPC services from the terminal.")
tool("websocat", "netcat/curl for WebSockets.")
tool("k6", "Scriptable load testing (JavaScript scenarios).")
tool("oha", "HTTP load generator with a live TUI: `oha -z 30s https://…`.")
tool("mkcert", "Locally trusted development TLS certificates: `mkcert -install && mkcert localhost`.")
