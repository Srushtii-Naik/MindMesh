import { apiClient } from '@/api/client';
import type {
  HabitTracking,
  ProductivityAnalytics,
  ProgressReport,
  Recommendations,
} from '@/features/analytics/types';

/**
 * Analytics domain requests. Consumed exclusively via the TanStack Query
 * hooks in `features/analytics/hooks/` — no component calls these
 * directly, per ARCHITECTURE.md Section 2 ("No direct fetch calls inside
 * components").
 */

export async function getProductivityAnalyticsRequest(
  days?: number
): Promise<ProductivityAnalytics> {
  const { data } = await apiClient.get<ProductivityAnalytics>('/analytics/productivity/', {
    params: days ? { days } : undefined,
  });
  return data;
}

export async function getHabitTrackingRequest(days?: number): Promise<HabitTracking> {
  const { data } = await apiClient.get<HabitTracking>('/analytics/habits/', {
    params: days ? { days } : undefined,
  });
  return data;
}

export async function getRecommendationsRequest(): Promise<Recommendations> {
  const { data } = await apiClient.get<Recommendations>('/analytics/recommendations/');
  return data;
}

export async function listProgressReportsRequest(): Promise<ProgressReport[]> {
  const { data } = await apiClient.get<ProgressReport[]>('/analytics/reports/');
  return data;
}

export async function getProgressReportRequest(reportId: string): Promise<ProgressReport> {
  const { data } = await apiClient.get<ProgressReport>(`/analytics/reports/${reportId}/`);
  return data;
}
