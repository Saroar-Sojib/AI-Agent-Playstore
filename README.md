# AgentHub — AI Agent Playstore

A "Play Store" for AI agents: browse a catalog of ~100 profession-based AI
personas, sign up for one specifically, and chat with it (and its specialized
sub-agents) — every reply powered by a real LLM (Gemini).

## 🚀 Live Demo

| | |
|---|---|
| **Frontend** | [agent-hub-frontend-frkh.onrender.com](https://agent-hub-frontend-frkh.onrender.com) |
| **Backend API** | [agent-hub-backend-7vtg.onrender.com](https://agent-hub-backend-7vtg.onrender.com) |

> ⏳ **Heads up — first load takes ~30–60 seconds.**
> This is hosted on **free-tier** infrastructure, which puts services to sleep
> after a period of inactivity. Your **first click** wakes the server up — the
> page will show a friendly "waking up the server…" screen and retry
> automatically, no need to refresh manually. Once it's awake, everything runs
> at normal speed until it goes idle again.

## What it does

- Browse a catalog of AI agents, each one a distinct profession persona
  (e.g. Financial Controller, Loan Officer, Relationship Manager)
- Sign up / log in **scoped to one agent** — your account only ever talks to
  that agent
- Chat with the main agent persona, or switch to one of its specialized
  sub-agents, each with its own focused system prompt
- Every reply is generated live by Google's Gemini API — no canned responses

## Architecture

<img src="system design.png" alt="System design" width="700">
<img src="db_design.png" alt="Database design" width="700">

## Tech stack

| | |
|---|---|
| **Frontend** | Next.js (App Router), React, Tailwind CSS |
| **Backend** | FastAPI (async), SQLAlchemy 2.0 + Alembic, PostgreSQL, Redis |
| **LLM** | Gemini `generateContent` REST API (direct `httpx` call, no SDK) |
| **CI** | GitHub Actions (separate pipelines for `frontend/` and `backend/`) |
| **Hosting** | Render (both services), Upstash (Redis) |

## Repo structure

```
.
├── backend/    FastAPI service — see backend/README.md for local setup
└── frontend/   Next.js app     — see frontend/README.md for local setup
```

Each folder has its own README with full local development instructions
(env vars, running migrations, seeding the agent catalog, running tests).

## Running locally

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # fill in SECRET_KEY, LLM_API_KEY
alembic upgrade head
python -m scripts.seed_agents
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env.local   # BACKEND_URL=http://localhost:8000
npm run dev
```

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md)
for details.
