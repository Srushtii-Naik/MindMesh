import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getHealthStatus } from '@/api/health';
import { APP_NAME, ROUTES } from '@/constants';
import { useAuthStore, useLogout } from '@/features/auth';

/**
 * Placeholder landing page. Confirms the frontend, routing, TanStack Query,
 * Axios client, and now authentication are wired together end-to-end.
 * Replaced by the real dashboard in Milestone 3.
 */
export function HomePage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: getHealthStatus,
    retry: false,
  });

  const user = useAuthStore((state) => state.user);
  const logout = useLogout();

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex min-h-screen flex-col items-center justify-center gap-3 px-6 text-center"
    >
      <h1 className="text-3xl font-semibold tracking-tight text-brand-700 dark:text-brand-300">
        {APP_NAME}
      </h1>
      {user && (
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Signed in as <span className="font-medium">{user.full_name}</span> ({user.email})
        </p>
      )}
      <p className="max-w-md text-sm text-slate-500 dark:text-slate-400">
        Backend connectivity: {isLoading && 'checking…'}
        {isError && 'unavailable (expected until the backend is running)'}
        {data && `connected (${data.status})`}
      </p>
      <div className="mt-2 flex items-center gap-3">
        <Link
          to={ROUTES.PROFILE}
          className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Profile
        </Link>
        <Link
          to={ROUTES.SETTINGS}
          className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Settings
        </Link>
      </div>
      <button
        type="button"
        onClick={() => logout.mutate()}
        disabled={logout.isPending}
        className="mt-2 rounded-md border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        {logout.isPending ? 'Signing out…' : 'Sign out'}
      </button>
    </motion.div>
  );
}
