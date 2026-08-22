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

/**
 * Mirrors apps/ai_companion/models.py's MemoryCategory (ROADMAP.md
 * Milestone 8 — Memory Engine).
 */
export type MemoryCategory =
  'preference' | 'important_date' | 'routine' | 'relationship' | 'personal_fact';

export interface MemoryFact {
  id: string;
  fact_text: string;
  category: MemoryCategory;
  created_at: string;
  updated_at: string;
}

export interface MemoryFactPayload {
  fact_text?: string;
  category?: MemoryCategory;
}

export interface MemoryFactFilters {
  category?: MemoryCategory;
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
