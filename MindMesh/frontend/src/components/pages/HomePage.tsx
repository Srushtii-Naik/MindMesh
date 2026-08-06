import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { getHealthStatus } from '@/api/health';
import { APP_NAME } from '@/constants';

/**
 * Placeholder landing page for Milestone 1 (Project Foundation).
 * Confirms the frontend, routing, TanStack Query, and Axios client are wired
 * together end-to-end. Replaced by the real dashboard in Milestone 3.
 */
export function HomePage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: getHealthStatus,
    retry: false,
  });

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
      <p className="max-w-md text-sm text-slate-500 dark:text-slate-400">
        Project foundation is running. Backend connectivity:{' '}
        {isLoading && 'checking…'}
        {isError && 'unavailable (expected until the backend is running)'}
        {data && `connected (${data.status})`}
      </p>
    </motion.div>
  );
}
