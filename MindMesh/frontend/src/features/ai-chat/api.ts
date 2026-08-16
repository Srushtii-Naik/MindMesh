import { apiClient } from '@/api/client';
import type { PaginatedResponse } from '@/types';
import type {
  AISuggestion,
  Conversation,
  ConversationPayload,
  MemoryFact,
  Message,
  MessagePayload,
} from '@/features/ai-chat/types';

/**
 * AI Companion domain requests (ROADMAP.md Milestone 7). Consumed
 * exclusively via the TanStack Query hooks in `features/ai-chat/hooks/` —
 * no component calls these directly, per ARCHITECTURE.md Section 2.
 */

// --------------------------------------------------------------------------
// Conversations
// --------------------------------------------------------------------------

export async function listConversationsRequest(): Promise<Conversation[]> {
  const { data } = await apiClient.get<Conversation[]>('/ai/conversations/');
  return data;
}

export async function getConversationRequest(conversationId: string): Promise<Conversation> {
  const { data } = await apiClient.get<Conversation>(`/ai/conversations/${conversationId}/`);
  return data;
}

export async function createConversationRequest(
  payload: ConversationPayload = {}
): Promise<Conversation> {
  const { data } = await apiClient.post<Conversation>('/ai/conversations/', payload);
  return data;
}

export async function deleteConversationRequest(conversationId: string): Promise<void> {
  await apiClient.delete(`/ai/conversations/${conversationId}/`);
}

// --------------------------------------------------------------------------
// Messages / Chat
// --------------------------------------------------------------------------

export async function listMessagesRequest(
  conversationId: string
): Promise<PaginatedResponse<Message>> {
  const { data } = await apiClient.get<PaginatedResponse<Message>>(
    `/ai/conversations/${conversationId}/messages/`
  );
  return data;
}

export async function sendMessageRequest(
  conversationId: string,
  payload: MessagePayload
): Promise<Message> {
  const { data } = await apiClient.post<Message>(
    `/ai/conversations/${conversationId}/messages/`,
    payload
  );
  return data;
}

// --------------------------------------------------------------------------
// Suggestions & Memory
// --------------------------------------------------------------------------

export async function getAISuggestionsRequest(): Promise<AISuggestion[]> {
  const { data } = await apiClient.get<AISuggestion[]>('/ai/suggestions/');
  return data;
}

export async function listMemoryFactsRequest(): Promise<MemoryFact[]> {
  const { data } = await apiClient.get<MemoryFact[]>('/ai/memory/');
  return data;
}
