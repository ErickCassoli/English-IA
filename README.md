# English IA

English IA is an open-source English coaching MVP offering chat corrections, adaptive quizzes,
SM-2 powered flashcards, lightweight stats, and a call-style websocket stub. The backend is written
in FastAPI with SQLite persistence, Prompt Orchestration Markup Language (POML) prompts, and
optional Ollama integration. A Streamlit demo showcases the chat flow.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Streamlit demo

```bash
streamlit run web/streamlit_app.py
```

### Quality gates

```bash
ruff check .
pytest -q
bandit -r app
```

### Ollama fallback
If the service is offline the API still responds thanks to deterministic fallbacks. When
`OLLAMA_HOST` is unreachable, the LLM client returns a deterministic JSON payload so the API remains
testable.

## Endpoints
- `GET /healthz`
- `POST /api/chat/correct`
- `POST /api/quiz/generate`
- `POST /api/quiz/answer`
- `GET /api/flashcards/due`
- `POST /api/flashcards/review`
- `GET /api/stats/summary`
- `WS /ws/call`

## Project layout
```
app/
  main.py              # FastAPI wiring
  routers/             # REST/WS endpoints
  services/            # LLM, POML, SRS, TTS helpers
  repo/                # SQLite helpers and DAO
  utils/               # Config, IDs, logging
prompts/               # POML prompt contracts
web/streamlit_app.py   # minimal chat client
.github/workflows/ci   # lint + tests + bandit
```

## License
MIT License. See `LICENSE` for details.
