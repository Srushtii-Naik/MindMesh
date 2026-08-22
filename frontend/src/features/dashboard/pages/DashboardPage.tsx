import { motion } from 'framer-motion';
import { useAuthStore } from '@/features/auth';
import { QuickActions } from '@/features/dashboard/components/QuickActions';
import { TodaySummaryCard } from '@/features/dashboard/components/TodaySummaryCard';
import { UpcomingEventsCard } from '@/features/dashboard/components/UpcomingEventsCard';
import { AIInsightsCard } from '@/features/dashboard/components/AIInsightsCard';
import { RecentActivityFeed } from '@/features/dashboard/components/RecentActivityFeed';

/**
 * ROADMAP.md Milestone 3 — Dashboard: "a single, calm home base that
 * orients the user and surfaces what matters most at a glance."
 * Replaces the Milestone 1/2 placeholder HomePage.
 */
export function DashboardPage() {
  const user = useAuthStore((state) => state.user);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8"
    >
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-brand-700 dark:text-brand-300">
          {user ? `Welcome back, ${user.full_name}` : 'Welcome back'}
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Here&apos;s what&apos;s going on.
        </p>
      </header>

      <QuickActions />

      <section
        aria-label="At a glance"
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        <TodaySummaryCard />
        <UpcomingEventsCard />
        <AIInsightsCard />
      </section>

      <RecentActivityFeed />
    </motion.div>
  );
}
