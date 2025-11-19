# English IA backend

FastAPI + SQLite backend that powers a conversational English coach. It exposes a clean API (no UI) that lets you spin up conversation sessions, talk to an AI tutor (mock/Ollama/OpenAI), finish the session to obtain quizzes/reports/flashcards, and read dashboard KPIs. Everything runs locally by default (deterministic mock LLM + SQLite file).

## Highlights

- **Practice topics** stored in the DB (Travel, Technology, Food, Work, Entertainment, Daily Life). GET /api/practice/topics feeds the client.
- **Session lifecycle** – POST /api/sessions picks a topic (random when omitted) and returns the tutor prompt; POST /api/chat/{session} streams the conversation with heuristic error detection; POST /api/sessions/{session}/finish generates quizzes/flashcards, and the report unlocks only after the learner answers the quizzes.
- **Evaluation modules** – deterministic quiz generation (3–5 items), CEFR-style reporting with KPIs + narrative summary, heuristic error spans, and SM-2 SRS utilities.
- **Flashcards & dashboard** – due flashcards, manual card creation/review endpoints, and GET /api/dashboard/summary exposes study_time_hours, words_learned, conversations, luency_level, and due_flashcards.
- **Modular LLM registry** – runtime switch between simple_mock, ollama, and openai providers through /api/settings.
- **Websocket stub** – /ws/call simply echoes text to unblock voice experiments.
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
| Sessions | `POST /api/sessions/{id}/finish` | Generates quizzes/flashcards and signals that the report will unlock after quizzes |
| Chat | `POST /api/chat/{session}/message` | Saves user msg, detects errors, calls LLM registry, stores assistant reply + error spans |
| Quiz | `GET /api/quiz/by-session/{session}` / `POST /api/quiz/{quiz_id}/answer` | Quiz flow + flashcard-on-repeat errors; answers return `report_ready` |
| Reports | `GET /api/reports/{session}` | Summary sentence, KPIs, quiz performance, strengths/improvements; only available once quizzes are done |
| Flashcards | `GET /api/flashcards/due`, `POST /api/flashcards/{id}/review`, `POST /api/flashcards/manual` | Due cards, SM‑2 review, manual creation |
| Dashboard | `GET /api/dashboard/summary` | Aggregated KPIs for the dashboard |
| Settings | `GET/POST /api/settings` | Switch `simple_mock`, `ollama`, or `openai` + model |
| Voice stub | `WS /ws/call` | Accepts messages and echoes JSON events |

All schemas live under `app/schemas/` and mirror these contracts.

## Documentação detalhada da API

Cada endpoint retorna/aceita JSON e está descrito abaixo. Autenticação ainda não é necessária; todos os fluxos operam para o “Local Learner” padrão.

### Health

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/healthz` | Verifica se o serviço e a DB estão ativos. |

**Resposta 200**

```json
{ "status": "ok" }
```

### Practice

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/api/practice/topics` | Lista os temas configurados (Travel, Technology, etc.). |

**Resposta 200**

```json
[
  {"code": "travel", "label": "Travel", "description": "Discuss trips..."},
  {"code": "technology", "label": "Technology", "description": "Talk about gadgets..."}
]
```

### Sessions

| Método | Rota | Payload | Descrição |
| --- | --- | --- | --- |
| `POST` | `/api/sessions` | `{ "topic_code": "travel" \| null }` | Cria uma sessão ativa. Tema opcional: `null` sorteia um aleatório. |
| `POST` | `/api/sessions/{session_id}/finish` | - | Finaliza a sessão, gera quizzes/flashcards e retorna `report_ready: false` até os quizzes serem respondidos. |

**Resposta 200 (criação)**

```json
{
  "session_id": "7ca...",
  "topic_code": "travel",
  "topic_label": "Travel",
  "topic_description": "Discuss trips...",
  "system_prompt": "You are a patient tutor...",
  "status": "active",
  "started_at": "2025-11-19T20:24:35.125872+00:00",
  "ended_at": null
}
```

**Resposta 200 (finish)**

```json
{
  "quizzes_created": 4,
  "flashcards_created": 2,
  "report_ready": false
}
```

### Chat

| Método | Rota | Payload | Descrição |
| --- | --- | --- | --- |
| `POST` | `/api/chat/{session_id}/message` | `{ "text": "..." }` | Salva mensagem do usuário, roda heurísticas de erro e obtém reply do LLM configurado. |

**Resposta 200**

```json
{
  "reply": "Here's a clearer version...",
  "detected_errors": [
    {
      "start": 0,
      "end": 10,
      "category": "grammar",
      "user_text": "I am agree",
      "corrected_text": "I agree",
      "note": "Use 'agree' sem auxiliar."
    }
  ]
}
```

### Quiz

| Método | Rota | Payload | Descrição |
| --- | --- | --- | --- |
| `GET` | `/api/quiz/by-session/{session_id}` | - | Lista quizzes gerados para a sessão. |
| `POST` | `/api/quiz/{quiz_id}/answer` | `{ "choice": "text", "latency_ms": 1200 }` | Registra tentativa; se erro reincidente gera flashcard e indica (`report_ready`) quando todos os quizzes já foram respondidos. |

**Resposta 200 (listar)**

```json
{
  "items": [
    {"id": "quiz1", "type": "mcq", "prompt": "Choose...", "choices": ["I agree", "I am agree"]}
  ]
}
```

**Resposta 200 (answer)**

```json
{
  "quiz_id": "quiz1",
  "is_correct": true,
  "flashcard_created": false,
  "report_ready": true
}
```

### Reports

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/api/reports/{session_id}` | Retorna resumo analítico, KPIs, desempenho nos quizzes e exemplos; disponível apenas depois que todos os quizzes forem respondidos. |

**Resposta 200**

```json
{
  "summary": "You practiced travel...",
  "kpis": {"words": 120, "errors": 4, "accuracy_pct": 96.7, "cefr_estimate": "B2"},
  "quiz_summary": {"total": 4, "correct": 3, "accuracy_pct": 75.0},
  "strengths": ["High lexical accuracy..."],
  "improvements": ["Link short sentences..."],
  "examples": [{"source": "peoples", "target": "people", "note": "Plural irregular."}]
}
```

### Flashcards

| Método | Rota | Payload | Descrição |
| --- | --- | --- | --- |
| `GET` | `/api/flashcards/due` | — | Lista cards vencidos (SM-2). |
| `POST` | `/api/flashcards/{id}/review` | `{ "quality": 0..5 }` | Atualiza ease/interval/due. |
| `POST` | `/api/flashcards/manual` | `{ "front": "...", "back": "..." }` | Cria card manual desvinculado de erros. |

### Dashboard

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/api/dashboard/summary` | KPIs agregados (`study_time_hours`, `words_learned`, `conversations`, `fluency_level`, `due_flashcards`). |

### Settings (LLM)

| Método | Rota | Payload | Descrição |
| --- | --- | --- | --- |
| `GET` | `/api/settings` | — | Mostra provider/model atuais. |
| `POST` | `/api/settings` | `{ "llm_provider": "simple_mock|ollama|openai", "llm_model": "..." }` | Persiste provider/model; validações básicas. |

### Websocket stub

| Método | Rota | Descrição |
| --- | --- | --- |
| `WS` | `/ws/call` | Aceita conexão, envia `{event:"start"}`, ecoa mensagens recebidas como `{event:"partial", "echo": "..."};` finaliza com `{event:"final"}`. Útil para testar stacks de voz. |

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
