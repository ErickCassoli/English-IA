# English IA

Local-first English coaching backend powered by FastAPI, SQLite, deterministic mock LLMs, and modular adapters (Ollama/OpenAI). Each chat session tracks mistakes, produces quizzes, flashcards (SM-2), KPIs, and a dashboard-friendly snapshot. No frontend is bundled; the API is the product.

## Features

- 🗣️ **Chat sessions**: user topic (or random) with heuristic error detection and modular LLM replies.
- 🧠 **Finish session**: auto-generate 3–5 quiz items, CEFR-style report, flashcards referencing detected errors, and metric snapshots.
- 🧾 **Reports & KPIs**: CEFR estimate, accuracy %, strengths/improvements, error examples.
- 🗂️ **Dashboard endpoints**: session summary, flashcards due, quiz attempts, settings toggle.
- 🔌 **LLM registry**: switch between `simple_mock`, `ollama`, or `openai` via `/api/settings`.
- 🔄 **Voice stub**: `/ws/call` placeholder for streaming audio events.

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Docs live at http://localhost:8000/docs

## Docker

```bash
docker compose up --build
```

Set environment overrides in `.env` (see `.env.example` for all keys, including `DEFAULT_LLM_PROVIDER`, `OLLAMA_BASE_URL`, and `OPENAI_API_KEY`).

## API overview

- `GET  /healthz`
- `POST /api/sessions` – create chat session (`topic` optional, defaults to `random`)
- `POST /api/chat/{session_id}/message`
- `POST /api/sessions/{session_id}/finish`
- `GET  /api/quiz/by-session/{session_id}`
- `POST /api/quiz/{quiz_id}/answer`
- `GET  /api/reports/{session_id}`
- `GET  /api/flashcards/due`
- `POST /api/flashcards/{id}/review`
- `GET  /api/dashboard/summary`
- `GET/POST /api/settings`
- `WS   /ws/call` (stub)

## Project structure

```
app/
  routers/             # FastAPI routers
  services/            # llm + evaluation modules
  repo/                # SQLAlchemy models, DAO, seeds
  schemas/             # Pydantic IO models
  utils/               # config/env helpers
  ws/                  # websocket stubs
prompts/               # POML contracts (correction, tutor roleplay, CEFR rubric)
alembic/               # migrations
tests/                 # unit tests for heuristics, quizgen, SRS, settings
```

SQLite is stored in `./data.db` by default (configurable through `DATABASE_URL`). Alembic manages schema evolution; run `alembic upgrade head` when deploying.

## Quality gates

```bash
ruff check .
bandit -r app
pytest
```

Pre-commit hooks run Ruff, Black, EOF fixer, and trailing-whitespace trims. Install them via `pre-commit install`.

## LLM settings

- `simple_mock` (default) provides deterministic replies for tests/CI.
- `ollama` uses `OLLAMA_BASE_URL` and the configured `llm_model`.
- `openai` uses `OPENAI_API_KEY` and the configured model name.

Switch providers at runtime:

```bash
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"llm_provider":"ollama", "llm_model":"llama3"}'
```

## License

MIT License – see `LICENSE`.
