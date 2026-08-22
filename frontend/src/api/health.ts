import { apiClient } from '@/api/client';

export interface HealthCheckResponse {
  status: string;
}

/**
 * Calls the backend health-check endpoint.
 * This is the only endpoint expected to exist at the Milestone 1 (Foundation) stage —
 * see ROADMAP.md, Milestone 1 Deliverables.
 */
export async function getHealthStatus(): Promise<HealthCheckResponse> {
  const { data } = await apiClient.get<HealthCheckResponse>('/health/');
  return data;
}
