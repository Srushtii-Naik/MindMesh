import { useState } from 'react';
import { extractApiErrorMessage } from '@/api/errors';
import {
  addDays,
  addMonths,
  formatMonthLabel,
  formatFullDateLabel,
  startOfWeek,
  toIsoDate,
} from '@/features/calendar/dateUtils';
import { useDeleteEvent } from '@/features/calendar/hooks';
import { CalendarToolbar } from '@/features/calendar/components/CalendarToolbar';
import { MonthView } from '@/features/calendar/components/MonthView';
import { WeekView } from '@/features/calendar/components/WeekView';
import { DayView } from '@/features/calendar/components/DayView';
import { EventForm } from '@/features/calendar/components/EventForm';
import { RemindersPanel } from '@/features/reminders';
import type { CalendarEvent, CalendarViewMode, IsoDate } from '@/features/calendar/types';

/**
 * ROADMAP.md Milestone 5 — Calendar & Scheduling: month/week/day calendar
 * views, event CRUD, and daily/weekly planners, all backed by real
 * event/task data. Reminders (foundational data model, per Milestone 5's
 * scope) surface here as a lightweight panel.
 */
export function CalendarPage() {
  const [viewMode, setViewMode] = useState<CalendarViewMode>('month');
  const [anchorDate, setAnchorDate] = useState<IsoDate>(() => toIsoDate(new Date()));
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | undefined>(undefined);
  const [formInitialDate, setFormInitialDate] = useState<IsoDate | undefined>(undefined);
  const [isFormOpen, setIsFormOpen] = useState(false);

  const deleteEvent = useDeleteEvent();

  const openCreateForm = (initialDate?: IsoDate) => {
    setEditingEvent(undefined);
    setFormInitialDate(initialDate);
    setIsFormOpen(true);
  };

  const openEditForm = (event: CalendarEvent) => {
    setEditingEvent(event);
    setFormInitialDate(undefined);
    setIsFormOpen(true);
  };

  const closeForm = () => {
    setIsFormOpen(false);
    setEditingEvent(undefined);
    setFormInitialDate(undefined);
  };

  const handleSelectDay = (day: IsoDate) => {
    setAnchorDate(day);
    setViewMode('day');
  };

  const handlePrevious = () => {
    if (viewMode === 'month') {
      setAnchorDate(addMonths(anchorDate, -1));
    } else if (viewMode === 'week') {
      setAnchorDate(addDays(anchorDate, -7));
    } else {
      setAnchorDate(addDays(anchorDate, -1));
    }
  };

  const handleNext = () => {
    if (viewMode === 'month') {
      setAnchorDate(addMonths(anchorDate, 1));
    } else if (viewMode === 'week') {
      setAnchorDate(addDays(anchorDate, 7));
    } else {
      setAnchorDate(addDays(anchorDate, 1));
    }
  };

  const handleToday = () => setAnchorDate(toIsoDate(new Date()));

  const handleDeleteEvent = (eventId: string) => {
    deleteEvent.mutate(eventId);
  };

  const toolbarLabel =
    viewMode === 'month'
      ? formatMonthLabel(anchorDate)
      : viewMode === 'week'
        ? `Week of ${formatFullDateLabel(startOfWeek(anchorDate))}`
        : formatFullDateLabel(anchorDate);

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-brand-700 dark:text-brand-300">
          Calendar
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Your events and task due dates, all in one place.
        </p>
      </header>

      <CalendarToolbar
        label={toolbarLabel}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        onPrevious={handlePrevious}
        onNext={handleNext}
        onToday={handleToday}
        onCreateEvent={() => openCreateForm(viewMode === 'day' ? anchorDate : undefined)}
      />

      {isFormOpen && (
        <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">
            {editingEvent ? 'Edit event' : 'New event'}
          </h2>
          <EventForm event={editingEvent} initialDate={formInitialDate} onDone={closeForm} />
        </section>
      )}

      {deleteEvent.isError && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {extractApiErrorMessage(deleteEvent.error)}
        </p>
      )}

      {viewMode === 'month' && <MonthView monthAnchor={anchorDate} onSelectDay={handleSelectDay} />}

      {viewMode === 'week' && (
        <WeekView
          weekStart={startOfWeek(anchorDate)}
          onEditEvent={openEditForm}
          onDeleteEvent={handleDeleteEvent}
          onSelectDay={handleSelectDay}
        />
      )}

      {viewMode === 'day' && (
        <DayView date={anchorDate} onEditEvent={openEditForm} onDeleteEvent={handleDeleteEvent} />
      )}

      <RemindersPanel />
    </div>
  );
}
