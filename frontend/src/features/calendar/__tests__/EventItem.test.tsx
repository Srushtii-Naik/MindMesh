import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { EventItem } from '@/features/calendar/components/EventItem';
import type { CalendarEvent } from '@/features/calendar/types';

function makeEvent(overrides: Partial<CalendarEvent> = {}): CalendarEvent {
  return {
    id: 'event-1',
    title: 'Dentist appointment',
    description: '',
    location: '',
    start_time: '2026-03-10T09:00:00Z',
    end_time: '2026-03-10T10:00:00Z',
    all_day: false,
    color: '#5f6dfa',
    task: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('EventItem', () => {
  it('renders the event title and location', () => {
    renderWithProviders(
      <EventItem
        event={makeEvent({ location: 'Downtown Clinic' })}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
      />
    );

    expect(screen.getByText('Dentist appointment')).toBeInTheDocument();
    expect(screen.getByText(/Downtown Clinic/)).toBeInTheDocument();
  });

  it('shows "All day" instead of a time range for all-day events', () => {
    renderWithProviders(
      <EventItem event={makeEvent({ all_day: true })} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    expect(screen.getByText(/All day/)).toBeInTheDocument();
  });

  it('shows the linked task title when present', () => {
    renderWithProviders(
      <EventItem
        event={makeEvent({ task: { id: 'task-1', title: 'Prepare report', is_completed: false } })}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
      />
    );

    expect(screen.getByText(/Linked to task: Prepare report/)).toBeInTheDocument();
  });

  it('calls onEdit when Edit is clicked', () => {
    const onEdit = vi.fn();
    const event = makeEvent();
    renderWithProviders(<EventItem event={event} onEdit={onEdit} onDelete={vi.fn()} />);

    fireEvent.click(screen.getByText('Edit'));

    expect(onEdit).toHaveBeenCalledWith(event);
  });

  it('calls onDelete with the event id when Delete is clicked', () => {
    const onDelete = vi.fn();
    renderWithProviders(<EventItem event={makeEvent()} onEdit={vi.fn()} onDelete={onDelete} />);

    fireEvent.click(screen.getByText('Delete'));

    expect(onDelete).toHaveBeenCalledWith('event-1');
  });
});
