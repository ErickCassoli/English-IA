# English IA

**Interactive AI English Learning Platform**

A full-stack application designed to help users practice English conversation through AI-driven tutoring, adaptive quizzes, and spaced repetition flashcards.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)

## Overview

English IA combines a robust **FastAPI backend** with a modern **React (Vite) frontend** to create an immersion-focused learning environment.

### Key Features

- **🗣️ AI Conversation Practice**: Chat with a context-aware AI tutor on various topics (Travel, Technology, Business).
- **📝 Automatic Error Correction**: Real-time feedback on grammar, vocabulary, and fluency provided by the AI.
- **🧠 Adaptive Quizzes**: "Knowledge Checks" generated dynamically based on your conversation history.
- **⚡ Spaced Repetition (SRS)**: Flashcards created automatically from your mistakes, reviewed using the SM-2 algorithm.
- **📊 Progress Dashboard**: Track vocabulary size, fluency level (CEFR estimation), and study streaks.
- **🔧 Modular LLM Support**: Switch between OpenAI, Ollama (local), or Mock providers easily.

## Architecture

- **Backend**: Python, FastAPI, SQLite (SQLAlchemy), Alembic (Migrations).
- **Frontend**: TypeScript, React, Vite, TailwindCSS, Lucide Icons.
- **Communication**: REST API + WebSockets.
- **Infrastructure**: Docker & Docker Compose support.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Docker (optional, for containerized run)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/english-ia.git
   cd english-ia
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv .venv
   # Activate (Windows: .\.venv\Scripts\activate, Linux/Mac: source .venv/bin/activate)
   . .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt -r requirements-dev.txt
   
   # Setup Database (Migrations + Seed)
   alembic upgrade head
   python -m app.repo.seed
   
   # Run API
   uvicorn app.main:app --reload
   ```
   *Note: In the new structure, backend files are located in `/api`. The `start-dev.ps1` script handles path switching automatically.*

3. **Frontend Setup**
   Open a new terminal in `web/`:
   ```bash
   cd web
   npm install
   npm run dev
   ```
   Frontend runs at: `http://localhost:5173` (Proxies requests to localhost:8000)

### Running with Docker

```bash
docker compose up --build
```
Access the application at `http://localhost:5173`. (Ensure docker-compose exposes the frontend port).

## Project Structure

```
├── app/                  # FastAPI Application
│   ├── main.py           # Entry point
│   ├── routers/          # API Endpoints
│   ├── services/         # Business Logic (LLM, SRS, Quiz)
│   └── repo/             # Database Models & Access
├── web/                  # React Frontend
│   ├── src/
│   │   ├── components/   # UI Components
│   │   ├── pages/        # Route Pages
│   │   └── services/     # API Client
├── scripts/              # Utility scripts for testing/verification
└── tests/                # Pytest suite
```

## Contributing

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

