import { useRecommendations } from '@/features/analytics/hooks';

/**
 * ROADMAP.md Milestone 11 checklist: "AI-generated recommendations
 * surfaced through the AI abstraction layer." Backed by
 * GET /analytics/recommendations/, which returns an empty list (never an
 * error) if the AI provider is unavailable — recommendations are advisory,
 * so an empty state here is expected, not a failure.
 */
export function RecommendationsCard() {
  const { data, isLoading, isError } = useRecommendations();
  const recommendations = data?.recommendations ?? [];

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">AI recommendations</h3>

      {isLoading && <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Loading…</p>}

      {isError && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400">
          Couldn&apos;t load recommendations right now.
        </p>
      )}

      {!isLoading && !isError && recommendations.length === 0 && (
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Nothing to suggest right now — keep going.
        </p>
      )}

      {recommendations.length > 0 && (
        <ul className="mt-2 space-y-2 text-sm text-slate-600 dark:text-slate-300">
          {recommendations.map((recommendation, index) => (
            <li key={index} className="flex gap-2">
              <span aria-hidden="true" className="text-brand-500 dark:text-brand-400">
                •
              </span>
              <span>{recommendation}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
