import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { APP_NAME } from '@/constants';

/**
 * Shared layout for unauthenticated auth screens (login, register).
 * Kept minimal and calm per PROJECT_RULES.md Section 5 — a centered card,
 * no navigation chrome, no distractions.
 */
export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="w-full max-w-sm"
      >
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-brand-700 dark:text-brand-300">
            {APP_NAME}
          </h1>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <Outlet />
        </div>
      </motion.div>
    </div>
  );
}
