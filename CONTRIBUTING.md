# Contributing

## Local setup

### Backend

Requirements: Python 3.12.

From `backend`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
cp .env.example .env
python -m uvicorn app.api:app --reload
```

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements_dev.txt
Copy-Item .env.example .env
python -m uvicorn app.api:app --reload
```

### Frontend

Requirements: Node.js LTS.

From `frontend`:

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

From `backend`:

```bash
ruff check .
python -m pytest
```

From `frontend`:

```bash
npm run format:check
npm test
npm run build
```

`npm run format` applies the Prettier style, and `ruff check . --fix` sorts imports.

CI runs the same checks.

## Project rules

- Keep one responsibility per file.
- Do not add comments in code, and do not use em dashes or hyphens as separators in text.
- Avoid duplicated logic.
- Use current APIs only.
- Every user-facing frontend string must exist in English and Spanish in `frontend/src/features/i18n/dictionaries.ts`.
- Add tests for new behavior.

## Commit and pull request rules

- Write commit messages in English.
- Use conventional prefixes without scopes: `add:`, `feat:`, `edit:`, `fix:`.
- Keep each commit focused on one file or one feature.
- Work in a branch and open a pull request against `main`.
