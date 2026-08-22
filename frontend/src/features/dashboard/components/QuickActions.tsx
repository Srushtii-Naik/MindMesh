import { Link } from 'react-router-dom';
import { ROUTES } from '@/constants';

interface QuickAction {
  label: string;
  description: string;
  to: string;
  icon: string;
}

const QUICK_ACTIONS: QuickAction[] = [
  { label: 'New task', description: 'Capture something to do', to: ROUTES.TASKS, icon: '✓' },
  { label: 'New note', description: 'Write down a thought', to: ROUTES.NOTES, icon: '✎' },
  {
    label: 'New event',
    description: 'Add something to your calendar',
    to: ROUTES.CALENDAR,
    icon: '◷',
  },
  {
    label: 'Ask MindMesh',
    description: 'Chat with your AI companion',
    to: ROUTES.AI_CHAT,
    icon: '✺',
  },
];

/**
 * ROADMAP.md Milestone 3: "Quick actions (create task, note, event, chat)",
 * routing to each module's placeholder until its own milestone builds it.
 */
export function QuickActions() {
  return (
    <section aria-labelledby="quick-actions-heading">
      <h2
        id="quick-actions-heading"
        className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300"
      >
        Quick actions
      </h2>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {QUICK_ACTIONS.map((action) => (
          <Link
            key={action.to}
            to={action.to}
            className="flex flex-col items-start gap-1 rounded-lg border border-slate-200 bg-white p-4 text-left transition hover:border-brand-300 hover:shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:hover:border-brand-700"
          >
            <span aria-hidden="true" className="text-lg text-brand-600 dark:text-brand-400">
              {action.icon}
            </span>
            <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
              {action.label}
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400">{action.description}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
