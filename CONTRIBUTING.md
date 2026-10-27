# Contributing

## Local setup

### Backend

Requirements: Python 3.12.

From `/home/runner/work/linkmortem/linkmortem/backend`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
cp .env.example .env
python -m uvicorn app.api:app --reload
```

### Frontend

Requirements: Node.js LTS.

From `/home/runner/work/linkmortem/linkmortem/frontend`:

```bash
npm ci
npm run dev
```

Vite proxies `/api` to `http://localhost:8000` in `frontend/vite.config.ts`.

### Model provider

Use Gemma with Ollama by default:

```env
LINKMORTEM_MODEL_PROVIDER=ollama
```

To use Backboard:

```env
LINKMORTEM_MODEL_PROVIDER=backboard
```

## Checks before opening a pull request

From `/home/runner/work/linkmortem/linkmortem/backend`:

```bash
python -m pytest
```

From `/home/runner/work/linkmortem/linkmortem/frontend`:

```bash
npm test
npm run build
```

CI runs the same checks.

## Project rules

- Keep one responsibility per file.
- Do not add comments in code.
- Avoid duplicated logic.
- Use current APIs only.
- Every user-facing frontend string must exist in English and Spanish in `frontend/src/features/i18n/dictionaries.ts`.
- Add tests for new behavior.

## Commit and pull request rules

- Write commit messages in English.
- Use conventional prefixes without scopes: `add:`, `feat:`, `edit:`, `fix:`.
- Keep each commit focused on one file or one feature.
- Work in a branch and open a pull request against `main`.
