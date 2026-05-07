#!/usr/bin/env python3
"""Bling ERP API v3 Client — with automatic OAuth2 token refresh.

Mirrors the pattern used by int-youtube/scripts/youtube_client.py:
- Loads .env from project root
- Reads access_token, refresh_token, client_id, client_secret from env
- Auto-retries once on HTTP 401 by refreshing the access token
- Persists new access_token back to .env and os.environ

Usage:
    python3 bling_client.py GET /produtos --params page=1 limit=50
    python3 bling_client.py POST /contatos --body '{"nome":"Foo","tipo":"F"}'
    python3 bling_client.py GET /pedidos/vendas --params dataInicial=2026-01-01
"""

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path


def _load_dotenv():
    """Load .env from project root."""
    env_path = Path(__file__).resolve().parents[4] / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()

BASE_URL = "https://www.bling.com.br/Api/v3"
TOKEN_URL = "https://www.bling.com.br/Api/v3/oauth/token"


# ── Env helpers ──────────────────────────────────────

def _env_path() -> Path:
    return Path(__file__).resolve().parents[4] / ".env"


def _set_env_var(key: str, value: str):
    """Upsert a key in .env."""
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


# ── OAuth refresh ────────────────────────────────────

def _refresh_access_token() -> str:
    """Exchange refresh_token for a new access_token + refresh_token.
    Persists both to .env and os.environ. Returns new access_token or empty string.

    Bling rotates the refresh_token on every refresh, so the new one must also be saved.
    """
    import base64

    refresh_token = os.environ.get("BLING_REFRESH_TOKEN", "")
    client_id = os.environ.get("BLING_CLIENT_ID", "")
    client_secret = os.environ.get("BLING_CLIENT_SECRET", "")

    if not (refresh_token and client_id and client_secret):
        sys.stderr.write(
            "[bling] cannot refresh: missing BLING_REFRESH_TOKEN / BLING_CLIENT_ID / BLING_CLIENT_SECRET. "
            "Run `make bling-auth` to set up OAuth.\n"
        )
        return ""

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
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
            tok = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        sys.stderr.write(f"[bling] refresh failed ({e.code}): {body}\n")
        return ""
    except Exception as e:
        sys.stderr.write(f"[bling] refresh error: {e}\n")
        return ""

    new_access = tok.get("access_token", "")
    new_refresh = tok.get("refresh_token", "")

    if not new_access:
        return ""

    _set_env_var("BLING_ACCESS_TOKEN", new_access)
    os.environ["BLING_ACCESS_TOKEN"] = new_access

    if new_refresh:
        _set_env_var("BLING_REFRESH_TOKEN", new_refresh)
        os.environ["BLING_REFRESH_TOKEN"] = new_refresh

    return new_access


# ── API call ─────────────────────────────────────────

def _api_call(method: str, path: str, params: dict = None, body: dict = None, _retried: bool = False):
    """Call Bling API v3. Auto-refreshes on 401 once."""
    access_token = os.environ.get("BLING_ACCESS_TOKEN", "")
    if not access_token:
        sys.stderr.write("[bling] missing BLING_ACCESS_TOKEN — run `make bling-auth`\n")
        sys.exit(1)

    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})

    data = None
    if body is not None:
        data = json.dumps(body).encode()

    req = urllib.request.Request(
        url,
        data=data,
        method=method.upper(),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        if e.code == 401 and not _retried:
            new_token = _refresh_access_token()
            if new_token:
                return _api_call(method, path, params, body, _retried=True)
        body_txt = e.read().decode("utf-8", "replace")[:500]
        sys.stderr.write(f"[bling] {method} {path} → HTTP {e.code}: {body_txt}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"[bling] {method} {path} → {e}\n")
        sys.exit(1)


# ── CLI ──────────────────────────────────────────────

def _parse_params(args: list[str]) -> dict:
    """Parse key=value pairs into a dict."""
    out = {}
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            out[k] = v
    return out


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(
            "Usage:\n"
            "  bling_client.py GET /produtos --params page=1 limit=50\n"
            "  bling_client.py POST /contatos --body '{\"nome\":\"Foo\"}'\n"
            "  bling_client.py PUT /produtos/123 --body '{\"nome\":\"Bar\"}'\n"
        )
        sys.exit(1)

    method = sys.argv[1].upper()
    path = sys.argv[2]
    params = {}
    body = None

    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--params":
            params = _parse_params(sys.argv[i + 1 : i + 1 + _count_kv(sys.argv[i + 1 :])])
            i += 1 + _count_kv(sys.argv[i + 1 :])
        elif arg == "--body":
            body = json.loads(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    result = _api_call(method, path, params=params, body=body)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def _count_kv(args: list[str]) -> int:
    n = 0
    for a in args:
        if a.startswith("--") or "=" not in a:
            break
        n += 1
    return n


if __name__ == "__main__":
    main()
