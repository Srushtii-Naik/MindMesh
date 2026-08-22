import { MessageBubble } from '@/features/ai-chat/components/MessageBubble';
import { useMessages } from '@/features/ai-chat/hooks';

interface MessageListProps {
  conversationId: string | undefined;
}

/** Renders a conversation's history (ROADMAP.md Milestone 7: "Conversation
 * history persisted and retrievable"). Mirrors features/notes/components/
 * NoteList.tsx's loading/empty/error handling. */
export function MessageList({ conversationId }: MessageListProps) {
  const { data, isLoading, isError } = useMessages(conversationId);

  if (!conversationId) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Start a new conversation or pick one from the list to begin.
      </p>
    );
  }

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading messages…</p>;
  }

  if (isError) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">
        Couldn&apos;t load this conversation.
      </p>
    );
  }

  if (!data || data.results.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Say hello to start the conversation.
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-3">
      {data.results.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </ul>
  );
}
