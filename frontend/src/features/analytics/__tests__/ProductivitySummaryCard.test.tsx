import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { ProductivitySummaryCard } from '@/features/analytics/components/ProductivitySummaryCard';

const { getProductivityAnalyticsRequest } = vi.hoisted(() => ({
  getProductivityAnalyticsRequest: vi.fn(),
}));

vi.mock('@/features/analytics/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/analytics/api')>(
    '@/features/analytics/api'
  );
  return { ...actual, getProductivityAnalyticsRequest };
});

describe('ProductivitySummaryCard', () => {
  it('shows productivity totals once loaded', async () => {
    getProductivityAnalyticsRequest.mockResolvedValue({
      period_start: '2026-07-22',
      period_end: '2026-08-20',
      tasks_created: 12,
      tasks_completed: 9,
      completion_rate: 75,
      notes_created: 4,
      events_scheduled: 3,
      daily_series: [{ date: '2026-08-20', tasks_completed: 2, tasks_created: 3 }],
    });

    renderWithProviders(<ProductivitySummaryCard />);

    expect(await screen.findByText('9')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('4 / 3')).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    getProductivityAnalyticsRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<ProductivitySummaryCard />);

    expect(await screen.findByText("Couldn't load productivity analytics.")).toBeInTheDocument();
  });
});
