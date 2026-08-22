import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { HabitStreakCard } from '@/features/analytics/components/HabitStreakCard';

const { getHabitTrackingRequest } = vi.hoisted(() => ({
  getHabitTrackingRequest: vi.fn(),
}));

vi.mock('@/features/analytics/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/analytics/api')>(
    '@/features/analytics/api'
  );
  return { ...actual, getHabitTrackingRequest };
});

describe('HabitStreakCard', () => {
  it('shows current and longest streaks once loaded', async () => {
    getHabitTrackingRequest.mockResolvedValue({
      period_start: '2026-05-22',
      period_end: '2026-08-20',
      current_streak_days: 4,
      longest_streak_days: 11,
      daily_activity: [
        { date: '2026-08-19', is_active_day: true },
        { date: '2026-08-20', is_active_day: true },
      ],
    });

    renderWithProviders(<HabitStreakCard />);

    expect(await screen.findByText('4 days')).toBeInTheDocument();
    expect(screen.getByText('11 days')).toBeInTheDocument();
  });

  it('singularizes a one-day streak', async () => {
    getHabitTrackingRequest.mockResolvedValue({
      period_start: '2026-08-20',
      period_end: '2026-08-20',
      current_streak_days: 1,
      longest_streak_days: 1,
      daily_activity: [{ date: '2026-08-20', is_active_day: true }],
    });

    renderWithProviders(<HabitStreakCard />);

    const oneDayLabels = await screen.findAllByText('1 day');
    expect(oneDayLabels).toHaveLength(2);
  });

  it('shows an error state when the request fails', async () => {
    getHabitTrackingRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<HabitStreakCard />);

    expect(await screen.findByText("Couldn't load habit tracking.")).toBeInTheDocument();
  });
});
