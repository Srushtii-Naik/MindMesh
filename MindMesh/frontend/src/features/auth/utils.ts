/**
 * Re-exported from the shared location (src/api/errors.ts) now that the
 * tasks feature needs the same DRF-error-shape parsing. Kept here under
 * its original name so existing imports throughout this feature don't
 * need to change.
 */
export { extractApiErrorMessage as extractAuthErrorMessage } from '@/api/errors';
