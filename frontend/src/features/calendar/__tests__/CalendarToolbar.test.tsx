import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { CalendarToolbar } from '@/features/calendar/components/CalendarToolbar';

describe('CalendarToolbar', () => {
  it('renders the current label', () => {
    renderWithProviders(
      <CalendarToolbar
        label="March 2026"
        viewMode="month"
        onViewModeChange={vi.fn()}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        onToday={vi.fn()}
        onCreateEvent={vi.fn()}
      />
    );

    expect(screen.getByText('March 2026')).toBeInTheDocument();
  });

  it('calls onPrevious/onNext/onToday when navigation buttons are clicked', () => {
    const onPrevious = vi.fn();
    const onNext = vi.fn();
    const onToday = vi.fn();

    renderWithProviders(
      <CalendarToolbar
        label="March 2026"
        viewMode="month"
        onViewModeChange={vi.fn()}
        onPrevious={onPrevious}
        onNext={onNext}
        onToday={onToday}
        onCreateEvent={vi.fn()}
      />
    );

    fireEvent.click(screen.getByLabelText('Previous'));
    fireEvent.click(screen.getByLabelText('Next'));
    fireEvent.click(screen.getByText('Today'));

    expect(onPrevious).toHaveBeenCalledOnce();
    expect(onNext).toHaveBeenCalledOnce();
    expect(onToday).toHaveBeenCalledOnce();
  });

  it('calls onViewModeChange with the selected view', () => {
    const onViewModeChange = vi.fn();

    renderWithProviders(
      <CalendarToolbar
        label="March 2026"
        viewMode="month"
        onViewModeChange={onViewModeChange}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        onToday={vi.fn()}
        onCreateEvent={vi.fn()}
      />
    );

    fireEvent.click(screen.getByText('Week'));

    expect(onViewModeChange).toHaveBeenCalledWith('week');
  });

  it('calls onCreateEvent when "New event" is clicked', () => {
    const onCreateEvent = vi.fn();

    renderWithProviders(
      <CalendarToolbar
        label="March 2026"
        viewMode="month"
        onViewModeChange={vi.fn()}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
        onToday={vi.fn()}
        onCreateEvent={onCreateEvent}
      />
    );

    fireEvent.click(screen.getByText('New event'));

    expect(onCreateEvent).toHaveBeenCalledOnce();
  });
});
