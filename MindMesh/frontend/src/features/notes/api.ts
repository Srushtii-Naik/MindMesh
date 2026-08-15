import { apiClient } from '@/api/client';
import type { PaginatedResponse } from '@/types';
import type {
  CategoryPayload,
  Note,
  NoteAttachment,
  NoteCategory,
  NoteFilters,
  NotePayload,
  NoteTag,
  TagPayload,
} from '@/features/notes/types';

/**
 * Notes & Knowledge domain requests (ROADMAP.md Milestone 6). Consumed
 * exclusively via the TanStack Query hooks in `features/notes/hooks/` — no
 * component calls these directly, per ARCHITECTURE.md Section 2.
 */

// --------------------------------------------------------------------------
// Categories
// --------------------------------------------------------------------------

export async function listNoteCategoriesRequest(): Promise<NoteCategory[]> {
  const { data } = await apiClient.get<NoteCategory[]>('/notes/categories/');
  return data;
}

export async function createNoteCategoryRequest(payload: CategoryPayload): Promise<NoteCategory> {
  const { data } = await apiClient.post<NoteCategory>('/notes/categories/', payload);
  return data;
}

export async function updateNoteCategoryRequest(
  categoryId: string,
  payload: CategoryPayload
): Promise<NoteCategory> {
  const { data } = await apiClient.patch<NoteCategory>(`/notes/categories/${categoryId}/`, payload);
  return data;
}

export async function deleteNoteCategoryRequest(categoryId: string): Promise<void> {
  await apiClient.delete(`/notes/categories/${categoryId}/`);
}

// --------------------------------------------------------------------------
// Tags
// --------------------------------------------------------------------------

export async function listNoteTagsRequest(): Promise<NoteTag[]> {
  const { data } = await apiClient.get<NoteTag[]>('/notes/tags/');
  return data;
}

export async function createNoteTagRequest(payload: TagPayload): Promise<NoteTag> {
  const { data } = await apiClient.post<NoteTag>('/notes/tags/', payload);
  return data;
}

export async function deleteNoteTagRequest(tagId: string): Promise<void> {
  await apiClient.delete(`/notes/tags/${tagId}/`);
}

// --------------------------------------------------------------------------
// Notes
// --------------------------------------------------------------------------

export async function listNotesRequest(filters: NoteFilters): Promise<PaginatedResponse<Note>> {
  const { data } = await apiClient.get<PaginatedResponse<Note>>('/notes/', { params: filters });
  return data;
}

export async function getNoteRequest(noteId: string): Promise<Note> {
  const { data } = await apiClient.get<Note>(`/notes/${noteId}/`);
  return data;
}

export async function createNoteRequest(payload: NotePayload): Promise<Note> {
  const { data } = await apiClient.post<Note>('/notes/', payload);
  return data;
}

export async function updateNoteRequest(noteId: string, payload: NotePayload): Promise<Note> {
  const { data } = await apiClient.patch<Note>(`/notes/${noteId}/`, payload);
  return data;
}

export async function deleteNoteRequest(noteId: string): Promise<void> {
  await apiClient.delete(`/notes/${noteId}/`);
}

export async function generateNoteSummaryRequest(noteId: string): Promise<Note> {
  const { data } = await apiClient.post<Note>(`/notes/${noteId}/summary/`);
  return data;
}

// --------------------------------------------------------------------------
// Attachments
// --------------------------------------------------------------------------

export async function uploadNoteAttachmentRequest(
  noteId: string,
  file: File
): Promise<NoteAttachment> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post<NoteAttachment>(
    `/notes/${noteId}/attachments/`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return data;
}

export async function deleteNoteAttachmentRequest(
  noteId: string,
  attachmentId: string
): Promise<void> {
  await apiClient.delete(`/notes/${noteId}/attachments/${attachmentId}/`);
}

/**
 * Downloads happen through `apiClient` (not a plain `<a href>`) because the
 * endpoint requires the JWT bearer token, which only the centralized
 * Axios instance's request interceptor attaches (client.ts) — a bare link
 * would hit the endpoint unauthenticated. The blob is saved via a
 * short-lived object URL, revoked immediately after the click.
 */
export async function downloadNoteAttachment(
  noteId: string,
  attachmentId: string,
  filename: string
): Promise<void> {
  const response = await apiClient.get(`/notes/${noteId}/attachments/${attachmentId}/download/`, {
    responseType: 'blob',
  });

  const objectUrl = URL.createObjectURL(response.data as Blob);
  const link = document.createElement('a');
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}
