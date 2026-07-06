#!/usr/bin/env bash
set -e

# Ensure mkcert is installed (via Scoop on Windows). This script works in WSL/git bash environments.
if ! command -v mkcert >/dev/null 2>&1; then
  echo "mkcert not found in PATH. Please install it via Scoop: scoop install mkcert" >&2
  exit 1
fi

# Install the local CA if not already installed
echo "Installing local CA (if not already installed)..."
mkcert -install

# Create certs directory if it doesn't exist
CERT_DIR="$(cd "$(dirname "$0")/.." && pwd)/certs"
mkdir -p "$CERT_DIR"

# Generate certificate for localhost (and 127.0.0.1, ::1)
echo "Generating localhost certificate..."
mkcert -cert-file "$CERT_DIR/nginx.crt" -key-file "$CERT_DIR/nginx.key" localhost 127.0.0.1 ::1

echo "Certificates generated at $CERT_DIR/nginx.crt and $CERT_DIR/nginx.key"
