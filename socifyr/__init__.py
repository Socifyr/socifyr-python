"""Official Python SDK for Socifyr — the social publishing API for teams and AI agents."""

from .client import Socifyr
from .errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    SocifyrError,
    UsageLimitError,
    ValidationError,
)
from .webhooks import verify_webhook_signature

__version__ = "0.2.0"

__all__ = [
    "Socifyr",
    "SocifyrError",
    "AuthenticationError",
    "RateLimitError",
    "UsageLimitError",
    "NotFoundError",
    "ValidationError",
    "verify_webhook_signature",
    "__version__",
]
