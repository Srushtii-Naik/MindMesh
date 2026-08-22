import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { NoteList } from '@/features/notes/components/NoteList';
import type { Note } from '@/features/notes/types';

const { listNotesRequest } = vi.hoisted(() => ({
  listNotesRequest: vi.fn(),
}));

vi.mock('@/features/notes/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/notes/api')>('@/features/notes/api');
  return { ...actual, listNotesRequest };
});

function makeNote(overrides: Partial<Note> = {}): Note {
  return {
    id: 'note-1',
    title: 'Doctor visit',
    content: 'Book a follow-up.',
    category: null,
    tags: [],
    attachments: [],
    ai_summary: '',
    ai_summary_generated_at: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('NoteList', () => {
  it('shows an empty state when there are no matching notes', async () => {
    listNotesRequest.mockResolvedValue({ count: 0, next: null, previous: null, results: [] });

    renderWithProviders(<NoteList filters={{}} onEdit={vi.fn()} />);

    await waitFor(() =>
      expect(screen.getByText('No notes match these filters yet.')).toBeInTheDocument()
    );
  });

  it('renders each note returned by the query', async () => {
    listNotesRequest.mockResolvedValue({
      count: 2,
      next: null,
      previous: null,
      results: [
        makeNote({ id: '1', title: 'Doctor visit' }),
        makeNote({ id: '2', title: 'Grocery list' }),
      ],
    });

    renderWithProviders(<NoteList filters={{}} onEdit={vi.fn()} />);

    expect(await screen.findByText('Doctor visit')).toBeInTheDocument();
    expect(screen.getByText('Grocery list')).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    listNotesRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<NoteList filters={{}} onEdit={vi.fn()} />);

    await waitFor(() => expect(screen.getByText("Couldn't load your notes.")).toBeInTheDocument());
  });
});
