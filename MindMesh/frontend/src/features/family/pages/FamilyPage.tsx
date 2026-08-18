import { useState } from 'react';
import { CreateFamilyPrompt } from '@/features/family/components/CreateFamilyPrompt';
import { EmergencyContactsPanel } from '@/features/family/components/EmergencyContactsPanel';
import { FamilyMembersPanel } from '@/features/family/components/FamilyMembersPanel';
import { SharedEventsPanel } from '@/features/family/components/SharedEventsPanel';
import { SharedNotesPanel } from '@/features/family/components/SharedNotesPanel';
import { SharedTasksPanel } from '@/features/family/components/SharedTasksPanel';
import { useMyFamily } from '@/features/family/hooks';

type Tab = 'members' | 'tasks' | 'calendar' | 'notes' | 'emergency';

const TABS: { id: Tab; label: string }[] = [
  { id: 'members', label: 'Members' },
  { id: 'tasks', label: 'Shared Tasks' },
  { id: 'calendar', label: 'Shared Calendar' },
  { id: 'notes', label: 'Shared Notes' },
  { id: 'emergency', label: 'Emergency Contacts' },
];

/**
 * Family & Shared Workspace (ROADMAP.md Milestone 10). Renders the
 * onboarding prompt when the user has no family yet, otherwise a simple
 * tabbed workspace mirroring the calm, minimal design philosophy from
 * PROJECT_RULES.md.
 */
export function FamilyPage() {
  const { data: family, isLoading } = useMyFamily();
  const [tab, setTab] = useState<Tab>('members');

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 text-sm text-slate-500 dark:text-slate-400 sm:px-6 lg:px-8">
        Loading…
      </div>
    );
  }

  if (!family) {
    return <CreateFamilyPrompt />;
  }

  return (
    <section className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{family.name}</h1>

      <nav className="mt-4 flex flex-wrap gap-1 border-b border-slate-200 dark:border-slate-700">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`rounded-t-md px-3 py-2 text-sm font-medium transition ${
              tab === t.id
                ? 'border-b-2 border-brand-600 text-brand-600 dark:text-brand-400'
                : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <div className="mt-6">
        {tab === 'members' && <FamilyMembersPanel family={family} />}
        {tab === 'tasks' && <SharedTasksPanel family={family} />}
        {tab === 'calendar' && <SharedEventsPanel family={family} />}
        {tab === 'notes' && <SharedNotesPanel family={family} />}
        {tab === 'emergency' && <EmergencyContactsPanel family={family} />}
      </div>
    </section>
  );
}
