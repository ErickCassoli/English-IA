# CLAUDE.md — English-IA Codebase Guide

This document provides context for AI assistants working in this repository.

---

## Project Overview

**English-IA** is an AI-powered English learning assistant. It uses LLMs to conduct conversational practice sessions, detect grammar/vocabulary errors, generate quizzes, manage spaced-repetition flashcards, and assess learner levels via CEFR placement tests.

---

## Repository Structure

```
English-IA/
├── api/                    # FastAPI backend (Python 3.11)
│   ├── app/
│   │   ├── main.py         # App factory, lifespan, router registration
│   │   ├── routers/        # REST endpoint handlers
│   │   ├── services/       # Business logic (LLM, evaluation)
│   │   ├── schemas/        # Pydantic v2 request/response models
│   │   ├── repo/           # SQLAlchemy ORM models + DAO layer
│   │   ├── utils/          # Config, logging, prompts, IDs, time
│   │   └── ws/             # WebSocket handlers
│   ├── prompts/            # POML prompt templates for LLMs
│   ├── alembic/            # Database migrations
│   ├── tests/              # pytest test suite
│   ├── scripts/            # Utility scripts
│   ├── pyproject.toml      # Python project config (ruff, black, pytest)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
├── web/                    # React frontend (TypeScript)
│   ├── src/
│   │   ├── pages/          # Route-level page components
│   │   ├── components/     # Shared UI components (ui/ = Radix primitives)
│   │   ├── layouts/        # Layout wrappers (DashboardLayout)
│   │   ├── services/api.ts # Typed REST client
│   │   └── lib/utils.ts    # Utility helpers
│   ├── vite.config.ts      # Vite config with proxy and test setup
│   ├── eslint.config.js    # ESLint flat config
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Orchestrates api + web services
├── .pre-commit-config.yaml # Ruff, Black, standard file fixers
└── .github/workflows/      # GitHub Actions CI/CD
    ├── ci.yml              # Backend tests + frontend build
    ├── poml-lint.yml       # POML prompt file linting
    └── codeql.yml          # Security scanning
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript 5.9, Vite 7, TailwindCSS 4, Radix UI |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Database | SQLite (default), PostgreSQL-compatible |
| LLM | OpenAI API, Ollama (local), Mock (default/testing) |
| Testing | pytest (backend), Vitest + Testing Library (frontend) |
| Code Quality | Ruff, Black, ESLint 9, bandit, CodeQL |
| DevOps | Docker, Docker Compose, GitHub Actions |

---

## Backend Architecture

### Clean Layered Architecture

```
Router → Schema validation → Service/DAO → ORM Model → DB
```

- **Routers** (`app/routers/`): HTTP handlers only — no business logic
- **Schemas** (`app/schemas/`): Pydantic v2 DTOs for input/output validation
- **Services** (`app/services/`): All business logic lives here
- **Repo** (`app/repo/`): `models.py` (ORM), `dao.py` (DB queries), `db.py` (session mgmt)
- **Utils** (`app/utils/`): Config, logger, ID generation, time helpers, POML loader

### Key Services

**LLM Layer** (`app/services/llm/`):
- `base.py`: Abstract `LLMClient` interface with `reply(history) -> str`
- `registry.py`: Factory function returning the configured provider
- Providers: `simple_mock.py` (default), `openai.py`, `ollama.py`
- Default is `simple_mock` — safe for development and testing without API keys

**Evaluation Layer** (`app/services/evaluation/`):
- `errors.py`: Detects grammar/vocabulary/fluency errors → `DetectedError` dataclass
- `srs.py`: SM-2 spaced repetition algorithm (`CardState`, `next_review`)
- `placement.py`: CEFR level assessment (A1–C2)
- `quizgen.py`: Generates quiz questions from session errors
- `report.py`: Computes session analytics and metrics

### Database

SQLite by default (configurable via `DATABASE_URL`). Managed with Alembic migrations.

**Core tables**: `users`, `sessions`, `messages`, `error_spans`, `practice_topics`, `quizzes`, `quiz_attempts`, `flashcards`, `settings`, `daily_practice`, `user_streak`

**Enums defined in `models.py`**:
- `LLMProvider`: `simple_mock`, `ollama`, `openai`
- `SessionStatus`: active, completed
- `MessageRole`: user, assistant
- `ErrorCategory`: grammar, vocabulary, fluency
- `QuizType`: multiple_choice, fill_blank
- `CEFRLevel`: A1, A2, B1, B2, C1, C2

### Prompt Templates (POML)

Prompts live in `api/prompts/*.poml`. The POML loader in `utils/prompts.py` reads and interpolates them. POML files are linted in CI (`poml-lint.yml`).

Prompt files:
- `tutor_roleplay.poml` — Main chat system prompt
- `correction.poml` — Error correction instructions
- `placement_test.poml` / `placement_assessment.poml` — Placement flow
- `session_analysis.poml` — Session report generation
- `cefr_rubric.poml` — CEFR scoring criteria

### API Routes

| Router | Prefix | Purpose |
|--------|--------|---------|
| chat | `/api/chat` | Send messages, get history, error detection |
| sessions | `/api/sessions` | Session lifecycle (create, end) |
| practice | `/api/practice` | Topic management |
| quiz | `/api/quiz` | Quiz generation and attempts |
| flashcards | `/api/flashcards` | Spaced repetition card review |
| reports | `/api/reports` | Session analytics |
| dashboard | `/api/dashboard` | User summary statistics |
| settings | `/api/settings` | User preferences |
| placement | `/api/placement` | CEFR placement tests |
| admin | `/api/admin` | Admin utilities |
| health | `/api/health` | Health check |
| ws | `/ws` | WebSocket real-time chat |

### Environment Configuration

Configured via `utils/config.py` (Pydantic Settings). Copy `api/.env.example` to `api/.env`:

```
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./data.db
DEFAULT_LLM_PROVIDER=simple_mock   # or: ollama, openai
DEFAULT_LLM_MODEL=mock-1
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=
SESSION_IDLE_TIMEOUT_MINUTES=5
```

---

## Frontend Architecture

### Structure

- **Pages** (`src/pages/`): One component per route — Dashboard, Chat, Practice, History, Flashcards, Quiz, Report, Settings, PlacementTest
- **Components** (`src/components/`): Shared components; `ui/` contains Radix UI primitives (Button, Card, Label, Popover, RadioGroup, Tooltip)
- **Layouts** (`src/layouts/`): `DashboardLayout` wraps all authenticated pages with persistent sidebar
- **API Client** (`src/services/api.ts`): Typed client for all backend calls; base URL is `/api` (proxied by Vite in dev)

### Routing

React Router v7. Routes defined in `App.tsx`:
- `/dashboard`, `/placement`, `/chat`, `/history`, `/flashcards`, `/practice`, `/settings`
- `/quiz/:sessionId`, `/report/:sessionId`

### Styling

TailwindCSS 4 via Vite plugin. Components use `class-variance-authority` (CVA) for variant-based class generation. Framer Motion for animations.

### Vite Dev Proxy

`vite.config.ts` proxies `/api` → `http://127.0.0.1:8000` and `/ws` → WebSocket backend. No CORS issues during local development.

---

## Development Workflows

### Local Setup (without Docker)

**Backend:**
```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
alembic upgrade head        # run migrations
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd web
npm install
npm run dev                 # starts at http://localhost:5173
```

### Docker (recommended)

```bash
docker-compose up --build
# API: http://localhost:8000
# Web: http://localhost:5173
```

### Database Migrations

```bash
cd api
alembic upgrade head                  # apply all migrations
alembic revision --autogenerate -m "description"  # create new migration
alembic downgrade -1                  # roll back one step
```

Migration files live in `api/alembic/versions/` and are numbered `0001_`, `0002_`, etc.

---

## Code Quality & Testing

### Backend

```bash
cd api
ruff check .          # lint
ruff format .         # format (replaces black in practice)
black .               # formatting (also configured)
bandit -r app/        # security scan
pytest tests/ -v      # run tests
```

**Ruff config** (in `pyproject.toml`): line-length=100, py311 target, rules E/F/I/B/UP selected.

**Test files** (`api/tests/`):
- `test_errors.py` — Error detection logic
- `test_srs.py` — Spaced repetition algorithm
- `test_quizgen.py` — Quiz generation
- `test_report.py` — Session report analytics
- `test_settings.py` — Settings handling

### Frontend

```bash
cd web
npm run lint          # ESLint
npm run build         # TypeScript compile + Vite build
npm test              # Vitest (watch mode)
npm run test -- --run # Vitest (single run)
```

**ESLint** uses flat config (`eslint.config.js`): typescript-eslint + react-hooks + react-refresh.

**Vitest** config is embedded in `vite.config.ts`: globals=true, jsdom environment, setup via `src/setupTests.ts`.

### Pre-commit Hooks

Install once: `pre-commit install`

Hooks run on commit: Ruff (lint + format), Black, end-of-file-fixer, trailing-whitespace.

### CI/CD (GitHub Actions)

- **`ci.yml`**: Runs on push/PR to main — backend pytest + frontend build
- **`poml-lint.yml`**: Validates POML prompt files
- **`codeql.yml`**: Security analysis (Python), weekly + on main push/PR

---

## Key Conventions

### Backend

1. **Always use Pydantic schemas** for request/response — never return raw ORM models
2. **Business logic belongs in services**, not routers or DAO
3. **Use the LLM registry** (`services/llm/registry.py`) to get a client — never instantiate providers directly in routers
4. **Database sessions** are injected via FastAPI `Depends(get_db)` — always close them properly
5. **New migrations** must be numbered sequentially (`0004_description.py`) and auto-generated with Alembic
6. **Line length is 100** — enforced by both Ruff and Black
7. **Python 3.11+** features are acceptable (match statements, `typing.Self`, etc.)

### Frontend

1. **API calls go through `src/services/api.ts`** — never use `fetch` directly in components
2. **UI primitives** live in `src/components/ui/` and wrap Radix UI — reuse these, don't add new libraries without discussion
3. **Path alias `@/`** maps to `src/` — use it for all internal imports
4. **TypeScript strict mode** is on — no `any` without justification
5. **No unused imports/variables** — enforced by tsconfig and ESLint

### Git

1. **Commit messages**: Use `feat:`, `fix:`, `chore:`, `docs:` prefixes (conventional commits style)
2. **Branch**: Feature work on feature branches, never directly to `main`
3. **Pre-commit**: Hooks must pass before committing

---

## Adding New Features

### New API Endpoint

1. Create/update a schema in `api/app/schemas/`
2. Add business logic to the appropriate service in `api/app/services/`
3. Add DB access in `api/app/repo/dao.py` if needed
4. Create or update a router in `api/app/routers/`
5. Register the router in `api/app/main.py`
6. If schema changes, create an Alembic migration

### New Frontend Page

1. Create the page component in `web/src/pages/`
2. Add the route in `web/src/App.tsx`
3. Add API calls to `web/src/services/api.ts`
4. Add navigation link in `web/src/components/Sidebar.tsx`

### New LLM Provider

1. Create a class in `api/app/services/llm/` implementing `LLMClient` from `base.py`
2. Register it in `api/app/services/llm/registry.py`
3. Add the provider name to the `LLMProvider` enum in `api/app/repo/models.py`

### New Prompt

1. Create a `.poml` file in `api/prompts/`
2. Load it using `utils/prompts.py` (`load_prompt()`)
3. Ensure it passes the POML linter (`tools/poml_lint.py`)

---

## Important Notes for AI Assistants

- **Default LLM is `simple_mock`** — tests and local dev work without any API keys
- **SQLite is the default DB** — no external DB needed for local development
- **The DB is seeded on startup** (`repo/seed.py`) with default topics and settings
- **WebSocket** endpoint is at `/ws/call` for real-time chat (alternative to REST `/api/chat`)
- **Session idle timeout** (default 5 min) auto-closes inactive sessions
- **CEFR levels**: A1 (beginner) → C2 (mastery) — used for placement and progress tracking
- **Flashcard scheduling** uses SM-2 algorithm — `ease`, `interval`, `reps`, `due_at` fields matter
- **Error categories**: grammar, vocabulary, fluency — used throughout evaluation and quiz generation
- When modifying `models.py`, always create a corresponding Alembic migration
- When modifying `.poml` files, run `python tools/poml_lint.py` locally before pushing
