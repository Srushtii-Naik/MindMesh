import { useState } from 'react';
import { MEMORY_CATEGORY_OPTIONS } from '@/features/ai-chat/components/MemoryCategoryBadge';
import { MemoryFactItem } from '@/features/ai-chat/components/MemoryFactItem';
import { useMemoryFacts } from '@/features/ai-chat/hooks';
import type { MemoryCategory } from '@/features/ai-chat/types';

/**
 * ROADMAP.md Milestone 8 — Memory Engine: what MindMesh currently
 * remembers about the user, with filter, edit, and delete controls.
 * PRD.md Section 13 ("Granular consent"): users can view, edit, or delete
 * stored memory at any time.
 */
export function MemoryPanel() {
  const [category, setCategory] = useState<MemoryCategory | ''>('');
  const { data: facts, isLoading, isError } = useMemoryFacts(category ? { category } : {});

  return (
    <div className="space-y-3">
      <select
        value={category}
        onChange={(event) => setCategory(event.target.value as MemoryCategory | '')}
        aria-label="Filter memory by category"
        className="w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
      >
        <option value="">All categories</option>
        {MEMORY_CATEGORY_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading memory…</p>}

      {isError && (
        <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load memory.</p>
      )}

      {!isLoading && !isError && (!facts || facts.length === 0) && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          MindMesh hasn&apos;t remembered anything yet — it learns as you chat.
        </p>
      )}

      {facts && facts.length > 0 && (
        <ul className="space-y-2">
          {facts.map((fact) => (
            <MemoryFactItem key={fact.id} fact={fact} />
          ))}
        </ul>
      )}
    </div>
  );
}
