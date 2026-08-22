import { HabitStreakCard } from '@/features/analytics/components/HabitStreakCard';
import { ProductivitySummaryCard } from '@/features/analytics/components/ProductivitySummaryCard';
import { ProgressReportList } from '@/features/analytics/components/ProgressReportList';
import { RecommendationsCard } from '@/features/analytics/components/RecommendationsCard';

/**
 * Analytics & Insights (ROADMAP.md Milestone 11). Turns accumulated task,
 * note, and calendar data into productivity analytics, habit tracking,
 * AI-generated recommendations, and weekly progress reports — presented
 * calmly and clearly, per PROJECT_RULES.md's "no dashboard clutter" bar.
 */
export function AnalyticsPage() {
  return (
    <section className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Insights</h1>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
        A calm look at how your week is going.
      </p>

      <div className="mt-6 grid gap-4">
        <ProductivitySummaryCard />
        <HabitStreakCard />
        <RecommendationsCard />
        <ProgressReportList />
      </div>
    </section>
  );
}
