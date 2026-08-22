import type { DailySeriesPoint } from '@/features/analytics/types';

interface ProductivityChartProps {
  series: DailySeriesPoint[];
}

/**
 * A calm, minimal bar chart of daily task completions, built with plain SVG
 * rather than a charting library — MindMesh's tech stack is locked
 * (PROJECT_RULES.md Section 2) and this is the only place in the app that
 * needs a chart, so a small purpose-built component avoids an unnecessary
 * new dependency while still meeting ROADMAP.md Milestone 11's "Insights
 * presented calmly and clearly — no dashboard clutter" bar.
 */
export function ProductivityChart({ series }: ProductivityChartProps) {
  if (series.length === 0) {
    return null;
  }

  const width = 700;
  const height = 160;
  const paddingBottom = 20;
  const barGap = 3;
  const barWidth = width / series.length - barGap;
  const maxValue = Math.max(1, ...series.map((point) => point.tasks_completed));

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-40 w-full"
      role="img"
      aria-label="Tasks completed per day"
    >
      {series.map((point, index) => {
        const barHeight =
          point.tasks_completed === 0
            ? 0
            : Math.max(3, (point.tasks_completed / maxValue) * (height - paddingBottom));
        const x = index * (barWidth + barGap);
        const y = height - paddingBottom - barHeight;

        return (
          <rect
            key={point.date}
            x={x}
            y={y}
            width={Math.max(barWidth, 1)}
            height={barHeight}
            rx={2}
            className={
              point.tasks_completed > 0
                ? 'fill-brand-500 dark:fill-brand-400'
                : 'fill-slate-100 dark:fill-slate-700'
            }
          >
            <title>
              {point.date}: {point.tasks_completed} completed
            </title>
          </rect>
        );
      })}
      <line
        x1={0}
        y1={height - paddingBottom}
        x2={width}
        y2={height - paddingBottom}
        className="stroke-slate-200 dark:stroke-slate-700"
        strokeWidth={1}
      />
    </svg>
  );
}
