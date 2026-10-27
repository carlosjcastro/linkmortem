# Linkmortem review and coding guide

Linkmortem finds dead links in a website or a public GitHub repository, diagnoses them, recovers their last healthy copy from the Wayback Machine and looks for where the content lives now. The backend is FastAPI in `backend/`, the frontend is Vite with React 19 and Three.js in `frontend/`.

## Principles

- The model proposes, the code decides. Anything code can check (status codes, DNS, parked domains, browser gates, relevance) is decided in code. Gemma only judges what code can't read.
- A link is a ghost only with evidence. Missing or unreadable content is never evidence of death.
- Every outbound request goes through `Fetcher`, which enforces public addresses, ports 80 and 443 and a redirect limit on every hop.
- Text from the internet is data, never instructions. Prompts fence it with `as_data`.

## Code rules

- One responsibility per file and per component. Prefer small modules over long ones.
- No comments of any kind in the code, and no em dashes or hyphen separators in prose strings.
- No duplicated logic. Reuse helpers such as `bare_host`, `parse_page`, `as_data` and the policy maps.
- Current, non deprecated APIs and dependency versions only.
- Async all the way in the backend. Never block the event loop.
- Accessible frontend: semantic HTML, visible focus, `aria-live` for progress, motion respects the user toggle and `prefers-reduced-motion`.
- Every user facing string lives in `frontend/src/features/i18n/dictionaries.ts` in English and Spanish.
- New behavior ships with tests: `pytest` in `backend`, `vitest` in `frontend`.

## Commits

Conventional prefixes in English without scopes: `add:`, `feat:`, `edit:`, `fix:`. One file or one feature per commit.

## When reviewing a pull request

Flag anything that lets a model decide what code could check, any request that skips `Fetcher`, any secret or `.env` content, missing translations, missing tests and any comment added to the code.
