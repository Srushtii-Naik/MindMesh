/**
 * Shared, cross-domain TypeScript types/contracts.
 * Domain-specific types belong inside their respective `features/<domain>/types.ts`.
 */

export interface ApiErrorResponse {
  detail: string;
  code?: string;
}
