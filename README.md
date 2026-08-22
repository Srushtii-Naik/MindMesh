# MindMesh

**The AI companion that remembers your life, so you don't have to manage it across a dozen apps.**

> Status: Version 1.0 — Milestone 12 (Production & Deployment) Complete

---

## Table of Contents

- [Project Overview](#project-overview)
- [Why MindMesh?](#why-mindmesh)
- [Features](#features)
- [Target Users](#target-users)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Development Roadmap Summary](#development-roadmap-summary)
- [Installation](#installation)
- [Production Deployment](#production-deployment)
- [Documentation](#documentation)
- [Future Vision](#future-vision)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

MindMesh is a single, intelligent layer that sits above the fragmented tools people use to manage their lives — tasks, calendars, reminders, notes, and family coordination — and quietly does the remembering, connecting, and organizing so people don't have to.

Rather than being "another app," MindMesh is designed as a **relationship**: an AI companion that knows a person's context over time, across every domain of daily life, and proactively reduces the mental load of staying organized. It is built to be private, adaptive, and genuinely useful from day one — with the long-term ambition of becoming the default "second brain" for individuals and families alike.

## Why MindMesh?

The average person manages their life across 8–15 disconnected applications — a calendar, a to-do list, a notes app, reminders, family group chats, and a stateless AI chatbot for questions. Each is excellent in isolation and nearly useless in combination. This fragmentation creates real, chronic costs:

- **Cognitive overload** — users act as the "human API," manually re-entering the same information across multiple tools.
- **Context loss** — no single tool knows a user's whole life, so nothing can be genuinely proactive.
- **App-switching fatigue** — constant context-switching carries a measurable cost in focus and time.
- **Family and caregiving blind spots** — parents, seniors, and children are rarely served by the same tools.
- **AI chat tools that forget** — general-purpose chatbots are powerful but stateless, forcing users to re-explain themselves constantly.

| Category of Existing Solution | Why It Falls Short |
|---|---|
| Single-purpose productivity apps | Solve one narrow slice of life; the user becomes the integration layer. |
| General-purpose AI chatbots | Powerful reasoning, but stateless and reactive — not built for a persistent life record. |
| "All-in-one" workspace tools | Built for enterprise workflows, not personal or family life; too complex for children or seniors. |
| Smart home / voice assistants | Good at simple commands, but shallow memory and minimal life-context reasoning. |
| Family organizer apps | Typically calendar-and-chore-chart tools with no real intelligence or adaptation. |

MindMesh is designed to close this gap by combining **deep personal memory, cross-domain intelligence, proactive behavior, and an interface that adapts to who is using it** — in one trusted, private product.

## Features

### Launch Scope (Current)

- AI Companion Chat — natural-language interface to the entire system
- Smart Task Manager
- Unified Calendar
- Context-Aware Reminders
- Notes & Personal Knowledge Capture
- Persistent Personal Memory ("MindMesh remembers")
- Family/Household Mode with linked profiles
- Adaptive Interface (complexity adjusts to user persona)
- Unified Notification Center
- Cross-Module Auto-Linking (e.g., note → task → reminder chains)
- Simple Onboarding & Preference Setup
- Basic Voice Input for supported modules

### Planned (Post-Launch Roadmap)

- Full voice-first companion mode (hands-free operation)
- Wearable device integration for health and routine tracking
- Deeper third-party integrations (email, banking notifications, health apps) via secure connectors
- Advanced family coordination (shared budgets, chore delegation with rewards for children)
- AI-powered life insights and pattern recognition (e.g., stress trends, routine drift)
- Multi-language and regional localization
- Offline-first mode for low-connectivity environments
- Enterprise/team companion variant (long-term expansion, not initial focus)
- Caregiver mode for eldercare support with remote family visibility (with explicit consent)

## Target Users

MindMesh is designed as a household and individual companion, not a niche vertical tool.

| Persona | Core Need |
|---|---|
| **The Child** (e.g., age 9) | Extremely simple UI, encouraging tone, parental oversight, homework/chore reminders |
| **The Student** (e.g., age 20) | Deadline tracking, study reminders, quick capture, help breaking down large projects |
| **The Professional** (e.g., age 34) | Fast task capture, intelligent prioritization, context-aware reminders, minimal manual entry |
| **The Parent** (e.g., age 41) | Shared family visibility, delegated tasks, reminders across multiple schedules |
| **The Senior Citizen** (e.g., age 68) | Large, high-contrast UI, voice-first interaction, gentle and clear reminders |

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript, Vite, Tailwind CSS |
| Server State | TanStack Query |
| UI/Local State | Zustand |
| Forms | React Hook Form |
| Routing | React Router (with route-level code splitting) |
| Animation | Framer Motion |
| HTTP Client | Axios (centralized client with interceptors) |
| Backend | Django + Django REST Framework |
| Database | PostgreSQL |
| Cache / Broker | Redis |
| Background Jobs | Celery (with Celery Beat for scheduling) |
| AI Providers | Gemini, OpenAI — behind an internal AI Provider Abstraction Layer |
| Auth | JWT (access + refresh tokens), Google OAuth |
| Reverse Proxy | Nginx |
| Containerization | Docker / Docker Compose |
| Deployment | Backend on Railway, Frontend on Vercel |

## System Architecture

MindMesh follows a **modular, layered client-server architecture** with a decoupled frontend and backend communicating over a versioned REST API (`/api/v1/`), built around Clean Architecture principles so that infrastructure (AI provider, database, task queue) can evolve independently of business logic.

```
Client (React SPA)
      │
      ▼
Nginx (TLS termination, routing, rate limiting)
      │
      ▼
Backend (Django + DRF)
      │
      ├──▶ Service Layer (business logic)
      ├──▶ Repository / Data Access Layer
      ├──▶ AI Provider Abstraction Layer ──▶ Gemini / OpenAI adapters
      │
      ▼
PostgreSQL (system of record)      Redis (cache, broker, short-lived state)
                                          │
                                          ▼
                                   Celery Workers
                          (reminders, AI processing, notifications)
```

**Guiding principles:**

- Stateless backend processes, horizontally scalable.
- PostgreSQL is the single source of truth; Redis is never authoritative.
- All AI provider calls pass through the abstraction layer — no direct SDK calls from domain code.
- The frontend never talks to the database, Redis, or AI providers directly.

The backend is organized into Django apps per domain (`accounts`, `tasks`, `notes`, `reminders`, `calendar_events`, `ai_companion`, `notifications`), each following a consistent internal layering: `models.py`, `serializers.py`, `services.py`, `repositories.py`, `tasks.py`, `urls.py`, `views.py`.

For full detail — including the AI module design, database overview, authentication flow, security strategy, and scalability strategy — see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

## Project Structure

```
mindmesh/
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios client + per-domain request definitions
│   │   ├── features/         # Feature-based modules (tasks, notes, ai-chat, reminders, calendar)
│   │   ├── components/       # Shared/reusable UI components
│   │   ├── hooks/             # Shared hooks (non-feature-specific)
│   │   ├── stores/            # Zustand stores
│   │   ├── router/            # React Router configuration
│   │   ├── styles/            # Tailwind config, design tokens
│   │   └── types/             # Shared TypeScript types/contracts
│   └── ...
│
├── backend/
│   ├── config/                # Django project settings, URL root, WSGI/ASGI
│   ├── apps/
│   │   ├── accounts/           # Auth, users, OAuth
│   │   ├── tasks/
│   │   ├── notes/
│   │   ├── reminders/
│   │   ├── calendar_events/
│   │   ├── ai_companion/       # AI abstraction layer, adapters, memory manager
│   │   └── notifications/
│   ├── common/                 # Shared utilities, permissions, exception handling
│   ├── celery_app/             # Celery configuration, task registration, beat schedules
│   └── ...
│
├── infra/
│   ├── docker/                 # Dockerfiles for frontend/backend (development + production targets)
│   ├── nginx/                  # Nginx config (dev + production-hardened)
│   ├── docker-compose.yml      # Local dev stack
│   └── docker-compose.prod.yml # Local verification of the production topology
│
└── docs/
    ├── ARCHITECTURE.md
    └── adr/                    # Architecture decision records
```

`backend/railway.json`, `frontend/vercel.json`, and
`backend/scripts/{backup,restore}_postgres.sh` / `load_test.py` (added in
Milestone 12) round out the deployment/production tooling.

## Development Roadmap Summary

Milestones are sequenced in strict dependency order, from `PROJECT_RULES.md`-aligned foundations through to Version 1.0.

| # | Milestone | Depends On | Status |
|---|---|---|---|
| 1 | Project Foundation | — | ✅ Complete |
| 2 | Authentication & User Management | Milestone 1 | ✅ Complete |
| 3 | Dashboard | Milestone 2 | ✅ Complete |
| 4 | Task Management | Milestone 3 | ✅ Complete |
| 5 | Calendar & Scheduling | Milestone 4 | ✅ Complete |
| 6 | Notes & Knowledge | Milestone 2 | ✅ Complete |
| 7 | AI Companion | Milestones 4, 5, 6 | ✅ Complete |
| 8 | Memory Engine | Milestone 7 | ✅ Complete |
| 9 | Notifications | Milestone 5, Milestone 1 infra | ✅ Complete |
| 10 | Family & Shared Workspace | Milestones 4, 5, 6 | ✅ Complete |
| 11 | Analytics & Insights | Milestones 4–8 | ✅ Complete |
| 12 | Production & Deployment | Milestones 1–11 | ✅ Complete* |

\* Security hardening, Docker production builds, monitoring/logging, backup
strategy, and load testing are complete and verified. Railway/Vercel deploy
configuration is complete and ready to use, but the live deploys themselves
require platform accounts/credentials not available in this environment —
see [Production Deployment](#production-deployment) below.

Full details, deliverables, and completion checklists for each milestone are documented in [`ROADMAP.md`](./ROADMAP.md).

> Reordering milestones, skipping completion checklist items, or pulling future-version features forward requires a deliberate revision of the roadmap — not an ad-hoc decision made mid-sprint.

## Installation

Milestone 1 (Project Foundation) is complete, so the local Docker Compose environment is available.

```bash
# 1. Copy environment templates and fill in local values
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 2. Bring up frontend, backend, PostgreSQL, and Redis together
cd infra
docker compose up --build

# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000/api/v1/
# Via Nginx: http://localhost:8080/
```

Google OAuth sign-in requires `GOOGLE_OAUTH_CLIENT_ID` (backend) and `VITE_GOOGLE_OAUTH_CLIENT_ID` (frontend) to be set to the same OAuth client ID; without it, the Google sign-in button stays hidden and email/password auth works as normal.

Notes' AI summaries (Milestone 6), the AI Companion chat with context-aware replies (Milestone 7), and the categorized long-term Memory Engine with view/edit/delete controls (Milestone 8) all work out of the box with no configuration — `AI_PROVIDER` defaults to an offline `stub` provider, so the whole AI surface is testable without any vendor account. Set `AI_PROVIDER=gemini` or `AI_PROVIDER=openai` with the matching `GEMINI_API_KEY`/`OPENAI_API_KEY` to use a real model instead; no code changes are required to switch providers.

Notifications (Milestone 9) work out of the box the same way: a Celery Beat task scans due reminders every 60 seconds and delivers them in-app, by email (via `EMAIL_BACKEND`, console by default), and by push to any registered device — `PUSH_PROVIDER` defaults to an offline `console` adapter that logs the push instead of calling a real vendor, so the notification pipeline is fully testable without FCM/APNs/Web Push credentials. Point `PUSH_PROVIDER` at a real adapter once vendor credentials are available; no other code changes are required. The notification bell in the app header and the full notification center at `/notifications` reflect deliveries as they happen.

Family & Shared Workspace (Milestone 10) turns MindMesh from a single-user tool into a household one at `/family`: create or join a family (invite by email, with owner/adult/child roles and a 7-day expiring invitation link), share individual tasks/calendar events/notes with the family, and keep a shared list of emergency contacts. Sharing a task can grant edit access, letting another family member complete it on the owner's behalf — the "delegate tasks to my children" flow from PRD.md's parent persona. Shared calendar events and notes are view-only for non-owners in this milestone. Every family action is enforced at the service layer (not just the API), so a stranger to the family can never read or modify its data — verified by dedicated data-isolation tests.

Analytics & Insights (Milestone 11) turns the data already captured by Tasks, Notes, and Calendar into personal insight at `/analytics`: a productivity summary (task completion rate, totals, and a daily bar chart) over a configurable window, a daily task-completion streak with a calendar-heatmap visualization for habit tracking, AI-generated recommendations routed through the same AI abstraction layer as the AI Companion (falling back to an empty, non-error state if the provider is unavailable, since recommendations are advisory), and weekly progress reports generated automatically by a Celery Beat task and listed with their own AI-written summary. All of it is computed from the existing Task/Note/Event data through each domain's own service layer — no new raw data is collected, and nothing here duplicates a model that Milestones 4–6 already own.

## Production Deployment

Milestone 12 hardened MindMesh for production and added the configuration
needed to deploy it — see `CHANGELOG.md` for the full list of changes and
`docs/adr/0001-token-storage-strategy.md` for the security rationale behind
the auth cookie migration.

### Security changes to be aware of

The refresh token is now delivered as an **httpOnly cookie**, not in the
JSON response body — a plain `fetch`/`curl` against `/auth/login/` will no
longer see a `refresh` field. Any API client (including a custom frontend)
must send requests with credentials included (`withCredentials: true` in
Axios, `credentials: 'include'` in `fetch`) and must echo the `mm_csrf`
cookie's value back as an `X-CSRF-Token` header on `/auth/token/refresh/`
and `/auth/logout/` calls. See `backend/apps/accounts/cookies.py` for the
full mechanism and `frontend/src/api/client.ts` / `frontend/src/api/cookies.ts`
for the reference implementation.

### Verifying the production build locally

Before deploying anywhere, the full production topology can be built and
smoke-tested on a laptop:

```bash
cp backend/.env.example backend/.env.production   # fill in real values — see below
cd infra
docker compose -f docker-compose.prod.yml --env-file ../backend/.env.production up --build

# Frontend (via Nginx):  http://localhost:8081/
# Backend (via Nginx):   http://localhost:8080/api/v1/health/ready/
# Backend (direct):      http://localhost:8000/api/v1/health/ready/
```

This runs gunicorn (not `runserver`), the Nginx-served static frontend
build (not the Vite dev server), and non-root containers — the same
topology as production, without needing a Railway/Vercel account.

Required production environment variables (`backend/.env.production` or
the platform's own env var settings) — `config/settings/production.py`
refuses to start without these:

- `DJANGO_SECRET_KEY` — a strong, unique value (`python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `DJANGO_ALLOWED_HOSTS` — e.g. `api.mindmesh.app`
- `CSRF_TRUSTED_ORIGINS` — e.g. `https://api.mindmesh.app`
- `CORS_ALLOWED_ORIGINS` — e.g. `https://mindmesh.app` (the Vercel frontend's real domain)
- `DATABASE_URL`, `REDIS_URL` — the production PostgreSQL/Redis connection strings

See `backend/.env.example` for the full list, including the Milestone 12
auth-cookie and logging settings.

### Deploying the backend to Railway

`backend/railway.json` configures the build (from
`infra/docker/Dockerfile.backend`'s `production` target) and deploy steps
(runs migrations via `releaseCommand`, then starts gunicorn bound to
Railway's `$PORT`, with `/api/v1/health/ready/` as the healthcheck path).
Point a new Railway service at the `backend/` directory of this repo, add
a PostgreSQL and Redis plugin, set the environment variables listed above
plus the AI/Google OAuth/email credentials from `.env.example`, and
deploy. Add a second Railway service running
`celery -A celery_app worker --loglevel=info` and a third running
`celery -A celery_app beat --loglevel=info` (same image, different start
command) for background jobs.

### Deploying the frontend to Vercel

`frontend/vercel.json` configures the Vite build, SPA rewrite (all paths
resolve to `index.html` for React Router), and security headers. Point a
new Vercel project at the `frontend/` directory, set `VITE_API_BASE_URL`
to the deployed Railway backend's `/api/v1` URL and
`VITE_GOOGLE_OAUTH_CLIENT_ID` if using Google sign-in, and deploy.

### Monitoring, logging, and backups

- `GET /api/v1/health/` — liveness (process is up).
- `GET /api/v1/health/ready/` — readiness (PostgreSQL + Redis reachable);
  point Railway's healthcheck and any uptime monitor at this path.
- Logs are written as structured, single-line JSON to stdout — Railway and
  Docker capture this directly, no extra configuration needed. Set
  `DJANGO_LOG_LEVEL=DEBUG` temporarily for deeper tracing.
- `backend/scripts/backup_postgres.sh` / `restore_postgres.sh` — run
  `DATABASE_URL=... ./scripts/backup_postgres.sh` on a schedule (or rely
  on Railway's managed PostgreSQL automated snapshots) and periodically
  rehearse a restore with `restore_postgres.sh` against a scratch
  database — a backup that's never been restored isn't a verified backup.

## Documentation

| Document | Description |
|---|---|
| [`PRD.md`](./PRD.md) | Product vision, mission, problem statement, personas, requirements, and success metrics |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Frontend/backend architecture, database design, AI module, security, and scalability strategy |
| [`ROADMAP.md`](./ROADMAP.md) | Milestone-by-milestone delivery plan through Version 1.0 and beyond |
| `PROJECT_RULES.md` | Source of truth for conflicts between planning documents (referenced by the roadmap) |
| [`CHANGELOG.md`](./CHANGELOG.md) | Version history and release notes |
| [`docs/adr/`](./docs/adr/) | Architecture decision records (e.g. the auth cookie migration) |

## Future Vision

Beyond Version 1.0, MindMesh's roadmap looks toward:

- **Version 1.1** — Offline support, multi-language support, expanded AI automation (proactive task/event creation from conversation)
- **Version 1.2** — Retrieval-Augmented Generation (RAG) for notes and knowledge base, wearable integration, enhanced predictive insights
- **Version 2.0** — Voice assistant capabilities, smart home integration, a desktop application, and full agentic AI automation across tasks, calendar, and notifications

The long-term goal is to unify daily life management into one coherent, trusted experience — proving that a single product can serve a 9-year-old and a 68-year-old equally well, while building a durable memory moat without ever compromising user ownership of their own data.

## Contributing

MindMesh is currently in its planning and pre-development phase. Contribution guidelines, coding standards, and PR processes will be published alongside Milestone 1 (Project Foundation), once the initial project skeleton is established.

## License

License to be determined and added prior to public release.
