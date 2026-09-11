"""HTTP API client for communicating with 9Router local daemon."""

from typing import Any, Dict, Optional
import httpx
from .auth import CLI_TOKEN_HEADER, get_cli_token


class RouterClient:
    def __init__(self, base_url: str = "http://localhost:20128", token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token or get_cli_token()

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers[CLI_TOKEN_HEADER] = self.token
        return headers

    def request(self, method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.request(method, url, headers=self._headers(), json=json)
            if resp.status_code >= 400:
                try:
                    err_msg = resp.json().get("error") or resp.text
                except Exception:
                    err_msg = resp.text
                raise RuntimeError(f"API {method} {path} failed ({resp.status_code}): {err_msg}")
            try:
                return resp.json()
            except Exception:
                return resp.text

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", path, json=json)

    def put(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PUT", path, json=json)

    def patch(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)
