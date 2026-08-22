import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { useAuthStore } from '@/features/auth';
import { SharedTasksPanel } from '@/features/family/components/SharedTasksPanel';
import type { Family, SharedTask } from '@/features/family/types';

const { listSharedTasksRequest, completeSharedTaskRequest, unshareTaskRequest } = vi.hoisted(
  () => ({
    listSharedTasksRequest: vi.fn(),
    completeSharedTaskRequest: vi.fn(),
    unshareTaskRequest: vi.fn(),
  })
);

vi.mock('@/features/family/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/family/api')>('@/features/family/api');
  return {
    ...actual,
    listSharedTasksRequest,
    completeSharedTaskRequest,
    unshareTaskRequest,
  };
});

const family: Family = {
  id: 'family-1',
  name: 'The Does',
  created_by: 'user-1',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

function makeSharedTask(overrides: Partial<SharedTask['share']> = {}): SharedTask {
  return {
    share: {
      id: 'share-1',
      resource_type: 'task',
      owner: { id: 'user-1', email: 'owner@example.com', full_name: 'Owner Person' },
      shared_by: { id: 'user-1', email: 'owner@example.com', full_name: 'Owner Person' },
      can_edit: false,
      created_at: '2026-01-01T00:00:00Z',
      ...overrides,
    },
    task: {
      id: 'task-1',
      title: 'Take out the trash',
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
    },
  };
}

beforeEach(() => {
  listSharedTasksRequest.mockReset();
  completeSharedTaskRequest.mockReset();
  unshareTaskRequest.mockReset();
  useAuthStore.setState({
    user: { id: 'user-2', email: 'kid@example.com', full_name: 'Kid Person', created_at: '' },
    isAuthenticated: true,
  });
});

describe('SharedTasksPanel', () => {
  it('shows an empty state when nothing is shared', async () => {
    listSharedTasksRequest.mockResolvedValue([]);
    renderWithProviders(<SharedTasksPanel family={family} />);

    expect(await screen.findByText(/no tasks have been shared/i)).toBeInTheDocument();
  });

  it('hides "Mark done" for a view-only share', async () => {
    listSharedTasksRequest.mockResolvedValue([makeSharedTask({ can_edit: false })]);
    renderWithProviders(<SharedTasksPanel family={family} />);

    await screen.findByText('Take out the trash');
    expect(screen.queryByRole('button', { name: /mark done/i })).not.toBeInTheDocument();
    expect(screen.getByText(/view only/i)).toBeInTheDocument();
  });

  it('lets a member with edit access complete a shared task', async () => {
    listSharedTasksRequest.mockResolvedValue([makeSharedTask({ can_edit: true })]);
    completeSharedTaskRequest.mockResolvedValue({});

    renderWithProviders(<SharedTasksPanel family={family} />);

    const button = await screen.findByRole('button', { name: /mark done/i });
    fireEvent.click(button);

    await waitFor(() =>
      expect(completeSharedTaskRequest).toHaveBeenCalledWith('family-1', 'share-1')
    );
  });
});
