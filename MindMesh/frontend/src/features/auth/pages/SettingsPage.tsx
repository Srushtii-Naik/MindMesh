import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { SettingsForm } from '@/features/auth/components/SettingsForm';
import { SessionsList } from '@/features/auth/components/SessionsList';
import { ROUTES } from '@/constants';

export function SettingsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mx-auto max-w-md px-6 py-12"
    >
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Settings</h1>
        <Link
          to={ROUTES.HOME}
          className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Back
        </Link>
      </div>

      <div className="mb-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h2 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">
          Preferences
        </h2>
        <SettingsForm />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h2 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">
          Active sessions
        </h2>
        <SessionsList />
      </div>
    </motion.div>
  );
}
