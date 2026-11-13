"""Resource groups mirroring the TypeScript SDK surface."""

from __future__ import annotations

from typing import Any

from ._http import HttpClient


def _compact(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


class Uploads:
    def __init__(self, http: HttpClient):
        self._http = http

    def text(
        self,
        *,
        connections: list[str],
        text: str,
        scheduled_at: str | None = None,
        timezone: str | None = None,
        first_comment: str | dict | None = None,
        save_draft: bool | None = None,
    ) -> dict:
        """Publish (or schedule) a text post to one or more connections."""
        return self._http.post(
            "/content/text",
            _compact(
                {
                    "connections": connections,
                    "text": text,
                    "scheduledAt": scheduled_at,
                    "timezone": timezone,
                    "firstComment": first_comment,
                    "saveDraft": save_draft,
                    "async": True,
                }
            ),
        )

    def photos(
        self,
        *,
        connections: list[str],
        medias: list[str],
        text: str | None = None,
        scheduled_at: str | None = None,
    ) -> dict:
        """Post photos by media library ID or public URL."""
        return self._http.post(
            "/content/photos",
            _compact(
                {
                    "connections": connections,
                    "medias": medias,
                    "text": text,
                    "scheduledAt": scheduled_at,
                    "async": True,
                }
            ),
        )

    def video(
        self,
        *,
        connections: list[str],
        medias: list[str],
        text: str | None = None,
        scheduled_at: str | None = None,
    ) -> dict:
        """Post a video by media library ID or public URL."""
        return self._http.post(
            "/content/video",
            _compact(
                {
                    "connections": connections,
                    "medias": medias,
                    "text": text,
                    "scheduledAt": scheduled_at,
                    "async": True,
                }
            ),
        )

    def bulk_schedule(
        self, *, rows: list[dict] | None = None, csv: str | None = None
    ) -> dict:
        """Schedule many text posts from rows or a CSV string.

        Returns ``{"created": int, "failed": [{"row": int, "error": str}]}``.
        """
        return self._http.post("/content/bulk-schedule", _compact({"rows": rows, "csv": csv}))

    def get_status(self, request_id: str) -> dict:
        return self._http.get("/content/status", {"requestId": request_id})

    def list(self, **query: Any) -> dict:
        return self._http.get("/content", query)

    def get(self, upload_id: str) -> dict:
        return self._http.get(f"/content/{upload_id}")

    def retry(self, upload_id: str) -> dict:
        return self._http.post(f"/content/{upload_id}/retry")

    def publish_draft(self, upload_id: str) -> dict:
        return self._http.post(f"/content/{upload_id}/publish")


class Workspaces:
    def __init__(self, http: HttpClient):
        self._http = http

    # An API key belongs to one workspace; "current" is that workspace. The
    # optional workspace_id arguments remain only for backward compatibility.

    def list_connections(self, workspace_id: str | None = None) -> list[dict]:
        return self._http.get(f"/workspaces/{workspace_id or 'current'}/connections")

    def refresh_connection(self, *args: str) -> dict:
        """Renew a connection's token: ``refresh_connection("x-me")``. Raises if it can't refresh — use reconnect_link.

        The legacy form ``refresh_connection(workspace_id, connection)`` still works.
        """
        if len(args) == 1:
            workspace_id, connection = None, args[0]
        elif len(args) == 2:
            workspace_id, connection = args
        else:
            raise TypeError("refresh_connection() takes a connection slug or id")
        return self._http.post(f"/workspaces/{workspace_id or 'current'}/connections/{connection}/refresh")

    def reconnect_link(self, connection: str) -> dict:
        """Short-lived single-use URL the owner opens to re-authorize a connection (no dashboard visit)."""
        return self._http.post(f"/oauth/connections/{connection}/reconnect-link")

    def usage(self) -> dict:
        """Current usage vs plan limits for the active workspace."""
        return self._http.get("/usage")


class Analytics:
    def __init__(self, http: HttpClient):
        self._http = http

    def get(self, **query: Any) -> dict:
        return self._http.get("/analytics", query)

    def get_post(self, upload_id: str) -> dict:
        return self._http.get(f"/analytics/post/{upload_id}")

    def sync(self) -> dict:
        return self._http.post("/analytics/sync")

    def followers(
        self,
        *,
        period: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        connection: str | None = None,
        platform: str | None = None,
    ) -> dict:
        """Follower growth per connected account (default window: last 30 days).

        ``period`` is one of last_day, last_week, last_month, last_3months, last_year.
        ``connection`` is a connection slug such as ``instagram-mybrand``.
        """
        return self._http.get(
            "/analytics/followers",
            _account_query(period, from_date, to_date, connection, platform),
        )

    def accounts(
        self,
        *,
        period: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        connection: str | None = None,
        platform: str | None = None,
    ) -> dict:
        """Compare connected accounts: followers, follower change, posts and engagement."""
        return self._http.get(
            "/analytics/accounts",
            _account_query(period, from_date, to_date, connection, platform),
        )


def _account_query(
    period: str | None,
    from_date: str | None,
    to_date: str | None,
    connection: str | None,
    platform: str | None,
) -> dict[str, Any]:
    return _compact(
        {
            "period": period,
            "from": from_date,
            "to": to_date,
            "connection": connection,
            "platform": platform,
        }
    )


class Ai:
    def __init__(self, http: HttpClient):
        self._http = http

    def generate_caption(
        self,
        *,
        upload_type: str,
        platforms: list[str],
        text: str | None = None,
        title: str | None = None,
        description: str | None = None,
        tone: str | None = None,
    ) -> dict:
        """Generate platform-tailored captions (requires a BYOK AI key on the workspace)."""
        return self._http.post(
            "/ai/generate-content",
            _compact(
                {
                    "uploadType": upload_type,
                    "platforms": platforms,
                    "text": text,
                    "title": title,
                    "description": description,
                    "tone": tone,
                }
            ),
        )

    def suggest_hashtags(
        self, *, text: str, platforms: list[str], count: int | None = None
    ) -> dict:
        return self._http.post(
            "/ai/suggest-hashtags",
            _compact({"text": text, "platforms": platforms, "count": count}),
        )
