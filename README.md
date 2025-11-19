# English IA backend

FastAPI + SQLite backend that powers a conversational English coach. It exposes a clean API (no UI) that lets you spin up conversation sessions, talk to an AI tutor (mock/Ollama/OpenAI), finish the session to obtain quizzes/reports/flashcards, and read dashboard KPIs. Everything runs locally by default (deterministic mock LLM + SQLite file).

## Highlights

- **Practice topics** stored in the DB (Travel, Technology, Food, Work, Entertainment, Daily Life). `GET /api/practice/topics` feeds the client.
- **Session lifecycle** – `POST /api/sessions` picks a topic (random when omitted) and returns a system prompt, `POST /api/chat/{session}` streams conversation with heuristic error detection, and `POST /api/sessions/{session}/finish` generates quizzes, reports, flashcards, and metric snapshots.
- **Evaluation modules** – deterministic quiz generation (3‑5 items), CEFR-style reporting with KPIs + narrative summary, heuristic error spans, and SM‑2 SRS utilities.
- **Flashcards & dashboard** – due flashcards, manual card creation/review endpoints, and `GET /api/dashboard/summary` exposes `study_time_hours`, `words_learned`, `conversations`, `fluency_level`, and `due_flashcards`.
- **Modular LLM registry** – runtime switch between `simple_mock`, `ollama`, and `openai` providers through `/api/settings`.
- **Websocket stub** – `/ws/call` simply echoes text to unblock voice experiments.

## Getting started

```bash
python -m venv .venv
. .venv/bin/activate             # Windows: .\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env             # adjust DATABASE_URL / provider defaults if needed

# Apply schema + seed default rows (startup also auto-runs migrations)
alembic upgrade head
python -m app.repo.seed

# Launch the API
uvicorn app.main:app --reload
```

Interactive docs live at http://localhost:8000/docs and http://localhost:8000/redoc.

### Docker

```bash
docker compose up --build
```

The compose file mounts the repo for live-reload and exposes port `8000`. An (optional) Ollama service block is already included but commented out.

## Database & migrations

- Default DB: `sqlite:///./data.db` (edit `DATABASE_URL` in `.env` for Postgres/MySQL/etc.).
- Create/upgrade schema: `alembic upgrade head`. The FastAPI lifespan also runs the Alembic upgrader automatically when the service boots, so manual upgrades are only necessary for CI/deployment scripts.
- Generate new migrations: `alembic revision --autogenerate -m "message"`.
- Seed lookup tables / defaults: `python -m app.repo.seed` (idempotent; creates the default user, LLM settings row, and practice topics).

## API rundown

| Domain | Endpoint | Notes |
| --- | --- | --- |
| Health | `GET /healthz` | Simple readiness probe |
| Practice | `GET /api/practice/topics` | Topic list for the Practice screen |
| Sessions | `POST /api/sessions` | Body: `{ "topic_code": "travel" | null }` → returns session id, topic details, system prompt |
| Sessions | `POST /api/sessions/{id}/finish` | Generates quizzes, flashcards, metric snapshot, and report |
| Chat | `POST /api/chat/{session}/message` | Saves user msg, detects errors, calls LLM registry, stores assistant reply + error spans |
| Quiz | `GET /api/quiz/by-session/{session}` / `POST /api/quiz/{quiz_id}/answer` | Quiz flow + flashcard-on-repeat errors |
| Reports | `GET /api/reports/{session}` | Summary sentence, KPI block, strengths/improvements, error examples |
| Flashcards | `GET /api/flashcards/due`, `POST /api/flashcards/{id}/review`, `POST /api/flashcards/manual` | Due cards, SM‑2 review, manual creation |
| Dashboard | `GET /api/dashboard/summary` | Aggregated KPIs for the dashboard |
| Settings | `GET/POST /api/settings` | Switch `simple_mock`, `ollama`, or `openai` + model |
| Voice stub | `WS /ws/call` | Accepts messages and echoes JSON events |

All schemas live under `app/schemas/` and mirror these contracts.

## Configuration

`.env.example` documents every knob:

```
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./data.db
DEFAULT_LLM_PROVIDER=simple_mock
DEFAULT_LLM_MODEL=mock-1
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=
```

At runtime you can switch providers via `/api/settings`:

```bash
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"llm_provider":"ollama","llm_model":"llama3"}'
```

The registry will attempt Ollama/OpenAI and fall back to the deterministic mock when credentials/endpoints are missing.

## Project layout

```
app/
  main.py                # FastAPI app factory + lifespan seeds
  routers/               # Endpoint routers (health, practice, sessions, chat, quiz, reports, flashcards, dashboard, settings, ws)
  repo/                  # SQLAlchemy models, DAO helpers, Alembic metadata, seed script
  services/
    llm/                 # LLM clients + registry
    evaluation/          # error heuristics, quiz gen, report builder, SM-2
  schemas/               # Pydantic request/response models
  utils/                 # config/env helpers, ids/time utils
  ws/                    # simple websocket echo stub
alembic/                 # migration env + versions (SQLite by default)
prompts/                 # tutor/correction/CEFR prompt templates
tests/                   # pytest suites (errors, quizgen, srs, settings)
```

## Quality & CI

- `ruff check .` – linting via Ruff (also runs in pre-commit + CI).
- `ruff format .` or `black .` – formatting (Black is wired into pre-commit; Ruff format mirrors it).
- `pytest` – runs the deterministic unit tests (errors, quizgen, SM‑2, settings persistence).
- GitHub Actions (`.github/workflows/ci.yml`) installs deps, runs Ruff, Bandit, and pytest on pushes/PRs.

Install the hooks locally with `pre-commit install` to match CI.

## License

MIT – see `LICENSE`.
