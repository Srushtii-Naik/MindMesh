import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { ReminderForm } from '@/features/reminders/components/ReminderForm';

const { createReminderRequest } = vi.hoisted(() => ({
  createReminderRequest: vi.fn(),
}));

vi.mock('@/features/reminders/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/reminders/api')>(
    '@/features/reminders/api'
  );
  return { ...actual, createReminderRequest };
});

beforeEach(() => {
  createReminderRequest.mockReset();
});

describe('ReminderForm', () => {
  it('submits the entered title and remind_at as an ISO payload', async () => {
    createReminderRequest.mockResolvedValue({
      id: 'reminder-1',
      title: 'Water plants',
      message: '',
      trigger_type: 'time',
      remind_at: '2026-03-10T09:00:00.000Z',
      task: null,
      event: null,
      is_sent: false,
      sent_at: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    renderWithProviders(<ReminderForm />);

    fireEvent.change(screen.getByLabelText('New reminder'), {
      target: { value: 'Water plants' },
    });
    fireEvent.change(screen.getByLabelText('Remind at'), {
      target: { value: '2026-03-10T09:00' },
    });
    fireEvent.click(screen.getByText('Add'));

    await waitFor(() => expect(createReminderRequest).toHaveBeenCalledOnce());

    const payload = createReminderRequest.mock.calls[0][0];
    expect(payload.title).toBe('Water plants');
    expect(typeof payload.remind_at).toBe('string');
  });

  it('shows a validation message when the title is left blank', async () => {
    renderWithProviders(<ReminderForm />);

    fireEvent.click(screen.getByText('Add'));

    expect(await screen.findByText('Title is required.')).toBeInTheDocument();
    expect(createReminderRequest).not.toHaveBeenCalled();
  });
});
