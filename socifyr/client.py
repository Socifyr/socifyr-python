"""Socifyr client — the entry point for the Python SDK."""

from __future__ import annotations

import os

from ._http import HttpClient
from .resources import Ai, Analytics, Uploads, Workspaces

DEFAULT_BASE_URL = "https://api.socifyr.com/api"


class Socifyr:
    """Socifyr API client.

    Example::

        from socifyr import Socifyr

        client = Socifyr(api_key="sk_...")
        client.uploads.text(connections=["x-me"], text="Hello from Python!")

    The API key falls back to the ``SOCIFYR_API_KEY`` environment variable.
    A key belongs to exactly one workspace, so no workspace id is needed;
    ``workspace_id`` is accepted only for backward compatibility.
    """

    def __init__(
        self,
        api_key: str | None = None,
        workspace_id: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ):
        key = api_key or os.environ.get("SOCIFYR_API_KEY")
        if not key:
            raise ValueError(
                "A Socifyr API key is required (pass api_key or set SOCIFYR_API_KEY)."
            )
        ws = workspace_id or os.environ.get("SOCIFYR_WORKSPACE_ID")
        url = base_url or os.environ.get("SOCIFYR_API_URL") or DEFAULT_BASE_URL

        self._http = HttpClient(key, ws, url, timeout)
        self.uploads = Uploads(self._http)
        self.workspaces = Workspaces(self._http)
        self.analytics = Analytics(self._http)
        self.ai = Ai(self._http)

    def usage(self) -> dict:
        """Shortcut for :meth:`Workspaces.usage`."""
        return self.workspaces.usage()
