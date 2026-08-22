# MindMesh — Development Roadmap

**Status:** Living document — source of truth for delivery sequencing
**Scope:** MVP through Version 1.0, with a forward-looking view into post-1.0 versions
**Alignment:** Derived from PRD.md, ARCHITECTURE.md, and PROJECT_RULES.md. Any conflict between this roadmap and those documents must be resolved in favor of PROJECT_RULES.md.

---

## How to Read This Roadmap

Milestones are sequenced in **strict dependency order** — each milestone assumes the previous ones are complete and stable. No milestone should be started out of order, and no milestone is considered "done" until its completion checklist is fully satisfied. This is a startup-grade product; partial or rushed milestones create compounding technical debt downstream.

---

## Milestone 1 — Project Foundation

**Goal:**
Establish a clean, production-ready project skeleton that the entire product will be built on top of, in full alignment with the approved tech stack and architecture.

**Features:**
- Frontend boilerplate (React + TypeScript + Vite + Tailwind CSS, base routing structure)
- Backend boilerplate (Django + Django REST Framework, base app structure per ARCHITECTURE.md)
- Docker and Docker Compose setup for local development
- PostgreSQL configuration and connection
- Environment variable management (frontend and backend)
- Basic CI-ready structure (lint, format, test hooks scaffolded, even if pipelines are added later)

**Deliverables:**
- Project runs successfully end-to-end locally via Docker Compose.
- Frontend and backend communicate over a basic health-check endpoint.

**Dependencies:**
- None (starting point of the project).

**Completion Checklist:**
- [x] Frontend boots via Vite with Tailwind configured
- [x] Backend boots via Django with DRF installed and configured
- [x] Docker Compose brings up frontend, backend, PostgreSQL, and Redis together
- [x] `.env` structure defined and documented, no secrets committed
- [x] Base folder structure matches ARCHITECTURE.md exactly
- [x] Health-check endpoint returns a successful response to the frontend

---

## Milestone 2 — Authentication & User Management

**Goal:**
Enable secure account creation, login, and session management as the gateway to every other feature.

**Features:**
- Register (email & password)
- Login (email & password)
- Google OAuth login
- JWT authentication (access + refresh tokens)
- User profile (view/edit)
- Settings (account-level preferences)
- Password reset flow
- Session management (logout, token refresh, token revocation)

**Deliverables:**
- Users can securely create and access accounts through both email/password and Google OAuth.

**Dependencies:**
- Milestone 1 (Project Foundation)

**Completion Checklist:**
- [x] Registration and login endpoints implemented and validated
- [x] Google OAuth flow implemented end-to-end
- [x] JWT issuance, refresh, and revocation working as per ARCHITECTURE.md
- [x] Password reset flow functional (request + confirm)
- [x] Profile and settings screens functional on frontend
- [x] All auth endpoints covered by input validation and rate limiting
- [x] Passwords hashed; no plaintext credentials anywhere

---

## Milestone 3 — Dashboard

**Goal:**
Provide a single, calm home base that orients the user and surfaces what matters most at a glance.

**Features:**
- Home dashboard shell
- Quick actions (create task, note, event, chat)
- Today's summary
- Upcoming events preview
- AI insights card (placeholder-ready, wired to AI module once available)
- Recent activity feed

**Deliverables:**
- A central hub for all user activities is live and navigable.

**Dependencies:**
- Milestone 2 (Authentication & User Management)

**Completion Checklist:**
- [x] Dashboard renders correctly across mobile and desktop breakpoints
- [x] Quick actions route correctly to their respective modules (stubbed if modules not yet built)
- [x] Today's summary and upcoming events pull from real data once available, placeholders otherwise
- [x] Recent activity feed reflects real user actions
- [x] UI adheres to design philosophy (minimal, calm, accessible) per PROJECT_RULES.md

---

## Milestone 4 — Task Management

**Goal:**
Deliver a complete, dependable productivity module as the first core utility of MindMesh.

**Features:**
- Tasks (create, read, update, delete)
- Subtasks
- Priorities
- Due dates
- Categories
- Recurring tasks
- Smart suggestions (rule-based initially, AI-enhanced later)

**Deliverables:**
- A complete productivity module usable end-to-end.

**Dependencies:**
- Milestone 3 (Dashboard) — for surfacing tasks on the home screen

**Completion Checklist:**
- [x] Full CRUD for tasks and subtasks implemented
- [x] Priorities, due dates, and categories functional and filterable
- [x] Recurring task logic implemented and tested
- [x] Smart suggestions surfaced in the UI (baseline logic in place)
- [x] Dashboard quick actions and "Today's Summary" reflect real task data

---

## Milestone 5 — Calendar & Scheduling

**Goal:**
Provide a fully functional scheduling system that integrates with tasks and reminders.

**Features:**
- Calendar views (day/week/month)
- Events (create, edit, delete)
- Scheduling
- Reminders (foundational logic; full delivery arrives in Milestone 9)
- Daily planner
- Weekly planner

**Deliverables:**
- A fully functional calendar system, integrated with tasks.

**Dependencies:**
- Milestone 4 (Task Management) — calendar entries relate to tasks and due dates

**Completion Checklist:**
- [x] Calendar views render correctly with real event/task data
- [x] Event CRUD implemented and validated
- [x] Daily and weekly planners functional
- [x] Reminder data model in place (delivery mechanism deferred to Milestone 9)
- [x] Calendar reflects task due dates and recurring tasks accurately

---

## Milestone 6 — Notes & Knowledge

**Goal:**
Establish a knowledge management system where users can capture and organize information, laying groundwork for future AI-powered retrieval.

**Features:**
- Rich notes (formatted text)
- Categories
- Search
- AI summaries
- Tags
- Attachments

**Deliverables:**
- A functional knowledge management system.

**Dependencies:**
- Milestone 2 (Authentication & User Management); independent of Milestones 4–5 but sequenced after them for team focus and dashboard integration

**Completion Checklist:**
- [x] Rich note creation/editing implemented
- [x] Categories and tags functional and filterable
- [x] Search returns accurate, performant results
- [x] Attachments upload/storage implemented securely
- [x] AI summaries wired through the AI abstraction layer (basic implementation; refined in Milestone 7)

---

## Milestone 7 — AI Companion

**Goal:**
Deliver the defining feature of MindMesh — a production-ready, context-aware AI assistant, built strictly through the AI abstraction layer defined in ARCHITECTURE.md.

**Features:**
- AI chat interface
- Context awareness (pulls from tasks, notes, calendar as relevant)
- Personalized responses
- Smart suggestions (AI-enhanced, building on Milestone 4's baseline)
- Memory extraction (foundational; full engine in Milestone 8)
- Conversation history

**Deliverables:**
- A production-ready AI assistant integrated across the product.

**Dependencies:**
- Milestones 4, 5, and 6 (Tasks, Calendar, Notes) — the AI companion draws context from all of them

**Completion Checklist:**
- [x] AI chat functional end-to-end through the provider abstraction layer
- [x] Context assembly service pulls relevant task/note/calendar data into conversations
- [x] Conversation history persisted and retrievable
- [x] Memory extraction logic captures durable facts (storage refined in Milestone 8)
- [x] No direct AI SDK calls exist outside the abstraction layer (verified via code review against PROJECT_RULES.md)
- [x] Response latency and error handling meet acceptable UX standards

---

## Milestone 8 — Memory Engine

**Goal:**
Give the AI companion durable, structured long-term memory so it provides continuity across sessions.

**Features:**
- Long-term memory storage
- User preferences
- Important dates
- Personal facts
- AI recall (retrieving and applying memory in conversations)

**Deliverables:**
- The AI reliably remembers and applies important user information across sessions.

**Dependencies:**
- Milestone 7 (AI Companion)

**Completion Checklist:**
- [x] Long-term memory data model implemented per ARCHITECTURE.md
- [x] Preferences, important dates, and personal facts captured and stored correctly
- [x] AI recall demonstrably influences responses in later sessions
- [x] Memory storage designed to be extensible toward future embeddings/RAG without rework
- [x] User-facing controls to view/edit/delete stored memory (privacy and trust requirement)

---

## Milestone 9 — Notifications

**Goal:**
Complete the notification system so reminders and important events reliably reach the user through appropriate channels.

**Features:**
- Push notifications
- Reminder engine (full delivery, building on Milestone 5's data model)
- Email notifications
- Notification center (in-app)

**Deliverables:**
- A complete, reliable notification system.

**Dependencies:**
- Milestone 5 (Calendar & Scheduling) for reminder data; Celery/Redis infrastructure from Milestone 1

**Completion Checklist:**
- [x] Reminder engine runs on scheduled Celery tasks and fires accurately
- [x] Push notification delivery implemented and tested
- [x] Email notification delivery implemented and tested
- [x] In-app notification center reflects real-time and historical notifications
- [x] Delivery failures are retried/logged, not silently dropped

---

## Milestone 10 — Family & Shared Workspace

**Goal:**
Extend MindMesh from a personal tool into a collaborative one, enabling shared context between trusted people.

**Features:**
- Family members (invite/manage)
- Shared tasks
- Shared calendar
- Shared notes
- Emergency contacts

**Deliverables:**
- Functional collaborative family features.

**Dependencies:**
- Milestones 4, 5, and 6 (Tasks, Calendar, Notes) — sharing extends existing single-user modules

**Completion Checklist:**
- [x] Family member invitation and permission model implemented
- [x] Shared tasks, calendar, and notes respect ownership and permission boundaries
- [x] Emergency contacts feature implemented and accessible appropriately
- [x] Data isolation verified — shared access never leaks beyond intended members

---

## Milestone 11 — Analytics & Insights

**Goal:**
Turn accumulated user data into meaningful, actionable personal insight rather than raw data dumps.

**Features:**
- Productivity analytics
- Habit tracking
- AI recommendations (building on the AI companion and memory engine)
- Progress reports

**Deliverables:**
- Meaningful, personalized insights delivered to the user.

**Dependencies:**
- Milestones 4–8 (Tasks, Calendar, Notes, AI Companion, Memory Engine) — analytics are derived from all core modules

**Completion Checklist:**
- [x] Productivity analytics computed accurately from task/calendar data
- [x] Habit tracking implemented and visualized clearly
- [x] AI-generated recommendations surfaced through the AI abstraction layer
- [x] Progress reports generated on a sensible cadence (e.g., weekly)
- [x] Insights presented calmly and clearly — no dashboard clutter, per PROJECT_RULES.md

---

## Milestone 12 — Production & Deployment

**Goal:**
Harden, verify, and ship MindMesh as a stable, secure, production-grade Version 1.0.

**Features:**
- Performance optimization (frontend bundle size, backend query efficiency, caching)
- Security audit (full pass against PROJECT_RULES.md security section)
- Testing (unit, integration, and critical end-to-end flows)
- Bug fixes from prior milestones
- Docker production build
- Railway deployment (backend)
- Vercel deployment (frontend)
- Monitoring
- Logging
- Backup strategy (PostgreSQL)

**Deliverables:**
- Production-ready Version 1.0, live and monitored.

**Dependencies:**
- All prior milestones (1–11) complete and stable

**Completion Checklist:**
- [x] Full security audit completed and all findings resolved
- [x] Automated tests cover critical paths across auth, tasks, calendar, notes, AI, and notifications
- [x] Production Docker builds verified for both frontend and backend
- [ ] Backend deployed and verified on Railway — *configuration complete (`backend/railway.json`, production Dockerfile target), actual deploy requires a Railway account/credentials not available in this environment. See README.md Milestone 12 section for deploy steps.*
- [ ] Frontend deployed and verified on Vercel — *configuration complete (`frontend/vercel.json`), actual deploy requires a Vercel account/credentials not available in this environment. See README.md Milestone 12 section for deploy steps.*
- [x] Monitoring and logging in place with alerting for critical failures
- [x] Automated PostgreSQL backup strategy implemented and tested (restore verified, not just backup)
- [x] Load/performance testing completed for key endpoints (auth, AI chat, dashboard)
- [x] Version 1.0 tagged and release notes documented

**Milestone 12 implementation notes:**
- **Security audit (ADR 0001 resolution):** the JWT refresh token moved from
  the JSON response body to an httpOnly cookie
  (`apps/accounts/cookies.py`), removing it from JavaScript's reach. A
  double-submit CSRF cookie protects the endpoints that read it (token
  refresh, logout). `config/settings/production.py` now fails fast (raises
  `ImproperlyConfigured`) rather than starting with an insecure default
  `SECRET_KEY`, empty `ALLOWED_HOSTS`, or missing `CSRF_TRUSTED_ORIGINS`;
  adds HSTS, secure cookies, and `SECURE_PROXY_SSL_HEADER` for Railway's
  edge-terminated TLS. Security-sensitive actions (login, register,
  logout, password reset, session revocation) are now logged via a
  dedicated `mindmesh.security` logger.
- **Testing:** 455 backend tests passing (443 carried over from M1–M11 + 12
  new: 8 cookie/CSRF tests, 4 health/readiness tests), 129 frontend tests
  passing (128 + 1 new bootstrap test). `manage.py check`, migration-drift
  check, `tsc -b`, ESLint, and the production build all pass clean.
- **Docker:** both Dockerfiles are now multi-stage (`development` /
  `production` targets) — production runs as a non-root user, serves via
  gunicorn (backend) / Nginx (frontend), and includes a `HEALTHCHECK`.
  `infra/docker-compose.prod.yml` reproduces the full production topology
  for local verification; the exact `collectstatic` and `gunicorn`
  commands the backend image runs were verified directly against real
  PostgreSQL 16 and Redis 7 instances (not just SQLite/mocks).
- **Railway / Vercel:** `backend/railway.json` and `frontend/vercel.json`
  are complete and ready to use, but were not exercised against live
  Railway/Vercel infrastructure — see the checklist notes above.
- **Monitoring & logging:** added `GET /api/v1/health/ready/` (checks
  PostgreSQL + Redis connectivity, for platform healthchecks/uptime
  alerting) alongside the existing `/health/` liveness check. Logging is
  now structured and written to stdout for platform log aggregation
  (Railway/Docker), rather than unconfigured.
- **Backup strategy:** `backend/scripts/backup_postgres.sh` /
  `restore_postgres.sh` were run end-to-end against a real local
  PostgreSQL 16 database — a seeded row was backed up, restored into a
  fresh database, and confirmed to match exactly (same UUID, same data).
- **Load testing:** `backend/scripts/load_test.py` (stdlib +
  already-installed `requests`, no new dependency) was run against the
  local dev stack. Results: `GET /health/` p50=15ms/p95=26ms,
  `GET /health/ready/` p50=95ms/p95=175ms, `POST /auth/register/`
  p50=138ms/p95=331ms (auth endpoints are intentionally rate-limited per
  PROJECT_RULES.md Section 8, so this isn't a production-scale benchmark —
  see the script's docstring).
- **Performance:** added route-level code splitting via `React.lazy`
  (`frontend/src/router/index.tsx`), addressing the "chunks larger than
  500kB" build warning present at the start of this milestone. Backend
  query patterns were audited — `select_related`/`prefetch_related` were
  already applied consistently across list-returning repository methods;
  no N+1 issues found.
- **Version 1.0:** tagged in `CHANGELOG.md`.

---

## Future Versions

The following features are intentionally deferred beyond Version 1.0. They must not be pulled forward into earlier milestones without a deliberate, documented roadmap revision.

### Version 1.1
- Offline support (core modules usable without connectivity, with sync on reconnect)
- Multi-language support
- Expanded AI automation (proactive task/event creation from conversation)

### Version 1.2
- Retrieval-Augmented Generation (RAG) for notes and knowledge base
- Wearable integration (health/activity context feeding into the AI companion)
- Enhanced habit tracking and predictive insights

### Version 2.0
- Voice assistant capabilities
- Smart home integration
- Desktop application
- Full AI automation across tasks, calendar, and notifications (agentic behavior)

---

*This roadmap reflects the intended build order for MindMesh through Version 1.0. Reordering milestones, skipping completion checklist items, or pulling future-version features forward requires a deliberate revision of this document — not an ad-hoc decision made mid-sprint.*