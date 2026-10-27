# Security policy

## Reporting a vulnerability

Please use GitHub Private Vulnerability Reporting:

1. Open the repository **Security** tab.
2. Click **Report a vulnerability**.
3. Share steps to reproduce, impact, and any proof of concept.

Do not open a public issue for security problems.

## Security model

Linkmortem reads public web pages and repository documentation. It does not edit external systems on its own.

Outbound requests are handled through `backend/app/scan/fetcher.py` and safety checks in `backend/app/scan/safety.py`:

- DNS is resolved before requesting a target.
- Only public addresses are allowed.
- Only ports 80 and 443 are allowed.
- Redirect hops are re-checked with the same guard.
- Redirects are limited to 5 hops.
- Response body reads are capped at 400 KB.

Scan traffic is controlled in `backend/app/ratelimit.py`:

- Per-client rate limiting.
- A cap on concurrent scans.

Prompt handling in `backend/app/llm/prompting.py` fences fetched text as data before model use.

Secrets are stored only in `backend/.env` (git ignored). The file `backend/.env.example` documents all required variables without secret values.

## Supported versions

Only the latest version on `main` is supported for security updates.
