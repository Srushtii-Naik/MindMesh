import { Link } from 'react-router-dom';
import { useAuthStore, useLogout } from '@/features/auth';
import { NotificationBell } from '@/features/notifications';
import { APP_NAME, ROUTES } from '@/constants';

/**
 * App-wide header for authenticated pages. Only renders nav/sign-out for a
 * signed-in user, so it's safe to mount unconditionally in AppLayout (e.g.
 * the 404 page, reached without auth, still gets a consistent shell).
 *
 * ROADMAP.md Milestone 3 lists "Home dashboard shell" as a feature — this is
 * that shell, applied consistently across every authenticated page rather
 * than duplicated per-page (it previously lived only inside HomePage).
 */
export function AppHeader() {
  const user = useAuthStore((state) => state.user);
  const logout = useLogout();

  return (
    <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <Link
          to={ROUTES.HOME}
          className="text-base font-semibold tracking-tight text-brand-700 dark:text-brand-300"
        >
          {APP_NAME}
        </Link>

        {user && (
          <nav className="flex items-center gap-4">
            <NotificationBell />
            <Link
              to={ROUTES.FAMILY}
              className="text-sm font-medium text-slate-600 hover:text-brand-600 dark:text-slate-300 dark:hover:text-brand-400"
            >
              Family
            </Link>
            <Link
              to={ROUTES.ANALYTICS}
              className="text-sm font-medium text-slate-600 hover:text-brand-600 dark:text-slate-300 dark:hover:text-brand-400"
            >
              Insights
            </Link>
            <Link
              to={ROUTES.PROFILE}
              className="text-sm font-medium text-slate-600 hover:text-brand-600 dark:text-slate-300 dark:hover:text-brand-400"
            >
              Profile
            </Link>
            <Link
              to={ROUTES.SETTINGS}
              className="text-sm font-medium text-slate-600 hover:text-brand-600 dark:text-slate-300 dark:hover:text-brand-400"
            >
              Settings
            </Link>
            <button
              type="button"
              onClick={() => logout.mutate()}
              disabled={logout.isPending}
              className="rounded-md border border-slate-300 px-3 py-1 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              {logout.isPending ? 'Signing out…' : 'Sign out'}
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}
