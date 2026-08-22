import type { DailyActivityPoint } from '@/features/analytics/types';

interface HabitHeatmapProps {
  activity: DailyActivityPoint[];
}

/**
 * A calm, minimal calendar heatmap of daily task-completion activity —
 * plain SVG rects, same rationale as ProductivityChart (no new charting
 * dependency needed for a single grid of squares).
 */
export function HabitHeatmap({ activity }: HabitHeatmapProps) {
  if (activity.length === 0) {
    return null;
  }

  const columns = Math.ceil(activity.length / 7);
  const cellSize = 12;
  const cellGap = 3;
  const width = columns * (cellSize + cellGap);
  const height = 7 * (cellSize + cellGap);

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-32 w-full"
      role="img"
      aria-label="Daily task-completion activity"
    >
      {activity.map((point, index) => {
        const column = Math.floor(index / 7);
        const row = index % 7;
        const x = column * (cellSize + cellGap);
        const y = row * (cellSize + cellGap);

        return (
          <rect
            key={point.date}
            x={x}
            y={y}
            width={cellSize}
            height={cellSize}
            rx={2}
            className={
              point.is_active_day
                ? 'fill-brand-500 dark:fill-brand-400'
                : 'fill-slate-100 dark:fill-slate-700'
            }
          >
            <title>
              {point.date}: {point.is_active_day ? 'active' : 'no tasks completed'}
            </title>
          </rect>
        );
      })}
    </svg>
  );
}
