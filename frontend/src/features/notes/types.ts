/**
 * Notes & Knowledge domain types (ROADMAP.md Milestone 6). Mirrors the
 * shape returned by apps/notes/serializers.py.
 */

export interface NoteCategory {
  id: string;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface NoteTag {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface NoteAttachment {
  id: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  created_at: string;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  category: NoteCategory | null;
  tags: NoteTag[];
  attachments: NoteAttachment[];
  ai_summary: string;
  ai_summary_generated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface NoteFilters {
  category_id?: string;
  tag_id?: string;
  search?: string;
  page?: number;
}

export interface NotePayload {
  title?: string;
  content?: string;
  category_id?: string | null;
  tag_ids?: string[];
}

export interface CategoryPayload {
  name: string;
  color?: string;
}

export interface TagPayload {
  name: string;
}
