#!/usr/bin/env python3
"""Bling OAuth2 Authorization Code flow — one-time CLI setup.

Opens the browser to authorize, captures the code via a local callback server,
exchanges it for access_token + refresh_token, and persists both to .env.

Usage:
    python3 bling_auth.py

Prerequisites (in .env):
    BLING_CLIENT_ID=<from developer.bling.com.br app>
    BLING_CLIENT_SECRET=<from developer.bling.com.br app>

The app on developer.bling.com.br must have redirect URI set to:
    http://localhost:8787/callback
"""

import base64
import http.server
import json
import os
import secrets
import socketserver
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path


CALLBACK_HOST = "localhost"
CALLBACK_PORT = 8787
CALLBACK_PATH = "/callback"
REDIRECT_URI = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}{CALLBACK_PATH}"

AUTHORIZE_URL = "https://www.bling.com.br/Api/v3/oauth/authorize"
TOKEN_URL = "https://www.bling.com.br/Api/v3/oauth/token"


# ── .env helpers ─────────────────────────────────────

def _env_path() -> Path:
    return Path(__file__).resolve().parents[4] / ".env"


def _load_dotenv():
    path = _env_path()
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k and k not in os.environ:
                os.environ[k] = v


def _set_env_var(key: str, value: str):
    path = _env_path()
    lines = []
    found = False
    if path.exists():
        with open(path) as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    k = stripped.split("=", 1)[0].strip()
                    if k == key:
                        lines.append(f"{key}={value}\n")
                        found = True
                        continue
                lines.append(line if line.endswith("\n") else line + "\n")
    if not found:
        lines.append(f"{key}={value}\n")
    with open(path, "w") as f:
        f.writelines(lines)


# ── Callback server ──────────────────────────────────

_received: dict = {}
_done = threading.Event()


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != CALLBACK_PATH:
            self.send_response(404)
            self.end_headers()
            return

        qs = urllib.parse.parse_qs(parsed.query)
        code = qs.get("code", [""])[0]
        state = qs.get("state", [""])[0]
        error = qs.get("error", [""])[0]

        _received["code"] = code
        _received["state"] = state
        _received["error"] = error

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        if error:
            html = f"<h1>Erro: {error}</h1><p>Pode fechar esta aba.</p>"
        elif code:
            html = "<h1>OK — pode fechar esta aba.</h1><p>Voltando pro terminal…</p>"
        else:
            html = "<h1>Callback sem code.</h1>"
        self.wfile.write(html.encode())
        _done.set()


def _start_callback_server():
    httpd = socketserver.TCPServer((CALLBACK_HOST, CALLBACK_PORT), _CallbackHandler)
    httpd.timeout = 1
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


# ── OAuth flow ───────────────────────────────────────

def _exchange_code(code: str, client_id: str, client_secret: str) -> dict:
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic}",
            "Accept": "1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.stderr.write(f"Token exchange failed ({e.code}): {body}\n")
        sys.exit(1)


def main():
    _load_dotenv()

    client_id = os.environ.get("BLING_CLIENT_ID", "").strip()
    client_secret = os.environ.get("BLING_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        print("ERROR: BLING_CLIENT_ID and BLING_CLIENT_SECRET must be set in .env")
        print()
        print("Steps to create a Bling app:")
        print("  1. Go to https://developer.bling.com.br")
        print("  2. Login with your Bling account")
        print("  3. Create a new application")
        print(f"  4. Set the redirect URI to: {REDIRECT_URI}")
        print("  5. Copy the Client ID and Client Secret into .env:")
        print("       BLING_CLIENT_ID=...")
        print("       BLING_CLIENT_SECRET=...")
        print("  6. Run `make bling-auth` again")
        sys.exit(1)

    state = secrets.token_urlsafe(24)
    auth_url = (
        f"{AUTHORIZE_URL}?"
        + urllib.parse.urlencode({
            "response_type": "code",
            "client_id": client_id,
            "state": state,
            "redirect_uri": REDIRECT_URI,
        })
    )

    print("→ Starting local callback server on", REDIRECT_URI)
    httpd = _start_callback_server()

    print("→ Opening browser for authorization…")
    print("  (if it doesn't open, paste this URL manually:)")
    print(" ", auth_url)
    print()
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("Waiting for callback (Ctrl+C to cancel)…")
    try:
        _done.wait(timeout=300)  # 5 min
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
    finally:
        httpd.shutdown()

    if not _received.get("code"):
        err = _received.get("error", "timeout or no code")
        print(f"ERROR: no authorization code received ({err})")
        sys.exit(1)

    if _received.get("state") != state:
        print("ERROR: state mismatch — possible CSRF, aborting")
        sys.exit(1)

    print("→ Got code, exchanging for tokens…")
    tokens = _exchange_code(_received["code"], client_id, client_secret)

    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")
    expires_in = tokens.get("expires_in", "?")

    if not access_token or not refresh_token:
        print(f"ERROR: missing tokens in response: {tokens}")
        sys.exit(1)

    _set_env_var("BLING_ACCESS_TOKEN", access_token)
    _set_env_var("BLING_REFRESH_TOKEN", refresh_token)

    print("→ Saved to .env:")
    print(f"    BLING_ACCESS_TOKEN=...{access_token[-8:]}")
    print(f"    BLING_REFRESH_TOKEN=...{refresh_token[-8:]}")
    print(f"    (access_token expires in {expires_in}s; refresh is automatic from now on)")
    print()
    print("✓ Done. The int-bling skill will auto-refresh the access token when it expires.")


if __name__ == "__main__":
    main()
