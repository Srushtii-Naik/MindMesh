import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { NoteFilterBar } from '@/features/notes/components/NoteFilterBar';

const { listNoteCategoriesRequest, listNoteTagsRequest } = vi.hoisted(() => ({
  listNoteCategoriesRequest: vi.fn(),
  listNoteTagsRequest: vi.fn(),
}));

vi.mock('@/features/notes/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/notes/api')>('@/features/notes/api');
  return { ...actual, listNoteCategoriesRequest, listNoteTagsRequest };
});

describe('NoteFilterBar', () => {
  it('reports search text changes merged with existing filters', () => {
    listNoteCategoriesRequest.mockResolvedValue([]);
    listNoteTagsRequest.mockResolvedValue([]);
    const onChange = vi.fn();

    renderWithProviders(<NoteFilterBar filters={{ category_id: 'cat-1' }} onChange={onChange} />);

    fireEvent.change(screen.getByPlaceholderText('Search notes…'), {
      target: { value: 'doctor' },
    });

    expect(onChange).toHaveBeenCalledWith({ category_id: 'cat-1', search: 'doctor' });
  });

  it('reports category selection changes', async () => {
    listNoteCategoriesRequest.mockResolvedValue([
      { id: 'cat-1', name: 'Ideas', color: '#5f6dfa', created_at: '', updated_at: '' },
    ]);
    listNoteTagsRequest.mockResolvedValue([]);
    const onChange = vi.fn();

    renderWithProviders(<NoteFilterBar filters={{}} onChange={onChange} />);

    expect(await screen.findByText('Ideas')).toBeInTheDocument();

    fireEvent.change(screen.getByDisplayValue('Any category'), {
      target: { value: 'cat-1' },
    });

    expect(onChange).toHaveBeenCalledWith({ category_id: 'cat-1' });
  });
});
