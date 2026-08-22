import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { ReminderList } from '@/features/reminders/components/ReminderList';
import type { Reminder } from '@/features/reminders/types';

const { listRemindersRequest } = vi.hoisted(() => ({
  listRemindersRequest: vi.fn(),
}));

vi.mock('@/features/reminders/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/reminders/api')>(
    '@/features/reminders/api'
  );
  return { ...actual, listRemindersRequest };
});

function makeReminder(overrides: Partial<Reminder> = {}): Reminder {
  return {
    id: 'reminder-1',
    title: 'Take medication',
    message: '',
    trigger_type: 'time',
    remind_at: '2026-03-10T09:00:00Z',
    task: null,
    event: null,
    is_sent: false,
    sent_at: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('ReminderList', () => {
  it('shows an empty state when there are no reminders', async () => {
    listRemindersRequest.mockResolvedValue({ count: 0, next: null, previous: null, results: [] });

    renderWithProviders(<ReminderList />);

    await waitFor(() => expect(screen.getByText('No upcoming reminders yet.')).toBeInTheDocument());
  });

  it('renders each reminder returned by the query', async () => {
    listRemindersRequest.mockResolvedValue({
      count: 2,
      next: null,
      previous: null,
      results: [
        makeReminder({ id: '1', title: 'Take medication' }),
        makeReminder({ id: '2', title: 'Water plants' }),
      ],
    });

    renderWithProviders(<ReminderList />);

    expect(await screen.findByText('Take medication')).toBeInTheDocument();
    expect(screen.getByText('Water plants')).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    listRemindersRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<ReminderList />);

    await waitFor(() => expect(screen.getByText("Couldn't load reminders.")).toBeInTheDocument());
  });

  it('shows the linked task title alongside the reminder time', async () => {
    listRemindersRequest.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        makeReminder({
          title: 'Report reminder',
          task: { id: 'task-1', title: 'Submit report' },
        }),
      ],
    });

    renderWithProviders(<ReminderList />);

    expect(await screen.findByText(/Submit report/)).toBeInTheDocument();
  });
});
