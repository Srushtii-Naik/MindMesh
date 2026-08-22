import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { TaskSuggestions } from '@/features/tasks/components/TaskSuggestions';

const { getTaskSuggestionsRequest } = vi.hoisted(() => ({
  getTaskSuggestionsRequest: vi.fn(),
}));

vi.mock('@/features/tasks/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/tasks/api')>('@/features/tasks/api');
  return { ...actual, getTaskSuggestionsRequest };
});

describe('TaskSuggestions', () => {
  it('renders nothing when there are no suggestions', async () => {
    getTaskSuggestionsRequest.mockResolvedValue([]);

    const { container } = renderWithProviders(<TaskSuggestions />);

    await waitFor(() => expect(container).toBeEmptyDOMElement());
  });

  it('renders each suggestion message', async () => {
    getTaskSuggestionsRequest.mockResolvedValue([
      { id: 'overdue', kind: 'overdue', message: 'You have 2 overdue tasks.', task_id: null },
    ]);

    renderWithProviders(<TaskSuggestions />);

    expect(await screen.findByText('You have 2 overdue tasks.')).toBeInTheDocument();
  });
});
