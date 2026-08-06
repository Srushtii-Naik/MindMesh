import { QueryClient } from '@tanstack/react-query';

/**
 * Shared TanStack Query client.
 * Per-domain query keys and hooks live inside each `features/<domain>` module.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30_000,
    },
  },
});
