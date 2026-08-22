import { useQuery } from '@tanstack/react-query';
import { getProgressReportRequest, listProgressReportsRequest } from '@/features/analytics/api';

export const PROGRESS_REPORTS_QUERY_KEY = ['analytics', 'reports'] as const;

export function useProgressReports() {
  return useQuery({
    queryKey: PROGRESS_REPORTS_QUERY_KEY,
    queryFn: listProgressReportsRequest,
  });
}

export function useProgressReport(reportId: string | undefined) {
  return useQuery({
    queryKey: [...PROGRESS_REPORTS_QUERY_KEY, 'detail', reportId ?? ''],
    queryFn: () => getProgressReportRequest(reportId as string),
    enabled: Boolean(reportId),
  });
}
