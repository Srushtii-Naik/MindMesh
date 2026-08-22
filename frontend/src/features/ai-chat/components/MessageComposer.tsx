import { useForm } from 'react-hook-form';
import { extractApiErrorMessage } from '@/api/errors';
import { useSendMessage } from '@/features/ai-chat/hooks';

interface MessageComposerFormValues {
  content: string;
}

interface MessageComposerProps {
  conversationId: string;
}

/** Chat input (ROADMAP.md Milestone 7: "AI chat functional end-to-end
 * through the provider abstraction layer"). Mirrors features/notes/
 * components/NoteForm.tsx's React Hook Form + mutation error pattern. */
export function MessageComposer({ conversationId }: MessageComposerProps) {
  const sendMessage = useSendMessage(conversationId);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<MessageComposerFormValues>({ defaultValues: { content: '' } });

  const onSubmit = (values: MessageComposerFormValues) => {
    sendMessage.mutate(
      { content: values.content },
      {
        onSuccess: () => reset({ content: '' }),
      }
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-2">
      {sendMessage.error && (
        <p className="text-sm text-red-600 dark:text-red-400">
          {extractApiErrorMessage(sendMessage.error)}
        </p>
      )}

      <div className="flex items-end gap-2">
        <label htmlFor="chat-message-input" className="sr-only">
          Message
        </label>
        <textarea
          id="chat-message-input"
          rows={2}
          placeholder="Ask MindMesh anything…"
          disabled={sendMessage.isPending}
          className="flex-1 resize-none rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 disabled:opacity-60 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
          {...register('content', { required: 'Type a message first.' })}
        />
        <button
          type="submit"
          disabled={sendMessage.isPending}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:opacity-60"
        >
          {sendMessage.isPending ? 'Sending…' : 'Send'}
        </button>
      </div>

      {errors.content && (
        <p className="text-xs text-red-600 dark:text-red-400">{errors.content.message}</p>
      )}
    </form>
  );
}
