import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { ProgressReportList } from '@/features/analytics/components/ProgressReportList';

const { listProgressReportsRequest } = vi.hoisted(() => ({
  listProgressReportsRequest: vi.fn(),
}));

vi.mock('@/features/analytics/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/analytics/api')>(
    '@/features/analytics/api'
  );
  return { ...actual, listProgressReportsRequest };
});

describe('ProgressReportList', () => {
  it('shows a calm empty state when no reports exist yet', async () => {
    listProgressReportsRequest.mockResolvedValue([]);

    renderWithProviders(<ProgressReportList />);

    expect(
      await screen.findByText(
        'Your first weekly report will appear here once a full week of activity has passed.'
      )
    ).toBeInTheDocument();
  });

  it('renders each report with its period and stats', async () => {
    listProgressReportsRequest.mockResolvedValue([
      {
        id: 'report-1',
        period_start: '2026-08-10',
        period_end: '2026-08-16',
        tasks_created: 10,
        tasks_completed: 8,
        completion_rate: 80,
        notes_created: 2,
        events_scheduled: 1,
        current_streak_days: 3,
        longest_streak_days: 5,
        ai_summary: 'A strong week — keep up the momentum.',
        created_at: '2026-08-17T01:00:00Z',
      },
    ]);

    renderWithProviders(<ProgressReportList />);

    expect(await screen.findByText('2026-08-10 – 2026-08-16')).toBeInTheDocument();
    expect(screen.getByText(/8 of 10 tasks completed/)).toBeInTheDocument();
    expect(screen.getByText('A strong week — keep up the momentum.')).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    listProgressReportsRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<ProgressReportList />);

    expect(await screen.findByText("Couldn't load progress reports.")).toBeInTheDocument();
  });
});
