# Security policy

## Reporting a vulnerability

Please use GitHub Private Vulnerability Reporting:

1. Open the repository **Security** tab.
2. Click **Report a vulnerability**.
3. Share steps to reproduce, impact, and any proof of concept.

Do not open a public issue for security problems.

## Security model

Linkmortem reads public web pages and repository documentation. It never edits anything on its own: patches are built on the server from the saved autopsy, never from what the browser sends, and the GitHub Action only opens a pull request and an issue for people to review.

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

Prompt handling in `backend/app/llm/prompting.py` fences fetched text as data before model use. Text from the internet is escaped in reports, issues and pull requests.

Every response carries the headers set in `backend/app/security.py`: a strict Content Security Policy, HSTS, `nosniff`, `no-referrer`, a Permissions Policy and a Cross Origin Opener Policy.

Sentry receives the agent traces, including the prompts and answers built from public pages, but never IP addresses, cookies or request bodies.

Each autopsy can be preserved in the Internet Archive only once.

Secrets never live in the repository. Locally they go in `backend/.env` (git ignored), in production in the Render dashboard and for the Action in GitHub repository secrets. The file `backend/.env.example` documents every variable without secret values.

## Supported versions

Only the latest version on `main` is supported for security updates.
