"""Thin HTTP layer: auth headers, JSON, and typed errors."""

from __future__ import annotations

from typing import Any

import requests

from .errors import SocifyrError, error_from_response


class HttpClient:
    def __init__(self, api_key: str, workspace_id: str | None, base_url: str, timeout: float):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {api_key}"})
        if workspace_id:
            self._session.headers["X-Workspace-Id"] = workspace_id

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        try:
            resp = self._session.request(
                method,
                url,
                params=self._clean(params),
                json=json,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:  # network-level failure
            raise SocifyrError(str(exc)) from exc

        if not resp.ok:
            raise error_from_response(resp.status_code, self._message(resp))

        if resp.headers.get("content-type", "").startswith("application/json"):
            body = resp.json()
            # API wraps success payloads as { success: true, data: <T> }.
            if isinstance(body, dict) and "data" in body and "success" in body:
                return body["data"]
            return body
        return resp.text

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, json: Any | None = None) -> Any:
        return self.request("POST", path, json=json)

    def patch(self, path: str, json: Any | None = None) -> Any:
        return self.request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)

    @staticmethod
    def _clean(params: dict[str, Any] | None) -> dict[str, Any] | None:
        if not params:
            return None
        return {k: v for k, v in params.items() if v is not None}

    @staticmethod
    def _message(resp: requests.Response) -> str:
        try:
            body = resp.json()
            err = body.get("error") if isinstance(body, dict) else None
            if isinstance(err, list):
                return "; ".join(str(e) for e in err)
            if err:
                return str(err)
        except ValueError:
            pass
        return f"Request failed with status {resp.status_code}"
