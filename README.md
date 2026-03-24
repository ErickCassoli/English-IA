# English IA

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-4.x-06B6D4?logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)

**An AI-Powered English Language Learning Platform**

English IA is a production-quality full-stack application that simulates a real-world English tutor. It uses Large Language Models to conduct open-ended conversations, correct the user in real time, and adaptively generate study material based on individual mistakes — all running locally with full privacy support via Ollama.

---

## Features

- **Context-Aware AI Tutor** — Conversational sessions driven by LLM with topic-aware system prompts (POML templates)
- **Real-Time Grammar Corrections** — Detects errors on-the-fly without interrupting the conversation flow; corrections shown in a polished popover
- **Placement Test** — 25-question adaptive assessment (A1–C2) to establish a CEFR baseline before unlocking practice features
- **Smart Flashcards (SRS)** — SM-2 Spaced Repetition algorithm generates vocabulary cards automatically from detected mistakes
- **Adaptive Knowledge Quizzes** — LLM-generated multiple-choice questions based on each specific session
- **Session Reports** — Detailed post-session analytics: CEFR estimate, accuracy %, quiz results, strengths, and corrections
- **Session History** — Full log of all past conversations with navigation to their reports
- **Daily Streak Tracking** — Keeps you accountable with consecutive-day streak monitoring
- **Multi-Provider LLM** — Supports OpenAI, Google Gemini, and local models via Ollama (no cloud required)
- **Fully Dockerized** — One-command startup with Docker Compose and Nginx reverse proxy

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript 5.9, Vite 7, TailwindCSS 4, Radix UI, Framer Motion |
| **Backend** | Python 3.11, FastAPI 0.111, SQLAlchemy 2, Alembic |
| **Database** | SQLite (local dev) / PostgreSQL-ready |
| **AI/LLM** | OpenAI API, Google Gemini, Ollama (local) |
| **DevOps** | Docker, Docker Compose, Nginx, GitHub Actions CI |
| **Testing** | Pytest (backend), Vitest + Testing Library (frontend) |

---

## Getting Started

### Prerequisites

**Option A — Docker (recommended):**
- Docker Desktop with Docker Compose

**Option B — Local development:**
- Node.js 20+
- Python 3.11+

---

### Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/ErickCassoli/English-IA.git
cd English-IA

# 2. Copy and configure the environment file
cp api/.env.example api/.env
# Edit api/.env to add your LLM provider key (optional — mock mode works out of the box)

# 3. Start everything
docker compose up --build
```

The app will be available at `http://localhost:5173`.

---

### Local Development

**Backend (FastAPI):**

```bash
cd api

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .\.venv\Scripts\activate         # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

The API will run at `http://localhost:8000`.

**Frontend (React + Vite):**

```bash
cd web
npm install
npm run dev
```

The frontend will run at `http://localhost:5173` and proxy API calls to the backend automatically.

---

## AI Provider Configuration

Edit `api/.env` (copy from `api/.env.example`):

```env
# Choose one: "ollama", "openai", or "simple_mock"
LLM_PROVIDER=simple_mock
LLM_MODEL=mock-1

# OpenAI
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
# OPENAI_API_KEY=sk-...

# Ollama (local, private)
# LLM_PROVIDER=ollama
# LLM_MODEL=llama3
# OLLAMA_BASE_URL=http://localhost:11434
```

You can also change the provider at any time from the **Settings** page in the UI.

**Ollama quick setup:**
```bash
# Install Ollama from https://ollama.com
ollama pull llama3
# Then set LLM_PROVIDER=ollama and LLM_MODEL=llama3
```

---

## Project Architecture

```
English-IA/
├── .github/workflows/       # CI/CD — tests, build checks, linting
├── api/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Application factory, router mounting
│   │   ├── routers/         # REST endpoints (chat, sessions, flashcards…)
│   │   ├── services/
│   │   │   ├── llm/         # LLM abstraction layer (OpenAI, Ollama, mock)
│   │   │   └── evaluation/  # SRS, quiz generation, error detection, reports
│   │   ├── repo/            # SQLAlchemy models, DAO layer
│   │   ├── schemas/         # Pydantic request/response models
│   │   └── utils/           # Config, logging, POML prompt loader
│   ├── prompts/             # POML prompt templates (tutor, placement…)
│   ├── alembic/             # Database migrations
│   └── tests/               # Pytest unit + integration tests
├── web/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/           # Route views (Dashboard, Chat, Flashcards…)
│   │   ├── components/      # Reusable UI components
│   │   ├── services/api.ts  # Typed API client
│   │   └── layouts/         # DashboardLayout (sidebar + main area)
│   └── public/
├── docker-compose.yml       # Full-stack orchestration
└── start-dev.ps1            # Windows dev convenience script
```

### Key Design Decisions

- **Domain-Driven Structure** — Services are separated by concern (LLM, evaluation, SRS) making each independently testable
- **POML Prompt Templates** — Prompts live in `.poml` files instead of hardcoded strings, making them easy to iterate on
- **LLM Registry Pattern** — A single `registry.get_llm()` call returns the correct provider based on settings, keeping all routers provider-agnostic
- **SRS (SM-2)** — The spaced repetition algorithm is isolated in `services/evaluation/srs.py` with full unit test coverage
- **Placement Gate** — The backend enforces that users complete a placement test before starting chat sessions (HTTP 403)

---

## Running Tests

```bash
# Backend tests
cd api
pytest tests/ -v

# Frontend tests
cd web
npm test
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Ensure tests pass: `pytest api/tests && cd web && npm test`
4. Submit a pull request with a clear description

Please follow the existing code style. All PRs are checked by the GitHub Actions CI pipeline.

---

## License

MIT License — see [LICENSE](./LICENSE) for details.
