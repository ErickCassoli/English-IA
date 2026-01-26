# English IA 🚀

**An AI-Powered English Language Learning Platform**

![Status](https://img.shields.io/badge/status-active-success.svg)
![CI](https://github.com/yourusername/english-ia/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tech](https://img.shields.io/badge/stack-FastAPI%20%7C%20React%20%7C%20TS-blue)

A production-ready full-stack application designed to simulate a real-world English tutor. It uses Large Language Models (LLM) to conduct open-ended conversations, correcting the user in real-time and adaptively creating study materials based on individual mistakes.

## ✨ Key Features

- **🤖 Context-Aware AI**: Chat with a tutor that understands context and nuance, not just scripted responses.
- **📝 Real-time Corrections**: Grammar and vocabulary mistakes are detected on-the-fly without interrupting the flow.
- **📚 Smart Flashcards**: Uses Spaced Repetition (SRS) algorithms (SM-2) to help you memorize vocabulary that *you* struggle with.
- **📜 Session History**: Review past conversations, topics discussed, and evolution over time.
- **🧠 Adaptive Quizzes**: "Knowledge Checks" generated dynamically based on specific conversation content to verify comprehension.
- **📊 Detailed Analytics**: CEFR level estimation (A1-C2), vocabulary tracking, and daily streak monitoring.

## 🛠️ Tech Stack & Engineering

Built with a focus on **Software Engineering Best Practices**:

- **Frontend**: React 18, TypeScript, Vite, TailwindCSS (Dark/Light mode ready), Radix UI.
- **Backend**: Python 3.11, FastAPI, SQLAlchemy (SQLite/PostgreSQL ready).
- **AI/LLM**: Modular design supporting OpenAI, Google Gemini, or local models via Ollama.
- **Quality Assurance**:
  - **CI/CD**: GitHub Actions pipeline for automated Backend Testing (`pytest`) and Frontend Build checks.
  - **Testing**: Comprehensive Unit/Integration tests for API and Frontend Components (`vitest`).
- **DevOps**: Fully Dockerized environment (`docker-compose`) with Nginx reverse proxy.

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose (Recommended)
- *Or* Node.js 20+ & Python 3.11+

### Quick Start (Docker)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/english-ia.git
cd english-ia

# 2. Run with Docker Compose
docker compose up --build
```
Access the app at `http://localhost:5173`.

### Local Development

1. **Backend**:
   ```bash
   cd api
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd web
   npm install
   npm run dev
   ```

## 📂 Project Structure

Verified clean architecture separating concerns:

```
├── .github/workflows/   # CI/CD Pipelines
├── api/                 # FastAPI Backend (Domain-Driven Design elements)
│   ├── app/services/    # Core Logic (LLM, SRS, Evaluation)
│   ├── app/routers/     # REST Endpoints
│   └── tests/           # Pytest Suite
├── web/                 # React Frontend
│   ├── src/components/  # Reusable UI Components
│   ├── src/pages/       # Route Views (Chat, History, Flashcards)
│   └── src/services/    # Typed API Client
└── scripts/             # Dev & Maintenance utilities
```

## 🤝 Contributing

Contributions are welcome! Please run the test suite before submitting PRs:
```bash
# Backend
pytest api/tests

# Frontend
cd web && npm test
```

## 📜 License

MIT License.
