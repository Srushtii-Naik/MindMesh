import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { TaskFilterBar } from '@/features/tasks/components/TaskFilterBar';

const { listCategoriesRequest } = vi.hoisted(() => ({
  listCategoriesRequest: vi.fn(),
}));

vi.mock('@/features/tasks/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/tasks/api')>('@/features/tasks/api');
  return { ...actual, listCategoriesRequest };
});

describe('TaskFilterBar', () => {
  it('reports search text changes merged with existing filters', () => {
    listCategoriesRequest.mockResolvedValue([]);
    const onChange = vi.fn();

    renderWithProviders(<TaskFilterBar filters={{ priority: 'high' }} onChange={onChange} />);

    fireEvent.change(screen.getByPlaceholderText('Search tasks…'), {
      target: { value: 'groceries' },
    });

    expect(onChange).toHaveBeenCalledWith({ priority: 'high', search: 'groceries' });
  });

  it('reports completion status changes as a boolean', () => {
    listCategoriesRequest.mockResolvedValue([]);
    const onChange = vi.fn();

    renderWithProviders(<TaskFilterBar filters={{}} onChange={onChange} />);

    fireEvent.change(screen.getByDisplayValue('All tasks'), {
      target: { value: 'true' },
    });

    expect(onChange).toHaveBeenCalledWith({ is_completed: true });
  });
});
