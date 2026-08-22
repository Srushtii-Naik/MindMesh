import { useAISuggestions } from '@/features/ai-chat/hooks';

/**
 * AI-enhanced suggestions (ROADMAP.md Milestone 7: "Smart suggestions —
 * AI-enhanced, building on Milestone 4's baseline"). Also powers the
 * dashboard's AI Insights card.
 */
export function SuggestionsPanel() {
  const { data: suggestions, isLoading, isError } = useAISuggestions();

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading suggestions…</p>;
  }

  if (isError) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load suggestions.</p>
    );
  }

  if (!suggestions || suggestions.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Nothing to flag right now — you&apos;re all caught up.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {suggestions.map((suggestion) => (
        <li
          key={suggestion.id}
          className="rounded-md border border-slate-200 bg-white p-3 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
        >
          {suggestion.message}
        </li>
      ))}
    </ul>
  );
}
