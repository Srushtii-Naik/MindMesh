# ADR 0001 — Token Storage Strategy (Access & Refresh Tokens)

**Status:** Accepted for current milestone — flagged for mandatory re-evaluation before production
**Date:** Milestone 2.1 (Core Authentication)
**Owning documents:** ARCHITECTURE.md Section 5 (Authentication Flow), PROJECT_RULES.md Section 8 (Security Rules)

---

## Context

ARCHITECTURE.md Section 5 states that refresh tokens should be "stored securely (httpOnly cookie preferred over localStorage where feasible) to reduce XSS exposure." PROJECT_RULES.md Section 8 similarly commits MindMesh to a security-first posture as a non-negotiable baseline, not an aspirational goal.

Milestone 2.1 (Core Authentication) implemented email/password registration, login, JWT issuance, refresh, and logout. A storage mechanism for the access and refresh tokens on the frontend had to be chosen to complete that milestone.

## Decision

The current implementation stores both the access token and the refresh token in the browser's `localStorage`, via a persisted Zustand store (`frontend/src/features/auth/store.ts`). The Axios client reads the access token from this store to attach it to outgoing requests, and reads the refresh token to silently obtain a new access token on a `401` response.

## Why This Was Chosen for the Current Milestone

- **Simplicity within Milestone 2.1's scope.** The milestone's brief was "core authentication" — a working register/login/JWT/refresh/logout loop — not a full session-security hardening pass. `localStorage` is the standard, low-friction pairing for a JSON-based JWT API where the backend returns tokens in the response body (as the current `/api/v1/auth/` endpoints do).
- **No backend cookie infrastructure yet.** httpOnly cookie storage requires the backend itself to set and read the refresh token (typically via `Set-Cookie` on login/refresh and reading it server-side on refresh requests), rather than returning it as JSON for the client to store. That is a distinct architectural shape — it touches CORS configuration (`credentials: true`), CSRF protection for the refresh endpoint, and the shape of the refresh contract — and was judged to be a deliberate, separate change rather than an incidental part of getting core auth working.
- **Consistent with a vanilla, framework-agnostic store.** Keeping tokens in a Zustand store (backed by `localStorage`) let the Axios interceptor — which lives outside the React component tree — read and update tokens directly via `useAuthStore.getState()`/`.setState()`, without needing cookies to be parsed or synchronized separately.
- **ARCHITECTURE.md itself leaves room for this.** The phrase "preferred... where feasible" was read as permitting a staged approach: ship a working, correctly-scoped auth system now, and treat the cookie migration as a defined, upcoming hardening step rather than a blocking requirement for Milestone 2.1.

## Security Trade-off

`localStorage` is readable by any JavaScript running on the page, including malicious scripts injected via a successful XSS attack. This means:

- A successful XSS attack on MindMesh's frontend could exfiltrate both the access token and the refresh token, giving an attacker a live, renewable session — not just a short-lived one.
- httpOnly cookies are not readable by JavaScript at all, so the same XSS attack would not be able to directly steal the refresh token if it were cookie-stored (though the attacker could still make authenticated requests as the user via the browser in some CSRF-adjacent scenarios, which is why cookie-based storage must be paired with CSRF protection on the endpoints that rely on it).
- MindMesh's threat model — a companion trusted with a user's tasks, notes, calendar, and personal memory across children, seniors, and other vulnerable personas (PRD.md Section 6) — makes this a meaningful, not theoretical, risk once real user data is at stake.

This trade-off is considered acceptable **only** for the current development stage, where the product has no production users and no real personal data.

## Required Before Production

**httpOnly cookie-based refresh-token storage must be reconsidered as part of the Milestone 12 security audit** (per ROADMAP.md, Milestone 12 — Production & Deployment, "Full security audit completed and all findings resolved"). This ADR itself constitutes that audit finding, pre-registered against Milestone 12's checklist rather than left to be rediscovered at audit time.

## What Would Need to Change to Migrate

If/when the migration to httpOnly cookie-based refresh-token storage is made, the following are expected to change:

- **Backend (`apps/accounts/views.py`):** `LoginView`, `RegisterView`, and the refresh endpoint would need to set the refresh token via `Set-Cookie` (httpOnly, `Secure`, `SameSite=Strict` or `Lax`) instead of returning it in the JSON response body. The access token can likely remain in the response body, since it is short-lived and does not need the same protection.
- **CORS configuration (`config/settings/base.py`):** `CORS_ALLOW_CREDENTIALS = True` would need to be set, and `CORS_ALLOWED_ORIGINS` kept as a strict allow-list (already the case) since credentialed CORS requests cannot use a wildcard origin.
- **CSRF protection:** The refresh endpoint would need explicit CSRF protection, since it would now rely on an automatically-sent cookie rather than a token the client must deliberately attach — the exact risk httpOnly cookies otherwise avoid for GET-style attacks.
- **Frontend (`features/auth/store.ts`, `api/client.ts`):** The refresh token would be removed from the Zustand store and from `localStorage` entirely; the store would retain only the access token (still needed in memory for the `Authorization` header) and user object. The Axios client would need `withCredentials: true` so the browser sends the httpOnly cookie automatically on refresh requests.
- **Logout flow:** Would need to clear the cookie server-side (via an expired `Set-Cookie`) in addition to blacklisting the token, since the frontend can no longer read or clear it directly.

## References

- ARCHITECTURE.md, Section 5 — Authentication Flow
- PROJECT_RULES.md, Section 8 — Security Rules
- ROADMAP.md, Milestone 12 — Production & Deployment
