import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { MemoryPanel } from '@/features/ai-chat/components/MemoryPanel';
import type { MemoryFact } from '@/features/ai-chat/types';

const { listMemoryFactsRequest, updateMemoryFactRequest, deleteMemoryFactRequest } = vi.hoisted(
  () => ({
    listMemoryFactsRequest: vi.fn(),
    updateMemoryFactRequest: vi.fn(),
    deleteMemoryFactRequest: vi.fn(),
  })
);

vi.mock('@/features/ai-chat/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/ai-chat/api')>('@/features/ai-chat/api');
  return { ...actual, listMemoryFactsRequest, updateMemoryFactRequest, deleteMemoryFactRequest };
});

function makeFact(overrides: Partial<MemoryFact> = {}): MemoryFact {
  return {
    id: 'fact-1',
    fact_text: 'Prefers tea over coffee',
    category: 'preference',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

beforeEach(() => {
  listMemoryFactsRequest.mockReset();
  updateMemoryFactRequest.mockReset();
  deleteMemoryFactRequest.mockReset();
});

describe('MemoryPanel', () => {
  it('shows an empty state when there are no stored facts', async () => {
    listMemoryFactsRequest.mockResolvedValue([]);

    renderWithProviders(<MemoryPanel />);

    await waitFor(() =>
      expect(
        screen.getByText("MindMesh hasn't remembered anything yet — it learns as you chat.")
      ).toBeInTheDocument()
    );
  });

  it('renders each stored fact with its category', async () => {
    listMemoryFactsRequest.mockResolvedValue([
      makeFact({ id: 'fact-1', fact_text: 'Prefers tea over coffee', category: 'preference' }),
      makeFact({ id: 'fact-2', fact_text: 'Is a teacher', category: 'personal_fact' }),
    ]);

    renderWithProviders(<MemoryPanel />);

    expect(await screen.findByText('Prefers tea over coffee')).toBeInTheDocument();
    expect(screen.getByText('Is a teacher')).toBeInTheDocument();
    expect(screen.getAllByText('Preference').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Personal fact').length).toBeGreaterThan(0);
  });

  it('shows an error state when the request fails', async () => {
    listMemoryFactsRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<MemoryPanel />);

    await waitFor(() => expect(screen.getByText("Couldn't load memory.")).toBeInTheDocument());
  });

  it('re-fetches with the selected category filter', async () => {
    listMemoryFactsRequest.mockResolvedValue([]);

    renderWithProviders(<MemoryPanel />);

    await waitFor(() => expect(listMemoryFactsRequest).toHaveBeenCalledWith({}));

    fireEvent.change(screen.getByLabelText('Filter memory by category'), {
      target: { value: 'preference' },
    });

    await waitFor(() =>
      expect(listMemoryFactsRequest).toHaveBeenCalledWith({ category: 'preference' })
    );
  });

  it('lets a user edit a fact and saves the new text and category', async () => {
    const fact = makeFact();
    listMemoryFactsRequest.mockResolvedValue([fact]);
    updateMemoryFactRequest.mockResolvedValue({ ...fact, fact_text: 'Prefers green tea' });

    renderWithProviders(<MemoryPanel />);

    fireEvent.click(await screen.findByText('Edit'));

    const textarea = screen.getByLabelText('Memory fact text');
    fireEvent.change(textarea, { target: { value: 'Prefers green tea' } });
    fireEvent.click(screen.getByText('Save'));

    await waitFor(() => expect(updateMemoryFactRequest).toHaveBeenCalledOnce());
    expect(updateMemoryFactRequest).toHaveBeenCalledWith('fact-1', {
      fact_text: 'Prefers green tea',
      category: 'preference',
    });
  });

  it('lets a user delete a fact', async () => {
    listMemoryFactsRequest.mockResolvedValue([makeFact()]);
    deleteMemoryFactRequest.mockResolvedValue(undefined);

    renderWithProviders(<MemoryPanel />);

    fireEvent.click(await screen.findByText('Delete'));

    await waitFor(() => expect(deleteMemoryFactRequest).toHaveBeenCalledWith('fact-1'));
  });
});
