# MindMesh

**The AI companion that remembers your life, so you don't have to manage it across a dozen apps.**

> Status: In Development — Milestone 6 (Notes & Knowledge) Complete

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
| Deployment (planned) | Backend on Railway, Frontend on Vercel |

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
│   ├── docker/                 # Dockerfiles for frontend/backend
│   ├── nginx/                  # Nginx config
│   └── docker-compose.yml
│
└── docs/
    └── ARCHITECTURE.md
```

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
| 7 | AI Companion | Milestones 4, 5, 6 | Not started |
| 8 | Memory Engine | Milestone 7 | Not started |
| 9 | Notifications | Milestone 5, Milestone 1 infra | Not started |
| 10 | Family & Shared Workspace | Milestones 4, 5, 6 | Not started |
| 11 | Analytics & Insights | Milestones 4–8 | Not started |
| 12 | Production & Deployment | Milestones 1–11 | Not started |

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

Notes' AI summaries (Milestone 6) work out of the box with no configuration — `AI_PROVIDER` defaults to an offline `stub` provider. Set `AI_PROVIDER=gemini` or `AI_PROVIDER=openai` with the matching `GEMINI_API_KEY`/`OPENAI_API_KEY` to use a real model instead.

## Documentation

| Document | Description |
|---|---|
| [`PRD.md`](./PRD.md) | Product vision, mission, problem statement, personas, requirements, and success metrics |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Frontend/backend architecture, database design, AI module, security, and scalability strategy |
| [`ROADMAP.md`](./ROADMAP.md) | Milestone-by-milestone delivery plan through Version 1.0 and beyond |
| `PROJECT_RULES.md` | Source of truth for conflicts between planning documents (referenced by the roadmap) |

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
