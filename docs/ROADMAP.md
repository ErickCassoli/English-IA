# English-IA — Análise de Estado e Roadmap

> Documento de diagnóstico técnico e direção de produto.
> Gerado a partir de uma varredura do backend (`/api`), frontend (`/web`), testes, CI e Docker.
> Data da análise: 2026-10-17.

---

## 1. Visão geral

English-IA é um monorepo full-stack de um tutor de inglês por IA:

- **Backend** (`/api`): FastAPI + SQLAlchemy 2 + SQLite, com Alembic, prompts em arquivos `.poml`.
- **Frontend** (`/web`): React 19 + Vite 7 + TypeScript 5.9 + Tailwind 4 + Radix UI + Framer Motion.
- **DevOps**: Docker Compose (api + web/nginx), GitHub Actions.

**Fluxo principal (funciona ponta a ponta):**

```
Placement test → Criar sessão (tópico) → Chat com detecção de erros
   → Finish (gera quiz) → Submit quiz (gera flashcards SRS) → Relatório
```

**Estado dos testes:** 7 testes unitários passando (`srs`, `errors`, `quizgen`, `report`, `settings`). Sem testes de rota/integração no backend; apenas 1 teste no frontend.

---

## 2. Pontos fortes

- **Separação de camadas limpa** no backend: `routers/`, `services/llm/` (abstração com registry), `services/evaluation/` (SRS, quizgen, placement, report), `repo/` (models + DAO), `schemas/`.
- **Prompts externalizados** em `.poml` — fáceis de iterar sem tocar em código.
- **Padrão Registry para LLM** — `registry.get_llm()` deixa os routers agnósticos de provider.
- **SRS (SM-2) isolado e testado** em `services/evaluation/srs.py`.
- **Placement gate** no backend (HTTP 403 antes de liberar o chat).
- **Frontend organizado por página/rota** com cliente de API tipado (`services/api.ts`).

---

## 3. Lacunas entre o que é prometido e o que roda

Estes itens não são bugs pontuais: são desalinhamentos que confundem quem lê o repo e quem usa o produto.

### 3.1 "Google Gemini" não existe no código
- O README anuncia suporte a **Google Gemini**.
- A CI (`.github/workflows/ci.yml`) roda com `LLM_PROVIDER=google` e `GOOGLE_API_KEY=dummy`.
- Mas o enum `LLMProvider` (`api/app/repo/models.py`) só tem `simple_mock`, `ollama`, `openai`, e **não existe `GoogleClient`**.
- O `registry.get_llm()` cai em `SimpleMockClient` **silenciosamente** quando o provider é desconhecido.
- **Efeito:** README e CI prometem uma capacidade inexistente; a CI, na prática, testa contra o mock.

### 3.2 Dois mecanismos de placement concorrentes
- **(a) Estático:** `routers/placement.py` com 25 perguntas fixas (`/api/placement/questions` + `/submit`) — é o que o frontend usa hoje.
- **(b) Conversacional:** `services/evaluation/placement.py` + prompts `placement_test.poml`/`placement_assessment.poml` + tópico `placement_test`, acionado dentro de `finish_session`.
- **Efeito:** dois caminhos para o mesmo resultado (nível CEFR), sem fonte única de verdade. Risco de divergência de nível.

### 3.3 As "skills" do dashboard são fabricadas
- Reading / Writing / Listening / Speaking (`api/app/repo/dao.py`, ~linha 429) derivam todas de um único `base_score` com offsets fixos (`+5 / 0 / −5 / −10`).
- **Efeito:** o radar de habilidades passa impressão de medição real que não existe.

### 3.4 A avaliação "inteligente" é rasa sem LLM externo
- Detecção de erros base = punhado de regex (`"peoples"`, `"i am agree"`, `"more better"`, `"i have X years"`) em `services/evaluation/errors.py`.
- CEFR do relatório = heurística `1 − (erros / palavras)` em `services/evaluation/report.py`.
- Como o provider default é `simple_mock`, **sem plugar OpenAI/Ollama o valor pedagógico é mínimo**.

---

## 4. Dívida técnica

| # | Item | Onde | Impacto |
|---|------|------|---------|
| 1 | **LLM 100% síncrono/bloqueante** — `httpx.post` em endpoints não-async | `services/llm/*.py`, `routers/chat.py` | Trava o event loop sob carga; sem streaming de chat (UX de tutor sofre) |
| 2 | **Interface `reply()` só retorna string** — sem saída estruturada | `services/llm/base.py` | Força parsing frágil de JSON "procurando `{ }`" em errors/quizgen/placement |
| 3 | **`init_db()` (create_all) em runtime; `upgrade_db()` comentado** | `main.py` (lifespan) | Alembic existe mas não é a fonte de verdade → risco de drift de schema |
| 4 | **`print()` / `traceback.print_exc()` de debug** | quizgen, placement, sessions | Deveria usar `logger`; há `error_log.txt` versionado |
| 5 | **Ruído no repositório** | `api/scripts/*` (~14), `api/legacy/` (Streamlit), `error_log.txt` | Dificulta navegação; código morto versionado |
| 6 | **Single-user, sem auth** | `dao.ensure_default_user` | OK para MVP local; é o teto para multi-usuário / deploy real |
| 7 | **`/ws/call` ("voice mode") é só stub de echo** | `ws/call.py` | Funcionalidade de voz implícita não existe |
| 8 | **Quizgen determinístico fraco** | `services/evaluation/quizgen.py` | Distractors por heurística (`in`→`on`), fallbacks tipo "I don't know" |
| 9 | **Cobertura de teste baixa** | `api/tests`, `web/src` | Sem testes de rota/integração; 1 teste de frontend |
| 10 | **CI não roda lint/segurança** | `.github/workflows/ci.yml` | `ruff`/`bandit`/`black` estão em `requirements-dev` e no pre-commit mas não na CI |
| 11 | **CORS default restrito a `localhost:8000`** | `utils/config.py` | Frágil fora do proxy nginx/vite |

---

## 5. Roadmap proposto (priorizado)

Três fases. A recomendação é **não empilhar features novas antes da Fase 0**.

### Fase 0 — Sanear a base (alinhar realidade × promessa)
*Objetivo: o repo passa a dizer a verdade e a base para de acumular risco.*

- [ ] **Decidir o provider real** e implementá-lo de fato (Gemini **ou** assumir OpenAI/Ollama). Corrigir README e CI para refletir o que existe.
- [ ] **Fazer o registry falhar de forma visível** (log/erro) quando o provider for desconhecido, em vez de cair no mock em silêncio.
- [ ] **Unificar o placement** num único mecanismo (recomendado: manter o estático de 25 perguntas como baseline; aposentar o conversacional, ou vice-versa — mas só um).
- [ ] **Ativar Alembic em runtime** (`upgrade_db()`) e parar de usar `create_all` como fonte de verdade.
- [ ] **Trocar `print()` por `logger`** e remover `error_log.txt` do versionamento (adicionar ao `.gitignore`).
- [ ] **Limpar `api/scripts/` e `api/legacy/`** (mover para fora do repo ou deletar o que é throwaway).
- [ ] **Rotular as "skills" do dashboard como estimativas** ou removê-las até existir medição real.

### Fase 1 — Fechar o MVP com confiança
*Objetivo: o fluxo atual (single-user, local) fica redondo e confiável.*

- [ ] **Tornar as chamadas de LLM async** (`httpx.AsyncClient`) e adicionar **streaming no chat**.
- [ ] **Introduzir saída estruturada** no `LLMClient` (método tipo `reply_json(schema)`), eliminando o parsing frágil.
- [ ] **Testes de integração de rota** (chat, sessions, placement, flashcards) com o mock.
- [ ] **Melhorar o quizgen determinístico** (distractors plausíveis) para quando o LLM não responder.
- [ ] **Rodar ruff/bandit na CI** e testar contra um provider real que exista.
- [ ] **Mais testes de frontend** nas páginas-chave (Chat, Report, Flashcards).

### Fase 2 — Evoluir produto
*Objetivo: crescer além do MVP local.*

- [ ] **Auth + multi-usuário** (substituir `ensure_default_user`; migrar SQLite → Postgres).
- [ ] **Voz real** no lugar do stub `/ws/call` (STT/TTS), destravando listening/speaking de verdade.
- [ ] **Avaliação CEFR e skills reais** baseadas em rubrica + evidência de conversa, não em heurística de contagem de erros.
- [ ] **Flashcards/quiz gerados por LLM** com qualidade pedagógica e revisão.

---

## 6. Resumo executivo

A **estrutura do projeto é sólida** e o fluxo principal funciona. Os maiores riscos hoje são de **alinhamento** (README/CI prometem Gemini que não existe; placement duplicado; skills fabricadas) e de **base técnica** (LLM síncrono sem streaming, migrations não aplicadas em runtime, ruído versionado). A recomendação é executar a **Fase 0** antes de qualquer feature nova, para que o repositório volte a refletir a realidade e pare de acumular dívida — e só então evoluir o produto.
