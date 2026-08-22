import { Link } from 'react-router-dom';
import { ROUTES } from '@/constants';

interface ComingSoonPageProps {
  title: string;
  description: string;
}

/**
 * Placeholder destination for dashboard quick actions that point at a
 * module not yet built (ROADMAP.md Milestone 3: "Quick actions route
 * correctly to their respective modules (stubbed if modules not yet
 * built)"). Generic and reusable across every stubbed module rather than a
 * one-off per feature, per PROJECT_RULES.md Section 4 on shared components.
 */
export function ComingSoonPage({ title, description }: ComingSoonPageProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-6 text-center">
      <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">{title}</h1>
      <p className="max-w-md text-sm text-slate-500 dark:text-slate-400">{description}</p>
      <Link
        to={ROUTES.HOME}
        className="mt-2 text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
      >
        Back to dashboard
      </Link>
    </div>
  );
}
