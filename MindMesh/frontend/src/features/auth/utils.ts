import { isAxiosError } from 'axios';

/**
 * DRF returns errors in a couple of shapes depending on where validation
 * failed:
 *   - Serializer field errors: { "email": ["..."], "password": ["..."] }
 *   - Service/view-level errors: { "detail": "...", "code": "..." }
 * This normalizes either shape into a single display string. A more complete
 * field-by-field mapping (RHF setError per field) can be layered on as forms
 * grow more complex; a single top-level message is sufficient for the
 * login/register forms at this stage.
 */
export function extractAuthErrorMessage(error: unknown): string {
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
