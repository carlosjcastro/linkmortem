# Linkmortem

Every dead link is a ghost. Linkmortem finds the dead links in a site or in the documentation of a repository, recovers what each lost page said from the Internet Archive and proposes how to replace it, with Gemma 4 as an open weights model.

This project is being built for the DEV Hacktoberfest Open Source AI Challenge, Week 4, "Ghost in the Machine".

## Run locally

Backend, from the `backend` folder:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements_dev.txt
copy .env.example .env
ollama pull gemma4:e4b
python -m pytest
python -m uvicorn app.api:app
```

Frontend, from the `frontend` folder:

```
npm install
npm test
npm run dev
```

## License

MIT
