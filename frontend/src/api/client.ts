import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL, API_TIMEOUT_MS } from '@/constants';
import { getCsrfHeader } from '@/api/cookies';
import { useAuthStore } from '@/features/auth/store';
import type { RefreshResponse } from '@/features/auth/types';

/**
 * Centralized Axios instance.
 *
 * Per ARCHITECTURE.md Section 2 & 6: all network communication is centralized
 * through this client — no direct fetch/axios calls inside components or
 * feature hooks. Domain-specific request functions live in `api/<domain>.ts`
 * or `features/<domain>/api.ts` and are consumed via TanStack Query hooks.
 *
 * `withCredentials: true` (Milestone 12 / ADR 0001) is required so the
 * browser sends the httpOnly refresh cookie and the CSRF cookie on requests
 * to the backend — without it, the cookies set on login/register would
 * never be included on subsequent requests, breaking the refresh flow
 * entirely.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * A separate, interceptor-free instance for the refresh call itself —
 * using `apiClient` here would recurse back into the 401 handler below.
 */
const refreshClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

/**
 * In-flight refresh promise, shared across concurrent 401s so a burst of
 * requests triggers exactly one refresh call rather than one per request.
 */
let refreshPromise: Promise<string> | null = null;

/**
 * Calls the refresh endpoint using the httpOnly refresh cookie (sent
 * automatically by the browser via `withCredentials`) and the readable
 * CSRF cookie (attached manually as a header, per apps/accounts/cookies.py
 * on the backend). No token is sent in the request body — there is none
 * for JavaScript to read anymore.
 */
export async function refreshAccessToken(): Promise<string> {
  const { setAccessToken, clearAuth } = useAuthStore.getState();
  const csrfHeader = getCsrfHeader();

  if (Object.keys(csrfHeader).length === 0) {
    // No CSRF cookie means no prior session to restore — not an error,
    // just nothing to refresh (e.g. a first-time visitor).
    clearAuth();
    throw new Error('No active session to refresh.');
  }

  try {
    const { data } = await refreshClient.post<RefreshResponse>(
      '/auth/token/refresh/',
      {},
      { headers: csrfHeader }
    );
    setAccessToken(data.access);
    return data.access;
  } catch (error) {
    clearAuth();
    throw error;
  }
}

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;
    const hasCsrfCookie = Object.keys(getCsrfHeader()).length > 0;

    const shouldAttemptRefresh =
      error.response?.status === 401 && originalRequest && !originalRequest._retry && hasCsrfCookie;

    if (!shouldAttemptRefresh || !originalRequest) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
      const newAccessToken = await refreshPromise;

      originalRequest.headers = originalRequest.headers ?? {};
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      return Promise.reject(refreshError);
    }
  }
);

export default apiClient;
