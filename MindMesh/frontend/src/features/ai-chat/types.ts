/**
 * AI Companion domain types (ROADMAP.md Milestone 7). Mirrors the shape
 * returned by apps/ai_companion/serializers.py.
 */

export type MessageRole = 'user' | 'assistant';

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface MemoryFact {
  id: string;
  fact_text: string;
  created_at: string;
}

export interface AISuggestion {
  id: string;
  kind: string;
  message: string;
  task_id: string | null;
}

export interface ConversationPayload {
  title?: string;
}

export interface MessagePayload {
  content: string;
}
