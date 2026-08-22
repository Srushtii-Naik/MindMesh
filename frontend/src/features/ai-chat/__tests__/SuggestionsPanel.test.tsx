import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { SuggestionsPanel } from '@/features/ai-chat/components/SuggestionsPanel';
import type { AISuggestion } from '@/features/ai-chat/types';

const { getAISuggestionsRequest } = vi.hoisted(() => ({
  getAISuggestionsRequest: vi.fn(),
}));

vi.mock('@/features/ai-chat/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/ai-chat/api')>('@/features/ai-chat/api');
  return { ...actual, getAISuggestionsRequest };
});

function makeSuggestion(overrides: Partial<AISuggestion> = {}): AISuggestion {
  return {
    id: 'overdue',
    kind: 'overdue',
    message: 'You have 2 overdue tasks.',
    task_id: null,
    ...overrides,
  };
}

describe('SuggestionsPanel', () => {
  it('shows an all-caught-up message when there are no suggestions', async () => {
    getAISuggestionsRequest.mockResolvedValue([]);

    renderWithProviders(<SuggestionsPanel />);

    await waitFor(() =>
      expect(
        screen.getByText("Nothing to flag right now — you're all caught up.")
      ).toBeInTheDocument()
    );
  });

  it('renders each suggestion returned by the query', async () => {
    getAISuggestionsRequest.mockResolvedValue([
      makeSuggestion({ id: 'overdue', message: 'You have 2 overdue tasks.' }),
      makeSuggestion({
        id: 'ai-proactive',
        kind: 'ai_proactive',
        message: 'Focus on the overdue ones first.',
      }),
    ]);

    renderWithProviders(<SuggestionsPanel />);

    expect(await screen.findByText('You have 2 overdue tasks.')).toBeInTheDocument();
    expect(screen.getByText('Focus on the overdue ones first.')).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    getAISuggestionsRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<SuggestionsPanel />);

    await waitFor(() => expect(screen.getByText("Couldn't load suggestions.")).toBeInTheDocument());
  });
});
