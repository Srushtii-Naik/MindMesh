import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { ProductivityChart } from '@/features/analytics/components/ProductivityChart';

describe('ProductivityChart', () => {
  it('renders nothing for an empty series', () => {
    const { container } = render(<ProductivityChart series={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders one bar per day in the series', () => {
    const { container } = render(
      <ProductivityChart
        series={[
          { date: '2026-08-18', tasks_completed: 1, tasks_created: 2 },
          { date: '2026-08-19', tasks_completed: 0, tasks_created: 0 },
          { date: '2026-08-20', tasks_completed: 3, tasks_created: 3 },
        ]}
      />
    );

    expect(container.querySelectorAll('rect')).toHaveLength(3);
    expect(container.querySelector('svg')).toHaveAttribute('aria-label', 'Tasks completed per day');
  });
});
