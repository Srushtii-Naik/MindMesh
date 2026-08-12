import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { QuickActions } from '@/features/dashboard/components/QuickActions';
import { ROUTES } from '@/constants';

describe('QuickActions', () => {
  it('links each action to its (stubbed) module route', () => {
    renderWithProviders(<QuickActions />);

    expect(screen.getByRole('link', { name: /new task/i })).toHaveAttribute('href', ROUTES.TASKS);
    expect(screen.getByRole('link', { name: /new note/i })).toHaveAttribute('href', ROUTES.NOTES);
    expect(screen.getByRole('link', { name: /new event/i })).toHaveAttribute(
      'href',
      ROUTES.CALENDAR
    );
    expect(screen.getByRole('link', { name: /ask mindmesh/i })).toHaveAttribute(
      'href',
      ROUTES.AI_CHAT
    );
  });
});
