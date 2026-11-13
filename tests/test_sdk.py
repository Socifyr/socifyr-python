"""Tests for the Socifyr Python SDK (stdlib unittest, no network)."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Make the package importable without an install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from socifyr import (  # noqa: E402
    Socifyr,
    AuthenticationError,
    RateLimitError,
    verify_webhook_signature,
)


def _resp(status=200, json_body=None, is_json=True):
    r = MagicMock()
    r.ok = 200 <= status < 300
    r.status_code = status
    r.headers = {"content-type": "application/json"} if is_json else {"content-type": "text/csv"}
    r.json.return_value = json_body if json_body is not None else {}
    r.text = "" if is_json else "raw,text"
    return r


class ClientTests(unittest.TestCase):
    def _client(self, resp):
        c = Socifyr(api_key="sk_test", workspace_id="ws_1")
        c._http._session = MagicMock()
        c._http._session.request.return_value = resp
        return c

    def test_reconnect_link_posts_to_oauth_route(self):
        c = self._client(_resp(200, {"success": True, "data": {"url": "https://api/x", "expiresIn": 600}}))
        out = c.workspaces.reconnect_link("x-me")
        self.assertEqual(out["expiresIn"], 600)
        args, _ = c._http._session.request.call_args
        self.assertEqual(args[0], "POST")
        self.assertTrue(args[1].endswith("/oauth/connections/x-me/reconnect-link"))

    def test_refresh_connection_posts_to_refresh_route(self):
        c = self._client(_resp(200, {"success": True, "data": {"status": "active"}}))
        out = c.workspaces.refresh_connection("ws_1", "x-me")
        self.assertEqual(out["status"], "active")
        args, _ = c._http._session.request.call_args
        self.assertTrue(args[1].endswith("/workspaces/ws_1/connections/x-me/refresh"))

    def test_refresh_connection_without_workspace_uses_current(self):
        c = self._client(_resp(200, {"success": True, "data": {"status": "active"}}))
        c.workspaces.refresh_connection("x-me")
        args, _ = c._http._session.request.call_args
        self.assertTrue(args[1].endswith("/workspaces/current/connections/x-me/refresh"))

    def test_list_connections_without_workspace_uses_current(self):
        c = self._client(_resp(200, {"success": True, "data": []}))
        c.workspaces.list_connections()
        args, _ = c._http._session.request.call_args
        self.assertTrue(args[1].endswith("/workspaces/current/connections"))

    def test_api_key_alone_is_enough(self):
        with patch.dict("os.environ", {}, clear=True):
            Socifyr(api_key="sk_test")

    def test_requires_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                Socifyr()

    def test_text_unwraps_data_envelope(self):
        c = self._client(_resp(200, {"success": True, "data": {"id": "cnt_1"}}))
        out = c.uploads.text(connections=["x-me"], text="hi")
        self.assertEqual(out, {"id": "cnt_1"})
        args, kwargs = c._http._session.request.call_args
        self.assertEqual(args[0], "POST")
        self.assertTrue(args[1].endswith("/content/text"))
        self.assertEqual(kwargs["json"]["connections"], ["x-me"])
        self.assertTrue(kwargs["json"]["async"])

    def test_bulk_schedule_posts_rows(self):
        c = self._client(_resp(200, {"success": True, "data": {"created": 2, "failed": []}}))
        out = c.uploads.bulk_schedule(rows=[{"text": "a", "connections": ["x-me"], "scheduledAt": "2099-01-01T00:00:00Z"}])
        self.assertEqual(out["created"], 2)
        args, kwargs = c._http._session.request.call_args
        self.assertTrue(args[1].endswith("/content/bulk-schedule"))

    def test_usage_shortcut(self):
        c = self._client(_resp(200, {"success": True, "data": {"tier": "pro"}}))
        self.assertEqual(c.usage()["tier"], "pro")

    def test_auth_error_mapped(self):
        c = self._client(_resp(401, {"success": False, "error": "bad key"}))
        with self.assertRaises(AuthenticationError):
            c.uploads.text(connections=["x-me"], text="hi")

    def test_rate_limit_error_mapped(self):
        c = self._client(_resp(429, {"success": False, "error": "slow down"}))
        with self.assertRaises(RateLimitError):
            c.usage()

    def test_followers_sends_camel_query(self):
        growth = {"totals": {"followers": 10, "change": 2}, "accounts": []}
        c = self._client(_resp(200, {"success": True, "data": growth}))
        out = c.analytics.followers(period="last_3months", connection="x-me")
        self.assertEqual(out, growth)
        args, kwargs = c._http._session.request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].endswith("/analytics/followers"))
        self.assertEqual(kwargs["params"], {"period": "last_3months", "connection": "x-me"})

    def test_accounts_maps_from_to(self):
        c = self._client(_resp(200, {"success": True, "data": {"accounts": []}}))
        c.analytics.accounts(from_date="2026-10-01", to_date="2026-10-31", platform="x")
        args, kwargs = c._http._session.request.call_args
        self.assertTrue(args[1].endswith("/analytics/accounts"))
        self.assertEqual(kwargs["params"], {"from": "2026-10-01", "to": "2026-10-31", "platform": "x"})

    def test_compact_drops_none_fields(self):
        c = self._client(_resp(200, {"success": True, "data": {}}))
        c.uploads.text(connections=["x-me"], text="hi")  # scheduled_at omitted
        _, kwargs = c._http._session.request.call_args
        self.assertNotIn("scheduledAt", kwargs["json"])


class WebhookTests(unittest.TestCase):
    def test_verify_signature_roundtrip(self):
        import hashlib
        import hmac

        secret = "whsec_test"
        body = '{"event":"upload.completed"}'
        sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        self.assertTrue(verify_webhook_signature(body, f"sha256={sig}", secret))
        self.assertTrue(verify_webhook_signature(body, sig, secret))  # bare hex too
        self.assertFalse(verify_webhook_signature(body, "sha256=deadbeef", secret))


if __name__ == "__main__":
    unittest.main()
