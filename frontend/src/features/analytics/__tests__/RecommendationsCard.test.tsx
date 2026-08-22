import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { RecommendationsCard } from '@/features/analytics/components/RecommendationsCard';

const { getRecommendationsRequest } = vi.hoisted(() => ({
  getRecommendationsRequest: vi.fn(),
}));

vi.mock('@/features/analytics/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/analytics/api')>(
    '@/features/analytics/api'
  );
  return { ...actual, getRecommendationsRequest };
});

describe('RecommendationsCard', () => {
  it('renders each recommendation returned by the API', async () => {
    getRecommendationsRequest.mockResolvedValue({
      recommendations: ['Wrap up the overdue report task first.', 'Take a short break today.'],
    });

    renderWithProviders(<RecommendationsCard />);

    expect(await screen.findByText('Wrap up the overdue report task first.')).toBeInTheDocument();
    expect(screen.getByText('Take a short break today.')).toBeInTheDocument();
  });

  it('shows a calm empty state when there are no recommendations', async () => {
    getRecommendationsRequest.mockResolvedValue({ recommendations: [] });

    renderWithProviders(<RecommendationsCard />);

    expect(
      await screen.findByText('Nothing to suggest right now — keep going.')
    ).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    getRecommendationsRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<RecommendationsCard />);

    expect(await screen.findByText("Couldn't load recommendations right now.")).toBeInTheDocument();
  });
});
