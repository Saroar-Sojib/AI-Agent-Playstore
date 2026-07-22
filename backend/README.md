# AgentHub — Backend

A "Play Store" for AI agents: browse a catalog of ~100 profession-based AI
personas, sign up/log in **scoped to exactly one agent**, and chat with it —
each turn calling a real LLM (Gemini) with that agent's system prompt.

This repo is the backend only (FastAPI). Frontend, deployment, and a real
Gemini API key end-to-end run are tracked separately — see
[Known limitations](#known-limitations).

## Stack

- **FastAPI** (async) + **SQLAlchemy 2.0** (async, asyncpg) + **Alembic**
- **PostgreSQL** — primary datastore
- **Redis** — rate limiting + JWT revocation (fails open if unavailable)
- **Gemini** (`generateContent` REST API, called directly via `httpx` —
  no SDK dependency) for chat completions
- **pytest** for tests, **GitHub Actions** for CI

## Setup (local)

1. **Start Postgres + Redis:**
   ```bash
   docker compose up -d postgres redis
   ```
2. **Create your env file:**
   ```bash
   cp .env.example .env
   # Fill in SECRET_KEY (python -c "import secrets; print(secrets.token_urlsafe(32))")
   # and LLM_API_KEY (free tier: https://aistudio.google.com/apikey)
   ```
3. **Install dependencies** (Python 3.12):
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements-dev.txt   # includes requirements.txt + pytest
   ```
4. **Run migrations:**
   ```bash
   alembic upgrade head
   ```
5. **Seed the agent catalog** (the content pipeline — turns
   `data/agents_sample.csv` into ~100 `Agent` + ~400 `SubAgent` rows, deriving
   each `system_prompt` from the row's own Industry/Profession/Task columns,
   no hand-written prompts):
   ```bash
   python -m scripts.seed_agents
   ```
6. **Run the app:**
   ```bash
   uvicorn app.main:app --reload
   # http://localhost:8000/docs for interactive API docs
   ```

### Running tests

Tests run against a **real Postgres** (not SQLite/mocks) — the async engine
is asyncpg-specific and the isolation guarantees are worth testing against
the real dialect. Point them at a scratch database:

```bash
docker run -d --name agenthub-test-pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_agent_playstore_test -p 5432:5432 postgres:16-alpine

TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_agent_playstore_test \
TEST_DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_agent_playstore_test \
pytest -v
```

`conftest.py` creates/drops all tables itself (`Base.metadata.create_all`,
bypassing Alembic) and wipes rows between tests — no fixtures/seed data
required beyond what each test creates. The Gemini call is monkeypatched in
chat tests, so no network access or real API key is needed to run the suite.
CI (`.github/workflows/ci.yml`) runs the same thing against a Postgres
service container on every push.

## API overview

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/api/v1/auth/signup` | — | body: `agent_slug, email, password` |
| POST | `/api/v1/auth/login` | — | body: `agent_slug, email, password` |
| POST | `/api/v1/auth/refresh` | refresh cookie | rotates refresh token |
| POST | `/api/v1/auth/logout` / `/logout-all` | bearer | revokes via Redis denylist |
| POST | `/api/v1/auth/change-password` | bearer | revokes all sessions |
| GET | `/api/v1/agents/` | — | paginated catalog |
| GET | `/api/v1/agents/{slug}` | — | agent detail (no `system_prompt` in response) |
| GET | `/api/v1/agents/{slug}/sub-agents` | — | that agent's 2–5 sub-agents |
| POST | `/api/v1/agents/{slug}/chat` | bearer | chat with the main persona |
| POST | `/api/v1/agents/{slug}/sub-agents/{id}/chat` | bearer | chat with one sub-agent |
| GET | `/api/v1/agents/{slug}/conversations/{id}/messages` | bearer | reload history |
| GET | `/api/v1/users/me` | bearer | |

Full interactive schema at `/docs` once running.

## Architecture decisions

**Agent-scoped auth, not full multi-tenant RBAC.** This backend started from
an existing multi-tenant "Field Force SaaS" template (tenants, companies,
role/permission RBAC, employees, audit log, file storage, transactional
outbox). Almost all of that was deleted rather than adapted — AgentHub's
isolation requirement ("a login scoped to one agent, no cross-agent access")
is a much shallower problem than B2B multi-company RBAC, and keeping the
unused machinery around would have violated the "architecture that visibly
isn't 100 copies of the same code" criterion in spirit even where it didn't
in fact. What survived: JWT issuance/verification, bcrypt hashing, the
Redis-backed rate limiter, and the repo/service/router layering pattern —
all genuinely reusable. What's new: the `agents` module (`Agent` model
doubles as both the catalog item and the auth-scope boundary) and the `chat`
module.

**Isolation mechanism: `UNIQUE(agent_id, email)` on `users`, not separate
databases/services per agent.** A user row belongs to exactly one agent;
the same email can independently sign up under two different agents because
uniqueness is scoped, not global. This is enforced at three layers: the DB
constraint, the login lookup (`WHERE email = ? AND agent_id = ?`, never
`WHERE email = ?` alone), and the JWT's `agent_id` claim, which every
chat/conversation endpoint checks against the resource being accessed
(`user.agent_id != agent.id` → 403). Chosen over fully separate
auth systems per agent because with ~100 (and growing) agents, provisioning
a new Postgres schema/service per agent would turn "agent #101 is a config
row" into "agent #101 is an infra deploy" — the opposite of the assignment's
core architectural requirement.

**Agents and sub-agents are data, not code.** `Agent` (id, slug, industry,
profession, `system_prompt`) and `SubAgent` (id, agent_id, name,
task_description, `system_prompt`, order_index) are the entire mechanism —
the chat endpoint resolves whichever `system_prompt` applies and passes it
to Gemini as `system_instruction`. Adding agent #101 is one CSV row plus a
script re-run; no route, model, or branch of code changes.

**LLM integration: Gemini's REST API directly via `httpx`, not the
`google-genai` SDK.** `httpx` was already a dependency; adding the SDK for
one call type (`generateContent`) seemed like unnecessary surface area for a
5-day project. The client (`llm_client.py`) is ~90 lines and wraps every
failure mode (timeout, non-200, malformed payload) in one `LLMError` so the
chat service never has to know about `httpx`/Gemini specifics.

**Content pipeline is a plain script, not a UI**, per the assignment's own
"a script is sufficient" — `scripts/seed_agents.py` reads
`data/agents_sample.csv` (the provided `agents_sample.xlsx`, converted once
to CSV to avoid an `openpyxl` runtime dependency) and derives every
`system_prompt` from that row's own columns via a template — nothing is
hand-written per agent. It's idempotent (matches existing rows by
`source_row_no` and updates in place), so it doubles as the "admin path to
add a new agent with zero code changes" stretch goal: edit the CSV, re-run.

**Rate limiting / cost control on LLM calls.** A Redis fixed-window counter
(`app/core/rate_limit.py`), keyed by bearer-token-or-IP, applied to
signup/login/refresh and both chat endpoints. Fails open if Redis is down —
availability over strict enforcement felt like the right tradeoff for a
side project, not a bank.

## What I'd do differently with more time

- **Streaming responses.** Gemini supports `streamGenerateContent`; the chat
  endpoint currently waits for the full completion before responding, which
  will feel slow for longer replies.
- **A real admin API for the content pipeline**, not just a script — e.g. an
  authenticated `POST /admin/agents/sync` that runs the same logic, so
  refreshing the catalog doesn't require shell access to the deployment.
- **An observability endpoint/dashboard** over `usage_logs` — the table
  captures per-request status/latency/tokens already, but nothing surfaces
  it yet beyond raw SQL.
- **Conversation titling and pagination** — conversations currently have no
  auto-generated title and message history has no pagination; fine at demo
  scale, not at real scale.
- **Move off `@app.on_event`** (deprecated in favor of FastAPI's `lifespan`
  context manager) — left as-is to match this repo's existing convention
  rather than a mid-project style change.

## Known limitations

- **No frontend, no deployment, and no real-Gemini-key end-to-end run
  yet** — this backend has been verified against a real (throwaway,
  Dockerized) Postgres + Redis with every endpoint hit directly, and the
  LLM call path has been verified for its request/response handling and
  error paths, but not against a live Gemini key yet.
- **`GET /agents/{slug}` intentionally omits `system_prompt`** from the
  public response (it's an implementation detail, not something a client
  needs) — flag if the eventual frontend turns out to need it server-side
  for some reason.
- **No admin authentication tier.** Adding/editing agents is done via the
  seed script with direct DB/repo access, not through an authenticated
  in-app role — acceptable for this project's scope (RBAC was deliberately
  removed as overkill for "user belongs to one agent"), but would need
  revisiting before letting untrusted people manage the catalog.
- **Rate limiter is fixed-window, not sliding-window/token-bucket** — simple
  and sufficient for abuse prevention, but bursty at window boundaries.

## AI-assisted development disclosure

This backend was built with **Claude Code** (Anthropic's CLI agent) as the
primary coding tool, working from an existing multi-tenant SaaS template the
author had from a prior project. Claude Code: read and summarized the
assignment PDF, the agent data spreadsheet, and the architecture diagrams;
audited the existing template module-by-module for what to keep, delete, or
adapt; performed the RBAC removal and tenant→agent conversion; built the
sub-agent/chat/LLM-integration module and the content pipeline script; wrote
the test suite and CI workflow; and ran real, live verification (spinning up
throwaway Postgres/Redis containers via Docker and exercising the actual
HTTP API) rather than relying on static review alone — including catching
and fixing two real bugs this way (signup returning HTTP 200 instead of
201; the rate limiter being wired to endpoints but never actually connected
to a live Redis client, silently failing open). All changes were reviewed,
tested against a live database, and committed incrementally by the author
rather than applied as one large unreviewed diff.
