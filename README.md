# English IA

[![CI](https://github.com/ErickCassoli/english-ia/actions/workflows/ci.yml/badge.svg)](https://github.com/ErickCassoli/english-ia/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](#quality-gates)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![release-please](https://img.shields.io/badge/release-please-automated-ff69b4.svg)](.github/workflows/release.yml)

English IA is a collaborative, open-source English coaching platform that combines FastAPI services, Prompt Orchestration Markup Language (POML), and an optional Streamlit demo to deliver chat corrections, adaptive quizzes, spaced-repetition flashcards, and voice call-style coaching.

## Highlights

- Multi-modal learning loops: chat correction, quiz generation, flashcards, stats, and call-style coaching.
- POML-driven prompts so contracts are explicit, tested, and linted in CI.
- Python 3.11 backend with FastAPI, async-friendly services, and SQLite/FAISS-ready persistence.
- Streamlit demo that surfaces the public API for product folks and stakeholders.
- Production guardrails: ruff, pytest+coverage, bandit, pre-commit hooks, Dependabot, CodeQL, release-please, and trunk-based contribution guidelines.

## Quickstart

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Run the API

```bash
uvicorn app.main:app --reload
```

FastAPI docs live at http://localhost:8000/docs and the JSON schema at http://localhost:8000/openapi.json.

### 3. Run the Streamlit demo

```bash
streamlit run web/streamlit_app.py
```

### 4. Tests and linting

```bash
ruff check .
pytest -q
```

### 5. Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

### 6. Docker Compose

```bash
docker compose -f docker/compose.yml up --build
```

The compose stack starts both the FastAPI service (port 8000) and the Streamlit web demo (port 8501) sharing the same volume-backed SQLite database.

## API

The backend is a FastAPI application defined in `app/main.py`. Primary routers live under `app/routers/*` and expose:

- `POST /api/chat/correct` — grammar and tone corrections.
- `POST /api/quiz/generate` and `POST /api/quiz/answer` — adaptive quizzes.
- `GET /api/flashcards/due` and `POST /api/flashcards/review` — SM-2 spaced repetition.
- `GET /api/stats/summary` — daily product analytics.
- `POST /api/auth/signup` and `POST /api/auth/login` — lightweight JWT auth for collaboration.

Swagger UI is available at http://localhost:8000/docs and the ReDoc view at http://localhost:8000/redoc.

## POML

Prompts live in `prompts/*.poml` and are described in `docs/POML.md`. Each prompt:

1. Declares variables and defaults.
2. Ships a canonical template rendered by `app/services/poml_runtime.py`.
3. Includes an explicit JSON contract that is validated by `app/services/parser.py` and linted by `tools/poml_lint.py`.

## Quality Gates

Continuous integration runs ruff, ruff format, pytest with coverage, and bandit via `.github/workflows/ci.yml`. POML linting, release automation, and CodeQL run in dedicated workflows.

## Roadmap (MVP)

- Chat correction with contextual highlights.
- Quiz generation plus answer checking pipeline.
- Flashcards with SM-2 scheduling and tags.
- Learning stats dashboard and progress summaries.
- JWT-based auth for collaborative sessions.
- Prompt runtime + linting for every LLM flow.
- Call-style coaching prompt and runtime support.

## Contributing & Governance

Trunk-based development on `main`, short-lived branches (`feat/*`, `fix/*`, `chore/*`, `docs/*`), Conventional Commits, and SemVer releases automated by release-please. Read `CONTRIBUTING.md` for the full workflow.

## Security

Responsible disclosure guidelines and contact instructions are documented in `SECURITY.md`.

## License

Released under the MIT License. See `LICENSE` for details.

## Maintainers

- @ErickCassoli
