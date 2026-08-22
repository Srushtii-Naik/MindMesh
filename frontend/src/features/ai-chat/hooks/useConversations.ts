import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createConversationRequest,
  deleteConversationRequest,
  getConversationRequest,
  listConversationsRequest,
} from '@/features/ai-chat/api';
import type { ConversationPayload } from '@/features/ai-chat/types';

export const CONVERSATIONS_QUERY_KEY = ['ai-conversations'] as const;
export const conversationDetailQueryKey = (conversationId: string) =>
  [...CONVERSATIONS_QUERY_KEY, 'detail', conversationId] as const;

function useInvalidateConversations() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: CONVERSATIONS_QUERY_KEY });
}

export function useConversations() {
  return useQuery({
    queryKey: CONVERSATIONS_QUERY_KEY,
    queryFn: listConversationsRequest,
  });
}

export function useConversation(conversationId: string | undefined) {
  return useQuery({
    queryKey: conversationDetailQueryKey(conversationId ?? ''),
    queryFn: () => getConversationRequest(conversationId as string),
    enabled: Boolean(conversationId),
  });
}

export function useCreateConversation() {
  const invalidateConversations = useInvalidateConversations();

  return useMutation({
    mutationFn: (payload: ConversationPayload = {}) => createConversationRequest(payload),
    onSuccess: invalidateConversations,
  });
}

export function useDeleteConversation() {
  const invalidateConversations = useInvalidateConversations();

  return useMutation({
    mutationFn: (conversationId: string) => deleteConversationRequest(conversationId),
    onSuccess: invalidateConversations,
  });
}
