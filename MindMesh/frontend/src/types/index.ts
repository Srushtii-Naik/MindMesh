/**
 * Shared, cross-domain TypeScript types/contracts.
 * Domain-specific types belong inside their respective `features/<domain>/types.ts`.
 */

export interface ApiErrorResponse {
  detail: string;
  code?: string;
}

/** Shape returned by any endpoint using DRF's PageNumberPagination. */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
