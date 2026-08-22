import { isAxiosError } from 'axios';

/**
 * DRF returns errors in a couple of shapes depending on where validation
 * failed:
 *   - Serializer field errors: { "email": ["..."], "password": ["..."] }
 *   - Service/view-level errors: { "detail": "...", "code": "..." }
 * This normalizes either shape into a single display string. A more complete
 * field-by-field mapping (RHF setError per field) can be layered on as forms
 * grow more complex; a single top-level message is sufficient for now.
 *
 * Originally lived in `features/auth/utils.ts` (which now re-exports this)
 * — moved here once the tasks feature needed the same DRF-error-shape
 * parsing, to avoid duplicating it per domain (PROJECT_RULES.md Section 3).
 */
export function extractApiErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | undefined;

    if (!data) {
      return 'Network error — please check your connection and try again.';
    }

    if (typeof data.detail === 'string') {
      return data.detail;
    }

    const firstFieldError = Object.values(data).find(
      (value): value is string[] => Array.isArray(value) && value.length > 0
    );
    if (firstFieldError) {
      return firstFieldError[0];
    }
  }

  return 'Something went wrong. Please try again.';
}
