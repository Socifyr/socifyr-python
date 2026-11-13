"""Typed errors for the Socifyr SDK."""

from __future__ import annotations


class SocifyrError(Exception):
    """Base class for all Socifyr SDK errors."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.message = message
        self.status = status


class AuthenticationError(SocifyrError):
    """401/403 — missing or invalid API key."""


class RateLimitError(SocifyrError):
    """429 — too many requests."""


class UsageLimitError(SocifyrError):
    """402/forbidden — a plan usage limit was reached."""


class NotFoundError(SocifyrError):
    """404 — the resource does not exist."""


class ValidationError(SocifyrError):
    """400 — request validation failed."""


def error_from_response(status: int, message: str) -> SocifyrError:
    if status in (401, 403):
        return AuthenticationError(message, status)
    if status == 429:
        return RateLimitError(message, status)
    if status == 402:
        return UsageLimitError(message, status)
    if status == 404:
        return NotFoundError(message, status)
    if status == 400:
        return ValidationError(message, status)
    return SocifyrError(message, status)
