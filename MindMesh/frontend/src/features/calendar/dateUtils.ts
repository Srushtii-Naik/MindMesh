import type { IsoDate } from '@/features/calendar/types';

/** Formats a Date as a local YYYY-MM-DD string (avoids UTC-shift bugs from toISOString()). */
export function toIsoDate(date: Date): IsoDate {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function fromIsoDate(isoDate: IsoDate): Date {
  const [year, month, day] = isoDate.split('-').map(Number);
  return new Date(year, month - 1, day);
}

export function addDays(isoDate: IsoDate, days: number): IsoDate {
  const date = fromIsoDate(isoDate);
  date.setDate(date.getDate() + days);
  return toIsoDate(date);
}

export function addMonths(isoDate: IsoDate, months: number): IsoDate {
  const date = fromIsoDate(isoDate);
  date.setDate(1);
  date.setMonth(date.getMonth() + months);
  return toIsoDate(date);
}

/** Monday of the week containing `isoDate`. */
export function startOfWeek(isoDate: IsoDate): IsoDate {
  const date = fromIsoDate(isoDate);
  const day = date.getDay(); // 0 = Sunday
  const diff = day === 0 ? -6 : 1 - day;
  date.setDate(date.getDate() + diff);
  return toIsoDate(date);
}

/** First day of the month grid — the Monday on/before the 1st of the month. */
export function startOfMonthGrid(isoDate: IsoDate): IsoDate {
  const date = fromIsoDate(isoDate);
  const firstOfMonth = toIsoDate(new Date(date.getFullYear(), date.getMonth(), 1));
  return startOfWeek(firstOfMonth);
}

/** Last day of the month grid — always 42 days (6 weeks) after the grid start, for a stable layout. */
export function endOfMonthGrid(isoDate: IsoDate): IsoDate {
  return addDays(startOfMonthGrid(isoDate), 41);
}

export function formatDayLabel(isoDate: IsoDate): string {
  return fromIsoDate(isoDate).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric' });
}

export function formatMonthLabel(isoDate: IsoDate): string {
  return fromIsoDate(isoDate).toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
}

export function formatFullDateLabel(isoDate: IsoDate): string {
  return fromIsoDate(isoDate).toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });
}

export function formatTimeLabel(isoDateTime: string): string {
  return new Date(isoDateTime).toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function isSameIsoDate(isoDateTime: string, isoDate: IsoDate): boolean {
  return toIsoDate(new Date(isoDateTime)) === isoDate;
}

export function isToday(isoDate: IsoDate): boolean {
  return isoDate === toIsoDate(new Date());
}
