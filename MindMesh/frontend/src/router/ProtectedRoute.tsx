import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/store';
import { ROUTES } from '@/constants';

/**
 * Gates its child routes behind authentication. Unauthenticated visitors are
 * redirected to /login, with the originally requested location preserved in
 * router state so the login flow can return them there afterward.
 *
 * Per PROJECT_RULES.md Section 4, this lives in `router/` rather than a
 * feature folder — route-guarding is a routing concern used across every
 * feature, not owned by the auth feature itself.
 */
export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
  }

  return <Outlet />;
}
