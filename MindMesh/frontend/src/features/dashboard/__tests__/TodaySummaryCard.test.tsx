import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { TodaySummaryCard } from '@/features/dashboard/components/TodaySummaryCard';

const { getTodaySummaryRequest } = vi.hoisted(() => ({
  getTodaySummaryRequest: vi.fn(),
}));

vi.mock('@/features/tasks/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/tasks/api')>('@/features/tasks/api');
  return { ...actual, getTodaySummaryRequest };
});

describe('TodaySummaryCard', () => {
  it('shows a calm empty state when nothing is due or overdue', async () => {
    getTodaySummaryRequest.mockResolvedValue({
      due_today_count: 0,
      overdue_count: 0,
      completed_today_count: 0,
    });

    renderWithProviders(<TodaySummaryCard />);

    expect(await screen.findByText('Nothing due today. Nice and clear.')).toBeInTheDocument();
  });

  it('shows counts of due-today and overdue tasks', async () => {
    getTodaySummaryRequest.mockResolvedValue({
      due_today_count: 3,
      overdue_count: 1,
      completed_today_count: 2,
    });

    renderWithProviders(<TodaySummaryCard />);

    expect(await screen.findByText('3 tasks due today')).toBeInTheDocument();
    expect(screen.getByText('1 overdue')).toBeInTheDocument();
    expect(screen.getByText('2 completed today')).toBeInTheDocument();
  });

  it('links to the tasks page', async () => {
    getTodaySummaryRequest.mockResolvedValue({
      due_today_count: 0,
      overdue_count: 0,
      completed_today_count: 0,
    });

    renderWithProviders(<TodaySummaryCard />);

    await waitFor(() =>
      expect(screen.getByRole('link', { name: 'View tasks' })).toHaveAttribute('href', '/tasks')
    );
  });
});
