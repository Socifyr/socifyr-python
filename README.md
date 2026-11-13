# Socifyr — Python SDK

The official Python SDK for [Socifyr](https://socifyr.com), the social publishing API for teams and AI agents. Publish to 18 platforms through one API — your agent gets just an API key, and never sees your account tokens.

## Install

```bash
pip install socifyr
```

## Quick start

```python
from socifyr import Socifyr

client = Socifyr(api_key="sk_...")
# or set SOCIFYR_API_KEY in the environment
# The key belongs to one workspace; there is no workspace ID to pass.

# Publish text to multiple platforms by slug
client.uploads.text(
    connections=["instagram-mybrand", "x-myhandle"],
    text="Shipped a new feature 🚀",
)

# Schedule for later
client.uploads.text(
    connections=["linkedin-mybrand"],
    text="Scheduled post",
    scheduled_at="2026-06-01T09:00:00Z",
)
```

## Bulk scheduling

```python
res = client.uploads.bulk_schedule(rows=[
    {"text": "Morning", "connections": ["x-me"], "scheduledAt": "2026-06-01T09:00:00Z"},
    {"text": "Evening", "connections": ["x-me"], "scheduledAt": "2026-06-01T18:00:00Z"},
])
print(f"{res['created']} scheduled, {len(res['failed'])} failed")

# ...or from a CSV string (header: text,connections,scheduledAt,title)
client.uploads.bulk_schedule(csv=open("posts.csv").read())
```

## Other resources

```python
client.workspaces.list_connections()           # connection slugs
client.usage()                                  # usage vs plan limits
client.analytics.get(period="last_month")       # engagement analytics
client.analytics.followers(period="last_3months")  # follower growth per account
client.analytics.accounts(period="last_month")     # side-by-side account comparison
client.ai.generate_caption(upload_type="text", platforms=["x"], text="...")  # BYOK AI
```

## Webhooks

```python
from socifyr import verify_webhook_signature

ok = verify_webhook_signature(raw_body, request.headers["X-Webhook-Signature"], secret)
```

## Errors

All failures raise a `SocifyrError` subclass: `AuthenticationError`, `RateLimitError`,
`UsageLimitError`, `NotFoundError`, `ValidationError`.

## License

AGPL-3.0-or-later
