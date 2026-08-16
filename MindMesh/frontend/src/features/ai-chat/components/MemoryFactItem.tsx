import { useState } from 'react';
import { extractApiErrorMessage } from '@/api/errors';
import {
  MEMORY_CATEGORY_OPTIONS,
  MemoryCategoryBadge,
} from '@/features/ai-chat/components/MemoryCategoryBadge';
import { useDeleteMemoryFact, useUpdateMemoryFact } from '@/features/ai-chat/hooks';
import type { MemoryFact } from '@/features/ai-chat/types';

/**
 * A single stored memory fact with view/edit/delete controls (ROADMAP.md
 * Milestone 8: "User-facing controls to view/edit/delete stored memory" —
 * PRD.md Section 13's trust/privacy requirement).
 */
export function MemoryFactItem({ fact }: { fact: MemoryFact }) {
  const [isEditing, setIsEditing] = useState(false);
  const [factText, setFactText] = useState(fact.fact_text);
  const [category, setCategory] = useState(fact.category);

  const updateFact = useUpdateMemoryFact();
  const deleteFact = useDeleteMemoryFact();

  const handleSave = (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = factText.trim();
    if (!trimmed) return;

    updateFact.mutate(
      { factId: fact.id, payload: { fact_text: trimmed, category } },
      { onSuccess: () => setIsEditing(false) }
    );
  };

  const handleCancel = () => {
    setFactText(fact.fact_text);
    setCategory(fact.category);
    updateFact.reset();
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <li className="rounded-md border border-brand-300 bg-white p-3 dark:border-brand-700 dark:bg-slate-800">
        <form onSubmit={handleSave} className="space-y-2">
          <textarea
            value={factText}
            onChange={(event) => setFactText(event.target.value)}
            rows={2}
            aria-label="Memory fact text"
            className="w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value as MemoryFact['category'])}
              aria-label="Memory fact category"
              className="rounded-md border border-slate-300 bg-white px-2 py-1 text-xs text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            >
              {MEMORY_CATEGORY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <div className="ml-auto flex gap-2">
              <button
                type="button"
                onClick={handleCancel}
                className="rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!factText.trim() || updateFact.isPending}
                className="rounded-md bg-brand-600 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Save
              </button>
            </div>
          </div>

          {updateFact.isError && (
            <p className="text-xs text-red-600 dark:text-red-400" role="alert">
              {extractApiErrorMessage(updateFact.error)}
            </p>
          )}
        </form>
      </li>
    );
  }

  return (
    <li className="flex items-start justify-between gap-3 rounded-md border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800">
      <div className="min-w-0 flex-1">
        <p className="text-sm text-slate-700 dark:text-slate-200">{fact.fact_text}</p>
        <div className="mt-1.5">
          <MemoryCategoryBadge category={fact.category} />
        </div>
      </div>

      <div className="flex shrink-0 gap-2">
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className="text-xs font-medium text-slate-500 hover:text-brand-600 dark:text-slate-400 dark:hover:text-brand-400"
        >
          Edit
        </button>
        <button
          type="button"
          onClick={() => deleteFact.mutate(fact.id)}
          disabled={deleteFact.isPending}
          className="text-xs font-medium text-slate-500 hover:text-red-600 disabled:opacity-60 dark:text-slate-400 dark:hover:text-red-400"
        >
          Delete
        </button>
      </div>
    </li>
  );
}
