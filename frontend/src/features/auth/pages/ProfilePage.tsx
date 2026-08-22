import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ProfileForm } from '@/features/auth/components/ProfileForm';
import { ROUTES } from '@/constants';

export function ProfilePage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mx-auto max-w-md px-6 py-12"
    >
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Profile</h1>
        <Link
          to={ROUTES.HOME}
          className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Back
        </Link>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <ProfileForm />
      </div>
      <p className="mt-4 text-center text-sm">
        <Link
          to={ROUTES.SETTINGS}
          className="font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Account settings
        </Link>
      </p>
    </motion.div>
  );
}
