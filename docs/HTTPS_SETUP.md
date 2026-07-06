# HTTPS Local Development Setup with mkcert

This document explains how to set up a local HTTPS certificate for the CashCtrl backend using `mkcert`.

## Prerequisites
- **mkcert** installed via Scoop (Windows) or Homebrew (macOS) or apt (Linux).
- **Git Bash** / **WSL** or any Bash-compatible shell.

## Steps
1. **Install mkcert (if not already installed)**
   ```bash
   scoop install mkcert   # Windows
   # or on macOS: brew install mkcert
   # or on Linux: sudo apt-get install mkcert
   ```
2. **Run the generation script**
   ```bash
   ./scripts/generate_cert.sh
   ```
   This will:
   - Install the local CA (once).
   - Create `certs/nginx.crt` and `certs/nginx.key` for `localhost`.
   - Place them in the `certs/` directory (which is ignored by Git).
3. **Start the Docker stack** (the Nginx service is already configured to use these certs):
   ```bash
   uv run docker compose up --build -d
   ```
4. **Access the application via HTTPS**
   Open your browser at `https://localhost`. You may need to accept the self‑signed certificate warning.

## Notes
- The `certs/` directory is listed in `.gitignore`, so the generated certificates are **not** committed to the repository.
- For production deployments, replace the certificates with a proper SSL certificate (e.g., from Let's Encrypt) and update the Nginx configuration accordingly.
