interface PlaceholderCardProps {
  title: string;
  message: string;
}

/**
 * Shared shell for dashboard cards whose real data source doesn't exist
 * yet. Today's Summary graduated off this shell in Milestone 4, Upcoming
 * Events in Milestone 5, and AI Insights in Milestone 7 once the AI
 * Companion existed to power it. Kept here, still exported, for any future
 * card (e.g. Milestone 11 Analytics) that needs the same placeholder shell
 * before its domain is built.
 */
export function PlaceholderCard({ title, message }: PlaceholderCardProps) {
  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400">{message}</p>
    </div>
  );
}
