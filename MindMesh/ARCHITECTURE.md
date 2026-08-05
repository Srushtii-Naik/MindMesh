# MindMesh — Software Architecture Document

**Version:** 1.0
**Status:** Living document — update as the system evolves

---

## 1. Overall System Architecture

MindMesh follows a **modular, layered client-server architecture** with a decoupled frontend and backend, communicating over a versioned REST API. The system is designed around Clean Architecture principles: business logic is isolated from frameworks, infrastructure, and delivery mechanisms so that individual pieces (AI provider, database, task queue) can evolve independently.

**High-level components:**

- **Client (React SPA)** — renders the UI, manages local/UI state, and talks to the backend exclusively through the API layer.
- **API Gateway / Nginx** — reverse proxy that terminates TLS, routes traffic to the backend, and serves as a boundary for rate limiting and static asset delivery.
- **Backend (Django + DRF)** — exposes REST endpoints, enforces business rules, orchestrates domain services (tasks, notes, reminders, AI, notifications).
- **PostgreSQL** — system of record for all persistent user and domain data.
- **Redis** — message broker for Celery, cache layer, and short-lived state (e.g., OTPs, rate-limit counters).
- **Celery Workers** — execute asynchronous and scheduled work (reminders, AI summarization, notifications, embedding generation).
- **AI Provider Abstraction Layer** — a backend-internal module that mediates all calls to external LLM providers (Gemini, OpenAI), decoupling domain logic from any single vendor.

**Data flow (typical request):**
Client → Nginx → Django/DRF → Domain Service → PostgreSQL/Redis/AI Layer → Response back through the same path. Long-running or scheduled work is handed off to Celery instead of blocking the request-response cycle.

**Guiding principles:**
- Stateless backend processes (horizontally scalable).
- Single source of truth in PostgreSQL; Redis is never authoritative.
- All AI provider calls pass through an abstraction layer — no direct SDK calls from domain code.
- Frontend never talks to the database, Redis, or AI providers directly.

---

## 2. Frontend Architecture

The frontend is a **React + TypeScript SPA** built with Vite, structured for clarity, mobile-first responsiveness, and long-term maintainability.

**Core responsibilities:**
- Presentation and interaction layer only — no business logic duplication from the backend.
- Manages two distinct categories of state:
  - **Server state** (tasks, notes, reminders, chat history) via **TanStack Query** — handles caching, background refetching, and optimistic updates.
  - **UI/local/session state** (theme, active view, modals, ephemeral form state) via **Zustand**.
- All network communication is centralized through an **Axios client instance** with interceptors for auth token attachment, refresh handling, and error normalization.
- **React Hook Form** manages form state and validation, keeping form logic out of components.
- **React Router** handles client-side routing, with route-level code splitting for performance.
- **Framer Motion** provides consistent, calm micro-interactions and transitions in line with the design philosophy.
- **Tailwind CSS** provides the design system's utility layer, supporting a consistent, accessible, minimal visual language across devices.

**Architectural conventions:**
- Feature-based organization (not type-based) so each domain (tasks, notes, AI chat, reminders) is self-contained.
- A shared `api/` layer defines typed request/response contracts per domain, consumed by TanStack Query hooks.
- Accessibility (WCAG-aligned) and mobile-first layout are treated as first-class constraints, not afterthoughts, given the target audience spans children to senior citizens.
- No direct fetch calls inside components — all data access goes through hooks backed by the Axios client.

---

## 3. Backend Architecture

The backend is built with **Django** and **Django REST Framework**, organized around **Clean Architecture / layered service design** rather than "fat" views or models.

**Layers:**
1. **API Layer (DRF views/serializers)** — handles HTTP concerns: request parsing, validation, serialization, status codes. Contains no business logic.
2. **Service Layer** — domain-specific business logic (task scheduling rules, memory update policies, AI orchestration). Views call services; services never import DRF.
3. **Repository/Data Access Layer** — encapsulates ORM queries per domain, isolating persistence details from services.
4. **Domain Models** — Django models represent persistence structure but core business rules live in the service layer, not in model methods, to keep logic testable and framework-agnostic.
5. **Integration Layer** — external system access (AI provider abstraction, Google OAuth, email/notification providers).

**Modularity:**
- The backend is organized into Django apps per domain (e.g., `tasks`, `notes`, `reminders`, `ai_companion`, `notifications`, `accounts`), each owning its models, serializers, services, and Celery tasks.
- Cross-domain communication happens through service interfaces, not direct model imports across apps, to prevent tight coupling.
- Shared concerns (auth, permissions, pagination, exception handling) live in a `core`/`common` app.

**API versioning:** all endpoints are namespaced under `/api/v1/` to allow non-breaking evolution.

---

## 4. Database Overview (High Level)

**PostgreSQL** is the system of record. Schema design follows normalized relational modeling with clear domain boundaries.

**Core entity groups:**
- **User & Identity** — user accounts, auth providers (email/password, Google OAuth), profile/preferences.
- **Tasks & Reminders** — tasks, subtasks, recurring rules, reminder schedules, completion state.
- **Notes** — note content, tags/folders, timestamps, links to AI-generated summaries.
- **Calendar/Events** — events, time ranges, associations to tasks/reminders.
- **AI & Memory** — conversation sessions, messages, long-term memory records (key facts/preferences extracted about the user), and (future) embedding references for RAG.
- **Notifications** — notification records, delivery status, channel (push/email/in-app).

**Design principles:**
- Every domain table is scoped to a `user_id` with row-level ownership enforced at the service layer.
- Soft-delete (`is_active`/`deleted_at`) preferred over hard deletes for user-generated content, to support recovery and auditability.
- Timestamps (`created_at`, `updated_at`) standardized across all tables.
- Embeddings/vector data (for future RAG) are planned to live either in a dedicated table with a vector-compatible extension (e.g., pgvector) or in an external vector store, kept behind the same repository abstraction so the choice can change without touching domain logic.
- Migrations are managed exclusively through Django's migration framework — no manual schema changes.

---

## 5. Authentication Flow

MindMesh supports **email/password login** and **Google OAuth**, both issuing the same internal **JWT-based session**.

**Email/Password flow:**
1. User registers or logs in via `/api/v1/auth/`.
2. Backend validates credentials (hashed passwords via Django's auth framework).
3. On success, backend issues a short-lived **access token** and a longer-lived **refresh token** (JWT).
4. Access token is sent with every subsequent request via the `Authorization` header; the Axios interceptor attaches it automatically.
5. When the access token expires, the frontend silently calls a refresh endpoint using the refresh token to obtain a new access token, avoiding forced re-login.

**Google OAuth flow:**
1. Frontend initiates Google's OAuth consent flow.
2. Google returns an authorization code/ID token to the frontend.
3. Frontend sends this token to a dedicated backend endpoint.
4. Backend verifies the token with Google, creates or matches the local user account, and issues the same internal JWT pair as the email/password flow.

**Session management:**
- Refresh tokens are stored securely (httpOnly cookie preferred over localStorage where feasible) to reduce XSS exposure.
- Token revocation/blacklisting is supported via a Redis-backed denylist for logout and security events.
- All authenticated endpoints enforce permission checks at the service layer, not just the view layer, to prevent accidental data leakage across users.

---

## 6. API Communication

- **Protocol:** REST over HTTPS, JSON payloads, versioned under `/api/v1/`.
- **Contract consistency:** DRF serializers define a single, consistent shape for requests/responses per resource; the frontend maintains matching TypeScript types.
- **Client-side:** All calls go through a centralized Axios instance with:
  - Base URL and timeout configuration.
  - Request interceptor for attaching the access token.
  - Response interceptor for handling 401s (trigger token refresh) and normalizing error shapes for TanStack Query.
- **Server-side:** Standardized response envelope for success and error cases (consistent error codes/messages) so the frontend can handle failures generically.
- **Pagination, filtering, sorting:** consistent query-parameter conventions applied across all list endpoints.
- **Rate limiting:** enforced at the Nginx layer and/or DRF throttling classes, especially on auth and AI-chat endpoints.
- **Real-time/async needs** (e.g., AI response streaming, live notifications) are handled either via polling through TanStack Query initially, with a clear upgrade path to WebSockets/Server-Sent Events as a future enhancement — not required for the initial architecture.

---

## 7. AI Module Architecture

The AI module is designed as a **companion engine**, not a stateless chatbot, and is built around an **AI Provider Abstraction Layer** so the underlying model vendor is an implementation detail.

**Structure:**
- **Abstraction Interface** — defines a provider-agnostic contract (e.g., `generate_response`, `summarize`, `extract_memory`) that all domain code depends on.
- **Provider Adapters** — concrete implementations for Gemini and OpenAI (and future providers) that translate the abstract interface into vendor-specific API calls. Swapping or adding a provider requires only a new adapter, not changes to domain logic.
- **Context Assembly Service** — before each AI call, gathers relevant context: recent conversation history, relevant long-term memory entries, and (in the future) retrieved documents/notes via RAG.
- **Memory Manager** — responsible for extracting, storing, and retrieving durable facts about the user (preferences, recurring commitments, important dates) so the companion has continuity across sessions. Initially implemented as structured records in PostgreSQL; designed to extend toward embedding-based retrieval.
- **Summarization & Suggestion Services** — dedicated service functions for note summarization, task suggestions, and proactive recommendations, all routed through the same abstraction layer.

**Future extensibility (explicitly designed for, not yet required):**
- **RAG pipeline** — document/note chunking, embedding generation, vector similarity search feeding into context assembly.
- **Multiple simultaneous providers** — e.g., a cheaper/faster model for lightweight tasks and a stronger model for complex reasoning, selected per use case by the abstraction layer.
- **Streaming responses** for a more conversational chat experience.

**Isolation principle:** no other part of the backend ever imports an AI SDK directly — all AI access goes through the abstraction layer, ensuring vendor changes or outages are contained.

---

## 8. Background Jobs (Redis + Celery)

Asynchronous and scheduled work is offloaded from the request-response cycle using **Celery** with **Redis** as the broker (and optionally result backend).

**Categories of background work:**
- **Reminders & scheduled notifications** — periodic tasks (via Celery Beat) that scan due reminders/events and dispatch notifications.
- **AI processing** — note summarization, memory extraction, and proactive recommendation generation, which may involve slower external API calls unsuitable for a synchronous request.
- **Notification delivery** — dispatching push/email notifications through third-party services, decoupled from the triggering request.
- **Housekeeping** — token cleanup, soft-deleted record purging, analytics aggregation.

**Design principles:**
- Views/services enqueue tasks and return immediately; workers process independently.
- Tasks are idempotent where possible, to safely tolerate retries.
- Retry policies with exponential backoff are defined for tasks calling external services (AI providers, email/push gateways).
- Redis is also used as a **cache layer** (e.g., caching AI provider responses for repeated queries, session/rate-limit counters) separate from its broker role — logically separated by key namespace/database index.
- Worker concurrency and queue separation (e.g., a distinct queue for AI tasks vs. notification tasks) allow independent scaling based on load characteristics.

---

## 9. Folder Structure

High-level structure only — reflects module boundaries, not file-by-file detail.

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

Each backend app follows the internal convention: `models.py`, `serializers.py`, `services.py`, `repositories.py`, `tasks.py`, `urls.py`, `views.py` — keeping the layering from Section 3 consistent across domains.

---

## 10. Security Strategy

- **Authentication & sessions:** JWT access/refresh tokens, short-lived access tokens, Redis-backed token denylist for revocation, secure cookie storage where possible.
- **Password security:** Django's built-in hashing (PBKDF2/Argon2), enforced password strength rules on registration.
- **Authorization:** row-level ownership checks enforced in the service layer for every domain object — a user can only ever access their own tasks, notes, memory, etc.
- **Transport security:** HTTPS enforced end-to-end; Nginx terminates TLS and redirects HTTP → HTTPS.
- **Input validation:** all inbound data validated via DRF serializers; no raw SQL — ORM usage only, preventing injection risks.
- **Secrets management:** environment-variable based configuration; no secrets committed to source control; separate secrets per environment (dev/staging/prod).
- **AI-specific security:** user data sent to AI providers is scoped and minimized (only necessary context, not full raw database access); provider adapters are the sole egress point for user data to third-party AI APIs, making data flow auditable.
- **Rate limiting & abuse prevention:** DRF throttling and/or Nginx-level limits on auth and AI-chat endpoints to prevent brute force and API cost abuse.
- **CORS:** strict allow-list limited to known frontend origins (Vercel domain, local dev).
- **Dependency & container hygiene:** regular dependency updates, minimal base Docker images, no root container processes in production.
- **Auditability:** key security-sensitive actions (login, password change, OAuth linking, data export/delete) are logged for traceability.

---

## 11. Scalability Strategy

- **Stateless backend:** Django/DRF processes hold no session state in-process, allowing horizontal scaling behind Nginx/a load balancer.
- **Database scaling path:** start with a single managed PostgreSQL instance; scale vertically first, then introduce read replicas for read-heavy endpoints (e.g., note/task listing) as load grows.
- **Caching:** Redis used to cache expensive or repeated reads (e.g., AI responses for identical prompts, frequently accessed reference data) to reduce database and AI provider load.
- **Asynchronous offloading:** any slow or bursty workload (AI calls, notifications, summarization) runs through Celery rather than blocking web workers, keeping API latency predictable under load.
- **Independent worker scaling:** Celery workers scale independently from web processes, and can be split into dedicated queues (e.g., `ai_queue`, `notifications_queue`) so a spike in one workload doesn't starve another.
- **AI cost/performance scaling:** the provider abstraction layer allows routing different task types to different models (cheaper/faster vs. higher-quality) and swapping providers without code changes elsewhere, supporting cost control as usage grows.
- **Frontend scaling:** static SPA deployment on Vercel's edge/CDN network inherently scales with traffic; no server-side rendering bottleneck.
- **Containerized deployment:** Docker/Docker Compose in development mirrors production topology; production deployment (Render or any Docker-compatible platform) allows straightforward horizontal scaling of backend and worker containers independently.
- **Future growth path:** the modular app boundaries (Section 3) and clean layering are designed so that any domain (e.g., `ai_companion`) could later be extracted into its own service if it outgrows the monolith, without a full rewrite.

---

*This document reflects the target architecture guiding MindMesh's development and should be revised as implementation decisions are finalized or evolve.*