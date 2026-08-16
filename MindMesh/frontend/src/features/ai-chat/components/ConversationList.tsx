import {
  useCreateConversation,
  useConversations,
  useDeleteConversation,
} from '@/features/ai-chat/hooks';
import type { Conversation } from '@/features/ai-chat/types';

interface ConversationListProps {
  activeConversationId: string | undefined;
  onSelect: (conversationId: string) => void;
}

/**
 * Sidebar list of the user's conversations (ROADMAP.md Milestone 7:
 * "Conversation history persisted and retrievable"). Mirrors
 * features/notes/components/NoteList.tsx's loading/empty/error handling.
 */
export function ConversationList({ activeConversationId, onSelect }: ConversationListProps) {
  const { data: conversations, isLoading, isError } = useConversations();
  const createConversation = useCreateConversation();
  const deleteConversation = useDeleteConversation();

  const handleNewConversation = () => {
    createConversation.mutate(
      {},
      {
        onSuccess: (conversation: Conversation) => onSelect(conversation.id),
      }
    );
  };

  const handleDelete = (conversationId: string) => {
    deleteConversation.mutate(conversationId, {
      onSuccess: () => {
        if (conversationId === activeConversationId) {
          onSelect('');
        }
      },
    });
  };

  return (
    <div className="flex h-full flex-col gap-3">
      <button
        type="button"
        onClick={handleNewConversation}
        disabled={createConversation.isPending}
        className="rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:opacity-60"
      >
        New conversation
      </button>

      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}

      {isError && (
        <p className="text-sm text-red-600 dark:text-red-400">
          Couldn&apos;t load your conversations.
        </p>
      )}

      {conversations && conversations.length === 0 && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          No conversations yet — start one above.
        </p>
      )}

      {conversations && conversations.length > 0 && (
        <ul className="flex-1 space-y-1 overflow-y-auto">
          {conversations.map((conversation) => (
            <li
              key={conversation.id}
              className={`group flex items-center gap-1 rounded-md text-sm transition ${
                conversation.id === activeConversationId
                  ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700'
              }`}
            >
              <button
                type="button"
                onClick={() => onSelect(conversation.id)}
                className="flex-1 truncate px-3 py-2 text-left"
              >
                {conversation.title || 'New conversation'}
              </button>
              <button
                type="button"
                aria-label="Delete conversation"
                onClick={() => handleDelete(conversation.id)}
                className="mr-2 shrink-0 text-xs text-slate-400 opacity-0 hover:text-red-600 group-hover:opacity-100 dark:hover:text-red-400"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
