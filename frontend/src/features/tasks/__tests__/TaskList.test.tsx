import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { TaskList } from '@/features/tasks/components/TaskList';
import type { Task } from '@/features/tasks/types';

const { listTasksRequest } = vi.hoisted(() => ({
  listTasksRequest: vi.fn(),
}));

vi.mock('@/features/tasks/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/tasks/api')>('@/features/tasks/api');
  return { ...actual, listTasksRequest };
});

function makeTask(overrides: Partial<Task> = {}): Task {
  return {
    id: 'task-1',
    title: 'Buy milk',
    description: '',
    category: null,
    priority: 'medium',
    due_date: null,
    is_completed: false,
    completed_at: null,
    recurrence: 'none',
    recurrence_interval: 1,
    subtasks: [],
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('TaskList', () => {
  it('shows an empty state when there are no matching tasks', async () => {
    listTasksRequest.mockResolvedValue({ count: 0, next: null, previous: null, results: [] });

    renderWithProviders(<TaskList filters={{}} onEdit={vi.fn()} />);

    await waitFor(() =>
      expect(screen.getByText('No tasks match these filters yet.')).toBeInTheDocument()
    );
  });

  it('renders each task returned by the query', async () => {
    listTasksRequest.mockResolvedValue({
      count: 2,
      next: null,
      previous: null,
      results: [
        makeTask({ id: '1', title: 'Buy milk' }),
        makeTask({ id: '2', title: 'Write report' }),
      ],
    });

    renderWithProviders(<TaskList filters={{}} onEdit={vi.fn()} />);

    expect(await screen.findByText('Buy milk')).toBeInTheDocument();
    expect(screen.getByText('Write report')).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    listTasksRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<TaskList filters={{}} onEdit={vi.fn()} />);

    await waitFor(() => expect(screen.getByText("Couldn't load your tasks.")).toBeInTheDocument());
  });
});
