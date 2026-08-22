import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { HabitHeatmap } from '@/features/analytics/components/HabitHeatmap';

describe('HabitHeatmap', () => {
  it('renders nothing for an empty activity list', () => {
    const { container } = render(<HabitHeatmap activity={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders one cell per day of activity', () => {
    const { container } = render(
      <HabitHeatmap
        activity={[
          { date: '2026-08-18', is_active_day: true },
          { date: '2026-08-19', is_active_day: false },
          { date: '2026-08-20', is_active_day: true },
        ]}
      />
    );

    expect(container.querySelectorAll('rect')).toHaveLength(3);
    expect(container.querySelector('svg')).toHaveAttribute(
      'aria-label',
      'Daily task-completion activity'
    );
  });
});
