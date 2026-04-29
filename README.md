# AT&T Account Platform (Nexus)

Internal web platform for the Accenture AT&T account: programs, portfolios, teams,
resources, AI adoption tracking, PPT generation, and conversational AI.

## Stack
- Backend: FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL 16 (pgvector)
- Frontend: React 18 + TypeScript + Vite + TanStack Router + Query + Tailwind
- LLM: Ollama (`llama3.2`) + LangChain / LangGraph / LangSmith
- Auth: Azure Entra ID (MSAL)
- Storage: Azure Blob (with local fallback)

## Local setup

```bash
# 1. Start infra
docker-compose up postgres ollama -d

# 2. Pull Ollama models
docker-compose exec ollama ollama pull llama3.2
docker-compose exec ollama ollama pull nomic-embed-text

# 3. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 4. Frontend
cd frontend
npm install
cp .env.example .env
npm run dev   # http://localhost:5173
```

## Project layout

```
backend/
  app/
    main.py, config.py, database.py
    auth/      entra.py, rbac.py
    models/    hierarchy, resource, program, ai_adoption, slides, embeddings
    schemas/   pydantic schemas matching models
    routers/   hierarchy, programs, resources, ai_adoption, slides, chat, reports
    services/  blob, ppt, ingestion, embedding
    agents/    base, platform_agent, slide_agent, tools/
  alembic/     migrations (0001_initial)
frontend/
  src/
    main.tsx, router.tsx, index.css
    auth/      msalConfig, AuthProvider
    api/       client + per-domain modules
    pages/     ProgramsPage, ProgramDetailPage, PortfolioPage,
               TeamPage, ResourcePage, AIAdoptionPage,
               SlideGeneratorPage, ChatPage, AdminPage
    components/ layout, programs, hierarchy, resources, ai-adoption,
                slides, chat, shared
    hooks/     usePrograms, useHierarchyNode, useChat
docker-compose.yml
```

## Notes
- RBAC roles: `account_admin`, `portfolio_lead`, `subportfolio_lead`, `team_lead`, `pm`, `member`.
- Recursive team/portfolio queries use PostgreSQL `WITH RECURSIVE` CTEs.
- Slide generation runs as a background job; poll `/api/slides/jobs/{id}` and download when complete.
- AI placeholder tokens (e.g. `{{EXEC_SUMMARY}}`) are resolved by Ollama; data tokens (e.g. `{{PROGRAM_NAME}}`) by direct DB query.
- LangSmith tracing is automatic when `LANGCHAIN_TRACING_V2=true` and a key is set.
- For dev without Azure Blob, files write to `./local_blobs/`.
- Add a pgvector index after data load:
  `CREATE INDEX ON document_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`
