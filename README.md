# English IA - Backend

Backend FastAPI + SQLite focado em pratica de conversacao em ingles. A API controla sessoes de dialogo, gera quizzes contextualizados, cria flashcards via SM-2 e expõe KPIs para dashboards. Nao existe frontend neste repositório.

## Destaques

- **Temas de pratica**: `/api/practice/topics` retorna os topicos seedados (travel, technology, etc.).
- **Ciclo da sessao**: `POST /api/sessions` cria a sessao com prompt orientado ao topico, `POST /api/chat/{session}` registra conversa + heuristicas de erro, `POST /api/sessions/{session}/finish` produz quizzes/flashcards e marca a sessao como pronta para avaliacoes. O relatorio so libera apos responder todos os quizzes.
- **Quizzes contextualizados**: gerados a partir de erros e dos ultimos trechos da conversa (lugares citados, detalhes da viagem, etc.), sempre com uma alternativa correta.
- **Relatorios com quiz_summary**: consolidam palavras, erros, CEFR estimado e desempenho nos quizzes (total, corretos, accuracy).
- **LLM modular**: registry alterna entre `simple_mock`, `ollama` e `openai`; `/api/settings` atualiza provider/modelo.
- **Infra pronta**: migrations Alembic, seed idempotente, Dockerfile + docker compose, hooks de qualidade (Ruff, Black, pytest) e CI no GitHub Actions.

## Requisitos

- Python 3.11+
- SQLite (bundle do Python ja atende)
- Pip/venv para isolar dependencias

## Como rodar localmente

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env

# aplica migrations e insere seed (tambem ocorre automaticamente no startup do FastAPI)
alembic upgrade head
python -m app.repo.seed

uvicorn app.main:app --reload
```

Docs interativas: http://localhost:8000/docs e http://localhost:8000/redoc.

## Docker / Compose

```bash
docker compose up --build
```

O servico `api` expõe a porta 8000 e monta o workspace para hot reload. Ha um bloco comentado para subir o Ollama lado a lado.

## Banco de dados e migrations

- URL padrao: `sqlite:///./data.db` (defina `DATABASE_URL` se quiser Postgres/MySQL).
- Rodar migration: `alembic upgrade head`. O lifespan do FastAPI executa `alembic upgrade head` automaticamente no bootstrap, portanto basta garantir que o arquivo `alembic.ini` esteja configurado.
- Seed: `python -m app.repo.seed` cria usuario default, settings e topicos.

## Variaveis de ambiente (.env)

```
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./data.db
DEFAULT_LLM_PROVIDER=simple_mock
DEFAULT_LLM_MODEL=mock-1
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=
```

Personalize `CORS_ORIGINS` se expor para frontends externos. Para usar o provider `openai`, defina `OPENAI_API_KEY`. Para `ollama`, garanta que o endpoint esteja acessivel no host configurado.

## Fluxo completo recomendado

1. `GET /api/practice/topics` para preencher a UI de escolha do tema.
2. `POST /api/sessions` (body opcional `{ "topic_code": "travel" }`). Resposta inclui `session_id` + prompt do tutor.
3. `POST /api/chat/{session_id}/message` repita quantas vezes quiser (minimo 3 recomendado). Cada chamada detecta erros (`detected_errors`) e grava a replica do LLM escolhido.
4. `POST /api/sessions/{session_id}/finish` ao encerrar a conversa. Esta etapa cria quizzes baseados nas mensagens e flashcards derivados dos erros. O campo `report_ready` vira `false` ate os quizzes serem respondidos.
5. `GET /api/quiz/by-session/{session_id}` para obter os quizzes.
6. `POST /api/quiz/{quiz_id}/answer` para cada quiz. A resposta contem `report_ready`; so apos o ultimo quiz respondido o relatorio eh liberado e o snapshot de metricas eh escrito.
7. `GET /api/reports/{session_id}` para ler o resumo (se todos quizzes foram respondidos).
8. `GET /api/flashcards/due` + `POST /api/flashcards/{id}/review` para revisoes SM-2; use `POST /api/flashcards/manual` para criar cards manuais.
9. `GET /api/dashboard/summary` para exibir KPIs agregados (tempo de estudo, palavras aprendidas, conversas, fluency level, due cards).
10. `GET/POST /api/settings` para trocar de provider LLM durante o fluxo.

## Documentacao detalhada da API

### Health

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `GET` | `/healthz` | status do servico |

Resp 200:
```json
{ "status": "ok" }
```

### Practice

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `GET` | `/api/practice/topics` | Lista os temas seedados. |

### Sessoes

| Metodo | Rota | Payload | Descricao |
| --- | --- | --- | --- |
| `POST` | `/api/sessions` | `{ "topic_code": "travel" \| null }` | Cria sessao e retorna prompt do tutor. |
| `POST` | `/api/sessions/{session_id}/finish` | - | Gera quizzes (3-5) + flashcards. `report_ready` permanece `false` ate quizzes terminarem. |

Exemplo de criacao:
```json
{
  "session_id": "c8f...",
  "topic_code": "travel",
  "topic_label": "Travel",
  "topic_description": "Discuss trips...",
  "system_prompt": "You are a patient tutor...",
  "status": "active",
  "started_at": "2025-11-19T20:24:35.125872+00:00",
  "ended_at": null
}
```

Resultado do finish:
```json
{
  "quizzes_created": 4,
  "flashcards_created": 2,
  "report_ready": false
}
```

### Chat

| Metodo | Rota | Payload | Descricao |
| --- | --- | --- | --- |
| `POST` | `/api/chat/{session_id}/message` | `{ "text": "..." }` | Salva mensagem do usuario, detecta erros, chama LLM (registry), armazena replica do assistente. |

Resposta:
```json
{
  "reply": "Here is a clearer version...",
  "detected_errors": [
    {
      "start": 0,
      "end": 10,
      "category": "grammar",
      "user_text": "I am agree",
      "corrected_text": "I agree",
      "note": "Use agree sem o verbo auxiliar."
    }
  ]
}
```

### Quiz

| Metodo | Rota | Payload | Descricao |
| --- | --- | --- | --- |
| `GET` | `/api/quiz/by-session/{session_id}` | - | Lista quizzes da sessao (MCQ ou cloze). |
| `POST` | `/api/quiz/{quiz_id}/answer` | `{ "choice": "texto", "latency_ms": 1234 }` | Registra tentativa, cria flashcard se erro reincidente e informa se o relatorio ja esta pronto. |

Exemplo de resposta no envio de resposta:
```json
{
  "quiz_id": "quiz1",
  "is_correct": true,
  "flashcard_created": false,
  "report_ready": true
}
```

### Relatorios

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `GET` | `/api/reports/{session_id}` | Libera apenas apos todos os quizzes terem uma resposta. |

Resposta:
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

| Metodo | Rota | Payload | Descricao |
| --- | --- | --- | --- |
| `GET` | `/api/flashcards/due` | - | Lista cards vencidos (SM-2). |
| `POST` | `/api/flashcards/{id}/review` | `{ "quality": 0..5 }` | Recalcula reps/interval/ease e agenda nova data. |
| `POST` | `/api/flashcards/manual` | `{ "front": "...", "back": "..." }` | Cria card manual. |

### Dashboard

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `GET` | `/api/dashboard/summary` | Retorna `study_time_hours`, `words_learned`, `conversations`, `fluency_level` e `due_flashcards`. |

### Settings

| Metodo | Rota | Payload | Descricao |
| --- | --- | --- | --- |
| `GET` | `/api/settings` | - | Le provider/modelo atuais. |
| `POST` | `/api/settings` | `{ "llm_provider": "simple_mock\|ollama\|openai", "llm_model": "..." }` | Atualiza provider/modelo; valida provider e exige nome de modelo. |

### WebSocket

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `WS` | `/ws/call` | Stub para modo voz: aceita conexao, envia evento `start`, ecoa mensagens como `partial` e encerra com `final`. |

## Qualidade e CI

- `ruff check .` – lint padrao (hook pre-commit e step no GitHub Actions).
- `black .` / `ruff format .` – formatacao.
- `pytest` – inclui testes de heuristica (`errors`), quiz generation contextual, relatorios (quiz summary), settings DAO e SM-2.
- `.github/workflows/ci.yml` instala dependencias, roda Ruff, Bandit e pytest em cada push/PR.

## Licenca

MIT License (ver `LICENSE`). Contributions seguem `CONTRIBUTING.md` e `CODE_OF_CONDUCT.md`.
