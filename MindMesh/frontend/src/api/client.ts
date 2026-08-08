import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL, API_TIMEOUT_MS } from '@/constants';
import { useAuthStore } from '@/features/auth/store';
import type { RefreshResponse } from '@/features/auth/types';

/**
 * Centralized Axios instance.
 *
 * Per ARCHITECTURE.md Section 2 & 6: all network communication is centralized
 * through this client — no direct fetch/axios calls inside components or
 * feature hooks. Domain-specific request functions live in `api/<domain>.ts`
 * or `features/<domain>/api.ts` and are consumed via TanStack Query hooks.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
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

async function refreshAccessToken(): Promise<string> {
  const { refreshToken, setTokens, clearAuth } = useAuthStore.getState();

  if (!refreshToken) {
    clearAuth();
    throw new Error('No refresh token available.');
  }

  try {
    const { data } = await refreshClient.post<RefreshResponse>('/auth/token/refresh/', {
      refresh: refreshToken,
    });
    // The backend rotates refresh tokens (SIMPLE_JWT.ROTATE_REFRESH_TOKENS),
    // so a new refresh token is issued alongside the new access token.
    setTokens({ access: data.access, refresh: data.refresh ?? refreshToken });
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
    const { refreshToken } = useAuthStore.getState();

    const shouldAttemptRefresh =
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      Boolean(refreshToken);

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
