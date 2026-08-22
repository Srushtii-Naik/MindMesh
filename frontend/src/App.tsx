import { useEffect, useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from 'react-router-dom';
import { queryClient } from '@/api/queryClient';
import { router } from '@/router';
import { bootstrapSession } from '@/features/auth/bootstrap';

/**
 * Attempts to restore a session (via the httpOnly refresh cookie, see
 * features/auth/bootstrap.ts) before the router renders anything. Without
 * this gate, a returning user with a valid session would flash the
 * logged-out UI/redirect to /login for a moment on every page load, since
 * `isAuthenticated` starts false until the silent refresh resolves.
 */
function useSessionBootstrap(): boolean {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    bootstrapSession().finally(() => setReady(true));
  }, []);

  return ready;
}

export default function App() {
  const isReady = useSessionBootstrap();

  if (!isReady) {
    // Intentionally minimal/unstyled — this only shows for the brief
    // moment the silent refresh call is in flight.
    return null;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}
