# Architecture

## Overview

English IA couples a FastAPI backend, declarative prompts, and a lightweight Streamlit demo. Core components:

- **FastAPI Service (`app/`)** — orchestrates routers for chat, quizzes, flashcards, stats, and auth. Each endpoint produces typed responses with trace IDs for observability.
- **POML Runtime (`app/services/poml_runtime.py`)** — parses XML-based Prompt Orchestration Markup Language files, validates required variables, and renders final prompts.
- **LLM Client (`app/services/llm.py`)** — calls Ollama via HTTP and falls back to deterministic mock JSON to keep contracts stable during tests/CI.
- **Persistence (`app/repo/*`)** — SQLite via the standard library, with tables for chat transcripts, prompt errors, quizzes/items, flashcards, stats, and users. FAISS (or sqlite-vss) can be introduced later for semantic retrieval.
- **Streamlit Demo (`web/streamlit_app.py`)** — simple front-end to exercise the API for demos and manual QA.

## Data Flow Examples

### Chat Corrections
1. `/api/chat/correct` receives learner text.
2. Router loads `prompts/chat-correct.poml`, renders the template, and calls the LLM client.
3. JSON output is validated via `app/services/parser.py`.
4. Transcripts and trace IDs are written to `messages` while failures go to `prompt_errors`.

### Quiz Generation
1. `/api/quiz/generate` requests topics/length.
2. Prompt runtime renders `prompts/quiz-gen.poml`.
3. Parsed quiz questions are persisted (`quizzes` + `quiz_items`).
4. `/api/quiz/answer` fetches the stored quiz, evaluates answers, and updates stats.

### Flashcards & SM-2
1. Flashcards live in the `flashcards` table with ease, interval, repetition, and due timestamps.
2. `GET /api/flashcards/due` surfaces the queue.
3. `POST /api/flashcards/review` passes responses through the `srs.review_card` function to compute next intervals and updates the DB.

### Stats
- Simple aggregates (chat count, quiz count, flashcard reviews, due cards) are derived from `stats_daily` plus live card queries.
- Results are exposed to Streamlit for at-a-glance dashboards.

### Call-Style Coaching
- The `prompts/call-coach.poml` plus runtime plumbing lays the groundwork for future PRs that will convert text to voice or telephony experiences.

## Deployment Targets

- **Local dev** via uvicorn + streamlit.
- **Docker Compose** for paired API + demo containers sharing a SQLite volume.
- **CI** via GitHub Actions with ruff, pytest+coverage, bandit, poml-lint, release-please, and CodeQL workflows.
