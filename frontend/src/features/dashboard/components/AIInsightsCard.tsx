import { Link } from 'react-router-dom';
import { useAISuggestions } from '@/features/ai-chat';
import { ROUTES } from '@/constants';

/**
 * ROADMAP.md Milestone 5's dashboard placeholder ("placeholder-ready, wired
 * to AI module once available") graduates here now that the AI Companion
 * (Milestone 7) exists — mirroring how UpcomingEventsCard graduated off
 * PlaceholderCard in Milestone 5 once Calendar had real data.
 */
export function AIInsightsCard() {
  const { data: suggestions, isLoading, isError } = useAISuggestions();

  const topSuggestion = suggestions?.[0];

  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">AI insights</h3>

      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}

      {isError && (
        <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load insights.</p>
      )}

      {suggestions && suggestions.length === 0 && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Nothing to flag right now — you&apos;re all caught up.
        </p>
      )}

      {topSuggestion && (
        <p className="text-sm text-slate-600 dark:text-slate-300">{topSuggestion.message}</p>
      )}

      <Link
        to={ROUTES.AI_CHAT}
        className="mt-auto text-xs font-medium text-brand-600 hover:underline dark:text-brand-400"
      >
        Chat with MindMesh
      </Link>
    </div>
  );
}
