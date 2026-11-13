"""Webhook signature verification (HMAC-SHA256, GitHub/Svix-style)."""

from __future__ import annotations

import hashlib
import hmac


def verify_webhook_signature(payload: str | bytes, signature: str, secret: str) -> bool:
    """Verify an ``X-Webhook-Signature`` header (``sha256=<hex>``) against the raw body.

    Pass the exact raw request body (string or bytes) — not a re-serialized dict.
    """
    body = payload.encode("utf-8") if isinstance(payload, str) else payload
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    provided = signature[7:] if signature.startswith("sha256=") else signature
    return hmac.compare_digest(expected, provided)
