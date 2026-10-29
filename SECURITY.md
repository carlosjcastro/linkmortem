# Security policy

## Reporting a vulnerability

Please use GitHub Private Vulnerability Reporting:

1. Open the repository **Security** tab.
2. Click **Report a vulnerability**.
3. Share steps to reproduce, impact, and any proof of concept.

Do not open a public issue for security problems.

## Security model

Linkmortem reads public web pages and repository documentation. It never edits anything on its own: patches are built on the server from the saved autopsy, never from what the browser sends, and the GitHub Action only opens a pull request and an issue for people to review.

The address a person enters is checked twice, in `frontend/src/lib/target.ts` and again in `backend/app/scan/targets.py`. Only `http` and `https` are accepted, up to 300 characters, without spaces or control characters, without a user name or password and without a port other than 80 or 443. Request bodies are capped at 16 KB by `backend/app/body_limit.py`. Links shown in results are rendered only when they are web addresses.

Outbound requests are handled through `backend/app/scan/fetcher.py` and safety checks in `backend/app/scan/safety.py`:

- DNS is resolved before requesting a target.
- Only public addresses are allowed.
- Only ports 80 and 443 are allowed, and malformed ports or embedded credentials are refused.
- Redirect hops are re-checked with the same guard.
- Redirects are limited to 5 hops.
- Response body reads are capped at 400 KB.

Scan traffic is controlled in `backend/app/ratelimit.py`:

- Per-client rate limiting, keyed by the address Cloudflare saw (`CF-Connecting-IP`) so a forged `X-Forwarded-For` can't dodge it. Clients are forgotten once their window passes.
- A cap on concurrent scans.
- A daily budget for web searches.

Prompt handling in `backend/app/llm/prompting.py` fences fetched text as data before model use. Text from the internet is escaped in reports, issues and pull requests.

Every response carries the headers set in `backend/app/security.py`: a strict Content Security Policy, HSTS, `nosniff`, `no-referrer`, a Permissions Policy and a Cross Origin Opener Policy.

Sentry receives the agent traces, including the prompts and answers built from public pages, but never IP addresses, cookies or request bodies.

Each autopsy can be preserved in the Internet Archive only once.

Secrets never live in the repository. Locally they go in `backend/.env` (git ignored), in production in the Render dashboard and for the Action in GitHub repository secrets. The file `backend/.env.example` documents every variable without secret values.

## Supported versions

Only the latest version on `main` is supported for security updates.
