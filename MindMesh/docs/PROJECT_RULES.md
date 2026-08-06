# MindMesh — Project Rules

**Status:** Permanent constitution — binding on every development session
**Authority:** This document governs how MindMesh is built. Where any other document (README.md, PRD.md, ARCHITECTURE.md, ROADMAP.md) appears to conflict with this one, PROJECT_RULES.md takes precedence, per ROADMAP.md's stated alignment.
**Audience:** Every contributor, every AI assistant, every future maintainer — present and future.

---

## Preamble

MindMesh is being built to become a trusted, long-lived product used by children, students, professionals, parents, and senior citizens alike. It is not a prototype, a hackathon entry, or a portfolio piece. Every decision made in this codebase — architectural, visual, or procedural — must be justifiable to that standard. This document exists so that standard survives every context switch, every new contributor, and every future session, without needing to be re-explained.

---

## 1. Project Philosophy

- **MindMesh is a production-grade startup, not an experiment.** It is being built with the expectation of real users, real data, and real consequences for getting things wrong.
- **Never treat it like a college project.** No shortcuts justified by "it's just for now." Temporary code has a way of becoming permanent; it must meet the same bar as everything else, or it must not be written.
- **Every feature must solve a real user problem.** Features are validated against the personas and problem statement in PRD.md (the Child, the Student, the Professional, the Parent, the Senior Citizen) before being built. If a feature cannot be traced back to a real pain point in PRD.md, it does not belong in the product.
- **Simplicity over feature overload.** MindMesh's core differentiator is coherence, not exhaustiveness. Every added feature is a tax on the product's simplicity and must earn its place. When in doubt, leave it out.
- **Long-term maintainability is mandatory.** Code is written for the maintainer six months from now, not for the fastest possible demo today. Velocity that creates technical debt is not velocity — it is borrowed time at interest.
- **Trust is the product.** Per PRD.md, MindMesh's central risk is trust — a companion that remembers "everything" is only viable if users believe in it deeply. Every technical and design decision is weighed against whether it strengthens or erodes that trust.

---

## 2. Tech Stack (Must Never Change)

The following stack is finalized per ARCHITECTURE.md and is considered locked. Introducing a new framework, library, or infrastructure provider requires a deliberate, documented revision to ARCHITECTURE.md and this document — never an ad-hoc substitution mid-feature.

**Frontend**
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Zustand
- Axios
- React Hook Form
- Framer Motion

**Backend**
- Python
- Django
- Django REST Framework

**Data & Infrastructure**
- PostgreSQL
- Redis
- Celery
- Docker
- Docker Compose
- Nginx

**Deployment**
- Railway (backend)
- Vercel (frontend)

**Authentication**
- JWT (access + refresh tokens)
- Google OAuth

**AI**
- Gemini and OpenAI, accessed exclusively through the AI Provider Abstraction Layer — never called directly

No substitutions, no "just this once" exceptions, no parallel tech stacks introduced by a single feature or a single contributor's preference.

---

## 3. Coding Standards

- **Clean Architecture.** Business logic is isolated from frameworks, infrastructure, and delivery mechanisms, per ARCHITECTURE.md Section 3. Views/controllers know about HTTP; services know about business rules; neither layer bleeds into the other.
- **SOLID Principles.** Every class and module has a single, well-defined responsibility. Dependencies are injected or abstracted, not hardcoded. Extension happens through new code, not modification of stable code.
- **DRY (Don't Repeat Yourself).** Duplicated logic is a defect waiting to diverge. Shared logic belongs in `common`/`shared` modules, not copy-pasted across features.
- **Reusable Components.** UI components and backend services are built to be composed and reused across features, not rebuilt per screen or per endpoint.
- **Modular Design.** Each domain (tasks, notes, reminders, AI, family, etc.) is self-contained and owns its own models, serializers, services, and UI. Cross-domain communication happens through defined interfaces, never through direct reach-ins.
- **Small Functions.** Functions and components do one thing. If a function needs a comment to explain what it does as a whole, it likely needs to be split.
- **TypeScript Only.** No plain JavaScript in the frontend codebase, ever. All types are explicit and meaningful — `any` is not an acceptable default.
- **Meaningful Naming.** Names describe intent, not implementation detail. No single-letter variables outside of trivial loop counters, no cryptic abbreviations, no misleading names.
- **Consistent Folder Structure.** Every domain, on both frontend and backend, follows the same internal shape (see Section 4). A contributor who understands one domain's structure should be able to navigate any other domain without relearning conventions.

---

## 4. Folder Rules

The folder structure defined in ARCHITECTURE.md Section 9 is authoritative. It must not drift, fragment, or grow inconsistent conventions over time.

**Frontend**
- Organization is **feature-based, not type-based.** Each domain (`tasks`, `notes`, `ai-chat`, `reminders`, `calendar`, etc.) lives under `src/features/` and is self-contained.
- `src/components/` holds only genuinely shared, cross-feature UI components — not feature-specific screens or widgets.
- `src/hooks/` holds only non-feature-specific shared hooks. Feature-specific hooks live inside that feature's folder.
- `src/api/` defines typed request/response contracts per domain, consumed by TanStack Query hooks. No component calls Axios or `fetch` directly.
- `src/stores/` holds Zustand stores for UI/local/session state only — never server state, which belongs to TanStack Query.
- `src/router/` owns all routing configuration, with route-level code splitting per feature.
- `src/styles/` holds Tailwind configuration and shared design tokens — the single source of truth for the visual system.
- `src/types/` holds only shared, cross-domain types. Domain-specific types live with their domain.

**Backend**
- Organization is by **Django app per domain** (`accounts`, `tasks`, `notes`, `reminders`, `calendar_events`, `ai_companion`, `notifications`), each owning its own models, serializers, services, repositories, tasks, urls, and views.
- Every domain app follows the same internal file convention: `models.py`, `serializers.py`, `services.py`, `repositories.py`, `tasks.py`, `urls.py`, `views.py`. No domain invents its own internal layout.
- `common/` holds only genuinely shared concerns: permissions, pagination, exception handling, and cross-cutting utilities. It never accumulates domain-specific logic.
- `celery_app/` owns Celery configuration and task registration only. Domain-specific task logic lives in that domain's `tasks.py`, not in `celery_app/`.
- `config/` owns Django project settings, URL root, and WSGI/ASGI — infrastructure concerns only, never business logic.
- **Cross-domain communication happens through service interfaces, never direct model imports across apps.** A `tasks` service must never reach directly into `notes` models.

**Docs**
- `docs/` is the canonical home for PRD.md, ARCHITECTURE.md, ROADMAP.md, and PROJECT_RULES.md. These are living documents and are kept current — see Section 13.

**Infra**
- `infra/` owns all deployment and orchestration concerns: Dockerfiles, Nginx configuration, and `docker-compose.yml`. Application code never contains infrastructure-specific logic that belongs here instead.

**Shared Components & Reusable Modules**
- A component, hook, or utility is only promoted to a shared location once it is genuinely used by two or more features. Premature abstraction into "shared" is avoided — duplication for a single use case is preferable to a wrong abstraction guessed too early.
- Shared code must remain domain-agnostic. The moment a "shared" utility needs to know about a specific feature's business rules, it no longer belongs in a shared location.

**Feature Isolation**
- A feature must be removable without breaking unrelated features. If deleting the `notes` feature folder breaks `tasks`, isolation has been violated and must be corrected before new work continues.

---

## 5. UI/UX Rules

MindMesh's interface must be usable, without exception, by a 9-year-old and a 68-year-old on the same day. The interface is always:

- **Minimal** — only what the user needs, when they need it. No clutter, no decorative complexity.
- **Elegant** — visual polish is a trust signal, not a vanity metric.
- **Professional** — the product looks and feels trustworthy at every screen, not just the marketing pages.
- **Accessible** — WCAG-aligned compliance is a requirement, not an aspiration, per PRD.md Section 8 and Section 12.
- **Responsive** — mobile-first, and correct across breakpoints, per ARCHITECTURE.md Section 2.
- **Calm** — the interface reduces cognitive load; it never competes for attention or manufactures urgency.
- **Premium** — every interaction should feel considered, not templated or default.

**Non-negotiables:**
- Interfaces must never be cluttered. If a screen needs a second pass to simplify, that pass happens before merge, not after.
- Animations (Framer Motion) must remain subtle — used to orient and reassure, never to impress or distract. No animation should slow a user down or call attention to itself.
- Accessibility is mandatory on every screen, every component, every release — not retrofitted at the end of a milestone.
- Interface complexity adapts to the user persona (child, student, professional, parent, senior) per PRD.md Section 11, but the underlying design system remains one coherent language, not fragmented sub-products.

---

## 6. API Rules

- **REST API** is the sole communication protocol between frontend and backend, per ARCHITECTURE.md Section 6.
- **Versioned** under `/api/v1/` for all endpoints, with no unversioned routes introduced.
- **Consistent JSON responses** — a standardized response envelope for both success and error cases, so the frontend can handle failures generically rather than per-endpoint.
- **Proper HTTP status codes** are used correctly and consistently — status codes communicate meaning and are never an afterthought.
- **Request validation** happens at the DRF serializer layer for every inbound request. No unvalidated data reaches a service or the database.
- **API documentation ready** — endpoints are structured and described such that formal API documentation can be generated or written without restructuring the API itself later.

---

## 7. Database Rules

- **PostgreSQL only.** No auxiliary databases are introduced without a deliberate architecture revision.
- **Use migrations exclusively.** All schema changes go through Django's migration framework — per ARCHITECTURE.md Section 4, no manual schema changes, ever.
- **Soft deletes where appropriate.** User-generated content uses `is_active`/`deleted_at` patterns rather than hard deletes, to support recovery and auditability.
- **`created_at` / `updated_at`** timestamps are standardized across all tables.
- **Normalized relationships.** Schema design follows normalized relational modeling with clear domain boundaries — no denormalization without a documented, deliberate performance justification.
- **Row-level ownership.** Every domain table is scoped to a `user_id`, with ownership enforced at the service layer, not just the database layer.

---

## 8. Security Rules

- **Environment variables** are the only mechanism for configuration and secrets. No credentials, keys, or environment-specific values are hardcoded anywhere in source.
- **Secure JWT** — short-lived access tokens, longer-lived refresh tokens, with Redis-backed denylisting for revocation on logout and security events.
- **Password hashing** via Django's built-in hashing framework (PBKDF2/Argon2), with enforced password strength rules at registration. Plaintext passwords never exist anywhere, even transiently in logs.
- **Input validation** on every inbound request via DRF serializers.
- **SQL Injection protection** — ORM usage only; no raw SQL queries.
- **XSS protection** — all rendered user content is properly escaped/sanitized; no `dangerouslySetInnerHTML`-equivalent shortcuts without deliberate, documented justification.
- **CSRF protection** enforced on all state-changing requests.
- **Rate limiting** on auth and AI-chat endpoints at minimum, enforced at the Nginx and/or DRF throttling layer, to prevent brute force and API cost abuse.
- **Secure secrets management** — no secrets committed to source control, ever; separate secrets per environment (dev/staging/prod).
- Security-sensitive actions (login, password change, OAuth linking, data export/delete) are logged for auditability.

---

## 9. Git Rules

- **Small commits.** Each commit represents one coherent, reviewable change — not a batch of unrelated edits.
- **Meaningful commit messages.** A commit message explains *why*, not just *what*; future contributors (including future AI sessions) must be able to understand intent from history alone.
- **Never commit secrets.** No API keys, credentials, tokens, or connection strings are ever committed, including in commit history — if this happens, it is treated as a security incident, not a typo to quietly fix.
- **Never commit `.env`.** Only `.env.example` templates are committed; real environment files are always gitignored.
- **Keep `main` stable.** `main` is always deployable. Work happens on branches; broken or incomplete work never lands on `main`.

---

## 10. AI Rules

- **Never call providers directly.** No part of the application — frontend, backend service, or Celery task — calls Gemini, OpenAI, or any future provider's SDK directly.
- **Always use the AI abstraction layer.** All AI access goes through the AI Provider Abstraction Layer defined in ARCHITECTURE.md Section 7 (`generate_response`, `summarize`, `extract_memory`, and equivalent contract methods). This is verified via code review against this document, per ROADMAP.md's Milestone 7 completion checklist.
- **Provider independent.** Domain logic never assumes a specific vendor's behavior, response format, or capability. Swapping or adding a provider requires only a new adapter, never changes to domain code.
- **Future RAG support.** Memory and context systems are designed to extend toward embedding-based retrieval without requiring architectural rework, per ARCHITECTURE.md Section 4 and Section 7.
- **Privacy-first AI.** User data sent to AI providers is scoped and minimized to only what's necessary for the given request — never full raw database access. Provider adapters are the sole egress point for user data to third-party AI APIs, keeping data flow auditable, per ARCHITECTURE.md Section 10.
- All AI-initiated actions that change user data require lightweight user confirmation before taking effect, per PRD.md Section 11 ("Confirmation-First Automation").

---

## 11. Performance Rules

- **Lazy loading.** Route-level code splitting is used throughout the frontend; nothing is loaded before it's needed.
- **Optimized API calls.** TanStack Query caching, background refetching, and optimistic updates are used deliberately to minimize redundant network traffic.
- **Redis caching.** Expensive or repeated reads (e.g., AI responses to identical prompts, frequently accessed reference data) are cached in Redis to reduce database and AI provider load, per ARCHITECTURE.md Section 11.
- **Celery for background jobs.** Any slow or bursty workload — AI calls, notifications, summarization, scheduled reminders — runs asynchronously through Celery, never blocking the request-response cycle.
- **Small bundle size.** Frontend dependencies and imports are chosen deliberately; unused libraries and unnecessary bundle weight are treated as technical debt, not ignored.

---

## 12. Testing Rules

- **Unit tests for services.** Business logic in the service layer is unit tested independent of the framework, in line with Clean Architecture's testability goals.
- **API tests.** Every endpoint's behavior — success paths, validation failures, and permission boundaries — is covered by tests.
- **Frontend component tests.** Components with meaningful logic or user interaction are tested, not just visually reviewed.
- **Integration tests for authentication.** The full auth flow (registration, login, OAuth, token refresh, revocation) is covered by integration tests given its role as the gateway to the entire product.
- **Test before merging.** No feature is merged to `main` without passing tests. A failing or absent test suite blocks the merge, not just a warning to fix later.

---

## 13. Documentation Rules

Documentation is treated as a first-class deliverable, not an afterthought.

- **Every completed milestone must update:**
  - `README.md` — to reflect any change in features, setup, or product surface area.
  - `ROADMAP.md` — checklist items marked complete, and any deliberate, documented scope revisions noted.
  - `CHANGELOG.md` (where applicable) — a record of what shipped, for future reference.
- **Documentation is kept synchronized with implementation at all times.** A milestone is not considered done if its documentation is stale — this is as binding as any completion checklist item in ROADMAP.md.
- When PROJECT_RULES.md, ARCHITECTURE.md, PRD.md, or ROADMAP.md need to change, the change is deliberate and documented — never an incidental side effect of an unrelated code change.

---

## 14. Things That Must Never Change

The following are foundational to MindMesh and must not be altered without a deliberate, explicit, and documented revision process — never as a side effect of a feature request, a shortcut under deadline pressure, or an individual contributor's preference:

- **Product Vision** — MindMesh as the single trusted, intelligent layer that remembers and connects a user's life, per PRD.md.
- **Architecture** — the layered, decoupled client-server design and Clean Architecture principles defined in ARCHITECTURE.md.
- **Tech Stack** — the finalized stack in Section 2 of this document.
- **Folder Structure** — the structure defined in ARCHITECTURE.md Section 9 and Section 4 of this document.
- **AI Abstraction Layer** — no direct provider SDK calls from domain code, ever.
- **Accessibility-first Philosophy** — the product must remain usable across the full age and ability spectrum described in PRD.md's personas.
- **Clean Architecture** — the separation of API, service, repository, and domain layers.
- **Security-first Mindset** — every rule in Section 8 of this document is treated as non-negotiable baseline, not aspirational best practice.

---

*This document is the permanent constitution of MindMesh. Every development session — human or AI — is expected to read and operate within these rules. Where a decision is ambiguous, resolve it in the direction of trust, simplicity, and long-term maintainability.*
