import { useTaskSuggestions } from '@/features/tasks/hooks';

/**
 * ROADMAP.md Milestone 4: "Smart suggestions (rule-based initially,
 * AI-enhanced later)". Backed by apps/tasks/services.py `get_task_suggestions`.
 */
export function TaskSuggestions() {
  const { data: suggestions, isLoading, isError } = useTaskSuggestions();

  if (isLoading || isError || !suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <section
      aria-label="Suggestions"
      className="rounded-lg border border-brand-200 bg-brand-50 p-4 dark:border-brand-800 dark:bg-brand-900/20"
    >
      <h2 className="mb-2 text-sm font-medium text-brand-700 dark:text-brand-300">Suggestions</h2>
      <ul className="space-y-1">
        {suggestions.map((suggestion) => (
          <li key={suggestion.id} className="text-sm text-brand-800 dark:text-brand-200">
            {suggestion.message}
          </li>
        ))}
      </ul>
    </section>
  );
}
