interface PlaceholderCardProps {
  title: string;
  message: string;
}

/**
 * Shared shell for dashboard cards whose real data source doesn't exist
 * yet (AI Insights needs the AI Companion — Milestone 7). Today's Summary
 * graduated off this shell in Milestone 4, and Upcoming Events graduated
 * in Milestone 5, once their domains had real data to show. Per
 * ROADMAP.md, AI Insights is explicitly allowed to stay placeholder-only
 * for now: "placeholder-ready, wired to AI module once available".
 */
export function PlaceholderCard({ title, message }: PlaceholderCardProps) {
  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400">{message}</p>
    </div>
  );
}
