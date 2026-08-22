/**
 * Reads a cookie's value by name.
 *
 * Used exclusively for the auth CSRF double-submit cookie (see
 * apps/accounts/cookies.py on the backend) — that cookie is deliberately
 * NOT httpOnly so this code can read it and echo it back as a header on
 * refresh/logout requests. The refresh token itself is httpOnly and never
 * touches `document.cookie` or any other JavaScript-readable storage,
 * per ADR 0001 (docs/adr/0001-token-storage-strategy.md).
 */
export function getCookie(name: string): string | null {
  const match = document.cookie.split('; ').find((row) => row.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.split('=').slice(1).join('=')) : null;
}

/** Name of the CSRF cookie set by the backend (apps/accounts/cookies.py). */
export const CSRF_COOKIE_NAME = 'mm_csrf';

/** Header the backend expects the CSRF cookie's value echoed back on. */
export const CSRF_HEADER_NAME = 'X-CSRF-Token';

export function getCsrfHeader(): Record<string, string> {
  const token = getCookie(CSRF_COOKIE_NAME);
  return token ? { [CSRF_HEADER_NAME]: token } : {};
}
