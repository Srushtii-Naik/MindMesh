# Changelog

All notable changes to MindMesh are documented here.

## [1.0.0] — Milestone 12: Production & Deployment

MindMesh's first production-ready release, covering Milestones 1–12 of
`docs/ROADMAP.md`. This entry documents what Milestone 12 itself added on
top of the already-complete M1–M11 feature set (auth, tasks, calendar,
notes, AI companion, memory engine, notifications, family workspace,
analytics & insights).

### Security

- **Refresh tokens moved to httpOnly cookies** (resolves ADR 0001,
  `docs/adr/0001-token-storage-strategy.md`). Previously stored in
  `localStorage` and readable by any script on the page; now delivered as
  an httpOnly, `Secure`-in-production cookie the browser manages, closing
  the XSS-exfiltration path documented in the ADR.
- Added a double-submit CSRF cookie protecting the two endpoints that read
  the refresh cookie (token refresh, logout) from cross-site request
  forgery.
- `config/settings/production.py` now fails fast — refuses to start — on
  an insecure default `SECRET_KEY`, empty `ALLOWED_HOSTS`, or missing
  `CSRF_TRUSTED_ORIGINS`, rather than silently running with unsafe
  defaults.
- Added HSTS, secure/httpOnly cookie flags, `X-Frame-Options`,
  `Referrer-Policy`, and `SECURE_PROXY_SSL_HEADER` (for Railway's
  edge-terminated TLS) to production settings.
- Security-sensitive actions (registration, login, Google OAuth login,
  logout, password reset, session revocation) are now logged via a
  dedicated `mindmesh.security` logger for auditability.

### Infrastructure

- Multi-stage Dockerfiles for both backend and frontend, with dedicated
  `development` and `production` targets — production runs as a non-root
  user, serves via gunicorn (backend) / Nginx (frontend), and defines a
  container `HEALTHCHECK`.
- `infra/docker-compose.prod.yml` — a production-topology stack for local
  verification of the production build before trusting a platform deploy.
- `infra/nginx/nginx.prod.conf` — adds rate-limit zones and security
  headers on top of the existing dev reverse-proxy config.
- `backend/railway.json` and `frontend/vercel.json` — deployment
  configuration for the two target platforms named in
  `PROJECT_RULES.md`.
- Added the previously-missing `celery_beat` service to
  `infra/docker-compose.yml`, so the local dev stack actually runs the
  scheduled jobs (reminders, weekly reports) it was already configured for.

### Reliability & Observability

- New `GET /api/v1/health/ready/` readiness endpoint — checks PostgreSQL
  and Redis connectivity, for platform healthchecks and uptime alerting,
  alongside the existing `/health/` liveness check.
- Structured, stdout-based logging configuration (`LOGGING` in
  `config/settings/base.py`), replacing the previously unconfigured
  default — Railway/Docker capture stdout directly.
- `backend/scripts/backup_postgres.sh` / `restore_postgres.sh` — automated
  PostgreSQL backup/restore, verified end-to-end against a real local
  database (round-tripped a seeded row and confirmed an exact match).
- `backend/scripts/load_test.py` — lightweight load-testing script (no new
  dependencies) for key endpoints, run against the local dev stack.

### Performance

- Route-level code splitting (`React.lazy`) across all page components,
  resolving the "chunk larger than 500kB" production build warning.

### Fixed

- None — no regressions from M1–M11 were found during this milestone's
  audit; the full existing test suite (443 tests) passed before any
  changes were made.
