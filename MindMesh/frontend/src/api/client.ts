import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios';
import { API_BASE_URL, API_TIMEOUT_MS } from '@/constants';

/**
 * Centralized Axios instance.
 *
 * Per ARCHITECTURE.md Section 2 & 6: all network communication is centralized
 * through this client — no direct fetch/axios calls inside components or
 * feature hooks. Domain-specific request functions live in `api/<domain>.ts`
 * and are consumed via TanStack Query hooks.
 *
 * NOTE (Milestone 1 — Foundation only):
 * Token attachment and refresh logic are scaffolded but intentionally inert.
 * Real authentication is implemented in Milestone 2 per ROADMAP.md.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
  },
});

/** Placeholder token getter — replaced by real auth/session storage in Milestone 2. */
function getAccessToken(): string | null {
  return null;
}

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Error-shape normalization for TanStack Query is expanded in Milestone 2
    // once the backend's standardized error envelope (ARCHITECTURE.md Section 6)
    // is implemented. For now, errors are passed through unmodified.
    return Promise.reject(error);
  }
);

export default apiClient;
