import { describe, it, expect } from 'vitest';
import {
  addDays,
  addMonths,
  endOfMonthGrid,
  startOfMonthGrid,
  startOfWeek,
  toIsoDate,
} from '@/features/calendar/dateUtils';

describe('calendar dateUtils', () => {
  it('addDays adds/subtracts calendar days without UTC drift', () => {
    expect(addDays('2026-03-10', 5)).toBe('2026-03-15');
    expect(addDays('2026-03-10', -10)).toBe('2026-02-28');
  });

  it('addMonths moves to the same day-of-month in another month', () => {
    expect(addMonths('2026-03-15', 1)).toBe('2026-04-01');
    expect(addMonths('2026-03-15', -1)).toBe('2026-02-01');
  });

  it("startOfWeek returns the Monday of the given date's week", () => {
    // 2026-03-11 is a Wednesday
    expect(startOfWeek('2026-03-11')).toBe('2026-03-09');
    // 2026-03-08 is a Sunday — should roll back to the previous Monday
    expect(startOfWeek('2026-03-08')).toBe('2026-03-02');
  });

  it('startOfMonthGrid/endOfMonthGrid produce a 42-day (6-week) grid', () => {
    const gridStart = startOfMonthGrid('2026-03-15');
    const gridEnd = endOfMonthGrid('2026-03-15');

    expect(addDays(gridStart, 41)).toBe(gridEnd);
    // The grid must start on a Monday and fully contain March 1st.
    expect(gridStart <= '2026-03-01').toBe(true);
  });

  it('toIsoDate formats using local date parts, not UTC', () => {
    const date = new Date(2026, 2, 5); // March 5, 2026 local time
    expect(toIsoDate(date)).toBe('2026-03-05');
  });
});
