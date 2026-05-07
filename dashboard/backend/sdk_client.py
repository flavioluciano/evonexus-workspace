"""Internal SDK client for calling the dashboard API from skills/agents.

Resolves base URL from environment in this order:
  1. EVONEXUS_API_URL (full URL, e.g. https://evo.example.com)
  2. http://localhost:$FLASK_PORT
  3. http://localhost:8080

Auto-injects Authorization: Bearer $DASHBOARD_API_TOKEN when present.

Usage from a skill:
    from dashboard.backend.sdk_client import evo
    ticket = evo.post("/api/tickets", {"title": "...", "assignee_agent": "zara-cs"})
    goals = evo.get("/api/goals")
"""
from __future__ import annotations

import os
from typing import Any

import requests


class EvoClient:
    def __init__(self) -> None:
        self._session = requests.Session()
        url = os.environ.get("EVONEXUS_API_URL", "").strip()
        if not url:
            port = os.environ.get("FLASK_PORT", "8080").strip() or "8080"
            url = f"http://localhost:{port}"
        self.base_url = url.rstrip("/")
        token = os.environ.get("DASHBOARD_API_TOKEN", "").strip()
        if token:
            self._session.headers["Authorization"] = f"Bearer {token}"
        self._session.headers["Content-Type"] = "application/json"

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        r = self._session.get(self._url(path), params=params, timeout=30)
        r.raise_for_status()
        return r.json() if r.content else None

    def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        r = self._session.post(self._url(path), json=json or {}, timeout=30)
        r.raise_for_status()
        return r.json() if r.content else None

    def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        r = self._session.patch(self._url(path), json=json or {}, timeout=30)
        r.raise_for_status()
        return r.json() if r.content else None

    def delete(self, path: str) -> Any:
        r = self._session.delete(self._url(path), timeout=30)
        r.raise_for_status()
        return r.json() if r.content else None


evo = EvoClient()
