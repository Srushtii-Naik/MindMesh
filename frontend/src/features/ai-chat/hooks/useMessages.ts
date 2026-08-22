import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { listMessagesRequest, sendMessageRequest } from '@/features/ai-chat/api';
import { CONVERSATIONS_QUERY_KEY } from '@/features/ai-chat/hooks/useConversations';
import type { MessagePayload } from '@/features/ai-chat/types';

export const messagesQueryKey = (conversationId: string) =>
  ['ai-messages', conversationId] as const;

export function useMessages(conversationId: string | undefined) {
  return useQuery({
    queryKey: messagesQueryKey(conversationId ?? ''),
    queryFn: () => listMessagesRequest(conversationId as string),
    enabled: Boolean(conversationId),
  });
}

/**
 * Sending a message also invalidates the conversation list — the backend
 * derives a title from the first message and bumps `updated_at`
 * (apps.ai_companion.services.send_message_for_user), so the sidebar's
 * ordering/title needs to refresh too.
 */
export function useSendMessage(conversationId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: MessagePayload) => sendMessageRequest(conversationId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: messagesQueryKey(conversationId) });
      queryClient.invalidateQueries({ queryKey: CONVERSATIONS_QUERY_KEY });
    },
  });
}
